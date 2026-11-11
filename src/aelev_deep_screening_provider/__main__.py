"""Provider image entry point."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import uvicorn

from .app import create_app
from .engine import Engine, Settings, read_profile, release_digest
from .health import clear_readiness, healthy, monitor_readiness
from .tls_server import serve

ROOT = Path(__file__).resolve().parents[2]


def paths() -> tuple[Path, Path, Path]:
    return (
        Path(
            os.environ.get("AELEV_PROVIDER_LOCK_PATH", str(ROOT / "provider.lock.json"))
        ),
        Path(os.environ.get("AELEV_PROVIDER_PROMPT_ROOT", str(ROOT / "prompts"))),
        Path(os.environ.get("AELEV_PROVIDER_RELEASE_PATH", str(ROOT / "release.json"))),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=("serve", "verify-config", "print-release-digest", "healthcheck"),
        nargs="?",
        default="serve",
    )
    args = parser.parse_args()
    if args.command == "healthcheck":
        raise SystemExit(0 if healthy() else 1)
    lock, prompts, release = paths()
    if args.command == "verify-config":
        read_profile(lock, prompts)
        release_digest(release)
        return
    if args.command == "print-release-digest":
        print(release_digest(release))
        return
    clear_readiness()
    digest = release_digest(release)
    engine: Engine | None = None
    blocker: str | None = None
    try:
        engine = Engine(Settings.environment())
    except RuntimeError as error:
        blocker = (
            str(error) if str(error).startswith("PROVIDER_") else "PROVIDER_NOT_READY"
        )
    tls_root = Path(
        os.environ.get("AELEV_PROVIDER_TLS_ROOT", "/run/secrets/model-module")
    )
    try:
        app = create_app(engine, digest, blocker)
        if os.environ.get("AELEV_PROVIDER_INSECURE_HTTP") == "1":
            with monitor_readiness(lambda: engine is not None):
                uvicorn.run(app, host="0.0.0.0", port=18486, access_log=False)
        else:
            serve(app, tls_root, "deep-screening", 18486, engine is not None)
    finally:
        clear_readiness()
        if engine is not None:
            engine.close()


if __name__ == "__main__":
    main()
