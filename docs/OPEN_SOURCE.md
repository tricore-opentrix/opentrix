<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# Open Source and Licensing

> **Language / Ngôn ngữ:** [English](#en) · [Tiếng Việt](#vi)

---

<a id="en"></a>

## Overview

OpenTrix is open source software licensed under the [Apache License 2.0](https://github.com/tricore-opentrix/opentrix/blob/main/LICENSE) (`Apache-2.0`). This document explains how the project handles licensing, contribution rights, third-party components and releases.

| File | Purpose |
| --- | --- |
| [LICENSE](https://github.com/tricore-opentrix/opentrix/blob/main/LICENSE) | Full text of the Apache License 2.0 |
| [LICENSES/Apache-2.0.txt](https://github.com/tricore-opentrix/opentrix/blob/main/LICENSES/Apache-2.0.txt) | License text referenced by the per-file SPDX headers (REUSE layout) |
| [NOTICE](https://github.com/tricore-opentrix/opentrix/blob/main/NOTICE) | Project attribution and the third-party services used by the local deployment |
| [THIRD-PARTY-NOTICES.md](https://github.com/tricore-opentrix/opentrix/blob/main/THIRD-PARTY-NOTICES.md) | Inventory of third-party packages and container images, with their licenses |
| [REUSE.toml](https://github.com/tricore-opentrix/opentrix/blob/main/REUSE.toml) | License information for files that cannot carry an inline header |

### Contribution rights

- Contributions are accepted under the Apache License 2.0, as described in section 5 of the license and in [CONTRIBUTING.md](https://github.com/tricore-opentrix/opentrix/blob/main/CONTRIBUTING.md). No separate CLA or DCO sign-off is required.
- Each contributor licenses only the work they have the right to license. Third-party code, assets, tools and container images keep their own licenses.
- Do not add code, icons, templates, images or other assets without the right to use them. Possible overlap with external material under another license is reported and investigated as described in [CONTRIBUTING.md](https://github.com/tricore-opentrix/opentrix/blob/main/CONTRIBUTING.md).
- The Apache License does not grant permission to use the OpenTrix name or logo, except as required to describe the origin of the software.

### AI-assisted development

The maintainers have disclosed that AI tools, including ChatGPT, Codex, Claude and Claude Code, were used for design, code, tests and documentation, to a different extent for each contributor. The disclosure and its limitations are recorded in [Issue #138](https://github.com/tricore-opentrix/opentrix/issues/138):

1. Complete records of historical AI prompts are not available.
2. Contributors did not intentionally copy external source code or give external code to an AI tool to copy. This describes their own actions; it is not a verification that generated output is independent of external sources.
3. A file-by-file comparison against external sources has not been completed. It is tracked for v1.0.0 in [Issue #255](https://github.com/tricore-opentrix/opentrix/issues/255).

New pull requests disclose AI assistance as required by [CONTRIBUTING.md](https://github.com/tricore-opentrix/opentrix/blob/main/CONTRIBUTING.md).

### SPDX and REUSE

- Every file carries an SPDX header with its copyright and license, following the [REUSE specification](https://reuse.software/spec/). Java and TypeScript use `//` comments, SQL uses `--`, YAML and shell scripts use `#`, and Markdown uses an HTML comment.
- Files that must keep their exact bytes, such as approved database migrations and lock files, are declared in [REUSE.toml](https://github.com/tricore-opentrix/opentrix/blob/main/REUSE.toml) instead.
- The `repo-hygiene` CI job runs `reuse lint` on every pull request. The TRICORE header is never applied to third-party material.

### Dependencies and SBOM

- Dependencies are declared in [backend/build.gradle](https://github.com/tricore-opentrix/opentrix/blob/main/backend/build.gradle), [portal-bff/build.gradle](https://github.com/tricore-opentrix/opentrix/blob/main/portal-bff/build.gradle) and [frontend/package.json](https://github.com/tricore-opentrix/opentrix/blob/main/frontend/package.json). Third-party code is not copied into the repository.
- On every pull request, the `r23-compliance` CI job generates CycloneDX SBOMs for the backend, Portal BFF and frontend, checks each dependency license against the allow-list in [CONTRIBUTING.md](https://github.com/tricore-opentrix/opentrix/blob/main/CONTRIBUTING.md), regenerates [THIRD-PARTY-NOTICES.md](https://github.com/tricore-opentrix/opentrix/blob/main/THIRD-PARTY-NOTICES.md) and fails if the committed file differs.
- The script is [scripts/r23-compliance.py](https://github.com/tricore-opentrix/opentrix/blob/main/scripts/r23-compliance.py). An unlisted or undeclared license fails the job.

### Third-party services

The local deployment runs the following upstream components unmodified. They are not part of the OpenTrix source code and keep their own licenses; versions and license links are listed in [THIRD-PARTY-NOTICES.md](https://github.com/tricore-opentrix/opentrix/blob/main/THIRD-PARTY-NOTICES.md).

| Component | Role | License |
| --- | --- | --- |
| [Keycloak](https://github.com/keycloak/keycloak) | Identity provider | [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) |
| [PostgreSQL](https://www.postgresql.org/) | Database | [PostgreSQL License](https://spdx.org/licenses/PostgreSQL.html) |
| [Apache APISIX](https://github.com/apache/apisix) | API gateway (optional) | [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) |
| [Caddy](https://github.com/caddyserver/caddy) | HTTPS ingress serving the Portal | [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) |

### Binary and byte-preserved files

| File | Handling |
| --- | --- |
| `backend/gradle/wrapper/gradle-wrapper.jar` | Upstream Gradle Wrapper (Apache-2.0, declared in `REUSE.toml`), checked by Gradle wrapper validation in CI and excluded from source archives |
| Flyway migrations V1–V4 and Helpdesk SQL resources | License declared in `REUSE.toml` so the files keep their verified checksums |
| `package-lock.json`, `favicon.svg`, `.gitignore` and similar files | License declared in `REUSE.toml` where the format does not allow a header |

### Releases

- [v0.2.0](https://github.com/tricore-opentrix/opentrix/releases/tag/v0.2.0) (2026-11-17) is a **source-only** release. It does not include prebuilt JARs, the built frontend or container images.
- Each release provides `dxos-open-core-<version>.tar.gz` and a `SHA256SUMS` file. The archive contains the source code, `LICENSE`, `NOTICE`, `THIRD-PARTY-NOTICES.md`, `CHANGELOG.md`, release notes, the CycloneDX SBOMs, the license inventory and a `MANIFEST.json` with the SHA-256 of every file.
- The release process is described in [docs/RELEASE.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/RELEASE.md).

### Limitations

This document describes the project's licensing policy and practices. It is not legal advice and does not certify the ownership of every file in the repository.

---

<a id="vi"></a>

## Tổng quan

OpenTrix là phần mềm nguồn mở theo [Giấy phép Apache 2.0](https://github.com/tricore-opentrix/opentrix/blob/main/LICENSE) (`Apache-2.0`). Tài liệu này mô tả cách dự án quản lý giấy phép, quyền đóng góp, thành phần bên thứ ba và bản phát hành.

| Tệp | Mục đích |
| --- | --- |
| [LICENSE](https://github.com/tricore-opentrix/opentrix/blob/main/LICENSE) | Toàn văn Giấy phép Apache 2.0 |
| [LICENSES/Apache-2.0.txt](https://github.com/tricore-opentrix/opentrix/blob/main/LICENSES/Apache-2.0.txt) | Văn bản giấy phép được header SPDX của từng tệp tham chiếu (theo cấu trúc REUSE) |
| [NOTICE](https://github.com/tricore-opentrix/opentrix/blob/main/NOTICE) | Ghi công dự án và các dịch vụ bên thứ ba dùng khi triển khai cục bộ |
| [THIRD-PARTY-NOTICES.md](https://github.com/tricore-opentrix/opentrix/blob/main/THIRD-PARTY-NOTICES.md) | Danh mục gói và image container bên thứ ba, kèm giấy phép |
| [REUSE.toml](https://github.com/tricore-opentrix/opentrix/blob/main/REUSE.toml) | Thông tin giấy phép cho các tệp không thể chèn header |

### Quyền đóng góp

- Đóng góp được tiếp nhận theo Giấy phép Apache 2.0, như mục 5 của giấy phép và [CONTRIBUTING.md](https://github.com/tricore-opentrix/opentrix/blob/main/CONTRIBUTING.md) quy định. Dự án không yêu cầu CLA hay ký DCO riêng.
- Mỗi người đóng góp chỉ cấp phép phần công việc mà mình có quyền cấp phép. Mã, tài sản, công cụ và image container của bên thứ ba giữ nguyên giấy phép của chúng.
- Không đưa vào mã, biểu tượng, mẫu, hình ảnh hay tài sản khác khi không có quyền sử dụng. Khả năng trùng với nội dung bên ngoài có giấy phép khác được báo cáo và xác minh theo [CONTRIBUTING.md](https://github.com/tricore-opentrix/opentrix/blob/main/CONTRIBUTING.md).
- Giấy phép Apache không cho phép dùng tên hay logo OpenTrix, trừ khi cần để mô tả nguồn gốc phần mềm.

### Phát triển có hỗ trợ AI

Các maintainer đã công khai việc dùng công cụ AI, gồm ChatGPT, Codex, Claude và Claude Code, cho thiết kế, mã, kiểm thử và tài liệu, với mức độ khác nhau ở từng người. Nội dung công khai và các giới hạn được ghi tại [Issue #138](https://github.com/tricore-opentrix/opentrix/issues/138):

1. Không có hồ sơ đầy đủ các prompt AI trước đây.
2. Người đóng góp không cố ý sao chép mã nguồn bên ngoài hay đưa mã bên ngoài cho công cụ AI sao chép. Đây là mô tả hành vi của chính họ, không phải xác minh rằng nội dung do AI sinh ra độc lập với nguồn bên ngoài.
3. Chưa đối chiếu từng tệp với nguồn bên ngoài. Việc này được theo dõi cho v1.0.0 tại [Issue #255](https://github.com/tricore-opentrix/opentrix/issues/255).

Pull request mới công khai việc dùng AI theo yêu cầu của [CONTRIBUTING.md](https://github.com/tricore-opentrix/opentrix/blob/main/CONTRIBUTING.md).

### SPDX và REUSE

- Mỗi tệp có header SPDX ghi bản quyền và giấy phép, theo [đặc tả REUSE](https://reuse.software/spec/). Java và TypeScript dùng comment `//`, SQL dùng `--`, YAML và shell script dùng `#`, Markdown dùng comment HTML.
- Các tệp phải giữ nguyên từng byte, như migration cơ sở dữ liệu đã duyệt và tệp lock, được khai báo trong [REUSE.toml](https://github.com/tricore-opentrix/opentrix/blob/main/REUSE.toml).
- Job CI `repo-hygiene` chạy `reuse lint` ở mỗi pull request. Header TRICORE không bao giờ được gắn lên nội dung của bên thứ ba.

### Phụ thuộc và SBOM

- Phụ thuộc được khai báo trong [backend/build.gradle](https://github.com/tricore-opentrix/opentrix/blob/main/backend/build.gradle), [portal-bff/build.gradle](https://github.com/tricore-opentrix/opentrix/blob/main/portal-bff/build.gradle) và [frontend/package.json](https://github.com/tricore-opentrix/opentrix/blob/main/frontend/package.json). Mã bên thứ ba không được sao chép vào kho mã.
- Ở mỗi pull request, job CI `r23-compliance` sinh SBOM CycloneDX cho backend, Portal BFF và frontend, kiểm tra giấy phép của từng phụ thuộc theo danh sách cho phép trong [CONTRIBUTING.md](https://github.com/tricore-opentrix/opentrix/blob/main/CONTRIBUTING.md), sinh lại [THIRD-PARTY-NOTICES.md](https://github.com/tricore-opentrix/opentrix/blob/main/THIRD-PARTY-NOTICES.md) và báo lỗi nếu tệp trong kho mã khác tệp sinh ra.
- Script thực hiện là [scripts/r23-compliance.py](https://github.com/tricore-opentrix/opentrix/blob/main/scripts/r23-compliance.py). Giấy phép không có trong danh sách hoặc không được khai báo sẽ làm job thất bại.

### Dịch vụ bên thứ ba

Triển khai cục bộ chạy nguyên bản các thành phần upstream dưới đây. Chúng không thuộc mã nguồn OpenTrix và giữ giấy phép riêng; phiên bản và liên kết giấy phép xem trong [THIRD-PARTY-NOTICES.md](https://github.com/tricore-opentrix/opentrix/blob/main/THIRD-PARTY-NOTICES.md).

| Thành phần | Vai trò | Giấy phép |
| --- | --- | --- |
| [Keycloak](https://github.com/keycloak/keycloak) | Quản lý định danh | [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) |
| [PostgreSQL](https://www.postgresql.org/) | Cơ sở dữ liệu | [PostgreSQL License](https://spdx.org/licenses/PostgreSQL.html) |
| [Apache APISIX](https://github.com/apache/apisix) | Cổng API (tùy chọn) | [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) |
| [Caddy](https://github.com/caddyserver/caddy) | Ingress HTTPS phục vụ Portal | [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) |

### Tệp nhị phân và tệp giữ nguyên byte

| Tệp | Cách xử lý |
| --- | --- |
| `backend/gradle/wrapper/gradle-wrapper.jar` | Gradle Wrapper gốc (Apache-2.0, khai báo trong `REUSE.toml`), được CI kiểm tra bằng Gradle wrapper validation và loại khỏi gói mã nguồn |
| Migration Flyway V1–V4 và tệp SQL của Helpdesk | Giấy phép khai báo trong `REUSE.toml` để tệp giữ nguyên checksum đã xác minh |
| `package-lock.json`, `favicon.svg`, `.gitignore` và các tệp tương tự | Giấy phép khai báo trong `REUSE.toml` khi định dạng không cho phép chèn header |

### Bản phát hành

- [v0.2.0](https://github.com/tricore-opentrix/opentrix/releases/tag/v0.2.0) (2026-11-17) là bản phát hành **chỉ gồm mã nguồn**. Bản này không kèm JAR dựng sẵn, frontend đã build hay image container.
- Mỗi bản phát hành có tệp `dxos-open-core-<version>.tar.gz` và `SHA256SUMS`. Gói chứa mã nguồn, `LICENSE`, `NOTICE`, `THIRD-PARTY-NOTICES.md`, `CHANGELOG.md`, ghi chú phát hành, các SBOM CycloneDX, danh mục giấy phép và `MANIFEST.json` ghi SHA-256 của từng tệp.
- Quy trình phát hành được mô tả trong [docs/RELEASE.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/RELEASE.md).

### Giới hạn

Tài liệu này mô tả chính sách và cách làm về giấy phép của dự án. Đây không phải tư vấn pháp lý và không xác nhận quyền sở hữu của từng tệp trong kho mã.
