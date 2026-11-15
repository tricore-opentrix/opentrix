<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# OpenTrix — Changelog

> **Ngôn ngữ / Language:** mỗi mục ghi tiếng Việt trước, tiếng Anh in nghiêng ngay dưới. ·
> _Each entry is written in Vietnamese first, with the English text in italics below._

Mọi thay đổi người dùng nhìn thấy được của OpenTrix được ghi tại đây, theo
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) và
[Semantic Versioning](https://semver.org/).
_All notable user-visible changes to OpenTrix are recorded here, following Keep a Changelog and Semantic Versioning._

## [Unreleased]

### Added · Thêm mới

- Theme đăng nhập Keycloak OpenTrix IT Helpdesk cho môi trường integration-local: bố cục hai cột, tiếng Việt, logo và hình minh họa nội bộ; kế thừa form gốc `keycloak.v2`, giữ nguyên Authorization Code + PKCE (#225: #243).
  _OpenTrix IT Helpdesk Keycloak login theme for integration-local: two-column layout, Vietnamese locale, local logo and illustration; inherits the stock `keycloak.v2` form and keeps Authorization Code + PKCE._
- Chạy thử toàn bộ hệ thống bằng một lệnh (`infra/demo/demo-up` / `demo-down`, PowerShell 7 và Bash): build image từ mã nguồn, ingress HTTPS bằng Caddy, sinh bí mật cục bộ và kiểm tra sức khỏe từng thành phần (#119: #229, #234, #237).
  _One-command integration-local demo stack (`infra/demo/demo-up` / `demo-down`, PowerShell 7 and Bash) with source-built images, Caddy HTTPS ingress, generated local secrets and health checks._
- Cổng API APISIX chạy độc lập: kiểm token qua JWKS, giới hạn tần suất, chuẩn hóa header chuyển tiếp; bật bằng `demo-up -Gateway` / `--gateway` (#116: #232).
  _Standalone APISIX gateway overlay with JWKS token validation, rate limiting and forwarded-header rewrite, enabled with `demo-up -Gateway` / `--gateway`._
- Realm Keycloak `tricore` có phiên bản cho môi trường demo, cùng cấu hình mạng dùng chung cho PostgreSQL, Keycloak và Backend (#226, #227).
  _Versioned `tricore` Keycloak demo realm and a shared-network demo setup for PostgreSQL, Keycloak and Backend._
- Đóng gói phát hành theo tag: gói mã nguồn, bản build Java và frontend, SBOM và NOTICE, checksum SHA256, ghi chú phát hành theo phiên bản; có cổng nghiệm thu trước khi công bố.
  _Tag-triggered release packaging: source archive, Java and frontend builds, SBOM and NOTICE inventory, SHA256 checksums and versioned release notes, guarded by an acceptance gate before publication._
- Quyết định kiến trúc ADR-009, ADR-016, ADR-017, ADR-018 và mục lục tài liệu kiến trúc tương ứng (#221).
  _Architecture decisions ADR-009, ADR-016, ADR-017 and ADR-018 with aligned architecture and documentation indexes._

### Changed · Thay đổi

- Portal: nhận diện OpenTrix · IT Helpdesk, khung đăng nhập cho integration-local và đăng xuất qua BFF có chống CSRF (#233).
  _Portal: OpenTrix · IT Helpdesk branding, an integration-local login panel and CSRF-protected logout through the BFF._
- Portal: nhãn trạng thái quy trình bằng tiếng Việt với huy hiệu riêng; giá trị API giữ nguyên, trạng thái lạ có hiển thị dự phòng (#106, #233).
  _Portal: Vietnamese workflow state labels with distinct badges; API values are unchanged and unknown states fall back safely._
- Portal: gắn nhãn chế độ MOCK và integration-local; Facility chỉ có trong MOCK (#224: #230).
  _Portal: label MOCK and integration-local demo modes and keep Facility MOCK-only._
- Đổi tên repository thành `tricore-opentrix/opentrix`; cập nhật đường dẫn, tài liệu và giá trị cài đặt mặc định (#136).
  _Repository renamed to `tricore-opentrix/opentrix`; links, documentation and setup defaults updated._
- Đồng bộ định nghĩa label và milestone GitHub với các quyết định kiến trúc đã chốt (#223).
  _GitHub label and milestone definitions aligned with the accepted architecture decisions._
- Viết lại README, CONTRIBUTING và thông tin giấy phép thành tài liệu song ngữ Việt – Anh (#228).
  _README, CONTRIBUTING and license information rewritten as bilingual Vietnamese–English project documentation._

### Fixed · Sửa lỗi

- Mã yêu cầu Helpdesk không còn tràn sang tiêu đề trong danh sách integration-local; giữ nguyên mã đầy đủ và đường dẫn (#225: #242).
  _Helpdesk request IDs no longer overflow into request titles in the integration-local list; full identifiers and links are preserved._

## [0.1.0] - 2026-11-04

### Added · Thêm mới

- API HTTP Backend IT Helpdesk (chín route ứng dụng), phân quyền theo tổ chức và tài nguyên, lưu trữ PostgreSQL 17, lịch sử chuyển trạng thái quy trình.
  _IT Helpdesk Backend HTTP API (nine application routes) with tenant/resource-scoped authorization, PostgreSQL 17 persistence and audited workflow transitions._
- Portal BFF với OIDC Authorization Code + PKCE, phiên trình duyệt phía server và chống CSRF.
  _Portal BFF with OIDC Authorization Code + PKCE, server-side browser session and CSRF protection._
- Portal React IT Helpdesk với chế độ MOCK độc lập và chế độ build `integration-local`.
  _React IT Helpdesk Portal with a standalone MOCK mode and an `integration-local` build mode._
- File `LICENSE` Apache-2.0 và `NOTICE` ở thư mục gốc.
  _Apache-2.0 root `LICENSE` and `NOTICE` files._
- Quy tắc phụ thuộc Core bằng ArchUnit và test kiểm chứng phản ví dụ.
  _ArchUnit Core dependency rules and negative canary tests._
- Hướng dẫn đóng góp, mẫu Issue và pull request, CODEOWNERS.
  _Contribution guidelines, issue and pull request templates, and CODEOWNERS._
- CI dùng chung cho pull request vào `main`: build và test backend, build ứng dụng, kiểm tra repository và hồi quy bảo mật Identity–Gateway.
  _Shared CI for pull requests to `main`: backend build and tests, application builds, repository checks and Identity–Gateway security regressions._

### Changed · Thay đổi

- `backend/gradlew` có quyền thực thi trên Linux và macOS.
  _`backend/gradlew` is executable on Linux and macOS._
- API HTTP Helpdesk trả HTTP 404 / `NOT_FOUND` cho tài nguyên bị ẩn hoặc không tồn tại; API Workflow dùng chung giữ mã riêng `DEFINITION_NOT_FOUND` / `INSTANCE_NOT_FOUND` (#105).
  _The Helpdesk HTTP API returns a scoped HTTP 404 / `NOT_FOUND` for hidden or missing resources; the generic Workflow HTTP API keeps its distinct `DEFINITION_NOT_FOUND` / `INSTANCE_NOT_FOUND` codes._

### Fixed · Sửa lỗi

- Build và test backend trên Linux: khôi phục ba fixture SQL, ghim hash manifest theo kết thúc dòng LF, chỉ chạy test riêng của PowerShell trên Windows.
  _Linux backend build and tests: restored three SQL fixtures, pinned the manifest hash to LF line endings and limited a PowerShell-specific test to Windows._
- Tạo yêu cầu Helpdesk bị từ chối sớm khi thiếu quyền kỹ thuật bắt buộc; khi không chắc commit Workflow đã thành công, API trả HTTP 503 với `COMMIT_OUTCOME_UNKNOWN` và không được tự động thử lại.
  _Helpdesk create rejects requests missing the required technical authorities before protected lookups; an uncertain Workflow commit returns HTTP 503 with `COMMIT_OUTCOME_UNKNOWN` and must not be retried automatically._

### Removed · Loại bỏ

- Gỡ prototype cũ `com.tricore.dxos.request` và các route `/api/v1/requests/*`; giữ nguyên migration Flyway V1/V2, Helpdesk vẫn ở `/api/v1/mvp/requests`.
  _Legacy `com.tricore.dxos.request` prototype and the `/api/v1/requests/*` routes; historical Flyway V1/V2 migrations are preserved and Helpdesk remains at `/api/v1/mvp/requests`._
- Gỡ workflow CI riêng của Issue #23; các kiểm tra bảo mật chạy trong CI dùng chung.
  _The separate Issue #23 workflow; its security checks run in shared CI._

[Unreleased]: https://github.com/tricore-opentrix/opentrix/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/tricore-opentrix/opentrix/releases/tag/v0.1.0
