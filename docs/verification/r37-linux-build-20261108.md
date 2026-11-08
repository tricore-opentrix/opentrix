<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors

SPDX-License-Identifier: Apache-2.0
-->

# R37 — Build and run on Linux (2026-11-08)

Evidence that the repository builds from source and the backend starts on Linux by following the root README and [the Linux runbook](../06-deployment/runbook-linux.md). Output below is copied from the terminal; no passwords, tokens, or personal paths are included.

**What this covers.** The runs were made on `main@187dbd2`. PR #158 changes only Markdown, removes nine empty `.gitkeep` files and adds `scripts/check_md_links.py`; it does not touch `backend/src`, `portal-bff/` or `frontend/src`, so the build results apply to the PR head as well. CI results for the PR head are linked in the PR conversation. Docs-only checks (link check, removed paths) are in [r37-docs-cleanup-20261108.md](r37-docs-cleanup-20261108.md).

## Environment

| Item | Value |
| --- | --- |
| OS | Ubuntu 26.04 (VirtualBox VM, 4 vCPU, 5.3 GiB RAM) |
| JDK | OpenJDK 21.0.12.1 |
| Node.js | v22.23.4 |
| Docker / Compose | Docker 29, Compose 2.40.3 |
| Source | `tricore-opentrix/opentrix`, `main@187dbd2`, fresh `git clone` into `~/opentrix` |
| Run by | A TRICORE team member (not an outside tester) |

## Results

| Step | Command | Result |
| --- | --- | --- |
| Backend build | `(cd backend && ./gradlew clean build)` | `BUILD SUCCESSFUL in 38s`, 9 of 9 tasks executed. JUnit XML totals: **783 tests, 0 failures, 0 errors, 171 skipped** |
| Portal BFF build | `./backend/gradlew -p portal-bff clean build` | `BUILD SUCCESSFUL in 15s`, 9 of 9 tasks executed. JUnit XML totals: **2 test files, 28 tests, 0 failures or errors, 0 skipped** |
| Frontend | `(cd frontend && npm ci && npm run build && npm test)` | 16 test files, **385 of 385 tests passed** |
| PostgreSQL 17 | `docker compose -f ../infra/compose.workflow-postgres.yml up -d --wait` | container `Healthy` (PostgreSQL 17.11) |
| Role and schema | `psql` statements from runbook step 4 | `CREATE ROLE`, `CREATE SCHEMA`, `GRANT` |
| Migrations | `./gradlew workflowSmokeBundle workflowSmoke --args=migrate --no-daemon` | `MIGRATION_PASS` |
| Backend without Keycloak | `./gradlew bootRun` | **Fails to start**: `Connection refused` on `http://localhost:8180/realms/tricore/.well-known/openid-configuration` |
| Keycloak 26.0 `start-dev`, empty realm `tricore` | runbook step 6 | discovery document served on port 8180 |
| Backend with Keycloak | `./gradlew bootRun`, then `curl http://localhost:8080/api/v1/health` | `{"status":"UP"}` |

The backend and Portal BFF were also built earlier in the same session with the same commands; those runs reported `BUILD SUCCESSFUL` and are not repeated here.

### Second pass: privilege grants and smoke runner

Runbook steps 3 to 5 were repeated on a fresh volume, then the optional smoke runner was run (same VM, same source):

| Step | Command | Result |
| --- | --- | --- |
| Migrations, first attempt | `./gradlew workflowSmokeBundle workflowSmoke --args=migrate --no-daemon` | `WORKFLOW_SMOKE_FAIL`. The runner hides the reason on purpose. Probable cause, not proven: the runtime password typed into `RUNTIME_DB_PASSWORD` differed from the one set with `\password`; resetting the role password to that value fixed it |
| Reset runtime password | `ALTER ROLE workflow_runtime PASSWORD :'pw'` via `psql -v pw=...` | `ALTER ROLE` |
| Migrations, second attempt | same command as above | `MIGRATION_PASS`, `BUILD SUCCESSFUL in 10s` |
| Runtime grants | the three `GRANT` statements from runbook step 5 | three times `GRANT` |
| Smoke | `./gradlew workflowSmoke --args="smoke local-first-run" --no-daemon` | `SMOKE_PASS` |
| Read after restart | `./gradlew workflowSmoke --args="read local-first-run" --no-daemon` | `RESTART_READ_PASS` |
| Privilege check | `has_table_privilege` INSERT, DELETE and `has_column_privilege` UPDATE on `current_state`, as `workflow_runtime` | `t\|f\|t` (INSERT allowed, DELETE denied, UPDATE on that column allowed) |

The database, network and volume were removed afterwards with `down -v`.

### The 171 skipped backend tests

All 171 are conditional tests that did not run in this build, none are failures:

| Group | Tests | Condition |
| --- | --- | --- |
| 12 PostgreSQL and Keycloak integration classes (for example `HelpdeskHttpPostgresTest`, `WorkflowIsolationIntegrationTest`, `PostgresWorkflowPersistenceIntegrationTest`, `OidcKeycloakIntegrationTest`) | 157 | `@EnabledIfEnvironmentVariable`: they run only when the variables pointing at a disposable database or Keycloak are set |
| 5 PowerShell launcher classes (`WorkflowSecurityDefinerReviewLauncherTest`, `WorkflowRuntimePrivilegeAuditLauncherTest`, `WorkflowApprovedMigrationTest`, `WorkflowSchemaBootstrapTest`, `WorkflowApprovedSmokeLauncherTest`) | 14 | `@EnabledOnOs(OS.WINDOWS)` |

The 157 environment-gated tests were not run with their variables set, so this build says nothing about them. The smoke runner above covers only the migration, grants, write and read-after-restart path.

## Findings

- The backend requires a reachable Keycloak realm at `OIDC_ISSUER_URI` to start, even for the health endpoint. The previous README did not say so; the README and runbook were corrected.
- `docker compose down` needs `WORKFLOW_LOCAL_DB_PASSWORD` defined even when only stopping; the runbook cleanup step was corrected.
- The smoke runner prints only `WORKFLOW_SMOKE_FAIL` when a login fails, so a mistyped runtime password is easy to miss; a troubleshooting row was added to the runbook.

## Not covered (open items)

| Item | Status | Owner |
| --- | --- | --- |
| The 157 environment-gated integration tests | Not run with their environment variables set (see above). | @lexuanbao258-collab |
| The 14 Windows-only launcher tests | Cannot run on Linux; they exercise the PowerShell scripts. | Not assigned |
| Authenticated routes, Helpdesk flow, Portal BFF login, Caddy ingress | Not exercised; no client, user or token was created in Keycloak. `{"status":"UP"}` shows the process started and the database connected; it is not an end-to-end result. | Not assigned |
| Reproduction on a clean machine by someone outside the team | Not done. This run was made on a VM by a team member. | Not assigned |
