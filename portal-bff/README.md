<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# Portal BFF

> **Language / Ngôn ngữ:** [English](#en) · [Tiếng Việt](#vi)

---

<a id="en"></a>

## Overview

The Portal BFF (backend for frontend) is a Spring Boot 3.5 application (Java 21) that sits between the React Portal and the backend. It signs users in with Keycloak, keeps the session on the server and forwards allowed IT Helpdesk requests to the backend. The browser never receives an access token.

```
Browser ── HTTPS ──> Caddy ingress ──> Portal BFF ── Bearer token ──> Backend
                          │                 │
                          └─ Portal (static) └─ Keycloak (OIDC)
```

Related documentation: [docs/API.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/API.md) · [docs/INTEGRATION.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/INTEGRATION.md) · [frontend/README.md](https://github.com/tricore-opentrix/opentrix/blob/main/frontend/README.md) · [infra/keycloak/README.md](https://github.com/tricore-opentrix/opentrix/blob/main/infra/keycloak/README.md)

### Endpoints

| Path | Method | Access | Purpose |
| --- | --- | --- | --- |
| `/oauth2/authorization/keycloak` | GET | Public | Starts the OIDC Authorization Code flow with PKCE (S256) |
| `/login/oauth2/code/keycloak` | GET | Public | OIDC callback |
| `/bff/session` | GET | Public | Returns `{"authenticated":false}` or `{"authenticated":true,"csrfToken":"…"}` |
| `/bff/logout` | POST | Signed in, CSRF | Ends the session and signs out of Keycloak |
| `/bff/api/v1/mvp/requests` | GET, POST | Signed in, CSRF for POST | Lists and creates Helpdesk requests |
| `/bff/api/v1/mvp/requests/{id}` | GET | Signed in | Request detail |
| `/bff/api/v1/mvp/requests/{id}/history` | GET | Signed in | Request history |
| `/bff/api/v1/mvp/requests/{id}/{action}` | POST | Signed in, CSRF | `action` is one of `triage`, `assign`, `start`, `resolve`, `confirm` |

Any other `/bff/**` path is denied. These nine routes map one to one to the backend Helpdesk API under `/api/v1/mvp/requests`.

### Security behavior

- **Session cookie:** `__Host-DXOS-Portal`, `Secure`, `HttpOnly`, `SameSite=Lax`, path `/`, 30-minute timeout. `SameSite=Lax` lets the top-level OIDC callback carry the login cookie.
- **CSRF:** enabled. Writes and logout must send the token from `/bff/session` in the `X-CSRF-TOKEN` header.
- **Tokens:** the access and refresh tokens stay in the server session. Only the access token is sent to the backend, as `Authorization: Bearer`. Browser headers and cookies are not forwarded.
- **Expired session:** if the token cannot be used or refreshed, the session is invalidated and the API returns `401`.
- **Backend responses:** redirects are not followed. Request bodies are limited to 32 KB and responses to 2 MB. If the backend cannot be reached during a write, the BFF returns `503` with `COMMIT_OUTCOME_UNKNOWN` and does not retry; the client checks the result by reading the request detail or history.
- **Startup checks:** the BFF refuses to start unless the Keycloak client is confidential (`client_secret_basic`), is not the backend client `tricore-api`, uses the Authorization Code grant and has the callback `${PORTAL_PUBLIC_ORIGIN}/login/oauth2/code/keycloak`. The public origin must be an HTTPS origin without a path; the backend URL must be HTTPS or `http://127.0.0.1`.
- The BFF listens on `127.0.0.1` only. It must run behind a trusted HTTPS reverse proxy that serves the Portal on the same origin.

### Configuration

| Environment variable | Example (local deployment) | Description |
| --- | --- | --- |
| `SERVER_PORT` | `8081` | HTTP port on `127.0.0.1` |
| `PORTAL_PUBLIC_ORIGIN` | `https://localhost:8443` | Public HTTPS origin of the Portal |
| `PORTAL_OIDC_REDIRECT_URI` | `https://localhost:8443/login/oauth2/code/keycloak` | OIDC callback; must equal `${PORTAL_PUBLIC_ORIGIN}/login/oauth2/code/keycloak` |
| `PORTAL_OIDC_ISSUER_URI` | `http://localhost:8180/realms/tricore` | Keycloak issuer; must match the backend issuer exactly |
| `PORTAL_OIDC_CLIENT_ID` | `dxos-portal-bff-local` | Confidential Keycloak client |
| `PORTAL_OIDC_CLIENT_SECRET` | from `infra/.env` | Client secret; supply it from a secret store, never commit it |
| `PORTAL_BACKEND_BASE_URL` | `http://127.0.0.1:8080` | Backend origin |

The Keycloak client settings for the local deployment are described in [infra/keycloak/README.md](https://github.com/tricore-opentrix/opentrix/blob/main/infra/keycloak/README.md).

### Run locally

The simplest way is the one-command local deployment, which starts the BFF with Keycloak, the backend, PostgreSQL and the Caddy ingress: see [infra/demo/README.md](https://github.com/tricore-opentrix/opentrix/blob/main/infra/demo/README.md).

To run the BFF on its own, set the variables above and start it with the backend Gradle wrapper (the BFF has no wrapper of its own):

```bash
./backend/gradlew -p portal-bff bootRun
```

[Caddyfile.local](https://github.com/tricore-opentrix/opentrix/blob/main/portal-bff/Caddyfile.local) is a loopback-only HTTPS ingress for this setup: it serves `frontend/dist`, routes `/bff/*`, `/oauth2/authorization/*` and `/login/oauth2/code/*` to port 8081, and returns `404` for `/api/*`. Build the Portal with `npm run build:integration-local` first (see [frontend/README.md](https://github.com/tricore-opentrix/opentrix/blob/main/frontend/README.md)).

### Tests

```bash
./backend/gradlew -p portal-bff test
```

The tests cover the session endpoint, CSRF, PKCE, the confidential-client and origin checks, bearer forwarding, rejection of redirects and forged headers, error propagation and the no-retry rule for writes. They use a mocked identity provider and backend; a sign-in against a running Keycloak can be checked with the local deployment.

---

<a id="vi"></a>

## Tổng quan

Portal BFF (backend for frontend) là ứng dụng Spring Boot 3.5 (Java 21) đứng giữa Portal React và backend. BFF đăng nhập người dùng qua Keycloak, giữ phiên ở phía máy chủ và chuyển tiếp các yêu cầu IT Helpdesk được phép tới backend. Trình duyệt không bao giờ nhận access token.

```
Trình duyệt ── HTTPS ──> Ingress Caddy ──> Portal BFF ── Bearer token ──> Backend
                              │                 │
                              └─ Portal (tĩnh)  └─ Keycloak (OIDC)
```

Tài liệu liên quan: [docs/API.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/API.md) · [docs/INTEGRATION.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/INTEGRATION.md) · [frontend/README.md](https://github.com/tricore-opentrix/opentrix/blob/main/frontend/README.md) · [infra/keycloak/README.md](https://github.com/tricore-opentrix/opentrix/blob/main/infra/keycloak/README.md)

### Endpoint

| Đường dẫn | Phương thức | Quyền truy cập | Mục đích |
| --- | --- | --- | --- |
| `/oauth2/authorization/keycloak` | GET | Công khai | Bắt đầu luồng OIDC Authorization Code với PKCE (S256) |
| `/login/oauth2/code/keycloak` | GET | Công khai | Callback OIDC |
| `/bff/session` | GET | Công khai | Trả về `{"authenticated":false}` hoặc `{"authenticated":true,"csrfToken":"…"}` |
| `/bff/logout` | POST | Đã đăng nhập, CSRF | Kết thúc phiên và đăng xuất khỏi Keycloak |
| `/bff/api/v1/mvp/requests` | GET, POST | Đã đăng nhập, CSRF cho POST | Liệt kê và tạo yêu cầu Helpdesk |
| `/bff/api/v1/mvp/requests/{id}` | GET | Đã đăng nhập | Chi tiết yêu cầu |
| `/bff/api/v1/mvp/requests/{id}/history` | GET | Đã đăng nhập | Lịch sử yêu cầu |
| `/bff/api/v1/mvp/requests/{id}/{action}` | POST | Đã đăng nhập, CSRF | `action` là một trong `triage`, `assign`, `start`, `resolve`, `confirm` |

Mọi đường dẫn `/bff/**` khác đều bị từ chối. Chín route này tương ứng một-một với API Helpdesk của backend tại `/api/v1/mvp/requests`.

### Cơ chế bảo mật

- **Cookie phiên:** `__Host-DXOS-Portal`, `Secure`, `HttpOnly`, `SameSite=Lax`, path `/`, hết hạn sau 30 phút. `SameSite=Lax` cho phép callback OIDC cấp cao nhất mang theo cookie đăng nhập.
- **CSRF:** được bật. Các thao tác ghi và đăng xuất phải gửi token lấy từ `/bff/session` trong header `X-CSRF-TOKEN`.
- **Token:** access token và refresh token nằm trong phiên phía máy chủ. Chỉ access token được gửi tới backend, dưới dạng `Authorization: Bearer`. Header và cookie của trình duyệt không được chuyển tiếp.
- **Phiên hết hạn:** nếu không dùng hoặc làm mới được token, phiên bị hủy và API trả `401`.
- **Phản hồi từ backend:** không đi theo redirect. Nội dung yêu cầu giới hạn 32 KB, phản hồi giới hạn 2 MB. Nếu không liên lạc được backend khi đang ghi, BFF trả `503` với `COMMIT_OUTCOME_UNKNOWN` và không thử lại; phía client kiểm tra kết quả bằng cách đọc chi tiết hoặc lịch sử yêu cầu.
- **Kiểm tra khi khởi động:** BFF không chạy nếu client Keycloak không phải confidential (`client_secret_basic`), trùng với client backend `tricore-api`, không dùng Authorization Code hoặc callback khác `${PORTAL_PUBLIC_ORIGIN}/login/oauth2/code/keycloak`. Origin công khai phải là HTTPS và không có path; URL backend phải là HTTPS hoặc `http://127.0.0.1`.
- BFF chỉ lắng nghe trên `127.0.0.1`. BFF phải chạy sau một reverse proxy HTTPS tin cậy, phục vụ Portal trên cùng origin.

### Cấu hình

| Biến môi trường | Ví dụ (triển khai cục bộ) | Mô tả |
| --- | --- | --- |
| `SERVER_PORT` | `8081` | Cổng HTTP trên `127.0.0.1` |
| `PORTAL_PUBLIC_ORIGIN` | `https://localhost:8443` | Origin HTTPS công khai của Portal |
| `PORTAL_OIDC_REDIRECT_URI` | `https://localhost:8443/login/oauth2/code/keycloak` | Callback OIDC; phải bằng `${PORTAL_PUBLIC_ORIGIN}/login/oauth2/code/keycloak` |
| `PORTAL_OIDC_ISSUER_URI` | `http://localhost:8180/realms/tricore` | Issuer của Keycloak; phải khớp chính xác với issuer của backend |
| `PORTAL_OIDC_CLIENT_ID` | `dxos-portal-bff-local` | Client Keycloak loại confidential |
| `PORTAL_OIDC_CLIENT_SECRET` | lấy từ `infra/.env` | Secret của client; cấp qua kho bí mật, không bao giờ commit |
| `PORTAL_BACKEND_BASE_URL` | `http://127.0.0.1:8080` | Origin của backend |

Cấu hình client Keycloak cho triển khai cục bộ được mô tả trong [infra/keycloak/README.md](https://github.com/tricore-opentrix/opentrix/blob/main/infra/keycloak/README.md).

### Chạy cục bộ

Cách đơn giản nhất là triển khai cục bộ bằng một lệnh, dựng BFF cùng Keycloak, backend, PostgreSQL và ingress Caddy: xem [infra/demo/README.md](https://github.com/tricore-opentrix/opentrix/blob/main/infra/demo/README.md).

Để chạy riêng BFF, đặt các biến ở trên rồi khởi động bằng Gradle wrapper của backend (BFF không có wrapper riêng):

```bash
./backend/gradlew -p portal-bff bootRun
```

[Caddyfile.local](https://github.com/tricore-opentrix/opentrix/blob/main/portal-bff/Caddyfile.local) là ingress HTTPS chỉ lắng nghe trên loopback cho cách chạy này: phục vụ `frontend/dist`, chuyển `/bff/*`, `/oauth2/authorization/*` và `/login/oauth2/code/*` tới cổng 8081, và trả `404` cho `/api/*`. Build Portal bằng `npm run build:integration-local` trước (xem [frontend/README.md](https://github.com/tricore-opentrix/opentrix/blob/main/frontend/README.md)).

### Kiểm thử

```bash
./backend/gradlew -p portal-bff test
```

Các test bao phủ endpoint phiên, CSRF, PKCE, kiểm tra client confidential và origin, chuyển tiếp bearer token, từ chối redirect và header giả mạo, truyền mã lỗi và quy tắc không thử lại khi ghi. Test dùng identity provider và backend giả lập; việc đăng nhập với Keycloak thật có thể kiểm tra bằng triển khai cục bộ.
