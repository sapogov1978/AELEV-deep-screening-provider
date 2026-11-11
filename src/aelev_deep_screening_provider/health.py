"""Local process readiness; this probe never reads a key or calls upstream."""

from __future__ import annotations

import json
import math
import os
import socket
import threading
import time
from collections.abc import Callable, Generator
from contextlib import contextmanager
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import cast

HEALTH_FILE = Path("/tmp/aelev-deep-screening-provider-readiness.json")
PORT = 18486


def record_readiness(ready: bool) -> None:
    """Publish the serving process's current inference and identity readiness."""
    with NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=HEALTH_FILE.parent, delete=False
    ) as stream:
        temporary = Path(stream.name)
        json.dump(
            {"ready": ready, "pid": os.getpid(), "observed_at": time.monotonic()},
            stream,
        )
    try:
        temporary.replace(HEALTH_FILE)
    finally:
        temporary.unlink(missing_ok=True)


def clear_readiness() -> None:
    HEALTH_FILE.unlink(missing_ok=True)


def healthy() -> bool:
    """Require fresh readiness, its live process, and its bound port."""
    try:
        if HEALTH_FILE.is_symlink():
            return False
        with HEALTH_FILE.open("rb") as stream:
            raw = stream.read(1025)
        if len(raw) > 1024:
            return False
        decoded: object = json.loads(raw)
        if not isinstance(decoded, dict):
            return False
        value = cast(dict[str, object], decoded)
        pid = value.get("pid")
        observed = value.get("observed_at")
        if isinstance(observed, bool) or not isinstance(observed, int | float):
            return False
        if (
            set(value) != {"ready", "pid", "observed_at"}
            or value.get("ready") is not True
            or type(pid) is not int
            or not 0 < pid <= 2_147_483_647
            or not math.isfinite(observed)
            or not 0 <= time.monotonic() - observed <= 5
        ):
            return False
        os.kill(pid, 0)
        with socket.create_connection(("127.0.0.1", PORT), timeout=2):
            return True
    except (OSError, ValueError):
        return False


@contextmanager
def monitor_readiness(check: Callable[[], bool]) -> Generator[None]:
    stopped = threading.Event()

    def observe() -> None:
        while not stopped.is_set():
            record_readiness(check())
            stopped.wait(1)

    observer = threading.Thread(target=observe, name="provider-readiness", daemon=True)
    observer.start()
    try:
        yield
    finally:
        stopped.set()
        observer.join(timeout=2)
        record_readiness(False)
