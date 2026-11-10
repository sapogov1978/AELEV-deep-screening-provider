# Bounded provider evaluation — 2026-11-10

Exact image:
`ghcr.io/sapogov1978/aelev-deep-screening-provider@sha256:f8c1d79e1442bee71e588dd6ecdc67d34c992e3a42f58b4ac42ce2f8309e496f`.
Artifact source: `0400ee14bfd106130fcce9eea0a610fc4f1dadbd`.

The existing `v0.1.0` image passed native arm64 mTLS replay of actual public
documents collected for a real Advance queue job. The same target had already
been delivered to Deep intake. This replay is a provider test, not execution of
the Deep worker or a full inter-service E2E.

With four real HTML document projections, the provider returned SUITABLE and
two supported access points. Every returned URL and content digest matched
the supplied collection. Codex reviewed the locations and unknown-scope
statement against the input. With all documents withheld, it returned REVIEW,
no candidates and an explicit absence-of-evidence explanation. Both calls
returned HTTP 200. Anonymous TLS failed; a wrong release digest returned 422
before inference. Test containers were stopped and removed.

Cosign 3.1.4 verified the image's keyless signature, certificate chain and
transparency-log claims for issuer `https://token.actions.githubusercontent.com`
and exact workflow identity
`https://github.com/sapogov1978/AELEV-deep-screening-provider/.github/workflows/release.yml@refs/tags/v0.1.0`.
The multi-platform index contains amd64 and arm64 plus BuildKit attestations;
SLSA provenance and SPDX SBOM are available for both. Source audit `42710912382` and image
publication `42711205625` passed; local source checks passed six tests, Ruff
and Pyright.

[Hash-only evidence](provider-quality-20261110.json) binds input/output hashes,
the exact image and real queue identity. Raw exchanges remain outside Git at
the path in that report. No credential or runtime database is included.

## Admission boundary

The evaluated media scope is HTML. PDF, spreadsheets, images and multilingual
material have not been admitted by this evaluation. Permanent owner mTLS
identities, independent representative quality, timeout/recovery behavior and
the full owner-worker E2E remain required. The functional owner must separately
admit the exact release; test certificates and a successful provider call do
not establish full platform production readiness. No queue RESUME was issued.
