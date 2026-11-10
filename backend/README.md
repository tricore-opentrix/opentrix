<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors

SPDX-License-Identifier: Apache-2.0
-->

# DX-OS Open-Core backend

The backend foundation for the TRICORE Internal Service Portal, built as a Modular
Monolith. Base package: `com.tricore.dxos`. Core provides the mechanisms; the
application owns the business semantics. Issue #1 created the project foundation and the
health API; Issue #5 once added a Request prototype (removed in R25, see below); Issue #7
added the IT Support workflow.

## Requirements

- JDK **21**, with `JAVA_HOME` pointing at the JDK directory.
- PowerShell on Windows, or bash on Linux/macOS (see the
  [Linux/macOS runbook](../docs/06-deployment/runbook-linux.md)).
- Internet access on the first build so the Gradle Wrapper can download Gradle and the dependencies.
- A reachable PostgreSQL when running the whole application; the Docker/PostgreSQL
  environment is provided by Issue #3.
- A reachable Keycloak realm (OIDC) when running the whole application: the backend loads
  `OIDC_ISSUER_URI/.well-known/openid-configuration` at startup. Building and testing do
  not need Keycloak.

The project uses Spring Boot 3.5.16, Gradle Groovy and Gradle Wrapper 8.14.3.
You do not need to install Gradle separately. The commands below run from the `backend/` directory.

## Build and test on Linux/macOS

```bash
cd backend
java -version          # must be 21
./gradlew test
./gradlew build
./gradlew test --tests com.tricore.dxos.common.health.HealthControllerTest
```

Building and testing need neither PostgreSQL nor Keycloak. The commands that run the
application with PostgreSQL and Keycloak on Linux/macOS are in the
[Linux/macOS runbook](../docs/06-deployment/runbook-linux.md).

## Build and test on Windows

Example JDK setup (change the path to match your machine):

```powershell
$env:JAVA_HOME = 'C:\Program Files\Java\jdk-21.0.11'
$env:Path = "$env:JAVA_HOME\bin;$env:Path"
java -version
.\gradlew.bat --version
.\gradlew.bat test
.\gradlew.bat build
```

The build produces an executable JAR at `build/libs/dxos-backend-<version>.jar`; the version comes from `build.gradle` (currently `0.1.0`).
The health test uses `@WebMvcTest` and checks HTTP 200, a JSON Content-Type and exactly
the body `{"status":"UP"}`. This build and test need neither PostgreSQL nor database
environment variables. There is no fake database and no H2 dependency.

Run only the health test:

```powershell
.\gradlew.bat test --tests com.tricore.dxos.common.health.HealthControllerTest
```

## PostgreSQL and environment variables

The process that runs the application must receive all five variables below. The
application also requires `OIDC_ISSUER_URI`, `OIDC_AUDIENCE` and `OIDC_RESOURCE_CLIENT_ID`;
these three have no default value either (see `application.yml`):

| Variable | Meaning |
| --- | --- |
| `DB_HOST` | PostgreSQL host reachable from the backend |
| `DB_PORT` | PostgreSQL port |
| `DB_NAME` | An existing database |
| `DB_USER` | PostgreSQL account |
| `DB_PASSWORD` | The account's password |

Datasource URL: `jdbc:postgresql://${DB_HOST}:${DB_PORT}/${DB_NAME}`.
There are no default credentials. Hibernate `ddl-auto: none` neither creates nor changes
the schema; `open-in-view: false` limits persistence outside HTTP rendering.

The Workflow adapter of Issue #25 also needs `DXOS_WORKFLOW_SCHEMA`, a datasource whose
`currentSchema` is the dedicated schema, and `SPRING_FLYWAY_ENABLED=false` at runtime. The
schema and migrations must exist before boot; see **Run the backend locally from a fresh
clone** or **Default Supabase PostgreSQL connection for Issue #25** below. A separate
runtime login is a requirement for long-term deployment, not a prerequisite of the initial
Supabase connection step.

PowerShell example that enters the configuration without writing the password into
source or the command history. A reachable Keycloak realm and all three `OIDC_*` variables
are required as well; setting only the database variables is not enough for `bootRun` to start:

```powershell
$env:DB_HOST = Read-Host 'DB_HOST (per the Issue #3 environment)'
$env:DB_PORT = Read-Host 'DB_PORT'
$env:DB_NAME = Read-Host 'DB_NAME'
$env:DB_USER = Read-Host 'DB_USER'
$env:DB_PASSWORD = Read-Host 'DB_PASSWORD' -MaskInput
$env:OIDC_ISSUER_URI = Read-Host 'OIDC_ISSUER_URI (a reachable Keycloak realm)'
$env:OIDC_AUDIENCE = Read-Host 'OIDC_AUDIENCE'
$env:OIDC_RESOURCE_CLIENT_ID = Read-Host 'OIDC_RESOURCE_CLIENT_ID'
.\gradlew.bat bootRun
```

`-MaskInput` needs PowerShell 7.1 or later. On Windows PowerShell 5.1, enter the
password the following way instead of the `DB_PASSWORD` line above:

```powershell
$dbCredential = Get-Credential -UserName $env:DB_USER -Message 'PostgreSQL credentials'
$env:DB_PASSWORD = $dbCredential.GetNetworkCredential().Password
.\gradlew.bat bootRun
```

You can also run the built JAR with the same environment variables (replace `<version>` with the version in `build.gradle`):

```powershell
java -jar .\build\libs\dxos-backend-<version>.jar
```

Spring Boot does not read a `.env` file by itself. If you use such a file through a local
tool, do not commit it. `.gitignore` excludes `.env`, build output, the Gradle cache, IDE
metadata and temporary files. After stopping the application you can remove the password
from the PowerShell process:

```powershell
Remove-Item Env:DB_PASSWORD
```

## Health API

After the application has started, from another PowerShell window:

```powershell
Invoke-RestMethod -Uri 'http://localhost:8080/api/v1/health'
```

On Linux/macOS:

```bash
curl -s http://localhost:8080/api/v1/health
```

`GET /api/v1/health` returns HTTP 200 with the JSON `{"status":"UP"}`. The controller
does not query the database and has no business logic or dependency on the
Helpdesk/Workflow modules. This is an HTTP check of the application; it does not prove that
PostgreSQL is available. The whole application still needs PostgreSQL to be configured
and connected for the backend to start.

Actuator exposes only `/actuator/health` over HTTP, shows no details or components, and
exposes no endpoint over JMX. The aggregated Actuator health may check the database and
return a status different from the health API, depending on the state of PostgreSQL. Do
not expose `env`, `beans`, `metrics` or any other management endpoint.

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

Cloud acceptance on 2026-10-15, as reported by the owner: V3/V4 COMMITTED_PASS,
checksum/inventory/seed PASS; smoke `cloud-20261015-01` COMMITTED_PASS,
precheck/postcheck/fresh-JVM persistence PASS, 2 instances / 4 history rows, exit 0.
Keep the test data; do not run the bootstrap, Flyway or smoke again. The cloud
instructions below are a record of what was executed and do not grant permission for a
new write. `postgres` is only a one-time development exception; a long-term deployment
needs a least-privilege runtime.

The JDBC adapter in `infrastructure.workflow` provides one `WorkflowPersistencePort` bean
and one `WorkflowRuntime` that uses `Clock.systemUTC()`. Core and Workflow HTTP are
unchanged; the Workflow controller is still not registered in production. The adapter
does not implement resource ACL and does not solve the revocation/TOCTOU problem of Issue #23.

V3 creates dedicated tables for definitions, instances and history; V1/V2 are unchanged.
V4 seeds two independent definitions: `document-review@1` and `incident-resolution@1`.
Import a definition with `PostgresWorkflowPersistence.provisionDefinition` using the
provisioner's datasource: the same key with the same content is idempotent, and different
content is rejected. All states/transitions must be inserted in the same transaction as
the new definition; the database blocks additions, UPDATE, DELETE and TRUNCATE after
commit. A content change needs a new version. The table owner/superuser can still disable
the triggers, so the runtime login must differ from the owner and must have no
DDL/provisioning privileges.

Time is stored losslessly as epoch seconds (BIGINT) and nanos (INTEGER), covering the whole
Java `Instant.MIN..MAX` range, including nanos that are not divisible by 1000. No clock
rounding is needed. The database must have `fsync=on` and `full_page_writes=on`; every
write sets `SET LOCAL synchronous_commit=on`, locks the instance and returns success only
after the COMMIT is confirmed. PostgreSQL's storage infrastructure must meet the
durability requirement.

An error before COMMIT with a confirmed rollback is `OPERATION_FAILURE`. A lost COMMIT
response, or a rollback that cannot be confirmed, is `COMMIT_OUTCOME_UNKNOWN`; the adapter
does not retry. A rollback after a COMMIT error does not prove that the earlier write was
not committed. Read the authoritative instance/history to reconcile, but two separate
reads do not share a snapshot, and stale or missing data while a transaction has not yet
finished proves neither a rollback nor which writer won.

### Required schema configuration

`DXOS_WORKFLOW_SCHEMA` (property `dxos.workflow.schema`) must be a lowercase identifier
matching `[a-z][a-z0-9_]{0,62}`, and must not be public/extensions/information_schema/pg_*.
There is no default schema. The schema must be provisioned separately.
Every connection must have a currentSchema/search_path that starts with this schema,
followed only by pg_catalog/pg_temp; the JDBC URL must not override it with another schema.
The adapter's SQL and all Workflow objects of V3/V4 use schema-qualified identifiers.
Flyway must go through `WorkflowMigrations.configure` or the Spring customizer:
defaultSchema/schemas set to the same schema, createSchemas=false, a mandatory
transaction, and no clean/repair/baseline. Flyway's native defaultSchema placeholder is
inserted after Java has validated the identifier; do not run SQL through an arbitrary
placeholder-substitution mechanism.

### Reproducible local PostgreSQL

The full check from source, which needs no Supabase, WARP or team credentials:

```powershell
# From backend/, with Docker running and JDK 21 on PATH:
powershell.exe -NoProfile -File ..\scripts\workflow-verify-local.ps1
if ($LASTEXITCODE -ne 0) { throw 'Local verification failed' }
```

The launcher uses PostgreSQL 17.11 on a random loopback port, generates valid and invalid
CAs with the OpenSSL of Git for Windows, and turns on all TLS/event-trigger/audit
fixtures. Credentials exist only in the environment/stdin; private keys are kept outside
Git in a current-user/SYSTEM directory. It runs `test build`, checks that the XML has no
FAIL/SKIP and that all nine integration suites ran, then stops and removes its container
and cleans up the certificates. This is a disposable database; use the Compose file below
when you need to keep local data.

Docker and JDK 21 are required. The Compose file `infra/compose.workflow-postgres.yml`
runs PostgreSQL 17.11 on loopback port 55425 and keeps a separate named volume for major
version 17; do not reuse a version 16 volume. The password is supplied only through a
secure environment and is never written into source or on the command line. Keep the old
password when reusing a volume.

Integration variables: WORKFLOW_TEST_JDBC_URL, WORKFLOW_TEST_DB_USER,
WORKFLOW_TEST_DB_PASSWORD, and optionally WORKFLOW_TEST_MIGRATION_USER and
WORKFLOW_TEST_MIGRATION_PASSWORD. The test URL must be a loopback URL with a port and
database and no query string; the fixtures reject cloud URLs. A separate runtime needs a
login and must not be a superuser or have CREATEDB, CREATEROLE or schema ownership; the
local migrator creates and drops the test schema. The isolation fixture creates fake API
roles in a disposable database and a sentinel in public, checks the external ACLs, then
removes exactly the objects the fixture created.

From `backend`, with the local environment configured:

```powershell
$env:WORKFLOW_EVENT_GUARD_LOCAL_DISPOSABLE = 'true'
.\gradlew.bat workflowIntegrationTest --no-daemon
.\gradlew.bat test build --no-daemon
```

The integration tests consist of the V1–V4 adapter regression and an independent V3/V4
isolation suite. Do not run these suites on the shared Supabase. Without a database, the
`test` task skips the integration tests, while `workflowIntegrationTest` fails because
the environment variables are missing.

### Run the backend locally from a fresh clone

The commands below use only the loopback database created by Compose. Do not use a
Supabase account or endpoint. Each new volume provisions the role and schema only once;
when you reuse a volume, keep the old password and read its state first, and do not run
`migrate` again if the schema already has Flyway history.

```powershell
# From backend/:
$localDb = Get-Credential -UserName workflow_test -Message 'Choose the local PostgreSQL owner password'
$env:WORKFLOW_LOCAL_DB_PASSWORD = $localDb.GetNetworkCredential().Password
docker compose -f ..\infra\compose.workflow-postgres.yml up -d --wait
docker compose -f ..\infra\compose.workflow-postgres.yml exec workflow-postgres psql -U workflow_test -d workflow_test
```

In psql on a new local volume, enter the runtime password at the hidden prompt:

```text
CREATE ROLE workflow_runtime LOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
\password workflow_runtime
CREATE SCHEMA dxos_wf25_smoke_01 AUTHORIZATION workflow_test;
GRANT USAGE ON SCHEMA dxos_wf25_smoke_01 TO workflow_runtime;
\q
```

Run V3/V4 separately with the local owner, then grant the runtime privileges:

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

In the local psql:

```sql
GRANT SELECT ON dxos_wf25_smoke_01.workflow_definitions,
  dxos_wf25_smoke_01.workflow_definition_states, dxos_wf25_smoke_01.workflow_definition_transitions,
  dxos_wf25_smoke_01.workflow_instances, dxos_wf25_smoke_01.workflow_transition_history TO workflow_runtime;
GRANT INSERT ON dxos_wf25_smoke_01.workflow_instances,
  dxos_wf25_smoke_01.workflow_transition_history TO workflow_runtime;
GRANT UPDATE (current_state, lifecycle, runtime_version, updated_at_seconds, updated_at_nanos)
  ON dxos_wf25_smoke_01.workflow_instances TO workflow_runtime;
```

After `\q`, verify the data and boot with the runtime login. The backend also needs a
reachable Keycloak realm and the three `OIDC_*` variables (the values below match the
throwaway Keycloak in the [Linux/macOS runbook](../docs/06-deployment/runbook-linux.md);
use your own realm if you have one):

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
$env:OIDC_ISSUER_URI = 'http://localhost:8180/realms/tricore'   # a Keycloak realm must answer here
$env:OIDC_AUDIENCE = 'tricore-api'
$env:OIDC_RESOURCE_CLIENT_ID = 'tricore-api'
.\gradlew.bat bootRun
```

Health is at `/api/v1/health`. The Workflow HTTP controller is still not registered in
production until a verified principal/authorization is integrated; #25 provides the
adapter/runtime bean and constructor injection and opens no route before that security
gate. V3/V4 do not create Request tables; the Request demo still needs V1/V2 from its own
process. After stopping the backend, `docker compose ... down` keeps the named volume;
avoid `down -v` when checking a restart. Read the same run-id again from a new process to
verify persistence. Do not run `smoke` again with an old run-id: the runner rejects a
replay before writing.

### Default Supabase PostgreSQL connection for Issue #25

According to the [Issue #25 update of 2026-10-14](https://github.com/tricore-opentrix/opentrix/issues/25),
use the project's Direct Connection as pgAdmin does: `db.<project-ref>.supabase.co`, port
`5432`, database `postgres`, account `postgres` and the existing database password.
The development machine needs IPv6; the local PostgreSQL above still runs independently
of Supabase/WARP. Do not run Stage 1A/1B, do not grant SCRAM/LOGIN and do not change the
two custom roles that are `NOLOGIN`. Those records are optional hardening for long-term
deployment.

In a PowerShell session that already has `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`,
`DB_PASSWORD` and `PGSSLROOTCERT` (a trusted CA taken from the project), run the
read-only connection check from the repository root:

```powershell
powershell.exe -NoProfile -File .\scripts\workflow-read-only-preflight.ps1
if ($LASTEXITCODE -ne 0) { throw 'Read-only connection check failed' }
```

The preflight forces JDBC `sslmode=verify-full`, the CA, timeouts and a READ ONLY
transaction, then rolls back and closes. It does not boot Spring, run Flyway or create a
role/schema. Do not put secrets in URLs, args, source, command history or reports; enter
them only through a secure prompt or the existing secret environment. A passing check is
not an approval for write operations.

Spring configuration uses the same `DB_*`; the URL must add the schema and TLS before use:

```powershell
$env:DXOS_WORKFLOW_SCHEMA = 'dxos_wf25_smoke_01'
$caPath = [Uri]::EscapeDataString($env:PGSSLROOTCERT)
$env:SPRING_DATASOURCE_URL = "jdbc:postgresql://$($env:DB_HOST):$($env:DB_PORT)/$($env:DB_NAME)?currentSchema=$($env:DXOS_WORKFLOW_SCHEMA),pg_catalog,pg_temp&sslmode=verify-full&sslrootcert=$caPath"
$env:SPRING_FLYWAY_ENABLED = 'false'
```

This is preparation only, not a boot/migrate command. Cloud writes need a separate owner
approval for the schema, the V3/V4 bundle only, the seed and a bounded
smoke/restart/read, together with postchecks and recovery; do not run V1/V2 or
clean/repair/baseline on the shared database. Do not retry when a COMMIT outcome is
unknown. Keep the existing checks for schema isolation, manifest/event triggers and
API/PUBLIC privileges; do not turn off a guard to make connecting easier.

`postgres` is only a one-time approved verification exception and is not used for a
long-running backend or for the frontend. A minimal runtime identity is required before a
persistent/shared production deployment. `WorkflowSmokeRunner` still requires a runtime
that differs from the owner; the production entrypoint and the default constructor do not
read the development flags. The cloud migration/smoke/restart Definition of Done is still
pending and is not replaced by a local PASS.

### One-time development integration with postgres

The separate task `workflowDevelopmentSmoke` calls `WorkflowDevelopmentSmokeRunner`. It is
not registered as a Spring bean and does not run from bootRun/build or from the
production configuration. It reuses the bounded smoke/check/restart scenario and only
opens the owner/runtime exception for the development mode that has been opted into. The
production runner keeps its existing non-owner and least-privilege checks. It does not
create schemas, roles, GRANTs, cleanup or retries by itself.

All of these are required together: the argument `--development-integration`, an opt-in
with the exact value, the single schema `dxos_wf25_smoke_01`, DB_USER/DB_NAME set to
`postgres`, the Direct endpoint of the correct project, the CA and verify-full. Every
connection verifies session_user=current_user=postgres, backend TLS, a schema owned by
postgres, no schema ACL for PUBLIC/other roles and no effective privileges for API roles,
and no relation owned by another owner. The guard/manifest, the pinned V3/V4 bundle,
durability, default ACL, history/checksums and inventory checks stay active. The
check/read mode has no permission to call migrate/smoke.

The schema was bootstrapped successfully according to the owner report; do not run it
again. After a fresh preflight, only prepare/check from the repository root (do not set a
write approval yet):

```powershell
# DB_* and PGSSLROOTCERT are already in the secret environment; do not print them.
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

Do not set `WORKFLOW_DEV_LOCAL_DISPOSABLE`, `WF25_DISPOSABLE_TEST` or
`WORKFLOW_EVENT_GUARD_LOCAL_DISPOSABLE` on the cloud, even with the value false. The local
mode requires all three fixture flags together with the marker `dxos.wf25_disposable=on`
of the postgres login, loopback and TLS verify-full; the local flags cannot apply to the
Supabase endpoint.

**The owner approved only the pinned V3/V4, after fresh prechecks PASS.**
Use the single-purpose launcher in the section below; do not run the Gradle example
directly, since that would skip the audit/report. The approval does not include smoke,
bootstrap or recovery. The launcher's internal entry point is a separate migration mode:

~~~powershell
# Needs an explicit WORKFLOW_DEV_WRITE_APPROVAL that matches the schema after approval; do not set it beforehand.
# Run from backend; credentials/CA only from the secret environment.
.\gradlew.bat workflowDevelopmentSmoke --args="--development-integration migrate" --offline --no-daemon --no-configuration-cache --quiet
~~~

Clear the write approval in a `finally` block, even when the command fails. Stop after
migrate to audit through a new READ ONLY connection. Smoke/read/restart are steps with
their own approval; do not run smoke in the same batch as migrate, and do not infer an
approval from the schema bootstrap.

The schema must already exist, be empty and be owned by postgres; the schema bootstrap is
a separate approval and is not done by the runner. Migrate runs only V3/V4: 5 tables plus
the Flyway history, 2 functions/9 explicit triggers (6 row, 3 statement), a seed of 2
definitions/7 states/5 transitions, and 2 success history rows/checksums. Smoke creates at
most 2 instances/4 history rows for a new run-id, races activation at version
0/transition, checks Instant nanos and replay; read uses a new process/JVM and does not
write. The smoke data is kept. This shows durability across a new JVM; a cloud restart of
Spring with the production bean still needs separate evidence.

If V3 committed and V4 failed, or on `WORKFLOW_DEVELOPMENT_FAIL_COMMIT_OUTCOME_UNKNOWN`,
stop, read the catalog/history/instances through a new connection and ask for a recovery
approval; do not rerun automatically, clean/repair/baseline or delete data that was
committed. The admin account can still act outside the schema; the guard narrows the
scope of the tool but is not a sandbox for admin privileges and does not remove
privileged concurrent DDL.

### Read-only Supabase preflight before the cloud migrations

**Update after the migrations:** the owner confirmed V3/V4 `COMMITTED_PASS`, with
checksum, inventory, seed and post-commit audit PASS, `MIGRATIONS_EXIT=0`. The migration
commands above and below are history; **do not run the bootstrap or Flyway again**.
The owner also confirmed the cloud smoke `cloud-20261015-01` COMMITTED_PASS, with
precheck, postcheck and fresh-JVM persistence PASS, 2 instances / 4 history rows, exit 0.
Do not run the cloud smoke again; keep the test data. The plan, data and recovery are in
the section "Cloud smoke after migrations" in the historical evidence of Issue #25; the
old document path is not present in this version.

From the repository root, with the Direct host/CA/password supplied through a secure
environment:

```powershell
$env:DB_PORT = '5432'
$env:DB_NAME = 'postgres'
$env:DB_USER = 'postgres'
powershell.exe -NoProfile -File .\scripts\workflow-read-only-preflight.ps1
if ($LASTEXITCODE -ne 0) { throw 'Direct read-only preflight failed' }
powershell.exe -NoProfile -File .\scripts\workflow-live-guard.ps1
if ($LASTEXITCODE -ne 0) { throw 'Reviewed catalog guard failed' }
```

Expected checks: Direct IPv6, client verify-full/CA, backend SSL=true,
transaction_read_only=on, session_user=current_user=postgres, the right database;
the schema is absent or its owner/ACL/inventory match the plan; the two custom roles are
still NOLOGIN; no drift outside the scope, and durability/settings and the manifest/bundle
pin match. The owner must also check that the Dashboard API exposed schemas do not
contain the test schema. `LIVE_GUARD=PASS` only verifies the catalog;
WRITE_READINESS=BLOCKED does not grant an approval by itself. The target has now been
bootstrapped: if a fresh preflight reports ABSENT, stop and report the discrepancy, and do
not run the bootstrap again. The dev check must return EMPTY before the migration. Do not
run Stage 1A/1B or change the credentials/custom roles.

### Schema bootstrap is complete — do not run it again

The owner reported SCHEMA_BOOTSTRAP=COMMITTED_PASS, POSTCOMMIT_AUDIT=PASS,
SCHEMA_OWNER=postgres, SCHEMA_EMPTY=YES, FLYWAY_HISTORY=ABSENT,
OTHER_CLOUD_WRITES=NONE, BOOTSTRAP_EXIT=0.
This is evidence supplied by the owner; Codex did not run the cloud step again.
Do not run workflow-schema-bootstrap.ps1 or CREATE SCHEMA again.

V3/V4 and the cloud smoke are complete according to the owner report. The Flyway V3/V4
execution part (see the issue and the test evidence related to #25) is a historical
record; it is not a next step and must not be run again.
The launcher locks the exact Direct endpoint and schema, and stops by itself if a
precheck FAILs. Use the Direct endpoint db.zsfctpnitkdztlfhzqgw.supabase.co:5432/postgres,
the postgres account, TLS verify-full and CA/credentials from the secret environment. A
fresh precheck must confirm that the schema is PRESENT/empty/owned by postgres and that
the guard/hash has not drifted; do not use the ABSENT condition from the historical
bootstrap plan.

The migration approval must cover the pinned V3/V4, the Flyway history, the V4 seed and
the V3 object ACL revocations only within the target; it does not cover smoke, role
changes or recovery. Do not call smoke in the same batch as migrate. If the migration
fails or the ACK is lost: stop, clear the write approval in a `finally` block, and
reconcile through a new READ ONLY connection; no retry/clean/repair/baseline/DROP. Run
the full postcheck before reporting a cloud PASS.

### Historical V3/V4 launcher — complete, do not run again

The command is kept so the executed work can be reviewed; do not run it while preparing a PR:

~~~powershell
& 'C:\Users\Admin\AppData\Local\codex-with-chatgpt\worktrees\dxos-data-postgres-adapter\scripts\workflow-approved-migrations.ps1' -ExecuteApprovedMigrations
~~~

By default it uses PGSSLROOTCERT; if that is not set, it asks for the CA path. The
password comes from an existing DB_PASSWORD or a hidden prompt. The launcher requires
JDK 21, WARP Connected and a Direct host with IPv6; it does not turn WARP on or fix it,
and does not fix a wrong CA or endpoint. The previous environment is restored in a
`finally` block; Gradle runs offline with no configuration cache and no exception
logging. It prints only a complete allowlisted report; a child that disappears or leaves
no report after the handoff is COMMIT_UNKNOWN.

The Java task workflowApprovedMigration runs only the pinned V3/V4 with
createSchemas=false and no baseline/repair/clean/retry/smoke. The READ ONLY precheck
verifies an empty schema owned by postgres, no history, TLS verify-full/backend SSL,
PG17.11, NOLOGIN custom roles, the raw hash of the manifest and the migration SHA/CRC.
The guard is repeated whenever a connection is opened. After the migration it uses a new
READ ONLY connection to check: history, an exact catalog fingerprint, the seed/0
instances, the schema ACL/owner, and a snapshot of the outside catalog/roles/membership.
The fingerprint includes columns/defaults/NOT NULL, indexes, constraints, function
definitions/ACL, explicit/internal triggers and types, not only counts. It exits 0 only
on COMMITTED_PASS plus audit/inventory/seed PASS; on an error it stops and does not retry.

Keep COMMIT_UNKNOWN when the ACK is lost even if the audit finds the data; the history and
the seed are reconciled separately, and success is not inferred from one side only. If V3
committed and V4 failed, the result is PARTIAL_COMMIT and is left untouched for the owner
to approve a recovery. A catalog drift or a fresh audit that cannot be read must not claim
OTHER_CLOUD_WRITES=NONE. In every case it stops after the migration/audit with
NEXT_APPROVAL_REQUIRED=YES for the cloud smoke.

### Optional hardening — read-only Runtime Privilege Audit on Supabase

From the worktree root, with JDK 21 and the variables DB_HOST, DB_PORT, DB_NAME, DB_USER,
DB_PASSWORD and PGSSLROOTCERT already set in the PowerShell session:

```powershell
powershell.exe -NoProfile -File .\scripts\workflow-runtime-privilege-audit.ps1
$LASTEXITCODE
```

The launcher supports the Direct Connection or the session pooler, port 5432; it forces
verify-full/CA, search_path pg_catalog,pg_temp and transaction_read_only=on. The audit SQL
is pinned by SHA-256; changing the SQL needs a review and an update of the pin. It does
not run Spring/Flyway/provisioning/smoke. WORKFLOW_EVENT_GUARD_LOCAL_DISPOSABLE must not
be set, even with the value false. Secrets are inherited only through the environment;
they are not passed through args, printed or written to a report.

AUDIT_REPORT contains only fixed role names, statuses, booleans/counts and the number of
true privileges per role/privilege; it contains no host/database/object identifiers,
function source, passwords or connection strings. NOT_PROVISIONED means the role does not
exist yet; it is not a permission PASS. RUNTIME_PRIVILEGE_AUDIT=PASS only confirms that
the catalog audit completed and the rollback/close succeeded; WRITE_READINESS stays
BLOCKED and a reviewer must assess the ACL/TLS.

### Optional hardening — SECURITY DEFINER metadata and private review

Run from the repository root in a PowerShell session that already holds `DB_*` and
`PGSSLROOTCERT`:

```powershell
powershell.exe -NoProfile -File .\scripts\workflow-security-definer-review.ps1
$LASTEXITCODE
```

The separate launcher uses JDBC `verify-full`, `pg_catalog,pg_temp`, a READ ONLY
transaction and SQL pinned by SHA-256. The metadata keeps the schema/signature/owner,
the EXECUTE/schema ACL, the function search_path, the nullable runtime privileges,
membership, dependencies and the definition/configuration fingerprints. It does not
return bodies or other GUCs. `NOT_PROVISIONED` keeps the runtime privileges as `null`,
not `false`.

Only after the valid metadata has been reviewed, use the `SHAREABLE_METADATA` path to
capture the bodies/configuration into a new protected directory outside Git:

```powershell
powershell.exe -NoProfile -File .\scripts\workflow-security-definer-review.ps1 -MetadataFile '<SHAREABLE_METADATA>'
```

The baseline must be in a directory that only the current user/SYSTEM can access; a
catalog drift, a wrong SQL pin, a rollback/close failure or a wrong TLS configuration all
fail closed. Share only `shareable-metadata.json`; do not send `private-function-review.json`
or credentials into chat/Git. When a body review finds a helper, capture new metadata with
`-HelperSignature 'schema.helper(argument_types)'`, then do the private capture from that
new baseline. Catalog dependencies are incomplete for dynamic SQL and string-body
routines. Every routine starts as `NEEDS_REVIEW`; a successful capture does not by itself
grant a security PASS, accept PUBLIC TEMP, approve roles or resolve the backend-hop TLS.

### Optional hardening — runner with a separate migrator/runtime

`workflowSmokeBundle` copies only V3/V4. The runner checks exactly two filenames and the
SHA-256 values pinned in `workflow-event-trigger-manifest.json` (CRLF normalized to LF),
together with the Flyway checksums/history. It does not load V1/V2.
The schema is fixed: dxos_wf25_smoke_01; the history lives in the same schema.
The runner does not boot Spring, does not create a schema/role by itself, does not
GRANT, clean up, DROP/TRUNCATE/DELETE, or retry when the commit outcome is unknown.

Independent variables: WORKFLOW_SMOKE_JDBC_URL (containing no user/password),
WORKFLOW_SMOKE_PROJECT_REF (required for the cloud), WORKFLOW_SMOKE_CA_CERT,
WORKFLOW_SMOKE_MIGRATOR_USER/PASSWORD, WORKFLOW_SMOKE_RUNTIME_USER/PASSWORD and
WORKFLOW_SMOKE_BUNDLE (the bundle path); WORKFLOW_SMOKE_RUN_ID is used for smoke/read when
the run-id is not passed through args. Supply secrets through a secure environment outside
chat. The cloud accepts only the Direct endpoint db.<project-ref>.supabase.co:5432/postgres
with the correct project ref, an existing CA file and TLS verify-full; the two usernames
are the direct PostgreSQL role names, with no project-ref suffix. The cloud URL has no
query/fragment; currentSchema and TLS are set only by the runner. Without a CA it stops.
WORKFLOW_SMOKE_LOCAL_DISPOSABLE=true is for loopback only and cannot lower the cloud TLS.

The migrator is the owner of the dedicated schema, with USAGE/CREATE on the schema and
USAGE on plpgsql. The runtime differs from the owner, is not a member of the owner, has
no CREATE on the schema and is not a superuser/CREATEROLE/CREATEDB/BYPASSRLS. After the
migration, the operator grants the runtime: USAGE on the schema, SELECT on the five
Workflow tables, INSERT on instances/history, and UPDATE only on
current_state/lifecycle/runtime_version/updated_at_seconds/updated_at_nanos of instances.
No DDL, no definition provisioning, no DELETE or TRUNCATE. Do not change default
privileges, database privileges or role membership. Using postgres as the migrator
creates objects that postgres owns; a powerful role can disable triggers or edit the
history, so use it only for an approved migration step and never as the runtime.
Customized default privileges or event triggers that differ from the manifest make the
runner stop; do not fix them or disable triggers yourself. The manifest locks exactly
six triggers, the function/config hashes, the owners/ACL and two reviewed internal
helpers. An OID capture is only evidence; helpers are resolved live by signature. The
remote accepts only the filesystem V3/V4 bundle and PostgreSQL 17.11. The local profile
needs `WORKFLOW_EVENT_GUARD_LOCAL_DISPOSABLE=true`, loopback and a completely empty
inventory of event triggers; the flag does not allow skipping an unfamiliar trigger or
the cloud. The guard reads hashes/config keys and does not load private bodies/config
values; a separate collector still keeps the private capture outside Git. The native
binary is a provider-trust assumption and is not attested by a catalog hash. Approved
watchers may send a NOTIFY to reload the schema. The live checks run on every connection,
before the migration and before each migration; the bundle is checked again at the
connection boundary too. They narrow the TOCTOU window but do not remove privileged
concurrent DDL or concurrent filesystem mutation.

```powershell
.\gradlew.bat workflowSmokeBundle --no-daemon
.\gradlew.bat workflowSmoke --args=check --no-daemon
# The commands below ONLY after a separate approval and a suitable role/schema bootstrap:
.\gradlew.bat workflowSmoke --args=migrate --no-daemon
# The operator grants the approved minimal runtime privileges, then:
.\gradlew.bat workflowSmoke --args="smoke unique-run-id" --no-daemon
.\gradlew.bat workflowSmoke --args="read unique-run-id" --no-daemon
```

check uses read-only transactions and verifies ownership/privileges, mode/durability,
the absence of unreviewed event triggers/default privileges, that the schema is empty or
has exactly the six tables, and the bundle and migration history. migrate accepts only a
schema that already exists and is empty. smoke creates two instances with their own
issue25/run-id prefix, races activation at version 0, races a transition, completes both
definitions, and checks the two history rows per instance and the Instant nanos. A run-id
that was already used is rejected. read uses a new JVM/connection to check the
snapshots/history and does not write. After an error or COMMIT_OUTCOME_UNKNOWN, stop and
investigate; do not rerun by yourself. The smoke data is kept.

## Dependency on Issue #3 and the limits of verification

Issue #3 is responsible for Docker/PostgreSQL for development: the database, account,
credentials and a suitable host/port. Issue #1 does not create a container, a business
schema, or any mechanism to bypass the database connection.

When the Issue #3 environment is not available, you can verify compilation, the MVC
tests and the JAR packaging; you cannot verify PostgreSQL integration, the whole startup
with JPA, or the HTTP health of a real application connected to PostgreSQL.

After Issue #3 is complete, provide all the `DB_*` variables (and the `OIDC_*` variables),
run `bootRun`, and check the startup, `/api/v1/health` and `/actuator/health` against a
real PostgreSQL.

Verification of the V3/V4 launcher (2026-10-15): full JDK 21 / PostgreSQL 17.11 TLS
disposable run, 752 PASS, 0 FAIL/SKIP, 9 integration suites, build PASS; this includes 38
new tests. This is not a cloud execution; Codex lacked credentials/CA and is waiting for
the owner to run the launcher.
