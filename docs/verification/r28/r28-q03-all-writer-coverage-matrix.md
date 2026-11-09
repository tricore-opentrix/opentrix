<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

## Acceptance closure update — baseline ee048142, 2026-11-09

Trạng thái hiện hành ở [acceptance report](r28-q03-m5-enforcement-acceptance.md).
Report run 05 và bảng preflight cũ bên dưới là lịch sử, không đại diện cho lần chạy mới.
[Source inventory](evidence/REVIEW/20261109-m5-acceptance-closure/source-inventory.json)
pin SHA-256, Git blob và last commit của 17 file liên quan. Production source/grants
không đổi so với baseline. PostgreSQL catalogs mới chỉ thuộc disposable prototype;
không có deployed catalog hoặc external credential/writer inventory.

| Writer | Đối chiếu source → quyền thực tế trong PostgreSQL disposable | Phần chưa đủ phạm vi closure | Status |
| --- | --- | --- | --- |
| W-01 | `HelpdeskService.create/grant` vẫn INSERT registry/ACL; role `helpdesk_rt` trong fixture bị từ chối policy DML (T08), legacy ACL omission bị deferred trigger từ chối (X-25) | Chưa cutover source/deployment; Create ngoài scope assignment; X-17 thiếu | BLOCKED |
| W-02 | Source assignment vẫn UPDATE/INSERT ACL; fixture H không DML, A chỉ EXECUTE assignment | Consumer CAS/reservation, X-16/X-26, cutover chưa có | BLOCKED |
| W-03 | `runtime-grants.sql:12` vẫn UPDATE(acl_revision); fixture actual roles không có quyền cột này, direct +1000 bị từ chối | Không phải bằng chứng revoke grant tại deployment | BLOCKED |
| W-04 | `helpdesk_policy_lock` là legacy invoker lock helper; reader-first/revoke-first dùng target helper khác | Chưa thay dependency trigger/FK và chưa kiểm chứng legacy cutover | BLOCKED |
| W-05 | Legacy immutability không liên kết receipt; fixture capture/deferred/immutable catalog và negative probes được thực thi | Không có deployment của Layer 2, chưa bao phủ policy writer khác assignment | BLOCKED |
| W-06 | Setup script chạy privileged; probe chứng minh owner disable trigger và bypass được | Closed-admission procedure mới là fixture thăm dò; operations chưa duyệt | BLOCKED |
| W-07 | Actor seed INSERT membership; target runtime không membership DML | Chưa có approved offline exclusion hoặc membership executor | BLOCKED |
| W-08 | `PostgresWorkflowPersistence` chỉ viết Workflow; fixture W SELECT policy/helper, không policy DML | Revoke-first mới kiểm chứng synthetic ACL executor, chưa Workflow integration | BLOCKED |
| W-09 | Java wrapper bảo toàn COMMIT_OUTCOME_UNKNOWN; DB SIGTERM/timeout/deadlock thực thi trên prototype | Không Java transport mapping, ACK-drop thật hoặc postmaster crash | BLOCKED |
| W-10 | Migration/bootstrap source có DDL capability; fixture migrator không SET owner hoặc publish function | Chưa có deployed migration/admission-closed catalog diff | BLOCKED |
| W-11 | Source tooling chỉ inspection; fixture catalog/grants/defaults/memberships được chụp | Không chạy tooling trên deployed environment; read-only path không chứng minh writer closure | BLOCKED |
| W-12 | `schema.sql.assign_replace`: actual A EXECUTE; omission/forgery/conflict/savepoint/concurrency probes | Không ingress/Java bridge; approved rejection/retention contract và independent review thiếu | BLOCKED |
| W-13 | Fixture chặn membership/binding/registry/authority/admission DML, không enable online entrypoint | Mỗi loại writer cần protocol/exclusion riêng; revoke fixture privileged không thay online writer proof | BLOCKED |
| W-14 | Actual lookup role/status-first được chạy; không cấp repair DML | Manual reconciliation/CAS convergence chưa có consumer contract | BLOCKED |
| W-15 | Runtime DELETE bị deny, immutable trigger và retained original replay được kiểm tra | Duration, compaction, durable key retirement và authority chưa chốt | BLOCKED |
| W-16 | Fixture admission-closed/reconcile và closed-backup restore được chuẩn bị/chạy theo report | Không approved stale/OPEN-backup/PITR/reopen procedure hoặc operations inventory | BLOCKED |
| W-17 | Chỉ metadata inventory các container; không kết nối staging/production | Deployed roles, memberships, pooler, external jobs/credentials chưa truy cập | BLOCKED / UNINVENTORIED |

Không row nào CLOSED. Legacy Helpdesk cutover chỉ là kế hoạch đã được Ánh chuẩn bị:
inventory → approved Core interface/consumer reservation → admission-closed disable
legacy writers → verify grants/FK/trigger dependencies → independent approval → reopen.
Không triển khai hoặc thay grant production trong gói này.

## Lịch sử preflight 02 — không phải trạng thái hiện hành

**2026-11-09 verification update (historical):** [M5 test-only report](r28-q03-m5-verification-report.md)
ghi nhận authorized preparation tại baseline `cecee84453cf5eaec16548959415c243675d56c4`,
nhưng preflight fail closed do credential safety chưa xác lập; Docker local cũng không
hoạt động. **0 DB tests; không writer nào CLOSED.** Production source/grants không đổi.
Prototype nguồn `161dc0d5be0c5c367155eddb33ad6d8fe0eba753` chỉ là bounded assignment harness.

Mỗi W giữ source location, required privileges, existing bypass và proposed enforcement
ở §1–2 bên dưới. Closure ledger mới bổ sung executed test/missing evidence và status:

| Writer | Executed test / missing evidence | Closure status |
| --- | --- | --- |
| W-01 | Không chạy. Legacy create/registry/ACL vẫn ở source; target H denial + X-17 + separate Create proof thiếu | BLOCKED; R27A cutover scope only |
| W-02 | Không chạy. Assignment replacement prototype có; legacy Helpdesk DML chưa bỏ, X-16/X-26/CAS và cutover thiếu | BLOCKED |
| W-03 | Không chạy. Prototype không UPDATE(acl_revision) grant; runtime-grants.sql hiện hành vẫn có; actual-role T08 thiếu | BLOCKED |
| W-04 | Không chạy. Legacy lock-only trigger không tạo receipt; prototype guard order/lock graph chưa execute | BLOCKED |
| W-05 | Không chạy. Legacy immutability không chứng minh receipt; actual delta/deferred trigger catalog + negative probes thiếu | BLOCKED |
| W-06 | Không chạy. Offline setup/superuser không là runtime proof; admission-closed maintenance và reconciliation thiếu | BLOCKED |
| W-07 | Không chạy. Seed membership là privileged; target membership writer không enable, offline seeding trước admission | BLOCKED; exclusion chưa được duyệt |
| W-08 | Không chạy. Workflow không policy DML trong target; helper chỉ synthetic; reader/revoke-first regression thiếu | BLOCKED; không suy rộng ACL-admin proof |
| W-09 | Không chạy. Java wrapper COMMIT_UNKNOWN được giữ; prototype không Java bridge; kill/ACK-loss thật thiếu | BLOCKED |
| W-10 | Không chạy. Migration/bootstrap có DDL capability; online owner membership không cấp trong prototype; maintenance proof thiếu | BLOCKED |
| W-11 | Không chạy. Tooling đọc catalog hiện hữu không là deployed snapshot; catalog harness chưa execute | BLOCKED |
| W-12 | Không chạy. tests/r28_m5/schema.sql assign_replace + omission/fault/concurrency probes đã chuẩn bị | BLOCKED; X-25/T07/X-12/X-13 NOT RUN |
| W-13 | Không chạy. Membership/binding/registry/authority/admission capture+deferred fail closed ngoài assignment; không có online mutation entrypoint | BLOCKED; per-writer scope/exclusion cần owner/security |
| W-14 | Không chạy. Chỉ status lookup prototype; repair qua new approved intent/manual disposition chưa có | BLOCKED; Q08 + X-16/X-26 |
| W-15 | Không chạy. Receipt immutable, không cleanup/TTL trong prototype; retention/tombstone contract và X-23 thiếu | BLOCKED |
| W-16 | Không chạy. Không restore/import/reopen fixture hay privileged reconciliation proof; admission row không tự đủ | BLOCKED; Q05/Q07/Q09 |
| W-17 | Không deployed catalog/credential manifest/external job/pooler evidence; repository search không đóng được | **BLOCKED / UNINVENTORIED** |

Evidence [X-25 preflight](evidence/X-25/20261109-m5-preflight-02/result.json),
[T08/X-09 preflight](evidence/T08-X-09/20261109-m5-preflight-02/result.json):
BLOCKED, zero actual-role sessions. Các row không có approved exception thay cho closure.

# R28 → R27A — Q03 all-writer coverage matrix

**Status: PROPOSED INVENTORY FOR INDEPENDENT REVIEW. No path is marked "closed" without executed evidence; every closure below is a *required change + proof*, status NOT RUN/BLOCKED.**
Companion: [enforcement design](r28-q03-core-enforcement-design.md) (boundary M5, INV-1, role model), [test specs](r28-q03-verification-test-specs.md).

**Method.** Source inventory by `grep` over `backend/src/main`, `scripts`, `infra`, `.github` for `resource_acl`, `resource_registry`, `tenant_memberships`, `tenant_guards`, `acl_revision`, `workflow_policy_audit`, `workflow_definition_bindings`, `SECURITY DEFINER`, `SET [LOCAL] ROLE`, `session_replication_role`, `advisory`, plus reading of each hit, at #168 HEAD `9254fd933a1ed03d0ae67a28f5ff87dc0fe53182` (backend/scripts identical to `5618091dc205b196b551465d2c52def9313ed1fb`). Test sources (`backend/src/test`) and the stale build output `backend/bin` were not treated as production writers. **Limits:** dynamic SQL, external credentials/jobs, deployed catalog, live role memberships and pooler configuration are **not observable from the repository** and are therefore listed as *UNINVENTORIED* (row W-17); the matrix cannot prove absence of writers it cannot see.

**Reading the columns.** *Bypass* = can the path change effective ACL/policy state **without** (T) the exclusive tenant guard, (K) scoped-key serialization, (A) policy audit with G advance, (R) complete terminal receipt. "Yes" means the path as observed/required has no such control today. *Source SHA* is the last commit touching the file (`git log -1 -- path`).

## 1. Observed writers (source-backed)

| ID | Path (file / function) · Source SHA | Tables and operations it can execute | Role / privilege it needs (today → target) | Bypass T / K / A / R | Required enforcement change | Proof required to close |
| --- | --- | --- | --- | --- | --- | --- |
| W-01 | `HelpdeskService.create` L60–L96, `grant` L350–L352 · `fa16f30d5c67a49186b1c36f2babe58d54a15e38` | INSERT `resource_registry`; INSERT … ON CONFLICT DO UPDATE `resource_acl` (grants for requester + all active coordinators); also `helpdesk_requests`, `workflow_instances` | Runtime role with `INSERT` on registry/ACL (`runtime-grants.sql:13`) and `UPDATE(granted)` (`:16`) → **none** on Core policy tables | T: via trigger `helpdesk_policy_lock` yes, via explicit `lockTenant` yes · K: **yes (no key)** · A: **yes (G not advanced, no audit)** · R: **yes** | Not an enabled writer in target. Create is a **separate** scope (out of ACL-admin proof). Remove H's Core DML in the separate cutover; until then it cannot coexist with Layer 2 | X-09/T08 role matrix: H has no policy DML; X-25 legacy-writer probe commits **fail**; separate Create regression suite (not this proof) |
| W-02 | `HelpdeskService` assign path L196–L204: `UPDATE resource_acl SET granted=false`, then `grant()` · `fa16f30d…` | UPDATE/INSERT `resource_acl` (revoke previous assignee, grant new); `UPDATE helpdesk_requests` | same as W-01 | T: yes (trigger + `lockTenant`) · K: **yes** · A: **yes (no G/audit)** · R: **yes** | Replace with the Core ACL-admin command via `assign_replace`; Helpdesk keeps only the Helpdesk-local reservation/CAS (Q08) | X-12/X-13/X-24/X-25 on `assign_replace`; X-16/X-26 consumer; X-17 FK/trigger cutover |
| W-03 | Runtime grant `UPDATE(acl_revision) ON tenant_guards` · `runtime-grants.sql` @ `44283466f1747d55ed39e782d0600e8d09a28427` L12 | `UPDATE tenant_guards SET acl_revision = <any value ≥ old>` (immutability trigger only blocks decrease) | Runtime (H legacy) → **revoked from every runtime role** | T: acquires row lock only by UPDATE · K: n/a · A: **yes — G can be advanced by any amount with no audit/receipt** · R: **yes** | Remove grant; G advances only inside the executor; Layer 2 requires `resulting = previous+1` + audit + receipt | Catalog test: `has_column_privilege(rt,'tenant_guards','acl_revision','UPDATE') = false` for A/R/W/H; X-25 direct `UPDATE … acl_revision+1000` denied (`42501`) |
| W-04 | `helpdesk_policy_lock` trigger function + triggers · `schema.sql` @ `44283466…` L31–L52 | `SELECT … FOR UPDATE` on `tenant_guards` inside BEFORE row triggers on `helpdesk_actors`, `tenant_memberships`, `resource_acl`, `resource_registry`, `workflow_definition_bindings` | SECURITY INVOKER; needs `UPDATE` privilege on `tenant_guards` of the *invoking* role (this is why the legacy runtime holds `UPDATE(acl_revision)`) | T: **provides** lock for those 5 tables · not on `tenant_guards`, `workflow_policy_audit`, receipt tables · K/A/R: **yes** | Keep as legacy lock aid; do not count as receipt/auth enforcement. In target, executor takes the guard itself and the trigger's invoker-privilege dependency disappears for non-owner roles | Coverage test: DML on each protected table by owner-simulating test role takes the tenant lock; documented as not receipt enforcement |
| W-05 | `stage6_policy_immutability_guard` + `s6_*` triggers · `policy-schema.sql` @ `44283466…` L96–L184 | Blocks DELETE/TRUNCATE and identity rewrites; **permits** `granted` flips, any increasing `acl_revision`, membership `active` flips, binding `active` flips, registry lifecycle ACTIVE→TOMBSTONED | SECURITY INVOKER, no PUBLIC EXECUTE | Not a writer. It does **not** link a delta to audit or receipt | Keep; add Layer 2 deferred triggers and receipt immutability; function lists must be enumerated (no unreviewed trigger functions) | Catalog enumeration of `pg_trigger`/`pg_proc` against manifest (X-09); X-25 |
| W-06 | `scripts/helpdesk-local-setup.ps1` L61–L135: `CREATE ROLE owner NOLOGIN`, runtime LOGIN, `SET LOCAL ROLE owner`, seeds `tenant_guards`, `workflow_definition_bindings`; runs as `POSTGRES_USER=helpdesk_setup` · `fa16f30d…` | DDL + `INSERT tenant_guards`, `INSERT workflow_definition_bindings`, role/grant creation | Docker superuser (`helpdesk_setup`) → **offline-only, admission-closed**, never a runtime/proof role | T/K/A/R: **yes (superuser)** | Declare disposable-local only. A production/shared setup path needs a separate reviewed procedure behind §6 maintenance boundary of the design | Maintenance-boundary checklist (design §6.1) executed and reconciled; not runtime proof |
| W-07 | `scripts/helpdesk-local-actor-seed.ps1` L53–L54 · `fa16f30d…` | `INSERT tenant_memberships`, `INSERT helpdesk_actors` | Setup/superuser role via the setup script | T/K/A/R: **yes** | Membership writers must follow the executor/maintenance protocol (membership changes alter effective authorization and G); local seeding only before admission opens | Same as W-06; reconciliation report before reopen |
| W-08 | `PostgresWorkflowPersistence` (`createInstance` L120, `commitActivation`, transition history L233, UPDATE instances L298) · `fa16f30d…` | INSERT/UPDATE Workflow tables only. **Does not write policy tables** | W role on Workflow tables | Not an ACL writer; it is a **reader** of policy facts and must share the guard ordering (guard before instance row) | Keep W without policy DML; take the guard via `reader_guard_share`; keep ACL-admin proof separate from Workflow CREATE/ACTIVATE/TRANSITION | T08 order tests (reader vs revoke); X-09 W has no policy DML |
| W-09 | `PostgresWorkflowPersistence.guardedTransaction` L365–L450 · `fa16f30d…` | Transaction wrapper: READ COMMITTED, callback, COMMIT, `COMMIT_OUTCOME_UNKNOWN` on commit failure | n/a | Runs **any** callback; no receipt enforcement | Executor call must use the same unknown-outcome mapping; a Java assert is not the invariant | T07 fault injection at the selected real boundary |
| W-10 | `WorkflowApprovedMigration`, `WorkflowSchemaBootstrap`, `WorkflowMigrations`, `WorkflowSchema` · `fa16f30d…` | DDL/catalog reads for Workflow schema; catalog queries over `pg_auth_members` (inspection) | Migration/bootstrap role | No policy DML observed; DDL capability implies trigger/function/grant change | Run only under §6 maintenance boundary; catalog diff before reopen | Catalog manifest diff |
| W-11 | `WorkflowSecurityDefinerReview`, `WorkflowEventTriggerReview`, `WorkflowEventTriggerGuard`, `WorkflowRuntimePrivilegeAudit`, `WorkflowReadOnlyPreflight` · `fa16f30d…` | **Read-only inspection** (catalog queries, `session_replication_role`, memberships) | Read-only audit role | None (inspection, not writer closure proof) | Reuse as the catalog-snapshot tooling for X-09 only after review; their existence is not evidence that deployed closure holds | Executed snapshot artifacts |

## 2. Required target paths (not implemented; NOT PROVEN)

| ID | Path | Needed protocol / role | Bypass today | Required change | Proof |
| --- | --- | --- | --- | --- | --- |
| W-12 | Core ACL-admin command: original, retry, concurrent resend, delayed original | A calls `assign_replace` only; guard → admission → key → authority → G/fence → mutation → receipt (design §4.1) | **No ingress, ledger, fence or receipt exists** | Implement behind M5 only after Bảo/Yến accept; one function, one path for all arrival types | X-12, X-13, X-24, X-25, T07 |
| W-13 | Membership / binding / registry / service-authority / admin-revoke / G writers | Every writer that changes *effective* policy goes through a reviewed entrypoint that takes the guard first and advances G + audit (+ receipt where an idempotency identity applies) | Legacy: triggers lock only; no G/audit | Enumerate each as its own definer function or declare it offline-only; no "unmanaged privileged shortcut"; Q01 anti-regrant unresolved | X-09; per-writer INV-1 test; Q01 X-14/X-15 |
| W-14 | Recovery / repair / manual reconciliation | Lookup-only operator has no mutation; corrective mutation = new authorized intent through W-12 after the old outcome is dispositioned | None implemented | Operator role gets `lookup_receipt` EXECUTE only; a repair that cannot use W-12 is **offline** (§6) | Authorization matrix test; X-16/X-26 manual closure |
| W-15 | Cleanup / archive / compaction / key retirement | No deletion in MVP; any compaction is a definer function under the same guard→key order preserving identity columns | None implemented | Immutability triggers on receipts; no DELETE/TRUNCATE; retirement authority Q05 | X-23 |
| W-16 | Restore / import / PITR / reopen | Admission-closed, executor credentials absent, first-write `CLOSED`, reconciliation, reopen by break-glass role with evidence (design §5.4/§6) | None implemented | Procedural boundary; a DB-visible admission gate is a Q05/Q07 decision | X-23 restore variants; reconciliation report |
| W-17 | **UNINVENTORIED**: dynamic SQL, external schedulers/ETL/BI credentials, DBA consoles, replicas promoted to primary, extensions, other databases/schemas that can connect with owner or superuser, pooler `SET ROLE` | Cannot be derived from the repository | Unknown | Deployed catalog and credential manifest (roles, memberships incl. `SET`/`INHERIT`, `pg_parameter_acl`, extensions, event triggers, `pg_hba`, pooler config) captured **per environment** before any "closed" statement | Executed X-09 snapshot; until then writer closure is BLOCKED |

## 3. Privileged-capability matrix (can bypass ordinary GRANT/REVOKE)

| Capability | What it defeats | Handling | Claim allowed |
| --- | --- | --- | --- |
| PostgreSQL superuser | Everything, incl. `ENABLE ALWAYS`, `session_replication_role`, `DROP TRIGGER` | Exclude from online execution; offline only | **No protection claimed** |
| Table / function owner (`core_acl_owner`) or any role that can `SET ROLE` to it | Layer 1 and Layer 2 (`ALTER TABLE … DISABLE TRIGGER`, `CREATE OR REPLACE FUNCTION`) | NOLOGIN, empty online membership, migrator behind admission closure | **No protection claimed**; detective reconciliation only |
| `CREATEROLE` / role with `ADMIN OPTION` on owner | Can grant itself membership | None may exist online; catalog audit | Verified by catalog test, not assumed |
| `GRANT SET ON PARAMETER` (PostgreSQL 15+) | Could allow `session_replication_role` | Audit `pg_parameter_acl`; `ENABLE ALWAYS` | Catalog test |
| `pg_write_all_data`, `pg_execute_server_program`, `pg_write_server_files`, replication role | Bypass table privileges / host access | Forbidden for runtime roles | Catalog test |
| Extension / untrusted language functions owned by a privileged role | Arbitrary SQL under owner | Extension manifest; no `CREATE EXTENSION` for runtime | Catalog test |
| `TRIGGER`/`REFERENCES`/`TRUNCATE` table privilege | Add own trigger, FK-lock side effects | Not granted | Catalog test |
| Search-path/`pg_temp` shadowing in a definer function | Run attacker code with owner rights | Fixed `search_path`, qualified names, no CREATE on schema | Static + catalog test |

## 4. Result

| Question | Answer |
| --- | --- |
| Is every known ACL writer path inventoried with source evidence? | **Yes for what the repository shows (W-01..W-11).** Deployed/dynamic/external writers are **UNINVENTORIED (W-17)**. |
| Which bypasses exist in current source? | W-01/W-02 (no key, no G, no audit, no receipt), W-03 (arbitrary G advance by the runtime role), W-05 (immutability permits any `granted` flip / G increase), cross-tenant DML not prevented by DB (design F-5), W-06/W-07 (superuser setup, offline), absence of any receipt/fence/admission mechanism. |
| Is complete enforcement claimed? | **No.** Required change and proof are specified for each row; owner/superuser paths are declared out of ordinary protection and covered only by the admission-closed boundary and detective reconciliation. |
| Status | **All closure proofs NOT RUN / BLOCKED** (Q02–Q05, Q07 open; no authorized disposable PostgreSQL environment). |
