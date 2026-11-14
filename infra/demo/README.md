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
| Windows (PowerShell **7.4+**) | `pwsh infra/demo/demo-up.ps1` (thêm `-TrustCa` lần đầu, `-Gateway` để bật APISIX) |
| Linux / macOS | `bash infra/demo/demo-up.sh` (thêm `--gateway` để bật APISIX) |

Lần đầu script sinh `infra/.env` (đã nằm trong `.gitignore`) gồm mật khẩu DB, secret client và mật khẩu 3 tài khoản demo. Muốn đổi mật khẩu hoặc tên hiển thị: sửa `infra/.env` rồi chạy lại `demo-up`.

Dừng: `demo-down` (giữ dữ liệu) · xóa sạch: `demo-down -Reset` / `demo-down.sh --reset`. `demo-down` luôn dừng cả APISIX nếu đang chạy.

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

## Xử lý lỗi thường gặp

| Dấu hiệu | Cách xử lý |
|---|---|
| Cổng `8443`, `8180` hoặc `9080` đang bị chiếm | `docker compose ls` để xem project nào đang chạy, dừng project đó (`docker compose -p <tên> stop`). Windows: `Get-NetTCPConnection -LocalPort 8443,8180,9080 -State Listen`; Linux: `ss -ltnp` |
| Lỗi đọc `compose.gateway.yml` (`!reset`) | Cần Docker Compose **2.24 trở lên**; cập nhật Docker Desktop |
| Windows: curl báo `(60) … revocation status is unknown` | CA cục bộ của Caddy không có CRL/OCSP. Dùng `curl.exe --ssl-revoke-best-effort --cacert infra/demo/.local/caddy-root.crt …`; `demo-up.ps1` đã làm sẵn |
| Trình duyệt cảnh báo chứng chỉ | Chạy `demo-up.ps1 -TrustCa` (hoặc nhập `caddy-root.crt` vào kho tin cậy), đóng và mở lại trình duyệt. Sau `-Reset` phải tin cậy lại |
| Script báo `Portal chua len` | Xem `docker compose -f infra/compose.demo.yml logs backend portal-bff keycloak`. Windows thiếu RAM: tăng `memory=8GB` trong `.wslconfig`, rồi `wsl --shutdown` |
| Kéo code mới có thay đổi DB, ứng dụng lỗi | `demo-down --reset` (xóa dữ liệu demo) rồi `demo-up` lại |
| Script `.sh` báo lỗi lạ có `\r` | File bị đổi sang CRLF; `.gitattributes` đã ép LF. Clone lại bằng Git thông thường, đừng sao chép qua Windows |
