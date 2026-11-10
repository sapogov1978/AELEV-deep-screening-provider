"""Local process readiness; this probe never reads a key or calls upstream."""

from __future__ import annotations

import json
import os
import socket
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import cast

HEALTH_FILE = Path("/tmp/aelev-deep-screening-provider-readiness.json")
PORT = 18486


def record_readiness(ready: bool) -> None:
    """Publish only the serving process's initialized inference state."""
    with NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=HEALTH_FILE.parent, delete=False
    ) as stream:
        temporary = Path(stream.name)
        json.dump({"ready": ready, "pid": os.getpid()}, stream)
    try:
        temporary.replace(HEALTH_FILE)
    finally:
        temporary.unlink(missing_ok=True)


def clear_readiness() -> None:
    HEALTH_FILE.unlink(missing_ok=True)


def healthy() -> bool:
    """Require initialized inference, its live process, and its bound port."""
    try:
        raw = HEALTH_FILE.read_bytes()
        if len(raw) > 1024:
            return False
        decoded: object = json.loads(raw)
        if not isinstance(decoded, dict):
            return False
        value = cast(dict[str, object], decoded)
        pid = value.get("pid")
        if (
            set(value) != {"ready", "pid"}
            or value.get("ready") is not True
            or type(pid) is not int
            or not 0 < pid <= 2_147_483_647
        ):
            return False
        os.kill(pid, 0)
        with socket.create_connection(("127.0.0.1", PORT), timeout=2):
            return True
    except (OSError, ValueError):
        return False
