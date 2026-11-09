<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors

SPDX-License-Identifier: Apache-2.0
-->

# R29 — Helpdesk six-use-case application contract (pre-integration)

**Status:** CANDIDATE / INTEGRATION BLOCKED BY R27 SERVICE SPLIT + R28 CORE OPENAPI.  
**Owner:** Ánh (Application). **Review:** Yến (Core/API), Bảo (architecture/release).

This branch adds one **transport-neutral sealed Java command contract** for exactly six Helpdesk operations (`Create`, `Triage`, `Assign`, `Start`, `Resolve`, `Confirm`) and unit tests of the command-value validation. It **does not** move the legacy service, change production routes, implement persistence/idempotency or enable LIVE traffic. Keeping it separate avoids prematurely coupling application logic to the old monolithic infrastructure class.

## Baseline checked

- `backend/src/main/java/com/tricore/dxos/infrastructure/workflow/HelpdeskService.java` on the audited source has 380 lines and owns JDBC transactions, authorization, data mutations and workflow calls.
- `gateway/helpdesk/HelpdeskController.java` currently delegates `create`, `assign` and string-based `transition(id, action, version, resolution)` for the remaining four commands.
- The current `create(title,description)` generates a fresh UUID and workflow ID, **without an idempotency key**; the command record's mandatory key is *not* a duplicate-prevention implementation.
- The existing `transition` looks up definition `it-helpdesk` version **1** directly; version-as-configuration requires a reviewed runtime/contract decision.
- Current state is read through persisted `WorkflowInstance` inside `HelpdeskService`. R29 must read authoritative state from Core after the split, never infer it from a local enum or cache.
- `assign` validates a distinct `expectedAssignmentVersion` (business assignment version) rather than workflow runtime version. Preserve the distinction in OpenAPI and handler behavior.

## Compatibility and migration map

| Typed use-case | Current HTTP route | Legacy handler | Required future dependency |
| --- | --- | --- | --- |
| `Create(title, description, idempotencyKey)` | `POST /api/v1/mvp/requests` | `HelpdeskService.create(title, description)` | Separate Helpdesk creation intent and Core activation; scoped idempotency and reconciliation |
| `Triage(requestId, expectedVersion)` | `POST /{id}/triage` | `transition(..., "triage", ..., null)` | Core workflow transition, authorization and optimistic version |
| `Assign(requestId, assigneeId, expectedAssignmentVersion)` | `POST /{id}/assign` | `assign(...)` | Qualified assignee; versioned Helpdesk intent and atomic Core ACL replacement (OD-06 Option A) |
| `Start(requestId, expectedVersion)` | `POST /{id}/start` | `transition(..., "start_work", ..., null)` | Core `start_work` transition, current actor authority and synchronized assignment |
| `Resolve(requestId, expectedVersion, resolution)` | `POST /{id}/resolve` | `transition(..., "resolve", ..., resolution)` | Durable resolution intent, authorized Core transition and conditional Helpdesk finalization |
| `Confirm(requestId, expectedVersion)` | `POST /{id}/confirm` | `transition(..., "confirm", ..., null)` | Requester-only confirmation; synchronized assignment, authoritative RESOLVED state and finalized matching Helpdesk resolution |

**Important boundaries:** These records validate only null, blank and basic length/version constraints (aligned with the current HTTP payload for title/description/assignee/resolution). They never check eligibility, tenant, ACL, definition binding, actor, state or transaction outcome. Those checks **must** happen server-side through independently reviewed Core and business ports before writes; no caller should bypass old protection by directly activating records. Key maximum length 256 is a **candidate internal limit**, pending R28 contract agreement.

## Cross-service contract

Source: [reviewed ADR-015 §§7–9](https://github.com/tricore-opentrix/opentrix/blob/35ab10a7fff600b1b2e48afd776d15c6834bdedd/docs/08-decisions/ADR-015-core-workflow-acl-v3-g0.md),
[R29 amendment](https://github.com/tricore-opentrix/opentrix/blob/35ab10a7fff600b1b2e48afd776d15c6834bdedd/docs/03-applications/helpdesk/r29-pr145-contract-amendment.md)
and [G0 verification matrix](https://github.com/tricore-opentrix/opentrix/blob/35ab10a7fff600b1b2e48afd776d15c6834bdedd/docs/verification/r27/adr015-g0-contract-verification-matrix.md).
[Yến selected Option A](https://github.com/tricore-opentrix/opentrix/pull/163#issuecomment-6731860971);
[Ánh approved](https://github.com/tricore-opentrix/opentrix/pull/163#pullrequestreview-5821754766)
and [Bảo reconfirmed](https://github.com/tricore-opentrix/opentrix/pull/163#issuecomment-6732338208)
the documentation direction at the reviewed SHA.

Helpdesk owns business state, durable intents and assignment versions. Core owns
effective ACL, policy generation, accepted fences, audit and Workflow state/history.
Each service commits independently. A Core commit survives loss of its response or
failure of Helpdesk finalization. Any compensation requires an explicit approved
business contract. Helpdesk has no direct access to Core-owned ACL or Workflow tables.

**Authority.** Helpdesk verifies the business actor and tenant/resource binding.
Core authenticates the caller and verifies tenant, exact resource and operation
authority independently. If those facts cannot be verified, Core fails closed. ACL administration requires dedicated authority for the
service principal in that tenant/resource and operation set. Core READ/HISTORY
uses a current, transactionally consistent effective ACL. Helpdesk intent, UI
status, caller-supplied identity and historical command results cannot establish
Core authorization. Safe responses preserve tenant isolation and resource visibility.

**Recovery and concurrency (all four groups).** Persist the versioned intent,
stable command identity and correlation before dispatching a write. The proposed
Core key scope is tenant, authenticated service principal, operation type and key.
The canonical fingerprint binds the resource and semantic payload, including
applicable version/generation/fence inputs. Correlation is for tracing. Same-key,
same-fingerprint retries return the historical outcome without a second mutation.
A different fingerprint conflicts. Serialize concurrent same-key execution.
After timeout, disconnect or lost ACK, use authenticated authoritative command-status
lookup bound to the original scope before any resend. Match the result to the
exact intent and check current state separately where needed. Unknown or unavailable
status stays reconciling. Retry the same key and payload only with authoritative
non-commit evidence and within the approved replay policy. An ambiguous absence or
expired record is insufficient. Persistent `IN_PROGRESS` and `OUTCOME_UNKNOWN`
ledger rows are open design choices. Finalize with compare-and-set (CAS) or
equivalent concurrency protection on the matching current Helpdesk intent and
expected versions. Superseded results never finalize current business state.

### Create + Activate

- **Purpose and preconditions.** Create a ticket linked to an active Core Workflow
  instance. Validate the authenticated requester, tenant, request data and intended
  definition binding. Core validates the exact binding and CREATE/ACTIVATE authority.
- **Intent and boundary.** Helpdesk commits a pending create intent with a stable
  request/resource identity and scoped key before invoking Core. Core creates and
  activates independently of that Helpdesk transaction. A composite Core command
  is a candidate. If R28 keeps two steps, reconcile the created but unactivated
  instance and apply the approved activation version check before completion.
- **Outcome.** Report pending creation while the Core outcome or local finalization
  is outstanding. Report success only after authoritative activation of the intended
  instance and matching Helpdesk finalization. An unavailable Core keeps the intent
  pending. A lost ACK or local finalization failure after Core commit triggers
  reconciliation. A definitive rejection records a safe failure against the matching
  intent. Duplicate or concurrent requests cannot create duplicate tickets or instances.
- **Dependencies and verification.** R28 owns the composite/two-step decision,
  activation version check and shared recovery details. See [R29 verification](#contract-verification)
  for duplicate creation and partial failure.

### Assign / Reassign

- **Purpose and preconditions.** Record a coordinator's eligible assignment for
  the exact tenant/ticket, at the expected assignment version and permitted
  business/workflow state. Core independently checks ACL-administration authority.
- **Intent and boundary.** In one Helpdesk transaction, CAS the expected business
  version, advance `assignmentVersion` and a distinct monotonically increasing
  tenant/resource `fencingSequence`, and persist the intent, pending state and
  durable command identity. Dispatch the authenticated ACL replacement only after
  that commit. Core treats the Helpdesk version token as opaque correlation and
  checks the fence independently of Workflow version, policy generation and
  idempotency. Core atomically commits revoke-old, grant-new, accepted fence,
  updated generation, audit and authoritative committed outcome.
- **Option A.** Until Core commits the replacement, the previous grant may remain
  effective and the intended new grant is unconfirmed. Timeout does not revoke
  access or establish a revocation deadline. A command with a fence at or below
  the last accepted fence cannot execute another replacement. If the older command
  commits first, its grant can remain effective until the newer command commits.
  Only the current matching intent may finalize, even if both commands committed.
- **State mapping.** These are Helpdesk contract states. The typed command exposes
  no synchronization state, so the mapping describes business meaning rather than
  new API fields or schema values.

| Contract state | Meaning and observable result |
| --- | --- |
| `PENDING_SYNCHRONIZATION` | Durable current intent is awaiting the exact Core outcome. An unsent command can remain pending when Core is unavailable. Show pending and gate synchronized-only actions. |
| `SYNCHRONIZED` | An authoritative ACK or status proves the exact replacement committed with its fence and generation, and Helpdesk CAS finalization succeeded for that command/version. Show complete. Core still determines current access. |
| `RECONCILIATION_REQUIRED` | Possible commit with timeout/lost ACK, status inconsistency, or Core commit with failed local finalization. Show reconciliation and keep the gate closed. Look up status, then finalize only the matching current intent. A failed CAS on a superseded version must never overwrite the newer state. |
| `SYNCHRONIZATION_FAILED` | Definitive rejection durably recorded against the current intent. Show a safe failure, keep the gate closed and require an authorized new intent/version/key for correction. An unrecorded definitive outcome still needs reconciliation. |

- **Dependencies and verification.** Apply the shared recovery rules for duplicate
  retry, payload conflict and unknown outcomes. Prolonged pending or reconciliation
  is visible to operators. Monitoring timeout and operational escalation are separate
  from a definitive business failure. Emergency revocation requires a separate
  approved security procedure. See [open decisions](#open-r28-and-g0-design-decisions)
  and [R29 verification](#contract-verification).

### Resolve

- **Purpose and preconditions.** Resolve as the eligible current worker/assignee.
  Check the tenant/resource, business and Workflow versions and current synchronized
  assignment before accepting the action. Core evaluates current exact transition
  authorization and Workflow prerequisites independently.
- **Intent and boundary.** Helpdesk commits the pending resolution intent, expected
  business/assignment versions, scoped key and correlation. Core validates the
  expected Workflow version and atomically commits the authorized resolution
  transition and history in Core. Helpdesk finalizes the resolution text and business
  result separately after authoritative evidence of the intended `RESOLVED` result,
  conditional on the matching intent, versions and assignment prerequisite.
- **Outcome and recovery.** An unsynchronized assignment blocks Resolve. Timeout
  or lost ACK triggers authenticated lookup. Core commit with local CAS failure
  stays reconciling for the matching attempt and cannot overwrite a newer intent.
  Definitive rejection records safe failure. Report resolved only after both Core
  outcome and Helpdesk finalization. Reconciliation cannot imply a reverse transition.
- **Dependencies and verification.** R28 owns status and transition transport and
  the concurrency protocol across these checks. See [R29 verification](#contract-verification).

### Confirm

- **Purpose and preconditions.** Preserve requester-only confirmation. Require a
  synchronized current assignment and durably finalized matching Helpdesk resolution
  for the same resource and expected business version. Require an authoritative
  Core read/status under current authorization that confirms `RESOLVED` at the
  expected Workflow version. Historical replay alone cannot satisfy this prerequisite.
- **Intent and boundary.** Persist a versioned confirmation intent under those
  Helpdesk prerequisites. The existing Confirm operation includes a Workflow
  transition, so retain its authenticated Core transition with the expected Workflow
  version. Core checks current authority/state/version and commits the transition and
  history in Core. Helpdesk prerequisite checks and CAS finalization are local steps.
- **Outcome and recovery.** Block Confirm when assignment or resolution prerequisites
  are pending. If the prerequisite read fails, keep confirmation uncompleted and
  recover through an authorized read. If the transition might have committed, look
  up its exact outcome before retry. Definitive rejection records a safe failure.
  Report completion only after the authoritative transition outcome and matching
  Helpdesk CAS, including the business and assignment prerequisites. Failed local
  finalization after Core commit requires reconciliation.
- **Dependencies and verification.** R28 must specify the cross-service prerequisite
  and version protocol, status lookup and replay/response semantics. See
  [R29 verification](#contract-verification).

### Open R28 and G0-DESIGN decisions

- Exact ACL-admin wire schema and service-principal authentication, canonical
  serialization/fingerprint, rejection and HTTP error mapping, authenticated
  command-status lookup, ledger retention and replay/expiry semantics. See the
  [candidate Core HTTP contract](https://github.com/tricore-opentrix/opentrix/blob/ef4b9484369c94ed7e5674e4b056b0d8f673e1ba/docs/01-architecture/r27-core-workflow-http-contract.md).
- Locking and privilege details, including READ/HISTORY versus revoke and
  least-privilege PostgreSQL roles. T07/T08 evidence is required at the relevant gate.
- **G0-DESIGN OPEN DECISION:** an unrelated ACL write can advance tenant-wide
  `expectedPolicyGeneration` and cause the candidate `STALE_POLICY_GENERATION`
  outcome despite a valid per-resource fence. Preserve the reviewed generation
  precondition and fencing pending the design decision.
- **OPEN — OWNER DECISION REQUIRED (Yến/Ánh):** monitoring thresholds, alerting
  and escalation, and the separate emergency-revocation procedure and authority.
  Retry/backoff and API-visible status mapping also require review before integration.
  No numeric SLA or emergency bypass is specified.

### Contract verification

Record future execution evidence at the tested SHA. Contract review alone does
not supply runtime evidence.

| Scenario | Expected contract behavior | Status |
| --- | --- | --- |
| Create + Activate success / duplicate | Match activation evidence and finalize one ticket/instance. | NOT RUN |
| Create activation lost ACK / local failure | Recover the same intent and instance; preserve the Core commit. | NOT RUN |
| Core ACL replacement commits | Exact authoritative ACK/status and Helpdesk CAS; replacement, fence, generation and audit commit together. | NOT RUN |
| Core unavailable | Keep pending when unsent; reconcile uncertain dispatch; no success. | NOT RUN |
| Lost ACK before/after Core commit | Authenticated status lookup before retry; no duplicate mutation or false failure. | NOT RUN |
| Same key and payload, concurrent or replayed | One historical result; distinguish current ACL. | NOT RUN |
| Same key, different payload | Reject with no mutation. | NOT RUN |
| Stale version or delayed older fence | Reject stale execution or discard stale local finalization. | NOT RUN |
| Concurrent reassignment | CAS and Core fence protect the current intent and ACL ordering. | NOT RUN |
| Core commit plus Helpdesk CAS failure | Reconcile the matching intent; preserve Core commit and newer business state. | NOT RUN |
| Resolve while assignment is pending | Block; no Core transition or local success. | NOT RUN |
| Resolve lost ACK / local failure | Recover the exact transition and finalize only the matching intent. | NOT RUN |
| Confirm while assignment or resolution is pending | Block even if Core reports `RESOLVED` without matching local finalization. | NOT RUN |
| Confirm lost ACK or stale finalization | Recover the exact command; gate completion on the matching local CAS. | NOT RUN |
| Cross-tenant command or status lookup | Deny with no mutation or disclosure. | NOT RUN |
| Old grant during lag / READ/HISTORY vs revoke | Old grant may remain until replacement commits; Core authorizes against current ACL. | NOT RUN |
| Timeout escalation | Monitor and escalate under an approved policy without implying revocation or definitive failure. | BLOCKED |
| Emergency revoke | Requires a separate approved procedure. | BLOCKED |

## Implementation gates

1. **R27 service split:** agree destination Java module, Core client interface, authentication token relay, tenant isolation, schema ownership, no cross-schema JOIN, and controlled Flyway migrations. Do not move 380 legacy lines into the new service unchanged.
2. **R28 OpenAPI:** decide exact Core workflow create/read/transition interfaces, idempotency-key transport and retry policy, expectedVersion semantics, error mapping, including the candidate `COMMIT_OUTCOME_UNKNOWN` HTTP 503, and definition-version configuration.
3. **Six application handlers:** wire the six command types through an application facade and ports only after R27/R28. Retain negative tests for 404 visibility parity, denied mutation no-write, tenant boundary, assignment ACL, eligibility, terminal state, definition binding, stale version and unknown commit.
4. **Create idempotency acceptance:** same tenant + authenticated caller + idempotency key + same payload cannot create two business tickets/two Core workflow instances, including concurrent calls, rollback and uncertain outcomes. A mismatched payload under an existing key must not silently return the prior result. Reconcile uncertain commits; no blind retry.
5. **R29 Done:** two-service CI is green, contract tests pass, all six use-case integration tests pass in real PostgreSQL/Core environment, definition version is configurable, authoritative state is Core-derived, no Helpdesk business mutations reside in `infrastructure`, and independent approval is recorded.

**Current verdict:** `TYPED_COMMAND_CONTRACT_CANDIDATE / BACKEND_GRADLE_BUILD_AND_TEST_PASSED_IN_CI / PRODUCTION_INTEGRATION_BLOCKED`.

The backend Gradle build ran the `:test` task and succeeded at reviewed SHA
`b3d80254459269deb5071e52e59e1bda6954b5c7` ([CI run 42565148187](https://github.com/tricore-opentrix/opentrix/actions/runs/42565148187)).
PostgreSQL and service-runtime verification remain **NOT RUN**. R27 integration
and G0-CONTRACT remain **BLOCKED**.
