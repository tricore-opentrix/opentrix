<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# ADR-015 — Core Workflow ACL V3 / G0: Atomic Authorization Contract

**Status:** PROPOSED — AWAITING INDEPENDENT REVIEW  
**Decision owner:** Yến  
**Reviewers:** Bảo (Core, PostgreSQL, transactions, security), Ánh (Helpdesk, service contracts, assignment synchronization)  
**Decision date:** Pending formal acceptance  
**Tracking:** R27 Step 03 / PR-0b  
**Related:** ADR-010 (PR #159), R28, R29 (PR #145; proposed amendment: [R29 contract amendment](../03-applications/helpdesk/r29-pr145-contract-amendment.md)), R31, T07/T08, Issue #138
**Reference baseline:** `main@187dbd2ea6935966f5c4cceb95ad9c3c53708a2e`  
**ADR-010 reviewed candidate:** `ef4b9484369c94ed7e5674e4b056b0d8f673e1ba`

## 1. Context

OpenTrix is separating the Core Workflow runtime from the Helpdesk application.

The legacy implementation allows Helpdesk to access Workflow persistence and authorization-related tables within a local PostgreSQL database. This cannot remain the final design because Helpdesk and Core must become independently deployed services with separate database ownership.

The proposed Core authorization boundary requires:

- Authoritative Core-owned ACL facts.
- Verified canonical actor identity.
- Tenant isolation.
- Exact resource grants and workflow definition bindings.
- Authorization and Workflow mutation within one Core database transaction.
- A consistent ordering between policy revocation and authorized operations.
- Fail-closed behavior when authority cannot be established.

Existing ACL SQL is evidence of historical behavior and candidate structures, not an approved Core ACL V3 migration.

This ADR establishes the intended contract before Core ACL persistence, migration and runtime privilege implementation.

## 2. Decision scope

This ADR governs **Core Workflow resource authorization**.

It does not independently approve:

- The full SYS-ADR-04 authorization architecture.
- The Core/Helpdesk deployment cutover.
- R28 OpenAPI definitions.
- R29 business transaction semantics.
- New database migrations or runtime grants.
- Activation of protected Core HTTP routes.
- Public release or source-rights clearance.

ADR-010 remains a prerequisite for the target service boundary.

## 3. Selected direction

The decision owner has selected the following candidates for independent review.

| ID | Selected option | Contract direction |
|---|---|---|
| G0-01 | A — Core Java transaction | Authorization is evaluated in Core Java within the transaction that performs the protected Core operation |
| G0-02 | A — Relational ACL | Core-owned relational tables hold effective memberships, resources, grants, bindings and policy revisions |
| G0-03 | A — Tenant-level lock | A tenant-scoped policy guard serializes policy changes against protected operations |
| G0-04 | A — Synchronous Core ACK | Helpdesk waits for authoritative Core acknowledgment of assignment-related ACL changes |
| G0-05 | A — Current consistent ACL | READ/HISTORY uses current, transactionally consistent Core authorization |
| G0-06 | A — Transactional audit and ledger | Policy mutations, audit and deduplication state have explicit atomicity rules |
| G0-07 | A — Separate owner/runtime roles | Migration owners and runtime roles are separate, with least-privilege Core/Helpdesk database isolation |
| G0-08 | A — Fail-closed and reconciliation | Unavailable authority denies execution; unknown commit outcomes require authoritative reconciliation |

These are **selected design directions**, not implemented or formally accepted contracts.

## 4. Required authorization invariants

### INV-01 — Identity authenticity

The Core ingress must obtain a verified canonical principal from its authentication mechanism.

Caller-supplied actor identifiers, tenant headers, ownership flags or forwarded identity headers must not establish trust.

A valid JWT operation authority does not by itself constitute a resource-specific ACL grant.

### INV-02 — Core authority

Core owns the effective Workflow authorization facts used for every protected operation.

The authorized decision must be based on exact authoritative facts, not:

- Helpdesk-owned business membership alone.
- Client-supplied ACL snapshots.
- Unverified JWT claims.
- Owner status alone.
- A cached policy whose revocation consistency is unproven.

### INV-03 — Exact resource binding

Authorization must use the authoritative tenant, resource identity, actor membership, explicit operation grant and, when required, exact Workflow definition/version binding.

Missing or incomplete facts fail closed.

Resource identity and tenant uniqueness rules must be recorded before DDL.

### INV-04 — Atomic authorization and write

A protected Core Workflow mutation must:

1. Begin one Core-owned transaction.
2. Acquire the required policy synchronization lock.
3. Read the authoritative facts for the verified actor and exact resource.
4. Evaluate authorization.
5. Lock and validate the authoritative Workflow instance where applicable.
6. Validate `expectedVersion` for operations that require it.
7. Apply the mutation and corresponding history within that transaction.
8. Commit the entire result or roll back the entire mutation.

A detached ACL check followed by an independent Workflow transaction is prohibited.

This atomicity applies **inside Core only**, not across Core and Helpdesk.

### INV-05 — Revocation ordering

For a protected Core operation and a conflicting policy revocation, the contract requires an observable serialization order.

- If revocation commits before the operation's authorization serialization point, the operation must not proceed under the revoked right.
- An operation serialized before revocation may complete under the prior rights, subject to the approved transaction protocol.
- A revoke acknowledgment may be reported as committed only after the authoritative Core mutation commits.

The exact PostgreSQL lock modes and transaction isolation levels remain subject to G0 technical review and T08 verification.

### INV-06 — Failure closes access

Missing facts, ACL read failures, lock timeouts, deadlocks, stale policy evidence and unavailable authoritative storage must never be interpreted as permission.

The caller must receive a stable, non-leaking error response appropriate to the failure.

### INV-07 — Ownership isolation

The Helpdesk runtime must not have USAGE, SELECT or DML privileges on Core-owned protected tables.

The Core runtime must not directly access Helpdesk tables.

Separate migration owners control each service's DDL and Flyway history.

### INV-08 — Version separation

The following version concepts must not be conflated:

- Workflow instance runtime version.
- Core ACL policy generation/revision.
- Helpdesk assignmentVersion.

Core treats a Helpdesk business version only as an opaque correlation/concurrency token according to an approved contract. Core cannot independently establish Helpdesk's latest business state.

### INV-09 — Audit integrity

A committed effective ACL change must have an authoritative corresponding policy audit record.

A rolled-back ACL change must not leave a committed success audit entry.

Workflow transition history remains distinct from policy audit.

### INV-10 — Reconciliation

A network timeout or lost response after a possible commit is not evidence of rollback.

The system must reconcile using authoritative Core command status, durable idempotency identity or authorized state/history evidence before choosing whether to retry.

## 5. Proposed relational authority model

The Core ACL V3 design should define the equivalent capabilities of these existing candidate relations:

| Logical relation | Purpose |
|---|---|
| `tenant_guards` | Tenant policy generation and synchronization point |
| `tenant_memberships` | Effective Core Workflow membership |
| `resource_registry` | Authoritative resource identity, tenant and lifecycle |
| `resource_acl` | Explicit actor/resource/operation grants |
| `workflow_definition_bindings` | Authorized active definition/version bindings |
| `workflow_policy_audit` | Durable policy mutation audit |
| Command ledger (name TBD) | Idempotency, replay and command outcome reconciliation |

These are logical design candidates, not approved SQL names or DDL.

Before schema implementation, reviewers must settle:

1. Whether resource IDs are globally unique or tenant-scoped.
2. How resource and actor identity keys are normalized and constrained.
3. Which operations require explicit grants.
4. Whether membership changes increment tenant policy generation.
5. Whether every effective policy mutation increments generation exactly once.
6. Whether tombstoned resources can ever be reactivated.
7. How binding replacement and definition-version transitions are authorized.
8. How command ledger retention, uniqueness and cleanup are managed.

No cross-service foreign keys are permitted.

## 6. Transaction and lock contract

### 6.1 Shared acquisition order

The proposed ordering from ADR-010 is retained:

**Tenant policy generation → exact authorization facts → Workflow instance → Workflow history**

Where multiple resource/actor keys are involved, acquisition must follow a deterministic order.

This ordering applies to the relevant parts of GRANT, REVOKE, CREATE, ACTIVATE, TRANSITION and READ/HISTORY.

### 6.2 Policy writes

Effective GRANT, REVOKE, membership changes and binding changes must synchronize through the tenant policy guard.

Each successful policy mutation must commit the policy state, revised generation and corresponding audit as one atomic Core operation.

Exactly what counts as one generation increment for a batch change remains open.

### 6.3 Workflow writes

Protected Workflow writes must acquire policy synchronization before evaluating authorization and mutating Workflow state.

Workflow transition writes do not increment the ACL policy generation merely because an instance version changes.

### 6.4 READ/HISTORY

READ/HISTORY must authorize against a current, transactionally consistent Core snapshot with revocation ordering.

The design must prove that a read serialized after committed revocation cannot return protected data under the revoked permission.

Candidate techniques include shared reader/exclusive writer row locking or a proven consistent-snapshot plus policy-generation validation protocol.

The final technique must be selected after examining PostgreSQL isolation behavior, row-lock privileges, contention and two-connection tests.

A plain detached ACL SELECT under `READ COMMITTED` is not sufficient evidence.

### 6.5 Performance boundary

Tenant-level synchronization is accepted as the selected MVP direction, recognizing that it may serialize independent Workflow operations within one tenant.

Resource-level locking is deferred optimization, not an implied fallback that implementation may introduce without review.

## 7. Core ACL administration command (OD-05)

Grant/revoke is a dedicated authenticated Core ACL-administration command. It is not an ordinary Workflow transition. A service credential proves the calling service principal only; it does not grant arbitrary cross-tenant ACL authority. Core must authorize the service principal for the tenant/resource and approved operation set using a dedicated policy before mutation.

The proposed command envelope is:

| Field | Contract meaning |
|---|---|
| `tenantId`, `resourceId` | Explicit tenant/resource scope; Core verifies that the resource belongs to that tenant. |
| `affectedActors` | Canonical actor IDs whose grants are replaced; callers cannot substitute these for the authenticated principal. |
| `grantOperations`, `revokeOperations` | Explicit operation sets; the replacement set is validated as one request. |
| `expectedPolicyGeneration` | Core-owned generation precondition, distinct from both Helpdesk assignment and Workflow versions. |
| `helpdeskVersionToken` | Opaque business correlation/concurrency token; Core does not infer ticket or assignment semantics from it. |
| `fencingSequence` | Helpdesk-issued, strictly increasing per resource. Core only applies the protocol comparison “greater than last accepted”; it does not interpret business meaning. It exists to reject delayed older commands. |
| `idempotencyKey` | Stable key scoped as defined in OD-07. |
| `correlationId` | End-to-end tracing identifier; not an authorization credential or uniqueness substitute. |

The identities remain distinct: (1) initiating business user, (2) authenticated service principal, (3) affected actor(s), and (4) recorded audit actor/source. The audit records both the verified service principal and the initiating user when supplied through a trusted, signed/verified context; an untrusted caller-supplied identity is never treated as verified.

Within one Core transaction, an accepted replacement performs the authorized old-grant revocation, new-grant insertion, audit record, policy-generation increment, command ledger COMMITTED outcome and accepted fencing-sequence update atomically. The Core API must not expose a partial replacement. A pre-commit failure rolls back all of these; a potentially committed but unacknowledged request is OUTCOME_UNKNOWN until looked up.

Proposed stable outcomes (transport mapping remains R28 work):

| Condition | Stable outcome candidate | Required effect |
|---|---|---|
| Missing/invalid authentication | `AUTHENTICATION_REQUIRED` | No mutation. |
| Caller lacks dedicated tenant/resource ACL-administration authority | `ACL_ADMIN_FORBIDDEN` | No mutation; do not infer authority from service credentials alone. |
| Resource absent or hidden in tenant | `RESOURCE_NOT_FOUND` | No mutation; preserve non-disclosure policy. |
| Expected Core policy generation stale | `STALE_POLICY_GENERATION` | No mutation; caller must reread/reconcile. |
| Fencing sequence is not greater than last accepted | `STALE_ASSIGNMENT_COMMAND` | No mutation; delayed command cannot overwrite newer assignment. |
| Same scoped key, different canonical payload | `IDEMPOTENCY_PAYLOAD_CONFLICT` | No mutation. |
| ACL authority/storage unavailable | `ACL_UNAVAILABLE` | Fail closed; no success response. |
| Transaction definitely rolled back | `COMMAND_REJECTED` or specific validation outcome | No success audit/generation change. |
| Commit may have succeeded but ACK is absent | `OUTCOME_UNKNOWN` | Reconcile command status; do not blind retry with a new key. |

HTTP status/body and exact visibility mapping are DECISION REQUIRED in R28. This table proposes stable semantic outcomes, not implemented API codes.

## 8. Helpdesk assignment/reassignment state machine (OD-06)

Helpdesk owns `assignee`, `assignmentVersion`, assignment intent, and its synchronization state. Core owns effective ACL state, `policyGeneration`, command history and the last accepted per-resource `fencingSequence`. Workflow runtime version remains independent. None of these versions may be substituted for another.

Each Helpdesk assignment attempt has a durable command identity. The Helpdesk transaction validates the actor and expected business version, serializes/CASes the current assignment row to issue a monotonically increasing `assignmentVersion`/`fencingSequence`, records the new assignment intent and durable outbox command, and commits `PENDING_SYNCHRONIZATION`. Only after that commit may an authenticated Core ACL replacement command be sent. The Core transaction atomically revokes the old effective grant, grants the replacement actor, writes audit and command outcome, increments policy generation, and advances the accepted fence.

### 8.1 States and operational behavior

The state is attached to the current Helpdesk assignment version and command ID; a later assignment creates a new version and command. Core's command ledger is authoritative for whether an earlier command committed.

| State | Entry condition / event | Retry and reconciliation | Effective Core access | UI behavior | Completion condition / failure handling |
|---|---|---|---|---|---|
| `PENDING_SYNCHRONIZATION` | Helpdesk has committed the validated intent/version and durable command/outbox identity; dispatch has not yet been authoritatively confirmed. Also used while a new command is in flight before any timeout is observed. | Dispatch the same authenticated command with the same scoped idempotency key. On timeout/lost response, move to `RECONCILIATION_REQUIRED`; never issue a new key merely because the response is late. | Under proposed atomic replacement, the previous Core ACL remains effective until Core commits. The new actor is not guaranteed access yet. This lag is **DECISION REQUIRED** as described below. | Show “Assignment pending”; do not say old access was revoked or new access granted. Expose the pending state and last update; prevent downstream workflows that require a synchronized assignment. | Leave only after authoritative Core COMMITTED result is verified and Helpdesk durably records matching version, command ID and policy generation as `SYNCHRONIZED`, or Core returns a definitive rejection and Helpdesk records `SYNCHRONIZATION_FAILED`. |
| `SYNCHRONIZED` | Core status/ACK proves this exact command committed, including its accepted fencing sequence and policy generation; Helpdesk finalization compare-and-set confirms it is still the current assignment version/command. | No retry for the completed command. A new desired assignment creates a new version/key. A replay/status lookup returns historical command result, not a guarantee the grants remain current. | Current ACL is read from Core; a later policy mutation may have changed it. The ACK establishes only that this command committed at the returned generation. | Show assignment complete only after Helpdesk finalization. Current access decisions still come from Core. | Terminal for that assignment attempt. If Helpdesk finalization fails after Core commit, show/recover as `RECONCILIATION_REQUIRED`, not completed. |
| `RECONCILIATION_REQUIRED` | Timeout, lost ACK, transport interruption after send, uncertain commit, Helpdesk finalization failure, or inconsistency between Helpdesk record and Core status. | First perform authenticated status lookup with the same tenant, caller scope and idempotency key. `COMMITTED`: validate the command/fence/generation and finalize with CAS. `IN_PROGRESS`: poll with bounded backoff. `REJECTED`: record failure. Definitive `NOT_FOUND` may retry the same key/payload only while retention guarantees it is authoritative. Status unavailable/ambiguous stays in this state and is retried; never blind retry with a new key. | Core's actual ACL is authoritative; it may reflect the previous grant or the committed replacement. Helpdesk must not infer effective permissions from this state. | Show “Assignment status being reconciled”; no success claim. Gate actions that require completed assignment. | Exit only after authoritative committed status and matching Helpdesk finalization, or definitive rejection is durably recorded. Timeout budget exhaustion raises an operational alert but does not convert unknown to failure/success. |
| `SYNCHRONIZATION_FAILED` | Core returns a definitive durable `REJECTED` outcome or a stable non-retryable validation/authorization result, and Helpdesk persists the failure against that version. | Do not retry unchanged payload/key as a new assignment. Corrected intent requires an authorized new business decision/version and new key; transient failures use reconciliation policy rather than this terminal state. | No mutation for the rejected command. A previous Core grant can remain effective unless the separately approved immediate-revocation policy applies. | Show assignment not completed and a safe reason/action; do not expose sensitive ACL details. Require authorized correction or reassignment. | Terminal for this attempt. If Core definitively rejected but Helpdesk cannot persist that result, remain `RECONCILIATION_REQUIRED` until Helpdesk has recorded it. |

### 8.2 Ordering, fencing and version ownership

`assignmentVersion` is the Helpdesk business version; `policyGeneration` is the Core ACL revision; `workflowRuntimeVersion` is the Core Workflow optimistic-concurrency version. The proposed `fencingSequence` is a separate monotonic per-resource command-order token persisted with the Helpdesk intent. Core stores and compares it only to reject values less than or equal to the last accepted fence. The opaque Helpdesk version token is correlation, not the fencing mechanism. Idempotency prevents duplicate execution of one command; it does not order distinct commands and cannot replace fencing.

If a delayed older command reaches Core after a newer command has committed, Core rejects it as `STALE_ASSIGNMENT_COMMAND`. If an older command commits before the newer command arrives, the newer higher fence may replace it; until that newer command commits, the old command's ACL is the actual Core ACL. Helpdesk must not report its latest intent as synchronized until its own matching command is acknowledged and finalized.

### 8.3 Authorization lag and immediate-revocation decision

Atomic replacement avoids a committed interval in which the old grant is revoked but the new grant has not yet been granted. It does **not** eliminate the interval before Core receives/commits the replacement: the old grant can remain effective and the new actor can lack access. Fail-closed behavior for unavailable Core means protected operations fail closed when authority cannot be checked; it does not by itself revoke a still-committed old grant.

**DECISION REQUIRED — Ánh (business/security), with Bảo (Core feasibility) and Yến (decision owner):**

1. **Option A — Atomic replacement with bounded/observable lag:** retain the old Core grant until the replacement transaction commits; show pending and gate Helpdesk actions requiring synchronization. Define acceptable lag/SLO and escalation. This gives no assertion that old access is immediately revoked.
2. **Option B — Fail-closed assignment fence:** before declaring the assignment change pending, Core must accept a tenant/resource-scoped deny/fence that blocks protected operations for the resource until replacement is committed. Then apply replacement and clear the fence transactionally according to an approved protocol. This may reduce availability and requires a reviewed Core protocol/state beyond a plain ACL replacement.
3. **Option C — Revoke-first:** commit revocation of old access before a later grant; this creates an intentional no-access interval and requires durable staged commands, fencing, reconciliation and explicit handling of partial completion.

No option is selected by this amendment. G0-CONTRACT remains blocked on the policy decision. A response timeout always enters reconciliation; it cannot be used as proof that access was revoked.

## 9. Idempotency, command ledger and recovery (OD-07)

The proposed uniqueness scope is `(tenantId, authenticatedServicePrincipal, operationType, idempotencyKey)`. Resource ID, actor set, operation sets, expected generation, opaque Helpdesk version token, fencing sequence and relevant command semantics are part of a canonical payload fingerprint. Correlation ID is stored for tracing but is not part of uniqueness. Canonicalization rules (encoding, field normalization, set ordering and hash algorithm) must be frozen in R28/G0-DESIGN before implementation.

Proposed transaction lifecycle: reserve the unique key/fingerprint and commit an `IN_PROGRESS` ledger row before execution; then apply the ACL replacement, audit, generation, accepted fence and transition of that ledger row to `COMMITTED` in one Core transaction. A definitive rejection is recorded as `REJECTED` without ACL mutation. If process/connection recovery cannot yet determine whether the transaction committed, expose `OUTCOME_UNKNOWN` as a reconciliation status and do not execute another mutation until the original transaction/ledger outcome is authoritatively resolved. The exact transition/recovery mechanism is a G0-DESIGN item; an `IN_PROGRESS` row is never permission to duplicate execution.

| Ledger status | Meaning and transition | Same-key replay/status response |
|---|---|---|
| `IN_PROGRESS` | Unique key and fingerprint reserved; transaction/command processing has not reached a durable terminal outcome. May transition to `COMMITTED` or `REJECTED`; after recovery timeout it is not assumed rolled back. | Return `IN_PROGRESS` with retry guidance; do not run a concurrent duplicate mutation. |
| `COMMITTED` | ACL replacement, audit, policy generation, accepted fence and committed result are durable in the same Core transaction. | Return the original historical command result and generation. Separately report current ACL/policy state if authorized; do not imply this grant is still effective after later policy changes. |
| `REJECTED` | Definitive no-mutation outcome with stable error classification. | Replay original rejection for same fingerprint. New intent/payload needs a new authorized key/version. |
| `OUTCOME_UNKNOWN` | Recovery cannot yet establish whether commit occurred; not a durable success or failure assertion. | Authenticated status endpoint returns unknown/reconciling and correlation metadata only; client must continue lookup. Core recovery must resolve against transactional ledger/audit state. |

Different fingerprint under the same unique scope is `IDEMPOTENCY_PAYLOAD_CONFLICT` (409 candidate). Concurrent same-key/same-fingerprint requests serialize on the unique key: one executes; others receive the current status/result and never apply a second mutation. Same-key/different-fingerprint requests fail without mutation. Distinct keys are ordered only by the per-resource fencing sequence and expected Core generation, not by idempotency.

The authenticated command-status lookup must bind the verified service principal and tenant to the original ledger scope; it must not reveal another tenant's command. A status lookup is not a fresh authorization grant. For a committed command, distinguish (a) historical command outcome, (b) generation at commit and (c) current effective ACL state, read independently under current Core authorization.

Retention/cleanup is a DECISION REQUIRED for Bảo and Ánh in G0-DESIGN/R28: retain deduplication identity, payload fingerprint, outcome and fence sufficiently long to cover supported retries/reconciliation and prevent replay after deletion; do not delete entries while status is IN_PROGRESS/OUTCOME_UNKNOWN or while a client retry window remains open. After expiry, Core must have an explicit tombstone/epoch or reject old keys/fences so an expired request cannot be replayed as new. Retention duration, cleanup schedule, tombstone period and post-expiry outcome are not selected here.

## 9.1 R28/R29 amendment boundary

The current PR #145 R29 candidate at `6e6e91e2e0f1f68f196eeb492dec371c52f402db` still labels Resolve as an “Atomic resolution write with Core workflow transition” and Confirm as relying on authoritative state without requiring Helpdesk finalization. Since #145 is Ánh's open Draft PR, this remediation does not modify its branch. The proposed changes and precise sequence are recorded in [the separate R29 amendment](../03-applications/helpdesk/r29-pr145-contract-amendment.md); Ánh must apply/review those changes on her branch or incorporate an equivalent amendment.

## 10. Database privilege and threat-model boundary

The selected baseline uses:

- Core migration owner: Core DDL and migration history only.
- Core runtime role: only the privileges necessary for approved Core operations.
- Helpdesk migration owner: Helpdesk DDL and migration history only.
- Helpdesk runtime role: no Core schema/data privileges.
- Public/API roles: no implicit access to protected Core tables.

### Security limitation requiring explicit review

Application-level checks do not, by themselves, prevent code holding broad Core runtime DML privileges from directly modifying ACL tables.

Two threat models must be distinguished:

**Model T1 — Trusted Core runtime boundary:** Core Java transaction orchestration is trusted; least privilege protects service isolation and limits accidental access. Direct SQL misuse by compromised Core runtime is not claimed to be prevented solely by database roles.

**Model T2 — Database-enforced ACL mutation boundary:** Even the Core runtime role cannot arbitrarily alter authorization facts outside approved restricted SQL entrypoints or equivalent database enforcement.

This ADR selects Core Java transaction authorization, but it does not yet select T1 versus T2.

If T2 is required, the team must review whether narrow SQL entrypoints or other physical privilege boundaries can coexist with Core Java policy evaluation.

No grant design is approved until the threat-model choice and effective runtime privilege matrix are recorded.

## 11. Error semantics

The candidate HTTP behavior is aligned with ADR-010 and the R27 Core HTTP draft:

| Situation | Candidate response |
|---|---|
| Missing or invalid authentication | 401 `AUTHENTICATION_REQUIRED` |
| Visible resource without exact operation grant | 403 `FORBIDDEN` |
| Missing or hidden resource, including revoked visibility | 404 `NOT_FOUND` |
| Stale Workflow version or conflicting command | 409 with a specific conflict code |
| Invalid Workflow transition | 422 `INVALID_TRANSITION` |
| Authoritative authorization facts unavailable | 503 `AUTHORIZATION_UNAVAILABLE` |
| Commit outcome unknown | 503 `COMMIT_OUTCOME_UNKNOWN` |

Exact endpoint mapping, visibility policy and command-specific error bodies require R28 approval.

A confirmed pre-commit rollback and an unknown post-commit outcome must not be conflated.

## 12. Alternatives considered

| Decision | Selected | Alternatives rejected or deferred |
|---|---|---|
| Authorization | Core Java transaction | Database-centered authorization deferred for security threat-model review |
| ACL storage | Relational tables | JSONB ACL, external policy engine |
| Locking | Tenant-level guard | Resource-level locks and optimistic-only concurrency |
| Assignment sync | Synchronous Core ACK | Eventual sync, Core querying Helpdesk |
| READ/HISTORY | Current consistent ACL | TTL cache, historical authorization snapshots |
| Audit/idempotency | Transactional audit and ledger | Post-commit-only audit, application logs |
| Database privileges | Separate owner/runtime roles | Shared database user; restrictive SQL entrypoints retained as a threat-model option |
| Recovery | Fail-closed and reconciliation | Blind retries, fail-open behavior |

These alternatives are evaluated for the current MVP and do not prohibit revisiting them through a subsequent ADR.

## 13. Mandatory verification matrix

The row-level contract/runtime cases and evidence states are tracked in [the ADR-015 G0 verification matrix](../verification/r27/adr015-g0-contract-verification-matrix.md). No new case is marked PASS by this documentation change. All runtime/database cases remain NOT RUN or BLOCKED pending implementation and disposable-environment evidence.

### G0 contract acceptance

- [ ] Bảo verifies the lock-order model and PostgreSQL isolation strategy.
- [ ] Bảo verifies the Core runtime privilege threat model.
- [ ] Ánh verifies assignment/ACL acknowledgment and loss-of-response semantics.
- [ ] Ánh verifies version ownership and the R29 contract interaction.
- [ ] R28 validates API/error/idempotency shapes.
- [ ] ADR-010 architectural dependency is resolved.
- [ ] Decision owner records acceptance and the resulting frozen revision.

### G0-DESIGN follow-ups from Bảo's review

- [ ] Review that PostgreSQL `SELECT ... FOR SHARE` requires UPDATE privilege; the final runtime privilege model must not allow request-path code to change `acl_revision` merely to acquire a lock. Select/prove an alternative lock protocol or tightly constrained mechanism.
- [ ] During the approved database cutover, remove cross-service foreign keys (including Helpdesk references to Core `instance_id`/`tenant_memberships`) and the Helpdesk trigger that locks Core `tenant_guards`; do not preserve cross-schema integrity coupling.
- [ ] Verify these properties with disposable PostgreSQL tests under the effective least-privilege roles. Bảo explicitly reported that PostgreSQL runtime verification has not been run.

### T07/T08 and runtime acceptance (not yet run for this target)

- [ ] Authorized GRANT/REVOKE and Workflow operations under effective Core runtime roles.
- [ ] REVOKE vs CREATE, ACTIVATE, TRANSITION and READ/HISTORY.
- [ ] GRANT vs each protected operation.
- [ ] Tenant membership revocation vs active operations.
- [ ] Stale instance version and stale policy generation.
- [ ] Duplicate instance and duplicate command IDs.
- [ ] Lock timeout and deadlock: fail closed.
- [ ] No partial Workflow/history changes on rollback.
- [ ] Policy mutation and audit atomicity.
- [ ] Lost ACK and unknown commit outcome reconciliation.
- [ ] Hidden-resource 404 and visible-denied 403.
- [ ] Forged actor/tenant header rejection.
- [ ] Two-tenant isolation and negative SQL privilege tests.
- [ ] No Helpdesk Core JDBC access or cross-schema privileges.
- [ ] No unapproved Flyway migration activation.

All new runtime acceptance tests are currently NOT RUN or BLOCKED unless separately demonstrated at an identified commit.

Legacy local PostgreSQL tests running as a superuser do not establish least-privilege acceptance.

## 14. Open decisions before persistence implementation

| ID | Open decision | Required reviewer |
|---|---|---|
| OD-01 | T1 vs T2 threat model and SQL enforcement | Bảo + Yến |
| OD-02 | Concrete READ/HISTORY lock protocol and isolation level | Bảo |
| OD-03 | ACL identity keys and tenant/resource uniqueness | Bảo |
| OD-04 | Policy generation increment and batch semantics | Bảo |
| OD-05 | Grant/revoke administrative authority and command schema | Bảo + Ánh |
| OD-06 | Assignment replacement ordering and pending-state behavior | Ánh |
| OD-07 | Ledger retention, in-progress outcomes and replay | Bảo + Ánh |
| OD-08 | R28/R29 error mappings and cross-service reconciliation | Ánh + Yến |
| OD-09 | Role/privilege matrix and T07/T08 acceptance criteria | Bảo + Yến |

### Review disposition recorded at reviewed HEAD `eb6d7b0e`

- **Bảo:** accepts T1 trusted Core runtime for MVP (OD-01); READ COMMITTED and tenant guard first, shared for protected operations and READ/HISTORY, exclusive for policy writes, with `lock_timeout` and `statement_timeout` failing closed (OD-02); accepts the direction for OD-03, OD-04, OD-05 and OD-09, with details deferred to G0-DESIGN. This records his review comment, not PostgreSQL verification or formal ADR approval.
- **Bảo's G0-DESIGN notes:** the `FOR SHARE`/UPDATE privilege issue and removal of cross-service FKs/Helpdesk trigger are listed above. His review says these do not block the ADR direction, but must be resolved before design/cutover.
- **Ánh:** accepts OD-05/OD-07/READ-HISTORY direction with conditions; OD-06 and OD-08 requested changes before G0-CONTRACT/integration acceptance. This amendment makes the contract more explicit but does not convert her verdict to approval.
- **Yến:** decision owner action remains outstanding; this file stays PROPOSED pending fresh independent re-review.

## 15. Consequences

### Benefits

- Core-owned, reusable authorization boundary.
- Deterministic policy revocation model.
- Clear service and database ownership.
- Auditability and retry-safe command processing.
- Explicit integration contract with Helpdesk.
- Reduced risk of redesigning persistence after G0 review.

### Costs

- Tenant-level locking may reduce concurrency.
- Additional ACL and ledger storage.
- More complex transaction orchestration and recovery.
- More negative/security/concurrency tests.
- Separate deployment and migration operations.
- A required threat-model decision for database-level defense.

## 16. Approval and implementation gates

**Gate G0-CONTRACT:** Decision owner selects the direction and Bảo/Ánh complete independent review with the open decisions resolved.

**Gate G0-ARCH:** ADR-010 compatibility and the formal architecture decision are recorded.

**Gate G0-DESIGN:** Relational schema, transaction design and database privilege matrix are approved.

**Gate G0-IMPLEMENT:** Implement Core ACL persistence and related code only after the applicable prior gates are cleared.

**Gate G0-RUNTIME:** Run disposable PostgreSQL migrations, T07/T08, least-privilege denial tests and security negatives before any protected runtime activation.

Until these gates are satisfied:

- No Core ACL V3 SQL migration is activated.
- No runtime grants are applied.
- No protected Workflow HTTP write route is enabled.
- No production cutover occurs.
- No G0 or R27 acceptance is claimed.

**Final status: PROPOSED — SELECTED DIRECTION, INDEPENDENT REVIEW REQUIRED.**
