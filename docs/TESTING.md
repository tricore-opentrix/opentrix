<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# Testing Guide / Hướng dẫn kiểm thử

> **Owner:** @ngang02012007-crypto · **Issue:** [#194](https://github.com/tricore-opentrix/opentrix/issues/194) · **Priority:** P0 · **Status:** DRAFT FOR REVIEW; NOT LIVE-ACCEPTED

**Mốc nguồn mã / Source baseline:** [`832c75fc3164cf170eed3bb8f1e380d24dd65aba`](https://github.com/tricore-opentrix/opentrix/commit/832c75fc3164cf170eed3bb8f1e380d24dd65aba). Đây là bản đối chiếu tài liệu, **không** phải kết quả kiểm thử mới. Chỉ gắn `VERIFIED` khi có kết quả chạy ở SHA, môi trường và log cụ thể.

## Tiếng Việt

### A. Hiện trạng — bằng chứng từ mã nguồn và Giai đoạn 2

**Mục đích:** Hướng dẫn phát hiện, chạy và ghi nhận kết quả kiểm thử tại đúng SHA. Các lệnh bên dưới được đối chiếu với cấu hình repository, **chưa được thực thi trong lượt biên soạn này**. Tham chiếu [Khối A](09-evidence/phase-2/block-a-architecture.md), [Khối B](09-evidence/phase-2/block-b-backend-infra.md), [Khối C](09-evidence/phase-2/block-c-application.md) và [CI](../.github/workflows/ci.yml).

| Tầng | Mã và công cụ đã khai báo | Không được suy diễn |
| --- | --- | --- |
| Core/Backend | JUnit, Spring Test, Gradle Wrapper, kiểm thử Identity/Workflow, ArchUnit | Có test trong source ≠ test đã chạy ở HEAD |
| Portal BFF | `PortalSecurityTest`, `PortalBackendClientTest`, session/PKCE/CSRF/forwarding giả lập | Không xác nhận Keycloak/browser thật |
| Frontend | React/Vitest + Playwright MOCK; `integration-local` mode riêng | Mock fetch và build không phải LIVE E2E |
| PostgreSQL | Workflow/Helpdesk opt-in integration suites, kiểm version/ACL/history | Nhiều ca chỉ chạy với DB tạm riêng, có thể SKIPPED |
| CI | Job backend, portal-bff, frontend, compliance, repo-hygiene | Job xanh không chứng minh mọi test DB, Keycloak hay browser |

**Điều kiện tiên quyết:** JDK 21, Node >=22.12, công cụ JavaScript/Gradle tương ứng; test cơ bản không tự provision cơ sở dữ liệu. Không chạy script/migration có khả năng ghi lên DB đang dùng chung. Token, password và cookie phải giữ ngoài Git/log. Trong môi trường Windows dùng các lệnh sau **từ đúng thư mục**:

```powershell
# Repository root: Backend & BFF
Push-Location backend
.\gradlew.bat test
Pop-Location
.\backend\gradlew.bat -p portal-bff test

# Frontend
Push-Location frontend
npm.cmd test
npm.cmd run build
npm.cmd run check:security
# Playwright smoke cần Chromium đã cài và bản build MOCK
npm.cmd run test:smoke
Pop-Location
```

**Cách đánh giá:** Lưu SHA, thay đổi working tree, phiên bản công cụ, câu lệnh, thời điểm chạy, số `PASS / FAIL / SKIPPED`, log/JUnit XML, test mode (MOCK/local/LIVE) và hạn chế. Test bị skip **không tính PASS**. Một ca test giả lập 401/403 không phải bằng chứng phân quyền LIVE. [TESTING evidence chi tiết trong phần tiếng Anh](#13-test-evidence-and-reporting).

**Golden Path cần chứng minh:** Create → Triage → Assign → Start → Resolve → Confirm, cuối cùng `CONFIRMED`, Workflow version 4, history có 4 transition; Assign tăng assignmentVersion riêng. Bài PostgreSQL có điều kiện cần fixture độc quyền; browser ba người dùng Keycloak là acceptance khác. [HelpdeskHttpPostgresTest](../backend/src/test/java/com/tricore/dxos/infrastructure/workflow/HelpdeskHttpPostgresTest.java), [#118](https://github.com/tricore-opentrix/opentrix/issues/118).

**Lưu ý an toàn:** Các script trong tài liệu chi tiết có thể tạo container, volume, schema, role và chạy migration trên fixture. Không chạy khi chưa chứng minh sở hữu DB tạm và hiểu tác động; không tự xóa dữ liệu để sửa lỗi test.

### B. Mục tiêu — PROPOSED, chưa nghiệm thu

- **PROPOSED · [#118](https://github.com/tricore-opentrix/opentrix/issues/118):** hoàn tất golden path browser thực với ba người dùng Keycloak, BFF/Backend/PostgreSQL, các ca âm tính và kiểm tra tồn tại sau restart.
- **PROPOSED · [#112](https://github.com/tricore-opentrix/opentrix/issues/112):** kiểm thử spec OpenAPI xuất từ runtime, tính nhất quán route/schema/error; chưa có bằng chứng nghiệm thu từ runtime export.
- **PROPOSED · [#194](https://github.com/tricore-opentrix/opentrix/issues/194):** chuẩn hóa báo cáo theo SHA và phân loại `PASS / FAIL / SKIPPED / NOT RUN`, giữ link bằng chứng, có reviewer độc lập.
- **PROPOSED · [#190](https://github.com/tricore-opentrix/opentrix/issues/190):** không coi kết quả test đã có là release sign-off; các cổng phát hành cần được xét riêng.

**Mẫu báo cáo tối thiểu:** `SHA | môi trường | bộ test | lệnh | exit code | executed/passed/failed/skipped | nguồn log | trạng thái | hạn chế` — không tự điền số PASS chưa thu được.

## English

### A. Current state — source and Phase 2 evidence

**Scope:** The detailed sections below preserve the source-inspected contract and test boundaries. This documentation update performs no runtime execution. Compare with [Phase 2 Block C](09-evidence/phase-2/block-c-application.md).

#### 1. Overview and Testing Principles

This guide documents existing tests for developers, QA and reviewers. **Code/configuration baseline and local HEAD inspected:** `832c75fc3164cf170eed3bb8f1e380d24dd65aba`. The Phase 2 reports referenced below are pinned separately at `5938d8e7cb117aa6bc8226ace1d786be2f7be703`; the three intervening commits only add reports.

Use the local draft [DEVELOPMENT.md](DEVELOPMENT.md) for installation, startup and configuration. It is not present on `main` at the audited baseline; before publishing `TESTING.md`, ensure this relative link resolves on the intended branch/PR. No application tests, provisioning, migrations or database cleanup were executed to prepare this guide. All commands are **SOURCE-CONFIRMED**, not fresh execution evidence.

- **SOURCE-CONFIRMED:** the suite, command or condition is supported by inspected source/configuration; execution is not established.
- **VERIFIED:** a specific check succeeded at an identified SHA/environment, with retained output and an explicit scope. Source presence, local tool versions and an old CI result are insufficient for a new runtime claim.
- **UNVERIFIED:** the required execution or acceptance evidence has not been established.
- **PASS / FAIL / SKIPPED:** report actual case outcomes separately. Disabled tests and aborted assumptions are not passes. An expected rejection is PASS only when the test ran and asserted the rejection.

State the boundary of every result: an in-memory contract, MVC filter handoff, disposable PostgreSQL transaction, MOCK browser journey and authenticated LIVE E2E are different claims. Never infer integrated acceptance from a green build, a health response or a frontend bundle.

#### 2. Test Architecture

| Layer | Existing source and mechanism | Boundary |
| --- | --- | --- |
| Backend domain/contracts | [core tests](../backend/src/test/java/com/tricore/dxos/core/), JUnit/JUnit parameterized tests and AssertJ | Identity, Workflow and Data contracts; includes in-memory persistence/storage doubles |
| Backend HTTP/security | [gateway tests](../backend/src/test/java/com/tricore/dxos/gateway/), [identity security tests](../backend/src/test/java/com/tricore/dxos/infrastructure/identity/security/), Spring MVC/Test and controlled JWT fixtures | HTTP mapping, validation, authentication handoff and authorization; some token suites opt into a real issuer |
| Architecture | [CoreDependencyRulesTest](../backend/src/test/java/com/tricore/dxos/architecture/CoreDependencyRulesTest.java), ArchUnit | Compiled production Core classes, dependency rules and negative canaries |
| Portal BFF | [PortalSecurityTest](../portal-bff/src/test/java/com/tricore/dxos/portal/PortalSecurityTest.java), [PortalBackendClientTest](../portal-bff/src/test/java/com/tricore/dxos/portal/PortalBackendClientTest.java) | MockMvc, synthetic OAuth sessions, mocked authorized-client manager and HTTP client |
| Frontend | [frontend/src](../frontend/src/), Vitest/Testing Library in jsdom | Components, services, transports and session composition with fake/mocked responses |
| Browser | [frontend/tests](../frontend/tests/), Playwright Chromium and axe | MOCK Portal plus an explicitly selected fake Helpdesk preview |
| PostgreSQL | [Workflow infrastructure tests](../backend/src/test/java/com/tricore/dxos/infrastructure/workflow/), JDBC/Flyway and real local fixtures | Persistence, migrations, concurrency, privileges, TLS and HTTP/database integration |
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

Versions come from [Backend build](../backend/build.gradle), [wrapper properties](../backend/gradle/wrapper/gradle-wrapper.properties), [BFF build](../portal-bff/build.gradle), [frontend package](../frontend/package.json) and [Compose](../infra/compose.workflow-postgres.yml). Local version observations are not fresh-clone test results. Linux/macOS commands use the committed POSIX wrapper/CI conventions but were not executed for this guide. Windows fixture/ACL helpers must not be assumed portable.

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

Linux/macOS: use `./gradlew` with the same arguments. These are the three suites checked explicitly by CI; they do not establish real Keycloak/browser acceptance. Commands derive from [Gradle test tasks](../backend/build.gradle), [CI](../.github/workflows/ci.yml), [npm scripts](../frontend/package.json) and the [MVP config](../frontend/tests/mvp.playwright.config.ts).

#### 5. Backend Testing

The following matrix describes source-confirmed groups. `test --tests ...` commands run from **`backend/`**, using `./gradlew` on Linux/macOS or `.\gradlew.bat` on Windows. Runtime outcomes remain **UNVERIFIED** in this review.

| Test suite / source location | Task / selection | Dependencies | Environment | Execution condition | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- |
| [Core Identity/Workflow/Data](../backend/src/test/java/com/tricore/dxos/core/), including `WorkflowRuntimeTest`, `WorkflowPersistencePortTest`, `ObjectStoragePortTest` | `test --tests 'com.tricore.dxos.core.*'` | JDK/wrapper | No infrastructure opt-in | Ordinary JUnit cases; persistence/storage contracts include in-memory doubles | Fresh task XML/HTML | SOURCE-CONFIRMED |
| [HealthControllerTest](../backend/src/test/java/com/tricore/dxos/common/health/HealthControllerTest.java) | `test --tests com.tricore.dxos.common.health.HealthControllerTest` | JDK, MVC slice | Test configuration | No live DB required | XML/HTML | SOURCE-CONFIRMED |
| [Authorization policy tests](../backend/src/test/java/com/tricore/dxos/application/authorization/), including `WorkflowAuthorizationTest`, `TenantResourceWorkflowAccessPolicyTest` | `test --tests 'com.tricore.dxos.application.authorization.*'` | JDK, controlled snapshots/principals | No real tokens | Unit policy decisions, not database ACL execution | XML/HTML | SOURCE-CONFIRMED |
| [Security validators/handoff](../backend/src/test/java/com/tricore/dxos/infrastructure/identity/security/), excluding the two real-token suites below | `test`; focused CI selection above | JDK, controlled JWT/MockMvc fixtures | Gradle supplies fallback `OIDC_ISSUER_URI`, `OIDC_AUDIENCE`, `OIDC_RESOURCE_CLIENT_ID` for ordinary `test` | No real IdP required for these controlled tests | XML/HTML; CI's three-suite assertion | SOURCE-CONFIRMED |
| [WorkflowControllerTest](../backend/src/test/java/com/tricore/dxos/gateway/workflow/controller/WorkflowControllerTest.java), [WorkflowHttpExposureTest](../backend/src/test/java/com/tricore/dxos/gateway/workflow/controller/WorkflowHttpExposureTest.java), [HelpdeskErrorContractTest](../backend/src/test/java/com/tricore/dxos/gateway/helpdesk/HelpdeskErrorContractTest.java) | `test` | JDK/Spring test configuration | Controller suite selects `workflow-http-tests` internally | A test-only profile/controller registration is not production exposure | XML/HTML | SOURCE-CONFIRMED |
| [CoreDependencyRulesTest](../backend/src/test/java/com/tricore/dxos/architecture/CoreDependencyRulesTest.java) | Focused command above | Compiled production classes, ArchUnit | No DB/token | Imports production classes, excludes test fixtures; positive/negative canaries | XML/HTML and class-count/canary output | SOURCE-CONFIRMED |
| [OidcKeycloakIntegrationTest](../backend/src/test/java/com/tricore/dxos/infrastructure/identity/security/OidcKeycloakIntegrationTest.java), [GatewayKeycloakTokenHttpIntegrationTest](../backend/src/test/java/com/tricore/dxos/infrastructure/identity/security/GatewayKeycloakTokenHttpIntegrationTest.java) | `test --tests '*OidcKeycloakIntegrationTest' --tests '*GatewayKeycloakTokenHttpIntegrationTest'` | Real reachable Keycloak discovery/JWKS | `OIDC_TEST_ACCESS_TOKEN` | Both classes skip if token absent; exact issuer fixed below | XML/HTML, sanitized provider/environment record | SOURCE-CONFIRMED |

The architecture test enforces Core-only dependencies on `java..` and the same Core package, excludes JDBC, and forbids dependencies between Core capabilities. It does not enforce all proposed Application/Gateway rules or prove authorization semantics.

The real-token suites hardcode **`http://localhost:8180/realms/tricore`** and audience `tricore-api`. The principal mapping test expects the four exact Workflow authorities: `workflow:create`, `workflow:activate`, `workflow:read`, `workflow:transition`. A token from `127.0.0.1:8182` is not interchangeable, even if its realm/user looks identical. Do not change issuer validation to make a token fit. These tests verify decoder/filter behavior, not browser login or full Helpdesk persistence.

Windows-only launcher coverage is also conditional: `WorkflowRuntimePrivilegeAuditLauncherTest`, `WorkflowSecurityDefinerReviewLauncherTest`, `WorkflowApprovedSmokeLauncherTest`, and selected methods in `WorkflowApprovedMigrationTest` / `WorkflowSchemaBootstrapTest` use `@EnabledOnOs(WINDOWS)`. Their non-Windows skips must be reported. Launcher tests use rejection/stub fixtures; they do not authorize running the actual operator scripts.

#### 6. Portal BFF Testing

Run the BFF command in Quick Test Commands; no genuine provider credentials, Backend or database are needed for its test fixtures.

| Suite | Source-confirmed checks | Fixture and limitation |
| --- | --- | --- |
| [PortalSecurityTest](../portal-bff/src/test/java/com/tricore/dxos/portal/PortalSecurityTest.java) | Anonymous/forged-header rejection, session response without tokens, CSRF on writes/logout, PKCE authorization parameters, confidential-client restrictions, failed/missing authorization handling | `@WebMvcTest`, `oauth2Login()`, synthetic client registration, mocked manager/Backend; not a real Authorization Code callback or provider session |
| [PortalBackendClientTest](../portal-bff/src/test/java/com/tricore/dxos/portal/PortalBackendClientTest.java) | HTTPS/loopback origin validation, server-held bearer forwarding, denied redirects, route/method allowlist, bounded response bodies, session invalidation, controlled refresh outcomes, sanitized 401/403/404/409, unknown writes with no replay | Mocked Java `HttpClient` and authorized-client manager; no live upstream/refresh/provider logout |

`COMMIT_OUTCOME_UNKNOWN` tests deliberately model a lost response after a write and assert that it is not retried. They do not establish whether a real database committed. Reconcile live unknown outcomes through authorized detail/history reads, without replaying a POST.

Evidence is fresh `portal-bff/build/test-results/test/` XML and `portal-bff/build/reports/tests/test/` HTML. BFF live cookie behavior, HTTPS ingress, real refresh/logout and browser trust require separate acceptance against [BFF configuration/runbook](../portal-bff/README.md).

#### 7. Frontend Testing

| Suite / location | Command in `frontend/` | Dependencies / environment | Run/skip condition | Evidence | Status |
| --- | --- | --- | --- | --- | --- |
| `src/**/*.test.{ts,tsx}` selected by [vite.config.ts](../frontend/vite.config.ts) | `npm test` (`npm.cmd` on Windows) | Installed Node dependencies, jsdom; no infrastructure variables | Includes component/service/transport tests; test setup is `src/test/setup.ts` | Vitest terminal output; retain invocation and per-file summary | SOURCE-CONFIRMED |
| [portal.spec.ts](../frontend/tests/portal.spec.ts), [session.spec.ts](../frontend/tests/session.spec.ts), [auth.spec.ts](../frontend/tests/auth.spec.ts) | `npm run build`, then `npm run test:smoke` | Chromium, MOCK `dist`, free port 4173 | Standard config starts preview; can reuse an existing server outside CI, so verify its build/mode | List reporter, test output and retained failure trace/screenshots where produced | SOURCE-CONFIRMED |
| [helpdesk-mvp.spec.ts](../frontend/tests/helpdesk-mvp.spec.ts) | `npx playwright test --config tests/mvp.playwright.config.ts` (`npx.cmd` on Windows) | Chromium, explicit fake preview; no Backend/Keycloak/DB | Standard config intentionally skips it. Only MVP config supplies `project.metadata.fakeHelpdeskPreview=true` and selects this spec | List output plus the actual temporary output directory printed by the run | SOURCE-CONFIRMED |
| [check-security.mjs](../frontend/scripts/check-security.mjs) | `npm run check:security` after build | `src`, `public`, `dist`, package/index files present | Heuristic credential-pattern scan; not a test of runtime authorization or comprehensive secret detection | Terminal scan result and reviewed build mode | SOURCE-CONFIRMED |
| Authenticated local browser composition | Manual checklist in section 11 | Full configured stack and real identities | `integration-local` bundle alone is insufficient | Sanitized browser/backend/database evidence | UNVERIFIED |

[AssignmentForm.integration.test.tsx](../frontend/src/components/AssignmentForm.integration.test.tsx) composes UI/service/transport fixtures; [LocalHelpdeskIntegration.test.tsx](../frontend/src/features/helpdesk/LocalHelpdeskIntegration.test.tsx) stubs browser location/fetch. Their names do not imply live HTTP or Keycloak execution. Likewise, MOCK login/register form validation is not identity-provider authentication.

**Screenshot side effects:** when Playwright runs from `frontend/`, `tests/portal.spec.ts` can create or overwrite screenshots in `docs/evidence/issue39-portal/` at repository root; `tests/auth.spec.ts` does so in its `auth/` subdirectory. Run `git status --short` before and after the tests and review new or modified evidence files. Preserve existing evidence; do not automatically delete, clean or revert it.

The [standard Playwright config](../frontend/playwright.config.ts) uses a **list** reporter, Chromium, `http://127.0.0.1:4173` and `trace: retain-on-failure`; it does not configure an HTML report. The [MVP config](../frontend/tests/mvp.playwright.config.ts) starts a separate Vite server and allocates a temporary `dxos-app14-browser-*` output directory. Capture the actual artifact paths before temporary files disappear. An intentional Helpdesk skip under standard smoke is **SKIPPED**, never PASS.

`npm run build:integration-local` selects the integration entry in [src/main.tsx](../frontend/src/main.tsx). It only creates a bundle in `dist`; it does not start Backend/BFF/Keycloak/PostgreSQL/Caddy or prove that `/bff/session` works. Default `npm run build` restores MOCK. Both modes write the same output directory; record which one was tested.

#### 8. PostgreSQL and Infrastructure Testing

**Destructive fixture warning:** the commands in this section are only for a separately prepared, exclusively owned disposable database. No connection values or cloud commands are supplied here. Stop if fixture ownership, credentials, TLS or the actual target is uncertain. An environment variable enables a suite; it does not make a target safe.

##### Workflow suite selection and conditions

[backend/build.gradle](../backend/build.gradle) selects exactly seven classes for `workflowIntegrationTest`. The nine Workflow integration classes below share [this source directory](../backend/src/test/java/com/tricore/dxos/infrastructure/workflow/); each row links its actual file. All rows are **SOURCE-CONFIRMED**, with execution **UNVERIFIED** here.

| Test suite / location | Included in `workflowIntegrationTest`? | Class-level enabling variable | Additional fixture requirements / coverage |
| --- | --- | --- | --- |
| [PostgresWorkflowPersistenceIntegrationTest](../backend/src/test/java/com/tricore/dxos/infrastructure/workflow/PostgresWorkflowPersistenceIntegrationTest.java) | Yes | `WORKFLOW_TEST_JDBC_URL` nonempty | Runtime/migrator credentials, isolated schema migrations, atomicity/conflicts/history. Least-privilege case aborts via `Assumptions.assumeTrue` unless a distinct migration login is supplied |
| [WorkflowIsolationIntegrationTest](../backend/src/test/java/com/tricore/dxos/infrastructure/workflow/WorkflowIsolationIntegrationTest.java) | Yes | `WORKFLOW_TEST_JDBC_URL` nonempty | Schema/role/probe setup; some TLS cases gated separately by correct/wrong CA variables |
| [WorkflowEventTriggerGuardIntegrationTest](../backend/src/test/java/com/tricore/dxos/infrastructure/workflow/WorkflowEventTriggerGuardIntegrationTest.java) | Yes | `WORKFLOW_TEST_JDBC_URL` nonempty | Privileged synthetic catalog/event-trigger fixture; TLS cases additionally gated by CA variables |
| [WorkflowEventTriggerReviewIntegrationTest](../backend/src/test/java/com/tricore/dxos/infrastructure/workflow/WorkflowEventTriggerReviewIntegrationTest.java) | Yes | `WORKFLOW_TEST_CA_CERT` nonempty | Also needs Workflow JDBC URL and migration credentials; verified TLS plus protected filesystem/ACL capture |
| [WorkflowDevelopmentSmokeIntegrationTest](../backend/src/test/java/com/tricore/dxos/infrastructure/workflow/WorkflowDevelopmentSmokeIntegrationTest.java) | Yes | `WORKFLOW_AUDIT_LOCAL_JDBC_URL` nonempty | Local `/postgres` TLS fixture, audit credentials/CA, marker; builds local development opt-ins inside test setup |
| [WorkflowSchemaBootstrapIntegrationTest](../backend/src/test/java/com/tricore/dxos/infrastructure/workflow/WorkflowSchemaBootstrapIntegrationTest.java) | Yes | `WORKFLOW_AUDIT_LOCAL_JDBC_URL` nonempty | Local audit fixture, correct/wrong CA, marker; creates/drops fixture schemas/roles and checks bootstrap boundaries |
| [WorkflowApprovedMigrationIntegrationTest](../backend/src/test/java/com/tricore/dxos/infrastructure/workflow/WorkflowApprovedMigrationIntegrationTest.java) | Yes | `WORKFLOW_AUDIT_LOCAL_JDBC_URL` nonempty | Local audit fixture, TLS and disposable marker; tests pinned V3/V4 migration and failure boundaries |
| [WorkflowRuntimePrivilegeAuditIntegrationTest](../backend/src/test/java/com/tricore/dxos/infrastructure/workflow/WorkflowRuntimePrivilegeAuditIntegrationTest.java) | **No**; selected through ordinary `test` | `WORKFLOW_AUDIT_LOCAL_JDBC_URL` nonempty | Audit fixture credentials/correct and wrong CA; read-only audit and TLS rejection cases |
| [WorkflowSecurityDefinerReviewIntegrationTest](../backend/src/test/java/com/tricore/dxos/infrastructure/workflow/WorkflowSecurityDefinerReviewIntegrationTest.java) | **No**; selected through ordinary `test` | `WORKFLOW_AUDIT_LOCAL_JDBC_URL` nonempty | Audit fixture/TLS; setup itself creates disposable SQL objects even though capture is read-only |

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

[Compose](../infra/compose.workflow-postgres.yml) provides a persistent Workflow database at loopback port 55425, not a complete TLS/audit/Helpdesk fixture. Do not point `HELPDESK_DISPOSABLE_URL` at it or assume its owner login verifies a least-privilege runtime. Do not edit applied V1–V4 migrations or disable catalog/privilege guards to satisfy tests.

##### Helpdesk HTTP/PostgreSQL and real-token B06

[HelpdeskHttpPostgresTest](../backend/src/test/java/com/tricore/dxos/infrastructure/workflow/HelpdeskHttpPostgresTest.java) is class-gated on exactly `HELPDESK_DISPOSABLE_URL=jdbc:postgresql://127.0.0.1:55439/helpdesk_disposable_test`. It also needs `HELPDESK_DISPOSABLE_PASSWORD`, the expected fixture login `helpdesk_test`, and `WORKFLOW_EVENT_GUARD_LOCAL_DISPOSABLE=true`. Setup generates a synthetic issuer/JWKS and an ephemeral HTTP server; most cases are real HTTP/database integration with fake identity-provider data, not real Keycloak.

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

[.github/workflows/ci.yml](../.github/workflows/ci.yml) declares:

| Job | Tests/checks run | What it does not establish |
| --- | --- | --- |
| `backend` | JDK21 `./gradlew build --no-daemon --stacktrace --rerun-tasks`; parses PKCE PowerShell syntax; checks XML for `GatewayIdentityHandoffHttpTest`, `SpringSecurityCurrentPrincipalTest`, `WorkflowHttpExposureTest` | No PostgreSQL/Keycloak fixture is provisioned; opt-in cases can skip; syntax parsing does not execute PKCE login |
| `portal-bff` | `./backend/gradlew -p portal-bff build --no-daemon --stacktrace` | Real provider, ingress, browser or database acceptance |
| `frontend` | Node22 `npm ci`, `npm run build`, `npm test` | Does not run Playwright, security scan or `build:integration-local` |
| `r23-compliance` | Wrapper validation; Python R23 rejection canary; Java/npm SBOM/license/notices checks | Product runtime, browser or DB E2E |
| `repo-hygiene` | Requires R23 success; PR-title/metadata, wrapper mode and REUSE checks | Runtime integration or release acceptance |

The explicit Backend XML check requires each of its three suites to exist, contain tests and have zero failures/errors/skips. It does **not** assert that every integration suite executed. Backend HTML test reports are uploaded **on failure**, with seven-day retention; successful-run per-suite XML is not generally uploaded by this workflow. Capture needed evidence separately rather than assuming a green job preserves all counts. R23 artifacts are separate compliance evidence.

Repository tooling canaries can run independently: from root, CI uses `python3 -m unittest discover -s scripts -p 'test_r23_*.py'`; use the available Python executable with the same arguments on Windows. These tests use synthetic SBOM fixtures, not product services. The separate [release workflow](../.github/workflows/release.yml) has its own gates; it is not LIVE E2E proof and is not invoked by this guide.

The standalone [test-helpdesk-local-actor-seed.ps1](../scripts/test-helpdesk-local-actor-seed.ps1) runs from root as `.\scripts\test-helpdesk-local-actor-seed.ps1` in PowerShell without Docker or a database. It asserts canonical identity/seed generation and rejection behavior using synthetic subjects and a temporary local JSON file; it does not provision identities or authenticate with Keycloak. Invocation and assertions are **SOURCE-CONFIRMED**, not execution results here.

Phase 2 reports contain historical exact-SHA CI observations. Keep those attributions distinct from a new local run, do not infer unrecorded counts, and do not treat a report-only commit as new runtime validation.

#### 11. LIVE E2E Acceptance

**UNVERIFIED in this review.** No automated Playwright configuration inspected here supplies full-stack real-provider acceptance. Follow the [BFF acceptance checklist](../portal-bff/README.md) and [local configuration guide](DEVELOPMENT.md) before executing this manual plan.

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
- [Helpdesk local runbook](../scripts/README-helpdesk-local.md), [script notes](../scripts/README.md), [CI](../.github/workflows/ci.yml).
- Phase 2 published snapshots at `5938d8e7cb117aa6bc8226ace1d786be2f7be703`: [Block A](https://github.com/tricore-opentrix/opentrix/blob/5938d8e7cb117aa6bc8226ace1d786be2f7be703/docs/09-evidence/phase-2/block-a-architecture.md), [Block B](https://github.com/tricore-opentrix/opentrix/blob/5938d8e7cb117aa6bc8226ace1d786be2f7be703/docs/09-evidence/phase-2/block-b-backend-infra.md), [Block C](https://github.com/tricore-opentrix/opentrix/blob/5938d8e7cb117aa6bc8226ace1d786be2f7be703/docs/09-evidence/phase-2/block-c-application.md). Reports are evidence inventories with their own limitations, not new runtime acceptance.

### B. Target — PROPOSED, not yet accepted

- **PROPOSED · [#118](https://github.com/tricore-opentrix/opentrix/issues/118):** capture same-SHA authenticated live end-to-end evidence for all six Helpdesk steps, negative authorization cases and restart persistence.
- **PROPOSED · [#112](https://github.com/tricore-opentrix/opentrix/issues/112):** check runtime OpenAPI route/schema/error parity after the spec is exported and independently reviewed.
- **PROPOSED · [#194](https://github.com/tricore-opentrix/opentrix/issues/194):** provide repeatable test logs, pass/fail/skip counts and an independent reviewer record.

**Publication gate:** Link validation, matched source SHA, real test outputs, SPDX/REUSE check and independent review are required; none is claimed PASS by this document edit.
