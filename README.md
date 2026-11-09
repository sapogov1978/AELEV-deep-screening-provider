# AELEV Deep Screening Provider

Independent black-box implementation of the Deep Screening
`SENSOR_SURFACE` compute contract. The image receives owner-collected site
material over mutually authenticated HTTPS and calls the OpenAI Responses API.
Model ID, prompt and credential remain provider-owned and never cross the
opaque port.

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
