# Deep provider v0.2.1 — real-material candidate evaluation

Image: `ghcr.io/sapogov1978/aelev-deep-screening-provider@sha256:922bf3fbb4e2e944fdf1eebf93bef12d1dccaf3e1e41fdd30433e1869cabc2d2`.
Source: `6e5cde6f57bfe1f7278fd93f3b240d8469e88bb5`.

Seven real-material calls were reviewed on the exact native arm64 image through
isolated mTLS. The corpus and expected decisions were frozen before inference.

| Material | Observed decision | Content review |
|---|---|---|
| Four retained queue HTML pages | SUITABLE | Supported observed access points and exact digests |
| Same target, no documents | REVIEW | No fabricated locations |
| Public two-page definitions PDF | REVIEW | Variable definitions distinguished from observed series values |
| Public CSV | SUITABLE | Quarterly records and date range recognized; projection limits explicit |
| Public XLSX | SUITABLE | Figure data and a literal Data_Sources reference recognized |
| Public PNG | SUITABLE | Viewed chart metric and time axis correctly described |
| Public one-page Spanish PDF | REVIEW | Spanish advice brochure identified; no unsupported observation source claimed |

The accepted queue target and retained instruction were reused. Binary files
were supplied by the evaluator, not collected by the deployed Deep worker.
Two static PDFs allowed SUITABLE or REVIEW before execution; both conservatively
returned REVIEW. CSV, XLSX and PNG required SUITABLE. Empty evidence required
REVIEW. This is bounded content understanding, not proof of numeric extraction
accuracy, all languages or complete site coverage.

The initial harness stopped on XLSX because it counted only separately
projected links. The response's G.17 URL was then verified literally in the
digest-bound workbook's Data_Sources XML. Offline revalidation admits only
exact-target URLs actually present in that attachment and tied to its digest.
The original failed receipt is preserved; neither input nor expected decisions
were changed. Only the two unexecuted cases were sent in a supplementary run.

The [machine report](provider-evaluation-v0.2.1-20261110.json) records all seven
request/response hashes, semantic reviews, source audit, release provenance,
signature, both platform SBOMs, and hashes of raw receipts outside Git.
Anonymous TLS and wrong-release requests were rejected in both test runs.
Both temporary containers were removed; no queue command or RESUME was issued.

**Production admission is blocked.** Trivy 0.76.1 with its November 10 database
reported 2 CRITICAL and 49 HIGH findings in this candidate. Runtime hardening
is a subsequent change requiring its own exact-image verification. Permanent
identities, functional-owner binary collection and deployed worker E2E remain
open. No GitHub release page is published for this candidate.
