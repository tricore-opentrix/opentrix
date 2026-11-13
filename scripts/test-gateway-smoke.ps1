#Requires -Version 7.2
# SPDX-FileCopyrightText: 2026 TRICORE contributors
# SPDX-License-Identifier: Apache-2.0
param([string]$Scenario, [string]$OutputDirectory)
$ErrorActionPreference = 'Stop'
$smoke = Join-Path $PSScriptRoot 'gateway-smoke.ps1'
function Assert([bool]$Condition, [string]$Message) { if (-not $Condition) { throw $Message } }
$cases = @{
    'gateway-origin'=@(2,'PASS','PASS'); 'upstream-401'=@(1,'FAIL','PASS')
    'wrong-nonce'=@(2,'BLOCKED','PASS'); 'wrong-path'=@(2,'BLOCKED','PASS')
    'log-status-mismatch'=@(1,'FAIL','PASS'); 'duplicate-log'=@(1,'FAIL','PASS')
    'log-error'=@(2,'BLOCKED','PASS'); 'no-container'=@(2,'BLOCKED','PASS')
    'delayed-log'=@(2,'PASS','PASS'); 'http-not-401'=@(1,'FAIL','PASS')
    'tcp-refused'=@(2,'PASS','PASS'); 'tcp-reachable'=@(1,'PASS','FAIL')
    'tcp-timeout'=@(2,'PASS','BLOCKED'); 'tcp-other-error'=@(2,'PASS','BLOCKED')
}
if (-not $OutputDirectory) {
    $OutputDirectory = Join-Path ([IO.Path]::GetTempPath()) ('opentrix-gateway-smoke-' + [guid]::NewGuid().ToString('N'))
}
if (-not $Scenario) {
    New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
    $config = Get-Content (Join-Path $PSScriptRoot '../infra/apisix/config.yaml') -Raw
    Assert ($config.Contains('smoke_id=$http_x_opentrix_smoke_id')) 'Missing nonce in access log format'
    Assert (-not $config.Contains('$http_authorization')) 'Authorization must not be logged'
    foreach ($name in $cases.Keys | Sort-Object) {
        & (Get-Process -Id $PID).Path -NoProfile -File $PSCommandPath -Scenario $name -OutputDirectory $OutputDirectory
        Assert ($LASTEXITCODE -eq 0) "Scenario failed: $name"
    }
    Write-Output "PASS $($cases.Count) smoke scenarios; evidence=$OutputDirectory"
    exit 0
}
Assert ($cases.ContainsKey($Scenario)) 'Unknown test scenario'
# Each fixture runs in a fresh process; no real HTTP, Docker or TCP connection is used.
class SmokeTestTcpClient {
    static [string]$Mode
    static [bool]$Disposed = $false
    [System.Threading.Tasks.Task] ConnectAsync([string]$Address, [int]$Port) {
        if ([SmokeTestTcpClient]::Mode -eq 'tcp-reachable') { return [System.Threading.Tasks.Task]::CompletedTask }
        if ([SmokeTestTcpClient]::Mode -eq 'tcp-timeout') { return [System.Threading.Tasks.TaskCompletionSource[bool]]::new().Task }
        $code = [System.Net.Sockets.SocketError]::ConnectionRefused
        if ([SmokeTestTcpClient]::Mode -eq 'tcp-other-error') { $code = [System.Net.Sockets.SocketError]::HostUnreachable }
        return [System.Threading.Tasks.Task]::FromException([System.Net.Sockets.SocketException]::new([int]$code))
    }
    [void] Dispose() { [SmokeTestTcpClient]::Disposed = $true }
}
[SmokeTestTcpClient]::Mode = $Scenario
$accelerators = [psobject].Assembly.GetType('System.Management.Automation.TypeAccelerators')
$accelerators::Add('Net.Sockets.TcpClient', [SmokeTestTcpClient])
$env:GATEWAY_MONITOR_CLIENT_SECRET = 'synthetic-test-value'
$global:smokeScenario = $Scenario
$global:smokeHealthCalls = 0
$global:smokeLogReads = 0
$global:smokeNonce = ''
function global:Start-Sleep { param($Seconds) }
function global:Invoke-RestMethod {
    param($Uri, $Method, $TimeoutSec, $Body)
    $claims = @{iss='http://localhost:8180/realms/tricore'; aud='tricore-api';
        sub='da54a88a-83cb-4e2f-9f52-71ef6d94641b'; resource_access=@{'tricore-api'=@{roles=@('workflow:read')}}}
    $encoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes(($claims | ConvertTo-Json -Depth 5 -Compress))).TrimEnd('=').Replace('+','-').Replace('/','_')
    return @{access_token="fixture.$encoded.signature"}
}
function global:Invoke-WebRequest {
    param($Uri, $Headers, [switch]$SkipHttpErrorCheck, $TimeoutSec)
    $path = ([uri]$Uri).AbsolutePath
    $r = [pscustomobject]@{StatusCode=200; Content='{"items":[]}'; Headers=@{'X-Request-Id'='fixture'}}
    if ($path -eq '/api/v1/health') {
        $global:smokeHealthCalls++
        if ($global:smokeHealthCalls -gt 60) { $r.StatusCode=429 }
    } elseif ($path -eq '/api/v1/workflow-instances') {
        $r.StatusCode=404
    } elseif (-not $Headers.Authorization) {
        $global:smokeNonce = $Headers['X-Opentrix-Smoke-Id']
        Assert ($global:smokeNonce -cmatch '^[0-9a-f]{32}$') 'Expected a fresh GUID nonce'
        $r.StatusCode = if ($global:smokeScenario -eq 'http-not-401') {200} else {401}
    }
    return $r
}
function global:docker {
    param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Arguments)
    Assert ($Arguments[0] -eq 'logs' -and $Arguments -contains '--since' -and $Arguments -contains '--tail') 'Expected bounded Docker log read'
    $global:smokeLogReads++
    $global:LASTEXITCODE = 0
    if ($global:smokeScenario -eq 'log-error') { $global:LASTEXITCODE=1; return 'fixture Docker error' }
    $nonce=$global:smokeNonce
    $unrelated='127.0.0.1 GET /api/v1/mvp/requests 401 upstream=- smoke_id=unrelated'
    if ($global:smokeScenario -eq 'wrong-nonce' -or ($global:smokeScenario -eq 'delayed-log' -and $global:smokeLogReads -lt 3)) { return $unrelated }
    $path = if ($global:smokeScenario -eq 'wrong-path') {'/api/v1/health'} else {'/api/v1/mvp/requests'}
    $status = if ($global:smokeScenario -eq 'log-status-mismatch') {'200'} else {'401'}
    $upstream = if ($global:smokeScenario -eq 'upstream-401') {'401'} else {'-'}
    $line="127.0.0.1 GET $path $status upstream=$upstream smoke_id=$nonce"
    if ($global:smokeScenario -eq 'duplicate-log') { return @($line,$line) }
    return @($unrelated,$line)
}
$output = Join-Path $OutputDirectory ($Scenario + '.json')
$timer = [Diagnostics.Stopwatch]::StartNew()
try {
    $arguments = @{OutputFile=$output}
    if ($Scenario -ne 'no-container') { $arguments.ApisixContainer='fixture-apisix' }
    & $smoke @arguments
    $code = $LASTEXITCODE
} finally { $null = $accelerators::Remove('Net.Sockets.TcpClient') }
$timer.Stop()
$results = (Get-Content -LiteralPath $output -Raw | ConvertFrom-Json).results
$expected = $cases[$Scenario]
Assert ($code -eq $expected[0]) "Wrong exit code: $Scenario = $code"
Assert (($results | Where-Object id -eq 2).status -eq $expected[1]) "Wrong gateway-origin result: $Scenario"
Assert (($results | Where-Object id -eq 7).status -eq $expected[2]) "Wrong TCP result: $Scenario"
Assert (($results | Where-Object id -eq 6).status -eq 'BLOCKED') 'Golden Path must stay BLOCKED'
Assert ([SmokeTestTcpClient]::Disposed) 'TCP client must be disposed'
if ($Scenario -eq 'tcp-timeout') { Assert ($timer.Elapsed.TotalSeconds -ge 2.5) 'Timeout did not wait for the configured deadline' }
if ($Scenario -eq 'delayed-log') { Assert ($global:smokeLogReads -eq 3) 'Expected buffered log polling' }
Write-Output "PASS $Scenario (smoke exit=$code)"
