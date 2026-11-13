# Scoped TLS runtime review — 2026-11-13

This review binds the corrected mTLS source in runtime-profile.json. It keeps
Python 3.13.7, Debian Bookworm, application/model/prompt locks and the existing
opaque owner/task contract. Earlier signed-release receipts do not admit this
new source automatically. Raw findings and each exact-image scan are retained.

The conditions and eleven CVE/package-specific decisions from the
[previous review](runtime-security-20261111.md) remain mandatory: UID 10001,
read-only root, no capabilities, no-new-privileges, no process/dynamic native
execution, absent MiniZip/systemd-homed/Archive::Tar and unavailable affected
CLI/native paths. No new vulnerability suppression is added. Unknown
HIGH/CRITICAL, changed reviewed sources/locks, absent probes or missing
controls block signing. Source hashes bind both gate tools as well as runtime.

[ADR-0002](../adr/0002-session-trust-lifecycle.md) closes existing-session
admission after a trust change. Each HTTP request requires the exact current
handshake context and peer identity. Original callback context stays strongly
referenced by the listener configuration. Production still requires fresh
SPIRE delivery, independent keys, hostname validation and routable endpoints.
The provider's empty local TLS mount has UID/GID 10001 and mode 0700; no
issuer key, foreign credentials or shared-volume transport is introduced.

Additional CPython TLS conditions were reviewed against the primary
[3.13.16](https://www.python.org/downloads/release/python-31316/) and
[3.13.18](https://www.python.org/downloads/release/python-31318/) advisories:

| Advisory | Reviewed condition and required evidence |
|---|---|
| CVE-2026-19445 | The original SNI callback context remains alive for the listener lifetime, following the [upstream mitigation](https://github.com/python/cpython/issues/156293). A real TLS 1.3 HRR/GC/renewal regression verifies HRR bytes and context lifetime. This is a mitigation, not an installed CPython patch. |
| CVE-2026-19553 | verified_self uses fixed literal server/client roles, no session and no hostname in its local in-memory handshake. Network server role and upstream locked hostname are fixed; opaque input never supplies TLS arguments. |
| CVE-2026-115557 | Both effective system and HTTPX/certifi trust bundles must exclude the four affected DER root fingerprints. The native gate records bundle hashes and requires known_compromised_ca_roots_absent. The [primary root list](https://emudhra.we-have-a-problem.com/roots.json) and [certifi removal release](https://github.com/certifi/python-certifi/releases/tag/2026.10.19) define the scope. |

This is a source review, not a clean CVE claim, exact release receipt, live
quality decision or platform/site admission. Both native architectures and
current signed-image controls must be checked before owner admission.
