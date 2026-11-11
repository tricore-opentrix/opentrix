<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors

SPDX-License-Identifier: Apache-2.0
-->

# Tài liệu OpenTrix / OpenTrix documentation

> **Trạng thái / Status:** 🚧 Khung — đang viết / Skeleton — in progress · **Owner:** @phanyen06ym-ien · **Issue:** #194

## Tiếng Việt

### Bộ tài liệu chính

| File | Nội dung | Người phụ trách |
|---|---|---|
| [DEVELOPMENT.md](DEVELOPMENT.md) | Môi trường, cài đặt Windows/Linux, chạy local, quy trình phát triển | Bảo |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Tổng quan, Core/Application, Identity, Workflow, Gateway, Data, ADR | Yến |
| [API.md](API.md) | Endpoint, xác thực, phân quyền, mã lỗi, OpenAPI | Ánh |
| [INTEGRATION.md](INTEGRATION.md) | Tích hợp ứng dụng với Core, ví dụ Helpdesk | Ánh |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Docker Compose, cấu hình, migration, health check | Bảo |
| [TESTING.md](TESTING.md) | Các lớp test, cách chạy, CI, bằng chứng | Ánh |
| [OPEN_SOURCE.md](OPEN_SOURCE.md) | Giấy phép, SPDX, thư viện bên thứ ba, nguồn gốc mã | Yến |
| [RELEASE.md](RELEASE.md) | Phiên bản, cổng phát hành, artifact, release notes | Bảo |

### Lộ trình đọc cho người mới

1. README ở thư mục gốc → 2. DEVELOPMENT.md → 3. ARCHITECTURE.md → 4. API.md / INTEGRATION.md → 5. TESTING.md

### Tài liệu tham chiếu

- Quyết định kiến trúc (ADR): [08-decisions/](08-decisions/)
- Bằng chứng kiểm kê Giai đoạn 2: [09-evidence/phase-2/](09-evidence/phase-2/)
- Báo cáo kiểm chứng: [verification/](verification/)

### Quy ước

Song ngữ (tiếng Việt trước, tiếng Anh sau). Mỗi file tách rõ **Hiện trạng** (có bằng chứng) và **Mục tiêu** (ghi `PROPOSED` kèm số Issue).

## English

### Main documentation set

| File | Content | Owner |
|---|---|---|
| [DEVELOPMENT.md](DEVELOPMENT.md) | Environment, Windows/Linux setup, local run, workflow | Bảo |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Overview, Core/Application, Identity, Workflow, Gateway, Data, ADRs | Yến |
| [API.md](API.md) | Endpoints, authentication, authorization, error codes, OpenAPI | Ánh |
| [INTEGRATION.md](INTEGRATION.md) | Integrating applications with Core, Helpdesk example | Ánh |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Docker Compose, configuration, migrations, health checks | Bảo |
| [TESTING.md](TESTING.md) | Test layers, running tests, CI, evidence | Ánh |
| [OPEN_SOURCE.md](OPEN_SOURCE.md) | License, SPDX, third-party libraries, provenance | Yến |
| [RELEASE.md](RELEASE.md) | Versioning, release gates, artifacts, release notes | Bảo |

### Reading path for newcomers

1. Root README → 2. DEVELOPMENT.md → 3. ARCHITECTURE.md → 4. API.md / INTEGRATION.md → 5. TESTING.md

### Reference material

- Architecture decisions (ADRs): [08-decisions/](08-decisions/)
- Phase 2 audit evidence: [09-evidence/phase-2/](09-evidence/phase-2/)
- Verification reports: [verification/](verification/)

### Conventions

Bilingual (Vietnamese first, then English). Each file separates **Current state** (with evidence) from **Target** (marked `PROPOSED` with an issue number).