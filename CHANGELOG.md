# Changelog

## Unreleased

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
