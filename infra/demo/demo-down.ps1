# SPDX-FileCopyrightText: 2026 TRICORE contributors
# SPDX-License-Identifier: Apache-2.0
# Dừng demo (#119). -Reset: xóa luôn dữ liệu (DB, CA Caddy); giữ infra\.env.
#Requires -Version 7.4
[CmdletBinding()]
param([switch]$Reset)
$ErrorActionPreference = 'Stop'
Set-Location (Join-Path (git rev-parse --show-toplevel) 'infra')
if ($Reset) {
    docker compose -f compose.demo.yml -f compose.gateway.yml down -v
    Remove-Item -Recurse -Force demo/.local -ErrorAction SilentlyContinue
} else {
    docker compose -f compose.demo.yml -f compose.gateway.yml down
}
