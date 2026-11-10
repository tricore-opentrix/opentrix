<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors

SPDX-License-Identifier: Apache-2.0
-->

# Mẫu báo cáo kiểm kê Giai đoạn 2 / Phase 2 Audit Report Template

> **VI:** Sao chép file này thành `block-a-architecture.md`, `block-b-backend-infra.md` hoặc `block-c-application.md` trong cùng thư mục. Không sửa file template trong PR báo cáo. Quy ước đầy đủ: #182 §7.
> **EN:** Copy this file to `block-a-architecture.md`, `block-b-backend-infra.md` or `block-c-application.md` in the same folder. Do not edit the template in report PRs. Full conventions: #182 §7.

## 1. Thông tin báo cáo / Report metadata

| Trường / Field | Giá trị / Value |
|---|---|
| Khối / Block | A / B / C |
| Issue | #183 / #184 / #185 |
| Owner | @ |
| Reviewer chính / Primary reviewer | @ |
| Baseline SHA | `832c75fc3164cf170eed3bb8f1e380d24dd65aba` |
| Ngày kiểm kê / Audit date (UTC) | YYYY-MM-DD |
| Phạm vi đã kiểm / Paths covered | |
| Chưa kiểm và lý do / Not covered and why | |

## 2. Tóm tắt / Summary

**VI:** 3–5 câu: hiện trạng chung của khối, các khoảng trống lớn nhất, rủi ro cần quyết định sớm.
**EN:** 3–5 sentences: overall state of the block, the largest gaps, risks that need an early decision.

| Trạng thái hiện thực / Implementation | Số finding / Count |
|---|---|
| `IMPLEMENTED` | |
| `PARTIAL` | |
| `DESIGNED_ONLY` | |
| `MISSING` | |
| `UNKNOWN` | |

## 3. Danh sách finding / Findings

| ID | Component/path | Branch + SHA | Quan sát / Observed | Bằng chứng / Evidence | Trạng thái / Status | Khoảng trống-rủi ro / Gap-risk | Priority | Owner | Reviewer | Bước tiếp / Next action |
|---|---|---|---|---|---|---|---|---|---|---|
| X-000 *(ví dụ, xóa khi dùng / example, delete)* | `backend/...` | `main@832c75f` | Mô tả ngắn hành vi quan sát được / Short description of observed behavior | Link file, PR, CI run / File, PR, CI run link | `PARTIAL` · `UNTESTED` | Thiếu gì, ảnh hưởng gì / What is missing, what it affects | P1 | @ | @ | Đề xuất Issue / Proposed Issue |

### Cách điền / How to fill in

| Cột / Column | Quy ước / Convention |
|---|---|
| ID | `<Khối>-<số 3 chữ số>`, ví dụ `A-001`, `B-014` / `<Block>-<3 digits>`, e.g. `A-001`, `B-014` |
| Branch + SHA | Nhánh và SHA rút gọn nơi quan sát / Branch and short SHA where observed |
| Evidence | Link tới file (kèm dòng), PR hoặc lượt chạy CI; không ghi "đã kiểm tra" suông / Link to file (with lines), PR or CI run; never a bare "checked" |
| Status | Hiện thực: `IMPLEMENTED` · `PARTIAL` · `DESIGNED_ONLY` · `MISSING` · `UNKNOWN`; kiểm chứng: `TESTED` · `INTEGRATED` · `UNTESTED`; cờ `BLOCKED` kèm lý do / Implementation, verification and optional `BLOCKED` flag with reason |
| Priority | **P0**: chặn nộp bài, thiếu yêu cầu bắt buộc của đề hoặc mất điểm PoF / blocks submission, a mandatory requirement or PoF points. **P1**: cần cho demo và chấm chung kết / needed for the demo and finals. **P2**: cải thiện, có thể hoãn / improvement, can wait |

## 4. UNKNOWN và BLOCKED cần xử lý / Open UNKNOWN and BLOCKED items

| ID | Câu hỏi hoặc lý do chặn / Question or blocker | Cần ai trả lời / Who can answer |
|---|---|---|
| | | |

## 5. Đề xuất backlog / Proposed backlog

| Finding ID | Tiêu đề Issue đề xuất / Proposed Issue title | Priority | Owner | Phụ thuộc / Depends on | Tiêu chí hoàn thành / Acceptance criteria |
|---|---|---|---|---|---|
| | | | | | |

## 6. Ghi chú review / Review notes

| Mức / Level | Finding ID | Nhận xét / Comment | Trạng thái / Status |
|---|---|---|---|
| `BLOCKER` / `MAJOR` / `MINOR` / `SUGGESTION` | | | OPEN / RESOLVED |
