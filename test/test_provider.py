from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

import httpx
import pytest

from aelev_deep_screening_provider.app import create_app
from aelev_deep_screening_provider.contract import (
    RequestInvalid,
    parse_request,
    validate_output,
)
from aelev_deep_screening_provider.engine import (
    Engine,
    Settings,
    read_api_key,
    read_profile,
    release_digest,
)

ROOT = Path(__file__).resolve().parents[1]
DIGEST = "sha256:e2551416b933fde52bd4921868333f3775b61221284ad768130a81d6d79696aa"
OUTPUT: dict[str, object] = {
    "decision": "REVIEW",
    "candidates": [],
    "unknown_scope": "The bounded material is insufficient.",
}
MODEL_INPUT: dict[str, object] = {
    "schema_version": 1,
    "target_url": "https://example.gov/",
    "documents": [],
}


def settings() -> Settings:
    profile = read_profile(ROOT / "provider.lock.json", ROOT / "prompts")
    return Settings(
        profile,
        release_digest(ROOT / "release.json"),
        profile.prompt_path.read_text(),
        "fixture-openai-key-not-secret",
        30,
    )


def api_response(output: dict[str, object]) -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "status": "completed",
            "model": "gpt-6.1-sol",
            "output": [
                {"type": "reasoning"},
                {
                    "type": "message",
                    "status": "completed",
                    "content": [{"type": "output_text", "text": json.dumps(output)}],
                },
            ],
        },
    )


def envelope(**changes: object) -> dict[str, object]:
    value: dict[str, object] = {
        "schema_version": 1,
        "owner": "deep-screening",
        "task": "SENSOR_SURFACE",
        "request_id": "job:attempt-1",
        "release_digest": DIGEST,
        "input": MODEL_INPUT,
    }
    value.update(changes)
    return value


def test_lock_prompt_and_neutral_release_are_exact() -> None:
    profile = read_profile(ROOT / "provider.lock.json", ROOT / "prompts")
    assert profile.model == "gpt-6.1-sol"
    assert profile.endpoint == "https://api.openai.com/v1/responses"
    assert release_digest(ROOT / "release.json") == DIGEST
    assert "openai" not in json.loads((ROOT / "release.json").read_text())


def test_placeholder_is_not_a_credential(tmp_path: Path) -> None:
    secret = tmp_path / "credential.env"
    secret.write_text("OPENAI_API_KEY=REPLACE_WITH_OPENAI_API_KEY\n")
    with pytest.raises(RuntimeError, match="PROVIDER_CREDENTIAL_UNREADABLE"):
        read_api_key(secret)


def test_request_and_output_are_exact() -> None:
    request = parse_request(envelope(), DIGEST)
    assert request.request_id == "job:attempt-1"
    assert validate_output(OUTPUT) == OUTPUT
    with pytest.raises(RequestInvalid):
        parse_request(envelope(model="forbidden"), DIGEST)
    with pytest.raises(RuntimeError):
        validate_output({**OUTPUT, "provider": "forbidden"})


def test_responses_request_is_stateless_structured_and_provider_owned() -> None:
    def respond(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == "https://api.openai.com/v1/responses"
        assert (
            request.headers["Authorization"] == "Bearer fixture-openai-key-not-secret"
        )
        payload = json.loads(request.content)
        assert payload["model"] == "gpt-6.1-sol"
        assert payload["store"] is False
        assert payload["reasoning"] == {"effort": "medium"}
        assert payload["text"]["format"]["strict"] is True
        assert "tools" not in payload and "previous_response_id" not in payload
        assert json.loads(payload["input"][0]["content"][0]["text"]) == MODEL_INPUT
        return api_response(OUTPUT)

    engine = Engine(settings(), httpx.MockTransport(respond))
    try:
        assert engine.infer(MODEL_INPUT) == OUTPUT
    finally:
        engine.close()


async def request(
    app: Any, method: str, path: str, payload: object | None = None
) -> httpx.Response:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://provider"
    ) as client:
        return await client.request(method, path, json=payload)


class FakeEngine:
    settings = object()

    def infer(self, model_input: dict[str, object]) -> dict[str, object]:
        assert model_input["target_url"] == "https://example.gov/"
        return OUTPUT


def test_http_contract_discloses_no_implementation_identity() -> None:
    app = create_app(FakeEngine(), DIGEST)
    status = asyncio.run(request(app, "GET", "/v1/status")).json()
    assert status["state"] == "READY"
    assert set(status) == {
        "schema_version",
        "owner",
        "task",
        "release_digest",
        "state",
        "blocker",
        "capabilities",
        "observed_at",
    }
    response = asyncio.run(request(app, "POST", "/v1/infer", envelope()))
    assert response.status_code == 200
    assert response.json()["output"] == OUTPUT
    assert "openai" not in json.dumps(response.json()).lower()


def test_blocked_status_needs_no_api_call() -> None:
    response = asyncio.run(
        request(
            create_app(None, DIGEST, "PROVIDER_CREDENTIAL_UNREADABLE"),
            "GET",
            "/v1/status",
        )
    )
    assert response.json()["state"] == "BLOCKED"
    assert response.json()["blocker"] == "PROVIDER_CREDENTIAL_UNREADABLE"
