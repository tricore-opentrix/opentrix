<!-- SPDX-FileCopyrightText: 2026 TRICORE contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# ADR-010: Core/Helpdesk service boundary and database ownership

**Status:** PROPOSED; not approved. Review by Bảo and Ánh is required. Production cutover BLOCKED.
**Decision date:** pending (no approval recorded).
**Tracking:** R27 (Checklist row 29); related R28, R31, R32b, R35.
**Supersedes:** nothing yet. If accepted, it supersedes only the single-backend deployment shape of SYS-ADR-01-B, and only for Core/Helpdesk (see Baseline conflict).
**Numbering:** ADR-009 is the Compose demo stack ([PR #123](https://github.com/tricore-opentrix/opentrix/pull/123)). ADR-015 is the planned Core ACL v3 / G0 contract (PR-0b, not yet submitted).

## Scope and provenance [ADR-010 addition]

Documentation only. `main` has no `core-service`/`helpdesk-service` Gradle module and none of the target Core/Helpdesk migrations, runtime grants or Core Workflow routes. The legacy Flyway V1–V4, `db/helpdesk/*.sql` and the backend HTTP routes exist on `main` and are unchanged. Sections marked **[Draft, verbatim]** are copied unchanged from the unmerged local draft "ADR-009: Core and Helpdesk database ownership cutover" (retained in the verified R27 worktree backup). Sections marked **[ADR-010 addition]** or **[Correction]** are new. Draft status, verbatim:

> **Decision status: proposed for review. Production cutover BLOCKED.** Source baseline: `187dbd2ea6935966f5c4cceb95ad9c3c53708a2e`, with uncommitted Stage 1–2D module changes. No migration or grant in this ADR is active.

## Context [ADR-010 addition]

Checklist row 29 (column O) records a team decision of 05/11/2026 ("Ý 2"): split a headless `core-service` from a `helpdesk-service` that owns ticket business, give each service its own schema, database role and Flyway chain, and use ArchUnit to block applications from importing Core internals. Today, ArchUnit on `main` (`CoreDependencyRulesTest`, PR #96) constrains only the Core packages. No implemented rule yet forbids Helpdesk from using Core JDBC adapters. That rule is required future enforcement. The documented fallback ("Ý 1": one process with module boundaries kept) applies if the Golden Path does not pass through APISIX by 15/11. Yến decides it after asking the team. **It has not been activated.**

## Baseline conflict [ADR-010 addition]

| Baseline document on `main@187dbd2` | Current content |
| --- | --- |
| `docs/01-architecture/system-architecture.md:18,84-95,434` | SYS-ADR-01-B Modular Monolith is a team-selected design direction, and its formal sign-off is PENDING. Option C "Microservices per Core" is Deferred. Source impact: "keep one backend project". SYS-ADR-03, 04, 05, 07, 09, 10 and 11 are OPEN. |
| `docs/01-architecture/core-application-boundary.md:7,24,264,268` | PROPOSED. SYS-ADR-01=B with "no claim of deployable Core services". SYS-ADR-04 records only a previous Application-enforced direction. |
| `docs/01-architecture/dependency-rules.md:13` | Lists SYS-ADR-01 B (Modular Monolith). |
| `docs/00-project/scope-and-mvp.md:9,46` | PROPOSED. "independent microservices" is OUT for the MVP. |
| `docs/00-project/product-vision.md:91` | A microservice split is out of scope for the current MVP. |
| `docs/00-project/project-overview.md:85,98` | Modular Monolith rationale. Microservice decomposition is not promised. |
| `docs/02-core/data/data-architecture.md:41` | "a Spring Boot modular monolith, not four compulsory microservices". |

ADR-010 is PROPOSED. **No approval of "Ý 2" exists in the repository.** If accepted, ADR-010 would supersede only SYS-ADR-01-B's single-backend deployment shape, and only for Core/Helpdesk, by selecting the deferred option C for that pair. SYS-ADR-01-B module boundaries, SYS-ADR-02 ports/adapters and dependency inversion, SYS-ADR-06 data ownership and SYS-ADR-08 would remain applicable. For the open SYS-ADR-04, it proposes Core-boundary enforcement of Workflow resource authorization only. All listed documents require alignment in a follow-up PR after acceptance.

## Proposed rules [ADR-010 addition]

| ID | Rule |
|---|---|
| D1 | Core is headless and provider-neutral. It owns shared Identity, Workflow and Data mechanisms. It must not encode Helpdesk tickets, assignment, resolution or Helpdesk tables. |
| D2 | Helpdesk owns ticket use cases, ticket data and its business membership. |
| D3 | Helpdesk must not call `PostgresWorkflowPersistence` or any Core JDBC adapter, must not hold grants on Core tables, and must not query the Core schema. Core must not query the Helpdesk schema. |
| D4 | Cross-service interaction uses only an explicitly approved, authenticated Core API contract. The candidate is the [R27 Core Workflow HTTP contract](../01-architecture/r27-core-workflow-http-contract.md); R28 owns the OpenAPI form. |
| D5 | Core verifies identity at its ingress (`CurrentPrincipal.requireVerified()`). It decides Workflow resource authorization from Core-owned facts, in the same Core transaction as the write ([authorization boundary](../01-architecture/r27-core-authorization-boundary.md), design A). |
| D6 | Each service owns its schema, migration owner, runtime role and Flyway history. |
| D7 | Database ownership follows the draft decision below. |
| D8 | Production Workflow HTTP write routes stay unregistered until G0 (proposed ADR-015), runtime least privilege and the concurrency gates are cleared with recorded review. |

## Decision [Draft, verbatim]

Use **B: controlled new private Core and Helpdesk schemas** as the target. Fresh installations require separately reviewed migration chains for each schema. Existing installations require a staged, write-frozen export/import and reconciliation, then an explicit role and traffic switch. Do not replay historical V1–V4 in the new schemas or call a Flyway baseline equivalent to data migration. Additive changes to the legacy schema are preparation only; they cannot by themselves remove the current Helpdesk runtime access to Workflow tables and the same-schema foreign keys.

## Exact current inventory and target ownership [Draft, verbatim]

| Current source | Relations and significant columns/constraints | Current physical owner | Target owner | Required split |
| --- | --- | --- | --- | --- |
| `db/migration/V1__create_requests.sql` | `requests`: UUID PK; title/description/type/status/timestamps and CHECKs | Legacy Flyway schema | Helpdesk historical prototype | Preserve bytes/history; decide whether rows map to live Helpdesk tickets or remain archived. |
| `db/migration/V2__add_request_workflow.sql` | Adds `requests.assignee_id`, `resolution`, `version`; `request_status_history` FK to `requests` and transition CHECK | Legacy Flyway schema | Helpdesk historical prototype | Keep history, never rewrite V2; export/import only if product requires it. |
| `db/migration/V3__create_workflow_persistence.sql` | `workflow_definitions`, states, transitions, instances, transition history; exact definition/state FKs, immutable definition triggers, instance resource index, history PK `(instance_id,resulting_runtime_version)` | Legacy private Workflow schema | Core | New Core migration chain must establish equivalent reviewed constraints without claiming it is V3 history. Preserve old rows and order. |
| `db/migration/V4__seed_workflow_definitions.sql` | `document-review` and `incident-resolution` v1 states/transitions | Legacy private Workflow schema | Core | Reconcile exact definition content and existing instances; seed only absent exact versions under new migration/owner approval. |
| `db/helpdesk/policy-schema.sql` | `tenant_guards.acl_revision`, memberships, resource registry, grants, definition bindings, policy audit; tenant/resource/actor FKs and immutability triggers | Offline disposable Helpdesk schema, not managed Flyway | Core **effective Workflow** policy | Design Core-owned relations/version/audit; no cross-schema FK to Helpdesk. Helpdesk business membership remains separate. |
| `db/helpdesk/schema.sql` | `helpdesk_actors` FK to membership; `helpdesk_requests` FK to Workflow instance and membership, plus ticket/assignee/resolution fields; policy lock triggers | Offline disposable Helpdesk schema, not managed Flyway | Helpdesk | Replace Workflow FK with opaque Core instance ID plus HTTP reconciliation. Replace membership FK only with Helpdesk-owned membership. |
| `db/helpdesk/definition.sql` | `it-helpdesk` v1 Workflow definition | Offline disposable, not V4 Flyway | Core definition content, subject to independent source/rights review | Import through Core-owned provisioner; preserve exact version/content and avoid duplicate seed. |
| `db/helpdesk/runtime-grants.sql` | Helpdesk runtime SELECT on policy, ticket **and Workflow** tables; INSERT on Workflow instance/history; UPDATE on instance state | Offline disposable grant script | Separate Core/Helpdesk grants | Never apply this grant file to the target schemas. Revoke legacy grants only after cutover and validation. |

The old schema has **same-schema** FKs; its Helpdesk request → Workflow instance and policy binding → Workflow definition FKs must not be reproduced across target schemas. Target Core SQL may refer only to Core relations. Target Helpdesk SQL may refer only to Helpdesk relations. Cross-service consistency is an authenticated command/acknowledgment and reconciliation problem, not a cross-schema join.

### Legacy Helpdesk runtime privileges [Correction]

The `runtime-grants.sql` row above and the Helpdesk runtime row below understate the current legacy grants. The exact grants are in `backend/src/main/resources/db/helpdesk/runtime-grants.sql:3-19` at `187dbd2`. This is an offline disposable script, so deployed state is UNKNOWN.

| Legacy privilege (current) | Objects |
| --- | --- |
| USAGE | the schema |
| SELECT | `tenant_guards`, `tenant_memberships`, `resource_registry`, `resource_acl`, `workflow_definition_bindings`, `helpdesk_actors`, `helpdesk_requests`, `workflow_definitions`, `workflow_definition_states`, `workflow_definition_transitions`, `workflow_instances`, `workflow_transition_history` |
| INSERT | `resource_registry`, `resource_acl`, `helpdesk_requests`, `workflow_instances`, `workflow_transition_history` |
| UPDATE (column-limited) | `tenant_guards(acl_revision)` (the file says it is needed for row locks); `resource_acl(granted)`; `helpdesk_requests(assignee_id, assignment_version, resolution)`; `workflow_instances(current_state, runtime_version, lifecycle, updated_at_seconds, updated_at_nanos)` |

**Isolation risk.** The legacy Helpdesk runtime can register resources, insert and flip ACL grants, bump the tenant ACL revision, and write Workflow instance state and history. These are the facts that D3/D5 assign to Core. The intended target is that the Helpdesk runtime has no USAGE, SELECT or DML on Core tables, and that Core ACL facts change only through authenticated Core commands. Remove these privileges only through the reviewed cutover; never apply them to target schemas.

## Role and Flyway matrix [Draft, verbatim]

| Role | Legacy current evidence | Target Core schema | Target Helpdesk schema |
| --- | --- | --- | --- |
| Legacy migration/owner | `WorkflowMigrations` requires one private schema, guarded TLS/config and `flyway_schema_history`; actual deployed grants/history not inspected | Read-only during migration verification; no automatic rebaseline | Read-only during migration verification |
| Core migration owner | Not present | DDL and Flyway history for Core only, separate credential; no Helpdesk SQL | None |
| Core runtime | Stage 2A config exists, Flyway disabled; no deployed role evidence | Narrow SELECT/DML required for Workflow and effective ACL, no DDL or policy-administration shortcut | None |
| Helpdesk migration owner | Offline SQL owner role in disposable tests | None | DDL and Flyway history for Helpdesk only |
| Helpdesk runtime | Current `runtime-grants.sql` grants Workflow SELECT/INSERT/UPDATE in one schema | **No USAGE, SELECT or DML on Core tables** | Narrow ticket/business DML only |
| PUBLIC/API roles | V3 and Helpdesk SQL revoke selected privileges | No Core data privilege | No Helpdesk data privilege unless separately reviewed |

V1–V4 source SHA-256, unchanged in this worktree:

| Migration | SHA-256 |
| --- | --- |
| V1 | `b496698d7695982d47d6004caa7dcf6047d4baf1b158503302b09ae45cad17ac` |
| V2 | `da39b56224cff56a65a37793a89595cb3c374c1b8516a950568b2dfa27cd7ad7` |
| V3 | `15d615162c09b0c843680cf0c3b9fe48b16cd637877eb91215d8698cd7bc4832` |
| V4 | `40ee5a6c3a357d7ebca6d198c9981760868fc872121e8caece6ae6e86634a3ef` |

These are file SHA-256 values, **not Flyway's stored checksum values**. The actual `flyway_schema_history` rows in each deployed installation are UNKNOWN. The pinned Workflow event-trigger manifest and `WorkflowMigrations` location/schema checks must be reviewed before a new migration chain is accepted. Core currently sets `spring.flyway.enabled=false` and has no V1–V4 resource bundle. Do not turn Flyway on or point it at old history by configuration alone.

**[Correction, local audit 09/11/2026, not repository evidence]** Since the draft, the local `core-service` JAR also packages candidate Core `V1__create_core_workflow.sql` and `V2__create_core_acl.sql` under `db/migration`. A version collision with the backend's V1/V2 on the backend classpath is possible but UNVERIFIED.

## Strategy comparison [Draft, verbatim]

| Criterion | A: additive staged changes in legacy schema | B: new private schemas and controlled data migration |
| --- | --- | --- |
| Existing database/history | Easier initial compatibility; old Flyway history remains in place | Requires explicit export/import and new history, never checksum rewrite or blind baseline |
| Data retention and FKs | Old rows remain; Helpdesk/Workflow FKs remain coupled until removed | Preserve legacy read-only copy, reconcile row counts, stable IDs, definitions, histories and references before switch; replace cross-service FKs with reconciliation |
| Concurrent writes | Dual writes create divergence unless serialized; final write freeze still needed | Freeze legacy writes for final snapshot, verify no in-flight transaction, import and reconcile before switching traffic |
| Rollback | Easy before new writes; harder after grants and FK removal | Revert traffic to untouched legacy only before new-side writes; afterward use an audited reverse reconciliation, never silent rollback |
| Privilege isolation | Cannot claim isolation while old grant file/runtime remain | Separate schemas, roles and credentials make denial testable |
| CI/fresh install | Old chain reproducible, target separation unproved | Requires new migration suites and role-denial tests for both schemas |
| Operational cost | Lower early cost; may postpone the real cutover | Higher: export/import, downtime window, new migrations, integrity checks and runbooks |

**Recommendation:** B for the target and fresh installs. For an upgrade, make non-destructive preparation while the legacy system stays authoritative, then require a reviewed cutover window. Strategy A alone is insufficient for the target security boundary.

## Upgrade sequence and rollback gate [Draft, verbatim]

1. Inventory the actual legacy schema, row counts, FK graph, `flyway_schema_history` versions/checksums, roles, grants and active connections. Do not infer deployed state from source files.
2. Review new Core and Helpdesk migration chains, event-trigger manifest, role DDL, mappings for V1/V2 prototype rows and `it-helpdesk` definition. Run each chain twice on distinct disposable fresh databases. Nothing is baselined against a guessed state.
3. Create target schemas/roles with no cross-schema privileges. Export from a consistent legacy snapshot; import into target via a controlled offline process, not cross-schema runtime SQL. Preserve IDs, definition versions, instance timestamps/history order, ticket links and authorization audit. Compute counts and content digests for every group.
4. Freeze legacy writes; wait for in-flight transactions; take a final snapshot/delta and reconcile. Reject switch on any orphaned ticket reference, definition mismatch, missing history, policy-version mismatch or unclear commit outcome.
5. Switch Core and Helpdesk credentials/traffic only after independent grant-denial and authenticated API tests. Helpdesk requests grant/binding changes through Core commands with a durable idempotency key. A Helpdesk-side revocation is `PENDING_SYNCHRONIZATION` until Core acknowledges its committed version. Lost acknowledgment requires status lookup before retry.
6. Keep legacy data read-only for a defined observation window. Before any target write, rollback may switch traffic back after confirming the legacy snapshot is unchanged. After target writes, rollback requires an audited reverse reconciliation; a blind switch would lose writes or resurrect revoked access.

Core grant/revoke and Workflow mutation must lock policy generation first, then exact resource/actor facts, then the Workflow instance row in one Core transaction. This serializes a committed revoke against a transition. A write committed before the revoke may complete; a revoke committed first must deny the write. Deadlock/lock-timeout aborts fail closed. Unknown commit outcomes require authorized reconciliation and must not be retried blindly. This design is not yet implemented.

## Test and CI scope [Draft, verbatim]

The latest disposable PostgreSQL 17.11 run executed nine legacy Workflow integration suites: 195 cases, zero failures or skips. Its full wrapper gate **failed** because 37 Helpdesk tests require `HELPDESK_DISPOSABLE_URL` at the exact loopback `:55439/helpdesk_disposable_test` plus setup/token prerequisites, and six Keycloak tests require a Keycloak/OIDC fixture. The Workflow script uses a random port and does not supply either fixture. Do not relax its zero-skip gate or treat the 43 skipped cases as PASS. New-schema migration, row-copy, role-denial, reconciliation and two-connection Core ACL tests are **NOT RUN** until the target migration chain and cutover mappings are reviewed.

## Intended design versus demonstrated evidence [ADR-010 addition]

| Item | State | Evidence |
|---|---|---|
| D1–D8 | Proposed design | This ADR and the linked R27 records |
| Gradle modules, 61 Core class moves (59 byte-identical, 2 modified) | Local only, not on `main` | Local audit 09/11/2026, not in the repository. PR-1 scope excludes the `lockInstance` hunk. |
| D3 Helpdesk independent of Core JDBC | **Not met** | Local `HelpdeskService` still constructs and calls `PostgresWorkflowPersistence` |
| D4 Core HTTP contract | Specified, not registered | [contract](../01-architecture/r27-core-workflow-http-contract.md) |
| D6 schema/role/Flyway ownership | Not demonstrated | Local Flyway execution BLOCKED; runtime roles NOLOGIN; no grants approved |
| T07 Core transaction tests (5 cases) | Local developer evidence, not CI | Disposable PostgreSQL 17.11, run as superuser; least privilege not shown |

## Unresolved decisions

[Draft, verbatim]

- Are V1/V2 request prototype rows part of the retained Helpdesk product record, or archival-only?
- Which deployed installations and Flyway history rows actually exist, including V3/V4 and any untracked V5 candidate?
- What is the approved Core effective-membership source and durable Helpdesk-to-Core synchronization protocol?
- Who owns new schema/role credentials and the reviewed migration chain, including event-trigger manifest updates?
- What downtime, reverse-reconciliation and independent security review gates are acceptable?

[ADR-010 addition]

- Approval or rejection of the SYS-ADR-01-B supersession for Core/Helpdesk, the SYS-ADR-04 direction above, and the MVP scope change.
- The Core effective-membership source and synchronization protocol (third draft question): proposed for ADR-015 (PR-0b, not yet submitted).
- Confirmation that ADR-011 to ADR-014 are reserved for R37 and ADR-015 for PR-0b.

Until answered and verified on disposable databases, production cutover, Core ACL persistence, privilege clearance and Workflow HTTP writes remain **BLOCKED**.
