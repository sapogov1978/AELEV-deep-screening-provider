# AELEV Deep Screening Provider

Independent black-box implementation of the Deep Screening
`SENSOR_SURFACE` compute contract. The image receives owner-collected site
material over mutually authenticated HTTPS and calls the OpenAI Responses API.
Model ID, prompt and credential remain provider-owned and never cross the
opaque port.

Release [v0.2.4](docs/audit/provider-release-v0.2.4-20261113.md) closes
existing-session admission after CA/SVID replacement under ADR-0002. Signatures,
both native security profiles and one selected actual real-material replay are
verified. Permanent identities, owner/current-scope and physical E2E remain open.

Release [v0.2.3](docs/audit/provider-release-v0.2.3-20261111.md) adds exact client SPIFFE authorization and renewable TLS
generations under [ADR-0001](docs/adr/0001-tls-identity-lifecycle.md). Local
real-TLS tests cover wrong identities, buffered unauthorized requests,
renewal, replacement CA and withdrawal; they do not call OpenAI or grant
deployment admission. Model, prompt and dependency locks are unchanged.

The exact signed image also passed two selected live regression requests
with retained real material, and rejected anonymous and same-CA foreign peers.
This bounded transport evidence is separate from current-policy owner admission.

The v0.2.2 release accepts bounded owner-supplied PDF, spreadsheet and image
bytes through that port. It verifies their SHA-256, binds them to the supplied
document URL, and creates provider-owned inline content parts. It does not fetch
source URLs or persistently upload files. Its bounded real-material
[evaluation](docs/audit/provider-release-v0.2.2-20261111.md) passed content
review and the restricted security profile on both native architectures.
Deployed owner collection, policy-scope admission and permanent identities
remain separate gates.

The initial lock selects `gpt-6.1-sol`, medium reasoning, `store=false` and a
strict JSON schema. The neutral [release.json](release.json) intentionally
contains no provider identity. It is not quality-admitted until a representative
bounded evaluation is reviewed.

Offline verification requires no API key:

```sh
poetry install
poetry run ruff check .
poetry run ruff format --check .
poetry run pyright
poetry run pytest -q
PYTHONPATH=src poetry run python -m aelev_deep_screening_provider verify-config
docker build --target test .
docker build --target runtime .
```

Copy `.env.local.example` to the ignored `.env.local` only when an operator is
ready to supply this provider's own key. A placeholder starts no billable API
request and is reported as a blocked local readiness condition.
