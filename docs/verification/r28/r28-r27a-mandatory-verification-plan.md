<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# R28 → R27A — Mandatory Verification Plan

**Status: TEST PLAN ONLY.** Không migration, grants, DB connection, PostgreSQL test hoặc runtime E2E được chạy bởi gói này. Runtime cases NOT RUN/BLOCKED; không actual executable harness command được phát minh.

## 1. Sources và ID preservation

| Source | PR / full SHA / path |
| --- | --- |
| Authority/atomicity/gates | [#160 ADR-015](https://github.com/tricore-opentrix/opentrix/blob/5618091dc205b196b551465d2c52def9313ed1fb/docs/08-decisions/ADR-015-core-workflow-acl-v3-g0.md), 5618091dc205b196b551465d2c52def9313ed1fb |
| C-ID definitions | [#160 C-01..C-30 matrix](https://github.com/tricore-opentrix/opentrix/blob/5618091dc205b196b551465d2c52def9313ed1fb/docs/verification/r27/adr015-g0-contract-verification-matrix.md), 5618091dc205b196b551465d2c52def9313ed1fb |
| X-ID schedule and fixtures | [#165 PostgreSQL plan §§5.1–5.4](https://github.com/tricore-opentrix/opentrix/blob/2335a0858b6eafeacdff82bf157b44df116145bc/docs/verification/r28/r28-postgresql-locking-privilege-t07-t08-plan.md#L166), 2335a0858b6eafeacdff82bf157b44df116145bc |
| Canonical/rejection/retention/resend | [#165 command design](https://github.com/tricore-opentrix/opentrix/blob/2335a0858b6eafeacdff82bf157b44df116145bc/docs/verification/r28/r28-core-acl-command-and-idempotency-design.md), 2335a0858b6eafeacdff82bf157b44df116145bc |
| Ownership/cutover | [#159 ADR-010](https://github.com/tricore-opentrix/opentrix/blob/ef4b9484369c94ed7e5674e4b056b0d8f673e1ba/docs/08-decisions/ADR-010-core-helpdesk-service-boundary.md), ef4b9484369c94ed7e5674e4b056b0d8f673e1ba |
| Consumer prerequisites/CAS | [#145 R29](https://github.com/tricore-opentrix/opentrix/blob/5d577dd4a0a8efa830459cf35cb1868e52a9de2f/docs/03-applications/helpdesk/r29-use-case-contract.md), 5d577dd4a0a8efa830459cf35cb1868e52a9de2f |

T07 = transaction atomicity/rollback; T08 = authorization/concurrency/isolation. Giữ C-20 READ/HISTORY vs revoke, C-21 rollback, C-22 timeout, C-23 deadlock, C-25 lock privilege, C-26 ownership/cutover. X-ID là local case IDs đã có trong #165, không đổi nghĩa C-ID hoặc sửa source matrix. [Closure Matrix](r28-r27a-decision-closure-matrix.md) chứa owner/decision blockers; [Dependency Contract](r28-r27a-dependency-contract.md) chứa six P0 scope và permission boundaries.

## 2. Mandatory prerequisites, roles và fixtures

- Applicable prior design/implementation approvals; selected schemas/identity/managed slice/invalidation, receipt/rejection/canonical/retention/admission, lock/role protocol và tested production transaction path. Chưa có thì affected case BLOCKED.
- Disposable PostgreSQL 17 baseline; pin actual minor/image digest, OS, JDBC/driver/harness version. Separate disposable Helpdesk/Core databases cho service cases; không production DSN, no same-DB cross-service transaction.
- Roles R reader, W Workflow writer, A ACL-admin executor, H Helpdesk runtime, O restricted observer; setup/migration owner riêng. Runtime assertions dùng actual non-owner/non-superuser logins; capture current/session role, inherited/default privileges, SET ROLE reachability và credential/pool separation. O không dùng làm writer.
- READ COMMITTED và approved transaction-local lock/statement budgets được assert trên mỗi connection. Không đặt duration/SLA trong tài liệu này. Timeout/deadlock phải full rollback và connection reset trước pool reuse.
- Fixture kế thừa #165 P0/F0: T1/T2, R1/R2 của T1 và R3 của T2; active Uold/Unew/Uadmin, explicit grants/binding/history; T1 G10, R1 accepted fence5; Q6 key K6/fence6/token V6/G10, Q7 distinct key/fence7. Same-key replay giữ payload/G/fence/version; baseline D-01 A không tự refresh G của Q7 để che conflict.
- Snapshot exact ACL/membership/registry/binding/G/fence/audit/ledger/instance/history và local intents/reservations trước mỗi schedule. No-op/batch G delta và rejection-audit counts theo approved choice, không đoán +1 cho mọi command.
- Barriers tại guard acquired/authorized/before commit/commit returned; observer capture blocker graph. Không sleep rồi đoán order. Core không chờ HTTP ACK hoặc giữ DB transaction qua Helpdesk network.
- Cleanup: archive evidence trước; rollback/close sessions/proxies/barriers; verify no lingering tx/locks; reset fixture bằng disposable setup controller. Không dùng production DROP/cleanup.

## 3. T07/T08 và C-20..C-23 coverage

| Gate/case | Exact oracle cần thực thi | Current execution status |
| --- | --- | --- |
| T07 / C-12,C-21 / X-05 | Fault sau reservation/revoke/grant/G/fence/audit/receipt và trước commit: authoritative server transaction end rồi observer thấy initial snapshot; no partial ACL/G/fence/success audit/ledger. Retry phase tách riêng, không yêu cầu initial snapshot sau retry thành công. | NOT RUN; target harness/schema chưa có |
| T07 / actual Workflow / X-22 | Fault trên actual CREATE/ACTIVATE/TRANSITION sau instance/history/receipt stage: instance/version/history/receipt rollback cùng nhau; Workflow-only không đổi policy G/fence. Không dùng untouched history của ACL command làm Workflow rollback proof. | NOT RUN; activation/version contract prerequisite |
| T08 / C-20 / X-01,X-02 | Reader-first giữ shared guard: revoke writer blocked tới reader end. Revoke-first giữ exclusive: reader blocked; sau revoke commit, fresh auth deny và zero protected instance/history output. No streaming trước complete authorization/materialization. | NOT RUN; Q07 mechanism còn BLOCKED |
| T08 / C-22 / X-06 timeout,X-07 | Lock wait và statement execution delay là fixtures riêng. Timeout classified bằng actual SQLSTATE/budget, full rollback snapshot, no stale-auth/savepoint fallback; aborted connection không reuse. Commit uncertainty xử lý X-12, không giả rollback từ timeout. | NOT RUN; budgets/harness chưa approved |
| T08 / C-23 / X-06 deadlock | Test-only authorized two-tenant cycle: capture actual deadlock graph/SQLSTATE, victim không cố định và full rollback; survivor chủ động rollback trong phase này, cả hai snapshots về initial. Sorted-order positive control riêng. Auth denial không là deadlock evidence. | NOT RUN; actual lock graph chưa có, deadlock freedom NOT PROVEN |
| T08 / auth negatives / X-08,X-18,X-19 | Forged/wrong tenant/service/delegation input deny/no disclosure/mutation; GRANT/REVOKE/membership schedules trước/sau năm Workflow operations đọc current facts. Explicit grant còn nhưng membership revoked vẫn deny. | NOT RUN; exact ingress/security contract BLOCKED |

## 4. Mandatory R27A dependency cases

Mọi case dùng prerequisites/evidence ở §§2/6 và giữ exact #165 source meaning. BLOCKED chỉ decision prerequisites chưa có; không đổi thành PASS vì docs lint hoặc unit CI.

| Case / gate / P0 | Deterministic schedule và exact acceptance oracle | Blocker / owner / current status |
| --- | --- | --- |
| X-09 / C-25 / P0-02,05 | R/W allowed shared acquisition thành công, không G/ACL delta; A writer blocked tới reader end. Actual R/W không direct guard/ACL UPDATE, SET ROLE owner/admin, unauthorized EXECUTE/CREATE/ALTER/REPLACE/ownership escape; H không Core access. Raw FOR SHARE với SELECT-only denied. Nếu definer: fixed signature/search_path/temp shadow/invalid args và atomic publication tests; uncommitted helper không visible, committed không PUBLIC EXECUTE, publication error rollback không publish. | Q07 exact mechanism/role/signature matrix; Bảo/Yến; **BLOCKED** |
| X-12 / C-03,C-04 / P0-04,06 | Suppress ACK sau confirmed server commit: lookup trả matching historical receipt; one mutation/receipt/audit/G/fence delta và one matching H finalize. Pre-commit disconnect control chỉ retry sau selected protocol. Hold original in-flight → S resend waits then replay after commit hoặc one execution after rollback; original đến sau resend cũng chỉ replay. N cần closure/admission proof trước resend. | Q02/Q05/Q06; Ánh+Bảo/Yến; **NOT RUN**, shared resend branch **BLOCKED** |
| X-13 / C-03,C-04,C-13,C-24 / P0-02,04 | Lookup original service/tenant/type/key được authorized trả exact historical result dù current ACL đã đổi. Wrong principal/tenant/revoked scope không receipt/G/fence leak. No visible row khi original in-flight không thành definitive non-commit; expired không fresh execution. Current ACL và local finalize kiểm riêng. | Exact status/auth/retention/Q06; Bảo+Ánh; **NOT RUN**, expiry/resend branches **BLOCKED** |
| X-14 / D-01,C-12 / P0-03 | Construct Q6 R1 at G10/fence6; unrelated R2 policy commit G11; Q6 sau guard phải STALE_POLICY_GENERATION theo baseline A, no R1 ACL/G/fence/success-audit mutation. Có thể rejection receipt chỉ nếu Q02 selected. Same-tenant guard vẫn serialize. Không đổi sang B/C để PASS. | Baseline A giữ nguyên; target harness/Q02 policy; Bảo/Yến/Ánh; **NOT RUN** |
| X-15 / C-10,C-11,C-28 / P0-03,06 | Higher accepted fence7 rồi fresh fence6 hoặc key mới không execute replacement; replay exact prior success vẫn historical. Admin variant giữ membership/service authority active: admin revoke G10→G11/fence5 rồi queued Q6 G10/fence6 phải reject/no regrant. Refresh G/new-key không được clear separately approved deny/invalidation; independent admin slice preserved. | Q01 managed slice/invalidation/error precedence, Q09 urgent authority; Bảo/Yến/Ánh; main **NOT RUN**, emergency branch **BLOCKED** |
| X-16 / C-02,C-04,C-16 / P0-06 | Core success sau đó H local finalize failure: Core history/receipt giữ nguyên. Same-current retry local finalize đúng một lần. Superseded Assign old CAS=0, new state không bị overwrite; old attempt có disposition riêng. Resolve dùng selected reservation/supersede policy; Confirm gated khi matching resolution chưa finalize. Không implicit reverse Core transition. | Q06/Q08 durable disposition/current-intent criteria; Ánh/Yến, Bảo; **NOT RUN**, convergence branch **BLOCKED** |
| X-17 / C-26 / P0-05 | Separate target databases/roles: catalog constraints/triggers/procs/dependencies/function bodies không H→Core FK/trigger/function/grant edge. Source/package checks không direct JDBC/JOIN. H local mutation không đợi Core guard do hidden edge; H direct Core denial có positive own-DB control. Remote unavailable/missing reference → selected pending/reconciliation/safe rejection, không substitute ID/tenant hoặc false activation/sync success. | ADR-010/cutover assets, Q07/Q09 và ID/receipt/fence reconciliation; Yến+Bảo+Ánh; **BLOCKED** |
| X-23 / C-24 / P0-03,04,05 | Cleanup/execution chạy guard→key với cả hai orders và restore fixture. Dispatch original Create **và** Assign sau full outcome cleanup: trong window historical replay; tombstone/retired identity không execute mới. Zero second instance/ACL/G/fence/success-audit delta. Same retired key/different payload không fresh. Restore mất identity/fence/incarnation/service mapping trong khi request còn admissible → FAIL/closed recovery, không replay-safe. | Q05 duration/admission/restore và Q01 incarnation; Bảo+Ánh/Yến; **BLOCKED** |
| X-25 / C-21 / P0-03,04,05 | Runtime A/W stage mutation+incomplete receipt, skip finalize rồi COMMIT; từng required identity/fingerprint/version/outcome/reference thiếu phải abort whole tx, observer sau end thấy initial snapshot. Test deferred và SET CONSTRAINTS IMMEDIATE, savepoint/catch, DELETE/disable/replace validator, replication-role/SET ROLE escapes. Complete success và selected rejection positive controls. Final-only alternative prove key-lock-before-mutation trên every writer và fault-before-receipt rollback. | Q03 mechanism/required fields và Q07 effective grants; Bảo/Yến, Ánh compatibility; **BLOCKED** |
| X-26 / C-16..C-19,C-30 / P0-06 | Durable H Resolve prerequisite reservation; competitor reassignment/Confirm ở barrier trước Core commit, rồi lost ACK/restart/CAS failure. Reservation choice: competitor không supersede reserved exact versions; unknown không timeout-release; authoritative matching outcome → local finalize/release đúng một lần. Supersede choice: preserve Core RESOLVED/history, old CAS=0 + durable conflict/recovery disposition trước business completion. Confirm không complete trước matching finalized resolution/current prerequisites. | Q08 recovery/cancel/release authority + Q06; Ánh/Yến, Bảo Core; **BLOCKED** |

## 5. Feasibility conditions cần review trước implementation

**Q03:** [PostgreSQL constraint trigger](https://www.postgresql.org/docs/17/sql-createtrigger.html) có thể AFTER ROW DEFERRABLE INITIALLY DEFERRED; validator phải đọc final row theo immutable key, không dùng pending INSERT NEW image làm final outcome. WHEN được đánh giá ngay, không deferred. Exact trigger/schema chưa chọn. Review bổ sung cho X-25: intentionally omit cả reservation/receipt trên từng command writer path; ledger-row trigger một mình không phát hiện mutation không tạo ledger row. Phải chứng minh path coverage/trust boundary hoặc DB enforcement bổ sung nếu owner đòi invariant rộng hơn. Completeness không chứng minh truthful receipt trước compromised trusted writer/T2.

**Final-only:** serialized scoped key trước execution + existing receipt lookup + terminal receipt cùng transaction; fault trước receipt insert phải full rollback. Không dùng unique violation cuối tx để tuyên bố external exactly-once; không external side effects/network trong Core tx.

**Q07:** [SELECT row-lock privilege](https://www.postgresql.org/docs/17/sql-select.html) đòi UPDATE trên ít nhất một column; raw SELECT-only không đủ. [Definer hardening/publication](https://www.postgresql.org/docs/17/sql-createfunction.html#SQL-CREATEFUNCTION-SECURITY) cần trusted search_path, exact grants trong cùng DB transaction. Helper không tự làm tenant authorization engine; cross-tenant denial phải test qua actual Core ingress/trusted orchestration. Advisory alternative cần all-writer/cleanup/repair inventory và transaction-lock namespace, không ngầm là T2.

**READ COMMITTED dedup:** conflicting INSERT DO NOTHING có thể không insert vì transaction chưa visible trong statement snapshot; sau conflict cần fresh statement lookup theo approved protocol, không coi no RETURNING là fresh key. Theo [PostgreSQL isolation](https://www.postgresql.org/docs/17/transaction-iso.html). Test concurrent receipt lookup, retention race và auth trước disclosure.

Các đoạn trên là feasibility assessment/review requirements, không approved SQL/DDL. Không mở rộng numbering hoặc thay source X/C oracle để khớp implementation.

## 6. Evidence requirements và CI contract-test backlog

Mỗi future run bắt buộc ghi:

1. Full tested implementation/contract/OpenAPI/schema/fixture commit SHAs + dirty diff nếu có; image digest, PostgreSQL full version, driver/harness versions, test seed/run ID.
2. Exact runnable command, exit code, suite/test counts/failures/errors/skipped; no zero/skipped-suite PASS. Harness chưa có thì ghi BLOCKED, không dựng tên Gradle/pytest target như đã chạy.
3. Actual login/session roles, memberships/default privileges, helper owner/signature/search_path, isolation/budgets; redact credentials/tokens.
4. Session-tagged statements và begin/commit/rollback, monotonic barrier timeline, pg_locks/activity/blocker PID graph; transaction-ID waits cũng hợp lệ, không đòi tuple lock luôn hiện.
5. Expected/actual HTTP/status/error visibility và canonical bytes/digests, before/after data digests/counts cho policy/receipt/Workflow và H intents/reservation/CAS; proxy fault cut point/server tx end.
6. Artifact URLs/hashes, negative-test outcomes, independent reviewer identity và scoped disposition. PostgreSQL-only evidence không thành two-service E2E; CI xanh không owner approval.

| Priority | Future CI work — chưa sửa workflow trong task này | Exit criterion |
| --- | --- | --- |
| P0 | Exact OpenAPI lint/schema/examples/compatibility diff + consumer/provider contract artifact | Approved exact method/schema/security/error/retry contract, immutable digest consumed by both sides; không Helpdesk terms trong public generic Core API. |
| P0 | Service-auth/tenant/resource/admin negatives | Actual verified credentials + current authorization, hidden404 parity, forged headers/body, status scope and delegated actor tests; mocks không thay ingress verification. |
| P0 | T07/T08 disposable PG với actual runtime roles | Cases ở §§3–4 có exact commands/barriers/SQLSTATE/artifacts; fail/skip không masked bởi aggregate green. |
| P0 | Two-service six-use-case integration | Create/Triage/Assign/Start/Resolve/Confirm, one ticket/instance, stale versions/fences/G, lost ACK/delayed original, CAS failure/restart và Confirm gate; Q06/Q08 phải closed trước encode selected branch. |
| P1 | Stacked-review CI trigger và artifact retention | Existing CI chỉ auto-trigger PR tới main; base feature branch của #165 không có automatic run. Review proposed trigger/dispatch riêng, không đổi workflow để green docs package; preserve existing checks. |

## 7. Documentation validation và execution disposition

Documentation validation chỉ kiểm package scope, traceability, required P0/Q/X/C coverage, local links/SPDX và diff whitespace; không có kết quả runtime suy từ checks này.

Local documentation run ngày 2026-11-09, trên isolated package worktree từ 2335a0858b6eafeacdff82bf157b44df116145bc:

- Command: python C:/Users/Admin/AppData/Local/codex-with-chatgpt/artifacts/r28-r27a-dependency/validate_docs.py C:/Users/Admin/AppData/Local/codex-with-chatgpt/worktrees/opentrix-r28-r27a-dependency — exit 0, 77 assertions PASS; 7 local Markdown links resolve, 24 GitHub blob links pin allowed full SHAs. Pin checks là local URL/traceability checks, không claim đã HTTP-probe mọi URL. Validator là local artifact ngoài repository, không runtime/test dependency được thêm vào project.
- Command: C:/Users/Admin/AppData/Local/codex-with-chatgpt/r28-doc-tools/bin/reuse.exe lint-file docs/verification/r28/r28-r27a-dependency-contract.md docs/verification/r28/r28-r27a-decision-closure-matrix.md docs/verification/r28/r28-r27a-mandatory-verification-plan.md, với PYTHONPATH=C:/Users/Admin/AppData/Local/codex-with-chatgpt/r28-doc-tools — REUSE 6.3.0 exit 0 cho đúng ba file. Không repository-wide REUSE/CI claim.
- Scope/consistency review: six P0, nine unique PENDING Q rows, required X/C coverage và bốn permission classes; không READY permission row, source ADR/R29/runtime/migration/grants/workflows không sửa. Git staged whitespace/scope checks được ghi trong PR evidence tại exact package HEAD.

**Runtime disposition:** T07/T08, PostgreSQL/security/service contract/E2E và migration/cutover NOT RUN hoặc BLOCKED như bảng; không connection/DDL/GRANT được thực thi. C-24/C-25/C-26/C-27/C-28/Q06/Q08 remain decision-blocked. C-29 historical amendment alignment không tự đóng: S4 đã sửa transaction boundaries nhưng Q06 vẫn discrepancy.

**Owner handoff:** Bảo chịu trách nhiệm executable PG/role/atomicity evidence, Ánh chịu trách nhiệm consumer/CAS/recovery và service scenarios, Yến review independent scope/gates/security/operations. Không báo gate PASS hay merge chỉ vì documentation validation thành công.
