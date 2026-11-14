<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# OpenTrix #233: UI Preview trên Windows, không Docker

Chạy trong PowerShell (Node và dependencies hiện tại của dự án đã có):

```powershell
Set-Location 'D:\dxos\opentrix-issue-233\frontend'
npm.cmd run ui:preview
```

Lệnh tự kiểm tra TypeScript, build React thật bằng mode `integration-local` vào
`.ui-preview-dist`, chạy static server trên `127.0.0.1:4176`, mở Chromium có cửa sổ
và giữ phiên cho đến khi đóng tab chính/cửa sổ hoặc nhấn `Ctrl+C` tại terminal.
Không cần Docker, backend, Keycloak hay cài chứng chỉ HTTPS.
Nếu máy chưa có Chromium của Playwright: `npx.cmd playwright install chromium`.

URL bắt đầu: **https://localhost:8443/mvp/helpdesk**.
Phải sử dụng **cửa sổ Chromium do lệnh trên mở**: Playwright chặn các request
trong browser context này. Đây là HTTPS origin ảo, không phải HTTPS server tại
port 8443. Dán URL vào Chrome/Edge thông thường sẽ không có preview; URL HTTP
port 4176 chỉ phục vụ file tĩnh và không tạo được phiên BFF.

## Chuyển màn hình

1. **Login:** màn hình ban đầu. Bấm **Đăng nhập** để chuyển sang list (SSO giả lập).
2. **List:** bấm **Danh sách Helpdesk** ở sidebar. Bấm tên yêu cầu để mở detail.
3. **Create:** bấm **Tạo yêu cầu**, nhập tiêu đề/mô tả và bấm **Gửi yêu cầu IT**.
   Yêu cầu mới xuất hiện trong list và có thể mở detail.
4. **Detail:** chọn yêu cầu “Không thể lưu báo cáo” hoặc yêu cầu vừa tạo.
   Bấm **Danh sách yêu cầu IT** để quay lại. **Đăng xuất** quay về login.

Trong cùng cửa sổ preview, có thể dán trực tiếp các URL điều khiển kiểm thử:

| Màn hình / tình huống               | URL                                          |
| ----------------------------------- | -------------------------------------------- |
| Login                               | https://localhost:8443/__ui_preview__/login  |
| List                                | https://localhost:8443/__ui_preview__/list   |
| Create                              | https://localhost:8443/__ui_preview__/create |
| Detail mẫu                          | https://localhost:8443/__ui_preview__/detail |
| Reset dữ liệu, về login             | https://localhost:8443/__ui_preview__/reset  |
| 401 ở lần đọc API kế tiếp, về login | https://localhost:8443/__ui_preview__/401    |
| Create, POST kế tiếp trả 409        | https://localhost:8443/__ui_preview__/409    |

Các URL điều khiển chỉ tồn tại trong fixture Playwright. Khi thử 409, điền form
và gửi để xem lỗi xung đột cùng việc chặn gửi lại của ứng dụng. Dùng URL `create`
để mở lại trang sau khi xem lỗi.

## Phạm vi mô phỏng và giới hạn

- Tái sử dụng `src/test/helpdeskFixtures.ts` và route harness dùng chung với
  `tests/integration-local.spec.ts`; không có React app riêng hoặc dữ liệu mock
  được import vào production entry.
- Mô phỏng BFF session, điều hướng đăng nhập/đăng xuất, danh sách, detail,
  lịch sử rỗng, tạo yêu cầu (201), CSRF thiếu/sai (403), 401 và 409.
- Dữ liệu tạo thử chỉ ở RAM của tiến trình Playwright, giữ qua reload/đổi route/
  đăng xuất trong phiên này; reset hoặc dừng/chạy lại sẽ xóa dữ liệu thử.
- Danh sách có một trang; không giả lập phân trang nhiều trang.
- Fixture mẫu giữ `allowedActions` hiện có. Không tự cấp quyền phân công,
  không tạo danh sách người được phân công giả. Ghi phân công/chuyển trạng thái
  không được hỗ trợ sẽ trả 403. Yêu cầu mới chỉ để xem, không có thao tác workflow.
- Không có xác thực OIDC thật, kiểm chứng quyền tenant/role thật, database,
  workflow đầy đủ, upload, email hay lưu trữ lâu dài. HTTPS origin ảo không
  kiểm chứng TLS/certificate hoặc các thuộc tính cookie của BFF thật.
- Tất cả HTTP(S) request từ context được chặn trước: chỉ GET file giao diện
  được tải từ static server loopback 4176. BFF/OIDC được trả lời trong Playwright;
  URL ngoài phạm vi, POST không được hỗ trợ và WebSocket bị chặn. Service worker
  bị tắt trong context này. Không gửi ghi tới backend thật.
- Không sửa mã production về bảo mật, CSRF, transport, API, phân quyền hay
  xử lý 401/409. Fixtures chạy ở tiến trình kiểm thử, không nằm trong bundle.
- Không commit, push, merge, dùng Docker hoặc thao tác worktree khác.

Kiểm tra tự động luồng tương tác và chặn mạng:

```powershell
npm.cmd run test:ui-preview
```

Hai lệnh preview và kiểm tra dùng chung port 4176, nên đóng preview trước khi
chạy kiểm tra. Nếu port đã được dùng, lệnh sẽ dừng thay vì tái sử dụng server lạ.
