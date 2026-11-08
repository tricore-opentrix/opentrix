<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors

SPDX-License-Identifier: Apache-2.0
-->

# DX-OS Portal demo at OLP 2026

**MOCK / DEVELOPMENT demonstration only. It does not claim that Core is integrated over HTTP.**

The Portal UI is in Vietnamese, so UI labels are quoted verbatim in bold with an English gloss in parentheses.

## Preparation

1. Run `npm.cmd ci` and `npm.cmd run dev` in `frontend/` (on Linux/macOS use `npm ci` and `npm run dev`).
2. Open `http://127.0.0.1:5173/session`. You can use a 1440 px desktop viewport, 390 px mobile or 834 px tablet.
3. Choose **Nhân viên — Ngọc Ánh** (Employee), click **Vào phiên demo** (Enter the demo session). All data and names in the UI are demo fixtures.
4. To start over: Integration status (**Trạng thái tích hợp**) → **Khôi phục dữ liệu demo** (Restore demo data). Reloading also resets the request data.

## Main scenario: two services, one platform

1. Dashboard: point out the statistics taken from fixtures and shown for the current role, the request table and the recent activity.
2. Click **Tạo yêu cầu mới** (Create a new request) and choose **Hỗ trợ CNTT** (IT support). Submit the empty form to show validation and focus on the first field with an error.
3. Enter a title of at least 8 characters, a description of at least 20 characters, a location and a priority. Attachments are marked **BLOCKED FEATURE** and no file is accepted.
4. Submit: the button shows loading and prevents duplicate submits, then the detail page opens with a success message. Note the request ID, usually `DX-1049` in a new session.
5. Use the **sidebar** to open Session status (**Trạng thái phiên**) → choose **Người xử lý — Lê Xuân Bảo** (Handler) → Continue. Do not reload the page during the demo flow.
6. Open the handler desk (**Bàn xử lý**) or My requests (**Yêu cầu của tôi**) and select the request you just created. Approve → enter a note → confirm. Continue with Start work → Complete; each step adds a timeline event. The request ends with no further actions.
7. Open Activity history (**Lịch sử hoạt động**) to follow the latest events.
8. Switch back to Employee and repeat with **Cơ sở vật chất** (Facilities). Explain that both services share the same form, model, service and timeline; the responses are currently mocks, and Core will own the real runtime.

## States to demonstrate

- **Search/filter/empty:** open the list, search for `cap quyen`, and combine it with the Facilities filter to reach the empty state. Clear the filters and use the Previous/Next buttons.
- **Loading:** open the list or a detail page; the mock has a 350 ms delay. Submitting the form shows the "Đang gửi" (Sending) state.
- **Network error:** Integration status → choose the simulated connection loss (**Mất kết nối mô phỏng**) → Apply → open the request list. Click "Tải lại dữ liệu" (Reload data) to recover; there is no automatic retry.
- **401:** apply the session-expired error (**Phiên hết hạn**) and then open the list. The demo session ends and the session page shows the simulated 401 message.
- **403/404:** apply the matching error and then open the list. No data is shown in the error. An employee who opens `/requests/DX-1047` gets the same message as for a non-existent ID. Do not present this as a real security test.
- **Unknown write result:** apply this error, use the sidebar to return to Overview, then open a new form and submit it completely. The error is kept for the next write even if data is read in between; the submit button is disabled after the error and nothing is resent automatically. Check the list and history as instructed.
- **Rejection:** choose a pending request, use the Handler role, enter a reason and confirm. The timeline shows the reason and the request ends.
- **Keyboard:** focus is clearly visible, the form has labels, dialogs keep focus and close on Escape; the mobile menu supports Escape. Reduced motion is respected.

## Finish with Integration status

Open Integration status and click **Kiểm tra chặn LIVE** (Check the LIVE block). State clearly that:

- Portal tier 2 builds and runs on its own; the backend is not modified.
- `RequestService` is a shared interface; the composition root currently binds `MockRequestService`.
- `HttpApiClient` always refuses before touching the network; there is no button or `.env` setting that enables LIVE.
- Identity, Gateway and Workflow wait for the security gates #22/#23/#24; the API contract waits for #37; attachments wait for an API with authorization checks (#26).
- Only a real end-to-end HTTP flow after a security review can be assessed against the Definition of Done of Issue #39. **Keep the Issue OPEN.**

The screenshots in the [evidence](https://github.com/tricore-opentrix/opentrix/blob/05c5d9967e88d24cfb4b41f4134dcc2522ac9253/docs/evidence/issue39-portal/README.md) (a permalink to commit `05c5d99` on the branch `feature/a05-portal-bff-integration`, which is not on `main`) were produced with browser automation on localhost; they are not visual mockups.
