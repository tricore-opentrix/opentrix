#!/bin/bash
# SPDX-FileCopyrightText: 2026 TRICORE contributors
# SPDX-License-Identifier: Apache-2.0
# Demo (#119, D2–D4): đặt secret client và mật khẩu 3 tài khoản demo từ .env. Chạy lại an toàn.
set -euo pipefail
KC=/opt/keycloak/bin/kcadm.sh
CFG=/tmp/kcadm.config

echo "== cho Keycloak + realm tricore"
for ((i = 1; i <= 90; i++)); do
  if $KC config credentials --config $CFG --server http://localhost:8180 --realm master \
       --user admin --password "$KEYCLOAK_ADMIN_PASSWORD" >/dev/null 2>&1 \
     && $KC get realms/tricore --config $CFG --fields realm >/dev/null 2>&1; then
    break
  fi
  (( i == 90 )) && { echo "Keycloak chua san sang sau 270s" >&2; exit 1; }
  sleep 3
done

set_secret() {
  local id
  id=$($KC get clients -r tricore --config $CFG -q clientId="$1" --fields id --format csv --noquotes)
  $KC update "clients/$id" -r tricore --config $CFG -s "secret=$2"
  echo "secret $1: da dat"
}
set_secret dxos-portal-bff-local "$PORTAL_OIDC_CLIENT_SECRET"
set_secret gateway-monitor "$GATEWAY_MONITOR_CLIENT_SECRET"

$KC set-password -r tricore --config $CFG --username employee-demo --new-password "$DEMO_EMPLOYEE_PASSWORD"
$KC set-password -r tricore --config $CFG --username coordinator-demo --new-password "$DEMO_COORDINATOR_PASSWORD"
$KC set-password -r tricore --config $CFG --username worker-demo --new-password "$DEMO_WORKER_PASSWORD"
echo "mat khau 3 tai khoan demo: da dat"
rm -f $CFG
echo "kc-init OK"
