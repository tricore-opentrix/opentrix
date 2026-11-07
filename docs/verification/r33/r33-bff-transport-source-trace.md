<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# R33 — BFF transport source trace and scoped integration

## Scope and exact technical references

- Target branch: `feature/r33-bff-transport-integration-20261107`, based on `main@187dbd2ea6935966f5c4cceb95ad9c3c53708a2e`.
- Source under review: [Draft PR #98](https://github.com/tricore-opentrix/opentrix/pull/98), exact reviewed head `25f73d10b51556b446af12e636b9e19cd53ad030`. Its parent feature base `feature/issue39-mvp-integration` is **not** merged wholesale into R33.
- Baseline integration source: `frontend/src/features/helpdesk/LocalHelpdeskIntegration.tsx` and `frontend/src/services/mvp/http/sameOriginTransport.ts` from `main@187dbd2`.
- This document is **technical correspondence and review scope**, not first-person copyright testimony or release-rights clearance. Rights register at [Issue #138](https://github.com/tricore-opentrix/opentrix/issues/138) stays `RIGHTS_PENDING`.

## Source correspondence

| Files in R33 | Technical source / change | Verification boundary |
| --- | --- | --- |
| `frontend/src/services/mvp/bff/BffSessionClient.ts`, `http.ts`, `browserAuthContract.ts` | PR #98 at `25f73d1`; imported with repository SPDX headers | Yến independently reviewed Phase 2A session/CSRF at source/test level; no server/browser E2E acceptance |
| `frontend/src/services/mvp/bff/createHelpdeskBffTransport.ts` | PR #98 at `25f73d1`; no intentional behavioral change | Nine allowlisted logical Helpdesk routes, same-origin `/bff/api/v1/mvp/requests` mapping, per-session CSRF, no arbitrary auth headers or retry |
| `frontend/src/services/mvp/bff/*.test.ts` | PR #98 corresponding four Vitest suites; SPDX additions only | Fake-fetch regression evidence; rerun required at current R33 head |
| `frontend/src/services/mvp/http/predispatch.ts` | PR #98 at `25f73d1`; SPDX addition only | Identity-based pre-dispatch evidence; not a claim about attempted writes |
| `frontend/src/services/mvp/errors.ts`, `http/HelpdeskApiClient.ts`, `http/codecs.ts`, `http/transport.ts` | PR #98 at `25f73d1`; SPDX restored | Session-generation check, predispatch validation, and `COMMIT_OUTCOME_UNKNOWN` semantics; retest against current main |
| `frontend/src/features/helpdesk/LocalHelpdeskIntegration.tsx` | **New R33 integration**, derived from main `187dbd2`, rewires separate local composition to PR #98 adapter | Needs fresh review + compile/test + real-provider integration fixture; keep MOCK default |

Historical PR #98 had security re-review by Yến at exact `25f73d1`: focused 331/331 PASS and 687/687 full frontend tests PASS in single-worker mode, with an initial parallel run showing two timeouts. Bảo accepted its isolated Phase 2A source/error contract with conditions. **Those historical runs do not attest to this new R33 commit.**

## Architectural and open-source preservation gates

1. Default Vite startup remains MOCK. Dynamic `integration-local` entry in `frontend/src/main.tsx` is unchanged. Local integration checks `https:` plus approved loopback hostname before any session request.
2. `HelpdeskApiClient` depends on injected `HelpdeskHttpTransport`; UI does not own BFF HTTP headers/credentials. No vendor-specific endpoint or OIDC token storage is added to Core.
3. BFF session is explicitly loaded; CSRF is kept in instance memory. Current 401 retires that session, with no refresh, POST replay or implicit reconciliation. Stale attempted POST remains `COMMIT_OUTCOME_UNKNOWN`.
4. Existing logical nine-route API remains unchanged. Route `/apps/helpdesk` via APISIX **not implemented in this patch**; requires R27/R35 approved gateway/contract. No claim of R36 real browser OIDC acceptance.
5. SPDX markers `SPDX-FileCopyrightText` and `SPDX-License-Identifier: Apache-2.0` are present for all new/modified source and this document. They state project attribution metadata, not proof of ownership or permission to license AI/third-party material.
6. No new dependency, binary archive, generated build output, SQL migration, SBOM or third-party code is intentionally introduced. Check REUSE/CI on exact R33 HEAD, and reconcile any deviations. License and provenance rights remain unresolved in #138.

## Review and acceptance remaining

- [ ] GitHub Actions CI at **exact R33 HEAD**: frontend build, unit tests, hygiene/REUSE and security check; inspect any flaky parallel runs.
- [ ] Independent Application/Identity reviewer confirms only the local R33 composition, session lifecycle and access boundaries; Bảo confirms HTTP/DTO and unknown-write contract.
- [ ] R27/R35 owners ratify APISIX route/gateway and cross-service contract before route adaptation.
- [ ] R36 owner runs real browser login/logout, session expiry, CSRF-negative and nine-step backend/Keycloak E2E on pinned runtime SHA.
- [ ] R27 Compliance owner and independent reviewers resolve actual copyright/provenance obligations per [#138](https://github.com/tricore-opentrix/opentrix/issues/138) before asserting release rights.

**Disposition:** `R33_SOURCE_PORTED_AND_LOCAL_COMPOSITION_PROPOSED`; `R33_INTEGRATION_ACCEPTANCE_PENDING`; `R36_LIVE_BLOCKED`; `RIGHTS_PENDING`. Do not merge or release on this record alone.
