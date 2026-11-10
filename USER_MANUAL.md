# Operator manual

## Secret

Copy `.env.local.example` to `.env.local` and replace the placeholder locally.
Never paste the key into chat or commit the file. Runtime mounts that file
read-only at `/run/secrets/provider/credential.env`; it must contain exactly one
`OPENAI_API_KEY=...` assignment.

The key is exclusive to this provider. It must not be shared with the Advance
Screening or Translation providers.

## Runtime

The image listens on port `18486`. By default it requires server files
`server.crt`, `server.key` and `client-ca.crt` under
`/run/secrets/model-module`. `AELEV_PROVIDER_INSECURE_HTTP=1` is accepted
only for an explicit local test outside production.

`python -m aelev_deep_screening_provider verify-config` validates the lock,
prompt and release descriptor without reading a key or using the network.
`print-release-digest` prints the exact digest to place in the owner connection
configuration.

## Admission

For multimedia evaluation, collect and retain the source bytes under the
functional owner's budgets, then supply their exact URL, MIME type, base64 and
SHA-256. The provider accepts at most 512 KiB per attachment and 512 KiB total;
the whole input remains bounded to 1 MiB. Rejected media must remain visible as
unknown or blocked scope; do not relabel a text-only projection as image/PDF
understanding. The v0.2.1 candidate's transport tests use synthetic bytes and
do not close the live multimedia quality gate.

A healthy process proves only local configuration. Before selecting the release
digest in Deep Screening, run representative sensor-surface evals with the exact
image/model/prompt, review evidence-binding failures and record the admission
decision. Changing the model, prompt or execution profile requires a new
provider release and evaluation. Rollback replaces only the provider image and
release digest; it never clears the Deep Screening queue or implies `RESUME`.
