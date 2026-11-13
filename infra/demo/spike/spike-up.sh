#!/usr/bin/env bash
# Spike D1 (#119): dựng postgres + keycloak + backend trong một namespace, rồi kiểm tra.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)/infra/demo/spike"
C="docker compose -f compose.spike.yml"

if [ ! -f .env ]; then
  umask 077
  {
    echo "HELPDESK_SETUP_PASSWORD=$(openssl rand -hex 16)"
    echo "HELPDESK_RUNTIME_PASSWORD=$(openssl rand -hex 16)"
    echo "KEYCLOAK_ADMIN_PASSWORD=$(openssl rand -hex 16)"
  } > .env
  echo "Da sinh .env (khong commit)"
fi
set -a; . ./.env; set +a

echo "== 1. postgres + keycloak"
$C up -d postgres keycloak
until [ "$(docker inspect -f '{{.State.Health.Status}}' "$($C ps -q postgres)")" = healthy ]; do sleep 2; done

echo "== 2. tao role, schema, bang, seed"
cd ../../..
{
  echo "BEGIN;"
  echo "CREATE ROLE helpdesk_owner_demo NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS NOINHERIT;"
  echo "CREATE ROLE helpdesk_runtime_demo LOGIN PASSWORD '${HELPDESK_RUNTIME_PASSWORD}' NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS NOINHERIT;"
  echo "REVOKE ALL ON DATABASE helpdesk_disposable_demo FROM PUBLIC;"
  echo "REVOKE ALL ON DATABASE postgres, template1 FROM PUBLIC;"
  echo "GRANT CONNECT ON DATABASE helpdesk_disposable_demo TO helpdesk_runtime_demo;"
  echo "REVOKE ALL ON SCHEMA public FROM PUBLIC;"
  echo "CREATE SCHEMA helpdesk_demo AUTHORIZATION helpdesk_owner_demo;"
  echo "SET LOCAL ROLE helpdesk_owner_demo;"
  echo "ALTER DEFAULT PRIVILEGES IN SCHEMA helpdesk_demo REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;"
  echo "ALTER DEFAULT PRIVILEGES IN SCHEMA helpdesk_demo REVOKE ALL ON TABLES FROM PUBLIC;"
  for f in db/migration/V3__create_workflow_persistence.sql db/helpdesk/policy-schema.sql \
           db/helpdesk/schema.sql db/helpdesk/definition.sql db/helpdesk/runtime-grants.sql; do
    sed -e 's/\${flyway:defaultSchema}/helpdesk_demo/g' -e 's/\${helpdesk:runtimeRole}/helpdesk_runtime_demo/g' \
      "backend/src/main/resources/$f"
    echo
  done
  echo "INSERT INTO helpdesk_demo.tenant_guards VALUES ('demo',0);"
  echo "INSERT INTO helpdesk_demo.workflow_definition_bindings VALUES ('demo','mvp_request','it-helpdesk',1,true);"
  echo "REVOKE ALL ON SCHEMA helpdesk_demo FROM PUBLIC;"
  echo "REVOKE ALL ON ALL TABLES IN SCHEMA helpdesk_demo FROM PUBLIC;"
  echo "REVOKE ALL ON ALL FUNCTIONS IN SCHEMA helpdesk_demo FROM PUBLIC;"
  echo "SET CONSTRAINTS ALL IMMEDIATE;"
  echo "COMMIT;"
} | (cd infra/demo/spike && $C exec -T postgres psql -q -v ON_ERROR_STOP=1 -U helpdesk_setup -d helpdesk_disposable_demo)
cd infra/demo/spike

echo "== 3. tao realm tricore (rong)"
until $C exec -T postgres wget -q -O /dev/null http://127.0.0.1:8180/realms/master; do sleep 3; done
$C exec -T keycloak /opt/keycloak/bin/kcadm.sh config credentials --server http://localhost:8180 \
  --realm master --user admin --password "$KEYCLOAK_ADMIN_PASSWORD" >/dev/null
$C exec -T keycloak /opt/keycloak/bin/kcadm.sh create realms -s realm=tricore -s enabled=true 2>/dev/null || true

echo "== 4. build + chay backend (lan dau mat vai phut)"
$C up -d --build backend
for i in $(seq 1 60); do
  $C exec -T postgres wget -q -O - http://127.0.0.1:8080/api/v1/health 2>/dev/null && break
  sleep 3
done
echo

echo "== 5. kiem tra"
echo "[A] health ben trong namespace:"; $C exec -T postgres wget -q -O - http://127.0.0.1:8080/api/v1/health || echo FAIL; echo
echo "[B] route Helpdesk khong token (mong doi 401):"; $C exec -T postgres wget -S -O /dev/null http://127.0.0.1:8080/api/v1/mvp/requests 2>&1 | grep -m1 'HTTP/' || true
echo "[C] issuer tu may host:"; curl -s http://localhost:8180/realms/tricore/.well-known/openid-configuration | grep -o '"issuer":"[^"]*"' || echo FAIL
echo "[D] backend KHONG mo ra host (mong doi FAIL):"; curl -s -m 3 http://127.0.0.1:8080/api/v1/health && echo "!! backend lo ra host" || echo "OK khong truy cap duoc"
echo "[E] loi loopback trong log (mong doi trong):"; $C logs backend 2>&1 | grep -i "requires loopback" || echo "OK khong co"
