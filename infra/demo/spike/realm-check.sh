#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 TRICORE contributors
# SPDX-License-Identifier: Apache-2.0
# Kiểm tra realm file (#119): nạp infra/keycloak/tricore-realm.json vào spike đang chạy,
# lấy token gateway-monitor, kiểm tra claim, seed actor monitor, gọi API phải được 200.
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT/infra/demo/spike"
C="docker compose -f compose.spike.yml"
set -a; . ./.env; set +a
ISS=http://localhost:8180/realms/tricore
KC=/opt/keycloak/bin/kcadm.sh
MON_SUB=da54a88a-83cb-4e2f-9f52-71ef6d94641b

echo "== 1. nap realm tu file"
$C cp "$ROOT/infra/keycloak/tricore-realm.json" keycloak:/tmp/tricore-realm.json
$C exec -T keycloak $KC config credentials --server http://localhost:8180 --realm master --user admin --password "$KEYCLOAK_ADMIN_PASSWORD" >/dev/null
$C exec -T keycloak $KC delete realms/tricore >/dev/null 2>&1 || true
$C exec -T keycloak $KC create realms -f /tmp/tricore-realm.json

echo "== 2. dat secret gateway-monitor (chi trong .env)"
if ! grep -q '^GATEWAY_MONITOR_CLIENT_SECRET=' .env; then
  echo "GATEWAY_MONITOR_CLIENT_SECRET=$(openssl rand -hex 24)" >> .env
fi
set -a; . ./.env; set +a
CID=$($C exec -T keycloak $KC get clients -r tricore -q clientId=gateway-monitor --fields id --format csv --noquotes | tr -d '\r')
$C exec -T keycloak $KC update "clients/$CID" -r tricore -s "secret=$GATEWAY_MONITOR_CLIENT_SECRET"

echo "== 3. lay token client credentials"
TOKEN=$(curl -s -X POST "$ISS/protocol/openid-connect/token" \
  -d grant_type=client_credentials -d client_id=gateway-monitor -d "client_secret=$GATEWAY_MONITOR_CLIENT_SECRET" \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')
python3 - "$TOKEN" <<'PY'
import sys,json,base64
p=sys.argv[1].split(".")[1]; c=json.loads(base64.urlsafe_b64decode(p+"="*(-len(p)%4)))
aud=c.get("aud"); aud=aud if isinstance(aud,list) else [aud]
roles=c.get("resource_access",{}).get("tricore-api",{}).get("roles",[])
ok=lambda b:"OK " if b else "FAIL"
print(ok(c.get("iss")=="http://localhost:8180/realms/tricore"),"iss =",c.get("iss"))
print(ok(c.get("sub")=="da54a88a-83cb-4e2f-9f52-71ef6d94641b"),"sub =",c.get("sub"))
print(ok("tricore-api" in aud),"aud =",aud)
print(ok(sorted(roles)==["workflow:read"]),"resource_access.tricore-api.roles =",roles)
sys.exit(0 if c.get("iss")=="http://localhost:8180/realms/tricore" and c.get("sub")=="da54a88a-83cb-4e2f-9f52-71ef6d94641b" and "tricore-api" in aud and sorted(roles)==["workflow:read"] else 1)
PY

echo "== 4. seed actor monitor (thanh vien tenant demo, khong co quyen nghiep vu)"
b64u() { printf '%s' "$1" | base64 -w0 | tr '+/' '-_' | tr -d '='; }
ACTOR="oidc:$(b64u "$ISS").$(b64u "$MON_SUB")"
$C exec -T postgres psql -q -v ON_ERROR_STOP=1 -U helpdesk_setup -d helpdesk_disposable_demo <<SQL
BEGIN;
SET LOCAL ROLE helpdesk_owner_demo;
INSERT INTO helpdesk_demo.tenant_memberships VALUES ('demo','$ACTOR',true) ON CONFLICT DO NOTHING;
INSERT INTO helpdesk_demo.helpdesk_actors (tenant_id,actor_id,submitter,coordinator,worker,display_name)
  VALUES ('demo','$ACTOR',false,false,false,'Gateway monitor') ON CONFLICT DO NOTHING;
COMMIT;
SQL

echo "== 5. goi API voi token (mong doi 200)"
$C exec -T -e TOKEN="$TOKEN" postgres sh -c 'wget -S -O - --header "Authorization: Bearer $TOKEN" http://127.0.0.1:8080/api/v1/mvp/requests 2>&1 | grep -E "HTTP/|^\[|^\{" | head -3' | tee /dev/stderr | grep 'HTTP/1.1 200' >/dev/null || { echo 'FAIL: mong doi 200' >&2; exit 1; }
echo "== 6. ghi (POST) voi token monitor (mong doi 403)"
$C exec -T -e TOKEN="$TOKEN" postgres sh -c 'wget -S -O /dev/null --header "Authorization: Bearer $TOKEN" --header "Content-Type: application/json" --post-data "{\"title\":\"x\",\"description\":\"y\",\"requestType\":\"IT_HELPDESK\"}" http://127.0.0.1:8080/api/v1/mvp/requests 2>&1 | grep -m1 "HTTP/"' | tee /dev/stderr | grep 'HTTP/1.1 403' >/dev/null || { echo 'FAIL: mong doi 403' >&2; exit 1; }
