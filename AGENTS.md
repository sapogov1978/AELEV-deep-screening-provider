# Repository Instructions

Read `README.md`, `SPEC.md`, `USER_MANUAL.md`, the accepted ADRs, `release.json`,
the opaque contract and `provider.lock.json` before editing. This repository owns
the Deep Screening inference implementation, prompt, OpenAI credential and
image healthcheck. It never owns the Deep Screening queue, storage, policy,
site collection, operator controls, UI or Kafka contracts.

Use `apply_patch` for manual edits, update `CHANGELOG.md`, preserve the opaque
owner/task contract and never commit secrets or runtime data. Build does not
start containers or call OpenAI. Release only immutable digest-pinned images
with SBOM, provenance and signature.
