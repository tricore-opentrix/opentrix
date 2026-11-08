<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors

SPDX-License-Identifier: Apache-2.0
-->

# Runbook — build and run on Linux / macOS

This runbook takes a fresh clone to a running backend on a disposable local PostgreSQL 17. It is the bash version of [Run the backend locally from a fresh clone](../../backend/README.md#run-the-backend-locally-from-a-fresh-clone) in the backend guide; the PowerShell steps there remain the reference for Windows.

Everything here uses loopback-only resources created by the repository's compose file. Do not point these commands at a shared or cloud database.

## 1. Requirements

| Tool | Version | Check |
| --- | --- | --- |
| Git | any recent | `git --version` |
| JDK | 21 | `java -version` |
| Node.js / npm | ≥ 22.12 | `node --version` |
| Docker with Compose v2 | any recent | `docker compose version` |
| curl | any | `curl --version` |

The first Gradle run downloads Gradle 8.14.3 and dependencies, so internet access is required. Free ports: `55425` (PostgreSQL), `8080` (backend), `5173` (MOCK Portal).

## 2. Build and test

```bash
git clone https://github.com/tricore-opentrix/opentrix.git
cd opentrix
(cd backend && ./gradlew build)
./backend/gradlew -p portal-bff build
(cd frontend && npm ci && npm run build && npm test)
```

These match the CI jobs on `ubuntu-24.04`. None of them needs PostgreSQL.

If `./gradlew: Permission denied`, run `chmod +x backend/gradlew` (the file is committed as executable, so this usually means the checkout lost file modes).

## 3. Start the local PostgreSQL 17

All remaining commands run from `backend/`.

```bash
cd backend
read -rs -p 'Choose local owner password: ' WORKFLOW_LOCAL_DB_PASSWORD; echo
export WORKFLOW_LOCAL_DB_PASSWORD
docker compose -f ../infra/compose.workflow-postgres.yml up -d --wait
```

This creates container `infra-workflow-postgres-1` (compose service `workflow-postgres`) on `127.0.0.1:55425` with database and owner `workflow_test`, and a named volume `infra_workflow-postgres-17-data`. The database password is fixed when the volume is first initialised, so provision the volume only once.

**Reusing an existing volume.** You may skip steps 4 and 5 and go to step 6 only if all of these hold: the volume `infra_workflow-postgres-17-data` already exists, you export the **same** `WORKFLOW_LOCAL_DB_PASSWORD` it was created with, and steps 4 and 5 (role, schema, migrations, grants) were completed against it earlier. Check with:

```bash
docker compose -f ../infra/compose.workflow-postgres.yml exec workflow-postgres \
  psql -U workflow_test -d workflow_test -tAc \
  "SELECT count(*) FROM pg_roles WHERE rolname='workflow_runtime'
   UNION ALL SELECT count(*) FROM information_schema.schemata WHERE schema_name='dxos_wf25_smoke_01'"
```

Expected output is two lines, `1` and `1`. If either is `0`, or `psql` reports an authentication failure, do not skip: run steps 4 and 5, or remove the volume (step 9, `down -v`) and start again.

## 4. Create the runtime role and schema

```bash
docker compose -f ../infra/compose.workflow-postgres.yml exec workflow-postgres \
  psql -U workflow_test -d workflow_test
```

In `psql` (the `\password` prompt hides the runtime password):

```text
CREATE ROLE workflow_runtime LOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
\password workflow_runtime
CREATE SCHEMA dxos_wf25_smoke_01 AUTHORIZATION workflow_test;
GRANT USAGE ON SCHEMA dxos_wf25_smoke_01 TO workflow_runtime;
\q
```

## 5. Apply migrations V3/V4 and grant runtime privileges

```bash
read -rs -p 'Runtime password (same as \password above): ' RUNTIME_DB_PASSWORD; echo
export WORKFLOW_EVENT_GUARD_LOCAL_DISPOSABLE=true
export WORKFLOW_SMOKE_LOCAL_DISPOSABLE=true
export WORKFLOW_SMOKE_JDBC_URL='jdbc:postgresql://127.0.0.1:55425/workflow_test'
export WORKFLOW_SMOKE_MIGRATOR_USER=workflow_test
export WORKFLOW_SMOKE_MIGRATOR_PASSWORD="$WORKFLOW_LOCAL_DB_PASSWORD"
export WORKFLOW_SMOKE_RUNTIME_USER=workflow_runtime
export WORKFLOW_SMOKE_RUNTIME_PASSWORD="$RUNTIME_DB_PASSWORD"
export WORKFLOW_SMOKE_BUNDLE="$PWD/build/workflow-smoke-bundle"
./gradlew workflowSmokeBundle workflowSmoke --args=migrate --no-daemon
```

Expect `MIGRATION_PASS`. Then open `psql` again (same command as step 4) and run:

```sql
GRANT SELECT ON dxos_wf25_smoke_01.workflow_definitions,
  dxos_wf25_smoke_01.workflow_definition_states, dxos_wf25_smoke_01.workflow_definition_transitions,
  dxos_wf25_smoke_01.workflow_instances, dxos_wf25_smoke_01.workflow_transition_history TO workflow_runtime;
GRANT INSERT ON dxos_wf25_smoke_01.workflow_instances,
  dxos_wf25_smoke_01.workflow_transition_history TO workflow_runtime;
GRANT UPDATE (current_state, lifecycle, runtime_version, updated_at_seconds, updated_at_nanos)
  ON dxos_wf25_smoke_01.workflow_instances TO workflow_runtime;
\q
```

Optional smoke check (writes one test instance; a run id cannot be reused):

```bash
./gradlew workflowSmoke --args="smoke local-first-run" --no-daemon   # SMOKE_PASS
./gradlew workflowSmoke --args="read local-first-run" --no-daemon    # RESTART_READ_PASS
```

## 6. Start a throwaway Keycloak

The backend fetches `OIDC_ISSUER_URI/.well-known/openid-configuration` while starting, so a Keycloak realm named `tricore` must answer on port 8180 first. The repository does not ship a realm export; this creates an empty realm, which is enough for the backend to start.

```bash
read -rs -p 'Keycloak admin password: ' KC_PW; echo
docker run -d --name kc-local -p 127.0.0.1:8180:8080 \
  -e KC_BOOTSTRAP_ADMIN_USERNAME=admin -e KC_BOOTSTRAP_ADMIN_PASSWORD="$KC_PW" \
  quay.io/keycloak/keycloak:26.0 start-dev
```

Wait until `docker logs kc-local | tail -3` shows `Listening on`, then create the realm and check it:

```bash
docker exec kc-local /opt/keycloak/bin/kcadm.sh config credentials \
  --server http://localhost:8080 --realm master --user admin --password "$KC_PW"
docker exec kc-local /opt/keycloak/bin/kcadm.sh create realms -s realm=tricore -s enabled=true
curl -s http://localhost:8180/realms/tricore/.well-known/openid-configuration | head -c 150; echo
```

The JSON must contain `"issuer":"http://localhost:8180/realms/tricore"`.

## 7. Start the backend

```bash
export DB_HOST=127.0.0.1 DB_PORT=55425 DB_NAME=workflow_test DB_USER=workflow_runtime
export DB_PASSWORD="$RUNTIME_DB_PASSWORD"
export DXOS_WORKFLOW_SCHEMA=dxos_wf25_smoke_01
export SPRING_DATASOURCE_URL="jdbc:postgresql://127.0.0.1:55425/workflow_test?currentSchema=dxos_wf25_smoke_01,pg_catalog,pg_temp"
export SPRING_FLYWAY_ENABLED=false
export OIDC_ISSUER_URI=http://localhost:8180/realms/tricore
export OIDC_AUDIENCE=tricore-api
export OIDC_RESOURCE_CLIENT_ID=tricore-api
./gradlew bootRun
```

## 8. Check health

From another terminal:

```bash
curl -fsS http://localhost:8080/api/v1/health
# {"status":"UP"}
```

`UP` means the HTTP application started. It does not prove login, Workflow, or Portal behaviour. Protected routes need a client, a user and a token from a realm whose issuer equals `OIDC_ISSUER_URI` exactly; creating those is not part of this runbook yet.

## 9. Stop and clean up

```bash
# Ctrl+C in the bootRun terminal, then:
unset DB_PASSWORD RUNTIME_DB_PASSWORD KC_PW \
      WORKFLOW_SMOKE_MIGRATOR_PASSWORD WORKFLOW_SMOKE_RUNTIME_PASSWORD
docker rm -f kc-local
# compose needs the variable defined even to stop; any value works here
export WORKFLOW_LOCAL_DB_PASSWORD=unused
docker compose -f ../infra/compose.workflow-postgres.yml down        # stop, keep data
# or, to also delete the data volume (wipes the database):
docker compose -f ../infra/compose.workflow-postgres.yml down -v
unset WORKFLOW_LOCAL_DB_PASSWORD   # do not reuse 'unused' as a real password
```

Use `down` (without `-v`) when you want to restart and verify persistence.

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `Could not resolve placeholder 'OIDC_ISSUER_URI'` (or `OIDC_AUDIENCE`, `dxos.workflow.schema`) | Variable not exported in this shell | Export every variable in step 7 |
| `Unable to resolve the Configuration with the provided Issuer` / `Connection refused` on 8180 | Keycloak is not running or the realm `tricore` does not exist | Do step 6 and re-check the discovery URL |
| `Unable to obtain connection` / `Connection refused` on 55425 | Container not running | `docker compose -f ../infra/compose.workflow-postgres.yml ps`, then `up -d --wait` |
| `password authentication failed` | Volume was created with another password | Reuse the original password, or `down -v` and start again from step 3 |
| `relation ... does not exist` / schema errors at startup | Step 4–5 skipped or different schema name | Check `DXOS_WORKFLOW_SCHEMA` and `currentSchema` match the provisioned schema |
| `Set WORKFLOW_LOCAL_DB_PASSWORD` from compose | Password not exported | Repeat the `read`/`export` in step 3 |
| `Address already in use` on 8080 | Another process holds the port | Stop it, or set `SERVER_PORT=8081` |
| Smoke runner refuses a run id | Run ids are single-use | Use a new id, e.g. `local-run-2` |
| `WORKFLOW_SMOKE_FAIL` with no other message, in step 5 | The runner hides the reason. Likely cause: `RUNTIME_DB_PASSWORD` differs from the password set with `\password` | Reset it: `docker compose -f ../infra/compose.workflow-postgres.yml exec -T workflow-postgres psql -U workflow_test -d workflow_test -v ON_ERROR_STOP=1 -v pw="$RUNTIME_DB_PASSWORD" <<'SQL'` then `ALTER ROLE workflow_runtime PASSWORD :'pw';` then `SQL`, and run the migration again |

## Planned

A one-command `docker compose up` for the full stack (PostgreSQL, Keycloak, backend, BFF, Portal) is tracked separately; this runbook will link to it when it lands.
