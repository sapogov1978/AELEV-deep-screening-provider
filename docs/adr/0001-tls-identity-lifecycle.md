# ADR-0001: Exact peer identity and renewable TLS material

- Status: accepted for the production-admission goal, 2026-11-11.
- Scope: the opaque HTTPS port, without changing inference or dependency locks.

The released port required a client certificate from a trusted CA but did not
authorize its exact SPIFFE URI. Its TLS context was loaded only at startup.
These properties do not satisfy permanent workload-identity admission.

The TLS root now includes immutable `identity.json` policy with exactly
`schema_version=1`, `environment`, `delivery`, `server_spiffe_id` and
`client_spiffe_id`. Both identities are canonical, distinct and belong to this
functional owner and trust domain. A changed policy blocks use until a new
controlled deployment. It does not silently grant a different client.

Production requires public `spire-file-v1` delivery: a fresh READY
`current.json` names immutable `generations/<64 hex>/tls.pem` and `bundle.pem`.
The recipient checks environment, exact identity, freshness within 20 seconds,
expiry within 3900 seconds, exact file hashes, private-key mode, real leaf
identity/expiry/serial and key/chain validity. Symlinks, non-regular files,
large inputs and CA certificates used as leaves are rejected. The consumer
never reads SPIRE registrations, bootstrap tokens or issuer keys.

The PEM layout remains available only with explicit `delivery=pem-files-v1`
and a local/test environment. Production never falls back to PEM, HTTP or the
last good generation after withdrawal or corruption.

Certificate validation uses bounded in-memory TLS handshakes through the
[public Python SSL APIs](https://docs.python.org/3.13/library/ssl.html#memory-bio-support),
without a socket, subprocess, new dependency, private certificate parser or
custom ASN.1 decoder. The verification-disabled inspection endpoint is only
an in-memory probe of the same owned material; its opposite endpoint performs
normal X.509 chain/purpose verification. The network listener always requires
a verified client certificate. No OpenAI credential enters this mechanism.

New handshakes select a fresh TLS context, including replacement trust roots.
The pinned Uvicorn protocol authorizes exactly one client URI SAN before
HTTP parsing. Rejected transports also discard already buffered bytes.
Every subsequent request checks fresh owned material and peer expiry before
dispatching to the application. An established TLS session is not reverified
against a replacement CA; immediate peer isolation requires the separate
operator/network revocation path. Withdrawn owned delivery blocks requests on
existing sessions as well as new handshakes.

Local readiness combines initialized inference and current identity. Its
producer renews the marker every second; the probe rejects a marker older
than five seconds, a dead process or an absent listener. The probe reads no
key and performs no upstream request.

Real-TLS tests cover exact/foreign/missing/multiple URI SAN, unauthorized POST
dispatch, no-SNI clients, leaf renewal, CA replacement/removal, existing-session
withdrawal, stale or damaged delivery and actual client certificate purpose.
They use ephemeral certificates and a counting test application, without an
OpenAI call. Native issuance, exact-image controls and live inference remain
separate deployment and release evidence.
