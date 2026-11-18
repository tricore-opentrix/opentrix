<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# Infrastructure

> **Language / Ngôn ngữ:** [English](#en) · [Tiếng Việt](#vi)

---

<a id="en"></a>

## Overview

Container, gateway and identity configuration for running OpenTrix locally. To start the whole stack with one command, see [demo/README.md](https://github.com/tricore-opentrix/opentrix/blob/main/infra/demo/README.md).

### Contents

| Path                                                                                                                          | Purpose                                                                                                                                                                              |
| ----------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [`demo/`](https://github.com/tricore-opentrix/opentrix/tree/main/infra/demo)                                                  | One-command local deployment: `demo-up` / `demo-down` scripts (PowerShell 7 and Bash), Caddy HTTPS ingress, Dockerfiles and initialization scripts                                   |
| [`compose.demo.yml`](https://github.com/tricore-opentrix/opentrix/blob/main/infra/compose.demo.yml)                           | Docker Compose services: PostgreSQL, Keycloak, backend, Portal BFF, the Caddy ingress that serves the Portal, and one-shot initialization containers                                 |
| [`compose.gateway.yml`](https://github.com/tricore-opentrix/opentrix/blob/main/infra/compose.gateway.yml)                     | Optional overlay that routes API traffic through Apache APISIX                                                                                                                       |
| [`apisix/`](https://github.com/tricore-opentrix/opentrix/tree/main/infra/apisix)                                              | APISIX standalone configuration: routes, token validation against Keycloak JWKS, rate limiting                                                                                       |
| [`keycloak/`](https://github.com/tricore-opentrix/opentrix/tree/main/infra/keycloak)                                          | Keycloak realm `tricore` (clients and roles) and the OpenTrix login theme; see [keycloak/README.md](https://github.com/tricore-opentrix/opentrix/blob/main/infra/keycloak/README.md) |
| [`compose.workflow-postgres.yml`](https://github.com/tricore-opentrix/opentrix/blob/main/infra/compose.workflow-postgres.yml) | Disposable PostgreSQL 17 for backend integration tests; see [backend/README.md](https://github.com/tricore-opentrix/opentrix/blob/main/backend/README.md)                            |
| [`release/`](https://github.com/tricore-opentrix/opentrix/tree/main/infra/release)                                            | Dockerfiles used by the release workflow to build the backend and Portal BFF images                                                                                                  |

### Conventions

- Images are pinned to specific versions; `latest` is never used.
- Services bind to `127.0.0.1` only. Secrets are generated into `infra/.env`, which is never committed.
- This configuration is intended for local development and evaluation, not for production. See [docs/DEPLOYMENT.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/DEPLOYMENT.md) and [SECURITY.md](https://github.com/tricore-opentrix/opentrix/blob/main/SECURITY.md).

---

<a id="vi"></a>

## Tổng quan

Cấu hình container, cổng API và định danh để chạy OpenTrix trên máy cục bộ. Để dựng toàn bộ hệ thống bằng một lệnh, xem [demo/README.md](https://github.com/tricore-opentrix/opentrix/blob/main/infra/demo/README.md).

### Nội dung

| Đường dẫn                                                                                                                     | Mục đích                                                                                                                                                                                |
| ----------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`demo/`](https://github.com/tricore-opentrix/opentrix/tree/main/infra/demo)                                                  | Triển khai cục bộ bằng một lệnh: script `demo-up` / `demo-down` (PowerShell 7 và Bash), ingress HTTPS Caddy, Dockerfile và script khởi tạo                                              |
| [`compose.demo.yml`](https://github.com/tricore-opentrix/opentrix/blob/main/infra/compose.demo.yml)                           | Các dịch vụ Docker Compose: PostgreSQL, Keycloak, backend, Portal BFF, ingress Caddy phục vụ Portal và các container khởi tạo chạy một lần                                              |
| [`compose.gateway.yml`](https://github.com/tricore-opentrix/opentrix/blob/main/infra/compose.gateway.yml)                     | Lớp bổ sung tùy chọn, định tuyến lưu lượng API qua Apache APISIX                                                                                                                        |
| [`apisix/`](https://github.com/tricore-opentrix/opentrix/tree/main/infra/apisix)                                              | Cấu hình APISIX chạy độc lập: route, kiểm tra token qua JWKS của Keycloak, giới hạn tần suất                                                                                            |
| [`keycloak/`](https://github.com/tricore-opentrix/opentrix/tree/main/infra/keycloak)                                          | Realm Keycloak `tricore` (client và vai trò) và giao diện đăng nhập OpenTrix; xem [keycloak/README.md](https://github.com/tricore-opentrix/opentrix/blob/main/infra/keycloak/README.md) |
| [`compose.workflow-postgres.yml`](https://github.com/tricore-opentrix/opentrix/blob/main/infra/compose.workflow-postgres.yml) | PostgreSQL 17 dùng một lần cho test tích hợp backend; xem [backend/README.md](https://github.com/tricore-opentrix/opentrix/blob/main/backend/README.md)                                 |
| [`release/`](https://github.com/tricore-opentrix/opentrix/tree/main/infra/release)                                            | Dockerfile dùng trong workflow phát hành để build image backend và Portal BFF                                                                                                           |

### Quy ước

- Image được ghim phiên bản cụ thể, không dùng `latest`.
- Dịch vụ chỉ lắng nghe trên `127.0.0.1`. Bí mật được sinh vào `infra/.env` và không bao giờ được commit.
- Cấu hình này dành cho phát triển và chạy thử cục bộ, không dùng cho production. Xem [docs/DEPLOYMENT.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/DEPLOYMENT.md) và [SECURITY.md](https://github.com/tricore-opentrix/opentrix/blob/main/SECURITY.md).
