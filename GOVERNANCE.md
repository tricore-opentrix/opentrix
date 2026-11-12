<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors

SPDX-License-Identifier: Apache-2.0
-->

# OPENTRIX — Governance

[Docs](docs/README.md) · [Contributing](CONTRIBUTING.md) · [Security](SECURITY.md) · [Code owners](.github/CODEOWNERS)

> **Ngôn ngữ / Language:** [Tiếng Việt](#vi) · [English](#en)
>
> **Owner / Phụ trách:** @phanyen06ym-ien · **Issue:** [#195](https://github.com/tricore-opentrix/opentrix/issues/195), [#194](https://github.com/tricore-opentrix/opentrix/issues/194) · **Trạng thái / Status:** Bản nháp — chờ review / Draft — review required

---

<a id="vi"></a>

## OPENTRIX — Quản trị dự án

Tài liệu này nêu ai giữ quyền gì trong repository, quyết định kỹ thuật được đưa ra thế nào, thay đổi được review và merge ra sao, và cách sửa chính các quy tắc này. Quy trình làm việc hằng ngày nằm trong [CONTRIBUTING.md](CONTRIBUTING.md); tài liệu này không lặp lại.

Phần "Cấu hình đã xác minh" mô tả cài đặt GitHub được kiểm tra trên trang Settings ngày 2026-11-12. Các phần còn lại là quy tắc nhóm thống nhất; chúng có hiệu lực khi PR chứa tài liệu này được merge.

### 1. Vai trò và quyền hạn

| Vai trò     | Ai                          | Quyền trên GitHub                         | Phạm vi chính                                                     |
| ----------- | --------------------------- | ----------------------------------------- | ----------------------------------------------------------------- |
| Maintainer  | Yến (@phanyen06ym-ien)      | Owner của organization `tricore-opentrix` | Tích hợp Core, điều phối phát hành và merge, bản quyền và bảo mật |
| Maintainer  | Bảo (@lexuanbao258-collab)  | Owner của organization                    | Kiểm thử Core, cấu hình repository, CI, hạ tầng                   |
| Maintainer  | Ánh (@ngang02012007-crypto) | Owner của organization                    | Ứng dụng IT Helpdesk, Portal BFF, frontend                        |
| Contributor | Bất kỳ ai                   | Mở Issue, fork và gửi PR                  | Theo [CONTRIBUTING.md](CONTRIBUTING.md)                           |

- Cả ba maintainer có cùng quyền kỹ thuật. Phân chia phạm vi ở bảng trên là thỏa thuận nhóm, không phải giới hạn do GitHub áp đặt.
- [CODEOWNERS](.github/CODEOWNERS) chỉ định ai được yêu cầu review theo đường dẫn. Nó không bảo đảm mọi người được liệt kê đều đã duyệt.
- Maintainer chịu trách nhiệm: review trong phạm vi của mình, giữ cấu hình bảo vệ nhánh, xử lý báo cáo bảo mật theo [SECURITY.md](SECURITY.md), và không tự duyệt PR của chính mình.
- Thêm hoặc bớt maintainer cần một Issue nêu lý do và sự đồng ý của tất cả maintainer hiện tại; CODEOWNERS và bảng trên được cập nhật trong cùng PR.

### 2. Ra quyết định kỹ thuật

1. **Đề xuất:** mọi thay đổi đáng kể bắt đầu bằng một Issue nêu vấn đề, phương án và tiêu chí nghiệm thu.
2. **Khi nào cần ADR:** thay đổi kiến trúc hoặc ranh giới Core/Application; định danh, phân quyền hoặc bảo mật; mô hình dữ liệu và schema; thêm hoặc thay thư viện, dịch vụ bên thứ ba; quy trình phát hành và phân phối.
3. **Viết ADR:** file `docs/08-decisions/ADR-NNN-<chủ-đề>.md` (số tiếp theo, kiểm tra PR đang mở để tránh trùng số), gồm bối cảnh, quyết định, hệ quả, tiêu chí nghiệm thu và liên kết. Trạng thái: `PROPOSED` khi mở PR, `ACCEPTED` khi PR được merge, `SUPERSEDED by ADR-NNN` khi có quyết định thay thế. ADR đã chấp nhận không bị viết lại; quyết định mới tạo ADR mới.
4. **Chấp nhận:** ADR được chấp nhận khi PR của nó được **cả hai maintainer không phải tác giả** approve và merge. Một quyết định chưa có ADR đã merge chỉ được ghi là đề xuất (`PROPOSED`) trong tài liệu khác.
5. **Bất đồng:** thảo luận trên Issue hoặc PR. Nếu sau hai ngày làm việc chưa thống nhất, ba maintainer biểu quyết; đa số (2/3) quyết định và kết quả được ghi vào ADR hoặc Issue.
6. **Quyết định gấp** (sự cố bảo mật, CI hỏng chặn toàn nhóm): một maintainer có thể xử lý trước qua PR có review bình thường, rồi mở Issue ghi lại lý do trong vòng một ngày.

### 3. Review, approve và merge

**Cấu hình đã xác minh** (Settings, 2026-11-12):

| Cài đặt                     | Giá trị                                                                                                                                           |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Nhánh `main`                | Bắt buộc PR, 1 approval, review của code owner, bỏ approval cũ khi có commit mới, giải quyết hết hội thoại                                        |
| Required checks trên `main` | `backend`, `portal-bff`, `frontend`, `repo-hygiene` (job này phụ thuộc `r23-compliance`, nên cả 5 job phải xanh); nhánh phải cập nhật theo `main` |
| Bypass                      | "Do not allow bypassing" bật: owner cũng phải đi qua PR; không có actor được bypass; cấm force push và xóa nhánh                                  |
| Lịch sử                     | Lịch sử tuyến tính; chỉ cho phép squash merge; tự xóa nhánh sau khi merge                                                                         |
| Tag `v*`                    | Ruleset `protect-release-tags`: hạn chế tạo, sửa, xóa tag; bypass: Repository admin                                                               |
| Phát hành                   | Environment `r24-release`: reviewer Yến hoặc Ánh, cấm tự duyệt, admin không bypass, chỉ tag `v*`                                                  |

`repo-hygiene` chỉ **cảnh báo** (không chặn) khi PR thiếu `Closes #N` hoặc vượt 400 dòng.

**Quy tắc review:**

- Tác giả không tự duyệt. Approval phải nằm trên đúng HEAD cuối; commit mới làm mất approval cũ.
- Reviewer ghi trong PR đã kiểm tra những gì (SHA, CI, lệnh đã chạy, phần chưa kiểm). "Request changes" phải nêu rõ điều kiện để chuyển sang approve.
- Đường dẫn Helpdesk cần cả Bảo và Ánh review (CODEOWNERS chỉ đòi một người; yêu cầu thứ hai do nhóm tự giữ).
- Người merge là tác giả hoặc người điều phối, chỉ sau khi đủ approval và CI xanh. CI xanh chưa có nghĩa là xong: Issue chỉ đóng khi tiêu chí nghiệm thu đã được xác minh trên `main`.

### 4. Thay đổi quy tắc quản trị

- Mọi thay đổi với tài liệu này, [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md) hoặc [CODEOWNERS](.github/CODEOWNERS) đi qua một PR có Issue liên kết.
- PR quản trị cần **cả hai maintainer không phải tác giả** approve và được để mở ít nhất một ngày làm việc trước khi merge.
- Thay đổi cài đặt GitHub (bảo vệ nhánh, ruleset, environment, quyền thành viên) phải được ghi trong một Issue kèm trạng thái trước và sau, và cập nhật bảng "Cấu hình đã xác minh" trong cùng tuần.
- Khi tài liệu này và cài đặt thực tế khác nhau, cài đặt thực tế là căn cứ; người phát hiện mở Issue để sửa tài liệu hoặc cài đặt.

---

<a id="en"></a>

## OPENTRIX — Governance

This document states who holds which rights in the repository, how technical decisions are made, how changes are reviewed and merged, and how these rules themselves change. The day-to-day workflow lives in [CONTRIBUTING.md](CONTRIBUTING.md) and is not repeated here.

The "Verified configuration" table reflects GitHub settings checked on the Settings pages on 2026-11-12. The remaining sections are rules agreed by the team; they take effect when the PR containing this document is merged.

### 1. Roles and permissions

| Role        | Who                         | GitHub permission                            | Primary scope                                                            |
| ----------- | --------------------------- | -------------------------------------------- | ------------------------------------------------------------------------ |
| Maintainer  | Yến (@phanyen06ym-ien)      | Owner of the `tricore-opentrix` organization | Core integration, release and merge coordination, licensing and security |
| Maintainer  | Bảo (@lexuanbao258-collab)  | Organization owner                           | Core testing, repository settings, CI, infrastructure                    |
| Maintainer  | Ánh (@ngang02012007-crypto) | Organization owner                           | IT Helpdesk application, Portal BFF, frontend                            |
| Contributor | Anyone                      | Open Issues, fork and submit PRs             | As described in [CONTRIBUTING.md](CONTRIBUTING.md)                       |

- All three maintainers hold the same technical permissions. The scope split above is a team agreement, not a limit enforced by GitHub.
- [CODEOWNERS](.github/CODEOWNERS) routes review requests by path. It does not guarantee that every listed owner has approved.
- Maintainers are responsible for reviewing within their scope, keeping branch protection in place, handling security reports under [SECURITY.md](SECURITY.md), and never approving their own PRs.
- Adding or removing a maintainer requires an Issue stating the reason and the agreement of all current maintainers; CODEOWNERS and the table above are updated in the same PR.

### 2. Technical decision making

1. **Proposal:** every significant change starts with an Issue stating the problem, options and acceptance criteria.
2. **When an ADR is required:** changes to the architecture or the Core/Application boundary; identity, authorization or security; data model and schemas; adding or replacing third-party libraries or services; release and distribution process.
3. **Writing an ADR:** `docs/08-decisions/ADR-NNN-<topic>.md` (next number; check open PRs to avoid collisions) with context, decision, consequences, acceptance criteria and links. Status: `PROPOSED` when the PR opens, `ACCEPTED` when it merges, `SUPERSEDED by ADR-NNN` when replaced. Accepted ADRs are not rewritten; a new decision gets a new ADR.
4. **Acceptance:** an ADR is accepted when its PR is approved by **both non-author maintainers** and merged. A decision without a merged ADR may only be described as `PROPOSED` elsewhere in the documentation.
5. **Disagreement:** discuss on the Issue or PR. If there is no agreement after two working days, the three maintainers vote; the majority (2 of 3) decides and the outcome is recorded in the ADR or Issue.
6. **Urgent decisions** (security incident, broken CI blocking the team): one maintainer may act first through a normally reviewed PR, then open an Issue recording the reason within one day.

### 3. Review, approval and merge

**Verified configuration** (Settings, 2026-11-12):

| Setting                   | Value                                                                                                                                                   |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `main` branch             | PR required, 1 approval, code-owner review, stale approvals dismissed on new commits, conversations must be resolved                                    |
| Required checks on `main` | `backend`, `portal-bff`, `frontend`, `repo-hygiene` (which depends on `r23-compliance`, so all 5 jobs must pass); branch must be up to date with `main` |
| Bypass                    | "Do not allow bypassing" enabled: owners must also go through PRs; no bypass actors; force pushes and branch deletion blocked                           |
| History                   | Linear history; squash merge only; head branches deleted automatically after merge                                                                      |
| `v*` tags                 | Ruleset `protect-release-tags`: tag creation, update and deletion restricted; bypass: Repository admin                                                  |
| Release                   | Environment `r24-release`: reviewer Yến or Ánh, self-review prevented, no admin bypass, `v*` tags only                                                  |

`repo-hygiene` only **warns** (does not block) when a PR lacks `Closes #N` or exceeds 400 lines.

**Review rules:**

- Authors do not approve their own PRs. Approval must be on the final HEAD; new commits dismiss earlier approvals.
- Reviewers state in the PR what they checked (SHA, CI, commands run, what was not checked). "Request changes" must state what is needed to approve.
- Helpdesk paths need review from both Bảo and Ánh (CODEOWNERS requires only one; the second is a team rule).
- The author or the coordinator merges only after the required approvals and green CI. Green CI is not completion: an Issue closes only after its acceptance criteria are verified on `main`.

### 4. Changing governance

- Any change to this document, [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md) or [CODEOWNERS](.github/CODEOWNERS) goes through a PR linked to an Issue.
- Governance PRs require approval from **both non-author maintainers** and stay open for at least one working day before merge.
- Changes to GitHub settings (branch protection, rulesets, environments, member permissions) are recorded in an Issue with before and after state, and the "Verified configuration" table is updated within the same week.
- When this document and the actual settings differ, the actual settings prevail; whoever notices opens an Issue to fix the document or the settings.
