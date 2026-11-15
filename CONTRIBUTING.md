<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# OpenTrix

> **Ngôn ngữ / Language:** [Tiếng Việt](#vi) · [English](#en)

---

<a id="vi"></a>

## OpenTrix — Hướng dẫn đóng góp

OpenTrix nhận đóng góp qua Issue và pull request trên repository này. Mọi đóng góp được gửi và phân phối theo [Apache License 2.0](LICENSE); quyền sử dụng, sửa đổi và phân phối phần đóng góp đến từ giấy phép này. Mã nguồn, thư viện và tài sản của bên thứ ba giữ nguyên giấy phép và nghĩa vụ riêng, được ghi trong [NOTICE](NOTICE) và [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).

### Trước khi bắt đầu

- Đọc [README](README.md), tài liệu kiến trúc và API trong [`docs/`](docs/), và các Issue đang mở.
- Mở Issue trước khi viết thay đổi lớn nếu thay đổi hợp đồng API công khai, ranh giới giữa core và ứng dụng, phân quyền hay cách lưu trữ dữ liệu.
- Chỉ dùng mã nguồn, dữ liệu và tài sản mà bạn có quyền đóng góp. Không đưa mật khẩu, token, file `.env` thật, dữ liệu người dùng thật hay hình ảnh chưa được phép vào Issue, pull request, test hoặc ảnh chụp màn hình. Hãy dùng dữ liệu mẫu tự dựng và giá trị giả trong `.env.example`.
- Khi gửi đóng góp để đưa vào dự án, bạn đồng ý với điều khoản đóng góp tại mục 5 của [Apache License 2.0](LICENSE) và bảo đảm chủ lao động hoặc chủ thể quyền khác cho phép. Dự án không yêu cầu thỏa thuận cấp phép đóng góp (CLA) riêng.

### Môi trường phát triển

Cách chạy toàn bộ hệ thống trên máy cục bộ được mô tả tại mục _Chạy cục bộ_ trong [README](README.md) và chi tiết trong [`infra/demo/README.md`](infra/demo/README.md).

### Header giấy phép và phiên bản image

- File nguồn mới do bạn tự viết — Java, TypeScript/TSX, SQL, YAML, shell, Markdown — phải mang header SPDX Apache-2.0:

  ```java
  // SPDX-FileCopyrightText: 2026 TRICORE contributors
  // SPDX-License-Identifier: Apache-2.0
  ```

  Dùng `--` cho SQL, `#` cho YAML và shell, `<!-- -->` cho Markdown. Tự kiểm tra trước khi gửi:

  ```
  reuse lint
  ```

  CI chạy cùng kiểm tra này (`fsfe/reuse-action`) trong job `repo-hygiene`; lỗi REUSE làm job thất bại. Không gắn header của dự án cho mã bên ngoài hoặc mã chưa xác minh được quyền.

- Container image trong các file Compose và CI phải pin tag cụ thể, không dùng `latest`. Khi giữ một phiên bản cũ vì lý do giấy phép, chỉ nâng cấp sau khi thảo luận trong Issue và cập nhật [NOTICE](NOTICE).

### Dependency và giấy phép bên thứ ba

- **Kiểm tra tự động:** job CI `r23-compliance` (`scripts/r23-compliance.py`) đối chiếu giấy phép dependency trong các SBOM CycloneDX với danh sách cho phép. Giấy phép không có trong danh sách hoặc không được khai báo làm job thất bại.
- **Danh sách cho phép:** 0BSD, Apache-2.0, BlueOak-1.0.0, BSD-2-Clause, BSD-3-Clause, CC0-1.0, CDDL-1.0, CDDL-1.1, EDL-1.0, EPL-1.0, EPL-2.0, ISC, MIT, MIT-0, MPL-2.0, OFL-1.1, Unicode-3.0, Unicode-DFS-2016, Unlicense, Zlib; cùng ngoại lệ đã rà soát GPL-2.0 kèm Classpath-exception-2.0.
- **Giấy phép có điều kiện:** dependency theo MPL, EPL, CDDL hoặc ngoại lệ Classpath chỉ được dùng nguyên bản, không sửa mã gốc, và phải được ghi nhận trong [NOTICE](NOTICE).
- **Thay đổi danh sách:** thêm hoặc bớt giấy phép phải qua PR sửa `scripts/r23-compliance.py` và cập nhật tài liệu này trong cùng PR.
- **THIRD-PARTY-NOTICES.md** được sinh tự động bởi `scripts/r23-compliance.py`; không sửa tay. CI so sánh file trong repository với bản sinh lại.
- **Image và dịch vụ chạy tách biệt** (ví dụ Keycloak, PostgreSQL, APISIX) không nằm trong kiểm tra tự động; giấy phép của chúng được rà soát thủ công và ghi trong [NOTICE](NOTICE).
- **Không sao chép từ dự án khác:** OpenTrix chỉ áp dụng các mẫu thiết kế độc lập, không sao chép mã, template, icon hay asset.

### Quy trình làm việc

```text
Issue → nhánh từ main → Draft PR vào main → CI → review độc lập → squash merge → đóng Issue → xóa nhánh
```

- **Issue:** mỗi thay đổi đáng kể cần một Issue có mục tiêu, tiêu chí nghiệm thu, người phụ trách và label `area:*`. Tiêu đề dạng `[Area] Mô tả ngắn`.
- **Nhánh:** tạo từ `main` mới nhất, đặt tên `<type>/<area>-<mô-tả>` (ví dụ `feat/workflow-outbox-event`) và giữ thời gian sống ngắn. Không push thẳng vào `main`.
- **Commit và tiêu đề PR:** theo [Conventional Commits](https://www.conventionalcommits.org/) — `<type>(<area>): <mô tả ngắn>`, với type là `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci` hoặc `build`.

### Pull request

1. Giữ thay đổi gọn theo phạm vi (khoảng 400 dòng), giải thích hành vi người dùng thấy được và ảnh hưởng tương thích. Dùng PR template; ghi `Refs #N` khi PR làm một phần Issue, `Closes #N` khi đáp ứng đủ tiêu chí nghiệm thu.
2. Giữ ranh giới giữa core headless và ứng dụng. Ứng dụng chỉ gọi core qua API đã công bố; không tin tenant hay danh tính do client chưa xác thực gửi lên.
3. Khi thay đổi hợp đồng API hoặc sự kiện, cập nhật hợp đồng và cả hai phía tiêu thụ trong cùng PR.
4. Chạy các kiểm tra phù hợp với module đã sửa và ghi lệnh cùng kết quả vào PR. Với thay đổi về phân quyền hay bảo mật, kèm test thể hiện cả đường bị từ chối và đường được phép.
5. Cập nhật README, tài liệu API hoặc [`CHANGELOG.md`](CHANGELOG.md) khi hành vi bên ngoài thay đổi, và nêu rõ kiểm tra nào chưa chạy được.
6. Cần ít nhất một phê duyệt độc lập và CI liên quan đạt trước khi squash merge. Issue chỉ được đóng khi tiêu chí nghiệm thu đã được xác minh trên `main`.

### Người duy trì

| Phạm vi                                          | Người duy trì         | Review                                        |
| ------------------------------------------------ | --------------------- | --------------------------------------------- |
| Tích hợp Core, phát hành và merge                | @phanyen06ym-ien      | @lexuanbao258-collab                          |
| Kiểm thử Core, quản trị repository, hạ tầng      | @lexuanbao258-collab  | @phanyen06ym-ien                              |
| Ứng dụng IT Helpdesk và Portal BFF               | @ngang02012007-crypto | @lexuanbao258-collab                          |
| Frontend                                         | @ngang02012007-crypto | @phanyen06ym-ien                              |
| Đường dẫn Core liên quan Helpdesk và API của BFF | —                     | @lexuanbao258-collab và @ngang02012007-crypto |

[CODEOWNERS](.github/CODEOWNERS) tự động yêu cầu review theo đường dẫn. Tác giả không tự duyệt PR của mình; nếu tác giả là một trong các reviewer bắt buộc, cần thống nhất reviewer thay thế trên PR trước khi merge.

### Bảo mật

Báo cáo lỗ hổng bảo mật qua kênh riêng, không đăng Issue công khai. Xem [SECURITY.md](SECURITY.md).

---

<a id="en"></a>

## OpenTrix — Contributing Guide

OpenTrix accepts contributions through Issues and pull requests in this repository. All contributions are submitted and distributed under the [Apache License 2.0](LICENSE); the rights to use, modify, and distribute them come from that license. Third-party code, libraries, and assets keep their own licenses and obligations, recorded in [NOTICE](NOTICE) and [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).

### Before you start

- Read the [README](README.md), the architecture and API documents in [`docs/`](docs/), and open Issues.
- Open an Issue before writing a large patch that changes public API contracts, the core/application boundary, authorization, or data storage.
- Use only code, data, and assets you have permission to contribute. Never include passwords, tokens, real `.env` files, real user data, or unapproved images in Issues, pull requests, tests, or screenshots. Use invented fixtures and placeholder values in `.env.example`.
- By submitting a contribution for inclusion, you agree to the contribution terms in section 5 of the [Apache License 2.0](LICENSE) and confirm that your employer or other rights holders authorize it. No separate contributor license agreement (CLA) is required.

### Development environment

Running the full system locally is described under _Run locally_ in the [README](README.md), with details in [`infra/demo/README.md`](infra/demo/README.md).

### License headers and image versions

- New source files you author — Java, TypeScript/TSX, SQL, YAML, shell, Markdown — must carry the SPDX Apache-2.0 header:

  ```java
  // SPDX-FileCopyrightText: 2026 TRICORE contributors
  // SPDX-License-Identifier: Apache-2.0
  ```

  Use `--` for SQL, `#` for YAML and shell, and `<!-- -->` for Markdown. Check locally before submitting:

  ```
  reuse lint
  ```

  CI runs the same check (`fsfe/reuse-action`) in the `repo-hygiene` job; a REUSE failure fails the job. Do not apply the project header to external or rights-unverified material.

- Container images in Compose files and CI must pin specific tags, never `latest`. When an older version is kept for licensing reasons, upgrade only after discussion in an Issue and update [NOTICE](NOTICE).

### Dependencies and third-party licenses

- **Automated check:** the `r23-compliance` CI job (`scripts/r23-compliance.py`) checks dependency licenses in the CycloneDX SBOMs against an allow-list. Any license not on the list, or undeclared, fails the job.
- **Allow-list:** 0BSD, Apache-2.0, BlueOak-1.0.0, BSD-2-Clause, BSD-3-Clause, CC0-1.0, CDDL-1.0, CDDL-1.1, EDL-1.0, EPL-1.0, EPL-2.0, ISC, MIT, MIT-0, MPL-2.0, OFL-1.1, Unicode-3.0, Unicode-DFS-2016, Unlicense, Zlib; plus the reviewed exception GPL-2.0 with Classpath-exception-2.0.
- **Conditional licenses:** dependencies under MPL, EPL, CDDL, or the Classpath exception are used unmodified only and must be recorded in [NOTICE](NOTICE).
- **Changing the list:** adding or removing a license requires a PR that changes `scripts/r23-compliance.py` and updates this document in the same PR.
- **THIRD-PARTY-NOTICES.md** is generated by `scripts/r23-compliance.py`; do not edit it by hand. CI compares the committed file with a fresh copy.
- **Separately running images and services** (for example Keycloak, PostgreSQL, APISIX) are outside the automated check; their licenses are reviewed manually and recorded in [NOTICE](NOTICE).
- **No copying from other projects:** OpenTrix applies independent design patterns only, never copied code, templates, icons, or assets.

### Workflow

```text
Issue → branch from main → Draft PR to main → CI → independent review → squash merge → close Issue → delete branch
```

- **Issues:** each significant change needs an Issue with a goal, acceptance criteria, an owner, and an `area:*` label. Use titles like `[Area] Short description`.
- **Branches:** create from an up-to-date `main`, name them `<type>/<area>-<description>` (for example `feat/workflow-outbox-event`), and keep them short-lived. Do not push directly to `main`.
- **Commits and PR titles:** follow [Conventional Commits](https://www.conventionalcommits.org/) — `<type>(<area>): <short description>`, where type is `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`, or `build`.

### Pull requests

1. Keep changes scoped (around 400 lines) and explain the user-visible behavior and any compatibility impact. Use the PR template; write `Refs #N` for partial work and `Closes #N` only when the full acceptance criteria are met.
2. Preserve the boundary between the headless core and applications. Applications call the core only through its published API; never trust a tenant or identity supplied by an unauthenticated client.
3. When changing API or event contracts, update the contract and both consumers in the same PR.
4. Run the checks appropriate to the touched modules and record the commands and results in the PR. For authorization or security changes, include tests demonstrating both the denied and allowed paths.
5. Update the README, API documentation, or [`CHANGELOG.md`](CHANGELOG.md) when external behavior changes, and state any check you could not run.
6. At least one independent approval and passing relevant CI are required before squash merge. Close the Issue only after its acceptance criteria are verified on `main`.

### Maintainers

| Scope                                                   | Maintainer            | Review                                         |
| ------------------------------------------------------- | --------------------- | ---------------------------------------------- |
| Core integration, release and merge                     | @phanyen06ym-ien      | @lexuanbao258-collab                           |
| Core testing, repository administration, infrastructure | @lexuanbao258-collab  | @phanyen06ym-ien                               |
| IT Helpdesk application and Portal BFF                  | @ngang02012007-crypto | @lexuanbao258-collab                           |
| Frontend                                                | @ngang02012007-crypto | @phanyen06ym-ien                               |
| Helpdesk-related Core paths and BFF API                 | —                     | @lexuanbao258-collab and @ngang02012007-crypto |

[CODEOWNERS](.github/CODEOWNERS) requests reviews by path automatically. Authors do not approve their own PRs; if the author is one of the required reviewers, agree on an alternative reviewer on the PR before merging.

### Security

Report security vulnerabilities privately, not in a public Issue. See [SECURITY.md](SECURITY.md).
