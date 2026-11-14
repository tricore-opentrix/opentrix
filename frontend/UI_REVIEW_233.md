<!-- SPDX-FileCopyrightText: 2026 TRICORE contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Đối chiếu giao diện integration-local — Issue #233

Tham chiếu: thiết kế nội bộ đã được đối chiếu trực quan. Chỉnh trực tiếp React/CSS của ứng dụng,
không tạo ứng dụng demo khác. CSS mới chỉ áp dụng dưới `.helpdesk-local`.

## Phần đã áp dụng

| Màn hình | Phạm vi tham chiếu | Giao diện thực hiện |
| --- | --- | --- |
| Khung chung | 1–9 | Header trắng, logo cỏ ba lá, OpenTrix và IT Helpdesk, badge integration-local, nút đăng xuất, nền xám nhạt, điều hướng mint, nút teal, card trắng bo tròn. Không thêm hồ sơ tài khoản giả. |
| Login | 5 | Card hai cột, minh họa bằng CSS, lời giới thiệu, nút đăng nhập tổ chức, footer mã nguồn mở. Mobile chuyển một cột; giữ nguyên URL OIDC. |
| List | 1, 6, 8 | Card bảng, cột mã/tiêu đề/trạng thái/người yêu cầu/người xử lý; nhãn trạng thái tiếng Việt. Mobile chuyển hàng thành thẻ có nhãn để đọc đủ dữ liệu tại 320px. Giữ cursor pagination, tải lại và dữ liệu từ service. |
| Create | 3 | Form trắng, loại yêu cầu IT cố định, placeholder, đánh dấu bắt buộc, khối hướng dẫn mint bên cạnh. Mobile xếp dọc, nút vừa chiều rộng. Giữ validation, giới hạn ký tự và khóa gửi một lần. |
| Detail | 2, 7, 9 | Khối thông tin/nội dung/thao tác/phân công ở cột chính, lịch sử ở cột bên; nền mint cho thao tác; màu trạng thái có chữ. Mobile xếp một cột. Nội dung lỗi, kết quả xử lý và dữ liệu dài xuống dòng trong card. |

A–E của #233 tiếp tục được giữ: tên sản phẩm/tab, đăng nhập và đăng xuất dùng
transport/CSRF hiện tại, 5 nhãn trạng thái và fallback mã lạ, ẩn Workflow version,
test hồi quy. Không sửa `allowedActions`, version guards, 401/409, unknown outcome,
API, BFF, backend hoặc phân quyền. Không thêm dependency vào package ứng dụng.

## Khác biệt có chủ đích và phần chưa tích hợp

| Thành phần trong thiết kế nội bộ | Giới hạn hiện tại |
| --- | --- |
| Tên/vai trò/avatar tài khoản ở header | `/bff/session` hiện phục vụ trạng thái phiên và CSRF; không dựng tên hoặc suy ra vai trò. Giữ header chung. |
| Dashboard riêng cho nhân viên/điều phối/kỹ thuật viên, lời chào và số việc | Chưa xây màn hình này trong #233. Danh sách phân trang không chứng minh tổng số toàn hệ thống; không tạo số đếm hoặc persona giả. |
| Bảng điều phối Kanban, tab việc cần tôi xử lý | Là màn hình/chức năng bổ sung ngoài bốn route hiện tại. Không thêm điều hướng không hoạt động hoặc tự suy ra quyền từ trạng thái. Backend đã trả trạng thái, nhưng điều đó không đồng nghĩa bảng điều phối đã được tích hợp. |
| Chat, số tin mới và người tham gia | Hợp đồng Helpdesk hiện tại không có API trao đổi trong yêu cầu. Không hiện hội thoại, bộ đếm hoặc nút gửi giả. |
| Ngày tạo/ngày hoàn thành trong thông tin yêu cầu | DTO yêu cầu hiện tại không cung cấp các trường này. Không suy ra từ lịch sử. |
| Tên người thực hiện trong lịch sử | History hiện có transition, trạng thái, version và thời điểm; không có actor. Không dựng người thực hiện. |
| Tên người yêu cầu/người xử lý và danh sách phân công | Chỉ dùng dữ liệu được service trả về; giữ thông báo thiếu dữ liệu và khóa phân công khi không có danh sách hợp lệ. |

## Ảnh trước/sau

Ảnh chụp từ bản build production integration-local bằng Playwright, không phải
ảnh dựng từ thiết kế nội bộ. BFF `https://localhost:8443` không hoạt động khi kiểm tra;
phản hồi BFF được **giả lập chỉ trong test** để chụp cùng dữ liệu trước/sau.
Không có fixture hay fallback mock mới trong mã production integration-local.
Những ảnh này xác nhận bố cục, không chứng minh đăng nhập OIDC, persistence hay
Golden Path với backend thật.

Chỉ mục ảnh được tạo tại
[`playwright-report/issue-233-comparison/README.md`](playwright-report/issue-233-comparison/README.md),
gồm login/list/create/detail, trước/sau tại **1440px và 320px** (16 ảnh).
Ảnh gốc của hai lần chạy còn ở `playwright-report/issue-233-before/` và
`playwright-report/issue-233-after/`; hai bộ có thêm kích thước 768px và 390px.
Các thư mục ảnh là artifact cục bộ bị Git bỏ qua.

## Chạy kiểm tra

Tại `frontend/`:

```powershell
npm.cmd test -- --maxWorkers=2
npm.cmd run build:integration-local
npm.cmd run test:smoke -- --config tests/integration-local.playwright.config.ts --output playwright-report/issue-233-after
npm.cmd run build
npm.cmd run test:smoke
npm.cmd run test:smoke -- --config tests/mvp.playwright.config.ts
npm.cmd run check:security
```

Bộ kiểm tra UI duyệt 1440/768/390/320px, kiểm tra tràn ngang, axe WCAG,
tên sản phẩm, màu nút teal, điều hướng và loại trừ Facility. Nghiệm thu OIDC và
Golden Path vẫn cần stack thật hoạt động. CI GitHub cần được kiểm tra trên từng commit trước khi merge.

Kết quả local sau khi chỉnh giao diện:

| Kiểm tra | Kết quả |
| --- | --- |
| Unit (`--maxWorkers=2`) | 401/401 PASS |
| Build mặc định + integration-local | Cả hai PASS |
| Smoke MOCK | 17 PASS, 5 SKIP (các suite cần cấu hình riêng) |
| Luồng Helpdesk với transport test | 1 PASS |
| UI integration-local với BFF intercepted | 4 PASS; 4 kích thước/màn hình; axe không phát hiện vi phạm trong các quy tắc đã chạy |
| Credential-pattern check + `git diff --check` | PASS |
