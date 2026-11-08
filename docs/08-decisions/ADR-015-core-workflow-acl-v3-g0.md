# ADR-015 — Core Workflow ACL V3 / G0: Atomic Authorization Contract

**Status:** PROPOSED — AWAITING INDEPENDENT REVIEW  
**Decision owner:** Yến  
**Reviewers:** Bảo (Core, PostgreSQL, transactions, security), Ánh (Helpdesk, service contracts, assignment synchronization)  
**Decision date:** Pending formal acceptance  
**Tracking:** R27 Step 03 / PR-0b  
**Related:** ADR-010 (PR #159), R28, R29 (PR #145), R31, T07/T08, Issue #138  
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

## 7. Core ACL administration contract

Grant/revoke must be performed using an authenticated, authorized Core command.

The caller must not be able to assign themselves resource grants through ordinary Workflow mutation requests.

The contract must distinguish:

- The end user initiating a business operation.
- The authorized service principal executing administrative synchronization.
- The effective actor whose grant changes.
- The audit actor and source of authority.

A service credential alone must not authorize arbitrary tenant-wide grant mutation.

For assignment-driven replacement, prefer one Core atomic command capable of applying the approved revocation/grant change set together.

The exact command shape, policy-administrator authority, tenant scope and revoke-before-grant behavior require explicit G0 approval.

## 8. Helpdesk synchronization contract

Helpdesk owns the business assignment and assignmentVersion.

Core owns the effective Workflow ACL.

A Helpdesk assignment change must use a durable synchronization state rather than assuming an HTTP request and business transaction are atomic.

Proposed states:

- `PENDING_SYNCHRONIZATION`
- `SYNCHRONIZED`
- `SYNCHRONIZATION_FAILED` or another specifically approved recoverable state

These state names and transitions remain subject to R29 contract review.

Helpdesk must not claim an ACL revocation has completed solely because its business assignment changed.

For lost Core acknowledgment, Helpdesk must reconcile using authoritative Core command status before declaring synchronization complete or safely retrying.

Any interim access by the old assignee must be addressed explicitly by the business contract and fail-closed rules, not hidden as an implementation detail.

## 9. Idempotency and audit contract

For effective policy mutation commands, the proposed durable ledger records at least:

- Tenant scope.
- Authorized caller identity.
- Operation type.
- Idempotency key.
- Canonical payload fingerprint.
- Authoritative command status.
- Committed outcome and policy generation where applicable.
- Correlation and audit references.

Required behavior:

- Same key, same scope, same payload: replay the authoritative committed result.
- Same key, different payload: conflict.
- Concurrent same-key commands: no duplicate effective mutation.
- Rollback: no committed successful policy mutation or success audit.
- Unknown commit outcome: reconcile rather than blind retry.

The ledger schema, retention, in-progress states and replay-response semantics require G0/R28 approval.

Broader Workflow CREATE idempotency and Helpdesk business idempotency remain governed by A2 and R28/R29. This ADR must not silently finalize those separate contracts.

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

### G0 contract acceptance

- [ ] Bảo verifies the lock-order model and PostgreSQL isolation strategy.
- [ ] Bảo verifies the Core runtime privilege threat model.
- [ ] Ánh verifies assignment/ACL acknowledgment and loss-of-response semantics.
- [ ] Ánh verifies version ownership and the R29 contract interaction.
- [ ] R28 validates API/error/idempotency shapes.
- [ ] ADR-010 architectural dependency is resolved.
- [ ] Decision owner records acceptance and the resulting frozen revision.

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