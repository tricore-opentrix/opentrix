<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# Frontend — OpenTrix Portal

> **Language / Ngôn ngữ:** [English](#en) · [Tiếng Việt](#vi)

---

<a id="en"></a>

## Overview

The OpenTrix Portal is the web interface for the IT Helpdesk application. It is built with React 19, TypeScript, Vite 8 and React Router 7, uses Lucide icons and bundles the Be Vietnam Pro font locally; the exact versions are pinned in [package-lock.json](https://github.com/tricore-opentrix/opentrix/blob/main/frontend/package-lock.json). The user interface is in Vietnamese. The Portal loads no fonts, analytics or other resources from third-party servers.

The Portal has two builds:

| Build | Command | Data source |
| --- | --- | --- |
| **MOCK** (default) | `npm run dev`, `npm run build` | Synthetic in-memory data. No backend, Keycloak, database or credentials are needed. |
| **integration-local** | `npm run build:integration-local` | The IT Helpdesk API through the [Portal BFF](https://github.com/tricore-opentrix/opentrix/blob/main/portal-bff/README.md), with sign-in through Keycloak. Used by the [local deployment](https://github.com/tricore-opentrix/opentrix/blob/main/infra/demo/README.md). |

### Requirements

Node.js 22.12 or later and npm.

### Run the MOCK build

```bash
cd frontend
npm ci
npm run dev
```

Open http://127.0.0.1:5173. On Windows PowerShell, use `npm.cmd` if `npm` is blocked by the execution policy.

To build and preview the production bundle:

```bash
npm run build
npm run preview -- --port 4173
```

A web server hosting the build must fall back to `index.html` for unknown paths so that deep links work.

### integration-local build

`npm run build:integration-local` builds a separate entry point that contains only the IT Helpdesk at `/mvp/helpdesk`:

- **Sign in** opens `/oauth2/authorization/keycloak`. **Sign out** sends `POST /bff/logout` with the CSRF token from `/bff/session`.
- All API calls go to `/bff/api/v1/mvp/requests` on the same origin. The browser never holds an access token.
- The build runs only over HTTPS on a loopback host (`localhost`, `127.0.0.1` or `[::1]`).

The local deployment builds and serves this entry automatically. To serve it yourself, see the Caddy setup in [portal-bff/README.md](https://github.com/tricore-opentrix/opentrix/blob/main/portal-bff/README.md).

### Pages (MOCK build)

| Route | Content |
| --- | --- |
| `/` | Dashboard with quick access to the IT Support and Facility services |
| `/requests`, `/requests/new`, `/requests/:id` | Request list with search and filters, request form, request detail with timeline |
| `/approvals` | Work queue for the simulated handler role |
| `/history` | Request history, newest first |
| `/mvp/helpdesk` | IT Helpdesk screens; they are connected in the integration-local build and show a notice in the MOCK build |
| `/session` | Start or end a demo session, switch the simulated role, simulate session expiry |
| `/integration` | Status of each capability and simulated failure controls |
| `/login`, `/register` | Sign-in and registration screens for UI preview only: submitting validates the form and shows "BLOCKED FEATURE"; nothing is sent |

### IT Helpdesk request states

| API state | Label shown |
| --- | --- |
| `SUBMITTED` | Mới gửi |
| `TRIAGED` | Đã tiếp nhận |
| `IN_PROGRESS` | Đang xử lý |
| `RESOLVED` | Chờ xác nhận |
| `CONFIRMED` | Hoàn thành |

An unknown state is shown with its original code and a gray badge. Labels affect presentation only; the backend decides which actions are allowed.

### Behavior

- Writes are protected against double submission and are never retried automatically. If the result of a write is unknown (`COMMIT_OUTCOME_UNKNOWN`), the form stays locked and the user is asked to check the request history.
- A `401` response ends the session; `403` and hidden `404` responses show a safe message.
- Signing out, switching roles or a `401` cancel pending results from the previous session.
- The MOCK build stores only the simulated role in `sessionStorage` (`dxos-demo-role`); this is not authentication. If the user selects "remember email" on `/login`, the email is stored in `localStorage` under `dxos-remembered-email-v1`. Passwords are never stored or sent.

### Project structure

```text
src/
  App.tsx, main.tsx              Routes; main.tsx selects the MOCK or integration-local entry
  features/helpdesk/             IT Helpdesk screens and the integration-local entry
  services/mvp/                  IT Helpdesk service port, commands, state labels
  services/mvp/http/             HTTP client and same-origin transport to the Portal BFF
  services/MockRequestService.ts In-memory service for the MOCK build
  fixtures/requests.ts           Synthetic demo data
  components/, pages/, hooks/    Shared UI components, pages and hooks
  tokens.css, styles.css         Design tokens and styles
tests/                           Playwright suites
scripts/check-security.mjs       Scans source and build output for credential patterns
```

### Tests

| Command | What it checks |
| --- | --- |
| `npm test` | Unit and component tests (Vitest) |
| `npm run test:smoke` | Browser tests (Playwright, Chromium) against the production preview on `127.0.0.1:4173`: request flows, error and empty states, keyboard and dialog use, desktop, tablet and mobile layouts, and accessibility with axe (WCAG 2.0 A/AA and 2.1 AA). Run `npm run build` and `npx playwright install chromium` first. |
| `npx playwright test --config tests/integration-local.playwright.config.ts` | The integration-local build against a simulated BFF on `https://localhost:9443`, at 1440, 768, 390 and 320 px. Run `npm run build:integration-local` first. |
| `npm run check:security` | Credential patterns in `src/` and `dist/` |

These tests use simulated data and a simulated BFF. A sign-in with Keycloak and a full IT Helpdesk flow can be checked with the local deployment.

### Limitations

- In the MOCK build, requests live in memory in one browser tab; reloading resets the data.
- The `/login` and `/register` screens do not create accounts or sessions.
- File attachments are not supported.
- Browser tests run on Chromium only; axe checks do not replace a full manual accessibility review.

---

<a id="vi"></a>

## Tổng quan

OpenTrix Portal là giao diện web của ứng dụng IT Helpdesk, xây dựng bằng React 19, TypeScript, Vite 8 và React Router 7, dùng biểu tượng Lucide và đóng gói sẵn font Be Vietnam Pro; phiên bản chính xác được ghim trong [package-lock.json](https://github.com/tricore-opentrix/opentrix/blob/main/frontend/package-lock.json). Giao diện dùng tiếng Việt. Portal không tải font, analytics hay tài nguyên nào khác từ máy chủ bên thứ ba.

Portal có hai bản build:

| Bản build | Lệnh | Nguồn dữ liệu |
| --- | --- | --- |
| **MOCK** (mặc định) | `npm run dev`, `npm run build` | Dữ liệu giả trong bộ nhớ. Không cần backend, Keycloak, cơ sở dữ liệu hay thông tin đăng nhập. |
| **integration-local** | `npm run build:integration-local` | API IT Helpdesk qua [Portal BFF](https://github.com/tricore-opentrix/opentrix/blob/main/portal-bff/README.md), đăng nhập qua Keycloak. Được dùng trong [triển khai cục bộ](https://github.com/tricore-opentrix/opentrix/blob/main/infra/demo/README.md). |

### Yêu cầu

Node.js 22.12 trở lên và npm.

### Chạy bản MOCK

```bash
cd frontend
npm ci
npm run dev
```

Mở http://127.0.0.1:5173. Trên Windows PowerShell, dùng `npm.cmd` nếu `npm` bị execution policy chặn.

Để build và xem trước bản production:

```bash
npm run build
npm run preview -- --port 4173
```

Máy chủ web phục vụ bản build phải trả về `index.html` cho các đường dẫn không tồn tại để liên kết sâu hoạt động.

### Bản build integration-local

`npm run build:integration-local` build một entry riêng, chỉ gồm IT Helpdesk tại `/mvp/helpdesk`:

- **Đăng nhập** mở `/oauth2/authorization/keycloak`. **Đăng xuất** gửi `POST /bff/logout` kèm CSRF token lấy từ `/bff/session`.
- Mọi lời gọi API đi tới `/bff/api/v1/mvp/requests` trên cùng origin. Trình duyệt không bao giờ giữ access token.
- Bản build chỉ chạy qua HTTPS trên máy cục bộ (`localhost`, `127.0.0.1` hoặc `[::1]`).

Triển khai cục bộ tự build và phục vụ entry này. Để tự phục vụ, xem cấu hình Caddy trong [portal-bff/README.md](https://github.com/tricore-opentrix/opentrix/blob/main/portal-bff/README.md).

### Các trang (bản MOCK)

| Route | Nội dung |
| --- | --- |
| `/` | Dashboard và truy cập nhanh hai dịch vụ Hỗ trợ IT và Cơ sở vật chất |
| `/requests`, `/requests/new`, `/requests/:id` | Danh sách yêu cầu có tìm kiếm và lọc, form tạo yêu cầu, chi tiết yêu cầu kèm timeline |
| `/approvals` | Bàn xử lý cho vai trò người xử lý mô phỏng |
| `/history` | Lịch sử yêu cầu, mới nhất trước |
| `/mvp/helpdesk` | Màn hình IT Helpdesk; được kết nối ở bản integration-local, còn ở bản MOCK chỉ hiện thông báo |
| `/session` | Bắt đầu hoặc kết thúc phiên demo, đổi vai trò mô phỏng, mô phỏng phiên hết hạn |
| `/integration` | Trạng thái từng năng lực và công cụ mô phỏng lỗi |
| `/login`, `/register` | Màn hình đăng nhập và đăng ký chỉ để xem trước giao diện: gửi form chỉ kiểm tra dữ liệu và hiện "BLOCKED FEATURE"; không gửi gì đi |

### Trạng thái yêu cầu IT Helpdesk

| Trạng thái API | Nhãn hiển thị |
| --- | --- |
| `SUBMITTED` | Mới gửi |
| `TRIAGED` | Đã tiếp nhận |
| `IN_PROGRESS` | Đang xử lý |
| `RESOLVED` | Chờ xác nhận |
| `CONFIRMED` | Hoàn thành |

Trạng thái không xác định được hiển thị bằng mã gốc kèm badge xám. Nhãn chỉ ảnh hưởng hiển thị; backend quyết định thao tác nào được phép.

### Hành vi

- Thao tác ghi được chặn gửi hai lần và không bao giờ tự thử lại. Nếu không xác định được kết quả ghi (`COMMIT_OUTCOME_UNKNOWN`), form bị khóa và người dùng được hướng dẫn kiểm tra lịch sử yêu cầu.
- Phản hồi `401` kết thúc phiên; `403` và `404` ẩn hiển thị thông báo an toàn.
- Đăng xuất, đổi vai trò hoặc nhận `401` sẽ hủy các kết quả đang chờ của phiên trước.
- Bản MOCK chỉ lưu vai trò mô phỏng trong `sessionStorage` (`dxos-demo-role`); đây không phải xác thực. Nếu người dùng chọn "ghi nhớ email" ở `/login`, email được lưu trong `localStorage` với khóa `dxos-remembered-email-v1`. Mật khẩu không bao giờ được lưu hay gửi đi.

### Cấu trúc mã

```text
src/
  App.tsx, main.tsx              Định tuyến; main.tsx chọn entry MOCK hoặc integration-local
  features/helpdesk/             Màn hình IT Helpdesk và entry integration-local
  services/mvp/                  Port dịch vụ IT Helpdesk, lệnh, nhãn trạng thái
  services/mvp/http/             HTTP client và transport cùng origin tới Portal BFF
  services/MockRequestService.ts Dịch vụ trong bộ nhớ cho bản MOCK
  fixtures/requests.ts           Dữ liệu demo giả
  components/, pages/, hooks/    Thành phần giao diện, trang và hook dùng chung
  tokens.css, styles.css         Design token và style
tests/                           Bộ test Playwright
scripts/check-security.mjs       Quét mã nguồn và bản build tìm mẫu thông tin đăng nhập
```

### Kiểm thử

| Lệnh | Nội dung kiểm tra |
| --- | --- |
| `npm test` | Unit test và component test (Vitest) |
| `npm run test:smoke` | Test trình duyệt (Playwright, Chromium) trên bản preview tại `127.0.0.1:4173`: luồng yêu cầu, trạng thái lỗi và rỗng, thao tác bàn phím và hộp thoại, bố cục desktop, tablet, mobile, và khả năng tiếp cận bằng axe (WCAG 2.0 A/AA và 2.1 AA). Chạy `npm run build` và `npx playwright install chromium` trước. |
| `npx playwright test --config tests/integration-local.playwright.config.ts` | Bản integration-local với BFF giả lập tại `https://localhost:9443`, ở các độ rộng 1440, 768, 390 và 320 px. Chạy `npm run build:integration-local` trước. |
| `npm run check:security` | Mẫu thông tin đăng nhập trong `src/` và `dist/` |

Các test này dùng dữ liệu và BFF giả lập. Việc đăng nhập bằng Keycloak và luồng IT Helpdesk đầy đủ có thể kiểm tra bằng triển khai cục bộ.

### Giới hạn

- Ở bản MOCK, yêu cầu chỉ nằm trong bộ nhớ của một tab trình duyệt; tải lại trang sẽ đặt lại dữ liệu.
- Màn hình `/login` và `/register` không tạo tài khoản hay phiên.
- Chưa hỗ trợ tệp đính kèm.
- Test trình duyệt chỉ chạy trên Chromium; kiểm tra axe không thay thế đánh giá khả năng tiếp cận thủ công đầy đủ.
