"""Provider image entry point."""

from __future__ import annotations

import argparse
import os
import ssl
from pathlib import Path

import uvicorn

from .app import create_app
from .engine import Engine, Settings, read_profile, release_digest

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
        choices=("serve", "verify-config", "print-release-digest"),
        nargs="?",
        default="serve",
    )
    args = parser.parse_args()
    lock, prompts, release = paths()
    if args.command == "verify-config":
        read_profile(lock, prompts)
        release_digest(release)
        return
    if args.command == "print-release-digest":
        print(release_digest(release))
        return
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
            uvicorn.run(app, host="0.0.0.0", port=18486, access_log=False)
        else:
            uvicorn.run(
                app,
                host="0.0.0.0",
                port=18486,
                access_log=False,
                ssl_certfile=str(tls_root / "server.crt"),
                ssl_keyfile=str(tls_root / "server.key"),
                ssl_ca_certs=str(tls_root / "client-ca.crt"),
                ssl_cert_reqs=ssl.CERT_REQUIRED,
            )
    finally:
        if engine is not None:
            engine.close()


if __name__ == "__main__":
    main()
