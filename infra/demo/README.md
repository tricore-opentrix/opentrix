<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# Demo integration-local (vòng trường 19/11)

> **Issue:** [#119](https://github.com/tricore-opentrix/opentrix/issues/119) · **Theo dõi:** [#225](https://github.com/tricore-opentrix/opentrix/issues/225) · **Chế độ:** integration-local (không phải LIVE)

Một lệnh dựng PostgreSQL 17, Keycloak (realm `tricore`), backend, Portal BFF và Portal `integration-local` sau Caddy HTTPS. Mọi service build từ mã nguồn trong Docker.

## Chạy

| Hệ điều hành | Lệnh (tại thư mục gốc repo) |
|---|---|
| Windows (PowerShell **7.4+**) | `pwsh infra/demo/demo-up.ps1` (thêm `-TrustCa` lần đầu) |
| Linux / macOS | `bash infra/demo/demo-up.sh` |

Lần đầu script sinh `infra/.env` (đã nằm trong `.gitignore`) gồm mật khẩu DB, secret client và mật khẩu 3 tài khoản demo. Muốn đổi mật khẩu hoặc tên hiển thị: sửa `infra/.env` rồi chạy lại `demo-up`.

Dừng: `demo-down` (giữ dữ liệu) · xóa sạch: `demo-down -Reset` / `demo-down.sh --reset`.

## Cổng / Ports

| Cổng trên máy | Dịch vụ |
|---|---|
| `127.0.0.1:8443` | Portal + BFF (Caddy HTTPS) |
| `127.0.0.1:8180` | Keycloak, issuer `http://localhost:8180/realms/tricore` |
| `127.0.0.1:9080` | APISIX — chỉ khi bật overlay `infra/compose.gateway.yml` (#116) |

Backend (`8080`), BFF (`8081`) và PostgreSQL (`5432`) chỉ nghe `127.0.0.1` bên trong namespace chung, không mở ra máy (D1).

## Tài khoản demo

`employee-demo` (người gửi), `coordinator-demo` (điều phối), `worker-demo` (kỹ thuật viên). Mỗi vai đăng nhập bằng **một browser profile riêng**. Không ghi tên thật vào repo, ảnh chụp hay slide.

## Tin cậy HTTPS

Caddy tự tạo CA cục bộ; `demo-up` chép CA ra `infra/demo/.local/caddy-root.crt` (không commit). Windows: chạy `demo-up.ps1 -TrustCa` một lần. Khi xóa sạch bằng `-Reset`, CA mới được tạo và phải tin cậy lại.
