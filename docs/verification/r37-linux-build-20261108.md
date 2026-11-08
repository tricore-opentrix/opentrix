<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors

SPDX-License-Identifier: Apache-2.0
-->

# R37 — Build and run on Linux (2026-11-08)

Evidence that the repository builds from source and the backend starts on Linux by following the root README and [the Linux runbook](../06-deployment/runbook-linux.md). Output below is copied from the terminal; no passwords, tokens, or personal paths are included.

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
| Portal BFF build | `./backend/gradlew -p portal-bff clean build` | `BUILD SUCCESSFUL in 15s`, 9 of 9 tasks executed |
| Frontend | `(cd frontend && npm ci && npm run build && npm test)` | 16 test files, **385 of 385 tests passed** |
| PostgreSQL 17 | `docker compose -f ../infra/compose.workflow-postgres.yml up -d --wait` | container `Healthy` (PostgreSQL 17.11) |
| Role and schema | `psql` statements from runbook step 4 | `CREATE ROLE`, `CREATE SCHEMA`, `GRANT` |
| Migrations | `./gradlew workflowSmokeBundle workflowSmoke --args=migrate --no-daemon` | `MIGRATION_PASS` |
| Backend without Keycloak | `./gradlew bootRun` | **Fails to start**: `Connection refused` on `http://localhost:8180/realms/tricore/.well-known/openid-configuration` |
| Keycloak 26.0 `start-dev`, empty realm `tricore` | runbook step 6 | discovery document served on port 8180 |
| Backend with Keycloak | `./gradlew bootRun`, then `curl http://localhost:8080/api/v1/health` | `{"status":"UP"}` |

The backend and Portal BFF were also built earlier in the same session with the same commands; those runs reported `BUILD SUCCESSFUL` and are not repeated here.

## Findings

- The backend requires a reachable Keycloak realm at `OIDC_ISSUER_URI` to start, even for the health endpoint. The previous README did not say so; the README and runbook were corrected.
- `docker compose down` needs `WORKFLOW_LOCAL_DB_PASSWORD` defined even when only stopping; the runbook cleanup step was corrected.

## Not covered

- The runtime privilege grants in runbook step 5 (`GRANT SELECT/INSERT/UPDATE`) were not confirmed in this run; the health check does not exercise them, and the optional smoke runner was not run.
- No client, user, or token was created in Keycloak, so authenticated routes, the Helpdesk flow, the Portal BFF login, and Caddy ingress were not exercised.
- The 171 skipped backend tests were not individually reviewed.
- The Portal BFF test count was not collected.
- The run was done on a VM by a team member. Acceptance still calls for an outside person to follow the README on a clean machine.
