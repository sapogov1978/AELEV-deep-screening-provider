# Local readiness correction — 2026-11-10

The signed v0.1.0 image was started with the tracked placeholder credential and
`--network none`. Its operator health endpoint returned HTTP 503 with
`PROVIDER_CREDENTIAL_UNREADABLE`, while the TCP-only Docker probe reported
`healthy`. This reproduced a false-positive readiness signal without a real
key, upstream traffic or a paid inference request.

The replacement image-owned `healthcheck` command requires the serving
process's initialized inference flag, the live process and the bound local
port. The process records readiness atomically and clears the record on startup
and shutdown. Blocked initialization records false. The health CLI does not
initialize inference, read a key or call OpenAI.

Local verification passed 18 unit/contract tests, Ruff, Pyright, lock integrity
and a runtime image build. The opt-in
[image regression](../../test/test_image_health.py) then ran the built image
with only the repository placeholder, no network, a read-only root filesystem
and no Linux capabilities. It required Docker `unhealthy` and HTTP 503 together;
both assertions passed within the 50-second bound. The test container was
removed. CI now executes the same regression after building the runtime image.

This fixes local process/configuration readiness. It does not turn the probe
into an upstream availability, quota or semantic-quality check. Those require
bounded evaluation against the exact signed release digest.
