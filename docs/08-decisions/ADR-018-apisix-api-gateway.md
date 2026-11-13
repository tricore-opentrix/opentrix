<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# ADR-018 - Apache APISIX as the API gateway

**Status:** ACCEPTED — effective on merge with approvals from @lexuanbao258-collab and @ngang02012007-crypto, per `GOVERNANCE.md`

**Decision date:** 2026-11-13

**Author:** @phanyen06ym-ien · **Reviewers:** @lexuanbao258-collab, @ngang02012007-crypto

**Tracking:** [#116](https://github.com/tricore-opentrix/opentrix/issues/116) · Phase 4 [#216](https://github.com/tricore-opentrix/opentrix/issues/216) · related [#119](https://github.com/tricore-opentrix/opentrix/issues/119), [#115](https://github.com/tricore-opentrix/opentrix/issues/115)

**AS-IS baseline:** `main@323b09b337e85474502f9021348708b5e91b0b0f`

## Tóm tắt

**Apache APISIX** (Apache-2.0) chạy ở **chế độ standalone**, đặt trước backend, là cổng API duy nhất để vào backend. Route khai báo trong file `apisix.yaml` nằm trong repo; không dùng etcd, Admin API hay Dashboard. Gateway kiểm tra bearer token của Keycloak, giới hạn tần suất và gắn request id; **backend vẫn tự kiểm tra JWT**. Chỉ mở route cho health và 9 API Helpdesk. Có mặt từ **vòng thi cấp trường 19/11/2026**.

## Context

The OLP 2026 brief makes an **API Gateway** one of the four mandatory Core services (with Identity/SSO, structured/unstructured data and Workflow) and lists Apache APISIX in its reference stack for the network edge, together with a Zero-Trust principle.

AS-IS on `main`:

- There is no API gateway. Clients reach the backend directly; the Portal reaches it through the Portal BFF (`PORTAL_BACKEND_BASE_URL`), served behind a local Caddy HTTPS ingress (`portal-bff/Caddyfile.local`).
- The backend is a Spring Boot resource server: every route except `GET /api/v1/health` requires a Keycloak JWT (realm `tricore`, audience `tricore-api`).
- Public routes: `GET /api/v1/health` and the nine Helpdesk operations under `/api/v1/mvp/requests`. The generic `/api/v1/workflow-instances` controller exists in source but is not registered (#115).
- Gateway work was tracked in #116; earlier designs (`docs/02-core/gateway/`) are historical.
- Naming: the backend package `com.tricore.dxos.gateway` holds the HTTP controllers and technical-authority checks (`WorkflowGatewayPrincipalGate`). It is part of the backend, not the API gateway. In this ADR "API gateway" always means APISIX.

## Decision

1. **Apache APISIX 3.x in standalone mode.** One `apache/apisix` container with a pinned exact 3.x version (3.13.0 or a later stable release, recorded at implementation). Routes, upstreams and plugins are declared in `infra/apisix/apisix.yaml`, versioned in Git and reviewed like code. No etcd, no Admin API, no APISIX Dashboard.
2. **Single entry to the backend.** In the Compose stack the backend has no published port; only APISIX reaches it on the internal network. The Portal BFF calls APISIX (`PORTAL_BACKEND_BASE_URL` points to the gateway); the BFF code does not change. External API clients also call APISIX.
3. **Routes:**

   | Route                                            | Upstream | Plugins                                                                                                |
   | ------------------------------------------------ | -------- | ------------------------------------------------------------------------------------------------------ |
   | `GET /api/v1/health`                             | backend  | `limit-count`                                                                                          |
   | `/api/v1/mvp/requests`, `/api/v1/mvp/requests/*` | backend  | `openid-connect` (bearer-only, Keycloak realm `tricore` discovery and JWKS), `limit-req`, `request-id` |
   | anything else                                    | —        | not declared; APISIX returns 404                                                                       |

   `/api/v1/workflow-instances` gets no route while #115 is open.

4. **Defense in depth.** The gateway rejects missing or invalid tokens before they reach the backend, but the backend keeps its own JWT validation, audience check and resource ACL. Authorization decisions are never moved to the gateway.
5. **Secrets.** Issuer URL, client identifiers and any secret come from environment variables or Compose secrets; none are committed. Rate-limit values are configuration, not code.

## Verification

Accepted implementation (#116, Compose under #119) must show on a pinned SHA:

1. `GET /api/v1/health` through APISIX returns 200.
2. `GET /api/v1/mvp/requests` without a token returns 401 at the gateway and does not reach the backend.
3. The same call with a valid Keycloak token returns 200 with the expected list.
4. `/api/v1/workflow-instances` through APISIX returns 404.
5. Requests above the configured rate return 429.
6. The six-step Helpdesk Golden Path works in the Portal (integration-local) through APISIX.
7. The backend port is not reachable from the host.

## Consequences

- **Benefits:** the mandatory gateway service exists and is demonstrable (401 → 200 → 429); one controlled entry point; configuration-as-code fits the brief's GitOps principle; the backend stays private.
- **Costs:** one more container and configuration file; one more hop to debug; token validation happens twice (gateway and backend).
- **Compliance:** APISIX (Apache-2.0) is added to `THIRD-PARTY-NOTICES.md` and the deployment documentation; it is distributed as an upstream image, not modified.
- **Out of scope for the competition:** APISIX Dashboard and Admin API, etcd cluster, WAF/ClamAV plugins, service discovery, multi-node deployment, a developer portal. These remain future direction.

## Alternatives considered

| Option                                  | Reason not selected                                                                              |
| --------------------------------------- | ------------------------------------------------------------------------------------------------ |
| No gateway; Portal BFF and Caddy only   | Does not provide the mandatory API Gateway service for API clients other than the Portal         |
| Spring Cloud Gateway inside the backend | Not a separate edge component; mixes gateway concerns into the monolith                          |
| Kong Gateway (open-source)              | Comparable features, but the brief names APISIX and the team's earlier design already targets it |
| Caddy or Nginx as reverse proxy only    | No built-in OIDC bearer validation or rate-limit policy without custom modules                   |
| APISIX with etcd and Admin API          | Extra stateful service and an admin surface to secure; not needed for a single-node demo         |

## References

- [#116](https://github.com/tricore-opentrix/opentrix/issues/116), [#119](https://github.com/tricore-opentrix/opentrix/issues/119), [#115](https://github.com/tricore-opentrix/opentrix/issues/115), [#216](https://github.com/tricore-opentrix/opentrix/issues/216)
- [ADR-009](ADR-009-modular-monolith-flowable.md) · [ADR-017](ADR-017-helpdesk-first-scope.md)
- [Architecture](../ARCHITECTURE.md) · [API](../API.md) · [Historical gateway design](../02-core/gateway/gateway-architecture.md)
- [Apache APISIX deployment modes](https://apisix.apache.org/docs/apisix/3.0/deployment-modes/) · [Apache APISIX 3.13.0 release](https://apisix.apache.org/blog/2025/06/27/release-apache-apisix-3.13.0/)
