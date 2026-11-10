from __future__ import annotations

import json
import os
import socket
import sys
from pathlib import Path

import pytest

from aelev_deep_screening_provider import __main__ as entrypoint
from aelev_deep_screening_provider import health


@pytest.fixture(autouse=True)
def isolated_health_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(health, "HEALTH_FILE", tmp_path / "readiness.json")


def test_blocked_inference_never_passes_even_with_a_listening_port(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden_connect(*_: object, **__: object) -> socket.socket:
        raise AssertionError("blocked inference must fail before probing TCP")

    monkeypatch.setattr(health.socket, "create_connection", forbidden_connect)
    health.record_readiness(False)
    assert not health.healthy()


def test_ready_inference_requires_a_live_listener(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen(1)
        monkeypatch.setattr(health, "PORT", listener.getsockname()[1])
        health.record_readiness(True)
        assert health.healthy()
    assert not health.healthy()
    health.clear_readiness()
    assert not health.HEALTH_FILE.exists()


@pytest.mark.parametrize(
    "value",
    [
        {"ready": True, "pid": True},
        {"ready": True, "pid": 0},
        {"ready": True, "pid": -1},
        {"ready": True, "pid": 2_147_483_648},
        {"ready": 1, "pid": os.getpid()},
        {"ready": True, "pid": os.getpid(), "unexpected": True},
        [],
    ],
)
def test_malformed_readiness_is_not_healthy(value: object) -> None:
    health.HEALTH_FILE.write_text(json.dumps(value))
    assert not health.healthy()


def test_missing_or_invalid_readiness_is_not_healthy() -> None:
    assert not health.healthy()
    health.HEALTH_FILE.write_text("{")
    assert not health.healthy()


@pytest.mark.parametrize("ready", [True, False])
def test_health_cli_does_not_initialize_inference(
    monkeypatch: pytest.MonkeyPatch, ready: bool
) -> None:
    def forbidden_paths() -> tuple[Path, Path, Path]:
        raise AssertionError("health CLI must not initialize inference or read a key")

    monkeypatch.setattr(sys, "argv", ["provider", "healthcheck"])
    monkeypatch.setattr(entrypoint, "paths", forbidden_paths)
    monkeypatch.setattr(entrypoint, "healthy", lambda: ready)
    with pytest.raises(SystemExit) as error:
        entrypoint.main()
    assert error.value.code == (0 if ready else 1)
