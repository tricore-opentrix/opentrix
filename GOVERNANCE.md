<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# OPENTRIX — Governance

[Documentation](docs/README.md) · [Contributing](CONTRIBUTING.md) · [Security](SECURITY.md) · [Code owners](.github/CODEOWNERS)

> **Language / Ngôn ngữ:** [Tiếng Việt](#vi) · [English](#en)  
> **Owner:** @phanyen06ym-ien · **Tracking:** [#195](https://github.com/tricore-opentrix/opentrix/issues/195), [#194](https://github.com/tricore-opentrix/opentrix/issues/194)  
> **Status:** PROPOSED — pending independent review and merge. This draft does not itself amend repository settings or grant release rights.

---

<a id="vi"></a>

## OPENTRIX — Chính sách quản trị dự án

### 1. Mục đích, phạm vi và hiệu lực

Tài liệu này xác định **ai có quyền ra quyết định**, **cách quyết định được thông qua**, **điều kiện review/merge**, **cách giải quyết bất đồng** và **quy trình thay đổi chính sách** đối với repository OpenTrix (DX-OS Open-Core). Chính sách áp dụng cho mọi phiên bản, trừ khi được thay thế bằng một PR quản trị hợp lệ. Đây không phải cam kết về mức độ hoàn thiện hay hỗ trợ production của phần mềm.

- [CONTRIBUTING.md](CONTRIBUTING.md) quy định cách contributor mở Issue, viết mã, chạy kiểm thử và gửi PR. [SECURITY.md](SECURITY.md) quy định báo cáo lỗ hổng qua kênh riêng. [CODEOWNERS](.github/CODEOWNERS) hỗ trợ định tuyến reviewer. Các tài liệu này bổ sung cho Governance, không thay thế nó.
- Quy tắc trong tài liệu này **chỉ có hiệu lực sau khi PR chấp nhận chúng được merge** với sự phê duyệt theo mục 5. Chúng không tạo ra quyền GitHub, không tự cấu hình branch protection và không tự cho phép phát hành.
- **Chính sách của nhóm** và **cấu hình GitHub quan sát được** là hai loại thông tin khác nhau. Cấu hình thực tế quyết định điều gì GitHub có thể cưỡng chế; nếu phát hiện chênh lệch, phải mở Issue để khôi phục kiểm soát hoặc cập nhật chính sách bằng PR. Không dùng chênh lệch đó làm lý do bypass.

### 2. Vai trò, trách nhiệm và tham gia cộng đồng

| Vai trò | Người / nhóm hiện tại | Thẩm quyền và trách nhiệm |
| --- | --- | --- |
| Maintainer — Core & phối hợp | Yến (`@phanyen06ym-ien`) | Điều phối Core, kiến trúc, kiểm tra quyền nguồn gốc, quy trình phát hành và phụ thuộc liên nhóm |
| Maintainer — hạ tầng & chất lượng | Bảo (`@lexuanbao258-collab`) | Backend/Core testing, CI, hạ tầng, kiểm chứng và đánh giá thay đổi có rủi ro |
| Maintainer — Application & Portal | Ánh (`@ngang02012007-crypto`) | Helpdesk, Portal BFF, frontend, hợp đồng tích hợp và trải nghiệm ứng dụng |
| Contributor | Bất kỳ người tham gia hợp lệ | Mở Issue/PR, cung cấp bằng chứng, thảo luận thiết kế và phản hồi review; không tự có quyền merge hoặc phát hành |
| Reviewer được mời | Contributor/maintainer am hiểu và độc lập với thay đổi | Kiểm tra phạm vi được giao; quyền phê duyệt có hiệu lực trên GitHub tùy quyền repository và quy tắc bảo vệ nhánh |

- Bảng trên mô tả **phân công nhóm**, không khẳng định một quyền GitHub cụ thể hay cơ chế kiểm soát tự động. Quyền kỹ thuật và danh sách thành viên phải được đối chiếu tại repository/organization Settings khi cần.
- Maintainer phải minh bạch về phần mình viết, review, nguồn gốc mã, xung đột lợi ích và những kiểm tra chưa thực hiện. Không tự approve PR; không dùng tài khoản khác hay quyền admin để tránh review.
- Contributor bên ngoài có quyền đề xuất và được phản hồi có lý do, nhưng việc merge phụ thuộc tiêu chí kỹ thuật, an toàn, nguồn gốc/quyền đóng góp và năng lực bảo trì — không phụ thuộc danh tính hay quan hệ với nhóm.
- Đề xuất thêm, thay hoặc bãi nhiệm maintainer phải có Issue công khai (trừ chi tiết bảo mật/cá nhân cần xử lý riêng), lý do, phạm vi quyền và kế hoạch bàn giao. Cần **sự đồng ý của toàn bộ maintainer đương nhiệm không có xung đột lợi ích**; nếu điều kiện này không thể đáp ứng, giữ `BLOCKED` và tìm người xác minh độc lập, không tự ý cấp quyền. Thay đổi cấu hình và tài liệu liên quan phải được ghi nhận.
- Tương tác phải tôn trọng, tập trung vào nội dung và bằng chứng. Không dung thứ quấy rối, đe dọa, tiết lộ dữ liệu cá nhân hoặc lạm dụng quyền truy cập. Báo cáo lỗ hổng đi theo `SECURITY.md`, không đưa chi tiết nhạy cảm vào Issue công khai.

### 3. Quyền đề xuất và ra quyết định kỹ thuật

- **Thay đổi thông thường:** mở Issue khi cần theo `CONTRIBUTING.md`, nêu mục tiêu, giải pháp, phạm vi, rủi ro, tiêu chí nghiệm thu. Contributor được tham gia thảo luận; maintainer phụ trách đưa ra hướng xử lý có lý do.
- **Bắt buộc ADR** đối với thay đổi dài hạn về kiến trúc Core/Application, security/identity/authorization, ownership dữ liệu/schema, API công khai có ảnh hưởng lớn, thay thế provider nền tảng, mô hình cấp phép hoặc quy trình phát hành. Đặt ADR trong `docs/08-decisions/`, dùng số không trùng và ghi bối cảnh, lựa chọn, quyết định, hệ quả, rủi ro và đường dẫn Issue/PR.
- **Trạng thái ADR:** `PROPOSED` trong lúc thảo luận; `ACCEPTED` chỉ sau khi PR quyết định được merge với **hai approval độc lập của hai maintainer không phải tác giả**; `SUPERSEDED` phải trỏ tới ADR thay thế đã được chấp nhận. Giữ lịch sử ADR đã chấp nhận; không viết lại để xóa dấu vết quyết định cũ.
- **Bất đồng:** ưu tiên thảo luận có bằng chứng và phương án thay thế. Nếu sau hai ngày làm việc không thống nhất, ba maintainer có thể ghi biểu quyết 2/3 cho **ưu tiên hoặc phương án tiếp tục nghiên cứu thông thường**. Biểu quyết **không thay thế** review PR, hai approval của ADR, quyền nguồn gốc, tiêu chí bảo mật, CI hay điều kiện release. Nếu không đạt cổng bắt buộc, quyết định vẫn `BLOCKED`.
- **Xung đột lợi ích hoặc thiếu reviewer:** người liên quan phải khai báo, không tự xác nhận độc lập. Có thể mời reviewer bên ngoài đủ năng lực để đưa ý kiến chuyên môn; nếu GitHub hoặc chính sách yêu cầu approval của maintainer cụ thể, chỉ thay reviewer theo một ngoại lệ được ghi nhận và thông qua trước bởi các maintainer không có xung đột. Không có ngoại lệ hợp lệ thì dừng merge.
- **Khẩn cấp:** sự cố bảo mật/CI có thể được xử lý qua nhánh và PR ưu tiên với kiểm tra độc lập phù hợp, không mặc nhiên cho bypass. Mở hoặc cập nhật Issue/advisory ghi nguyên nhân và quyết định sau khi không còn nguy cơ lộ thông tin; không công khai chi tiết lỗ hổng trước thời điểm cho phép.

### 4. Review, merge và trách nhiệm chất lượng

| Loại thay đổi | Điều kiện tối thiểu theo chính sách |
| --- | --- |
| PR thông thường | Một approval **độc lập**, CI/checks liên quan thành công, không có finding blocking chưa xử lý, tác giả xác nhận phạm vi và evidence |
| Helpdesk Core hoặc API BFF có rủi ro liên ranh giới | Bảo và Ánh cùng kiểm tra khi độc lập; nếu một người là tác giả, phải ghi conflict và có reviewer độc lập thay thế theo thỏa thuận trước merge |
| Thay đổi kiến trúc qua ADR | Hai approval của các maintainer không phải tác giả, đúng HEAD cuối cùng; cần record quyết định |
| Governance / thay đổi cơ chế phê duyệt | Hai approval của maintainer không phải tác giả, PR mở ít nhất một ngày làm việc, Issue nêu lý do và tác động |
| Bảo mật, nguồn gốc/quyền, phát hành | Đáp ứng các cổng chuyên biệt trong `SECURITY.md`, `CONTRIBUTING.md`, Issue liên quan và release workflow; approval thông thường không thay thế các cổng này |

- `CODEOWNERS` định tuyến yêu cầu review; tên xuất hiện trong file không đồng nghĩa reviewer đã approve. Đối chiếu review tại **HEAD cuối cùng**, trạng thái requested changes, resolved threads, tính độc lập và branch rules thực tế.
- PR phải mô tả ảnh hưởng đối với hợp đồng/API, migration, backward compatibility, test, dữ liệu và bảo mật; nêu SHA, lệnh đã chạy, PASS/FAIL/SKIPPED và phần `UNVERIFIED`. CI xanh không chứng minh LIVE E2E hoặc quyền phân phối.
- Không push trực tiếp vào nhánh được bảo vệ. Chỉ squash merge sau khi toàn bộ điều kiện GitHub và chính sách nhóm được đáp ứng; không tự động đóng Issue chỉ vì PR đã merge nếu chưa xác minh acceptance criteria trên `main`.
- Nếu quy tắc nhóm nghiêm ngặt hơn GitHub Settings, phải tuân thủ quy tắc nghiêm ngặt hơn. Nếu Settings nghiêm ngặt hơn chính sách, phải tuân thủ Settings. Không được dùng quyền owner/admin để lách điều kiện chưa đạt.

### 5. Quyền phát hành và nguồn gốc đóng góp

- Việc có mã nguồn, file `LICENSE`, SPDX/REUSE PASS, SBOM, CI PASS hoặc artifact tái lập được **không tự xác nhận quyền tác giả, quyền phân phối hay release acceptance**.
- Mỗi release phải có phạm vi, source/tag SHA, artifact/checksum, kiểm thử, thông tin bên thứ ba, trạng thái quyền nguồn gốc, người review, ghi nhận rủi ro và quyết định xuất bản; áp dụng cổng version-specific trong [`docs/RELEASE.md`](docs/RELEASE.md) khi file đó được merge.
- Các vấn đề quyền còn mở theo [Issue #138](https://github.com/tricore-opentrix/opentrix/issues/138); release dự thi theo [Issue #190](https://github.com/tricore-opentrix/opentrix/issues/190). Không coi candidate v0.2.0 hoặc kế hoạch v0.3/v0.4.1 là bản phát hành đã được chấp nhận.
- Chỉ nhận code, dữ liệu, assets và AI-assisted contributions khi người đóng góp có quyền cung cấp theo điều khoản giấy phép tương ứng; nguồn gốc và nghĩa vụ ghi công phải được khai báo. Không sao chép nội dung của OpenVie hay bên thứ ba chỉ vì cùng mô hình quản trị.

### 6. Thay đổi chính sách và lưu bằng chứng cấu hình

- Thay đổi `GOVERNANCE.md`, `CONTRIBUTING.md`, `SECURITY.md` hoặc `.github/CODEOWNERS` phải có Issue, PR, so sánh trước/sau, lý do và ảnh hưởng tới contributor. Chính sách mới chỉ có hiệu lực sau merge.
- Governance PR phải có hai approval độc lập từ các maintainer không phải tác giả. Không sửa điều kiện review ngay trong cùng PR rồi dùng điều kiện mới để tự thông qua PR đó.
- Mọi thay đổi về GitHub rulesets, branch protection, environment, CODEOWNERS thực thi hoặc membership phải được ghi trong Issue/PR với thời điểm, actor được phép, cấu hình trước/sau và bằng chứng đã xác minh. Tránh đưa bí mật hoặc dữ liệu quản trị nhạy cảm vào bản công khai.
- **Snapshot cấu hình GitHub (quan sát, không phải chính sách bất biến):** bản nháp PR #204 ngày 2026-11-12 ghi `main` yêu cầu PR/review, checks `backend`, `portal-bff`, `frontend`, `repo-hygiene` (kèm `r23-compliance`), squash, ruleset `protect-release-tags` và environment `r24-release`. Đây là **bản khai từ draft**, cần reviewer xác minh bằng GitHub Settings hoặc evidence trước khi ghi `VERIFIED`; các giá trị có thể thay đổi mà không làm mất hiệu lực nguyên tắc quản trị.
- Nếu cấu hình khác chính sách, lập Issue để khôi phục/đối chiếu; không âm thầm coi việc thiếu enforcement là miễn trừ. Nhóm rà soát chính sách khi thay đổi cơ cấu maintainer, mô hình phân phối, kiến trúc governance hoặc quy định pháp lý, **không mặc định sửa sau mỗi bản phát hành phần mềm**.

---

<a id="en"></a>

## OPENTRIX — Project governance policy

### 1. Purpose, scope and effect

This policy defines **decision authority**, **decision approval**, **review and merge requirements**, **conflict resolution**, and **governance amendments** for the OpenTrix (DX-OS Open-Core) repository. It is intended to apply across software versions until properly superseded. It is not a claim that the software is production-ready.

- [CONTRIBUTING.md](CONTRIBUTING.md) covers the day-to-day contribution workflow. [SECURITY.md](SECURITY.md) covers private vulnerability reporting. [CODEOWNERS](.github/CODEOWNERS) routes review requests. They complement, rather than replace, this policy.
- This policy **takes effect only when its adopting PR is merged** under Section 6. It does not grant GitHub privileges, configure branch protection or authorize releases.
- **Team policy** and **observed GitHub settings** are different. Actual settings control what GitHub enforces. Any gap must be tracked through an Issue and corrected through the proper process; a configuration gap is not permission to bypass policy.

### 2. Roles, responsibilities and community participation

| Role | Current participants | Authority and responsibilities |
| --- | --- | --- |
| Maintainer — Core & coordination | Yến (`@phanyen06ym-ien`) | Core integration, architecture, source-rights review, release process and cross-team dependencies |
| Maintainer — infrastructure & quality | Bảo (`@lexuanbao258-collab`) | Backend/Core testing, CI, infrastructure, evidence and high-risk changes |
| Maintainer — Application & Portal | Ánh (`@ngang02012007-crypto`) | Helpdesk, Portal BFF, frontend, integration contracts and application experience |
| Contributor | Any eligible participant | Submit Issues/PRs, evidence and review feedback; no automatic merge or release authority |
| Invited reviewer | Competent person independent of the change | Review the assigned scope; the effect of any approval depends on GitHub access and branch rules |

- This table documents **team responsibilities**, not independently verified GitHub permission levels or automatically enforced access. Verify current organization/repository settings when permissions matter.
- Maintainers must disclose authorship, review scope, provenance, conflicts of interest and unperformed checks. They must not self-approve or circumvent review with an alternate account or admin privilege.
- External contributors may propose changes and receive reasoned feedback. Merging depends on technical merit, safety, contribution rights and maintainability, not personal relationships.
- Adding, replacing or removing a maintainer requires a recorded Issue (with sensitive personal/security details handled privately), rationale, scope and handover. Require **agreement from all non-conflicted incumbent maintainers**; where this is impossible, retain `BLOCKED` and seek independent assessment instead of granting access unilaterally. Record relevant settings and document updates.
- Interactions must be respectful and evidence-focused. Harassment, threats, disclosure of private data and access abuse are unacceptable. Security details belong in the private channel described by `SECURITY.md`.

### 3. Proposals and technical decisions

- **Ordinary changes:** open an Issue as specified by `CONTRIBUTING.md`, stating the problem, proposal, scope, risks and acceptance criteria. Contributors may participate; the responsible maintainer records a reasoned disposition.
- **ADR required** for durable changes to Core/Application architecture, identity/security/authorization, data ownership or schemas, materially significant public API contracts, foundational providers, licensing model or release process. Store ADRs under `docs/08-decisions/` with a unique identifier, context, options, decision, consequences, risks and Issue/PR references.
- **ADR status:** `PROPOSED` while discussed; `ACCEPTED` only after the decision PR is merged with **independent approval by both non-author maintainers**; `SUPERSEDED` must reference an accepted replacement ADR. Preserve the history of accepted ADRs rather than silently rewriting earlier decisions.
- **Disagreement:** prefer evidence-based discussion and alternatives. After two business days without consensus, a recorded 2-of-3 maintainer vote may select **ordinary priorities or an option for continued investigation**. A vote **does not replace** PR review, two ADR approvals, source rights, security controls, CI or release gates. If a mandatory gate is unsatisfied, the decision stays `BLOCKED`.
- **Conflicts or missing reviewers:** disclose conflicts; do not claim independent review of one's own work. An external expert may be invited for technical assessment. If GitHub or policy requires specific maintainer approval, substitutions require an exception agreed and recorded in advance by non-conflicted maintainers. Without a valid exception, do not merge.
- **Urgent situations:** prioritize security or CI fixes through appropriately reviewed branches/PRs, not automatic bypasses. Record the reason and outcome in an Issue or advisory once that can be done without exposing sensitive security details.

### 4. Review, merge and quality accountability

| Change category | Minimum team-policy requirements |
| --- | --- |
| Ordinary PR | One **independent** approval, passing applicable CI/checks, no unresolved blocking finding, and documented scope/evidence |
| Cross-boundary Helpdesk Core or BFF API | Both Bảo and Ánh review when independent; if one authored the change, disclose the conflict and agree on an independent replacement reviewer before merging |
| Architecture change requiring an ADR | Two approvals from non-author maintainers at the final HEAD, plus a recorded decision |
| Governance or approval-mechanism change | Two approvals from non-author maintainers, PR open for at least one business day and Issue explaining rationale/impact |
| Security, rights or release change | Applicable gates in `SECURITY.md`, `CONTRIBUTING.md`, linked Issues and the release workflow; ordinary approval never replaces those gates |

- `CODEOWNERS` requests reviews; being listed does not mean a reviewer approved. Verify review at the **final HEAD**, requested-changes state, resolved threads, independence and actual branch rules.
- PRs must describe API/contract, migration, compatibility, testing, data and security impacts where applicable; record SHA, commands executed, PASS/FAIL/SKIPPED and anything `UNVERIFIED`. Passing CI does not establish LIVE E2E or redistribution rights.
- Do not push directly to protected branches. Squash-merge only after all GitHub and team-policy gates pass. A merged PR does not automatically justify closing its Issue until acceptance criteria are verified on `main`.
- Apply whichever is stricter: team policy or GitHub enforcement. Owner/admin permissions are not grounds for bypassing unmet requirements.

### 5. Release authority and contribution provenance

- Source availability, a `LICENSE` file, SPDX/REUSE results, SBOM, green CI or reproducible artifacts **do not alone establish authorship, distribution rights or release acceptance**.
- Every release needs documented scope, source/tag SHA, artifacts/checksums, testing, third-party obligations, rights status, reviewers, accepted risks and publication decision. Apply the version-specific gates in [`docs/RELEASE.md`](docs/RELEASE.md) once that document is merged.
- Open source-rights issues remain tracked in [#138](https://github.com/tricore-opentrix/opentrix/issues/138); competition release acceptance in [#190](https://github.com/tricore-opentrix/opentrix/issues/190). Do not describe a v0.2.0 candidate or future v0.3/v0.4.1 work as an accepted public release.
- Accept code, data, assets and AI-assisted contributions only where the contributor is authorized to submit them under applicable licenses. Disclose provenance and attribution obligations. Architectural inspiration from OpenVie or another project does not authorize copying its code or assets.

### 6. Amending policy and retaining configuration evidence

- Changes to `GOVERNANCE.md`, `CONTRIBUTING.md`, `SECURITY.md` or `.github/CODEOWNERS` require a linked Issue, PR, before/after description, rationale and contributor impact. A new policy becomes effective only after merge.
- Governance PRs require two independent non-author maintainer approvals. Do not amend the required approval rule and then use the newly proposed lower bar to approve that same PR.
- Changes to GitHub rulesets, branch protection, environments, enforced CODEOWNERS or membership need an Issue/PR record with date, authorized actor, before/after settings and verification evidence. Do not expose secrets or sensitive administrator information publicly.
- **GitHub configuration snapshot (observation, not immutable policy):** the PR #204 draft dated 2026-11-12 states that `main` requires PR/review, checks `backend`, `portal-bff`, `frontend`, `repo-hygiene` (with `r23-compliance`), squash merges, the `protect-release-tags` ruleset and the `r24-release` environment. This is a **claim from the draft**, not independent verification; reviewers should inspect GitHub Settings or evidence before labeling it `VERIFIED`. These specifics can evolve without changing the underlying governance principles.
- If observed settings diverge from policy, open an Issue to reconcile them; missing enforcement is not a waiver. Review this policy when maintainer composition, distribution governance or applicable obligations change — **not automatically for each software release**.
