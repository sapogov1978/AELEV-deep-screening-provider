# ADR-0002: Bind each HTTP dispatch to its TLS handshake trust

- Status: accepted under the confirmed independent-placement goal, 2026-11-13.
- Amends: ADR-0001's existing-session behavior; opaque inference and locks are unchanged.

A real-TLS regression reproduced that an already open connection could still
POST after replacement of the authority and own leaf. Checking only that the
current identity was available did not bind the session to that current trust.

Each admitted connection retains the actual SSLContext from its completed
handshake. Before every HTTP dispatch the provider resolves current delivery
and requires that exact context object, plus the exact unexpired peer URI.
Changed, stale, corrupted or withdrawn delivery returns bounded HTTP 503 with
Connection: close before application/inference dispatch. A new connection can
use the new authority without restarting the listener. There is no last-good
context fallback. Requests already dispatched follow their existing deadline;
this decision does not claim to interrupt an in-flight upstream inference.

The listener configuration retains its original callback-bearing context for
its whole lifetime. A TLS 1.3 HelloRetryRequest test forces garbage collection,
checks actual HRR wire bytes, renews identity and checks successful requests.
This exercises the upstream context-lifetime mitigation on pinned Python 3.13.7.
No interpreter, dependency, model, prompt or opaque contract is changed.

Both tests use ephemeral test PKI and a counting application without OpenAI.
Exact-image security, semantic quality, owner admission and physically distinct
machines remain separate acceptance gates.
