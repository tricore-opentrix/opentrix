<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# OpenTrix Documentation

> **Language / Ngôn ngữ:** [English](#en) · [Tiếng Việt](#vi)

---

<a id="en"></a>

## Overview

[Project README](https://github.com/tricore-opentrix/opentrix/blob/main/README.md) · [Local development](https://github.com/tricore-opentrix/opentrix/blob/main/docs/DEVELOPMENT.md)

Start from the guide that matches what you need to do.

### Reading path for newcomers

1. Read the [project overview and repository map](https://github.com/tricore-opentrix/opentrix/blob/main/README.md).
2. Run the whole system with the [local deployment guide](https://github.com/tricore-opentrix/opentrix/blob/main/infra/demo/README.md).
3. Follow [local development](https://github.com/tricore-opentrix/opentrix/blob/main/docs/DEVELOPMENT.md) to build and run each part.
4. Read the [architecture](https://github.com/tricore-opentrix/opentrix/blob/main/docs/ARCHITECTURE.md) to understand the core/application boundary.
5. Read the guide for the code you will change:
   - [Backend](https://github.com/tricore-opentrix/opentrix/blob/main/backend/README.md): Identity, Workflow and Data core plus the Helpdesk application.
   - [Portal BFF](https://github.com/tricore-opentrix/opentrix/blob/main/portal-bff/README.md): OIDC login, session, CSRF.
   - [Frontend](https://github.com/tricore-opentrix/opentrix/blob/main/frontend/README.md): React Portal, MOCK and integration-local modes.
6. Review [licensing and open source](https://github.com/tricore-opentrix/opentrix/blob/main/docs/OPEN_SOURCE.md) and [CONTRIBUTING.md](https://github.com/tricore-opentrix/opentrix/blob/main/CONTRIBUTING.md) before contributing.

### Guides by task

| I want to... | Read |
| --- | --- |
| Run the whole system with one command | [infra/demo/README.md](https://github.com/tricore-opentrix/opentrix/blob/main/infra/demo/README.md) |
| Understand the infrastructure configuration | [infra/README.md](https://github.com/tricore-opentrix/opentrix/blob/main/infra/README.md) |
| Set up, build and run each part | [DEVELOPMENT.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/DEVELOPMENT.md) |
| Understand the architecture and core/application boundary | [ARCHITECTURE.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/ARCHITECTURE.md) |
| Call the API, authenticate, authorize, handle errors | [API.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/API.md) |
| Build a new application on the OpenTrix core | [INTEGRATION.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/INTEGRATION.md) |
| Run tests and understand test layers and CI | [TESTING.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/TESTING.md) |
| Find a helper script | [scripts/README.md](https://github.com/tricore-opentrix/opentrix/blob/main/scripts/README.md) |
| Deploy, configure, migrate, check health | [DEPLOYMENT.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/DEPLOYMENT.md) |
| Version and package a release | [RELEASE.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/RELEASE.md) |
| Check licensing, SPDX/REUSE and third-party libraries | [OPEN_SOURCE.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/OPEN_SOURCE.md) |
| Learn why a technology was chosen | [Architecture decisions (ADR)](https://github.com/tricore-opentrix/opentrix/blob/main/docs/08-decisions/README.md) |
| Look up a term | [GLOSSARY.md](https://github.com/tricore-opentrix/opentrix/blob/main/GLOSSARY.md) |

### Architecture decisions

| ADR | Decision |
| --- | --- |
| [ADR-009](https://github.com/tricore-opentrix/opentrix/blob/main/docs/08-decisions/ADR-009-modular-monolith-flowable.md) | Modular monolith with embedded Flowable for BPMN workflow |
| [ADR-016](https://github.com/tricore-opentrix/opentrix/blob/main/docs/08-decisions/ADR-016-s3-compatible-storage.md) | File storage through an S3-compatible API; each module owns its data |
| [ADR-017](https://github.com/tricore-opentrix/opentrix/blob/main/docs/08-decisions/ADR-017-helpdesk-first-scope.md) | IT Helpdesk as the first application |
| [ADR-018](https://github.com/tricore-opentrix/opentrix/blob/main/docs/08-decisions/ADR-018-apisix-api-gateway.md) | Apache APISIX as the API gateway |
| [ADR-008](https://github.com/tricore-opentrix/opentrix/blob/main/docs/08-decisions/ADR-008-dashboard-tool.md) | Apache Superset for analytics dashboards |
| [ADR-007](https://github.com/tricore-opentrix/opentrix/blob/main/docs/08-decisions/ADR-007-data-storage.md) | MinIO file storage (superseded by ADR-016) |

### Diagrams and records

| Folder | Content |
| --- | --- |
| [`diagrams/`](https://github.com/tricore-opentrix/opentrix/tree/main/docs/diagrams) | Architecture and topology diagrams used in the documentation |
| [`00-project/`](https://github.com/tricore-opentrix/opentrix/tree/main/docs/00-project), [`01-architecture/`](https://github.com/tricore-opentrix/opentrix/tree/main/docs/01-architecture), [`02-core/`](https://github.com/tricore-opentrix/opentrix/tree/main/docs/02-core) | Early project, architecture and core design records; kept for design rationale, do not describe the current state |
| [`06-deployment/`](https://github.com/tricore-opentrix/opentrix/tree/main/docs/06-deployment) | Deployment prerequisites, and release, compliance and repository records |
| [`evidence/`](https://github.com/tricore-opentrix/opentrix/tree/main/docs/evidence), [`09-evidence/`](https://github.com/tricore-opentrix/opentrix/tree/main/docs/09-evidence), [`verification/`](https://github.com/tricore-opentrix/opentrix/tree/main/docs/verification) | Database review queries and verification records |

The guides above are the source of truth. Records are kept for reference and may describe earlier states of the project.

### Root files

| File | Content |
| --- | --- |
| [README.md](https://github.com/tricore-opentrix/opentrix/blob/main/README.md) | Project introduction, scope, running locally |
| [LICENSE](https://github.com/tricore-opentrix/opentrix/blob/main/LICENSE) | Full Apache License 2.0 text |
| [NOTICE](https://github.com/tricore-opentrix/opentrix/blob/main/NOTICE) | Copyright notice |
| [THIRD-PARTY-NOTICES.md](https://github.com/tricore-opentrix/opentrix/blob/main/THIRD-PARTY-NOTICES.md) | Third-party libraries and licenses |
| [CHANGELOG.md](https://github.com/tricore-opentrix/opentrix/blob/main/CHANGELOG.md) | Changes by version |
| [CONTRIBUTING.md](https://github.com/tricore-opentrix/opentrix/blob/main/CONTRIBUTING.md) | Contribution workflow, SPDX headers |
| [GOVERNANCE.md](https://github.com/tricore-opentrix/opentrix/blob/main/GOVERNANCE.md) | Maintainer roles, decision-making |
| [SECURITY.md](https://github.com/tricore-opentrix/opentrix/blob/main/SECURITY.md) | Reporting security vulnerabilities |
| [GLOSSARY.md](https://github.com/tricore-opentrix/opentrix/blob/main/GLOSSARY.md) | Project terminology |

### Documentation conventions

- Bilingual: English first, then Vietnamese, with matching sections and tables.
- Use absolute GitHub links (`https://github.com/tricore-opentrix/opentrix/blob/main/...`) so links work wherever the document is read; images use relative paths.
- Describe what the source code does today; features not yet built go under "Not provided yet" or the roadmap, with an Issue link.
- Do not put owner names, review status, PR numbers or internal task codes in documents; those belong in Issues and pull requests.
- New files carry an SPDX header as described in [CONTRIBUTING.md](https://github.com/tricore-opentrix/opentrix/blob/main/CONTRIBUTING.md).

---

<a id="vi"></a>

## Tổng quan

[README dự án](https://github.com/tricore-opentrix/opentrix/blob/main/README.md) · [Phát triển cục bộ](https://github.com/tricore-opentrix/opentrix/blob/main/docs/DEVELOPMENT.md)

Bắt đầu từ tài liệu đúng với việc bạn cần làm.

### Lộ trình đọc cho người mới

1. Đọc [tổng quan dự án và sơ đồ kho mã](https://github.com/tricore-opentrix/opentrix/blob/main/README.md).
2. Chạy thử toàn bộ hệ thống theo [hướng dẫn triển khai cục bộ](https://github.com/tricore-opentrix/opentrix/blob/main/infra/demo/README.md).
3. Làm theo [phát triển cục bộ](https://github.com/tricore-opentrix/opentrix/blob/main/docs/DEVELOPMENT.md) để build và chạy từng phần.
4. Đọc [kiến trúc](https://github.com/tricore-opentrix/opentrix/blob/main/docs/ARCHITECTURE.md) để hiểu ranh giới giữa lõi và ứng dụng.
5. Đọc hướng dẫn của phần mã bạn sẽ sửa:
   - [Backend](https://github.com/tricore-opentrix/opentrix/blob/main/backend/README.md): lõi Identity, Workflow, Data và ứng dụng Helpdesk.
   - [Portal BFF](https://github.com/tricore-opentrix/opentrix/blob/main/portal-bff/README.md): đăng nhập OIDC, phiên, CSRF.
   - [Frontend](https://github.com/tricore-opentrix/opentrix/blob/main/frontend/README.md): Portal React, chế độ MOCK và integration-local.
6. Xem [giấy phép và nguồn mở](https://github.com/tricore-opentrix/opentrix/blob/main/docs/OPEN_SOURCE.md) và [CONTRIBUTING.md](https://github.com/tricore-opentrix/opentrix/blob/main/CONTRIBUTING.md) trước khi đóng góp.

### Tài liệu theo việc

| Tôi muốn... | Đọc |
| --- | --- |
| Chạy thử toàn bộ hệ thống bằng một lệnh | [infra/demo/README.md](https://github.com/tricore-opentrix/opentrix/blob/main/infra/demo/README.md) |
| Hiểu cấu hình hạ tầng | [infra/README.md](https://github.com/tricore-opentrix/opentrix/blob/main/infra/README.md) |
| Cài môi trường, build và chạy từng phần | [DEVELOPMENT.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/DEVELOPMENT.md) |
| Hiểu kiến trúc, ranh giới lõi và ứng dụng | [ARCHITECTURE.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/ARCHITECTURE.md) |
| Gọi API, xác thực, phân quyền, mã lỗi | [API.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/API.md) |
| Xây ứng dụng mới trên lõi OpenTrix | [INTEGRATION.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/INTEGRATION.md) |
| Chạy test, hiểu các lớp kiểm thử và CI | [TESTING.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/TESTING.md) |
| Tìm script hỗ trợ | [scripts/README.md](https://github.com/tricore-opentrix/opentrix/blob/main/scripts/README.md) |
| Triển khai, cấu hình, migration, health check | [DEPLOYMENT.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/DEPLOYMENT.md) |
| Gắn phiên bản và đóng gói bản phát hành | [RELEASE.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/RELEASE.md) |
| Kiểm tra giấy phép, SPDX/REUSE, thư viện bên thứ ba | [OPEN_SOURCE.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/OPEN_SOURCE.md) |
| Biết vì sao chọn một công nghệ | [Quyết định kiến trúc (ADR)](https://github.com/tricore-opentrix/opentrix/blob/main/docs/08-decisions/README.md) |
| Tra thuật ngữ | [GLOSSARY.md](https://github.com/tricore-opentrix/opentrix/blob/main/GLOSSARY.md) |

### Quyết định kiến trúc

| ADR | Quyết định |
| --- | --- |
| [ADR-009](https://github.com/tricore-opentrix/opentrix/blob/main/docs/08-decisions/ADR-009-modular-monolith-flowable.md) | Modular monolith, workflow BPMN bằng Flowable nhúng |
| [ADR-016](https://github.com/tricore-opentrix/opentrix/blob/main/docs/08-decisions/ADR-016-s3-compatible-storage.md) | Lưu tệp qua API tương thích S3; mỗi mô-đun sở hữu dữ liệu của mình |
| [ADR-017](https://github.com/tricore-opentrix/opentrix/blob/main/docs/08-decisions/ADR-017-helpdesk-first-scope.md) | IT Helpdesk là ứng dụng đầu tiên |
| [ADR-018](https://github.com/tricore-opentrix/opentrix/blob/main/docs/08-decisions/ADR-018-apisix-api-gateway.md) | Apache APISIX làm cổng API |
| [ADR-008](https://github.com/tricore-opentrix/opentrix/blob/main/docs/08-decisions/ADR-008-dashboard-tool.md) | Apache Superset cho bảng phân tích |
| [ADR-007](https://github.com/tricore-opentrix/opentrix/blob/main/docs/08-decisions/ADR-007-data-storage.md) | Lưu tệp bằng MinIO (đã thay bằng ADR-016) |

### Sơ đồ và hồ sơ

| Thư mục | Nội dung |
| --- | --- |
| [`diagrams/`](https://github.com/tricore-opentrix/opentrix/tree/main/docs/diagrams) | Sơ đồ kiến trúc và topology dùng trong tài liệu |
| [`00-project/`](https://github.com/tricore-opentrix/opentrix/tree/main/docs/00-project), [`01-architecture/`](https://github.com/tricore-opentrix/opentrix/tree/main/docs/01-architecture), [`02-core/`](https://github.com/tricore-opentrix/opentrix/tree/main/docs/02-core) | Hồ sơ thiết kế dự án, kiến trúc và lõi ở giai đoạn đầu; giữ lại để tham khảo lý do thiết kế, không mô tả hiện trạng |
| [`06-deployment/`](https://github.com/tricore-opentrix/opentrix/tree/main/docs/06-deployment) | Điều kiện tiên quyết để triển khai, cùng hồ sơ phát hành, tuân thủ và kho mã |
| [`evidence/`](https://github.com/tricore-opentrix/opentrix/tree/main/docs/evidence), [`09-evidence/`](https://github.com/tricore-opentrix/opentrix/tree/main/docs/09-evidence), [`verification/`](https://github.com/tricore-opentrix/opentrix/tree/main/docs/verification) | Truy vấn rà soát cơ sở dữ liệu và hồ sơ kiểm chứng |

Các hướng dẫn ở trên là nguồn chuẩn. Hồ sơ được giữ để tham khảo và có thể mô tả trạng thái cũ của dự án.

### Tệp ở thư mục gốc

| Tệp | Nội dung |
| --- | --- |
| [README.md](https://github.com/tricore-opentrix/opentrix/blob/main/README.md) | Giới thiệu dự án, phạm vi, cách chạy cục bộ |
| [LICENSE](https://github.com/tricore-opentrix/opentrix/blob/main/LICENSE) | Toàn văn Apache License 2.0 |
| [NOTICE](https://github.com/tricore-opentrix/opentrix/blob/main/NOTICE) | Thông báo bản quyền |
| [THIRD-PARTY-NOTICES.md](https://github.com/tricore-opentrix/opentrix/blob/main/THIRD-PARTY-NOTICES.md) | Thư viện bên thứ ba và giấy phép |
| [CHANGELOG.md](https://github.com/tricore-opentrix/opentrix/blob/main/CHANGELOG.md) | Thay đổi theo phiên bản |
| [CONTRIBUTING.md](https://github.com/tricore-opentrix/opentrix/blob/main/CONTRIBUTING.md) | Quy trình đóng góp, header SPDX |
| [GOVERNANCE.md](https://github.com/tricore-opentrix/opentrix/blob/main/GOVERNANCE.md) | Vai trò maintainer, cách ra quyết định |
| [SECURITY.md](https://github.com/tricore-opentrix/opentrix/blob/main/SECURITY.md) | Báo cáo lỗ hổng bảo mật |
| [GLOSSARY.md](https://github.com/tricore-opentrix/opentrix/blob/main/GLOSSARY.md) | Thuật ngữ của dự án |

### Quy ước viết tài liệu

- Song ngữ: tiếng Anh trước, tiếng Việt sau, cùng mục và cùng bảng.
- Dùng liên kết GitHub tuyệt đối (`https://github.com/tricore-opentrix/opentrix/blob/main/...`) để liên kết hoạt động ở mọi nơi đọc tài liệu; hình ảnh dùng đường dẫn tương đối.
- Mô tả hành vi hiện có của mã nguồn; tính năng chưa làm ghi ở mục "Chưa cung cấp" hoặc lộ trình, kèm liên kết Issue.
- Không ghi tên người phụ trách, trạng thái review, số PR hay mã công việc nội bộ trong tài liệu; các thông tin đó nằm ở Issue và pull request.
- Tệp mới có header SPDX theo [CONTRIBUTING.md](https://github.com/tricore-opentrix/opentrix/blob/main/CONTRIBUTING.md).