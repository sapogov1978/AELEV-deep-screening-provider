"""Mutually authenticated owner-facing HTTP application."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated, Protocol

from fastapi import Body, FastAPI, HTTPException

from .contract import OWNER, TASK, RequestInvalid, parse_request, response
from .engine import ProviderUnavailable


class InferenceEngine(Protocol):
    def infer(self, model_input: dict[str, object]) -> dict[str, object]: ...


def create_app(
    engine: InferenceEngine | None, release_digest: str, blocker: str | None = None
) -> FastAPI:
    app = FastAPI(
        title="AELEV opaque Deep Screening provider",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )

    @app.get("/v1/status")
    def status() -> dict[str, object]:
        return {
            "schema_version": 1,
            "owner": OWNER,
            "task": TASK,
            "release_digest": release_digest,
            "state": "READY" if engine is not None else "BLOCKED",
            "blocker": None if engine is not None else blocker or "PROVIDER_NOT_READY",
            "capabilities": ["INFERENCE"],
            "observed_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        }

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        if engine is None:
            raise HTTPException(status_code=503, detail=blocker or "PROVIDER_NOT_READY")
        return {"status": "ok"}

    @app.post("/v1/infer")
    def infer(payload: Annotated[object, Body()]) -> dict[str, object]:
        if engine is None:
            raise HTTPException(status_code=503, detail=blocker or "PROVIDER_NOT_READY")
        try:
            request = parse_request(payload, release_digest)
            return response(request, release_digest, engine.infer(request.input))
        except RequestInvalid as error:
            raise HTTPException(
                status_code=422, detail="DSS_PROVIDER_REQUEST_INVALID"
            ) from error
        except (ProviderUnavailable, RuntimeError) as error:
            code = (
                str(error)
                if str(error).startswith("PROVIDER_")
                else "PROVIDER_RUNTIME_UNAVAILABLE"
            )
            raise HTTPException(status_code=503, detail=code) from error

    return app
