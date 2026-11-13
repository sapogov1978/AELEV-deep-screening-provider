# AELEV Deep Screening Provider specification

## Responsibility

The provider owns the remote API choice, model lock, prompt, credential,
structured-output schema, response validation and image healthcheck. Deep
Screening owns research collection, queueing, retries, decisions, evidence,
admission, UI, storage and Kafka publication.

## Opaque port

`GET /v1/status` and `POST /v1/infer` implement schema version 1 for owner
`deep-screening`, task `SENSOR_SURFACE`, capability `INFERENCE` and the exact
SHA-256 digest of [release.json](release.json). Requests and responses use the
envelope in [contracts/opaque-compute-v1.json](contracts/opaque-compute-v1.json).
No provider, model, prompt, upstream body or credential is disclosed.

The port additionally requires exact SPIFFE peer authorization and renewable
TLS material under [ADR-0001](docs/adr/0001-tls-identity-lifecycle.md). A trusted
CA alone is insufficient. An unauthorized connection cannot dispatch buffered
HTTP bytes. Production consumes fresh `spire-file-v1` output, replaces leaf
and CA contexts for new handshakes and blocks stale, changed or withdrawn
material. Subsequent requests on existing sessions also require current
owned identity and an unexpired exact client identity. Under
[ADR-0002](docs/adr/0002-session-trust-lifecycle.md), every dispatch also requires
the exact current SSLContext used by that connection's completed handshake.
CA/SVID replacement therefore blocks an old keep-alive request with 503 and
Connection: close before inference; in-flight inference retains its deadline.

Inference output contains `decision` (`SUITABLE`, `UNSUITABLE` or `REVIEW`),
bounded candidate groups, exact evidence URLs/digests and `unknown_scope`.
Deep Screening revalidates every location against its own collected evidence
and remains the only component allowed to apply that result.

## OpenAI execution

### Bounded document bytes

Existing text-only `documents` remain compatible. A binary document supplies
`content_type`, `content_base64`, `content_digest` and its observed HTTP(S) `url`
alongside the ordinary document metadata. This is source evidence, not an API
model setting. No provider-specific fields are added to the opaque envelope.

The provider accepts PDF; CSV/TSV and XLS/XLSX spreadsheets; PNG, JPEG and WebP
images. Limits are eight documents, 524288 decoded bytes per attachment and
524288 decoded bytes across attachments, within the existing 1 MiB input limit.
Invalid base64, unsupported media, missing bytes and digest mismatches return
422 before any API call. The owner remains responsible for safe collection,
coverage accounting, exact-target authorization and its canonical snapshots.

Supplied bytes are sent inline as file/image content parts, with exact URL and
digest binding immediately before each attachment. Base64 is removed from the
text metadata. The provider never uses upstream `file_url`, persistent Files
uploads or a provider-side source fetch. PDF page images and ordinary images use
high detail under the locked `bounded-document-content-v2` profile.

Spreadsheet input does not establish review of embedded charts or every row;
the v2 prompt requires explicit unknown scope for unobserved content. Transport
unit fixtures do not establish semantic quality. The exact released image must
pass a separate real-material multimedia evaluation before owner admission.

Official API behavior: [file inputs](https://developers.openai.com/api/docs/guides/file-inputs)
and [image inputs](https://developers.openai.com/api/docs/guides/images-vision).

### Locked request

[provider.lock.json](provider.lock.json) pins the Responses endpoint, model,
reasoning effort, output budget, `store=false`, exact prompt digest and direct
HTTPS transport. Each call is a stateless, buffered request with no tools,
streaming, background mode or stored-response chaining. Input material is data,
not instructions. Only one strict structured-output object is accepted.

`store=false` requests stateless API behavior; it is not a claim that the
OpenAI project has Zero Data Retention or a particular data residency setting.
Those account-level properties remain admission gates.

## Readiness and release

Security admission uses the [reviewed runtime profile](security/runtime-profile.json)
and [current TLS review](docs/audit/runtime-security-20261113.md), retaining
the earlier [CVE-specific evidence](docs/audit/runtime-security-20261111.md). It is scoped
to the default opaque entrypoint under non-root, read-only, no-capabilities and
no-new-privileges conditions. The owner verifies those conditions at deployment.
Any changed reviewed source/dependency or unreviewed HIGH/CRITICAL blocks the
gate. Release signing requires the exact successful main audit and a scan of
the actual published native digest; raw findings and decisions are retained.

The runtime uses the same Python 3.13.7 Debian Bookworm base as the builder,
but copies only the locked application environment. Poetry, its build-only
dependencies, pip and setuptools are excluded from runtime. Build and test
stages continue to use pinned Poetry 2.2.1.
The unused distribution SQLite library is excluded from runtime. The opaque
provider has no SQL interface or durable database; owner storage is independent.

One upstream inference is active at a time. An overlapping inference returns
HTTP 503 `PROVIDER_BUSY` immediately without a second API call or an internal
waiting queue. The functional owner retains retry responsibility. Timeouts and
transport failures release the capacity for subsequent requests.

Local readiness validates immutable configuration and a non-placeholder secret
without performing a billable upstream probe. Docker healthcheck requires the
serving process's initialized inference state, a live process and the bound
local port; a listening port with blocked configuration is unhealthy. Its
readiness requires current TLS identity and a producer marker no older than
five seconds. The marker is cleared at startup and shutdown, and the health CLI never
initializes inference or reads a key. Provider quota, model access and
semantic quality require a bounded live evaluation. Production use additionally
requires an immutable signed image digest, SBOM, provenance, mTLS identities and
an explicit Deep Screening quality-admission decision.
