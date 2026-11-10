"""Overload and timeout checks never invoke an upstream API."""

from __future__ import annotations

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

import httpx
import pytest
from test_provider import OUTPUT, api_response, envelope, request, settings

from aelev_deep_screening_provider.app import create_app
from aelev_deep_screening_provider.engine import Engine, ProviderUnavailable


def test_overlapping_http_inference_is_busy_without_a_second_upstream_call() -> None:
    entered = threading.Event()
    release = threading.Event()
    calls = 0

    def respond(_request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        entered.set()
        assert release.wait(5)
        return api_response(OUTPUT)

    engine = Engine(settings(), httpx.MockTransport(respond))
    app = create_app(engine, engine.settings.release_digest)
    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            first = pool.submit(engine.infer, {"documents": []})
            assert entered.wait(2)
            try:
                response = asyncio.run(request(app, "POST", "/v1/infer", envelope()))
                assert response.status_code == 503
                assert response.json() == {"detail": "PROVIDER_BUSY"}
                assert calls == 1 and not first.done()
            finally:
                release.set()
            assert first.result(timeout=2) == OUTPUT
        assert engine.infer({"documents": []}) == OUTPUT
        assert calls == 2
    finally:
        release.set()
        engine.close()


def test_upstream_timeout_releases_capacity_for_the_next_request() -> None:
    calls = 0

    def respond(upstream: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise httpx.ReadTimeout("fixture timeout", request=upstream)
        return api_response(OUTPUT)

    engine = Engine(settings(), httpx.MockTransport(respond))
    try:
        with pytest.raises(ProviderUnavailable, match="PROVIDER_DEADLINE_EXCEEDED"):
            engine.infer({"documents": []})
        assert engine.infer({"documents": []}) == OUTPUT
        assert calls == 2
    finally:
        engine.close()
