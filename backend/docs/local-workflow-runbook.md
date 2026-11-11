<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# Workflow PostgreSQL cục bộ / Local Workflow PostgreSQL

> **Status / Trạng thái:** DRAFT / UNVERIFIED — technical checklist, not an executed result · **Scope:** local disposable Workflow only · [#197](https://github.com/tricore-opentrix/opentrix/issues/197)
>
> **Mã nguồn / Source:** [Backend](../README.md), [Compose](../../infra/compose.workflow-postgres.yml), [Backend config](../src/main/resources/application.yml). Legacy cloud/migration commands are preserved in the [historical archive](../legacy-workflow-runbook.md) but **must not be executed as current instructions**.

## Tiếng Việt

### 1. Ranh giới an toàn và trạng thái

- **AS-IS (source):** `infra/compose.workflow-postgres.yml` định nghĩa **chỉ** PostgreSQL `postgres:17.11-alpine`, `workflow_test`, cổng `127.0.0.1:55425:5432`, named volume và `pg_isready`. Không có Backend, Keycloak, Portal hay BFF trong Compose này.
- **UNVERIFIED:** bản tài liệu này không chạy Docker, `migrate`, `smoke`, `bootRun` hoặc test PostgreSQL. Mọi kết quả của lần chạy cũ ở [archive](../legacy-workflow-runbook.md) là lịch sử, không phải PASS tại HEAD.
- **KHÔNG chạy:** các launcher bootstrap/V3/V4/cloud smoke cũ, hoặc `docker compose down -v` / xóa volume. [#25](https://github.com/tricore-opentrix/opentrix/issues/25) có báo cáo owner về các thao tác cloud đã hoàn tất; không lặp lại.

### 2. Preflight chỉ đọc (root repository)

Điều kiện: Docker Compose v2, JDK 21; mật khẩu `WORKFLOW_LOCAL_DB_PASSWORD` đã được cấp **an toàn** trong process. Không commit mật khẩu, file `.env` hay token; `.env.example` không được Spring tự đọc.

```powershell
# Windows PowerShell, from repository root; no DB creation in these commands:
git rev-parse HEAD
java -version
docker compose -f infra/compose.workflow-postgres.yml config --quiet
docker compose -f infra/compose.workflow-postgres.yml ps
```

```sh
# Linux/macOS from repository root; no DB creation:
git rev-parse HEAD
java -version
docker compose -f infra/compose.workflow-postgres.yml config --quiet
docker compose -f infra/compose.workflow-postgres.yml ps
```

Nếu chưa có fixture, `ps` có thể trống; **không** coi đó là lỗi phải tự sửa bằng `up`. Chỉ operator sở hữu hoàn toàn DB và volume dùng một lần mới được quyết định khởi động/tạo schema. Sử dụng lại volume phải giữ mật khẩu gốc, kiểm schema/Flyway history/role trước mọi thao tác ghi.

### 3. Build và giới hạn của boot

Kiểm tra nguồn không cần DB, từ thư mục `backend/`:

```powershell
.\gradlew.bat test
.\gradlew.bat build
```

```sh
./gradlew test
./gradlew build
```

Đây chỉ là lệnh từ source, **không có kết quả chạy mới**. Test DB có thể `SKIPPED` nếu thiếu opt-in. `workflowIntegrationTest` cần `WORKFLOW_TEST_JDBC_URL`, `WORKFLOW_TEST_DB_USER` và `WORKFLOW_TEST_DB_PASSWORD` cùng fixture *disposable* được kiểm soát; không chạy nó trên DB dùng chung hoặc cloud.

Khi operator đã provision riêng theo approval (migrator ≠ runtime), mới xem xét boot Backend. Phải cung cấp **cả** `DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD` và `OIDC_ISSUER_URI/OIDC_AUDIENCE/OIDC_RESOURCE_CLIENT_ID`; Workflow cần `DXOS_WORKFLOW_SCHEMA` cùng JDBC `currentSchema` khớp. Chỉ tắt Flyway qua `SPRING_FLYWAY_ENABLED=false` sau khi có bằng chứng migration tương ứng được áp dụng. **Không** sao chép các snippet lịch sử thiếu OIDC để chạy thẳng.

Nếu boot thành công theo môi trường đã duyệt, `GET /api/v1/health` chỉ cho biết HTTP app đáp ứng; không chứng minh DB/Workflow/ACL. Real browser Keycloak E2E vẫn theo [#118](https://github.com/tricore-opentrix/opentrix/issues/118). Xem [Helpdesk local](../../scripts/README-helpdesk-local.md) cho demo Helpdesk **tách biệt**; không trộn fixture của hai lộ trình.

### 4. Evidence và xử lý sự cố

Lưu SHA, OS/JDK/Docker, endpoint loopback, xác nhận sở hữu fixture, schema/role, lệnh, exit code, PASS/FAIL/SKIPPED, log không bí mật, tình trạng restart và người review. `healthy` từ `pg_isready` không xác minh migration/authorization. Lỗi issuer hoặc mật khẩu phải xử lý bằng đối chiếu cấu hình, không bypass TLS/guard; `COMMIT_OUTCOME_UNKNOWN` không tự retry thao tác ghi. **Chỉ reviewer có evidence đúng SHA mới xác nhận PASS.**

---

## English

### 1. Safety boundaries and status

- **AS-IS (source):** `infra/compose.workflow-postgres.yml` defines **PostgreSQL only** — `postgres:17.11-alpine`, `workflow_test`, `127.0.0.1:55425:5432`, a named volume and `pg_isready`. It does not start Backend, Keycloak, Portal or BFF.
- **UNVERIFIED:** this document did not run Docker, `migrate`, `smoke`, `bootRun` or PostgreSQL tests. Earlier owner-reported runs in the [archive](../legacy-workflow-runbook.md) are historical, not current HEAD PASS.
- **DO NOT run:** the archived cloud bootstrap/V3/V4/smoke launchers or `docker compose down -v`/volume deletion. Prior #25 cloud operations have owner-reported completion; never replay them.

### 2. Read-only preflight (repository root)

Prerequisites: Docker Compose v2 and JDK 21; provide `WORKFLOW_LOCAL_DB_PASSWORD` to the process through a secure method. Never commit credentials, tokens or real `.env` files. Spring does not automatically read `.env.example`.

```powershell
# Windows PowerShell, from repository root; no database creation:
git rev-parse HEAD
java -version
docker compose -f infra/compose.workflow-postgres.yml config --quiet
docker compose -f infra/compose.workflow-postgres.yml ps
```

```sh
# Linux/macOS, from repository root; no database creation:
git rev-parse HEAD
java -version
docker compose -f infra/compose.workflow-postgres.yml config --quiet
docker compose -f infra/compose.workflow-postgres.yml ps
```

`ps` may show no resources before provisioning; **do not** treat that as approval to run `up`. Only the operator owning an exclusive disposable DB and volume can authorize creation/schema writes. Reused volumes retain the original database password; inspect current schema/Flyway history/roles before any migration.

### 3. Build and boot boundaries

Source-defined ordinary checks, from `backend/`:

```powershell
.\gradlew.bat test
.\gradlew.bat build
```

```sh
./gradlew test
./gradlew build
```

No new execution results are claimed. Conditional database suites may be `SKIPPED`. `workflowIntegrationTest` requires `WORKFLOW_TEST_JDBC_URL`, `WORKFLOW_TEST_DB_USER` and `WORKFLOW_TEST_DB_PASSWORD` against an exclusively owned disposable fixture; never run against shared/cloud DBs.

Only after approved provisioning with separate migrator/runtime roles may Backend startup be considered. It requires **both** `DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD` and `OIDC_ISSUER_URI/OIDC_AUDIENCE/OIDC_RESOURCE_CLIENT_ID`. Also match `DXOS_WORKFLOW_SCHEMA` to JDBC `currentSchema`. Use `SPRING_FLYWAY_ENABLED=false` only when there is independent evidence that approved migrations are complete. Do not copy OIDC-incomplete historical examples into a new startup.

Once booted under approved conditions, `GET /api/v1/health` proves only an HTTP response, not database/Workflow/ACL behavior. Real Keycloak/browser acceptance remains [#118](https://github.com/tricore-opentrix/opentrix/issues/118). The [local Helpdesk runbook](../../scripts/README-helpdesk-local.md) is a **different fixture path**; do not mix them.

### 4. Evidence and troubleshooting

Record full SHA, OS/JDK/Docker versions, loopback endpoint, fixture ownership, schema/roles, commands, exit status, PASS/FAIL/SKIPPED, sanitized logs, restart result and independent reviewer. `pg_isready` healthy is not migration/authorization evidence. Investigate issuer/credential failures without weakening TLS/guards; never blindly retry `COMMIT_OUTCOME_UNKNOWN` writes. **Only an independent same-SHA evidence review can mark PASS.**
