<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors

SPDX-License-Identifier: Apache-2.0
-->

# Backend

## Overview

The backend is a Spring Boot modular monolith (base package `com.tricore.dxos`). It provides the
Identity, Workflow and Data cores, and the IT Helpdesk application (`it-helpdesk@1`) built on them.
The cores provide mechanisms; the application owns business meaning.

| Package | Responsibility |
| --- | --- |
| `core.identity` | Authenticated principal, authorities and authorization decisions |
| `core.workflow` | Workflow definitions, instances, transitions and the persistence port |
| `core.data` | Object storage port |
| `application` | Workflow authorization policy and the Helpdesk use-case interface |
| `gateway` | HTTP adapters for the Helpdesk API |
| `infrastructure` | JWT validation, the PostgreSQL Workflow adapter and the Helpdesk service |
| `common` | Health endpoint and the shared error body |

Each core package depends only on the Java standard library (excluding JDBC) and on itself.
Architecture tests ([`CoreDependencyRulesTest`](https://github.com/tricore-opentrix/opentrix/blob/main/backend/src/test/java/com/tricore/dxos/architecture/CoreDependencyRulesTest.java))
enforce this rule. See [ARCHITECTURE.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/ARCHITECTURE.md)
and [dependency-rules.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/01-architecture/dependency-rules.md).

## Requirements

- JDK 21.
- PostgreSQL 17 to run the application or the integration tests.
- An OpenID Connect issuer (Keycloak realm `tricore` in the local deployment).
- Docker, for the local deployment and the local verification script.

The Gradle Wrapper (Gradle 8.14.3) is included. Commands below run from `backend/`.

## Endpoints

| Method and path | Access | Purpose |
| --- | --- | --- |
| `GET /api/v1/health` | Public | Returns `{"status":"UP"}`. Does not query the database. |
| `GET /actuator/health` | Bearer token | Aggregate health, without details or components |
| `POST /api/v1/mvp/requests` | Bearer token | Create a request: `title` (≤ 200), `description` (≤ 4000), `requestType: "IT_HELPDESK"` |
| `GET /api/v1/mvp/requests` | Bearer token | List visible requests; cursor `after`, `limit` 1–100 (default 50) |
| `GET /api/v1/mvp/requests/{id}` | Bearer token | Read one request |
| `GET /api/v1/mvp/requests/{id}/history` | Bearer token | Read Workflow transition history |
| `POST /api/v1/mvp/requests/{id}/triage` | Coordinator | `SUBMITTED → TRIAGED`, with `expectedVersion` |
| `POST /api/v1/mvp/requests/{id}/assign` | Coordinator | Set the assignee while `TRIAGED`, with `assigneeId` and `expectedAssignmentVersion` |
| `POST /api/v1/mvp/requests/{id}/start` | Assigned worker | `TRIAGED → IN_PROGRESS`, with `expectedVersion` |
| `POST /api/v1/mvp/requests/{id}/resolve` | Assigned worker | `IN_PROGRESS → RESOLVED`, with `expectedVersion` and `resolution` (≤ 4000) |
| `POST /api/v1/mvp/requests/{id}/confirm` | Requester (submitter) | `RESOLVED → CONFIRMED`, with `expectedVersion` |

The `/api/v1/mvp/requests` routes are registered only when `dxos.helpdesk.enabled=true`.
`CONFIRMED` is the final state. Assignment is not a Workflow state; it increments a separate
`assignment_version`. Request bodies reject unknown fields. The full contract is in
[API.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/API.md).

The Workflow HTTP adapter (`/api/v1/workflow-instances`) is not registered as a Spring controller.
It is tested independently and is not reachable in a running application.

## Security behavior

- **Stateless resource server.** Every route except `/api/v1/health` requires a bearer JWT. No HTTP
  session is created.
- **Token validation.** Issuer, signature, timestamps, audience (`OIDC_AUDIENCE`), access-token type
  and a string `sub` claim are checked.
- **Authorities.** Authorities are read from `resource_access.<OIDC_RESOURCE_CLIENT_ID>.roles`.
- **Helpdesk authorization.** Every call checks the verified identity, tenant membership, the
  per-request access list and the actor's role (submitter, coordinator or worker) before any change
  is committed. Actor roles are provisioned in the database, not taken from the request.
- **Optimistic concurrency.** A stale `expectedVersion` or `expectedAssignmentVersion` is rejected
  with a version conflict.
- **Durable writes.** A write reports success only after PostgreSQL confirms the `COMMIT`. If the
  outcome of a `COMMIT` is unknown, the backend reports it and does not retry.
- **Actuator.** Only the `health` endpoint is exposed over HTTP; JMX exposure is disabled.

## Configuration

| Variable | Required | Description |
| --- | --- | --- |
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | Yes, unless `SPRING_DATASOURCE_*` is set | Main datasource (`jdbc:postgresql://DB_HOST:DB_PORT/DB_NAME`). There are no default credentials. |
| `DXOS_WORKFLOW_SCHEMA` | Yes | Workflow schema: lowercase `[a-z][a-z0-9_]{0,62}`, not `public` or a system schema |
| `SPRING_FLYWAY_ENABLED` | No | Set to `false` when the schema is provisioned separately (as in the local deployment) |
| `OIDC_ISSUER_URI` | Yes | Issuer, for example `http://localhost:8180/realms/tricore` |
| `OIDC_AUDIENCE` | Yes | Required token audience, for example `tricore-api` |
| `OIDC_RESOURCE_CLIENT_ID` | Yes | Client whose roles are read as authorities, for example `tricore-api` |
| `DXOS_HELPDESK_ENABLED` | No | `true` registers the Helpdesk API |
| `DXOS_HELPDESK_JDBCURL`, `DXOS_HELPDESK_USERNAME`, `DXOS_HELPDESK_PASSWORD` | With Helpdesk | Helpdesk database connection |
| `DXOS_HELPDESK_SCHEMA`, `DXOS_HELPDESK_TENANT` | With Helpdesk | Helpdesk schema and tenant |
| `SERVER_ADDRESS`, `SERVER_PORT` | No | Bind address and port (default port `8080`) |

The Helpdesk API refuses to start unless all of the following hold: `SERVER_ADDRESS` is `127.0.0.1`,
the JDBC URL is `jdbc:postgresql://127.0.0.1:<port>/helpdesk_disposable_<name>`, and the login is
`helpdesk_runtime_<name>`. It is intended for a local, disposable database only.

Spring Boot does not read `.env` files. Do not commit credentials.

## Run locally

The simplest way to run the backend with PostgreSQL, Keycloak, the Portal BFF and the Portal is the
local deployment in [infra/demo](https://github.com/tricore-opentrix/opentrix/blob/main/infra/demo/README.md).
It builds the backend from source, provisions the Helpdesk schema and sets every variable above.

To build and run the backend on its own:

```powershell
.\gradlew.bat build          # Windows
./gradlew build              # Linux and macOS
java -jar build/libs/dxos-backend-0.1.0.jar
```

The application needs the variables from [Configuration](#configuration) at startup.

A source archive from a release does not include `gradle-wrapper.jar`. In that case, install
Gradle 8.14.3 and run `gradle -p backend build` from the archive root. See
[RELEASE.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/RELEASE.md).

## Database migrations

| Location | Content |
| --- | --- |
| `src/main/resources/db/migration/V1`, `V2` | Earlier request tables. Kept so that `flyway validate` passes on existing databases; no code uses them. |
| `src/main/resources/db/migration/V3` | Workflow definitions, instances and transition history |
| `src/main/resources/db/migration/V4` | Seed definitions `document-review@1` and `incident-resolution@1` |
| `src/main/resources/db/helpdesk/` | Helpdesk tables, the `it-helpdesk@1` definition and runtime grants, applied outside Flyway |

Definitions are immutable once committed; a change needs a new version. Flyway is restricted to the
configured schema and has `clean` and baseline-on-migrate disabled. The runtime login should not own the
schema and should have only the grants in
[runtime-grants.sql](https://github.com/tricore-opentrix/opentrix/blob/main/backend/src/main/resources/db/helpdesk/runtime-grants.sql).

## Tests

| Command | What it runs | Needs |
| --- | --- | --- |
| `./gradlew test` | Unit, MVC, security and architecture tests. PostgreSQL tests are skipped. | JDK 21 |
| `./gradlew workflowIntegrationTest` | Workflow persistence and isolation suites against PostgreSQL | `WORKFLOW_TEST_JDBC_URL`, `WORKFLOW_TEST_DB_USER`, `WORKFLOW_TEST_DB_PASSWORD` (loopback only) |
| `powershell -File ..\scripts\workflow-verify-local.ps1` | Starts a disposable PostgreSQL 17.11 container with TLS, runs `test build` with every integration suite, then removes the container | Docker, JDK 21, Windows |

The integration fixtures refuse non-loopback database URLs. Do not run them against a shared database.

The `workflowSmoke`, `workflowSchemaBootstrap`, `workflowApprovedMigration` and related Gradle tasks
are operator tools for a hosted PostgreSQL. They write to a real database only with explicit approval
variables. See [scripts/README.md](https://github.com/tricore-opentrix/opentrix/blob/main/scripts/README.md)
before using them.

## Limitations

- The Helpdesk API runs only against a local, disposable database (see [Configuration](#configuration)).
- The Workflow HTTP adapter is not registered.
- `core.data` defines the storage port; no production storage adapter is included.
- The backend is not packaged as a container image or a published JAR.

---

## Tổng quan

Backend là một modular monolith viết bằng Spring Boot (package gốc `com.tricore.dxos`). Backend cung
cấp các core Identity, Workflow và Data, cùng ứng dụng IT Helpdesk (`it-helpdesk@1`) xây dựng trên các
core đó. Core cung cấp cơ chế; ứng dụng sở hữu ngữ nghĩa nghiệp vụ.

| Package | Trách nhiệm |
| --- | --- |
| `core.identity` | Principal đã xác thực, authority và quyết định phân quyền |
| `core.workflow` | Định nghĩa, instance, transition của Workflow và cổng lưu trữ |
| `core.data` | Cổng lưu trữ đối tượng |
| `application` | Chính sách phân quyền Workflow và giao diện use case Helpdesk |
| `gateway` | Adapter HTTP cho Helpdesk API |
| `infrastructure` | Kiểm tra JWT, adapter Workflow cho PostgreSQL và dịch vụ Helpdesk |
| `common` | Endpoint health và cấu trúc lỗi dùng chung |

Mỗi package core chỉ phụ thuộc vào thư viện chuẩn Java (trừ JDBC) và chính nó. Quy tắc này được kiểm
tra bằng test kiến trúc ([`CoreDependencyRulesTest`](https://github.com/tricore-opentrix/opentrix/blob/main/backend/src/test/java/com/tricore/dxos/architecture/CoreDependencyRulesTest.java)).
Xem [ARCHITECTURE.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/ARCHITECTURE.md)
và [dependency-rules.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/01-architecture/dependency-rules.md).

## Yêu cầu

- JDK 21.
- PostgreSQL 17 để chạy ứng dụng hoặc integration test.
- Một OpenID Connect issuer (realm Keycloak `tricore` trong bản triển khai cục bộ).
- Docker, cho bản triển khai cục bộ và script kiểm tra cục bộ.

Repository có sẵn Gradle Wrapper (Gradle 8.14.3). Các lệnh bên dưới chạy từ thư mục `backend/`.

## Endpoint

| Phương thức và đường dẫn | Truy cập | Mục đích |
| --- | --- | --- |
| `GET /api/v1/health` | Công khai | Trả `{"status":"UP"}`. Không truy vấn database. |
| `GET /actuator/health` | Bearer token | Health tổng hợp, không hiển thị chi tiết hay thành phần |
| `POST /api/v1/mvp/requests` | Bearer token | Tạo yêu cầu: `title` (≤ 200), `description` (≤ 4000), `requestType: "IT_HELPDESK"` |
| `GET /api/v1/mvp/requests` | Bearer token | Liệt kê yêu cầu được phép xem; con trỏ `after`, `limit` 1–100 (mặc định 50) |
| `GET /api/v1/mvp/requests/{id}` | Bearer token | Đọc một yêu cầu |
| `GET /api/v1/mvp/requests/{id}/history` | Bearer token | Đọc lịch sử chuyển trạng thái Workflow |
| `POST /api/v1/mvp/requests/{id}/triage` | Điều phối viên | `SUBMITTED → TRIAGED`, kèm `expectedVersion` |
| `POST /api/v1/mvp/requests/{id}/assign` | Điều phối viên | Gán người xử lý khi đang `TRIAGED`, kèm `assigneeId` và `expectedAssignmentVersion` |
| `POST /api/v1/mvp/requests/{id}/start` | Người xử lý được gán | `TRIAGED → IN_PROGRESS`, kèm `expectedVersion` |
| `POST /api/v1/mvp/requests/{id}/resolve` | Người xử lý được gán | `IN_PROGRESS → RESOLVED`, kèm `expectedVersion` và `resolution` (≤ 4000) |
| `POST /api/v1/mvp/requests/{id}/confirm` | Người gửi yêu cầu | `RESOLVED → CONFIRMED`, kèm `expectedVersion` |

Các route `/api/v1/mvp/requests` chỉ được đăng ký khi `dxos.helpdesk.enabled=true`.
`CONFIRMED` là trạng thái cuối. Việc gán người xử lý không phải một trạng thái Workflow; thao tác này
tăng một giá trị riêng là `assignment_version`. Body của request từ chối trường không xác định. Hợp đồng
đầy đủ có trong [API.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/API.md).

Adapter HTTP của Workflow (`/api/v1/workflow-instances`) không được đăng ký làm Spring controller.
Adapter này được kiểm thử độc lập và không thể truy cập trong ứng dụng đang chạy.

## Hành vi bảo mật

- **Resource server không trạng thái.** Mọi route, trừ `/api/v1/health`, yêu cầu bearer JWT. Không
  tạo HTTP session.
- **Kiểm tra token.** Kiểm tra issuer, chữ ký, thời gian, audience (`OIDC_AUDIENCE`), loại access
  token và claim `sub` dạng chuỗi.
- **Authority.** Authority được đọc từ `resource_access.<OIDC_RESOURCE_CLIENT_ID>.roles`.
- **Phân quyền Helpdesk.** Mỗi lời gọi kiểm tra danh tính đã xác minh, tư cách thành viên tenant,
  danh sách quyền của từng yêu cầu và vai trò của người thực hiện (người gửi, điều phối viên hoặc
  người xử lý) trước khi commit bất kỳ thay đổi nào. Vai trò được cấp sẵn trong database, không lấy
  từ request.
- **Kiểm soát đồng thời lạc quan.** `expectedVersion` hoặc `expectedAssignmentVersion` đã cũ bị từ
  chối với lỗi xung đột phiên bản.
- **Ghi bền vững.** Thao tác ghi chỉ báo thành công sau khi PostgreSQL xác nhận `COMMIT`. Nếu không
  xác định được kết quả `COMMIT`, backend báo lại và không thử lại.
- **Actuator.** Chỉ endpoint `health` được mở qua HTTP; JMX bị tắt.

## Cấu hình

| Biến | Bắt buộc | Mô tả |
| --- | --- | --- |
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | Có, trừ khi đặt `SPRING_DATASOURCE_*` | Datasource chính (`jdbc:postgresql://DB_HOST:DB_PORT/DB_NAME`). Không có credentials mặc định. |
| `DXOS_WORKFLOW_SCHEMA` | Có | Schema Workflow: chữ thường `[a-z][a-z0-9_]{0,62}`, không phải `public` hay schema hệ thống |
| `SPRING_FLYWAY_ENABLED` | Không | Đặt `false` khi schema được cấp riêng (như trong bản triển khai cục bộ) |
| `OIDC_ISSUER_URI` | Có | Issuer, ví dụ `http://localhost:8180/realms/tricore` |
| `OIDC_AUDIENCE` | Có | Audience bắt buộc của token, ví dụ `tricore-api` |
| `OIDC_RESOURCE_CLIENT_ID` | Có | Client có role được đọc làm authority, ví dụ `tricore-api` |
| `DXOS_HELPDESK_ENABLED` | Không | `true` để đăng ký Helpdesk API |
| `DXOS_HELPDESK_JDBCURL`, `DXOS_HELPDESK_USERNAME`, `DXOS_HELPDESK_PASSWORD` | Khi bật Helpdesk | Kết nối database của Helpdesk |
| `DXOS_HELPDESK_SCHEMA`, `DXOS_HELPDESK_TENANT` | Khi bật Helpdesk | Schema và tenant của Helpdesk |
| `SERVER_ADDRESS`, `SERVER_PORT` | Không | Địa chỉ và cổng lắng nghe (cổng mặc định `8080`) |

Helpdesk API từ chối khởi động nếu không thỏa đồng thời các điều kiện: `SERVER_ADDRESS` là
`127.0.0.1`, JDBC URL có dạng `jdbc:postgresql://127.0.0.1:<port>/helpdesk_disposable_<name>`, và
tài khoản đăng nhập có dạng `helpdesk_runtime_<name>`. API này chỉ dành cho database cục bộ, dùng
một lần.

Spring Boot không đọc tệp `.env`. Không commit credentials.

## Chạy cục bộ

Cách đơn giản nhất để chạy backend cùng PostgreSQL, Keycloak, Portal BFF và Portal là bản triển khai
cục bộ trong [infra/demo](https://github.com/tricore-opentrix/opentrix/blob/main/infra/demo/README.md).
Bản này build backend từ mã nguồn, cấp schema Helpdesk và đặt toàn bộ biến ở trên.

Để build và chạy riêng backend:

```powershell
.\gradlew.bat build          # Windows
./gradlew build              # Linux và macOS
java -jar build/libs/dxos-backend-0.1.0.jar
```

Ứng dụng cần các biến trong phần [Cấu hình](#cấu-hình) khi khởi động.

Archive mã nguồn của bản phát hành không có `gradle-wrapper.jar`. Khi đó, cài Gradle 8.14.3 và chạy
`gradle -p backend build` từ thư mục gốc của archive. Xem
[RELEASE.md](https://github.com/tricore-opentrix/opentrix/blob/main/docs/RELEASE.md).

## Migration database

| Vị trí | Nội dung |
| --- | --- |
| `src/main/resources/db/migration/V1`, `V2` | Các bảng request trước đây. Được giữ để `flyway validate` vẫn đạt trên database đã có; không mã nào sử dụng. |
| `src/main/resources/db/migration/V3` | Định nghĩa, instance và lịch sử chuyển trạng thái của Workflow |
| `src/main/resources/db/migration/V4` | Dữ liệu mẫu cho định nghĩa `document-review@1` và `incident-resolution@1` |
| `src/main/resources/db/helpdesk/` | Bảng Helpdesk, định nghĩa `it-helpdesk@1` và quyền runtime, áp dụng ngoài Flyway |

Định nghĩa không thể sửa sau khi đã commit; muốn thay đổi phải tạo phiên bản mới. Flyway bị giới hạn
trong schema đã cấu hình và tắt `clean` và baseline-on-migrate. Tài khoản runtime
không nên sở hữu schema và chỉ nên có các quyền trong
[runtime-grants.sql](https://github.com/tricore-opentrix/opentrix/blob/main/backend/src/main/resources/db/helpdesk/runtime-grants.sql).

## Kiểm thử

| Lệnh | Nội dung chạy | Cần |
| --- | --- | --- |
| `./gradlew test` | Unit, MVC, bảo mật và kiến trúc. Bỏ qua các test PostgreSQL. | JDK 21 |
| `./gradlew workflowIntegrationTest` | Bộ test lưu trữ và cô lập Workflow trên PostgreSQL | `WORKFLOW_TEST_JDBC_URL`, `WORKFLOW_TEST_DB_USER`, `WORKFLOW_TEST_DB_PASSWORD` (chỉ loopback) |
| `powershell -File ..\scripts\workflow-verify-local.ps1` | Khởi động container PostgreSQL 17.11 dùng một lần có TLS, chạy `test build` với mọi bộ integration test, rồi xóa container | Docker, JDK 21, Windows |

Integration fixture từ chối URL database không phải loopback. Không chạy chúng trên database dùng chung.

Các task Gradle `workflowSmoke`, `workflowSchemaBootstrap`, `workflowApprovedMigration` và các task
liên quan là công cụ vận hành cho PostgreSQL được lưu trữ từ xa. Chúng chỉ ghi vào database thật khi
có biến phê duyệt rõ ràng. Đọc [scripts/README.md](https://github.com/tricore-opentrix/opentrix/blob/main/scripts/README.md)
trước khi sử dụng.

## Giới hạn

- Helpdesk API chỉ chạy với database cục bộ, dùng một lần (xem [Cấu hình](#cấu-hình)).
- Adapter HTTP của Workflow chưa được đăng ký.
- `core.data` định nghĩa cổng lưu trữ; chưa có adapter lưu trữ cho môi trường production.
- Backend chưa được đóng gói thành container image hay JAR phát hành.
