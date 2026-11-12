<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# Triển khai / Deployment

**Điều hướng / Navigation:** [Tài liệu](README.md) · [Development](DEVELOPMENT.md) · [Deployment](DEPLOYMENT.md) · [Release](RELEASE.md) · **Ngôn ngữ / Language:** [Tiếng Việt](#vi) | [English](#en)

> **Trạng thái / Status:** Đã review — merge ở #203 / Reviewed — merged in #203 · **Owner:** @lexuanbao258-collab · **Refs:** [#194](https://github.com/tricore-opentrix/opentrix/issues/194), [#197](https://github.com/tricore-opentrix/opentrix/issues/197)
>
> **Source SHA:** `main@e31497f364cc7e9d3cee03ee59b9e48db524ea77` (mã/hạ tầng đã đối chiếu / inspected application and infrastructure), baseline `832c75fc3164cf170eed3bb8f1e380d24dd65aba`; chỉ `docs/` đổi giữa hai SHA. **Deployment, migration, container startup và LIVE E2E: UNVERIFIED tại SHA này.**

[Docs index](README.md) · [Development](DEVELOPMENT.md) · [Testing](TESTING.md) · [Release](RELEASE.md) · [Phase 2 infra evidence](09-evidence/phase-2/block-b-backend-infra.md)

<a id="vi"></a>

## Tiếng Việt

### 1. Hiện trạng và phạm vi triển khai (AS-IS)

#### Bảng trạng thái tính năng / Feature status matrix (AS-IS / UNVERIFIED / PROPOSED)

| Thành phần | Nguồn có sẵn | Xác minh / giới hạn |
| --- | --- | --- |
| Identity / Keycloak | Backend [OIDC](../backend/src/main/resources/application.yml), BFF [OAuth client](../portal-bff/src/main/resources/application.yml) | **SOURCE IMPLEMENTED**; browser login ba người dùng **LIVE E2E UNVERIFIED** ([#118](https://github.com/tricore-opentrix/opentrix/issues/118)) |
| Workflow Core | `WorkflowRuntime`, `WorkflowPersistencePort`, PostgreSQL adapter và test source ([Backend](../backend/README.md)) | **SOURCE IMPLEMENTED / TEST-LEVEL**; không chứng minh Flowable/E2E |
| Helpdesk | `/api/v1/mvp/requests` khi bật `dxos.helpdesk.enabled`, authorization/version test | **SOURCE IMPLEMENTED / TEST-LEVEL**; Golden Path thật **UNVERIFIED** |
| Portal Frontend | [Frontend](../frontend/package.json): MOCK và build `integration-local` | MOCK dùng dữ liệu giả; build bundle chưa chứng minh kết nối runtime |
| Portal BFF | [BFF](../portal-bff/README.md): OAuth/PKCE, session, CSRF, fixture test | **TEST-LEVEL**; Keycloak/Browser/DB **LIVE E2E UNVERIFIED** |
| PostgreSQL / Flyway | [Compose](../infra/compose.workflow-postgres.yml), migration Workflow V1–V4/Helpdesk SQL | **SOURCE IMPLEMENTED**; schema/ACL/restart cùng SHA cần kiểm chứng |
| Docker Compose | `infra/compose.workflow-postgres.yml`: chỉ PostgreSQL | Full-stack Compose **PROPOSED** [#119](https://github.com/tricore-opentrix/opentrix/issues/119) |
| APISIX / Flowable | Chưa có runtime tích hợp được nghiệm thu; Workflow dùng engine nội bộ | **PROPOSED** [APISIX #116](https://github.com/tricore-opentrix/opentrix/issues/116) / [Flowable #191](https://github.com/tricore-opentrix/opentrix/issues/191) |

SOURCE IMPLEMENTED = có mã; TEST-LEVEL = chỉ các ca được ghi; UNVERIFIED ≠ FAIL. Nguồn: [Block B](09-evidence/phase-2/block-b-backend-infra.md) / [Block C](09-evidence/phase-2/block-c-application.md).




`AS-IS` nghĩa là có mã/cấu hình tại SHA đã đối chiếu, **không phải đã chạy thành công**. `UNVERIFIED` là thiếu bằng chứng vận hành đúng môi trường/SHA. `PROPOSED` chỉ mục tiêu có Issue. Cấu hình hiện tại phục vụ phát triển và kiểm chứng cục bộ; **chưa có một Compose full-stack được nghiệm thu**.

| Thành phần | Có trong repo | Chưa được khẳng định |
| --- | --- | --- |
| PostgreSQL Workflow | [`infra/compose.workflow-postgres.yml`](../infra/compose.workflow-postgres.yml): `postgres:17.11-alpine`, `127.0.0.1:55425:5432`, database/user `workflow_test`, named volume `workflow-postgres-17-data`, `pg_isready` healthcheck | Compose này **không** chạy Backend, BFF, Portal, Keycloak hay Caddy |
| Backend | Java 21, Spring Boot; datasource, Flyway và OIDC qua [`application.yml`](../backend/src/main/resources/application.yml) | Boot, PostgreSQL, login thật và bảo mật E2E cùng một SHA: `UNVERIFIED` |
| Portal BFF | OIDC Authorization Code + PKCE, server-side session, CSRF; bind loopback theo [`portal-bff/README.md`](../portal-bff/README.md) | Browser/Keycloak callback và token forwarding thực tế: `UNVERIFIED` |
| React Portal | MOCK mặc định; build `integration-local` riêng theo [`frontend/package.json`](../frontend/package.json) | MOCK/build không chứng minh API hoặc lưu dữ liệu LIVE |
| HTTPS ingress | [`portal-bff/Caddyfile.local`](../portal-bff/Caddyfile.local) cho demo cục bộ | Không phải cấu hình production / stack tái lập đa hệ điều hành |
| Release containers | [`infra/release/`](../infra/release/) chứa Dockerfile phục vụ R24 | Không phải Compose triển khai production; không suy ra image đã được phép phát hành |

### 2. Docker Compose: kiểm tra trước, khởi động sau khi được phép

Từ **root repository**, có Docker Compose v2. `WORKFLOW_LOCAL_DB_PASSWORD` là mật khẩu riêng của fixture, phải cấp qua môi trường/secret an toàn; không commit, echo hay đặt giá trị thật trong hướng dẫn. `config` kiểm tra cấu hình và vẫn yêu cầu biến này được cung cấp.

```powershell
# PowerShell; mật khẩu phải được cung cấp an toàn cho process từ trước.
docker compose -f infra/compose.workflow-postgres.yml config --quiet
docker compose -f infra/compose.workflow-postgres.yml ps
```

```sh
# Linux/macOS; mật khẩu phải được cung cấp an toàn cho process từ trước.
docker compose -f infra/compose.workflow-postgres.yml config --quiet
docker compose -f infra/compose.workflow-postgres.yml ps
```

**Điều kiện/kết quả kỳ vọng:** cài Docker Compose v2 và cấp `WORKFLOW_LOCAL_DB_PASSWORD` an toàn. `docker compose config --quiet` trả exit code 0 nếu cấu hình hợp lệ, không tạo container; `docker compose ps` liệt kê tài nguyên hiện có, có thể trống. Dù hiển thị `healthy`, `pg_isready` không xác nhận migration, quyền runtime hay dữ liệu nghiệp vụ. **Chưa có log chạy cùng SHA chứng minh PASS.**

Hai lệnh trên chỉ đọc/kiểm tra cấu hình và trạng thái, **không khởi tạo database**. Người vận hành chỉ được dùng `docker compose ... up -d` sau khi xác nhận quyền sở hữu fixture và nguy cơ tạo volume/schema. Không tự chạy `down -v`, xóa volume hoặc dùng Compose này cho dữ liệu dùng chung. Volume đã tồn tại giữ mật khẩu PostgreSQL ban đầu; thay biến môi trường không đổi mật khẩu trong volume.

### 3. Cấu hình, secrets, cổng và ranh giới bảo mật

| Thành phần | Điều kiện nguồn mã | Ranh giới |
| --- | --- | --- |
| Backend DB | `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | Datasource phải được cấp biến thật qua process; [` .env.example `](../.env.example) chỉ là mẫu, Spring **không tự đọc** `.env` |
| Backend OIDC | `OIDC_ISSUER_URI`, `OIDC_AUDIENCE`, `OIDC_RESOURCE_CLIENT_ID` | Phải khớp issuer/audience/token thực; không bỏ xác minh JWT |
| Workflow | `DXOS_WORKFLOW_SCHEMA`, JDBC `currentSchema`, Flyway | Kiểm tra schema, migration, quyền runtime theo runbook; không chạy DDL vào DB không sở hữu |
| Helpdesk | `DXOS_HELPDESK_ENABLED` và nhóm `DXOS_HELPDESK_*` | Khi bật, `HelpdeskConfiguration.requireDisposable` giới hạn JDBC/DB/user và địa chỉ loopback; không bỏ guard |
| BFF | `PORTAL_PUBLIC_ORIGIN`, `PORTAL_BACKEND_BASE_URL`, `PORTAL_OIDC_ISSUER_URI`, `PORTAL_OIDC_CLIENT_ID`, `PORTAL_OIDC_CLIENT_SECRET`, `PORTAL_OIDC_REDIRECT_URI` | HTTPS cùng origin, confidential client, CSRF; secret nằm phía server |
| Local ingress | Caddyfile mẫu: HTTPS `https://localhost:8443`; BFF mặc định mẫu dùng `127.0.0.1:8081`; Backend local thường `127.0.0.1:8080` | Không mở port/backend cho Internet, không bỏ CA trust/CSRF để vượt lỗi |

Mẫu issuer ở `.env.example` và issuer trong runbook BFF có host/port khác nhau. **Không trộn token, subject hoặc client giữa các issuer**. Không đặt password, private key, bearer, cookie hoặc dữ liệu người dùng thật vào Git/PR/log.

### 4. Migration và chạy cục bộ: hai lộ trình khác nhau

**AS-IS so với chưa xác minh:** Flyway V1–V4 và script setup tồn tại trong source; bản ghi migration thực tế trong PostgreSQL cần được operator đọc/đối chiếu. Không suy ra `flyway migrate` đã chạy chỉ từ tên file SQL. `-Execute -ConfirmDemoDatabase`, `migrate`, `up -d`, `down -v` có thể tạo, sửa hoặc xóa tài nguyên; không chạy trên dữ liệu dùng chung.


**Portal MOCK (không có backend/DB):** từ `frontend/` chạy `npm ci` rồi `npm run dev` (PowerShell: `npm.cmd ci`, `npm.cmd run dev`). Lệnh dev bind `127.0.0.1`; đây không phải deployment đã nghiệm thu.

**Backend/Helpdesk cục bộ có DB:** làm đúng [runbook Helpdesk](../scripts/README-helpdesk-local.md) và [Backend README](../backend/README.md). Các bước preflight có thể chỉ đọc nhưng bước setup `-Execute -ConfirmDemoDatabase` **ghi dữ liệu, tạo fixture**; chỉ thực hiện trên tài nguyên disposable vừa được xác nhận độc quyền. V3/V4 Workflow và các launcher cloud trong [scripts README](../scripts/README.md) là luồng được phê duyệt lịch sử, **không phải thao tác setup mặc định** và không được tự chạy lại. Flyway trong source không chứng minh schema, roles và grant Helpdesk đã được provision.

**BFF + Portal integration-local:** chạy theo [BFF runbook](../portal-bff/README.md): issuer đồng nhất, Keycloak client riêng, CA HTTPS tin cậy, Caddy, BFF và Backend với DB disposable. Chỉ build `npm run build:integration-local` không khởi động stack và không chứng minh [#118](https://github.com/tricore-opentrix/opentrix/issues/118). Hướng dẫn build/test thuần ở [DEVELOPMENT.md](DEVELOPMENT.md); không đưa password vào command line.

### 5. Health check, kiểm chứng và xử lý sự cố

- PostgreSQL: `docker compose -f infra/compose.workflow-postgres.yml ps` sau khi operator khởi động; `healthy` chỉ chứng minh `pg_isready` của instance đó, **không chứng minh migration, ACL hoặc nghiệp vụ**.
- Backend: khi đã khởi động bằng cấu hình an toàn, `GET http://127.0.0.1:8080/api/v1/health` trả trạng thái ứng dụng; endpoint health không truy vấn nghiệp vụ DB và không thay cho E2E. Actuator chỉ expose `/actuator/health`, ẩn details/components.
- BFF: `GET /bff/session` qua HTTPS cùng origin; `authenticated:false` là kết quả hợp lệ khi chưa đăng nhập. Chỉ khi ba principal thật chạy Golden Path, negative cases và restart với bằng chứng mới đánh giá LIVE.
- `BFF 502`: kiểm Backend/BFF, issuer, callback, CA trust và host/port; không tắt TLS/CSRF. `401/403/404`: kiểm bearer, CSRF, role, tenant và resource ACL, không sửa bằng cách mở quyền.
- DB port/mật khẩu sai: kiểm đúng `127.0.0.1:55425` và volume hiện hữu; không reset dữ liệu để vượt lỗi. `COMMIT_OUTCOME_UNKNOWN`: chỉ đối soát bằng GET detail/history có quyền, **không tự retry POST**.

**Biên bản kiểm chứng bắt buộc trước claim PASS:** commit SHA, OS/Docker/Java/Node, mode, fixture owner, command, exit code, count PASS/FAIL/SKIPPED, log đã khử bí mật, evidence URL, restart/rollback và reviewer độc lập. Chưa có biên bản mới của trang này: **`UNVERIFIED`**.

### 6. Kiến trúc mục tiêu — PROPOSED

- [#119](https://github.com/tricore-opentrix/opentrix/issues/119): một Compose **full stack** source-built, PostgreSQL/Keycloak/Backend/BFF/Portal/Caddy, HTTPS, health/readiness và demo đa hệ điều hành; chưa nghiệm thu.
- [#118](https://github.com/tricore-opentrix/opentrix/issues/118): LIVE browser → Keycloak → BFF → Backend → PostgreSQL với ba principal, negative paths và persistence; chưa nghiệm thu.
- [#116](https://github.com/tricore-opentrix/opentrix/issues/116): API Gateway chuyên dụng; **không** khẳng định APISIX đã tích hợp.
- [#181](https://github.com/tricore-opentrix/opentrix/issues/181), [#192](https://github.com/tricore-opentrix/opentrix/issues/192): provider/adapter S3-compatible storage; chưa có production adapter được chấp nhận.

---

<a id="en"></a>

## English

### 1. Current deployment boundary (AS-IS)

#### Feature status matrix / Bảng trạng thái tính năng (AS-IS / UNVERIFIED / PROPOSED)

| Component | Existing source | Verification / limits |
| --- | --- | --- |
| Identity / Keycloak | Backend [OIDC](../backend/src/main/resources/application.yml), BFF [OAuth client](../portal-bff/src/main/resources/application.yml) | **SOURCE IMPLEMENTED**; real three-principal browser login **LIVE E2E UNVERIFIED** ([#118](https://github.com/tricore-opentrix/opentrix/issues/118)) |
| Workflow Core | `WorkflowRuntime`, `WorkflowPersistencePort`, PostgreSQL adapter and test sources ([Backend](../backend/README.md)) | **SOURCE IMPLEMENTED / TEST-LEVEL**; does not prove Flowable/E2E |
| Helpdesk | `/api/v1/mvp/requests` when `dxos.helpdesk.enabled` is enabled, authorization/version tests | **SOURCE IMPLEMENTED / TEST-LEVEL**; real Golden Path **UNVERIFIED** |
| Portal Frontend | [Frontend](../frontend/package.json): MOCK and `integration-local` build | MOCK uses synthetic data; bundle build is not proof of runtime integration |
| Portal BFF | [BFF](../portal-bff/README.md): OAuth/PKCE, session, CSRF, fixture test | **TEST-LEVEL**; Keycloak/browser/DB **LIVE E2E UNVERIFIED** |
| PostgreSQL / Flyway | [Compose](../infra/compose.workflow-postgres.yml), migration Workflow V1–V4/Helpdesk SQL | **SOURCE IMPLEMENTED**; same-SHA schema/ACL/restart evidence pending |
| Docker Compose | `infra/compose.workflow-postgres.yml`: Workflow PostgreSQL only | Full-stack Compose **PROPOSED** [#119](https://github.com/tricore-opentrix/opentrix/issues/119) |
| APISIX / Flowable | No accepted integrated runtime; Workflow uses an in-house engine | **PROPOSED** [APISIX #116](https://github.com/tricore-opentrix/opentrix/issues/116) / [Flowable #191](https://github.com/tricore-opentrix/opentrix/issues/191) |

SOURCE IMPLEMENTED = source exists; TEST-LEVEL = recorded test scope only; UNVERIFIED ≠ FAIL. Sources: [Block B](09-evidence/phase-2/block-b-backend-infra.md) / [Block C](09-evidence/phase-2/block-c-application.md).




`AS-IS` means source/configuration was inspected at the pinned SHA, **not** a successful deployment. `UNVERIFIED` means same-environment, same-SHA runtime evidence is missing. `PROPOSED` denotes an issue-tracked target. Current assets support local development and controlled verification; **no accepted full-stack Compose deployment exists**.

| Component | Existing source | Not established |
| --- | --- | --- |
| Workflow PostgreSQL | [`infra/compose.workflow-postgres.yml`](../infra/compose.workflow-postgres.yml): `postgres:17.11-alpine`, `127.0.0.1:55425:5432`, `workflow_test` DB/user, `workflow-postgres-17-data` volume, `pg_isready` healthcheck | Does **not** start Backend, BFF, Portal, Keycloak or Caddy |
| Backend | Java 21/Spring Boot, datasource/Flyway/OIDC from [`application.yml`](../backend/src/main/resources/application.yml) | Boot + real Postgres/login/full-stack security at the same SHA: `UNVERIFIED` |
| Portal BFF | OIDC Authorization Code + PKCE, server-side session and CSRF, loopback binding per [BFF README](../portal-bff/README.md) | Real browser/Keycloak callback and forwarding: `UNVERIFIED` |
| React Portal | Default MOCK mode; separate `integration-local` build from [package.json](../frontend/package.json) | MOCK/build is not LIVE API or persistence evidence |
| HTTPS ingress | [Local Caddyfile](../portal-bff/Caddyfile.local) | Not production or cross-platform deployment acceptance |
| Release images | [`infra/release/`](../infra/release/) Dockerfiles used by R24 | Not an operational full stack or permission to distribute images |

### 2. Docker Compose: inspect before any authorized start

From the **repository root**, with Docker Compose v2. Supply `WORKFLOW_LOCAL_DB_PASSWORD` securely to the process; never echo, commit, or place actual credentials in documentation. Even `config` needs the variable because Compose rejects missing values.

```powershell
# PowerShell; password supplied securely beforehand.
docker compose -f infra/compose.workflow-postgres.yml config --quiet
docker compose -f infra/compose.workflow-postgres.yml ps
```

```sh
# Linux/macOS; password supplied securely beforehand.
docker compose -f infra/compose.workflow-postgres.yml config --quiet
docker compose -f infra/compose.workflow-postgres.yml ps
```

**Prerequisites/expected results:** install Docker Compose v2 and supply `WORKFLOW_LOCAL_DB_PASSWORD` securely. `docker compose config --quiet` exits 0 for valid config without creating a container; `docker compose ps` lists existing resources and can be empty. Even if `healthy`, `pg_isready` does not verify migration, runtime grants or business data. **No same-SHA run log establishes PASS.**

These commands only check configuration/status; they do **not** start a database. Only the fixture owner may decide to run `docker compose ... up -d` after reviewing volume/schema effects. Do not run `down -v`, delete volumes, or reuse this stack for shared data. An existing volume keeps its initial database password; editing an environment variable does not rotate it.

### 3. Configuration, secrets, ports and trust boundaries

| Component | Source-defined variables | Requirement |
| --- | --- | --- |
| Backend database | `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | Set in the process environment; [`.env.example`](../.env.example) is a template and Spring does **not** automatically read `.env` |
| Backend OIDC | `OIDC_ISSUER_URI`, `OIDC_AUDIENCE`, `OIDC_RESOURCE_CLIENT_ID` | Exact issuer/audience/token validation must remain enabled |
| Workflow | `DXOS_WORKFLOW_SCHEMA`, JDBC `currentSchema`, Flyway | Check ownership, schema/migration state and runtime privilege before any write |
| Helpdesk | `DXOS_HELPDESK_ENABLED` and `DXOS_HELPDESK_*` | `HelpdeskConfiguration.requireDisposable` restricts JDBC/DB/user and loopback address when enabled; do not bypass it |
| BFF | `PORTAL_PUBLIC_ORIGIN`, `PORTAL_BACKEND_BASE_URL`, `PORTAL_OIDC_ISSUER_URI`, `PORTAL_OIDC_CLIENT_ID`, `PORTAL_OIDC_CLIENT_SECRET`, `PORTAL_OIDC_REDIRECT_URI` | Same-origin HTTPS, confidential client, CSRF and server-only secret |
| Local ingress | Example Caddy origin `https://localhost:8443`; BFF example `127.0.0.1:8081`; Backend typically `127.0.0.1:8080` | Do not expose private endpoints or disable CA trust/CSRF |

The issuer in `.env.example` differs by host/port from the BFF runbook issuer. **Do not mix tokens, subjects or clients across issuers.** Keep passwords, private keys, bearer tokens, cookies and actual user data out of Git/PR/logs.

### 4. Distinct migration and local startup tracks

**AS-IS vs unverified:** Flyway V1–V4 and setup scripts are present in source; real PostgreSQL migration history requires operator inspection. SQL files alone do not establish executed migrations. `-Execute -ConfirmDemoDatabase`, `migrate`, `up -d`, and `down -v` can create, modify or delete resources; never run them against shared data.


**MOCK Portal:** From `frontend/` run `npm ci` and `npm run dev` (PowerShell: `npm.cmd ci` / `npm.cmd run dev`). Vite binds loopback; this is not an accepted deployment.

**Disposable Backend/Helpdesk:** Follow the [Helpdesk runbook](../scripts/README-helpdesk-local.md) and [Backend README](../backend/README.md). A preflight may be read-only; the setup `-Execute -ConfirmDemoDatabase` **creates a fixture and writes schema/data** and is allowed only on exclusively owned disposable resources. Historical V3/V4 cloud launchers in [scripts README](../scripts/README.md) are **not default local setup** and must not be rerun. Flyway source alone does not establish completed Helpdesk schema/roles/grants.

**Integration-local BFF + Portal:** Follow the [BFF runbook](../portal-bff/README.md): exact common issuer, separate Keycloak client, trusted HTTPS CA, Caddy, BFF/Backend and disposable DB. `npm run build:integration-local` builds a bundle only; it does not start the stack or prove [#118](https://github.com/tricore-opentrix/opentrix/issues/118). See [DEVELOPMENT.md](DEVELOPMENT.md) for build/test instructions; keep credentials out of command arguments.

### 5. Health, evidence and troubleshooting

- After an authorized start, `docker compose -f infra/compose.workflow-postgres.yml ps` can show Postgres health. `healthy` reflects `pg_isready` only; not migrations, ACL or business behavior.
- After safe Backend startup, `GET http://127.0.0.1:8080/api/v1/health` indicates HTTP application health, not workflow database persistence. Actuator exposes `/actuator/health` without details/components.
- `GET /bff/session` over same-origin HTTPS may legitimately return `authenticated:false`. Only a real three-principal browser Golden Path plus negative/restart evidence could establish LIVE acceptance.
- For `502`, check Backend/BFF availability, issuer, callback, CA trust and port; never bypass TLS/CSRF. For `401/403/404`, check tokens/CSRF/roles/tenant/resource ACL rather than weakening access control.
- For database credential failures, check port `127.0.0.1:55425` and existing volume rather than resetting data. For `COMMIT_OUTCOME_UNKNOWN` reconcile through authorized GET detail/history, **never blindly repeat the POST**.

**Required evidence before a PASS claim:** exact SHA; OS/Docker/Java/Node; mode; fixture ownership; command/exit status; PASS/FAIL/SKIPPED counts; sanitized logs; evidence URLs; restart/rollback results; independent reviewer. No fresh execution report exists for this page: **`UNVERIFIED`**.

### 6. Target — PROPOSED

- [#119](https://github.com/tricore-opentrix/opentrix/issues/119): source-built full-stack Compose with PostgreSQL/Keycloak/Backend/BFF/Portal/Caddy, HTTPS/readiness and cross-platform proof.
- [#118](https://github.com/tricore-opentrix/opentrix/issues/118): three-principal real-browser/Keycloak/Backend/PostgreSQL Golden Path, negative cases and persistence.
- [#116](https://github.com/tricore-opentrix/opentrix/issues/116): dedicated edge gateway; **APISIX is not an accepted integrated runtime**.
- [#181](https://github.com/tricore-opentrix/opentrix/issues/181), [#192](https://github.com/tricore-opentrix/opentrix/issues/192): S3-compatible provider selection and adapter; no accepted production adapter.
