<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# R28 — PostgreSQL locking/privileges và T07/T08 verification plan

**Status:** PROPOSED DESIGN / TEST PLAN ONLY — PENDING OWNER/CORE REVIEW.
**Scope:** D-04 lock/privilege/cutover analysis và D-05 reproducible disposable PostgreSQL plan; không chạy PostgreSQL tests/migrations/grants.
**Source SHA:** ADR-015/#163 `35ab10a7fff600b1b2e48afd776d15c6834bdedd`; base `5618091dc205b196b551465d2c52def9313ed1fb`; ADR-010/#159 `ef4b9484369c94ed7e5674e4b056b0d8f673e1ba`.
**Owner/reviewer:** Bảo PostgreSQL/security; Yến owner/security review; Ánh cross-service/R29 review. Không có APPROVE trong tài liệu này.
**Decisions confirmed:** READ COMMITTED/T1/tenant-first là direction review của Bảo; ADR vẫn proposed, concrete lock/privilege mechanism chưa được duyệt.
**Recommendations pending approval:** guard SHARE readers / UPDATE policy writers, narrow reader locking boundary nếu phù hợp, separate ACL-admin role; không default SECURITY DEFINER.
**Open blockers:** selected role/lock protocol, D-01/D-03, target schema/harness, ADR-010/cutover và owner timeout/emergency policies.
**Verification status:** PostgreSQL T07/T08 **NOT RUN**; C-25/C-26 **BLOCKED**; case statuses §5. Không có database connection được mở bởi task này.
**Next actions:** review privileges/protocol rồi hiện thực harness trong task riêng sau applicable gates.

ADR-015 **PROPOSED**, G0-CONTRACT **BLOCKED**, G0-DESIGN/IMPLEMENT/RUNTIME **NOT ACCEPTED**, R27 STEP 03 **IN PROGRESS**.

## 1. D-04 — authoritative protocol và lock order

Nguồn: [ADR-015 §§4–6,10,13–14](../../08-decisions/ADR-015-core-workflow-acl-v3-g0.md), [ADR-010 shared order](https://github.com/tricore-opentrix/opentrix/blob/ef4b9484369c94ed7e5674e4b056b0d8f673e1ba/docs/08-decisions/ADR-010-core-helpdesk-service-boundary.md), [readiness source register](r28-g0-design-readiness-review.md). Tên relations ở đây là logical candidates, không approved target schema.

### 1.1 Lock-order table (recommendation, chưa approved)

| Thứ tự | READ/HISTORY | Workflow CREATE/ACTIVATE/TRANSITION | ACL replacement / REVOKE / membership / binding policy update |
| --- | --- | --- | --- |
| 0: ingress | Verify principal/shape; no DB lease across HTTP | Như reader | Verify service identity/shape; dedicated admin scope required |
| 1: tenant guard | `FOR SHARE` qua approved privilege boundary | `FOR SHARE` nếu không đổi policy; biết có policy mutation thì UPDATE ngay từ đầu | `FOR UPDATE` ngay từ đầu; không upgrade SHARE→UPDATE |
| 2: exact facts | Resolve registry/lifecycle, actor membership, grant, binding cần thiết; authorization sau guard | Như reader, all current facts trước mutation | Current service/resource/recipient scope; lock resource/fence/facts theo deterministic composite identity |
| 2a: command key | Status/replay current lookup authorization trước expose; nếu cần guard thì lấy trước key | Unique scoped reservation nếu approved operation dùng ledger | Unique scoped reservation, duplicate receipt/fingerprint resolution; luôn sau guard, không key→guard |
| 2b: policy/ACL rows | Không ACL DML | Không ACL DML nếu chỉ workflow | Lock/update approved managed slice, deterministic actor/operation order; nonexistent rows protected bởi guard + uniqueness |
| 3: instance | One data statement materialize current instance/history; nếu multi-statement cần approved additional consistency protocol | Exact instance `FOR UPDATE`; create uniqueness/definition constraints | Chỉ khi operation cần instance; không Helpdesk row |
| 4: append/finalize | Materialize authorized response trước release lock | History/receipt theo transaction | Policy audit + fence/G + terminal receipt cùng commit |
| 5: end | Commit/release rồi trả materialized data; không stream protected rows trước authorization hoàn tất | Commit rồi authoritative ACK | Commit rồi authoritative ACK; không remote network wait trong tx |

Mọi entrypoint kể cả admin/maintenance/retention/repair phải dùng cùng order. Một tenant trước; nếu future batch nhiều tenant/resource, sort tenant rồi composite keys và lấy mode mạnh nhất từ đầu. Multi-tenant batch chưa được chọn; không thêm để tối ưu. No guard row → fail closed, không skip lock hoặc tự provision từ user path.

Trong READ COMMITTED, mỗi statement có snapshot mới; shared guard giữ **policy** ổn định nếu mọi policy writer tuân thủ, không tự tạo repeatable snapshot cho Workflow data. Đề xuất READ/HISTORY materialize instance + relevant history trong một data statement sau current ACL check, cùng transaction đang giữ guard. Multi-statement/pagination/streaming cần proof riêng (instance lock qua approved boundary hoặc snapshot/version-bound query); không hứa all-pages snapshot. Thiết kế này suy từ [PostgreSQL transaction isolation](https://www.postgresql.org/docs/17/transaction-iso.html), cần C-20 kiểm chứng.

### 1.2 Reader/revoke ordering và race analysis

| Race | Expected serialization / residual limit |
| --- | --- |
| Reader giữ SHARE trước revoke | Writer UPDATE đợi. Reader authorize/read/finish dưới quyền trước revoke; sau reader end writer mới commit. Response có thể tới client sau revoke ACK do network, không thể “thu hồi bytes” đã authorize trước. |
| Revoke giữ UPDATE trước reader | Reader SHARE đợi; sau writer commit, reader dùng statements mới đọc current facts và deny revoked access. Nếu writer rollback, reader có thể được phép theo facts còn effective. |
| Concurrent replacement cùng tenant/resource | Writer guard serialize; compare fence/G sau chờ. Distinct keys không bypass fence; same key không thêm mutation. |
| Unrelated resource policy update | Cùng tenant guard vẫn serialize; D-01 chỉ thay logical precondition, không loại contention vật lý. |
| Membership/definition/registry/service-authority update | Phải lấy UPDATE guard + generation/audit như ACL write; nếu writer bypass, authorization proof thất bại. |
| Concurrent Workflow writes | SHARE guard không serialize writers với nhau; instance UPDATE + expected Workflow version và history constraints quyết định winner. Policy generation không bump chỉ vì Workflow version đổi. |
| Existing admin revoke rồi pending assignment | Guard chỉ order, không giải quyết regrant intent. D-01 admin invalidation/managed-slice decision vẫn BLOCKED. |
| Two SHARE readers cùng upgrade UPDATE | Có thể deadlock; prohibit upgrade. Class có policy side effect phải lấy UPDATE ngay đầu. |
| Retention/cleanup vs execution | Cleanup cũng guard trước key; tombstone/admission không mất giữa conflict/select; không key-first maintenance. |

`FOR SHARE` chặn non-key UPDATE/DELETE, còn `FOR KEY SHARE` không chặn non-key generation update lấy NO KEY UPDATE. Đổi SHARE sang KEY SHARE không phải cách sửa C-25; FOR UPDATE cho tất cả readers làm giảm concurrency và vẫn cần UPDATE privilege. Deadlock victim không xác định trước; rollback toàn transaction và reconcile retry. Đây là behavior theo [PostgreSQL explicit locking](https://www.postgresql.org/docs/17/explicit-locking.html); lock protocol trên là recommendation cần test.

`lock_timeout` giới hạn chờ lock; `statement_timeout` giới hạn statement, không phải business revocation deadline. Proposal transaction-local budgets, lock budget nhỏ hơn statement budget để phân loại lỗi; values cần owner duyệt. Theo [PostgreSQL client defaults](https://www.postgresql.org/docs/17/runtime-config-client.html), không dùng global timeout để chứng minh fail-closed. Sau timeout/deadlock: abort toàn operation, rollback connection trước reuse pool; không catch lỗi rồi tiếp tục với stale ACL/savepoint fallback. Capture raw SQLSTATE, sanitize external error; commit uncertainty dùng command-status. Không dùng NOWAIT/SKIP LOCKED rồi suy missing row là permission.

## 2. C-25 — privilege design alternatives

PostgreSQL 17 yêu cầu SELECT cho columns được đọc và UPDATE trên **ít nhất một column của mỗi table bị row-lock** với `FOR SHARE`, `FOR UPDATE`, `FOR NO KEY UPDATE`, `FOR KEY SHARE`. Cấp `UPDATE(acl_revision)` để request path lấy lock cho phép sửa chính security generation; không đạt mục tiêu C-25. [PostgreSQL SELECT privilege requirements](https://www.postgresql.org/docs/17/sql-select.html).

| Lựa chọn | Ưu điểm | Rủi ro / disposition đề xuất |
| --- | --- | --- |
| Dedicated trusted Core execution role | Phù hợp T1, explicit code boundary cho admin DML; separate pools/credentials giới hạn accidental use | Nếu reader request path giữ role UPDATE guard thì vấn đề C-25 vẫn còn. Đổi tên role hoặc SET ROLE mà reader được phép không tạo isolation. Dùng riêng cho ACL-admin path, không broad request credential. |
| Narrow lock-only SECURITY DEFINER | Reader SELECT không UPDATE G; helper owner có đúng lock privileges, không cho tùy ý generation DML | Candidate để review nếu Java tiếp tục trusted T1 authorization. Không auto chọn. Helper chỉ locking/return bounded metadata, không generic SQL/GRANT function. Cần hardening và negative tests dưới đây. |
| Transaction advisory shared/exclusive locks + SELECT guard | Không cần UPDATE table để row-lock | All writers phải cooperate, namespace/key mapping cố định, collisions có thể tạo cross-tenant DoS; bypass SQL writer phá proof. Transaction locks, không session locks ở pool. [PostgreSQL advisory functions](https://www.postgresql.org/docs/17/functions-admin.html#FUNCTIONS-ADVISORY-LOCKS). Cần owner chấp thuận đổi protocol. |
| Snapshot + generation validation | Có thể tránh lock UPDATE privilege | Detached/double-read check đơn thuần không đủ proof; concurrent mutate sau final check, data materialization và starvation/retry phải phân tích. Defer thay vì tuyên bố safe. |
| Dummy writable column / weaker row lock / broad UPDATE | Dễ cho câu lệnh chạy | Không chọn workaround tăng surface hoặc lock sai conflict. Không cấp request UPDATE generation để “PASS”. |

**Recommendation pending approval:** giữ tenant shared/exclusive protocol; tách reader/workflow và ACL-admin credentials. Review narrow lock-only helper nếu muốn row locks mà reader không thể sửa guard; nếu owner từ chối SECURITY DEFINER, phải prove một alternative trước C-25 acceptance. Không grant/CREATE FUNCTION trong task này. T1 là trusted Java boundary, không tuyên bố database ngăn mọi SQL misuse trong Core.

### 2.1 Privilege matrix (capabilities đề xuất, không grants)

Các role labels dưới đây là logical, không tên role đã triển khai. `Deny` bao gồm inherited memberships/SET ROLE, PUBLIC/default privileges và SECURITY DEFINER escape paths.

| Capability | Public/API caller | Helpdesk runtime | Core request reader | Core Workflow writer | Core ACL-admin executor | Core migration owner | Narrow lock helper owner (nếu chọn) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Direct DB login | Deny | Chỉ Helpdesk DB | Separate Core credential | Separate Core credential | Restricted Core credential | Offline controlled | NOLOGIN |
| Core ACL/registry SELECT | Deny | Deny | Need-to-read under trusted Core boundary | Need-to-read | Need-to-read | DDL responsibility, không request use | Guard only |
| Guard UPDATE/G mutation | Deny | Deny | **Deny** | **Deny** nếu không policy writer | Exact approved guard update | DDL only during operations | Minimum UPDATE needed for lock, not exposed DML |
| ACL/membership/binding/resource mutation | Deny | Deny | Deny | Deny | Exact approved command capabilities | DDL lifecycle | Deny |
| Workflow/history | Deny | Deny | SELECT authorized materialization | Required instance DML/history INSERT; no history rewrite | Only if command needs approved capability | DDL lifecycle | Deny unless separately reviewed minimal lock requirement |
| Ledger/audit | Deny | No Core access | Status SELECT by trusted path, no mutation | Own approved transaction receipt/audit insert | Own approved receipt/audit insert, no arbitrary overwrite | DDL lifecycle/controlled retention | Deny |
| Execute lock helper | Deny | Deny | Allow only approved signature | Allow only approved signature | Direct guard lock or approved helper | Control ownership | Owner only |
| Helpdesk tables | Deny | Own tables only | Deny | Deny | Deny | Deny (separate Helpdesk owner) | Deny |
| DDL/schema CREATE/role admin/BYPASSRLS | Deny | Deny | Deny | Deny | Deny | Schema-scoped controlled DDL, not API | Deny extra powers |

T1 limitation: Core reader có SELECT có thể bypass Java resource checks nếu Core process bị compromise; matrix không phải row-security T2 proof. RLS nếu muốn cần threat-model decision riêng. Dedicated ACL-admin executor có thể direct DML trong trusted boundary; không hứa T2 chỉ nhờ API. Không cho request pool inherit/admin-switch vào ACL executor hoặc migration/helper owner. Migration owner không dùng cho test runtime acceptance.

### 2.2 SECURITY DEFINER hardening nếu được chọn

Theo [PostgreSQL safe SECURITY DEFINER usage](https://www.postgresql.org/docs/17/sql-createfunction.html#SQL-CREATEFUNCTION-SECURITY): fixed trusted search_path, `pg_temp` last; default PUBLIC EXECUTE phải được thu hẹp. Yêu cầu review cụ thể:

- Dedicated NOLOGIN/non-superuser owner; không CREATEROLE/BYPASSRLS/schema ownership không cần thiết. Request role không member owner, không ALTER/REPLACE function, không CREATE trong trusted schemas.
- Schema-qualified table/function/operator references; fixed SQL, không dynamic identifier/SQL do caller chọn. Fixed `search_path = pg_catalog, <trusted_core_schema>, pg_temp`; trusted schema không writable bởi untrusted role. Không coi `search_path` parameter/GUC caller truyền là trusted tenant.
- Exact function signature allowlist, no generic relation/lock-mode parameter; verify bounded tenant argument/existence handling, fixed lock mode, giữ transaction lock tới caller end. Current tenant/resource auth vẫn Core trusted boundary; helper không tự cấp quyền grant.
- CREATE FUNCTION và REVOKE PUBLIC EXECUTE, rồi exact-signature GRANT cho approved callers phải nằm trong **cùng một database transaction**, không chỉ cùng commit/PR/migration file. Error rollback cả publication; không có autocommit window cho PUBLIC gọi helper. Default privileges/future overloads không mở lại quyền. Không execute grants ở task này.
- Negative tests: malicious temp shadow relation/function, crafted tenant value, search_path override, unauthorized EXECUTE/SET ROLE/UPDATE, schema CREATE, ownership transfer; verify helper không đổi G/ACL và lock không release sớm.

Escalation risk còn lại: helper owner có UPDATE guard cần cho lock; bug trong helper có thể sửa security metadata hoặc lock tenant khác gây DoS. Đây là trusted code mới phải review độc lập, không free security upgrade hoặc default chosen mechanism.

### 2.3 P1-04 — selection và privilege acceptance consequences

| Alternative | Must prove trước acceptance | Disposition |
| --- | --- | --- |
| Separate trusted ACL-admin executor + SELECT-only R/W | R/W không inherit/SET ROLE/admin credential escape; R/W vẫn có approved shared guard acquisition | Giới hạn accidental/admin path use trong T1, không tự giải quyết row-lock privilege; cần helper hoặc alternative. |
| Narrow lock-only definer | Atomic publication; trusted immutable ownership/search_path; fixed lock mode/typed tenant argument; missing guard fail closed; no ACL/G DML; lock retained through caller transaction | Recommendation để review nếu giữ row locks. X-09 phải chứng minh positive reader blocks writer và negative privilege probes; chưa chọn function/schema/grants. |
| Transaction advisory shared/exclusive | Stable collision-aware namespace/key mapping; all effective writers/cleanup/repair cooperate; no session-lock pool leak; current guard exists | Có thể tránh UPDATE privilege, nhưng cần protocol amendment và all-writer inventory. Advisory lock không tự bảo vệ trước SQL bypass/T2. |
| Broad UPDATE, dummy column hoặc KEY SHARE thay SHARE | Không đạt C-25 hoặc conflict semantics | Không đề xuất làm passing workaround. |

Owner Bảo/Yến cần freeze actual login roles, inheritance/SET ROLE, credential/pool separation, table/column privileges, default privileges và helper owner/signature trước schema acceptance. NOLOGIN owner vẫn cần kiểm membership escape; schema-qualified SQL không an toàn nếu referenced schema/function/operator bị untrusted role thay đổi. X-09 gồm caller search_path/temp shadow, unauthorized CREATE/ALTER/REPLACE/ownership/EXECUTE và NULL/malformed/wrong-tenant inputs; helper không phải tenant authorization engine trong T1. Không tự nâng claim thành T2.

Lock-order proof hiện là conditional: guard trước facts/key/instance, mode mạnh nhất ngay đầu; implicit FK/unique/trigger locks và maintenance paths phải có actual SQL/catalog inventory. X-06 deliberate cycle chỉ kiểm fail-closed victim handling, không chứng minh production graph acyclic. Cần positive schedules của X-18..22 và actual wait graph; chưa có SQL verification thì **deadlock freedom NOT PROVEN**, không tuyên bố deadlock-free. Savepoint/exception rollback có thể release locks: nếu mất guard, operation phải abort hoặc restart full authorization, không tiếp tục dưới old facts.

## 3. C-26 — ownership/cutover dependency plan

Observed legacy evidence: [schema.sql](../../../backend/src/main/resources/db/helpdesk/schema.sql) có FK từ `helpdesk_actors`/requester/assignee sang `tenant_memberships`, request `instance_id` sang `workflow_instances`; `helpdesk_policy_lock` lock `tenant_guards`, attached cho Helpdesk actor và policy tables. [policy-schema.sql](../../../backend/src/main/resources/db/helpdesk/policy-schema.sql) chứa registry/ACL/membership/binding/audit, binding→definition FK; [runtime-grants.sql](../../../backend/src/main/resources/db/helpdesk/runtime-grants.sql) có `UPDATE(acl_revision)`. Đây là same-schema legacy/offline source, không chứng minh actual deployed catalog. Không đem nguyên edges sang target cross-service schemas.

Target: Core sở hữu effective memberships/registry/ACL/guard/bindings/audit/ledger/Workflow, Helpdesk sở hữu business membership/tickets/intents/outbox/CAS. Internal Core binding→definition FK có thể hợp lệ vì cùng owner; Helpdesk→Core membership/instance FK và Helpdesk trigger→Core guard không hợp lệ. Thay liên kết remote bằng opaque immutable IDs + authenticated API/reconciliation, không cross-service trigger/JOIN/SQL.

Migration sequencing **chỉ kế hoạch** theo ADR-010:

1. Inventory actual FK/trigger/function dependency graph, roles/grants/defaults/memberships, Flyway history, existing IDs and audit/G/fence/ledger. Source inventory không thay catalog snapshot.
2. Owner review mappings, separate migration locations/history/owners, retention và frozen legacy V1–V4 bytes. Fresh disposable databases prove target constraints, package/resource isolation và no cross-service edges.
3. Plan controlled snapshot/export/import preserving IDs/history/version/receipt/fence; establish target same-service references và opaque remote references. Legacy remains authority trước approved freeze; không dual-write assumption.
4. At separately approved cutover: freeze legacy writes/drain in-flight, reconcile final counts/content/grants/pending intents; remove dependency trong target path trước revoke legacy access. Không drop constraint khi legacy writers còn cần nó hoặc strip all FKs hàng loạt.
5. Verify catalog graph, denied cross-service SQL và authenticated recovery, rồi owner mới cho switch traffic/credentials. Old trigger/function không còn accessible ở target; chỉ retention legacy read-only theo policy.
6. Rollback trước target writes có thể switch sau evidence; sau target writes cần audited reverse reconciliation, không blind rollback có thể mất revoke/ledger. Cleanup/decommission là separate reviewed step.

Chưa có executable migration hay actual DB catalog; C-26 tiếp tục **BLOCKED**. Removal timing/actual installations/downtime và integrity owner còn unresolved.

## 4. SQL transaction pseudocode

**NON-EXECUTABLE DESIGN PSEUDOCODE.** Placeholder budgets, functions và schemas chưa được chọn; không SQL implementation/harness.

```text
-- NON-EXECUTABLE DESIGN PSEUDOCODE: READ/HISTORY
BEGIN ISOLATION LEVEL READ COMMITTED;
SET LOCAL lock_timeout = <approved lock budget>;
SET LOCAL statement_timeout = <approved statement budget>;
<acquire tenant guard FOR SHARE through selected least-privilege mechanism>;
<fresh statement read exact current ACL facts; missing/revoked => deny>;
<one data statement materialize exact instance + requested history snapshot>;
<assert no protected output was streamed before authorization/materialization complete>;
COMMIT;
<return materialized response>;
ON <error>: ROLLBACK; <stable fail-closed response, no data>;

-- NON-EXECUTABLE DESIGN PSEUDOCODE: policy writer / REVOKE
BEGIN ISOLATION LEVEL READ COMMITTED;
<set transaction-local approved timeouts>;
<lock tenant guard FOR UPDATE, then exact current service/resource authority facts>;
<resolve scoped idempotency reservation/receipt AFTER guard, never before>;
<for execution check fence/G per approved class and lock facts in sorted order>;
<apply revoke/replacement and approved admin invalidation semantics>;
<advance policy generation + accepted fence where applicable>;
<write corresponding audit + complete durable terminal command receipt>;
COMMIT;
<ACK only after commit; uncertain ACK => authenticated reconciliation>;
ON <pre-commit error>: ROLLBACK <all effects>;
```

Không đổi isolation level sang REPEATABLE READ ngầm: stale snapshot có error behavior khác; READ COMMITTED không đủ nếu không guard/protocol. Full reservation/replay flow ở [D-03](r28-core-acl-command-and-idempotency-design.md#6-sql-transaction-pseudocode).

## 5. D-05 — reproducible T07/T08 test specification

### 5.1 Giữ nguyên test IDs và common fixture

Đã đọc [matrix tại reviewed #163](../r27/adr015-g0-contract-verification-matrix.md): **C-20** READ/HISTORY vs REVOKE; **C-21** transaction rollback; **C-22** lock_timeout/statement_timeout; **C-23** deadlock; **C-25** reader lock privilege; **C-26** cutover ownership edges. Không đổi nghĩa hoặc đánh lại ID. X-01..X-17 bên dưới là **local plan case IDs**, không thay C-IDs. T07 = transaction/atomicity evidence, T08 = authorization/concurrency/isolation theo source; không tự tạo gate PASS.

Common preconditions **P0** cho mọi case (được kế thừa trừ override): future approved schema/protocol/commands/harness tại exact tested SHA; disposable PostgreSQL 17 baseline, pin actual minor + container image digest/OS/driver. Không production DSN. Hai direct authenticated DB sessions A/B (không superuser/owner), autocommit off cho tx, READ COMMITTED được assert trên mỗi connection. Setup-only role tách biệt, không là execution role. Instrumented Core transaction path giữ đúng code/role; test không sửa SQL để bỏ guard.

Logical roles: **R** = Core request reader; **W** = Workflow writer; **A** = ACL-admin executor; **H** = Helpdesk runtime trên database riêng; **O** = restricted observation role đọc lock/activity evidence theo approved privileges. Tên role actual/NOLOGIN memberships/SET ROLE phải capture. R/W lock helper là candidate, test BLOCKED cho đến selected mechanism. Dùng actual service principal auth trong future HTTP contract cases; DB role không chứng minh JWT verification.

Initial data **F0**: tenants T1/T2; resource R1/R2 thuộc T1, R3 thuộc T2; active members Uold/Unew/Uadmin ở T1 và Uother ở T2; explicit READ grant cho Uold trên R1, allowed service S1 chỉ T1/approved assignment slice; exact definition/version binding; Workflow instance I1 và known history H0. T1 G=10, R1 accepted fence=5, Helpdesk business assignment version=5. No ledger for scoped key K6; command Q6 incoming fence=6, token V6, replace Uold→Unew, baseline expected G=10. Q7 distinct key/fence=7, intended assignment Uadmin (membership eligible); identity/value types là fixture symbols, không schema lựa chọn. Khi baseline A, Q7 expected G=10 trừ subcase explicitly refresh/new authorized intent; không sửa payload/key của attempt cũ.

Initial snapshots gồm exact ACL rows, generation, fence, audit, ledger, instance/history và matching Helpdesk intent khi case cần. Không assume policy increment count cho no-op/batch trước owner quyết định; với một approved effective replacement fixture, assert frozen expected delta và tương ứng audit.

**Lock orders:** L-R = guard SHARE → current facts → one data query → end; L-A = guard UPDATE → exact authority/resource/fence facts → unique key → affected rows sorted → audit/G/fence/receipt → end; L-W = guard SHARE → facts/key nếu applicable → instance UPDATE → history/receipt → end. L-H = Helpdesk local CAS/intents, không Core SQL. Reader lock acquisition dùng selected mechanism, không cấp UPDATE G để test chạy.

Barriers deterministic tại `guard acquired`, `authorized`, `before commit`, `commit returned`; O poll lock graph tới bounded deadline, không “sleep rồi đoán” thứ tự. Unrelated setup/control data ngoài critical transaction; no network call while holding Core locks. Nếu không chứng minh barrier/order, result không PASS.

Common **evidence E0** cho mỗi case:

- Exact tested commit SHA và dirty diff nếu có; source SHA contract, schema/fixture/migration manifest digests; PostgreSQL full version/image digest, OS, driver/harness versions.
- Current/session roles, complete effective grants/defaults/role memberships/function owner/search_path, isolation level/timeouts; protected secrets/tokens redacted.
- Exact executable test command (chỉ bổ sung khi future harness tồn tại), seed/run ID, session-tagged statements, tx begin/commit/rollback và monotonic barrier timestamps, SQLSTATE/row counts.
- `pg_locks` + activity wait events + blocker PID graph (`pg_blocking_pids` nếu available); row-lock waits có thể hiện qua transaction-ID locks, không đòi tuple lock luôn visible. Restricted O credentials không dùng cho mutation.
- Expected vs actual authorization/result/data digests, ACL/G/fence/ledger/audit/history before/after, commit uncertainty/fault injection log; pass/fail reason và artifact links/reviewer. Không chỉ aggregate CI badge.

Common **cleanup K0**: rollback/close A/B, release all barriers/fault proxies, verify no open tx/locks; archive E0 trước teardown disposable DB/container bởi setup controller. Reset F0 bằng fixture riêng cho next case, không cleanup bằng production schema drop. Cases H dùng thêm disposable Helpdesk DB. Không delete committed evidence trước capture.

Future runner command **chưa tồn tại/chưa approved**: mỗi case phải có exact runnable command + exit code trước execution; hiện không phát minh `pytest`/Gradle target như đã có. Evidence thiếu command/version/role/ordering → case NOT RUN/BLOCKED, không PASS.

### 5.2 Case specifications (mọi hàng kế thừa P0/F0/E0/K0)

#### X-01 — READ vs REVOKE (C-20); status NOT RUN

- **Preconditions/roles/data:** P0/F0; A=R as Uold, B=A authorized revoke; READ R1, explicit grant active.
- **Session A:** L-R, barrier sau authorize/before data, materialize I1; commit sau O xác nhận B blocked.
- **Session B:** B bắt đầu revoke sau A SHARE; L-A chờ guard rồi revoke READ, generation/audit/outcome atomic, commit.
- **Order/blocking:** A SHARE trước B UPDATE; B phải chờ A end. Run reverse schedule riêng: B UPDATE+revoke before commit; A SHARE blocked, sau B commit A fresh facts deny và zero protected rows.
- **Expected:** prior serialized read được phép; post-revoke read denied; không stale successful read trong reverse schedule. Response arrival time không thay serialization.
- **Evidence:** E0 + two barrier timelines, blocked PID graph, exact response bytes/denial and revoke ACK time. **Cleanup:** K0/reset revoked grant via setup only. **Gate:** T08/C-20, G0 runtime evidence, NOT RUN.

#### X-02 — HISTORY vs REVOKE (C-20); status NOT RUN

- **Preconditions/roles/data:** P0/F0 với nonempty H0; A=R Uold, B=A; HISTORY dùng current READ authority theo #159.
- **A:** L-R authorize/materialize history trong một data statement, hold barrier trước end. **B:** L-A revoke READ, đợi guard rồi commit.
- **Order/blocking:** như X-01, run cả reader-first và revoke-first; không query H0 trước auth hoặc stream partial history.
- **Expected:** history read trước serialization được phép; sau committed revoke không historical grant replay/cache nào mở H0.
- **Evidence:** E0 + history snapshot digest, zero leaked row assertion, reader/writer barrier trace. **Cleanup:** K0, erase disposable output sau lưu approved evidence. **Gate:** T08/C-20; NOT RUN.

#### X-03 — concurrent assignment/reassignment (C-10/C-12); status NOT RUN

- **Preconditions/roles/data:** P0/F0; durable Helpdesk intents Q6/Q7 issued bằng H CAS trước dispatch; A/B=A same S1, distinct keys. Nếu A baseline G=10, Q7 cũng G=10 để thấy conflict.
- **A:** L-A Q6 hold trước commit. **B:** L-A Q7, block guard; sau A commit đọc lại accepted fence/G.
- **Order/blocking:** guard UPDATE serialize, no partial revoke/grant visible. Repeat B-first schedule; Q7 may win, Q6 stale fence.
- **Expected:** baseline A, Q6-first: Q6 effective replacement commit G'>10 theo frozen increment rule (G11 nếu +1), fence6/Unew; Q7 với G10 phải `STALE_POLICY_GENERATION`, không mutation, final fence6. Q7-first: Q7 commit G'>10/fence7/Uadmin; Q6 không execute (stale G/fence, exact error precedence cần freeze). D-01 B/C no-G branch BLOCKED đến approved class/invalidation: Q6→Q7 thì final Uadmin/fence7, Q7→Q6 thì Q6 stale/final Uadmin/fence7. Helpdesk chỉ finalize matching current intent; không chọn option theo kết quả implementation.
- **Evidence:** E0 + both intent/version/fingerprint receipts, final grant slice, G/audit deltas, no intermediate mixed grants. **Cleanup:** K0 + disposable H intent reset. **Gate:** T07 atomicity + T08 order, D-01 class dependency; NOT RUN.

#### X-04 — out-of-order commands (C-10/C-11); status NOT RUN

- **Preconditions/roles/data:** P0/F0; A/B=A; Q7 fence 7 and delayed Q6 fence 6, distinct keys, approved generation values for chosen class.
- **A:** L-A commit Q7. **B:** after ACK L-A deliver Q6; also retry Q6 with another key to show dedup không order commands.
- **Order/blocking:** non-overlap schedule không cần blocking; overlap variant B đợi A guard. Fence check sau wait.
- **Expected:** fresh lower fence rejects, fence/ACL/G unchanged by rejected execution; không require contiguous fences theo baseline > rule. Same-key Q7 replay historical once, không bị nhầm stale execution.
- **Evidence:** E0 + accepted/rejected fences, before/after audit/G counts and keys. **Cleanup:** K0. **Gate:** T08 stale-command rejection; NOT RUN.

#### X-05 — transaction rollback/crash (C-21/C-12); status NOT RUN

- **Preconditions/roles/data:** P0/F0; A=A, B=R hoặc A same-key duplicate; fixture fault hook tại reservation, revoke, grant, G/fence, audit, receipt finalization và before commit.
- **A:** L-A inject exception ở từng point, rollback toàn tx; separate variant terminate disposable client connection trước commit, không kill production backend. **B:** L-R/L-A chờ A, đọc state hoặc retry same key sau rollback.
- **Order/blocking:** B guard blocked đến rollback/connection loss được server phát hiện; no persistent progress residue.
- **Expected:** rollback-only phase: B chỉ observe sau server tx end, ACL/G/fence/audit-success/ledger/Workflow-history đều F0. Retry phase reset fixture riêng: B same-key reauthorize/current-check, có thể execute một lần; snapshot sau retry không còn bắt buộc F0. Semantic committed rejection ở X-24; actual L-W rollback ở X-22, không dùng untouched history của ACL command để chứng minh Workflow atomicity.
- **Evidence:** E0 + per-fault write-stage traces, server tx end, snapshots/zero partial rows, no reservation survives. **Cleanup:** K0, remove fault hook/proxy state. **Gate:** T07/C-21; NOT RUN.

#### X-06 — lock timeout + deliberate deadlock (C-22/C-23); status NOT RUN

- **Preconditions/roles/data:** P0/F0; A/B=A; selected timeout budgets recorded. Timeout variant A holds T1 guard, B shorter lock budget than statement budget. Deadlock variant uses two **test-only** disposable tenant guards, authorized per-tenant fixture principals (B được phép T2) và intentional reversed order; không production protocol change.
- **A/B timeout:** A L-A hold; B L-A times out waiting, rollback. **A/B deadlock:** A locks T1, B locks T2, barrier, A requests T2/B requests T1; set timeout đủ dài để detector chạy (capture effective deadlock_timeout).
- **Order/blocking:** timeout wait expected; deadlock intentionally violates canonical order solely fault injection. Positive control same sorted order không cycle.
- **Expected:** timeout holder và waiter đều rollback, final F0. Deadlock fixture stage known per-tenant mutation/audit/receipt trước cycle; detector chọn một victim (không cố định), full victim rollback; survivor chủ động rollback, không commit trong subcase này, final cả hai tenant về snapshots. Positive sorted-order control chạy riêng với approved effective mutations, commits và expected per-tenant deltas đã freeze. Retry là phase riêng qua status/key flow; không permission fallback. SQLSTATE phải match PostgreSQL lock timeout/deadlock, không gộp cancellation khác làm PASS.
- **Evidence:** E0 + wait/deadlock graph, SQLSTATE (expected lock timeout/deadlock class), no partial state/victim audit-success. **Cleanup:** K0 cho cả tenant fixtures, verify no lingering lock. **Gate:** T08/C-22/C-23; NOT RUN.

#### X-07 — statement timeout (C-22); status NOT RUN

- **Preconditions/roles/data:** P0/F0; A=A, B=R; test-only deterministic delay after staged policy writes, selected statement budget smaller than delay, no competing lock để phân biệt timeout cause.
- **A:** L-A writes rồi timeout statement/fault query trước commit, abort/rollback. **B:** L-R chờ A guard, sau abort authorize trên F0.
- **Order/blocking:** A guard first, B blocked đến rollback; timeout do statement execution, không lock budget.
- **Expected:** no partial grant/G/fence/receipt/success audit; connection không return pool trong aborted tx. Unknown commit variant thuộc X-12, không giả định từ timeout.
- **Evidence:** E0 + effective budgets, cancellation SQLSTATE, staged/rolled-back rows, pool cleanup assertion. **Cleanup:** K0, remove delay hook. **Gate:** T07/T08/C-22; NOT RUN.

#### X-08 — cross-tenant/authentication denial (C-13/C-14); status NOT RUN

- **Preconditions/roles/data:** P0/F0; A=Core A/R under verified S1 scope T1; B=A provisioned S2 scope T2 for control; H direct Core SQL forbidden. Future ingress harness required.
- **A:** request tenant T1/resource R3 or forged T2/actor header; variants expired/wrong-audience service credential, valid service without admin authority. **B:** execute authorized T2 control command/read to prove resource exists; no shared-tx grants.
- **Order/blocking:** invalid credentials fail before protected locks; valid denied scope never mutate. Cross-tenant sessions không chờ nhau về tenant guard (system incidental locks measured separately).
- **Expected:** hidden/missing parity, no R3 receipt/ACL leak, no mutation/G/audit-success; body/hash/principal substitution không cấp authority. Visible-denied admin case distinct per frozen mapping.
- **Evidence:** E0 + redacted auth/response matrix, T2 before/after digest, status/replay denial, denied SQL snapshot. **Cleanup:** K0 cả T1/T2. **Gate:** security/contract + T08 isolation; NOT RUN.

#### X-09 — least-privilege enforcement (C-25); status BLOCKED

- **Preconditions/roles/data:** P0/F0 **sau chọn mechanism**; A=R/W/H lần lượt qua actual login credentials, B=A control. Never run assertion as owner/superuser.
- **A:** reader lấy allowed shared lock; reset connection/rollback giữa các probes direct UPDATE generation/ACL, SET ROLE admin/helper-owner, unauthorized EXECUTE, trusted-schema CREATE, ALTER/REPLACE/ownership escape; H thử Core access. Nếu definer selected: NULL/malformed/missing/wrong-tenant args, temp/search_path shadow; setup-only publication transaction hold trước REVOKE và inject rollback, unauthorized session thử EXECUTE trước/sau publication. **B:** L-A approved policy change đợi A reader lock, authorized control commit; owner không dùng làm runtime assertion role.
- **Order/blocking:** selected reader mechanism phải block B như SHARE; denied probes không acquire unintended admin rights; rollback aborted probe trước connection reuse.
- **Expected:** R/W direct guard/ACL UPDATE và escalation probes fail; selected lock succeeds without G/ACL mutation và B blocked đến A end. Invalid/missing guard không authorize; authorized helper signature không cho untrusted caller chọn object/mode. H Core access denied tại earliest applicable privilege boundary; PUBLIC/inherited paths không bypass. Definer publication: uncommitted helper không visible cho unauthorized session; committed helper không có PUBLIC EXECUTE; failure rollback không publish helper. Raw `SELECT FOR SHARE` với SELECT-only phải insufficient privilege. Cần selected exact SQLSTATE/role/signature matrix trước chạy; chưa chọn mechanism thì BLOCKED, không cấp UPDATE để PASS.
- **Evidence:** E0 + effective grants/role memberships/function owners/search_path/default privileges, positive lock graph + each negative SQLSTATE; T1 limits documented. **Cleanup:** K0 + remove temp objects. **Gate:** C-25/G0 design privilege proof và runtime acceptance; BLOCKED chưa selected protocol.

#### X-10 — duplicate scoped key (C-07/C-09); status NOT RUN

- **Preconditions/roles/data:** P0/F0; A/B=A same S1/K6/identical canonical payload. Variant first winner rollback ở X-05.
- **A:** L-A reserve+stage Q6, hold before commit. **B:** L-A same Q6, normally wait guard then find existing receipt; run selected shared-ledger operation fixture nếu cần observe unique-index wait trực tiếp, không bypass guard.
- **Order/blocking:** guard before key cho cả hai; capture actual blocker (guard hoặc unique transaction), không assert sai lock location.
- **Expected:** after A commit B returns same historical outcome; one replacement/audit/G delta/fence advance/receipt. After first rollback B có thể execute một lần với current checks.
- **Evidence:** E0 + identical fingerprints, receipt references, mutation/audit counts; no success receipt trước A commit. **Cleanup:** K0. **Gate:** T07/T08 dedup; NOT RUN.

#### X-11 — fingerprint substitution/conflict (C-08); status NOT RUN

- **Preconditions/roles/data:** P0/F0; A/B=A same scope/K6; B changed resource/actor/operations/token/fence/G (mỗi field subcase), cùng fake client digest.
- **A:** L-A Q6 commit; concurrent variant hold trước commit. **B:** L-A changed payload waits nếu concurrent, recompute fingerprint and conflict. Canonically equivalent set ordering/correlation-only vector là positive same-payload control.
- **Order/blocking:** guard→key before any B mutation; original receipt immutable.
- **Expected:** different semantics conflict; unknown/duplicate fields/ambiguous numbers rejected theo frozen canonical rule; same semantic payload replay once. Rolled-back reservation không để lại key binding: negative limit phải match owner rejection policy, không tự claim conflict khi no receipt.
- **Evidence:** E0 + canonical version/V-01..09 từ command design §2.1, exact golden bytes/digests sau owner freeze, no B writes/receipt overwrite. **Cleanup:** K0. **Gate:** D-02/D-03 contract/T07; NOT RUN, conditional canonical profile branches BLOCKED.

#### X-12 — successful commit with lost ACK (C-03/C-04); status NOT RUN

- **Preconditions/roles/data:** P0/F0; A=A Q6 through fault proxy/instrumented client, B=A authenticated status/retry same scope; durable H V6 pending.
- **A:** L-A commit, suppress ACK after server commit confirmation. Pre-commit control disconnects before commit with authoritative rollback log. **B:** lookup receipt then serialized same-key replay if allowed; H CAS same intent.
- **Order/blocking:** no Core locks retained waiting HTTP ACK; B guard/status protocol; before-commit variant status may see no receipt while tx still pending, không false COMMITTED.
- **Expected:** post-commit status historical outcome, no second mutation; pre-commit known rollback retry current checks. Unknown timing dùng selected protocol N/S command design §5.1: S exact same-key resend chờ original commit/rollback và một mutation, kể cả original đến sau resend; N cần admission/closure evidence trước resend, không suy từ empty SELECT. Chưa chọn shared protocol thì branch BLOCKED; three facts commit/current ACL/local finalize kept separate.
- **Evidence:** E0 + proxy cut point/server commit log, receipt/query trace and H CAS trace, one audit/G delta. **Cleanup:** K0 + proxy reset/disposable H cleanup. **Gate:** T07/reconciliation + future service E2E, NOT RUN.

#### X-13 — authenticated command-status lookup (C-03/C-04/C-13/C-24); status NOT RUN

- **Preconditions/roles/data:** P0/F0 + committed Q6 receipt and later legitimate revoke or Q7; A=Core status reader S1, B=A writer; frozen lookup visibility/retention policy needed for expiry subcase.
- **A:** query original scope/key, variants wrong tenant/principal/type, revoked service authority, expired/tombstoned key. **B:** hold new Q7 uncommitted then commit/rollback; O observe while A lookup no visible Q7 receipt.
- **Order/blocking:** if status guard SHARE chosen it waits B UPDATE; if snapshot lookup chosen it can observe only committed state. Selected semantics explicit, absence never permits new-key execution.
- **Expected:** S1 authorized gets historical Q6 only; denied caller learns no receipt; current ACL independently denied/changed; no durable IN_PROGRESS required. Expired/missing/in-flight responses follow §5 D-03, no false non-commit guarantee.
- **Evidence:** E0 + auth-scope/status response matrix, lookup timing/isolation, no current-grant assertion, receipt immutability. **Cleanup:** K0; tombstone fixture not deleted until archived. **Gate:** status/security/recovery; expiry subcase BLOCKED on C-24; main case NOT RUN.

#### X-14 — unrelated tenant-wide generation update (D-01; C-12); status NOT RUN

- **Preconditions/roles/data:** P0/F0; A/B=A; Q6 for R1 constructed at G10; B approved unrelated ACL write R2 → G11.
- **B:** L-A commit R2 change. **A:** then L-A Q6, additional overlap variant A waits B; compare G/fence after wait.
- **Order/blocking:** same tenant exclusive guard serializes even resource khác; R1 accepted fence still 5.
- **Expected:** baseline A rejects STALE_POLICY_GENERATION with no R1 effects. If future owner approves B/C assignment class, no reject **chỉ vì** R2 G bump, but current auth/admin invariants still enforced. Không choose passing branch theo implementation tùy tiện.
- **Evidence:** E0 + unchanged R1 facts/fence before request, G10→11, rejected/accepted reason per frozen option, retry/dispatch counts and latency (measurement only, no SLA).
- **Cleanup:** K0 reset both resources. **Gate:** D-01 decision proof/T08; NOT RUN.

#### X-15 — resource fence conflict + admin invalidation (C-10/C-11; C-28 dependency); status NOT RUN

- **Preconditions/roles/data:** P0/F0; A/B=A, distinct keys; variants incoming 5, incoming 6 after accepted 7, proposed expected fence mismatch nếu field selected. Admin variant membership stays active để không che grant-revoke race.
- **B:** L-A Q7 or resource-specific admin revoke commit; admin variant intentionally leaves assignment stream accepted fence=5 nếu baseline permits. **A:** pending Q6 attempts L-A replacement; test all approved D-01 classes and current admin restrictions.
- **Order/blocking:** A must wait B guard then validate current fence/policy. Post-revoke A may not silently regrant contrary approved invalidation policy.
- **Expected:** stale/equal incoming reject new execution; replay old same-key receipt remains historical. Admin race must either reject or enforce deny/invalidation; if bare B regrants under still-active membership, capture counterexample, không call safe. Emergency procedure assertions BLOCKED đến owner approve.
- **Evidence:** E0 + grants/membership/fence/G before/after, pending issuance time, admin authority and regrant/non-regrant proof. **Cleanup:** K0; preserve failed safety evidence. **Gate:** D-01/T08, C-28 subcase BLOCKED; main stale-fence case NOT RUN.

#### X-16 — Core commit + Helpdesk CAS failure (C-02/C-04/C-16); status NOT RUN

- **Preconditions/roles/data:** P0/F0 + separate disposable H DB pending intent V6/K6; A=Core A, B=H (hai dịch vụ, thêm O Core observer nếu cần). Assign variant Q6 và Resolve variant resolution intent, expected Workflow version.
- **A:** L-A Q6 (Resolve dùng L-W) commit authoritative outcome. **B:** before finalize persist authorized newer intent/version, or inject local finalize failure; consume A receipt then CAS exact old intent/version fails.
- **Order/blocking:** local L-H không lock/read Core tables; không distributed transaction/blocking. Core guard released trước response/local CAS.
- **Expected:** common safety: Core commit/history/receipt giữ nguyên, old CAS affected rows=0 và không overwrite latest H hoặc reverse transition; Confirm blocked nếu resolution chưa finalize. Same-current transient failure: không tạo newer version, retry local CAS sau recovery phải finalize exact intent một lần. Superseded Assign: disposition old committed attempt riêng, latest intent chỉ finalize theo receipt của chính nó. Superseded Resolve: theo option §4.1 readiness đã chọn; reservation option phải chặn newer intent (forced bypass chỉ là negative test, không valid schedule); supersede option phải persist unresolved conflict/reconciling và owner-authorized recovery disposition trước complete. Chưa chọn option thì convergence branch BLOCKED, không chỉ assert CAS=0 rồi PASS.
- **Evidence:** E0 + both DB tx traces, authoritative receipt, CAS affected-row count=0, safe read-model/action-gate responses and subsequent recovery; no duplicate Core history/audit.
- **Cleanup:** K0 cho cả DB + queues, archive cross-service trace. **Gate:** C-16 + R29 integration/E2E (runtime NOT RUN), **PENDING R28/R29 PROTOCOL DECISION**.

#### X-17 — cross-service FK/trigger cutover dependency (C-26); status BLOCKED

- **Preconditions/roles/data:** approved future cutover assets **chưa có**; disposable legacy + target Core/Helpdesk databases/schemas; setup owners riêng, A=H, B=Core A/W, O catalog observer. Source inventory §3 là starting hypothesis.
- **A:** run target Helpdesk-only mutation under H; attempt denied Core relation/function access; no Core guard call. **B:** hold Core guard under L-A and perform Core-only control write; target A không chờ Core tenant guard qua hidden trigger/FK.
- **Order/blocking:** catalog traversal qua constraints/triggers/functions/dependencies và function bodies; no Helpdesk→Core edge after selected split. Internal same-service FKs retained; no blanket FK deletion.
- **Expected:** target không cross-service FK/trigger/function/privilege edge và H local intent mutation không đợi Core guard; source/package inspection bổ sung cho application JOIN/query (catalog đơn độc không chứng minh không JOIN). Core unavailable: chỉ pending local intent, no false synchronized/active completion. Missing remote reference: unresolved pending/reconciliation, zero substitute resource/tenant hoặc fabricated activation; definitive Core rejection chỉ finalize safe failure theo approved contract. Owner phải chọn exact status/error/repair/disposition và ID reconciliation manifest trước missing-reference acceptance; unresolved branch BLOCKED. Legacy edges chỉ retained trong documented pre-cutover boundary, không accessible từ target H.
- **Evidence:** E0 + before/after `pg_constraint`/`pg_trigger`/`pg_proc`/`pg_depend` inventory and definitions, ownership/Flyway/migration-location manifest, denial logs and no unexpected wait graph, mapping/count/digest reconciliation.
- **Cleanup:** K0 target+legacy fixtures; không apply/remove production constraint. **Gate:** C-26/ADR-010 architecture/cutover, BLOCKED; separate migration review bắt buộc.

### 5.3 Additional specifications — append IDs, giữ X-01..17 và C-IDs

Mọi case kế thừa P0/F0/E0/K0; actual commands/harness và selected contract chưa có. `NOT RUN` chỉ test đã mô tả, không evidence; conditional branches BLOCKED đến decision tương ứng.

#### X-18 — GRANT/REVOKE vs protected Workflow operations; status NOT RUN

- **Preconditions/roles/data:** A=W cho CREATE/ACTIVATE/TRANSITION hoặc R cho READ/HISTORY; B=A policy writer. Parametrize cả năm operations, exact required grants/binding, valid initial state/Workflow version; CREATE dùng resource chưa có instance.
- **A/B/order:** chạy operation-first: A L-W/L-R giữ guard tại authorization-decision barrier trước tx end (denied case cũng capture trước rollback), B L-A blocked; rồi policy-first: B giữ UPDATE trước mutation/commit, A blocked và đọc fresh facts sau B end. Mỗi GRANT/REVOKE là fixture riêng; GRANT bắt đầu denied, REVOKE bắt đầu granted. Case operation-first GRANT bị denied và end trước writer.
- **Expected:** REVOKE-first deny/no instance/history/data output; operation-first REVOKE cho đúng one authorized operation trước revoke. GRANT-first cho đúng operation sau committed grant; operation-first denied trước grant không tự resume/mutate sau grant. Rollback policy control dùng facts ban đầu. Workflow-only mutation không bump policy G; policy delta/audit match frozen rule.
- **Evidence/cleanup/gate:** E0 + 20 ordered schedules (2 policy types × 5 operations × 2 orders), exact granted operation và wait graph, instance/history/output counts; K0/reset riêng từng schedule. T08/ADR-015 §13; không thay C-20 reader meaning hoặc gán C-ID mới.

#### X-19 — membership revoke vs active protected operations; status NOT RUN

- **Preconditions/roles/data:** A=W/R Uold; B=A membership admin; retain explicit resource grants để không che membership enforcement. Parametrize năm operations như X-18, valid state/version.
- **A/B/order:** operation-first A SHARE/authorize rồi B UPDATE blocked; membership-first B revoke membership/commit trước A fresh facts; thêm writer rollback control. Membership update phải guard→G/audit, không bypass bằng direct fixture change trong critical schedule.
- **Expected:** membership-first deny mọi protected operation dù grant row còn; operation-first hoàn tất đúng authorized result trước revoke; rollback control tiếp tục theo active membership. No reactivation/grant resurrection; denial không Workflow/history mutation hoặc protected rows.
- **Evidence/cleanup/gate:** E0 + membership/grant snapshots, ten ordered schedules + rollback controls, policy G/audit và no-write digests; K0. T08/ADR-015 §13, NOT RUN.

#### X-20 — stale Workflow version; status NOT RUN

- **Preconditions/roles/data:** A/B=W cùng I1, current ACL active, expected runtime version W0; ACTIVATE/TRANSITION fixtures riêng có valid transitions. Assignment/G/fence là independent snapshots.
- **A/B/order:** A L-W locks instance, commits W0→W1 + history; B SHARE guard rồi waits instance UPDATE, validate expected W0 sau wait. Sequential stale input control và wrong assignmentVersion-as-runtime-version control dùng selected DTO contract.
- **Expected:** B stale-version conflict/no instance/history mutation, no success receipt; G/fence/assignment không đổi vì Workflow write. A đúng một version/history delta. Idempotent replay A, nếu supported, trả original receipt trước stale execution check; không test replay như new stale command.
- **Evidence/cleanup/gate:** E0 + instance wait graph, before/after versions/history và semantic error (wire mapping OPEN); K0. T07/T08/ADR-015 §13, NOT RUN.

#### X-21 — duplicate instance identity / Create+Activate; status NOT RUN

- **Preconditions/roles/data:** A/B=W valid CREATE, cùng approved tenant/resource/instance identity; distinct command keys. Shared identity uniqueness còn OD-03; same-key duplicate đối chiếu X-10, không lẫn với distinct-key duplicate instance.
- **A/B/order:** A L-W stages create, B same identity chờ unique/instance protocol; run A commit và A rollback schedules. Với two-step Create/Activate, capture stable created identity và activation version/outcome riêng; composite nếu selected thì one Core tx.
- **Expected:** A commit → B duplicate-identity conflict, one instance và approved creation/activation history, no orphan success receipt. A rollback → B có thể tạo một instance sau current checks. H duplicate request chỉ một business ticket và intended Core instance sau local finalize; activation failure pending/reconciling hoặc definitive failure theo selected composite/two-step protocol, không fabricate rollback Core create.
- **Evidence/cleanup/gate:** E0 + constraints/keys, instance/history/receipt và H traces; K0 cả hai DB khi E2E. OD-03 và create composite/two-step branch BLOCKED đến freeze; Core concurrency/runtime NOT RUN, C-15 boundary giữ nguyên.

#### X-22 — actual Workflow/history rollback; status NOT RUN

- **Preconditions/roles/data:** A=W actual CREATE/ACTIVATE/TRANSITION path; B=R/W observer sau rollback. Inject faults sau instance insert/update, history INSERT, receipt stage nếu supported, before commit; control code/SQL chính là future production path.
- **A/B/order:** A L-W guard→facts/key→instance→history, hold after staged write, throw/fault/connection disconnect trước commit. B waits required guard/instance serialization hoặc chỉ observe sau authoritative server transaction end. Capture snapshots **trước** separate retry phase.
- **Expected:** all staged instance/version/history/receipt changes rolled back, no partial history/orphan instance; policy G/fence/audit unchanged bởi Workflow-only command. New CREATE row absent sau rollback; existing instance/history bằng initial snapshot. Retry phase reset riêng, allowed execution đúng một lần/current checks.
- **Evidence/cleanup/gate:** E0 + per-stage actual row counts/digests/transaction end và fault trace; K0. T07/ADR-015 INV-04/§13, NOT RUN; không dùng ACL replacement untouched history làm proof.

#### X-23 — replay execution after retention cleanup/restore; status BLOCKED

- **Preconditions/roles/data:** selected retention/admission/restore policy chưa có; A=A hoặc W với committed assignment và Create fixtures riêng, B=restricted cleanup controller. Persist original scope/key/payload/fingerprint và intended instance/fence; archive before cleanup.
- **A/B/order:** B guard→key cleanup full outcome theo selected policy, hold before commit; A dispatch original request, waits đúng selected guard/key path rồi status/replay. Reverse schedule A trước B; additional restore fixture có old request, resource incarnation, service mapping và admission floor/fence manifests.
- **Expected:** within replay window historical result, one original mutation; after tombstone/retired epoch explicit expired rejection/no new execution. Full-retain policy chỉ replay nếu admissible. Same retired key/different payload không fresh. Zero second instance/ACL/G/fence/audit delta; old key không resurrect qua ID reuse/fence reset/partial restore. Lost identity + request still admissible là FAIL/closed recovery, không PASS TTL-only.
- **Evidence/cleanup/gate:** E0 + cleanup/restore manifest, exact expired response theo owner, dispatch trace và counts trước/sau; K0 sau archive identity evidence. C-24 và D01 invalidation dependency; BLOCKED, không tự chọn retention duration/schema.

#### X-24 — rejected attempt replay và rollback identity limit; status BLOCKED

- **Preconditions/roles/data:** A/B=A cùng scoped key, deterministic authorized domain rejection; selected rejection set/storage policy còn OPEN. Malformed/unauthenticated control tách khỏi domain rejection; policy đổi để old request trở nên executable là deliberate fixture.
- **A/B/order:** A reject, B lookup/replay same payload và changed payload sau policy change; concurrent B waits guard/key. Separate unexpected SQL-error/full-rollback fixture rồi same-key retry qua selected recovery protocol.
- **Expected:** committed-no-op choice: stable rejection replay và changed-payload conflict, no ACL/G/fence/success-audit; rejection receipt/audit theo frozen rule. Success-only: terminal failure không được dispatcher resend; Core không hứa persisted key binding sau rollback, corrected authorized intent cần version/key mới. Unexpected rollback không fabricate rejection receipt; retry reauthorize/current-check. Test không report success-only changed-payload conflict khi fingerprint không còn.
- **Evidence/cleanup/gate:** E0 + rejection classification/outcome/receipt immutability và dispatch trace; K0. D03/C-08/C-24 semantics, BLOCKED đến owner selection.

#### X-25 — incomplete receipt commit và role escape; status BLOCKED

- **Preconditions/roles/data:** selected completeness mechanism ở command design §3.4; A=A/W actual runtime role, B=R observer. Setup owner chỉ install reviewed fixture, không chạy runtime assertions bằng owner.
- **A/B/order:** early-reservation option: A stage mutation + incomplete receipt, skip finalization rồi attempt COMMIT; variants missing identity/fingerprint/version/outcome/applicable references, receipt delete, disable/replace validation, SET session_replication_role hoặc SET ROLE escape. Chạy selected deferred/default và SET CONSTRAINTS IMMEDIATE timings; immediate validation có thể fail sớm nhưng không được cho partial commit. B observe sau tx end. Positive complete terminal success/rejection fixtures. Final-only option: fault trước receipt insert, prove mandatory scoped-key lock trước execution và full rollback.
- **Expected:** incomplete commit abort toàn tx và F0 restored; unauthorized delete/disable/alter/role probes denied. Positive complete receipt commit đúng immutable outcome; no public/inherited bypass. Nếu application-only check có thể bị cùng role direct COMMIT bỏ qua thì không coi là database-enforced completeness; phải owner chấp nhận trust boundary rõ hoặc chọn enforcement khác, không claim T2.
- **Evidence/cleanup/gate:** E0 + commit SQLSTATE, selected trigger/protocol definitions và effective privileges, all effects snapshots; K0. D03 completeness/C-21, BLOCKED, không actual DDL trong plan.

#### X-26 — Resolve/Confirm prerequisite reservation/convergence; status BLOCKED

- **Preconditions/roles/data:** separate H/Core DBs; synchronized V6, actual eligible worker, valid Workflow W0; H resolution Z6, reassignment V7 và requester Confirm fixtures; owner chọn readiness §4.1 option.
- **A/B/order:** H commits Z6 prerequisites/intent, barrier trước Core Resolve commit; competing H V7 attempts acceptance, Core Resolve serializes trước replacement và commit W1/RESOLVED. Run reservation-selected và supersede-selected schedules riêng, không đổi passing option theo implementation. Confirm variant đổi H prerequisites giữa Core authorized read và transition/finalize; inject lost ACK/restart/local CAS failure.
- **Expected:** reservation option V7/competing action không supersede reserved versions; unknown outcome giữ reservation/reconciling, status+same-intent finalize đúng một lần rồi release. Supersede option Core commit giữ nguyên, old CAS=0, durable conflict/reconciling + explicit authorized recovery disposition trước business complete; no automatic reverse transition hoặc discard committed history. Confirm không complete khi matching resolution/prerequisites chưa finalize; reservation hoặc conflict disposition phải chặn stale completion. Current ACL check độc lập.
- **Evidence/cleanup/gate:** E0 + both DB intent/reservation/CAS/receipt/history traces, restart persistence và gate responses; K0 cả hai DB. P1-06/C-16..19/C-30/R29 E2E; BLOCKED đến convergence/recovery authority chọn, runtime NOT RUN.

### 5.4 Evidence disposition / unresolved issues

Tất cả case trên là future specification: không có actual test command, test SHA implementation, role/grant snapshot hoặc PostgreSQL artifacts mới trong task này. Không case nào được đánh dấu PASS bởi việc viết plan. Chạy bằng superuser, skipped suite, missing barriers, green docs lint hoặc unit tests không thay T07/T08 least-privilege evidence.

Blockers cần đóng trước chạy: actual schema/identity/managed slice, D-01 command classes/invalidation, ledger rejection/retention/status, chosen lock/privilege mechanism, future disposable harness và owner deadlines/emergency procedure. Không giảm C-20..23/C-25/26 assertions để khớp implementation. Plan gồm case transaction lẫn future service fault injection; PostgreSQL-only results sẽ không được gọi runtime E2E.

Next actions: Bảo review locking/privileges/cases, Yến approve owner/gate scope và Ánh review X-12/X-13/X-16 + PR #145. Sau applicable approvals mới tạo riêng executable harness/migrations và gắn exact command/evidence vào từng case. Task hiện tại kết thúc ở documentation-only review.