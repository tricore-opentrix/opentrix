#!/usr/bin/env bash
# Xóa toàn bộ spike, kể cả dữ liệu.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)/infra/demo/spike"
docker compose -f compose.spike.yml down -v
rm -f .env
