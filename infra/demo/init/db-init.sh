#!/bin/sh
# SPDX-FileCopyrightText: 2026 TRICORE contributors
# SPDX-License-Identifier: Apache-2.0
# Demo (#119, D5): tạo role, schema, bảng Helpdesk và 3 actor demo. Chạy lại an toàn.
set -eu
PSQL="psql -h 127.0.0.1 -U helpdesk_setup -d helpdesk_disposable_demo -v ON_ERROR_STOP=1 -q"
ISS="http://localhost:8180/realms/tricore"
EMP=d2a43dd7-e129-46f9-b09a-eccde2cde032
COO=6afab46d-b455-41e7-a1cb-a2ec6d4841de
WRK=b79f9591-e3bf-4428-a69b-06b523a5564a
MON=da54a88a-83cb-4e2f-9f52-71ef6d94641b

b64u() { printf '%s' "$1" | base64 | tr -d '\n=' | tr '+/' '-_'; }
actor() { echo "oidc:$(b64u "$ISS").$(b64u "$1")"; }
q() { printf '%s' "$1" | sed "s/'/''/g"; }   # escape cho chuỗi SQL

if [ "$($PSQL -tAc "SELECT 1 FROM pg_namespace WHERE nspname='helpdesk_demo'")" != "1" ]; then
  echo "== tao schema helpdesk_demo"
  {
    echo "BEGIN;"
    echo "CREATE ROLE helpdesk_owner_demo NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS NOINHERIT;"
    echo "CREATE ROLE helpdesk_runtime_demo LOGIN PASSWORD '$(q "$HELPDESK_RUNTIME_PASSWORD")' NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS NOINHERIT;"
    echo "REVOKE ALL ON DATABASE helpdesk_disposable_demo FROM PUBLIC;"
    echo "REVOKE ALL ON DATABASE postgres, template1 FROM PUBLIC;"
    echo "GRANT CONNECT ON DATABASE helpdesk_disposable_demo TO helpdesk_runtime_demo;"
    echo "REVOKE ALL ON SCHEMA public FROM PUBLIC;"
    echo "CREATE SCHEMA helpdesk_demo AUTHORIZATION helpdesk_owner_demo;"
    echo "SET LOCAL ROLE helpdesk_owner_demo;"
    echo "ALTER DEFAULT PRIVILEGES IN SCHEMA helpdesk_demo REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;"
    echo "ALTER DEFAULT PRIVILEGES IN SCHEMA helpdesk_demo REVOKE ALL ON TABLES FROM PUBLIC;"
    for f in migration/V3__create_workflow_persistence.sql helpdesk/policy-schema.sql \
             helpdesk/schema.sql helpdesk/definition.sql helpdesk/runtime-grants.sql; do
      sed -e 's/\${flyway:defaultSchema}/helpdesk_demo/g' \
          -e 's/\${helpdesk:runtimeRole}/helpdesk_runtime_demo/g' "/sql/$f"
      echo
    done
    echo "INSERT INTO helpdesk_demo.tenant_guards VALUES ('demo',0);"
    echo "INSERT INTO helpdesk_demo.workflow_definition_bindings VALUES ('demo','mvp_request','it-helpdesk',1,true);"
    echo "REVOKE ALL ON SCHEMA helpdesk_demo FROM PUBLIC;"
    echo "REVOKE ALL ON ALL TABLES IN SCHEMA helpdesk_demo FROM PUBLIC;"
    echo "REVOKE ALL ON ALL FUNCTIONS IN SCHEMA helpdesk_demo FROM PUBLIC;"
    echo "SET CONSTRAINTS ALL IMMEDIATE;"
    echo "COMMIT;"
  } | $PSQL
else
  echo "== schema helpdesk_demo da co, dong bo mat khau runtime"
  $PSQL -c "ALTER ROLE helpdesk_runtime_demo PASSWORD '$(q "$HELPDESK_RUNTIME_PASSWORD")';"
fi

echo "== actor demo (ten hien thi lay tu .env)"
$PSQL <<SQL
BEGIN;
SET LOCAL ROLE helpdesk_owner_demo;
INSERT INTO helpdesk_demo.tenant_memberships VALUES
  ('demo','$(actor $EMP)',true), ('demo','$(actor $COO)',true), ('demo','$(actor $WRK)',true), ('demo','$(actor $MON)',true)
  ON CONFLICT DO NOTHING;
INSERT INTO helpdesk_demo.helpdesk_actors (tenant_id,actor_id,submitter,coordinator,worker,display_name) VALUES
  ('demo','$(actor $EMP)',true,false,false,'$(q "$DEMO_EMPLOYEE_NAME")'),
  ('demo','$(actor $COO)',false,true,false,'$(q "$DEMO_COORDINATOR_NAME")'),
  ('demo','$(actor $WRK)',false,false,true,'$(q "$DEMO_WORKER_NAME")')
  ON CONFLICT (tenant_id,actor_id) DO UPDATE SET display_name = EXCLUDED.display_name;
COMMIT;
SQL
echo "db-init OK"
