<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# Keycloak realm `tricore` (demo integration-local)

> **Trạng thái / Status:** Bản nháp cho vòng trường 19/11/2026 · **Issue:** [#119](https://github.com/tricore-opentrix/opentrix/issues/119) · **Quyết định / Decisions:** D1–D5 trong #119, [ADR-018](../../docs/08-decisions/ADR-018-apisix-api-gateway.md)

`tricore-realm.json` là nguồn sự thật cho realm demo. File **không chứa mật khẩu, secret, tên thật hay email thật**. Ba tài khoản demo có email giả `<username>@example.com` (tên miền dành riêng theo RFC 2606), chỉ để Keycloak 26 không bắt nhập hồ sơ (VERIFY_PROFILE) trong demo cục bộ; không gửi email nào. Secret client và mật khẩu người dùng được đặt lúc chạy từ `.env` cục bộ (đã nằm trong `.gitignore`).

`tricore-realm.json` is the source of truth for the demo realm. It contains **no passwords, secrets, real names or real emails**; the three demo users carry fake `<username>@example.com` addresses (RFC 2606 reserved domain) only so Keycloak 26 skips the VERIFY_PROFILE action locally, and no email is ever sent; client secrets and user passwords are set at runtime from a local, git-ignored `.env`.

## Issuer

`http://localhost:8180/realms/tricore` — dùng chung cho trình duyệt, BFF, backend và APISIX (D1). Các test backend cũng dùng đúng issuer này.

## Client

| Client | Loại / Type | Luồng bật / Enabled flows | Ghi chú / Notes |
|---|---|---|---|
| `tricore-api` | Resource (bearer-only) | — | Giữ 4 role mà backend đọc ở `resource_access.tricore-api.roles` |
| `dxos-portal-bff-local` | Confidential | Authorization Code + PKCE S256 | Redirect `https://localhost:8443/login/oauth2/code/keycloak`; post-logout `https://localhost:8443/`; audience `tricore-api`; scope giới hạn 4 role |
| `gateway-monitor` | Confidential | Service account | Chỉ cho `scripts/gateway-smoke.ps1`; role `workflow:read`; audience `tricore-api` |

Không client nào bật implicit flow hay direct access grants (password grant).

## Role và tài khoản / Roles and accounts

Role client `tricore-api`: `workflow:create`, `workflow:activate`, `workflow:transition`, `workflow:read`.

| Username | UUID (`sub`) | Role `tricore-api` | Helpdesk actor (submitter / coordinator / worker) |
|---|---|---|---|
| `employee-demo` | `d2a43dd7-e129-46f9-b09a-eccde2cde032` | create, activate, read, transition | true / false / false |
| `coordinator-demo` | `6afab46d-b455-41e7-a1cb-a2ec6d4841de` | read, transition | false / true / false |
| `worker-demo` | `b79f9591-e3bf-4428-a69b-06b523a5564a` | read, transition | false / false / true |
| `service-account-gateway-monitor` | `da54a88a-83cb-4e2f-9f52-71ef6d94641b` | read | false / false / false |

UUID cố định để mã actor trong DB (`oidc:<base64url(issuer)>.<base64url(sub)>`) không đổi giữa các lần nạp realm. Tên `Employee/Coordinator/Worker Demo` là tên giữ chỗ; tên hiển thị khi thi được gán từ `.env` lúc chạy.

## Kiểm tra / Verification

Gateway smoke yêu cầu **PowerShell 7.2 trở lên** và quyền đọc log Docker. Chạy `pwsh -File scripts/gateway-smoke.ps1 -ApisixContainer <ten-container-apisix>` từ gốc repo; secret monitor lấy từ `.env` hoặc environment. Script đối chiếu nonce của request không token với access log APISIX để xác nhận `401` và `upstream=-`; thiếu log tương quan thì BLOCKED. Golden Path tiếp tục BLOCKED cho đến khi có Portal/BFF và evidence thật từ #119. Exit code: `0` = tất cả PASS, `1` = có FAIL, `2` = có BLOCKED và không có FAIL.

Sau `infra/demo/spike/spike-up.sh`, chạy `infra/demo/spike/realm-check.sh`. Kết quả mong đợi: 4 dòng `OK` cho `iss`, `sub`, `aud`, `resource_access`; `GET /api/v1/mvp/requests` với token `gateway-monitor` trả **200**; `POST` trả **403**.

## Lưu ý / Notes

- Nạp lại realm bằng `realm-check.sh` sẽ xóa realm `tricore` cũ (dữ liệu demo dùng một lần).
- Đổi redirect URI, role hay UUID: sửa file JSON, báo trong #225, rồi nạp lại.
