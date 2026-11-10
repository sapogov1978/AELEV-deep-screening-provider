"""Bounded owner documents mapped to provider-owned Responses content parts."""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
from typing import Any, cast
from urllib.parse import urlsplit

from .contract import RequestInvalid

MAX_DOCUMENT_BYTES = 131_072
MAX_TOTAL_DOCUMENT_BYTES = 524_288
MAX_DOCUMENTS = 8
FILE_TYPES = {
    "application/pdf": ".pdf",
    "text/csv": ".csv",
    "text/tab-separated-values": ".tsv",
    "application/vnd.ms-excel": ".xls",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
}
IMAGE_TYPES = {"image/png", "image/jpeg", "image/webp"}


def content_parts(model_input: dict[str, Any]) -> list[dict[str, object]]:
    """Preserve legacy text input and attach verified supplied bytes only.

    No URL is downloaded and no file is uploaded to a persistent Files API.
    Binary data is removed from text metadata before tokenization.
    """
    raw_documents = model_input.get("documents", [])
    if not isinstance(raw_documents, list):
        raise RequestInvalid("DSS_PROVIDER_DOCUMENTS_INVALID")
    documents = cast(list[object], raw_documents)
    if len(documents) > MAX_DOCUMENTS:
        raise RequestInvalid("DSS_PROVIDER_DOCUMENTS_INVALID")
    projected: list[dict[str, Any]] = []
    attachments: list[dict[str, object]] = []
    total = 0
    for index, raw_document in enumerate(documents):
        if not isinstance(raw_document, dict):
            raise RequestInvalid("DSS_PROVIDER_DOCUMENT_INVALID")
        document = dict(cast(dict[str, Any], raw_document))
        content_type = (
            str(document.get("content_type", "")).split(";", 1)[0].strip().lower()
        )
        supplied_bytes = "content_base64" in document
        encoded = document.pop("content_base64", None)
        if supplied_bytes or content_type in FILE_TYPES or content_type in IMAGE_TYPES:
            body = _decode(encoded, content_type)
            total += len(body)
            if total > MAX_TOTAL_DOCUMENT_BYTES:
                raise RequestInvalid("DSS_PROVIDER_DOCUMENT_BUDGET_EXCEEDED")
            url = document.get("url")
            if not isinstance(url, str) or len(url) > 4096:
                raise RequestInvalid("DSS_PROVIDER_DOCUMENT_URL_INVALID")
            try:
                parsed = urlsplit(url)
            except ValueError as error:
                raise RequestInvalid("DSS_PROVIDER_DOCUMENT_URL_INVALID") from error
            if (
                parsed.scheme not in {"http", "https"}
                or not parsed.hostname
                or parsed.username
                or parsed.password
                or parsed.fragment
            ):
                raise RequestInvalid("DSS_PROVIDER_DOCUMENT_URL_INVALID")
            digest = "sha256:" + hashlib.sha256(body).hexdigest()
            if document.get("content_digest") != digest:
                raise RequestInvalid("DSS_PROVIDER_DOCUMENT_DIGEST_MISMATCH")
            document["attachment_index"] = index
            attachments.append(
                {
                    "type": "input_text",
                    "text": json.dumps(
                        {
                            "attachment_index": index,
                            "url": url,
                            "content_digest": digest,
                            "content_type": content_type,
                        },
                        ensure_ascii=False,
                        separators=(",", ":"),
                    ),
                }
            )
            data_url = "data:" + content_type + ";base64," + cast(str, encoded)
            if content_type in IMAGE_TYPES:
                attachments.append(
                    {"type": "input_image", "image_url": data_url, "detail": "high"}
                )
            else:
                part: dict[str, object] = {
                    "type": "input_file",
                    "filename": f"document-{index}{FILE_TYPES[content_type]}",
                    "file_data": data_url,
                }
                if content_type == "application/pdf":
                    part["detail"] = "high"
                attachments.append(part)
        projected.append(document)
    metadata = {**model_input, "documents": projected} if attachments else model_input
    return [
        {
            "type": "input_text",
            "text": json.dumps(metadata, ensure_ascii=False, separators=(",", ":")),
        },
        *attachments,
    ]


def _decode(encoded: object, content_type: str) -> bytes:
    if content_type not in FILE_TYPES and content_type not in IMAGE_TYPES:
        raise RequestInvalid("DSS_PROVIDER_DOCUMENT_TYPE_UNSUPPORTED")
    if (
        not isinstance(encoded, str)
        or not encoded
        or len(encoded) > 4 * ((MAX_DOCUMENT_BYTES + 2) // 3)
    ):
        raise RequestInvalid("DSS_PROVIDER_DOCUMENT_BYTES_INVALID")
    try:
        body = base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error) as error:
        raise RequestInvalid("DSS_PROVIDER_DOCUMENT_BYTES_INVALID") from error
    if not body or len(body) > MAX_DOCUMENT_BYTES:
        raise RequestInvalid("DSS_PROVIDER_DOCUMENT_BYTES_INVALID")
    return body
