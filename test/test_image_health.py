"""Opt-in networkless test of the image-owned readiness probe."""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from uuid import uuid4

import pytest

IMAGE = os.environ.get("AELEV_PROVIDER_TEST_IMAGE", "")
ROOT = Path(__file__).resolve().parents[1]


def command(*arguments: str) -> str:
    return subprocess.run(
        arguments, check=True, capture_output=True, text=True, timeout=90
    ).stdout.strip()


@pytest.mark.skipif(not IMAGE, reason="requires an explicitly built runtime image")
def test_placeholder_image_is_unhealthy_even_when_the_http_port_is_open() -> None:
    container = command(
        "docker",
        "run",
        "--rm",
        "--detach",
        "--name",
        "aelev-deep-screening-health-test-" + uuid4().hex[:10],
        "--network",
        "none",
        "--read-only",
        "--tmpfs",
        "/tmp:rw,noexec,nosuid,size=16m",
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges",
        "--pids-limit",
        "64",
        "--memory",
        "256m",
        "--env",
        "AELEV_PROVIDER_INSECURE_HTTP=1",
        "--mount",
        "type=bind,source="
        + str(ROOT / ".env.local.example")
        + ",target=/run/secrets/provider/credential.env,readonly",
        IMAGE,
    )
    try:
        deadline = time.monotonic() + 50
        status = "starting"
        while time.monotonic() < deadline:
            status = command(
                "docker",
                "inspect",
                "--format",
                "{{.State.Health.Status}}",
                container,
            )
            assert status != "healthy", "blocked inference was marked healthy"
            if status == "unhealthy":
                break
            time.sleep(1)
        assert status == "unhealthy", "healthcheck did not reach a bounded failure"
        probe = (
            "import json,urllib.request,urllib.error\n"
            "try:\n"
            " r=urllib.request.urlopen('http://127.0.0.1:18486/healthz')\n"
            "except urllib.error.HTTPError as error:\n"
            " r=error\n"
            "print(json.dumps({'status':r.status,'body':json.loads(r.read())}))"
        )
        response = json.loads(
            command("docker", "exec", container, "python", "-c", probe)
        )
        assert response == {
            "status": 503,
            "body": {"detail": "PROVIDER_CREDENTIAL_UNREADABLE"},
        }
    finally:
        command("docker", "stop", "--time", "3", container)
