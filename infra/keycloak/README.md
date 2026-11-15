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

Gateway smoke yêu cầu **PowerShell 7.2 trở lên** và quyền đọc log Docker. Chạy `pwsh -File scripts/gateway-smoke.ps1 -ApisixContainer <ten-container-apisix>` từ gốc repo; secret monitor lấy từ `.env` hoặc environment. Script đối chiếu nonce của request không token với access log APISIX để xác nhận `401` và `upstream=-`; thiếu log tương quan thì BLOCKED. Exit code: `0` = tất cả PASS, `1` = có FAIL, `2` = có BLOCKED và không có FAIL.

Sau `infra/demo/spike/spike-up.sh`, chạy `infra/demo/spike/realm-check.sh`. Kết quả mong đợi: 4 dòng `OK` cho `iss`, `sub`, `aud`, `resource_access`; `GET /api/v1/mvp/requests` với token `gateway-monitor` trả **200**; `POST` trả **403**.

## OpenTrix login theme (demo only)

- `themes/opentrix/login` kế thừa **`keycloak.v2` của Keycloak 26.8.0**. Theme chỉ bổ sung CSS, message bundle `vi`/`en` và hai SVG nội bộ (logo cỏ ba lá, hình minh họa yêu cầu hỗ trợ). **Không có bản sao FreeMarker (`*.ftl`), file `.js` hoặc form đăng nhập tự viết**: `login.ftl`, `field.ftl`, `template.ftl`, form username/password, cơ chế báo lỗi và xử lý OIDC/PKCE đều kế thừa từ Keycloak. React Portal vẫn chỉ có nút điều hướng `/oauth2/authorization/keycloak`.
- **Accessibility:** theme không ghi đè `field.ftl`; các trường nhập, validation và thông báo lỗi dùng template gốc Keycloak 26.8.0. Thuộc tính `aria-describedby` bổ sung ở thiết kế trước không được giữ lại. Khi thay đổi CSS hoặc nâng cấp Keycloak, kiểm tra bàn phím và trình đọc màn hình.
- Ngôn ngữ: realm bật `internationalizationEnabled`, `supportedLocales: ["vi"]`, `defaultLocale: "vi"` để trang render `<html lang="vi">` (WCAG 3.1.1). Chỉ có `vi` nên không hiện bộ chọn ngôn ngữ và trình duyệt gửi `Accept-Language: en` vẫn thấy tiếng Việt. Muốn hỗ trợ tiếng Anh: thêm `"en"` vào `supportedLocales` (Keycloak sẽ chọn theo `Accept-Language`/`ui_locales` và hiện bộ chọn ngôn ngữ — cần kiểm tra lại giao diện bộ chọn). Hệ quả phụ: các trang khác của realm `tricore` (account console, email) cũng dùng tiếng Việt; realm `master`/Admin Console không bị ảnh hưởng.
- Bố cục hai cột ("Calm Enterprise Workspace") dựng hoàn toàn trên DOM gốc: `#kc-header` thành cột thương hiệu, `<main>` giữ nguyên form của Keycloak. Nội dung cột thương hiệu nằm ở message key `loginTitleHtml` — Keycloak render key này qua `kcSanitize()`, nên chỉ được chứa `div/span/p/ul/li` + `class` (test `test_brand_panel_is_inert_markup_and_assets_are_local` chặn link, ảnh, script, URL ngoài). Nhãn `integration-local` trong key này là cố ý vì theme chỉ dùng cho demo cục bộ; nếu tái sử dụng cho môi trường khác phải sửa message.
- `messages_vi.properties` giữ toàn bộ chữ tiếng Việt; thông báo lỗi đăng nhập giữ nguyên nghĩa gốc (không tiết lộ trường nào sai hay tài khoản có tồn tại không). `messages_en.properties` chỉ chứa cột thương hiệu bằng tiếng Anh; nhãn và lỗi tiếng Anh kế thừa từ Keycloak.
- Font: ưu tiên `Be Vietnam Pro` nếu máy có sẵn, nếu không dùng `Segoe UI`/font hệ thống. Theme **không** nhúng file font và không tải từ CDN.
- Khi nâng phiên bản Keycloak: bố cục phụ thuộc các class PatternFly 5 (`pf-v5-c-login__*`, `pf-v5-c-form-control`) và id `#kc-header-wrapper`, `#kc-page-title`. Nếu Keycloak đổi DOM, form vẫn hoạt động nhưng giao diện có thể lùi về mặc định — cần kiểm tra lại bằng trình duyệt.
- `infra/compose.demo.yml` mount theme read-only tại `/opt/keycloak/themes/opentrix`. `tricore-realm.json` bật `loginTheme: opentrix` cho **realm mới**; `kc-init.sh` cập nhật cùng trường cho **realm đã tồn tại** khi init job chạy lại.
- **Nạp theme cho realm đã tồn tại:** sau khi xác nhận theme đã được mount, dùng Keycloak Admin Console → Realm `tricore` → Realm Settings → Themes → Login Theme → `opentrix` → Save; hoặc chạy `kcadm.sh update realms/tricore -s loginTheme=opentrix` trong phiên quản trị đã xác thực. Chỉ thao tác trên Compose project demo được phép quản trị; không reset volume. Không cần chạy lại toàn bộ `kc-init.sh` chỉ để đổi giao diện, vì script đó còn đặt lại mật khẩu demo và client secrets từ `.env`. Kiểm tra Compose tại gốc repo: `docker compose -f infra/compose.demo.yml config` (có thể cần `.env` hợp lệ trong `infra/`).
- **Kiểm tra giao diện trong trình duyệt:** mở Portal → trang đăng nhập Keycloak, xác minh logo và CSS OpenTrix; nhập sai để kiểm tra thông báo lỗi; đăng nhập và đăng xuất bằng tài khoản demo. Xác nhận URL vẫn thuộc `localhost:8180/realms/tricore`, các trường username/password hoạt động bình thường và giao diện dùng được bằng bàn phím và trên màn hình di động.
- Nếu có lỗi giao diện hoặc cần quay về theme mặc định, làm theo mục **Rollback realm đang chạy** bên dưới. Không thay đổi issuer, client, role, session hoặc xóa volume.
- CI bắt buộc chạy `python3 -m unittest discover -s scripts -p 'test_opentrix_*.py'` trong job `repo-hygiene`. Đây chỉ là kiểm thử tĩnh, **không thay** kiểm thử đăng nhập/đăng xuất bằng Keycloak thật.

### Rollback realm đang chạy / Existing-realm rollback

Thực hiện trên môi trường demo được phép quản trị; ưu tiên Compose project thử nghiệm cô lập. Giữ nguyên database/volume, realm, tài khoản, OIDC và cấu hình BFF.

1. **Đổi ngay trên realm đang chạy** (không đủ nếu chỉ sửa JSON trong Git):
   - **Admin Console:** chọn realm `tricore` → **Realm Settings → Themes → Login Theme** → `keycloak.v2` → Save.
   - **Hoặc Admin CLI**, trong môi trường có `kcadm.sh` đã được xác thực bằng tài khoản quản trị (không in mật khẩu/secret ra terminal hoặc log):

   ```bash
   kcadm.sh get realms/tricore --fields loginTheme
   kcadm.sh update realms/tricore -s loginTheme=keycloak.v2
   kcadm.sh get realms/tricore --fields loginTheme
   ```

   Lệnh `get` cuối phải trả về `loginTheme: keycloak.v2`. Kiểm tra trang đăng nhập thật trong trình duyệt trở lại giao diện gốc, lỗi đăng nhập vẫn hiển thị. Không kết luận PASS chỉ từ kết quả CLI.
2. **Giữ rollback sau lần triển khai tiếp theo:** trong cấu hình triển khai, đổi `loginTheme` trong `infra/keycloak/tricore-realm.json` sang `keycloak.v2`, đồng thời bỏ/đổi lệnh `kcadm update ... loginTheme=opentrix` trong `infra/demo/init/kc-init.sh`. Nếu không, lần chạy lại `kc-init` sẽ kích hoạt theme OpenTrix trở lại. Chỉ triển khai cấu hình rollback khi cả hai file đã được điều chỉnh đồng bộ.
3. **Xác nhận tính bền vững:** trên Compose project demo thử nghiệm riêng, dùng `kcadm.sh get realms/tricore --fields loginTheme` trước và sau một lần khởi động lại có kiểm soát; xác minh màn hình đăng nhập vẫn sử dụng `keycloak.v2` và dữ liệu volume còn nguyên. Không chạy `down -v`, không xóa realm và không chạy script tái tạo realm. Chỉ chạy lại `kc-init` khi chấp nhận các tác động phụ: script cập nhật client secret và mật khẩu demo từ `.env`.
4. **Nếu thất bại:** nếu lệnh update bị từ chối, kiểm tra endpoint, quyền admin và kết nối; không reset volume. Nếu đã đổi realm mà giao diện vẫn là OpenTrix, kiểm tra realm đang chọn, cache trình duyệt và việc `kc-init` có chạy lại không. Nếu rollback mất hiệu lực sau restart, điều chỉnh đồng bộ `tricore-realm.json` và `kc-init.sh` trước khi thử lại.

- Theme này không sửa theme của realm `master`, màn Admin Console hoặc bất kỳ hệ thống production nào.

## Lưu ý / Notes

- Nạp lại realm bằng `realm-check.sh` sẽ xóa realm `tricore` cũ (dữ liệu demo dùng một lần).
- Đổi redirect URI, role hay UUID: sửa file JSON, báo trong #225, rồi nạp lại.
