<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# ADR-009 - Modular Monolith with embedded Flowable workflow engine

**Status:** ACCEPTED — effective on merge with approvals from @lexuanbao258-collab and @ngang02012007-crypto, per `GOVERNANCE.md`

**Decision date:** 2026-11-12

**Author:** @phanyen06ym-ien · **Reviewers:** @lexuanbao258-collab, @ngang02012007-crypto

**Tracking:** [#191](https://github.com/tricore-opentrix/opentrix/issues/191) · Phase 4 [#216](https://github.com/tricore-opentrix/opentrix/issues/216) · related [#193](https://github.com/tricore-opentrix/opentrix/issues/193), [#90](https://github.com/tricore-opentrix/opentrix/issues/90), [#115](https://github.com/tricore-opentrix/opentrix/issues/115)

**AS-IS baseline:** `main@323b09b337e85474502f9021348708b5e91b0b0f`

**Supersedes:** the two-service split direction recorded for R27 on 2026-11-05 (never implemented on `main`)

## Tóm tắt

Backend giữ **một ứng dụng Spring Boot dạng Modular Monolith**. **Flowable 7.2.x nhúng (chỉ engine BPMN)** là workflow engine của **bản dự thi quốc gia (v1.0.0, nộp 06/12/2026)**, thay engine tự viết `WorkflowRuntime`. **Vòng thi cấp trường ngày 19/11/2026 chạy engine hiện tại** (`internal`). Chuyển đổi theo các cổng G1–G4 có ngày cố định; **go/no-go ngày 28/11/2026**. Hợp đồng HTTP Helpdesk, phân quyền Java và lịch sử nghiệp vụ không đổi. ADR này là quyết định thiết kế; nó **không** chứng minh Flowable đã được triển khai, không thay thế #138 (quyền nguồn gốc) hay #190 (phát hành).

## Context

The OLP 2026 brief requires a headless Core that provides Identity/SSO, API Gateway, structured/unstructured data and a **Workflow engine**, used by at least one demo application. The brief's reference stack lists **Flowable (BPMN)** for the process-automation layer.

AS-IS on `main`:

- The backend is one Java 21 / Spring Boot 3.5.16 Gradle project with logical packages `core`, `application`, `gateway`, `infrastructure`.
- Workflow uses an **in-house engine**, not Flowable: `core.workflow.WorkflowRuntime`, `WorkflowDefinition`, `WorkflowInstance`, `WorkflowPersistencePort`, with `infrastructure.workflow.PostgresWorkflowPersistence` (`guardedTransaction`, optimistic `version`, `COMMIT_OUTCOME_UNKNOWN` without retry), Flyway `V2`–`V4` and Helpdesk SQL in `db/helpdesk/`.
- The Helpdesk definition `it-helpdesk` v1 has four state transitions — `triage` (SUBMITTED→TRIAGED), `start_work` (TRIAGED→IN_PROGRESS), `resolve` (IN_PROGRESS→RESOLVED), `confirm` (RESOLVED→CONFIRMED) — plus `assign`, which changes `assignmentVersion` without changing state.
- `HelpdeskController` depends on `infrastructure.workflow.HelpdeskService`; PR #215 (#193) introduces the `HelpdeskUseCase` application boundary.
- The SQL reviews in `docs/evidence/issue-25-*.sql` cover the in-house workflow tables only.

The Phase 2 audit (`docs/09-evidence/phase-2/`, findings RISK-02, REQ-06, B-001) found that the custom engine works for one application but is product code the team must maintain and defend, and that the two-service split was not implemented.

## Decision

1. **One Modular Monolith.** The backend stays one deployable Spring Boot application. Modules (Identity, Workflow, Data, Helpdesk, and the backend `gateway` package that holds the HTTP controllers) expose public Java APIs; no module depends on another module's `infrastructure` package. ArchUnit enforces the rules (#90). External traffic reaches the backend only through the API gateway ([ADR-018](ADR-018-apisix-api-gateway.md)). No separate workflow service, message broker, Flowable REST API or Flowable UI.
2. **Flowable is the workflow engine of the competition build (v1.0.0).** Use Flowable open source **7.2.x** (Apache-2.0; 7.2.0 is built on Spring Boot 3.5), embedded through the Spring Boot starter for the **BPMN process engine only**. IDM, CMMN, DMN, form, app and event-registry engines are disabled. Flowable 8 (Spring Boot 4) is out of scope.
3. **Persistence.** Flowable tables live in a dedicated `flowable` schema on the same PostgreSQL DataSource and transaction manager as the Helpdesk tables, so one Helpdesk command commits its business row and its engine state **in one transaction**. The runtime database role receives only the privileges Flowable needs; schema migration privileges stay with the migration role.
4. **Engine-independent boundary.** Applications call the Workflow module API and `HelpdeskUseCase`, never Flowable classes (`RuntimeService`, `TaskService`, entities). A Flowable adapter in `infrastructure.workflow.flowable` implements the workflow contract. The nine Helpdesk HTTP operations, their payloads, status codes and errors do not change.
5. **Authorization and concurrency stay in Java.** The verified principal, tenant and resource ACL are checked before the engine is asked to move. Flowable task assignment is never an authorization source. Optimistic concurrency keeps using `version` and `assignmentVersion`; an unknown commit outcome is still reported as `COMMIT_OUTCOME_UNKNOWN` without automatic retry.
6. **Domain history is the source of truth for the API.** The `history` endpoint keeps reading the domain transition history with the same `HistoryView` fields, not Flowable `ACT_HI_*` tables.
7. **Engine selection** uses one configuration property, `dxos.workflow.engine` (`internal` | `flowable`). One ticket is never processed by both engines, and there is no dual write.

## Cutover plan

| Gate         | Content                                                                                                                                                                                                                                                                                 | Evidence required                                                                         | Due                        |
| ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- | -------------------------- |
| G0           | This ADR accepted                                                                                                                                                                                                                                                                       | PR merged with both approvals                                                             | 2026-11-14                 |
| —            | **School-round demo freeze:** no workflow-engine change is merged to `main` from the evening of 2026-11-17 until after the school round; the demo runs `internal`                                                                                                                       | Demo tag on `main`                                                                        | 2026-11-17 → 2026-11-19    |
| G1           | Contract freeze: crosswalk of create / read / list / history / assign / four transitions — actor, tenant ACL, versions, errors, unknown commit (documentation only, no runtime change)                                                                                                  | Crosswalk table reviewed by both reviewers, pinned SHA                                    | 2026-11-20                 |
| G2           | BPMN model for `it-helpdesk`; Flowable adapter; `flowable` schema migration; switch with default `internal`                                                                                                                                                                             | Build green; adapter tests; schema and dependency versions recorded                       | 2026-11-23                 |
| G3           | Regression and security with `flowable`: all Workflow/Helpdesk tests, `HelpdeskHttpParityTest`, negative authorization (401/403/hidden 404), concurrency, rollback, history, restart; privilege review of the `flowable` schema; R23 inventory and `THIRD-PARTY-NOTICES.md` regenerated | JUnit PASS/FAIL/SKIP counts, SHA, JDK/Gradle/Flowable/PostgreSQL versions, sanitized logs | 2026-11-27                 |
| **Go/no-go** | Team decision recorded on #191                                                                                                                                                                                                                                                          | G1–G3 evidence                                                                            | **2026-11-28**             |
| G4           | Default becomes `flowable`; Helpdesk Golden Path E2E on the release candidate                                                                                                                                                                                                           | E2E log at the release-candidate SHA; reviewer sign-off                                   | 2026-12-01 (source freeze) |

The in-house engine code and tables are removed in a separate PR after the competition release, not during the freeze window.

## Rollback

- **Before G4:** `dxos.workflow.engine=internal` restores current behavior; Flowable test data is disposable.
- **After G4 with real writes:** Flowable process state is not compatible with the in-house engine. Rollback means restoring the tested database restore point taken before cutover; there is no configuration-only rollback. Ambiguous commits are reconciled, never replayed blindly.
- **Go/no-go fails:** the competition build ships with `internal`; README, demo and release notes state that Flowable is the accepted target with status `NOT_CUTOVER`, and #191 records the reason. Flowable must not be described as integrated without G3 evidence.
- **Data:** competition and demo databases are created fresh; instances of the in-house engine are not migrated.

## Consequences

- **Benefits:** a maintained, standard BPMN engine named in the competition reference stack replaces custom engine code; process changes become model changes; one deployable keeps transactions and operations simple.
- **Costs:** about two weeks of implementation and regression in the last four weeks before submission; a new schema and privilege set; a larger dependency tree.
- **Compliance:** Flowable and its transitive dependencies enter the R23 inventory; `THIRD-PARTY-NOTICES.md` is regenerated in the same PR that adds them, because the `r23-compliance` job compares it. Source rights (#138) and release acceptance (#190) remain separate gates. ADR ACCEPTED is not `RIGHTS_CLEARED` or `RELEASE_ACCEPTED`.
- **Evidence:** the `issue-25` SQL reviews do not cover the `flowable` schema; G3 adds its own review.
- **Documentation:** `docs/ARCHITECTURE.md` and `docs/02-core/README.md` reference this ADR in the Phase 4 documentation PR after the school round (2026-11-20); `docs/API.md` and `docs/TESTING.md` change only when G2–G4 change observable behavior or test commands.
- **Out of scope:** generic public Workflow HTTP API (#115), Flowable UI/REST, DMN/CMMN, microservices, message brokers, migration of historical instances, Facility.

## Alternatives considered

| Option                                                       | Reason not selected                                                                                                           |
| ------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------- |
| Keep the in-house engine for the competition; Flowable later | Leaves custom engine code as the evaluated product and diverges from the reference stack. Kept only as the go/no-go fallback. |
| Separate workflow service (R27 split, 2026-11-05)            | Adds network calls, token exchange and distributed transactions without a requirement for them. Superseded.                   |
| Camunda 7 / Camunda 8                                        | Camunda 7 Community Edition is end-of-life; Camunda 8 needs a separate Zeebe cluster and does not fit an embedded monolith.   |
| Temporal or other code-first engines                         | Not BPMN; adds a separate server; not in the reference stack.                                                                 |

## References

- [ADR-016](ADR-016-s3-compatible-storage.md) · [ADR-017](ADR-017-helpdesk-first-scope.md) · [ADR-018](ADR-018-apisix-api-gateway.md)
- [#191](https://github.com/tricore-opentrix/opentrix/issues/191), [#216](https://github.com/tricore-opentrix/opentrix/issues/216), [#193](https://github.com/tricore-opentrix/opentrix/issues/193), [#90](https://github.com/tricore-opentrix/opentrix/issues/90), [#115](https://github.com/tricore-opentrix/opentrix/issues/115), [#118](https://github.com/tricore-opentrix/opentrix/issues/118), [#138](https://github.com/tricore-opentrix/opentrix/issues/138), [#190](https://github.com/tricore-opentrix/opentrix/issues/190)
- [Phase 2 Block A audit](../09-evidence/phase-2/block-a-architecture.md)
- [Architecture](../ARCHITECTURE.md) · [Historical workflow design](../02-core/workflow/workflow-architecture.md)
- [Flowable 7.2.0 release](https://github.com/flowable/flowable-engine/releases/tag/flowable-7.2.0) · [Flowable engine source and license](https://github.com/flowable/flowable-engine)
