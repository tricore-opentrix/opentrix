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

## Not covered (open items)

| Item | Status | Owner |
| --- | --- | --- |
| Runtime privilege grants (runbook step 5) and the optional smoke runner (`SMOKE_PASS`, `RESTART_READ_PASS`) | Not run. `{"status":"UP"}` shows the process started and the database connected; it is not an end-to-end result and does not prove the grants. | @lexuanbao258-collab |
| 171 skipped backend tests | Not classified; no reason recorded per test. | @lexuanbao258-collab |
| Portal BFF test count | Not collected. | @lexuanbao258-collab |
| Authenticated routes, Helpdesk flow, Portal BFF login, Caddy ingress | Not exercised; no client, user or token was created in Keycloak. | Not assigned |
| Reproduction on a clean machine by someone outside the team | Not done. This run was made on a VM by a team member. | Not assigned |
