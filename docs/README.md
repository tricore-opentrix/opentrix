<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors

SPDX-License-Identifier: Apache-2.0
-->

# OpenTrix documentation

> **Ngôn ngữ / Language:** [Tiếng Việt](#tài-liệu-opentrix--tiếng-việt) · [English](#opentrix-documentation--english)

---

## Tài liệu OpenTrix — Tiếng Việt

[README dự án](../README.md) · [Phát triển cục bộ](DEVELOPMENT.md)

Bắt đầu từ tài liệu đúng với việc bạn cần làm.

### Lộ trình đọc cho người mới

1. Đọc [tổng quan dự án và sơ đồ kho mã](../README.md).
2. Chạy thử toàn bộ hệ thống theo [hướng dẫn chạy thử](../infra/demo/README.md).
3. Làm theo [phát triển cục bộ](DEVELOPMENT.md) để build và chạy từng phần.
4. Đọc [kiến trúc](ARCHITECTURE.md) để hiểu ranh giới giữa lõi và ứng dụng.
5. Đọc hướng dẫn của phần mã bạn sẽ sửa:
   - [Backend](../backend/README.md): lõi Identity, Workflow, Data và ứng dụng Helpdesk.
   - [Portal BFF](../portal-bff/README.md): đăng nhập OIDC, phiên, CSRF.
   - [Frontend](../frontend/README.md): Portal React, chế độ MOCK và integration-local.
6. Xem [giấy phép và nguồn mở](OPEN_SOURCE.md) trước khi đóng góp.

### Tài liệu theo việc

| Tôi muốn...                                         | Đọc                                                  |
| --------------------------------------------------- | ---------------------------------------------------- |
| Chạy thử toàn bộ hệ thống bằng một lệnh             | [infra/demo/README.md](../infra/demo/README.md)      |
| Cài môi trường, build và chạy từng phần             | [DEVELOPMENT.md](DEVELOPMENT.md)                     |
| Hiểu kiến trúc, ranh giới lõi và ứng dụng           | [ARCHITECTURE.md](ARCHITECTURE.md)                   |
| Gọi API, xác thực, phân quyền, mã lỗi               | [API.md](API.md)                                     |
| Xây ứng dụng mới trên lõi OpenTrix                  | [INTEGRATION.md](INTEGRATION.md)                     |
| Chạy test, hiểu các lớp kiểm thử và CI              | [TESTING.md](TESTING.md)                             |
| Triển khai, cấu hình, migration, health check       | [DEPLOYMENT.md](DEPLOYMENT.md)                       |
| Gắn phiên bản và đóng gói bản phát hành             | [RELEASE.md](RELEASE.md)                             |
| Kiểm tra giấy phép, SPDX/REUSE, thư viện bên thứ ba | [OPEN_SOURCE.md](OPEN_SOURCE.md)                     |
| Biết vì sao chọn một công nghệ                      | [Quyết định kiến trúc (ADR)](08-decisions/README.md) |
| Tra thuật ngữ                                       | [GLOSSARY.md](../GLOSSARY.md)                        |

### Quyết định kiến trúc

| ADR                                                          | Quyết định                                                         |
| ------------------------------------------------------------ | ------------------------------------------------------------------ |
| [ADR-009](08-decisions/ADR-009-modular-monolith-flowable.md) | Modular monolith, workflow BPMN bằng Flowable nhúng                |
| [ADR-016](08-decisions/ADR-016-s3-compatible-storage.md)     | Lưu tệp qua API tương thích S3; mỗi mô-đun sở hữu dữ liệu của mình |
| [ADR-017](08-decisions/ADR-017-helpdesk-first-scope.md)      | IT Helpdesk là ứng dụng đầu tiên                                   |
| [ADR-018](08-decisions/ADR-018-apisix-api-gateway.md)        | Apache APISIX làm cổng API                                         |
| [ADR-008](08-decisions/ADR-008-dashboard-tool.md)            | Apache Superset cho bảng phân tích                                 |
| [ADR-007](08-decisions/ADR-007-data-storage.md)              | Lưu tệp bằng MinIO (đã thay bằng ADR-016)                          |

### Tệp ở thư mục gốc

| Tệp                                                 | Nội dung                                 |
| --------------------------------------------------- | ---------------------------------------- |
| [README.md](../README.md)                           | Giới thiệu dự án, phạm vi, cách chạy thử |
| [LICENSE](../LICENSE)                               | Toàn văn Apache License 2.0              |
| [NOTICE](../NOTICE)                                 | Thông báo bản quyền                      |
| [THIRD-PARTY-NOTICES.md](../THIRD-PARTY-NOTICES.md) | Thư viện bên thứ ba và giấy phép         |
| [CHANGELOG.md](../CHANGELOG.md)                     | Thay đổi theo phiên bản                  |
| [CONTRIBUTING.md](../CONTRIBUTING.md)               | Quy trình đóng góp, header SPDX          |
| [GOVERNANCE.md](../GOVERNANCE.md)                   | Vai trò maintainer, cách ra quyết định   |
| [SECURITY.md](../SECURITY.md)                       | Báo cáo lỗ hổng bảo mật                  |

### Quy ước viết tài liệu

- Song ngữ: tiếng Việt trước, tiếng Anh sau, cùng mục và cùng bảng.
- Mô tả hành vi hiện có của mã nguồn; tính năng chưa làm ghi ở mục "Chưa cung cấp" hoặc lộ trình, kèm liên kết Issue.
- Không ghi tên người phụ trách, trạng thái review, số PR hay mã công việc nội bộ trong tài liệu; các thông tin đó nằm ở Issue và pull request.
- Tệp mới có header SPDX theo [CONTRIBUTING.md](../CONTRIBUTING.md).

---

## OpenTrix documentation — English

[Project README](../README.md) · [Local development](DEVELOPMENT.md)

Start from the guide that matches what you need to do.

### Reading path for newcomers

1. Read the [project overview and repository map](../README.md).
2. Run the whole system with the [trial run guide](../infra/demo/README.md).
3. Follow [local development](DEVELOPMENT.md) to build and run each part.
4. Read the [architecture](ARCHITECTURE.md) to understand the core/application boundary.
5. Read the guide for the code you will change:
   - [Backend](../backend/README.md): Identity, Workflow and Data core plus the Helpdesk application.
   - [Portal BFF](../portal-bff/README.md): OIDC login, session, CSRF.
   - [Frontend](../frontend/README.md): React Portal, MOCK and integration-local modes.
6. Review [licensing and open source](OPEN_SOURCE.md) before contributing.

### Guides by task

| I want to...                                              | Read                                                   |
| --------------------------------------------------------- | ------------------------------------------------------ |
| Run the whole system with one command                     | [infra/demo/README.md](../infra/demo/README.md)        |
| Set up, build and run each part                           | [DEVELOPMENT.md](DEVELOPMENT.md)                       |
| Understand the architecture and core/application boundary | [ARCHITECTURE.md](ARCHITECTURE.md)                     |
| Call the API, authenticate, authorize, handle errors      | [API.md](API.md)                                       |
| Build a new application on the OpenTrix core              | [INTEGRATION.md](INTEGRATION.md)                       |
| Run tests and understand test layers and CI               | [TESTING.md](TESTING.md)                               |
| Deploy, configure, migrate, check health                  | [DEPLOYMENT.md](DEPLOYMENT.md)                         |
| Version and package a release                             | [RELEASE.md](RELEASE.md)                               |
| Check licensing, SPDX/REUSE and third-party libraries     | [OPEN_SOURCE.md](OPEN_SOURCE.md)                       |
| Learn why a technology was chosen                         | [Architecture decisions (ADR)](08-decisions/README.md) |
| Look up a term                                            | [GLOSSARY.md](../GLOSSARY.md)                          |

### Architecture decisions

| ADR                                                          | Decision                                                             |
| ------------------------------------------------------------ | -------------------------------------------------------------------- |
| [ADR-009](08-decisions/ADR-009-modular-monolith-flowable.md) | Modular monolith with embedded Flowable for BPMN workflow            |
| [ADR-016](08-decisions/ADR-016-s3-compatible-storage.md)     | File storage through an S3-compatible API; each module owns its data |
| [ADR-017](08-decisions/ADR-017-helpdesk-first-scope.md)      | IT Helpdesk as the first application                                 |
| [ADR-018](08-decisions/ADR-018-apisix-api-gateway.md)        | Apache APISIX as the API gateway                                     |
| [ADR-008](08-decisions/ADR-008-dashboard-tool.md)            | Apache Superset for analytics dashboards                             |
| [ADR-007](08-decisions/ADR-007-data-storage.md)              | MinIO file storage (superseded by ADR-016)                           |

### Root files

| File                                                | Content                                |
| --------------------------------------------------- | -------------------------------------- |
| [README.md](../README.md)                           | Project introduction, scope, trial run |
| [LICENSE](../LICENSE)                               | Full Apache License 2.0 text           |
| [NOTICE](../NOTICE)                                 | Copyright notice                       |
| [THIRD-PARTY-NOTICES.md](../THIRD-PARTY-NOTICES.md) | Third-party libraries and licenses     |
| [CHANGELOG.md](../CHANGELOG.md)                     | Changes by version                     |
| [CONTRIBUTING.md](../CONTRIBUTING.md)               | Contribution workflow, SPDX headers    |
| [GOVERNANCE.md](../GOVERNANCE.md)                   | Maintainer roles, decision-making      |
| [SECURITY.md](../SECURITY.md)                       | Reporting security vulnerabilities     |

### Documentation conventions

- Bilingual: Vietnamese first, English second, with matching sections and tables.
- Describe what the source code does today; unbuilt features go under "Not provided yet" or the roadmap, with an Issue link.
- Do not put owner names, review status, PR numbers or internal task codes in documents; those belong in Issues and pull requests.
- New files carry an SPDX header as described in [CONTRIBUTING.md](../CONTRIBUTING.md).
