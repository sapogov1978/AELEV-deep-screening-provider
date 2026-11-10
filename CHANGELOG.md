# Changelog

## Unreleased

- Raised the individual attachment limit to the existing 512 KiB aggregate
  budget after a real 256628-byte one-page Spanish PDF failed the initial
  128 KiB limit. The total decoded-byte budget and 1 MiB opaque input bound
  remain unchanged; the updated media profile is locked as v2.
- Return bounded HTTP 503 `PROVIDER_BUSY` for overlapping inference rather than
  queueing behind the active upstream call. HTTP and timeout tests prove a busy
  request makes no second API call and failures release provider capacity.
- Added bounded PDF, spreadsheet and image content parts behind the unchanged
  opaque compute envelope. Supplied document bytes are bound to their URL and
  SHA-256 before inference; the provider performs no document fetch or persistent
  file upload. The v2 prompt preserves attachment evidence and operator intent.

- Recorded the exact v0.1.1 signed image's native mTLS HTML replay: four collected
  pages produced evidenced access points and withheld evidence produced REVIEW.
  Multimedia and production owner admission remain separate gates.
- Fixed false-positive Docker health: a placeholder credential could previously
  return HTTP 503 while its listening TCP port made the image healthy. The
  non-billable health CLI now checks serving-process inference readiness.
- CI runs the runtime image without a network or real key and requires Docker
  unhealthy together with HTTP 503 for the repository placeholder.
- Recorded exact v0.1.0 signature, native arm64 mTLS and real collected HTML
  evidence-binding evaluation. Broader media and owner production admission
  remain explicit gates.
- Recomputed prompt, execution and neutral release digests after canonical
  single-newline file normalization.
- Created an independent OpenAI Responses API provider for the opaque Deep
  Screening `SENSOR_SURFACE` contract.
- Added an immutable provider lock, digest-pinned prompt, neutral release
  descriptor, strict structured output and bounded failures.
- Added a separate ignored API-key placeholder, mutual-TLS server defaults,
  offline tests and a non-root multi-stage image.
