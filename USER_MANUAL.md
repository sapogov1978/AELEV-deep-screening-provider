# Operator manual

## Secret

Copy `.env.local.example` to `.env.local` and replace the placeholder locally.
Never paste the key into chat or commit the file. Runtime mounts that file
read-only at `/run/secrets/provider/credential.env`; it must contain exactly one
`OPENAI_API_KEY=...` assignment.

The key is exclusive to this provider. It must not be shared with the Advance
Screening or Translation providers.

## Runtime

The image listens on port `18486`. Its read-only TLS root is
`/run/secrets/model-module`. Supply `identity.json` with exactly:

```json
{
  "schema_version": 1,
  "environment": "production",
  "delivery": "spire-file-v1",
  "server_spiffe_id": "spiffe://identity.example/deep-screening/compute/installation",
  "client_spiffe_id": "spiffe://identity.example/deep-screening/control/installation"
}
```

Replace both exact identities with approved owner values. Mount only the
public file-delivery result of the corresponding SPIRE agent at the TLS root,
and the owner policy read-only as `identity.json` within that root. The agent
provides `current.json`, `generations/<generation>/tls.pem` (mode 0600) and
`bundle.pem`; no bootstrap, agent state or issuer key is mounted. Stale,
withdrawn, changed or unavailable delivery blocks new requests without reuse
of the previous generation.

An explicitly local/test policy may select `pem-files-v1` with `server.crt`,
`server.key` (mode 0600) and `client-ca.crt`; this layout assumes the same
approved authority for server and client. It is forbidden for production.
`AELEV_PROVIDER_INSECURE_HTTP=1` remains only an explicit local test override,
forbidden by the production image/admission profile.

Leaf/CA generations reload without restarting the provider. A connection
established with replaced material cannot dispatch another request; the worker
must establish a fresh authenticated connection. This does not cancel an
inference that was dispatched before the change. The image initializes its
empty private TLS mount as UID/GID 10001, mode 0700; no root initializer or
shared worker volume is required. Changing policy
or expected identities requires a controlled deployment and renewed owner
admission. The healthcheck requires a live readiness observer, initialized
inference and current identity. See the complete
[identity lifecycle contract](docs/adr/0001-tls-identity-lifecycle.md).

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
understanding. Release v0.2.2 has a separately reviewed seven-case
[real-material evaluation](docs/audit/provider-release-v0.2.2-20261111.md)
and a verified restricted security profile for both native architectures.
Release v0.2.3 adds exact peer authorization and renewable TLS; its two-case
[transport regression](docs/audit/provider-release-v0.2.3-20261111.md) links
the unchanged inference/locks to that seven-case baseline.
It does not close deployed owner-collection or policy-scope admission.

A healthy process proves only local configuration. Before selecting the release
digest in Deep Screening, run representative sensor-surface evals with the exact
image/model/prompt, review evidence-binding failures and record the admission
decision. Changing the model, prompt or execution profile requires a new
provider release and evaluation. Rollback replaces only the provider image and
release digest; it never clears the Deep Screening queue or implies `RESUME`.

The exact [v0.2.4 component report](docs/audit/provider-release-v0.2.4-20261113.md)
records current-session trust admission, both native security gates and one
selected real-material inference. It retains the limited replay scope, prior
corpus availability and remaining owner/identity/physical deployment gates.
