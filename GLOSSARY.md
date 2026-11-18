<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# Workflow Authorization Glossary / Thuật ngữ phân quyền Workflow

> **Ngôn ngữ / Language:** [Tiếng Việt](#vi) · [English](#en)

---


<a id="vi"></a>

## Truy cập quy trình

Các thuật ngữ dùng để quyết định ai được gắn một tài nguyên vào quy trình hoặc truy cập một phiên
bản quy trình đã có. Các quy tắc này được hiện thực trong package
[`application.authorization`](https://github.com/tricore-opentrix/opentrix/tree/main/backend/src/main/java/com/tricore/dxos/application/authorization)
của backend.

| Thuật ngữ                                            | Định nghĩa                                                                                                                                                                                            | Trong mã                                                                       | Tránh dùng                         |
| ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ | ---------------------------------- |
| **Bên gọi đã xác minh** (_Verified caller_)          | Bên gọi có danh tính đã được ranh giới xác thực tin cậy chấp nhận. Danh tính tự khai báo không phải là bên gọi đã xác minh, và việc tạo được một đối tượng principal không có nghĩa là đã xác minh.   | `AuthenticatedPrincipal` lấy qua `CurrentPrincipal.requireVerified()`          | Người dùng tự nhận, cờ đã xác thực |
| **Quyền thao tác** (_Operation authority_)           | Quyền của bên gọi được yêu cầu một nhóm thao tác quy trình. Quyền này không cho phép truy cập một tài nguyên cụ thể.                                                                                  | `workflow:create`, `workflow:activate`, `workflow:transition`, `workflow:read` | Quyền trên tài nguyên              |
| **Liên kết tài nguyên** (_Resource binding_)         | Định danh của tài nguyên gắn với một phiên bản quy trình, đọc từ dữ liệu đã lưu chứ không lấy từ yêu cầu gửi lên. Liên kết này không xác lập việc bên gọi thuộc tổ chức (tenant) nào hay có quyền gì. | `ResourceReference`                                                            | Quyền sở hữu tài nguyên            |
| **Tài nguyên được thấy** (_Visible resource_)        | Tài nguyên mà bên gọi được phép biết là có tồn tại. Được thấy không đồng nghĩa với được gắn hoặc thao tác trên tài nguyên đó.                                                                         | `ALLOWED` hoặc `FORBIDDEN`                                                     | —                                  |
| **Tài nguyên ẩn** (_Hidden resource_)                | Tài nguyên không được tiết lộ sự tồn tại cho bên gọi. Phản hồi từ chối với tài nguyên ẩn giống hệt phản hồi với tài nguyên không tồn tại.                                                             | `HIDDEN`                                                                       | —                                  |
| **Chính sách không khả dụng** (_Unavailable policy_) | Chính sách truy cập không thể đưa ra quyết định đáng tin cậy. Khi không chắc chắn, hệ thống không bao giờ cấp quyền truy cập.                                                                         | `UNAVAILABLE`                                                                  | —                                  |

### Các quyết định truy cập

Mỗi lần kiểm tra truy cập quy trình trả về đúng một quyết định. Quyết định về tài nguyên được xét
trước, nên tài nguyên ẩn không bao giờ lộ ra qua lỗi thiếu quyền; quyền thao tác chỉ được kiểm tra
sau khi quyết định về tài nguyên là `ALLOWED`.

| Quyết định    | Ý nghĩa                                             | Phản hồi HTTP                   |
| ------------- | --------------------------------------------------- | ------------------------------- |
| `ALLOWED`     | Tài nguyên được thấy và thao tác được phép          | Yêu cầu được xử lý tiếp         |
| `FORBIDDEN`   | Tài nguyên được thấy nhưng thao tác không được phép | `403 FORBIDDEN`                 |
| `HIDDEN`      | Tài nguyên bị ẩn hoặc không tồn tại                 | `404 NOT_FOUND`                 |
| `UNAVAILABLE` | Không đưa ra được quyết định đáng tin cậy           | `503 AUTHORIZATION_UNAVAILABLE` |

---

<a id="en"></a>

## Workflow access

Terms used to decide who may bind a resource to a workflow or access an existing workflow
instance. The rules are implemented in the
[`application.authorization`](https://github.com/tricore-opentrix/opentrix/tree/main/backend/src/main/java/com/tricore/dxos/application/authorization)
package of the backend.

| Term                    | Definition                                                                                                                                                                                        | In code                                                                        | Avoid                            |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ | -------------------------------- |
| **Verified caller**     | A caller whose identity has been accepted by the trusted authentication boundary. A self-declared identity is not a verified caller, and constructing a principal object is not verification.     | `AuthenticatedPrincipal` obtained through `CurrentPrincipal.requireVerified()` | Claimed user, authenticated flag |
| **Operation authority** | A caller's permission to request a category of workflow operations. It does not grant access to an individual resource.                                                                           | `workflow:create`, `workflow:activate`, `workflow:transition`, `workflow:read` | Resource permission              |
| **Resource binding**    | The identity of the resource associated with a workflow instance, read from stored data rather than from the request. A binding does not establish the caller's tenant membership or permissions. | `ResourceReference`                                                            | Resource ownership               |
| **Visible resource**    | A resource whose existence the caller is allowed to know. Visibility alone does not grant permission to bind or act on that resource.                                                             | `ALLOWED` or `FORBIDDEN`                                                       | —                                |
| **Hidden resource**     | A resource whose existence must not be disclosed to the caller. A denial for a hidden resource is indistinguishable from a denial for a resource that does not exist.                             | `HIDDEN`                                                                       | —                                |
| **Unavailable policy**  | An access policy that cannot reach a trustworthy decision. Uncertainty never grants access.                                                                                                       | `UNAVAILABLE`                                                                  | —                                |

### Access decisions

Every workflow access check returns one decision. The resource decision is evaluated first, so a
hidden resource never reveals itself through a permission error; the operation authority is
checked only after the resource decision is `ALLOWED`.

| Decision      | Meaning                                                    | HTTP response                   |
| ------------- | ---------------------------------------------------------- | ------------------------------- |
| `ALLOWED`     | The resource is visible and the operation is permitted     | Request proceeds                |
| `FORBIDDEN`   | The resource is visible but the operation is not permitted | `403 FORBIDDEN`                 |
| `HIDDEN`      | The resource is hidden or does not exist                   | `404 NOT_FOUND`                 |
| `UNAVAILABLE` | No trustworthy decision could be made                      | `503 AUTHORIZATION_UNAVAILABLE` |
