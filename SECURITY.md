<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# Security Policy

> **Language / Ngôn ngữ:** [English](#en) · [Tiếng Việt](#vi)

---

<a id="en"></a>

## Security Policy

### 1. Purpose and scope

This policy describes how to report and handle security vulnerabilities in the OpenTrix source
code in this repository: the headless core, the IT Helpdesk application, the Portal BFF, the
frontend and the sample deployment configuration. Third-party software (Keycloak, Apache APISIX,
PostgreSQL, Caddy and others) has its own security policies; report issues in those projects to
the upstream project.

Current releases are intended for evaluation and **have not been audited for production use**.

### 2. Supported versions

| Version | Release | Security support |
| --- | --- | --- |
| `main` | Development branch | Yes |
| [`v0.2.0`](https://github.com/tricore-opentrix/opentrix/releases/tag/v0.2.0) | Stable release, 2026-11-17 (source only) | Yes |
| [`v0.1.0`](https://github.com/tricore-opentrix/opentrix/releases/tag/v0.1.0) | Pre-release, 2026-11-04 | No — upgrade to `v0.2.0` or use `main` |

The latest stable release and `main` receive security fixes. Release archives are named
`dxos-open-core-<version>.tar.gz`, after the project's previous name; they contain OpenTrix source
code.

### 3. Reporting a vulnerability

**Do not report vulnerabilities through public Issues, pull requests, Discussions or social media.**

- **Primary channel:** GitHub Private Vulnerability Reporting — open the repository's
  **Security** tab and choose **Report a vulnerability**.
- **If that channel is unavailable:** open an Issue with the
  **Security contact request** template, **without any vulnerability details**. A maintainer will
  reply and arrange a private channel for your report.

### 4. What to include

- Affected component and version (commit SHA or tag).
- Description of the vulnerability and its potential impact.
- Minimal reproduction steps and relevant environment configuration.
- Proof of concept, if available, using only invented data.
- Suggested fix, if any.
- How you would like to be credited (name or anonymous).

Do not attach real personal data, passwords or tokens.

### 5. Handling process

1. **Intake:** acknowledge receipt of the report.
2. **Triage:** reproduce the issue and assess its severity (with reference to CVSS) and the
   affected components.
3. **Remediation:** develop the fix in a private branch or draft Security Advisory, with tests for
   both the denied and the allowed paths.
4. **Verification:** independent review and CI before merging.
5. **Release and disclosure:** release the fix, update the [changelog](https://github.com/tricore-opentrix/opentrix/blob/main/CHANGELOG.md) and publish
   a Security Advisory.

### 6. Response and disclosure timeline

| Step | Target |
| --- | --- |
| Acknowledgement | Within 3 business days |
| Initial assessment | Within 7 business days |
| Progress updates | At least every 14 days until resolved |
| Coordinated disclosure | After a fix is available, or at most 90 days after intake |

These are targets for a small team, not contractual commitments. Disclosure timing is agreed with
the reporter; if a vulnerability is being actively exploited, the maintainers may disclose earlier
with mitigation guidance.

### 7. Security boundaries

The boundaries below are design goals. Reports showing that any of them can be crossed are in
scope.

| Component | In-scope concerns |
| --- | --- |
| Keycloak / OIDC | Token validation (signature, issuer, audience, expiry), session handling, login flows and PKCE |
| API gateway / APISIX | Gateway trust boundary, forged headers, authentication bypass, direct access to backend services |
| Core Workflow | Authorization checks, role escalation, invalid workflow transitions |
| Tenant isolation | Cross-tenant access, organization-level data authorization |
| PostgreSQL | SQL injection, database access rights, schema isolation |
| Portal / BFF | Session security, CSRF, XSS, token relay |
| Sample infrastructure | TLS, secret handling, exposed ports, insecure defaults in Compose files |

Deployment assumption: only the gateway is exposed to external networks, and internal services
never trust an identity or tenant supplied by a client without token validation.

### 8. Secure deployment guidance

- **Keycloak:** change the default admin password, use HTTPS, restrict redirect URIs and enable
  MFA for administrator accounts.
- **APISIX:** expose only the gateway port; keep the Admin API on the internal network and change
  the default admin key.
- **PostgreSQL:** use a separate least-privilege account for each service; never expose the
  database port externally.
- **General:** never commit a real `.env` file; replace every placeholder in `.env.example`; pin
  image versions; apply security updates for third-party components.
- **Sample accounts:** remove them or change their passwords before using real data.

### 9. Out of scope

- Vulnerabilities that exist only in unmodified third-party software — report them upstream.
- Issues caused by not following the deployment guidance (default passwords, internal ports
  exposed to the Internet and similar).
- Volumetric denial of service, spam, social engineering or physical attacks.
- Automated scanner output without a demonstrated exploit.
- Missing security headers or version disclosure without concrete impact.

Test only against your own environment. Do not test against systems or data that belong to
others, and do not access, modify or delete data that is not yours.

### 10. References

- Fixed vulnerabilities are published under the repository's **Security → Advisories** tab and in
  the [changelog](https://github.com/tricore-opentrix/opentrix/blob/main/CHANGELOG.md).
- Contribution process: [CONTRIBUTING.md](https://github.com/tricore-opentrix/opentrix/blob/main/CONTRIBUTING.md). License: [LICENSE](https://github.com/tricore-opentrix/opentrix/blob/main/LICENSE),
  [NOTICE](https://github.com/tricore-opentrix/opentrix/blob/main/NOTICE).
- Maintainers: listed in [GOVERNANCE.md](https://github.com/tricore-opentrix/opentrix/blob/main/GOVERNANCE.md).

---

<a id="vi"></a>

## Chính sách bảo mật

### 1. Mục đích và phạm vi

Chính sách này mô tả cách báo cáo và xử lý lỗ hổng bảo mật trong mã nguồn OpenTrix thuộc
repository này: core headless, ứng dụng IT Helpdesk, Portal BFF, frontend và cấu hình triển khai
mẫu. Phần mềm bên thứ ba (Keycloak, Apache APISIX, PostgreSQL, Caddy và các phần mềm khác) có
chính sách bảo mật riêng; lỗi thuộc chính các dự án đó hãy báo cho dự án gốc.

Các bản phát hành hiện tại dành cho thử nghiệm và **chưa được kiểm định để vận hành production**.

### 2. Phiên bản được hỗ trợ

| Phiên bản | Phát hành | Hỗ trợ bảo mật |
| --- | --- | --- |
| `main` | Nhánh phát triển | Có |
| [`v0.2.0`](https://github.com/tricore-opentrix/opentrix/releases/tag/v0.2.0) | Bản ổn định, 17/11/2026 (chỉ mã nguồn) | Có |
| [`v0.1.0`](https://github.com/tricore-opentrix/opentrix/releases/tag/v0.1.0) | Pre-release, 04/11/2026 | Không — nâng cấp lên `v0.2.0` hoặc dùng `main` |

Bản ổn định mới nhất và `main` được vá lỗi bảo mật. Gói phát hành có tên
`dxos-open-core-<phiên bản>.tar.gz` theo tên cũ của dự án; nội dung bên trong là mã nguồn OpenTrix.

### 3. Báo cáo lỗ hổng

**Không báo cáo lỗ hổng qua Issue, pull request, Discussion hay mạng xã hội công khai.**

- **Kênh chính:** GitHub Private Vulnerability Reporting — vào tab **Security** của repository
  và chọn **Report a vulnerability**.
- **Nếu kênh trên không dùng được:** mở Issue bằng mẫu **Security contact request**,
  **không ghi bất kỳ chi tiết nào về lỗ hổng**. Maintainer sẽ trả lời và hướng dẫn bạn gửi báo cáo
  qua kênh riêng.

### 4. Thông tin cần cung cấp

- Thành phần và phiên bản bị ảnh hưởng (commit SHA hoặc tag).
- Mô tả lỗ hổng và tác động có thể xảy ra.
- Các bước tái hiện tối thiểu và cấu hình môi trường liên quan.
- Mã khai thác thử (proof of concept), nếu có, chỉ dùng dữ liệu tự tạo.
- Đề xuất cách khắc phục, nếu có.
- Cách bạn muốn được ghi nhận (tên hoặc ẩn danh).

Không đính kèm dữ liệu cá nhân, mật khẩu hay token thật.

### 5. Quy trình xử lý

1. **Tiếp nhận:** xác nhận đã nhận báo cáo.
2. **Phân loại:** tái hiện lỗi, đánh giá mức độ nghiêm trọng (tham chiếu CVSS) và thành phần bị
   ảnh hưởng.
3. **Khắc phục:** sửa lỗi trong nhánh riêng tư hoặc bản nháp Security Advisory, kèm test cho cả
   trường hợp bị từ chối và được phép.
4. **Kiểm chứng:** review độc lập và chạy CI trước khi merge.
5. **Phát hành và công bố:** phát hành bản sửa, cập nhật [nhật ký thay đổi](https://github.com/tricore-opentrix/opentrix/blob/main/CHANGELOG.md) và công
   bố Security Advisory.

### 6. Thời hạn phản hồi và công bố

| Bước | Thời hạn mục tiêu |
| --- | --- |
| Xác nhận đã nhận | Trong 3 ngày làm việc |
| Đánh giá ban đầu | Trong 7 ngày làm việc |
| Cập nhật tiến độ | Ít nhất 14 ngày một lần cho đến khi xử lý xong |
| Công bố có phối hợp | Sau khi có bản sửa, hoặc tối đa 90 ngày kể từ khi tiếp nhận |

Đây là mục tiêu của một nhóm nhỏ, không phải cam kết hợp đồng. Thời điểm công bố được thống nhất
với người báo cáo; nếu lỗ hổng đang bị khai thác, maintainer có thể công bố sớm hơn kèm hướng dẫn
giảm thiểu.

### 7. Ranh giới bảo mật

Các ranh giới dưới đây là mục tiêu thiết kế. Báo cáo cho thấy một ranh giới bị vượt qua đều nằm
trong phạm vi.

| Thành phần | Nội dung trong phạm vi |
| --- | --- |
| Keycloak / OIDC | Kiểm tra token (chữ ký, issuer, audience, thời hạn), quản lý phiên, luồng đăng nhập và PKCE |
| Cổng API / APISIX | Ranh giới tin cậy tại gateway, header giả mạo, vượt qua xác thực, truy cập trực tiếp vào service phía sau |
| Core Workflow | Kiểm tra quyền, leo thang vai trò, chuyển trạng thái quy trình không hợp lệ |
| Cô lập tenant | Truy cập chéo tenant, phân quyền dữ liệu theo tổ chức |
| PostgreSQL | SQL injection, quyền truy cập cơ sở dữ liệu, cô lập schema |
| Portal / BFF | Bảo mật phiên, CSRF, XSS, chuyển tiếp token |
| Hạ tầng mẫu | TLS, quản lý bí mật, cổng bị lộ, cấu hình mặc định không an toàn trong tệp Compose |

Giả định triển khai: chỉ gateway được mở ra mạng ngoài, và các service nội bộ không tin vào danh
tính hay tenant do client gửi lên khi chưa kiểm tra token.

### 8. Khuyến cáo triển khai an toàn

- **Keycloak:** đổi mật khẩu quản trị mặc định, dùng HTTPS, giới hạn redirect URI và bật MFA cho
  tài khoản quản trị.
- **APISIX:** chỉ mở cổng gateway; giữ Admin API trong mạng nội bộ và đổi admin key mặc định.
- **PostgreSQL:** mỗi service dùng một tài khoản riêng với quyền tối thiểu; không mở cổng cơ sở dữ
  liệu ra ngoài.
- **Chung:** không commit tệp `.env` thật; thay mọi giá trị mẫu trong `.env.example`; ghim phiên
  bản image; cập nhật bản vá bảo mật cho các thành phần bên thứ ba.
- **Tài khoản mẫu:** xóa hoặc đổi mật khẩu trước khi dùng với dữ liệu thật.

### 9. Ngoài phạm vi

- Lỗ hổng chỉ tồn tại trong phần mềm bên thứ ba chưa sửa đổi — hãy báo cho dự án gốc.
- Sự cố do không làm theo khuyến cáo triển khai (dùng mật khẩu mặc định, mở cổng nội bộ ra
  Internet và các trường hợp tương tự).
- Tấn công từ chối dịch vụ bằng lưu lượng lớn, spam, social engineering hoặc tấn công vật lý.
- Kết quả từ công cụ quét tự động không có bằng chứng khai thác được.
- Thiếu header bảo mật hoặc lộ thông tin phiên bản mà không có tác động cụ thể.

Khi kiểm thử, chỉ dùng môi trường của chính bạn. Không kiểm thử trên hệ thống hoặc dữ liệu của
người khác, và không truy cập, sửa hay xóa dữ liệu không thuộc về bạn.

### 10. Tài liệu tham khảo

- Lỗ hổng đã xử lý được công bố tại tab **Security → Advisories** của repository và trong
  [nhật ký thay đổi](https://github.com/tricore-opentrix/opentrix/blob/main/CHANGELOG.md).
- Quy trình đóng góp: [CONTRIBUTING.md](https://github.com/tricore-opentrix/opentrix/blob/main/CONTRIBUTING.md). Giấy phép: [LICENSE](https://github.com/tricore-opentrix/opentrix/blob/main/LICENSE),
  [NOTICE](https://github.com/tricore-opentrix/opentrix/blob/main/NOTICE).
- Danh sách maintainer: xem [GOVERNANCE.md](https://github.com/tricore-opentrix/opentrix/blob/main/GOVERNANCE.md).