<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# Contributing to OpenTrix

> **Language / Ngôn ngữ:** [English](#en) · [Tiếng Việt](#vi)

---

<a id="en"></a>

## Contributing Guide

Thank you for your interest in OpenTrix. Contributions are accepted through Issues and pull
requests in this repository. All contributions are submitted and distributed under the
[Apache License 2.0](https://github.com/tricore-opentrix/opentrix/blob/main/LICENSE). Third-party code, libraries and assets keep their own licenses
and obligations, which are recorded in [NOTICE](https://github.com/tricore-opentrix/opentrix/blob/main/NOTICE) and
[THIRD-PARTY-NOTICES.md](https://github.com/tricore-opentrix/opentrix/blob/main/THIRD-PARTY-NOTICES.md).

### Before you start

- Read the [README](https://github.com/tricore-opentrix/opentrix/blob/main/README.md), the architecture and API documentation in [`docs/`](https://github.com/tricore-opentrix/opentrix/tree/main/docs), and
  the open Issues.
- Open an Issue before starting a large change that affects public API contracts, the
  core/application boundary, authorization or data storage.
- Contribute only code, data and assets you have the right to submit. Never include passwords,
  tokens, real `.env` files, real user data or unapproved images in Issues, pull requests, tests
  or screenshots. Use invented fixtures and the placeholder values in `.env.example`.
- By submitting a contribution, you agree to the terms in section 5 of the
  [Apache License 2.0](https://github.com/tricore-opentrix/opentrix/blob/main/LICENSE) and confirm that your employer or any other rights holder
  permits it. No separate Contributor License Agreement (CLA) is required.

### Use of AI tools

AI tools, including but not limited to ChatGPT, Codex, Claude and Claude Code, may be used to
assist with requirements analysis, design, writing or changing code, testing and documentation.
**Using AI does not change the contributor's responsibility** for what they submit.

- **Review and testing:** read and assess all AI output; verify correctness, security,
  architecture boundaries, API contracts and maintainability; run the appropriate tests and state
  any check that was skipped or not run. Unreviewed or untested AI output is not considered
  accepted.
- **Disclosure in pull requests:** for every pull request that includes AI-assisted work, state
  (1) the AI tools used, if known; (2) the scope of use, such as design, code, tests, fixtures,
  documentation or review; (3) external code, images, templates, data or documents given to or
  referenced by the tool, if known; (4) the tests and license checks performed; and (5) any
  remaining uncertainty. If a tool, source or detail cannot be recalled, write `UNKNOWN` or
  `NOT_RECALLED` instead of guessing. If no AI was used, you may write `AI use: None`.
- **Provenance and rights:** do not ask an AI tool to reproduce code, templates, icons, assets or
  content you are not entitled to use. If AI output is known or suspected to closely resemble
  external material, check its origin, license terms and attribution requirements before
  proposing it. AI generation, Git history, SPDX headers or passing CI are not proof of
  originality or of the right to redistribute.
- **Unverified material:** mark unknown provenance as `UNKNOWN` and unverified usage or
  distribution rights as `RIGHTS_PENDING`; never change these to `CLEARED` without review.
  Describe the affected scope and refer it to an independent maintainer. Material with unresolved
  rights must not be included in a release. Each decision needs a documented reason and review
  record; the outcome may be correction, replacement, exclusion from distribution or continued
  blocking.
- **Possible source overlap:** if you find code or assets that may closely match external
  material under a different license, open an Issue, or report it privately as described in
  [SECURITY.md](https://github.com/tricore-opentrix/opentrix/blob/main/SECURITY.md) when security or sensitive information is involved. Maintainers
  investigate **within 7 days of receiving the report**, record the findings and decide whether to
  remove, rewrite or add the required attribution and license compliance. The outcome is recorded
  in [CHANGELOG.md](https://github.com/tricore-opentrix/opentrix/blob/main/CHANGELOG.md). While distribution rights remain unverified, the material stays
  `RIGHTS_PENDING` and is excluded from releases. The 7-day investigation period does not mean
  every case can be fully resolved within that time.
- **Protecting information:** never give AI tools passwords, tokens, private keys, personal or
  customer data, internal secrets, restricted third-party code or material you are not allowed to
  share. Use synthetic data and follow [SECURITY.md](https://github.com/tricore-opentrix/opentrix/blob/main/SECURITY.md).
- **Applicability:** these disclosure rules apply to contributions submitted after this policy was
  adopted. The provenance of earlier contributions is reviewed separately in
  [Issue #138](https://github.com/tricore-opentrix/opentrix/issues/138).

**Pull request disclosure template** (fill in with actual facts; do not leave placeholder values):

```text
AI use: [Tools used, or None]
Scope: [Code / tests / docs / design / review / other]
External sources: [Links and licenses, or UNKNOWN / none known]
Review and tests: [Commands, results, skipped checks]
Provenance / rights status: [Verified scope; UNKNOWN / RIGHTS_PENDING where applicable]
```

### Development environment

To run the whole system locally, follow [Run locally](https://github.com/tricore-opentrix/opentrix/blob/main/README.md#run-locally) in the README and
the detailed guide in [`infra/demo/README.md`](https://github.com/tricore-opentrix/opentrix/blob/main/infra/demo/README.md).

### License headers and container images

- New source files you write (Java, TypeScript/TSX, SQL, YAML, shell, Markdown) must carry the
  SPDX Apache-2.0 header:

  ```java
  // SPDX-FileCopyrightText: 2026 TRICORE contributors
  // SPDX-License-Identifier: Apache-2.0
  ```

  Use `--` for SQL, `#` for YAML and shell, and `<!-- -->` for Markdown. Check locally before
  submitting:

  ```sh
  reuse lint
  ```

  CI runs the same check in the `repo-hygiene` job, and a REUSE failure fails the job. Do not add
  the project header to external code or to material whose rights have not been verified.

- Container images in Compose files and CI must be pinned to a specific tag, never `latest`. If
  an older version is kept for licensing reasons, upgrade it only after discussion in an Issue,
  and update [NOTICE](https://github.com/tricore-opentrix/opentrix/blob/main/NOTICE).

### Dependencies and third-party licenses

- **Automated check:** a CI job checks the licenses of all dependencies in the CycloneDX SBOMs
  against an allow-list (`scripts/r23-compliance.py`). A license that is not on the list, or is
  not declared, fails the job.
- **Allow-list:** 0BSD, Apache-2.0, BlueOak-1.0.0, BSD-2-Clause, BSD-3-Clause, CC0-1.0, CDDL-1.0,
  CDDL-1.1, EDL-1.0, EPL-1.0, EPL-2.0, ISC, MIT, MIT-0, MPL-2.0, OFL-1.1, Unicode-3.0,
  Unicode-DFS-2016, Unlicense and Zlib, plus the reviewed exception GPL-2.0 with
  Classpath-exception-2.0.
- **Conditional licenses:** dependencies under MPL, EPL, CDDL or the Classpath exception are used
  without modification and must be listed in [NOTICE](https://github.com/tricore-opentrix/opentrix/blob/main/NOTICE).
- **Changing the allow-list:** adding or removing a license requires a pull request that updates
  the script and this document together.
- **THIRD-PARTY-NOTICES.md** is generated by the same script; do not edit it by hand. CI compares
  the committed file with a freshly generated copy.
- **Separately running services** such as Keycloak, PostgreSQL and APISIX are not covered by the
  automated check; their licenses are reviewed manually and recorded in [NOTICE](https://github.com/tricore-opentrix/opentrix/blob/main/NOTICE).
- **No copying from other projects:** OpenTrix follows independent design patterns and does not
  copy code, templates, icons or assets from other projects.

### Workflow

```text
Issue → branch from main → draft pull request to main → CI → independent review → squash merge → close Issue → delete branch
```

- **Issues:** every significant change needs an Issue with a goal, acceptance criteria, an
  assignee and an `area:*` label. Use titles of the form `[Area] Short description`.
- **Branches:** branch from an up-to-date `main`, name the branch `<type>/<area>-<description>`
  (for example `feat/workflow-outbox-event`) and keep it short-lived. Never push directly to `main`.
- **Commits and pull request titles:** follow
  [Conventional Commits](https://www.conventionalcommits.org/):
  `<type>(<area>): <short description>`, where `type` is `feat`, `fix`, `docs`, `test`,
  `refactor`, `chore`, `ci` or `build`.

### Pull requests

1. Keep each change focused (around 400 lines) and describe the user-visible behavior and any
   compatibility impact. Use the pull request template; write `Refs #N` for partial work and
   `Closes #N` only when all acceptance criteria are met.
2. Keep the boundary between the headless core and applications. Applications call the core only
   through its published API, and never trust a tenant or identity sent by an unauthenticated
   client.
3. When an API or event contract changes, update the contract and both consumers in the same pull
   request.
4. Run the checks for the modules you changed and record the commands and results in the pull
   request. For authorization or security changes, add tests for both the denied and the allowed
   paths.
5. Update the README, API documentation or [CHANGELOG.md](https://github.com/tricore-opentrix/opentrix/blob/main/CHANGELOG.md) when external behavior
   changes, and state any check you could not run.
6. Disclose AI use and provenance status as described in [Use of AI tools](#use-of-ai-tools).
   Disclosure alone does not clear any rights.
7. At least one independent approval and passing CI are required before squash merging. Close the
   Issue only after its acceptance criteria are verified on `main`.

### Maintainers

| Scope                                                   | Maintainer            | Reviewers                                      |
| ------------------------------------------------------- | --------------------- | ---------------------------------------------- |
| Core integration, releases and merging                  | @phanyen06ym-ien      | @lexuanbao258-collab                           |
| Core testing, repository administration, infrastructure | @lexuanbao258-collab  | @phanyen06ym-ien                               |
| IT Helpdesk application and Portal BFF                  | @ngang02012007-crypto | @lexuanbao258-collab                           |
| Frontend                                                | @ngang02012007-crypto | @phanyen06ym-ien                               |
| Helpdesk-related core paths and BFF API                 | —                     | @lexuanbao258-collab and @ngang02012007-crypto |

[CODEOWNERS](https://github.com/tricore-opentrix/opentrix/blob/main/.github/CODEOWNERS) requests reviews automatically by path. Authors do not approve
their own pull requests; if the author is one of the required reviewers, agree on a replacement
reviewer in the pull request before merging.

**Changing this policy:** changes to `CONTRIBUTING.md` require an Issue explaining the reason, the
recorded agreement of all three maintainers, and a pull request that stays open for at least one
business day and receives two approvals from maintainers other than the author, as described in
[GOVERNANCE.md](https://github.com/tricore-opentrix/opentrix/blob/main/GOVERNANCE.md). Agreement does not replace independent review, CI or release
requirements. The new policy takes effect once the pull request is merged.

### Security

Report security vulnerabilities privately, not in a public Issue. See [SECURITY.md](https://github.com/tricore-opentrix/opentrix/blob/main/SECURITY.md).

---

<a id="vi"></a>

## Hướng dẫn đóng góp

Cảm ơn bạn đã quan tâm đến OpenTrix. Dự án nhận đóng góp qua Issue và pull request trên
repository này. Mọi đóng góp được gửi và phân phối theo [Apache License 2.0](https://github.com/tricore-opentrix/opentrix/blob/main/LICENSE). Mã nguồn,
thư viện và tài sản của bên thứ ba giữ nguyên giấy phép và nghĩa vụ riêng, được ghi trong
[NOTICE](https://github.com/tricore-opentrix/opentrix/blob/main/NOTICE) và [THIRD-PARTY-NOTICES.md](https://github.com/tricore-opentrix/opentrix/blob/main/THIRD-PARTY-NOTICES.md).

### Trước khi bắt đầu

- Đọc [README](https://github.com/tricore-opentrix/opentrix/blob/main/README.md), tài liệu kiến trúc và API trong [`docs/`](https://github.com/tricore-opentrix/opentrix/tree/main/docs), và các Issue đang mở.
- Mở Issue trước khi bắt đầu thay đổi lớn ảnh hưởng đến hợp đồng API công khai, ranh giới giữa
  core và ứng dụng, phân quyền hoặc cách lưu trữ dữ liệu.
- Chỉ đóng góp mã nguồn, dữ liệu và tài sản mà bạn có quyền gửi. Không đưa mật khẩu, token, tệp
  `.env` thật, dữ liệu người dùng thật hay hình ảnh chưa được phép vào Issue, pull request, test
  hoặc ảnh chụp màn hình. Dùng dữ liệu mẫu tự tạo và các giá trị giả trong `.env.example`.
- Khi gửi đóng góp, bạn đồng ý với điều khoản tại mục 5 của [Apache License 2.0](https://github.com/tricore-opentrix/opentrix/blob/main/LICENSE) và xác
  nhận rằng chủ lao động hoặc chủ thể quyền khác cho phép việc này. Dự án không yêu cầu thỏa thuận
  cấp phép đóng góp (CLA) riêng.

### Sử dụng công cụ AI

Có thể dùng công cụ AI, bao gồm nhưng không giới hạn ở ChatGPT, Codex, Claude và Claude Code, để
hỗ trợ phân tích yêu cầu, thiết kế, viết hoặc sửa mã nguồn, kiểm thử và viết tài liệu.
**Việc dùng AI không thay đổi trách nhiệm của người đóng góp** đối với nội dung đã gửi.

- **Review và kiểm thử:** đọc và đánh giá toàn bộ đầu ra của AI; kiểm tra tính đúng đắn, bảo mật,
  ranh giới kiến trúc, hợp đồng API và khả năng bảo trì; chạy các kiểm thử phù hợp và ghi rõ kiểm
  tra nào bị bỏ qua hoặc chưa chạy. Đầu ra AI chưa được review hoặc kiểm thử không được coi là đã
  nghiệm thu.
- **Khai báo trong pull request:** với mọi pull request có phần việc do AI hỗ trợ, ghi rõ (1) công
  cụ AI đã dùng, nếu biết; (2) phạm vi sử dụng, ví dụ thiết kế, mã nguồn, kiểm thử, fixture, tài
  liệu hoặc review; (3) mã, hình ảnh, template, dữ liệu hoặc tài liệu bên ngoài đã đưa vào hoặc
  được công cụ tham chiếu, nếu biết; (4) các kiểm thử và kiểm tra giấy phép đã thực hiện; và
  (5) các điểm còn chưa chắc chắn. Nếu không nhớ được công cụ, nguồn hoặc chi tiết, ghi `UNKNOWN`
  hoặc `NOT_RECALLED` thay vì đoán. Nếu không dùng AI, có thể ghi `AI use: None`.
- **Nguồn gốc và quyền:** không yêu cầu AI tái tạo mã, template, icon, asset hoặc nội dung mà bạn
  không có quyền sử dụng. Nếu biết hoặc nghi ngờ đầu ra AI giống đáng kể với nội dung bên ngoài,
  hãy kiểm tra nguồn gốc, điều kiện giấy phép và yêu cầu ghi công trước khi đề xuất. Việc AI sinh
  ra nội dung, lịch sử Git, header SPDX hay CI đạt không chứng minh tính nguyên gốc hoặc quyền phân
  phối lại.
- **Nội dung chưa xác minh:** ghi `UNKNOWN` cho nguồn gốc chưa xác định và `RIGHTS_PENDING` cho
  quyền sử dụng hoặc phân phối chưa được xác minh; không tự đổi sang `CLEARED` khi chưa review. Nêu
  rõ phạm vi bị ảnh hưởng và chuyển cho một maintainer độc lập xem xét. Nội dung còn vướng quyền
  không được đưa vào bản phát hành. Mỗi quyết định cần có lý do và dấu vết review; kết quả có thể
  là sửa, thay thế, loại khỏi phân phối hoặc tiếp tục chặn.
- **Nghi ngờ trùng nguồn:** nếu phát hiện mã hoặc tài sản có thể giống đáng kể với nội dung bên
  ngoài theo giấy phép khác, hãy mở Issue, hoặc báo cáo riêng theo [SECURITY.md](https://github.com/tricore-opentrix/opentrix/blob/main/SECURITY.md) nếu
  liên quan đến bảo mật hay thông tin nhạy cảm. Maintainer xác minh **trong vòng 7 ngày kể từ khi
  nhận báo cáo**, ghi lại kết quả và quyết định gỡ bỏ, viết lại hoặc bổ sung ghi công và tuân thủ
  giấy phép. Kết quả được ghi vào [CHANGELOG.md](https://github.com/tricore-opentrix/opentrix/blob/main/CHANGELOG.md). Khi quyền phân phối chưa được xác
  minh, nội dung giữ trạng thái `RIGHTS_PENDING` và không được đưa vào bản phát hành. Thời hạn xác
  minh 7 ngày không có nghĩa mọi trường hợp đều được xử lý dứt điểm trong thời gian đó.
- **Bảo vệ thông tin:** không nhập vào công cụ AI mật khẩu, token, private key, dữ liệu cá nhân hoặc
  của khách hàng, bí mật nội bộ, mã bên thứ ba bị hạn chế hay tài liệu không được phép chia sẻ. Dùng
  dữ liệu giả và tuân thủ [SECURITY.md](https://github.com/tricore-opentrix/opentrix/blob/main/SECURITY.md).
- **Phạm vi áp dụng:** các quy định khai báo này áp dụng cho đóng góp gửi sau khi chính sách được
  thông qua. Nguồn gốc của các đóng góp trước đó được xem xét riêng tại
  [Issue #138](https://github.com/tricore-opentrix/opentrix/issues/138).

**Mẫu khai báo trong pull request** (điền theo thông tin thực tế; không để nguyên giá trị mẫu):

```text
AI use: [Công cụ đã dùng, hoặc None]
Scope: [Code / tests / docs / design / review / other]
External sources: [Liên kết và giấy phép, hoặc UNKNOWN / none known]
Review and tests: [Lệnh đã chạy, kết quả, kiểm tra bị bỏ qua]
Provenance / rights status: [Phạm vi đã xác minh; UNKNOWN / RIGHTS_PENDING nếu có]
```

### Môi trường phát triển

Để chạy toàn bộ hệ thống trên máy cục bộ, làm theo mục [Chạy cục bộ](https://github.com/tricore-opentrix/opentrix/blob/main/README.md#chạy-cục-bộ)
trong README và hướng dẫn chi tiết trong [`infra/demo/README.md`](https://github.com/tricore-opentrix/opentrix/blob/main/infra/demo/README.md).

### Header giấy phép và container image

- Tệp nguồn mới do bạn viết (Java, TypeScript/TSX, SQL, YAML, shell, Markdown) phải có header SPDX
  Apache-2.0:

  ```java
  // SPDX-FileCopyrightText: 2026 TRICORE contributors
  // SPDX-License-Identifier: Apache-2.0
  ```

  Dùng `--` cho SQL, `#` cho YAML và shell, `<!-- -->` cho Markdown. Tự kiểm tra trước khi gửi:

  ```sh
  reuse lint
  ```

  CI chạy cùng kiểm tra này trong job `repo-hygiene`; lỗi REUSE làm job thất bại. Không gắn header
  của dự án cho mã bên ngoài hoặc nội dung chưa xác minh được quyền.

- Container image trong các tệp Compose và CI phải ghim một tag cụ thể, không dùng `latest`. Nếu
  giữ phiên bản cũ vì lý do giấy phép, chỉ nâng cấp sau khi thảo luận trong Issue và cập nhật
  [NOTICE](https://github.com/tricore-opentrix/opentrix/blob/main/NOTICE).

### Thư viện phụ thuộc và giấy phép bên thứ ba

- **Kiểm tra tự động:** một job CI đối chiếu giấy phép của mọi thư viện phụ thuộc trong các SBOM
  CycloneDX với danh sách cho phép (`scripts/r23-compliance.py`). Giấy phép không có trong danh sách
  hoặc không được khai báo sẽ làm job thất bại.
- **Danh sách cho phép:** 0BSD, Apache-2.0, BlueOak-1.0.0, BSD-2-Clause, BSD-3-Clause, CC0-1.0,
  CDDL-1.0, CDDL-1.1, EDL-1.0, EPL-1.0, EPL-2.0, ISC, MIT, MIT-0, MPL-2.0, OFL-1.1, Unicode-3.0,
  Unicode-DFS-2016, Unlicense và Zlib, cùng ngoại lệ đã được rà soát GPL-2.0 kèm
  Classpath-exception-2.0.
- **Giấy phép có điều kiện:** thư viện theo MPL, EPL, CDDL hoặc ngoại lệ Classpath được dùng nguyên
  bản, không sửa đổi, và phải được liệt kê trong [NOTICE](https://github.com/tricore-opentrix/opentrix/blob/main/NOTICE).
- **Thay đổi danh sách cho phép:** thêm hoặc bớt giấy phép phải qua một pull request cập nhật đồng
  thời script và tài liệu này.
- **THIRD-PARTY-NOTICES.md** được sinh tự động bởi cùng script; không sửa tay. CI so sánh tệp trong
  repository với bản sinh lại.
- **Dịch vụ chạy tách biệt** như Keycloak, PostgreSQL và APISIX không nằm trong kiểm tra tự động;
  giấy phép của chúng được rà soát thủ công và ghi trong [NOTICE](https://github.com/tricore-opentrix/opentrix/blob/main/NOTICE).
- **Không sao chép từ dự án khác:** OpenTrix áp dụng các mẫu thiết kế độc lập, không sao chép mã,
  template, icon hay asset của dự án khác.

### Quy trình làm việc

```text
Issue → nhánh từ main → pull request nháp vào main → CI → review độc lập → squash merge → đóng Issue → xóa nhánh
```

- **Issue:** mỗi thay đổi đáng kể cần một Issue có mục tiêu, tiêu chí nghiệm thu, người phụ trách
  và nhãn `area:*`. Tiêu đề có dạng `[Area] Mô tả ngắn`.
- **Nhánh:** tạo từ `main` mới nhất, đặt tên `<type>/<area>-<mô-tả>` (ví dụ
  `feat/workflow-outbox-event`) và giữ thời gian sống ngắn. Không push thẳng vào `main`.
- **Commit và tiêu đề pull request:** theo
  [Conventional Commits](https://www.conventionalcommits.org/):
  `<type>(<area>): <mô tả ngắn>`, trong đó `type` là `feat`, `fix`, `docs`, `test`, `refactor`,
  `chore`, `ci` hoặc `build`.

### Pull request

1. Giữ mỗi thay đổi gọn (khoảng 400 dòng), mô tả hành vi người dùng thấy được và ảnh hưởng tương
   thích. Dùng mẫu pull request; ghi `Refs #N` khi chỉ làm một phần, `Closes #N` khi đáp ứng đủ
   tiêu chí nghiệm thu.
2. Giữ ranh giới giữa core headless và ứng dụng. Ứng dụng chỉ gọi core qua API đã công bố và không
   tin tenant hay danh tính do client chưa xác thực gửi lên.
3. Khi hợp đồng API hoặc sự kiện thay đổi, cập nhật hợp đồng và cả hai phía sử dụng trong cùng một
   pull request.
4. Chạy các kiểm tra cho module đã sửa và ghi lệnh cùng kết quả vào pull request. Với thay đổi về
   phân quyền hoặc bảo mật, bổ sung test cho cả trường hợp bị từ chối và được phép.
5. Cập nhật README, tài liệu API hoặc [CHANGELOG.md](https://github.com/tricore-opentrix/opentrix/blob/main/CHANGELOG.md) khi hành vi bên ngoài thay đổi,
   và ghi rõ kiểm tra nào chưa chạy được.
6. Khai báo việc dùng AI và tình trạng nguồn gốc theo mục [Sử dụng công cụ AI](#sử-dụng-công-cụ-ai).
   Bản khai báo không tự xác nhận quyền.
7. Cần ít nhất một phê duyệt độc lập và CI đạt trước khi squash merge. Chỉ đóng Issue khi tiêu chí
   nghiệm thu đã được xác minh trên `main`.

### Người duy trì

| Phạm vi                                          | Người duy trì         | Người review                                  |
| ------------------------------------------------ | --------------------- | --------------------------------------------- |
| Tích hợp core, phát hành và merge                | @phanyen06ym-ien      | @lexuanbao258-collab                          |
| Kiểm thử core, quản trị repository, hạ tầng      | @lexuanbao258-collab  | @phanyen06ym-ien                              |
| Ứng dụng IT Helpdesk và Portal BFF               | @ngang02012007-crypto | @lexuanbao258-collab                          |
| Frontend                                         | @ngang02012007-crypto | @phanyen06ym-ien                              |
| Đường dẫn core liên quan Helpdesk và API của BFF | —                     | @lexuanbao258-collab và @ngang02012007-crypto |

[CODEOWNERS](https://github.com/tricore-opentrix/opentrix/blob/main/.github/CODEOWNERS) tự động yêu cầu review theo đường dẫn. Tác giả không tự duyệt pull
request của mình; nếu tác giả là một trong các reviewer bắt buộc, cần thống nhất reviewer thay thế
trong pull request trước khi merge.

**Thay đổi chính sách này:** sửa đổi `CONTRIBUTING.md` cần một Issue nêu lý do, sự đồng ý được ghi
nhận của cả ba maintainer, và một pull request mở ít nhất một ngày làm việc với hai phê duyệt từ
maintainer không phải tác giả, theo [GOVERNANCE.md](https://github.com/tricore-opentrix/opentrix/blob/main/GOVERNANCE.md). Sự đồng thuận không thay thế
review độc lập, CI hay các yêu cầu phát hành. Chính sách mới có hiệu lực khi pull request được merge.

### Bảo mật

Báo cáo lỗ hổng bảo mật qua kênh riêng, không đăng Issue công khai. Xem [SECURITY.md](https://github.com/tricore-opentrix/opentrix/blob/main/SECURITY.md).
