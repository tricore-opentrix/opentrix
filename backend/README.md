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

Bản README này được soạn **không** chạy build, test, database hay dịch vụ. Không có số liệu test mới. Các con số test/PASS trong [runbook lưu trữ lịch sử](legacy-workflow-runbook.md) là báo cáo theo lần chạy cũ, không phải kết quả của SHA hiện tại. Hướng dẫn vận hành cục bộ ở [Workflow local](docs/local-workflow-runbook.md) và [Helpdesk local](../scripts/README-helpdesk-local.md).

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
| Workflow | `DXOS_WORKFLOW_SCHEMA`, `currentSchema` khớp, `SPRING_FLYWAY_ENABLED=false` | [Workflow local](docs/local-workflow-runbook.md) |
| Helpdesk | `DXOS_HELPDESK_ENABLED`, `DXOS_HELPDESK_JDBCURL`, `DXOS_HELPDESK_USERNAME`, `DXOS_HELPDESK_PASSWORD`, `DXOS_HELPDESK_SCHEMA`, `DXOS_HELPDESK_TENANT` | `HelpdeskConfiguration`, runbook |

**Chỉ `DB_*` là chưa đủ**: `application.yml` còn yêu cầu ba biến OIDC. (Hướng dẫn cũ ghi "đủ năm biến `DB_*`" đã được hiệu chỉnh.) Hành vi khởi động khi issuer không truy cập được: **UNVERIFIED**.

Khởi động an toàn:

1. Chọn **một** lộ trình đã rà soát: [Workflow cục bộ](docs/local-workflow-runbook.md) hoặc [Helpdesk cục bộ](../scripts/README-helpdesk-local.md). Bản lưu trữ lịch sử **không phải** các bước thực thi hiện hành.
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

Helpdesk (`it-helpdesk@1`), chỉ khi `dxos.helpdesk.enabled=true`: `POST/GET /api/v1/mvp/requests`, `GET .../{id}`, `GET .../{id}/history`, `POST .../{id}/triage|assign|start|resolve|confirm`. Luồng: `SUBMITTED → TRIAGED → IN_PROGRESS → RESOLVED → CONFIRMED`; `assign` không phải trạng thái Workflow (tăng `assignment_version`); không có `/close` hoặc `CLOSED`. Chi tiết: [tài liệu API](../docs/API.md) và [runbook lịch sử](legacy-workflow-runbook.md) (chỉ tham khảo); mã: `HelpdeskController`, `HelpdeskService`.

Workflow runtime: `WorkflowRuntime` (Core) + `WorkflowPersistencePort`; adapter `PostgresWorkflowPersistence` (schema riêng, V3/V4, ghi lossless thời gian, `COMMIT_OUTCOME_UNKNOWN` không retry). Chi tiết lịch sử ở [Workflow archive](legacy-workflow-runbook.md); lộ trình hiện hành: [Workflow local](docs/local-workflow-runbook.md).

Guard hiện có (AS-IS, theo source):

| Guard | Hành vi |
|---|---|
| `SecurityConfig` | Mọi request phải xác thực trừ `/api/v1/health`; JWT resource server; stateless; CSRF tắt (Backend nhận Bearer token; CSRF thuộc BFF) |
| Validator JWT | Issuer, audience, loại access token, subject (chuỗi), hết hạn |
| `CurrentPrincipal.requireVerified()` | Helpdesk lấy danh tính từ principal đã xác minh, không từ tham số của caller |
| `HelpdeskConfiguration.requireDisposable` | Chỉ chấp nhận JDBC URL khớp toàn bộ mẫu `jdbc:postgresql://127.0.0.1:[0-9]{1,5}/helpdesk_disposable_[a-zA-Z0-9_]+`, user khớp toàn bộ `helpdesk_runtime_[a-z0-9_]+`, và `server.address` chính xác `127.0.0.1`. Regex chỉ kiểm cổng có 1–5 chữ số, **không** xác nhận cổng TCP hợp lệ hoặc DB đã thuộc quyền sở hữu người chạy |
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
| Workflow | `DXOS_WORKFLOW_SCHEMA`, matching `currentSchema`, `SPRING_FLYWAY_ENABLED=false` | [Local Workflow](docs/local-workflow-runbook.md) |
| Helpdesk | `DXOS_HELPDESK_ENABLED`, `DXOS_HELPDESK_JDBCURL`, `DXOS_HELPDESK_USERNAME`, `DXOS_HELPDESK_PASSWORD`, `DXOS_HELPDESK_SCHEMA`, `DXOS_HELPDESK_TENANT` | `HelpdeskConfiguration`, runbook |

**`DB_*` alone is not enough**: `application.yml` also requires the three OIDC variables. (The older "all five `DB_*` variables are enough" wording has been corrected.) Startup behavior when the issuer is unreachable: **UNVERIFIED**.

Safe startup:

1. Choose **one** reviewed path: [local Workflow](docs/local-workflow-runbook.md) or [local Helpdesk](../scripts/README-helpdesk-local.md). The historical archive is **not** the current execution guide.
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

Helpdesk (`it-helpdesk@1`), only when `dxos.helpdesk.enabled=true`: `POST/GET /api/v1/mvp/requests`, `GET .../{id}`, `GET .../{id}/history`, `POST .../{id}/triage|assign|start|resolve|confirm`. Flow: `SUBMITTED → TRIAGED → IN_PROGRESS → RESOLVED → CONFIRMED`; `assign` is not a Workflow state (it increments `assignment_version`); there is no `/close` or `CLOSED`. Details: [API documentation](../docs/API.md) and [historical archive](legacy-workflow-runbook.md) (reference only); source: `HelpdeskController`, `HelpdeskService`.

Workflow runtime: `WorkflowRuntime` (Core) + `WorkflowPersistencePort`; adapter `PostgresWorkflowPersistence` (dedicated schema, V3/V4, lossless time storage, no retry on `COMMIT_OUTCOME_UNKNOWN`). Historical details: [Workflow archive](legacy-workflow-runbook.md); current path: [local Workflow](docs/local-workflow-runbook.md).

Existing guards (AS-IS, per source):

| Guard | Behavior |
|---|---|
| `SecurityConfig` | Every request must be authenticated except `/api/v1/health`; JWT resource server; stateless; CSRF disabled (the Backend takes Bearer tokens; CSRF belongs to the BFF) |
| JWT validators | Issuer, audience, access-token type, subject (string), expiry |
| `CurrentPrincipal.requireVerified()` | Helpdesk takes identity from the verified principal, not from caller-supplied parameters |
| `HelpdeskConfiguration.requireDisposable` | Requires a full JDBC URL match: `jdbc:postgresql://127.0.0.1:[0-9]{1,5}/helpdesk_disposable_[a-zA-Z0-9_]+`; full user match: `helpdesk_runtime_[a-z0-9_]+`; exact `server.address`: `127.0.0.1`. The regex permits 1–5 port digits but **does not** validate TCP port range or prove database ownership |
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

## Tài liệu vận hành liên quan / Related operator docs

- **VI — hiện hành:** [Workflow local](docs/local-workflow-runbook.md) là checklist an toàn; [Helpdesk local](../scripts/README-helpdesk-local.md) là runbook riêng. **Lịch sử:** [phụ lục Workflow trước khi tách](legacy-workflow-runbook.md) giữ nguyên nội dung cũ để truy vết, **không chạy trực tiếp**.
- **EN — current:** [Local Workflow](docs/local-workflow-runbook.md) is the safety checklist; [local Helpdesk](../scripts/README-helpdesk-local.md) is a separate runbook. **Historical:** [preserved legacy appendix](legacy-workflow-runbook.md) retains old context and commands and is **not executable current guidance**.

