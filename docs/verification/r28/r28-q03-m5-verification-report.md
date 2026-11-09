<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# Q03 M5 — isolated prototype và hồ sơ P0 chưa đủ điều kiện đóng

**Kết quả: BLOCKED; 0 test PostgreSQL đã chạy; 0 DB PASS / 0 DB FAIL.**
Ngày kiểm tra: 2026-11-09. Có prototype/harness test-only và 6 kiểm tra offline PASS;
chưa có bằng chứng thực nghiệm cho semantic trigger, atomic receipt hay privilege graph.

## Baseline và quyền thực thi

Đã đọc GitHub metadata, discussion, review và owner decision trước khi sửa file:

| Nguồn | Trạng thái kiểm tra |
| --- | --- |
| [PR #168](https://github.com/tricore-opentrix/opentrix/pull/168) | OPEN/Draft, actual head `cecee84453cf5eaec16548959415c243675d56c4`; local HEAD ban đầu khớp, không có delta baseline |
| [Yến M5 review](https://github.com/tricore-opentrix/opentrix/pull/168#pullrequestreview-5823960897) | Reviewed đúng baseline; ACCEPT WITH CONDITIONS chỉ cho hướng thiết kế |
| [Bảo M5 decision](https://github.com/tricore-opentrix/opentrix/pull/168#issuecomment-6736636086) | Chọn A/M5 có điều kiện; chỉ authorize isolated disposable PG17 verification |
| [Ánh consumer/cutover response](https://github.com/tricore-opentrix/opentrix/pull/168#issuecomment-6736714175) | Q06 B/Q08 B; R29 delta và legacy cutover chuẩn bị, chưa áp dụng |
| [PR #165](https://github.com/tricore-opentrix/opentrix/pull/165) | OPEN/Draft, head `2335a0858b6eafeacdff82bf157b44df116145bc` |
| [R29 #145](https://github.com/tricore-opentrix/opentrix/pull/145) | Head `5d577dd4a0a8efa830459cf35cb1868e52a9de2f`; không sửa branch hoặc contract |

Đã đọc sáu tài liệu mandatory, ADR-015, Core Java `HelpdeskService` và
`PostgresWorkflowPersistence`, policy schema, Helpdesk lock triggers, runtime grants,
cùng các source paths trong writer matrix. Thư mục có sẵn `portal-bff/bin/` giữ nguyên.
Không đổi Java/runtime SQL/migration/grants/ADR/R29 hay dịch vụ triển khai.

**Source prototype commit:** `161dc0d5be0c5c367155eddb33ad6d8fe0eba753`.
Evidence run ghim commit này cùng SHA-256 của từng source file; working tree prototype
sạch khi chạy. Commit hồ sơ sau đó được xác định bằng `git rev-parse HEAD`, không tạo
self-reference SHA trong file thuộc chính commit đó. Chưa push branch/merge/activate.

## Môi trường và kết quả thực thi

Lệnh đã thử ngoài sandbox:

```powershell
docker version --format '{{json .Server}}'
python -B tests/r28_m5/run.py --run-id 20261109-m5-preflight-02
```

Docker trả `null`, không tìm thấy pipe `dockerDesktopLinuxEngine`: daemon local không
hoạt động. Runner sau đó phát hiện **tên** biến `CART_DB_PASSWORD`, `ORDER_DB_PASSWORD`
trước bất kỳ Docker/DB operation nào; không đọc/ghi giá trị chúng vào evidence.
Không xác định được nguồn/test-only status của credential, nên fail closed.
Run mới ghi trực tiếp process exit **2** và exact command tại
[preflight invocation](evidence/HARNESS/20261109-m5-preflight-02/preflight-invocation.json);
không có DB execution.
Không sanitize các biến rồi kết nối thử để vượt qua điều kiện an toàn.

Run lịch sử `20261109-m5-preflight-01` tại source
`6627699124079ab1d76f6ac8ba5433e4359a567c` được giữ nguyên (5 offline checks, 0 DB).
Revision hiện tại sửa global default function privileges và thêm regression check;
run `20261109-m5-preflight-02` ghim source mới, 6 offline checks, vẫn 0 DB.

| Thuộc tính cần chứng minh | Quan sát thực tế |
| --- | --- |
| PostgreSQL version | NOT ESTABLISHED / null |
| Image digest, container identity | NOT ESTABLISHED / null; không tạo container |
| Disposable DSN | Chỉ có cấu hình dự kiến Unix socket trong container mới; chưa tồn tại DB |
| Credential safety | NOT ESTABLISHED; dừng trước kết nối |
| Schema/grant SHA-256 | `0cd560b10bfe0eb067e0f8e147e90bb52d33e9dbb90c2778ff2f11a9392bc99c`; grant nằm cùng `schema.sql` |
| Fixture | Chưa load; chỉ định nghĩa synthetic T1/T2, R1/R2, admin/old/new, G10/fence5 |
| Actual role, SQLSTATE, transaction trace, before/after | NOT AVAILABLE; không có session PostgreSQL |

Evidence thật của preflight nằm tại:

- [X-25 result](evidence/X-25/20261109-m5-preflight-02/result.json)
- [T07 result](evidence/T07/20261109-m5-preflight-02/result.json)
- [T08/X-09 result](evidence/T08-X-09/20261109-m5-preflight-02/result.json)
- [Environment/source hashes](evidence/X-25/20261109-m5-preflight-02/environment.json)
- [Checksums](evidence/X-25/20261109-m5-preflight-02/checksums.json)

Evidence `.gitattributes` giữ nguyên byte JSON khi commit/checkout, tránh Git đổi
CRLF/LF làm sai checksum trên máy của reviewer.

X-12/X-13/X-23/X-24/X-16-X-26 cũng có result/environment/checksums cho cùng run ID,
đều BLOCKED và 0 ca DB. Không có snapshot hay SQLSTATE giả lập được trình bày như thực nghiệm.

## Prototype đã chuẩn bị và phạm vi bằng chứng

[Hướng dẫn tái lập](../../../tests/r28_m5/README.md),
[schema](../../../tests/r28_m5/schema.sql),
[runner](../../../tests/r28_m5/run.py),
[offline checks](../../../tests/r28_m5/test_harness.py).

Layer 1: owner NOLOGIN tách biệt; actual LOGIN roles; không online owner membership;
không runtime DML; hardened definer, schema qualification, PUBLIC revoke/default revoke.
Executor kiểm tra caller/T1 principal scope, tenant-exclusive guard trước DML/FK lock,
admission, scoped replay/conflict, current authority, expected G/fence; thay ACL,
advance G/fence, audit rồi receipt trong cùng transaction. Tenant-exclusive guard
serialize cả các key cùng tenant, không cần khóa một receipt chưa tồn tại.

Layer 2: capture trigger ghi old/new thực tế vào immutable mutation log, deferred
constraint trigger trên 10 bảng kiểm tra receipt cuối transaction. Audit phải khớp
actual changes, cùng tenant/resource/key/principal/service/operation/G/fence/xid;
receipt APPLIED cũng bị kiểm tra ngược về actual effect. Membership, registry, binding,
authority, admission mutation không thuộc assignment bị fail closed, kể cả có receipt.
Đây là proposal hardening cần Yến review, chưa chứng minh bằng PostgreSQL.

Điểm sửa thiết kế: digest receipt = digest audit **không đủ** chứng minh audit đúng ACL.
Prototype đối chiếu delta do trigger ghi lại. Hàm đọc delta khai báo VOLATILE để tránh
snapshot STABLE khi quan sát mutation trong cùng outer call. Deferred validator query
lại bảng cuối transaction, không dùng queued NEW như trạng thái cuối.
Owner dùng global default privilege revoke: per-schema revoke không loại được default
PUBLIC EXECUTE global theo [PG17 ALTER DEFAULT PRIVILEGES](https://www.postgresql.org/docs/17/sql-alterdefaultprivileges.html).
Các quy tắc visibility phù hợp với [trigger visibility PG17](https://www.postgresql.org/docs/17/trigger-datachanges.html)
và [constraint trigger timing](https://www.postgresql.org/docs/17/sql-createtrigger.html);
đây là suy luận thiết kế từ docs, **không phải kết quả chạy**.

| Nhóm | Ca harness đã chuẩn bị | Kết quả DB / phần còn thiếu |
| --- | --- | --- |
| X-25 | Multi-row normal; omission; INSERT CHECK/NOT NULL failure; wrong digest/xid/audit/actual ACL; receipt change/delete; savepoint; immediate constraints; legacy ACL/G write; runtime DML/escalation | NOT RUN/BLOCKED; autonomous unique conflict và owner-bypass reconciliation chưa có executable case |
| T07 | READ COMMITTED; không lộ staged effects; reader-first lock; rollback winner; COMMIT-response discard model + status | NOT RUN/BLOCKED; kill stages, actual network ACK drop, lock/statement timeout/deadlock còn thiếu |
| T08/X-09 | Actual-role DML matrix trên 11 bảng; function/owner/trigger/role/parameter/default/schema catalogs; no UPDATE(acl_revision); reader helper positive control | NOT RUN/BLOCKED; đầy đủ exact grant allow-list assertion, atomic publication failure và revoke-first authorization còn thiếu |
| X-12 | Original-first cùng key; winner rollback và follower thực thi; lock graph barrier | NOT RUN/BLOCKED; retry-first/delayed-original đầy đủ lịch còn thiếu |
| X-13 | COMMITTED/UNRESOLVED, wrong principal/resource, direct receipt denial | NOT RUN/BLOCKED; revoke, expiry/auth transport/latency/error mapping chưa được chốt |
| X-23 | Không cleanup/TTL; immutable receipt | NOT RUN/BLOCKED; tombstone/restore/reopen và privileged procedure chưa có fixture được duyệt |
| X-24 | G/fence conflict rollback, không tạo receipt rejection | NOT RUN/BLOCKED; không thay thế terminal rejection proof; Q02 chưa chốt |
| X-16/X-26 | Giữ spec consumer, request Ánh fixture/status fields và cutover confirmation | NOT RUN/BLOCKED; chưa có Helpdesk reservation/CAS integration |

Không suy rộng từ prototype sang production-shaped schema đầy đủ. SQL chưa được
parse/load bởi PostgreSQL; chưa có counterexample thực nghiệm và cũng chưa có proof.
Một bypass non-privileged thực nghiệm sẽ khiến M5 CHANGES_REQUIRED/REJECTED.
Owner/superuser có thể sửa function/disable trigger/journal: ngoài ordinary grants,
chỉ xử lý bằng offline admission-closed maintenance + reconciliation được review riêng.

## Q02–Q05/Q07 — đề xuất quyết định, không tự freeze

| ID | Proposed Core choice | Security implications | Helpdesk/R29 implications | Owner confirmation cần có | Status |
| --- | --- | --- | --- | --- | --- |
| Q02 | Chỉ receipt deterministic authorized monotone rejection: stale G, nonadvancing fence, immutable tombstone; auth/hidden/malformed/infra không bind key | Tránh lỗi reversible thành terminal hoặc leak receipt; phải duyệt error/audit classes | Exact-intent CAS/manual closure phải phân biệt rejection và unknown | Bảo + Ánh; Yến policy/security | PROPOSED; prototype chỉ rollback, X-24 BLOCKED |
| Q03 | Giữ owner-selected A/M5, Final-only, scope ACL-admin assignment | Cần cả capability confinement và deferred actual-delta validation; không chống owner | Không thay Q08; legacy receipt-less writers không được coexist khi cutover | Bảo chọn direction tại baseline; Yến conditional direction; new-source review còn thiếu | DESIGN_DIRECTION ACCEPTED_WITH_CONDITIONS; ENFORCEMENT CHANGES_REQUIRED |
| Q04 | Versioned server-derived typed canonical profile, exact tenant/service/resource/incarnation, integer/range/null/unknown rules, approved golden bytes/digests | Chặn client digest và ambiguous identity; bảo toàn nghĩa key khi upgrade | Persist nguyên scoped key/payload/G/fence/version; không tự refresh | Bảo + Ánh; Yến identity | PROPOSED; synthetic JSONB profile không phải wire freeze |
| Q05 | MVP giữ full receipt/identity, không TTL delete/compaction; restore closed, reconciliation trước reopen | Chống key reuse và stale backup; duration/tombstone/retirement authority cần quyết định | Status absent vẫn UNRESOLVED; reservation không tự release | Bảo + Ánh; Yến retention/restore + operations owner | PROPOSED; X-23 BLOCKED |
| Q07 | Narrow lock-only definer, riêng pool/role, không UPDATE(acl_revision), guard order trước FK | Kiểm chứng effective graph/SET reachability/publication; T1 principal do Core xác nhận | H không Core SQL; cần bỏ FK/trigger cross-owner theo cutover riêng | Bảo + Yến; Ánh reviewer cutover | PROPOSED; T08/X-09 BLOCKED |

Q01 managed-slice/admin invalidation, Q08 cancellation/convergence, Q09 cutover/emergency
authority vẫn mở. Giữ D-01 A, ADR-015 Model T1, OD-06 A.
Q06 **Option B / Conditional Protocol S**, Q08 **Option B / durable reservation + manual
reconciliation** được bảo toàn theo owner; joint contract chưa freeze; status-first;
RESEND DISABLED; automated worker DEFERRED. Không sửa owner selection hay R29 #145.

## P0 blockers và disposition

1. Môi trường an toàn chưa xác lập: service password variables chưa rõ nguồn và Docker
   daemon local không hoạt động. Cần một phiên test sạch được xác nhận, official image
   PG17 có digest sẵn, rồi chạy run ID mới; không dùng DSN/service credentials hiện hành.
2. X-25/T07/T08 và dependencies chưa chạy; SQL/privileges/commit-time visibility chưa
   được verify. Cần bổ sung các gap executable ở bảng trên, không giảm oracle.
3. W-01–W-16 còn source/cutover/maintenance evidence; W-17 deployed catalog và external
   credential/writer inventory BLOCKED. Không có approved exclusion thay cho closure.
4. Q02/Q04/Q05/Q07 và Q01/Q08/Q09 chi tiết chưa được owner/security chốt; R29 reviewed
   delta, X-17 và X-16/X-26 chưa có. Maintenance/restore procedure chưa verify.
5. Yến cần review độc lập exact source + evidence + resulting package SHA. Đây không
   phải personal Core sign-off, Step 2 PASS, G0 acceptance hoặc permission triển khai.

| Item | Final disposition |
| --- | --- |
| M5_DESIGN_DIRECTION | ACCEPTED_WITH_CONDITIONS — theo Yến tại baseline, chỉ direction |
| M5_ENFORCEMENT_VERIFICATION | BLOCKED / CHANGES_REQUIRED |
| ALL_WRITER_COVERAGE | BLOCKED; W-17 UNINVENTORIED |
| ATOMIC_RECEIPT | NOT_PROVEN / NOT_RUN |
| X25 | NOT_RUN / BLOCKED; 0 DB cases |
| T07 | NOT_RUN / BLOCKED; 0 DB cases |
| T08_X09 | NOT_RUN / BLOCKED; 0 DB cases |
| Q02_Q05_Q07 | PROPOSED / OWNER_CONFIRMATION_PENDING; bao gồm Q04; Q03 direction riêng |
| Q06 | OPTION_B_CONDITIONAL_S / NOT_FROZEN |
| RESEND | DISABLED |
| STEP_2_COMPLETION | NOT_PASSED |
| G0_CONTRACT | BLOCKED |
| R27A_IMPLEMENTATION | NOT_AUTHORIZED |

Offline command: `python -B -m unittest discover -s tests/r28_m5 -p test_harness.py -v`:
6/6 PASS. Kiểm tra này chỉ xác nhận fault generator, manifest tĩnh, local-socket role
command, credential fail-closed và ghi evidence/checksum BLOCKED với zero execution.
Output được lưu ở [offline-checks.json](evidence/HARNESS/20261109-m5-preflight-02/offline-checks.json).
[Package checks](evidence/HARNESS/20261109-m5-preflight-02/package-checks.json) ghi số
local links/checksums đã kiểm tra, source hashes khớp exact commit, đủ 13 disposition
và mọi DB result BLOCKED/zero execution.
[Scoped REUSE check](evidence/HARNESS/20261109-m5-preflight-02/reuse-check.json) lưu
exact lint-file command, danh sách file và exit code; không phải repository-wide CI.
Reproduction tiếp theo dùng [README](../../../tests/r28_m5/README.md) và run ID mới;
giữ nguyên evidence preflight thất bại, không overwrite. Không CI/backend/service E2E PASS claim.
