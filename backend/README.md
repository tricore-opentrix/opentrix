<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors

SPDX-License-Identifier: Apache-2.0
-->

# DX-OS Open-Core backend

> **Trạng thái / Status:** 📝 Bản nháp chờ review độc lập / Draft for independent review · **Issue:** [#194](https://github.com/tricore-opentrix/opentrix/issues/194), [#197](https://github.com/tricore-opentrix/opentrix/issues/197) (Phase 3, Block B)
>
> **Source SHA:** `d98aa6f6f8b05add9cf90b67739681eae4e41176`. Mã và cấu hình `backend/` không đổi so với baseline kiểm kê Giai đoạn 2 `832c75fc3164cf170eed3bb8f1e380d24dd65aba` (các commit sau chỉ đổi `docs/`). / `backend/` code and configuration are unchanged since the Phase 2 audit baseline `832c75f…`; later commits touch only `docs/`.

## Tiếng Việt

### Nhãn bằng chứng

| Nhãn | Ý nghĩa |
|---|---|
| **AS-IS** | Có trong source/cấu hình tại SHA trên, đã đối chiếu bằng đọc file. **Không** có nghĩa lệnh đã chạy thành công. |
| **UNVERIFIED** | Chưa có bằng chứng chạy/nghiệm thu; không phải PASS. |
| **PROPOSED (#N)** | Mục tiêu/đề xuất, kèm Issue theo dõi; không phải hiện trạng. |

Bản README này được soạn **không** chạy build, test, database hay dịch vụ. Không có số liệu test mới. Các con số test/PASS trong phần Phụ lục là bằng chứng lịch sử của lần chạy được ghi, không phải kết quả của SHA hiện tại.

### A. Hiện trạng (AS-IS)

#### A1. Chức năng và phạm vi thực tế

Backend là một project Gradle duy nhất (`dxos-backend`), Spring Boot 3.5.16, kiến trúc Modular Monolith, base package `com.tricore.dxos`. Core cung cấp cơ chế tái sử dụng; application sở hữu ngữ nghĩa nghiệp vụ.

Có trong source (AS-IS):

- **Health:** `GET /api/v1/health` (công khai) và Actuator `/actuator/health`.
- **Identity/Security:** Spring Security resource server, xác thực JWT (issuer, audience, loại token, subject, hết hạn), phiên stateless. Cổng `CurrentPrincipal` cho lớp trên.
- **Workflow:** engine `WorkflowRuntime` tự viết trong Core, `WorkflowPersistencePort`, adapter JDBC PostgreSQL (`PostgresWorkflowPersistence`), migration V3/V4 và các công cụ vận hành guarded.
- **Helpdesk MVP:** `/api/v1/mvp/requests`, chỉ đăng ký khi `dxos.helpdesk.enabled=true` (xem A8).
- **Data:** hợp đồng `ObjectStoragePort` trong Core; chỉ có fake in-memory trong test, **không** có adapter production.

Không phải hiện trạng: Flowable, APISIX, object storage production, Workflow HTTP chung (`/api/v1/workflow-instances`, controller chưa đăng ký), LIVE browser E2E. Xem phần PROPOSED (B).

#### A2. Công cụ yêu cầu

| Công cụ | Yêu cầu | Nguồn |
|---|---|---|
| JDK | **21**; đặt `JAVA_HOME` | `build.gradle` (toolchain `JavaLanguageVersion.of(21)`), CI Temurin 21 |
| Gradle | Wrapper **8.14.3**, không cài riêng | `gradle/wrapper/gradle-wrapper.properties` |
| Spring Boot | 3.5.16 | `build.gradle` |
| PostgreSQL | Không cần cho build/test thường; cần để chạy ứng dụng. Fixture/Compose dùng `postgres:17.11-alpine` | `../infra/compose.workflow-postgres.yml` |
| Docker | Chỉ cho fixture database | runbook Helpdesk/Workflow |
| PowerShell, OpenSSL | Cho các script `.ps1` (Windows) | `../scripts/` |
| Internet | Lần build đầu (Gradle, dependency) | — |

Dùng chung hướng dẫn cài đặt môi trường, clone và cấu hình chi tiết tại [../docs/DEVELOPMENT.md](../docs/DEVELOPMENT.md); README này không lặp lại.

#### A3. Build và test (Windows / Linux)

Từ thư mục `backend/`:

```powershell
.\gradlew.bat --version
.\gradlew.bat test
.\gradlew.bat build
.\gradlew.bat test --tests com.tricore.dxos.common.health.HealthControllerTest
```

```sh
./gradlew --version
./gradlew test
./gradlew build
./gradlew test --tests com.tricore.dxos.common.health.HealthControllerTest
```

`build` đã gồm `test` và đóng gói. Test thường không cần PostgreSQL: `build.gradle` cấp giá trị mặc định cho `OIDC_ISSUER_URI`, `OIDC_AUDIENCE`, `OIDC_RESOURCE_CLIENT_ID` khi chạy `test`. Các ca cần database hoặc token thật chỉ chạy khi có biến opt-in (xem A9). Lệnh chạy trên Linux/macOS theo Wrapper POSIX (`backend/gradlew` ghi trong Git index mode `100755`) và CI Ubuntu 24.04; chưa chạy trên máy Linux cục bộ: **UNVERIFIED**.

#### A4. Artifact (JAR) — đã hiệu chỉnh

Tên cũ `dxos-backend-0.0.1-SNAPSHOT.jar` trong các hướng dẫn trước **đã lỗi thời**. Cấu hình hiện tại: `rootProject.name = 'dxos-backend'` (`settings.gradle`), `version = '0.1.0'` (`build.gradle`), không ghi đè tên archive/`bootJar`. Vì vậy tên theo mặc định của Gradle/Spring Boot là:

- `backend/build/libs/dxos-backend-0.1.0.jar` — executable JAR (Spring Boot `bootJar`).
- Plugin Spring Boot cũng tạo JAR `-plain`; không dùng JAR này để chạy.

Chạy: `java -jar build/libs/dxos-backend-0.1.0.jar` (với đủ biến môi trường). Tên này **suy ra từ cấu hình Gradle**; chưa chạy `build` nên file thực tế **UNVERIFIED** — liệt kê `build/libs/` sau khi build để xác nhận.

#### A5. Cấu hình local và khởi động an toàn

Spring Boot **không** đọc `.env`. Đặt biến vào môi trường của process; không commit mật khẩu/token; không đặt mật khẩu trong tham số lệnh.

| Nhóm | Biến | Nguồn |
|---|---|---|
| Datasource | `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | `application.yml` (không mặc định) |
| OIDC | `OIDC_ISSUER_URI`, `OIDC_AUDIENCE`, `OIDC_RESOURCE_CLIENT_ID` | `application.yml` (không mặc định) |
| Workflow | `DXOS_WORKFLOW_SCHEMA`, `currentSchema` khớp, `SPRING_FLYWAY_ENABLED=false` | Phụ lục |
| Helpdesk | `DXOS_HELPDESK_ENABLED`, `DXOS_HELPDESK_JDBCURL`, `DXOS_HELPDESK_USERNAME`, `DXOS_HELPDESK_PASSWORD`, `DXOS_HELPDESK_SCHEMA`, `DXOS_HELPDESK_TENANT` | `HelpdeskConfiguration`, runbook |

**Chỉ `DB_*` là chưa đủ**: `application.yml` còn yêu cầu ba biến OIDC. (Hướng dẫn cũ ghi "đủ năm biến `DB_*`" đã được hiệu chỉnh.) Hành vi khởi động khi issuer không truy cập được: **UNVERIFIED**.

Khởi động an toàn:

1. Chọn **một** runbook đầy đủ: Workflow cục bộ (Phụ lục, "Chạy backend local từ clone mới") hoặc [Helpdesk cục bộ](../scripts/README-helpdesk-local.md).
2. Spring Boot có Flyway; các runbook provision schema riêng và tắt Flyway tự động. Không trỏ lần khởi động chưa review vào database dùng chung. Không dùng lại launcher cloud bootstrap/migration/smoke lịch sử.
3. Sau khi sẵn sàng, từ `backend/`: `.\gradlew.bat bootRun` (Windows) hoặc `./gradlew bootRun` (Linux); kiểm tra `GET http://localhost:8080/api/v1/health` → `{"status":"UP"}`. Endpoint này không truy vấn PostgreSQL, nên không chứng minh persistence hay phân quyền.

#### A6. Bản đồ package (AS-IS)

Gốc: `backend/src/main/java/com/tricore/dxos/`.

| Package | Nội dung (theo source) |
|---|---|
| `core/identity` | `AuthenticatedPrincipal`, `Authority`, `RequiredAuthority`, `AuthorizationDecision`, `IdentityException`… |
| `core/workflow` | `WorkflowRuntime`, `WorkflowPersistencePort`, `WorkflowDefinition`, `WorkflowInstance`, `TransitionCommand/Record/Result`, `WorkflowException`… |
| `core/data` | `ObjectStoragePort`, `ObjectKey`, `ObjectMetadata`, `StoreObjectCommand`… (chưa có bên dùng ở runtime) |
| `application/authorization` | `WorkflowAuthorization`, `WorkflowAccessPolicy`, `TenantResourceWorkflowAccessPolicy`, `WorkflowOperation`… |
| `application/identity` | `CurrentPrincipal` (cổng principal đã xác minh) |
| `application/helpdesk`, `application/facility` | Chỉ có `.gitkeep`; chưa có mã |
| `gateway/helpdesk` | `HelpdeskController`, `HelpdeskExceptionHandler` |
| `gateway/workflow` | `controller/WorkflowController` (không đăng ký), `dto/*`, `security/WorkflowGatewayPrincipalGate`, `WorkflowJsonConfiguration` |
| `infrastructure/identity/security` | `SecurityConfig`, `SpringSecurityCurrentPrincipal`, các validator JWT, `ApiAuthenticationEntryPoint` |
| `infrastructure/workflow` | `HelpdeskService`, `HelpdeskConfiguration`, `PostgresWorkflowPersistence`, `WorkflowPersistenceConfiguration`, `WorkflowSchema`, `WorkflowMigrations`, các runner/guard vận hành (`WorkflowSmokeRunner`, `WorkflowEventTriggerGuard`, `WorkflowLiveGuard`…) |
| `infrastructure/persistence`, `infrastructure/storage` | Chỉ `package-info`; chưa có triển khai |
| `common` | `error/ApiError`, `health/HealthController` |

Resource: `db/migration` (V1–V4, lịch sử bất biến), `db/helpdesk` (SQL demo Helpdesk), `workflow-event-trigger-manifest.json`.

Lưu ý lệch với thiết kế: nghiệp vụ Helpdesk hiện nằm ở `infrastructure.workflow.HelpdeskService`, không ở `application.helpdesk` (xem B).

#### A7. Ranh giới module và quy tắc phụ thuộc

**Được thực thi tự động (AS-IS):** `CoreDependencyRulesTest` (ArchUnit 1.5.1, `testImplementation`):

- `core..` chỉ phụ thuộc `java..` (loại `java.sql..`) và chính package Core.
- Ba năng lực `core.identity`, `core.workflow`, `core.data` không phụ thuộc lẫn nhau.
- Có canary âm/dương để chứng minh quy tắc bắt được vi phạm.

**Chưa được thực thi tự động:** quy tắc cho Application/Gateway/Infrastructure. Theo [báo cáo Block A](../docs/09-evidence/phase-2/block-a-architecture.md) (jdeps tại baseline): có đúng một cạnh đi vào `infrastructure` từ tầng trên là `gateway.helpdesk → infrastructure.workflow` (BND-01); `HelpdeskService` gộp phân quyền, điều phối và JDBC (BND-02); hai gói gateway phụ thuộc lẫn nhau (BND-08); `WorkflowController` gọi thẳng `WorkflowRuntime` (BND-10, controller chưa đăng ký). Đây là sai lệch đã ghi nhận, không phải hành vi mong muốn; xem B (#193).

#### A8. Helpdesk API, Workflow runtime và security guard

Helpdesk (`it-helpdesk@1`), chỉ khi `dxos.helpdesk.enabled=true`: `POST/GET /api/v1/mvp/requests`, `GET .../{id}`, `GET .../{id}/history`, `POST .../{id}/triage|assign|start|resolve|confirm`. Luồng: `SUBMITTED → TRIAGED → IN_PROGRESS → RESOLVED → CONFIRMED`; `assign` không phải trạng thái Workflow (tăng `assignment_version`); không có `/close` hoặc `CLOSED`. Chi tiết: mục "Helpdesk Application API" ở Phụ lục; mã: `HelpdeskController`, `HelpdeskService`.

Workflow runtime: `WorkflowRuntime` (Core) + `WorkflowPersistencePort`; adapter `PostgresWorkflowPersistence` (schema riêng, V3/V4, ghi lossless thời gian, `COMMIT_OUTCOME_UNKNOWN` không retry). Chi tiết ở Phụ lục "Workflow PostgreSQL adapter".

Guard hiện có (AS-IS, theo source):

| Guard | Hành vi |
|---|---|
| `SecurityConfig` | Mọi request phải xác thực trừ `/api/v1/health`; JWT resource server; stateless; CSRF tắt (Backend nhận Bearer token; CSRF thuộc BFF) |
| Validator JWT | Issuer, audience, loại access token, subject (chuỗi), hết hạn |
| `CurrentPrincipal.requireVerified()` | Helpdesk lấy danh tính từ principal đã xác minh, không từ tham số của caller |
| `HelpdeskConfiguration.requireDisposable` | Từ chối nếu JDBC URL không có dạng loopback `127.0.0.1`, cổng bất kỳ, tên database bắt đầu bằng `helpdesk_disposable_`; user không bắt đầu bằng `helpdesk_runtime_`; hoặc `server.address` khác `127.0.0.1` |
| `WorkflowController` | Không phải `@RestController`/`@Component`; cố ý không đăng ký production (`WorkflowHttpExposureTest` có trong bộ CI) |
| `WorkflowGatewayPrincipalGate` | Chuyển giao Identity → Gateway; không quyết định tenant/ACL |
| `WorkflowSchema` | Xác thực định danh schema (lowercase, không phải schema hệ thống) |
| `WorkflowEventTriggerGuard` và manifest | Chặn event trigger/privilege lệch manifest ở các công cụ vận hành |
| Phiên bản lạc quan | `expectedVersion` / `expectedAssignmentVersion`; xung đột bị từ chối |

Hệ quả: Helpdesk hiện chỉ chạy với database cục bộ dùng một lần. Chưa có đường chạy cho database dùng chung/production.

#### A9. Phân biệt các lớp kiểm thử

| Lớp | Cách chạy | Phạm vi và giới hạn |
|---|---|---|
| Unit / MVC / hợp đồng / kiến trúc | `./gradlew test` | Không cần DB; gồm `HealthControllerTest`, `CoreDependencyRulesTest`, test Core/Authorization/Security |
| Integration PostgreSQL (Workflow) | `./gradlew workflowIntegrationTest --no-daemon` | Cần `WORKFLOW_TEST_JDBC_URL`, `WORKFLOW_TEST_DB_USER`, `WORKFLOW_TEST_DB_PASSWORD` và DB loopback dùng một lần; thiếu biến thì task fail. Trong `test` thường, các ca này bị bỏ qua nếu thiếu cờ |
| Helpdesk HTTP + PostgreSQL | `HelpdeskHttpPostgresTest`, `scripts/helpdesk-negative-local.ps1` | Opt-in, DB cục bộ; JWKS giả, không phải Keycloak thật |
| Token Keycloak thật | `OidcKeycloakIntegrationTest`, `GatewayKeycloakTokenHttpIntegrationTest` với `OIDC_TEST_ACCESS_TOKEN` | Opt-in; issuer cố định `http://localhost:8180/realms/tricore` |
| CI | `.github/workflows/ci.yml` job `backend`: `./gradlew build --no-daemon --stacktrace --rerun-tasks`, rồi xác nhận ba suite `GatewayIdentityHandoffHttpTest`, `SpringSecurityCurrentPrincipalTest`, `WorkflowHttpExposureTest` đã chạy (tests > 0, không failure/skip) | `ci.yml` không cấp biến `WORKFLOW_TEST_*`, nên các ca DB không được kỳ vọng chạy trong CI (chưa xác minh từ log CI cụ thể). CI PASS **không** chứng minh PostgreSQL/Keycloak tích hợp |
| LIVE browser E2E | Cổng nghiệm thu #118 | **UNVERIFIED**; cần Keycloak → BFF → Backend → PostgreSQL thật từ trình duyệt. CI PASS hay build PASS **không phải** LIVE E2E PASS |

Đọc báo cáo mới trong `build/test-results/test/` và `build/reports/tests/test/`; ca bị skip không phải PASS. Xem thêm [../docs/DEVELOPMENT.md](../docs/DEVELOPMENT.md) mục 4.1.

#### A10. Bằng chứng Phase 2 (tại source SHA)

Baseline kiểm kê: `832c75fc3164cf170eed3bb8f1e380d24dd65aba` (mã `backend/` giống SHA hiện tại).

- [Block A — Kiến trúc](../docs/09-evidence/phase-2/block-a-architecture.md): ranh giới BND-01…BND-11, ma trận phụ thuộc, Flowable/APISIX là quyết định đang chờ.
- [Block B — Backend & hạ tầng](../docs/09-evidence/phase-2/block-b-backend-infra.md): P2-CORE-01 (Backend/Core/Workflow/Identity), P2-DATA-02 (PostgreSQL, storage), P2-INFRA-03 (CI/Gradle/Docker).
- [Block C — Ứng dụng](../docs/09-evidence/phase-2/block-c-application.md): Portal/BFF/Helpdesk; #118, #112 là việc tiếp theo.

Issue [#182](https://github.com/tricore-opentrix/opentrix/issues/182) đã đóng với verdict `PHASE_2_ACCEPTED` ngày 11/11/2026. Verdict này là **nghiệm thu kiểm kê/báo cáo Giai đoạn 2**. Nó **không** thay thế: (1) xác minh runtime (PostgreSQL/Keycloak tích hợp, LIVE E2E #118); (2) xác minh nguồn gốc và quyền tác giả ([#138](https://github.com/tricore-opentrix/opentrix/issues/138)); (3) nghiệm thu release (R24). Các điều kiện này vẫn được xét riêng; ví dụ trạng thái `RIGHTS_CLEARED` hay `RELEASE_ACCEPTED` không được suy ra từ `PHASE_2_ACCEPTED`. (Ngày đóng Issue và verdict do owner cung cấp; chưa kiểm tra trực tiếp trên GitHub.)

### B. Mục tiêu (PROPOSED)

| Hạng mục | Issue |
|---|---|
| Quyết định kiến trúc Modular Monolith + Flowable (hiện dùng `WorkflowRuntime` tự viết; Flowable chưa tích hợp) | PROPOSED ([#191](https://github.com/tricore-opentrix/opentrix/issues/191)) |
| Tách use-case Helpdesk khỏi `infrastructure` thành Application use-case / Module API theo kiến trúc được duyệt (giải quyết BND-01/02; cấu trúc package cụ thể chưa chốt) | PROPOSED ([#193](https://github.com/tricore-opentrix/opentrix/issues/193)) |
| OpenAPI/Swagger tại runtime (hiện không có) | PROPOSED ([#112](https://github.com/tricore-opentrix/opentrix/issues/112)) |
| LIVE browser E2E | PROPOSED ([#118](https://github.com/tricore-opentrix/opentrix/issues/118)) |
| Quyết định hướng lưu trữ: ADR-016 và provider object storage | PROPOSED ([#181](https://github.com/tricore-opentrix/opentrix/issues/181)) |
| Triển khai adapter production cho `ObjectStoragePort` qua API tương thích S3 (hiện chỉ có fake trong test); phụ thuộc quyết định #181 | PROPOSED ([#192](https://github.com/tricore-opentrix/opentrix/issues/192)) |
| API Gateway chuyên dụng (APISIX) | PROPOSED ([#116](https://github.com/tricore-opentrix/opentrix/issues/116)) |

Tất cả các mục trên chưa hoàn thành hoặc chưa nghiệm thu; README này không gán trạng thái hoàn thành cho Issue nào.

## English

### Evidence labels

| Label | Meaning |
|---|---|
| **AS-IS** | Present in source/config at the SHA above, cross-checked by reading files. It does **not** mean the command was run successfully. |
| **UNVERIFIED** | No run/acceptance evidence; not PASS. |
| **PROPOSED (#N)** | Target/proposal with a tracking Issue; not current state. |

This README was drafted **without** running any build, test, database or service. No new test figures are given. Test/PASS figures in the Appendix are historical evidence for the recorded run, not results for the current SHA.

### A. Current state (AS-IS)

#### A1. Function and actual scope

The backend is a single Gradle project (`dxos-backend`), Spring Boot 3.5.16, Modular Monolith, base package `com.tricore.dxos`. Core provides reusable mechanisms; applications own business semantics.

Present in source (AS-IS):

- **Health:** `GET /api/v1/health` (public) and Actuator `/actuator/health`.
- **Identity/Security:** Spring Security resource server, JWT validation (issuer, audience, token type, subject, expiry), stateless sessions. A `CurrentPrincipal` port for upper layers.
- **Workflow:** in-house `WorkflowRuntime` engine in Core, `WorkflowPersistencePort`, PostgreSQL JDBC adapter (`PostgresWorkflowPersistence`), V3/V4 migrations and guarded operator tools.
- **Helpdesk MVP:** `/api/v1/mvp/requests`, registered only when `dxos.helpdesk.enabled=true` (see A8).
- **Data:** `ObjectStoragePort` contract in Core; only an in-memory fake in tests, **no** production adapter.

Not current state: Flowable, APISIX, production object storage, the generic Workflow HTTP API (`/api/v1/workflow-instances`, controller not registered), LIVE browser E2E. See PROPOSED (B).

#### A2. Required tools

| Tool | Requirement | Source |
|---|---|---|
| JDK | **21**; set `JAVA_HOME` | `build.gradle` (toolchain `JavaLanguageVersion.of(21)`), CI Temurin 21 |
| Gradle | Wrapper **8.14.3**, no separate install | `gradle/wrapper/gradle-wrapper.properties` |
| Spring Boot | 3.5.16 | `build.gradle` |
| PostgreSQL | Not needed for ordinary build/test; needed to run the application. Fixtures/Compose use `postgres:17.11-alpine` | `../infra/compose.workflow-postgres.yml` |
| Docker | Database fixtures only | Helpdesk/Workflow runbooks |
| PowerShell, OpenSSL | For the `.ps1` scripts (Windows) | `../scripts/` |
| Internet | First build (Gradle, dependencies) | — |

Environment setup, cloning and detailed configuration are shared with [../docs/DEVELOPMENT.md](../docs/DEVELOPMENT.md); this README does not repeat them.

#### A3. Build and test (Windows / Linux)

From `backend/`:

```powershell
.\gradlew.bat --version
.\gradlew.bat test
.\gradlew.bat build
.\gradlew.bat test --tests com.tricore.dxos.common.health.HealthControllerTest
```

```sh
./gradlew --version
./gradlew test
./gradlew build
./gradlew test --tests com.tricore.dxos.common.health.HealthControllerTest
```

`build` already includes `test` and packaging. Ordinary tests need no PostgreSQL: `build.gradle` supplies defaults for `OIDC_ISSUER_URI`, `OIDC_AUDIENCE`, `OIDC_RESOURCE_CLIENT_ID` when running `test`. Cases needing a database or real tokens run only with opt-in variables (see A9). Linux/macOS commands follow the POSIX Wrapper (`backend/gradlew` is recorded in the Git index as mode `100755`) and the Ubuntu 24.04 CI; not run on a local Linux machine: **UNVERIFIED**.

#### A4. Artifact (JAR) — corrected

The earlier name `dxos-backend-0.0.1-SNAPSHOT.jar` in previous instructions is **stale**. Current configuration: `rootProject.name = 'dxos-backend'` (`settings.gradle`), `version = '0.1.0'` (`build.gradle`), no archive/`bootJar` name override. The Gradle/Spring Boot default name is therefore:

- `backend/build/libs/dxos-backend-0.1.0.jar` — executable JAR (Spring Boot `bootJar`).
- The Spring Boot plugin also produces a `-plain` JAR; do not use it to run the application.

Run: `java -jar build/libs/dxos-backend-0.1.0.jar` (with the full environment). This name is **derived from Gradle configuration**; `build` was not run, so the actual file is **UNVERIFIED** — list `build/libs/` after building to confirm.

#### A5. Local configuration and safe startup

Spring Boot does **not** read `.env`. Set variables in the process environment; never commit passwords/tokens; never put passwords in command arguments.

| Group | Variables | Source |
|---|---|---|
| Datasource | `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | `application.yml` (no defaults) |
| OIDC | `OIDC_ISSUER_URI`, `OIDC_AUDIENCE`, `OIDC_RESOURCE_CLIENT_ID` | `application.yml` (no defaults) |
| Workflow | `DXOS_WORKFLOW_SCHEMA`, matching `currentSchema`, `SPRING_FLYWAY_ENABLED=false` | Appendix |
| Helpdesk | `DXOS_HELPDESK_ENABLED`, `DXOS_HELPDESK_JDBCURL`, `DXOS_HELPDESK_USERNAME`, `DXOS_HELPDESK_PASSWORD`, `DXOS_HELPDESK_SCHEMA`, `DXOS_HELPDESK_TENANT` | `HelpdeskConfiguration`, runbook |

**`DB_*` alone is not enough**: `application.yml` also requires the three OIDC variables. (The older "all five `DB_*` variables are enough" wording has been corrected.) Startup behavior when the issuer is unreachable: **UNVERIFIED**.

Safe startup:

1. Choose **one** complete runbook: local Workflow (Appendix, "Chạy backend local từ clone mới") or [local Helpdesk](../scripts/README-helpdesk-local.md).
2. Spring Boot includes Flyway; the runbooks provision a separate schema and disable automatic Flyway. Never point an unreviewed startup at a shared database. Do not re-run the historical cloud bootstrap/migration/smoke launchers.
3. When ready, from `backend/`: `.\gradlew.bat bootRun` (Windows) or `./gradlew bootRun` (Linux); check `GET http://localhost:8080/api/v1/health` → `{"status":"UP"}`. This endpoint does not query PostgreSQL, so it proves neither persistence nor authorization.

#### A6. Package map (AS-IS)

Root: `backend/src/main/java/com/tricore/dxos/`.

| Package | Contents (per source) |
|---|---|
| `core/identity` | `AuthenticatedPrincipal`, `Authority`, `RequiredAuthority`, `AuthorizationDecision`, `IdentityException`… |
| `core/workflow` | `WorkflowRuntime`, `WorkflowPersistencePort`, `WorkflowDefinition`, `WorkflowInstance`, `TransitionCommand/Record/Result`, `WorkflowException`… |
| `core/data` | `ObjectStoragePort`, `ObjectKey`, `ObjectMetadata`, `StoreObjectCommand`… (no runtime consumer yet) |
| `application/authorization` | `WorkflowAuthorization`, `WorkflowAccessPolicy`, `TenantResourceWorkflowAccessPolicy`, `WorkflowOperation`… |
| `application/identity` | `CurrentPrincipal` (verified-principal port) |
| `application/helpdesk`, `application/facility` | `.gitkeep` only; no code |
| `gateway/helpdesk` | `HelpdeskController`, `HelpdeskExceptionHandler` |
| `gateway/workflow` | `controller/WorkflowController` (not registered), `dto/*`, `security/WorkflowGatewayPrincipalGate`, `WorkflowJsonConfiguration` |
| `infrastructure/identity/security` | `SecurityConfig`, `SpringSecurityCurrentPrincipal`, JWT validators, `ApiAuthenticationEntryPoint` |
| `infrastructure/workflow` | `HelpdeskService`, `HelpdeskConfiguration`, `PostgresWorkflowPersistence`, `WorkflowPersistenceConfiguration`, `WorkflowSchema`, `WorkflowMigrations`, operator runners/guards (`WorkflowSmokeRunner`, `WorkflowEventTriggerGuard`, `WorkflowLiveGuard`…) |
| `infrastructure/persistence`, `infrastructure/storage` | `package-info` only; no implementation |
| `common` | `error/ApiError`, `health/HealthController` |

Resources: `db/migration` (V1–V4, immutable history), `db/helpdesk` (Helpdesk demo SQL), `workflow-event-trigger-manifest.json`.

Deviation from the design: Helpdesk business logic currently lives in `infrastructure.workflow.HelpdeskService`, not in `application.helpdesk` (see B).

#### A7. Module boundaries and dependency rules

**Enforced automatically (AS-IS):** `CoreDependencyRulesTest` (ArchUnit 1.5.1, `testImplementation`):

- `core..` may depend only on `java..` (excluding `java.sql..`) and its own Core packages.
- The three capabilities `core.identity`, `core.workflow`, `core.data` must not depend on each other.
- Negative/positive canaries prove the rule catches violations.

**Not enforced automatically:** rules for Application/Gateway/Infrastructure. Per the [Block A report](../docs/09-evidence/phase-2/block-a-architecture.md) (jdeps at baseline): exactly one upper-layer edge into `infrastructure` exists, `gateway.helpdesk → infrastructure.workflow` (BND-01); `HelpdeskService` mixes authorization, orchestration and JDBC (BND-02); the two gateway packages depend on each other (BND-08); `WorkflowController` calls `WorkflowRuntime` directly (BND-10, controller not registered). These are recorded deviations, not intended behavior; see B (#193).

#### A8. Helpdesk API, Workflow runtime and security guards

Helpdesk (`it-helpdesk@1`), only when `dxos.helpdesk.enabled=true`: `POST/GET /api/v1/mvp/requests`, `GET .../{id}`, `GET .../{id}/history`, `POST .../{id}/triage|assign|start|resolve|confirm`. Flow: `SUBMITTED → TRIAGED → IN_PROGRESS → RESOLVED → CONFIRMED`; `assign` is not a Workflow state (it increments `assignment_version`); there is no `/close` or `CLOSED`. Details: the "Helpdesk Application API" section in the Appendix; code: `HelpdeskController`, `HelpdeskService`.

Workflow runtime: `WorkflowRuntime` (Core) + `WorkflowPersistencePort`; adapter `PostgresWorkflowPersistence` (dedicated schema, V3/V4, lossless time storage, no retry on `COMMIT_OUTCOME_UNKNOWN`). Details: Appendix "Workflow PostgreSQL adapter".

Existing guards (AS-IS, per source):

| Guard | Behavior |
|---|---|
| `SecurityConfig` | Every request must be authenticated except `/api/v1/health`; JWT resource server; stateless; CSRF disabled (the Backend takes Bearer tokens; CSRF belongs to the BFF) |
| JWT validators | Issuer, audience, access-token type, subject (string), expiry |
| `CurrentPrincipal.requireVerified()` | Helpdesk takes identity from the verified principal, not from caller-supplied parameters |
| `HelpdeskConfiguration.requireDisposable` | Rejects unless the JDBC URL is loopback `127.0.0.1` with any port and a database name starting with `helpdesk_disposable_`, the user starts with `helpdesk_runtime_`, and `server.address` is `127.0.0.1` |
| `WorkflowController` | Not a `@RestController`/`@Component`; deliberately not registered in production (`WorkflowHttpExposureTest` is in the CI suite set) |
| `WorkflowGatewayPrincipalGate` | Identity → Gateway handoff; does not decide tenant/ACL |
| `WorkflowSchema` | Validates the schema identifier (lowercase, not a system schema) |
| `WorkflowEventTriggerGuard` and manifest | Blocks event-trigger/privilege drift from the manifest in the operator tools |
| Optimistic versions | `expectedVersion` / `expectedAssignmentVersion`; conflicts are rejected |

Consequence: Helpdesk currently runs only against a local disposable database. No path exists for a shared/production database.

#### A9. Test layers

| Layer | How to run | Scope and limits |
|---|---|---|
| Unit / MVC / contract / architecture | `./gradlew test` | No DB; includes `HealthControllerTest`, `CoreDependencyRulesTest`, Core/Authorization/Security tests |
| PostgreSQL integration (Workflow) | `./gradlew workflowIntegrationTest --no-daemon` | Needs `WORKFLOW_TEST_JDBC_URL`, `WORKFLOW_TEST_DB_USER`, `WORKFLOW_TEST_DB_PASSWORD` and a disposable loopback DB; the task fails if they are missing. Under plain `test`, these cases are skipped without their flags |
| Helpdesk HTTP + PostgreSQL | `HelpdeskHttpPostgresTest`, `scripts/helpdesk-negative-local.ps1` | Opt-in, local DB; synthetic JWKS, not real Keycloak |
| Real Keycloak tokens | `OidcKeycloakIntegrationTest`, `GatewayKeycloakTokenHttpIntegrationTest` with `OIDC_TEST_ACCESS_TOKEN` | Opt-in; issuer hardcoded to `http://localhost:8180/realms/tricore` |
| CI | `.github/workflows/ci.yml` job `backend`: `./gradlew build --no-daemon --stacktrace --rerun-tasks`, then confirms the three suites `GatewayIdentityHandoffHttpTest`, `SpringSecurityCurrentPrincipalTest`, `WorkflowHttpExposureTest` ran (tests > 0, no failures/skips) | `ci.yml` supplies no `WORKFLOW_TEST_*` variables, so DB cases are not expected to run in CI (not verified from a specific CI log). CI PASS does **not** prove PostgreSQL/Keycloak integration |
| LIVE browser E2E | Acceptance gate #118 | **UNVERIFIED**; needs real Keycloak → BFF → Backend → PostgreSQL from a browser. CI PASS or build PASS is **not** LIVE E2E PASS |

Read fresh reports in `build/test-results/test/` and `build/reports/tests/test/`; a skipped case is not PASS. See also [../docs/DEVELOPMENT.md](../docs/DEVELOPMENT.md) section 4.1.

#### A10. Phase 2 evidence (at the source SHA)

Audit baseline: `832c75fc3164cf170eed3bb8f1e380d24dd65aba` (`backend/` code identical to the current SHA).

- [Block A — Architecture](../docs/09-evidence/phase-2/block-a-architecture.md): boundaries BND-01…BND-11, dependency matrix, Flowable/APISIX as pending decisions.
- [Block B — Backend & infrastructure](../docs/09-evidence/phase-2/block-b-backend-infra.md): P2-CORE-01 (Backend/Core/Workflow/Identity), P2-DATA-02 (PostgreSQL, storage), P2-INFRA-03 (CI/Gradle/Docker).
- [Block C — Application](../docs/09-evidence/phase-2/block-c-application.md): Portal/BFF/Helpdesk; #118 and #112 are follow-up work.

Issue [#182](https://github.com/tricore-opentrix/opentrix/issues/182) was closed with verdict `PHASE_2_ACCEPTED` on 2026-11-11. This verdict is **acceptance of the Phase 2 inventory/reports**. It does **not** replace: (1) runtime verification (integrated PostgreSQL/Keycloak, LIVE E2E #118); (2) source-origin and rights verification ([#138](https://github.com/tricore-opentrix/opentrix/issues/138)); (3) release acceptance (R24). These remain separate gates; for example `RIGHTS_CLEARED` or `RELEASE_ACCEPTED` must not be inferred from `PHASE_2_ACCEPTED`. (The closing date and verdict were supplied by the owner; not checked directly on GitHub.)

### B. Targets (PROPOSED)

| Item | Issue |
|---|---|
| Architecture decision Modular Monolith + Flowable (currently the in-house `WorkflowRuntime`; Flowable is not integrated) | PROPOSED ([#191](https://github.com/tricore-opentrix/opentrix/issues/191)) |
| Move Helpdesk use cases out of `infrastructure` into an Application use-case / Module API per the approved architecture (addresses BND-01/02; the concrete package structure is not decided) | PROPOSED ([#193](https://github.com/tricore-opentrix/opentrix/issues/193)) |
| Runtime OpenAPI/Swagger (none today) | PROPOSED ([#112](https://github.com/tricore-opentrix/opentrix/issues/112)) |
| LIVE browser E2E | PROPOSED ([#118](https://github.com/tricore-opentrix/opentrix/issues/118)) |
| Storage direction decision: ADR-016 and object-storage provider | PROPOSED ([#181](https://github.com/tricore-opentrix/opentrix/issues/181)) |
| Production adapter for `ObjectStoragePort` via an S3-compatible API (only a test fake exists today); depends on the #181 decision | PROPOSED ([#192](https://github.com/tricore-opentrix/opentrix/issues/192)) |
| Dedicated API Gateway (APISIX) | PROPOSED ([#116](https://github.com/tricore-opentrix/opentrix/issues/116)) |

None of the above is complete or accepted; this README assigns no completion status to any Issue.

## Phụ lục / Appendix — Runbook chi tiết (giữ nguyên, chủ yếu tiếng Việt)

> **VI:** Phần dưới là runbook vận hành gốc, giữ nguyên nội dung lịch sử (chủ yếu tiếng Việt, một số mục tiếng Anh). Chỉ các điểm lỗi thời đã được đánh dấu "**Hiệu chỉnh**". Mô tả Issue gốc: Issue #1 tạo nền dự án và health API; Issue #5 từng bổ sung Request prototype (đã gỡ ở R25); Issue #7 bổ sung workflow IT Support. / **EN:** The section below is the original operational runbook, kept as historical content (mostly Vietnamese, some English). Only stale points are marked "**Hiệu chỉnh**" (corrected). Original issue notes: Issue #1 created the project base and health API; Issue #5 once added a Request prototype (removed in R25); Issue #7 added IT Support workflow. Hard-coded paths and dated owner reports below are historical records, not instructions.

## Yêu cầu

- JDK **21**, với `JAVA_HOME` trỏ đến thư mục JDK.
- PowerShell trên Windows.
- Internet ở lần build đầu để Gradle Wrapper tải Gradle và dependency.
- PostgreSQL khả dụng khi chạy toàn bộ ứng dụng; môi trường Docker/PostgreSQL
  do Issue #3 cung cấp. **[LỊCH SỬ]** Issue #3 đã bị xóa; không còn là điều kiện hướng dẫn hiện tại. Dùng runbook Workflow/Helpdesk cục bộ (A5). Việc Issue bị xóa không có nghĩa công việc đã hoàn thành.

Dự án sử dụng Spring Boot 3.5.16, Gradle Groovy và Gradle Wrapper 8.14.3.
Không cần cài Gradle riêng. Các lệnh bên dưới chạy từ thư mục `backend/`.

## Build và test trên Windows

Ví dụ thiết lập JDK (thay đường dẫn theo máy):

```powershell
$env:JAVA_HOME = 'C:\Program Files\Java\jdk-21.0.11'
$env:Path = "$env:JAVA_HOME\bin;$env:Path"
java -version
.\gradlew.bat --version
.\gradlew.bat test
.\gradlew.bat build
```

Build tạo executable JAR tại `build/libs/dxos-backend-0.1.0.jar`
(**Hiệu chỉnh:** tên cũ `0.0.1-SNAPSHOT` đã lỗi thời; xem A4. Tên suy ra từ cấu hình Gradle, UNVERIFIED cho đến khi build).
Test health dùng `@WebMvcTest`, kiểm tra HTTP 200, Content-Type JSON và chính
xác body `{"status":"UP"}`. Build và test này không cần PostgreSQL hay biến
môi trường database. Không có database giả hoặc dependency H2.

Chạy riêng test health:

```powershell
.\gradlew.bat test --tests com.tricore.dxos.common.health.HealthControllerTest
```

## PostgreSQL và biến môi trường

**Hiệu chỉnh:** năm biến `DB_*` dưới đây là chưa đủ; ứng dụng còn cần `OIDC_ISSUER_URI`, `OIDC_AUDIENCE`, `OIDC_RESOURCE_CLIENT_ID` (xem A5). Cần cung cấp năm biến sau trong process chạy ứng dụng:

| Biến | Ý nghĩa |
| --- | --- |
| `DB_HOST` | Host PostgreSQL có thể truy cập từ backend |
| `DB_PORT` | Cổng PostgreSQL |
| `DB_NAME` | Database đã được tạo |
| `DB_USER` | Tài khoản PostgreSQL |
| `DB_PASSWORD` | Mật khẩu của tài khoản |

Datasource URL: `jdbc:postgresql://${DB_HOST}:${DB_PORT}/${DB_NAME}`.
Không có credentials mặc định. Hibernate `ddl-auto: none` không tạo hoặc sửa
schema; `open-in-view: false` giới hạn persistence ngoài HTTP rendering.

Ví dụ PowerShell nhập cấu hình mà không ghi mật khẩu vào source hoặc command
history:

Adapter Workflow #25 còn cần `DXOS_WORKFLOW_SCHEMA`, datasource có `currentSchema`
đúng schema riêng và `SPRING_FLYWAY_ENABLED=false` ở runtime. Schema/migrations phải
có trước khi boot; xem **Chạy backend local từ clone mới** hoặc **Kết nối Supabase
PostgreSQL mặc định cho Issue #25** bên dưới. Login runtime riêng là yêu cầu cho
triển khai lâu dài, không phải prerequisite của bước kết nối Supabase ban đầu.

```powershell
$env:DB_HOST = Read-Host 'DB_HOST (theo môi trường đã provision; Issue #3 cũ là lịch sử)'
$env:DB_PORT = Read-Host 'DB_PORT'
$env:DB_NAME = Read-Host 'DB_NAME'
$env:DB_USER = Read-Host 'DB_USER'
$env:DB_PASSWORD = Read-Host 'DB_PASSWORD' -MaskInput
.\gradlew.bat bootRun
```

`-MaskInput` cần PowerShell 7.1 trở lên. Với Windows PowerShell 5.1, nhập
mật khẩu bằng cách sau thay cho dòng `DB_PASSWORD` bên trên:

```powershell
$dbCredential = Get-Credential -UserName $env:DB_USER -Message 'PostgreSQL credentials'
$env:DB_PASSWORD = $dbCredential.GetNetworkCredential().Password
.\gradlew.bat bootRun
```

Cũng có thể chạy JAR đã build, với cùng các biến môi trường:

```powershell
java -jar .\build\libs\dxos-backend-0.1.0.jar
```

Spring Boot không tự đọc file `.env`. Nếu dùng file này qua công cụ local,
không commit nó. `.gitignore` loại trừ `.env`, build output, Gradle cache,
IDE metadata và file tạm. Sau khi dừng ứng dụng, có thể xóa mật khẩu khỏi
process PowerShell:

```powershell
Remove-Item Env:DB_PASSWORD
```

## Health API

Sau khi ứng dụng khởi động, từ cửa sổ PowerShell khác:

```powershell
Invoke-RestMethod -Uri 'http://localhost:8080/api/v1/health'
```

`GET /api/v1/health` trả HTTP 200 với JSON `{"status":"UP"}`. Controller
không truy vấn database, không có logic nghiệp vụ hoặc phụ thuộc module
Helpdesk/Workflow. Đây là kiểm tra HTTP của ứng dụng, không chứng minh
PostgreSQL khả dụng. Toàn bộ ứng dụng vẫn cần cấu hình và kết nối PostgreSQL
để backend khởi động.

Actuator chỉ expose `/actuator/health` qua HTTP, không hiển thị details hoặc
components và không expose endpoint qua JMX. Health tổng hợp của Actuator
có thể kiểm tra database và trả trạng thái khác health API tùy tình trạng
PostgreSQL. Không expose `env`, `beans`, `metrics` hoặc endpoint quản trị khác.

## Legacy Request prototype (removed in R25)

The historical `/api/v1/requests/*` routes and `com.tricore.dxos.request` JPA prototype are no longer registered or compiled. The supported Helpdesk Application API is `/api/v1/mvp/requests` (see the Helpdesk integration documentation). The historic Flyway V1/V2 scripts and existing tables remain in the migration history to preserve `flyway validate` on databases already initialized with v0.1.0. Removing these historical objects is outside R25.

## Helpdesk Application API (`it-helpdesk@1`)

The supported application entry point is `/api/v1/mvp/requests` when `dxos.helpdesk.enabled=true`. The workflow is:

`SUBMITTED → TRIAGED → IN_PROGRESS → RESOLVED → CONFIRMED`

Assignment is not a Workflow state: `POST /api/v1/mvp/requests/{id}/assign` records the assignee and increments `assignment_version` (guarded by `expectedAssignmentVersion`) while the request is `TRIAGED`; `POST /api/v1/mvp/requests/{id}/start` performs the `start_work` transition to `IN_PROGRESS`.

`CONFIRMED` is terminal; there is **no** `/close` route or `CLOSED` state in the Helpdesk workflow.

| Method and route | Purpose |
| --- | --- |
| `POST /api/v1/mvp/requests` | Create a request with `title`, `description`, and `requestType: "IT_HELPDESK"` |
| `GET /api/v1/mvp/requests` | List authorized requests (cursor pagination) |
| `GET /api/v1/mvp/requests/{id}` | Read a request visible to the verified caller |
| `GET /api/v1/mvp/requests/{id}/history` | Read Workflow transition history |
| `POST /api/v1/mvp/requests/{id}/triage` | Triage, with `expectedVersion` |
| `POST /api/v1/mvp/requests/{id}/assign` | Assign, with `assigneeId` and `expectedAssignmentVersion` |
| `POST /api/v1/mvp/requests/{id}/start` | Start work, with `expectedVersion` |
| `POST /api/v1/mvp/requests/{id}/resolve` | Resolve, with `expectedVersion` and `resolution` |
| `POST /api/v1/mvp/requests/{id}/confirm` | Requester confirmation, with `expectedVersion` |

Helpdesk enforces verified identity, tenant/resource authorization, eligibility and versions before committing business and Workflow changes. It uses its own `helpdesk_requests` data and Workflow tables in a deliberately provisioned PostgreSQL schema, **not** the retired Request JPA entity/repository. Consult `HelpdeskController`, `HelpdeskService`, and `HelpdeskHttpPostgresTest` for the exact contract and tested behavior.

## Workflow PostgreSQL adapter (Issue #25)

Nghiệm thu cloud ngày 2026-10-15 theo owner: V3/V4 COMMITTED_PASS,
checksum/inventory/seed PASS; smoke `cloud-20261015-01` COMMITTED_PASS,
precheck/postcheck/fresh-JVM persistence PASS, 2 instances / 4 history, exit 0.
Giữ dữ liệu thử; không chạy lại bootstrap, Flyway hoặc smoke. Các hướng dẫn cloud
phía dưới là hồ sơ đã thực thi, không tự cấp quyền cho lượt ghi mới. `postgres`
chỉ là ngoại lệ development một lần; deployment lâu dài cần runtime ít quyền.

Adapter JDBC ở `infrastructure.workflow` cung cấp một bean `WorkflowPersistencePort`
và một `WorkflowRuntime` dùng `Clock.systemUTC()`. Core và Workflow HTTP không thay
đổi; controller Workflow vẫn không được đăng ký production. Adapter không thực
hiện resource ACL, không giải quyết revocation/TOCTOU của Issue #23.

V3 tạo bảng riêng cho definitions, instances và history; V1/V2 giữ nguyên. V4
seed hai definition độc lập: `document-review@1` và `incident-resolution@1`.
Import definition bằng `PostgresWorkflowPersistence.provisionDefinition` với
datasource của provisioner: cùng key/cùng nội dung là idempotent, khác nội dung
bị từ chối. Toàn bộ states/transitions phải được insert trong cùng transaction
với definition mới; database chặn bổ sung, UPDATE, DELETE và TRUNCATE sau commit.
Thay đổi nội dung cần version mới. Table owner/superuser vẫn có thể vô hiệu hóa
trigger, vì vậy runtime login phải khác owner và không có quyền DDL/provisioning.

Thời gian lưu lossless bằng epoch seconds BIGINT và nanos INTEGER, nhận toàn bộ
miền `Instant.MIN..MAX` của Java, kể cả nanos không chia hết cho 1000. Không cần
clock làm tròn. Database phải có `fsync=on`, `full_page_writes=on`; mỗi write đặt
`SET LOCAL synchronous_commit=on`, khóa instance và chỉ trả success sau COMMIT
được xác nhận. Hạ tầng lưu trữ của PostgreSQL phải đáp ứng durability.

Lỗi trước COMMIT có rollback được xác nhận là `OPERATION_FAILURE`. Mất phản hồi
COMMIT hoặc không xác nhận được rollback là `COMMIT_OUTCOME_UNKNOWN`; adapter
không retry. Một rollback sau lỗi COMMIT không chứng minh write trước đó chưa
commit. Đọc authoritative instance/history để reconcile, nhưng hai lần đọc
riêng không dùng chung snapshot, dữ liệu cũ hoặc chưa có khi transaction đang
chưa kết thúc không chứng minh rollback hay xác định writer thắng.

### Cấu hình schema bắt buộc

`DXOS_WORKFLOW_SCHEMA` (property `dxos.workflow.schema`) phải là identifier lowercase
`[a-z][a-z0-9_]{0,62}`, không phải public/extensions/information_schema/pg_*.
Không có schema mặc định. Schema phải được provision riêng.
Mỗi connection phải có currentSchema/search_path bắt đầu bằng schema này, chỉ theo
sau bởi pg_catalog/pg_temp; JDBC URL không được ghi đè sang schema khác.
SQL adapter và toàn bộ Workflow objects V3/V4 dùng schema-qualified identifiers.
Flyway phải đi qua `WorkflowMigrations.configure` hoặc Spring customizer:
defaultSchema/schemas cùng một schema, createSchemas=false, transaction bắt buộc,
không clean/repair/baseline. Flyway native defaultSchema placeholder được chèn sau
khi Java đã xác thực identifier; không chạy SQL bằng cơ chế thay placeholder tùy ý.

### PostgreSQL local có thể tái lập

Cách kiểm tra đầy đủ từ source, không cần Supabase, WARP hoặc credentials nhóm:

```powershell
# Từ backend/, với Docker đang chạy và JDK 21 trên PATH:
powershell.exe -NoProfile -File ..\scripts\workflow-verify-local.ps1
if ($LASTEXITCODE -ne 0) { throw 'Local verification failed' }
```

Launcher dùng PostgreSQL 17.11 trên cổng loopback ngẫu nhiên, sinh CA đúng/sai
bằng OpenSSL của Git for Windows và bật toàn bộ TLS/event-trigger/audit fixtures.
Credentials chỉ ở environment/stdin; private keys nằm ngoài Git trong thư mục
current user/SYSTEM. Nó chạy `test build`, kiểm tra XML không có FAIL/SKIP và đủ
chín integration suites, rồi dừng/xóa container của nó và dọn certificates.
Đây là database disposable; dùng Compose bên dưới khi cần giữ dữ liệu local.

Cần Docker và JDK 21. Compose `infra/compose.workflow-postgres.yml` chạy PostgreSQL
17.11 trên loopback 55425, giữ named volume riêng cho major 17; không dùng lại volume 16.
Password chỉ cấp qua môi trường bảo mật,
không ghi vào source/command line. Giữ password cũ khi dùng lại volume.

Các biến integration: WORKFLOW_TEST_JDBC_URL, WORKFLOW_TEST_DB_USER,
WORKFLOW_TEST_DB_PASSWORD và tùy chọn WORKFLOW_TEST_MIGRATION_USER,
WORKFLOW_TEST_MIGRATION_PASSWORD. Test URL phải là loopback với port/database,
không có query; fixtures từ chối URL cloud. Runtime riêng cần login, không superuser,
CREATEDB, CREATEROLE hoặc schema ownership; migrator local tạo/xóa schema test.
Isolation fixture tạo API roles giả trong database disposable, sentinel trong public,
kiểm tra ACL bên ngoài, rồi xóa đúng objects do fixture tạo.

Từ backend, với môi trường local đã cấu hình:

```powershell
$env:WORKFLOW_EVENT_GUARD_LOCAL_DISPOSABLE = 'true'
.\gradlew.bat workflowIntegrationTest --no-daemon
.\gradlew.bat test build --no-daemon
```

Integration gồm regression adapter V1–V4 và isolation suite V3/V4 độc lập.
Không chạy các suite này trên shared Supabase. Không có database thì task test skip
integration, còn workflowIntegrationTest fail vì thiếu biến môi trường.

### Chạy backend local từ clone mới

Các lệnh dưới đây chỉ dùng database loopback do Compose tạo. Không dùng tài khoản
hoặc endpoint Supabase. Mỗi volume mới chỉ provision role/schema một lần; khi dùng
lại volume, giữ mật khẩu cũ và đọc trạng thái trước, không chạy lại `migrate` nếu
schema đã có Flyway history.

```powershell
# Từ backend/:
$localDb = Get-Credential -UserName workflow_test -Message 'Choose the local PostgreSQL owner password'
$env:WORKFLOW_LOCAL_DB_PASSWORD = $localDb.GetNetworkCredential().Password
docker compose -f ..\infra\compose.workflow-postgres.yml up -d --wait
docker compose -f ..\infra\compose.workflow-postgres.yml exec workflow-postgres psql -U workflow_test -d workflow_test
```

Trong psql của volume local mới, nhập mật khẩu runtime ở prompt ẩn:

```text
CREATE ROLE workflow_runtime LOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
\password workflow_runtime
CREATE SCHEMA dxos_wf25_smoke_01 AUTHORIZATION workflow_test;
GRANT USAGE ON SCHEMA dxos_wf25_smoke_01 TO workflow_runtime;
\q
```

Chạy V3/V4 riêng bằng owner local, rồi cấp quyền runtime:

```powershell
$runtimeDb = Get-Credential -UserName workflow_runtime -Message 'Enter the local runtime password'
$env:WORKFLOW_EVENT_GUARD_LOCAL_DISPOSABLE = 'true'
$env:WORKFLOW_SMOKE_LOCAL_DISPOSABLE = 'true'
$env:WORKFLOW_SMOKE_JDBC_URL = 'jdbc:postgresql://127.0.0.1:55425/workflow_test'
$env:WORKFLOW_SMOKE_MIGRATOR_USER = 'workflow_test'
$env:WORKFLOW_SMOKE_MIGRATOR_PASSWORD = $env:WORKFLOW_LOCAL_DB_PASSWORD
$env:WORKFLOW_SMOKE_RUNTIME_USER = 'workflow_runtime'
$env:WORKFLOW_SMOKE_RUNTIME_PASSWORD = $runtimeDb.GetNetworkCredential().Password
$env:WORKFLOW_SMOKE_BUNDLE = Join-Path (Get-Location) 'build\workflow-smoke-bundle'
.\gradlew.bat workflowSmokeBundle workflowSmoke --args=migrate --no-daemon
if ($LASTEXITCODE -ne 0) { throw 'Local migration failed' }
docker compose -f ..\infra\compose.workflow-postgres.yml exec workflow-postgres psql -U workflow_test -d workflow_test
```

Trong psql local:

```sql
GRANT SELECT ON dxos_wf25_smoke_01.workflow_definitions,
  dxos_wf25_smoke_01.workflow_definition_states, dxos_wf25_smoke_01.workflow_definition_transitions,
  dxos_wf25_smoke_01.workflow_instances, dxos_wf25_smoke_01.workflow_transition_history TO workflow_runtime;
GRANT INSERT ON dxos_wf25_smoke_01.workflow_instances,
  dxos_wf25_smoke_01.workflow_transition_history TO workflow_runtime;
GRANT UPDATE (current_state, lifecycle, runtime_version, updated_at_seconds, updated_at_nanos)
  ON dxos_wf25_smoke_01.workflow_instances TO workflow_runtime;
```

Sau `\q`, kiểm tra dữ liệu và boot với login runtime:

```powershell
.\gradlew.bat workflowSmoke --args="smoke local-first-run" --no-daemon
if ($LASTEXITCODE -ne 0) { throw 'Local smoke failed' }
.\gradlew.bat workflowSmoke --args="read local-first-run" --no-daemon
if ($LASTEXITCODE -ne 0) { throw 'New-process read failed' }
$env:DB_HOST = '127.0.0.1'
$env:DB_PORT = '55425'
$env:DB_NAME = 'workflow_test'
$env:DB_USER = 'workflow_runtime'
$env:DB_PASSWORD = $runtimeDb.GetNetworkCredential().Password
$env:DXOS_WORKFLOW_SCHEMA = 'dxos_wf25_smoke_01'
$env:SPRING_DATASOURCE_URL = 'jdbc:postgresql://127.0.0.1:55425/workflow_test?currentSchema=dxos_wf25_smoke_01,pg_catalog,pg_temp'
$env:SPRING_FLYWAY_ENABLED = 'false'
.\gradlew.bat bootRun
```

Health ở `/api/v1/health`. Workflow HTTP controller vẫn chưa đăng ký production
cho đến khi verified principal/authorization được tích hợp; #25 cung cấp bean
adapter/runtime và constructor injection, không mở route trước gate bảo mật đó.
V3/V4 không tạo Request tables; demo Request vẫn cần V1/V2 của quy trình riêng.
Sau khi dừng backend, `docker compose ... down` giữ named volume; tránh `down -v`
khi kiểm tra restart. Đọc lại cùng run-id từ process mới để xác minh persistence.
Không chạy `smoke` lại với run-id cũ: runner từ chối replay trước write.

### Kết nối Supabase PostgreSQL mặc định cho Issue #25

Theo [Issue #25 cập nhật ngày 2026-10-14](https://github.com/tricore-opentrix/opentrix/issues/25),
dùng Direct Connection của project như pgAdmin: `db.<project-ref>.supabase.co`, port
`5432`, database `postgres`, tài khoản `postgres` và mật khẩu database hiện có.
Máy phát triển cần IPv6; PostgreSQL local ở trên vẫn chạy độc lập với Supabase/WARP.
Không chạy Stage 1A/1B, không cấp SCRAM/LOGIN và không đổi hai custom roles đang
`NOLOGIN`. Các hồ sơ đó là optional hardening cho triển khai lâu dài.

Trong phiên PowerShell đã có `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
và `PGSSLROOTCERT` (CA tin cậy lấy từ project), kiểm tra kết nối chỉ đọc từ repo root:

```powershell
powershell.exe -NoProfile -File .\scripts\workflow-read-only-preflight.ps1
if ($LASTEXITCODE -ne 0) { throw 'Read-only connection check failed' }
```

Preflight ép JDBC `sslmode=verify-full`, CA, timeout và transaction READ ONLY, rồi
rollback/close. Không boot Spring, chạy Flyway hay tạo role/schema. Không đưa secrets
vào URL, args, source, command history hoặc báo cáo; chỉ nhập bằng secure prompt hay
secret environment hiện có. Kết quả kiểm tra không phải phê duyệt thao tác ghi.

Cấu hình Spring dùng cùng `DB_*`; URL phải bổ sung schema và TLS trước khi sử dụng:

```powershell
$env:DXOS_WORKFLOW_SCHEMA = 'dxos_wf25_smoke_01'
$caPath = [Uri]::EscapeDataString($env:PGSSLROOTCERT)
$env:SPRING_DATASOURCE_URL = "jdbc:postgresql://$($env:DB_HOST):$($env:DB_PORT)/$($env:DB_NAME)?currentSchema=$($env:DXOS_WORKFLOW_SCHEMA),pg_catalog,pg_temp&sslmode=verify-full&sslrootcert=$caPath"
$env:SPRING_FLYWAY_ENABLED = 'false'
```

Đây chỉ là cấu hình chuẩn bị, chưa phải lệnh boot/migrate. Cloud writes cần owner
phê duyệt riêng schema, chỉ bundle V3/V4, seed và bounded smoke/restart/read, kèm
postchecks và recovery; không chạy V1/V2 hoặc clean/repair/baseline trên shared DB.
Không retry khi COMMIT chưa rõ kết quả. Giữ kiểm tra schema isolation, manifest/event
triggers và quyền API/PUBLIC hiện có; không tắt guard để kết nối dễ hơn.

`postgres` chỉ là ngoại lệ kiểm chứng một lần được phê duyệt, không dùng cho backend
chạy lâu dài hoặc frontend. Phải có runtime identity tối thiểu trước triển khai
persistent/shared production. `WorkflowSmokeRunner` vẫn yêu cầu runtime khác owner;
entrypoint production và constructor mặc định không đọc các cờ development.
Cloud migration/smoke/restart DoD còn pending, không thay bằng local PASS.

### Development integration một lần bằng postgres

Task riêng `workflowDevelopmentSmoke` gọi `WorkflowDevelopmentSmokeRunner`, không
được đăng ký Spring bean hay chạy từ bootRun/build hoặc cấu hình production.
Nó tái sử dụng bounded smoke/check/restart scenario, chỉ mở ngoại lệ owner/runtime
cho chế độ development đã opt-in. Runner production giữ kiểm tra non-owner và
least-privilege hiện có. Không tự tạo schema, roles, GRANT, cleanup hoặc retry.

Yêu cầu đồng thời: argument `--development-integration`, opt-in có giá trị chính xác,
schema duy nhất `dxos_wf25_smoke_01`, DB_USER/DB_NAME là `postgres`, Direct endpoint
đúng project, CA và verify-full. Mỗi connection xác minh session_user=current_user
postgres, backend TLS, schema owner postgres, không schema ACL cho PUBLIC/roles
khác hoặc quyền hiệu lực của API roles, không relation do owner khác sở hữu.
Guard/manifest, bundle V3/V4 pin, durability, default ACL, history/checksums và
inventory checks vẫn hoạt động. Chế độ check/read không có quyền gọi migrate/smoke.

Schema đã bootstrap thành công theo report owner; không chạy lại. Sau preflight
fresh, chỉ chuẩn bị/check từ repo root (chưa đặt write approval):

```powershell
# DB_* và PGSSLROOTCERT đã có trong secret environment; không in chúng.
$env:WORKFLOW_DEV_INTEGRATION_OPT_IN = 'issue-25-postgres-development-only'
$env:WORKFLOW_DEV_APPROVED_SCHEMA = 'dxos_wf25_smoke_01'
$env:WORKFLOW_DEV_PROJECT_REF = $env:DB_HOST.Split('.')[1]
Remove-Item Env:WORKFLOW_DEV_WRITE_APPROVAL -ErrorAction SilentlyContinue
Push-Location backend
.\gradlew.bat workflowSmokeBundle --no-daemon
if ($LASTEXITCODE -ne 0) { throw 'Bundle preparation failed' }
$env:WORKFLOW_DEV_BUNDLE = (Resolve-Path 'build/workflow-smoke-bundle').Path
.\gradlew.bat workflowDevelopmentSmoke --args="--development-integration check" --no-daemon
Pop-Location
```

Không đặt `WORKFLOW_DEV_LOCAL_DISPOSABLE`, `WF25_DISPOSABLE_TEST` hoặc
`WORKFLOW_EVENT_GUARD_LOCAL_DISPOSABLE` trên cloud, kể cả giá trị false. Chế độ local
đòi cả ba cờ fixture cùng marker `dxos.wf25_disposable=on` của login postgres,
loopback và TLS verify-full; cờ local không thể áp dụng cho endpoint Supabase.

**Owner đã phê duyệt chỉ V3/V4 đã pin sau fresh prechecks PASS.**
Dùng launcher một mục đích ở phần dưới; không chạy trực tiếp ví dụ Gradle để bỏ qua
audit/report. Approval không bao gồm smoke, bootstrap hoặc recovery.
Entry point nội bộ của launcher là mode migration riêng:

~~~powershell
# Cần explicit WORKFLOW_DEV_WRITE_APPROVAL khớp schema sau approval, không đặt trước.
# Chạy từ backend; credentials/CA chỉ từ secret environment.
.\gradlew.bat workflowDevelopmentSmoke --args="--development-integration migrate" --offline --no-daemon --no-configuration-cache --quiet
~~~

Clear write approval trong finally, kể cả command lỗi. Dừng sau migrate để audit
qua connection mới READ ONLY. Smoke/read/restart là bước có approval riêng;
không chạy smoke cùng batch migrate hoặc suy ra approval từ schema bootstrap.

Schema phải đã tồn tại/rỗng và owner postgres; thao tác bootstrap schema là approval
riêng, không do runner thực hiện. Migrate chỉ V3/V4: 5 tables + Flyway history,
2 functions/9 explicit triggers (6 row, 3 statement), seed 2 definitions/7 states/5 transitions, 2 success
history rows/checksums. Smoke tạo tối đa 2 instances/4 history rows cho run-id mới,
race activation version 0/transition, kiểm tra Instant nanos và replay; read dùng
process/JVM mới không ghi. Dữ liệu smoke giữ lại. Đây là durability qua JVM mới;
cloud restart Spring bằng production bean còn cần evidence riêng.

Nếu V3 đã commit/V4 lỗi hoặc `WORKFLOW_DEVELOPMENT_FAIL_COMMIT_OUTCOME_UNKNOWN`,
dừng, đọc catalog/history/instances bằng connection mới và xin recovery approval;
không rerun tự động, clean/repair/baseline hay xóa dữ liệu đã commit. Tài khoản admin
vẫn có thể tác động ngoài schema; guard thu hẹp phạm vi tool, không sandbox quyền
admin hoặc loại bỏ privileged concurrent DDL.

### Lệnh preflight Supabase chỉ đọc trước cloud migrations

**Cập nhật sau migrations:** owner đã xác nhận V3/V4 `COMMITTED_PASS`, checksum,
inventory, seed và postcommit audit PASS, `MIGRATIONS_EXIT=0`. Các lệnh migration
trên/dưới là lịch sử; **không chạy lại bootstrap hoặc Flyway**.
Owner cũng xác nhận cloud smoke `cloud-20261015-01` COMMITTED_PASS, precheck,
postcheck và fresh-JVM persistence PASS, 2 instances / 4 history, exit 0.
Không chạy lại cloud smoke; giữ nguyên dữ liệu thử. Kế hoạch, dữ liệu và recovery ở phần “Cloud smoke sau migrations”
trong evidence lịch sử của Issue #25; đường dẫn tài liệu cũ chưa có trong phiên bản này.

Từ repo root, Direct host/CA/password đã được cấp qua môi trường bảo mật:

```powershell
$env:DB_PORT = '5432'
$env:DB_NAME = 'postgres'
$env:DB_USER = 'postgres'
powershell.exe -NoProfile -File .\scripts\workflow-read-only-preflight.ps1
if ($LASTEXITCODE -ne 0) { throw 'Direct read-only preflight failed' }
powershell.exe -NoProfile -File .\scripts\workflow-live-guard.ps1
if ($LASTEXITCODE -ne 0) { throw 'Reviewed catalog guard failed' }
```

Kiểm tra dự kiến: Direct IPv6, client verify-full/CA, backend SSL=true,
transaction_read_only=on, session_user=current_user=postgres, đúng database;
schema absent hoặc owner/ACL/inventory đúng kế hoạch; hai custom roles vẫn NOLOGIN;
không drift ngoài phạm vi, durability/settings và manifest/bundle pin khớp.
Owner phải kiểm tra thêm Dashboard API exposed schemas không chứa schema test.
`LIVE_GUARD=PASS` chỉ xác minh catalog; WRITE_READINESS=BLOCKED không tự cấp approval.
Target hiện đã bootstrap: nếu preflight fresh báo ABSENT, dừng và báo sai lệch,
không chạy lại bootstrap. Dev check phải trả EMPTY trước migration. Không chạy Stage 1A/1B hoặc thay credentials/custom roles.

### Schema Bootstrap đã hoàn tất — không chạy lại

Owner báo SCHEMA_BOOTSTRAP=COMMITTED_PASS, POSTCOMMIT_AUDIT=PASS,
SCHEMA_OWNER=postgres, SCHEMA_EMPTY=YES, FLYWAY_HISTORY=ABSENT,
OTHER_CLOUD_WRITES=NONE, BOOTSTRAP_EXIT=0.
Đây là evidence owner cung cấp; Codex không thực thi lại cloud.
Không chạy workflow-schema-bootstrap.ps1 hoặc CREATE SCHEMA lại.

V3/V4 và cloud smoke đã hoàn tất theo owner report. Phần
thực thi Flyway V3/V4 (xem issue và bằng chứng kiểm thử liên quan tới #25)
là hồ sơ lịch sử; không phải bước tiếp theo và không chạy lại.
Launcher khóa đúng Direct endpoint và schema; tự dừng nếu precheck FAIL.
Dùng Direct db.zsfctpnitkdztlfhzqgw.supabase.co:5432/postgres, tài khoản postgres,
TLS verify-full và CA/credentials từ secret environment. Precheck fresh phải xác
nhận schema PRESENT/rỗng/owner postgres, guard/hash không drift; không dùng
điều kiện ABSENT từ kế hoạch bootstrap lịch sử.

Approval migration phải gồm V3/V4 pin, Flyway history, V4 seed và V3 object ACL
revocations chỉ trong target; không gồm smoke, role changes hoặc recovery.
Không gọi smoke trong cùng batch migrate. Migrate thất bại hoặc mất ACK:
dừng, clear write approval trong finally, reconcile qua connection READ ONLY mới;
không retry/clean/repair/baseline/DROP. Postcheck đầy đủ trước khi báo cloud PASS.

### Launcher V3/V4 lịch sử — đã hoàn tất, không chạy lại

Lệnh lưu để review việc đã thực thi; không chạy trong lúc chuẩn bị PR:

~~~powershell
& 'C:\Users\Admin\AppData\Local\codex-with-chatgpt\worktrees\dxos-data-postgres-adapter\scripts\workflow-approved-migrations.ps1' -ExecuteApprovedMigrations
~~~

Mặc định dùng PGSSLROOTCERT; nếu chưa có, hỏi đường dẫn CA. Password lấy từ
DB_PASSWORD đã có hoặc prompt ẩn. Launcher yêu cầu JDK 21, WARP Connected và Direct
host có IPv6; không tự bật/sửa WARP, CA hay endpoint sai. Environment cũ được khôi
phục trong finally; Gradle offline, không configuration cache, không log exception.
Chỉ in report allowlist đầy đủ; child mất/thiếu report sau handoff là COMMIT_UNKNOWN.

Java task workflowApprovedMigration chỉ chạy V3/V4 đã pin, createSchemas=false,
không baseline/repair/clean/retry/smoke. Precheck READ ONLY xác minh schema rỗng
owner postgres, history absent, TLS verify-full/backend SSL, PG17.11, NOLOGIN custom
roles, manifest raw hash và migration SHA/CRC. Guard lặp lại khi mở connection.
Sau migrate dùng connection mới READ ONLY: history, exact catalog fingerprint,
seed/0 instances, schema ACL/owner và outside catalog/roles/membership snapshot.
Fingerprint bao gồm columns/defaults/NOT NULL, indexes, constraints, function
definitions/ACL, explicit/internal triggers và types; không chỉ so counts.
Chỉ exit 0 khi COMMITTED_PASS + audit/inventory/seed PASS; lỗi thì dừng, không retry.

Giữ COMMIT_UNKNOWN khi mất ACK dù audit tìm thấy dữ liệu; history và seed được
đối chiếu riêng, không suy ra thành công chỉ từ một bên. V3 đã commit/V4 lỗi:
PARTIAL_COMMIT, giữ nguyên để owner duyệt recovery. Catalog drift hoặc fresh audit
không đọc được không được claim OTHER_CLOUD_WRITES=NONE. Mọi trường hợp đều dừng
sau migration/audit, NEXT_APPROVAL_REQUIRED=YES cho cloud smoke.

### Optional hardening — Runtime Privilege Audit READ-ONLY trên Supabase

Từ root worktree, với JDK 21 và các biến DB_HOST, DB_PORT, DB_NAME, DB_USER,
DB_PASSWORD, PGSSLROOTCERT đã có trong phiên PowerShell:

```powershell
powershell.exe -NoProfile -File .\scripts\workflow-runtime-privilege-audit.ps1
$LASTEXITCODE
```

Launcher hỗ trợ Direct Connection hoặc session pooler, port 5432; ép verify-full/CA,
search_path pg_catalog,pg_temp và transaction_read_only=on. SQL audit được pin SHA-256;
thay đổi SQL cần review rồi cập nhật pin. Không chạy Spring/Flyway/provisioning/smoke.
WORKFLOW_EVENT_GUARD_LOCAL_DISPOSABLE phải không được đặt, kể cả giá trị false.
Secrets chỉ được kế thừa qua environment; không truyền qua args, in hoặc ghi báo cáo.

AUDIT_REPORT chỉ có role names cố định, statuses, booleans/counts và số quyền true
theo role/privilege; không chứa host/database/object identifiers, function source,
passwords hay connection strings. NOT_PROVISIONED nghĩa là chưa có role, không phải
permission PASS. RUNTIME_PRIVILEGE_AUDIT=PASS chỉ xác nhận catalog audit hoàn tất,
rollback/close thành công; WRITE_READINESS vẫn BLOCKED và cần reviewer xét ACL/TLS.

### Optional hardening — SECURITY DEFINER metadata và private review

Chạy từ root repo trong phiên PowerShell đã giữ `DB_*` và `PGSSLROOTCERT`:

```powershell
powershell.exe -NoProfile -File .\scripts\workflow-security-definer-review.ps1
$LASTEXITCODE
```

Launcher riêng dùng JDBC `verify-full`, `pg_catalog,pg_temp`, transaction READ ONLY
và SQL được pin SHA-256. Metadata giữ schema/signature/owner, EXECUTE/schema ACL,
search_path của function, quyền runtime nullable, membership, dependencies và
definition/configuration fingerprints. Không trả bodies hoặc các GUC khác.
`NOT_PROVISIONED` giữ quyền runtime là `null`, không phải `false`.

Chỉ sau khi metadata hợp lệ đã được xem xét, dùng đường dẫn `SHAREABLE_METADATA`
để lấy bodies/configuration vào một thư mục bảo vệ mới ngoài Git:

```powershell
powershell.exe -NoProfile -File .\scripts\workflow-security-definer-review.ps1 -MetadataFile '<SHAREABLE_METADATA>'
```

Baseline phải ở thư mục chỉ current user/SYSTEM truy cập; catalog drift, SQL pin
sai, rollback/close lỗi hoặc cấu hình TLS sai đều fail closed. Chỉ chia sẻ
`shareable-metadata.json`; không gửi `private-function-review.json` hay credentials
vào chat/Git. Helper tìm thấy khi review body cần capture metadata mới bằng
`-HelperSignature 'schema.helper(argument_types)'`, rồi private capture từ baseline
mới đó. Catalog dependencies không đầy đủ cho dynamic SQL/string-body routines.
Mọi routine bắt đầu `NEEDS_REVIEW`; capture thành công không tự cấp PASS bảo mật,
chấp nhận PUBLIC TEMP, phê duyệt roles hoặc giải quyết TLS backend-hop.

### Optional hardening — runner dùng migrator/runtime riêng

`workflowSmokeBundle` chỉ copy V3/V4. Runner kiểm tra chính xác hai filenames và
SHA-256 được pin trong `workflow-event-trigger-manifest.json` (chuẩn hóa CRLF thành LF), cùng Flyway checksums/history. Không nạp V1/V2.
Schema cố định: dxos_wf25_smoke_01; history đặt trong cùng schema.
Runner không boot Spring, không tự tạo schema/role, không GRANT, không cleanup,
DROP/TRUNCATE/DELETE hoặc retry khi kết quả commit chưa xác định.

Biến độc lập: WORKFLOW_SMOKE_JDBC_URL (không chứa user/password),
WORKFLOW_SMOKE_PROJECT_REF (bắt buộc cho cloud),
WORKFLOW_SMOKE_CA_CERT, WORKFLOW_SMOKE_MIGRATOR_USER/PASSWORD,
WORKFLOW_SMOKE_RUNTIME_USER/PASSWORD, WORKFLOW_SMOKE_BUNDLE (đường dẫn bundle);
WORKFLOW_SMOKE_RUN_ID dùng cho smoke/read khi không truyền run-id qua args.
Cấp secrets bằng secure environment bên ngoài chat. Cloud chỉ chấp nhận Direct
db.<project-ref>.supabase.co:5432/postgres với đúng project ref, CA file tồn tại và TLS verify-full;
hai username là tên role PostgreSQL trực tiếp, không có hậu tố project ref.
URL cloud không có query/fragment; currentSchema và TLS chỉ do runner đặt. Không có CA thì dừng.
WORKFLOW_SMOKE_LOCAL_DISPOSABLE=true chỉ dùng loopback, không thể hạ TLS cloud.

Migrator là owner của schema riêng, có USAGE/CREATE trong schema và USAGE plpgsql.
Runtime khác owner, không membership owner, không quyền CREATE schema, không
superuser/CREATEROLE/CREATEDB/BYPASSRLS. Sau migration, operator cấp runtime:
USAGE schema, SELECT năm Workflow tables, INSERT instances/history, UPDATE chỉ
current_state/lifecycle/runtime_version/updated_at_seconds/updated_at_nanos của
instances. Không cấp DDL, provisioning definitions, DELETE hoặc TRUNCATE.
Không sửa default privileges, database privileges hay role membership.
Dùng postgres làm migrator tạo objects do postgres sở hữu; role mạnh có thể tắt
trigger/sửa history nên chỉ dùng cho bước migration đã duyệt, không dùng runtime.
Default privileges tùy chỉnh hoặc event triggers lệch manifest khiến runner dừng;
không tự sửa hoặc tắt triggers. Manifest khóa đúng sáu triggers, function/config hashes,
owners/ACL và hai helper internal đã review. OID capture chỉ là evidence; helper được
resolve live theo signature. Remote chỉ nhận bundle filesystem V3/V4 và PostgreSQL 17.11.
Profile local cần `WORKFLOW_EVENT_GUARD_LOCAL_DISPOSABLE=true`, loopback và inventory
event triggers hoàn toàn trống; flag không cho phép bỏ qua trigger lạ hoặc cloud.
Guard đọc hashes/config keys, không tải private bodies/config values; collector riêng
vẫn giữ private capture ngoài Git. Native binary là giả định tin cậy provider, không
được attested bằng hash catalog. Các watcher được duyệt có thể gửi NOTIFY reload schema.
Kiểm tra live chạy trên mỗi connection, trước migration và trước từng migration;
bundle được kiểm tra lại cả tại connection boundary. Chúng thu hẹp TOCTOU, không
loại bỏ privileged concurrent DDL hay concurrent filesystem mutation.

```powershell
.\gradlew.bat workflowSmokeBundle --no-daemon
.\gradlew.bat workflowSmoke --args=check --no-daemon
# Các lệnh dưới đây CHỈ sau phê duyệt riêng và bootstrap role/schema phù hợp:
.\gradlew.bat workflowSmoke --args=migrate --no-daemon
# Operator cấp các quyền runtime tối thiểu đã duyệt, rồi:
.\gradlew.bat workflowSmoke --args="smoke unique-run-id" --no-daemon
.\gradlew.bat workflowSmoke --args="read unique-run-id" --no-daemon
```

check dùng read-only transactions, xác minh ownership/quyền, mode/durability,
không có event triggers/default privileges chưa review, schema trống hoặc đúng
sáu tables, bundle và migration history. migrate chỉ nhận schema đã tồn tại và trống.
smoke tạo hai instances có prefix issue25/run-id riêng, race activation version 0,
race transition, hoàn tất cả hai definitions, kiểm tra hai history/instance và
Instant nanos. Run-id đã dùng bị từ chối. read dùng JVM/connection mới kiểm tra
snapshots/history; không ghi. Sau lỗi/COMMIT_OUTCOME_UNKNOWN dừng và điều tra,
không tự chạy lại. Dữ liệu smoke được giữ lại.

## Phụ thuộc Issue #3 và giới hạn xác minh

> **[LỊCH SỬ — chỉ lưu trữ]** Issue #3 đã bị xóa và không còn là điều kiện của hướng dẫn hiện tại. Không suy ra việc xóa Issue nghĩa là công việc Docker/PostgreSQL đã hoàn thành. Phần dưới giữ nguyên làm ghi chép; thay bằng runbook cục bộ ở A5 và [../docs/DEVELOPMENT.md](../docs/DEVELOPMENT.md).

Issue #3 chịu trách nhiệm Docker/PostgreSQL cho phát triển: database, tài
khoản, credentials và host/port phù hợp. Issue #1 không tạo container,
schema nghiệp vụ hoặc cơ chế bỏ qua kết nối database.

Khi môi trường Issue #3 chưa khả dụng, có thể xác minh compilation, test MVC
và đóng gói JAR; chưa xác minh tích hợp PostgreSQL, toàn bộ startup với JPA,
hoặc HTTP health trên ứng dụng thực tế kết nối PostgreSQL.

Sau khi Issue #3 hoàn thành, cung cấp đủ biến `DB_*`, chạy `bootRun`, kiểm
tra startup, `/api/v1/health` và `/actuator/health` với PostgreSQL thực tế.

Kiểm chứng launcher V3/V4 (2026-10-15): full JDK21/PostgreSQL17.11 TLS disposable
752 PASS, 0 FAIL/SKIP, 9 integration suites, build PASS; bao gồm 38 tests mới.
Đây chưa là cloud execution; Codex thiếu credentials/CA và chờ owner chạy launcher.
