<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# ADR-017 - Helpdesk-first competition scope

**Status:** ACCEPTED — effective on merge with approvals from @lexuanbao258-collab and @ngang02012007-crypto, per `GOVERNANCE.md`

**Decision date:** 2026-11-12

**Author:** @phanyen06ym-ien · **Reviewers:** @lexuanbao258-collab, @ngang02012007-crypto · **Scope proposal:** @ngang02012007-crypto (comment on [#194](https://github.com/tricore-opentrix/opentrix/issues/194))

**Tracking:** Phase 4 [#216](https://github.com/tricore-opentrix/opentrix/issues/216)

**AS-IS baseline:** `main@323b09b337e85474502f9021348708b5e91b0b0f`

## Tóm tắt

Bản dự thi chỉ có **một ứng dụng nghiệp vụ: IT Helpdesk**. **Facility Maintenance, Node-RED và Superset hoãn** đến sau cuộc thi. Đề thi yêu cầu "ít nhất **một** ứng dụng minh họa", nên phạm vi này đáp ứng đề. Phạm vi chia hai mốc: **vòng trường 19/11/2026** trình diễn luồng Helpdesk bằng dữ liệu thật qua Keycloak và APISIX trên engine hiện tại; **bản dự thi 06/12/2026** thêm Flowable (ADR-009) và tệp đính kèm (ADR-016). Nhóm chỉ được nói Core **được thiết kế để tái sử dụng**, không được nói Core **đã được tái sử dụng cho hai ứng dụng**.

## Context

Section 3 of the OLP 2026 brief requires a headless Core on Tier 1 and **at least one** demo application with a user interface on Tier 2 (H-P-D-I space). Repository judging is 7–9/12/2026 and the final demonstration is 10/12/2026.

AS-IS on `main`:

- IT Helpdesk has a backend API (nine operations under `/api/v1/mvp/requests`), the `it-helpdesk` workflow (SUBMITTED → TRIAGED → IN_PROGRESS → RESOLVED → CONFIRMED, plus assignment), a React Portal and a Portal BFF.
- Facility Maintenance has no backend implementation: `application/facility/` holds only a `.gitkeep` reserving the package, and there is no Facility API, workflow definition or backend test. The React Portal has a `facility` request kind (`frontend/src/domain/request.ts`) used by MOCK fixtures and UI tests only; it is not connected to any backend. Facility design appears in historical documents (`docs/00-project/`, `docs/02-core/gateway/`).
- Portal tests run in MOCK mode; real Keycloak → BFF → backend → database browser E2E is not yet evidenced (#118).

The team decided on 2026-11-12 (Ánh's scope comment on #194, confirmed by all three maintainers) to focus the remaining time on one complete, verifiable application.

## Decision

1. **Competition scope:** IT Helpdesk is the only business application in the v1.0.0 release, the demo and the Golden Path.
2. **Golden Path:** authenticated create → triage → assign → start → resolve → confirm, plus list, detail and history, with their authorization checks. The path ends in `CONFIRMED`; no `CLOSED` state or `/close` endpoint is added without a separate contract.
3. **Facility Maintenance is deferred** until after the competition. It is not listed as implemented, integrated or demonstrated anywhere. The Portal's `facility` request kind stays available only in MOCK mode and is not offered in integration-local or LIVE mode; the reserved `application/facility/` package stays empty.
4. **Core stays application-neutral.** Helpdesk-specific policy does not move into Core because only one application exists. Core boundaries and public APIs (ADR-009, ADR-016, #90, #193) are kept so a second application can be added later.
5. **Claims:** documentation, slides and release notes say **"reusable by design"**. **"Reuse verified across two applications"** is used only when a second application exists with integration, tests and reviewed evidence.
6. **Demo labels:** every demonstration states its mode — **MOCK**, **integration-local** or **LIVE**. LIVE is claimed only with exact-SHA E2E evidence.
7. **Two milestones, one scope:**

   | Milestone                    | Date       | Content                                                                                                                                                                                                                                                               |
   | ---------------------------- | ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
   | School round                 | 2026-11-19 | Golden Path with real data (integration-local): Keycloak login, APISIX gateway ([ADR-018](ADR-018-apisix-api-gateway.md)), backend on the current engine (`internal`), PostgreSQL. API frozen at the nine current Helpdesk operations. MOCK is the declared fallback. |
   | National submission (v1.0.0) | 2026-12-06 | School-round scope plus Flowable after a passed go/no-go ([ADR-009](ADR-009-modular-monolith-flowable.md)), Helpdesk attachments on S3-compatible storage ([ADR-016](ADR-016-s3-compatible-storage.md)), one-command Compose and LIVE E2E evidence (#118, #119).      |

8. **Deferred until after the competition:**
   - **Superset dashboards.** [ADR-008](ADR-008-dashboard-tool.md) stays ACCEPTED as the dashboard architecture; its implementation (R54: reporting views, Portal embedding, tenant-isolation tests) is not part of either milestone.
   - **Node-RED** email intake and automation, selected on 2026-11-05.
   - **Hybrid manifest-driven application loading** and formal dual (capability/application) contracts, listed as targets in `docs/ARCHITECTURE.md`. The competition build keeps Helpdesk as a Java module with its published `HelpdeskUseCase` API.

   These are documented as future direction only.

## Consequences

- **Benefits:** remaining time goes to one complete Golden Path (gateway and real-data demo for the school round; Flowable cutover, attachments, LIVE E2E #118, Compose stack #119, rights #138, release #190 for v1.0.0); fewer UI, API and migration changes; simpler regression and demo.
- **Portal:** if the `facility` request kind is reachable outside MOCK mode, the Portal owner removes it from those modes in a separate PR with tests.
- **Trade-off:** the submission does not prove cross-application Core reuse; this is stated openly rather than implied.
- **Documentation:** `README.md`, `docs/ARCHITECTURE.md`, `docs/INTEGRATION.md`, `docs/API.md`, slides and release notes label Facility as deferred. Historical Facility documents stay unchanged as records.
- **Out of scope for the competition:** Facility runtime, a second application built only for presentation, dynamic application installation, a generic public Workflow HTTP API (#115), Node-RED automation, Superset or other dashboards, and any feature shown without runtime evidence.

## Alternatives considered

| Option                                              | Reason not selected                                                                                     |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| Build Facility as a second application before 06/12 | Not required by the brief; would split the time needed for Flowable cutover, LIVE E2E and release gates |
| Minimal Facility demo (UI only, mock data)          | Would suggest reuse without evidence; contradicts the evidence policy                                   |
| Keep both applications in scope without a decision  | Leaves documentation and demo claims inconsistent                                                       |

## Revisit conditions

Facility (or another second application) is reopened after 10/12/2026, or earlier only if the Helpdesk Golden Path, ADR-009 gate G4 and release gates #138 and #190 are all complete. Reopening requires its own issue, API contract, tests and review.

## References

- OLP 2026 brief, section 3 (project files) — "ít nhất một ứng dụng minh họa"
- [#216](https://github.com/tricore-opentrix/opentrix/issues/216), [#194](https://github.com/tricore-opentrix/opentrix/issues/194) (scope comment), [#118](https://github.com/tricore-opentrix/opentrix/issues/118), [#119](https://github.com/tricore-opentrix/opentrix/issues/119), [#138](https://github.com/tricore-opentrix/opentrix/issues/138), [#190](https://github.com/tricore-opentrix/opentrix/issues/190)
- [ADR-008](ADR-008-dashboard-tool.md) · [ADR-009](ADR-009-modular-monolith-flowable.md) · [ADR-016](ADR-016-s3-compatible-storage.md) · [ADR-018](ADR-018-apisix-api-gateway.md)
- [Phase 2 Block C audit](../09-evidence/phase-2/block-c-application.md)
- [Integration](../INTEGRATION.md) · [API](../API.md)
