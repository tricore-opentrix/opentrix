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

## Clean-clone rerun by the README author (2026-11-08)

Run to follow the README text on a fresh clone; it is **not** an independent reproduction.

| Item | Value |
| --- | --- |
| Commit | `468eed09463e9f441e48871b7d91788e336aa4fc` (checked with `git rev-parse HEAD`) |
| Machine | Ubuntu 26.04.1 LTS, x86_64, VirtualBox VM on a Windows host |
| Tools | git 2.53.0, OpenJDK 21.0.12.1 (Ubuntu package), Node.js 22.23.4 via nvm, npm 10.9.9; all already installed on this VM |
| Run by | @lexuanbao258-collab, the README author |
| Preparation | New clone in an empty directory; `~/.gradle` and `~/.npm` renamed aside so dependencies were downloaded again |

| Step (README "Build from source → Linux / macOS" and "Quick start") | Result |
| --- | --- |
| `(cd backend && ./gradlew build)` | PASS, `BUILD SUCCESSFUL in 2m 11s`, 8 tasks executed |
| `./backend/gradlew -p portal-bff build` | PASS, 19 s |
| `(cd frontend && npm ci && npm run build && npm test)` | PASS, 16 test files, 385 / 385 tests, `found 0 vulnerabilities` |
| Artifacts | `frontend/dist/` present; backend JAR present as `dxos-backend-0.1.0.jar` (see deviations) |
| MOCK Portal (`npm run dev`, <http://127.0.0.1:5173>) | PASS, demo dashboard rendered with mock data and the "not real SSO" notice |
| Backend with PostgreSQL and Keycloak (runbook) | Not rerun on this commit; see the earlier run above |

Deviations:

- The README named the JAR `dxos-backend-0.0.1-SNAPSHOT.jar`; since the v0.1.0 release commit the build produces `dxos-backend-0.1.0.jar` and `dxos-backend-0.1.0-plain.jar`. `README.md` and `backend/README.md` were corrected to `dxos-backend-<version>.jar`.
- The Gradle Wrapper download returned HTTP 504 from GitHub Releases (`github.com` itself answered 200 and no proxy was set). To continue, only the Gradle 8.14.3 distribution was copied back from the renamed cache; `~/.gradle/caches` stayed empty, so all dependencies were downloaded fresh. This is an environment issue, not a documentation one.
- The VM was not freshly installed (tools preinstalled; `sudo` was not used).

## Findings

- The backend requires a reachable Keycloak realm at `OIDC_ISSUER_URI` to start, even for the health endpoint. The previous README did not say so; the README and runbook were corrected.
- The README named a JAR file that the build no longer produces (`0.0.1-SNAPSHOT` instead of `0.1.0`); found by the clean-clone rerun and corrected.
- `docker compose down` needs `WORKFLOW_LOCAL_DB_PASSWORD` defined even when only stopping; the runbook cleanup step was corrected.
- The smoke runner prints only `WORKFLOW_SMOKE_FAIL` when a login fails, so a mistyped runtime password is easy to miss; a troubleshooting row was added to the runbook.

## Not covered (open items)

| Item | Status | Owner |
| --- | --- | --- |
| The 157 environment-gated integration tests | Not run with their environment variables set (see above). | @lexuanbao258-collab |
| The 14 Windows-only launcher tests | Cannot run on Linux; they exercise the PowerShell scripts. | Not assigned |
| Authenticated routes, Helpdesk flow, Portal BFF login, Caddy ingress | Not exercised; no client, user or token was created in Keycloak. `{"status":"UP"}` shows the process started and the database connected; it is not an end-to-end result. | Not assigned |
| Reproduction on a clean machine by someone outside the team | Not done. Both runs were made by a team member (the second by the README author on a fresh clone, see above). No outside tester is available to the team; whether this satisfies the R37 gate is for the reviewer to decide. | @phanyen06ym-ien (decision) |
