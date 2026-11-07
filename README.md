# OpenTrix — DX-OS Open-Core

**Reusable digital capabilities for internal service applications.**

OpenTrix is TRICORE's open-source implementation of DX-OS Open-Core, built for OLP PMNM 2026. DX-OS is a digital-transformation platform concept, not a computer operating system. The demonstration scenario is an **IT Helpdesk / Internal Service Portal**: employees submit requests, a coordinator triages and assigns them, a worker resolves them, and the requester confirms.

**Navigate:** [What it does](#what-it-does) · [Architecture](#architecture) · [Quick start](#quick-start-mock-portal) · [Build from source](#build-from-source) · [Run with PostgreSQL](#run-the-backend-with-postgresql) · [Configuration](#configuration) · [Known limitations](#known-limitations) · [Contributing](#reporting-issues-and-contributing) · [License](#license)

## What it does

Internal requests often arrive through email, paper, spreadsheets, and chat, so ownership and history get lost. OpenTrix puts submission, assignment, processing, and status in one application, and keeps the reusable mechanisms in a Core that other applications can share.

| Capability | What you get | Application keeps |
| --- | --- | --- |
| Identity / SSO | OIDC token verification, principal and authority contracts (Keycloak is the selected provider) | Business roles and request-specific permissions |
| API Gateway | Spring Boot API boundary, verified caller checks, scoped error contracts | User-facing business operations |
| Workflow | In-house state machine: definitions, instances, transitions, versions, history | Business states and conditions |
| Data | PostgreSQL 17 persistence behind a port, with transaction guards | Business data, ownership, retention |
| Helpdesk app | `it-helpdesk@1` workflow `SUBMITTED → TRIAGED → IN_PROGRESS → RESOLVED → CONFIRMED`, nine HTTP routes under `/api/v1/mvp/requests` | — |
| Portal BFF | Server-side OIDC (PKCE), session and CSRF boundary in front of the backend | — |
| React Portal | Vietnamese SPA; standalone **MOCK** mode and an `integration-local` mode that talks to the BFF | — |

## Architecture

The backend is a Java 21 / Spring Boot **modular monolith**; the boundaries below are logical, not separately deployed services.

```text
External client / application
            |
            v
    API Gateway boundary
       /          \
      v            v
 Identity       Application
 contracts         layer
                     |
                     v
                Workflow Core
                     |
                     v
         WorkflowPersistencePort
                     |
                     v
        Data / persistence adapter
                     |
                     v
                 PostgreSQL
```

Workflow owns `WorkflowPersistencePort`; a data adapter implements it. Gateway owns neither business rules nor persistence, and client-supplied identity headers are never trusted just because they reached the HTTP boundary. In the browser flow, the React Portal talks only to the Portal BFF, and the BFF forwards the server-held access token to the backend.

```text
opentrix/
├── backend/      # Spring Boot backend (Gradle wrapper lives here)
├── portal-bff/   # Spring Boot OIDC/session boundary for the Portal
├── frontend/     # React 19 + TypeScript + Vite Portal
├── infra/        # Local infrastructure (PostgreSQL 17 compose file)
├── scripts/      # Helper and verification scripts
└── docs/         # Design notes, decisions, deployment notes
```

## Quick start (MOCK Portal)

The fastest way to see the UI. It uses in-memory demo data and needs **no backend, database, credentials, or SSO**.

Requires Node.js **22.12 or newer** and npm.

```bash
git clone https://github.com/tricore-opentrix/opentrix.git
cd opentrix/frontend
npm ci
npm run dev
```

Open <http://127.0.0.1:5173>. On Windows PowerShell use `npm.cmd` instead of `npm`.

## Build from source

Prerequisites: Git, **JDK 21** (`JAVA_HOME` set or `java` on `PATH`), Node.js ≥ 22.12 with npm, and internet access on the first run (Gradle wrapper and dependencies). You do not need to install Gradle. Building and unit-testing does **not** need PostgreSQL.

These are the same commands CI runs on `ubuntu-24.04`.

### Linux / macOS

```bash
git clone https://github.com/tricore-opentrix/opentrix.git
cd opentrix

# Backend: compile, test, build the executable JAR
(cd backend && ./gradlew build)

# Portal BFF (reuses the backend's Gradle wrapper)
./backend/gradlew -p portal-bff build

# Frontend: install, type-check + build, test
(cd frontend && npm ci && npm run build && npm test)
```

Artifacts: `backend/build/libs/dxos-backend-0.0.1-SNAPSHOT.jar` and `frontend/dist/`. To run a single backend test class: `cd backend && ./gradlew test --tests 'com.tricore.dxos.core.workflow.*'`.

### Windows (PowerShell)

```powershell
git clone https://github.com/tricore-opentrix/opentrix.git
Set-Location opentrix
Push-Location backend; .\gradlew.bat build; Pop-Location
.\backend\gradlew.bat -p portal-bff build
Push-Location frontend; npm.cmd ci; npm.cmd run build; npm.cmd test; Pop-Location
```

## Run the backend with PostgreSQL

The backend refuses to start unless all variables below are set; there are no defaults. Spring Boot does **not** read `.env` automatically, so export the values in the shell that starts the process, and never commit real credentials.

You need a PostgreSQL 17 database with the Workflow schema already provisioned (`DXOS_WORKFLOW_SCHEMA` names it). The repository ships a disposable local database: [`infra/compose.workflow-postgres.yml`](infra/compose.workflow-postgres.yml). The step-by-step provisioning (roles, schema, migrations) is in the [backend guide](backend/README.md#chạy-backend-local-từ-clone-mới).

```bash
cd backend

export DB_HOST=127.0.0.1
export DB_PORT=55425
export DB_NAME=workflow_test
export DB_USER=workflow_runtime
read -rs -p 'DB_PASSWORD: ' DB_PASSWORD; export DB_PASSWORD; echo

export DXOS_WORKFLOW_SCHEMA=dxos_wf25_smoke_01
export SPRING_DATASOURCE_URL="jdbc:postgresql://${DB_HOST}:${DB_PORT}/${DB_NAME}?currentSchema=${DXOS_WORKFLOW_SCHEMA},pg_catalog,pg_temp"
export SPRING_FLYWAY_ENABLED=false

export OIDC_ISSUER_URI=http://localhost:8180/realms/tricore
export OIDC_AUDIENCE=tricore-api
export OIDC_RESOURCE_CLIENT_ID=tricore-api

./gradlew bootRun
```

The values above match the local database in the backend guide and `.env.example`; replace them for your own environment. Optionally set `DXOS_HELPDESK_ENABLED=true` to register the Helpdesk routes under `/api/v1/mvp/requests`.

In another terminal:

```bash
curl http://localhost:8080/api/v1/health
# {"status":"UP"}
```

`UP` only shows the HTTP application is running. Calling protected routes needs a token from a real Keycloak realm whose issuer matches `OIDC_ISSUER_URI` exactly.

<details>
<summary>Windows PowerShell version</summary>

```powershell
Set-Location backend
$env:DB_HOST = '127.0.0.1'
$env:DB_PORT = '55425'
$env:DB_NAME = 'workflow_test'
$env:DB_USER = 'workflow_runtime'
$dbCredential = Get-Credential -UserName $env:DB_USER -Message 'PostgreSQL credentials'
$env:DB_PASSWORD = $dbCredential.GetNetworkCredential().Password
$env:DXOS_WORKFLOW_SCHEMA = 'dxos_wf25_smoke_01'
$env:SPRING_DATASOURCE_URL = "jdbc:postgresql://$($env:DB_HOST):$($env:DB_PORT)/$($env:DB_NAME)?currentSchema=$($env:DXOS_WORKFLOW_SCHEMA),pg_catalog,pg_temp"
$env:SPRING_FLYWAY_ENABLED = 'false'
$env:OIDC_ISSUER_URI = 'http://localhost:8180/realms/tricore'
$env:OIDC_AUDIENCE = 'tricore-api'
$env:OIDC_RESOURCE_CLIENT_ID = 'tricore-api'
.\gradlew.bat bootRun
```

Check health with `Invoke-RestMethod -Uri 'http://localhost:8080/api/v1/health'`.

</details>

### Full stack with login (advanced)

The connected Portal (`npm run build:integration-local`) needs a Keycloak client, the Portal BFF, and an HTTPS ingress (Caddy). Follow the [Portal BFF guide](portal-bff/README.md) and the [local Helpdesk runbook](scripts/README-helpdesk-local.md). These guides are currently written for Windows PowerShell; a one-command Linux setup is planned.

## Configuration

Copy [`.env.example`](.env.example) as a reference for the variable names.

| Variable | Used by | Meaning |
| --- | --- | --- |
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | backend | PostgreSQL connection (JDBC URL is built from these) |
| `DXOS_WORKFLOW_SCHEMA` | backend | Lowercase schema that holds the Workflow tables; must exist before startup |
| `SPRING_DATASOURCE_URL` | backend | Overrides the JDBC URL; use it to set `currentSchema` as shown above |
| `SPRING_FLYWAY_ENABLED` | backend | `false` at runtime; migrations are applied separately (see the backend guide) |
| `OIDC_ISSUER_URI` | backend | Exact issuer URL of the Keycloak realm |
| `OIDC_AUDIENCE`, `OIDC_RESOURCE_CLIENT_ID` | backend | Expected token audience and the client whose roles are read |
| `DXOS_HELPDESK_ENABLED` | backend | `true` registers the Helpdesk API routes |
| `PORTAL_*` | portal-bff | OIDC client and origin settings; see the [Portal BFF guide](portal-bff/README.md) |

## Known limitations

- The MOCK Portal is a demonstration, not a live application or a security check.
- The full browser login (Keycloak + PKCE) and the three-persona Helpdesk flow have not been accepted end to end yet.
- A one-command Docker Compose demo is planned; today the full stack needs manual Keycloak, PostgreSQL, and Caddy setup.
- APISIX (gateway), an object-storage provider and Node-RED are planned and not part of the current runtime; Facility reuse is shown only in the MOCK Portal.
- The local setup guides under `scripts/` and `portal-bff/` are written for Windows PowerShell.

## Documentation

- [Backend guide](backend/README.md): configuration, APIs, tests, local database.
- [Portal BFF guide](portal-bff/README.md) and [frontend guide](frontend/README.md).
- [Glossary](GLOSSARY.md) and the [docs index](docs/README.md).
- [CHANGELOG.md](CHANGELOG.md): user-visible changes.

## Reporting issues and contributing

- **Report a bug or request a feature:** open an [issue](https://github.com/tricore-opentrix/opentrix/issues) with the commit you tested, your OS, the command you ran, and the output.
- **Contribute:** read [CONTRIBUTING.md](CONTRIBUTING.md). In short: branch from `main`, open a pull request with a Conventional Commits title, keep it near 400 changed lines, and make sure CI passes. Changes land by squash merge only.
- New source files need an SPDX header (see CONTRIBUTING.md).

## Team

TRICORE is a student team in OLP PMNM 2026: Lê Xuân Bảo, Phan Hải Yến, Nguyễn Ngọc Ánh.

## License

Original material is released under the **Apache License 2.0** ([LICENSE](LICENSE), attribution in [NOTICE](NOTICE)). Third-party dependencies keep their own licenses; see [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).
