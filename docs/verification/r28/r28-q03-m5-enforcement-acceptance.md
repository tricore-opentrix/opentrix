<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# R28 Step 2 — M5 enforcement acceptance evidence closure

**Evidence supplement, không tự nghiệm thu. STEP_2_COMPLETION = NOT_PASSED / PENDING_YEN_REVIEW.**
Baseline `ee048142c805b0a14324a3ed0557326d9880e653`, PR [#170](https://github.com/tricore-opentrix/opentrix/pull/170),
nhánh `review/r28-q03-m5-isolated-verification-20261109`, stacked trên #168/base
`docs/r28-r27a-p0-dependency-contract-20261109` tại `cecee84453cf5eaec16548959415c243675d56c4`.
SHA package cuối được báo sau commit để tránh self-reference; source thực thi pin
bằng byte snapshot + SHA-256 từng file, không gọi baseline là exact uncommitted source.

## Preflight và provenance

HEAD/remote/PR metadata khớp baseline và repository `tricore-opentrix/opentrix`.
Worktree ban đầu chỉ có `?? portal-bff/bin/`, được giữ ngoài commit.
GitHub trả `reviews=[]` và `comments=[]` cho #170 ở lần đọc này; không dựng một review
mới chưa quan sát được. Checklist bổ sung lấy từ yêu cầu tác vụ hiện tại và
[review Yến tại cecee844](https://github.com/tricore-opentrix/opentrix/pull/168#pullrequestreview-5823960897).
[Bảo đã chọn A/M5](https://github.com/tricore-opentrix/opentrix/pull/168#issuecomment-6736636086);
[Ánh giữ Q06 B/Q08 B và chuẩn bị cutover](https://github.com/tricore-opentrix/opentrix/pull/168#issuecomment-6736714175).
Không có owner confirmation mới cho các option còn mở.

[Audit lịch sử](evidence/REVIEW/20261109-m5-acceptance-closure/history-audit.json)
kiểm tra 437 payload run 05, đủ 388 case artifact khớp summary, 5 source snapshot
khớp byte baseline. Tám hàm oracle lịch sử không đổi theo AST. `schema.sql`/grant SHA-256
vẫn `0cd560b10bfe0eb067e0f8e147e90bb52d33e9dbb90c2778ff2f11a9392bc99c`.
Đây là kiểm tra provenance/integrity của **388/388 prototype PASS**, không phải
independent rerun hoặc production acceptance. Report/evidence lịch sử giữ nguyên.

| Run | Kết quả và ý nghĩa |
| --- | --- |
| `20261109-m5-isolated-05` | 388/388 prototype PASS lịch sử; X-25 19, T07 4, T08/X-09 359, X-12 2, X-13 4; X-23/X-24/X-16/X-26 chưa chạy |
| `20261109-m5-enforcement-preflight-07` | Docker daemon tắt; BLOCKED trước SQL, 0 DB case |
| `20261109-m5-enforcement-08` | 418 DB case: 413 PASS, 5 FAIL; exit 2 vì fixture maintenance lỗi cú pháp. 5 exact-allow-list FAIL `42703` do biến record `c` che alias SQL; maintenance `42601` do `ENABLE ALWAYS TRIGGER USER` không hợp lệ. Không có counterexample runtime receipt-less commit được quan sát. Giữ nguyên lỗi/artifact/source snapshot riêng, không hồi tố PASS |
| `20261109-m5-enforcement-09` | 447 case: 446 PASS, 1 FAIL; exit 1. 388 case cũ đều PASS; exact migrator probe FAIL `42501` vì text→regclass lookup cần schema USAGE mà migrator cố ý không có. Sửa lookup sang catalog OID, không cấp thêm USAGE. Audit FAIL vì manifest HARNESS bỏ sót 9 source snapshot; giữ nguyên artifacts và audit lỗi |
| `20261109-m5-enforcement-10` | Chỉ supplement trên fixture mới: 60/60 PASS, exit 0; không rerun 388 case. Audit vẫn FAIL vì source snapshot chưa nằm trong manifest; không dùng làm package provenance hoàn chỉnh |
| `20261109-m5-enforcement-11` | **60/60 supplement PASS, 0 FAIL, exit 0**, 13/13 offline checks PASS. Audit PASS: 98 payload, 9 source snapshot khớp current bytes, không unlisted/missing payload. Đây là run supplement hiện hành; không ghi thành 448 case cùng một source/run |

Docker Desktop được khởi động sau preflight 07. Mọi SQL chạy qua full ID của container
PG17 mới có task/run labels, image ID/digest đã pin, `network none`, không port/bind
mount/privileged mode, PGDATA tmpfs. Bootstrap credential sinh riêng trong memory;
runtime dùng actual LOGIN roles qua Unix socket local trust, không claim SCRAM.
Không exec SQL, sửa schema/grants hoặc thao tác container staging/production.

Run 11: PostgreSQL **17.11** (`170011`, Debian 17.11-1.pgdg13+2), image ID và RepoDigest
`sha256:2d2b8998d31037bf721cfdf764d76ba74171b4fab3431b7f72c27c56ddbdf9e3`;
container `3a081f5218a9ce61696e235673fd30d2b1a067927284dcdcdc35a2fd5f41a75f`.
Cleanup PASS; metadata ID/name/image/state của các container có sẵn không đổi.
Bootstrap-value scan trong memory: 105 file, 0 match; không lưu credential.

| Run 11 group | Executed / PASS / FAIL | Group acceptance |
| --- | --- | --- |
| X-25 | 10 / 10 / 0 | PARTIAL_NOT_ACCEPTED |
| T07 | 15 / 15 / 0 | BLOCKED: actual ACK-drop thiếu |
| T08/X-09 | 11 / 11 / 0 | PARTIAL_NOT_ACCEPTED |
| X-12 | 3 / 3 / 0 | PARTIAL_NOT_ACCEPTED |
| X-23 | 9 / 9 / 0 | BLOCKED: approved Q05 thiếu |
| X-24 | 12 / 12 / 0 | BLOCKED: main rejection receipt chưa có; 7 case chỉ exploratory |
| X-13, X-16/X-26 | 0 / 0 / 0 | Không rerun X-13 standalone; 4 authenticated status-first probes ở T07 và revoke status ở T08. Consumer integration vẫn BLOCKED |

## Lệnh tái lập và artifact

```powershell
python -B -m unittest discover -s tests/r28_m5 -p test_harness.py -v
python -I -B tests/r28_m5/launch.py --acceptance --run-id <NEW_UNIQUE_RUN_ID>
python -I -B tests/r28_m5/launch.py --acceptance-only --run-id 20261109-m5-enforcement-11
python -I -B tests/r28_m5/audit.py --run-id <RUN_ID>
```

Mỗi group/run có `environment.json`, `result.json`, case JSON và `checksums.json`.
`HARNESS/<run>/source/` chứa executed source; `preflight.json` pin PostgreSQL version,
image digest, full container ID, socket DSN, role và isolation trước SQL.
`completion.json` chứa cleanup, offline publication SQL/log, blockers và inventory.
Case JSON chứa command/actor, SQL hoặc session SQL/traces/PID/lock barrier,
SQLSTATE, expected/observed, before/after. Provenance chỉ tới source/schema/grant SHA.
Checksum tra bằng đúng artifact path trong manifest; không sao chép hash thủ công.
Superuser chỉ publish fixture/observe catalogs/kill test backend/backup restore;
bằng chứng runtime isolation đến từ actual non-owner sessions.

Lệnh run 11 trên là exact invocation đã chạy; run ID không được dùng lại.
[Audit run 11](evidence/REVIEW/20261109-m5-acceptance-closure/run11-audit.json),
[offline 13/13](evidence/REVIEW/20261109-m5-acceptance-closure/offline-final.json),
[publication SQL hashes](evidence/REVIEW/20261109-m5-acceptance-closure/publication-hashes.json).
Các hash publication bổ sung cho baseline schema/grant SHA khi cố ý publish faulty
definer hoặc temporary legacy grants; không gọi baseline grant SHA là active grant
graph của từng fault. SQL và catalog snapshots cho phép dựng lại trạng thái đó.

- [X-25 result + case artifacts](evidence/X-25/20261109-m5-enforcement-11/result.json), [checksums](evidence/X-25/20261109-m5-enforcement-11/checksums.json).
- [T07 result + session/kill/timeout/deadlock traces](evidence/T07/20261109-m5-enforcement-11/result.json), [checksums](evidence/T07/20261109-m5-enforcement-11/checksums.json).
- [T08/X-09 result + catalogs/allow-list/revoke/publication](evidence/T08-X-09/20261109-m5-enforcement-11/result.json), [checksums](evidence/T08-X-09/20261109-m5-enforcement-11/checksums.json).
- [X-23 restore/admission/tombstone](evidence/X-23/20261109-m5-enforcement-11/result.json), [X-24 exploratory/main rollback](evidence/X-24/20261109-m5-enforcement-11/result.json), [X-12 schedules](evidence/X-12/20261109-m5-enforcement-11/result.json).
- [Preflight/source/environment](evidence/HARNESS/20261109-m5-enforcement-11/preflight.json), [completion/offline SQL/inventory/secret scan](evidence/HARNESS/20261109-m5-enforcement-11/completion.json), [source manifest](evidence/HARNESS/20261109-m5-enforcement-11/checksums.json).

## Phạm vi case bổ sung

| Nhóm | Đã bổ sung thực thi | Giới hạn/điều kiện còn mở |
| --- | --- | --- |
| X-25 | Hai transaction độc lập: original giữ tenant guard, faulty executor bỏ lookup chờ guard rồi đụng receipt UNIQUE `23505`; winner-only snapshot. `ON CONFLICT DO NOTHING` không đủ receipt transaction hiện tại, phải fail `23514`. Forged principal/resource/key, reused audit, omission, direct multi-row/multi-table DML, partial savepoint rollback; oracle cũ giữ nguyên | Fault definer/grant chỉ publish offline trong disposable. Đây là finite prototype writer set, không all-deployed-writer proof |
| T07 | `pg_terminate_backend(pid,5000)` gửi SIGTERM thật ở before mutation, after mutation, before COMMIT sau validate, COMMIT-in-flight bị deferred barrier giữ; `57P01`, full rollback, authenticated status UNRESOLVED trước same-key retry. Guard lock_timeout `55P03`, statement_timeout `57014`, actual executor/reader lock-cycle deadlock `40P01`; original-first/retry-first/delayed-original/rollback-replay | COMMIT-in-flight test quan sát được nhánh rollback, không chứng minh lost successful COMMIT ACK. Actual ACK-drop **BLOCKED**: network none/host reject/Unix socket, chưa có transport proxy được xác minh; không đổi isolation. Không SIGKILL/postmaster crash hoặc Java transport test |
| T08/X-09 | Exact effective schema/table/column/function allow-list trên actual roles, signatures/owner/membership/SET ROLE/PUBLIC EXECUTE/default privileges/definer search_path/trigger state; transactional CREATE+GRANT failure rollback, migrator denied; revoke-first guard barrier rồi fresh auth `42501`, status hidden | Authority revoke publisher là privileged offline probe; không chứng minh production revoke writer hoặc Workflow integration |
| X-23 | Retention DELETE denial và immutable trigger; retained late original replay; owner bypass, closed admission, receipt-less ACL drift detection, exact snapshot reconciliation; actual closed-backup pg_dump/pg_restore trong cùng disposable container, runtime không được execute sau restore; tombstone new command denial và retained replay | Probe thăm dò, chưa approved Q05 procedure; OPEN/stale backup, PITR, durable retirement, duration/compaction/reopen authority chưa chốt. Reconciliation ở đây dựa trên exact saved fixture, không là production recovery mechanism |
| X-24 | Main executor deterministic stale G/nonadvancing fence rollback lặp lại, APPLIED payload conflict; schema `m5_probe` riêng thăm dò REJECTED_TERMINAL keyed immutable result/replay, payload conflict và DML/owner-trigger denial | Main M5 receipt vẫn chỉ `APPLIED`; candidate rejection không phải approved contract, không có rejection audit policy đã chốt. X-24 acceptance BLOCKED Q02 |
| X-16/X-26 | [Consumer fixture](../../../tests/r28_m5/consumer_fixture.json) chuẩn bị timeout/restart, durable reservation, superseded CAS, receipt/history retention và authorized manual reconciliation | 0 consumer integration case; thiếu approved consumer contract và consumer environment; giữ BLOCKED |

Owner/superuser bypass được xác nhận là giới hạn, không gọi đó là grant-based isolation.
Nếu non-privileged writer commit effect thiếu matching receipt, oracle phải FAIL;
không được sửa expected thành PASS. Regression offline kiểm tra counterexample vẫn
được ghi FAIL và matching-receipt oracle từ chối tampering.
PostgreSQL xác nhận quyền owner có thể thay object và quyền thông thường không thể
loại bỏ khả năng đó ([PG17 privileges](https://www.postgresql.org/docs/17/ddl-priv.html));
backend termination được dùng theo [server signaling](https://www.postgresql.org/docs/17/functions-admin.html#FUNCTIONS-ADMIN-SIGNAL).

## Decision closure — không ký thay owner

| ID | Option giữ/đề xuất | Rủi ro cần quyết định | Ảnh hưởng R29 | Owner và evidence | Closure |
| --- | --- | --- | --- | --- | --- |
| Q02 | Đề xuất receipt rejection chỉ cho authorized monotone stale G/nonadvancing fence/immutable tombstone; auth/malformed/infra không bind key | Reversible rejection bị đóng vĩnh viễn; disclosure; error precedence/rejection audit chưa chốt | Persist original intent; phân biệt rejection/unknown; không tự release reservation | Bảo chốt Core classes; Ánh consumer; Yến security. Main rollback + exploratory `contract_probes.sql` | OWNER_CONFIRMATION_REQUIRED |
| Q03 | **Giữ A/M5 Final-only**, ACL-admin assignment, đã chọn có điều kiện | Cần capability confinement + actual-delta deferred validation; owner protection procedural; legacy writer coexistence không hợp lệ | Không thay Q08 durable reservation; Create/Workflow ngoài scope | Bảo decision `6736636086`, Yến review `5823960897`; run mới cần exact-SHA independent review | DIRECTION_SELECTED_CONDITIONALLY; ENFORCEMENT_ACCEPTANCE_PENDING |
| Q04 | Đề xuất versioned server-derived canonical profile + tenant/service/resource incarnation + golden vectors | Ambiguous identity, integer/decimal/null/duplicate/unknown/set ordering, upgrade semantics; JSONB synthetic không phải canonical wire | Giữ nguyên key/payload/G/fence/version; không manufacture retry intent | Bảo + Ánh; Yến identity. Design §9 và source fixture; chưa có approved golden bytes | OWNER_CONFIRMATION_REQUIRED |
| Q05 | Đề xuất full receipt/identity retained, không TTL delete; restore admission closed, reconcile trước reopen | Retention/privacy, compaction, key retirement và stale backup có thể tái thực thi | Missing lookup luôn UNRESOLVED; reservation không auto release | Bảo + Yến + operations, Ánh consumer; X-23 exploratory evidence | OWNER_CONFIRMATION_REQUIRED |
| Q07 | Đề xuất narrow lock helper, split roles/pools, không UPDATE(acl_revision), guard order trước FK | Membership/SET/PUBLIC/default-grant drift, timeout/SLA, partial publication; credential cutover | H không Core SQL sau approved cutover; dependency FK/trigger phải xử lý | Bảo + Yến, Ánh cutover; exact allow-list/publication/revoke-first evidence | OWNER_CONFIRMATION_REQUIRED |

Giữ Q06 **Option B conditional S**, Q08 **Option B durable reservation/manual
reconciliation**, ADR-015 **Model T1**. Không tự đổi sang Early Reservation hoặc T2.

## All-writer coverage và handoff

[W-01–W-17 ledger hiện hành](r28-q03-all-writer-coverage-matrix.md) đối chiếu từng
source path với privilege evidence disposable và phần deployment còn thiếu. Không
writer nào CLOSED. W-17 vẫn **BLOCKED/UNINVENTORIED**, không có deployed/external
writer inventory. Legacy Helpdesk cutover chỉ lập kế hoạch theo Ánh, không thực hiện.

Yến independent review exact resulting SHA: kiểm tra lại manifest/provenance và suy
ra kết luận từ logs/snapshots; chỉ Yến quyết định STEP_2_COMPLETION PASSED hay
CHANGES_REQUIRED. Ánh xác nhận receipt/status fields, X-16/X-26, R29 scope/cutover;
Bảo xác nhận Q02/Q04/Q05/Q07. [Handoff](r28-q03-m5-review-handoff.md) là yêu cầu review
được chuẩn bị, không chứng nhận phản hồi đã có hoặc gửi thông điệp riêng.

| Final disposition | Trạng thái |
| --- | --- |
| X25 | PARTIAL_NOT_ACCEPTED — prototype evidence; independent/deployed closure thiếu |
| T07 | BLOCKED — actual ACK-drop, crash/transport coverage thiếu |
| T08_X09 | PARTIAL_NOT_ACCEPTED — actual fixture role proof, chưa deployment/cutover |
| X23 | BLOCKED — approved retention/restore/retirement contract thiếu |
| X24 | BLOCKED — Q02; terminal rejection chỉ là exploratory fixture |
| X16_X26 | BLOCKED — consumer contract/environment thiếu |
| W01_W17 | BLOCKED — không writer nào CLOSED; W-17 UNINVENTORIED |
| Q02_Q05_Q07 | OWNER_CONFIRMATION_REQUIRED — bao gồm Q04; Q03 direction giữ A/M5 |
| STEP_2_COMPLETION | NOT_PASSED / PENDING_YEN_REVIEW — đề nghị CHANGES_REQUIRED khi các P0 blocker còn mở; Yến quyết định |
| Q06 | NOT_FROZEN |
| RESEND | DISABLED |
| G0_CONTRACT | BLOCKED |
| R27A_IMPLEMENTATION | NOT_AUTHORIZED |
