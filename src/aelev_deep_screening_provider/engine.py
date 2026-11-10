"""Lock-pinned OpenAI Responses execution."""

from __future__ import annotations

import hashlib
import json
import os
import re
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

import httpx

from .contract import validate_output
from .media import content_parts

ENDPOINT = "https://api.openai.com/v1/responses"
ROOT = Path(__file__).resolve().parents[2]
PLACEHOLDERS = frozenset(
    {"REPLACE_WITH_OPENAI_API_KEY", "YOUR_OPENAI_API_KEY", "CHANGE_ME"}
)
OUTPUT_FORMAT = {
    "type": "json_schema",
    "name": "sensor_surface_result",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "required": ["decision", "candidates", "unknown_scope"],
        "properties": {
            "decision": {
                "type": "string",
                "enum": ["SUITABLE", "UNSUITABLE", "REVIEW"],
            },
            "candidates": {
                "type": "array",
                "maxItems": 128,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["seed_url", "description", "access_points"],
                    "properties": {
                        "seed_url": {"type": "string", "maxLength": 4096},
                        "description": {"type": "string", "maxLength": 160},
                        "access_points": {
                            "type": "array",
                            "minItems": 1,
                            "maxItems": 128,
                            "items": {
                                "type": "object",
                                "additionalProperties": False,
                                "required": [
                                    "url",
                                    "description",
                                    "evidence_url",
                                    "evidence_digest",
                                ],
                                "properties": {
                                    "url": {"type": "string", "maxLength": 4096},
                                    "description": {"type": "string", "maxLength": 160},
                                    "evidence_url": {
                                        "type": "string",
                                        "maxLength": 4096,
                                    },
                                    "evidence_digest": {
                                        "type": "string",
                                        "pattern": "^sha256:[0-9a-f]{64}$",
                                    },
                                },
                            },
                        },
                    },
                },
            },
            "unknown_scope": {"type": "string", "maxLength": 2000},
        },
    },
}


class ProviderUnavailable(RuntimeError):
    """Bounded upstream or configuration failure."""


def _mapping(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise RuntimeError("PROVIDER_RUNTIME_RESPONSE_INVALID")
    return cast(dict[str, Any], value)


def execution_reference(api: dict[str, Any], transport: dict[str, Any]) -> str:
    raw = json.dumps(
        {"api": api, "transport": transport}, sort_keys=True, separators=(",", ":")
    ).encode()
    return "openai-responses@sha256:" + hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True, slots=True)
class Profile:
    model: str
    endpoint: str
    reasoning_effort: str
    max_output_tokens: int
    prompt_path: Path
    execution_ref: str


def read_profile(lock_path: Path, prompt_root: Path) -> Profile:
    try:
        lock = _mapping(json.loads(lock_path.read_text(encoding="utf-8")))
    except (OSError, ValueError) as error:
        raise RuntimeError("PROVIDER_LOCK_INVALID") from error
    api = _mapping(lock.get("api"))
    transport = _mapping(lock.get("transport"))
    profile = api.get("prompt_profile")
    prompt_digest = api.get("prompt_sha256")
    if (
        lock.get("schema_version") != "2.0.0"
        or lock.get("status") != "SELECTED_REMOTE_API"
        or lock.get("provider") != "openai"
        or api.get("endpoint") != ENDPOINT
        or not isinstance(api.get("model"), str)
        or re.fullmatch(r"gpt-[a-z0-9][a-z0-9.-]{1,63}", cast(str, api["model"]))
        is None
        or api.get("reasoning_effort") not in {"low", "medium", "high", "xhigh", "max"}
        or type(api.get("max_output_tokens")) is not int
        or not 256 <= cast(int, api["max_output_tokens"]) <= 128000
        or api.get("store") is not False
        or api.get("media_profile") != "bounded-document-content-v2"
        or not isinstance(profile, str)
        or re.fullmatch(r"[a-z0-9][a-z0-9-]{1,63}", profile) is None
        or not isinstance(prompt_digest, str)
        or re.fullmatch(r"[0-9a-f]{64}", prompt_digest) is None
        or transport != {"mode": "direct-https", "tls_verification": "system-ca"}
        or lock.get("execution_ref") != execution_reference(api, transport)
    ):
        raise RuntimeError("PROVIDER_LOCK_INVALID")
    prompt_path = prompt_root / f"{profile}.txt"
    try:
        prompt = prompt_path.read_bytes()
    except OSError as error:
        raise RuntimeError("PROVIDER_PROMPT_INVALID") from error
    if prompt_path.is_symlink() or hashlib.sha256(prompt).hexdigest() != prompt_digest:
        raise RuntimeError("PROVIDER_PROMPT_DIGEST_INVALID")
    return Profile(
        cast(str, api["model"]),
        ENDPOINT,
        cast(str, api["reasoning_effort"]),
        cast(int, api["max_output_tokens"]),
        prompt_path,
        cast(str, lock["execution_ref"]),
    )


def release_digest(path: Path) -> str:
    try:
        raw = path.read_bytes()
        release = _mapping(json.loads(raw))
    except (OSError, ValueError) as error:
        raise RuntimeError("PROVIDER_RELEASE_INVALID") from error
    if release != {
        "capabilities": ["INFERENCE"],
        "owner": "deep-screening",
        "schema_version": 1,
        "task": "SENSOR_SURFACE",
    }:
        raise RuntimeError("PROVIDER_RELEASE_INVALID")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def read_api_key(path: Path) -> str:
    try:
        lines = [
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
    except OSError as error:
        raise RuntimeError("PROVIDER_CREDENTIAL_UNREADABLE") from error
    if len(lines) != 1 or not lines[0].startswith("OPENAI_API_KEY="):
        raise RuntimeError("PROVIDER_CREDENTIAL_UNREADABLE")
    key = lines[0].split("=", 1)[1].strip().strip("'\"")
    if (
        not key
        or key in PLACEHOLDERS
        or len(key) < 20
        or any(item.isspace() for item in key)
    ):
        raise RuntimeError("PROVIDER_CREDENTIAL_UNREADABLE")
    return key


@dataclass(frozen=True, slots=True)
class Settings:
    profile: Profile
    release_digest: str
    prompt: str
    api_key: str = field(repr=False)
    timeout: float = 180

    @classmethod
    def environment(cls) -> Settings:
        lock = Path(
            os.environ.get("AELEV_PROVIDER_LOCK_PATH", str(ROOT / "provider.lock.json"))
        )
        prompts = Path(
            os.environ.get("AELEV_PROVIDER_PROMPT_ROOT", str(ROOT / "prompts"))
        )
        release = Path(
            os.environ.get("AELEV_PROVIDER_RELEASE_PATH", str(ROOT / "release.json"))
        )
        profile = read_profile(lock, prompts)
        timeout = float(os.environ.get("AELEV_PROVIDER_TIMEOUT_SECONDS", "180"))
        if not 0 < timeout <= 240:
            raise RuntimeError("PROVIDER_DEADLINE_INVALID")
        key_file = Path(
            os.environ.get(
                "OPENAI_API_KEY_FILE", "/run/secrets/provider/credential.env"
            )
        )
        return cls(
            profile,
            release_digest(release),
            profile.prompt_path.read_text(encoding="utf-8"),
            read_api_key(key_file),
            timeout,
        )


class Engine:
    def __init__(
        self, settings: Settings, transport: httpx.BaseTransport | None = None
    ) -> None:
        self.settings = settings
        self._lock = threading.Lock()
        self._client = httpx.Client(trust_env=False, transport=transport)

    def close(self) -> None:
        self._client.close()

    def infer(self, model_input: dict[str, Any]) -> dict[str, object]:
        payload = {
            "model": self.settings.profile.model,
            "instructions": self.settings.prompt,
            "input": [
                {
                    "role": "user",
                    "content": content_parts(model_input),
                }
            ],
            "reasoning": {"effort": self.settings.profile.reasoning_effort},
            "max_output_tokens": self.settings.profile.max_output_tokens,
            "store": False,
            "text": {"format": OUTPUT_FORMAT},
        }
        if not self._lock.acquire(blocking=False):
            raise ProviderUnavailable("PROVIDER_BUSY")
        try:
            result = self._client.post(
                self.settings.profile.endpoint,
                headers={"Authorization": f"Bearer {self.settings.api_key}"},
                json=payload,
                timeout=self.settings.timeout,
            )
        except httpx.TimeoutException as error:
            raise ProviderUnavailable("PROVIDER_DEADLINE_EXCEEDED") from error
        except httpx.HTTPError as error:
            raise ProviderUnavailable("PROVIDER_RUNTIME_UNAVAILABLE") from error
        finally:
            self._lock.release()
        if result.status_code in {401, 403, 429} or result.status_code >= 500:
            raise ProviderUnavailable("PROVIDER_RUNTIME_UNAVAILABLE")
        if result.status_code != 200:
            raise ProviderUnavailable("PROVIDER_RUNTIME_RESPONSE_INVALID")
        try:
            value = _mapping(result.json())
            if value.get("status") == "incomplete":
                raise ProviderUnavailable("PROVIDER_OUTPUT_LIMIT_EXCEEDED")
            if (
                value.get("status") != "completed"
                or value.get("model") != self.settings.profile.model
                or not isinstance(value.get("output"), list)
            ):
                raise ProviderUnavailable("PROVIDER_RUNTIME_RESPONSE_INVALID")
            texts: list[str] = []
            for raw_item in cast(list[object], value["output"]):
                item = _mapping(raw_item)
                if item.get("type") == "reasoning":
                    continue
                if (
                    item.get("type") != "message"
                    or item.get("status") != "completed"
                    or not isinstance(item.get("content"), list)
                ):
                    raise ProviderUnavailable("PROVIDER_RUNTIME_RESPONSE_INVALID")
                for raw_content in cast(list[object], item["content"]):
                    content = _mapping(raw_content)
                    if content.get("type") != "output_text" or not isinstance(
                        content.get("text"), str
                    ):
                        raise ProviderUnavailable("PROVIDER_RUNTIME_RESPONSE_INVALID")
                    texts.append(cast(str, content["text"]))
            if len(texts) != 1:
                raise ProviderUnavailable("PROVIDER_RUNTIME_RESPONSE_INVALID")
            return validate_output(json.loads(texts[0]))
        except (ValueError, RuntimeError) as error:
            if isinstance(error, ProviderUnavailable):
                raise
            raise ProviderUnavailable("PROVIDER_RUNTIME_RESPONSE_INVALID") from error
