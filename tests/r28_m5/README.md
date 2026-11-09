<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# M5 — prototype kiểm chứng, không phải migration runtime

Phạm vi duy nhất: thay thế assignment trên ACL synthetic đã provision trước;
G cấp tenant, fence cấp resource, audit và receipt trong cùng transaction.
Core xác nhận principal theo ADR-015 T1; PostgreSQL kiểm tra lại authority hiện tại.
Không có API/Java bridge, CREATE/Workflow, Helpdesk CAS hoặc quyền triển khai production.

Chạy từ repository root, Python standard library và Docker Linux engine cục bộ:

```powershell
python -B -m unittest discover -s tests/r28_m5 -p test_harness.py -v
python -I -B tests/r28_m5/launch.py --run-id m5-review-001
python -I -B tests/r28_m5/launch.py --acceptance --run-id m5-acceptance-001
python -I -B tests/r28_m5/launch.py --acceptance-only --run-id m5-supplement-001
python -I -B tests/r28_m5/audit.py --run-id m5-acceptance-001
```

Image `postgres:17` phải có sẵn cùng official RepoDigest. Runner không pull image,
không nhận DSN, không đọc `.env`, không dùng Docker registry credentials.
Nó dùng Docker config rỗng, local socket/Windows DockerDesktopLinuxEngine pipe cố định,
image ID bất biến sau inspect, container mới mang UUID + task label,
`--network none`, không port/bind mount, PGDATA trên tmpfs. Host connections bị reject;
psql dùng Unix socket bên trong container với actual LOGIN role và local trust chỉ
trong container bị cô lập. PostgreSQL bootstrap superuser chỉ dùng để tạo fixture,
publish fault và chụp catalog; không thay cho actor runtime.

`launch.py` tạo process Python mới (`-I -B`), chỉ truyền allow-list biến OS;
HOME/USERPROFILE trỏ vào thư mục tạm mới. Service credentials của process cha không
được truyền vào process test; không sửa môi trường cha và không bỏ qua gate của runner.
Runner vẫn từ chối biến credential/DSN và mọi biến ngoài allow-list trước Docker.
Bootstrap password được sinh bằng `secrets.token_urlsafe(32)` mỗi run, truyền bằng
environment riêng cho `docker run --env POSTGRES_PASSWORD`, không nằm trong argv,
logs hoặc evidence. Password được đối chiếu trong bộ nhớ với container inspect;
không lưu raw inspect. Actual runtime roles dùng local trust, không có claim test SCRAM.
Network `none` tương thích với Unix socket; không cần TCP, publish port hay network mới.
Preflight kiểm tra ID/name/labels/image, network/mount/tmpfs, database/auth config,
binary PG17 trước SQL; SQL identity và Unix-socket positive control trước fixture.
Không chứng minh được bất kỳ điều kiện nào thì dừng và chỉ cleanup đúng container mới.

Runner từ chối các biến credential/DSN PostgreSQL/database hoặc Docker remote target
được nhận diện trước khi chạm Docker. Nó chỉ truyền allow-list môi trường OS cho process con;
không quét toàn máy hay chứng nhận host không chứa bất kỳ credential nào.
Không mount file host/credential vào container. PostgreSQL phải báo major version 17,
đúng database `m5_disposable`; isolation không chứng minh được thì dừng.

Exit `2` = BLOCKED/infrastructure, `1` = có ca FAIL, `0` = các ca đã chạy đạt oracle.
Ngay cả exit `0` cũng chỉ là **PARTIAL_NOT_ACCEPTED**, không phải toàn bộ X-25/T07/T08 PASS.
Mỗi run ID chỉ dùng một lần. JSON evidence + checksum nằm ở
`docs/verification/r28/evidence/<TEST_ID>/<RUN_ID>/`; lỗi preflight tạo evidence BLOCKED,
`database_cases_executed=0`. `source_commit` là HEAD lúc bắt đầu chạy; hash file đi kèm
xác định chính xác SQL/grant/harness nếu working tree có thay đổi.
Container được xóa theo ID + task label được kiểm tra lại; không dọn container/volume khác.
`HARNESS/<RUN_ID>/preflight.json` ghi preflight PASS trước fixture;
`completion.json` ghi blocker/cleanup cuối run. Thứ tự ưu tiên: X-25, T07, T08/X-09,
rồi X-12 và X-13. FAIL đã quan sát được giữ nguyên kể cả khi có blocker về sau.

`schema.sql` sở hữu mọi protected object bằng `core_acl_owner NOLOGIN`.
Migrator không có membership owner khi admission OPEN. Executor chỉ được EXECUTE;
reader/Workflow SELECT đúng policy tables + helper; Helpdesk không có table privilege;
observer test-only SELECT tất cả. Schema USAGE cho Helpdesk chỉ để kiểm tra table denial.
Receipt không sửa/xóa/truncate; không có cleanup. Trigger capture delta thực tế và
validator deferred trên cả ACL/G/fence/audit/receipt lẫn membership/registry/binding/
authority/admission. Validator đối chiếu toàn bộ old/new ACL/G/fence với audit và
receipt cuối transaction, thay vì chỉ đối chiếu hai digest tự khai.

Tenant guard độc quyền serialize mọi key trong tenant (mạnh hơn scoped-key lock);
không có persistent early reservation. Executor yêu cầu READ COMMITTED và chưa có xid
trước khi bắt đầu; một command/transaction. Managed slice là hai operation synthetic,
mọi hàng ACL được seed trước; không suy rộng thành schema/canonical wire contract Q04.
G/fence conflict rollback, chưa có terminal rejection receipt vì Q02 chưa được chốt.
Reader helper chỉ có mapping synthetic T1; không phải authorization adapter dùng thật.

Fault executor được tạo offline bằng bản sao có một defect, grant tạm cho actual A,
rồi drop sau từng ca. Không có fault argument/config trên entrypoint bình thường.
Các probe legacy grant chỉ tồn tại trong disposable DB và được revoke sau probe.
Concurrency dùng hai psql session và `pg_blocking_pids`, giữ lock tới khi observer
xác nhận cạnh waiter/blocker; polling không được dùng làm suy đoán lịch chạy.

`--acceptance` chạy 388 case cũ cùng `acceptance.py`; `--acceptance-only` seed một
normal assignment rồi chỉ chạy phần bổ sung trên database mới, không claim chạy lại
388 case. Source snapshot/hash và schema/grant không thay thế exact committed SHA.
Supplement có autonomous receipt conflict, swallowed conflict, forged/direct/savepoint
probes, actual backend SIGTERM trước mutation/sau mutation/trước COMMIT/COMMIT-in-flight,
lock/statement timeout, deadlock, exact role allow-list, failed publication và revoke-first.
Lịch retry/delayed dùng actual sessions và lock graph, không sleep để suy đoán thứ tự.

`contract_probes.sql` là Q02 exploratory candidate riêng, không sửa main receipt
`APPLIED` contract. Closed admission/reconciliation, closed-backup dump/restore và
tombstone probes cũng không phải approved Q05 procedure. `consumer_fixture.json`
chuẩn bị X-16/X-26; chưa có consumer execution. Xem disposition và run lỗi được giữ
nguyên tại [acceptance report](../../docs/verification/r28/r28-q03-m5-enforcement-acceptance.md).

Các gap còn bắt buộc: actual COMMIT-ACK drop (BLOCKED dưới network none/Unix socket,
chưa có verified proxy; không đổi isolation), SIGKILL/postmaster crash, Java transport/
latency mapping, approved retention/retirement/restore-reopen/rejection contract,
X-16/X-26 với Ánh, privileged operational procedure và W-17 deployed inventory.
Chủ sở hữu/superuser có thể sửa function/trigger/journal và bypass toàn bộ prototype;
không có claim bảo vệ họ bằng grants. No live maintenance procedure is verified here.

Tham chiếu semantics để review, không thay kết quả thực thi:
[deferred constraint triggers](https://www.postgresql.org/docs/17/sql-createtrigger.html),
[trigger visibility](https://www.postgresql.org/docs/17/trigger-datachanges.html),
[SECURITY DEFINER](https://www.postgresql.org/docs/17/sql-createfunction.html).
