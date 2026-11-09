# OpenAI API Migration Decision Ledger

**Application:** AELEV Deep Screening Provider
**Current integration:** New opaque provider; no legacy API integration
**Selected integration and model:** OpenAI Responses API with `gpt-6.1-sol`
**Approved migration scope and feature-stage plan:** User approved a provider analogous to Translation Provider, using its own placeholder credential; contract, adapter, offline tests and DRP recipe are in scope, live API evaluation and admission wait for a real key.
**Privacy and retention requirements:** Stateless single-turn calls with `store=false`; Zero Data Retention and residency are not claimed and remain account-level admission checks.
**Assessment or implementation:** Implemented offline; live validation pending credential, quota and explicit admission.

The decisions below review every capability in the migration guidance. `[x]`
means implemented and verified offline; `[ ]` means not applicable, deferred or
pending external admission.

## Model Selection

| Guidance items | Applicable | Supported | Decision | Implemented | Rationale or evidence |
|---|---|---|---|---|---|
| Concrete model, preservation, quality/latency/cost | yes | yes | implemented | [x] | `provider.lock.json` selects the same operator-approved `gpt-6.1-sol` profile as Translation Provider; a model change requires a new lock, eval and release. |

## Instruction File Naming

| Guidance items | Applicable | Supported | Decision | Implemented | Rationale or evidence |
|---|---|---|---|---|---|
| Preserve instructions and add compatibility files only with approval | yes | yes | implemented | [x] | New repository has one provider-owned prompt; no existing instruction file was renamed or replaced. |

## Migrate from Chat Completions to the Responses API

| Guidance items | Applicable | Supported | Decision | Implemented | Rationale or evidence |
|---|---|---|---|---|---|
| Responses route and behavior preservation | yes | yes | implemented | [x] | New integration calls only `/v1/responses`; opaque owner contract is independent of provider identity. |

## Streaming

| Guidance items | Applicable | Supported | Decision | Implemented | Rationale or evidence |
|---|---|---|---|---|---|
| Preserve or add streaming; typed events; complete-response fallback | no | yes | not applicable | [ ] | Owner contract is one bounded atomic sensor-surface decision and has no partial user-visible output. |

## WebSocket Mode

| Guidance items | Applicable | Supported | Decision | Implemented | Rationale or evidence |
|---|---|---|---|---|---|
| Persistent transport, concurrency, recovery and reconnect | no | yes | not applicable | [ ] | One buffered stateless HTTP request has no tool loop, lane, reconnect or side effect. |

## Data Privacy and Residency

### Zero Data Retention

| Guidance items | Applicable | Supported | Decision | Implemented | Rationale or evidence |
|---|---|---|---|---|---|
| Confirm ZDR, feature compatibility, stateless storage and expectations | yes | partial | deferred | [x] | Request uses `store=false` and provider stores no response; ZDR is not inferred and must be confirmed for the OpenAI project before admission. |

### Data Residency

| Guidance items | Applicable | Supported | Decision | Implemented | Rationale or evidence |
|---|---|---|---|---|---|
| Jurisdiction, regional endpoint/availability and tradeoff confirmation | unknown | unknown | deferred | [ ] | No residency requirement was supplied; operator must confirm project and deployment requirements before production admission. |

## Processing Tiers

| Guidance items | Applicable | Supported | Decision | Implemented | Rationale or evidence |
|---|---|---|---|---|---|
| Per-workload tier; standard/priority/flex/batch/reserved; pricing and latency | yes | yes | implemented | [x] | No service tier override is sent, retaining standard synchronous processing; other tiers would alter latency/cost and require approval. |

## Prompt Caching

### Prompt Cache Keys

| Guidance items | Applicable | Supported | Decision | Implemented | Rationale or evidence |
|---|---|---|---|---|---|
| Cache keys and prefix fragmentation | no | yes | not applicable | [ ] | No explicit cache key is added; stateless inputs vary by site and privacy is preferred. |

### Extended Cache Retention for Earlier Models

| Guidance items | Applicable | Supported | Decision | Implemented | Rationale or evidence |
|---|---|---|---|---|---|
| Extended retention assessment | no | unknown | not applicable | [ ] | Retention extension conflicts with the selected stateless profile. |

### Explicit Cache Breakpoints for GPT-5.6 and Later

| Guidance items | Applicable | Supported | Decision | Implemented | Rationale or evidence |
|---|---|---|---|---|---|
| Stable breakpoints and implicit/explicit policy | no | unknown | not applicable | [ ] | Selected model and workload do not require an explicit cache strategy. |

### Prompt Cache Diagnostics

| Guidance items | Applicable | Supported | Decision | Implemented | Rationale or evidence |
|---|---|---|---|---|---|
| Comparison response diagnostics | no | unknown | not applicable | [ ] | No cache optimization is approved for this privacy-sensitive one-shot workload. |

## State Management

| Guidance items | Applicable | Supported | Decision | Implemented | Rationale or evidence |
|---|---|---|---|---|---|
| Local/server state, stateless replay and stored chaining | yes | yes | implemented | [x] | Every request contains complete owner input; `store=false`, no previous response ID and no provider conversation state. |

### Instruction Persistence Gotcha

| Guidance items | Applicable | Supported | Decision | Implemented | Rationale or evidence |
|---|---|---|---|---|---|
| Durable instructions across replay/chaining | yes | yes | implemented | [x] | Digest-pinned top-level instructions are resent on every request. |

## Reasoning

### Encrypted Reasoning Items

| Guidance items | Applicable | Supported | Decision | Implemented | Rationale or evidence |
|---|---|---|---|---|---|
| Preserve ordering, payloads and tool identifiers | no | yes | not applicable | [ ] | No multi-turn replay or tools; reasoning items are neither requested nor replayed. |

### Reasoning Effort

| Guidance items | Applicable | Supported | Decision | Implemented | Rationale or evidence |
|---|---|---|---|---|---|
| Configure effort, preserve preference and verify support | yes | yes | implemented | [x] | Lock pins `medium`, matching the approved Translation Provider profile; request-shape test enforces it. |

### Reasoning Preservation

| Guidance items | Applicable | Supported | Decision | Implemented | Rationale or evidence |
|---|---|---|---|---|---|
| Cross-turn/current-turn preservation | no | yes | not applicable | [ ] | One turn, no conversation state. |

### Reasoning Summaries and Tool-Call Preambles

| Guidance items | Applicable | Supported | Decision | Implemented | Rationale or evidence |
|---|---|---|---|---|---|
| Summaries, preambles and visible behavior | no | yes | not applicable | [ ] | Only schema-bound classification crosses the opaque port. |

## Verbosity

| Guidance items | Applicable | Supported | Decision | Implemented | Rationale or evidence |
|---|---|---|---|---|---|
| Configure verbosity and confirm UX/cost compatibility | no | unknown | not applicable | [ ] | Strict schema and field limits, not prose verbosity, bound output. |

## Maximum Output Tokens

| Guidance items | Applicable | Supported | Decision | Implemented | Rationale or evidence |
|---|---|---|---|---|---|
| Preserve/invent limit and include reasoning tokens | yes | yes | implemented | [x] | Lock pins 8192 for reasoning plus a small structured result; changing it requires a lock update. |

## Assistant Message Phases

| Guidance items | Applicable | Supported | Decision | Implemented | Rationale or evidence |
|---|---|---|---|---|---|
| Preserve phases, structure and commentary/tool loops | no | yes | not applicable | [ ] | Provider accepts exactly one completed `output_text` JSON object. |

## Context Compaction

| Guidance items | Applicable | Supported | Decision | Implemented | Rationale or evidence |
|---|---|---|---|---|---|
| Compaction strategy, thresholds, encrypted items and privacy | no | unknown | not applicable | [ ] | No long-running conversation or accumulated context. |

## Structured Outputs

| Guidance items | Applicable | Supported | Decision | Implemented | Rationale or evidence |
|---|---|---|---|---|---|
| Schema, compatibility, parsing and focused tests | yes | yes | implemented | [x] | `text.format` uses strict JSON Schema; provider and DRP both validate the result. |

## Tools

### Tool Choice

| Guidance items | Applicable | Supported | Decision | Implemented | Rationale or evidence |
|---|---|---|---|---|---|
| Tool selection policy | no | yes | not applicable | [ ] | No tools are sent; site collection remains owner-side. |

### Tool Search and Additional Tools

| Guidance items | Applicable | Supported | Decision | Implemented | Rationale or evidence |
|---|---|---|---|---|---|
| Deferred discovery, replay, caching and approval | no | yes | not applicable | [ ] | No tool catalog exists. |

### Parallel Tool Calls

| Guidance items | Applicable | Supported | Decision | Implemented | Rationale or evidence |
|---|---|---|---|---|---|
| Concurrency, order, approvals and side effects | no | yes | not applicable | [ ] | No tool calls; inference is serialized locally. |

### Programmatic Tool Calling

| Guidance items | Applicable | Supported | Decision | Implemented | Rationale or evidence |
|---|---|---|---|---|---|
| Coordination, compatibility, permissions and tests | no | unknown | not applicable | [ ] | No provider-side orchestration is permitted. |

### Model-Aligned Tool Interfaces

| Guidance items | Applicable | Supported | Decision | Implemented | Rationale or evidence |
|---|---|---|---|---|---|
| Repository or patch interfaces | no | unknown | not applicable | [ ] | This classification service exposes no development tools. |

## Outcome

**Implemented or already present:** Lock-pinned Responses request, stateless
storage profile, strict structured output, bounded parsing/failures, exact opaque
contract, placeholder-secret rejection and offline tests.
**Remaining work:** Real provider-specific key, model/quota access, bounded live
quality evaluation, mTLS clean-room test, signed image and owner admission.
**Developer decisions requiring follow-up:** ZDR/residency requirement and any
non-standard processing tier before production.
**Validation evidence:** Source tests and image builds recorded in the delivery
turn; no live API call or semantic admission is claimed.

Official references reviewed: [Responses API](https://developers.openai.com/api/reference/resources/responses/methods/create), [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs), and [migration guidance](https://developers.openai.com/api/docs/guides/migrate-to-responses).
