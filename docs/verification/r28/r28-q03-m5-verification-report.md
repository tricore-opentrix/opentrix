<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# Q03 M5 — isolated prototype và hồ sơ P0 chưa đủ điều kiện đóng

**Kết quả hiện tại: PARTIAL_NOT_ACCEPTED — preflight PASS, 388 ca DB prototype PASS,
0 FAIL trong run cuối `20261109-m5-isolated-05`. Chưa đủ điều kiện đóng M5/Step 2.**
Ngày kiểm tra: 2026-11-09. Local HEAD vẫn là
`f26f0ed10e80c108015944e46d61bad481ca07fd`; thay đổi test-only chưa commit trên nhánh
`review/r28-q03-m5-isolated-verification-20261109`. Đây là kiểm chứng prototype synthetic,
không phải production sign-off hoặc independent security review.

## Run cuối 05 — hồ sơ review hiện hành

Đã đọc toàn bộ runner/preflight, offline tests và SQL fixture trước khi sửa.
Phạm vi thay đổi: thêm `tests/r28_m5/launch.py`; sửa preflight, thứ tự chạy và cách ghi
evidence trong runner; bổ sung offline regression checks; cập nhật README/báo cáo.
Không sửa `schema.sql`, oracle X-25/T07/T08, production schema/migration/grants/runtime.
Thư mục `portal-bff/bin/` có sẵn được giữ nguyên; không commit/push/merge hoặc bật resend.

Launcher tạo tiến trình Python mới với `-I -B`, chỉ truyền 7 loại biến OS cùng
HOME/USERPROFILE là thư mục tạm riêng. Parent environment không bị sửa; hai service
password không được kế thừa. Runner vẫn từ chối credential/DSN/remote target và mọi
biến ngoài allow-list trước Docker. Đây là tiến trình test mới được yêu cầu rõ ràng,
không phải unset biến trong phiên cũ để bỏ qua gate. Bootstrap password sinh mới bằng
`secrets.token_urlsafe(32)`, chỉ truyền qua environment riêng của `docker run`, đối
chiếu trong bộ nhớ và không đưa giá trị vào argv/log/source/evidence.

| Preflight | Bằng chứng thực tế run 05 |
| --- | --- |
| Container mới | `d1f7f8c7a1392caf42589d4adfdf76ffeaf8537789142e8491f992c3aa29f69e`, tên `r28-m5-afd1fab79adf456dab542f92df00ce38`; full ID/name/image và task/run labels khớp |
| Image/version | Image ID và RepoDigest `sha256:2d2b8998d31037bf721cfdf764d76ba74171b4fab3431b7f72c27c56ddbdf9e3`; binary và server PostgreSQL **17.11**, Debian 17.11-1.pgdg13+2 |
| Cách ly | `network none`; không published port, bind mount hoặc privileged mode; PGDATA `/var/lib/postgresql/data` có tmpfs config và `stat -f` trả `tmpfs` |
| DSN test | `host=/var/run/postgresql dbname=m5_disposable user=<actual LOGIN role>`; psql qua `docker exec` theo đúng full container ID, không external DSN/TCP |
| Auth thực tế | `pg_hba.conf` local trust, mọi host rule reject; actual-role positive controls; không claim SCRAM/password authentication cho runtime roles |
| Socket positive control | `postgres/postgres/m5_disposable`, `inet_server_addr() IS NULL = true`; network none tương thích Unix socket, không nới cách ly |
| Thứ tự gate | Kiểm tra image/ID/credentials/network/tmpfs/auth trước identity SQL; identity/socket control trước load fixture; preflight PASS trước các ca DB |
| Source pin | HEAD nêu trên + SHA-256 riêng cho 5 file test; working tree có thay đổi được ghi rõ; bản sao byte-exact source nằm trong `HARNESS/…/source/` |
| SQL/grants | `schema.sql` không đổi: `0cd560b10bfe0eb067e0f8e147e90bb52d33e9dbb90c2778ff2f11a9392bc99c` |
| Cleanup | PASS — chỉ xóa container mới sau khi kiểm tra lại full ID + task/run label; metadata ID/image/state của toàn bộ container có sẵn không đổi |

Lệnh đã chạy thành công:

```powershell
python -B -m unittest discover -s tests/r28_m5 -p test_harness.py -v
python -I -B tests/r28_m5/launch.py --run-id 20261109-m5-isolated-05
```

Offline **10/10 PASS**, exit 0. DB runner exit **0**, 194.458 giây; thứ tự X-25 →
T07 → T08/X-09 → X-12 → X-13. Mỗi ca dùng actual LOGIN role, có SQL/command,
SQLSTATE hoặc session trace, và snapshots before/after theo dạng ca.

| Nhóm | Ca chạy / PASS / FAIL | Trạng thái toàn nhóm | Phạm vi được chứng minh |
| --- | --- | --- | --- |
| X-25 | 19 / 19 / 0 | PARTIAL_NOT_ACCEPTED | Multi-row assignment, 10 fault variants, savepoints, immediate constraints, isolation/principal/scope rejection, legacy ACL/G denial |
| T07 | 4 / 4 / 0 | PARTIAL_NOT_ACCEPTED | Reader-first lock graph barrier; COMMIT-response discard model, status và replay; không phải network ACK-drop thật |
| T08/X-09 | 359 / 359 / 0 | PARTIAL_NOT_ACCEPTED | 5 actual roles × 11 tables × 5 DML/lock probes, escalation/DDL/parameter denial, effective catalogs, reader helpers và migrator denial |
| X-12 | 2 / 2 / 0 | PARTIAL_NOT_ACCEPTED | Original-first/replay và winner rollback; `pg_blocking_pids` xác nhận cạnh waiter/blocker |
| X-13 | 4 / 4 / 0 | PARTIAL_NOT_ACCEPTED | COMMITTED, hidden/unknown/cross-resource UNRESOLVED |
| X-23, X-24, X-16/X-26 | 0 / 0 / 0 | NOT RUN; contract/integration prerequisites còn BLOCKED | Chưa có fixture/owner decisions tương ứng; không suy luận từ các ca PASS khác |

SQLSTATE thực nghiệm: `23514` cho receipt/delta/immutability hoặc COMMIT rejection;
`23502` cho malformed NULL receipt; `42501` cho unauthorized SQL/actor/scope;
`25001` cho REPEATABLE READ. Các ca thành công exit 0; không xuất hiện SQLSTATE lỗi.
Lock/session traces và snapshots chứng minh không nhìn thấy staged effects và chỉ
một committed effect trong các lịch đã chạy. Không suy rộng thành deadlock-freedom.

Run `20261109-m5-isolated-04` cũng thực thi 388 ca, exit 0, nhưng phát hiện lỗi evidence
có sẵn: `publish_fault('insert_failure')` ghi đè file trace `fault-insert_failure.json`.
Giữ nguyên run 04 để đối chiếu, không dùng nó làm bộ X-25 evidence đầy đủ. Sửa tên
publication thành `publication-*.json`, thêm regression test, rồi chạy lại toàn bộ
trên source cuối thành run 05. Run 05 có đủ 388 case artifacts; không sửa oracle để PASS.

Evidence hiện hành:

- [Preflight](evidence/HARNESS/20261109-m5-isolated-05/preflight.json), [completion/cleanup](evidence/HARNESS/20261109-m5-isolated-05/completion.json), [exact invocation và output](evidence/HARNESS/20261109-m5-isolated-05/invocation.json)
- [Offline checks](evidence/HARNESS/20261109-m5-isolated-05/offline-checks.json), [secret audit](evidence/HARNESS/20261109-m5-isolated-05/secret-audit.json), [container inventory trước/sau](evidence/HARNESS/20261109-m5-isolated-05/container-inventory.json)
- [X-25](evidence/X-25/20261109-m5-isolated-05/result.json), [T07](evidence/T07/20261109-m5-isolated-05/result.json), [T08/X-09](evidence/T08-X-09/20261109-m5-isolated-05/result.json), [roles](evidence/T08-X-09/20261109-m5-isolated-05/catalog-roles.json), [grants](evidence/T08-X-09/20261109-m5-isolated-05/catalog-grants.json)
- [Source snapshot runner](evidence/HARNESS/20261109-m5-isolated-05/source/run.py), [HARNESS SHA-256 manifest](evidence/HARNESS/20261109-m5-isolated-05/checksums.json); mỗi nhóm có checksum manifest riêng

Secret audit kiểm tra 879 file source/report/evidence hiện có ở thời điểm run hoàn tất:
không chứa giá trị hai service credentials hoặc bootstrap password run 05; chỉ lưu
boolean/counts. Password run 04 đã bị hủy cùng container nên chỉ review đường xử lý
source, không claim value-scan cho password run 04.

**Còn thiếu / bước tiếp theo cho Yến:** review độc lập source snapshots và evidence
run 05; tái suy ra oracle từ snapshots/catalogs. Các gap vẫn giữ nguyên: X-25 autonomous
unique-conflict và owner-bypass reconciliation; T07 backend kill ở từng stage, ACK-drop
thật, lock/statement timeout và deadlock; T08 exact grant allow-list/publication-failure
và revoke-first fresh authorization; đủ lịch X-12; X-13 revoke/transport/latency;
X-23 restore/retention/admission; X-24 terminal rejection; X-16/X-26 với Ánh; W-17
deployed/external writer inventory và privileged maintenance. Q02/Q04/Q05/Q07 cùng
các owner decisions còn mở. Environment blocker đã gỡ cho tiến trình test mới;
M5 enforcement acceptance và Step 2 vẫn chưa PASS. RESEND DISABLED.

## Lịch sử run 03 — preflight dừng trước DB

Run `20261109-m5-docker-ready-03` tại cùng baseline HEAD đã BLOCKED trước tạo container
do service credentials kế thừa chưa rõ provenance. Sáu offline checks PASS, 0 ca DB.
Phần dưới giữ nguyên hồ sơ của run 03; kết quả mới ở trên thay thế kết luận hiện hành.

## Kiểm tra tiếp tục tại f26f0ed — hồ sơ cho Yến review

| Hạng mục | Quan sát và trạng thái |
| --- | --- |
| Repository | PASS — `https://github.com/tricore-opentrix/opentrix.git` |
| Worktree / branch | PASS — `D:/olp/opentrix-r28-g0-design`, `docs/r28-q03-core-enforcement-closure-20261109` |
| HEAD / harness | PASS — đúng SHA yêu cầu; `tests/r28_m5/` không có diff so với HEAD; hash bốn source file được lưu |
| Thay đổi có sẵn | `?? portal-bff/bin/`; giữ nguyên |
| Docker | PASS — `version`, `info`, danh sách container và inspect image chỉ đọc đều thành công ngoài sandbox; Linux engine 29.7.2, Docker Desktop 4.87.0 |
| Image có sẵn | `postgres:17`, Linux amd64; image ID và RepoDigest cùng `sha256:2d2b8998d31037bf721cfdf764d76ba74171b4fab3431b7f72c27c56ddbdf9e3` |
| Credentials / environment | BLOCKED — có tên biến `CART_DB_PASSWORD`, `ORDER_DB_PASSWORD`; chưa chứng minh nguồn hoặc test-only status; không ghi giá trị vào evidence |
| Container / network / volume mới | NOT RUN — dừng trước thao tác tạo tài nguyên vì preflight chưa đạt |
| Container ID / DSN / credentials mới | NOT ESTABLISHED — chưa có container hoặc kết nối; không dùng credentials hiện có |
| PostgreSQL server version | NOT ESTABLISHED — chỉ inspect image; chưa chạy server hay SQL để chứng minh major 17 |
| Offline checks | PASS — `python -B -m unittest discover -s tests/r28_m5 -p test_harness.py -v`, exit 0, 6/6 |
| Database runner | NOT RUN — không gọi `tests/r28_m5/run.py`; không tạo schema hoặc thực hiện SQL |

Docker trong sandbox ban đầu bị từ chối quyền API; kiểm tra ngoài sandbox xác nhận
daemon hoạt động. Preflight chỉ đọc tiếp theo dùng Docker config rỗng tạm thời và
endpoint cố định `npipe:////./pipe/dockerDesktopLinuxEngine`, không dùng registry
credentials hay `.env`. Hai biến nêu trên được phát hiện bằng quy tắc từ runner;
không unset/sanitize môi trường để vượt qua gate. Script ghi evidence hoàn tất exit 0;
đây **không phải** exit code của database runner, vì runner chưa được gọi.

| Nhóm ưu tiên | Kết quả kiểm chứng | Thực thi | DB PASS / FAIL | SQLSTATE, role/grant snapshot, transaction trace |
| --- | --- | --- | --- | --- |
| X-25 | BLOCKED | NOT RUN, 0 ca | 0 / 0 | Không có session DB; không tạo evidence giả |
| T07 | BLOCKED | NOT RUN, 0 ca | 0 / 0 | Không có session DB; không tạo evidence giả |
| T08/X-09 | BLOCKED | NOT RUN, 0 ca | 0 / 0 | Không có session DB; không tạo evidence giả |

X-12, X-13, X-23, X-24 và X-16/X-26 cũng BLOCKED / NOT RUN, 0 ca DB.
Không có kết luận PASS hay FAIL cho semantic trigger, atomic receipt, privilege graph.
Hai container được bảo vệ `dxos-stage6-pg17-local` và
`dxos-olp-staging-postgres-1` chỉ xuất hiện trong danh sách Docker đọc metadata;
không có exec, SQL, inspect riêng hay thao tác thay đổi chúng. Không sửa production
migration/grants/runtime, không sửa harness/oracle, không bật resend, không merge PR.

Evidence mới, không ghi đè hai lần kiểm tra lịch sử:

- [Preflight và provenance](evidence/HARNESS/20261109-m5-docker-ready-03/preflight.json)
- [Offline command, exit code và output](evidence/HARNESS/20261109-m5-docker-ready-03/offline-checks.json)
- [Danh sách container trước/sau](evidence/HARNESS/20261109-m5-docker-ready-03/container-inventory.json)
- [X-25 result](evidence/X-25/20261109-m5-docker-ready-03/result.json), [T07 result](evidence/T07/20261109-m5-docker-ready-03/result.json), [T08/X-09 result](evidence/T08-X-09/20261109-m5-docker-ready-03/result.json)
- [Environment và source hashes](evidence/X-25/20261109-m5-docker-ready-03/environment.json), [HARNESS checksums](evidence/HARNESS/20261109-m5-docker-ready-03/checksums.json); mỗi nhóm có manifest SHA-256 riêng, tổng 19 payload đã kiểm tra khi ghi

**Bước tiếp theo đề xuất cho Yến:** review blocker credentials cùng exact source/hash
tại SHA trên. Khởi tạo một phiên kiểm thử độc lập có provenance môi trường sạch và
credentials sinh riêng cho run, thay vì chỉ xóa biến của phiên hiện tại. Trước DB run,
cần đối chiếu yêu cầu tài nguyên riêng với baseline runner: runner hiện dùng network
`none`, tmpfs mới và bootstrap password synthetic cố định; chưa cung cấp named network,
named volume và password duy nhất mỗi run. Chỉ điều chỉnh cơ chế khởi tạo test-only
nếu cần sau review, giữ nguyên SQL fixture và oracle; chứng minh ID/image/version,
DSN, credentials và cách ly trước SQL, rồi chạy X-25 → T08/X-09 → T07 với run ID mới.
Các khoảng trống coverage và owner decisions bên dưới vẫn chưa được đóng.

## Hồ sơ lịch sử — preflight-01 và preflight-02

Các mục từ đây mô tả lần kiểm tra trước khi Docker hoạt động; không thay thế kết quả
`20261109-m5-docker-ready-03` ở trên.

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
