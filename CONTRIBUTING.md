<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# OPENTRIX

> **Ngôn ngữ / Language:** [Tiếng Việt](#vi) · [English](#en)

---

<a id="vi"></a>

## OPENTRIX — Đóng góp

OPENTRIX nhận đóng góp cho nền tảng DX-OS Open-Core theo giấy phép Apache-2.0 trong repository này. Quyền sử dụng, sửa đổi và phân phối mã nguồn của bạn đến từ [Apache License 2.0](LICENSE), không đến từ bất kỳ dịch vụ hay thỏa thuận nào.

### Trước khi gửi

- Đọc [README](README.md), tài liệu kiến trúc và API trong [`docs/`](docs/), và các Issue đang mở.
- Mở Issue trước khi viết thay đổi lớn nếu thay đổi hợp đồng API công khai, ranh giới giữa core và ứng dụng, phân quyền hay cách lưu trữ dữ liệu.
- Chỉ dùng mã nguồn, dữ liệu và tài sản mà bạn có quyền đóng góp. Không đưa mật khẩu, token, file `.env` thật, dữ liệu người dùng thật, câu trả lời khảo sát gốc hay hình ảnh chưa được phép vào Issue, pull request, test hay ảnh chụp màn hình. Hãy dùng dữ liệu mẫu tự dựng và giá trị giả trong `.env.example`.
- Khi gửi đóng góp để đưa vào, bạn đồng ý với điều khoản đóng góp tại mục 5 của [Apache License 2.0](LICENSE). Đảm bảo chủ lao động hoặc chủ thể quyền khác cho phép. Repository này không yêu cầu thỏa thuận cấp phép đóng góp riêng.

### License header và pin image

- Mọi file nguồn do con người viết — Java, TypeScript/TSX, SQL, YAML, shell, Markdown — phải mang header SPDX Apache-2.0:

  ```java
  // SPDX-FileCopyrightText: 2026 TRICORE contributors
  // SPDX-License-Identifier: Apache-2.0
  ```

  Dùng `--` cho SQL, `#` cho YAML và shell, `<!-- -->` cho Markdown. Tự kiểm tra trước khi gửi:

  ```
  reuse lint
  ```

  Kiểm tra REUSE trong CI hiện mới ở mức cảnh báo cho đến khi việc cưỡng chế được thống nhất. Không gắn header chung cho mã bên ngoài hoặc chưa xác minh quyền.
- Container image trong `docker-compose*.yml` và CI phải pin tag cụ thể, không dùng `latest`. Khi giữ một phiên bản cũ vì lý do giấy phép, chỉ nâng cấp sau khi thảo luận và cập nhật [NOTICE](NOTICE).

### Chính sách Dependency và Bản quyền bên thứ ba

- **Giấy phép được phép:** Apache-2.0, MIT, BSD-2-Clause, BSD-3-Clause, ISC, 0BSD, PostgreSQL, Unlicense, CC0-1.0.
- **Giấy phép được phép kèm ghi chú NOTICE:** MPL-2.0, EPL-2.0 (không sửa mã nguồn gốc, không liên kết tĩnh).
- **Cấm đưa vào mã nguồn OPENTRIX:** GPL, AGPL, LGPL, SSPL, RSAL, BUSL, "Commons Clause", hoặc không rõ bản quyền. Ngoại lệ duy nhất là service chạy tách biệt qua mạng, dùng nguyên bản và đã công bố trong NOTICE.
- **Không sao chép từ dự án khác:** OPENTRIX chỉ kế thừa các mẫu thiết kế (design pattern) độc lập, không sao chép code, template, icon hay asset.

### Quy trình làm việc

```text
Issue → nhánh từ main → Draft PR vào main → CI → review độc lập → squash merge → đóng Issue → xóa nhánh
```

- **Issue:** việc trên khoảng hai giờ cần một Issue có mục tiêu, tiêu chí nghiệm thu, người phụ trách, milestone và label `area:*`. Tiêu đề dạng `[Area] Mô tả ngắn`; số Issue do GitHub cấp là mã định danh duy nhất.
- **Nhánh:** tạo từ `main` mới nhất, đặt tên `<type>/<area>-<mô-tả>` (ví dụ `feat/workflow-outbox-event`), sống không quá ba ngày. Không push thẳng vào `main` hoặc `gh-pages`; không tạo nhánh `review/*`, `candidate/*`, `diagnostic/*`.
- **Commit và tiêu đề PR:** theo [Conventional Commits](https://www.conventionalcommits.org/) — `<type>(<area>): <mô tả ngắn>`, với type là `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci` hoặc `build`.

### Phân công và review

| Phạm vi | Người phụ trách | Review |
| --- | --- | --- |
| Tích hợp Core, điều phối phát hành và merge | Yến (@phanyen06ym-ien) | Bảo |
| Kiểm thử Core, quản trị repository, hạ tầng | Bảo (@lexuanbao258-collab) | Yến |
| Ứng dụng IT Helpdesk và Portal BFF | Ánh (@ngang02012007-crypto) | Bảo |
| Đường dẫn Core liên quan Helpdesk và API của BFF | — | Cả Bảo và Ánh |

[CODEOWNERS](.github/CODEOWNERS) tự động yêu cầu review theo đường dẫn nhưng không bảo đảm mọi người được liệt kê đều đã duyệt. Tác giả không được tự duyệt PR của mình; nếu tác giả là một trong hai reviewer bắt buộc, ghi rõ trên PR và thống nhất reviewer thay thế trước khi merge.

### Pull request

1. Giữ thay đổi gọn theo phạm vi (khoảng 400 dòng), giải thích hành vi người dùng thấy được và ảnh hưởng tương thích. Dùng PR template; `Refs #N` khi PR làm một phần Issue, `Closes #N` khi đáp ứng đủ tiêu chí nghiệm thu.
2. Giữ ranh giới giữa core headless và ứng dụng. Ứng dụng chỉ gọi core qua API đã công bố; không tin tenant hay danh tính do client chưa xác thực gửi lên.
3. Với thay đổi hợp đồng API hoặc sự kiện, cập nhật hợp đồng và cả hai phía tiêu thụ cùng lúc; mô tả năng lực mới hoặc bị gỡ mà không trình bày công việc đề xuất như đã phát hành.
4. Chạy các kiểm tra phù hợp với module đã sửa và ghi lệnh cùng kết quả vào PR. Với thay đổi về phân quyền hay bảo mật, kèm test thể hiện cả đường bị từ chối và đường được phép.
5. Cập nhật README, tài liệu API hoặc `CHANGELOG.md` khi hành vi bên ngoài thay đổi, và nêu rõ kiểm tra nào bạn chưa chạy được.
6. Cần ít nhất một phê duyệt độc lập và CI liên quan đạt trước khi squash merge. CI đạt chưa có nghĩa là xong: Issue chỉ được đóng khi tiêu chí nghiệm thu đã được xác minh trên `main`.
7. PR mới luôn nhắm vào `main`. Các PR xếp chồng cũ được xử lý theo thứ tự phụ thuộc trong [Issue #171](https://github.com/tricore-opentrix/opentrix/issues/171); không âm thầm đổi base của chúng.

Báo cáo vấn đề bảo mật qua kênh riêng, không đăng Issue công khai; xem [SECURITY.md](SECURITY.md). Câu hỏi về nguồn gốc mã và giấy phép còn mở được theo dõi tại [Issue #138](https://github.com/tricore-opentrix/opentrix/issues/138).

---

<a id="en"></a>

## OPENTRIX — Contributing

OPENTRIX accepts contributions to the Apache-2.0 DX-OS Open-Core platform in this repository. Your rights to use, modify, and distribute the code come from the [Apache License 2.0](LICENSE), not from any service or agreement.

### Before submitting

- Read the [README](README.md), the architecture and API documents in [`docs/`](docs/), and open Issues.
- Open an Issue before writing a large patch that changes public API contracts, the core/application boundary, authorization, or data storage.
- Use code, data, and assets you have permission to contribute. Never include passwords, tokens, real `.env` files, real user data, raw survey responses, or unapproved images in Issues, pull requests, tests, or screenshots. Use invented fixtures and placeholder values in `.env.example`.
- By submitting a contribution for inclusion, you agree to the contribution terms in section 5 of the [Apache License 2.0](LICENSE). Ensure your employer or other rights holders authorize it. No separate contributor license agreement is required by this repository.

### License headers and image pins

- Every human-authored source file — Java, TypeScript/TSX, SQL, YAML, shell, Markdown — must carry the SPDX Apache-2.0 header:

  ```java
  // SPDX-FileCopyrightText: 2026 TRICORE contributors
  // SPDX-License-Identifier: Apache-2.0
  ```

  Use `--` for SQL, `#` for YAML and shell, and `<!-- -->` for Markdown. Check locally before submitting:

  ```
  reuse lint
  ```

  The REUSE check in CI is currently advisory until enforcement has been agreed. Do not apply the generic header to external or rights-unverified material.
- Container images in `docker-compose*.yml` and CI must pin specific tags, never `latest`. When an older version is kept for licensing reasons, upgrade only after discussion and update [NOTICE](NOTICE).

### Dependency policy & third-party licensing

- **Allowed licenses:** Apache-2.0, MIT, BSD-2-Clause, BSD-3-Clause, ISC, 0BSD, PostgreSQL, Unlicense, CC0-1.0.
- **Allowed with NOTICE disclosure:** MPL-2.0, EPL-2.0 (unmodified, not statically linked).
- **Not allowed in OPENTRIX source:** GPL, AGPL, LGPL, SSPL, RSAL, BUSL, "Commons Clause", or unknown licenses. The only exception is an unmodified, network-separated service disclosed in NOTICE.
- **No copying from other projects:** OPENTRIX reuses independent design patterns only, never code, templates, icons, or assets.

### Workflow

```text
Issue → branch from main → Draft PR to main → CI → independent review → squash merge → close Issue → delete branch
```

- **Issues:** work taking over about two hours needs one Issue with a goal, acceptance criteria, owner, milestone, and an `area:*` label. Use titles like `[Area] Short description`; the GitHub Issue number is the only identifier.
- **Branches:** create from an up-to-date `main`, name them `<type>/<area>-<description>` (for example `feat/workflow-outbox-event`), and keep them open no longer than three days. Do not push directly to `main` or `gh-pages`; do not create `review/*`, `candidate/*`, or `diagnostic/*` branches.
- **Commits and PR titles:** follow [Conventional Commits](https://www.conventionalcommits.org/) — `<type>(<area>): <short description>`, where type is `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`, or `build`.

### Ownership and review

| Scope | Owner | Review |
| --- | --- | --- |
| Core integration, release and merge coordination | Yến (@phanyen06ym-ien) | Bảo |
| Core testing, repository administration, infrastructure | Bảo (@lexuanbao258-collab) | Yến |
| IT Helpdesk application and Portal BFF | Ánh (@ngang02012007-crypto) | Bảo |
| Helpdesk-related Core paths and BFF API | — | Both Bảo and Ánh |

[CODEOWNERS](.github/CODEOWNERS) requests reviews by path but does not guarantee that every listed owner has approved. Authors cannot approve their own PRs; if the author is one of the two required reviewers, record it on the PR and agree on an alternative reviewer before merging.

### Pull requests

1. Keep changes scoped (around 400 lines) and explain the user-visible behavior and any compatibility impact. Use the PR template; write `Refs #N` for partial work and `Closes #N` only when the full acceptance criteria are met.
2. Preserve the boundary between the headless core and applications. Applications call the core only through its published API; never trust a tenant or identity supplied by an unauthenticated client.
3. Update API or event contracts and both consumers together; document new or removed capabilities without describing proposed work as shipped.
4. Run the checks appropriate to the touched modules and record the commands and results in the PR. For authorization or security changes, include tests demonstrating both the denied and allowed paths.
5. Update the README, API documentation, or `CHANGELOG.md` when external behavior changes, and describe any check you could not run.
6. At least one independent approval and passing relevant CI are required before squash merge. Passing CI is not completion: close the Issue only after its acceptance criteria are verified on `main`.
7. New PRs always target `main`. Legacy stacked PRs are resolved in dependency order under [Issue #171](https://github.com/tricore-opentrix/opentrix/issues/171); do not silently retarget them.

Report security problems privately, not in a public Issue; see [SECURITY.md](SECURITY.md). Open source-origin and licensing questions are tracked in [Issue #138](https://github.com/tricore-opentrix/opentrix/issues/138).
