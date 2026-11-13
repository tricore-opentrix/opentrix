#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 TRICORE contributors
# SPDX-License-Identifier: Apache-2.0
# Xóa toàn bộ spike, kể cả dữ liệu.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)/infra/demo/spike"
docker compose -f compose.spike.yml down -v
rm -f .env
