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
- Tests exercise the **actual** `LocalHelpdeskIntegration` and `BffSessionClient` lifecycle. The presentation-only `HelpdeskPortal` child is mocked to isolate the integration boundary; consequently, the suite does **not** send a Portal-originated Helpdesk API request through the transport. It verifies session loading, composition gating and lifecycle behavior, not end-to-end transport execution.
- Denied origins include HTTP localhost/loopback and HTTPS non-loopback; assert **zero** session fetches and **no mounted authenticated Portal**.
- Allowed HTTPS loopback origins are tested with an explicit authenticated BFF response; assert one same-origin session request with no redirect.
- Anonymous session does not mount authenticated Portal.
- An actual captured session scope is invalidated on component unmount.
- Response delivered after unmount, response body decoded after unmount, and old response delivered after a new authenticated mount never revive the retired Portal or invalidate the successor.
- No production code or public LIVE route was modified. **Tests are not a substitute for an actual-browser BFF/Keycloak E2E.**
- **Independent review:** Yến re-reviewed exact HEAD `c0f15bccbeb1127fd901e475a2e0a56cf1fa6b77` and marked Y-R33-01 **PASS for source/local composition only** ([review](https://github.com/tricore-opentrix/opentrix/pull/156)). This does not claim provider-backed browser E2E.

## Y-R33-02 — Browser auth contract (intentionally NOT approved)

File: `frontend/src/services/mvp/bff/browserAuthContract.ts`.

- Browser OIDC logout redirect: **PENDING YEN CONFIRMATION**.
- Policy for CSRF-403: **PENDING YEN CONFIRMATION**.
- Session expiry and renewal/reauthentication: **PENDING YEN CONFIRMATION**.
- These are contract-data placeholders, not runtime promises. No fake browser acceptance, logout implementation, refresh/replay or new provider coupling is introduced.
- Owner of contract decision: **Yến (Identity/BFF)**; independent Backend/API cross-check: **Bảo**.

## Y-R33-03 — CSRF 403 (policy clarification required)

- Existing scoped test: `frontend/src/services/mvp/bff/sessionErrorBoundary.test.ts` (the bare-403 regression; no server-specific error code is assumed).
- The client maps a bare HTTP 403 to `FORBIDDEN` and does not automatically replay the POST, refresh CSRF, invalidate the session or log out. The fake-fetch test demonstrates only this client behavior; it does **not** establish that the response was caused by CSRF or that a later request will succeed.
- Bảo confirmed the BFF test currently establishes HTTP 403 only; it does not return a `CSRF_REJECTED` response code. A 403 on a write is therefore ambiguous at the client boundary: it may reflect authorization, CSRF validation or an expired session/filter ordering. Do not infer the cause from status alone.
- Bảo recommends retaining the conservative no-replay behavior and recording the ambiguity, then having R36 add a server-backed negative test for POST with an expired/absent session and capture the actual response. Identity/Backend must decide the user-facing recovery policy from that evidence.
- **Decision:** policy remains CONDITIONAL/PENDING server-backed evidence. Do not silently change this behavior. Any approved change requires new unit/integration regressions and independent review.

## Y-R33-04 — LIVE, gateway and legal boundaries remain blocked

- Real browser login/logout/expiry, CSRF-negative, actual Keycloak and Backend Golden Path: **R36 / NOT_TESTED**.
- Gateway/APISIX `/apps/helpdesk` and architectural integration: **R27/R35 contract pending**. Default MOCK and isolated `integration-local` stay unchanged.
- Provenance and redistribution rights: **Issue #138 / RIGHTS_PENDING**. A passing REUSE check proves license-metadata hygiene, **not** ownership or a right to distribute AI-assisted/third-party content.
- R33 PR remains Draft. Neither CI, this document, nor source-only regression tests imply LIVE, legal or release acceptance.

## Reviewer decision checklist

- [x] Yến independently re-reviewed Y-R33-01 at `c0f15bcc` and marked source/local composition PASS; provider-backed E2E remains outside scope.
- [x] Bảo re-reviewed route/DTO/error boundaries at `c0f15bcc`: scoped PASS, with two documentation/test precision findings now addressed in this follow-up.
- [ ] Re-run CI and obtain reviewer re-check on the follow-up HEAD.
- [ ] Yến and Bảo confirm the owner/decision route for Y-R33-02 and the server-backed policy evidence for Y-R33-03; no undocumented assumptions.
- [ ] R36 real-browser and Issue #138 rights remain explicitly blocked until independently verified.

**Status at reviewed HEAD `c0f15bcc`:** `Y-R33-01_SOURCE_LOCAL_PASS`; `Y-R33-02_CONTRACT_PENDING`; `Y-R33-03_CONDITIONAL_SERVER_EVIDENCE_PENDING`; `Y-R33-04_LIVE_AND_RIGHTS_BLOCKED`. Follow-up wording/test correction requires fresh CI and reviewer re-check.
