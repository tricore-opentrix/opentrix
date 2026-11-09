<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# R28 → R27A — Q03 Core enforcement design closure (Workstreams A–C)

**Status: PROPOSED DESIGN FOR INDEPENDENT REVIEW — AI-assisted preparation for Bảo; not Bảo's personal sign-off, not Yến's approval, not G0 acceptance.**
**Scope:** Core ACL-admin assignment commands only (Q03 / Q06 S, conditional). Workflow CREATE/ACTIVATE/TRANSITION and Helpdesk ticket creation are out of scope and need their own proof.
**Gates unchanged:** `Q03_DIRECTION = OWNER-SELECTED CONDITIONALLY`; `Q03_ENFORCEMENT = CHANGES_REQUIRED` (candidate boundary now specified, **unproven**); `Q06 = NOT FROZEN`; `RESEND = DISABLED`; `G0-CONTRACT = BLOCKED`; `0/6 P0 READY`; PR #168 Draft.

Companion documents: [all-writer coverage matrix](r28-q03-all-writer-coverage-matrix.md), [verification test specifications](r28-q03-verification-test-specs.md), [Q06/Q03 evidence pack](r28-r27a-q06-core-decision-evidence-pack.md).

## 0. Result in one paragraph

A Java callback, a unique constraint on receipts, or a trigger on the receipt table cannot make "no ACL mutation commits without a complete receipt" true while any role holds direct DML on the policy tables. This document therefore specifies a **two-layer candidate boundary** that must be reviewed and executed before Final-only is accepted:

1. **Capability layer (authenticity + guard + authority):** policy/receipt tables are owned by a NOLOGIN owner; no runtime role has DML on them; the only mutation entrypoint is one reviewed SECURITY DEFINER function that cannot return after a mutation without having inserted its receipt.
2. **Commit-time invariant layer (completeness backstop):** `DEFERRABLE INITIALLY DEFERRED` constraint triggers (`ENABLE ALWAYS`) on every policy table abort COMMIT unless a complete, linked receipt exists for every policy delta in the transaction.

Neither layer alone is sufficient (§3.3). Neither constrains a PostgreSQL superuser, a table owner or a role that can `SET ROLE` to the owner; those are handled only by an **admission-closed maintenance boundary** (§6) and detective reconciliation, never by a "protected" claim. All of this is **design only**: no SQL has been executed, `X-25`/`T07`/`T08` are **NOT RUN/BLOCKED**.

If review rejects either layer, or X-25 finds any enabled path that commits without a complete receipt, the disposition for Final-only is **REJECTED** (not "fallback to Early Reservation", which remains an unapproved comparison, §8).

## 1. Source baseline

All observed-source claims use these commits; the backend/scripts tree at #168 HEAD `9254fd933a1ed03d0ae67a28f5ff87dc0fe53182` is byte-identical to the Core baseline `5618091dc205b196b551465d2c52def9313ed1fb` (the #168 branch changes `docs/` only).

| Path | Last-change commit | Used for |
| --- | --- | --- |
| `backend/src/main/java/com/tricore/dxos/infrastructure/workflow/HelpdeskService.java` | `fa16f30d5c67a49186b1c36f2babe58d54a15e38` | legacy create/assign direct registry/ACL DML (L78–L88, L200, L350–L352) |
| `backend/src/main/java/com/tricore/dxos/infrastructure/workflow/PostgresWorkflowPersistence.java` | `fa16f30d…` | `guardedTransaction` READ COMMITTED, COMMIT_OUTCOME_UNKNOWN (L365–L450) |
| `backend/src/main/resources/db/helpdesk/policy-schema.sql` | `44283466f1747d55ed39e782d0600e8d09a28427` | policy tables, immutability triggers |
| `backend/src/main/resources/db/helpdesk/schema.sql` | `44283466…` | `helpdesk_policy_lock` trigger (L31–L52) |
| `backend/src/main/resources/db/helpdesk/runtime-grants.sql` | `44283466…` | runtime DML grants (L3–L19) |
| `scripts/helpdesk-local-setup.ps1`, `scripts/helpdesk-local-actor-seed.ps1` | `fa16f30d…` | offline provisioning, owner/setup role |
| `docs/08-decisions/ADR-015-core-workflow-acl-v3-g0.md` | `5618091dc205b196b551465d2c52def9313ed1fb` | Model T1 (L358) |

Static source findings used below (re-derivable by `grep`; none is runtime evidence):

- **F-1** No file in `backend/src/main`, `scripts`, `infra`, `.github` writes `acl_revision`, `workflow_policy_audit`, any receipt/ledger/fence, or admission state. The only `acl_revision` write capability is the grant `GRANT UPDATE (acl_revision) ON tenant_guards TO runtime` (`runtime-grants.sql:12`).
- **F-2** Legacy `HelpdeskService.create/assign` mutate `resource_registry`/`resource_acl` **without advancing G or writing audit**. A D-01 `expectedPolicyGeneration` therefore cannot observe legacy ACL changes at all; legacy writes violate the target invariant by construction.
- **F-3** `stage6_policy_immutability_guard` only forbids identity rewrites, deletes and a *decreasing* `acl_revision`. It permits any increase (`+1000`), permits any `granted` flip, and links nothing to audit or receipt.
- **F-4** `helpdesk_policy_lock` (SECURITY INVOKER) takes `tenant_guards … FOR UPDATE` in BEFORE row triggers on `helpdesk_actors`, `tenant_memberships`, `resource_acl`, `resource_registry`, `workflow_definition_bindings`. This gives direct-SQL writers on those tables tenant serialization (useful), but **not** on `tenant_guards`, `workflow_policy_audit`, or any receipt table, and does not enforce receipt creation.
- **F-5** The runtime role has table-level DML on policy tables with **no tenant predicate in the database**; tenant scope is a Java field (`HelpdeskService`). Cross-tenant DML by the same credential is not blocked by PostgreSQL.
- **F-6** The offline provisioner uses `POSTGRES_USER=helpdesk_setup` (superuser in the Docker image), creates a NOLOGIN owner and uses `SET LOCAL ROLE owner` (`helpdesk-local-setup.ps1:128`). It is a maintenance role, never a runtime-proof role.
- **F-7** ADR-015 Model T1 treats the Core Java runtime as trusted and does not claim DB roles stop a *compromised* Core runtime. The boundary below is **compatible with T1** (it needs no T2) and strictly stronger against every *other* role and against accidental receipt omission. It does not claim protection from a Core runtime that forges the principal it passes (§4.2). ADR-015 is not edited here.

## 2. Candidate enforcement mechanisms evaluated

| ID | Mechanism | All-writer closure | Receipt completeness | Verdict |
| --- | --- | --- | --- | --- |
| M0 | Java `guardedTransaction` callback convention (today) | None. Broad DML (F-5) | None; writer may skip INSERT | **REJECTED** (counterexample: any caller of the runtime role, `UPDATE tenant_guards SET acl_revision=acl_revision+1`) |
| M1 | Unique key + `NOT NULL` columns on receipt only | None | Constrains a row *if inserted*; cannot force insertion | **REJECTED as sufficient** (necessary backstop only) |
| M2 | Trigger on the receipt table | None | Never fires when the receipt is omitted | **REJECTED** |
| M3 | Restricted SECURITY DEFINER executor, DML revoked from runtime roles | Closed for all non-owner/non-superuser roles, *if* grants verified | Closed by function structure (single path) | **CANDIDATE — Layer 1** |
| M4 | Deferred constraint triggers on mutation-side tables requiring a linked receipt | Closed for any writer without trigger-disable rights, even with DML | Closed at COMMIT for linked deltas; cannot prove delta ⇔ receipt semantic equality; forged receipts possible if writer can INSERT receipts | **CANDIDATE — Layer 2 (backstop)** |
| M5 | M3 + M4 | See §3.3 | See §3.3 | **RECOMMENDED CANDIDATE** for independent review |
| M6 | Early Reservation + Deferred Validation | A writer omitting the ledger bypasses ledger-only triggers | Same gap | **UNAPPROVED COMPARISON** (§8) |
| M7 | Row-level security | Owner and superuser bypass; policy tables are tenant-scoped, not receipt-scoped | None | Not selected; may be added for tenant isolation later |

Mechanism M5 is a *candidate*, not an accepted design. Its cost (new owner role, definer function, deferred triggers, role/pool split, legacy cutover) is larger than "just add a receipt table" and must be counted when Bảo decides whether Final-only remains the MVP direction.

## 3. Candidate boundary M5 — specification

### 3.1 Role and ownership model (target; no GRANT is issued by this document)

| Role | Login | Purpose | Allowed on policy/receipt/fence/admission tables | Other |
| --- | --- | --- | --- | --- |
| `core_acl_owner` | NOLOGIN, NOINHERIT, NOSUPERUSER, NOCREATEROLE, NOREPLICATION, NOBYPASSRLS | Owns tables, the `core_acl_exec` schema and all executor/helper functions | All (as owner) | **No login role is a member** (`pg_auth_members` empty for it, or `WITH SET FALSE, INHERIT FALSE`); membership is granted only to the offline migrator during an admission-closed window (§6) |
| `core_acl_exec_rt` (A) | LOGIN, NOINHERIT, no memberships | Core ACL-admin command service | **None**; `EXECUTE` on `assign_replace`, `lookup_receipt` only | Own connection pool; pool reset must `DISCARD ALL` |
| `core_authz_reader_rt` (R) | LOGIN, NOINHERIT | Core authorization snapshot reader | `SELECT` on policy tables it needs today; `EXECUTE` on `reader_guard_share` | **No `UPDATE(acl_revision)`**; no receipt SELECT |
| `core_workflow_rt` (W) | LOGIN, NOINHERIT | Workflow instance writer | `SELECT` on policy tables; `EXECUTE` on `reader_guard_share`; own Workflow table DML | No policy-table DML |
| `helpdesk_rt` (H, target) | LOGIN | Helpdesk service, separate DB/service | **None** on Core policy tables (legacy monolith grant is removed only by the separate cutover) | Exactly the Helpdesk-local tables |
| `core_observer` (O, test-only) | LOGIN, read-only | Snapshots in tests | `SELECT` on everything incl. receipts | Must not exist in production grants |
| `core_migrator` | LOGIN, offline only | DDL/migration | Via `SET ROLE core_acl_owner` | Only during an admission-closed window; credentials not held by any runtime pool |

Required hardening (each is an oracle in X-09/T08, none is assumed):

- `REVOKE ALL … FROM PUBLIC` on the schema, every table, and `REVOKE EXECUTE … FROM PUBLIC` on every function (**PostgreSQL grants EXECUTE on new functions to PUBLIC by default**); `ALTER DEFAULT PRIVILEGES … REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC` for the owner. Publication of each function is one transaction: `CREATE FUNCTION; REVOKE … FROM PUBLIC; GRANT EXECUTE TO exact role`.
- Definer functions: `SECURITY DEFINER SET search_path = pg_catalog, pg_temp`, every object schema-qualified, **no dynamic SQL**, no `EXCEPTION` block (swallowing guard, §4.4), fixed parameter types, no overloads.
- `REVOKE CREATE ON SCHEMA … FROM PUBLIC` and from runtime roles; `REVOKE TEMPORARY ON DATABASE … FROM PUBLIC`; no `TRIGGER`, `REFERENCES`, `TRUNCATE` table privilege to any runtime role.
- No runtime role is a member (direct or inherited) of `core_acl_owner`, `pg_write_all_data`, `pg_execute_server_program`, `pg_write_server_files` or any role with `CREATEROLE`; audit effective membership with `SET` and `INHERIT` options (PostgreSQL 16+; target is 17) and `pg_parameter_acl` for `GRANT SET ON PARAMETER session_replication_role` or similar.
- All new triggers `ALTER TABLE … ENABLE ALWAYS TRIGGER` so `session_replication_role = replica` does not skip them; `session_replication_role` is superuser-only by default and must remain so.
- Executor entry assertions (defense in depth, not the boundary): `session_user = 'core_acl_exec_rt'` (cannot be changed by `SET ROLE`), `current_setting('transaction_isolation') = 'read committed'`, `pg_current_xact_id_if_assigned() IS NULL` (call is the first write of its transaction, so it cannot be composed with Workflow writes).

### 3.2 Receipt schema (candidate; DDL not executed, names not frozen)

Table `core_acl_command_receipt`, owner `core_acl_owner`, no privileges to any other role.

| Column | Type | Rule |
| --- | --- | --- |
| `receipt_id` | uuid PK | server generated |
| `tenant_id` | text NOT NULL | FK `tenant_guards` (RESTRICT) |
| `service_principal_id` | text NOT NULL | canonical verified service identity after the Q04 mapping; **never** client-supplied header |
| `operation_class` | text NOT NULL | `CHECK IN ('ACL_ASSIGN_REPLACE')` for v1 |
| `idempotency_key` | text NOT NULL | length/charset CHECK (Q04) |
| — | UNIQUE | `(tenant_id, service_principal_id, operation_class, idempotency_key)` |
| `fingerprint_version` | smallint NOT NULL | Q04 |
| `request_fingerprint` | bytea NOT NULL | `CHECK octet_length = 32`; computed **in the function** as SHA-256 of the canonical bytes passed in (a caller-supplied digest is untrusted) |
| `resource_type`, `resource_id` | text NOT NULL | FK `resource_registry`; plus resource incarnation (Q04 OPEN) |
| `expected_policy_generation` | bigint NOT NULL | D-01 A input |
| `incoming_fence` | bigint NOT NULL | D-01 A input |
| `outcome` | text NOT NULL | `CHECK IN ('APPLIED','REJECTED_TERMINAL')` (Q02 may restrict) |
| `reject_code` | text | NOT NULL iff `REJECTED_TERMINAL`; NULL iff `APPLIED` |
| `resulting_policy_generation` | bigint | NOT NULL iff `APPLIED` (= expected + 1); NULL otherwise |
| `accepted_fence` | bigint | NOT NULL iff `APPLIED` (= incoming_fence) |
| `audit_event_id` | uuid | NOT NULL iff `APPLIED`; FK `workflow_policy_audit` |
| `change_digest` | bytea | NOT NULL iff `APPLIED`; SHA-256 of the canonical change set, equal to the digest of audit `change_set` |
| `business_token` | text | opaque, per Q04 |
| `recorded_xid` | xid8 NOT NULL | `DEFAULT pg_current_xact_id()` |
| `recorded_at` | timestamptz NOT NULL | `DEFAULT now()` |

Completeness is a table-level `CHECK` over the iff-rules above (a "complete" receipt is *defined* by the CHECK; an `APPLIED` row cannot exist with any effect-column NULL). Immutability: BEFORE UPDATE/DELETE/TRUNCATE triggers raise unconditionally (MVP has no compaction; if Q05 later approves payload compaction, the only permitted UPDATE is a function-driven transition that preserves every identity column). **No role other than `core_acl_owner` has SELECT**; disclosure is only through `lookup_receipt` (§5.3), which authorizes first.

Supporting tables (candidate): `core_acl_resource_fence(tenant_id, resource_type, resource_id, accepted_fence)`; `core_acl_admission(scope PK 'GLOBAL' | tenant_id, state IN ('OPEN','CLOSED'), reason, changed_at)`. A separate fence table avoids altering the legacy `resource_registry`. Audit gets `recorded_xid xid8 DEFAULT pg_current_xact_id()`.

Rejection receipts (Q02) are written only for *authorized, deterministic, monotone-stable* rejections. Candidate set for Bảo's decision: `STALE_POLICY_GENERATION` and `FENCE_NOT_ADVANCING` (G and fence only increase, so the rejection cannot later flip to success on the same inputs), `RESOURCE_TOMBSTONED` (immutable). **Not receipted** (plain rollback, key remains unused): failed authentication, hidden resource/tenant, malformed request, admission closed, lock/statement timeout, deadlock, serialization failure, connection loss, any SQL error, and reversible-state rejections (e.g. inactive assignee) unless Q02 explicitly decides otherwise.

### 3.3 The completeness invariant and why both layers

**INV-1** *For every transaction T that commits a delta to `tenant_guards.acl_revision`, `resource_acl`, `resource_registry`, `tenant_memberships`, `workflow_definition_bindings`, `core_acl_resource_fence`, or `workflow_policy_audit`, there exists exactly one `core_acl_command_receipt` row with `recorded_xid = T`, whose `(tenant_id, resulting_policy_generation, audit_event_id, change_digest, accepted_fence)` equal the actual delta, and conversely every `APPLIED` receipt has exactly that delta.*

Layer 2 (deferred constraint trigger, one function attached `AFTER INSERT OR UPDATE OR DELETE … DEFERRABLE INITIALLY DEFERRED … FOR EACH ROW` to each table above, `ENABLE ALWAYS`) evaluates at COMMIT, on the **final** state (PostgreSQL constraint triggers fire at end of transaction when deferred; they see the committed-to-be rows, unlike the transient INSERT image). It checks, per touched `(tenant_id)`: exactly one audit row with `recorded_xid = pg_current_xact_id()`, `resulting_acl_revision = previous + 1`, `tenant_guards.acl_revision` equals it, and exactly one linked `APPLIED` receipt. Any failure aborts the whole transaction.

| Attack / failure | Layer 1 only | Layer 2 only | M5 (both) |
| --- | --- | --- | --- |
| Writer skips receipt INSERT (the unique-constraint counterexample) | Impossible for roles without DML; owner-role bug in function = **possible** | Aborts COMMIT | Closed except owner/superuser trigger-disable |
| Role with DML inserts a *forged* complete receipt with its own bogus delta | Denied (no INSERT privilege) | **Not detected** (forged receipt passes linkage) | Denied by Layer 1 |
| Bypass tenant guard / authority / fence checks by direct DML | Denied | **Not detected** (structurally valid delta + forged receipt) | Denied by Layer 1 |
| Definer function bug omits receipt | **Not detected** | Aborts COMMIT | Closed |
| Receipt row present but delta differs from receipt (semantic mismatch) | Function code reviewed only | Only structural linkage (digest equals audit digest) | Residual: audit `change_set` vs actual ACL rows equality is **not** DB-enforced; covered by X-25 positive controls and a detective reconciliation job (§6.3) |
| `ALTER TABLE … DISABLE TRIGGER`, `session_replication_role=replica` without ALWAYS, `DROP TRIGGER` | Unaffected | Bypassed by owner/superuser | **Not closed** — §6 |

So the receipt UNIQUE index is necessary (integrity backstop and replay key), complete-row CHECK is necessary, and **neither is sufficient**: sufficiency comes from "no unreviewed path may INSERT/UPDATE policy rows" (Layer 1) plus "an unreviewed path that exists anyway cannot commit" (Layer 2).

## 4. Atomic Final-only transaction sequence (Workstream B)

### 4.1 Sequence (`assign_replace`, one call = one transaction)

| # | Where | Step | On failure |
| --- | --- | --- | --- |
| 0 | Java, no DB | Authenticate caller, derive canonical service identity and tenant, validate shape, canonicalize (Q04), build `p_canonical_request bytea`. Open connection as A (`core_acl_exec_rt`), `BEGIN ISOLATION LEVEL READ COMMITTED`, `SET LOCAL lock_timeout/statement_timeout/idle_in_transaction_session_timeout` (values OPEN; legacy 5 s/15 s are not an approved SLA) | Error before DB: no receipt |
| 1 | DB | Entry assertions (§3.1). Verify tenant exists; scope check of execution principal against tenant/resource using the principal id passed by Java | Rollback, indistinguishable denial, no receipt |
| 2 | DB | `SELECT … FROM tenant_guards WHERE tenant_id=$1 FOR UPDATE` — **first lock**, before any FK-bearing DML (FK checks take `FOR KEY SHARE`; taking `FOR UPDATE` after one is a lock upgrade and a deadlock risk) | Missing → hidden denial; lock timeout → rollback, no receipt |
| 2b | DB | Read `core_acl_admission` (`GLOBAL` and tenant) with a plain SELECT under the guard; `CLOSED` → non-terminal refusal, no receipt, **for replay and lookup as well** (post-restore receipts are untrusted until reconciled) | Rollback |
| 3 | DB | `SELECT` receipt by `(tenant, service_principal, operation_class, key)`. READ COMMITTED gives this statement a **fresh snapshot after the guard wait**, so every earlier same-tenant commit is visible | — |
| 4 | DB | Receipt exists, same `request_fingerprint` and caller authorized for lookup → return historical receipt (`REPLAY`), **zero writes**, no re-check of old G/fence. Exists, different fingerprint → `CONFLICT` (after lookup authorization), zero writes. Lookup authorization failure → same denial as unknown tenant | Rollback (read-only) |
| 5 | DB | No receipt: re-authorize *execution* (current ACL-admin authority of the principal for tenant/resource, current membership, resource ACTIVE), check `expectedPolicyGeneration = tenant_guards.acl_revision`, `incoming_fence > accepted_fence` (`FOR UPDATE` on the fence row, resources in ascending order) | Mismatch of a receipt-eligible class → step 7r; any other failure → rollback, no receipt |
| 6 | DB | Apply managed grant-slice replacement on `resource_acl` (INSERT / UPDATE `granted`; **no DELETE**, the immutability trigger forbids it), `UPDATE tenant_guards SET acl_revision = acl_revision + 1`, set `accepted_fence`, INSERT `workflow_policy_audit` (`previous`, `resulting = previous+1`, `change_set`, `recorded_xid`) | Any error → statement-level abort, whole call rolls back |
| 7 | DB | **Final write:** INSERT complete `APPLIED` receipt (`audit_event_id`, `change_digest`, G, fence). Last statement of the function; no `EXCEPTION` block; no `ON CONFLICT DO NOTHING` | Unique/CHECK/FK failure → exception → **everything in steps 6–7 rolls back** |
| 7r | DB | Receipt-eligible deterministic rejection: INSERT `REJECTED_TERMINAL` receipt only (zero G, fence, ACL, success-audit delta). Layer 2 sees no policy delta and requires none | Same as 7 |
| 8 | Java | `COMMIT`. Deferred Layer 2 triggers run inside COMMIT; a violation makes COMMIT fail and rolls back | COMMIT error response ⇒ outcome is **UNKNOWN**, not "failed" (§5) |
| 9 | Java | Only after COMMIT success acknowledge to the client; no network call inside the transaction; Helpdesk CAS is a separate local transaction | — |

Ordering note (honest): "receipt last" is **not** what makes the commit atomic — PostgreSQL transaction atomicity does. It is a structural rule so that a receipt failure is an exception in the same statement as the mutation; INV-1 is guaranteed by Layer 1 structure plus Layer 2 at COMMIT.

### 4.2 Authentication limit

PostgreSQL authenticates the **role** (A), not the end principal. The principal id and its provenance are asserted by the Core service (Model T1). The function re-checks the principal's *current authority from database state* (step 5), so a stale or revoked principal is rejected, but a Core runtime that deliberately passes another principal's id is a T1-trusted behavior and is **not** prevented. A signed assertion verified in the database would be a T2-style addition and is not proposed; it is listed as an open question for ADR-015 OD-01 owners.

### 4.3 Failure and bypass analysis

| Case | Outcome under M5 |
| --- | --- |
| Writer skips receipt INSERT entirely | Layer 1: non-owner role has no DML ⇒ `42501`; function always inserts. Layer 2: any other committed delta ⇒ COMMIT aborts. Owner/superuser: §6 |
| Receipt INSERT unique conflict (same scoped key) | Unreachable after step 3 under the guard; if reached it is a protocol violation: exception, whole call rolls back. Never `ON CONFLICT DO NOTHING` then continue |
| Receipt INSERT SQL failure | Exception ⇒ ACL/G/fence/audit of the same call roll back |
| Incomplete / malformed receipt | Table CHECK rejects the row; Layer 2 rejects a missing/unlinked receipt |
| Savepoint rollback / exception swallowing | A caller's `ROLLBACK TO` undoes mutation **and** receipt together (same statement). Inside the function no `EXCEPTION` block (verified by a catalog static check in X-25). Java must not catch-and-continue after an executor error: the transaction is aborted |
| Direct DML bypass | Denied by privilege (Layer 1) or aborted at COMMIT (Layer 2) for every non-owner, non-superuser role; legacy H with DML **cannot coexist** with an enabled Layer 2 (its writes have no receipt, F-2) — cutover dependency |
| Rollback before COMMIT | No effect, no receipt, key unused |
| Unknown COMMIT outcome | Outcome unknown; resolved only by authorized status lookup of a *committed* receipt (§5.3); a later rollback or empty lookup does not disprove commit |
| Deterministic rejection vs infrastructure failure | Rejection receipted only for the Q02 set; lock/statement timeout, deadlock, serialization, I/O, auth failure never produce a receipt |

## 5. Concurrency, recovery, retention (Workstream C)

### 5.1 Same-key behavior (serialized by the tenant guard)

| Schedule | Result |
| --- | --- |
| Original-first | Original holds the guard; retry blocks on step 2; after original COMMIT the retry's step-3 statement sees the receipt ⇒ `REPLAY` |
| Retry-first | Retry executes (it is a valid first arrival); late original sees receipt ⇒ `REPLAY` of the retry's result. Same-key/same-payload ⇒ at most one effect |
| Concurrent same key/same payload | One winner via guard; others replay |
| Same key, different fingerprint after a committed or tombstoned receipt | `CONFLICT`, no write. **Not guaranteed** against an erased rolled-back attempt (Final-only does not bind an attempt before commit); Helpdesk must keep the immutable original intent |
| Delayed original after retry/recovery | Same guard → replay/conflict; after durable retirement (Q05) → refused without execution |
| Rollback before COMMIT | Next arrival executes once after current G/fence/auth checks; a higher G/fence from other commands may reject it (fresh retry) |
| Lost ACK after possible COMMIT | Uncertain; §5.3 |
| READ COMMITTED | Each statement re-snapshots after the lock wait; `REPEATABLE READ`/`SERIALIZABLE` are forbidden for the executor (assertion in §3.1) because their snapshot is fixed before the guard wait |

### 5.2 Fixed lock order (candidate; ties to #165 §1.1 and ADR-015 T1)

1. `tenant_guards(T)` — `FOR UPDATE` (writers, maintenance, admission closer), `FOR SHARE` through the lock-only helper (readers). Multiple tenants: ascending `tenant_id`.
2. `core_acl_admission` — plain read (no lock) after the guard; a closer updates it **and** then takes every tenant guard `FOR UPDATE` ascending in the same transaction, so it drains in-flight executors and every later arrival reads `CLOSED`. No extra lock class ⇒ no new cycle.
3. receipt scoped key — read; the INSERT at the end takes the unique-index entry.
4. authority/membership/ACL rows — read under the guard.
5. `core_acl_resource_fence` and `resource_registry` rows — `FOR UPDATE`, ascending `(resource_type, resource_id)`.
6. Workflow instance rows — **not touched** in an ACL-admin transaction; if ever needed they come after 5 and ascending by instance id (legacy `FOR UPDATE`, `PostgresWorkflowPersistence` L282).
7. Mutations in primary-key order; audit INSERT; receipt INSERT.

Rules: never `SHARE → UPDATE` upgrade; never take `FOR UPDATE` on `tenant_guards` after an FK-checking DML in the same transaction; timeouts are `SET LOCAL`; timeout/deadlock ⇒ full rollback and **no stale-authorization fallback**. Deadlock-freedom is *not* claimed; X-06/X-09 verify detection and rollback only.

Reader locking without `UPDATE(acl_revision)`: PostgreSQL `SELECT … FOR SHARE` needs `UPDATE` on at least one column, so readers use a **lock-only** definer helper `reader_guard_share(text)` (owner `core_acl_owner`, fixed `search_path`, body is a single `SELECT 1 FROM tenant_guards WHERE tenant_id=$1 FOR SHARE`, `EXECUTE` to R and W only, PUBLIC revoked in the publishing transaction). The helper establishes a lock, **not** the receipt invariant, and does not authorize reads. Transaction-scoped advisory locks are the alternative and are not recommended: they need an all-writer namespace proof and are invisible to the existing `helpdesk_policy_lock` mechanism.

### 5.3 Status-first recovery (`lookup_receipt`)

- Caller: A or a dedicated lookup role; never direct table SELECT. Definer function; first authorizes lookup (original service principal, tenant, operation class, current scope; wrong tenant, wrong principal, forged header, expired credential ⇒ the same indistinguishable denial and **no** existence, fingerprint, G or fence disclosure).
- Returns exactly one of `COMMITTED(receipt)`, `UNRESOLVED`. `UNRESOLVED` is returned for empty lookup, in-flight, expired, admission-closed and unavailable. **A missing receipt, an empty lookup or an `ON CONFLICT DO NOTHING` result never means "not committed".** An empty lookup taken after the guard wait proves only "no committed receipt as of now and no in-flight holder on this tenant"; it cannot exclude a delayed original that has not arrived. A third state `CLOSED_NOT_COMMITTED` would require a durable scoped retirement that is **not designed** (Q05/Q08 OPEN); until then Helpdesk stays in `RECONCILIATION_REQUIRED` and resend stays DISABLED.
- A historical receipt is not current authorization; Helpdesk still performs its own current-intent CAS.

### 5.4 Retention, tombstone, cleanup, restore (Q05, minimum safe rules)

- No TTL deletion, no key reuse, no identity deletion in the MVP (Final-only has no durable attempt binding, so a cleanup window would let a retired key become fresh). Full receipts retained; payload compaction needs a separate owner decision and, if approved, a function (not DML) that keeps all identity columns.
- Cleanup, resend and delayed original all go guard → key; there is no identity-absence window because nothing is deleted.
- **Restore:** backup taken before a commit lacks its receipt; restoring ACL/G/fence from it does not reconstruct dedup identity, and a restored `core_acl_admission` row may say `OPEN`. Therefore admission closure for restore **cannot be a row in the restored database**; it is the §6 maintenance boundary (executor credentials/network absent) followed by a first-write `CLOSED`, reconciliation of acknowledged-or-uncertain command identities against Helpdesk intents and tombstones, and a reopen by break-glass role with evidence. If any acknowledged or uncertain commit cannot be accounted for, admission and resend stay closed.
- This revises the evidence-pack assumption "no new API / epoch field" (§2.4): a *DB-visible admission gate* is needed to make "admission closed" testable rather than procedural; whether it is a table, a flag or a role state is a Q05/Q07 decision (`core_acl_admission` above is a proposal).

## 6. Admission-closed maintenance boundary (privileged / break-glass / offline)

PostgreSQL superusers, table/function owners and roles that can `SET ROLE` to the owner can bypass **both** layers (disable trigger, `DROP`, `CREATE OR REPLACE FUNCTION`, direct DML, `session_replication_role`). Ordinary `GRANT/REVOKE` does not protect against them, and this document does not claim it does.

### 6.1 Rule

No owner/superuser/migrator DML on policy, receipt, fence, audit or admission tables is allowed while `GLOBAL` admission is `OPEN` or while any executor/reader/writer credential can connect. Such operations (migration, repair, manual ACL fix, restore, key retirement, cleanup compaction, role/grant change, trigger maintenance) are **offline operations**:

1. **Close:** executor and writer credentials disabled at the connection layer (pooler/network/`pg_hba`, or `ALTER ROLE … NOLOGIN` followed by termination of their backends), then `admission GLOBAL = CLOSED` through the closer transaction (§5.2). Evidence: closure timestamp, backend list showing no A/R/W sessions.
2. **Operate** as `core_migrator` with `SET ROLE core_acl_owner`, with statement logging to an append-only external sink. Maintenance that changes effective policy must also write audit and a receipt-equivalent **maintenance record** (separate table/type; it is not an idempotency receipt and must not be mistaken for one). Layer 2 triggers stay enabled; a maintenance change that needs them disabled needs a documented, reviewed disable/enable pair.
3. **Reopen criteria** (all required): (a) schema/trigger/function/grant catalog diff against the reviewed manifest is empty (`ENABLE ALWAYS` present, no unexpected overloads, `prosecdef`/`proconfig`/owner/ACL as specified, no `EXCEPTION` in `prosrc`); (b) role-membership/`SET` option/`pg_parameter_acl` audit clean; (c) reconciliation report (§6.3) shows INV-1 holds over the whole table set; (d) restore only: command identities and fences reconciled with Helpdesk intents, canonical service mapping verified; (e) independent sign-off recorded; (f) reopen executed by a named break-glass role, not by the migrator that did the work.

### 6.2 Properties that are procedural, not database-enforced (declared)

Closing credentials at the network layer; keeping `core_acl_owner` membership empty between windows; restoring with the DB unreachable; external sink for statement logs; reopen sign-off. These are **operational controls to be audited**, not enforced invariants.

### 6.3 Detective control (not a preventive claim)

A reconciliation query/job (read-only, run by O) that proves INV-1 for every tenant: audit chain contiguous (`resulting = previous+1`, no gaps), every `APPLIED` receipt ↔ exactly one audit row ↔ equal `change_digest`, no policy row changed without a corresponding audit (compare `resource_acl` state against replaying the audit change sets from the last verified snapshot), no receipt without audit for `APPLIED`. Runs before every reopen and on a schedule. A detective control finds a bypass after the fact; it does not make the boundary non-bypassable.

## 7. Evaluation of "restricted Core mutation executor" (the task's candidate)

| Concern | Finding |
| --- | --- |
| Ownership | Tables and functions owned by one NOLOGIN role with no login membership. The table owner can always re-grant itself; hence the owner must be unreachable online (§6). Functions owned by a *different* owner would not help: the table owner is still the root of trust |
| SECURITY DEFINER safety | Fixed `search_path = pg_catalog, pg_temp`, schema-qualified names, no dynamic SQL, no overloads, EXECUTE to exact roles, PUBLIC revoked in the publishing transaction, no `EXCEPTION`, assertions on `session_user`; definers inherit the owner's table privileges, so each function is a privilege-escalation surface and needs line-by-line review |
| PUBLIC privileges | Default `EXECUTE` on functions and default table/schema privileges must be revoked and checked in a catalog test |
| `SET ROLE` | Prove no runtime role can reach the owner via direct, inherited or `SET`-option membership; `session_user` assertion in the function is defense in depth |
| Trigger controls | `ENABLE ALWAYS`; no `TRIGGER`/`ALTER` ownership for runtime roles; catalog check `tgenabled = 'A'` |
| Migration roles | Offline only, behind §6; the Docker `helpdesk_setup` superuser pattern (F-6) is acceptable only for disposable local setup and never as a proof role |
| Cost | New roles, schema, 2 definer functions + 1 helper, deferred triggers, fence/admission tables, pool split, removal of H's DML (separate cutover). This is a real redesign relative to "add a receipt table"; Final-only is cheaper than Early Reservation only if the cost of this boundary is the same for both (it is, §8) |
| Verdict | **Enforceable against non-owner/non-superuser paths if the catalog and X-25/X-09 evidence pass; no claim against owner/superuser; NOT PROVEN today** |

## 8. Early Reservation + Deferred Validation (comparison only)

Not approved, not an automatic fallback. It needs the same Layer 1 (a writer that skips the ledger bypasses a ledger-only deferred trigger), adds a nullable transient state, a finalize `UPDATE` privilege and a deferred validator. The boundary cost in §7 applies identically, so rejecting Final-only on enforcement grounds does **not** make Early Reservation acceptable; it would need its own owner decision and the same X-12/X-23/X-24/X-25 oracles.

## 9. Q02–Q05, Q07 — decisions still required

| Q | Needed from | Open items |
| --- | --- | --- |
| Q02 | Bảo + Yến | Final rejection-class set and which are receipted; status/error/wire precedence; rejection audit vs none; compacted rejection replay |
| Q03 | Bảo + Yến | Accept M5 (or an alternative) as the enforcement boundary; accept the legacy-H cutover dependency; accept that owner/superuser protection is procedural |
| Q04 | Bảo + Ánh | Canonical bytes, versioning, integer/decimal encoding, set ordering, unknown/duplicate fields, service-identity mapping and migration, resource incarnation, golden vectors V-01..V-09 |
| Q05 | Bảo + Yến + operations | Retention duration/privacy budget, compaction, key retirement authority, restore reopen authority, DB-visible admission gate design |
| Q07 | Bảo + Yến | Lock-only helper vs advisory, exact signatures, pool/credential split, who may EXECUTE, `SET`/membership policy, timeouts |
| New | Bảo | Whether a signed-principal assertion (T2-style) is wanted; today it is out of scope (T1) |
| New | Ánh | Q08 manual-reconciliation authority, cancellation proof, CAS convergence (consumer side, unchanged) |

## 10. Disposition

| Item | Value |
| --- | --- |
| `DESIGN_DIRECTION` | Final-only Receipt **conditionally acceptable** (owner-selected, Yến ACCEPT WITH CONDITIONS, direction only) |
| `ENFORCEMENT_READINESS` | **CHANGES_REQUIRED** — candidate M5 specified, no executed evidence; X-25/T07/T08 NOT RUN |
| `Q06_CONTRACT_FREEZE` | **NOT FROZEN** |
| `RESEND_PERMISSION` | **DISABLED** |
| `G0_CONTRACT` | **BLOCKED** |
| `R27A_IMPLEMENTATION_PERMISSION` | **NOT GRANTED** (0/6 P0 READY) |
