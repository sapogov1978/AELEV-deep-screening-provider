"""Transport conformance fixtures; these are not live semantic quality evidence."""

from __future__ import annotations

import base64
import copy
import hashlib
import json

import httpx
import pytest
from test_provider import OUTPUT, api_response, settings

from aelev_deep_screening_provider.contract import RequestInvalid
from aelev_deep_screening_provider.engine import Engine
from aelev_deep_screening_provider.media import (
    MAX_DOCUMENT_BYTES,
    MAX_TOTAL_DOCUMENT_BYTES,
    content_parts,
)


def document(
    content_type: str, body: bytes = b"bounded fixture bytes"
) -> dict[str, object]:
    return {
        "url": "https://example.test/material",
        "status": 200,
        "content_type": content_type,
        "content_digest": "sha256:" + hashlib.sha256(body).hexdigest(),
        "content_base64": base64.b64encode(body).decode(),
        "text": "",
        "links": [],
    }


@pytest.mark.parametrize(
    ("content_type", "extension"),
    [
        ("application/pdf", ".pdf"),
        ("text/csv", ".csv"),
        ("text/tab-separated-values", ".tsv"),
        ("application/vnd.ms-excel", ".xls"),
        ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".xlsx"),
    ],
)
def test_supplied_files_are_bound_to_metadata_and_not_tokenized_as_base64(
    content_type: str, extension: str
) -> None:
    attachment = document(content_type)
    original = {"schema_version": 1, "documents": [attachment]}
    before = copy.deepcopy(original)
    parts = content_parts(original)
    assert original == before
    metadata = json.loads(str(parts[0]["text"]))
    assert "content_base64" not in metadata["documents"][0]
    assert metadata["documents"][0]["content_digest"] == attachment["content_digest"]
    binding = json.loads(str(parts[1]["text"]))
    assert binding["url"] == "https://example.test/material"
    assert binding["content_digest"] == attachment["content_digest"]
    assert (
        binding["attachment_index"] == metadata["documents"][0]["attachment_index"] == 0
    )
    assert parts[2] == {
        "type": "input_file",
        "filename": "document-0" + extension,
        "file_data": "data:"
        + content_type
        + ";base64,"
        + str(attachment["content_base64"]),
        **({"detail": "high"} if extension == ".pdf" else {}),
    }


@pytest.mark.parametrize("content_type", ["image/png", "image/jpeg", "image/webp"])
def test_images_use_inline_bytes_without_upstream_url_fetch(content_type: str) -> None:
    image = document(content_type)
    parts = content_parts({"documents": [image]})
    assert parts[2] == {
        "type": "input_image",
        "image_url": "data:" + content_type + ";base64," + str(image["content_base64"]),
        "detail": "high",
    }
    assert all("file_url" not in part and "file_id" not in part for part in parts)


@pytest.mark.parametrize(
    "changes",
    [
        {"content_digest": "sha256:" + "0" * 64},
        {"content_base64": "not base64!"},
        {"content_base64": None},
        {"content_base64": ""},
        {"content_type": "application/zip"},
        {"url": "file:///etc/passwd"},
        {"url": "https://user:password@example.test/material"},
        {"url": "https://example.test/material#unbound-fragment"},
        {"url": "https://[invalid-address"},
    ],
)
def test_invalid_attachment_is_rejected_before_api_call(
    changes: dict[str, object],
) -> None:
    def unexpected(_request: httpx.Request) -> httpx.Response:
        pytest.fail("An invalid attachment must not reach the billable API")

    engine = Engine(settings(), httpx.MockTransport(unexpected))
    try:
        with pytest.raises(RequestInvalid):
            engine.infer({"documents": [{**document("application/pdf"), **changes}]})
    finally:
        engine.close()


def test_missing_binary_document_bytes_are_not_silently_omitted() -> None:
    missing = document("image/png")
    del missing["content_base64"]
    with pytest.raises(RequestInvalid):
        content_parts({"documents": [missing]})


def test_individual_decoded_byte_budget() -> None:
    with pytest.raises(RequestInvalid):
        content_parts(
            {
                "documents": [
                    document("application/pdf", b"x" * (MAX_DOCUMENT_BYTES + 1))
                ]
            }
        )


def test_one_document_can_use_the_shared_budget_without_raising_total_capacity() -> (
    None
):
    attachment = document("application/pdf", b"x" * 256_628)
    assert content_parts({"documents": [attachment]})[2]["type"] == "input_file"
    within_individual_limit = document(
        "application/pdf", b"x" * (MAX_TOTAL_DOCUMENT_BYTES // 2 + 1)
    )
    assert (
        content_parts({"documents": [within_individual_limit]})[2]["type"]
        == "input_file"
    )
    with pytest.raises(RequestInvalid, match="BUDGET_EXCEEDED"):
        content_parts({"documents": [within_individual_limit, within_individual_limit]})


def test_engine_sends_mixed_evidence_as_provider_owned_content_parts() -> None:
    payload = {
        "documents": [
            {"url": "https://example.test/", "text": "Observed page"},
            document("application/pdf"),
            document("image/png"),
        ]
    }

    def respond(request: httpx.Request) -> httpx.Response:
        value = json.loads(request.content)
        assert str(request.url) == "https://api.openai.com/v1/responses"
        assert value["store"] is False
        parts = value["input"][0]["content"]
        assert [part["type"] for part in parts] == [
            "input_text",
            "input_text",
            "input_file",
            "input_text",
            "input_image",
        ]
        assert json.loads(parts[0]["text"])["documents"][0]["text"] == "Observed page"
        assert json.loads(parts[1]["text"])["attachment_index"] == 1
        assert json.loads(parts[3]["text"])["attachment_index"] == 2
        assert value["text"]["format"]["strict"] is True
        return api_response(OUTPUT)

    engine = Engine(settings(), httpx.MockTransport(respond))
    try:
        assert engine.infer(payload) == OUTPUT
    finally:
        engine.close()
