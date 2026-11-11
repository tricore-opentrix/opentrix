<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# API Reference / Tham chiếu API

> **Owner:** @ngang02012007-crypto · **Issue:** [#194](https://github.com/tricore-opentrix/opentrix/issues/194) · **Priority:** P0 · **Status:** DRAFT FOR REVIEW; NOT LIVE-ACCEPTED

**Mốc nguồn mã / Source baseline:** [`832c75fc3164cf170eed3bb8f1e380d24dd65aba`](https://github.com/tricore-opentrix/opentrix/commit/832c75fc3164cf170eed3bb8f1e380d24dd65aba). Đây là bản đối chiếu tài liệu, **không** phải kết quả kiểm thử mới. Chỉ gắn `VERIFIED` khi có kết quả chạy ở SHA, môi trường và log cụ thể.

## Tiếng Việt

### A. Hiện trạng — bằng chứng từ mã nguồn và Giai đoạn 2

**Phạm vi:** Tài liệu này mô tả hợp đồng HTTP Backend, Portal BFF, xác thực, phân quyền, trạng thái Helpdesk và kiểm chứng có thể suy ra từ mã nguồn. Đây không phải tài liệu Swagger/OpenAPI xuất từ runtime. Tham chiếu [Khối C Giai đoạn 2](09-evidence/phase-2/block-c-application.md), [R31 crosswalk](verification/r31/r31-helpdesk-api-crosswalk.md), [Khối A](09-evidence/phase-2/block-a-architecture.md) và [Khối B](09-evidence/phase-2/block-b-backend-infra.md).

| Thành phần | Hiện trạng có nguồn | Giới hạn bằng chứng |
| --- | --- | --- |
| Backend Helpdesk | [HelpdeskController](../backend/src/main/java/com/tricore/dxos/gateway/helpdesk/HelpdeskController.java) khai báo **9 tuyến** `/api/v1/mvp/requests` (4 tuyến tạo/đọc, 5 tuyến hành động) | Chỉ đăng ký khi `dxos.helpdesk.enabled=true`; không suy ra endpoint đang chạy |
| Portal BFF | [PortalBackendClient](../portal-bff/src/main/java/com/tricore/dxos/portal/PortalBackendClient.java) có ánh xạ 9 tuyến qua `/bff/api/v1/mvp/requests`; phiên OAuth/PKCE và CSRF từ [PortalSecurity](../portal-bff/src/main/java/com/tricore/dxos/portal/PortalSecurity.java) | Không chứng minh đăng nhập Keycloak và trình duyệt LIVE |
| Workflow | `it-helpdesk@1`: `SUBMITTED → TRIAGED → IN_PROGRESS → RESOLVED → CONFIRMED`; có Assign tại TRIAGED | Assign tăng **assignmentVersion**, không tăng Workflow version; không có tuyến `/close` |
| Phân quyền | Backend kiểm token, authority, membership, tenant, ACL tài nguyên và vai trò nghiệp vụ | Không tin vai trò từ MOCK, header tùy ý hay `allowedActions` trên UI |
| OpenAPI | [R31 crosswalk](verification/r31/r31-helpdesk-api-crosswalk.md) đối chiếu source và assertions; [#112](https://github.com/tricore-opentrix/opentrix/issues/112) chưa đạt acceptance | **OpenAPI/Swagger runtime chưa được xác minh và chưa công bố chính thức** |
| Kiểm thử | Có mã kiểm thử HTTP/PostgreSQL, BFF, frontend; [báo cáo Khối C](09-evidence/phase-2/block-c-application.md) | Không có xác nhận E2E cùng SHA; từng trường hợp PostgreSQL có thể skip |

#### Hợp đồng Helpdesk: 9 tuyến

| Phương thức | Đường dẫn Backend (sau `/api/v1/mvp/requests`) | Chính sách/đầu vào chính |
| --- | --- | --- |
| POST | *(collection)* | Requester, `title`, `description`, `requestType=IT_HELPDESK` → `201` |
| GET | *(collection)* | Danh sách giới hạn theo quyền, `after`, `limit` (1–100) |
| GET | `/{id}` | Chi tiết bản ghi có quyền đọc; hidden/missing trả scoped 404 |
| GET | `/{id}/history` | Lịch sử chuyển trạng thái sau kiểm quyền đọc |
| POST | `/{id}/triage` | Coordinator, `expectedVersion` |
| POST | `/{id}/assign` | Coordinator, `assigneeId`, `expectedAssignmentVersion` |
| POST | `/{id}/start` | Worker đang được giao, `expectedVersion` |
| POST | `/{id}/resolve` | Worker đang được giao, `expectedVersion`, `resolution` |
| POST | `/{id}/confirm` | Requester ban đầu, `expectedVersion` |

Đường dẫn tương ứng ở trình duyệt chỉ được gọi qua BFF cùng HTTPS origin và phiên hợp lệ. **MOCK** không gọi Backend thật. `integration-local` có mã vận chuyển qua BFF, nhưng build hoặc test giả lập không phải bằng chứng LIVE. Xem [tài liệu tích hợp](INTEGRATION.md) và [hướng dẫn kiểm thử](TESTING.md).

#### Trạng thái, phiên bản và lỗi

Luồng chuẩn: Create (`SUBMITTED`, Workflow version 0) → Triage (1) → Assign (assignmentVersion +1, Workflow vẫn 1) → Start (2) → Resolve (3) → Confirm (`CONFIRMED`, Workflow 4). Chỉ có bốn history transition: `triage`, `start_work`, `resolve`, `confirm`. `allowedActions` chỉ là gợi ý UI, không cấp quyền thực tế. [Định nghĩa](../backend/src/main/resources/db/helpdesk/definition.sql) · [HelpdeskService](../backend/src/main/java/com/tricore/dxos/infrastructure/workflow/HelpdeskService.java).

Xác thực thiếu/không hợp lệ: 401; tài nguyên nhìn thấy nhưng thiếu quyền: 403; tài nguyên bị ẩn hoặc thiếu: scoped 404; version/state xung đột: 409; outcome ghi không rõ có thể là `COMMIT_OUTCOME_UNKNOWN` 503. **Không tự gửi lại POST** nếu response bị mất, hãy hòa giải bằng các GET hợp lệ. BFF có thể trả dạng lỗi ngắn hơn Backend. Chi tiết mã lỗi và DTO ở phần tiếng Anh bên dưới, được giữ để tra cứu trường-level.

**Môi trường:** MOCK Vite thường ở `127.0.0.1:5173`; local Backend/BFF/Caddy yêu cầu cấu hình riêng. Không có URL production được xác minh. Tài liệu này không ghi nhận bài kiểm thử mới hoặc payload LIVE thu được; JSON minh họa là dữ liệu tổng hợp.

### B. Mục tiêu — PROPOSED, chưa nghiệm thu

- **PROPOSED · [#112](https://github.com/tricore-opentrix/opentrix/issues/112):** xuất bản OpenAPI/Swagger từ runtime, đối chiếu đủ 9 tuyến, schema, security, lỗi và kiểm thử loopback rồi review độc lập. **Chưa có OpenAPI chính thức theo acceptance #112.**
- **PROPOSED · [#118](https://github.com/tricore-opentrix/opentrix/issues/118):** bằng chứng trình duyệt thực với Keycloak → Portal BFF → Backend → PostgreSQL, ba danh tính, trường hợp âm tính và lịch sử đủ sáu bước.
- **PROPOSED · [#194](https://github.com/tricore-opentrix/opentrix/issues/194):** liên kết chuẩn từ `docs/README.md`, đối chiếu tài liệu với HEAD PR và giữ các giới hạn bằng chứng.
- **PROPOSED · [#166](https://github.com/tricore-opentrix/opentrix/issues/166):** chỉ đưa hợp đồng R29 vào runtime sau quyết định hợp lệ; [PR #145](https://github.com/tricore-opentrix/opentrix/pull/145) đã đóng và chưa merge.

**Điều kiện công bố:** nguồn code, runtime export và test log phải cùng mốc SHA hoặc giải thích chênh lệch; không dùng file thiết kế hay CI cũ để khẳng định tính năng đã nghiệm thu.

## English

### A. Current state — source and Phase 2 evidence

**Scope:** The detailed sections below preserve the source-inspected contract and test boundaries. This documentation update performs no runtime execution. Compare with [Phase 2 Block C](09-evidence/phase-2/block-c-application.md).

#### 1. Overview

This draft describes application-owned routes and explicitly configured framework endpoints at **`832c75fc3164cf170eed3bb8f1e380d24dd65aba`**, the local HEAD inspected. The initial working tree had no tracked changes, but contained local documentation drafts and other pre-existing untracked artifacts. Those artifacts are not treated as baseline implementation. Only this file is created by this task.

Evidence levels: **SOURCE-CONFIRMED** means inspected implementation or test assertions; **VERIFIED** requires a successful check at an identified SHA/environment with retained results; **UNVERIFIED** means execution/acceptance is not established. No application tests, servers, database operations or LIVE E2E were run for this document. Examples are synthetic illustrations, not captured responses.

Availability labels are separate from evidence: **IMPLEMENTED** = registered code/configuration exists; **GUARDED** = explicit opt-in/runtime restrictions apply; **TEST-ONLY** = exposure exists in test configuration only; **PROPOSED** = design, not an implemented route. None implies a deployed or accepted service.

[DEVELOPMENT.md](DEVELOPMENT.md) and [TESTING.md](TESTING.md) are local drafts, absent from `main` at the audited baseline. Before publication, ensure both relative links resolve on the intended branch/PR. No GitHub publication is performed here.

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
| `http://127.0.0.1:8081` | BFF port selected in its runbook and targeted by [Caddyfile.local](../portal-bff/Caddyfile.local) | Private loopback upstream; Secure cookies require browser access through HTTPS |
| `https://localhost:8443` | Supplied Caddy public origin; BFF/OIDC paths and built frontend | Requires configured stack and browser-trusted local CA. `/api/*` is rejected with 404 by ingress |
| `http://127.0.0.1:5173` | Default MOCK Vite development URL in [README](../README.md) | UI demonstration, not Backend/BFF base URL |
| `http://127.0.0.1:4173` | [Playwright preview](../frontend/playwright.config.ts) | MOCK browser fixture, not LIVE API deployment |
| `http://localhost:8180/realms/tricore` | Older template/test issuer; real-token tests hardcode it | Exact issuer identity; not interchangeable with `127.0.0.1` or another port |
| `http://127.0.0.1:8182/realms/tricore` | Separate disposable browser scenario in the BFF runbook | Historical setup instructions, not confirmation of current provider availability |

Use the exact discovery issuer configured for the selected environment. Backend `OIDC_ISSUER_URI`, audience and resource client ID come from [application.yml](../backend/src/main/resources/application.yml); BFF provider/client/origin settings come from [its application.yml](../portal-bff/src/main/resources/application.yml). There is no production base URL or deployment acceptance established here. Do not reuse retained database resources, credentials or issuer/sub mappings merely because a runbook names them.

#### 4. Authentication and Authorization

##### Backend

[SecurityConfig](../backend/src/main/java/com/tricore/dxos/infrastructure/identity/security/SecurityConfig.java) permits `/api/v1/health` without authentication; all other requests require authentication. The Backend is stateless, disables CSRF for its bearer boundary and does not use browser session cookies as identity.

JWT verification includes signature/provider keys, exact configured issuer, audience, timestamp checks, an access-token `typ` claim equal to `Bearer`, required expiration and a nonblank, well-formed string subject. See [AccessTokenTypeValidator](../backend/src/main/java/com/tricore/dxos/infrastructure/identity/security/AccessTokenTypeValidator.java), [SubjectValidator](../backend/src/main/java/com/tricore/dxos/infrastructure/identity/security/SubjectValidator.java) and [ExpirationValidator](../backend/src/main/java/com/tricore/dxos/infrastructure/identity/security/ExpirationValidator.java). A public health path does not make an invalid bearer token trusted.

[SpringSecurityCurrentPrincipal](../backend/src/main/java/com/tricore/dxos/infrastructure/identity/security/SpringSecurityCurrentPrincipal.java) derives the canonical actor ID as `oidc:base64url(UTF8(iss)).base64url(UTF8(sub))`, without padding. It reads only supported exact authority names from `resource_access.<configured-resource-client-id>.roles`: `workflow:create`, `workflow:activate`, `workflow:read`, `workflow:transition`. Realm roles, client headers or fabricated principal fields do not grant these authorities.

| Operation | Required exact authorities | Additional authoritative business policy |
| --- | --- | --- |
| Create Helpdesk request | `workflow:create`, `workflow:activate`, `workflow:read` | Active configured-tenant membership, `submitter` actor fact, active `mvp_request -> it-helpdesk@1` binding |
| List/detail/history | `workflow:read` | Active tenant/member/resource and readable resource ACL; list only returns visible/readable items |
| Triage/Assign | `workflow:transition` **and** `workflow:read` | Coordinator actor fact, explicit resource grants; assignment also requires `TRIAGED` and an eligible active worker in the same tenant |
| Start/Resolve | `workflow:transition` **and** `workflow:read` | Current assignee with active worker eligibility and applicable resource grants |
| Confirm | `workflow:transition` **and** `workflow:read` | Original requester still has submitter eligibility; resolution exists and state/version permit confirmation |

The tenant is server configuration, not a request field. Employee/Coordinator/Worker are application role descriptions backed by database actor facts; they are not automatic JWT roles or mutually exclusive roles. No administrator bypass is implemented by these rules.

[WorkflowAuthorization](../backend/src/main/java/com/tricore/dxos/application/authorization/WorkflowAuthorization.java) and [TenantResourceWorkflowAccessPolicy](../backend/src/main/java/com/tricore/dxos/application/authorization/TenantResourceWorkflowAccessPolicy.java) enforce visibility before an instance-operation authority denial: inactive/missing resource/member or no visibility produces hidden 404; a visible resource without the requested grant/authority can produce 403. Ownership alone never substitutes for explicit operation grants. Creation/list have their own preliminary checks; do not assume every denial has the same precedence.

##### BFF

The BFF requires a confidential Authorization Code client using `client_secret_basic`, adds PKCE S256, pins the HTTPS callback and keeps OAuth tokens server-side. Backend verifies the forwarded token independently. Browser writes use the BFF session cookie plus `X-CSRF-TOKEN`; a demo persona, browser actor ID or BFF route allowlist cannot grant Backend resource access.

#### 5. API Endpoint Inventory

##### Registered health and guarded Helpdesk

Health owners: [HealthController](../backend/src/main/java/com/tricore/dxos/common/health/HealthController.java), [management configuration](../backend/src/main/resources/application.yml) and [security configuration](../backend/src/main/java/com/tricore/dxos/infrastructure/identity/security/SecurityConfig.java).

| Method/path | Owner | Authentication | Availability |
| --- | --- | --- | --- |
| `GET /api/v1/health` | `HealthController.health` | Public when no bearer is supplied | IMPLEMENTED |
| `GET /actuator/health` | Spring Boot Actuator | Authenticated under the custom security chain | IMPLEMENTED exposure configuration; exact runtime health result UNVERIFIED |

Every pair below is source-confirmed in [HelpdeskController](../backend/src/main/java/com/tricore/dxos/gateway/helpdesk/HelpdeskController.java) and [PortalBackendClient](../portal-bff/src/main/java/com/tricore/dxos/portal/PortalBackendClient.java). Backend routes are **GUARDED**, disabled unless `dxos.helpdesk.enabled=true`; [HelpdeskConfiguration](../backend/src/main/java/com/tricore/dxos/infrastructure/workflow/HelpdeskConfiguration.java) additionally requires a `127.0.0.1` disposable database, `helpdesk_runtime_*` login and `server.address=127.0.0.1`. BFF mappings are **IMPLEMENTED** in a separately configured BFF; they do not enable the Backend guard.

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
| `GET /bff/session` | [PortalSessionController](../portal-bff/src/main/java/com/tricore/dxos/portal/PortalSessionController.java): usable session/CSRF projection | Public session check; IMPLEMENTED |
| `GET /oauth2/authorization/keycloak` | [PortalSecurity](../portal-bff/src/main/java/com/tricore/dxos/portal/PortalSecurity.java) authorization resolver: initiate provider login | No existing login required; IMPLEMENTED framework handler |
| `GET /login/oauth2/code/keycloak` | Spring OAuth2 login filter; exact callback pinned by `PortalSecurity` and client configuration | Provider callback with framework-validated login transaction; IMPLEMENTED configuration, live callback UNVERIFIED |
| `POST /bff/logout` | `PortalSecurity` logout filter / OIDC logout success handler | Session and CSRF required; IMPLEMENTED configuration, live provider logout UNVERIFIED |

These are the configured application/authentication contracts, not an inventory of every Spring internal/default error or navigation handler. Frontend `/login` and `/register` pages are MOCK form previews, not Backend password/registration APIs.

##### Unregistered Workflow adapter and test probes

| Method/path | Source / status |
| --- | --- |
| `POST /api/v1/workflow-instances` | [WorkflowController.create](../backend/src/main/java/com/tricore/dxos/gateway/workflow/controller/WorkflowController.java); unregistered adapter, TEST-ONLY exposure |
| `POST /api/v1/workflow-instances/{instanceId}/activate` | `WorkflowController.activate`; same restriction |
| `POST /api/v1/workflow-instances/{instanceId}/transitions` | `WorkflowController.transition`; same restriction |
| `GET /api/v1/workflow-instances/{instanceId}` | `WorkflowController.get`; same restriction |
| `GET /api/v1/workflow-instances/{instanceId}/history` | `WorkflowController.history`; same restriction |
| `GET /__test_only/gateway/identity-handoff` | Nested probe in [GatewayIdentityHandoffHttpTest](../backend/src/test/java/com/tricore/dxos/infrastructure/identity/security/GatewayIdentityHandoffHttpTest.java); TEST-ONLY controlled identity handoff |
| `GET /__test_only/gateway/identity-handoff-live` | Nested probe in [GatewayKeycloakTokenHttpIntegrationTest](../backend/src/test/java/com/tricore/dxos/infrastructure/identity/security/GatewayKeycloakTokenHttpIntegrationTest.java); TEST-ONLY real-token filter test, not a production route |

Do not register generic Workflow routes or test probes to make this reference executable. [WorkflowHttpExposureTest](../backend/src/test/java/com/tricore/dxos/gateway/workflow/controller/WorkflowHttpExposureTest.java) checks the absent production mappings with a test security setup; a real request can be rejected by authentication before reaching an absent handler.

Both identity probes accept no application parameters/body and return **204 with no body** only after their test `WorkflowGatewayPrincipalGate` requires verified identity plus `workflow:read`. They do not read business resources or authorize tenant/resource access. The first uses controlled authentication; the second is gated on `OIDC_TEST_ACCESS_TOKEN` and the hardcoded `http://localhost:8180/realms/tricore` issuer.

#### 6. Backend API Reference

##### Health

`GET /api/v1/health` has no parameters/body. Success is `200 application/json` with `{"status":"UP"}`. It does not query PostgreSQL or change business state. [HealthControllerTest](../backend/src/test/java/com/tricore/dxos/common/health/HealthControllerTest.java) asserts the exact body in a MVC slice with a controlled decoder; application startup and persistence are separate claims.

`GET /actuator/health` is the only management endpoint ID exposed over HTTP in configuration; JMX exposure is disabled, and health details/components are hidden. It is not the public controller above. Its aggregate result and concrete HTTP/body variations depend on running infrastructure and were not exercised here; do not infer a fixed `UP` or claim a new verified payload.

##### Shared Helpdesk input/response rules

All nine operations use [HelpdeskService](../backend/src/main/java/com/tricore/dxos/infrastructure/workflow/HelpdeskService.java). `{id}` and optional list `after` are parsed as UUIDs. Write DTOs require a JSON body; use `Content-Type: application/json`. DTOs reject unknown fields, including caller-supplied identity/tenant/role fields. [WorkflowJsonConfiguration](../backend/src/main/java/com/tricore/dxos/gateway/workflow/WorkflowJsonConfiguration.java) also rejects trailing JSON tokens for these inputs. This is not a claim of duplicate-key detection or a global strict-JSON policy for every endpoint.

| Input DTO | Required fields and constraints |
| --- | --- |
| `Create` | `title`: nonblank String, max 200; `description`: nonblank String, max 4000; `requestType`: non-null String matching exactly `IT_HELPDESK` |
| `Version` | `expectedVersion`: non-null, nonnegative Java Long, JSON integer token only |
| `Assign` | `assigneeId`: nonblank String, max 1024, an eligible server-recognized actor ID; `expectedAssignmentVersion`: same strict nonnegative Long rule |
| `Resolve` | `expectedVersion`: strict nonnegative Long; `resolution`: nonblank String, max 4000 |

[WorkflowVersionDeserializer](../backend/src/main/java/com/tricore/dxos/gateway/workflow/dto/WorkflowVersionDeserializer.java) does not coerce strings or decimals into versions. Negative/null values fail validation and values beyond signed Long range fail decoding. The frontend additionally rejects numbers outside JavaScript's safe-integer range; its accepted numeric range is narrower than Java Long. Text is not documented as server-trimmed.

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

Create/action responses and list items omit all three detail-only fields. Detail may include available names independently of the candidate directory. [HelpdeskHttpPostgresTest](../backend/src/test/java/com/tricore/dxos/infrastructure/workflow/HelpdeskHttpPostgresTest.java), especially `detailProjectsTrustedDisplayNamesAndLimitsCandidateDirectoryToAuthorizedAssign` and `noDirectoryNameMeansNullRatherThanInventedLabel`, asserts these distinctions.

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

`HistoryView.occurredAt` is a Java `Instant` without the generic Workflow DTO's explicit string-format annotation. The [frontend decoder](../frontend/src/services/mvp/http/codecs.ts) accepts string or finite numeric Jackson output. **Exact Helpdesk timestamp wire format is UNVERIFIED here**: no inspected Helpdesk HTTP assertion pins it. No timestamp payload is invented below. Do not assume it matches generic Workflow's explicitly string-formatted history.

Detailed test pointers: `goldenPathUsesAllNineRoutesAndAuthoritativeVersions`, `paginationAndPrototypeIsolation`, `identityFieldsAreRejected`, `invalidVersionsAreRejectedWithoutWrite`, `staleAssignmentAndReassignmentRevokePreviousWorker`, `staleResolutionRollsBackBusinessFactAndHistory`, concurrent-assignment/resolution cases and `unknownCommitIsNotRetriedAndCanBeReconciled` in [HelpdeskHttpPostgresTest](../backend/src/test/java/com/tricore/dxos/infrastructure/workflow/HelpdeskHttpPostgresTest.java). These are source-confirmed assertions, not new passing results.

##### Generic Workflow DTOs: inspection only, not callable production APIs

The five routes in section 5 have no supported production exposure/authorization contract at this baseline. Tests register a controller explicitly. [WorkflowControllerTest](../backend/src/test/java/com/tricore/dxos/gateway/workflow/controller/WorkflowControllerTest.java) supplies the reserved server-side `workflow.verifiedActor` request attribute for transitions; client headers, bearer text or body fields cannot substitute for that trusted attribute.

| Test-exposed operation | Inspected input and projection |
| --- | --- |
| Create | [CreateWorkflowInstanceRequest](../backend/src/main/java/com/tricore/dxos/gateway/workflow/dto/CreateWorkflowInstanceRequest.java): nonblank `instanceId` matching `[A-Za-z0-9][A-Za-z0-9._:-]*`, nonblank `definitionId`, strict nonnegative Long `definitionVersion`, nonblank `resourceType`/`resourceId`; rejects unknown fields. Test success: 201 + Location + `WorkflowInstanceResponse` |
| Activate | [ActivateWorkflowInstanceRequest](../backend/src/main/java/com/tricore/dxos/gateway/workflow/dto/ActivateWorkflowInstanceRequest.java): absent body or empty JSON object; no client state/version. Test success: 200 `WorkflowInstanceResponse` |
| Transition | [ExecuteWorkflowTransitionRequest](../backend/src/main/java/com/tricore/dxos/gateway/workflow/dto/ExecuteWorkflowTransitionRequest.java): nonblank `transitionId`, strict nonnegative Long `expectedVersion`; server-supplied actor attribute. Test success: 200 `{instance, record}` |
| Get/history | `instanceId` uses the same path pattern. Test success: 200 instance or history array; no business Helpdesk policy should be inferred from these fixtures |

[WorkflowInstanceResponse](../backend/src/main/java/com/tricore/dxos/gateway/workflow/dto/WorkflowInstanceResponse.java) fields: `instanceId`, `definitionId`, `definitionVersion`, `resourceType`, `resourceId`, `currentState`, `runtimeVersion`, `lifecycle`, `createdAt`, `updatedAt`. [WorkflowHistoryResponse](../backend/src/main/java/com/tricore/dxos/gateway/workflow/dto/WorkflowHistoryResponse.java) fields: `instanceId`, `transitionId`, `sourceState`, `targetState`, `actorId`, `resultingRuntimeVersion`, `occurredAt`. Their Instants explicitly serialize as strings. [WorkflowTransitionResponse](../backend/src/main/java/com/tricore/dxos/gateway/workflow/dto/WorkflowTransitionResponse.java) wraps the two records. These are not Helpdesk response schemas.

In these generic projections, definition/runtime/resulting versions are integers; IDs, resource references and state names are strings. `lifecycle` uses the Core values `NOT_STARTED`, `ACTIVE`, `COMPLETED`. The explicitly formatted timestamps are JSON strings.

#### 7. Portal BFF API Reference

##### Session, login and logout

`GET /bff/session` returns **200**, `Cache-Control: no-store` and either `{"authenticated":false}` or `{"authenticated":true,"csrfToken":"<session-csrf-token>"}`. It does not expose access/refresh tokens or user/role claims. [PortalAuthorization](../portal-bff/src/main/java/com/tricore/dxos/portal/PortalAuthorization.java) asks the authorized-client manager for a usable unexpired token; failure/missing authorization invalidates the existing session and returns the anonymous projection. This GET can trigger server-side authorization/refresh handling; it is not a database health check.

Login initiation redirects through `GET /oauth2/authorization/keycloak`; [PortalSecurityTest](../portal-bff/src/test/java/com/tricore/dxos/portal/PortalSecurityTest.java) asserts a 3xx URL containing `state`, `code_challenge` and `code_challenge_method=S256`. The callback is exactly `${PORTAL_PUBLIC_ORIGIN}/login/oauth2/code/keycloak`; client configuration pins it, requires a secret and rejects the reused `tricore-api` client. Callback query processing, success/failure navigation and provider errors are framework-managed, not a custom JSON DTO; live behavior is **UNVERIFIED** here.

`POST /bff/logout` requires the session CSRF token in `X-CSRF-TOKEN`; missing CSRF is tested as 403. Logout configuration invalidates the HTTP session, deletes `__Host-DXOS-Portal`, invokes the OIDC logout handler and sets the post-logout destination to the public origin plus `/`. Successful provider redirect/revocation is **UNVERIFIED**; there is no implemented JSON logout response contract to invent.

[BFF application.yml](../portal-bff/src/main/resources/application.yml) configures a 30-minute session timeout and a Secure, HttpOnly, SameSite=Lax cookie named `__Host-DXOS-Portal`, path `/`, with no configured Domain. Actual browser cookie behavior requires HTTPS/browser verification.

##### Allowed forwarding and responses

The nine BFF routes in section 5 use UUID path binding and the same `after`/`limit` page inputs. The `/{id}/{action}` handler admits exactly `triage`, `assign`, `start`, `resolve`, `confirm`; an unsupported action returns empty 404 after applicable security checks. Tests assert an unrelated path is unmapped and PUT on the collection is 405 in a controller fixture. Do not generalize those fixture results into a promise that every unauthenticated unknown route reaches routing before security.

The BFF reads at most **32,768 bytes** for a write, sends those bytes as `application/json` to the fixed Backend origin and leaves Helpdesk DTO/business validation to Backend. It does not derive a target URL from browser input. List forwarding constructs only `limit` and optional `after`; it is not an unrestricted query/header tunnel.

- Only the server-held token becomes upstream `Authorization: Bearer`; `Accept: application/json` is supplied, and writes get JSON content type. Browser cookies, arbitrary identity headers and browser bearer credentials are not forwarded.
- Backend origin must be HTTPS or literal `http://127.0.0.1` with no credentials/query/fragment/path beyond `/`. The public origin is pinned HTTPS without a path/trailing slash; [PortalOrigin](../portal-bff/src/main/java/com/tricore/dxos/portal/PortalOrigin.java) and `PortalSecurity` check it.
- The HTTP client refuses redirects, uses a 5-second connect timeout and a 15-second request timeout. Read responses are bounded to **2,000,000 bytes**; bodies are closed.
- Accepted upstream statuses/bodies are relayed as JSON with `Cache-Control: no-store`. Upstream **401** instead invalidates the BFF session and becomes an empty 401. Backend 403/404/409 preserve their status/body and do not invalidate the session in the tested client behavior.
- Arbitrary upstream response headers are not forwarded: specifically, the Backend create **Location header is not propagated** by this implementation. Use the returned request `id` for subsequent reads.

Local BFF failures and error-body differences are listed in section 9. Even an empty 502 after a POST does not prove the Backend rolled back. The BFF makes one attempt and never automatically retries a write.

The [same-origin frontend transport](../frontend/src/services/mvp/http/sameOriginTransport.ts) permits local HTTPS only, prefixes approved Backend-style paths with `/bff`, uses same-origin cookies, rejects redirects and keeps CSRF in memory. Its route/query restrictions are frontend controls, not a substitute for Backend authorization. [HelpdeskApiClient](../frontend/src/services/mvp/http/HelpdeskApiClient.ts) expects create 201 and other successes 200, validates response projections, invalidates its instance on 401 and treats an unreadable successful write response as potentially committed.

#### 8. Helpdesk Workflow and State Model

The application pins [it-helpdesk@1](../backend/src/main/resources/db/helpdesk/definition.sql); it is a business definition consumed by generic Workflow mechanisms, not a hardcoded Core business API.

| HTTP operation | Actor policy | State change | Workflow version/history | Assignment version |
| --- | --- | --- | --- | --- |
| Create | Eligible submitter | Creates/activates `SUBMITTED` | Starts at 0; activation adds no transition entry | Starts at 0 |
| Triage | Coordinator | `SUBMITTED -> TRIAGED` | +1 / append `triage` | Unchanged |
| Assign/reassign | Coordinator | `TRIAGED -> TRIAGED` | Unchanged / no transition entry | +1 on each successful assignment |
| Start | Eligible current Worker | `TRIAGED -> IN_PROGRESS` | +1 / append `start_work` | Unchanged |
| Resolve | Eligible current Worker | `IN_PROGRESS -> RESOLVED` | +1 / append `resolve` | Unchanged |
| Confirm | Eligible original requester | `RESOLVED -> CONFIRMED` | +1 / append `confirm`; terminal | Unchanged |

Each successful transition requires the current `expectedVersion`; assignment requires current `expectedAssignmentVersion`. They are independent counters, not ETags. Do not send `expectedVersion` to assignment or use assignment version for transitions. The Golden Path ends at Workflow version 4 with four transition entries; there is no `CLOSED` state, `/close`, public activation endpoint for Helpdesk or arbitrary-transition endpoint.

[HelpdeskService](../backend/src/main/java/com/tricore/dxos/infrastructure/workflow/HelpdeskService.java) rechecks caller/resource/business facts under the tenant guard in the transaction owned by [PostgresWorkflowPersistence](../backend/src/main/java/com/tricore/dxos/infrastructure/workflow/PostgresWorkflowPersistence.java). Business updates, Workflow state and transition history commit together. Rejected/stale writes must not leave partial changes. The read projection's `allowedActions` can become stale; server authorization/version checks remain decisive.

No idempotency key is implemented in these DTOs; unknown fields are rejected. Even repeated assignment to the same actor can increment assignment version. After a lost response, reconcile detail/history before any user-controlled recovery; do not blindly recreate a request or replay an action.

#### 9. Error Handling

##### Backend envelope and policy

[ApiError](../backend/src/main/java/com/tricore/dxos/common/error/ApiError.java) is `{status: integer, code: string, message: string, errors: object<string,string>}`. It does not define timestamp/path/request-ID fields. [ApiAuthenticationEntryPoint](../backend/src/main/java/com/tricore/dxos/infrastructure/identity/security/ApiAuthenticationEntryPoint.java) returns 401 JSON with `WWW-Authenticate: Bearer`, code `AUTHENTICATION_REQUIRED` and message `Authentication is required` for missing/invalid bearer authentication.

[HelpdeskExceptionHandler](../backend/src/main/java/com/tricore/dxos/gateway/helpdesk/HelpdeskExceptionHandler.java) inherits [WorkflowExceptionHandler](../backend/src/main/java/com/tricore/dxos/gateway/workflow/controller/WorkflowExceptionHandler.java), with a Helpdesk-only anti-enumeration override:

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

Generic Workflow test exposure retains distinct `DEFINITION_NOT_FOUND` / `INSTANCE_NOT_FOUND` 404 codes. Helpdesk deliberately makes them indistinguishable from hidden ACL resources. [HelpdeskErrorContractTest](../backend/src/test/java/com/tricore/dxos/gateway/helpdesk/HelpdeskErrorContractTest.java) asserts the distinction and unknown-commit mapping; its mocked GET failure does not prove a real write occurred.

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

The base fields are from `RequestView`, initial counters from [schema.sql](../backend/src/main/resources/db/helpdesk/schema.sql) / Workflow activation, and state/action expectations from the Golden Path test. Detail names/candidates are deliberately absent from this create response.

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

Use the local draft [TESTING.md](TESTING.md) for commands, environment guards and evidence requirements; this file does not run those commands or provision fixtures.

| Contract | Inspected evidence | Limit |
| --- | --- | --- |
| Health body/public access | [HealthControllerTest](../backend/src/test/java/com/tricore/dxos/common/health/HealthControllerTest.java) | MockMvc/controller slice, not connected application health |
| Missing/invalid JWT, exact role mapping, header forgery | [SecurityConfigTest](../backend/src/test/java/com/tricore/dxos/infrastructure/identity/security/SecurityConfigTest.java), [SpringSecurityCurrentPrincipalTest](../backend/src/test/java/com/tricore/dxos/infrastructure/identity/security/SpringSecurityCurrentPrincipalTest.java), identity handoff probes | Controlled decoder/filter tests; optional real-token probe needs its exact issuer/token |
| Helpdesk payloads, roles/ACL, lifecycle, conflicts, atomicity | [HelpdeskHttpPostgresTest](../backend/src/test/java/com/tricore/dxos/infrastructure/workflow/HelpdeskHttpPostgresTest.java) | Opt-in disposable PostgreSQL; most identity data is synthetic. B06 separately requires real tokens and still is not BFF/browser E2E |
| Helpdesk hidden/missing and unknown-commit error contract | [HelpdeskErrorContractTest](../backend/src/test/java/com/tricore/dxos/gateway/helpdesk/HelpdeskErrorContractTest.java) | Mocked service mapping; separate DB cases model commit uncertainty |
| Generic adapter DTO/errors and absent runtime registration | [WorkflowControllerTest](../backend/src/test/java/com/tricore/dxos/gateway/workflow/controller/WorkflowControllerTest.java), [WorkflowHttpExposureTest](../backend/src/test/java/com/tricore/dxos/gateway/workflow/controller/WorkflowHttpExposureTest.java) | Explicit test registration does not open production routes |
| BFF PKCE/session/CSRF and forwarding | [PortalSecurityTest](../portal-bff/src/test/java/com/tricore/dxos/portal/PortalSecurityTest.java), [PortalBackendClientTest](../portal-bff/src/test/java/com/tricore/dxos/portal/PortalBackendClientTest.java) | Synthetic OAuth session/manager, mocked HTTP client; not a real Keycloak callback, refresh or logout |
| Frontend wire decoding and local composition | [HelpdeskApiClient.test.ts](../frontend/src/services/mvp/http/HelpdeskApiClient.test.ts), [sameOriginTransport.test.ts](../frontend/src/services/mvp/http/sameOriginTransport.test.ts), [LocalHelpdeskIntegration.test.tsx](../frontend/src/features/helpdesk/LocalHelpdeskIntegration.test.tsx) | Fake transport/fetch; MOCK/fake browser suites are not LIVE API proof |

[CI](../.github/workflows/ci.yml) explicitly verifies execution/no skips for three identity/exposure suites, but does not provision the complete PostgreSQL/Keycloak/BFF browser environment. A green job is not proof of every guarded API behavior. No new counts/PASS results are claimed. LIVE acceptance needs exact SHA/environment, actual authenticated requests, negative cases, versions/history, restart persistence, fresh reports and sanitized evidence as described in TESTING/BFF runbooks.

#### 13. Known Limitations

| Status | Limit |
| --- | --- |
| IMPLEMENTED / SOURCE-CONFIRMED | The documented controller, DTO, policy and handler code exists; this does not establish a running service |
| GUARDED | Helpdesk opt-in and disposable-loopback/runtime-login restrictions remain in place; configuration/build alone does not prove authenticated operation |
| TEST-ONLY | Generic Workflow HTTP exposure and two identity probes exist only in test registration; they are not public service contracts |
| PROPOSED / absent runtime API | Architecture targets, candidate OpenAPI tooling, Facility, uploads/object storage, Flowable and APISIX must not be presented as completed endpoints |
| UNVERIFIED | Fresh startup, exact Helpdesk history timestamp serialization, Actuator result, real BFF callback/refresh/logout/cookie behavior and same-SHA LIVE E2E were not executed here |
| Documentation dependency | DEVELOPMENT/TESTING are local drafts. `docs/contracts/` does not exist in this checkout; no replacement source/spec was fabricated |

Unsupported capabilities include the removed Request prototype, a Helpdesk `/close` action, arbitrary generic proxying, caller-selected tenant/identity fields and a Helpdesk idempotency-key field. Framework routing/security errors do not share one guaranteed JSON schema. Historical reports and architecture proposals do not lift these restrictions.

#### 14. References

- [README](../README.md), [CONTRIBUTING](../CONTRIBUTING.md), [SECURITY](../SECURITY.md).
- Local drafts: [DEVELOPMENT](DEVELOPMENT.md), [TESTING](TESTING.md); verify publication-branch availability before publishing this file.
- [Backend runbook](../backend/README.md), [BFF runbook](../portal-bff/README.md), [Helpdesk local runbook](../scripts/README-helpdesk-local.md).
- [R31 Helpdesk API crosswalk](verification/r31/r31-helpdesk-api-crosswalk.md), [Core/Application design](01-architecture/core-application-boundary.md), [Gateway design](02-core/gateway/gateway-architecture.md). Each has its own baseline/status; current source remains decisive.
- Phase 2 snapshots pinned at `5938d8e7cb117aa6bc8226ace1d786be2f7be703`: [Block A](https://github.com/tricore-opentrix/opentrix/blob/5938d8e7cb117aa6bc8226ace1d786be2f7be703/docs/09-evidence/phase-2/block-a-architecture.md), [Block B](https://github.com/tricore-opentrix/opentrix/blob/5938d8e7cb117aa6bc8226ace1d786be2f7be703/docs/09-evidence/phase-2/block-b-backend-infra.md), [Block C](https://github.com/tricore-opentrix/opentrix/blob/5938d8e7cb117aa6bc8226ace1d786be2f7be703/docs/09-evidence/phase-2/block-c-application.md). These report-only changes do not supply new runtime acceptance for this draft.

### B. Target — PROPOSED, not yet accepted

- **PROPOSED · [#112](https://github.com/tricore-opentrix/opentrix/issues/112):** publish a reviewed runtime-exported OpenAPI/Swagger reference for nine guarded Helpdesk routes; **not yet an accepted OpenAPI contract**.
- **PROPOSED · [#118](https://github.com/tricore-opentrix/opentrix/issues/118):** verify the real Keycloak–BFF–Backend–PostgreSQL browser golden path and its negative cases.
- **PROPOSED · [#194](https://github.com/tricore-opentrix/opentrix/issues/194):** keep navigation, relative links, source revisions and evidence in sync.

**Publication gate:** Link validation, matched source SHA, real test outputs, SPDX/REUSE check and independent review are required; none is claimed PASS by this document edit.
