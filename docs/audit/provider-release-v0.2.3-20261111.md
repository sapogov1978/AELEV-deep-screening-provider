# Deep provider v0.2.3: exact-image component verification

The signed release adds exact client SPIFFE authorization and renewable leaf/CA
contexts. Wrong clients cannot dispatch buffered HTTP bytes. Identity withdrawal
blocks new requests; the readiness marker expires after five seconds.

- Image: `ghcr.io/sapogov1978/aelev-deep-screening-provider@sha256:7f831b76c10938a2001ad26d7f43b51785e31a330c378aa8d77866c04677d10c`.
- Source: `a3f07764a05bec63e02dc4253c5c9734e9ba4935`; successful main audit `42966540584`, release `42968878563`.
- Native manifests, signatures, source provenance and SBOM: AMD64 and ARM64.
- Linux suite: 70 passed; the one image-health skip was exercised separately and passed.
- Exact-image live requests: 2; each returned HTTP 200.

| Retained real-material case | Result |
| --- | --- |
| real-collected-queue-site-surface | SUITABLE |
| real-media-data-csv | SUITABLE |

The semantic review checks supplied source content and per-document URL/digest
binding. Complete prior component coverage is recorded for [v0.2.2](provider-release-v0.2.2-20261111.md).
The inference/application, prompt, descriptor and dependency bytes are unchanged;
the [machine-readable report](provider-release-v0.2.3-20261111.json) retains the exact comparison hashes.
The raw request and response JSON content remains at `/private/var/tmp/aelev-production-admission.wDuzQd/deep-v023/deep-screening-quality.json`. These are frozen
component replays, not fresh working-queue or current-policy processing.

Both native security reports pass the reviewed restricted runtime profile. Each
raw scan still contains one CRITICAL and 35 HIGH package findings; the specific
conditions are assessed as not affected in this execution profile. This is not a
claim that the distribution packages are patched or suitable for arbitrary CLI
use. Any unreviewed HIGH/CRITICAL or changed reviewed source blocks admission.

Anonymous clients and a wrong exact identity from the same CA were rejected by
the released image. Rotation, CA replacement, stale delivery and withdrawal
were exercised with real TLS in Linux source tests. Native issuer operation and
permanent deployment identities remain separate gates. Established TLS sessions
are not reverified against a changed CA; see [ADR-0001](../adr/0001-tls-identity-lifecycle.md).

The first staging attempt failed before serving startup and made no inference.
The successful attempt's cleanup hit Docker's asynchronous auto-removal race;
its original receipt is retained, cleanup was independently reconciled, and no
paid POST was repeated. All 138 pre-existing containers retained their image,
start, restart count and mounts. No working runtime switch or RESUME occurred.

Functional-owner scope admission, permanent identities and grants, deployed
collection/workers and clean-checkout platform E2E remain required.
