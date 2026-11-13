# Changelog

## Unreleased

- Verified signed v0.2.4: exact tag identity, per-platform SLSA/SPDX, both
  native security profiles and one actual real-material mTLS request. Recorded
  source/output hashes, unchanged inference baseline, unavailable historical
  raw paths, limited replay scope and open owner/identity/physical gates.

- Candidate 0.2.4 binds every HTTP dispatch to the actual current handshake
  context. Replacing CA/SVID blocks old keep-alive sessions before inference,
  with fresh connections accepted without a listener restart. Regression tests
  reproduce the old failure and cover TLS 1.3 HRR/GC/renewal.
- Refresh exact source/gate security bindings and require compromised CA roots
  absent from system and certifi bundles; retain raw findings and existing
  CVE-specific conditions. Model, prompt, opaque descriptor and locks are unchanged.
- Initialize the private TLS mount as UID/GID 10001, mode 0700, and verify the
  first empty volume can prepare its own material without root or capabilities.
  New signed-image, semantic-quality and owner-deployment admission remain open.

- Verified signed v0.2.3: both native security profiles, Linux TLS tests and
  two selected real-material live requests. Retained the staging/cleanup
  discrepancies and reconciled cleanup without repeating successful inference.
- Require exact client/server SPIFFE identities and fresh SPIRE delivery for
  production mTLS. Reload leaf and CA generations for new connections, block
  stale or withdrawn material and retain the existing model/dependency locks.
  Certificate inspection uses bounded in-memory OpenSSL handshakes, without
  network access, a new dependency or a private Python certificate parser.
- Verified signed v0.2.2 on both native architectures against the reviewed
  runtime profile, and reviewed all seven frozen real-material inference
  cases. Reports retain raw CVEs, bounded descriptions and unknown coverage;
  deployed owner collection, identities and worker admission remain open.
- Added source/lock/gate-bound CVE applicability evidence for the restricted
  provider entrypoint. Raw findings remain visible; unknown HIGH/CRITICAL,
  changed reviewed code/dependencies and missing controls block admission.
- Release signing now requires the exact main source audit and a native amd64
  scan of the published digest followed by the scoped security gate. Runtime
  profile evidence is retained as a release-workflow artifact.
- Added an immutable-image runtime probe and CI receipt for both Python
  environments, absent build tools/SQLite, MiniZip and systemd-homed. It runs
  without network or credentials and does not claim complete CVE admission.
- Removed the unused distribution SQLite library from runtime after a dry-run
  proved it has no dependent package removals. The provider exposes no SQL;
  functional-owner storage, queues and application locks are unaffected.
- Release builds refresh the OS-update stage instead of reusing its cache;
  image builds assert build tools are absent from both Python environments.
- Recorded seven real-material v0.2.1 inference calls with semantic review for
  HTML, missing evidence, PDF, CSV, XLSX, PNG and Spanish PDF. Preserved the
  initial harness failure and verified the XLSX URL directly in its source
  bytes. Exact-image security scanning blocks production admission.
- Isolated the runtime from the Poetry builder after exact-image scanning
  found vulnerable build-only tools in the published image. The Python/OS and
  application dependency locks are unchanged; global and virtualenv installers
  are removed from the runtime. Distribution vulnerability admission remains open.
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
