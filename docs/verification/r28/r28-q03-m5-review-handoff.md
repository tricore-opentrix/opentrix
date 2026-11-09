<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# R28 Q03 M5 — bàn giao review cho Yến, 2026-11-09

## Handoff acceptance closure — hiện hành

Đọc [acceptance report](r28-q03-m5-enforcement-acceptance.md) và manifest của run mới
trước phần run 05 bên dưới. Báo cáo cũ `r28-q03-m5-verification-report.md` được giữ
nguyên byte vì đã có checksum trong evidence lịch sử; các summary NOT RUN/388 PASS
trong đó chỉ mô tả run tương ứng. Bảng disposition mới không tự nghiệm thu Step 2.

Yến: đề nghị independent review trên **exact resulting HEAD SHA được báo sau commit**,
đối chiếu source snapshot/hash, SQLSTATE, before/after và privilege graph; đặc biệt
phân biệt actual SIGTERM/COMMIT-in-flight với ACK-drop thật vẫn BLOCKED, cùng các
probe Q02/Q05 thăm dò. Run lỗi 08 phải giữ FAIL, không chuyển thành PASS hồi tố.

Ánh: xác nhận R29 impact/cutover, receipt/status wire fields, fixture
[`consumer_fixture.json`](../../../tests/r28_m5/consumer_fixture.json) cho durable
reservation, superseded CAS và authorized manual reconciliation. Fixture chưa là
consumer contract hoặc bằng chứng integration. Giữ Q06 B conditional S, Q08 B và
ADR-015 Model T1; không áp dụng R29 delta hoặc legacy cutover tại đây.

Q02/Q04/Q05/Q07 còn `OWNER_CONFIRMATION_REQUIRED`; Q03 Option A/M5 đã chọn có điều
kiện, không lựa chọn lại. Giữ `Q06=NOT_FROZEN`, `RESEND=DISABLED`,
`G0_CONTRACT=BLOCKED`, `R27A_IMPLEMENTATION=NOT_AUTHORIZED`. Không merge.
Handoff được chuẩn bị trong repository; không giả định Yến/Ánh đã phản hồi hoặc ký duyệt.

## Handoff run 05 — lịch sử, đã được thay thế về trạng thái hiện hành

**PARTIAL_NOT_ACCEPTED. STEP_2_COMPLETION = NOT_PASSED; RESEND = DISABLED;
G0_CONTRACT = BLOCKED.** Gói này dành cho review độc lập, chưa phải nghiệm thu M5
hoặc bằng chứng production all-writer coverage.

## Source và evidence

- Nhánh review: `review/r28-q03-m5-isolated-verification-20261109`.
- HEAD lúc chạy `20261109-m5-isolated-05`: `f26f0ed10e80c108015944e46d61bad481ca07fd`.
  Harness lúc chạy có thay đổi chưa commit; không coi SHA baseline là exact executed
  source. Năm file tại [source snapshot](evidence/HARNESS/20261109-m5-isolated-05/source/)
  khớp byte với `tests/r28_m5/` trong gói review và hash trong environment/completion.
  SHA gói bàn giao là kết quả `git rev-parse HEAD` sau commit, được báo riêng để tránh
  self-reference trong chính commit.
- [Report](r28-q03-m5-verification-report.md) là hồ sơ tại thời điểm run 05, trước
  commit review. Giữ nguyên byte để bảo toàn `report_sha256` trong package-checks
  run 05; mô tả uncommitted/không commit ở đó áp dụng cho thời điểm chạy.
- [Audit bàn giao](evidence/REVIEW/20261109-m5-handoff-06/review-audit.json) và
  [offline chạy lại](evidence/REVIEW/20261109-m5-handoff-06/offline-checks.json).
  Chỉ kiểm tra evidence đã lưu và chạy offline; phiên review này không chạy lại DB.
- Run 03: BLOCKED, 0 DB. Run 04: trace `X-25/fault-insert_failure.json` bị lần
  publication tiếp theo ghi đè; checksum của file còn lại đúng nhưng không chứng
  minh trace đã mất. Giữ nguyên toàn bộ lịch sử, không dùng run 04 để đóng X-25.
- Run 05: 388/388 **prototype-only** PASS, 0 FAIL; X-25 19, T07 4, T08/X-09 359,
  X-12 2, X-13 4. X-23/X-24/X-16/X-26 chưa chạy. 10/10 offline PASS được chạy lại.
  877 payload checksum của ba run 03/04/05 khớp, không thiếu hoặc thừa payload
  ngoài manifest. Tất cả 388 case artifact run 05 khớp summary.
- Không đổi `schema.sql` hoặc tám hàm oracle; sửa harness gồm launcher/preflight,
  thứ tự chạy và tách tên publication khỏi case trace. Bản test bổ sung là regression
  checks, không giảm assertion. `portal-bff/bin/` (11 `.class`, 1 YAML) không thuộc
  commit. JSON SQL/trace/snapshot cần cho review được giữ, không có raw Docker inspect,
  `.env`, private key hoặc giá trị credential trong gói được chọn.
- Secret scan chỉ kiểm tra pattern và năm giá trị nhạy cảm hiện có trong environment
  phiên review, gồm hai service passwords: không thấy giá trị trùng. Không xác minh
  lại giá trị bootstrap password đã bị hủy; audit tại run 05 ghi đã kiểm tra trong
  bộ nhớ, password run 04 chỉ được review đường xử lý source.

## Yêu cầu Yến kiểm tra độc lập

Review exact SHA gói đã commit; kiểm tra manifest, source snapshot và tự suy ra kết
luận từ SQLSTATE, transaction traces, before/after và catalogs. Nếu checksum/provenance
không khớp, giữ BLOCKED, nêu đúng file/hash và dừng dùng evidence đó; không sửa evidence
hoặc test để hợp thức hóa kết quả.

1. **X-25:** kiểm tra atomic mutation/audit/receipt, 10 fault variants, savepoint,
   immediate constraints và legacy writer denial. Autonomous unique-conflict và
   owner-bypass reconciliation vẫn chưa chứng minh.
2. **T07:** kiểm tra reader-first lock graph, status/replay và response-discard model.
   Backend kill ở từng stage, network ACK-drop thật, lock/statement timeout và deadlock
   còn thiếu; không coi response-discard là ACK-drop hoặc chứng minh deadlock-freedom.
3. **T08/X-09:** kiểm tra actual LOGIN roles, effective grants/SET reachability,
   definer/trigger/default ACL catalogs, reader helper và migrator denial. Exact grant
   allow-list, atomic publication failure và **revoke-first fresh authorization** còn thiếu.
4. **X-23/X-24:** cần approved retention/tombstone/restore/reopen/admission procedures
   và terminal-rejection contract/fixture; 0 case, không suy từ X-25 PASS.
5. **W-17:** deployed catalogs, external credential/writer inventory và privileged
   maintenance/restore vẫn BLOCKED. W-01–W-16 chưa được đóng bằng prototype; production
   all-writer coverage chưa chứng minh. Giữ các gap X-12/X-13 và X-16/X-26 với Ánh,
   cùng owner decisions Q02/Q04/Q05/Q07 và các closure còn mở trong report.

Ghi reviewed SHA, findings, phần đã chứng minh và gap chưa chứng minh. Không tự đóng
Step 2/G0, bật resend, freeze joint contract, merge hoặc sửa production.

## Chuẩn bị push và Draft PR

PR #168 được kiểm tra qua GitHub: OPEN/Draft; head branch
`docs/r28-r27a-p0-dependency-contract-20261109`, head SHA
`cecee84453cf5eaec16548959415c243675d56c4`. Đây là **base** của Draft PR mới, không
phải nhánh base của chính #168. Local baseline kế thừa đúng SHA này.

Đã soạn [nội dung Draft PR](r28-q03-m5-draft-pr.md). Các lệnh dưới đây chưa thực thi;
trước khi dùng, kiểm tra lại head branch/SHA của #168 và SHA commit bàn giao, không
force-push nếu remote đã có thay đổi khác.

```powershell
git rev-parse HEAD
gh pr view 168 --repo tricore-opentrix/opentrix --json headRefName,headRefOid,isDraft
git push --set-upstream origin review/r28-q03-m5-isolated-verification-20261109
gh pr create --repo tricore-opentrix/opentrix --draft --base docs/r28-r27a-p0-dependency-contract-20261109 --head review/r28-q03-m5-isolated-verification-20261109 --title "test(r28): M5 isolated prototype evidence for independent review" --body-file docs/verification/r28/r28-q03-m5-draft-pr.md
```

Không gửi riêng thông điệp/review request cho Yến trong phiên này; nội dung bàn giao
đã chuẩn bị tại đây. Không push, mở PR hoặc merge trong bước chuẩn bị.
