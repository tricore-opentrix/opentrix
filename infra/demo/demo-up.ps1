# SPDX-FileCopyrightText: 2026 TRICORE contributors
# SPDX-License-Identifier: Apache-2.0
# Dựng demo integration-local (#119) trên Windows. Cần PowerShell 7 và Docker Desktop.
# -TrustCa: thêm CA cục bộ của Caddy vào kho tin cậy của người dùng hiện tại (Windows sẽ hỏi xác nhận).
#Requires -Version 7.4
[CmdletBinding()]
param([switch]$TrustCa)
$ErrorActionPreference = 'Stop'
Set-Location (Join-Path (git rev-parse --show-toplevel) 'infra')
$compose = @('compose', '-f', 'compose.demo.yml')

if (-not (Test-Path .env)) {
    function New-DemoSecret { [System.Security.Cryptography.RandomNumberGenerator]::GetHexString(32).ToLower() }
    @(
        '# Sinh tự động bởi demo-up (#119). KHÔNG commit. Đổi mật khẩu/tên rồi chạy lại demo-up.'
        "HELPDESK_SETUP_PASSWORD=$(New-DemoSecret)"
        "HELPDESK_RUNTIME_PASSWORD=$(New-DemoSecret)"
        "KEYCLOAK_ADMIN_PASSWORD=$(New-DemoSecret)"
        "PORTAL_OIDC_CLIENT_SECRET=$(New-DemoSecret)"
        "GATEWAY_MONITOR_CLIENT_SECRET=$(New-DemoSecret)"
        "DEMO_EMPLOYEE_PASSWORD=$(New-DemoSecret)"
        "DEMO_COORDINATOR_PASSWORD=$(New-DemoSecret)"
        "DEMO_WORKER_PASSWORD=$(New-DemoSecret)"
        'DEMO_EMPLOYEE_NAME=Nhan vien demo'
        'DEMO_COORDINATOR_NAME=Dieu phoi demo'
        'DEMO_WORKER_NAME=Ky thuat vien demo'
    ) | Set-Content -Path .env -Encoding utf8NoBOM
    Write-Host 'Da sinh infra\.env (khong commit). Mat khau 3 tai khoan demo nam trong file nay.'
}

Write-Host '== build + chay (lan dau mat 5-10 phut)'
docker @compose up -d --build
if ($LASTEXITCODE -ne 0) { throw 'docker compose up that bai' }

Write-Host '== cho Portal https://localhost:8443'
New-Item -ItemType Directory -Force demo/.local | Out-Null
$ca = 'demo/.local/caddy-root.crt'
$ready = $false
for ($i = 1; $i -le 100 -and -not $ready; $i++) {
    docker @compose cp ingress:/data/caddy/pki/authorities/local/root.crt $ca 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) {
        $ready = ((curl.exe -s -o NUL -w '%{http_code}' --cacert $ca https://localhost:8443/bff/session) -eq '200')
    }
    if (-not $ready) { Start-Sleep 3 }
}
if (-not $ready) { throw 'Portal chua len. Xem: docker compose -f infra/compose.demo.yml logs' }

function Code($url) { curl.exe -s -o NUL -w '%{http_code}' --cacert $ca $url }
$fail = $false
function Check($name, $got, $want) {
    if ($got -eq $want) { Write-Host "OK   $name ($got)" }
    else { Write-Host "FAIL $name (nhan $got, mong doi $want)" -ForegroundColor Red; $script:fail = $true }
}
Check 'Portal trang chu' (Code 'https://localhost:8443/') '200'
Check 'BFF /bff/session' (Code 'https://localhost:8443/bff/session') '200'
Check '/api/* bi chan o ingress' (Code 'https://localhost:8443/api/v1/health') '404'
$iss = (Invoke-RestMethod http://localhost:8180/realms/tricore/.well-known/openid-configuration).issuer
Check 'issuer Keycloak' $iss 'http://localhost:8180/realms/tricore'
Check 'backend khong mo ra may' (curl.exe -s -m 3 -o NUL -w '%{http_code}' http://127.0.0.1:8080/api/v1/health) '000'

if ($TrustCa) {
    Import-Certificate -FilePath $ca -CertStoreLocation Cert:\CurrentUser\Root | Out-Null
    Write-Host 'Da them CA Caddy vao Cert:\CurrentUser\Root (dong va mo lai trinh duyet).'
}
if ($fail) { Write-Host 'Co kiem tra FAIL. Xem: docker compose -f infra/compose.demo.yml logs backend portal-bff'; exit 1 }
Write-Host ''
Write-Host 'Mo https://localhost:8443 va dang nhap employee-demo / coordinator-demo / worker-demo (moi vai mot browser profile).'
