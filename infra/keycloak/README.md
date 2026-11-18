<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# Keycloak realm `tricore`

> **Language / Ngôn ngữ:** [English](#en) · [Tiếng Việt](#vi)

---

<a id="en"></a>

## Overview

Keycloak configuration for running OpenTrix locally: the `tricore` realm, its clients and roles,
and the OpenTrix login theme. Architecture decision: [ADR-018](https://github.com/tricore-opentrix/opentrix/blob/main/docs/08-decisions/ADR-018-apisix-api-gateway.md).

`tricore-realm.json` is the source of truth for the realm. It contains **no passwords, secrets,
real names or real email addresses**. The three sample users have placeholder
`<username>@example.com` addresses (a reserved domain under RFC 2606) only so that Keycloak 26
skips the profile verification step; no email is ever sent. Client secrets and user passwords are
set at runtime from the local, git-ignored `infra/.env`.

## Issuer

`http://localhost:8180/realms/tricore` is shared by the browser, Portal BFF, backend and APISIX.
Backend tests use the same issuer.

## Clients

| Client                  | Type                   | Enabled flows                  | Notes                                                                                                                                                        |
| ----------------------- | ---------------------- | ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `tricore-api`           | Resource (bearer-only) | —                              | Holds the four roles the backend reads from `resource_access.tricore-api.roles`                                                                              |
| `dxos-portal-bff-local` | Confidential           | Authorization Code + PKCE S256 | Redirect `https://localhost:8443/login/oauth2/code/keycloak`; post-logout `https://localhost:8443/`; audience `tricore-api`; scope limited to the four roles |
| `gateway-monitor`       | Confidential           | Service account                | Used only by `scripts/gateway-smoke.ps1`; role `workflow:read`; audience `tricore-api`                                                                       |

No client enables the implicit flow or direct access grants (password grant).

## Roles and accounts

Client roles on `tricore-api`: `workflow:create`, `workflow:activate`, `workflow:transition`,
`workflow:read`.

| Username                          | UUID (`sub`)                           | `tricore-api` roles                | Helpdesk actor (submitter / coordinator / worker) |
| --------------------------------- | -------------------------------------- | ---------------------------------- | ------------------------------------------------- |
| `employee-demo`                   | `d2a43dd7-e129-46f9-b09a-eccde2cde032` | create, activate, read, transition | true / false / false                              |
| `coordinator-demo`                | `6afab46d-b455-41e7-a1cb-a2ec6d4841de` | read, transition                   | false / true / false                              |
| `worker-demo`                     | `b79f9591-e3bf-4428-a69b-06b523a5564a` | read, transition                   | false / false / true                              |
| `service-account-gateway-monitor` | `da54a88a-83cb-4e2f-9f52-71ef6d94641b` | read                               | false / false / false                             |

UUIDs are fixed so that the actor identifier stored in the database
(`oidc:<base64url(issuer)>.<base64url(sub)>`) does not change when the realm is reloaded. The
names `Employee/Coordinator/Worker Demo` are placeholders; display names are set from `infra/.env`
at runtime.

## Verification

- **Gateway smoke test** (requires PowerShell 7.2 or later and permission to read Docker logs):
  run `pwsh -File scripts/gateway-smoke.ps1 -ApisixContainer <apisix-container-name>` from the
  repository root. The monitor secret is read from `infra/.env` or the environment. The script
  matches the nonce of an unauthenticated request against the APISIX access log to confirm `401`
  and `upstream=-`; without a correlated log entry the result is BLOCKED. Exit codes: `0` all
  passed, `1` at least one failure, `2` blocked with no failure.
- **Realm check:** after `infra/demo/spike/spike-up.sh`, run `infra/demo/spike/realm-check.sh`.
  Expected: four `OK` lines for `iss`, `sub`, `aud` and `resource_access`;
  `GET /api/v1/mvp/requests` with a `gateway-monitor` token returns **200** and `POST` returns
  **403**.

## OpenTrix login theme

- `themes/opentrix/login` extends the **`keycloak.v2` theme of Keycloak 26.8.0**. It adds only CSS,
  `vi`/`en` message bundles and two local SVG files (logo and illustration). There are **no copied
  FreeMarker templates (`*.ftl`), JavaScript files or custom login forms**: `login.ftl`,
  `field.ftl`, `template.ftl`, the username/password form, error handling and the OIDC/PKCE flow
  are all inherited from Keycloak. The React Portal only links to
  `/oauth2/authorization/keycloak`.
- **Accessibility:** the theme does not override `field.ftl`, so input fields, validation and
  error messages use the Keycloak 26.8.0 templates. Check keyboard and screen-reader use whenever
  the CSS changes or Keycloak is upgraded.
- **Language:** the realm sets `internationalizationEnabled`, `supportedLocales: ["vi"]` and
  `defaultLocale: "vi"`, so pages render with `<html lang="vi">`. With a single locale no language
  selector is shown, and a browser sending `Accept-Language: en` still sees Vietnamese. To add
  English, add `"en"` to `supportedLocales`; Keycloak then selects the language from
  `Accept-Language` or `ui_locales` and shows a language selector, which should be checked in the
  browser. Other pages of the `tricore` realm (account console, emails) also use Vietnamese; the
  `master` realm and the Admin Console are not affected.
- **Layout:** the two-column layout is built on Keycloak's own DOM: `#kc-header` becomes the brand
  column and `<main>` keeps Keycloak's form. The brand column content comes from the
  `loginTitleHtml` message key, which Keycloak renders through `kcSanitize()`, so it may contain
  only `div`, `span`, `p`, `ul`, `li` and `class` attributes. The test
  `test_brand_panel_is_inert_markup_and_assets_are_local` rejects links, images, scripts and
  external URLs. The `integration-local` label in this key is intentional; change the message if
  the theme is reused in another environment.
- **Messages:** `messages_vi.properties` holds all Vietnamese text; login error messages keep
  their original meaning and do not reveal which field was wrong or whether an account exists.
  `messages_en.properties` contains only the brand column; English labels and errors are inherited
  from Keycloak.
- **Fonts:** `Be Vietnam Pro` is used if installed, otherwise `Segoe UI` or the system font. The
  theme does not bundle font files or load them from a CDN.
- **Upgrading Keycloak:** the layout depends on PatternFly 5 classes (`pf-v5-c-login__*`,
  `pf-v5-c-form-control`) and the ids `#kc-header-wrapper` and `#kc-page-title`. If Keycloak changes
  its DOM, the form keeps working but the styling may fall back to the default; check it in a
  browser.
- **Deployment:** `infra/compose.demo.yml` mounts the theme read-only at
  `/opt/keycloak/themes/opentrix`. `tricore-realm.json` sets `loginTheme: opentrix` for a **new
  realm**, and `infra/demo/init/kc-init.sh` sets the same field on an **existing realm** when the
  init job runs again.
- **Enabling the theme on an existing realm:** after confirming the theme is mounted, open the
  Admin Console → realm `tricore` → **Realm Settings → Themes → Login Theme** → `opentrix` →
  **Save**, or run `kcadm.sh update realms/tricore -s loginTheme=opentrix` in an authenticated
  admin session. Do not rerun the whole `kc-init.sh` only to change the theme, because it also
  resets sample passwords and client secrets from `infra/.env`. To validate the Compose file, run
  `docker compose -f infra/compose.demo.yml config` from the repository root (a valid
  `infra/.env` may be required).
- **Browser check:** open the Portal, go to the Keycloak login page and verify the OpenTrix logo
  and styling; enter wrong credentials to check the error message; sign in and sign out with a
  sample account. Confirm the URL stays on `localhost:8180/realms/tricore`, the fields work
  normally, and the page is usable with a keyboard and on a mobile screen.
- **Tests:** CI runs `python3 -m unittest discover -s scripts -p 'test_opentrix_*.py'` in the
  `repo-hygiene` job. These are static checks and **do not replace** a real sign-in and sign-out
  test against Keycloak.

### Rolling back the theme on a running realm

Work only in an environment you are allowed to administer, preferably an isolated Compose
project. Keep the database volume, realm, accounts, OIDC and BFF configuration unchanged.

1. **Change the running realm** (editing the JSON in Git is not enough):
   - **Admin Console:** realm `tricore` → **Realm Settings → Themes → Login Theme** →
     `keycloak.v2` → **Save**.
   - **Or the Admin CLI**, with `kcadm.sh` authenticated as an administrator (do not print
     passwords or secrets to the terminal or logs):

   ```bash
   kcadm.sh get realms/tricore --fields loginTheme
   kcadm.sh update realms/tricore -s loginTheme=keycloak.v2
   kcadm.sh get realms/tricore --fields loginTheme
   ```

   The last command must return `loginTheme: keycloak.v2`. Check in a browser that the login page
   is back to the default theme and that login errors are still shown; the CLI result alone is not
   enough.

2. **Keep the rollback after the next deployment:** set `loginTheme` to `keycloak.v2` in
   `infra/keycloak/tricore-realm.json` and remove or change the
   `kcadm update ... loginTheme=opentrix` command in `infra/demo/init/kc-init.sh`. Otherwise the
   next `kc-init` run enables the OpenTrix theme again. Change both files together.
3. **Confirm it persists:** in an isolated Compose project, run
   `kcadm.sh get realms/tricore --fields loginTheme` before and after a controlled restart, and
   check that the login page still uses `keycloak.v2` and the volume data is intact. Do not run
   `down -v`, delete the realm or run a realm re-creation script. Rerun `kc-init` only if you
   accept that it resets client secrets and sample passwords from `infra/.env`.
4. **If it fails:** if the update is rejected, check the endpoint, admin permissions and
   connectivity; do not reset the volume. If the realm was changed but the OpenTrix theme still
   appears, check the selected realm, the browser cache and whether `kc-init` ran again. If the
   rollback is lost after a restart, update `tricore-realm.json` and `kc-init.sh` together before
   retrying.

The theme does not change the `master` realm, the Admin Console or any production system.

## Notes

- Reloading the realm with `realm-check.sh` deletes the existing `tricore` realm and its local
  data.
- To change a redirect URI, role or UUID, edit `tricore-realm.json` and reload the realm. Changes
  to identity configuration go through an Issue and pull request as described in
  [CONTRIBUTING.md](https://github.com/tricore-opentrix/opentrix/blob/main/CONTRIBUTING.md).

---

<a id="vi"></a>

## Tổng quan

Cấu hình Keycloak để chạy OpenTrix trên máy cục bộ: realm `tricore`, các client và vai trò, cùng
giao diện đăng nhập OpenTrix. Quyết định kiến trúc: [ADR-018](https://github.com/tricore-opentrix/opentrix/blob/main/docs/08-decisions/ADR-018-apisix-api-gateway.md).

`tricore-realm.json` là nguồn chuẩn của realm. Tệp **không chứa mật khẩu, secret, tên thật hay
email thật**. Ba người dùng mẫu có email giữ chỗ `<username>@example.com` (tên miền dành riêng
theo RFC 2606), chỉ để Keycloak 26 bỏ qua bước xác minh hồ sơ; hệ thống không gửi email nào.
Secret của client và mật khẩu người dùng được đặt lúc chạy từ tệp `infra/.env` cục bộ (đã nằm
trong `.gitignore`).

## Issuer

`http://localhost:8180/realms/tricore` dùng chung cho trình duyệt, Portal BFF, backend và APISIX.
Test backend cũng dùng đúng issuer này.

## Client

| Client                  | Loại                   | Luồng được bật                 | Ghi chú                                                                                                                                                       |
| ----------------------- | ---------------------- | ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tricore-api`           | Resource (bearer-only) | —                              | Giữ bốn vai trò mà backend đọc từ `resource_access.tricore-api.roles`                                                                                         |
| `dxos-portal-bff-local` | Confidential           | Authorization Code + PKCE S256 | Redirect `https://localhost:8443/login/oauth2/code/keycloak`; post-logout `https://localhost:8443/`; audience `tricore-api`; scope giới hạn trong bốn vai trò |
| `gateway-monitor`       | Confidential           | Service account                | Chỉ dùng cho `scripts/gateway-smoke.ps1`; vai trò `workflow:read`; audience `tricore-api`                                                                     |

Không client nào bật implicit flow hay direct access grants (password grant).

## Vai trò và tài khoản

Vai trò của client `tricore-api`: `workflow:create`, `workflow:activate`, `workflow:transition`,
`workflow:read`.

| Username                          | UUID (`sub`)                           | Vai trò `tricore-api`              | Vai trò Helpdesk (người gửi / điều phối / kỹ thuật) |
| --------------------------------- | -------------------------------------- | ---------------------------------- | --------------------------------------------------- |
| `employee-demo`                   | `d2a43dd7-e129-46f9-b09a-eccde2cde032` | create, activate, read, transition | true / false / false                                |
| `coordinator-demo`                | `6afab46d-b455-41e7-a1cb-a2ec6d4841de` | read, transition                   | false / true / false                                |
| `worker-demo`                     | `b79f9591-e3bf-4428-a69b-06b523a5564a` | read, transition                   | false / false / true                                |
| `service-account-gateway-monitor` | `da54a88a-83cb-4e2f-9f52-71ef6d94641b` | read                               | false / false / false                               |

UUID được cố định để định danh người thực hiện lưu trong cơ sở dữ liệu
(`oidc:<base64url(issuer)>.<base64url(sub)>`) không đổi khi nạp lại realm. Tên
`Employee/Coordinator/Worker Demo` chỉ là tên giữ chỗ; tên hiển thị được đặt từ `infra/.env` lúc
chạy.

## Kiểm tra

- **Smoke test cổng API** (cần PowerShell 7.2 trở lên và quyền đọc log Docker): chạy
  `pwsh -File scripts/gateway-smoke.ps1 -ApisixContainer <tên-container-apisix>` từ thư mục gốc
  repo. Secret của monitor được đọc từ `infra/.env` hoặc biến môi trường. Script đối chiếu nonce
  của request không có token với access log của APISIX để xác nhận `401` và `upstream=-`; nếu
  không tìm thấy log tương ứng thì kết quả là BLOCKED. Mã thoát: `0` tất cả đạt, `1` có ít nhất
  một lỗi, `2` bị chặn và không có lỗi.
- **Kiểm tra realm:** sau `infra/demo/spike/spike-up.sh`, chạy `infra/demo/spike/realm-check.sh`.
  Kết quả mong đợi: bốn dòng `OK` cho `iss`, `sub`, `aud` và `resource_access`;
  `GET /api/v1/mvp/requests` với token `gateway-monitor` trả **200**, còn `POST` trả **403**.

## Giao diện đăng nhập OpenTrix

- `themes/opentrix/login` kế thừa **theme `keycloak.v2` của Keycloak 26.8.0**. Theme chỉ bổ sung
  CSS, bộ thông điệp `vi`/`en` và hai tệp SVG cục bộ (logo và hình minh họa). **Không sao chép
  template FreeMarker (`*.ftl`), tệp JavaScript hay form đăng nhập tự viết**: `login.ftl`,
  `field.ftl`, `template.ftl`, form username/password, cách báo lỗi và luồng OIDC/PKCE đều kế
  thừa từ Keycloak. Portal React chỉ liên kết tới `/oauth2/authorization/keycloak`.
- **Khả năng tiếp cận:** theme không ghi đè `field.ftl`, nên trường nhập, kiểm tra dữ liệu và thông
  báo lỗi dùng template của Keycloak 26.8.0. Mỗi khi đổi CSS hoặc nâng cấp Keycloak, cần kiểm tra
  thao tác bằng bàn phím và trình đọc màn hình.
- **Ngôn ngữ:** realm bật `internationalizationEnabled`, `supportedLocales: ["vi"]` và
  `defaultLocale: "vi"`, nên trang hiển thị với `<html lang="vi">`. Vì chỉ có một ngôn ngữ nên
  không hiện bộ chọn ngôn ngữ, và trình duyệt gửi `Accept-Language: en` vẫn thấy tiếng Việt. Muốn
  thêm tiếng Anh, thêm `"en"` vào `supportedLocales`; khi đó Keycloak chọn ngôn ngữ theo
  `Accept-Language` hoặc `ui_locales` và hiện bộ chọn ngôn ngữ, cần kiểm tra lại trên trình duyệt.
  Các trang khác của realm `tricore` (account console, email) cũng dùng tiếng Việt; realm `master`
  và Admin Console không bị ảnh hưởng.
- **Bố cục:** bố cục hai cột dựng trên DOM gốc của Keycloak: `#kc-header` thành cột thương hiệu,
  `<main>` giữ nguyên form của Keycloak. Nội dung cột thương hiệu lấy từ khóa thông điệp
  `loginTitleHtml`, được Keycloak hiển thị qua `kcSanitize()`, nên chỉ được chứa `div`, `span`,
  `p`, `ul`, `li` và thuộc tính `class`. Test `test_brand_panel_is_inert_markup_and_assets_are_local`
  chặn liên kết, hình ảnh, script và URL bên ngoài. Nhãn `integration-local` trong khóa này là cố
  ý; nếu dùng theme cho môi trường khác thì sửa lại thông điệp.
- **Thông điệp:** `messages_vi.properties` chứa toàn bộ chữ tiếng Việt; thông báo lỗi đăng nhập
  giữ nguyên nghĩa gốc, không tiết lộ trường nào sai hay tài khoản có tồn tại không.
  `messages_en.properties` chỉ chứa cột thương hiệu; nhãn và lỗi tiếng Anh kế thừa từ Keycloak.
- **Font:** dùng `Be Vietnam Pro` nếu máy đã cài, nếu không thì dùng `Segoe UI` hoặc font hệ thống.
  Theme không kèm tệp font và không tải font từ CDN.
- **Nâng cấp Keycloak:** bố cục phụ thuộc các class PatternFly 5 (`pf-v5-c-login__*`,
  `pf-v5-c-form-control`) và các id `#kc-header-wrapper`, `#kc-page-title`. Nếu Keycloak đổi DOM,
  form vẫn hoạt động nhưng giao diện có thể quay về mặc định; cần kiểm tra lại trên trình duyệt.
- **Triển khai:** `infra/compose.demo.yml` mount theme ở chế độ chỉ đọc tại
  `/opt/keycloak/themes/opentrix`. `tricore-realm.json` đặt `loginTheme: opentrix` cho **realm
  mới**, còn `infra/demo/init/kc-init.sh` đặt cùng giá trị đó cho **realm đã tồn tại** khi job khởi
  tạo chạy lại.
- **Bật theme cho realm đã tồn tại:** sau khi xác nhận theme đã được mount, vào Admin Console →
  realm `tricore` → **Realm Settings → Themes → Login Theme** → `opentrix` → **Save**, hoặc chạy
  `kcadm.sh update realms/tricore -s loginTheme=opentrix` trong phiên quản trị đã xác thực. Không
  chạy lại toàn bộ `kc-init.sh` chỉ để đổi giao diện, vì script này còn đặt lại mật khẩu mẫu và
  secret của client từ `infra/.env`. Để kiểm tra tệp Compose, chạy
  `docker compose -f infra/compose.demo.yml config` từ thư mục gốc repo (có thể cần `infra/.env`
  hợp lệ).
- **Kiểm tra trên trình duyệt:** mở Portal, vào trang đăng nhập Keycloak và xác nhận logo, giao
  diện OpenTrix; nhập sai thông tin để kiểm tra thông báo lỗi; đăng nhập và đăng xuất bằng tài
  khoản mẫu. Xác nhận URL vẫn thuộc `localhost:8180/realms/tricore`, các trường nhập hoạt động bình
  thường, và trang dùng được bằng bàn phím và trên màn hình di động.
- **Test:** CI chạy `python3 -m unittest discover -s scripts -p 'test_opentrix_*.py'` trong job
  `repo-hygiene`. Đây chỉ là kiểm tra tĩnh, **không thay thế** việc thử đăng nhập và đăng xuất với
  Keycloak thật.

### Khôi phục theme mặc định trên realm đang chạy

Chỉ thao tác trên môi trường bạn được phép quản trị, ưu tiên một Compose project cô lập. Giữ
nguyên volume cơ sở dữ liệu, realm, tài khoản, cấu hình OIDC và BFF.

1. **Đổi trên realm đang chạy** (chỉ sửa JSON trong Git là chưa đủ):
   - **Admin Console:** realm `tricore` → **Realm Settings → Themes → Login Theme** →
     `keycloak.v2` → **Save**.
   - **Hoặc Admin CLI**, với `kcadm.sh` đã xác thực bằng tài khoản quản trị (không in mật khẩu hay
     secret ra terminal hoặc log):

   ```bash
   kcadm.sh get realms/tricore --fields loginTheme
   kcadm.sh update realms/tricore -s loginTheme=keycloak.v2
   kcadm.sh get realms/tricore --fields loginTheme
   ```

   Lệnh cuối phải trả về `loginTheme: keycloak.v2`. Kiểm tra trên trình duyệt rằng trang đăng nhập
   đã về giao diện mặc định và lỗi đăng nhập vẫn hiển thị; chỉ dựa vào kết quả CLI là chưa đủ.

2. **Giữ kết quả sau lần triển khai tiếp theo:** đặt `loginTheme` thành `keycloak.v2` trong
   `infra/keycloak/tricore-realm.json`, và bỏ hoặc sửa lệnh `kcadm update ... loginTheme=opentrix`
   trong `infra/demo/init/kc-init.sh`. Nếu không, lần chạy `kc-init` tiếp theo sẽ bật lại theme
   OpenTrix. Sửa cả hai tệp cùng lúc.
3. **Xác nhận kết quả được giữ:** trên một Compose project cô lập, chạy
   `kcadm.sh get realms/tricore --fields loginTheme` trước và sau một lần khởi động lại có kiểm
   soát, kiểm tra trang đăng nhập vẫn dùng `keycloak.v2` và dữ liệu volume còn nguyên. Không chạy
   `down -v`, không xóa realm và không chạy script tạo lại realm. Chỉ chạy lại `kc-init` khi chấp
   nhận việc script đặt lại secret của client và mật khẩu mẫu từ `infra/.env`.
4. **Nếu không thành công:** nếu lệnh update bị từ chối, kiểm tra endpoint, quyền quản trị và kết
   nối; không reset volume. Nếu đã đổi realm mà vẫn thấy theme OpenTrix, kiểm tra realm đang chọn,
   bộ nhớ đệm trình duyệt và việc `kc-init` có chạy lại hay không. Nếu sau khi khởi động lại mất kết
   quả, sửa đồng thời `tricore-realm.json` và `kc-init.sh` rồi thử lại.

Theme này không thay đổi realm `master`, Admin Console hay bất kỳ hệ thống production nào.

## Lưu ý

- Nạp lại realm bằng `realm-check.sh` sẽ xóa realm `tricore` hiện có cùng dữ liệu cục bộ.
- Muốn đổi redirect URI, vai trò hoặc UUID, sửa `tricore-realm.json` rồi nạp lại realm. Thay đổi
  cấu hình định danh đi qua Issue và pull request theo [CONTRIBUTING.md](https://github.com/tricore-opentrix/opentrix/blob/main/CONTRIBUTING.md).
