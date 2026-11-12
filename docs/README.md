<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors

SPDX-License-Identifier: Apache-2.0
-->

# OpenTrix documentation

[Project README](../README.md) · [Development](DEVELOPMENT.md) · [Architecture](ARCHITECTURE.md) · [API](API.md)

> **Ngôn ngữ / Language:** [Tiếng Việt](#tài-liệu-opentrix--tiếng-việt) · [English](#opentrix-documentation--english)

---

## Tài liệu OpenTrix — Tiếng Việt

[README dự án](../README.md) · [Phát triển](DEVELOPMENT.md) · [Kiến trúc](ARCHITECTURE.md) · [API](API.md)

**Trạng thái bộ tài liệu:** Bản nháp, chờ review · **Owner:** @phanyen06ym-ien · **Issue:** #194. Bộ tài liệu đang được viết trong Giai đoạn 3; cột "Trạng thái" bên dưới cho biết file nào đã có nội dung. Tài liệu chỉ mô tả hiện trạng có bằng chứng; phần mục tiêu luôn ghi rõ `PROPOSED` kèm số Issue.

OpenTrix (DX-OS Open-Core) là nền tảng nguồn mở cung cấp năng lực dùng chung (Identity, Workflow, Data) cho ứng dụng dịch vụ nội bộ, với ứng dụng minh họa IT Helpdesk. Trang này là mục lục: cần đọc gì, theo thứ tự nào, tài liệu nào đã sẵn sàng.

### 1. Bộ tài liệu chính

| Tài liệu | Đọc khi | Phụ trách | Trạng thái |
| --- | --- | --- | --- |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Cài môi trường Windows/Linux, chạy local, làm theo quy trình phát triển | Bảo | Khung — bản nháp ở PR #203 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Cần hiểu tô-pô, ranh giới Core/Application, Identity, Workflow, Gateway, Data và kiến trúc mục tiêu | Yến | Bản nháp |
| [API.md](API.md) | Gọi endpoint, xác thực, phân quyền, xử lý mã lỗi, tra OpenAPI | Ánh | Khung — bản nháp ở PR #200 |
| [INTEGRATION.md](INTEGRATION.md) | Tích hợp ứng dụng mới với Core, theo ví dụ Helpdesk | Ánh | Khung — bản nháp ở PR #200 |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Triển khai bằng Docker Compose, cấu hình, migration, health check | Bảo | Khung — bản nháp ở PR #203 |
| [TESTING.md](TESTING.md) | Chạy test, hiểu các lớp test, CI và bằng chứng | Ánh | Khung — bản nháp ở PR #200 |
| [OPEN_SOURCE.md](OPEN_SOURCE.md) | Đánh giá giấy phép, SPDX/REUSE, thư viện bên thứ ba, cổng xuất bản | Yến | Bản nháp |
| [RELEASE.md](RELEASE.md) | Gắn phiên bản, qua cổng phát hành, đóng gói artifact, viết release notes | Bảo | Khung — bản nháp ở PR #203 |

**Khung:** mới có đề mục. **Bản nháp:** đã có nội dung, chờ review. **Đã review:** đã được review và merge.

Trạng thái phản ánh nội dung trên `main`. PR nào thay nội dung một tài liệu thì cập nhật luôn dòng của tài liệu đó trong bảng này.

### 2. Lộ trình đọc theo vai trò

- **Người phát triển mới:** [README gốc](../README.md) → [DEVELOPMENT](DEVELOPMENT.md) → [ARCHITECTURE](ARCHITECTURE.md) → [TESTING](TESTING.md)
- **Người tích hợp ứng dụng:** [ARCHITECTURE](ARCHITECTURE.md) → [API](API.md) → [INTEGRATION](INTEGRATION.md)
- **Người đánh giá / giám khảo:** [README gốc](../README.md) → [ARCHITECTURE](ARCHITECTURE.md) → [OPEN_SOURCE](OPEN_SOURCE.md) → [RELEASE](RELEASE.md) → [09-evidence/phase-2/](09-evidence/phase-2/)
- **Người đóng góp:** [CONTRIBUTING.md](../CONTRIBUTING.md) → [DEVELOPMENT](DEVELOPMENT.md) → [OPEN_SOURCE](OPEN_SOURCE.md)

### 3. Tệp ở thư mục gốc

| Tệp | Nội dung |
| --- | --- |
| [README.md](../README.md) | Giới thiệu dự án, trạng thái phát hành |
| [LICENSE](../LICENSE) | Toàn văn Apache License 2.0 |
| [NOTICE](../NOTICE) | Ghi công bản quyền dự án |
| [CHANGELOG.md](../CHANGELOG.md) | Lịch sử thay đổi theo phiên bản |
| [CONTRIBUTING.md](../CONTRIBUTING.md) | Quy trình đóng góp, header SPDX, chính sách giấy phép |
| [SECURITY.md](../SECURITY.md) | Cách báo cáo lỗ hổng bảo mật |

### 4. Tài liệu tham chiếu

- **Quyết định kiến trúc (ADR)** — [08-decisions/](08-decisions/):
  - [ADR-007 — MVP object storage provider](08-decisions/ADR-007-data-storage.md) (đang được thay thế, #181)
  - [ADR-008 — MVP analytics dashboard provider](08-decisions/ADR-008-dashboard-tool.md)
- **Bằng chứng kiểm kê Giai đoạn 2** — [09-evidence/phase-2/](09-evidence/phase-2/): Khối A (kiến trúc), Khối B (backend/hạ tầng), Khối C (ứng dụng).
- **Báo cáo kiểm chứng** — [verification/](verification/): Issue #53 (Helpdesk), Issue #90 (ArchUnit), R31 (bảng đối chiếu API Helpdesk).

### 5. Tài liệu cũ đang chuyển tiếp

| Thư mục cũ | Sẽ gộp vào |
| --- | --- |
| [00-project/](00-project/) | Chưa chốt |
| [01-architecture/](01-architecture/) | [ARCHITECTURE.md](ARCHITECTURE.md) |
| [02-core/](02-core/) | [ARCHITECTURE.md](ARCHITECTURE.md) |
| [06-deployment/](06-deployment/) | [DEPLOYMENT.md](DEPLOYMENT.md), [RELEASE.md](RELEASE.md) |
| [evidence/](evidence/) | [09-evidence/](09-evidence/) |

Các thư mục này sẽ bị gỡ sau khi nội dung đã được gộp. **Không** dùng chúng làm nguồn chuẩn.

### 6. Quy ước

- Song ngữ: tiếng Việt trước, tiếng Anh sau, cùng mục và cùng bảng.
- Mỗi file tách **Hiện trạng** (có bằng chứng) và **Mục tiêu** (ghi `PROPOSED` kèm số Issue).
- Trạng thái ghi bằng chữ, không dùng biểu tượng.
- File mới phải có header SPDX (xem [CONTRIBUTING.md](../CONTRIBUTING.md) và [OPEN_SOURCE.md](OPEN_SOURCE.md)).

---

## OpenTrix documentation — English

[Project README](../README.md) · [Development](DEVELOPMENT.md) · [Architecture](ARCHITECTURE.md) · [API](API.md)

**Documentation status:** Draft, pending review · **Owner:** @phanyen06ym-ien · **Issue:** #194. The documentation set is being written in Phase 3; the "Status" column below shows which files have content. The documents describe only the evidenced current state; target material is always marked `PROPOSED` with an issue number.

OpenTrix (DX-OS Open-Core) is an open-source platform providing shared capabilities (Identity, Workflow, Data) to internal service applications, with IT Helpdesk as the reference application. This page is the index: what to read, in which order, and what is ready.

### 1. Main documentation set

| Document | Read when you need to | Owner | Status |
| --- | --- | --- | --- |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Set up Windows/Linux, run locally, follow the development workflow | Bảo | Skeleton — draft in PR #203 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Understand the topology, Core/Application boundaries, Identity, Workflow, Gateway, Data and the target architecture | Yến | Draft |
| [API.md](API.md) | Call endpoints, authenticate, authorize, handle error codes, consult OpenAPI | Ánh | Skeleton — draft in PR #200 |
| [INTEGRATION.md](INTEGRATION.md) | Integrate a new application with Core, following the Helpdesk example | Ánh | Skeleton — draft in PR #200 |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Deploy with Docker Compose, configure, migrate, check health | Bảo | Skeleton — draft in PR #203 |
| [TESTING.md](TESTING.md) | Run tests, understand test layers, CI and evidence | Ánh | Skeleton — draft in PR #200 |
| [OPEN_SOURCE.md](OPEN_SOURCE.md) | Assess licensing, SPDX/REUSE, third-party libraries, the publication gate | Yến | Draft |
| [RELEASE.md](RELEASE.md) | Version, pass release gates, package artifacts, write release notes | Bảo | Skeleton — draft in PR #203 |

**Skeleton:** headings only. **Draft:** content written, pending review. **Reviewed:** reviewed and merged.

Status reflects what is on `main`. A PR that changes a document's content updates that document's row here in the same PR.

### 2. Reading paths by role

- **New developer:** [Root README](../README.md) → [DEVELOPMENT](DEVELOPMENT.md) → [ARCHITECTURE](ARCHITECTURE.md) → [TESTING](TESTING.md)
- **Application integrator:** [ARCHITECTURE](ARCHITECTURE.md) → [API](API.md) → [INTEGRATION](INTEGRATION.md)
- **Reviewer / judge:** [Root README](../README.md) → [ARCHITECTURE](ARCHITECTURE.md) → [OPEN_SOURCE](OPEN_SOURCE.md) → [RELEASE](RELEASE.md) → [09-evidence/phase-2/](09-evidence/phase-2/)
- **Contributor:** [CONTRIBUTING.md](../CONTRIBUTING.md) → [DEVELOPMENT](DEVELOPMENT.md) → [OPEN_SOURCE](OPEN_SOURCE.md)

### 3. Root files

| File | Content |
| --- | --- |
| [README.md](../README.md) | Project introduction, release status |
| [LICENSE](../LICENSE) | Full Apache License 2.0 text |
| [NOTICE](../NOTICE) | Project copyright attribution |
| [CHANGELOG.md](../CHANGELOG.md) | Change history by version |
| [CONTRIBUTING.md](../CONTRIBUTING.md) | Contribution workflow, SPDX headers, license policy |
| [SECURITY.md](../SECURITY.md) | How to report security vulnerabilities |

### 4. Reference material

- **Architecture decisions (ADRs)** — [08-decisions/](08-decisions/):
  - [ADR-007 — MVP object storage provider](08-decisions/ADR-007-data-storage.md) (being superseded, #181)
  - [ADR-008 — MVP analytics dashboard provider](08-decisions/ADR-008-dashboard-tool.md)
- **Phase 2 audit evidence** — [09-evidence/phase-2/](09-evidence/phase-2/): Block A (architecture), Block B (backend/infrastructure), Block C (application).
- **Verification reports** — [verification/](verification/): Issue #53 (Helpdesk), Issue #90 (ArchUnit), R31 (Helpdesk API crosswalk).

### 5. Legacy documents in transition

| Legacy folder | Will be merged into |
| --- | --- |
| [00-project/](00-project/) | Not decided |
| [01-architecture/](01-architecture/) | [ARCHITECTURE.md](ARCHITECTURE.md) |
| [02-core/](02-core/) | [ARCHITECTURE.md](ARCHITECTURE.md) |
| [06-deployment/](06-deployment/) | [DEPLOYMENT.md](DEPLOYMENT.md), [RELEASE.md](RELEASE.md) |
| [evidence/](evidence/) | [09-evidence/](09-evidence/) |

These folders will be removed once their content has been merged. **Do not** use them as the authoritative source.

### 6. Conventions

- Bilingual: Vietnamese first, then English, with the same sections and tables.
- Each file separates **Current state** (with evidence) from **Target** (marked `PROPOSED` with an issue number).
- Status is written in words, not icons.
- New files must carry an SPDX header (see [CONTRIBUTING.md](../CONTRIBUTING.md) and [OPEN_SOURCE.md](OPEN_SOURCE.md)).
