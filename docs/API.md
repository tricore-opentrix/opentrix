<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# Tham chiếu API / API Reference

[Docs](README.md) · [Architecture](ARCHITECTURE.md) · [API](API.md) · [Testing](TESTING.md) · [Integration](INTEGRATION.md)

[Tiếng Việt](#vi) · [English](#en)

> **Owner / Phụ trách:** @ngang02012007-crypto · **Issue:** [#196](https://github.com/tricore-opentrix/opentrix/issues/196), [#194](https://github.com/tricore-opentrix/opentrix/issues/194) · **Status / Trạng thái:** DRAFT — REVIEW REQUIRED / BẢN NHÁP — CHỜ REVIEW.
>
> **Source baseline / Mốc source:** [832c75fc3164cf170eed3bb8f1e380d24dd65aba](https://github.com/tricore-opentrix/opentrix/commit/832c75fc3164cf170eed3bb8f1e380d24dd65aba). **Phase 2 evidence / Bằng chứng kiểm kê:** [5938d8e7cb117aa6bc8226ace1d786be2f7be703](https://github.com/tricore-opentrix/opentrix/commit/5938d8e7cb117aa6bc8226ace1d786be2f7be703). Các mốc khác nhau được giữ riêng; tài liệu không xác nhận runtime mới. / These revisions remain distinct; documentation is not new runtime acceptance.

<a id="vi"></a>

## Tiếng Việt

### A. Hiện trạng — mã nguồn và bằng chứng Giai đoạn 2

**Phạm vi:** Tham chiếu hợp đồng và giới hạn kiểm chứng từ mã nguồn tại `832c75fc3164cf170eed3bb8f1e380d24dd65aba`, đối chiếu [Khối C](09-evidence/phase-2/block-c-application.md). Không có kết quả chạy runtime mới trong bản sửa tài liệu này.

#### 1. Tổng quan

Tài liệu mô tả các tuyến do ứng dụng sở hữu và endpoint framework được cấu hình rõ. Hiện diện trong source không đồng nghĩa dịch vụ đã triển khai. `SOURCE-CONFIRMED`: đã đối chiếu implementation hoặc assertion; `VERIFIED`: phép kiểm cụ thể đã thành công tại SHA/môi trường xác định và có đầu ra lưu lại; `UNVERIFIED`: chưa đủ bằng chứng chạy/nghiệm thu. Ví dụ là dữ liệu tổng hợp, không phải phản hồi đã thu từ dịch vụ.

Nhãn khả dụng độc lập với bằng chứng: `IMPLEMENTED` = có code/cấu hình đăng ký; `GUARDED` = chịu điều kiện bật và giới hạn runtime; `TEST-ONLY` = chỉ đăng ký trong test; `PROPOSED` = thiết kế, chưa phải tuyến hiện thực. Không nhãn nào tự xác nhận triển khai/nghiệm thu. [DEVELOPMENT](DEVELOPMENT.md) và [TESTING](TESTING.md) thuộc bộ tài liệu canonical; phải đối chiếu phiên bản có trong nhánh công bố. Tệp không được theo dõi trong Git không phải implementation của baseline.

#### 2. Kiến trúc API

- **Backend riêng tư:** Spring MVC health và Helpdesk có guard; Spring Security kiểm bearer, Helpdesk quyết định quyền ứng dụng/tài nguyên trong transaction DB.
- **Portal BFF:** ứng dụng Spring riêng, giữ OAuth session và CSRF phía server; chỉ chuyển tiếp chín tuyến cho phép. Không phải proxy tổng quát và không thay thế phân quyền Backend.
- **Workflow chung:** có Java controller/DTO nhưng cố ý không đăng ký production; test exposure không phải API runtime được hỗ trợ.
- **Probe test:** controller lồng trong test kiểm handoff định danh; không phải endpoint production.
- **MOCK/fake:** dữ liệu Portal, fake Helpdesk preview và fetch mô phỏng không phải Backend API. `integration-local` chọn transport BFF nhưng không khởi động stack hay chứng minh kết nối xác thực.

[Thiết kế Core/Application](01-architecture/core-application-boundary.md) và [Gateway](02-core/gateway/gateway-architecture.md) có đề xuất/baseline cũ; ưu tiên source đăng ký tuyến, DTO, handler và test hiện hành. Prototype `/api/v1/requests/*` đã gỡ không được hỗ trợ. [R31](verification/r31/r31-helpdesk-api-crosswalk.md) là đối chiếu source tại baseline riêng, không phải OpenAPI/Swagger xuất từ runtime.

#### 3. Base URL và môi trường

| Địa chỉ local | Nguồn/mục đích | Giới hạn |
| --- | --- | --- |
| `http://127.0.0.1:8080` | Backend trong [Helpdesk runbook](../scripts/README-helpdesk-local.md) và [BFF runbook](../portal-bff/README.md) | Cấu hình local, Helpdesk buộc loopback; không chứng minh server đang chạy |
| `http://127.0.0.1:8081` | BFF và [Caddyfile.local](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/portal-bff/Caddyfile.local) | Upstream loopback; cookie Secure cần HTTPS ở trình duyệt |
| `https://localhost:8443` | Origin Caddy cho BFF/OIDC và frontend build | Cần stack và CA được tin cậy; ingress từ chối `/api/*` bằng 404 |
| `http://127.0.0.1:5173` | Vite MOCK trong [README](../README.md) | Demo UI, không phải base URL Backend/BFF |
| `http://127.0.0.1:4173` | [Playwright preview](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/frontend/playwright.config.ts) | Fixture browser MOCK, không phải LIVE |
| `http://localhost:8180/realms/tricore` | Issuer template/test cũ, hardcode trong real-token tests | Phải khớp chính xác; không thay bằng IP hoặc cổng khác |
| `http://127.0.0.1:8182/realms/tricore` | Kịch bản browser disposable riêng trong runbook BFF | Hướng dẫn lịch sử, không xác nhận provider đang hoạt động |

Dùng đúng discovery issuer của môi trường đã chọn. `OIDC_ISSUER_URI`, audience và resource client ID nằm trong [Backend application.yml](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/resources/application.yml); cấu hình client/provider/origin BFF nằm trong [BFF application.yml](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/portal-bff/src/main/resources/application.yml). Chưa có base URL production hay nghiệm thu triển khai. Không tái sử dụng DB, credentials hoặc issuer/sub cũ chỉ vì runbook nhắc tới.

#### 4. Xác thực và phân quyền

##### Backend

[SecurityConfig](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/java/com/tricore/dxos/infrastructure/identity/security/SecurityConfig.java) cho phép `/api/v1/health` khi không gửi bearer; các request khác cần xác thực. Backend stateless, tắt CSRF tại ranh giới bearer và không dùng cookie phiên browser làm định danh. Token sai không trở nên hợp lệ vì tuyến health là public.

JWT được kiểm chữ ký/khóa provider, issuer chính xác, audience, thời gian, `typ=Bearer`, expiration bắt buộc và subject dạng chuỗi không rỗng/đúng định dạng. Xem các validator được dẫn ở phần Anh. [SpringSecurityCurrentPrincipal](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/java/com/tricore/dxos/infrastructure/identity/security/SpringSecurityCurrentPrincipal.java) tạo actor ID `oidc:base64url(UTF8(iss)).base64url(UTF8(sub))` không padding. Chỉ nhận authority chính xác từ `resource_access.<configured-resource-client-id>.roles`: `workflow:create`, `workflow:activate`, `workflow:read`, `workflow:transition`; realm roles, header client hay principal tự tạo không cấp các quyền này.

| Thao tác | Authority chính xác | Điều kiện nghiệp vụ có thẩm quyền |
| --- | --- | --- |
| Create | `workflow:create`, `workflow:activate`, `workflow:read` | Membership tenant hoạt động, actor fact `submitter`, binding `mvp_request -> it-helpdesk@1` hoạt động |
| List/detail/history | `workflow:read` | Tenant/member/resource hoạt động và ACL cho đọc; list chỉ trả mục được thấy/đọc |
| Triage/Assign | `workflow:transition` và `workflow:read` | Coordinator và grant tài nguyên; Assign cần `TRIAGED`, worker hợp lệ/hoạt động cùng tenant |
| Start/Resolve | `workflow:transition` và `workflow:read` | Worker hiện được giao, còn hợp lệ và có grant tài nguyên |
| Confirm | `workflow:transition` và `workflow:read` | Requester gốc còn là submitter hợp lệ, có resolution, state/version phù hợp |

Tenant do server cấu hình, không lấy từ payload. Employee/Coordinator/Worker là vai trò ứng dụng từ actor facts trong DB, không tự suy từ JWT và không nhất thiết loại trừ nhau; không có admin bypass. [WorkflowAuthorization](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/java/com/tricore/dxos/application/authorization/WorkflowAuthorization.java) và [TenantResourceWorkflowAccessPolicy](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/java/com/tricore/dxos/application/authorization/TenantResourceWorkflowAccessPolicy.java) kiểm visibility trước lỗi thiếu quyền thao tác instance: tài nguyên/member thiếu hoặc không hoạt động/không thấy trả hidden 404; tài nguyên thấy được nhưng thiếu grant/authority có thể trả 403. Ownership không thay grant. Create/list có thứ tự kiểm riêng, không áp một thứ tự lỗi cho mọi thao tác.

##### BFF

Client confidential Authorization Code dùng `client_secret_basic`, PKCE S256, callback HTTPS ghim chính xác và token giữ ở server. Backend tự kiểm token chuyển tiếp. Ghi từ browser cần cookie phiên và `X-CSRF-TOKEN`; demo persona, actor ID browser và allowlist BFF không cấp quyền tài nguyên Backend.

#### 5. Danh mục endpoint

##### Health và Helpdesk có guard

| Method/path | Chủ sở hữu | Xác thực | Khả dụng |
| --- | --- | --- | --- |
| `GET /api/v1/health` | [HealthController](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/java/com/tricore/dxos/common/health/HealthController.java) | Public khi không có bearer | IMPLEMENTED |
| `GET /actuator/health` | Spring Boot Actuator | Cần xác thực theo security chain tùy chỉnh | Có cấu hình exposure; kết quả runtime UNVERIFIED |

Nguồn: [HelpdeskController](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/java/com/tricore/dxos/gateway/helpdesk/HelpdeskController.java), [PortalBackendClient](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/portal-bff/src/main/java/com/tricore/dxos/portal/PortalBackendClient.java). Backend chỉ bật khi `dxos.helpdesk.enabled=true`; [HelpdeskConfiguration](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/java/com/tricore/dxos/infrastructure/workflow/HelpdeskConfiguration.java) còn buộc DB disposable tại `127.0.0.1`, login `helpdesk_runtime_*`, `server.address=127.0.0.1`. BFF được cấu hình riêng, không bật hộ guard Backend.

| Method | Backend path | BFF browser path | Handler/mục đích | Xác thực |
| --- | --- | --- | --- | --- |
| POST | `/api/v1/mvp/requests` | `/bff/api/v1/mvp/requests` | `create`: tạo/kích hoạt | Bearer và create policy; BFF session + CSRF |
| GET | `/api/v1/mvp/requests` | `/bff/api/v1/mvp/requests` | `list`: trang cursor | Bearer và read policy; BFF session |
| GET | `/api/v1/mvp/requests/{id}` | `/bff/api/v1/mvp/requests/{id}` | `get`: chi tiết có quyền | Read policy/session |
| GET | `/api/v1/mvp/requests/{id}/history` | `/bff/api/v1/mvp/requests/{id}/history` | `history`: chuyển trạng thái | Read policy/session |
| POST | `/api/v1/mvp/requests/{id}/triage` | `/bff/api/v1/mvp/requests/{id}/triage` | `triage` / BFF `action` | Transition/read + Coordinator; session + CSRF |
| POST | `/api/v1/mvp/requests/{id}/assign` | `/bff/api/v1/mvp/requests/{id}/assign` | `assign` / `action` | Transition/read + Coordinator; session + CSRF |
| POST | `/api/v1/mvp/requests/{id}/start` | `/bff/api/v1/mvp/requests/{id}/start` | `start` / `action` | Transition/read + Worker được giao; session + CSRF |
| POST | `/api/v1/mvp/requests/{id}/resolve` | `/bff/api/v1/mvp/requests/{id}/resolve` | `resolve` / `action` | Worker được giao; session + CSRF |
| POST | `/api/v1/mvp/requests/{id}/confirm` | `/bff/api/v1/mvp/requests/{id}/confirm` | `confirm` / `action` | Transition/read + requester gốc hợp lệ; session + CSRF |

##### Session và handler xác thực BFF

| Method/path | Chủ sở hữu/mục đích | Xác thực/khả dụng |
| --- | --- | --- |
| `GET /bff/session` | [PortalSessionController](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/portal-bff/src/main/java/com/tricore/dxos/portal/PortalSessionController.java): chiếu session/CSRF | Public session check; IMPLEMENTED |
| `GET /oauth2/authorization/keycloak` | Resolver của [PortalSecurity](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/portal-bff/src/main/java/com/tricore/dxos/portal/PortalSecurity.java), bắt đầu login | Không cần phiên đăng nhập trước; handler framework IMPLEMENTED |
| `GET /login/oauth2/code/keycloak` | OAuth2 filter và callback ghim | Framework kiểm login transaction; cấu hình IMPLEMENTED, callback LIVE UNVERIFIED |
| `POST /bff/logout` | Logout filter và OIDC success handler | Session/CSRF; cấu hình IMPLEMENTED, logout provider LIVE UNVERIFIED |

Không phải danh mục mọi handler lỗi/điều hướng mặc định của Spring. `/login`, `/register` frontend là xem trước form MOCK, không phải API password/đăng ký Backend.

##### Workflow chưa đăng ký và probe test

| Method/path | Nguồn/trạng thái |
| --- | --- |
| `POST /api/v1/workflow-instances` | [WorkflowController.create](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/java/com/tricore/dxos/gateway/workflow/controller/WorkflowController.java); adapter chưa đăng ký, TEST-ONLY |
| `POST /api/v1/workflow-instances/{instanceId}/activate` | `activate`; cùng giới hạn |
| `POST /api/v1/workflow-instances/{instanceId}/transitions` | `transition`; cùng giới hạn |
| `GET /api/v1/workflow-instances/{instanceId}` | `get`; cùng giới hạn |
| `GET /api/v1/workflow-instances/{instanceId}/history` | `history`; cùng giới hạn |
| `GET /__test_only/gateway/identity-handoff` | Controller lồng trong `GatewayIdentityHandoffHttpTest`, TEST-ONLY |
| `GET /__test_only/gateway/identity-handoff-live` | Controller lồng trong `GatewayKeycloakTokenHttpIntegrationTest`, TEST-ONLY |

Không đăng ký các tuyến này để làm tài liệu có thể gọi được. `WorkflowHttpExposureTest` kiểm không có mapping production trong cấu hình test; request thật có thể bị security chặn trước routing. Hai probe không có tham số/body, chỉ trả 204 không body sau `WorkflowGatewayPrincipalGate` kiểm identity đã xác minh và `workflow:read`; không kiểm tài nguyên nghiệp vụ/tenant. Probe đầu dùng authentication kiểm soát; probe thứ hai cần `OIDC_TEST_ACCESS_TOKEN`, issuer hardcode `http://localhost:8180/realms/tricore`.

#### 6. Tham chiếu API Backend

##### Health

`GET /api/v1/health` không tham số/body, trả 200 `application/json`, `{"status":"UP"}`; không truy vấn PostgreSQL hay ghi nghiệp vụ. `HealthControllerTest` dùng MVC slice và decoder kiểm soát; không chứng minh startup/persistence. `/actuator/health` là management endpoint ID duy nhất được expose HTTP; JMX tắt, details/components ẩn. Kết quả tổng hợp, body/status phụ thuộc hạ tầng đang chạy, chưa được kiểm tại đây; không mặc định `UP`.

##### Quy tắc input/response chung

Chín thao tác dùng [HelpdeskService](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/java/com/tricore/dxos/infrastructure/workflow/HelpdeskService.java). `{id}` và `after` tùy chọn được parse UUID. Ghi cần JSON body, `Content-Type: application/json`; từ chối trường lạ, kể cả identity/tenant/role. `WorkflowJsonConfiguration` từ chối token JSON thừa phía sau. Không suy ra kiểm khóa trùng hoặc JSON strict toàn hệ thống.

| Input DTO | Trường bắt buộc/ràng buộc |
| --- | --- |
| `Create` | `title`: String không blank, tối đa 200; `description`: không blank, tối đa 4000; `requestType`: String không null, đúng `IT_HELPDESK` |
| `Version` | `expectedVersion`: Java Long không null, không âm, chỉ nhận JSON integer token |
| `Assign` | `assigneeId`: String không blank, tối đa 1024, actor hợp lệ do server nhận diện; `expectedAssignmentVersion`: Long strict không âm |
| `Resolve` | `expectedVersion`: Long strict không âm; `resolution`: String không blank, tối đa 4000 |

`WorkflowVersionDeserializer` không ép string/decimal thành version; âm/null lỗi validation, vượt signed Long lỗi decode. Frontend còn giới hạn safe integer JavaScript, hẹp hơn Java Long. Không khẳng định server tự trim text.

| Trường `RequestView` | Ý nghĩa/nullability |
| --- | --- |
| `id` | UUID request do server tạo |
| `title`, `description` | Nội dung được lưu |
| `requestType` | `IT_HELPDESK` |
| `requesterId` | Actor ID canonical do server suy ra |
| `assigneeId`, `resolution` | String có thể null, ban đầu null |
| `assignmentVersion` | Integer không âm, ban đầu 0, tăng khi assign |
| `workflowInstanceId` | ID Workflow do server tạo, khác UUID request |
| `state`, `version` | State Helpdesk và Workflow version hiện tại |
| `allowedActions` | Mảng theo caller từ `triage`, `assign`, `start`, `resolve`, `confirm`, có thể rỗng; gợi ý, không cấp quyền |
| `requesterDisplayName`, `assigneeDisplayName` | Chỉ detail, lấy từ record tin cậy; bỏ khi null qua `@JsonInclude(NON_NULL)`, không tự bịa nhãn |
| `eligibleAssignees` | Chỉ detail: mảng `{id, displayName}` với tên có thể null; chỉ xuất hiện khi caller có `assign` trong allowedActions. Rỗng khác với bị bỏ |

Create/action và list items không có ba trường detail-only. Detail có thể có tên dù không có danh bạ ứng viên. Các assertion `detailProjectsTrustedDisplayNamesAndLimitsCandidateDirectoryToAuthorizedAssign`, `noDirectoryNameMeansNullRatherThanInventedLabel` trong `HelpdeskHttpPostgresTest` kiểm phân biệt này.

##### Hợp đồng thao tác

Áp dụng phân quyền mục 4; input lỗi có thể 400/415, thiếu/sai authentication 401, policy 403/hidden 404/503 theo mục 9. Mapper chung không chứng minh mọi mã lỗi đều xảy ra ở mọi route.

| Method/path (sau `/api/v1/mvp/requests`) | Input | Thành công/tác động | Điều kiện riêng |
| --- | --- | --- | --- |
| POST collection | `Create` | 201 + Backend `Location: /api/v1/mvp/requests/{id}` + `RequestView`; tạo IDs, resource/ACL/business và kích hoạt `it-helpdesk@1` cùng transaction; `SUBMITTED`, version 0, assignment 0 | Không ID/idempotency key từ caller; đủ ba authority tạo và binding active; lỗi không để record dở dang |
| GET collection | `after` UUID tùy chọn, `limit` mặc định 50, integer 1–100 | 200 `Page` `{items: RequestView[], nextCursor: UUID-or-null}`; không ghi | Sort UUID không phải thời gian; IDs lớn hơn after và được thấy/đọc; không total/search/status filter/sort param |
| GET `/{id}` | UUID, không body | 200 `RequestView` và detail fields được phép; không ghi | Kiểm resource/member/grant hiện hành; hidden/missing cùng 404 |
| GET `/{id}/history` | UUID, không body | 200 `HistoryView[]`, không phân trang/ghi | Kiểm quyền request trước; entry chỉ `transitionId`, `sourceState`, `targetState`, `version`, `occurredAt`; không actorId/title/note/event ID giả |
| POST `/{id}/triage` | `Version` | 200 `RequestView`, `SUBMITTED -> TRIAGED`, version +1/history | Coordinator + transition/read; stale/wrong state 409 |
| POST `/{id}/assign` | `Assign` | 200 `RequestView`, vẫn TRIAGED, assignment +1, Workflow/history không đổi | Coordinator, assignment version đúng, worker active cùng tenant; stale/wrong state 409, assignee không hợp lệ 403; reassign cập nhật grants, có thể thu quyền worker cũ |
| POST `/{id}/start` | `Version` | 200 `RequestView`, `TRIAGED -> IN_PROGRESS`, version/history +1 | Worker hiện được giao; action HTTP `start`, history `start_work` |
| POST `/{id}/resolve` | `Resolve` | 200 `RequestView`, lưu resolution và `IN_PROGRESS -> RESOLVED` cùng version/history trong transaction | Worker hiện được giao; stale 409 không được giữ resolution/history mới |
| POST `/{id}/confirm` | `Version` | 200 `RequestView`, `RESOLVED -> CONFIRMED`, version/history +1 | Requester gốc hợp lệ, có resolution; terminal, không close route |

`HistoryView.occurredAt` là Java Instant không có annotation ép string như DTO Workflow chung. Decoder frontend nhận string hoặc số hữu hạn Jackson. **Định dạng timestamp wire Helpdesk chính xác vẫn UNVERIFIED**, không có HTTP assertion đã xem ghim định dạng; không tự tạo payload timestamp hoặc coi giống DTO chung. Các case `goldenPathUsesAllNineRoutesAndAuthoritativeVersions`, `paginationAndPrototypeIsolation`, `identityFieldsAreRejected`, `invalidVersionsAreRejectedWithoutWrite`, `staleAssignmentAndReassignmentRevokePreviousWorker`, `staleResolutionRollsBackBusinessFactAndHistory`, concurrent assignment/resolution và `unknownCommitIsNotRetriedAndCanBeReconciled` là assertion source, không phải kết quả PASS mới.

##### DTO Workflow chung — chỉ tham khảo test

Năm route chung chưa có hợp đồng expose/authorization production được hỗ trợ. Test đăng ký controller rõ ràng và cấp request attribute server `workflow.verifiedActor` cho transition; header/body/bearer text do client gửi không thay thế được.

| Thao tác test | Input và projection |
| --- | --- |
| Create | `CreateWorkflowInstanceRequest`: instanceId không blank khớp `[A-Za-z0-9][A-Za-z0-9._:-]*`, definitionId không blank, definitionVersion Long strict không âm, resourceType/resourceId không blank, từ chối trường lạ; test 201 + Location + WorkflowInstanceResponse |
| Activate | `ActivateWorkflowInstanceRequest`: không body hoặc JSON object rỗng; không state/version từ client; test 200 WorkflowInstanceResponse |
| Transition | `ExecuteWorkflowTransitionRequest`: transitionId không blank, expectedVersion Long strict không âm, actor attribute server; test 200 `{instance, record}` |
| Get/history | instanceId cùng pattern; test 200 instance/mảng history, không suy ra policy nghiệp vụ Helpdesk |

`WorkflowInstanceResponse`: `instanceId`, `definitionId`, `definitionVersion`, `resourceType`, `resourceId`, `currentState`, `runtimeVersion`, `lifecycle`, `createdAt`, `updatedAt`. `WorkflowHistoryResponse`: `instanceId`, `transitionId`, `sourceState`, `targetState`, `actorId`, `resultingRuntimeVersion`, `occurredAt`. `WorkflowTransitionResponse` bọc hai record. Version là integer, IDs/resource/state là string; lifecycle `NOT_STARTED`, `ACTIVE`, `COMPLETED`; Instant ở DTO chung ép JSON string. Đây không phải schema Helpdesk.

#### 7. Tham chiếu Portal BFF

##### Session, login, logout

`GET /bff/session`: 200, `Cache-Control: no-store`, `{"authenticated":false}` hoặc `{"authenticated":true,"csrfToken":"<session-csrf-token>"}`; không token/user/role claims. `PortalAuthorization` hỏi authorized-client manager lấy token còn hạn dùng được; không có/không dùng được authorization thì vô hiệu phiên và trả anonymous. GET này có thể kích hoạt xử lý refresh server, không phải DB health.

Login qua `/oauth2/authorization/keycloak`; test assertion redirect 3xx có state, code_challenge và S256. Callback đúng `${PORTAL_PUBLIC_ORIGIN}/login/oauth2/code/keycloak`, cần secret và không tái dùng client `tricore-api`. Framework quản lý query/callback/navigation/lỗi provider, không có DTO JSON tùy chỉnh; LIVE UNVERIFIED. Logout POST cần `X-CSRF-TOKEN` (thiếu trả 403 theo test), vô hiệu session, xóa `__Host-DXOS-Portal`, gọi OIDC logout handler, đặt đích public origin + `/`; redirect/revocation thật chưa xác minh, không bịa JSON logout response. Session timeout 30 phút; cookie Secure, HttpOnly, SameSite=Lax, path `/`, không Domain; hành vi browser cần kiểm HTTPS.

##### Forwarding và response

Chín route dùng UUID và after/limit như Backend. Action chỉ `triage`, `assign`, `start`, `resolve`, `confirm`; action lạ trả 404 rỗng sau security. Test MVC fixture có unmapped route và PUT collection 405, không suy ra routing luôn chạy trước authentication.

BFF đọc ghi tối đa **32,768 bytes**, chuyển JSON tới Backend origin cố định, Backend kiểm DTO/nghiệp vụ. Không tạo URL đích từ input browser; list chỉ chuyển limit/after, không tunnel query/header tùy ý. Chỉ token server thành Authorization Bearer, thêm Accept JSON/content type ghi; không chuyển cookie, identity header hay bearer browser. Backend origin chỉ HTTPS hoặc literal `http://127.0.0.1`, không credentials/query/fragment/path ngoài `/`; public origin HTTPS ghim, không path/trailing slash, được `PortalOrigin`/`PortalSecurity` kiểm.

Client không theo redirect; connect timeout 5 giây, request timeout 15 giây; response giới hạn **2,000,000 bytes**, body được đóng. Status/body upstream được chấp nhận chuyển JSON + no-store; upstream 401 làm mất phiên và trả 401 rỗng, 403/404/409 giữ status/body không làm mất phiên theo test. Không chuyển header tùy ý, đặc biệt **không chuyển Location khi create**; dùng id response để đọc tiếp. Kể cả 502 rỗng sau POST cũng không chứng minh rollback; một attempt, không tự retry.

Transport frontend same-origin chỉ local HTTPS, thêm `/bff` vào path cho phép, cookie same-origin, từ chối redirect, CSRF trong memory; không thay authorization Backend. HelpdeskApiClient yêu cầu create 201, còn lại 200, kiểm projection, vô hiệu instance khi 401; write thành công nhưng response không đọc được có thể đã commit.

#### 8. Workflow Helpdesk và state

Định nghĩa [it-helpdesk@1](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/resources/db/helpdesk/definition.sql) là nghiệp vụ dùng cơ chế Workflow chung, không phải API nghiệp vụ hardcode trong Core.

| HTTP operation | Actor | State | Workflow version/history | Assignment version |
| --- | --- | --- | --- | --- |
| Create | Submitter hợp lệ | Tạo/kích hoạt SUBMITTED | Bắt đầu 0; activation không thêm transition | Bắt đầu 0 |
| Triage | Coordinator | SUBMITTED -> TRIAGED | +1 / triage | Không đổi |
| Assign/reassign | Coordinator | TRIAGED -> TRIAGED | Không đổi/không transition | +1 mỗi lần thành công |
| Start | Worker hiện được giao, hợp lệ | TRIAGED -> IN_PROGRESS | +1 / start_work | Không đổi |
| Resolve | Worker hiện được giao, hợp lệ | IN_PROGRESS -> RESOLVED | +1 / resolve | Không đổi |
| Confirm | Requester gốc hợp lệ | RESOLVED -> CONFIRMED | +1 / confirm, terminal | Không đổi |

Hai counter độc lập, không phải ETag: transition nhận expectedVersion, assign nhận expectedAssignmentVersion. Golden Path cuối version 4, bốn transition; không CLOSED, close, public activate Helpdesk hoặc transition tùy ý. HelpdeskService kiểm lại caller/resource/business trong tenant guard của transaction PostgresWorkflowPersistence; business/state/history commit cùng nhau, ghi bị từ chối/stale không được để thay đổi dở dang. allowedActions có thể cũ; server/version quyết định. Không idempotency key; trường lạ bị từ chối. Assign lại cùng người vẫn có thể tăng version; mất response phải đọc detail/history có quyền trước khôi phục, không replay POST/tạo lại mù.

#### 9. Xử lý lỗi

##### Envelope và policy Backend

`ApiError`: `{status: integer, code: string, message: string, errors: object<string,string>}`; không timestamp/path/request ID. Entry point authentication trả 401 JSON, `WWW-Authenticate: Bearer`, code AUTHENTICATION_REQUIRED, message `Authentication is required`. HelpdeskExceptionHandler kế thừa mapper Workflow và bổ sung chống dò tài nguyên.

| HTTP | Code | Ý nghĩa/phạm vi |
| --- | --- | --- |
| 400 | VALIDATION_FAILED | Constraint DTO/method/bound param; field errors nếu exception có |
| 400 | INVALID_BODY | JSON lỗi/không chấp nhận, trường lạ, version strict sai, trailing tokens |
| 401 | AUTHENTICATION_REQUIRED | Thiếu/sai token; adapter test chung cũng map thiếu actor attribute với message khác |
| 403 | FORBIDDEN | Tài nguyên thấy được nhưng thiếu quyền hoặc không đủ eligibility/authority |
| 404 | NOT_FOUND | Hidden/missing Helpdesk, kể cả definition/instance thiếu; `Workflow resource not found`, errors rỗng |
| 409 | VERSION_CONFLICT, TRANSITION_NOT_ALLOWED, INSTANCE_COMPLETED, INSTANCE_ALREADY_EXISTS | Mapper version/state/trùng; route Helpdesk cố định không expose mọi operation chung |
| 415 | UNSUPPORTED_MEDIA_TYPE | MVC handler chung, message `Workflow input requires application/json` |
| 422 | INVALID_TRANSITION | ID transition chung không có; caller Helpdesk không truyền ID tùy ý qua năm action |
| 500 | OPERATION_FAILURE, INTERNAL_ERROR | Lỗi normalized, không lộ SQL/provider thô |
| 503 | AUTHORIZATION_UNAVAILABLE | Không xác lập được facts/authorization có thẩm quyền, khác unknown commit |
| 503 | COMMIT_OUTCOME_UNKNOWN | Có thể đã commit; đối soát detail/history, không tự retry |

Adapter test Workflow giữ DEFINITION_NOT_FOUND/INSTANCE_NOT_FOUND riêng; Helpdesk cố ý gộp với hidden resource. HelpdeskErrorContractTest dùng service mock để kiểm mapper; GET mock lỗi không chứng minh ghi thật đã xảy ra. Envelope chỉ áp dụng entry point/advice được chỉ ra, không mọi routing/management/security-filter failure; không mặc định mọi 404/405/BFF đều là ApiError.

##### Lỗi sinh tại BFF

| HTTP/body | Điều kiện |
| --- | --- |
| 400 rỗng | Limit ngoài 1–100 hoặc lỗi đọc body ghi; UUID/type binding do framework |
| 401 rỗng | Không token server dùng được hoặc upstream 401; vô hiệu phiên khi áp dụng |
| 403 framework | CSRF/denied route trước forwarding; không ghim schema ApiError |
| 404 rỗng | Action không hỗ trợ sau security; unmapped route được test MVC riêng |
| 405 framework | Method không được MVC fixture hỗ trợ |
| 413 rỗng | Ghi vượt 32,768 bytes, không forward |
| 502 rỗng | Redirect/status upstream không được nhận hoặc response quá 2,000,000 bytes; không chứng minh write rollback |
| 503 `{"code":"UPSTREAM_UNAVAILABLE"}` | I/O/interruption khi đọc |
| 503 `{"code":"COMMIT_OUTCOME_UNKNOWN"}` | I/O/interruption khi ghi/khi đọc response ghi, không retry |

503 Backend được relay có thể đầy đủ ApiError, 503 sinh ở BFF chỉ có code. Đọc status/code có sẵn, không giả định schema đồng nhất. Lỗi đọc và ghi không rõ outcome cần xử lý khác nhau.

#### 10. Ví dụ request/response

Các JSON, UUID, text và placeholder dưới đây là minh họa theo source, không phải credentials/kết quả chạy. Chỉ thay actor/version bằng giá trị server trả được phép; không gửi vào dữ liệu dùng chung.

##### Tạo qua BFF

POST `/bff/api/v1/mvp/requests`, có session và X-CSRF-TOKEN. Client Backend riêng dùng route private tương ứng và bearer được cấp quyền.

```json
{"title":"QA disposable request","description":"Synthetic request for an isolated review environment.","requestType":"IT_HELPDESK"}
```

Ví dụ 201 RequestView cho submitter không có action Coordinator; Backend có Location, BFF không chuyển header đó:

```json
{
  "id":"00000000-0000-4000-8000-000000000001",
  "title":"QA disposable request",
  "description":"Synthetic request for an isolated review environment.",
  "requestType":"IT_HELPDESK",
  "requesterId":"<server-derived-canonical-actor-id>",
  "assigneeId":null,"resolution":null,"assignmentVersion":0,
  "workflowInstanceId":"<server-generated-workflow-id>",
  "state":"SUBMITTED","version":0,"allowedActions":[]
}
```

Trường lấy từ RequestView, counter ban đầu từ schema.sql/activation và state/action theo assertion Golden Path. Create không có tên/danh bạ detail-only.

##### Body action

Coordinator Triage POST `.../{id}/triage`:

```json
{"expectedVersion":0}
```

Coordinator Assign khi TRIAGED:

```json
{"assigneeId":"<id-from-authorized-detail-eligibleAssignees>","expectedAssignmentVersion":0}
```

Start trong chuỗi ví dụ dùng `{"expectedVersion":1}`; Resolve:

```json
{"expectedVersion":2,"resolution":"Synthetic issue resolved and checked."}
```

Confirm dùng `{"expectedVersion":3}`. Đây chỉ là version của đúng chuỗi đó; có thao tác/concurrency khác phải lấy version server hiện tại. Action thành công trả toàn bộ RequestView, không chỉ status hay Workflow transition DTO.

##### Trang rỗng và lỗi

```json
{"items":[],"nextCursor":null}
```

Helpdesk 404 hidden/missing:

```json
{"status":404,"code":"NOT_FOUND","message":"Workflow resource not found","errors":{}}
```

BFF uncertain write 503:

```json
{"code":"COMMIT_OUTCOME_UNKNOWN"}
```

Dạng Backend cùng code còn status/message đối soát/errors; session xem mục 7. Không cung cấp ví dụ timestamp history hoặc response callback khi wire behavior chưa xác minh.

#### 11. Lưu ý bảo mật

- Kiểm riêng identity JWT, authority, tenant/resource grants active và eligibility nghiệp vụ; session BFF/ownership không bypass Backend.
- Không gửi tenant/requester/actor/role trong body; Assign dùng actor ID server nhận, không display name/role browser.
- Giữ Backend private; ingress HTTPS bỏ forwarding header không tin cậy, ghim host/protocol, khớp SNI/Host, chặn `/api/*`; triển khai/trust thực cần review.
- OAuth secret/token ở server; CSRF ở memory browser. Giữ HTTPS, cookie Secure/HttpOnly, CSRF; không chia sẻ/log credentials, cookie, key hay identity thật.
- Giữ hai version counter và đọc lại allowedActions theo caller; không override concurrency. Hidden/missing cùng response theo thiết kế.
- Không auto replay/idempotency key; mất mạng, malformed success, unknown commit hoặc BFF 502 sau POST không cho phép retry. Đối soát bằng GET có quyền.

#### 12. Kiểm thử và xác minh API

[TESTING](TESTING.md) là nguồn lệnh/guard/evidence canonical; tài liệu API không provision fixture hoặc xác nhận lệnh đã chạy.

| Hợp đồng | Bằng chứng source | Giới hạn |
| --- | --- | --- |
| Health/public | HealthControllerTest | MVC slice, không health hạ tầng thật |
| JWT/role/header giả | SecurityConfigTest, SpringSecurityCurrentPrincipalTest, identity probes | Decoder/filter kiểm soát; real-token cần issuer/token đúng |
| Payload/ACL/lifecycle/conflict/atomicity | HelpdeskHttpPostgresTest | DB opt-in disposable, đa số IdP tổng hợp; B06 có token thật vẫn không BFF/browser E2E |
| Hidden/missing/unknown commit | HelpdeskErrorContractTest | Service mock, commit uncertainty DB là phép kiểm riêng |
| Generic DTO/error/không đăng ký route | WorkflowControllerTest, WorkflowHttpExposureTest | Đăng ký test không mở route production |
| PKCE/session/CSRF/forwarding | PortalSecurityTest, PortalBackendClientTest | OAuth session/manager/HTTP mock, không callback/refresh/logout thật |
| Decode/composition frontend | HelpdeskApiClient.test.ts, sameOriginTransport.test.ts, LocalHelpdeskIntegration.test.tsx | Fake transport/fetch; MOCK/fake browser không chứng minh LIVE |

Các link đến từng suite tương ứng nằm ở bảng cùng mục trong bản Anh. CI kiểm rõ execution/zero-skip của ba suite identity/exposure, không provision toàn stack PostgreSQL/Keycloak/BFF/browser. Không suy green job thành mọi behavior có guard đã chạy; không có counts/PASS mới ở đây. LIVE cần exact SHA/environment, request xác thực thật, negative cases, version/history, restart persistence, báo cáo mới và evidence đã làm sạch.

#### 13. Giới hạn đã biết

| Trạng thái | Giới hạn |
| --- | --- |
| IMPLEMENTED / SOURCE-CONFIRMED | Có controller/DTO/policy/handler; không chứng minh service đang chạy |
| GUARDED | Giữ opt-in, DB disposable loopback, runtime login; cấu hình/build không chứng minh operation đã xác thực |
| TEST-ONLY | Generic Workflow HTTP và identity probes chỉ đăng ký test, không public service contract |
| PROPOSED / chưa có runtime API | Kiến trúc mục tiêu, OpenAPI tooling, Facility, upload/storage, Flowable, APISIX không được quảng bá là endpoint hoàn thành |
| UNVERIFIED | Startup mới, timestamp Helpdesk chính xác, Actuator, callback/refresh/logout/cookie thật, LIVE cùng SHA chưa được kiểm |
| Phụ thuộc tài liệu | Đối chiếu DEVELOPMENT/TESTING tại nhánh công bố; docs/contracts không có tại baseline source, không tạo nguồn/spec thay thế giả |

Không hỗ trợ prototype Request đã gỡ, close Helpdesk, proxy tổng quát, identity/tenant tự chọn và idempotency-key field. Lỗi framework/security không có một schema JSON bảo đảm chung. Báo cáo lịch sử và đề xuất không bỏ các giới hạn đó.

#### 14. Nguồn tham chiếu

- [README](../README.md), [CONTRIBUTING](../CONTRIBUTING.md), [SECURITY](../SECURITY.md), [DEVELOPMENT](DEVELOPMENT.md), [TESTING](TESTING.md).
- [Backend](../backend/README.md), [BFF](../portal-bff/README.md), [Helpdesk runbook](../scripts/README-helpdesk-local.md).
- [R31](verification/r31/r31-helpdesk-api-crosswalk.md), [Core/Application](01-architecture/core-application-boundary.md), [Gateway](02-core/gateway/gateway-architecture.md), mỗi nguồn có baseline/status riêng.
- Snapshot Phase 2 tại `5938d8e7cb117aa6bc8226ace1d786be2f7be703`: [Khối A](https://github.com/tricore-opentrix/opentrix/blob/5938d8e7cb117aa6bc8226ace1d786be2f7be703/docs/09-evidence/phase-2/block-a-architecture.md), [Khối B](https://github.com/tricore-opentrix/opentrix/blob/5938d8e7cb117aa6bc8226ace1d786be2f7be703/docs/09-evidence/phase-2/block-b-backend-infra.md), [Khối C](https://github.com/tricore-opentrix/opentrix/blob/5938d8e7cb117aa6bc8226ace1d786be2f7be703/docs/09-evidence/phase-2/block-c-application.md); commit chỉ thêm báo cáo không chứng minh runtime mới.

### B. Mục tiêu — PROPOSED, chưa nghiệm thu

- **PROPOSED · [#112](https://github.com/tricore-opentrix/opentrix/issues/112):** công bố OpenAPI/Swagger xuất runtime, review chín route có guard; chưa phải hợp đồng được nghiệm thu.
- **PROPOSED · [#118](https://github.com/tricore-opentrix/opentrix/issues/118):** chứng minh Golden Path browser Keycloak–BFF–Backend–PostgreSQL và ca âm tính.
- **PROPOSED · [#194](https://github.com/tricore-opentrix/opentrix/issues/194):** đồng bộ điều hướng, link, source revisions và bằng chứng.

**Điều kiện công bố:** kiểm link, SHA source phù hợp, kết quả test thật, SPDX/REUSE và independent review; bản sửa tài liệu không tự xác nhận các điều kiện này PASS.

<a id="en"></a>

## English

### A. Current state — source and Phase 2 evidence

**Scope:** The detailed sections below preserve the source-inspected contract and test boundaries. This documentation update performs no runtime execution. Compare with [Phase 2 Block C](09-evidence/phase-2/block-c-application.md).

#### 1. Overview

This reference describes application-owned routes and explicitly configured framework endpoints at **`832c75fc3164cf170eed3bb8f1e380d24dd65aba`**. Untracked artifacts are not baseline implementation. Source presence alone does not establish deployment or acceptance.

Evidence levels: **SOURCE-CONFIRMED** means inspected implementation or test assertions; **VERIFIED** requires a successful check at an identified SHA/environment with retained results; **UNVERIFIED** means execution/acceptance is not established. No application tests, servers, database operations or LIVE E2E were run for this document. Examples are synthetic illustrations, not captured responses.

Availability labels are separate from evidence: **IMPLEMENTED** = registered code/configuration exists; **GUARDED** = explicit opt-in/runtime restrictions apply; **TEST-ONLY** = exposure exists in test configuration only; **PROPOSED** = design, not an implemented route. None implies a deployed or accepted service.

[DEVELOPMENT.md](DEVELOPMENT.md) and [TESTING.md](TESTING.md) are canonical guides; use the versions available on the publication branch. A documentation link alone does not establish runtime acceptance.

#### 2. API Architecture

- **Backend private API:** Spring MVC health and guarded Helpdesk handlers. Spring Security validates bearer tokens; Helpdesk performs authoritative application/resource authorization inside its database transaction.
- **Portal BFF browser API:** separate Spring application using a server-side OAuth session and CSRF. It forwards only the Helpdesk routes listed below, with a server-held bearer token. It is not a generic proxy or a replacement for Backend authorization.
- **Generic Workflow adapter:** Java controller/DTO code exists, but the controller is deliberately not registered in production. Its test exposure is not a supported runtime API.
- **Test-only probes:** nested test controllers verify identity handoff; they are not production endpoints.
- **MOCK/fake transports:** Portal demo data, fake Helpdesk preview and mocked fetch responses are not Backend APIs. `integration-local` selects real BFF transport code but does not start a stack or prove authenticated connectivity.

The [Core/Application design](01-architecture/core-application-boundary.md) and [Gateway architecture](02-core/gateway/gateway-architecture.md) contain proposals and older baselines. Route registration, current DTOs, handlers and tests take precedence for this reference. Removed `/api/v1/requests/*` prototype routes are not supported. No OpenAPI/Swagger specification is added; the existing [R31 crosswalk](verification/r31/r31-helpdesk-api-crosswalk.md) is a source comparison at its own historical baseline, not a runtime specification.

#### 3. Base URLs and Environments

| Local address | Evidence / purpose | Limit |
| --- | --- | --- |
| `http://127.0.0.1:8080` | Backend address/port in [Helpdesk runbook](../scripts/README-helpdesk-local.md) and [BFF runbook](../portal-bff/README.md) | Explicit local setup; Helpdesk requires loopback binding. Not evidence of a running server |
| `http://127.0.0.1:8081` | BFF port selected in its runbook and targeted by [Caddyfile.local](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/portal-bff/Caddyfile.local) | Private loopback upstream; Secure cookies require browser access through HTTPS |
| `https://localhost:8443` | Supplied Caddy public origin; BFF/OIDC paths and built frontend | Requires configured stack and browser-trusted local CA. `/api/*` is rejected with 404 by ingress |
| `http://127.0.0.1:5173` | Default MOCK Vite development URL in [README](../README.md) | UI demonstration, not Backend/BFF base URL |
| `http://127.0.0.1:4173` | [Playwright preview](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/frontend/playwright.config.ts) | MOCK browser fixture, not LIVE API deployment |
| `http://localhost:8180/realms/tricore` | Older template/test issuer; real-token tests hardcode it | Exact issuer identity; not interchangeable with `127.0.0.1` or another port |
| `http://127.0.0.1:8182/realms/tricore` | Separate disposable browser scenario in the BFF runbook | Historical setup instructions, not confirmation of current provider availability |

Use the exact discovery issuer configured for the selected environment. Backend `OIDC_ISSUER_URI`, audience and resource client ID come from [application.yml](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/resources/application.yml); BFF provider/client/origin settings come from [its application.yml](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/portal-bff/src/main/resources/application.yml). There is no production base URL or deployment acceptance established here. Do not reuse retained database resources, credentials or issuer/sub mappings merely because a runbook names them.

#### 4. Authentication and Authorization

##### Backend

[SecurityConfig](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/java/com/tricore/dxos/infrastructure/identity/security/SecurityConfig.java) permits `/api/v1/health` without authentication; all other requests require authentication. The Backend is stateless, disables CSRF for its bearer boundary and does not use browser session cookies as identity.

JWT verification includes signature/provider keys, exact configured issuer, audience, timestamp checks, an access-token `typ` claim equal to `Bearer`, required expiration and a nonblank, well-formed string subject. See [AccessTokenTypeValidator](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/java/com/tricore/dxos/infrastructure/identity/security/AccessTokenTypeValidator.java), [SubjectValidator](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/java/com/tricore/dxos/infrastructure/identity/security/SubjectValidator.java) and [ExpirationValidator](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/java/com/tricore/dxos/infrastructure/identity/security/ExpirationValidator.java). A public health path does not make an invalid bearer token trusted.

[SpringSecurityCurrentPrincipal](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/java/com/tricore/dxos/infrastructure/identity/security/SpringSecurityCurrentPrincipal.java) derives the canonical actor ID as `oidc:base64url(UTF8(iss)).base64url(UTF8(sub))`, without padding. It reads only supported exact authority names from `resource_access.<configured-resource-client-id>.roles`: `workflow:create`, `workflow:activate`, `workflow:read`, `workflow:transition`. Realm roles, client headers or fabricated principal fields do not grant these authorities.

| Operation | Required exact authorities | Additional authoritative business policy |
| --- | --- | --- |
| Create Helpdesk request | `workflow:create`, `workflow:activate`, `workflow:read` | Active configured-tenant membership, `submitter` actor fact, active `mvp_request -> it-helpdesk@1` binding |
| List/detail/history | `workflow:read` | Active tenant/member/resource and readable resource ACL; list only returns visible/readable items |
| Triage/Assign | `workflow:transition` **and** `workflow:read` | Coordinator actor fact, explicit resource grants; assignment also requires `TRIAGED` and an eligible active worker in the same tenant |
| Start/Resolve | `workflow:transition` **and** `workflow:read` | Current assignee with active worker eligibility and applicable resource grants |
| Confirm | `workflow:transition` **and** `workflow:read` | Original requester still has submitter eligibility; resolution exists and state/version permit confirmation |

The tenant is server configuration, not a request field. Employee/Coordinator/Worker are application role descriptions backed by database actor facts; they are not automatic JWT roles or mutually exclusive roles. No administrator bypass is implemented by these rules.

[WorkflowAuthorization](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/java/com/tricore/dxos/application/authorization/WorkflowAuthorization.java) and [TenantResourceWorkflowAccessPolicy](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/java/com/tricore/dxos/application/authorization/TenantResourceWorkflowAccessPolicy.java) enforce visibility before an instance-operation authority denial: inactive/missing resource/member or no visibility produces hidden 404; a visible resource without the requested grant/authority can produce 403. Ownership alone never substitutes for explicit operation grants. Creation/list have their own preliminary checks; do not assume every denial has the same precedence.

##### BFF

The BFF requires a confidential Authorization Code client using `client_secret_basic`, adds PKCE S256, pins the HTTPS callback and keeps OAuth tokens server-side. Backend verifies the forwarded token independently. Browser writes use the BFF session cookie plus `X-CSRF-TOKEN`; a demo persona, browser actor ID or BFF route allowlist cannot grant Backend resource access.

#### 5. API Endpoint Inventory

##### Registered health and guarded Helpdesk

Health owners: [HealthController](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/java/com/tricore/dxos/common/health/HealthController.java), [management configuration](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/resources/application.yml) and [security configuration](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/java/com/tricore/dxos/infrastructure/identity/security/SecurityConfig.java).

| Method/path | Owner | Authentication | Availability |
| --- | --- | --- | --- |
| `GET /api/v1/health` | `HealthController.health` | Public when no bearer is supplied | IMPLEMENTED |
| `GET /actuator/health` | Spring Boot Actuator | Authenticated under the custom security chain | IMPLEMENTED exposure configuration; exact runtime health result UNVERIFIED |

Every pair below is source-confirmed in [HelpdeskController](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/java/com/tricore/dxos/gateway/helpdesk/HelpdeskController.java) and [PortalBackendClient](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/portal-bff/src/main/java/com/tricore/dxos/portal/PortalBackendClient.java). Backend routes are **GUARDED**, disabled unless `dxos.helpdesk.enabled=true`; [HelpdeskConfiguration](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/java/com/tricore/dxos/infrastructure/workflow/HelpdeskConfiguration.java) additionally requires a `127.0.0.1` disposable database, `helpdesk_runtime_*` login and `server.address=127.0.0.1`. BFF mappings are **IMPLEMENTED** in a separately configured BFF; they do not enable the Backend guard.

| Method | Backend path | BFF browser path | Handler / business purpose | Authentication |
| --- | --- | --- | --- | --- |
| POST | `/api/v1/mvp/requests` | `/bff/api/v1/mvp/requests` | `create`: create and activate | Backend bearer + create policy; BFF session + CSRF |
| GET | `/api/v1/mvp/requests` | `/bff/api/v1/mvp/requests` | `list`: cursor page | Backend bearer + read policy; BFF session |
| GET | `/api/v1/mvp/requests/{id}` | `/bff/api/v1/mvp/requests/{id}` | `get`: authorized detail | Same read policy/session |
| GET | `/api/v1/mvp/requests/{id}/history` | `/bff/api/v1/mvp/requests/{id}/history` | `history`: authorized transition history | Same read policy/session |
| POST | `/api/v1/mvp/requests/{id}/triage` | `/bff/api/v1/mvp/requests/{id}/triage` | Backend `triage`, BFF `action` | Backend transition/read + Coordinator; BFF session + CSRF |
| POST | `/api/v1/mvp/requests/{id}/assign` | `/bff/api/v1/mvp/requests/{id}/assign` | `assign` / `action` | Backend transition/read + Coordinator; BFF session + CSRF |
| POST | `/api/v1/mvp/requests/{id}/start` | `/bff/api/v1/mvp/requests/{id}/start` | `start` / `action` | Backend transition/read + assigned Worker; BFF session + CSRF |
| POST | `/api/v1/mvp/requests/{id}/resolve` | `/bff/api/v1/mvp/requests/{id}/resolve` | `resolve` / `action` | Same assigned-Worker/session/CSRF policy |
| POST | `/api/v1/mvp/requests/{id}/confirm` | `/bff/api/v1/mvp/requests/{id}/confirm` | `confirm` / `action` | Backend transition/read + eligible original requester; BFF session + CSRF |

##### BFF session and authentication handlers

| Method/path | Owner / purpose | Authentication and availability |
| --- | --- | --- |
| `GET /bff/session` | [PortalSessionController](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/portal-bff/src/main/java/com/tricore/dxos/portal/PortalSessionController.java): usable session/CSRF projection | Public session check; IMPLEMENTED |
| `GET /oauth2/authorization/keycloak` | [PortalSecurity](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/portal-bff/src/main/java/com/tricore/dxos/portal/PortalSecurity.java) authorization resolver: initiate provider login | No existing login required; IMPLEMENTED framework handler |
| `GET /login/oauth2/code/keycloak` | Spring OAuth2 login filter; exact callback pinned by `PortalSecurity` and client configuration | Provider callback with framework-validated login transaction; IMPLEMENTED configuration, live callback UNVERIFIED |
| `POST /bff/logout` | `PortalSecurity` logout filter / OIDC logout success handler | Session and CSRF required; IMPLEMENTED configuration, live provider logout UNVERIFIED |

These are the configured application/authentication contracts, not an inventory of every Spring internal/default error or navigation handler. Frontend `/login` and `/register` pages are MOCK form previews, not Backend password/registration APIs.

##### Unregistered Workflow adapter and test probes

| Method/path | Source / status |
| --- | --- |
| `POST /api/v1/workflow-instances` | [WorkflowController.create](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/java/com/tricore/dxos/gateway/workflow/controller/WorkflowController.java); unregistered adapter, TEST-ONLY exposure |
| `POST /api/v1/workflow-instances/{instanceId}/activate` | `WorkflowController.activate`; same restriction |
| `POST /api/v1/workflow-instances/{instanceId}/transitions` | `WorkflowController.transition`; same restriction |
| `GET /api/v1/workflow-instances/{instanceId}` | `WorkflowController.get`; same restriction |
| `GET /api/v1/workflow-instances/{instanceId}/history` | `WorkflowController.history`; same restriction |
| `GET /__test_only/gateway/identity-handoff` | Nested probe in [GatewayIdentityHandoffHttpTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/infrastructure/identity/security/GatewayIdentityHandoffHttpTest.java); TEST-ONLY controlled identity handoff |
| `GET /__test_only/gateway/identity-handoff-live` | Nested probe in [GatewayKeycloakTokenHttpIntegrationTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/infrastructure/identity/security/GatewayKeycloakTokenHttpIntegrationTest.java); TEST-ONLY real-token filter test, not a production route |

Do not register generic Workflow routes or test probes to make this reference executable. [WorkflowHttpExposureTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/gateway/workflow/controller/WorkflowHttpExposureTest.java) checks the absent production mappings with a test security setup; a real request can be rejected by authentication before reaching an absent handler.

Both identity probes accept no application parameters/body and return **204 with no body** only after their test `WorkflowGatewayPrincipalGate` requires verified identity plus `workflow:read`. They do not read business resources or authorize tenant/resource access. The first uses controlled authentication; the second is gated on `OIDC_TEST_ACCESS_TOKEN` and the hardcoded `http://localhost:8180/realms/tricore` issuer.

#### 6. Backend API Reference

##### Health

`GET /api/v1/health` has no parameters/body. Success is `200 application/json` with `{"status":"UP"}`. It does not query PostgreSQL or change business state. [HealthControllerTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/common/health/HealthControllerTest.java) asserts the exact body in a MVC slice with a controlled decoder; application startup and persistence are separate claims.

`GET /actuator/health` is the only management endpoint ID exposed over HTTP in configuration; JMX exposure is disabled, and health details/components are hidden. It is not the public controller above. Its aggregate result and concrete HTTP/body variations depend on running infrastructure and were not exercised here; do not infer a fixed `UP` or claim a new verified payload.

##### Shared Helpdesk input/response rules

All nine operations use [HelpdeskService](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/java/com/tricore/dxos/infrastructure/workflow/HelpdeskService.java). `{id}` and optional list `after` are parsed as UUIDs. Write DTOs require a JSON body; use `Content-Type: application/json`. DTOs reject unknown fields, including caller-supplied identity/tenant/role fields. [WorkflowJsonConfiguration](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/java/com/tricore/dxos/gateway/workflow/WorkflowJsonConfiguration.java) also rejects trailing JSON tokens for these inputs. This is not a claim of duplicate-key detection or a global strict-JSON policy for every endpoint.

| Input DTO | Required fields and constraints |
| --- | --- |
| `Create` | `title`: nonblank String, max 200; `description`: nonblank String, max 4000; `requestType`: non-null String matching exactly `IT_HELPDESK` |
| `Version` | `expectedVersion`: non-null, nonnegative Java Long, JSON integer token only |
| `Assign` | `assigneeId`: nonblank String, max 1024, an eligible server-recognized actor ID; `expectedAssignmentVersion`: same strict nonnegative Long rule |
| `Resolve` | `expectedVersion`: strict nonnegative Long; `resolution`: nonblank String, max 4000 |

[WorkflowVersionDeserializer](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/java/com/tricore/dxos/gateway/workflow/dto/WorkflowVersionDeserializer.java) does not coerce strings or decimals into versions. Negative/null values fail validation and values beyond signed Long range fail decoding. The frontend additionally rejects numbers outside JavaScript's safe-integer range; its accepted numeric range is narrower than Java Long. Text is not documented as server-trimmed.

`RequestView` is the response to create, detail and all five action POSTs, and the item type in a list page:

| Field | Wire meaning / nullability |
| --- | --- |
| `id` | Server-generated request UUID string |
| `title`, `description` | Stored request text |
| `requestType` | `IT_HELPDESK` |
| `requesterId` | Server-derived canonical actor ID; not caller-controlled |
| `assigneeId`, `resolution` | Nullable strings; initially null |
| `assignmentVersion` | Nonnegative integer; initially 0, incremented by assignment |
| `workflowInstanceId` | Server-generated Workflow ID, distinct from request UUID |
| `state`, `version` | Current Helpdesk state and Workflow runtime version |
| `allowedActions` | Caller-specific array drawn from `triage`, `assign`, `start`, `resolve`, `confirm`; can be empty. A hint, not an authorization grant |
| `requesterDisplayName`, `assigneeDisplayName` | Detail-only labels from trusted provisioned records. Omitted when null (`@JsonInclude(NON_NULL)`), not an invented fallback label |
| `eligibleAssignees` | Detail-only array of `{id, displayName}`; candidate `displayName` may be null. Included only when the current caller has `assign` in `allowedActions`; omitted otherwise. An empty array is distinct from omission |

Create/action responses and list items omit all three detail-only fields. Detail may include available names independently of the candidate directory. [HelpdeskHttpPostgresTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/infrastructure/workflow/HelpdeskHttpPostgresTest.java), especially `detailProjectsTrustedDisplayNamesAndLimitsCandidateDirectoryToAuthorizedAssign` and `noDirectoryNameMeansNullRatherThanInventedLabel`, asserts these distinctions.

##### Operation contracts

The authorization table in section 4 applies to each operation. Invalid inputs can produce 400/415, missing/invalid authentication 401, and policy failures 403/hidden 404/503 as detailed in section 9. Version/state conflicts apply to writes as described below; the shared error mapper is not proof that every error code is reachable from every operation.

| Method/path | Parameters/body | Success / database or state effect | Specific conditions and evidence |
| --- | --- | --- | --- |
| `POST /api/v1/mvp/requests` | `Create` | **201** + Backend `Location: /api/v1/mvp/requests/{id}` + `RequestView`. Generates request/Workflow IDs, resource/ACL/business records and creates/activates `it-helpdesk@1` in one guarded transaction; `SUBMITTED`, Workflow version 0, assignment version 0 | No caller-selected IDs or idempotency key. Needs all three create authorities and active binding. Creation/activation failure must not leave partial business/Workflow records |
| `GET /api/v1/mvp/requests` | Optional `after` UUID; `limit` default **50**, integer **1–100** | **200** `Page`: `{items: RequestView[], nextCursor: UUID-or-null}`. No business writes | Ordered by request UUID, not creation time. Cursor filters IDs greater than `after`; inaccessible items are excluded. No total count, search, status filter or sort parameter is implemented |
| `GET /api/v1/mvp/requests/{id}` | UUID path; no body | **200** `RequestView`, including authorized detail fields. No business writes | Reads current authoritative resource/member/grant facts. Hidden/missing are indistinguishable 404 |
| `GET /api/v1/mvp/requests/{id}/history` | UUID path; no body | **200** `HistoryView[]`. No business writes; no pagination | Authorizes the request before history lookup. Each entry has only `transitionId`, `sourceState`, `targetState`, `version`, `occurredAt`; no `actorId`, title, note or synthetic event ID |
| `POST /api/v1/mvp/requests/{id}/triage` | `Version` | **200** `RequestView`; `SUBMITTED -> TRIAGED`, Workflow version +1 and one transition history record | Coordinator + transition/read policy; stale version 409; wrong source state 409 |
| `POST /api/v1/mvp/requests/{id}/assign` | `Assign` | **200** `RequestView`; remains `TRIAGED`, assignment version +1; no Workflow version increment/history transition | Coordinator, current assignment version and eligible active same-tenant worker. Stale assignment version/wrong state 409; ineligible assignee 403. Reassignment updates resource grants and can revoke previous worker access |
| `POST /api/v1/mvp/requests/{id}/start` | `Version` | **200** `RequestView`; `TRIAGED -> IN_PROGRESS`, version +1/history append | Current eligible assigned Worker. HTTP action is `start`; recorded transition ID is `start_work` |
| `POST /api/v1/mvp/requests/{id}/resolve` | `Resolve` | **200** `RequestView`; stores resolution and `IN_PROGRESS -> RESOLVED`, version +1/history append atomically | Current eligible assigned Worker; stale version 409 must not retain a resolution or append history |
| `POST /api/v1/mvp/requests/{id}/confirm` | `Version` | **200** `RequestView`; `RESOLVED -> CONFIRMED`, version +1/history append | Eligible original submitter/requester; existing resolution required. Terminal state; no close route |

`HistoryView.occurredAt` is a Java `Instant` without the generic Workflow DTO's explicit string-format annotation. The [frontend decoder](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/frontend/src/services/mvp/http/codecs.ts) accepts string or finite numeric Jackson output. **Exact Helpdesk timestamp wire format is UNVERIFIED here**: no inspected Helpdesk HTTP assertion pins it. No timestamp payload is invented below. Do not assume it matches generic Workflow's explicitly string-formatted history.

Detailed test pointers: `goldenPathUsesAllNineRoutesAndAuthoritativeVersions`, `paginationAndPrototypeIsolation`, `identityFieldsAreRejected`, `invalidVersionsAreRejectedWithoutWrite`, `staleAssignmentAndReassignmentRevokePreviousWorker`, `staleResolutionRollsBackBusinessFactAndHistory`, concurrent-assignment/resolution cases and `unknownCommitIsNotRetriedAndCanBeReconciled` in [HelpdeskHttpPostgresTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/infrastructure/workflow/HelpdeskHttpPostgresTest.java). These are source-confirmed assertions, not new passing results.

##### Generic Workflow DTOs: inspection only, not callable production APIs

The five routes in section 5 have no supported production exposure/authorization contract at this baseline. Tests register a controller explicitly. [WorkflowControllerTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/gateway/workflow/controller/WorkflowControllerTest.java) supplies the reserved server-side `workflow.verifiedActor` request attribute for transitions; client headers, bearer text or body fields cannot substitute for that trusted attribute.

| Test-exposed operation | Inspected input and projection |
| --- | --- |
| Create | [CreateWorkflowInstanceRequest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/java/com/tricore/dxos/gateway/workflow/dto/CreateWorkflowInstanceRequest.java): nonblank `instanceId` matching `[A-Za-z0-9][A-Za-z0-9._:-]*`, nonblank `definitionId`, strict nonnegative Long `definitionVersion`, nonblank `resourceType`/`resourceId`; rejects unknown fields. Test success: 201 + Location + `WorkflowInstanceResponse` |
| Activate | [ActivateWorkflowInstanceRequest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/java/com/tricore/dxos/gateway/workflow/dto/ActivateWorkflowInstanceRequest.java): absent body or empty JSON object; no client state/version. Test success: 200 `WorkflowInstanceResponse` |
| Transition | [ExecuteWorkflowTransitionRequest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/java/com/tricore/dxos/gateway/workflow/dto/ExecuteWorkflowTransitionRequest.java): nonblank `transitionId`, strict nonnegative Long `expectedVersion`; server-supplied actor attribute. Test success: 200 `{instance, record}` |
| Get/history | `instanceId` uses the same path pattern. Test success: 200 instance or history array; no business Helpdesk policy should be inferred from these fixtures |

[WorkflowInstanceResponse](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/java/com/tricore/dxos/gateway/workflow/dto/WorkflowInstanceResponse.java) fields: `instanceId`, `definitionId`, `definitionVersion`, `resourceType`, `resourceId`, `currentState`, `runtimeVersion`, `lifecycle`, `createdAt`, `updatedAt`. [WorkflowHistoryResponse](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/java/com/tricore/dxos/gateway/workflow/dto/WorkflowHistoryResponse.java) fields: `instanceId`, `transitionId`, `sourceState`, `targetState`, `actorId`, `resultingRuntimeVersion`, `occurredAt`. Their Instants explicitly serialize as strings. [WorkflowTransitionResponse](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/java/com/tricore/dxos/gateway/workflow/dto/WorkflowTransitionResponse.java) wraps the two records. These are not Helpdesk response schemas.

In these generic projections, definition/runtime/resulting versions are integers; IDs, resource references and state names are strings. `lifecycle` uses the Core values `NOT_STARTED`, `ACTIVE`, `COMPLETED`. The explicitly formatted timestamps are JSON strings.

#### 7. Portal BFF API Reference

##### Session, login and logout

`GET /bff/session` returns **200**, `Cache-Control: no-store` and either `{"authenticated":false}` or `{"authenticated":true,"csrfToken":"<session-csrf-token>"}`. It does not expose access/refresh tokens or user/role claims. [PortalAuthorization](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/portal-bff/src/main/java/com/tricore/dxos/portal/PortalAuthorization.java) asks the authorized-client manager for a usable unexpired token; failure/missing authorization invalidates the existing session and returns the anonymous projection. This GET can trigger server-side authorization/refresh handling; it is not a database health check.

Login initiation redirects through `GET /oauth2/authorization/keycloak`; [PortalSecurityTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/portal-bff/src/test/java/com/tricore/dxos/portal/PortalSecurityTest.java) asserts a 3xx URL containing `state`, `code_challenge` and `code_challenge_method=S256`. The callback is exactly `${PORTAL_PUBLIC_ORIGIN}/login/oauth2/code/keycloak`; client configuration pins it, requires a secret and rejects the reused `tricore-api` client. Callback query processing, success/failure navigation and provider errors are framework-managed, not a custom JSON DTO; live behavior is **UNVERIFIED** here.

`POST /bff/logout` requires the session CSRF token in `X-CSRF-TOKEN`; missing CSRF is tested as 403. Logout configuration invalidates the HTTP session, deletes `__Host-DXOS-Portal`, invokes the OIDC logout handler and sets the post-logout destination to the public origin plus `/`. Successful provider redirect/revocation is **UNVERIFIED**; there is no implemented JSON logout response contract to invent.

[BFF application.yml](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/portal-bff/src/main/resources/application.yml) configures a 30-minute session timeout and a Secure, HttpOnly, SameSite=Lax cookie named `__Host-DXOS-Portal`, path `/`, with no configured Domain. Actual browser cookie behavior requires HTTPS/browser verification.

##### Allowed forwarding and responses

The nine BFF routes in section 5 use UUID path binding and the same `after`/`limit` page inputs. The `/{id}/{action}` handler admits exactly `triage`, `assign`, `start`, `resolve`, `confirm`; an unsupported action returns empty 404 after applicable security checks. Tests assert an unrelated path is unmapped and PUT on the collection is 405 in a controller fixture. Do not generalize those fixture results into a promise that every unauthenticated unknown route reaches routing before security.

The BFF reads at most **32,768 bytes** for a write, sends those bytes as `application/json` to the fixed Backend origin and leaves Helpdesk DTO/business validation to Backend. It does not derive a target URL from browser input. List forwarding constructs only `limit` and optional `after`; it is not an unrestricted query/header tunnel.

- Only the server-held token becomes upstream `Authorization: Bearer`; `Accept: application/json` is supplied, and writes get JSON content type. Browser cookies, arbitrary identity headers and browser bearer credentials are not forwarded.
- Backend origin must be HTTPS or literal `http://127.0.0.1` with no credentials/query/fragment/path beyond `/`. The public origin is pinned HTTPS without a path/trailing slash; [PortalOrigin](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/portal-bff/src/main/java/com/tricore/dxos/portal/PortalOrigin.java) and `PortalSecurity` check it.
- The HTTP client refuses redirects, uses a 5-second connect timeout and a 15-second request timeout. Read responses are bounded to **2,000,000 bytes**; bodies are closed.
- Accepted upstream statuses/bodies are relayed as JSON with `Cache-Control: no-store`. Upstream **401** instead invalidates the BFF session and becomes an empty 401. Backend 403/404/409 preserve their status/body and do not invalidate the session in the tested client behavior.
- Arbitrary upstream response headers are not forwarded: specifically, the Backend create **Location header is not propagated** by this implementation. Use the returned request `id` for subsequent reads.

Local BFF failures and error-body differences are listed in section 9. Even an empty 502 after a POST does not prove the Backend rolled back. The BFF makes one attempt and never automatically retries a write.

The [same-origin frontend transport](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/frontend/src/services/mvp/http/sameOriginTransport.ts) permits local HTTPS only, prefixes approved Backend-style paths with `/bff`, uses same-origin cookies, rejects redirects and keeps CSRF in memory. Its route/query restrictions are frontend controls, not a substitute for Backend authorization. [HelpdeskApiClient](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/frontend/src/services/mvp/http/HelpdeskApiClient.ts) expects create 201 and other successes 200, validates response projections, invalidates its instance on 401 and treats an unreadable successful write response as potentially committed.

#### 8. Helpdesk Workflow and State Model

The application pins [it-helpdesk@1](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/resources/db/helpdesk/definition.sql); it is a business definition consumed by generic Workflow mechanisms, not a hardcoded Core business API.

| HTTP operation | Actor policy | State change | Workflow version/history | Assignment version |
| --- | --- | --- | --- | --- |
| Create | Eligible submitter | Creates/activates `SUBMITTED` | Starts at 0; activation adds no transition entry | Starts at 0 |
| Triage | Coordinator | `SUBMITTED -> TRIAGED` | +1 / append `triage` | Unchanged |
| Assign/reassign | Coordinator | `TRIAGED -> TRIAGED` | Unchanged / no transition entry | +1 on each successful assignment |
| Start | Eligible current Worker | `TRIAGED -> IN_PROGRESS` | +1 / append `start_work` | Unchanged |
| Resolve | Eligible current Worker | `IN_PROGRESS -> RESOLVED` | +1 / append `resolve` | Unchanged |
| Confirm | Eligible original requester | `RESOLVED -> CONFIRMED` | +1 / append `confirm`; terminal | Unchanged |

Each successful transition requires the current `expectedVersion`; assignment requires current `expectedAssignmentVersion`. They are independent counters, not ETags. Do not send `expectedVersion` to assignment or use assignment version for transitions. The Golden Path ends at Workflow version 4 with four transition entries; there is no `CLOSED` state, `/close`, public activation endpoint for Helpdesk or arbitrary-transition endpoint.

[HelpdeskService](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/java/com/tricore/dxos/infrastructure/workflow/HelpdeskService.java) rechecks caller/resource/business facts under the tenant guard in the transaction owned by [PostgresWorkflowPersistence](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/java/com/tricore/dxos/infrastructure/workflow/PostgresWorkflowPersistence.java). Business updates, Workflow state and transition history commit together. Rejected/stale writes must not leave partial changes. The read projection's `allowedActions` can become stale; server authorization/version checks remain decisive.

No idempotency key is implemented in these DTOs; unknown fields are rejected. Even repeated assignment to the same actor can increment assignment version. After a lost response, reconcile detail/history before any user-controlled recovery; do not blindly recreate a request or replay an action.

#### 9. Error Handling

##### Backend envelope and policy

[ApiError](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/java/com/tricore/dxos/common/error/ApiError.java) is `{status: integer, code: string, message: string, errors: object<string,string>}`. It does not define timestamp/path/request-ID fields. [ApiAuthenticationEntryPoint](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/java/com/tricore/dxos/infrastructure/identity/security/ApiAuthenticationEntryPoint.java) returns 401 JSON with `WWW-Authenticate: Bearer`, code `AUTHENTICATION_REQUIRED` and message `Authentication is required` for missing/invalid bearer authentication.

[HelpdeskExceptionHandler](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/java/com/tricore/dxos/gateway/helpdesk/HelpdeskExceptionHandler.java) inherits [WorkflowExceptionHandler](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/java/com/tricore/dxos/gateway/workflow/controller/WorkflowExceptionHandler.java), with a Helpdesk-only anti-enumeration override:

| HTTP | Code | Source-confirmed meaning / scope |
| --- | --- | --- |
| 400 | `VALIDATION_FAILED` | DTO constraint failure, method validation or invalid bound parameter; field errors where supplied by the validation exception |
| 400 | `INVALID_BODY` | Malformed/unaccepted JSON, unknown fields, invalid strict version decoding or trailing JSON tokens |
| 401 | `AUTHENTICATION_REQUIRED` | Security entry point for missing/invalid token; generic test adapter also maps a missing reserved actor attribute to this code with a different message |
| 403 | `FORBIDDEN` | Visible resource/operation denied or business eligibility/technical authority denied |
| 404 | `NOT_FOUND` | Helpdesk hidden/missing resource, including missing definition/instance; message `Workflow resource not found`, empty `errors` |
| 409 | `VERSION_CONFLICT`, `TRANSITION_NOT_ALLOWED`, `INSTANCE_COMPLETED`, `INSTANCE_ALREADY_EXISTS` | Shared mapper for version/state/duplicate errors; fixed Helpdesk routes do not expose every generic operation |
| 415 | `UNSUPPORTED_MEDIA_TYPE` | Shared MVC input handler; message still says `Workflow input requires application/json` |
| 422 | `INVALID_TRANSITION` | Shared mapper for unknown generic transition IDs. Helpdesk callers cannot supply an arbitrary transition ID through its five fixed action routes |
| 500 | `OPERATION_FAILURE`, `INTERNAL_ERROR` | Normalized operation failure or unexpected handler exception; not a raw SQL/provider response |
| 503 | `AUTHORIZATION_UNAVAILABLE` | Cannot establish authoritative authorization/guarded facts; distinct from an unknown commit |
| 503 | `COMMIT_OUTCOME_UNKNOWN` | Write may already have committed; reconcile authoritative detail/history, **do not automatically retry** |

Generic Workflow test exposure retains distinct `DEFINITION_NOT_FOUND` / `INSTANCE_NOT_FOUND` 404 codes. Helpdesk deliberately makes them indistinguishable from hidden ACL resources. [HelpdeskErrorContractTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/gateway/helpdesk/HelpdeskErrorContractTest.java) asserts the distinction and unknown-commit mapping; its mocked GET failure does not prove a real write occurred.

These envelopes apply to the named entry point/advice scope, not every framework routing, management or security-filter failure. Do not assume all 404/405 or all BFF errors contain `ApiError`.

##### BFF-generated errors

| HTTP/body | Trigger / forwarding behavior |
| --- | --- |
| 400, empty body | Handler rejects `limit` outside 1–100 or fails reading the incoming write body; UUID/type binding is framework-managed |
| 401, empty body | No usable server token or upstream 401; session invalidated where applicable |
| 403, framework security response | CSRF/denied-route failures can occur before forwarding; no custom `ApiError` schema is pinned here |
| 404, empty body | Unsupported action after security; unrelated unmapped routes are also tested in a standalone MVC fixture |
| 405, framework response | Unsupported HTTP method in the tested MVC mapping |
| 413, empty body | Write exceeds 32,768 bytes; not forwarded |
| 502, empty body | Upstream redirect/unaccepted status or response exceeds 2,000,000 bytes; not proof of rollback for a write |
| 503, `{"code":"UPSTREAM_UNAVAILABLE"}` | I/O/interruption while forwarding a read |
| 503, `{"code":"COMMIT_OUTCOME_UNKNOWN"}` | I/O/interruption while forwarding a write, including an upstream response-read failure; no retry |

Otherwise the BFF relays bounded Backend JSON bytes/status, so a relayed Backend 503 may have the full `ApiError` shape while a BFF-generated 503 has only `code`. Inspect status and available code without assuming a uniform error schema. Read unavailability and unknown write outcome require different handling.

#### 10. Request/Response Examples

These are source-shaped JSON examples with invented text/UUIDs and explicit placeholders. They are not evidence of execution and are not credentials. Replace actor/version placeholders only with authorized server-returned values; do not submit examples against shared data.

##### Create through the BFF

`POST /bff/api/v1/mvp/requests`, with an existing session and its `X-CSRF-TOKEN` header. Backend direct callers use the corresponding private route and their authorized bearer context instead.

```json
{
  "title": "QA disposable request",
  "description": "Synthetic request for an isolated review environment.",
  "requestType": "IT_HELPDESK"
}
```

Illustrative **201** `RequestView` for a submitter without Coordinator actions; generated IDs below are placeholders. The Backend adds Location; this BFF does not relay that header.

```json
{
  "id": "00000000-0000-4000-8000-000000000001",
  "title": "QA disposable request",
  "description": "Synthetic request for an isolated review environment.",
  "requestType": "IT_HELPDESK",
  "requesterId": "<server-derived-canonical-actor-id>",
  "assigneeId": null,
  "resolution": null,
  "assignmentVersion": 0,
  "workflowInstanceId": "<server-generated-workflow-id>",
  "state": "SUBMITTED",
  "version": 0,
  "allowedActions": []
}
```

The base fields are from `RequestView`, initial counters from [schema.sql](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/main/resources/db/helpdesk/schema.sql) / Workflow activation, and state/action expectations from the Golden Path test. Detail names/candidates are deliberately absent from this create response.

##### Action bodies

For a Coordinator triaging the initial request, `POST .../{id}/triage`:

```json
{"expectedVersion": 0}
```

For a Coordinator assigning a currently triaged request, `POST .../{id}/assign`:

```json
{
  "assigneeId": "<id-from-authorized-detail-eligibleAssignees>",
  "expectedAssignmentVersion": 0
}
```

In the Golden Path, Start uses `{"expectedVersion":1}`. Resolve then uses:

```json
{"expectedVersion": 2, "resolution": "Synthetic issue resolved and checked."}
```

Confirm uses `{"expectedVersion":3}`. These numbers illustrate that exact sequence; use current server versions after other actions or concurrent activity. Each action success returns the complete `RequestView`, not a bare status or Workflow transition DTO.

##### Empty page and errors

Source-shaped terminal empty list page:

```json
{"items": [], "nextCursor": null}
```

Helpdesk hidden/missing response, **404**:

```json
{"status": 404, "code": "NOT_FOUND", "message": "Workflow resource not found", "errors": {}}
```

BFF-generated uncertain write response, **503**:

```json
{"code": "COMMIT_OUTCOME_UNKNOWN"}
```

The Backend form of the same code additionally includes `status`, its reconciliation message and `errors`. Session examples are in section 7. No history timestamp example or provider callback response is supplied because their exact runtime behavior remains unverified in the scope described above.

#### 11. API Security Considerations

- Treat verified JWT identity, technical authority, active tenant/resource grants and current business eligibility as separate checks. Neither a BFF session nor resource ownership bypasses the Backend policy.
- Do not send tenant, requester, actor or role claims in Helpdesk bodies; unknown fields are rejected. Assign an eligible server-recognized actor ID, not a display name or browser role.
- Keep Backend private. The supplied HTTPS ingress strips untrusted forwarding headers, pins forwarded host/protocol, enforces SNI/Host agreement and rejects `/api/*`; actual deployment/trust still needs review.
- Keep OAuth secrets/tokens server-side; CSRF stays in browser memory. Preserve HTTPS, Secure/HttpOnly cookie configuration and CSRF. Do not log/share authorization headers, cookies, CSRF values, passwords, private keys or real identity data.
- Honor the two version counters and re-read caller-specific `allowedActions`; reject stale actions rather than overriding concurrency checks. Missing/hidden resources intentionally share a response.
- There is no automatic write replay or idempotency key. Network interruption, malformed success, unknown commit and a BFF 502 after a POST do not authorize retry. Reconcile authorized detail/history without inventing a new write.

#### 12. API Testing and Verification

Use the canonical [TESTING.md](TESTING.md) for commands, environment guards and evidence requirements; this file does not run those commands or provision fixtures.

| Contract | Inspected evidence | Limit |
| --- | --- | --- |
| Health body/public access | [HealthControllerTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/common/health/HealthControllerTest.java) | MockMvc/controller slice, not connected application health |
| Missing/invalid JWT, exact role mapping, header forgery | [SecurityConfigTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/infrastructure/identity/security/SecurityConfigTest.java), [SpringSecurityCurrentPrincipalTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/infrastructure/identity/security/SpringSecurityCurrentPrincipalTest.java), identity handoff probes | Controlled decoder/filter tests; optional real-token probe needs its exact issuer/token |
| Helpdesk payloads, roles/ACL, lifecycle, conflicts, atomicity | [HelpdeskHttpPostgresTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/infrastructure/workflow/HelpdeskHttpPostgresTest.java) | Opt-in disposable PostgreSQL; most identity data is synthetic. B06 separately requires real tokens and still is not BFF/browser E2E |
| Helpdesk hidden/missing and unknown-commit error contract | [HelpdeskErrorContractTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/gateway/helpdesk/HelpdeskErrorContractTest.java) | Mocked service mapping; separate DB cases model commit uncertainty |
| Generic adapter DTO/errors and absent runtime registration | [WorkflowControllerTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/gateway/workflow/controller/WorkflowControllerTest.java), [WorkflowHttpExposureTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/gateway/workflow/controller/WorkflowHttpExposureTest.java) | Explicit test registration does not open production routes |
| BFF PKCE/session/CSRF and forwarding | [PortalSecurityTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/portal-bff/src/test/java/com/tricore/dxos/portal/PortalSecurityTest.java), [PortalBackendClientTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/portal-bff/src/test/java/com/tricore/dxos/portal/PortalBackendClientTest.java) | Synthetic OAuth session/manager, mocked HTTP client; not a real Keycloak callback, refresh or logout |
| Frontend wire decoding and local composition | [HelpdeskApiClient.test.ts](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/frontend/src/services/mvp/http/HelpdeskApiClient.test.ts), [sameOriginTransport.test.ts](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/frontend/src/services/mvp/http/sameOriginTransport.test.ts), [LocalHelpdeskIntegration.test.tsx](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/frontend/src/features/helpdesk/LocalHelpdeskIntegration.test.tsx) | Fake transport/fetch; MOCK/fake browser suites are not LIVE API proof |

[CI](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/.github/workflows/ci.yml) explicitly verifies execution/no skips for three identity/exposure suites, but does not provision the complete PostgreSQL/Keycloak/BFF browser environment. A green job is not proof of every guarded API behavior. No new counts/PASS results are claimed. LIVE acceptance needs exact SHA/environment, actual authenticated requests, negative cases, versions/history, restart persistence, fresh reports and sanitized evidence as described in TESTING/BFF runbooks.

#### 13. Known Limitations

| Status | Limit |
| --- | --- |
| IMPLEMENTED / SOURCE-CONFIRMED | The documented controller, DTO, policy and handler code exists; this does not establish a running service |
| GUARDED | Helpdesk opt-in and disposable-loopback/runtime-login restrictions remain in place; configuration/build alone does not prove authenticated operation |
| TEST-ONLY | Generic Workflow HTTP exposure and two identity probes exist only in test registration; they are not public service contracts |
| PROPOSED / absent runtime API | Architecture targets, candidate OpenAPI tooling, Facility, uploads/object storage, Flowable and APISIX must not be presented as completed endpoints |
| UNVERIFIED | Fresh startup, exact Helpdesk history timestamp serialization, Actuator result, real BFF callback/refresh/logout/cookie behavior and same-SHA LIVE E2E were not executed here |
| Documentation dependency | Use DEVELOPMENT/TESTING from the publication branch. `docs/contracts/` is absent at the source baseline; no substitute specification is implied |

Unsupported capabilities include the removed Request prototype, a Helpdesk `/close` action, arbitrary generic proxying, caller-selected tenant/identity fields and a Helpdesk idempotency-key field. Framework routing/security errors do not share one guaranteed JSON schema. Historical reports and architecture proposals do not lift these restrictions.

#### 14. References

- [README](../README.md), [CONTRIBUTING](../CONTRIBUTING.md), [SECURITY](../SECURITY.md).
- Canonical guides: [DEVELOPMENT](DEVELOPMENT.md), [TESTING](TESTING.md); verify publication-branch availability.
- [Backend runbook](../backend/README.md), [BFF runbook](../portal-bff/README.md), [Helpdesk local runbook](../scripts/README-helpdesk-local.md).
- [R31 Helpdesk API crosswalk](verification/r31/r31-helpdesk-api-crosswalk.md), [Core/Application design](01-architecture/core-application-boundary.md), [Gateway design](02-core/gateway/gateway-architecture.md). Each has its own baseline/status; current source remains decisive.
- Phase 2 snapshots pinned at `5938d8e7cb117aa6bc8226ace1d786be2f7be703`: [Block A](https://github.com/tricore-opentrix/opentrix/blob/5938d8e7cb117aa6bc8226ace1d786be2f7be703/docs/09-evidence/phase-2/block-a-architecture.md), [Block B](https://github.com/tricore-opentrix/opentrix/blob/5938d8e7cb117aa6bc8226ace1d786be2f7be703/docs/09-evidence/phase-2/block-b-backend-infra.md), [Block C](https://github.com/tricore-opentrix/opentrix/blob/5938d8e7cb117aa6bc8226ace1d786be2f7be703/docs/09-evidence/phase-2/block-c-application.md). These report-only changes do not supply new runtime acceptance for this draft.

### B. Target — PROPOSED, not yet accepted

- **PROPOSED · [#112](https://github.com/tricore-opentrix/opentrix/issues/112):** publish a reviewed runtime-exported OpenAPI/Swagger reference for nine guarded Helpdesk routes; **not yet an accepted OpenAPI contract**.
- **PROPOSED · [#118](https://github.com/tricore-opentrix/opentrix/issues/118):** verify the real Keycloak–BFF–Backend–PostgreSQL browser golden path and its negative cases.
- **PROPOSED · [#194](https://github.com/tricore-opentrix/opentrix/issues/194):** keep navigation, relative links, source revisions and evidence in sync.

**Publication gate:** Link validation, matched source SHA, real test outputs, SPDX/REUSE check and independent review are required; none is claimed PASS by this document edit.
