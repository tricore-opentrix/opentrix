#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 TRICORE contributors
# SPDX-License-Identifier: Apache-2.0
# Dừng demo (#119). --reset: xóa luôn dữ liệu (DB, CA Caddy); giữ infra/.env.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)/infra"
if [ "${1:-}" = "--reset" ]; then
  docker compose -f compose.demo.yml down -v
  rm -rf demo/.local
else
  docker compose -f compose.demo.yml down
fi
