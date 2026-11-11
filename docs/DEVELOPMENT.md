<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors

SPDX-License-Identifier: Apache-2.0
-->

# Hướng dẫn phát triển / Development guide

> **Trạng thái / Status:** 📝 Bản nháp chờ review / Draft for review · **Owner:** @lexuanbao258-collab · **Issue:** [#194](https://github.com/tricore-opentrix/opentrix/issues/194), [#197](https://github.com/tricore-opentrix/opentrix/issues/197)
>
> **Source SHA:** `d98aa6f6f8b05add9cf90b67739681eae4e41176` (`main`). So với baseline kiểm kê Giai đoạn 2 `832c75fc3164cf170eed3bb8f1e380d24dd65aba`, các commit sau chỉ thêm/đổi tài liệu dưới `docs/`; mã và cấu hình không đổi (`git diff --name-only 832c75f HEAD`). / Compared with the Phase 2 audit baseline `832c75f…`, later commits touch only `docs/`; code and configuration are unchanged.

## Tiếng Việt

### Nhãn bằng chứng

| Nhãn | Ý nghĩa |
|---|---|
| **AS-IS** | Có trong source/cấu hình tại SHA trên và đã được đối chiếu bằng cách đọc file. **Chưa** nghĩa là lệnh đã được chạy thành công. |
| **UNVERIFIED** | Chưa có bằng chứng chạy/nghiệm thu. Không được hiểu là PASS. |
| **PROPOSED (#N)** | Đề xuất/mục tiêu, kèm số Issue theo dõi. Không phải hiện trạng. |

Tài liệu này **không** chạy build, test, database hay dịch vụ nào. Mọi lệnh bên dưới là AS-IS theo source (chưa thực thi khi soạn). Môi trường mẫu của lần kiểm kê trước ghi Java 21.0.11, Node.js 24.19.0, npm 11.17.0: chỉ là phiên bản công cụ, không chứng minh cài đặt hay build từ clone mới. Chưa chạy trên Linux/macOS: **UNVERIFIED**.

### 1. Yêu cầu môi trường

| Công cụ | Yêu cầu | Nguồn (AS-IS) |
|---|---|---|
| Git | Clone và kiểm tra commit | — |
| JDK | **21**; đặt `JAVA_HOME`, thêm `bin` vào `PATH` | `backend/build.gradle`, `portal-bff/build.gradle` (toolchain 21), CI Temurin 21 |
| Gradle | Dùng Wrapper **8.14.3** trong `backend/`; không cài Gradle riêng | `backend/gradle/wrapper/gradle-wrapper.properties` |
| Node.js | **>= 22.12.0**; CI dùng major 22 | `frontend/package.json` (`engines`), `ci.yml` |
| npm | Cần; không ghi phiên bản cụ thể. Giữ `package-lock.json` | `frontend/package-lock.json` |
| PostgreSQL | Không cần cho Portal MOCK và test thường. Fixture/Compose dùng `postgres:17.11-alpine` | `infra/compose.workflow-postgres.yml` |
| Docker | Chỉ cần cho fixture database; runbook Helpdesk yêu cầu Docker Desktop Linux Engine, context `desktop-linux` | `scripts/README-helpdesk-local.md` |
| PowerShell | 5.1 hoặc 7 cho các script `.ps1` | `scripts/` |
| OpenSSL | `workflow-verify-local.ps1` cần (tìm `openssl.exe` hoặc bản của Git for Windows) | `backend/README.md` |
| Keycloak, Caddy | Chỉ cho luồng đăng nhập thật cục bộ; tự cài và cấu hình thủ công | `portal-bff/README.md` |

Lần build đầu cần Internet để tải Gradle, dependency và (cho smoke test) trình duyệt Playwright.

**Windows và Linux:** script provisioning Helpdesk/Workflow (`scripts/*.ps1`) là PowerShell, runbook nhắm Windows + Docker Desktop. Script Linux/macOS tương đương: **NOT AVAILABLE** tại SHA này (hiện trạng). Việc demo stack đa nền tảng được theo dõi riêng tại [#119](https://github.com/tricore-opentrix/opentrix/issues/119) (PROPOSED), không phải script đã có. Build/test Gradle và npm dùng được ở cả hai hệ điều hành theo Wrapper POSIX và CI Ubuntu 24.04 (**UNVERIFIED** trên máy Linux cục bộ).

### 2. Clone và cấu hình

Cấu trúc thư mục (AS-IS):

```text
backend/     Java 21, Spring Boot 3.5.16, Gradle Groovy, modular monolith (com.tricore.dxos)
portal-bff/  Spring Boot riêng: ranh giới OAuth/session + Caddyfile.local
frontend/    React 19, Vite 8, TypeScript, Vitest, Playwright
infra/       Compose PostgreSQL cho Workflow; Dockerfile đóng gói release
scripts/     Script setup/verify local (PowerShell), tuân thủ R23/R24 (Python)
docs/        Tài liệu, ADR, bằng chứng
```

`backend/` và `portal-bff/` là hai project Gradle độc lập, không phải subproject của một root. BFF dùng Wrapper của backend qua `-p portal-bff`.

**Windows PowerShell:**

```powershell
git clone https://github.com/tricore-opentrix/opentrix.git
Set-Location opentrix
git rev-parse HEAD
java -version
node --version
npm.cmd --version
```

**Linux/macOS:**

```sh
git clone https://github.com/tricore-opentrix/opentrix.git
cd opentrix
git rev-parse HEAD
java -version
node --version
npm --version
```

#### Cấu hình

[`.env.example`](../.env.example) chỉ là mẫu. Spring Boot **không** tự đọc `.env`; đặt biến vào môi trường của process (IDE, secret manager). Không commit `.env`, mật khẩu, token. Không đặt mật khẩu trong tham số lệnh.

| Thành phần | Biến (AS-IS, từ `application.yml` và runbook) |
|---|---|
| Backend datasource | `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` (không có giá trị mặc định) |
| Backend OIDC | `OIDC_ISSUER_URI`, `OIDC_AUDIENCE`, `OIDC_RESOURCE_CLIENT_ID` (không mặc định trong `application.yml`) |
| Workflow runtime | `DXOS_WORKFLOW_SCHEMA`, `currentSchema` khớp, `SPRING_FLYWAY_ENABLED=false` sau khi provision riêng |
| Helpdesk local | `DXOS_HELPDESK_ENABLED`, `DXOS_HELPDESK_JDBCURL`, `DXOS_HELPDESK_USERNAME`, `DXOS_HELPDESK_PASSWORD`, `DXOS_HELPDESK_SCHEMA`, `DXOS_HELPDESK_TENANT` — dùng đúng khối trong runbook |
| Portal BFF | `PORTAL_PUBLIC_ORIGIN`, `PORTAL_BACKEND_BASE_URL`, `PORTAL_OIDC_ISSUER_URI`, `PORTAL_OIDC_CLIENT_ID`, `PORTAL_OIDC_CLIENT_SECRET`, `PORTAL_OIDC_REDIRECT_URI`, `SERVER_PORT=8081` |
| Compose Workflow | `WORKFLOW_LOCAL_DB_PASSWORD` |
| Frontend MOCK | Không cần biến nào |

`.env.example` dùng issuer `http://localhost:8180/realms/tricore`, còn runbook BFF dùng `http://127.0.0.1:8182/realms/tricore`. Hai issuer là hai danh tính khác nhau; không trộn token/subject. Mẫu này không chứng minh Keycloak đã tồn tại.

### 3. Chạy local trên Windows và Linux

Hai chế độ chạy cục bộ và một cổng nghiệm thu (AS-IS về thiết kế; chạy thực tế **UNVERIFIED**):

| Chế độ / cổng | Cung cấp | Không chứng minh |
|---|---|---|
| MOCK (chế độ chạy) | Portal với dữ liệu giả trong bộ nhớ | Phân quyền backend, SSO, lưu trữ |
| integration-local (chế độ chạy) | Build `integration-local` + HTTPS (Caddy) + BFF + Backend + định danh thật + DB dùng một lần | Nghiệm thu trình duyệt |
| LIVE E2E (cổng nghiệm thu, không phải chế độ chạy độc lập) | Bằng chứng hành trình trình duyệt có xác thực, thu được từ stack integration-local | **UNVERIFIED**; theo dõi tại [#118](https://github.com/tricore-opentrix/opentrix/issues/118) |

#### 3.1 Portal MOCK (không cần Java/DB)

Từ `frontend/`:

```powershell
npm.cmd ci
npm.cmd run dev
```

```sh
npm ci
npm run dev
```

Mở `http://127.0.0.1:5173` (script `dev` dùng `vite --host 127.0.0.1`). Dữ liệu mất khi tải lại. Persona, login/register chỉ là xem trước giao diện, không xác thực.

Build và kiểm tra (cùng thư mục; Linux dùng `npm`):

```powershell
npm.cmd run build
npm.cmd test
npm.cmd run check:security
```

`build` chạy `tsc --noEmit` rồi `vite build`. `npm.cmd run build:integration-local` chọn entry tích hợp BFF; cả hai build cùng ghi `frontend/dist`, nên build đúng chế độ ngay trước khi phục vụ.

#### 3.2 Backend

Từ `backend/`:

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

`build` đã gồm test và đóng gói. Phiên bản project là `0.1.0` (`rootProject.name = dxos-backend`), nên JAR nằm ở `backend/build/libs/`; tên JAR cũ `dxos-backend-0.0.1-SNAPSHOT.jar` chỉ thuộc bản ghi lịch sử; [Backend README](../backend/README.md) đã ghi tên suy ra `dxos-backend-0.1.0.jar` (chưa xác minh build). Test thường không cần PostgreSQL: `build.gradle` cấp giá trị OIDC mặc định cho test.

Chạy ứng dụng (`bootRun`) cần database đã provision và biến OIDC. **Chỉ `DB_*` là chưa đủ.** Spring Boot có Flyway; các runbook provision riêng và đặt `SPRING_FLYWAY_ENABLED=false`. Không trỏ lần khởi động chưa review vào database dùng chung. Chọn **một** đường đi đầy đủ:

- Workflow cục bộ: [runbook Workflow hiện hành](../backend/docs/local-workflow-runbook.md) (checklist an toàn). [Lệnh vận hành gốc](../backend/legacy-workflow-runbook.md) đã chuyển sang lưu trữ lịch sử, không chạy trực tiếp.
- Helpdesk cục bộ: [scripts/README-helpdesk-local.md](../scripts/README-helpdesk-local.md).

Sau khi môi trường sẵn sàng, từ `backend/`: `.\gradlew.bat bootRun` (Windows) hoặc `./gradlew bootRun` (Linux). Kiểm tra: `Invoke-RestMethod -Uri 'http://localhost:8080/api/v1/health'` → `{"status":"UP"}`. Endpoint này không truy vấn PostgreSQL; nó không chứng minh persistence hay phân quyền. Actuator chỉ mở `/actuator/health`, không chi tiết.

Helpdesk API hỗ trợ là `/api/v1/mvp/requests` (khi `dxos.helpdesk.enabled=true`). Route `/api/v1/requests/*` cũ đã bị gỡ.

#### 3.3 Portal BFF

Từ thư mục gốc repo:

```powershell
.\backend\gradlew.bat -p portal-bff test
.\backend\gradlew.bat -p portal-bff build
```

```sh
./backend/gradlew -p portal-bff test
./backend/gradlew -p portal-bff build
```

Test dùng fixture có kiểm soát (PKCE, CSRF, kiểm tra origin, bearer forwarding, từ chối redirect, không retry ghi). Chúng không chứng minh đăng nhập Keycloak thật, refresh, logout phía provider hay lưu trữ qua trình duyệt. Chạy đăng nhập thật cục bộ: làm theo từng bước trong [portal-bff/README.md](../portal-bff/README.md) (client Keycloak confidential + PKCE S256, issuer thống nhất, build `integration-local`, `bootRun` BFF, `caddy validate`/`caddy run` với [Caddyfile.local](../portal-bff/Caddyfile.local) tại `https://localhost:8443`). Nghiệm thu trình duyệt thật ở README đó ghi **NOT RUN / BLOCKED** → **UNVERIFIED**.

#### 3.4 Database và hạ tầng

- Không có Compose full-stack. [infra/compose.workflow-postgres.yml](../infra/compose.workflow-postgres.yml) chỉ tạo PostgreSQL cho Workflow (`postgres:17.11-alpine`, `127.0.0.1:55425`, named volume). Cần `WORKFLOW_LOCAL_DB_PASSWORD` qua kênh bảo mật; dùng lại volume thì giữ mật khẩu cũ.
- Helpdesk: làm theo runbook; preflight chỉ đọc là `.\scripts\helpdesk-local-setup.ps1 -RunId <id mới>` từ thư mục gốc. Bước `-Execute -ConfirmDemoDatabase` tạo container/volume mới và ghi schema — đọc runbook trước.
- Flyway V1–V4 là lịch sử bất biến. Không chạy lại launcher cloud bootstrap/migration/smoke như bước setup local. Không bỏ qua guard cấu hình Helpdesk để dùng DB dùng chung.
- Dockerfile trong `infra/release/` chỉ là đầu vào đóng gói, không phải stack triển khai (xem [DEPLOYMENT.md](DEPLOYMENT.md)).

### 4. Quy trình phát triển

#### 4.1 Kiểm thử (AS-IS: lệnh; kết quả **UNVERIFIED** nếu bạn chưa chạy)

| Kiểm tra | Lệnh / thư mục | Ghi chú |
|---|---|---|
| Backend | `./gradlew test` trong `backend/` | Test đơn vị, MVC, kiến trúc; ca cần DB/token thật có thể bị skip |
| Ranh giới Core | `./gradlew test --tests com.tricore.dxos.architecture.CoreDependencyRulesTest` | Chỉ kiểm quy tắc phụ thuộc của Core |
| BFF | `./backend/gradlew -p portal-bff test` (gốc repo) | Fixture, không cần IdP thật |
| Frontend | `npm test` trong `frontend/` | Vitest (jsdom) |
| Quét bảo mật frontend | `npm run check:security` | Kiểm tra mẫu, không phải audit đầy đủ |
| Workflow PostgreSQL | `./gradlew workflowIntegrationTest --no-daemon` trong `backend/` | Cần `WORKFLOW_TEST_JDBC_URL`, `WORKFLOW_TEST_DB_USER`, `WORKFLOW_TEST_DB_PASSWORD`; dùng DB loopback dùng một lần; task fail nếu thiếu biến |
| Helpdesk local | `scripts/helpdesk-negative-local.ps1 -RunId <id>` | Docker Desktop; JWKS giả; tạo và giữ tài nguyên mới |
| Token Keycloak thật | `OIDC_TEST_ACCESS_TOKEN` + `test` | Issuer cố định `http://localhost:8180/realms/tricore` |

Playwright (từ `frontend/`, sau khi `npm run build`):

```powershell
npx.cmd playwright install chromium
npm.cmd run test:smoke
npx.cmd playwright test --config tests/mvp.playwright.config.ts
```

Cấu hình chuẩn chạy preview tại `127.0.0.1:4173` (`--strictPort`); giải phóng cổng này trước. `helpdesk-mvp.spec.ts` tự skip dưới cấu hình chuẩn; chỉ `tests/mvp.playwright.config.ts` bật nó. Báo cáo ca skip là **SKIPPED**, không phải PASS. Cả hai đều dùng dữ liệu/transport giả, không phải LIVE E2E.

Đọc báo cáo mới trong `build/test-results/test/` và `build/reports/tests/test/` của từng project Java. Ghi lại commit, lệnh, fixture, số ca chạy/skip. Build thành công khi test DB bị skip **không** phải bằng chứng PostgreSQL đã được kiểm.

`scripts/workflow-verify-local.ps1` dựng fixture TLS rồi chạy `test build`, yêu cầu 0 skip toàn bộ. Việc nó đủ làm lệnh xác minh duy nhất tại SHA này là **UNVERIFIED** (các ca Helpdesk/Keycloak có cờ opt-in riêng mà nó không cấp). Không nới guard hay tính ca skip là PASS.

Kết quả kiểm thử đã ghi trong README là bằng chứng lịch sử theo lần chạy đó, không phải kết quả của SHA hiện tại. Con số 999 tests/992 passed trong `portal-bff/README.md` là kết quả chạy `test` của **Backend** (bằng chứng Backend lịch sử, ghi trong README của BFF), không phải số lượng test của BFF; 752 PASS trong `backend/README.md` cũng là lần chạy lịch sử khác.

#### 4.2 Quy tắc mã nguồn (AS-IS)

- Backend là modular monolith; Core cung cấp cơ chế, application sở hữu nghiệp vụ. Code nhà cung cấp nằm ở `infrastructure`.
- `CoreDependencyRulesTest` ép Core chỉ phụ thuộc `java..` và package Core, loại JDBC, cấm phụ thuộc chéo giữa ba năng lực Core. Quy tắc Application/Gateway nêu trong tài liệu thiết kế chưa được test này ép hết.
- Không tin vai trò/identity từ trình duyệt; backend giữ quyền quyết định. Giữ ghi nguyên tử, version lạc quan; không retry mù khi `COMMIT_OUTCOME_UNKNOWN` — đọc chi tiết/lịch sử có quyền để đối soát.
- Workflow HTTP controller chưa đăng ký production; không bật khi chưa có security gate.
- [.editorconfig](../.editorconfig): UTF-8, LF, thụt 4 dấu cách cho Java/Gradle/SQL, 2 dấu cách mặc định; `.ps1/.bat/.cmd` dùng CRLF. Thêm SPDX vào file mới.

#### 4.3 Git và Pull Request (theo [CONTRIBUTING.md](../CONTRIBUTING.md), AS-IS)

1. Công việc quá ~2 giờ cần Issue; thay đổi lớn về API/kiến trúc/bảo mật/lưu trữ thảo luận trước.
2. Nhánh từ `main` dạng `<type>/<area>-<description>`; không push thẳng `main`/`gh-pages`.
3. Conventional Commits cho commit và tiêu đề PR; PR nháp, khoảng 400 dòng; `Refs #N` cho phần dở, `Closes #N` chỉ khi đủ tiêu chí.
4. Chạy kiểm tra liên quan, ghi lệnh/kết quả/điểm bỏ sót; cần review độc lập theo [CODEOWNERS](../.github/CODEOWNERS).
5. Squash merge sau khi CI và review đạt.

CI ([ci.yml](../.github/workflows/ci.yml)): `backend`, `portal-bff`, `frontend`, `r23-compliance`, `repo-hygiene`. Backend và BFF build trên JDK 21 (Ubuntu 24.04); frontend `npm ci`, `npm run build`, `npm test` trên Node 22; R23 sinh SBOM và kiểm giấy phép/notice; hygiene kiểm tiêu đề PR, bit thực thi của `gradlew`, REUSE. Tiêu đề PR sai thì CI fail; thiếu `Closes #N` hoặc >400 dòng chỉ cảnh báo. CI không chạy Playwright hay `build:integration-local`, và không dựng Keycloak/PostgreSQL. Thiết lập branch protection: **UNVERIFIED** (chỉ đọc YAML).

#### 4.4 Mục tiêu (PROPOSED)

| Mục | Issue |
|---|---|
| Nghiệm thu trình duyệt Keycloak → BFF → Backend → PostgreSQL | PROPOSED ([#118](https://github.com/tricore-opentrix/opentrix/issues/118)) |
| Quyết định object storage thay thế MinIO (chưa có adapter production) | PROPOSED ([#181](https://github.com/tricore-opentrix/opentrix/issues/181)) |
| Kiểm chứng OpenAPI tại runtime | PROPOSED ([#112](https://github.com/tricore-opentrix/opentrix/issues/112), theo báo cáo Block C) |
| Xác minh nguồn gốc/quyền tác giả | PROPOSED ([#138](https://github.com/tricore-opentrix/opentrix/issues/138)) |
| Tích hợp Flowable (engine hiện tại là `WorkflowRuntime` tự viết) | PROPOSED ([#191](https://github.com/tricore-opentrix/opentrix/issues/191)) |
| Tích hợp APISIX (hiện dùng Spring MVC/Security và allowlist của BFF) | PROPOSED ([#116](https://github.com/tricore-opentrix/opentrix/issues/116)) |
| Playwright trong CI (job `frontend` chưa chạy Playwright) | PROPOSED ([#132](https://github.com/tricore-opentrix/opentrix/issues/132)) |

Flowable, APISIX và provider object storage chưa được tích hợp vào runtime được chấp nhận; báo cáo Phase 2 chỉ xác minh được điều này, không kết luận công nghệ hoàn toàn vắng mặt khỏi mã. Xem [Block A](09-evidence/phase-2/block-a-architecture.md), [Block B](09-evidence/phase-2/block-b-backend-infra.md) và [Block C](09-evidence/phase-2/block-c-application.md) (ứng dụng/Portal/BFF, bằng chứng cho #118 và #112). Không coi chúng là điều kiện hay năng lực hiện có.

### 5. Xử lý sự cố

| Triệu chứng | Kiểm tra / hành động |
|---|---|
| Sai Java hoặc Wrapper lỗi | So `java -version`, `JAVA_HOME`, `PATH`; dùng JDK 21 và Wrapper đã commit |
| `./gradlew` permission denied (Linux) | Git index ghi `backend/gradlew` mode `100755`; kiểm quyền/line ending khi checkout |
| PowerShell chặn `npm.ps1` | Dùng `npm.cmd`/`npx.cmd` |
| Lỗi engine Node hoặc dependency | Node >= 22.12; `npm ci` với lockfile; không tái tạo lockfile chỉ để qua lỗi |
| Biến trong `.env` không có tác dụng | Spring không đọc `.env`; đặt vào môi trường process |
| Backend không khởi động | Kiểm `DB_*`, `OIDC_*`, `DXOS_WORKFLOW_SCHEMA`, `currentSchema`, trạng thái migration, quyền runtime |
| Route Helpdesk thiếu / guard từ chối | Kiểm `DXOS_HELPDESK_ENABLED`, các biến Helpdesk, địa chỉ loopback, tên DB `helpdesk_disposable_*`, login `helpdesk_runtime_*`; không tắt guard |
| Đăng nhập PostgreSQL lỗi khi dùng lại volume | Giữ mật khẩu gốc; đổi biến Compose không reset mật khẩu của DB đã khởi tạo |
| Build xanh nhưng test DB bị skip | Kiểm biến môi trường và báo cáo mới; skip không phải PASS |
| Lỗi issuer/audience Keycloak hoặc 404 ẩn | So issuer theo đúng ký tự (host/port); kiểm audience, `resource_access.tricore-api.roles`, membership và ACL |
| BFF 502, login lỗi, CSRF 403 | Kiểm Backend/BFF (cổng 8081), origin/callback HTTPS, client secret, tin cậy CA, header `X-CSRF-TOKEN`; không bỏ qua TLS/CSRF |
| Deep link lỗi hoặc Portal hiện MOCK | Caddy phải phục vụ `frontend/dist` có SPA fallback; build đúng chế độ |
| Playwright không chạy | `npx playwright install chromium`, build MOCK, kiểm cổng 4173 |
| Kết quả ghi không rõ | Đọc chi tiết/lịch sử có quyền để đối soát; không replay POST, không chạy lại migration/smoke |
| Mất dữ liệu DB | Không dùng `down -v`/xóa volume để "sửa" setup; test DB tạo và xóa đối tượng fixture, chỉ dùng DB dùng một lần |

Chi tiết: [Backend](../backend/README.md), [BFF](../portal-bff/README.md), [Frontend](../frontend/README.md), [Helpdesk local](../scripts/README-helpdesk-local.md), [Kiến trúc](ARCHITECTURE.md), [Kiểm thử](TESTING.md), [Triển khai](DEPLOYMENT.md).

## English

### Evidence labels

| Label | Meaning |
|---|---|
| **AS-IS** | Present in source/config at the SHA above and cross-checked by reading files. It does **not** mean the command was run successfully. |
| **UNVERIFIED** | No run/acceptance evidence. Never read as PASS. |
| **PROPOSED (#N)** | Target/proposal with a tracking Issue. Not current state. |

This document ran **no** build, test, database or service. All commands below are AS-IS per source (not executed while drafting). The earlier audit machine reported Java 21.0.11, Node.js 24.19.0, npm 11.17.0: tool versions only, not evidence of a fresh-clone install or build. Execution on Linux/macOS: **UNVERIFIED**.

### 1. Prerequisites

| Tool | Requirement | Source (AS-IS) |
|---|---|---|
| Git | Clone and inspect the commit | — |
| JDK | **21**; set `JAVA_HOME`, put `bin` on `PATH` | `backend/build.gradle`, `portal-bff/build.gradle` (toolchain 21), CI Temurin 21 |
| Gradle | Use Wrapper **8.14.3** in `backend/`; no separate install | `backend/gradle/wrapper/gradle-wrapper.properties` |
| Node.js | **>= 22.12.0**; CI uses major 22 | `frontend/package.json` (`engines`), `ci.yml` |
| npm | Required; no exact version declared. Keep `package-lock.json` | `frontend/package-lock.json` |
| PostgreSQL | Not needed for the MOCK Portal or ordinary tests. Fixtures/Compose use `postgres:17.11-alpine` | `infra/compose.workflow-postgres.yml` |
| Docker | Only for database fixtures; the Helpdesk runbook requires Docker Desktop Linux Engine, context `desktop-linux` | `scripts/README-helpdesk-local.md` |
| PowerShell | 5.1 or 7 for the `.ps1` scripts | `scripts/` |
| OpenSSL | Needed by `workflow-verify-local.ps1` (finds `openssl.exe` or Git for Windows' copy) | `backend/README.md` |
| Keycloak, Caddy | Only for the real local login flow; install and configure manually | `portal-bff/README.md` |

The first build needs Internet for Gradle, dependencies and (for smoke tests) the Playwright browser.

**Windows and Linux:** the Helpdesk/Workflow provisioning scripts (`scripts/*.ps1`) are PowerShell and the runbooks target Windows + Docker Desktop. An equivalent Linux/macOS script is **NOT AVAILABLE** at this SHA (current state). A cross-platform demo stack is tracked separately in [#119](https://github.com/tricore-opentrix/opentrix/issues/119) (PROPOSED); it is not an existing script. Gradle and npm builds/tests work on both OSes per the POSIX Wrapper and the Ubuntu 24.04 CI (**UNVERIFIED** on a local Linux machine).

### 2. Clone and configure

Layout (AS-IS):

```text
backend/     Java 21, Spring Boot 3.5.16, Gradle Groovy, modular monolith (com.tricore.dxos)
portal-bff/  Separate Spring Boot app: OAuth/session boundary + Caddyfile.local
frontend/    React 19, Vite 8, TypeScript, Vitest, Playwright
infra/       Workflow PostgreSQL Compose; release packaging Dockerfiles
scripts/     Local setup/verify scripts (PowerShell), R23/R24 compliance (Python)
docs/        Documentation, ADRs, evidence
```

`backend/` and `portal-bff/` are independent Gradle projects, not subprojects of one root. The BFF reuses the backend Wrapper via `-p portal-bff`.

**Windows PowerShell:**

```powershell
git clone https://github.com/tricore-opentrix/opentrix.git
Set-Location opentrix
git rev-parse HEAD
java -version
node --version
npm.cmd --version
```

**Linux/macOS:**

```sh
git clone https://github.com/tricore-opentrix/opentrix.git
cd opentrix
git rev-parse HEAD
java -version
node --version
npm --version
```

#### Configuration

[`.env.example`](../.env.example) is a template only. Spring Boot does **not** read `.env`; set variables in the process environment (IDE, secret manager). Never commit `.env`, passwords or tokens. Never put passwords in command arguments.

| Component | Variables (AS-IS, from `application.yml` and runbooks) |
|---|---|
| Backend datasource | `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` (no defaults) |
| Backend OIDC | `OIDC_ISSUER_URI`, `OIDC_AUDIENCE`, `OIDC_RESOURCE_CLIENT_ID` (no defaults in `application.yml`) |
| Workflow runtime | `DXOS_WORKFLOW_SCHEMA`, matching `currentSchema`, `SPRING_FLYWAY_ENABLED=false` after separate provisioning |
| Helpdesk local | `DXOS_HELPDESK_ENABLED`, `DXOS_HELPDESK_JDBCURL`, `DXOS_HELPDESK_USERNAME`, `DXOS_HELPDESK_PASSWORD`, `DXOS_HELPDESK_SCHEMA`, `DXOS_HELPDESK_TENANT` — use the exact block in the runbook |
| Portal BFF | `PORTAL_PUBLIC_ORIGIN`, `PORTAL_BACKEND_BASE_URL`, `PORTAL_OIDC_ISSUER_URI`, `PORTAL_OIDC_CLIENT_ID`, `PORTAL_OIDC_CLIENT_SECRET`, `PORTAL_OIDC_REDIRECT_URI`, `SERVER_PORT=8081` |
| Workflow Compose | `WORKFLOW_LOCAL_DB_PASSWORD` |
| Frontend MOCK | None |

`.env.example` uses issuer `http://localhost:8180/realms/tricore`, while the BFF runbook uses `http://127.0.0.1:8182/realms/tricore`. These are different identities; do not mix tokens or subjects. The template does not prove a Keycloak instance exists.

### 3. Run locally on Windows and Linux

Two local run modes and one acceptance gate (AS-IS as design; actual runs **UNVERIFIED**):

| Mode / gate | Provides | Does not establish |
|---|---|---|
| MOCK (run mode) | Portal with synthetic in-memory data | Backend authorization, SSO, persistence |
| integration-local (run mode) | `integration-local` build + HTTPS (Caddy) + BFF + Backend + real identities + disposable DB | Browser acceptance |
| LIVE E2E (acceptance gate, not a standalone run mode) | Evidence of an authenticated browser journey, collected from the integration-local stack | **UNVERIFIED**; tracked in [#118](https://github.com/tricore-opentrix/opentrix/issues/118) |

#### 3.1 MOCK Portal (no Java/DB needed)

From `frontend/`:

```powershell
npm.cmd ci
npm.cmd run dev
```

```sh
npm ci
npm run dev
```

Open `http://127.0.0.1:5173` (the `dev` script uses `vite --host 127.0.0.1`). Data resets on reload. Personas and login/register are UI previews only and do not authenticate.

Build and check (same directory; use `npm` on Linux):

```powershell
npm.cmd run build
npm.cmd test
npm.cmd run check:security
```

`build` runs `tsc --noEmit` then `vite build`. `npm.cmd run build:integration-local` selects the BFF-integration entry; both builds write `frontend/dist`, so build the intended mode right before serving.

#### 3.2 Backend

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

`build` already includes tests and packaging. The project version is `0.1.0` (`rootProject.name = dxos-backend`), so the JAR is under `backend/build/libs/`; the old JAR name `dxos-backend-0.0.1-SNAPSHOT.jar` belongs to historical material; the [Backend README](../backend/README.md) derives `dxos-backend-0.1.0.jar` (build not rerun). Ordinary tests need no PostgreSQL: `build.gradle` supplies default OIDC values for tests.

Running the application (`bootRun`) needs a provisioned database and OIDC variables. **`DB_*` alone is not enough.** Spring Boot includes Flyway; the runbooks provision separately and set `SPRING_FLYWAY_ENABLED=false`. Never point an unreviewed startup at a shared database. Pick **one** complete path:

- Local Workflow: [current Workflow checklist](../backend/docs/local-workflow-runbook.md). The [former operational steps](../backend/legacy-workflow-runbook.md) are archived historical material, not executable current instructions.
- Local Helpdesk: [scripts/README-helpdesk-local.md](../scripts/README-helpdesk-local.md).

When the environment is ready, from `backend/`: `.\gradlew.bat bootRun` (Windows) or `./gradlew bootRun` (Linux). Check: `Invoke-RestMethod -Uri 'http://localhost:8080/api/v1/health'` → `{"status":"UP"}`. This endpoint does not query PostgreSQL; it does not prove persistence or authorization. Actuator exposes only `/actuator/health`, without details.

The supported Helpdesk API is `/api/v1/mvp/requests` (when `dxos.helpdesk.enabled=true`). The old `/api/v1/requests/*` routes were removed.

#### 3.3 Portal BFF

From the repository root:

```powershell
.\backend\gradlew.bat -p portal-bff test
.\backend\gradlew.bat -p portal-bff build
```

```sh
./backend/gradlew -p portal-bff test
./backend/gradlew -p portal-bff build
```

Tests use controlled fixtures (PKCE, CSRF, origin checks, bearer forwarding, redirect rejection, no write retry). They do not prove real Keycloak login, refresh, provider logout or browser persistence. For a real local login, follow [portal-bff/README.md](../portal-bff/README.md) step by step (confidential Keycloak client + PKCE S256, consistent issuer, `integration-local` build, BFF `bootRun`, `caddy validate`/`caddy run` with [Caddyfile.local](../portal-bff/Caddyfile.local) at `https://localhost:8443`). That README marks real browser acceptance **NOT RUN / BLOCKED** → **UNVERIFIED**.

#### 3.4 Database and infrastructure

- There is no full-stack Compose. [infra/compose.workflow-postgres.yml](../infra/compose.workflow-postgres.yml) provisions Workflow PostgreSQL only (`postgres:17.11-alpine`, `127.0.0.1:55425`, named volume). Supply `WORKFLOW_LOCAL_DB_PASSWORD` securely; keep the original password when reusing the volume.
- Helpdesk: follow the runbook; the read-only preflight is `.\scripts\helpdesk-local-setup.ps1 -RunId <new id>` from the root. The `-Execute -ConfirmDemoDatabase` step creates a new container/volume and writes schema — read the runbook first.
- Flyway V1–V4 are immutable history. Do not re-run the cloud bootstrap/migration/smoke launchers as local setup. Do not bypass the Helpdesk configuration guard to use a shared database.
- Dockerfiles in `infra/release/` are packaging inputs, not a deployment stack (see [DEPLOYMENT.md](DEPLOYMENT.md)).

### 4. Development workflow

#### 4.1 Testing (AS-IS: commands; results **UNVERIFIED** until you run them)

| Check | Command / directory | Notes |
|---|---|---|
| Backend | `./gradlew test` in `backend/` | Unit, MVC, architecture tests; cases needing DB/real tokens may skip |
| Core boundary | `./gradlew test --tests com.tricore.dxos.architecture.CoreDependencyRulesTest` | Core dependency rules only |
| BFF | `./backend/gradlew -p portal-bff test` (repo root) | Fixtures, no real IdP |
| Frontend | `npm test` in `frontend/` | Vitest (jsdom) |
| Frontend security scan | `npm run check:security` | Pattern check, not a full audit |
| Workflow PostgreSQL | `./gradlew workflowIntegrationTest --no-daemon` in `backend/` | Needs `WORKFLOW_TEST_JDBC_URL`, `WORKFLOW_TEST_DB_USER`, `WORKFLOW_TEST_DB_PASSWORD`; use a disposable loopback DB; the task fails if they are missing |
| Helpdesk local | `scripts/helpdesk-negative-local.ps1 -RunId <id>` | Docker Desktop; synthetic JWKS; creates and retains new resources |
| Real Keycloak tokens | `OIDC_TEST_ACCESS_TOKEN` + `test` | Issuer hardcoded to `http://localhost:8180/realms/tricore` |

Playwright (from `frontend/`, after `npm run build`):

```powershell
npx.cmd playwright install chromium
npm.cmd run test:smoke
npx.cmd playwright test --config tests/mvp.playwright.config.ts
```

The standard config serves a preview at `127.0.0.1:4173` (`--strictPort`); free that port first. `helpdesk-mvp.spec.ts` skips itself under the standard config; only `tests/mvp.playwright.config.ts` enables it. Report skipped cases as **SKIPPED**, not PASS. Both use fake data/transport and are not LIVE E2E.

Read fresh reports in `build/test-results/test/` and `build/reports/tests/test/` of each Java project. Record commit, command, fixture, executed/skipped counts. A green build with skipped DB tests is **not** evidence that PostgreSQL was exercised.

`scripts/workflow-verify-local.ps1` provisions TLS fixtures and runs `test build`, requiring zero skips overall. Whether it suffices as the single verification command at this SHA is **UNVERIFIED** (Helpdesk/Keycloak cases have separate opt-ins it does not supply). Do not weaken guards or count skips as PASS.

Results recorded in READMEs are historical evidence for those runs, not results for the current SHA. The 999 tests/992 passed figure in `portal-bff/README.md` is the result of running `test` for the **Backend** (historical Backend evidence recorded in the BFF README), not the BFF test count; the 752 PASS in `backend/README.md` is a separate historical run.

#### 4.2 Coding rules (AS-IS)

- The backend is a modular monolith; Core provides mechanisms, applications own business semantics. Provider code stays in `infrastructure`.
- `CoreDependencyRulesTest` restricts Core to `java..` and Core packages, excludes JDBC, and forbids cross-dependencies among the three Core capabilities. Application/Gateway rules in design documents are not fully enforced by this test.
- Never trust browser roles/identity; the backend stays authoritative. Keep atomic writes and optimistic versions; never blind-retry on `COMMIT_OUTCOME_UNKNOWN` — reconcile through an authorized detail/history read.
- The Workflow HTTP controller is not registered in production; do not enable it without the security gate.
- [.editorconfig](../.editorconfig): UTF-8, LF, 4-space indent for Java/Gradle/SQL, 2 spaces by default; `.ps1/.bat/.cmd` use CRLF. Add SPDX headers to new files.

#### 4.3 Git and Pull Requests (per [CONTRIBUTING.md](../CONTRIBUTING.md), AS-IS)

1. Work over ~2 hours needs an Issue; discuss large API/architecture/security/storage changes first.
2. Branch from `main` as `<type>/<area>-<description>`; never push directly to `main`/`gh-pages`.
3. Conventional Commits for commits and PR titles; Draft PR, about 400 lines; `Refs #N` for partial work, `Closes #N` only when criteria are met.
4. Run relevant checks, record commands/results/omissions; independent review per [CODEOWNERS](../.github/CODEOWNERS).
5. Squash-merge after CI and review pass.

CI ([ci.yml](../.github/workflows/ci.yml)): `backend`, `portal-bff`, `frontend`, `r23-compliance`, `repo-hygiene`. Backend and BFF build on JDK 21 (Ubuntu 24.04); frontend runs `npm ci`, `npm run build`, `npm test` on Node 22; R23 generates SBOMs and checks licenses/notices; hygiene checks PR title, `gradlew` executable bit, REUSE. A bad PR title fails CI; a missing `Closes #N` or >400 lines only warns. CI runs neither Playwright nor `build:integration-local`, and provisions no Keycloak/PostgreSQL. Branch-protection settings: **UNVERIFIED** (YAML read only).

#### 4.4 Targets (PROPOSED)

| Item | Issue |
|---|---|
| Browser acceptance Keycloak → BFF → Backend → PostgreSQL | PROPOSED ([#118](https://github.com/tricore-opentrix/opentrix/issues/118)) |
| Object-storage decision replacing MinIO (no production adapter yet) | PROPOSED ([#181](https://github.com/tricore-opentrix/opentrix/issues/181)) |
| Runtime OpenAPI verification | PROPOSED ([#112](https://github.com/tricore-opentrix/opentrix/issues/112), per the Block C report) |
| Source-origin/rights verification | PROPOSED ([#138](https://github.com/tricore-opentrix/opentrix/issues/138)) |
| Flowable integration (the current engine is the in-house `WorkflowRuntime`) | PROPOSED ([#191](https://github.com/tricore-opentrix/opentrix/issues/191)) |
| APISIX integration (currently Spring MVC/Security and the BFF allowlist) | PROPOSED ([#116](https://github.com/tricore-opentrix/opentrix/issues/116)) |
| Playwright in CI (the `frontend` job does not run Playwright) | PROPOSED ([#132](https://github.com/tricore-opentrix/opentrix/issues/132)) |

Flowable, APISIX and an object-storage provider are not integrated into an accepted runtime; the Phase 2 reports verify only that, and do not conclude the technologies are entirely absent from the code. See [Block A](09-evidence/phase-2/block-a-architecture.md), [Block B](09-evidence/phase-2/block-b-backend-infra.md) and [Block C](09-evidence/phase-2/block-c-application.md) (application/Portal/BFF; evidence for #118 and #112). Do not treat them as prerequisites or existing capabilities.

### 5. Troubleshooting

| Symptom | Check / action |
|---|---|
| Wrong Java or Wrapper failure | Compare `java -version`, `JAVA_HOME`, `PATH`; use JDK 21 and the committed Wrapper |
| `./gradlew` permission denied (Linux) | The Git index records `backend/gradlew` as `100755`; check checkout permissions/line endings |
| PowerShell blocks `npm.ps1` | Use `npm.cmd`/`npx.cmd` |
| Node engine or dependency error | Node >= 22.12; `npm ci` with the lockfile; do not regenerate it just to pass |
| `.env` values ignored | Spring does not read `.env`; set the process environment |
| Backend fails to start | Check `DB_*`, `OIDC_*`, `DXOS_WORKFLOW_SCHEMA`, `currentSchema`, migration state, runtime grants |
| Helpdesk route missing / guard rejects | Check `DXOS_HELPDESK_ENABLED`, Helpdesk variables, loopback address, `helpdesk_disposable_*` DB name, `helpdesk_runtime_*` login; do not disable the guard |
| PostgreSQL login fails on volume reuse | Keep the original password; changing Compose variables does not reset an initialized database |
| Build green but DB tests skipped | Check environment gates and fresh reports; a skip is not PASS |
| Keycloak issuer/audience error or hidden 404 | Match the issuer literally (host/port); check audience, `resource_access.tricore-api.roles`, membership and ACL |
| BFF 502, login failure, CSRF 403 | Check Backend/BFF (port 8081), HTTPS origin/callback, client secret, CA trust, `X-CSRF-TOKEN`; never bypass TLS/CSRF |
| Deep link fails or Portal shows MOCK | Caddy must serve `frontend/dist` with SPA fallback; build the right mode |
| Playwright will not run | `npx playwright install chromium`, build MOCK, check port 4173 |
| Unknown write result | Read authorized detail/history to reconcile; do not replay POST or re-run migration/smoke |
| Database data loss | Do not use `down -v`/delete volumes to "fix" setup; DB tests create and drop fixture objects, use disposable databases only |

More detail: [Backend](../backend/README.md), [BFF](../portal-bff/README.md), [Frontend](../frontend/README.md), [Helpdesk local](../scripts/README-helpdesk-local.md), [Architecture](ARCHITECTURE.md), [Testing](TESTING.md), [Deployment](DEPLOYMENT.md).
