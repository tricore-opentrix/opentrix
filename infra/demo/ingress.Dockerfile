# SPDX-FileCopyrightText: 2026 TRICORE contributors
# SPDX-License-Identifier: Apache-2.0
# Demo (#119): build Portal integration-local từ mã nguồn, phục vụ qua Caddy HTTPS.
FROM node:22.20.0-alpine AS build
WORKDIR /src
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --ignore-scripts --no-audit --no-fund
COPY frontend/ ./
RUN npm run build:integration-local

FROM caddy:2.10.2-alpine
COPY infra/demo/Caddyfile /etc/caddy/Caddyfile
COPY --from=build /src/dist /srv/portal
