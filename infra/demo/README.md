<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# Local deployment

> **Language / Ngôn ngữ:** [English](#en) · [Tiếng Việt](#vi)

---

<a id="en"></a>

## Run OpenTrix locally with one command

One command starts PostgreSQL 17, Keycloak (realm `tricore`), the backend, the Portal BFF and the `integration-local` Portal behind Caddy HTTPS. Every service is built from source in Docker.

### Requirements

- Git and Docker with Docker Compose **2.24 or later**.
- Windows: **PowerShell 7.4 or later** (`winget install --id Microsoft.PowerShell`).
- At least 8 GB of RAM for Docker is recommended.

### Run

| Operating system | Command (from the repository root)                    |
| ---------------- | ----------------------------------------------------- |
| Windows          | `pwsh -File infra/demo/demo-up.ps1 -Gateway -TrustCa` |
| Linux / macOS    | `bash infra/demo/demo-up.sh --gateway`                |

- `-Gateway` / `--gateway`: put the APISIX API gateway in front of the backend.
- `-TrustCa` (Windows): trust the local HTTPS certificate; needed on the first run only.

On the first run the script generates `infra/.env` (already in `.gitignore`) with the database passwords, client secrets and the passwords of the three sample accounts. To change a password or display name, edit `infra/.env` and run `demo-up` again.

| Command                                         | Effect                                                 |
| ----------------------------------------------- | ------------------------------------------------------ |
| `demo-down.ps1` / `demo-down.sh`                | Stop and keep data (also stops APISIX if running)      |
| `demo-down.ps1 -Reset` / `demo-down.sh --reset` | Stop and delete all local data, including the local CA |

### Ports

| Host port        | Service                                                 |
| ---------------- | ------------------------------------------------------- |
| `127.0.0.1:8443` | Portal and BFF (Caddy HTTPS)                            |
| `127.0.0.1:8180` | Keycloak, issuer `http://localhost:8180/realms/tricore` |
| `127.0.0.1:9080` | APISIX, when started with `-Gateway` / `--gateway`      |

The backend (`8080`), BFF (`8081`) and PostgreSQL (`5432`) listen on `127.0.0.1` inside the shared network namespace only and are not exposed to the host.

### Sample accounts

| Account            | Role        |
| ------------------ | ----------- |
| `employee-demo`    | Employee    |
| `coordinator-demo` | Coordinator |
| `worker-demo`      | Technician  |

Passwords are in `infra/.env`. To switch roles in the same browser, select **Đăng xuất** (Sign out) and sign in with another account.

### HTTPS trust

Caddy creates a local CA; `demo-up` copies it to `infra/demo/.local/caddy-root.crt` (not committed). On Windows, run `demo-up.ps1 -TrustCa` once. After a full reset with `-Reset` / `--reset`, a new CA is created and must be trusted again.

### Troubleshooting

| Symptom                                                               | Fix                                                                                                                                                                                              |
| --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Windows reports `#requires ... PowerShell 7.4`                        | You are in Windows PowerShell 5.1. Install PowerShell 7 and run `pwsh -File infra/demo/demo-up.ps1`                                                                                              |
| Port `8443`, `8180` or `9080` is in use                               | Run `docker compose ls` to find the running project and stop it with `docker compose -p <name> stop`. Windows: `Get-NetTCPConnection -LocalPort 8443,8180,9080 -State Listen`; Linux: `ss -ltnp` |
| Error reading `compose.gateway.yml` (`!reset`)                        | Docker Compose 2.24 or later is required; update Docker Desktop                                                                                                                                  |
| Windows: curl reports `(60) … revocation status is unknown`           | The local CA has no CRL/OCSP. Use `curl.exe --ssl-revoke-best-effort --cacert infra/demo/.local/caddy-root.crt …`; `demo-up.ps1` already does this                                               |
| Browser certificate warning                                           | Run `demo-up.ps1 -TrustCa` (or import `caddy-root.crt` into the trust store), then restart the browser                                                                                           |
| Script prints `Portal chua len`                                       | Check the logs: `docker compose -f infra/compose.demo.yml logs backend portal-bff keycloak`. Low memory on Windows: set `memory=8GB` in `.wslconfig`, then `wsl --shutdown`                      |
| `db-init` exits with code 2 and logs `password authentication failed` | `infra/.env` was deleted or changed while old data remained. Run `demo-down.ps1 -Reset` / `demo-down.sh --reset`, then `demo-up` again                                                           |
| The app fails after pulling database changes                          | Run `demo-down.ps1 -Reset` / `demo-down.sh --reset`, then `demo-up` again                                                                                                                        |
| A `.sh` script fails with a stray `\r`                                | The file was converted to CRLF; `.gitattributes` enforces LF. Clone again with Git instead of copying files through Windows                                                                      |

---

<a id="vi"></a>

## Chạy OpenTrix trên máy cục bộ bằng một lệnh

Một lệnh dựng PostgreSQL 17, Keycloak (realm `tricore`), backend, Portal BFF và Portal `integration-local` sau Caddy HTTPS. Mọi service được build từ mã nguồn trong Docker.

### Yêu cầu

- Git và Docker kèm Docker Compose **2.24 trở lên**.
- Windows: **PowerShell 7.4 trở lên** (`winget install --id Microsoft.PowerShell`).
- Khuyến nghị tối thiểu 8 GB RAM cho Docker.

### Chạy

| Hệ điều hành  | Lệnh (tại thư mục gốc repo)                           |
| ------------- | ----------------------------------------------------- |
| Windows       | `pwsh -File infra/demo/demo-up.ps1 -Gateway -TrustCa` |
| Linux / macOS | `bash infra/demo/demo-up.sh --gateway`                |

- `-Gateway` / `--gateway`: bật cổng API APISIX phía trước backend.
- `-TrustCa` (Windows): tin cậy chứng chỉ HTTPS cục bộ; chỉ cần ở lần chạy đầu.

Lần đầu, script sinh `infra/.env` (đã có trong `.gitignore`) gồm mật khẩu cơ sở dữ liệu, secret client và mật khẩu ba tài khoản mẫu. Muốn đổi mật khẩu hoặc tên hiển thị: sửa `infra/.env` rồi chạy lại `demo-up`.

| Lệnh                                            | Tác dụng                                            |
| ----------------------------------------------- | --------------------------------------------------- |
| `demo-down.ps1` / `demo-down.sh`                | Dừng, giữ dữ liệu (dừng cả APISIX nếu đang chạy)    |
| `demo-down.ps1 -Reset` / `demo-down.sh --reset` | Dừng và xóa toàn bộ dữ liệu cục bộ, kể cả CA cục bộ |

### Cổng

| Cổng trên máy    | Dịch vụ                                                 |
| ---------------- | ------------------------------------------------------- |
| `127.0.0.1:8443` | Portal và BFF (Caddy HTTPS)                             |
| `127.0.0.1:8180` | Keycloak, issuer `http://localhost:8180/realms/tricore` |
| `127.0.0.1:9080` | APISIX, khi chạy kèm `-Gateway` / `--gateway`           |

Backend (`8080`), BFF (`8081`) và PostgreSQL (`5432`) chỉ nghe `127.0.0.1` bên trong namespace mạng dùng chung, không mở ra máy.

### Tài khoản mẫu

| Tài khoản          | Vai trò        |
| ------------------ | -------------- |
| `employee-demo`    | Nhân viên      |
| `coordinator-demo` | Điều phối viên |
| `worker-demo`      | Kỹ thuật viên  |

Mật khẩu nằm trong `infra/.env`. Đổi vai trò trên cùng trình duyệt: bấm **Đăng xuất** rồi đăng nhập bằng tài khoản khác.

### Tin cậy HTTPS

Caddy tự tạo CA cục bộ; `demo-up` chép CA ra `infra/demo/.local/caddy-root.crt` (không commit). Trên Windows, chạy `demo-up.ps1 -TrustCa` một lần. Sau khi xóa sạch bằng `-Reset` / `--reset`, CA mới được tạo và phải tin cậy lại.

### Xử lý lỗi thường gặp

| Dấu hiệu                                                           | Cách xử lý                                                                                                                                                                         |
| ------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Windows báo `#requires ... PowerShell 7.4`                         | Đang dùng Windows PowerShell 5.1. Cài PowerShell 7 rồi chạy bằng `pwsh -File infra/demo/demo-up.ps1`                                                                               |
| Cổng `8443`, `8180` hoặc `9080` đang bị chiếm                      | `docker compose ls` để xem project đang chạy, dừng bằng `docker compose -p <tên> stop`. Windows: `Get-NetTCPConnection -LocalPort 8443,8180,9080 -State Listen`; Linux: `ss -ltnp` |
| Lỗi đọc `compose.gateway.yml` (`!reset`)                           | Cần Docker Compose 2.24 trở lên; cập nhật Docker Desktop                                                                                                                           |
| Windows: curl báo `(60) … revocation status is unknown`            | CA cục bộ không có CRL/OCSP. Dùng `curl.exe --ssl-revoke-best-effort --cacert infra/demo/.local/caddy-root.crt …`; `demo-up.ps1` đã làm sẵn                                        |
| Trình duyệt cảnh báo chứng chỉ                                     | Chạy `demo-up.ps1 -TrustCa` (hoặc nhập `caddy-root.crt` vào kho tin cậy), đóng và mở lại trình duyệt                                                                               |
| Script báo `Portal chua len`                                       | Xem log: `docker compose -f infra/compose.demo.yml logs backend portal-bff keycloak`. Windows thiếu RAM: đặt `memory=8GB` trong `.wslconfig`, rồi `wsl --shutdown`                 |
| `db-init` dừng với exit 2, log có `password authentication failed` | `infra/.env` bị xóa hoặc đổi trong khi dữ liệu cũ còn. Chạy `demo-down.ps1 -Reset` / `demo-down.sh --reset` rồi `demo-up` lại                                                      |
| Kéo code mới có thay đổi cơ sở dữ liệu, ứng dụng lỗi               | `demo-down.ps1 -Reset` / `demo-down.sh --reset` rồi `demo-up` lại                                                                                                                  |
| Script `.sh` báo lỗi lạ có `\r`                                    | File bị chuyển sang CRLF; `.gitattributes` đã ép LF. Clone lại bằng Git, không sao chép file qua Windows                                                                           |
