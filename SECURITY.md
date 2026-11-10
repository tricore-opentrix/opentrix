<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# OPENTRIX

> **Ngôn ngữ / Language:** [Tiếng Việt](#vi) · [English](#en)

---

<a id="vi"></a>

## OPENTRIX — Chính sách bảo mật

### 1. Mục đích và phạm vi

Chính sách này mô tả cách báo cáo và xử lý lỗ hổng bảo mật trong mã nguồn OPENTRIX (DX-OS Open-Core) thuộc repository này: core headless, ứng dụng IT Helpdesk, Portal BFF, frontend và cấu hình triển khai mẫu. Phần mềm bên thứ ba (Keycloak, Apache APISIX, PostgreSQL, SeaweedFS, Node-RED…) có chính sách bảo mật riêng; lỗi thuộc chính các dự án đó hãy báo cho dự án gốc.

OPENTRIX là dự án do nhóm sinh viên TRICORE phát triển cho cuộc thi OLP Phần mềm nguồn mở 2026. Bản phát hành hiện tại dùng cho thử nghiệm và trình diễn, **chưa được kiểm định để vận hành production**.

### 2. Phiên bản được hỗ trợ

| Phiên bản | Trạng thái phát hành | Hỗ trợ bảo mật |
| --- | --- | --- |
| `main` | Nhánh phát triển | Có |
| `v0.1.0` | [Pre-release công khai](https://github.com/tricore-opentrix/opentrix/releases/tag/v0.1.0) ngày 2026-11-04 (kèm `dxos-open-core-0.1.0.tar.gz` và `SHA256SUMS`) | Không — bản MVP để thử nghiệm; dùng `main` |

Hiện chưa có bản phát hành ổn định (không phải pre-release). Bảng này sẽ được cập nhật khi có bản phát hành ổn định; từ đó bản ổn định mới nhất cũng được hỗ trợ bảo mật. Việc một bản được công bố không có nghĩa là quyền phân phối của toàn bộ nội dung đã được xác minh; phần đó được theo dõi tại [Issue #138](https://github.com/tricore-opentrix/opentrix/issues/138).

### 3. Báo cáo lỗ hổng

**Không báo cáo lỗ hổng qua Issue, Pull Request, Discussion hay mạng xã hội công khai.**

- **Kênh chính:** GitHub Private Vulnerability Reporting — vào tab **Security** của repository và chọn **Report a vulnerability**.
- **Nếu kênh trên không dùng được:** mở một Issue công khai với tiêu đề `Security contact request`, **không ghi bất kỳ chi tiết nào về lỗ hổng**. Maintainer sẽ trả lời và hướng dẫn bạn gửi báo cáo qua kênh riêng.

### 4. Thông tin cần cung cấp

- Thành phần và phiên bản bị ảnh hưởng (commit SHA hoặc tag).
- Mô tả lỗ hổng và tác động có thể xảy ra.
- Các bước tái hiện tối thiểu, cấu hình môi trường liên quan.
- Mã khai thác thử (proof of concept), nếu có — chỉ dùng dữ liệu tự tạo.
- Đề xuất cách khắc phục, nếu có.
- Cách bạn muốn được ghi nhận (tên hoặc ẩn danh).

Không đính kèm dữ liệu cá nhân, mật khẩu hay token thật.

### 5. Quy trình xử lý

1. **Tiếp nhận:** xác nhận đã nhận báo cáo.
2. **Phân loại:** tái hiện, đánh giá mức độ nghiêm trọng (tham chiếu CVSS) và thành phần bị ảnh hưởng.
3. **Khắc phục:** sửa lỗi trong nhánh riêng tư hoặc bản nháp Security Advisory, kèm test thể hiện cả đường bị từ chối và đường được phép.
4. **Kiểm chứng:** review độc lập và chạy CI trước khi merge.
5. **Phát hành và công bố:** phát hành bản sửa, cập nhật `CHANGELOG.md` và công bố Security Advisory.

### 6. Thời hạn phản hồi và công bố

| Bước | Thời hạn mục tiêu |
| --- | --- |
| Xác nhận đã nhận | Trong 3 ngày làm việc |
| Đánh giá ban đầu | Trong 7 ngày làm việc |
| Cập nhật tiến độ | Ít nhất 14 ngày một lần cho đến khi xử lý xong |
| Công bố có phối hợp | Sau khi có bản sửa, hoặc tối đa 90 ngày kể từ khi tiếp nhận |

Đây là mục tiêu của một nhóm nhỏ, không phải cam kết hợp đồng. Thời điểm công bố được thống nhất với người báo cáo; nếu lỗ hổng đang bị khai thác, nhóm có thể công bố sớm hơn kèm hướng dẫn giảm thiểu.

### 7. Ranh giới bảo mật

Các ranh giới dưới đây là mục tiêu thiết kế. Báo cáo cho thấy một ranh giới bị vượt qua đều nằm trong phạm vi.

| Thành phần | Nội dung trong phạm vi |
| --- | --- |
| Keycloak / OIDC | Kiểm tra token (chữ ký, issuer, audience, thời hạn), quản lý phiên, luồng đăng nhập và PKCE |
| API Gateway / APISIX | Ranh giới tin cậy tại gateway, header giả mạo, vượt qua xác thực, truy cập trực tiếp vào service phía sau |
| Core Workflow | Kiểm tra quyền, leo thang vai trò, chuyển trạng thái quy trình không hợp lệ |
| Cô lập tenant | Truy cập chéo tenant, phân quyền dữ liệu theo tổ chức |
| PostgreSQL | SQL injection, quyền truy cập cơ sở dữ liệu, cô lập schema |
| Lưu trữ đối tượng | Phân quyền theo object, lộ thông tin xác thực, truy cập tệp trái phép |
| Portal / BFF | Bảo mật phiên, CSRF, XSS, chuyển tiếp token |
| Hạ tầng mẫu | TLS, quản lý secret, cổng bị lộ, cấu hình mặc định không an toàn trong compose |

Giả định triển khai: chỉ gateway được mở ra mạng ngoài; service nội bộ không tin vào danh tính hay tenant do client gửi lên mà không qua kiểm tra token.

### 8. Khuyến cáo triển khai an toàn

- **Keycloak:** đổi mật khẩu quản trị mặc định, dùng HTTPS, giới hạn redirect URI, bật MFA cho tài khoản quản trị.
- **APISIX:** chỉ mở cổng gateway; khóa Admin API vào mạng nội bộ và đổi admin key mặc định.
- **PostgreSQL:** dùng tài khoản riêng với quyền tối thiểu cho từng service; không mở cổng cơ sở dữ liệu ra ngoài.
- **Lưu trữ đối tượng:** dùng khóa truy cập riêng, không để bucket công khai.
- **Chung:** không commit file `.env` thật; thay mọi giá trị mẫu trong `.env.example`; ghim phiên bản image; cập nhật bản vá bảo mật của các thành phần bên thứ ba.
- **Tài khoản demo:** xóa hoặc đổi mật khẩu trước khi dùng với dữ liệu thật.

### 9. Ngoài phạm vi

- Lỗ hổng chỉ tồn tại trong phần mềm bên thứ ba chưa sửa đổi — hãy báo cho dự án gốc.
- Sự cố do không làm theo khuyến cáo triển khai (dùng mật khẩu mặc định, mở cổng nội bộ ra Internet…).
- Tấn công từ chối dịch vụ bằng lưu lượng lớn, spam, social engineering, tấn công vật lý.
- Báo cáo từ công cụ quét tự động không có bằng chứng khai thác được.
- Thiếu header bảo mật hoặc thông tin phiên bản mà không có tác động cụ thể.

Khi kiểm thử, chỉ dùng môi trường của chính bạn. Không kiểm thử trên hệ thống hoặc dữ liệu của người khác, không truy cập, sửa hay xóa dữ liệu không thuộc về bạn.

### 10. Tài liệu và liên hệ

- Bản sửa và lỗ hổng đã xử lý được công bố tại tab **Security → Advisories** của repository và trong `CHANGELOG.md`.
- Quy trình đóng góp: [CONTRIBUTING.md](CONTRIBUTING.md). Giấy phép: [LICENSE](LICENSE), [NOTICE](NOTICE).
- Maintainer: @phanyen06ym-ien, @lexuanbao258-collab, @ngang02012007-crypto.

---

<a id="en"></a>

## OPENTRIX — Security Policy

### 1. Purpose and scope

This policy describes how to report and handle security vulnerabilities in the OPENTRIX (DX-OS Open-Core) source code in this repository: the headless core, the IT Helpdesk application, the Portal BFF, the frontend, and the sample deployment configuration. Third-party software (Keycloak, Apache APISIX, PostgreSQL, SeaweedFS, Node-RED…) has its own security policies; report issues in those projects themselves to the upstream project.

OPENTRIX is developed by the TRICORE student team for the OLP Open Source Software 2026 competition. Current releases are intended for evaluation and demonstration and **have not been audited for production use**.

### 2. Supported versions

| Version | Release status | Security support |
| --- | --- | --- |
| `main` | Development branch | Yes |
| `v0.1.0` | [Public pre-release](https://github.com/tricore-opentrix/opentrix/releases/tag/v0.1.0) published 2026-11-04 (with `dxos-open-core-0.1.0.tar.gz` and `SHA256SUMS`) | No — MVP for evaluation; use `main` |

There is no stable (non-pre-release) release yet. This table will be updated when a stable release is published; from then on, the latest stable release will also receive security support. Publication of a release does not mean that redistribution rights for all content have been verified; that is tracked in [Issue #138](https://github.com/tricore-opentrix/opentrix/issues/138).

### 3. Reporting a vulnerability

**Do not report vulnerabilities through public Issues, Pull Requests, Discussions, or social media.**

- **Primary channel:** GitHub Private Vulnerability Reporting — open the repository's **Security** tab and choose **Report a vulnerability**.
- **If that channel is unavailable:** open a public Issue titled `Security contact request` **without any vulnerability details**. A maintainer will respond and arrange for the report to be sent through a private channel.

### 4. Required report information

- Affected component and version (commit SHA or tag).
- Description of the vulnerability and its potential impact.
- Minimal reproduction steps and relevant environment configuration.
- Proof of concept, if available — using only invented data.
- Suggested fix, if any.
- How you would like to be credited (name or anonymous).

Do not attach real personal data, passwords, or tokens.

### 5. Vulnerability handling process

1. **Intake:** acknowledge receipt of the report.
2. **Triage:** reproduce and assess severity (with reference to CVSS) and affected components.
3. **Remediation:** develop the fix in a private branch or draft Security Advisory, with tests demonstrating both the denied and allowed paths.
4. **Verification:** independent review and CI before merge.
5. **Release and disclosure:** release the fix, update `CHANGELOG.md`, and publish a Security Advisory.

### 6. Response and disclosure timeline

| Step | Target |
| --- | --- |
| Acknowledgement | Within 3 business days |
| Initial assessment | Within 7 business days |
| Progress updates | At least every 14 days until resolved |
| Coordinated disclosure | After a fix is available, or at most 90 days after intake |

These are targets for a small team, not contractual commitments. Disclosure timing is agreed with the reporter; if a vulnerability is being actively exploited, the team may disclose earlier with mitigation guidance.

### 7. Security architecture boundaries

The boundaries below are design goals. Reports showing that any boundary can be crossed are in scope.

| Component | In-scope concerns |
| --- | --- |
| Keycloak / OIDC | Token validation (signature, issuer, audience, expiry), session handling, login flows and PKCE |
| API Gateway / APISIX | Gateway trust boundary, forged headers, authentication bypass, direct access to backend services |
| Core Workflow | Authorization checks, role escalation, invalid workflow transitions |
| Tenant isolation | Cross-tenant access, organization-level data authorization |
| PostgreSQL | SQL injection, database access rights, schema isolation |
| Object storage | Per-object authorization, credential exposure, unauthorized file access |
| Portal / BFF | Session security, CSRF, XSS, token relay |
| Sample infrastructure | TLS, secret handling, exposed ports, insecure defaults in compose files |

Deployment assumption: only the gateway is exposed to external networks; internal services never trust an identity or tenant supplied by a client without token validation.

### 8. Secure deployment guidance

- **Keycloak:** change the default admin password, use HTTPS, restrict redirect URIs, and enable MFA for administrator accounts.
- **APISIX:** expose only the gateway port; restrict the Admin API to the internal network and change the default admin key.
- **PostgreSQL:** use a separate least-privilege account per service; never expose the database port externally.
- **Object storage:** use dedicated access keys and do not make buckets public.
- **General:** never commit a real `.env`; replace every placeholder in `.env.example`; pin image versions; apply security updates for third-party components.
- **Demo accounts:** remove them or change their passwords before using real data.

### 9. Out-of-scope reports

- Vulnerabilities that exist only in unmodified third-party software — report them upstream.
- Issues caused by ignoring the deployment guidance (default passwords, internal ports exposed to the Internet…).
- Volumetric denial of service, spam, social engineering, or physical attacks.
- Automated scanner output without a demonstrated exploit.
- Missing security headers or version disclosure without concrete impact.

Test only against your own environment. Do not test against systems or data belonging to others, and do not access, modify, or delete data that is not yours.

### 10. References and contacts

- Fixes and resolved vulnerabilities are published under the repository's **Security → Advisories** tab and in `CHANGELOG.md`.
- Contribution process: [CONTRIBUTING.md](CONTRIBUTING.md). License: [LICENSE](LICENSE), [NOTICE](NOTICE).
- Maintainers: @phanyen06ym-ien, @lexuanbao258-collab, @ngang02012007-crypto.
