<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors

SPDX-License-Identifier: Apache-2.0
-->

# OpenTrix documentation

[Project README](../README.md) · [Development](DEVELOPMENT.md) · [Architecture](ARCHITECTURE.md) · [API](API.md)

> **Ngôn ngữ / Language:** [Tiếng Việt](#tài-liệu-opentrix--tiếng-việt) · [English](#opentrix-documentation--english)
>
> **Owner / Phụ trách:** @phanyen06ym-ien · **Issue:** [#195](https://github.com/tricore-opentrix/opentrix/issues/195), [#194](https://github.com/tricore-opentrix/opentrix/issues/194) · **Trạng thái / Status:** Đã review — merge ở #201, cập nhật ở #205 / Reviewed — merged in #201, updated in #205

---

## Tài liệu OpenTrix — Tiếng Việt

[README dự án](../README.md) · [Phát triển](DEVELOPMENT.md) · [Kiến trúc](ARCHITECTURE.md) · [API](API.md)

**Trạng thái bộ tài liệu:** Đã review, chờ nghiệm thu Giai đoạn 3 · **Owner:** @phanyen06ym-ien · **Issue:** #194. Cả 9 tài liệu chính đã được review và merge; việc gộp thư mục cũ và kiểm tra liên kết toàn repo vẫn đang làm ở #194. Cột "Trạng thái" bên dưới cho biết PR đã merge nội dung. Tài liệu chỉ mô tả hiện trạng có bằng chứng; phần mục tiêu luôn ghi rõ `PROPOSED` kèm số Issue.

OpenTrix (DX-OS Open-Core) là nền tảng nguồn mở cung cấp năng lực dùng chung (Identity, Workflow, Data) cho ứng dụng dịch vụ nội bộ, với ứng dụng minh họa IT Helpdesk. Trang này là mục lục: cần đọc gì, theo thứ tự nào, tài liệu nào đã sẵn sàng.

### 1. Bộ tài liệu chính

| Tài liệu | Đọc khi | Phụ trách | Trạng thái |
| --- | --- | --- | --- |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Cài môi trường Windows/Linux, chạy local, làm theo quy trình phát triển | Bảo | Đã review — #203 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Cần hiểu tô-pô, ranh giới Core/Application, Identity, Workflow, Gateway, Data và kiến trúc mục tiêu | Yến | Đã review — #201 |
| [API.md](API.md) | Gọi endpoint, xác thực, phân quyền, xử lý mã lỗi, tra OpenAPI | Ánh | Đã review — #200 |
| [INTEGRATION.md](INTEGRATION.md) | Tích hợp ứng dụng mới với Core, theo ví dụ Helpdesk | Ánh | Đã review — #200 |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Triển khai bằng Docker Compose, cấu hình, migration, health check | Bảo | Đã review — #203 |
| [TESTING.md](TESTING.md) | Chạy test, hiểu các lớp test, CI và bằng chứng | Ánh | Đã review — #200 |
| [OPEN_SOURCE.md](OPEN_SOURCE.md) | Đánh giá giấy phép, SPDX/REUSE, thư viện bên thứ ba, cổng xuất bản | Yến | Đã review — #201 |
| [RELEASE.md](RELEASE.md) | Gắn phiên bản, qua cổng phát hành, đóng gói artifact, viết release notes | Bảo | Đã review — #203 |

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
| [GOVERNANCE.md](../GOVERNANCE.md) | Vai trò maintainer, cách ra quyết định, quy tắc review và phát hành |
| [SECURITY.md](../SECURITY.md) | Cách báo cáo lỗ hổng bảo mật |

### 4. Tài liệu tham chiếu

- **Quyết định kiến trúc (ADR)** — [08-decisions/](08-decisions/):
  - [ADR-007 — MVP object storage provider](08-decisions/ADR-007-data-storage.md) (đang được thay thế, #181)
  - [ADR-008 — MVP analytics dashboard provider](08-decisions/ADR-008-dashboard-tool.md)
- **Bằng chứng kiểm kê Giai đoạn 2** — [09-evidence/phase-2/](09-evidence/phase-2/): Khối A (kiến trúc), Khối B (backend/hạ tầng), Khối C (ứng dụng).
- **Báo cáo kiểm chứng** — [verification/](verification/): Issue #53 (Helpdesk), Issue #90 (ArchUnit), R31 (bảng đối chiếu API Helpdesk).

### 5. Tài liệu cũ đang chuyển tiếp

| Thư mục cũ | Xử lý |
| --- | --- |
| [00-project/](00-project/) | Chưa chốt nơi gộp; phân loại từng file ở #195 |
| [01-architecture/](01-architecture/) | Gộp vào [ARCHITECTURE.md](ARCHITECTURE.md); phần Workflow và lưu trữ chờ #191, #181 |
| [02-core/](02-core/) | Gộp vào [ARCHITECTURE.md](ARCHITECTURE.md); phần Workflow và lưu trữ chờ #191, #181 |
| [06-deployment/](06-deployment/) | **Giữ lại** — hồ sơ R23/R24/R26; hướng dẫn chuẩn ở [DEPLOYMENT.md](DEPLOYMENT.md), [RELEASE.md](RELEASE.md) |
| [evidence/](evidence/) | **Giữ lại** — 3 file SQL là đầu vào của test backend |

Nguồn chuẩn là 9 tài liệu chính ở mục 1. Thư mục cũ được giữ làm hồ sơ lịch sử cho đến khi từng file được phân loại và gộp (#195).

- **Không xoá, không đổi tên** `06-deployment/` và `evidence/`: `.github/workflows/release.yml`, `scripts/r24-upstream.py` và test backend đọc file theo đúng các đường dẫn này. [R24 runbook](06-deployment/r24-release.md) vẫn là tài liệu kỹ thuật chuẩn của quy trình R24 (xem [RELEASE.md](RELEASE.md)); điều này không có nghĩa bản phát hành đã được chấp thuận.
- Nội dung về Workflow và lưu trữ trong thư mục cũ là **lịch sử**, không phải quyết định hiện hành, cho đến khi #191 và #181 được chốt.
- Facility được **hoãn** theo quyết định phạm vi ở #194; tài liệu Facility cũ chỉ là bản ghi lịch sử, không chứng minh Core đã được tái sử dụng cho hai ứng dụng.

### 6. Quy ước

- Song ngữ: tiếng Việt trước, tiếng Anh sau, cùng mục và cùng bảng.
- Mỗi file tách **Hiện trạng** (có bằng chứng) và **Mục tiêu** (ghi `PROPOSED` kèm số Issue).
- Trạng thái ghi bằng chữ, không dùng biểu tượng.
- File mới phải có header SPDX (xem [CONTRIBUTING.md](../CONTRIBUTING.md) và [OPEN_SOURCE.md](OPEN_SOURCE.md)).

---

## OpenTrix documentation — English

[Project README](../README.md) · [Development](DEVELOPMENT.md) · [Architecture](ARCHITECTURE.md) · [API](API.md)

**Documentation status:** Reviewed, pending Phase 3 acceptance · **Owner:** @phanyen06ym-ien · **Issue:** #194. All 9 main documents are reviewed and merged; legacy-folder consolidation and the repo-wide link check are still in progress under #194. The "Status" column below shows the PR that merged the content. The documents describe only the evidenced current state; target material is always marked `PROPOSED` with an issue number.

OpenTrix (DX-OS Open-Core) is an open-source platform providing shared capabilities (Identity, Workflow, Data) to internal service applications, with IT Helpdesk as the reference application. This page is the index: what to read, in which order, and what is ready.

### 1. Main documentation set

| Document | Read when you need to | Owner | Status |
| --- | --- | --- | --- |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Set up Windows/Linux, run locally, follow the development workflow | Bảo | Reviewed — #203 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Understand the topology, Core/Application boundaries, Identity, Workflow, Gateway, Data and the target architecture | Yến | Reviewed — #201 |
| [API.md](API.md) | Call endpoints, authenticate, authorize, handle error codes, consult OpenAPI | Ánh | Reviewed — #200 |
| [INTEGRATION.md](INTEGRATION.md) | Integrate a new application with Core, following the Helpdesk example | Ánh | Reviewed — #200 |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Deploy with Docker Compose, configure, migrate, check health | Bảo | Reviewed — #203 |
| [TESTING.md](TESTING.md) | Run tests, understand test layers, CI and evidence | Ánh | Reviewed — #200 |
| [OPEN_SOURCE.md](OPEN_SOURCE.md) | Assess licensing, SPDX/REUSE, third-party libraries, the publication gate | Yến | Reviewed — #201 |
| [RELEASE.md](RELEASE.md) | Version, pass release gates, package artifacts, write release notes | Bảo | Reviewed — #203 |

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
| [GOVERNANCE.md](../GOVERNANCE.md) | Maintainer roles, decision-making, review and release rules |
| [SECURITY.md](../SECURITY.md) | How to report security vulnerabilities |

### 4. Reference material

- **Architecture decisions (ADRs)** — [08-decisions/](08-decisions/):
  - [ADR-007 — MVP object storage provider](08-decisions/ADR-007-data-storage.md) (being superseded, #181)
  - [ADR-008 — MVP analytics dashboard provider](08-decisions/ADR-008-dashboard-tool.md)
- **Phase 2 audit evidence** — [09-evidence/phase-2/](09-evidence/phase-2/): Block A (architecture), Block B (backend/infrastructure), Block C (application).
- **Verification reports** — [verification/](verification/): Issue #53 (Helpdesk), Issue #90 (ArchUnit), R31 (Helpdesk API crosswalk).

### 5. Legacy documents in transition

| Legacy folder | Disposition |
| --- | --- |
| [00-project/](00-project/) | Destination not decided; per-file classification in #195 |
| [01-architecture/](01-architecture/) | Merge into [ARCHITECTURE.md](ARCHITECTURE.md); Workflow and storage parts wait for #191, #181 |
| [02-core/](02-core/) | Merge into [ARCHITECTURE.md](ARCHITECTURE.md); Workflow and storage parts wait for #191, #181 |
| [06-deployment/](06-deployment/) | **Kept** — R23/R24/R26 records; canonical guides are [DEPLOYMENT.md](DEPLOYMENT.md), [RELEASE.md](RELEASE.md) |
| [evidence/](evidence/) | **Kept** — the 3 SQL files are inputs to backend tests |

The canonical sources are the 9 main documents in section 1. Legacy folders are kept as historical records until each file is classified and merged (#195).

- **Do not delete or rename** `06-deployment/` or `evidence/`: `.github/workflows/release.yml`, `scripts/r24-upstream.py` and backend tests read files at these exact paths. The [R24 runbook](06-deployment/r24-release.md) remains the canonical technical procedure for R24 (see [RELEASE.md](RELEASE.md)); this does not mean any release has been approved.
- Workflow and storage content in legacy folders is **historical**, not a current decision, until #191 and #181 are settled.
- Facility is **deferred** per the scope decision in #194; legacy Facility documents are historical records and do not prove Core reuse across two applications.

### 6. Conventions

- Bilingual: Vietnamese first, then English, with the same sections and tables.
- Each file separates **Current state** (with evidence) from **Target** (marked `PROPOSED` with an issue number).
- Status is written in words, not icons.
- New files must carry an SPDX header (see [CONTRIBUTING.md](../CONTRIBUTING.md) and [OPEN_SOURCE.md](OPEN_SOURCE.md)).
