<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# Changelog

> **Language / Ngôn ngữ:** [English](#en) · [Tiếng Việt](#vi)

---

<a id="en"></a>

## [Unreleased]

### Changed

- GitHub-generated source archives no longer include `backend/gradle/wrapper/gradle-wrapper.jar`.
  To build from an extracted archive, use an external Gradle 8.14.3 installation ([#256](https://github.com/tricore-opentrix/opentrix/pull/256)).

## [0.2.0] - 2026-11-17

This release is distributed as source code only. It does not include prebuilt JAR files, a
frontend `dist` bundle or container images.

### Added

- One-command local deployment with `infra/demo/demo-up` and `demo-down` (PowerShell 7 and Bash):
  images are built from source and served behind a Caddy HTTPS ingress, with generated local
  secrets and per-service health checks ([#229](https://github.com/tricore-opentrix/opentrix/pull/229), [#234](https://github.com/tricore-opentrix/opentrix/pull/234), [#237](https://github.com/tricore-opentrix/opentrix/pull/237)).
- Optional Apache APISIX API gateway with JWKS token validation, rate limiting and
  forwarded-header normalization, enabled with `-Gateway` / `--gateway` ([#232](https://github.com/tricore-opentrix/opentrix/pull/232)).
- Versioned Keycloak realm `tricore` and a shared network configuration for PostgreSQL, Keycloak
  and the backend ([#226](https://github.com/tricore-opentrix/opentrix/pull/226), [#227](https://github.com/tricore-opentrix/opentrix/pull/227)).
- OpenTrix Keycloak login theme with a Vietnamese locale, based on the standard `keycloak.v2`
  theme; the Authorization Code + PKCE flow is unchanged ([#243](https://github.com/tricore-opentrix/opentrix/pull/243)).
- Source release packaging: source archive, SBOM, NOTICE, `SHA256SUMS` and release notes, with an
  approval step before publication.
- Architecture decision records ADR-009, ADR-016, ADR-017 and ADR-018, with updated architecture
  and documentation indexes ([#221](https://github.com/tricore-opentrix/opentrix/pull/221)).

### Changed

- Portal: OpenTrix IT Helpdesk branding, a sign-in page for the integrated mode and logout through
  the BFF with CSRF protection ([#238](https://github.com/tricore-opentrix/opentrix/pull/238)).
- Portal: workflow states are shown with Vietnamese labels and distinct badges; API values are
  unchanged and unknown states fall back to a default label ([#238](https://github.com/tricore-opentrix/opentrix/pull/238)).
- Portal: the active mode (MOCK or `integration-local`) is labelled in the interface; the Facility
  application is available in MOCK mode only ([#230](https://github.com/tricore-opentrix/opentrix/pull/230)).
- The repository moved to `tricore-opentrix/opentrix`; links, documentation and default settings
  were updated ([#136](https://github.com/tricore-opentrix/opentrix/pull/136)).
- GitHub labels and milestones aligned with the accepted architecture decisions ([#223](https://github.com/tricore-opentrix/opentrix/pull/223)).
- README, contribution guide and licensing information rewritten as bilingual documentation ([#239](https://github.com/tricore-opentrix/opentrix/pull/239)).

### Fixed

- Request identifiers no longer overlap request titles in the Helpdesk request list; full
  identifiers and links are preserved ([#242](https://github.com/tricore-opentrix/opentrix/pull/242)).

## [0.1.0] - 2026-11-04

### Added

- IT Helpdesk HTTP API with nine operations, tenant- and resource-scoped authorization,
  PostgreSQL 17 persistence and an audited workflow history.
- Portal BFF with OpenID Connect Authorization Code + PKCE, server-side sessions and CSRF
  protection.
- React IT Helpdesk Portal with a standalone MOCK mode and an `integration-local` build mode.
- Apache License 2.0 `LICENSE` and `NOTICE` files.
- Core dependency rules enforced with ArchUnit, including negative tests.
- Contribution guide, issue and pull request templates, and `CODEOWNERS`.
- Continuous integration for pull requests to `main`: backend build and tests, application builds,
  repository checks and identity/gateway security regression tests.

### Changed

- `backend/gradlew` is now executable on Linux and macOS.
- The Helpdesk API returns HTTP 404 `NOT_FOUND` for both hidden and missing resources; the generic
  Workflow API keeps the distinct `DEFINITION_NOT_FOUND` and `INSTANCE_NOT_FOUND` codes.

### Fixed

- Backend build and tests on Linux: restored three SQL test fixtures, pinned the manifest hash to
  LF line endings and limited a PowerShell-specific test to Windows.
- Request creation is rejected early when required technical permissions are missing. When the
  outcome of a workflow commit is unknown, the API returns HTTP 503 `COMMIT_OUTCOME_UNKNOWN`;
  clients must not retry such requests automatically.

### Removed

- The legacy `com.tricore.dxos.request` prototype and the `/api/v1/requests/*` routes. Existing
  Flyway migrations V1 and V2 are preserved; the Helpdesk API remains at `/api/v1/mvp/requests`.
- The standalone security CI workflow; its checks now run in the shared CI pipeline.

---

<a id="vi"></a>

# Nhật ký thay đổi

## [Unreleased]

### Thay đổi

- Gói mã nguồn do GitHub tự sinh không còn chứa `backend/gradle/wrapper/gradle-wrapper.jar`. Khi
  build từ gói đã giải nén, dùng Gradle 8.14.3 cài đặt riêng ([#256](https://github.com/tricore-opentrix/opentrix/pull/256)).

## [0.2.0] - 2026-11-17

Bản phát hành này chỉ phân phối mã nguồn, không kèm tệp JAR dựng sẵn, gói frontend `dist` hay
container image.

### Thêm mới

- Triển khai cục bộ bằng một lệnh với `infra/demo/demo-up` và `demo-down` (PowerShell 7 và Bash):
  image được build từ mã nguồn và chạy sau ingress HTTPS Caddy, tự sinh bí mật cục bộ và kiểm tra
  tình trạng từng dịch vụ ([#229](https://github.com/tricore-opentrix/opentrix/pull/229), [#234](https://github.com/tricore-opentrix/opentrix/pull/234), [#237](https://github.com/tricore-opentrix/opentrix/pull/237)).
- Cổng API Apache APISIX tùy chọn: kiểm tra token qua JWKS, giới hạn tần suất, chuẩn hóa header
  chuyển tiếp; bật bằng `-Gateway` / `--gateway` ([#232](https://github.com/tricore-opentrix/opentrix/pull/232)).
- Realm Keycloak `tricore` được quản lý phiên bản, cùng cấu hình mạng dùng chung cho PostgreSQL,
  Keycloak và backend ([#226](https://github.com/tricore-opentrix/opentrix/pull/226), [#227](https://github.com/tricore-opentrix/opentrix/pull/227)).
- Giao diện đăng nhập Keycloak của OpenTrix có bản địa hóa tiếng Việt, kế thừa theme chuẩn
  `keycloak.v2`; luồng Authorization Code + PKCE giữ nguyên ([#243](https://github.com/tricore-opentrix/opentrix/pull/243)).
- Đóng gói bản phát hành mã nguồn: gói mã nguồn, SBOM, NOTICE, `SHA256SUMS` và ghi chú phát hành,
  có bước phê duyệt trước khi công bố.
- Các bản ghi quyết định kiến trúc ADR-009, ADR-016, ADR-017, ADR-018 và mục lục tài liệu kiến trúc
  tương ứng ([#221](https://github.com/tricore-opentrix/opentrix/pull/221)).

### Thay đổi

- Portal: nhận diện OpenTrix IT Helpdesk, trang đăng nhập cho chế độ tích hợp và đăng xuất qua BFF
  có chống CSRF ([#238](https://github.com/tricore-opentrix/opentrix/pull/238)).
- Portal: trạng thái quy trình hiển thị bằng nhãn tiếng Việt với huy hiệu riêng; giá trị API giữ
  nguyên, trạng thái không xác định dùng nhãn mặc định ([#238](https://github.com/tricore-opentrix/opentrix/pull/238)).
- Portal: giao diện ghi rõ chế độ đang chạy (MOCK hoặc `integration-local`); ứng dụng Facility chỉ
  có trong chế độ MOCK ([#230](https://github.com/tricore-opentrix/opentrix/pull/230)).
- Repository chuyển sang `tricore-opentrix/opentrix`; đường dẫn, tài liệu và cấu hình mặc định được
  cập nhật ([#136](https://github.com/tricore-opentrix/opentrix/pull/136)).
- Nhãn và milestone trên GitHub được đồng bộ với các quyết định kiến trúc đã chấp nhận ([#223](https://github.com/tricore-opentrix/opentrix/pull/223)).
- README, hướng dẫn đóng góp và thông tin giấy phép được viết lại thành tài liệu song ngữ ([#239](https://github.com/tricore-opentrix/opentrix/pull/239)).

### Sửa lỗi

- Mã yêu cầu không còn đè lên tiêu đề trong danh sách yêu cầu Helpdesk; mã đầy đủ và đường dẫn được
  giữ nguyên ([#242](https://github.com/tricore-opentrix/opentrix/pull/242)).

## [0.1.0] - 2026-11-04

### Thêm mới

- API HTTP IT Helpdesk với chín thao tác, phân quyền theo tổ chức và theo tài nguyên, lưu trữ
  PostgreSQL 17 và lịch sử quy trình có ghi vết.
- Portal BFF dùng OpenID Connect Authorization Code + PKCE, phiên phía máy chủ và chống CSRF.
- Portal React IT Helpdesk với chế độ MOCK chạy độc lập và chế độ build `integration-local`.
- Tệp `LICENSE` (Apache License 2.0) và `NOTICE`.
- Quy tắc phụ thuộc của Core được kiểm tra bằng ArchUnit, kèm test phản ví dụ.
- Hướng dẫn đóng góp, mẫu issue và pull request, tệp `CODEOWNERS`.
- Tích hợp liên tục cho pull request vào `main`: build và test backend, build các ứng dụng, kiểm tra
  repository và test hồi quy bảo mật cho định danh và cổng API.

### Thay đổi

- `backend/gradlew` có quyền thực thi trên Linux và macOS.
- API Helpdesk trả HTTP 404 `NOT_FOUND` cho cả tài nguyên bị ẩn và không tồn tại; API Workflow dùng
  chung giữ các mã riêng `DEFINITION_NOT_FOUND` và `INSTANCE_NOT_FOUND`.

### Sửa lỗi

- Build và test backend trên Linux: khôi phục ba fixture SQL, cố định hash manifest theo ký tự xuống
  dòng LF và chỉ chạy test dành cho PowerShell trên Windows.
- Yêu cầu tạo mới bị từ chối sớm khi thiếu quyền kỹ thuật bắt buộc. Khi không xác định được kết quả
  commit của quy trình, API trả HTTP 503 `COMMIT_OUTCOME_UNKNOWN`; client không được tự động gửi lại
  các yêu cầu này.

### Loại bỏ

- Prototype cũ `com.tricore.dxos.request` và các route `/api/v1/requests/*`. Các migration Flyway V1
  và V2 được giữ nguyên; API Helpdesk vẫn ở `/api/v1/mvp/requests`.
- Workflow CI bảo mật chạy riêng; các kiểm tra này nay chạy trong pipeline CI dùng chung.

[Unreleased]: https://github.com/tricore-opentrix/opentrix/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/tricore-opentrix/opentrix/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/tricore-opentrix/opentrix/releases/tag/v0.1.0
