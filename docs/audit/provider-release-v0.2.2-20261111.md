# Deep provider v0.2.2 — exact-release component verification

Image: `ghcr.io/sapogov1978/aelev-deep-screening-provider@sha256:0a15ed0d7f91889cb50f95e2859d18e8829bc6f47be334b4b4bed9169a251a3b`.
Source: `b783bc53406aa4c5a1d04d941259ffa8bce57eac`.

The exact native arm64 image passed 7 bounded live API cases. Codex
separately reviewed every actual output against the supplied material and
expected meaning. Frozen retained real queue material and policy, replayed through isolated mTLS; seven real HTML/binary cases, binary files supplied by evaluator. Not deployed owner collection, queue processing, or cascade E2E.

The [machine report](provider-release-v0.2.2-20261111.json) binds the frozen corpus, complete opaque
request/response hashes, native image, security scans and supply-chain receipts.
Raw exchanges remain outside Git at `/var/tmp/aelev-production-admission.wDuzQd/deep-v022/deep-screening-quality.json`.

Cosign verified the exact tag workflow identity and GitHub OIDC issuer. Both
amd64 and arm64 have SPDX SBOMs and SLSA provenance matching the source above.
Source audit [42924970779](https://github.com/sapogov1978/AELEV-deep-screening-provider/actions/runs/42924970779)
and release [42925400304](https://github.com/sapogov1978/AELEV-deep-screening-provider/actions/runs/42925400304) passed.

Both native architectures passed the [scoped security review](runtime-security-20261111.md).
Each raw scan retains **1 CRITICAL and 35 HIGH** package findings. Individual
applicability decisions admit only the reviewed default opaque entrypoint with
UID 10001, read-only root, no effective capabilities, no-new-privileges and an
empty fstab. This is not a claim that those OS packages are patched. The owner
must verify the same profile at deployment; an unknown HIGH/CRITICAL blocks.

Retained HTML returned SUITABLE; withheld evidence returned REVIEW. Both static
PDFs returned REVIEW. CSV, XLSX and PNG returned SUITABLE, with correct observed
row counts, workbook source references and chart meaning. URL/digest bindings
were validated independently; literal workbook references are not claimed as
fetched pages. Description fields are capped at 160 characters, and some final
clauses truncate; supporting observations and access-point identities remain
intact. This is not proof of numeric extraction, complete rows/charts, every
language, deployed owner collection or complete site coverage.

Anonymous TLS and a wrong release digest were rejected. Temporary containers
were removed; no queue command or RESUME was issued. Functional-owner binary
collection, policy-scope admission, permanent identities and owner-worker E2E
remain open.
