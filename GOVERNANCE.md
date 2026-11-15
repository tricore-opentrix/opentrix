<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# OpenTrix

> **Ngôn ngữ / Language:** [Tiếng Việt](#vi) · [English](#en)

---

<a id="vi"></a>

## OpenTrix — Quản trị dự án

Tài liệu này mô tả ai ra quyết định trong dự án, quyết định được thông qua thế nào, điều kiện review và merge, cách giải quyết bất đồng và cách sửa đổi chính sách. Quy trình đóng góp hằng ngày nằm trong [CONTRIBUTING.md](CONTRIBUTING.md); báo cáo lỗ hổng theo [SECURITY.md](SECURITY.md).

### 1. Vai trò

| Vai trò                            | Thành viên            | Trách nhiệm                                                           |
| ---------------------------------- | --------------------- | --------------------------------------------------------------------- |
| Maintainer — Core và phát hành     | @phanyen06ym-ien      | Tích hợp Core, kiến trúc, quy trình phát hành, phối hợp giữa các phần |
| Maintainer — Hạ tầng và chất lượng | @lexuanbao258-collab  | Kiểm thử Backend/Core, CI, hạ tầng, rà soát thay đổi có rủi ro        |
| Maintainer — Ứng dụng và Portal    | @ngang02012007-crypto | IT Helpdesk, Portal BFF, frontend, hợp đồng tích hợp                  |
| Contributor                        | Bất kỳ ai             | Mở Issue và pull request, tham gia thảo luận và review                |

- Maintainer không tự duyệt PR của mình và không dùng quyền quản trị để bỏ qua review.
- Contributor nhận phản hồi có lý do; việc merge dựa trên chất lượng kỹ thuật, an toàn, quyền đóng góp và khả năng bảo trì.
- Thêm, thay hoặc rút maintainer cần một Issue công khai nêu lý do, phạm vi và kế hoạch bàn giao, và được tất cả maintainer hiện tại không có xung đột lợi ích đồng ý.
- Mọi tương tác cần tôn trọng và tập trung vào nội dung. Không chấp nhận quấy rối, đe dọa hay tiết lộ thông tin cá nhân.

### 2. Ra quyết định

- **Thay đổi thông thường:** thảo luận trong Issue và pull request theo [CONTRIBUTING.md](CONTRIBUTING.md); maintainer phụ trách phần liên quan đưa ra quyết định có lý do.
- **Quyết định kiến trúc (ADR):** bắt buộc với thay đổi lâu dài về kiến trúc Core/ứng dụng, định danh và phân quyền, sở hữu dữ liệu, API công khai, nền tảng chính, giấy phép hoặc quy trình phát hành. ADR nằm trong [`docs/08-decisions/`](docs/08-decisions/README.md) với trạng thái `PROPOSED` → `ACCEPTED` → (`SUPERSEDED`). Một ADR được chấp nhận khi PR của nó được hai maintainer không phải tác giả phê duyệt và merge. ADR đã chấp nhận không bị viết lại; thay đổi được ghi bằng ADR mới.
- **Bất đồng:** ưu tiên thảo luận dựa trên bằng chứng và phương án thay thế. Nếu sau hai ngày làm việc chưa thống nhất, maintainer biểu quyết theo đa số 2/3. Biểu quyết không thay thế các điều kiện review, bảo mật, CI hay phát hành.
- **Xung đột lợi ích:** người liên quan phải nêu rõ và không tự xác nhận review độc lập cho thay đổi của mình.

### 3. Review và merge

| Loại thay đổi                                        | Điều kiện tối thiểu                                                                                                     |
| ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Pull request thông thường                            | Một phê duyệt độc lập, CI liên quan đạt, không còn góp ý chặn chưa xử lý                                                |
| Đường dẫn Core liên quan Helpdesk hoặc API của BFF   | Review của cả hai maintainer phụ trách hai phía; nếu một người là tác giả, thống nhất reviewer thay thế trước khi merge |
| Quyết định kiến trúc (ADR)                           | Hai phê duyệt của maintainer không phải tác giả                                                                         |
| Chính sách quản trị, CODEOWNERS, điều kiện phê duyệt | Hai phê duyệt của maintainer không phải tác giả; PR mở ít nhất một ngày làm việc                                        |
| Bảo mật và phát hành                                 | Thêm các điều kiện trong [SECURITY.md](SECURITY.md) và [docs/RELEASE.md](docs/RELEASE.md)                               |

- [CODEOWNERS](.github/CODEOWNERS) tự động yêu cầu review theo đường dẫn; phê duyệt được tính trên commit cuối cùng của PR.
- Chỉ squash merge sau khi mọi điều kiện đạt. Issue chỉ được đóng khi tiêu chí nghiệm thu đã được xác minh trên `main`.
- Khi chính sách này và cấu hình GitHub khác nhau, áp dụng điều kiện chặt hơn và mở Issue để đồng bộ.

### 4. Phát hành và nguồn gốc đóng góp

- Mỗi bản phát hành có tag, phạm vi thay đổi trong [CHANGELOG.md](CHANGELOG.md), checksum của gói phát hành và thông tin bên thứ ba; quy trình chi tiết trong [docs/RELEASE.md](docs/RELEASE.md).
- Chỉ nhận mã, dữ liệu và tài sản (kể cả nội dung có hỗ trợ của AI) mà người đóng góp có quyền cung cấp theo giấy phép tương ứng, kèm khai báo nguồn gốc và nghĩa vụ ghi công khi có.

### 5. Sửa đổi chính sách

- Thay đổi `GOVERNANCE.md`, `CONTRIBUTING.md`, `SECURITY.md` hoặc `.github/CODEOWNERS` cần Issue nêu lý do và pull request mô tả thay đổi; chính sách mới có hiệu lực sau khi merge.
- Không được hạ điều kiện phê duyệt trong một PR rồi dùng điều kiện mới đó để thông qua chính PR ấy.
- Thay đổi cấu hình GitHub (branch protection, ruleset, environment, thành viên) được ghi lại trong Issue hoặc pull request, không kèm thông tin bí mật.

---

<a id="en"></a>

## OpenTrix — Project governance

This document describes who makes decisions in the project, how decisions are approved, review and merge requirements, how disagreements are resolved and how this policy is amended. The day-to-day contribution workflow is in [CONTRIBUTING.md](CONTRIBUTING.md); vulnerability reporting follows [SECURITY.md](SECURITY.md).

### 1. Roles

| Role                                    | Members               | Responsibilities                                                              |
| --------------------------------------- | --------------------- | ----------------------------------------------------------------------------- |
| Maintainer — Core and release           | @phanyen06ym-ien      | Core integration, architecture, release process, cross-component coordination |
| Maintainer — Infrastructure and quality | @lexuanbao258-collab  | Backend/Core testing, CI, infrastructure, review of high-risk changes         |
| Maintainer — Application and Portal     | @ngang02012007-crypto | IT Helpdesk, Portal BFF, frontend, integration contracts                      |
| Contributor                             | Anyone                | Open Issues and pull requests, take part in discussion and review             |

- Maintainers do not approve their own pull requests and do not use admin rights to bypass review.
- Contributors receive reasoned feedback; merging depends on technical quality, safety, contribution rights and maintainability.
- Adding, replacing or removing a maintainer requires a public Issue with the rationale, scope and handover plan, and the agreement of all current maintainers without a conflict of interest.
- All interactions should be respectful and focused on the work. Harassment, threats and disclosure of personal information are not accepted.

### 2. Decision-making

- **Ordinary changes:** discussed in Issues and pull requests following [CONTRIBUTING.md](CONTRIBUTING.md); the maintainer responsible for the area makes a reasoned decision.
- **Architecture decisions (ADR):** required for lasting changes to the Core/application architecture, identity and authorization, data ownership, public APIs, foundational platforms, licensing or the release process. ADRs live in [`docs/08-decisions/`](docs/08-decisions/README.md) with status `PROPOSED` → `ACCEPTED` → (`SUPERSEDED`). An ADR is accepted when its pull request is approved by two non-author maintainers and merged. Accepted ADRs are not rewritten; changes are recorded in a new ADR.
- **Disagreements:** prefer evidence-based discussion and alternatives. If there is no agreement after two business days, maintainers decide by a 2-of-3 vote. A vote does not replace review, security, CI or release requirements.
- **Conflicts of interest:** must be disclosed; nobody provides independent review of their own change.

### 3. Review and merge

| Change                                   | Minimum requirements                                                                                                         |
| ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Ordinary pull request                    | One independent approval, relevant CI passing, no unresolved blocking comments                                               |
| Helpdesk-related Core paths or BFF API   | Review by both maintainers responsible for either side; if one is the author, agree on a replacement reviewer before merging |
| Architecture decision (ADR)              | Two approvals from non-author maintainers                                                                                    |
| Governance, CODEOWNERS or approval rules | Two approvals from non-author maintainers; pull request open for at least one business day                                   |
| Security and release                     | Additional requirements in [SECURITY.md](SECURITY.md) and [docs/RELEASE.md](docs/RELEASE.md)                                 |

- [CODEOWNERS](.github/CODEOWNERS) requests reviews by path; approvals count against the final commit of the pull request.
- Squash-merge only after all requirements are met. Close an Issue only after its acceptance criteria are verified on `main`.
- Where this policy and GitHub settings differ, the stricter rule applies and an Issue is opened to align them.

### 4. Releases and contribution provenance

- Each release has a tag, its changes in [CHANGELOG.md](CHANGELOG.md), checksums for the release archives and third-party information; the detailed process is in [docs/RELEASE.md](docs/RELEASE.md).
- Code, data and assets (including AI-assisted content) are accepted only when the contributor has the right to submit them under the applicable licenses, with provenance and attribution obligations declared where relevant.

### 5. Amending this policy

- Changes to `GOVERNANCE.md`, `CONTRIBUTING.md`, `SECURITY.md` or `.github/CODEOWNERS` need an Issue stating the rationale and a pull request describing the change; the new policy takes effect once merged.
- A pull request must not lower the approval requirements and then use the lowered requirements to approve itself.
- Changes to GitHub settings (branch protection, rulesets, environments, membership) are recorded in an Issue or pull request without any secrets.
