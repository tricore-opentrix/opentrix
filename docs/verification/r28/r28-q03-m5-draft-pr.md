<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

## Summary

Gói review độc lập cho R28 Q03 M5, stacked trên head branch của #168
`docs/r28-r27a-p0-dependency-contract-20261109`.

```text
tests/r28_m5/                 prototype SQL, runner, launcher và offline checks
docs/verification/r28/        report, handoff và evidence run 01–05 + audit bàn giao
```

388/388 PASS của run `20261109-m5-isolated-05` là **prototype-only**, chưa chứng minh
production all-writer coverage. Kết quả tổng thể **PARTIAL_NOT_ACCEPTED**.

## Evidence

- **Before:** baseline `f26f0ed10e80c108015944e46d61bad481ca07fd` dừng trước DB;
  run 03 còn credential blocker. Run 04 chạy 388 case nhưng mất trace X-25
  `fault-insert_failure` do publication ghi đè; giữ lịch sử có hạn chế.
  **After:** tiến trình test mới có OS-only environment, credentials mới mỗi run,
  network none/tmpfs/local socket preflight; run 05 có đủ 388 case artifact và
  publication riêng. Không giảm oracle để PASS.
- X-25 19/19, T07 4/4, T08/X-09 359/359, X-12 2/2, X-13 4/4; DB invocation exit 0
  được kiểm tra từ evidence đã lưu. Phiên bàn giao không chạy lại DB.
- `python -B -m unittest discover -s tests/r28_m5 -p test_harness.py -v`: chạy lại
  10/10 PASS, exit 0. Audit ba run 03/04/05: 877 payload SHA-256 khớp; năm source
  snapshot khớp byte với harness; tám hàm oracle và schema không đổi so với baseline.
- Source lúc run là dirty worktree tại SHA baseline cộng hash file, không được mô
  tả thành clean committed execution. Report được giữ byte nguyên để bảo toàn hash
  trong package-checks. Xem [report](https://github.com/tricore-opentrix/opentrix/blob/review/r28-q03-m5-isolated-verification-20261109/docs/verification/r28/r28-q03-m5-verification-report.md)
  và [handoff/audit](https://github.com/tricore-opentrix/opentrix/blob/review/r28-q03-m5-isolated-verification-20261109/docs/verification/r28/r28-q03-m5-review-handoff.md).
- Đề nghị Yến review độc lập exact PR head SHA và X-25/T07/T08 từ snapshots/catalogs.
  Kill-stage, ACK-drop thật, timeout/deadlock, revoke-first, X-23/X-24 và W-17 còn
  BLOCKED/chưa chứng minh; cùng gap X-12/X-13/X-16/X-26 và owner decisions trong report.
  Không coi model response-discard là network ACK-drop.

## Merge Danger

**Door:** two-way

**Blast Radius:** verification

Phạm vi test-only và tài liệu/evidence; không đổi production Java/migration/grants
hoặc R29. Build output `portal-bff/bin/` bị loại khỏi commit. Secret scan không thấy
giá trị credential hiện có trong gói; không thể kiểm tra lại bootstrap passwords đã
bị hủy. Run 04 có provenance gap đã nêu, không dùng để nghiệm thu X-25.

Giữ Draft, không merge/activate. **STEP_2_COMPLETION = NOT_PASSED;
RESEND = DISABLED; G0_CONTRACT = BLOCKED.** Chưa có independent security sign-off.
