<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# R28 → R27A — Q03 verification test specifications (Workstream D)

**Status: EXECUTION-READY SPECIFICATIONS. NOTHING IN THIS FILE HAS BEEN EXECUTED. Every test is `NOT RUN` or `BLOCKED`; there is no PASS and no FAIL.**
Reason: no authorized disposable PostgreSQL environment was provided for this task, the executor/receipt/fence/admission objects do not exist in the repository, and Q02–Q05/Q07 are undecided. A documentation check, a lint, or this file is not runtime evidence.

Companions: [enforcement design](r28-q03-core-enforcement-design.md) (M5, INV-1, §4.1 sequence, §5.2 lock order), [all-writer matrix](r28-q03-all-writer-coverage-matrix.md), [mandatory verification plan](r28-r27a-mandatory-verification-plan.md), [T07/T08 plan](r28-postgresql-locking-privilege-t07-t08-plan.md). Test IDs are preserved from those documents.

## 0. Status vocabulary and rules

| Status | Meaning |
| --- | --- |
| `PASS` | Executed on the pinned environment, evidence artifacts present and digest-listed, independent reviewer re-ran the oracle. **None today.** |
| `FAIL` | Executed, explicit FAIL condition observed. **None today.** A source-level counterexample (e.g. W-03) is not a FAIL. |
| `NOT RUN` | Specification is complete enough to run once the listed prerequisites exist. |
| `BLOCKED` | Cannot be specified to the final byte/SQL until the named decision or object exists. |

Rules: never mark PASS without artifacts; exact commands and a non-zero executed-test count are required (no hidden skipped suites); setup/owner/superuser sessions never stand in for runtime roles; a test that only proves a Java callback convention does not count; a negative-lookup is never accepted as proof of non-commit.

## 1. Common harness (prerequisites for every test)

| Item | Requirement |
| --- | --- |
| Database | Disposable PostgreSQL 17, pinned image **digest** and minor version, no production DSN, loopback only, destroyed after the run (the existing local-provisioner isolation checks are a reference; its superuser `helpdesk_setup` is used **only** for setup) |
| Roles | Actual `core_acl_exec_rt` (A, second pool = A2), `core_authz_reader_rt` (R), `core_workflow_rt` (W), `helpdesk_rt` (H, pre- and post-cutover grants as two variants), `core_observer` (O, read-only, test-only), `core_migrator` (setup), owner `core_acl_owner` (NOLOGIN). Grants are produced by the **reviewed grant script under test**, not by the test |
| Fixtures | Reset per phase: tenant T1 with G=10, resource R1 fence=5, verified service S1 with dedicated ACL-admin authority, immutable key K6, canonical payload P6 (G=10, fence=6, business token V6), no receipt; tenant T2 as scope-denial control; positive-control keys K7.. |
| Barriers | **Named, not sleeps.** (a) "in-flight original" = a setup-owner session `S0` holding `tenant_guards(T1) FOR UPDATE` in an open transaction; (b) "blocked" is confirmed when `pg_stat_activity.wait_event_type='Lock'` and `pg_blocking_pids()` names `S0` for the target backend; (c) pause "mutation applied, receipt INSERT pending" via a **test-only BEFORE INSERT trigger on the receipt table** installed by the owner in the disposable DB that blocks on `pg_advisory_xact_lock(K_BARRIER)` held by the harness, or `RAISE` for fault cases (the trigger DDL is recorded in the evidence and removed afterwards); (d) "after receipt INSERT, before COMMIT" is natural: the call has returned, the transaction is open; (e) lost ACK = TCP proxy that forwards `COMMIT` but drops the server reply, then closes |
| Observation | O snapshots **after the server-side transaction end** (use `pg_stat_activity` state / `pg_locks` absence, not client timing): `tenant_guards.acl_revision`, `resource_acl` rows, `core_acl_resource_fence`, `workflow_policy_audit`, `core_acl_command_receipt`, plus per-scoped-identity counts |
| Fault tools | `pg_terminate_backend`, `pg_cancel_backend`, `SET LOCAL lock_timeout/statement_timeout`, proxy drop; `ISOLATION` assertions via `SHOW transaction_isolation` captured in the timeline |
| Evidence layout (to be created by the run, **not now**) | `docs/verification/r28/evidence/<TEST>/<run-id>/` containing `env.json` (image digest, PG minor, driver, source/schema/grant SHAs), `roles-grants.json` (catalog snapshot incl. memberships with SET/INHERIT, default privileges, `pg_parameter_acl`), `commands.txt` (exact commands), `timeline.ndjson` (session-tagged, SQLSTATE, txn start/end), `lock-graph.json`, `snapshots/before.json`, `snapshots/after.json`, `result.json` (executed test count, skipped=0), `SHA256SUMS` |
| Independent review | Yến (or delegate) re-derives the oracle from `snapshots/*` and `roles-grants.json`; AI-generated analysis is not that review |

## 2. Test specifications

### X-12 — same-key concurrent execution produces at most one committed effect

| Field | Specification |
| --- | --- |
| Preconditions | Fixtures above; S1 authorized; selected `assign_replace` implemented; Q04 canonical vectors fixed; no receipt for K6 |
| Actor / role | Sessions A and A2 (`core_acl_exec_rt`, separate backends, same identity K6/P6); S0 and O as setup/observer; R for status |
| Transaction sequence | For each schedule, run `BEGIN READ COMMITTED; SELECT core_acl_exec.assign_replace(<P6>, K6); COMMIT;` on A and A2: **(1)** original-first: A runs to "after receipt INSERT, before COMMIT"; A2 starts, assert blocked on guard; A COMMITs; A2 completes. **(2)** retry-first: A paused by S0 at step 2 (guard); A2 arrives later but is released first by test ordering (S0 releases; both queue; record actual winner). **(3)** in-flight original + late original after retry winner. **(4)** A rolled back at barrier (c) with `RAISE`; A2 then executes. **(5)** COMMIT sent, ACK dropped; R status; A2 retry. **(6)** changed-payload control P6' same K6 after committed winner |
| Expected | Per scoped identity: at most 1 committed `resource_acl` replacement, 1 G advance (10→11), 1 fence advance (5→6), 1 success audit, 1 receipt. Loser gets authorized `REPLAY` (same fingerprint) or `CONFLICT` (P6'), zero writes. Rollback case: no effect, no receipt; the next admissible arrival executes once after current G/fence/auth |
| FAIL | Two committed effects; staged-receipt absence treated as permission to execute again; resend with changed G/key; success returned before COMMIT; stale admin regrant; receipt disclosed to an unauthorized reader; `REPEATABLE READ` accepted. Do **not** assert a conflict against an erased rolled-back fingerprint |
| Evidence | `evidence/X-12/<run-id>/` (one sub-folder per schedule 1–6) |
| Status | **BLOCKED** (Q02–Q05, Q07; executor not implemented; no authorized PG) |

### X-13 — authenticated receipt lookup, historical replay, no information leak

| Field | Specification |
| --- | --- |
| Preconditions | Complete `APPLIED` receipt for K6 (created through the real executor); then S1's current authority or tenant scope is revoked/changed in a second phase |
| Actor / role | R or lookup role calling `lookup_receipt` as the original verified service/tenant/operation/key; controls: wrong tenant T2, wrong principal, wrong operation class, forged header, expired credential, revoked authority, unknown key |
| Transaction sequence | (1) lookup while A holds its call before COMMIT (guard held): expect `UNRESOLVED`. (2) lookup after COMMIT: expect `COMMITTED(receipt)` identical to the committed row. (3) revoke S1's lookup authority (via the executor path), repeat lookup. (4) each control call. (5) lookup while `GLOBAL` admission is `CLOSED` |
| Expected | Authorized caller sees the immutable historical result only; after revocation/hidden tenant the denial is byte-identical to the unknown-tenant response (same status, error body, comparable latency class), with no receipt/G/fence/fingerprint/existence leak. `UNRESOLVED` for absent/in-flight/expired/unavailable/closed. A direct `SELECT` on the receipt table by R/W/H/A is `42501` |
| FAIL | `UNRESOLVED` interpreted or documented as non-commit; any difference distinguishing "exists but forbidden" from "absent"; historical grant opens current access; conflict metadata leaked; receipt readable without `lookup_receipt` |
| Evidence | `evidence/X-13/<run-id>/`, including response bodies and a diff of denial responses |
| Status | **BLOCKED** (status/security mapping, Q05) |

### X-23 — late original, tombstone, cleanup and restore admission

| Field | Specification |
| --- | --- |
| Preconditions | MVP rule: no TTL deletion. Variants: (a) full retained receipt; (b) payload-compacted tombstone **only if Q05 approves compaction**; (c) a never-admitted key with and without a durable scoped retirement fixture (only if Q05 defines one); (d) backup taken before an acknowledged commit |
| Actor / role | A (original), A2 (retry), cleanup/controller function role (definer), O, break-glass reopen role, restore operator (offline) |
| Transaction sequence | (1) A original and cleanup/compaction both start; barriers force **cleanup-first** and **resend-first** in turn; both use guard → key. (2) Original Assign and changed-payload same key after tombstone. (3) First arrival of a never-retired admissible key (positive control: executes once). (4) First arrival of a key with durable retirement. (5) Restore: take backup B0 before commit C1; commit C1 and acknowledge; restore B0 into a fresh instance with executor credentials absent; first write `GLOBAL = CLOSED`; attempt A call, lookup, and Helpdesk intent replay while closed; run reconciliation; reopen via break-glass; replay |
| Expected | Full retained receipt replays; compacted/retired identity returns the approved historical/expired terminal disposition without execution; no deletion window; lateness alone never expires a never-retired key; while `CLOSED` every command and lookup is refused with a non-terminal result and **no write**; reopen refused until reconciliation covers C1 (identity, G, fence, incarnation, service mapping); zero duplicate ACL/G/fence/audit effects |
| FAIL | Tombstone delete/reuse window; local Helpdesk cancellation treated as Core closure; restore opens on empty lookup or on stale backup; a restored `OPEN` row honored without the offline closure procedure; new principal/ID bypass; assignment proof claimed for Create |
| Evidence | `evidence/X-23/<run-id>/` incl. restore procedure transcript and reconciliation report |
| Status | **BLOCKED** (Q05 compaction/restore/admission contract; Create has separate coverage) |

### X-24 — deterministic rejection receipt and safe replay

| Field | Specification |
| --- | --- |
| Preconditions | Q02 rejection-class set chosen (candidate: `STALE_POLICY_GENERATION`, `FENCE_NOT_ADVANCING`, `RESOURCE_TOMBSTONED`); K6 submitted with G=9 (stale) |
| Actor / role | A (rejected original), A2 (same-key replay after the state becomes execution-eligible), controls |
| Transaction sequence | (1) A: authorized stale-G call; barrier before COMMIT; A2 waits on the guard; A COMMITs; A2 replays. (2) A2 changed payload → conflict. (3) Policy later becomes eligible for the old inputs (impossible for monotone classes: assert it cannot; for any reversible class, assert it is **not** receipted). (4) Malformed, unauthenticated, hidden resource, admission-closed, lock timeout, deadlock, SQL error, killed backend: assert **no** receipt row |
| Expected | One immutable `REJECTED_TERMINAL` receipt; replay returns the same rejection; zero ACL/G/fence/success-audit delta (Layer 2 sees none and requires none); changed semantics conflict; infrastructure/unknown failures leave no receipt and no key binding |
| FAIL | Rejection later turns into success on the same identity; wrong prior result returned; fabricated terminal state for rollback/infra failure; any policy delta on a rejection; reversible-state rejection receipted without a Q02 decision |
| Evidence | `evidence/X-24/<run-id>/` |
| Status | **BLOCKED** (Q02 set, audit/visibility, Q04, Q05) |

### X-25 — no mutation COMMIT without a complete receipt (including direct-DML bypass)

This is the reject-or-accept test for Final-only enforcement. Any single FAIL below ⇒ the candidate boundary is **REJECTED**, X-25 is not waived, Early Reservation is not thereby approved.

| Sub | Attempt (role) | Expected | FAIL if |
| --- | --- | --- | --- |
| a | Positive: `assign_replace` complete (A) | Commit; INV-1 holds: 1 audit, G+1, 1 `APPLIED` receipt, `change_digest` = audit digest, effects equal receipt | Any mismatch |
| b | Fault after revoke/grant/G/fence/audit and **during** receipt INSERT (`RAISE` hook) (A) | Exception; all staged effects rolled back; snapshot equals before | Any residual row, G, fence or audit |
| c | Receipt INSERT unique conflict forced after mutation: the test hook (BEFORE INSERT on the receipt table) inserts a row with the same scoped key from an autonomous owner session (a conflict is otherwise unreachable under the guard, so this only exercises the protocol-violation branch) | Whole call aborts, all staged effects rolled back, no `ON CONFLICT DO NOTHING` path | Mutation commits, or the conflict is swallowed |
| c2 | Hold the guard in S0, commit a complete receipt for K6 as owner, release S0 while A waits at step 2 | A finds the receipt at step 3 → `REPLAY`/`CONFLICT`, zero writes | A mutates again |
| d | Test-only owner-run function mutates policy and **omits** the receipt, exposed to A for this test only (simulates a definer bug) | `COMMIT` fails (Layer 2), nothing persists | Delta persists with no receipt |
| e | Incomplete/malformed receipt: NULL effect column on `APPLIED`; `REJECTED_TERMINAL` receipt alongside a policy delta; `change_digest` ≠ audit digest; `recorded_xid` of another transaction | CHECK `23514` or COMMIT abort | Any commits |
| f | Savepoint: `SAVEPOINT s; SELECT assign_replace(..)` with injected receipt failure; (i) `ROLLBACK TO s; COMMIT` (ii) continue after error then `COMMIT` | (i) no effect (ii) `25P02`, COMMIT behaves as ROLLBACK | Mutation persists without receipt |
| g | Static catalog scan of executor/helper `prosrc`: no `EXCEPTION`, no `ON CONFLICT DO NOTHING` on the receipt, no dynamic `EXECUTE`, `prosecdef`, `proconfig` search_path, owner, `proacl` | Matches reviewed manifest | Any deviation |
| h | Direct DML by A, R, W, H(post-cutover), O: INSERT/UPDATE/DELETE/TRUNCATE on every policy table, receipt, fence, admission, audit; `UPDATE tenant_guards SET acl_revision = acl_revision+1000`; `SELECT … FOR UPDATE`; `LOCK TABLE` | `42501` for all; row/ACL counts unchanged | Any statement succeeds |
| i | `SET ROLE core_acl_owner`, `SET SESSION AUTHORIZATION`, `ALTER TABLE … DISABLE TRIGGER`, `SET session_replication_role = replica`, `CREATE FUNCTION`/`CREATE TABLE` in the schema, `CREATE TEMP TABLE` shadowing, `GRANT`, `COPY … PROGRAM` (A, R, W, H) | `42501` / `22023` | Any succeeds |
| j | **Legacy variant** (pre-cutover H with `INSERT/UPDATE` on ACL tables and `UPDATE(acl_revision)`) performs W-01/W-02-style writes | Layer 2 aborts COMMIT (no receipt); documents that legacy H cannot coexist with the boundary | Legacy write commits |
| k | **Negative-claim control:** owner or superuser disables the deferred triggers and commits a delta | Commit succeeds (**known, declared limitation**); the reconciliation job (design §6.3) flags the delta | Reconciliation misses it, or the doc/report claims protection |
| l | Every enabled path as a subcase: original, retry, delayed original, maintenance, recovery, nested function | Each either uses `assign_replace` or is shown unreachable for online roles | An enabled path with a different mutation entry |

Evidence `evidence/X-25/<run-id>/` per sub-case. Status **BLOCKED** (Q03 boundary acceptance, Q07 roles, executor objects absent; current source is `CHANGES_REQUIRED`, not an executed FAIL).

### T07 — actual-role PostgreSQL transaction, lock and atomicity enforcement

| Field | Specification |
| --- | --- |
| Preconditions | Same path and fault stages as X-25; real production-shaped connection settings; `SHOW transaction_isolation = 'read committed'` recorded |
| Actor / role | A (executor), S0 and O; Helpdesk local finalize is a **separate** Helpdesk-side transaction |
| Transaction sequence | Kill/terminate A (1) before the guard, (2) after guard, (3) after mutation before receipt (hook), (4) after receipt, before COMMIT, (5) after `COMMIT` sent with ACK dropped. Capture all snapshots **before** any retry phase. Then separate retry phase: R status → A2 retry according to X-12 |
| Expected | (1)–(4) leave initial ACL/G/fence/audit/receipt exactly; (5) is UNKNOWN until an authorized status shows a committed receipt; a later rollback or empty lookup cannot disprove commit; confirmed commit contains every effect; no network/remote side effect inside the transaction |
| FAIL | Partial rows; success emitted before COMMIT; a cleanup exception rewrites a confirmed or unknown outcome; an uncertain result auto-resends; timeout/deadlock falls back to stale authorization; deadlock-freedom claimed |
| Evidence | `evidence/T07/<run-id>/` |
| Status | **NOT RUN / BLOCKED** (approved actual path and fault harness) |

### T08 / X-09 — least privilege, role escalation, direct SQL, unauthorized write denial (C-20..C-23, C-25)

| Field | Specification |
| --- | --- |
| Preconditions | Grants produced by the reviewed script; `roles-grants.json` captured first |
| Actor / role | A, R, W, H, O, migrator, owner (each as itself) |
| Catalog assertions | (1) No runtime role has any privilege on policy/receipt/fence/admission tables except the exact allow-list (R/W `SELECT` on policy tables; none on receipts). (2) `has_column_privilege(<each>, 'tenant_guards','acl_revision','UPDATE') = false`. (3) No effective membership (direct/inherited/`SET` option) from any runtime role to `core_acl_owner`, `pg_write_all_data`, `pg_execute_server_program`, `pg_write_server_files`, any `CREATEROLE`/`SUPERUSER`/`REPLICATION` role. (4) `pg_parameter_acl` has no `SET` grant on `session_replication_role`. (5) `PUBLIC` has no schema `USAGE/CREATE`, table, or function `EXECUTE` privileges; default privileges revoked. (6) `pg_trigger.tgenabled = 'A'` for every protected trigger. (7) Every definer function: owner, `proconfig` `search_path=pg_catalog, pg_temp`, `proacl` exact. (8) No unexpected overloads of executor names; no extensions beyond manifest. (9) Temporary-table privilege revoked |
| Behavioral order tests | R `FOR SHARE` via helper first, A revoke blocks until R ends; reverse order: R blocks then authorizes freshly after revoke commits (revoke-first denies protected data and history). Two same-tenant A/B writers never SHARE→UPDATE upgrade. Timeouts and a test-only deadlock fixture ⇒ full rollback, distinct SQLSTATEs (`55P03` lock timeout, `57014` statement timeout, `40P01` deadlock), no stale-authorization fallback |
| Expected | Only `EXECUTE` on the allow-listed functions works; every other write/escalation is `42501`; helper holds a lock and mutates nothing (`acl_revision` unchanged) |
| FAIL | Any privilege outside the allow-list; reader granted `UPDATE(acl_revision)`; non-blocking invalid lock; protected data readable after a serialized revoke; an authorization denial mislabeled as a deadlock proof; setup/owner session used as a proof role |
| Evidence | `evidence/T08-X-09/<run-id>/` |
| Status | **BLOCKED** (Q07 roles/mechanism; no deployed-catalog snapshot) |

### X-16 / X-26 — consumer-facing Q08 reservation / CAS conflicts (coordinate with Ánh)

| Field | Specification |
| --- | --- |
| Ownership | Helpdesk-side tests belong to Ánh/R29; Core provides the receipt and status oracle. This file does **not** edit R29 #145 |
| Preconditions | Helpdesk durable exact-version reservation exists before dispatch; Core receipt `APPLIED` available through `lookup_receipt` |
| Actor / role | Helpdesk service (H, separate DB), Core executor (A), authorized manual operator, unauthorized-operator control |
| Transaction sequence | Core COMMIT then Helpdesk CAS: same-current success; superseded CAS failure; restart; lost ACK; expiry; competitor reassignment; unauthorized cancel; blind-resend attempt; unknown status |
| Expected | Core history/receipt and newer Helpdesk state preserved; a per-attempt conflict/reconciliation record is persisted; reservation and gates remain on unknown/CAS conflict; no refreshed-version CAS retry; same-current convergence only under an explicitly approved rule; manual closure only with authorized audited evidence; no automatic worker in MVP |
| FAIL | Silent reservation release; reverse transition or regrant; false success; operator blind resend; unapproved cancellation; timeout converted to `SYNCHRONIZATION_FAILED` |
| Evidence | `evidence/X-16-X-26/<run-id>/` |
| Status | **BLOCKED** (Core/security joint closure; Q08 release/cancel authority). **Requested of Ánh:** confirm the Helpdesk-side fixtures and the status/receipt fields she needs from `lookup_receipt` |

## 3. Summary

| Test | Status | Blocking reason |
| --- | --- | --- |
| X-12 | BLOCKED | Q02–Q05, Q07; executor absent; no authorized PG |
| X-13 | BLOCKED | status/security mapping; Q05 |
| X-23 | BLOCKED | Q05 compaction/restore/admission; Create separate |
| X-24 | BLOCKED | Q02 rejection set; Q04; Q05 |
| X-25 | BLOCKED | Q03 boundary acceptance; Q07 roles; objects absent |
| T07 | NOT RUN / BLOCKED | approved path and fault harness |
| T08 / X-09 | BLOCKED | Q07; no deployed-catalog snapshot |
| X-16 / X-26 | BLOCKED | joint closure; Q08 authority (Ánh) |
| **Executed PASS / FAIL** | **0 / 0** | no run authorized or performed |
