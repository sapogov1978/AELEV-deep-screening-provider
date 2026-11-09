"""Exact owner-visible compute contract and provider-owned output validation."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, cast
from urllib.parse import urlsplit

OWNER = "deep-screening"
TASK = "SENSOR_SURFACE"
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
MAX_BODY_BYTES = 1024 * 1024


class RequestInvalid(ValueError):
    """Opaque request did not match the exact owner contract."""


@dataclass(frozen=True, slots=True)
class InferenceRequest:
    request_id: str
    input: dict[str, Any]


def parse_request(value: object, release_digest: str) -> InferenceRequest:
    if not isinstance(value, dict):
        raise RequestInvalid("DSS_PROVIDER_REQUEST_INVALID")
    payload = cast(dict[str, object], value)
    request_id = payload.get("request_id")
    model_input = payload.get("input")
    if (
        set(payload)
        != {"schema_version", "owner", "task", "request_id", "release_digest", "input"}
        or payload.get("schema_version") != 1
        or payload.get("owner") != OWNER
        or payload.get("task") != TASK
        or payload.get("release_digest") != release_digest
        or not isinstance(request_id, str)
        or not 0 < len(request_id) <= 240
        or not isinstance(model_input, dict)
        or len(json.dumps(model_input, ensure_ascii=False).encode()) > MAX_BODY_BYTES
    ):
        raise RequestInvalid("DSS_PROVIDER_REQUEST_INVALID")
    return InferenceRequest(request_id, cast(dict[str, Any], model_input))


def validate_output(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise RuntimeError("PROVIDER_RUNTIME_RESPONSE_INVALID")
    output = cast(dict[str, object], value)
    decision = output.get("decision")
    raw_candidates = output.get("candidates")
    candidates = (
        cast(list[object], raw_candidates) if isinstance(raw_candidates, list) else None
    )
    unknown_scope = output.get("unknown_scope")
    if (
        set(output) != {"decision", "candidates", "unknown_scope"}
        or decision not in {"SUITABLE", "UNSUITABLE", "REVIEW"}
        or candidates is None
        or len(candidates) > 128
        or not _text(unknown_scope, 2000)
        or (decision == "SUITABLE") != bool(candidates)
    ):
        raise RuntimeError("PROVIDER_RUNTIME_RESPONSE_INVALID")
    seen: set[str] = set()
    for raw_candidate in candidates:
        if not isinstance(raw_candidate, dict):
            raise RuntimeError("PROVIDER_RUNTIME_RESPONSE_INVALID")
        candidate = cast(dict[str, object], raw_candidate)
        raw_points = candidate.get("access_points")
        points = (
            cast(list[object], raw_points) if isinstance(raw_points, list) else None
        )
        if (
            set(candidate) != {"seed_url", "description", "access_points"}
            or not _url(candidate.get("seed_url"))
            or not _text(candidate.get("description"), 160)
            or points is None
            or not points
            or len(points) > 128
        ):
            raise RuntimeError("PROVIDER_RUNTIME_RESPONSE_INVALID")
        for raw_point in points:
            if not isinstance(raw_point, dict):
                raise RuntimeError("PROVIDER_RUNTIME_RESPONSE_INVALID")
            point = cast(dict[str, object], raw_point)
            url = point.get("url")
            evidence_digest = point.get("evidence_digest")
            if (
                set(point) != {"url", "description", "evidence_url", "evidence_digest"}
                or not _url(url)
                or not _text(point.get("description"), 160)
                or not _url(point.get("evidence_url"))
                or not isinstance(evidence_digest, str)
                or DIGEST.fullmatch(evidence_digest) is None
                or url in seen
            ):
                raise RuntimeError("PROVIDER_RUNTIME_RESPONSE_INVALID")
            seen.add(cast(str, url))
    return output


def _text(value: object, maximum: int) -> bool:
    return isinstance(value, str) and 0 < len(value) <= maximum


def _url(value: object) -> bool:
    if not isinstance(value, str) or len(value) > 4096:
        return False
    parsed = urlsplit(value)
    return (
        parsed.scheme in {"http", "https"}
        and bool(parsed.hostname)
        and not parsed.username
        and not parsed.password
        and not parsed.fragment
    )


def response(
    request: InferenceRequest, release_digest: str, output: dict[str, object]
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "owner": OWNER,
        "task": TASK,
        "request_id": request.request_id,
        "release_digest": release_digest,
        "output": output,
    }
