<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# Kiểm thử / Testing

[Docs](README.md) · [Architecture](ARCHITECTURE.md) · [API](API.md) · [Testing](TESTING.md) · [Integration](INTEGRATION.md)

[Tiếng Việt](#vi) · [English](#en)

> **Owner / Phụ trách:** @ngang02012007-crypto · **Issue:** [#196](https://github.com/tricore-opentrix/opentrix/issues/196), [#194](https://github.com/tricore-opentrix/opentrix/issues/194) · **Trạng thái / Status:** Đã review — merge ở #200 / Reviewed — merged in #200
>
> **Source baseline / Mốc source:** [832c75fc3164cf170eed3bb8f1e380d24dd65aba](https://github.com/tricore-opentrix/opentrix/commit/832c75fc3164cf170eed3bb8f1e380d24dd65aba). **Phase 2 evidence / Bằng chứng kiểm kê:** [5938d8e7cb117aa6bc8226ace1d786be2f7be703](https://github.com/tricore-opentrix/opentrix/commit/5938d8e7cb117aa6bc8226ace1d786be2f7be703). Các mốc khác nhau được giữ riêng; tài liệu không xác nhận runtime mới. / These revisions remain distinct; documentation is not new runtime acceptance.

<a id="vi"></a>

## Tiếng Việt

### A. Hiện trạng — mã nguồn và bằng chứng Giai đoạn 2

**Phạm vi:** Hướng dẫn các suite, lệnh và giới hạn từ source tại `832c75fc3164cf170eed3bb8f1e380d24dd65aba`; đối chiếu [Khối C](09-evidence/phase-2/block-c-application.md). Không có kết quả thực thi runtime mới trong bản sửa này.

#### 1. Tổng quan và nguyên tắc

Tài liệu dành cho developer, QA và reviewer. Baseline source/config là SHA trên; snapshot Phase 2 `5938d8e7cb117aa6bc8226ace1d786be2f7be703` được dẫn riêng (ba commit xen giữa chỉ thêm báo cáo). [DEVELOPMENT](DEVELOPMENT.md) hướng dẫn cài đặt/startup/cấu hình; phải dùng phiên bản có trên nhánh công bố. Không provision, migration, dọn DB hay chạy test ứng dụng khi sửa tài liệu này; lệnh dưới đây là SOURCE-CONFIRMED, không phải kết quả chạy mới.

- `SOURCE-CONFIRMED`: suite/lệnh/điều kiện được source/config hỗ trợ, chưa chứng minh thực thi.
- `VERIFIED`: phép kiểm thành công tại SHA/môi trường cụ thể, giữ đầu ra và phạm vi; tool version, source hoặc CI cũ không đủ để kết luận runtime mới.
- `UNVERIFIED`: thiếu bằng chứng thực thi/nghiệm thu cần thiết.
- `PASS / FAIL / SKIPPED`: ghi riêng kết quả case thực tế; disabled/assumption abort không phải pass. Case từ chối chỉ PASS khi đã chạy và assert đúng rejection.

Phân biệt in-memory contract, MVC filter handoff, transaction PostgreSQL disposable, browser MOCK và LIVE xác thực. Build xanh, health response và bundle không đồng nghĩa tích hợp đã nghiệm thu.

#### 2. Kiến trúc kiểm thử

| Lớp | Source/cơ chế | Ranh giới |
| --- | --- | --- |
| Backend domain/contracts | [core tests](https://github.com/tricore-opentrix/opentrix/tree/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/core/), JUnit/parameterized/AssertJ | Identity/Workflow/Data; có persistence/storage doubles in-memory |
| Backend HTTP/security | [gateway](https://github.com/tricore-opentrix/opentrix/tree/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/gateway/), [identity security](https://github.com/tricore-opentrix/opentrix/tree/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/infrastructure/identity/security/), MVC/Test và JWT kiểm soát | Mapping, validation, handoff/authorization; một số suite opt-in issuer thật |
| Kiến trúc | [CoreDependencyRulesTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/architecture/CoreDependencyRulesTest.java), ArchUnit | Core production classes biên dịch, dependency rules/canary âm |
| Portal BFF | PortalSecurityTest, PortalBackendClientTest | MockMvc, session OAuth tổng hợp, manager/HTTP client mock |
| Frontend | [src](https://github.com/tricore-opentrix/opentrix/tree/832c75fc3164cf170eed3bb8f1e380d24dd65aba/frontend/src/), Vitest/Testing Library/jsdom | Component/service/transport/composition với fake/mock |
| Browser | [tests](https://github.com/tricore-opentrix/opentrix/tree/832c75fc3164cf170eed3bb8f1e380d24dd65aba/frontend/tests/), Chromium Playwright/axe | MOCK và fake Helpdesk preview chọn riêng |
| PostgreSQL | [Workflow infrastructure](https://github.com/tricore-opentrix/opentrix/tree/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/infrastructure/workflow/), JDBC/Flyway/fixture local thật | Persistence, migration, concurrency, privileges, TLS, HTTP/DB |
| Tooling repo | [scripts](../scripts/), Python unittest/PowerShell assertions | Compliance/release tooling và identity seed local, không product E2E |

Không suite nào tự xác nhận production object storage, Flowable, APISIX hay Facility E2E. Helper có tên live vẫn có thể dùng kết nối inject/catalog tổng hợp; đọc setup thay vì suy từ tên.

#### 3. Điều kiện trước khi chạy

| Nhóm | Yêu cầu |
| --- | --- |
| Java | JDK 21, Gradle Wrapper 8.14.3 trong backend; BFF dùng lại với `-p portal-bff` |
| Frontend | Node >=22.12.0, dependencies theo package-lock; npm không pin; CI Node22 |
| Tooling | Python3 hoặc PowerShell actor-seed; CI đã xem không pin Python patch version |
| Browser | Dependencies và Playwright Chromium đã cài; build MOCK cho standard smoke |
| PostgreSQL | Fixture local PG17 disposable chuẩn bị riêng, sở hữu độc quyền; tooling pin postgres:17.11-alpine |
| TLS/audit | CA đúng/sai, hostname khớp certificate, credentials riêng, marker disposable khi cần |
| Windows | PowerShell/Docker Desktop Linux Engine; Helpdesk dùng context desktop-linux; Workflow verifier còn cần OpenSSL, Windows executables/ACL |
| Identity thật | Discovery/JWKS đúng issuer, token thật mới/còn hạn, audience/roles đúng; browser cần confidential client, ingress HTTPS, trust CA |

Nguồn version: [Backend build](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/build.gradle), [wrapper](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/gradle/wrapper/gradle-wrapper.properties), [BFF build](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/portal-bff/build.gradle), [package frontend](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/frontend/package.json), [Compose](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/infra/compose.workflow-postgres.yml). Version local không chứng minh fresh-clone test. Lệnh POSIX theo wrapper/CI chưa được chạy tại đây; không mặc định helper Windows/ACL portable.

Trước test thường: terminal mới, không kế thừa opt-in DB/token của operator. Chỉ kiểm tên biến, không in secret. Task test vẫn phát hiện integration class; biến môi trường có thể bật ghi DB. Trước DB test: kiểm endpoint/port/database/roles, ownership và quyền dùng độc quyền; loopback không chứng minh disposable và có thể forward tới dịch vụ dùng chung. Fixture có thể tạo/xóa schema, role, event trigger, public probe. Không chạy đồng thời các suite fixture trên cùng DB.

#### 4. Lệnh kiểm nhanh

Giả định dependencies/browser đã cài; không provision môi trường. Cài đặt theo DEVELOPMENT. Tất cả lệnh SOURCE-CONFIRMED, không kèm kết quả PASS giả.

**Backend — thư mục `backend/`, PowerShell:**

```powershell
.\gradlew.bat test
.\gradlew.bat test --tests 'com.tricore.dxos.core.*'
.\gradlew.bat test --tests com.tricore.dxos.architecture.CoreDependencyRulesTest
```

**Linux/macOS, cùng thư mục:**

```sh
./gradlew test
./gradlew test --tests 'com.tricore.dxos.core.*'
./gradlew test --tests com.tricore.dxos.architecture.CoreDependencyRulesTest
```

**BFF — từ gốc repo:**

```powershell
.\backend\gradlew.bat -p portal-bff test
```

```sh
./backend/gradlew -p portal-bff test
```

**Frontend — thư mục `frontend/`:**

```powershell
npm.cmd test
npm.cmd run build
npm.cmd run check:security
npm.cmd run test:smoke
npx.cmd playwright test --config tests/mvp.playwright.config.ts
```

```sh
npm test
npm run build
npm run check:security
npm run test:smoke
npx playwright test --config tests/mvp.playwright.config.ts
```

Build trước scan bundle và standard preview. MVP fake dùng dev preview riêng; không thay MOCK build bằng integration-local khi standard smoke.

**Ba suite security/exposure được CI kiểm rõ — từ `backend/`:**

```powershell
.\gradlew.bat test --tests com.tricore.dxos.infrastructure.identity.security.GatewayIdentityHandoffHttpTest --tests com.tricore.dxos.infrastructure.identity.security.SpringSecurityCurrentPrincipalTest --tests com.tricore.dxos.gateway.workflow.controller.WorkflowHttpExposureTest
```

POSIX dùng ./gradlew cùng arguments. Không chứng minh Keycloak/browser thật. Nguồn: build.gradle, [CI](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/.github/workflows/ci.yml), [npm scripts](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/frontend/package.json), [MVP config](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/frontend/tests/mvp.playwright.config.ts).

#### 5. Kiểm thử Backend

Mọi selection chạy trong backend bằng ./gradlew hoặc .\gradlew.bat. Matrix source dưới đây không phải kết quả thực thi mới.

| Suite/source | Task/selection | Dependencies | Môi trường | Điều kiện | Bằng chứng cần lưu | Trạng thái |
| --- | --- | --- | --- | --- | --- | --- |
| Core Identity/Workflow/Data: WorkflowRuntimeTest, WorkflowPersistencePortTest, ObjectStoragePortTest | `test --tests 'com.tricore.dxos.core.*'` | JDK/wrapper | Không opt-in hạ tầng | JUnit thường, persistence/storage có double memory | XML/HTML mới | SOURCE-CONFIRMED |
| HealthControllerTest | `test --tests com.tricore.dxos.common.health.HealthControllerTest` | JDK/MVC slice | Config test | Không DB thật | XML/HTML | SOURCE-CONFIRMED |
| WorkflowAuthorizationTest, TenantResourceWorkflowAccessPolicyTest | `test --tests 'com.tricore.dxos.application.authorization.*'` | JDK/snapshot/principal kiểm soát | Không token thật | Unit policy, không DB ACL thực thi | XML/HTML | SOURCE-CONFIRMED |
| Security validators/handoff, trừ hai suite real token bên dưới | test hoặc selection mục 4 | JDK/JWT/MockMvc | Gradle fallback OIDC_ISSUER_URI, OIDC_AUDIENCE, OIDC_RESOURCE_CLIENT_ID | Test kiểm soát không cần IdP thật | XML/HTML + CI ba-suite gate | SOURCE-CONFIRMED |
| WorkflowControllerTest, WorkflowHttpExposureTest, HelpdeskErrorContractTest | test | JDK/Spring test | Controller suite chọn profile workflow-http-tests | Đăng ký controller/profile test không phải production exposure | XML/HTML | SOURCE-CONFIRMED |
| CoreDependencyRulesTest | Selection mục 4 | Production classes/ArchUnit | Không DB/token | Loại fixture test, có canary âm/dương | XML/HTML và counts/canary output | SOURCE-CONFIRMED |
| OidcKeycloakIntegrationTest, GatewayKeycloakTokenHttpIntegrationTest | `test --tests '*OidcKeycloakIntegrationTest' --tests '*GatewayKeycloakTokenHttpIntegrationTest'` | Keycloak discovery/JWKS thật | OIDC_TEST_ACCESS_TOKEN | Thiếu token skip cả class; issuer hardcode | XML/HTML và môi trường provider đã làm sạch | SOURCE-CONFIRMED |

Source: [Core](https://github.com/tricore-opentrix/opentrix/tree/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/core/), [policy](https://github.com/tricore-opentrix/opentrix/tree/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/application/authorization/), [security](https://github.com/tricore-opentrix/opentrix/tree/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/infrastructure/identity/security/), [gateway](https://github.com/tricore-opentrix/opentrix/tree/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/gateway/), [ArchUnit](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/architecture/CoreDependencyRulesTest.java).

ArchUnit Core chỉ cho java.. và cùng package Core, loại JDBC, cấm dependencies giữa capability Core; chưa cưỡng chế mọi quy tắc Application/Gateway hoặc chứng minh authorization. Real-token suites hardcode issuer `http://localhost:8180/realms/tricore`, audience tricore-api; principal mapping cần đúng bốn authority workflow:create/activate/read/transition. Token 127.0.0.1:8182 không thay thế; không sửa issuer validation để token khớp. Đây là decoder/filter test, không browser login/Helpdesk persistence.

WorkflowRuntimePrivilegeAuditLauncherTest, WorkflowSecurityDefinerReviewLauncherTest, WorkflowApprovedSmokeLauncherTest và một số method WorkflowApprovedMigrationTest/WorkflowSchemaBootstrapTest có @EnabledOnOs(WINDOWS); phải báo skip ở OS khác. Launcher test dùng stub/rejection fixture, không cấp phép chạy operator script thật.

#### 6. Kiểm thử Portal BFF

Lệnh mục 4 không cần Backend, DB hoặc credentials provider thật cho fixture.

| Suite | Điều được kiểm từ source | Fixture/giới hạn |
| --- | --- | --- |
| [PortalSecurityTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/portal-bff/src/test/java/com/tricore/dxos/portal/PortalSecurityTest.java) | Từ chối anonymous/header giả, session không token, CSRF ghi/logout, PKCE, confidential client, authorization thiếu/lỗi | WebMvcTest/oauth2Login, client tổng hợp, manager/Backend mock; không callback/provider session thật |
| [PortalBackendClientTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/portal-bff/src/test/java/com/tricore/dxos/portal/PortalBackendClientTest.java) | Origin HTTPS/loopback, bearer server, không redirect, allowlist, giới hạn body, mất session, refresh mô phỏng, lỗi sạch và unknown-write không replay | Java HttpClient/manager mock; không upstream/refresh/logout provider thật |

COMMIT_OUTCOME_UNKNOWN mô phỏng mất response và assert không retry, không chứng minh DB thật commit. Đối soát LIVE bằng GET detail/history có quyền, không replay POST. Lưu XML mới portal-bff/build/test-results/test và HTML portal-bff/build/reports/tests/test. Cookie/ingress/refresh/logout/trust browser cần nghiệm thu riêng theo [BFF runbook](../portal-bff/README.md).

#### 7. Kiểm thử Frontend

| Suite/vị trí | Lệnh trong frontend | Dependencies/môi trường | Chạy/skip | Bằng chứng | Trạng thái |
| --- | --- | --- | --- | --- | --- |
| src/**/*.test.{ts,tsx} theo vite.config.ts | npm test | Node deps/jsdom, không infra variables | Component/service/transport, setup src/test/setup.ts | stdout Vitest, invocation và per-file summary | SOURCE-CONFIRMED |
| portal.spec.ts, session.spec.ts, auth.spec.ts | npm run build rồi npm run test:smoke | Chromium, dist MOCK, cổng 4173 trống | Config preview có thể tái dùng server ngoài CI; kiểm mode/build | List output, trace/screenshots lỗi khi có | SOURCE-CONFIRMED |
| helpdesk-mvp.spec.ts | npx playwright test --config tests/mvp.playwright.config.ts | Chromium/fake preview, không Backend/Keycloak/DB | Standard config cố ý skip; MVP đặt metadata.fakeHelpdeskPreview=true | List output và actual temporary output path | SOURCE-CONFIRMED |
| check-security.mjs | npm run check:security sau build | src/public/dist/package/index | Scan pattern heuristic, không runtime authorization hay kiểm secret đầy đủ | stdout và mode đã kiểm | SOURCE-CONFIRMED |
| Browser local xác thực | Checklist mục 11 | Full stack/identity thật | Build integration-local chưa đủ | Browser/backend/DB evidence sạch | UNVERIFIED |

Windows dùng npm.cmd/npx.cmd. Nguồn: [vite.config.ts](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/frontend/vite.config.ts), [tests](https://github.com/tricore-opentrix/opentrix/tree/832c75fc3164cf170eed3bb8f1e380d24dd65aba/frontend/tests/), [scan](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/frontend/scripts/check-security.mjs). AssignmentForm.integration.test.tsx dùng UI/service/transport fixture; LocalHelpdeskIntegration.test.tsx stub location/fetch. Tên integration không chứng minh HTTP/Keycloak thật; form MOCK login/register không phải xác thực IdP.

**Ảnh chụp có tác dụng ghi file:** portal.spec.ts có thể tạo/ghi đè docs/evidence/issue39-portal từ repo root; auth.spec.ts ghi subfolder auth. Kiểm git status --short trước/sau, giữ evidence hiện có, không tự xóa/clean/revert.

[Standard config](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/frontend/playwright.config.ts): list reporter, Chromium, 127.0.0.1:4173, trace retain-on-failure, không cấu hình HTML report. [MVP](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/frontend/tests/mvp.playwright.config.ts) chạy Vite riêng và thư mục tạm dxos-app14-browser-*; giữ path thật trước khi mất temporary files. Helpdesk skip trong standard smoke là SKIPPED, không PASS. build:integration-local chọn entry main.tsx và ghi dist, không start Backend/BFF/Keycloak/PostgreSQL/Caddy hoặc chứng minh bff/session. Build thường trả MOCK; hai mode dùng chung dist, phải ghi mode được kiểm.

#### 8. Kiểm thử PostgreSQL và hạ tầng

**Fixture có thể phá dữ liệu:** chỉ dùng DB disposable đã chuẩn bị và sở hữu độc quyền. Không cung cấp connection/command cloud ở đây. Dừng nếu chưa chắc target/credential/TLS/ownership; env var chỉ bật suite, không làm DB an toàn.

##### Chọn suite Workflow

[build.gradle](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/build.gradle) chọn đúng bảy class cho workflowIntegrationTest; chín class tại [source infrastructure/workflow](https://github.com/tricore-opentrix/opentrix/tree/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/infrastructure/workflow/) dưới đây đều SOURCE-CONFIRMED, execution UNVERIFIED.

| Suite | Trong workflowIntegrationTest? | Biến bật class (không rỗng) | Fixture/coverage bổ sung |
| --- | --- | --- | --- |
| PostgresWorkflowPersistenceIntegrationTest | Có | WORKFLOW_TEST_JDBC_URL | Runtime/migrator khác nhau, migration schema cô lập, atomicity/conflict/history; least-privilege abort bằng Assumptions nếu không có migration login riêng |
| WorkflowIsolationIntegrationTest | Có | WORKFLOW_TEST_JDBC_URL | Schema/role/probe; TLS cases còn cần CA đúng/sai |
| WorkflowEventTriggerGuardIntegrationTest | Có | WORKFLOW_TEST_JDBC_URL | Catalog/event-trigger tổng hợp có quyền; TLS cần CA |
| WorkflowEventTriggerReviewIntegrationTest | Có | WORKFLOW_TEST_CA_CERT | Còn JDBC/migration credentials, verified TLS và filesystem/ACL capture |
| WorkflowDevelopmentSmokeIntegrationTest | Có | WORKFLOW_AUDIT_LOCAL_JDBC_URL | Fixture TLS local /postgres, audit credentials/CA/marker, setup dựng dev opt-ins |
| WorkflowSchemaBootstrapIntegrationTest | Có | WORKFLOW_AUDIT_LOCAL_JDBC_URL | Audit/TLS đúng-sai/marker, tạo/xóa schema/role, kiểm bootstrap |
| WorkflowApprovedMigrationIntegrationTest | Có | WORKFLOW_AUDIT_LOCAL_JDBC_URL | Audit/TLS/marker, migration V3/V4 ghim và failure boundary |
| WorkflowRuntimePrivilegeAuditIntegrationTest | Không; ordinary test | WORKFLOW_AUDIT_LOCAL_JDBC_URL | Audit credentials/CA đúng-sai, capture read-only/TLS rejection |
| WorkflowSecurityDefinerReviewIntegrationTest | Không; ordinary test | WORKFLOW_AUDIT_LOCAL_JDBC_URL | Audit/TLS; setup vẫn tạo SQL objects disposable dù capture read-only |

| Input fixture | Ý nghĩa/điều kiện |
| --- | --- |
| WORKFLOW_TEST_JDBC_URL, WORKFLOW_TEST_DB_USER, WORKFLOW_TEST_DB_PASSWORD | Dedicated task bắt buộc trước chạy; URL qua guard loopback/port/database, không query. Chưa tự chuẩn bị roles/schema/TLS/all gates |
| WORKFLOW_TEST_MIGRATION_USER, WORKFLOW_TEST_MIGRATION_PASSWORD | Credentials migration riêng; fallback runtime có thể làm least-privilege abort và thiếu quyền setup |
| WORKFLOW_TEST_CA_CERT, WORKFLOW_TEST_WRONG_CA_CERT | CA đúng/sai cho TLS/event review; không tắt verify để bật case |
| WORKFLOW_AUDIT_LOCAL_JDBC_URL | /postgres disposable riêng cho năm suite; guard khác nhau, hai audit suite cần literal 127.0.0.1 |
| WORKFLOW_AUDIT_LOCAL_DB_PASSWORD, WORKFLOW_AUDIT_LOCAL_CA_CERT, WORKFLOW_AUDIT_LOCAL_WRONG_CA_CERT | Audit credentials/cert; một số helper dùng fixture login postgres |
| WORKFLOW_EVENT_GUARD_LOCAL_DISPOSABLE=true, WF25_DISPOSABLE_TEST=1 | Guard local verifier, không bật cho shared service; fixture liên quan kiểm dxos.wf25_disposable=on trong DB |

Chỉ sau operator chuẩn bị/kiểm fixture đầy đủ, từ backend:

```powershell
.\gradlew.bat workflowIntegrationTest --no-daemon
.\gradlew.bat test --tests '*WorkflowRuntimePrivilegeAuditIntegrationTest' --tests '*WorkflowSecurityDefinerReviewIntegrationTest' --no-daemon
```

POSIX dùng ./gradlew cùng args; helper Windows ACL cần review portability. Task riêng ghi build/test-results/workflowIntegrationTest và build/reports/tests/workflowIntegrationTest; lệnh thứ hai ghi test/. Task xanh vẫn có thể skip class/method. Compose là DB Workflow persistent loopback55425, không đủ TLS/audit/Helpdesk; không trỏ HELPDESK_DISPOSABLE_URL vào đó hoặc lấy owner login làm proof runtime ít quyền. Không sửa migration V1–V4 đã áp dụng hay tắt catalog/privilege guard.

##### Helpdesk HTTP/PostgreSQL và B06 real-token

HelpdeskHttpPostgresTest bật class chỉ khi `HELPDESK_DISPOSABLE_URL=jdbc:postgresql://127.0.0.1:55439/helpdesk_disposable_test`; cần HELPDESK_DISPOSABLE_PASSWORD, login helpdesk_test, WORKFLOW_EVENT_GUARD_LOCAL_DISPOSABLE=true. Setup tạo issuer/JWKS tổng hợp và HTTP server tạm, phần lớn test HTTP/DB thật nhưng IdP giả, không Keycloak thật.

Với fixture đã chuẩn bị và sở hữu độc quyền, từ backend chọn `.\gradlew.bat test --tests '*HelpdeskHttpPostgresTest' --no-daemon` (POSIX ./gradlew). Case b06RealKeycloakTokensAndPostgres skip nếu thiếu B06_EMPLOYEE_ACCESS_TOKEN; bật cần đủ bốn token thật, khác nhau và mới: B06_EMPLOYEE_ACCESS_TOKEN, B06_COORDINATOR_ACCESS_TOKEN, B06_WORKER_ACCESS_TOKEN, B06_FOREIGN_ACCESS_TOKEN. Issuer hardcode http://localhost:8180/realms/tricore, audience có tricore-api, token còn >90 giây lúc kiểm. B06 không phải BFF/browser journey.

| Runner/source | Lệnh từ repo root | Điều kiện/tác dụng/evidence |
| --- | --- | --- |
| [helpdesk-negative-local.ps1](../scripts/helpdesk-negative-local.ps1) | `.\scripts\helpdesk-negative-local.ps1 -RunId <new_id>` | Docker Desktop, image ghim có sẵn, cổng55439 trống, tên/evidence dir mới; tạo và giữ container/volume, xóa opt-in liên quan kể cả B06 employee token; ghi sanitized output/http-postgres-results.json trong backend/build/closeout-ID; B06 skip |
| [helpdesk-b06-local.ps1](../scripts/helpdesk-b06-local.ps1) | `.\scripts\helpdesk-b06-local.ps1 -ExecuteDisposable` | Review trước opt-in; bốn token thật, Docker/image/port/JDK; tạo container rồi xóa container sở hữu; expected counts phải khớp source; chưa chạy tại đây |
| [workflow-verify-local.ps1](../scripts/workflow-verify-local.ps1) | `powershell.exe -NoProfile -File .\scripts\workflow-verify-local.ps1` | Windows Docker/JDK21/OpenSSL/ACL; tạo TLS PG17.11 random port, test build, dừng container sở hữu/xóa cert dir; caveat zero-skip bên dưới |

Workflow verifier đòi chín Workflow suite và zero skip trong mọi ordinary-test XML; không provision Helpdesk fixture/token OIDC riêng nên có thể fail dù Workflow pass. Success end-to-end baseline UNVERIFIED. Kiểm per-suite/giải thích skip, không làm yếu guard hoặc bịa token. Provision theo Helpdesk/Backend runbook riêng; không dùng cloud operator bootstrap/migration/smoke làm test setup. Không xóa volume/down -v để sửa test lỗi vì mất dữ liệu/evidence.

#### 9. Kiểm thử bảo mật

| Thuộc tính | Kiểm hiện có | Giới hạn |
| --- | --- | --- |
| Authentication | JWT issuer/audience/type/subject/time validators, SecurityConfigTest, principal/header giả handoff; real-token opt-in | JWKS tổng hợp/MockMvc không browser SSO/provider triển khai |
| Operation/resource authorization | WorkflowAuthorizationTest, TenantResourceWorkflowAccessPolicyTest, HTTP/PG allow/deny Helpdesk | Snapshot unit không xác nhận DB ACL transaction; DB opt-in phải chạy |
| Tenant/least privilege | Isolation, runtime-permission, cross-actor/tenant/B06 foreign | Credentials/fixture/assumptions thực cần xác nhận, skipped assertion không evidence |
| Session/CSRF | CSRF bff/session, thiếu/giả token, identity header giả, authorization failures | Cookie/trust/refresh/logout/expiry thật cần browser |
| Concurrency/unknown writes | Workflow/Helpdesk version/history, no-replay BFF/frontend | Transport failure kiểm soát không phải production commit bị mất |
| Lộ credentials | Scan frontend heuristic, error/session assertions và manual review | Scan sạch không chứng minh không secrets/toàn diện security |

Theo CONTRIBUTING, security change phải có allow và deny. Giữ 401/403/hidden404, stale409, state/history không đổi khi bị từ chối. Không công bố JWT/cookie/CSRF/password/key/full connection string/real user records. Báo lỗ hổng theo SECURITY.

#### 10. Xác minh CI

Nguồn [.github/workflows/ci.yml](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/.github/workflows/ci.yml):

| Job | Lệnh/kiểm | Không chứng minh |
| --- | --- | --- |
| backend | JDK21 ./gradlew build --no-daemon --stacktrace --rerun-tasks; parse cú pháp PowerShell PKCE; XML ba suite GatewayIdentityHandoffHttpTest, SpringSecurityCurrentPrincipalTest, WorkflowHttpExposureTest | Không provision PostgreSQL/Keycloak; opt-in có thể skip; parse không chạy login |
| portal-bff | ./backend/gradlew -p portal-bff build --no-daemon --stacktrace | Provider/ingress/browser/DB thật |
| frontend | Node22 npm ci, npm run build, npm test | Không Playwright/security scan/build:integration-local |
| r23-compliance | Wrapper validation, Python rejection canary, Java/npm SBOM/license/notices | Không product/browser/DB E2E |
| repo-hygiene | Sau R23; PR title/metadata, wrapper mode, REUSE | Không runtime/release acceptance |

XML gate ba suite yêu cầu tồn tại, có tests, zero failure/error/skip; không chứng minh mọi suite tích hợp chạy. Backend HTML upload chỉ khi failure, retention7 ngày; success XML per-suite không upload thường xuyên. Giữ evidence cần riêng, không suy mọi counts từ job xanh; artifact R23 là compliance riêng.

Từ root, tooling canary `python3 -m unittest discover -s scripts -p 'test_r23_*.py'` (Windows dùng Python executable có sẵn), fixture SBOM tổng hợp không service. Release workflow có gate riêng, không LIVE và không được gọi từ hướng dẫn này. `.\scripts\test-helpdesk-local-actor-seed.ps1` chạy root PowerShell không DB/Docker; assert identity/seed/rejection tổng hợp với JSON tạm, không provision/login Keycloak; source-confirmed, chưa chạy mới. Kết quả CI lịch sử Phase 2 phải giữ SHA attribution, không chuyển counts/PASS sang run mới/commit tài liệu.

#### 11. Nghiệm thu LIVE E2E

**UNVERIFIED ở phạm vi tài liệu.** Chưa thấy Playwright config cung cấp full-stack real-provider acceptance. Theo BFF runbook/DEVELOPMENT trước manual plan.

Điều kiện: commit cụ thể; Helpdesk DB disposable độc quyền/runtime grants đúng; Backend/BFF; Keycloak client confidential Code+PKCE với issuer/audience/client roles đúng; ba identity Employee/Coordinator/Worker thật khác nhau và membership issuer/sub chính xác; bundle integration-local; Caddy HTTPS trusted. Browser context cô lập. Subject đã provision không chứng minh login; bff/session 502 là prerequisite thất bại.

| Bước | Principal | Quan sát/evidence sạch |
| --- | --- | --- |
| Create | Employee | Request tổng hợp mới, ID trả về, detail có quyền |
| Triage rồi Assign | Coordinator | Version hiện hành, assignee hợp lệ server; assignment version riêng |
| Start rồi Resolve | Worker được giao | Chỉ state transition/resource access hợp lệ |
| Confirm | Employee gốc | CONFIRMED, không close |
| Reload/history | Principal có quyền | Workflow version4, bốn transitions triage/start_work/resolve/confirm; assign không thêm transition |
| Restart Java/đọc lại | Principal có quyền | Cùng DB giữ detail/history, không setup/reset fixture lại |

Negative: anonymous/expired session, CSRF thiếu/sai, thiếu operation role, actor/resource/tenant trái quyền, stale Workflow/assignment, disconnected reads và unknown write. Ghi 401/403/hidden404/409 theo contract, rejected write không đổi state/history, không POST lần hai sau unknown outcome. Kiểm cookie __Host-DXOS-Portal Secure/HttpOnly/host-only/SameSite=Lax, exact HTTPS origin/Host, không bearer browser storage hoặc gọi Backend trực tiếp. Refresh/logout/trust cần quan sát riêng; fixture denial không thay identity thật bị từ chối.

Giữ SHA, role/test-data identifiers sạch, tham chiếu config, trình tự/status/history/version trước-sau, restart persistence, negatives; review network capture riêng và xóa credentials/cookie/token trước chia sẻ. Thiếu case/prerequisite giữ UNVERIFIED, không PASS. Facility/object storage ngoài đường Helpdesk này.

#### 12. Khắc phục sự cố

| Hiện tượng | Cần kiểm |
| --- | --- |
| Task xanh nhưng integration skip | Gate class/method/OS/assumption; selection không execution, skip không pass |
| Thiếu Workflow variables | Task kiểm ba biến nhưng còn CA/audit/fixture; không điền shared endpoint |
| Privilege case abort | Runtime/migrator fixture riêng được duyệt, không nâng runtime thành owner |
| TLS/hostname lỗi | SAN, CA đúng/sai, verify-full; Compose thường không TLS fixture, không tắt verify |
| Schema/role/event-trigger trùng | Dừng dùng đồng thời, xem ownership, giữ resources điều tra, không broad cleanup |
| Helpdesk class skip/setup fail | URL55439 đúng, helpdesk_test/password/local guard; DB runtime thường khác tên |
| Keycloak token bị từ chối | Exact localhost:8180, audience/client roles, distinct subjects/freshness; token8182 không thay |
| Windows launcher skip trên POSIX | Ghi gap OS; helper TLS/ACL còn assumption nền tảng |
| Frontend test pass không service | Kiểm fake transport/fetch/jsdom và boundary được tuyên bố |
| Standard smoke skip Helpdesk | Guard fakeHelpdeskPreview có chủ ý; MVP config riêng, standard case ghi SKIPPED |
| Browser/server thiếu | Chromium/cổng4173, MOCK build trước smoke, dừng preview không liên quan; không cài deps thay chẩn đoán sai mode |
| Scan không đọc dist | Build mode đúng trước; scan cả bundle/source |
| Verifier fail dù Workflow pass | Zero-skip mọi ordinary reports bao gồm Helpdesk/OIDC opt-in độc lập |
| CI xanh không evidence runtime | Đọc exact job steps/report mới; DB/token/browser không được bảo đảm |
| Unknown write | GET detail/history có quyền đối soát, không replay POST/migration/smoke mù |

#### 13. Bằng chứng và báo cáo test

Mỗi kết quả ghi exact SHA/working-tree changes, OS/tool versions, suite/task/config, ownership fixture và tên env (không secret), command/exit, outcomes, vị trí evidence/giới hạn. UP-TO-DATE/FROM-CACHE/XML cũ là reused evidence, không thực thi mới. Backend CI đã dùng --rerun-tasks; khi cần chạy Java mới chỉ áp dụng sau kiểm an toàn fixture.

Đọc XML có sẵn, không chạy test, từ backend hoặc portal-bff trong PowerShell:

```powershell
Get-ChildItem -LiteralPath .\build\test-results\test -Filter 'TEST-*.xml' |
  ForEach-Object {
    [xml]$report = Get-Content -LiteralPath $_.FullName -Raw
    $report.testsuite | Select-Object name, tests, failures, errors, skipped
  }
```

workflowIntegrationTest đọc folder riêng. Kiểm freshness, class/case chính xác, testcase/skipped reasons và reconcile totals/pass/fail/error/skip. Không output hoặc khác task/SHA không evidence. Disabled/parameterized counts đổi khi bật; không hardcode totals lịch sử. Vitest giữ per-file/case terminal summary; Playwright list, không HTML mặc định: giữ stdout, skip reasons/config/run và actual paths. Trace không chứng minh toàn journey nếu bước trước mock/skip.

Mẫu **chưa chạy**, không chứa counts thành công tự tạo:

```text
SHA / thay đổi working tree: <SHA chính xác; thay đổi liên quan hoặc không>
Môi trường: <OS/tool versions; fixture ID/ownership; build mode; không secret>
Suite / config / ranh giới: <class hoặc browser spec; MOCK/local/LIVE>
Thư mục và lệnh: <lệnh chính xác>
Thời gian / exit code: <chưa thu>
Tổng báo cáo / đã chạy / PASS / failures / errors / SKIPPED: <chưa thu>
Lý do skip/abort và case không được chọn: <chưa thu>
Bằng chứng: <XML/log/artifact đã làm sạch; chưa thu>
Trạng thái: NOT RUN / UNVERIFIED
Giới hạn: <thiếu điều kiện; ranh giới chưa kiểm; reused evidence>
```

Dữ liệu tổng hợp có thể dùng title QA disposable request và ID không nhạy cảm do server trả trong evidence riêng; đó là input minh họa, không kết quả. Theo CONTRIBUTING/security và công khai check chưa chạy.

#### 14. Nguồn tham chiếu

- [README](../README.md), [DEVELOPMENT](DEVELOPMENT.md), [CONTRIBUTING](../CONTRIBUTING.md), [SECURITY](../SECURITY.md).
- [Backend](../backend/README.md), [BFF](../portal-bff/README.md), [Frontend](../frontend/README.md), [Helpdesk runbook](../scripts/README-helpdesk-local.md), [scripts](../scripts/README.md), [CI](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/.github/workflows/ci.yml).
- Phase2 tại `5938d8e7cb117aa6bc8226ace1d786be2f7be703`: [A](https://github.com/tricore-opentrix/opentrix/blob/5938d8e7cb117aa6bc8226ace1d786be2f7be703/docs/09-evidence/phase-2/block-a-architecture.md), [B](https://github.com/tricore-opentrix/opentrix/blob/5938d8e7cb117aa6bc8226ace1d786be2f7be703/docs/09-evidence/phase-2/block-b-backend-infra.md), [C](https://github.com/tricore-opentrix/opentrix/blob/5938d8e7cb117aa6bc8226ace1d786be2f7be703/docs/09-evidence/phase-2/block-c-application.md); inventory có giới hạn riêng, không runtime acceptance mới.

### B. Mục tiêu — PROPOSED, chưa nghiệm thu

- **PROPOSED · [#118](https://github.com/tricore-opentrix/opentrix/issues/118):** thu LIVE xác thực cùng SHA đủ sáu bước, negatives/restart.
- **PROPOSED · [#112](https://github.com/tricore-opentrix/opentrix/issues/112):** route/schema/error parity OpenAPI sau export/review độc lập.
- **PROPOSED · [#194](https://github.com/tricore-opentrix/opentrix/issues/194):** log tái lập, pass/fail/skip thật và reviewer record độc lập.

**Điều kiện công bố:** kiểm link, SHA source, kết quả test thật, SPDX/REUSE và independent review; bản sửa không tự khẳng định PASS.

<a id="en"></a>

## English

### A. Current state — source and Phase 2 evidence

**Scope:** The detailed sections below preserve the source-inspected contract and test boundaries. This documentation update performs no runtime execution. Compare with [Phase 2 Block C](09-evidence/phase-2/block-c-application.md).

#### 1. Overview and Testing Principles

This guide documents existing tests for developers, QA and reviewers. **Code/configuration source baseline:** `832c75fc3164cf170eed3bb8f1e380d24dd65aba`. The Phase 2 reports referenced below are pinned separately at `5938d8e7cb117aa6bc8226ace1d786be2f7be703`; the three intervening commits only add reports.

Use the canonical [DEVELOPMENT.md](DEVELOPMENT.md) for installation, startup and configuration, matching the publication branch. No new application execution, provisioning, migration or cleanup result is claimed. All commands are **SOURCE-CONFIRMED**, not fresh execution evidence.

- **SOURCE-CONFIRMED:** the suite, command or condition is supported by inspected source/configuration; execution is not established.
- **VERIFIED:** a specific check succeeded at an identified SHA/environment, with retained output and an explicit scope. Source presence, local tool versions and an old CI result are insufficient for a new runtime claim.
- **UNVERIFIED:** the required execution or acceptance evidence has not been established.
- **PASS / FAIL / SKIPPED:** report actual case outcomes separately. Disabled tests and aborted assumptions are not passes. An expected rejection is PASS only when the test ran and asserted the rejection.

State the boundary of every result: an in-memory contract, MVC filter handoff, disposable PostgreSQL transaction, MOCK browser journey and authenticated LIVE E2E are different claims. Never infer integrated acceptance from a green build, a health response or a frontend bundle.

#### 2. Test Architecture

| Layer | Existing source and mechanism | Boundary |
| --- | --- | --- |
| Backend domain/contracts | [core tests](https://github.com/tricore-opentrix/opentrix/tree/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/core/), JUnit/JUnit parameterized tests and AssertJ | Identity, Workflow and Data contracts; includes in-memory persistence/storage doubles |
| Backend HTTP/security | [gateway tests](https://github.com/tricore-opentrix/opentrix/tree/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/gateway/), [identity security tests](https://github.com/tricore-opentrix/opentrix/tree/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/infrastructure/identity/security/), Spring MVC/Test and controlled JWT fixtures | HTTP mapping, validation, authentication handoff and authorization; some token suites opt into a real issuer |
| Architecture | [CoreDependencyRulesTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/architecture/CoreDependencyRulesTest.java), ArchUnit | Compiled production Core classes, dependency rules and negative canaries |
| Portal BFF | [PortalSecurityTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/portal-bff/src/test/java/com/tricore/dxos/portal/PortalSecurityTest.java), [PortalBackendClientTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/portal-bff/src/test/java/com/tricore/dxos/portal/PortalBackendClientTest.java) | MockMvc, synthetic OAuth sessions, mocked authorized-client manager and HTTP client |
| Frontend | [frontend/src](https://github.com/tricore-opentrix/opentrix/tree/832c75fc3164cf170eed3bb8f1e380d24dd65aba/frontend/src/), Vitest/Testing Library in jsdom | Components, services, transports and session composition with fake/mocked responses |
| Browser | [frontend/tests](https://github.com/tricore-opentrix/opentrix/tree/832c75fc3164cf170eed3bb8f1e380d24dd65aba/frontend/tests/), Playwright Chromium and axe | MOCK Portal plus an explicitly selected fake Helpdesk preview |
| PostgreSQL | [Workflow infrastructure tests](https://github.com/tricore-opentrix/opentrix/tree/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/infrastructure/workflow/), JDBC/Flyway and real local fixtures | Persistence, migrations, concurrency, privileges, TLS and HTTP/database integration |
| Repository tooling | [scripts](../scripts/), Python unittest and PowerShell assertions | Compliance/release tooling and local identity-seed generation; not product E2E |

No production object-storage provider, Flowable runtime, APISIX deployment or Facility E2E acceptance is established by these tests. Test helpers with names such as `live` can still use injected local connections or synthetic catalogs; inspect their setup, not just their name.

#### 3. Prerequisites

| Group | Requirements |
| --- | --- |
| Java tests | JDK **21**, Gradle Wrapper **8.14.3** in `backend/`; BFF reuses it with `-p portal-bff` |
| Frontend tests | Node.js **>=22.12.0**, installed dependencies matching `frontend/package-lock.json`; npm version is not pinned. CI selects Node 22 |
| Repository tooling tests | Python 3 for the CI unittest command, or PowerShell for the standalone actor-seed assertions; no exact Python version is pinned by the inspected CI |
| Browser | Existing frontend dependencies and Playwright Chromium installation; MOCK production build for standard smoke tests |
| PostgreSQL | A separately prepared, exclusively owned **disposable local PostgreSQL 17** fixture; repository container tooling pins `postgres:17.11-alpine` |
| TLS/database audit | Correct/wrong CA files, matching certificate hostname, separate credentials and disposable database marker where required |
| Windows helpers | PowerShell, Docker Desktop Linux Engine, local `desktop-linux` context for Helpdesk; Workflow verifier also uses OpenSSL, Windows executables and ACL APIs |
| Real identity | Reachable exact issuer, genuine fresh tokens, correct audience/roles; browser E2E additionally needs confidential client, HTTPS ingress and trusted certificates |

Versions come from [Backend build](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/build.gradle), [wrapper properties](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/gradle/wrapper/gradle-wrapper.properties), [BFF build](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/portal-bff/build.gradle), [frontend package](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/frontend/package.json) and [Compose](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/infra/compose.workflow-postgres.yml). Local version observations are not fresh-clone test results. Linux/macOS commands use the committed POSIX wrapper/CI conventions but were not executed for this guide. Windows fixture/ACL helpers must not be assumed portable.

**Before ordinary tests:** use a fresh terminal without database/token opt-ins inherited from an operator session. Inspect the names of configured variables without printing secret values. `test` also discovers conditional integration classes; setting their environment variables can activate database writes.

**Before database tests:** confirm fixture ownership, actual endpoint, port, database name, roles and exclusive use. Loopback alone does not prove a database is disposable; never target shared data or a local port forwarding to a shared service. Fixtures can create/drop schemas, roles, event triggers and public probe objects. Do not run concurrent fixture suites against the same database.

#### 4. Quick Test Commands

These commands assume dependencies/browser binaries are already installed. They do not provision an environment. See [DEVELOPMENT.md](DEVELOPMENT.md) for installation. All commands are **SOURCE-CONFIRMED**; no results are claimed here.

**Backend — working directory `backend/`:**

```powershell
.\gradlew.bat test
# Focused alternatives:
.\gradlew.bat test --tests 'com.tricore.dxos.core.*'
.\gradlew.bat test --tests com.tricore.dxos.architecture.CoreDependencyRulesTest
```

```sh
./gradlew test
./gradlew test --tests 'com.tricore.dxos.core.*'
./gradlew test --tests com.tricore.dxos.architecture.CoreDependencyRulesTest
```

**Portal BFF — working directory repository root:**

```powershell
.\backend\gradlew.bat -p portal-bff test
```

```sh
./backend/gradlew -p portal-bff test
```

**Frontend — working directory `frontend/`:**

```powershell
npm.cmd test
npm.cmd run build
npm.cmd run check:security
npm.cmd run test:smoke
# Separate fake Helpdesk journey:
npx.cmd playwright test --config tests/mvp.playwright.config.ts
```

```sh
npm test
npm run build
npm run check:security
npm run test:smoke
npx playwright test --config tests/mvp.playwright.config.ts
```

The build is needed before the bundle security scan and standard browser preview. The fake Helpdesk config uses its own development preview. Do not substitute an `integration-local` bundle for the MOCK build when running standard smoke tests.

**Focused Backend security — working directory `backend/`:**

```powershell
.\gradlew.bat test --tests com.tricore.dxos.infrastructure.identity.security.GatewayIdentityHandoffHttpTest --tests com.tricore.dxos.infrastructure.identity.security.SpringSecurityCurrentPrincipalTest --tests com.tricore.dxos.gateway.workflow.controller.WorkflowHttpExposureTest
```

Linux/macOS: use `./gradlew` with the same arguments. These are the three suites checked explicitly by CI; they do not establish real Keycloak/browser acceptance. Commands derive from [Gradle test tasks](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/build.gradle), [CI](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/.github/workflows/ci.yml), [npm scripts](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/frontend/package.json) and the [MVP config](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/frontend/tests/mvp.playwright.config.ts).

#### 5. Backend Testing

The following matrix describes source-confirmed groups. `test --tests ...` commands run from **`backend/`**, using `./gradlew` on Linux/macOS or `.\gradlew.bat` on Windows. Runtime outcomes remain **UNVERIFIED** in the cited evidence scope.

| Test suite / source location | Task / selection | Dependencies | Environment | Execution condition | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- |
| [Core Identity/Workflow/Data](https://github.com/tricore-opentrix/opentrix/tree/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/core/), including `WorkflowRuntimeTest`, `WorkflowPersistencePortTest`, `ObjectStoragePortTest` | `test --tests 'com.tricore.dxos.core.*'` | JDK/wrapper | No infrastructure opt-in | Ordinary JUnit cases; persistence/storage contracts include in-memory doubles | Fresh task XML/HTML | SOURCE-CONFIRMED |
| [HealthControllerTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/common/health/HealthControllerTest.java) | `test --tests com.tricore.dxos.common.health.HealthControllerTest` | JDK, MVC slice | Test configuration | No live DB required | XML/HTML | SOURCE-CONFIRMED |
| [Authorization policy tests](https://github.com/tricore-opentrix/opentrix/tree/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/application/authorization/), including `WorkflowAuthorizationTest`, `TenantResourceWorkflowAccessPolicyTest` | `test --tests 'com.tricore.dxos.application.authorization.*'` | JDK, controlled snapshots/principals | No real tokens | Unit policy decisions, not database ACL execution | XML/HTML | SOURCE-CONFIRMED |
| [Security validators/handoff](https://github.com/tricore-opentrix/opentrix/tree/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/infrastructure/identity/security/), excluding the two real-token suites below | `test`; focused CI selection above | JDK, controlled JWT/MockMvc fixtures | Gradle supplies fallback `OIDC_ISSUER_URI`, `OIDC_AUDIENCE`, `OIDC_RESOURCE_CLIENT_ID` for ordinary `test` | No real IdP required for these controlled tests | XML/HTML; CI's three-suite assertion | SOURCE-CONFIRMED |
| [WorkflowControllerTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/gateway/workflow/controller/WorkflowControllerTest.java), [WorkflowHttpExposureTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/gateway/workflow/controller/WorkflowHttpExposureTest.java), [HelpdeskErrorContractTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/gateway/helpdesk/HelpdeskErrorContractTest.java) | `test` | JDK/Spring test configuration | Controller suite selects `workflow-http-tests` internally | A test-only profile/controller registration is not production exposure | XML/HTML | SOURCE-CONFIRMED |
| [CoreDependencyRulesTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/architecture/CoreDependencyRulesTest.java) | Focused command above | Compiled production classes, ArchUnit | No DB/token | Imports production classes, excludes test fixtures; positive/negative canaries | XML/HTML and class-count/canary output | SOURCE-CONFIRMED |
| [OidcKeycloakIntegrationTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/infrastructure/identity/security/OidcKeycloakIntegrationTest.java), [GatewayKeycloakTokenHttpIntegrationTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/infrastructure/identity/security/GatewayKeycloakTokenHttpIntegrationTest.java) | `test --tests '*OidcKeycloakIntegrationTest' --tests '*GatewayKeycloakTokenHttpIntegrationTest'` | Real reachable Keycloak discovery/JWKS | `OIDC_TEST_ACCESS_TOKEN` | Both classes skip if token absent; exact issuer fixed below | XML/HTML, sanitized provider/environment record | SOURCE-CONFIRMED |

The architecture test enforces Core-only dependencies on `java..` and the same Core package, excludes JDBC, and forbids dependencies between Core capabilities. It does not enforce all proposed Application/Gateway rules or prove authorization semantics.

The real-token suites hardcode **`http://localhost:8180/realms/tricore`** and audience `tricore-api`. The principal mapping test expects the four exact Workflow authorities: `workflow:create`, `workflow:activate`, `workflow:read`, `workflow:transition`. A token from `127.0.0.1:8182` is not interchangeable, even if its realm/user looks identical. Do not change issuer validation to make a token fit. These tests verify decoder/filter behavior, not browser login or full Helpdesk persistence.

Windows-only launcher coverage is also conditional: `WorkflowRuntimePrivilegeAuditLauncherTest`, `WorkflowSecurityDefinerReviewLauncherTest`, `WorkflowApprovedSmokeLauncherTest`, and selected methods in `WorkflowApprovedMigrationTest` / `WorkflowSchemaBootstrapTest` use `@EnabledOnOs(WINDOWS)`. Their non-Windows skips must be reported. Launcher tests use rejection/stub fixtures; they do not authorize running the actual operator scripts.

#### 6. Portal BFF Testing

Run the BFF command in Quick Test Commands; no genuine provider credentials, Backend or database are needed for its test fixtures.

| Suite | Source-confirmed checks | Fixture and limitation |
| --- | --- | --- |
| [PortalSecurityTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/portal-bff/src/test/java/com/tricore/dxos/portal/PortalSecurityTest.java) | Anonymous/forged-header rejection, session response without tokens, CSRF on writes/logout, PKCE authorization parameters, confidential-client restrictions, failed/missing authorization handling | `@WebMvcTest`, `oauth2Login()`, synthetic client registration, mocked manager/Backend; not a real Authorization Code callback or provider session |
| [PortalBackendClientTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/portal-bff/src/test/java/com/tricore/dxos/portal/PortalBackendClientTest.java) | HTTPS/loopback origin validation, server-held bearer forwarding, denied redirects, route/method allowlist, bounded response bodies, session invalidation, controlled refresh outcomes, sanitized 401/403/404/409, unknown writes with no replay | Mocked Java `HttpClient` and authorized-client manager; no live upstream/refresh/provider logout |

`COMMIT_OUTCOME_UNKNOWN` tests deliberately model a lost response after a write and assert that it is not retried. They do not establish whether a real database committed. Reconcile live unknown outcomes through authorized detail/history reads, without replaying a POST.

Evidence is fresh `portal-bff/build/test-results/test/` XML and `portal-bff/build/reports/tests/test/` HTML. BFF live cookie behavior, HTTPS ingress, real refresh/logout and browser trust require separate acceptance against [BFF configuration/runbook](../portal-bff/README.md).

#### 7. Frontend Testing

| Suite / location | Command in `frontend/` | Dependencies / environment | Run/skip condition | Evidence | Status |
| --- | --- | --- | --- | --- | --- |
| `src/**/*.test.{ts,tsx}` selected by [vite.config.ts](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/frontend/vite.config.ts) | `npm test` (`npm.cmd` on Windows) | Installed Node dependencies, jsdom; no infrastructure variables | Includes component/service/transport tests; test setup is `src/test/setup.ts` | Vitest terminal output; retain invocation and per-file summary | SOURCE-CONFIRMED |
| [portal.spec.ts](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/frontend/tests/portal.spec.ts), [session.spec.ts](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/frontend/tests/session.spec.ts), [auth.spec.ts](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/frontend/tests/auth.spec.ts) | `npm run build`, then `npm run test:smoke` | Chromium, MOCK `dist`, free port 4173 | Standard config starts preview; can reuse an existing server outside CI, so verify its build/mode | List reporter, test output and retained failure trace/screenshots where produced | SOURCE-CONFIRMED |
| [helpdesk-mvp.spec.ts](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/frontend/tests/helpdesk-mvp.spec.ts) | `npx playwright test --config tests/mvp.playwright.config.ts` (`npx.cmd` on Windows) | Chromium, explicit fake preview; no Backend/Keycloak/DB | Standard config intentionally skips it. Only MVP config supplies `project.metadata.fakeHelpdeskPreview=true` and selects this spec | List output plus the actual temporary output directory printed by the run | SOURCE-CONFIRMED |
| [check-security.mjs](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/frontend/scripts/check-security.mjs) | `npm run check:security` after build | `src`, `public`, `dist`, package/index files present | Heuristic credential-pattern scan; not a test of runtime authorization or comprehensive secret detection | Terminal scan result and reviewed build mode | SOURCE-CONFIRMED |
| Authenticated local browser composition | Manual checklist in section 11 | Full configured stack and real identities | `integration-local` bundle alone is insufficient | Sanitized browser/backend/database evidence | UNVERIFIED |

[AssignmentForm.integration.test.tsx](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/frontend/src/components/AssignmentForm.integration.test.tsx) composes UI/service/transport fixtures; [LocalHelpdeskIntegration.test.tsx](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/frontend/src/features/helpdesk/LocalHelpdeskIntegration.test.tsx) stubs browser location/fetch. Their names do not imply live HTTP or Keycloak execution. Likewise, MOCK login/register form validation is not identity-provider authentication.

**Screenshot side effects:** when Playwright runs from `frontend/`, `tests/portal.spec.ts` can create or overwrite screenshots in `docs/evidence/issue39-portal/` at repository root; `tests/auth.spec.ts` does so in its `auth/` subdirectory. Run `git status --short` before and after the tests and review new or modified evidence files. Preserve existing evidence; do not automatically delete, clean or revert it.

The [standard Playwright config](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/frontend/playwright.config.ts) uses a **list** reporter, Chromium, `http://127.0.0.1:4173` and `trace: retain-on-failure`; it does not configure an HTML report. The [MVP config](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/frontend/tests/mvp.playwright.config.ts) starts a separate Vite server and allocates a temporary `dxos-app14-browser-*` output directory. Capture the actual artifact paths before temporary files disappear. An intentional Helpdesk skip under standard smoke is **SKIPPED**, never PASS.

`npm run build:integration-local` selects the integration entry in [src/main.tsx](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/frontend/src/main.tsx). It only creates a bundle in `dist`; it does not start Backend/BFF/Keycloak/PostgreSQL/Caddy or prove that `/bff/session` works. Default `npm run build` restores MOCK. Both modes write the same output directory; record which one was tested.

#### 8. PostgreSQL and Infrastructure Testing

**Destructive fixture warning:** the commands in this section are only for a separately prepared, exclusively owned disposable database. No connection values or cloud commands are supplied here. Stop if fixture ownership, credentials, TLS or the actual target is uncertain. An environment variable enables a suite; it does not make a target safe.

##### Workflow suite selection and conditions

[backend/build.gradle](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/build.gradle) selects exactly seven classes for `workflowIntegrationTest`. The nine Workflow integration classes below share [this source directory](https://github.com/tricore-opentrix/opentrix/tree/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/infrastructure/workflow/); each row links its actual file. All rows are **SOURCE-CONFIRMED**, with execution **UNVERIFIED** here.

| Test suite / location | Included in `workflowIntegrationTest`? | Class-level enabling variable | Additional fixture requirements / coverage |
| --- | --- | --- | --- |
| [PostgresWorkflowPersistenceIntegrationTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/infrastructure/workflow/PostgresWorkflowPersistenceIntegrationTest.java) | Yes | `WORKFLOW_TEST_JDBC_URL` nonempty | Runtime/migrator credentials, isolated schema migrations, atomicity/conflicts/history. Least-privilege case aborts via `Assumptions.assumeTrue` unless a distinct migration login is supplied |
| [WorkflowIsolationIntegrationTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/infrastructure/workflow/WorkflowIsolationIntegrationTest.java) | Yes | `WORKFLOW_TEST_JDBC_URL` nonempty | Schema/role/probe setup; some TLS cases gated separately by correct/wrong CA variables |
| [WorkflowEventTriggerGuardIntegrationTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/infrastructure/workflow/WorkflowEventTriggerGuardIntegrationTest.java) | Yes | `WORKFLOW_TEST_JDBC_URL` nonempty | Privileged synthetic catalog/event-trigger fixture; TLS cases additionally gated by CA variables |
| [WorkflowEventTriggerReviewIntegrationTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/infrastructure/workflow/WorkflowEventTriggerReviewIntegrationTest.java) | Yes | `WORKFLOW_TEST_CA_CERT` nonempty | Also needs Workflow JDBC URL and migration credentials; verified TLS plus protected filesystem/ACL capture |
| [WorkflowDevelopmentSmokeIntegrationTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/infrastructure/workflow/WorkflowDevelopmentSmokeIntegrationTest.java) | Yes | `WORKFLOW_AUDIT_LOCAL_JDBC_URL` nonempty | Local `/postgres` TLS fixture, audit credentials/CA, marker; builds local development opt-ins inside test setup |
| [WorkflowSchemaBootstrapIntegrationTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/infrastructure/workflow/WorkflowSchemaBootstrapIntegrationTest.java) | Yes | `WORKFLOW_AUDIT_LOCAL_JDBC_URL` nonempty | Local audit fixture, correct/wrong CA, marker; creates/drops fixture schemas/roles and checks bootstrap boundaries |
| [WorkflowApprovedMigrationIntegrationTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/infrastructure/workflow/WorkflowApprovedMigrationIntegrationTest.java) | Yes | `WORKFLOW_AUDIT_LOCAL_JDBC_URL` nonempty | Local audit fixture, TLS and disposable marker; tests pinned V3/V4 migration and failure boundaries |
| [WorkflowRuntimePrivilegeAuditIntegrationTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/infrastructure/workflow/WorkflowRuntimePrivilegeAuditIntegrationTest.java) | **No**; selected through ordinary `test` | `WORKFLOW_AUDIT_LOCAL_JDBC_URL` nonempty | Audit fixture credentials/correct and wrong CA; read-only audit and TLS rejection cases |
| [WorkflowSecurityDefinerReviewIntegrationTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/infrastructure/workflow/WorkflowSecurityDefinerReviewIntegrationTest.java) | **No**; selected through ordinary `test` | `WORKFLOW_AUDIT_LOCAL_JDBC_URL` nonempty | Audit fixture/TLS; setup itself creates disposable SQL objects even though capture is read-only |

| Fixture input | Meaning and condition |
| --- | --- |
| `WORKFLOW_TEST_JDBC_URL`, `WORKFLOW_TEST_DB_USER`, `WORKFLOW_TEST_DB_PASSWORD` | Required by the dedicated Gradle task before execution; URL must satisfy fixture loopback/port/database guards and have no query. These variables alone do not prepare roles, schema, TLS or all suite gates |
| `WORKFLOW_TEST_MIGRATION_USER`, `WORKFLOW_TEST_MIGRATION_PASSWORD` | Separate migration credentials. Some helpers fall back to runtime credentials when absent, but least-privilege coverage then aborts and setup may lack privileges. Use distinct fixture roles |
| `WORKFLOW_TEST_CA_CERT`, `WORKFLOW_TEST_WRONG_CA_CERT` | Correct and intentionally wrong CA files for nested TLS cases and event-trigger review. Do not disable verification to enable a case |
| `WORKFLOW_AUDIT_LOCAL_JDBC_URL` | Separate disposable `/postgres` connection used by five suites; specific URL guards differ, including literal `127.0.0.1` in the two audit suites |
| `WORKFLOW_AUDIT_LOCAL_DB_PASSWORD`, `WORKFLOW_AUDIT_LOCAL_CA_CERT`, `WORKFLOW_AUDIT_LOCAL_WRONG_CA_CERT` | Audit fixture credentials and certificates; several helpers use the fixture's `postgres` login internally |
| `WORKFLOW_EVENT_GUARD_LOCAL_DISPOSABLE=true`, `WF25_DISPOSABLE_TEST=1` | Local fixture controls used by the verifier; do not set against shared services. Relevant fixtures also check `dxos.wf25_disposable=on` in the database |

After an operator has prepared and checked the complete fixture, run from **`backend/`**:

```powershell
.\gradlew.bat workflowIntegrationTest --no-daemon
# To include the two audit suites in a focused run against that same prepared fixture:
.\gradlew.bat test --tests '*WorkflowRuntimePrivilegeAuditIntegrationTest' --tests '*WorkflowSecurityDefinerReviewIntegrationTest' --no-daemon
```

Linux/macOS: use `./gradlew` with the same arguments; Windows-specific ACL fixture paths still require manual portability review. Inspect **`build/test-results/workflowIntegrationTest/`** and **`build/reports/tests/workflowIntegrationTest/`** for the dedicated task; the second command writes the ordinary **`test/`** reports. A successful dedicated task can still contain conditionally skipped classes/methods.

[Compose](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/infra/compose.workflow-postgres.yml) provides a persistent Workflow database at loopback port 55425, not a complete TLS/audit/Helpdesk fixture. Do not point `HELPDESK_DISPOSABLE_URL` at it or assume its owner login verifies a least-privilege runtime. Do not edit applied V1–V4 migrations or disable catalog/privilege guards to satisfy tests.

##### Helpdesk HTTP/PostgreSQL and real-token B06

[HelpdeskHttpPostgresTest](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/backend/src/test/java/com/tricore/dxos/infrastructure/workflow/HelpdeskHttpPostgresTest.java) is class-gated on exactly `HELPDESK_DISPOSABLE_URL=jdbc:postgresql://127.0.0.1:55439/helpdesk_disposable_test`. It also needs `HELPDESK_DISPOSABLE_PASSWORD`, the expected fixture login `helpdesk_test`, and `WORKFLOW_EVENT_GUARD_LOCAL_DISPOSABLE=true`. Setup generates a synthetic issuer/JWKS and an ephemeral HTTP server; most cases are real HTTP/database integration with fake identity-provider data, not real Keycloak.

With that **already prepared, exclusively owned fixture**, select it from `backend/` using `.\gradlew.bat test --tests '*HelpdeskHttpPostgresTest' --no-daemon` (POSIX: `./gradlew` with the same arguments). The nested `b06RealKeycloakTokensAndPostgres` case skips without `B06_EMPLOYEE_ACCESS_TOKEN`. When enabled, it requires **all four** genuine, distinct, fresh tokens: `B06_EMPLOYEE_ACCESS_TOKEN`, `B06_COORDINATOR_ACCESS_TOKEN`, `B06_WORKER_ACCESS_TOKEN`, `B06_FOREIGN_ACCESS_TOKEN`; issuer is hardcoded to `http://localhost:8180/realms/tricore`, audience includes `tricore-api`, and tokens must remain valid for more than 90 seconds at the check. B06 is not a BFF/browser journey.

Existing Windows runners are documented here for review, **not automatic setup steps**:

| Runner / source | Invocation from repository root | Prerequisites, side effects and evidence |
| --- | --- | --- |
| [helpdesk-negative-local.ps1](../scripts/helpdesk-negative-local.ps1) | `.\scripts\helpdesk-negative-local.ps1 -RunId <new_id>` | Local Docker Desktop, pinned image already present, port 55439 free, new names/evidence directory. Creates and retains container/volume, clears relevant opt-ins including B06 employee token; writes sanitized output and `http-postgres-results.json` under `backend/build/closeout-<new_id>/`. B06 remains skipped |
| [helpdesk-b06-local.ps1](../scripts/helpdesk-b06-local.ps1) | `.\scripts\helpdesk-b06-local.ps1 -ExecuteDisposable` | Review before opting in: requires four real tokens, Docker/pinned image/free port and configured JDK path. Creates a disposable container and removes its owned container afterward; fixed expected case counts must match the checked-out source. Not executed here |
| [workflow-verify-local.ps1](../scripts/workflow-verify-local.ps1) | `powershell.exe -NoProfile -File .\scripts\workflow-verify-local.ps1` | Windows Docker/JDK21/OpenSSL/ACL support; creates random-port PG17.11 TLS fixtures, runs `test build`, stops its owned disposable container and removes its certificate directory. **Zero-skip caveat below** |

**Workflow verifier caveat:** it requires nine Workflow integration suites and zero skipped cases across every ordinary-test XML report. It does not provision the independent Helpdesk fixture or real OIDC tokens, so its gate can fail even when the Workflow cases pass. Its end-to-end success at this baseline is **UNVERIFIED**. Inspect per-suite execution and explain skips; do not weaken guards, fabricate tokens or call this a guaranteed green command.

For provisioning details, consult the [Helpdesk runbook](../scripts/README-helpdesk-local.md) and [Backend runbook](../backend/README.md) separately. No provisioning/migration/cleanup instructions are executed by this documentation task. Never use cloud operator bootstrap/migration/smoke launchers as test setup. **Do not delete volumes or run `down -v` to repair a failed test**: retained data/evidence would be destroyed.

#### 9. Security Testing

| Property | Existing checks | Evidence limit |
| --- | --- | --- |
| Authentication | JWT issuer/audience/type/subject/time validators, `SecurityConfigTest`, verified-principal and forged-header handoff tests; optional real-token suites | Synthetic signing/JWKS or MockMvc is not browser SSO or a currently deployed provider |
| Operation and resource authorization | `WorkflowAuthorizationTest`, `TenantResourceWorkflowAccessPolicyTest`, Helpdesk HTTP/PostgreSQL allowed/denied paths | Unit snapshots do not establish transactional PostgreSQL ACL behavior; opt-in DB cases must execute |
| Tenant isolation/least privilege | Workflow isolation suite, runtime-permission case, Helpdesk cross-actor/tenant checks including B06 foreign identity | Distinct credentials, actual fixture and assumption outcome matter; a skipped privilege assertion is not evidence |
| Session/CSRF | BFF tests obtain CSRF from `/bff/session`, reject absent/forged headers, reject forged identity headers and model authorization failures | Real cookie attributes, browser trust, provider refresh/logout and session expiry need browser evidence |
| Concurrency/unknown writes | Workflow/Helpdesk version/history tests, BFF and frontend no-replay assertions | Controlled transport failures must not be described as a lost real production commit |
| Credential exposure | Frontend heuristic scan, sanitized error/session assertions and manual evidence review | A clean scan is not proof of no secrets or a full security audit |

For security changes, follow [CONTRIBUTING.md](../CONTRIBUTING.md): test both allowed and denied paths. Preserve 401/403 and hidden-resource 404 semantics, stale-version 409 behavior and unchanged state/history after rejected writes. Never publish JWTs, cookies, CSRF values, passwords, private keys, full connection strings or real user records. Report vulnerabilities through [SECURITY.md](../SECURITY.md).

#### 10. CI Verification

[.github/workflows/ci.yml](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/.github/workflows/ci.yml) declares:

| Job | Tests/checks run | What it does not establish |
| --- | --- | --- |
| `backend` | JDK21 `./gradlew build --no-daemon --stacktrace --rerun-tasks`; parses PKCE PowerShell syntax; checks XML for `GatewayIdentityHandoffHttpTest`, `SpringSecurityCurrentPrincipalTest`, `WorkflowHttpExposureTest` | No PostgreSQL/Keycloak fixture is provisioned; opt-in cases can skip; syntax parsing does not execute PKCE login |
| `portal-bff` | `./backend/gradlew -p portal-bff build --no-daemon --stacktrace` | Real provider, ingress, browser or database acceptance |
| `frontend` | Node22 `npm ci`, `npm run build`, `npm test` | Does not run Playwright, security scan or `build:integration-local` |
| `r23-compliance` | Wrapper validation; Python R23 rejection canary; Java/npm SBOM/license/notices checks | Product runtime, browser or DB E2E |
| `repo-hygiene` | Requires R23 success; PR-title/metadata, wrapper mode and REUSE checks | Runtime integration or release acceptance |

The explicit Backend XML check requires each of its three suites to exist, contain tests and have zero failures/errors/skips. It does **not** assert that every integration suite executed. Backend HTML test reports are uploaded **on failure**, with seven-day retention; successful-run per-suite XML is not generally uploaded by this workflow. Capture needed evidence separately rather than assuming a green job preserves all counts. R23 artifacts are separate compliance evidence.

Repository tooling canaries can run independently: from root, CI uses `python3 -m unittest discover -s scripts -p 'test_r23_*.py'`; use the available Python executable with the same arguments on Windows. These tests use synthetic SBOM fixtures, not product services. The separate [release workflow](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/.github/workflows/release.yml) has its own gates; it is not LIVE E2E proof and is not invoked by this guide.

The standalone [test-helpdesk-local-actor-seed.ps1](../scripts/test-helpdesk-local-actor-seed.ps1) runs from root as `.\scripts\test-helpdesk-local-actor-seed.ps1` in PowerShell without Docker or a database. It asserts canonical identity/seed generation and rejection behavior using synthetic subjects and a temporary local JSON file; it does not provision identities or authenticate with Keycloak. Invocation and assertions are **SOURCE-CONFIRMED**, not execution results here.

Phase 2 reports contain historical exact-SHA CI observations. Keep those attributions distinct from a new local run, do not infer unrecorded counts, and do not treat a report-only commit as new runtime validation.

#### 11. LIVE E2E Acceptance

**UNVERIFIED in the cited evidence scope.** No automated Playwright configuration inspected here supplies full-stack real-provider acceptance. Follow the [BFF acceptance checklist](../portal-bff/README.md) and [local configuration guide](DEVELOPMENT.md) before executing this manual plan.

Prerequisites: an explicitly selected commit; exclusively owned disposable Helpdesk database and correct runtime grants; Backend/BFF; real Keycloak confidential Code + PKCE client with exact issuer/audience/client roles; three distinct real Employee/Coordinator/Worker identities mapped to exact issuer/sub memberships; `integration-local` bundle; trusted Caddy HTTPS origin. Use isolated browser contexts. A provisioned subject is not proof of successful authentication, and `/bff/session` returning 502 is a failed prerequisite.

| Step | Principal | Observe and retain sanitized evidence |
| --- | --- | --- |
| Create | Employee | New synthetic request, returned identifier, authorized detail |
| Triage, then Assign | Coordinator | Current versions and server-provided eligible assignee; assignment changes its own version |
| Start, then Resolve | Assigned Worker | Only permitted state transitions and resource access |
| Confirm | Original Employee | Terminal `CONFIRMED`; no `/close` operation |
| Reload/read history | Authorized principal | Workflow version **4**, four transitions `triage`, `start_work`, `resolve`, `confirm`; assignment adds no Workflow history transition |
| Restart Java, reread | Authorized principal | Same disposable database retains detail/history; do not rerun setup or reset fixtures |

Include negative checks: anonymous/expired sessions, missing/wrong CSRF, insufficient operation role, unauthorized actor/resource/tenant reads, stale Workflow/assignment versions, disconnected reads and unknown write responses. Record expected 401/403/hidden 404/409 according to the contract and unchanged state/history for rejected writes. Confirm no second POST after an unknown outcome.

Inspect the real browser cookie (`__Host-DXOS-Portal`, Secure, HttpOnly, host-only, SameSite=Lax), exact HTTPS origin/Host handling, no bearer tokens in browser storage, and no direct browser-to-Backend calls. Provider refresh/logout and certificate trust need their own observations. Use a genuine unauthorized identity for live denial evidence; fixture-only denials do not substitute.

Retain commit, sanitized role/test-data identifiers, environment configuration references, ordered actions, HTTP statuses, authorized history, before/after versions, restart persistence and negative-case results. Review network captures privately and redact credentials/cookies/tokens before sharing. Any missing prerequisite/case remains **UNVERIFIED**, not PASS. Facility/object-storage acceptance is outside this Helpdesk path.

#### 12. Troubleshooting

| Symptom | Check |
| --- | --- |
| Green task with skipped integration cases | Inspect class/method gates, OS and assumption reasons. Selection is not execution; do not count skipped cases as passes |
| Missing Workflow variables | Dedicated task checks three variables; additional CA/audit credentials and fixture state are still required. Do not fill them with shared endpoints |
| Privilege case aborted | Supply distinct approved migrator/runtime fixture roles; do not elevate runtime to owner to obtain a green result |
| TLS/hostname failure | Check actual certificate SAN, correct/wrong CA paths and `verify-full`; plain Compose is not the TLS fixture. Do not disable TLS validation |
| Schema/role/event-trigger collision | Stop concurrent users/suites and inspect ownership. Preserve resources for investigation; do not issue broad cleanup |
| Helpdesk class skipped/fails setup | Check its exact 55439 disposable URL, expected fixture login/password and local guard; normal runtime Helpdesk database names are different |
| Keycloak token rejected | Match literal issuer `localhost:8180`, audience, exact client roles, distinct subjects and freshness. Browser runbook's 8182 tokens do not satisfy hardcoded 8180 tests |
| Windows launcher skips on Linux/macOS | Expected OS condition; record the gap. TLS/ACL helpers may have further platform assumptions |
| Frontend integration test passes without services | It may use fake transport/fetch in jsdom; verify the boundary claimed |
| Standard smoke skips Helpdesk journey | Intentional `fakeHelpdeskPreview` guard; use the explicit MVP config and report the standard case as SKIPPED |
| Playwright browser/server unavailable | Check installed Chromium and port 4173; build MOCK before smoke and stop an unrelated preview. Do not install dependencies as a substitute for diagnosing a wrong build mode |
| Security scan cannot read `dist` | Build the intended mode first; the script scans the bundle as well as source |
| Verifier fails despite Workflow cases passing | Its zero-skip gate spans all ordinary-test reports, including independent Helpdesk/OIDC opt-ins |
| CI green, no runtime evidence | Read exact job steps and available fresh reports; DB/real-token/browser gates are not guaranteed by that status |
| Unknown write outcome | Reconcile using authorized detail/history; do not retry POST, migration or smoke blindly |

#### 13. Test Evidence and Reporting

For each claimed result, record exact SHA and working-tree changes, tool versions/OS, selected suite/task/config, fixture ownership and environment references (names, not secret values), command/exit status, case outcomes, evidence location and limitations. Treat `UP-TO-DATE`/`FROM-CACHE` and old XML as reused evidence, not a fresh execution. When fresh Java execution is required, `--rerun-tasks` is already used by Backend CI; apply it only after rechecking fixture safety.

To inspect existing ordinary-task XML without running tests, working directory **`backend/`** or **`portal-bff/`**, PowerShell:

```powershell
Get-ChildItem -LiteralPath .\build\test-results\test -Filter 'TEST-*.xml' |
  ForEach-Object {
    [xml]$report = Get-Content -LiteralPath $_.FullName -Raw
    $report.testsuite | Select-Object name, tests, failures, errors, skipped
  }
```

For `workflowIntegrationTest`, inspect `build/test-results/workflowIntegrationTest` instead. Confirm report freshness and exact class/case names, inspect `<testcase>` entries and `<skipped>` reasons, and reconcile declared totals with passed/failed/error/skipped outcomes. An empty output or a report from a different task/SHA is no evidence. Class-disabled and parameterized case counts can differ when enabled; do not hardcode historical totals.

Vitest defaults here to terminal reporting; retain its per-file/case summary. Playwright uses the list reporter, not a configured HTML report: retain stdout, skip reasons, run/config identity and actual artifact paths. Do not claim a trace proves the whole journey if earlier steps were mocked or skipped.

Copy this **unexecuted reporting template**; it contains no fabricated successful counts:

```text
SHA / working-tree changes: <exact SHA; relevant changes or none>
Environment: <OS/tool versions; fixture ID/ownership; build mode; no secrets>
Suite / config / boundary: <class or browser spec; MOCK/local/LIVE>
Working directory and command: <exact invocation>
Run time / exit code: <not collected>
Total reported / executed / passed / failures / errors / skipped: <not collected>
Skip/abort reasons and cases not selected: <not collected>
Evidence: <sanitized XML/log/artifact reference; not yet collected>
Status: NOT RUN / UNVERIFIED
Limitations: <missing prerequisites, untested boundaries, reused results>
```

Synthetic live test data can use a title such as `QA disposable request` and a non-sensitive returned identifier in private evidence. This is an example input, not a test result. Apply [CONTRIBUTING.md](../CONTRIBUTING.md) evidence/security rules and disclose any check not run.

#### 14. References

- [README](../README.md), [DEVELOPMENT](DEVELOPMENT.md), [CONTRIBUTING](../CONTRIBUTING.md), [SECURITY](../SECURITY.md).
- [Backend runbook](../backend/README.md), [BFF runbook](../portal-bff/README.md), [Frontend guide](../frontend/README.md).
- [Helpdesk local runbook](../scripts/README-helpdesk-local.md), [script notes](../scripts/README.md), [CI](https://github.com/tricore-opentrix/opentrix/blob/832c75fc3164cf170eed3bb8f1e380d24dd65aba/.github/workflows/ci.yml).
- Phase 2 published snapshots at `5938d8e7cb117aa6bc8226ace1d786be2f7be703`: [Block A](https://github.com/tricore-opentrix/opentrix/blob/5938d8e7cb117aa6bc8226ace1d786be2f7be703/docs/09-evidence/phase-2/block-a-architecture.md), [Block B](https://github.com/tricore-opentrix/opentrix/blob/5938d8e7cb117aa6bc8226ace1d786be2f7be703/docs/09-evidence/phase-2/block-b-backend-infra.md), [Block C](https://github.com/tricore-opentrix/opentrix/blob/5938d8e7cb117aa6bc8226ace1d786be2f7be703/docs/09-evidence/phase-2/block-c-application.md). Reports are evidence inventories with their own limitations, not new runtime acceptance.

### B. Target — PROPOSED, not yet accepted

- **PROPOSED · [#118](https://github.com/tricore-opentrix/opentrix/issues/118):** capture same-SHA authenticated live end-to-end evidence for all six Helpdesk steps, negative authorization cases and restart persistence.
- **PROPOSED · [#112](https://github.com/tricore-opentrix/opentrix/issues/112):** check runtime OpenAPI route/schema/error parity after the spec is exported and independently reviewed.
- **PROPOSED · [#194](https://github.com/tricore-opentrix/opentrix/issues/194):** provide repeatable test logs, pass/fail/skip counts and an independent reviewer record.

**Publication gate:** Link validation, matched source SHA, real test outputs, SPDX/REUSE check and independent review are required; none is claimed PASS by this document edit.
