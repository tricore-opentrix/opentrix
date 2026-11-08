<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# R33 independent Identity/Security review — disposition and trace

## Fixed references

- PR: [#156](https://github.com/tricore-opentrix/opentrix/pull/156) (Draft, local integration only).
- Independent Identity/Security review: [Yến comment 6718512131](https://github.com/tricore-opentrix/opentrix/pull/156#issuecomment-6718512131).
- Reviewed baseline source HEAD: `4f10f106f883b3fb5eb13652958c2c81e465aca2`.
- Y-R33-01 test addition commit: `402c71389e01f60b1d1ef39c2b1ce73ff9a7d82c`.
- Earlier adapter technical source: [PR #98](https://github.com/tricore-opentrix/opentrix/pull/98) at `25f73d10b51556b446af12e636b9e19cd53ad030`.
- Rights and contributor source audit: [Issue #138](https://github.com/tricore-opentrix/opentrix/issues/138); **RIGHTS_PENDING**.

## Y-R33-01 — Direct local composition tests (implementation supplied; acceptance pending)

- Added `frontend/src/features/helpdesk/LocalHelpdeskIntegration.lifecycle.test.tsx`.
- Tests exercise **actual** `LocalHelpdeskIntegration`, `BffSessionClient` and the approved transport composition. The presentation-only `HelpdeskPortal` component is mocked to isolate the integration boundary and avoid unrelated listing fetches.
- Denied origins include HTTP localhost/loopback and HTTPS non-loopback; assert **zero** session fetches and **no mounted authenticated Portal**.
- Allowed HTTPS loopback origins are tested with an explicit authenticated BFF response; assert one same-origin session request with no redirect.
- Anonymous session does not mount authenticated Portal.
- An actual captured session scope is invalidated on component unmount.
- Response delivered after unmount, response body decoded after unmount, and old response delivered after a new authenticated mount never revive the retired Portal or invalidate the successor.
- No production code or public LIVE route was modified. **Tests are not a substitute for an actual-browser BFF/Keycloak E2E.**
- **Verification:** exact-HEAD CI pending; Yến must independently review the new tests and report PASS/CONDITIONAL/BLOCKED with line-specific evidence.

## Y-R33-02 — Browser auth contract (intentionally NOT approved)

File: `frontend/src/services/mvp/bff/browserAuthContract.ts`.

- Browser OIDC logout redirect: **PENDING YEN CONFIRMATION**.
- Policy for CSRF-403: **PENDING YEN CONFIRMATION**.
- Session expiry and renewal/reauthentication: **PENDING YEN CONFIRMATION**.
- These are contract-data placeholders, not runtime promises. No fake browser acceptance, logout implementation, refresh/replay or new provider coupling is introduced.
- Owner of contract decision: **Yến (Identity/BFF)**; independent Backend/API cross-check: **Bảo**.

## Y-R33-03 — CSRF 403 (policy clarification required)

- Existing scoped test: `frontend/src/services/mvp/bff/sessionErrorBoundary.test.ts` around lines 388–407 at reviewed HEAD.
- Current source behavior treats HTTP 403/CSRF_REJECTED as a `FORBIDDEN` response without automatic POST replay, CSRF refresh, credential escalation or browser logout. The test shows that an explicit subsequent user action can reuse the still-active session; this is **not** proof that the server will permit or reject that action.
- **Decision requested of Yến and Bảo:** On the actual BFF policy, should CSRF_REJECTED force session invalidation/reauthentication, or remain FORBIDDEN until an explicit user intervention? Which server response and negative test prove that disposition?
- Do not silently change this policy without backend contract evidence. Any approved change requires new unit/integration regressions and review.

## Y-R33-04 — LIVE, gateway and legal boundaries remain blocked

- Real browser login/logout/expiry, CSRF-negative, actual Keycloak and Backend Golden Path: **R36 / NOT_TESTED**.
- Gateway/APISIX `/apps/helpdesk` and architectural integration: **R27/R35 contract pending**. Default MOCK and isolated `integration-local` stay unchanged.
- Provenance and redistribution rights: **Issue #138 / RIGHTS_PENDING**. A passing REUSE check proves license-metadata hygiene, **not** ownership or a right to distribute AI-assisted/third-party content.
- R33 PR remains Draft. Neither CI, this document, nor source-only regression tests imply LIVE, legal or release acceptance.

## Reviewer decision checklist

- [ ] CI at the new test commit passes (frontend build/Vitest, REUSE/hygiene, BFF, backend, compliance).
- [ ] Yến independently reviews the new local-composition tests and confirms Y-R33-01 disposition.
- [ ] Yến and Bảo confirm ownership/decision route for Y-R33-02 and Y-R33-03; no undocumented policy assumptions.
- [ ] Bảo reviews route/DTO/error boundaries of PR #156.
- [ ] R36 real-browser and Issue #138 rights remain explicitly blocked until independently verified.

**Status:** `Y-R33-01_IMPLEMENTED_BUT_REVIEW_PENDING`; `Y-R33-02_CONTRACT_PENDING`; `Y-R33-03_POLICY_PENDING`; `Y-R33-04_LIVE_AND_RIGHTS_BLOCKED`.
