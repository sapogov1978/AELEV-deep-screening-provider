# AELEV Deep Screening Provider specification

## Responsibility

The provider owns the remote API choice, model lock, prompt, credential,
structured-output schema, response validation and image healthcheck. Deep
Screening owns research collection, queueing, retries, decisions, evidence,
admission, UI, storage and Kafka publication.

## Opaque port

`GET /v1/status` and `POST /v1/infer` implement schema version 1 for owner
`deep-screening`, task `SENSOR_SURFACE`, capability `INFERENCE` and the exact
SHA-256 digest of [release.json](release.json). Requests and responses use the
envelope in [contracts/opaque-compute-v1.json](contracts/opaque-compute-v1.json).
No provider, model, prompt, upstream body or credential is disclosed.

Inference output contains `decision` (`SUITABLE`, `UNSUITABLE` or `REVIEW`),
bounded candidate groups, exact evidence URLs/digests and `unknown_scope`.
Deep Screening revalidates every location against its own collected evidence
and remains the only component allowed to apply that result.

## OpenAI execution

[provider.lock.json](provider.lock.json) pins the Responses endpoint, model,
reasoning effort, output budget, `store=false`, exact prompt digest and direct
HTTPS transport. Each call is a stateless, buffered request with no tools,
streaming, background mode or stored-response chaining. Input material is data,
not instructions. Only one strict structured-output object is accepted.

`store=false` requests stateless API behavior; it is not a claim that the
OpenAI project has Zero Data Retention or a particular data residency setting.
Those account-level properties remain admission gates.

## Readiness and release

Local readiness validates immutable configuration and a non-placeholder secret
without performing a billable upstream probe. Provider quota, model access and
semantic quality require a bounded live evaluation. Production use additionally
requires an immutable signed image digest, SBOM, provenance, mTLS identities and
an explicit Deep Screening quality-admission decision.
