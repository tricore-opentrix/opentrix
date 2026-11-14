<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors

SPDX-License-Identifier: Apache-2.0
-->

# DX-OS Internal Service Portal / Cổng dịch vụ nội bộ

**Trạng thái / Status:** Mặc định **MOCK / DEVELOPMENT**. Build **integration-local** là lựa chọn riêng, cần các thành phần chạy thực tế và không tự xác nhận LIVE. **LIVE E2E: UNVERIFIED**; xem [#118](https://github.com/tricore-opentrix/opentrix/issues/118).

**Điều hướng / Navigation:** [Bộ tài liệu / Docs index](../docs/README.md) · [Phát triển / Development](../docs/DEVELOPMENT.md) · [API](../docs/API.md) · [Tích hợp / Integration](../docs/INTEGRATION.md) · [Kiểm thử / Testing](../docs/TESTING.md) · [Portal BFF](../portal-bff/README.md)

## Phân biệt các chế độ / Mode boundaries

| Chế độ / Mode | Có gì / What exists | Chưa chứng minh / Not evidence of |
| --- | --- | --- |
| **MOCK / DEVELOPMENT** (mặc định / default) | `npm.cmd run dev` và `npm.cmd run build` dùng fixtures/dữ liệu giả trong bộ nhớ, không cần Keycloak/Backend/PostgreSQL. | SSO, backend ACL, lưu trữ ticket, tích hợp LIVE |
| **integration-local** (opt-in) | `npm.cmd run build:integration-local` chọn entry tích hợp với BFF; yêu cầu setup Keycloak, BFF, Backend, HTTPS ingress, database riêng; xem [BFF runbook](../portal-bff/README.md). | Build thành công không chứng minh stack đã chạy hoặc browser acceptance đạt |
| **LIVE E2E** (cổng nghiệm thu / acceptance gate) | Chỉ có thể đánh giá bằng bằng chứng đăng nhập thật, quyền truy cập, workflow và persistence tại SHA/môi trường cụ thể. | **UNVERIFIED** theo [#118](https://github.com/tricore-opentrix/opentrix/issues/118); không phải tên chế độ tự bật từ MOCK |

**English:** The default Portal uses synthetic in-memory MOCK data. `integration-local` is a separate opt-in build entry, not a deployed or accepted LIVE stack. Real Keycloak login, authorized Helpdesk transitions and database persistence remain **LIVE E2E UNVERIFIED**. See canonical [API](../docs/API.md), [integration](../docs/INTEGRATION.md), [testing](../docs/TESTING.md), and [development](../docs/DEVELOPMENT.md) guides.

**Bối cảnh lịch sử / Historical Issue #39:** Prototype UI tiếng Việt trình diễn IT Support và Facility bằng thành phần giao diện dùng chung. Các dữ liệu Facility trong MOCK **không** chứng minh Facility backend đã triển khai hay chứng minh Core tái sử dụng ở hai ứng dụng. Những kết quả lịch sử chỉ áp dụng cho SHA/fixture đã kiểm chứng; không suy ra trạng thái Issue hiện nay.

## Chạy localhost

**Demo #233:** Tên sản phẩm là **IT Helpdesk · OpenTrix**; bản integration-local giữ badge môi trường và ẩn Workflow version khỏi giao diện. / The product is **IT Helpdesk · OpenTrix**; integration-local keeps its environment badge and hides the workflow version from the UI.

**Phiên integration-local / Integration-local session:** Nút Đăng nhập mở `/oauth2/authorization/keycloak`; Đăng xuất chỉ hiện khi có phiên BFF và POST `/bff/logout` bằng form `_csrf` lấy từ `/bff/session`. Trình duyệt đi theo redirect OIDC; đổi ba tài khoản trên cùng trình duyệt vẫn cần kiểm chứng thực tế. / Login opens `/oauth2/authorization/keycloak`; authenticated logout posts the session CSRF token to `/bff/logout` using a browser form. Real OIDC redirects and three-account switching still require verification.

**Trạng thái #106 / States #106:** `SUBMITTED` → Mới gửi; `TRIAGED` → Đã tiếp nhận; `IN_PROGRESS` → Đang xử lý; `RESOLVED` → Chờ xác nhận; `CONFIRMED` → Hoàn thành. Mã lạ giữ nguyên chữ và dùng badge xám; payload, version và `allowedActions` giữ nguyên. / These Vietnamese labels affect presentation only; unknown codes retain their original text with a gray badge. API values, versions and authorization remain unchanged.

Yêu cầu Node.js >= 22.12 (đã kiểm tra bằng Node 24.19.0), npm và trình duyệt hiện đại.

```powershell
Set-Location frontend
npm.cmd ci
npm.cmd run dev
```

Mở **http://127.0.0.1:5173**. Trên macOS/Linux dùng `npm` thay cho `npm.cmd`. Không cần backend, database, `.env` hoặc credentials.

```powershell
npm.cmd run build
npm.cmd run preview -- --port 4173
```

Production hosting phải có SPA fallback về `index.html` cho các deep links. Không có deployment trong phạm vi này.

## Stack và cấu trúc

React 19, Vite 8, TypeScript strict, React Router 7, Lucide, Be Vietnam Pro được phục vụ cục bộ, CSS tokens; phiên bản chính xác nằm trong `package-lock.json`. Stack được người dùng xác nhận sau audit. Không tải font, analytics hoặc tài nguyên bên thứ ba khi sử dụng app.

```text
src/
  components/ui.tsx           Shared table, badges, timeline, modal, UI states
  domain/request.ts          Shared view model, labels, validation, filtering
  fixtures/requests.ts        Synthetic demo records for both services
  services/RequestService.ts  UI-facing application service interface
  services/portalService.ts   Composition root: interface -> mock service
  services/MockRequestService.ts  In-memory demo responses and fault controls
  services/HttpApiClient.ts   Closed HTTP boundary; rejects before networking
  hooks/useRequests.ts        Loading, read errors, expired demo session handling
  pages/                     Dashboard, list/history/desk, create, detail, system
  context.tsx                Demo role, success announcements, refresh state
  tokens.css / styles.css    Palette, typography, responsive and reduced motion
tests/portal.spec.ts          Browser smoke, WCAG checks and real screenshots
scripts/check-security.mjs    Source/bundle credential-pattern check
```

Ở chế độ MOCK, `RequestService` dùng mock fixture qua composition root; `HttpApiClient` của đường MOCK từ chối LIVE với `LIVE_BLOCKED`. Mapper, Assignment Form và typed Helpdesk adapter được kiểm thử với fake transport; đường `integration-local` dùng entry riêng, không biến MOCK mặc định thành LIVE. Không coi view model mock là DTO backend. Xem [API contract](../docs/API.md) và [tài liệu tích hợp](../docs/INTEGRATION.md) để đối chiếu trạng thái hiện hành.

Logout, đổi vai trò và 401 vô hiệu hóa kết quả async của phiên cũ. Response muộn không chuyển trang, phát thông báo hay làm hết hạn phiên mới; 401 của phiên hiện tại vẫn kết thúc phiên sau khi rời màn hình. Assignment không bắt đầu GET Detail sau logout. Lệnh ghi đã gửi không bị hủy/replay; unknown outcome của MVP vẫn khóa để chờ đối soát. Đây là vòng đời phiên demo/fake, chưa phải logout hoặc thu hồi phiên OIDC/BFF.

Hai workflow UX dùng chung form, bảng, metadata, action dialog và timeline. Những phản hồi cố định trong mock chỉ phục vụ demo; **không phải frontend Workflow engine**, không thực thi definition, không có BPMN editor, persistence hay orchestration Core. Các thao tác được cho phép thật phải do backend quyết định sau security gate.

## Các màn hình

| Route           | Nội dung                                                            |
| --------------- | ------------------------------------------------------------------- |
| `/session`      | Vào/kết thúc phiên demo, đổi vai trò, mô phỏng hết hạn; SSO bị chặn |
| `/login`        | Form email/mật khẩu, ghi nhớ riêng email; submit và khôi phục mật khẩu bị chặn |
| `/register`     | Form đăng ký Sinh viên/Giảng viên; không tạo tài khoản hoặc cấp quyền |
| `/`             | Dashboard và truy cập nhanh hai dịch vụ                             |
| `/requests`     | Search không dấu, filter dịch vụ/trạng thái, phân trang             |
| `/requests/new` | Form dùng chung, validation, loading, success/error                 |
| `/approvals`    | Bàn xử lý dành cho vai trò người xử lý mô phỏng                     |
| `/requests/:id` | Chi tiết, phiên bản mock, thao tác xử lý và timeline                |
| `/history`      | Lịch sử từng yêu cầu, mới nhất trước                                |
| `/integration`  | Trạng thái các capability, kiểm tra chặn LIVE và fault controls     |

Loading được mô phỏng với độ trễ 350 ms. Không có kết quả: hướng dẫn đổi bộ lọc. Lỗi đọc có nút tải lại do người dùng chủ động. Form giữ nội dung khi lỗi mạng. Ghi có khóa chống double-submit và không tự retry. Khi `COMMIT_OUTCOME_UNKNOWN`, UI vô hiệu hóa gửi tiếp và hướng dẫn kiểm tra lịch sử. Lỗi 401 mô phỏng kết thúc phiên và hiển thị thông báo; 403 và hidden/missing 404 có thông báo an toàn. Đây không phải bằng chứng kiểm quyền backend.

## Ranh giới bảo mật và BLOCKED API

| Capability               | Điều kiện còn thiếu                                                                                                               |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------------------- |
| Identity / SSO           | Verified browser login, OIDC Authorization Code + PKCE, #24                                                                       |
| Gateway / Workflow HTTP  | Registration, resource ACL, tenant binding và security gate #22/#23/#24; mọi create/activate/transition/snapshot/history đều chặn |
| Data persistence         | HTTP application contract được duyệt; không nối PostgreSQL hoặc Java trực tiếp                                                    |
| Attachments              | Backend Storage API có kiểm quyền #26: **BLOCKED FEATURE**, không có file input hoặc upload giả                                   |
| HTTP DTO / error mapping | OpenAPI và review contract #37                                                                                                    |

Không có secret, admin token, service-role key, database credential hay `X-User`/`X-Role` làm nguồn định danh. Chỉ có tên/vai trò demo trong `sessionStorage`; sửa giá trị này không phải chứng minh authentication/authorization. Fixture visibility (nhân viên xem yêu cầu mẫu của mình; người xử lý xem bộ dữ liệu mẫu) chỉ là hành vi UX.

## Kiểm thử

Đối chiếu thiết kế nội bộ, phạm vi tích hợp thực tế và chỉ mục ảnh trước/sau #233:
xem [UI_REVIEW_233.md](UI_REVIEW_233.md).

Kiểm tra giao diện integration-local (#233) trên entry production hiện tại:

```powershell
npm.cmd run build:integration-local
npx.cmd playwright test --config tests/integration-local.playwright.config.ts
```

Bộ kiểm tra dùng phản hồi BFF giả lập trên origin ảo `https://localhost:9443` (khác stack Docker `https://localhost:8443`), chụp bốn màn hình ở 1440/768/390/320px
vào `playwright-report/issue-233/`, kiểm tra tràn ngang và axe WCAG.
Kết quả này không xác nhận đăng nhập/đăng xuất OIDC, đổi ba tài khoản thật hay
Golden Path. Các bước đó cần stack Docker hoạt động theo runbook #119.
Chạy lại `npm.cmd run build` trước bộ smoke MOCK dưới đây.

```powershell
npm.cmd run build
npm.cmd test
npx.cmd playwright install chromium
npm.cmd run test:smoke
npm.cmd run check:security
```

Smoke suite khởi chạy production preview tại `127.0.0.1:4173`, kiểm tra hai luồng UI, lỗi/empty/validation, chặn API, keyboard/modal, desktop/tablet/mobile và axe WCAG 2 A/AA + 2.1 AA. Screenshot được tạo trực tiếp từ localhost tại evidence cục bộ của từng lần chạy (không có đường dẫn ảnh chuẩn được xác minh trên `main`). Không dùng ảnh dựng làm bằng chứng. Script security chỉ là kiểm tra mẫu credentials phổ biến, đi kèm review source và staged diff.

Python không có trong môi trường triển khai nên browser suite dùng Playwright TypeScript, có thể chạy bằng dependencies đã khóa của dự án.

## Giới hạn

### Email/mật khẩu: chỉ xem trước giao diện

`/login` và `/register` dùng thương hiệu DX-OS, Be Vietnam Pro và Lucide, bố cục
hai cột trên desktop và một cột trên mobile. Truy cập từ liên kết tại `/session`
hoặc mở trực tiếp URL. Nút **Vào phiên Demo** luôn mở luồng Demo hiện có riêng.

Email, họ tên, độ dài mật khẩu (đăng ký: 12–128 ký tự) và xác nhận mật khẩu được
kiểm tra tại form. Đây là quy tắc UI tạm thời, không phải chính sách Identity đã
được duyệt. Chỉ dùng dữ liệu giả; không nhập mật khẩu thật để thử nghiệm.

Submit hợp lệ chỉ kiểm tra form cục bộ, xóa các ô mật khẩu rồi hiển thị
**BLOCKED FEATURE**. Không gửi HTTP, không tạo JWT, không tạo tài khoản, không
thay đổi vai trò/phiên Demo và không báo đăng nhập thành công. Quên mật khẩu cũng
hiển thị **BLOCKED FEATURE**. Không có endpoint hoặc công tắc mở authentication.
Luồng thật phải do backend Identity xử lý qua API được phê duyệt và bảo vệ.

Chỉ khi người dùng chọn **Ghi nhớ email**, email hợp lệ được lưu trong
`localStorage` dưới khóa `dxos-remembered-email-v1`; bỏ chọn sẽ xóa ngay. Mật khẩu
chỉ tồn tại tạm trong ô nhập và bộ nhớ lúc validation, không được lưu vào browser
storage, fixtures, logs hoặc gửi qua mạng. Đăng ký chỉ có Sinh viên/Giảng viên và
từ chối giá trị vai trò bị sửa thành admin/processor. Không có quyền thực được cấp.

Test mới nằm tại `src/pages/Auth.test.tsx` và `tests/auth.spec.ts`. Xem
ảnh Login/Register của lần chạy riêng (cần đính kèm log và ảnh ở Issue tương ứng) ở desktop,
tablet, mobile 390px và 320px. Bộ smoke hiện có tiếp tục kiểm tra tạo yêu cầu,
phê duyệt, xử lý, timeline và `HttpApiClient` fail-closed. Theme chỉ tăng tương
phản một số màu chữ phụ để các kiểm tra WCAG hiện có đạt; không đổi bố cục dashboard.

- Request và lịch sử chỉ ở bộ nhớ trong **một tab**. Reload hoặc khôi phục demo sẽ reset fixtures; đổi route bằng sidebar giữ dữ liệu.
- Phiên demo chỉ lưu lựa chọn vai trò trong tab, không có SSO, access token hay quyền thực.
- Kết quả ghi chưa xác định chỉ là mô phỏng lỗi; mock không xác nhận một commit thật đã xảy ra.
- Chưa kiểm chứng real 401/403/404, cross-tenant denial, concurrency/persistence hoặc HTTP end-to-end.
- Browser coverage hiện là Chromium; axe không thay thế audit accessibility thủ công đầy đủ. Bảng cuộn ngang bên trong ở màn hình nhỏ.
- Chưa upload/read file, chưa gửi thông báo thực, chưa triển khai hosting.

Xem [hướng dẫn demo](DEMO_GUIDE.md). Refs #39; kết quả local chỉ chứng minh đúng phạm vi, SHA và environment từng lần chạy; không suy ra trạng thái đóng/mở Issue #39 hoặc LIVE E2E.
