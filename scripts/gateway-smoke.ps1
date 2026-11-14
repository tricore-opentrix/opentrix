#Requires -Version 7.2
# SPDX-FileCopyrightText: 2026 TRICORE contributors
# SPDX-License-Identifier: Apache-2.0
<#
.EXAMPLE
pwsh -File scripts/gateway-smoke.ps1 -ApisixContainer opentrix-p116-final-apisix
.NOTES
Requires PowerShell 7.2 (.NET 6) and Docker log access for gateway-origin proof.
Missing correlated log evidence is BLOCKED; upstream authentication is not gateway proof.
#>
param(
    [string]$GatewayUrl = 'http://127.0.0.1:9080',
    [string]$EnvFile = (Join-Path $PSScriptRoot '../.env'),
    [string]$OutputFile,
    [ValidatePattern('^[A-Za-z0-9][A-Za-z0-9_.-]*$')]
    [string]$ApisixContainer
)
$ErrorActionPreference = 'Stop'
$results = [Collections.Generic.List[object]]::new()
function Record($Id, $Check, $Status, $Evidence) {
    $results.Add([pscustomobject]@{ id=$Id; check=$Check; status=$Status; evidence=$Evidence })
    Write-Host "$Id $Check : $Status ($Evidence)"
}
function Get-Response($Path, $Headers = @{}) {
    Invoke-WebRequest "$($GatewayUrl.TrimEnd('/'))$Path" -Headers $Headers -SkipHttpErrorCheck -TimeoutSec 5
}
# Credentials are sent only to the agreed local issuer; never print token responses.
$uri = [uri]$GatewayUrl
if ($uri.Scheme -ne 'http' -or $uri.Host -notin @('127.0.0.1','localhost') -or $uri.Port -ne 9080 -or
    $uri.AbsolutePath -ne '/' -or $uri.Query -or $uri.UserInfo -or $uri.Fragment) {
    throw 'GatewayUrl must be http://127.0.0.1:9080 or http://localhost:9080.'
}
$secret = $env:GATEWAY_MONITOR_CLIENT_SECRET
if (-not $secret -and (Test-Path -LiteralPath $EnvFile)) {
    foreach ($line in Get-Content -LiteralPath $EnvFile) {
        if ($line -match '^GATEWAY_MONITOR_CLIENT_SECRET=(.+)$') { $secret = $Matches[1].Trim().Trim('"').Trim("'") }
    }
}
try {
    $r = Get-Response '/api/v1/health'
    Record 1 health $(if ($r.StatusCode -eq 200) {'PASS'} else {'FAIL'}) "HTTP $($r.StatusCode)"
} catch { Record 1 health BLOCKED 'Gateway unreachable' }
try {
    $probeId = [guid]::NewGuid().ToString('N')
    $probeStarted = [DateTime]::UtcNow.ToString('o')
    $r = Get-Response '/api/v1/mvp/requests' @{'X-Opentrix-Smoke-Id'=$probeId}
    if ($r.StatusCode -ne 401) {
        Record 2 no-token FAIL "HTTP $($r.StatusCode)"
    } elseif (-not $ApisixContainer) {
        Record 2 no-token BLOCKED 'HTTP 401; ApisixContainer required for gateway-origin proof'
    } else {
        $accessEntries = @()
        $logExit = 0
        $pattern = "^\S+ GET /api/v1/mvp/requests (?<status>\d{3}) upstream=(?<upstream>.*?) smoke_id=$probeId$"
        # Nginx buffers access logs; poll for this nonce without printing raw Docker logs.
        for ($attempt=0; $attempt -lt 6; $attempt++) {
            $logLines = @(& docker logs --since $probeStarted --tail 1000 $ApisixContainer 2>&1)
            $logExit = $LASTEXITCODE
            if ($logExit -ne 0) { break }
            $accessEntries = @(foreach ($line in $logLines) {
                if ([string]$line -cmatch $pattern) {
                    [pscustomobject]@{ status=$Matches.status; upstream=$Matches.upstream }
                }
            })
            if ($accessEntries.Count -gt 0) { break }
            if ($attempt -lt 5) { Start-Sleep -Seconds 1 }
        }
        if ($logExit -ne 0 -or $accessEntries.Count -eq 0) {
            Record 2 no-token BLOCKED "HTTP 401; correlated access log unavailable; probe=$probeId"
        } elseif ($accessEntries.Count -ne 1) {
            Record 2 no-token FAIL "Ambiguous correlated access records; probe=$probeId"
        } elseif ($accessEntries[0].status -ne '401' -or $accessEntries[0].upstream -ne '-') {
            Record 2 no-token FAIL "Correlated log does not prove gateway rejection; probe=$probeId"
        } else {
            Record 2 no-token PASS "HTTP 401; upstream=-; probe=$probeId"
        }
    }
} catch { Record 2 no-token BLOCKED 'Gateway request or correlated access log unavailable' }
$headers = @{}
if (-not $secret) {
    Record 3 gateway-monitor BLOCKED 'GATEWAY_MONITOR_CLIENT_SECRET missing'
} else {
    try {
        $token = Invoke-RestMethod 'http://localhost:8180/realms/tricore/protocol/openid-connect/token' -Method Post -TimeoutSec 10 -Body @{
            grant_type='client_credentials'; client_id='gateway-monitor'; client_secret=$secret
        }
        $encoded = $token.access_token.Split('.')[1].Replace('-','+').Replace('_','/')
        $encoded = $encoded.PadRight($encoded.Length + (4 - $encoded.Length % 4) % 4, '=')
        $claims = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($encoded)) | ConvertFrom-Json
        $roles = @($claims.resource_access.'tricore-api'.roles)
        if ($claims.iss -cne 'http://localhost:8180/realms/tricore' -or
            'tricore-api' -cnotin @($claims.aud) -or $roles.Count -ne 1 -or $roles[0] -cne 'workflow:read' -or
            $claims.sub -cne 'da54a88a-83cb-4e2f-9f52-71ef6d94641b') {
            Record 3 gateway-monitor FAIL 'Unexpected monitor issuer/audience/subject/roles'
        } else {
            $headers = @{Authorization="Bearer $($token.access_token)"}
            $r = Get-Response '/api/v1/mvp/requests' $headers
            $page = if ($r.StatusCode -eq 200) { $r.Content | ConvertFrom-Json } else { $null }
            $ok = $r.StatusCode -eq 200 -and $page.PSObject.Properties.Name -contains 'items' -and
                $page.items -is [array] -and $r.Headers.ContainsKey('X-Request-Id')
            Record 3 gateway-monitor $(if ($ok) {'PASS'} else {'FAIL'}) "HTTP $($r.StatusCode); expected list and request ID"
        }
    } catch { Record 3 gateway-monitor BLOCKED 'Token endpoint or authenticated request failed; credentials omitted' }
}
try {
    $r = Get-Response '/api/v1/workflow-instances' $headers
    Record 4 hidden-workflow $(if ($r.StatusCode -eq 404) {'PASS'} else {'FAIL'}) "HTTP $($r.StatusCode)"
} catch { Record 4 hidden-workflow BLOCKED 'Gateway unreachable' }
try {
    $limited = $false
    for ($i=0; $i -lt 70; $i++) {
        $r = Get-Response '/api/v1/health'
        if ($r.StatusCode -eq 429) { $limited = $true; break }
        if ($r.StatusCode -ne 200) { break }
    }
    Record 5 rate-limit $(if ($limited) {'PASS'} else {'FAIL'}) "Last HTTP $($r.StatusCode) after $($i+1) requests"
} catch { Record 5 rate-limit BLOCKED 'Gateway unreachable' }
# shortcut: #119 has no Portal browser harness yet; add the six-step check when it is available.
Record 6 portal-golden-path BLOCKED '#119 Portal/BFF browser verification required; service-account checks cannot prove this'
$tcp = [Net.Sockets.TcpClient]::new()
try {
    $null = $tcp.ConnectAsync('127.0.0.1',8080).WaitAsync([TimeSpan]::FromSeconds(3)).GetAwaiter().GetResult()
    Record 7 backend-private FAIL 'Host TCP 127.0.0.1:8080 reachable'
} catch [Net.Sockets.SocketException] {
    if ($_.Exception.SocketErrorCode -eq [Net.Sockets.SocketError]::ConnectionRefused) {
        Record 7 backend-private PASS 'Host TCP 127.0.0.1:8080 refused'
    } else {
        Record 7 backend-private BLOCKED 'TCP probe inconclusive'
    }
} catch {
    Record 7 backend-private BLOCKED 'TCP probe inconclusive'
} finally { $tcp.Dispose() }
if ($OutputFile) {
    $root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
    $sha = & git -c "safe.directory=$($root.Replace('\','/'))" -C $root rev-parse HEAD
    @{ head=$sha; testedAt=[DateTime]::UtcNow.ToString('o'); results=@($results.ToArray()) } |
        ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $OutputFile -Encoding utf8
}
if ($results.status -contains 'FAIL') { exit 1 }
if ($results.status -contains 'BLOCKED') { exit 2 }
exit 0
