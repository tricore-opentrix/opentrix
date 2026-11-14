#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 TRICORE contributors
# SPDX-License-Identifier: Apache-2.0
# Dựng demo integration-local (#119) trên Linux/macOS. Bản Windows: demo-up.ps1.
# --gateway: bật APISIX (infra/compose.gateway.yml, #116); Portal gọi backend qua 127.0.0.1:9080.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)/infra"
C="docker compose -f compose.demo.yml"
GW=0; [ "${1:-}" = "--gateway" ] && { GW=1; C="$C -f compose.gateway.yml"; }

if [ ! -f .env ]; then
  umask 077
  r() { openssl rand -hex 16; }
  cat > .env <<ENV
# Sinh tự động bởi demo-up (#119). KHÔNG commit. Đổi mật khẩu/tên rồi chạy lại demo-up.
HELPDESK_SETUP_PASSWORD=$(r)
HELPDESK_RUNTIME_PASSWORD=$(r)
KEYCLOAK_ADMIN_PASSWORD=$(r)
PORTAL_OIDC_CLIENT_SECRET=$(r)
GATEWAY_MONITOR_CLIENT_SECRET=$(r)
DEMO_EMPLOYEE_PASSWORD=$(r)
DEMO_COORDINATOR_PASSWORD=$(r)
DEMO_WORKER_PASSWORD=$(r)
DEMO_EMPLOYEE_NAME=Nhan vien demo
DEMO_COORDINATOR_NAME=Dieu phoi demo
DEMO_WORKER_NAME=Ky thuat vien demo
ENV
  echo "Da sinh infra/.env (khong commit). Mat khau 3 tai khoan demo nam trong file nay."
fi

echo "== build + chay (lan dau mat 5-10 phut)"
$C up -d --build

echo "== cho Portal https://localhost:8443"
mkdir -p demo/.local
for i in $(seq 1 100); do
  if $C cp ingress:/data/caddy/pki/authorities/local/root.crt demo/.local/caddy-root.crt >/dev/null 2>&1 \
     && [ "$(curl -s -o /dev/null -w '%{http_code}' --cacert demo/.local/caddy-root.crt https://localhost:8443/bff/session)" = 200 ]; then
    break
  fi
  [ "$i" = 100 ] && { echo "FAIL: Portal chua len. Xem: $C logs" >&2; exit 1; }
  sleep 3
done

code() { curl -s -o /dev/null -w '%{http_code}' --cacert demo/.local/caddy-root.crt "$1"; }
fail=0
check() { if [ "$2" = "$3" ]; then echo "OK   $1 ($2)"; else echo "FAIL $1 (nhan $2, mong doi $3)"; fail=1; fi; }
check "Portal trang chu" "$(code https://localhost:8443/)" 200
check "BFF /bff/session" "$(code https://localhost:8443/bff/session)" 200
check "/api/* bi chan o ingress" "$(code https://localhost:8443/api/v1/health)" 404
check "issuer Keycloak" "$(curl -s http://localhost:8180/realms/tricore/.well-known/openid-configuration | grep -o '"issuer":"[^"]*"')" '"issuer":"http://localhost:8180/realms/tricore"'
check "backend khong mo ra may" "$(curl -s -m 3 -o /dev/null -w '%{http_code}' http://127.0.0.1:8080/api/v1/health || true)" 000
if [ "$GW" = 1 ]; then
  gw=000
  for i in $(seq 1 20); do
    gw="$(curl -s -m 5 -o /dev/null -w '%{http_code}' http://127.0.0.1:9080/api/v1/health || true)"
    [ "$gw" = 200 ] && break; sleep 3
  done
  check "APISIX /api/v1/health" "$gw" 200
fi
[ "$fail" = 0 ] || { echo "Co kiem tra FAIL. Xem: $C logs backend portal-bff" >&2; exit 1; }

echo
echo "Mo https://localhost:8443 va dang nhap employee-demo / coordinator-demo / worker-demo (moi vai mot browser profile)."
echo "Trinh duyet can tin CA cua Caddy: infra/demo/.local/caddy-root.crt (xem infra/demo/README.md)."
