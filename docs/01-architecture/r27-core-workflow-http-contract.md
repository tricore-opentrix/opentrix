<!-- SPDX-FileCopyrightText: 2026 TRICORE contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# R27 Core Workflow HTTP contract proposal (Stage 2B)

> **Record status (09/11/2026):** candidate contract for [ADR-010](../08-decisions/ADR-010-core-helpdesk-service-boundary.md) D4. The referenced DTO file is uncommitted local work and is not on `main`. R28 owns the OpenAPI form. Routes stay unregistered per ADR-010 D8.

**Status: specified, not registered.** The transport DTOs are in
`core-service/src/main/java/com/tricore/dxos/api/workflow/CoreWorkflowHttpContract.java`.
No Workflow controller has been enabled in the Core process. A contract
definition does not authorize production traffic.

| Method | Path | JSON input | Successful output | Required operation |
| --- | --- | --- | --- | --- |
| POST | `/api/v1/core/workflow-instances` | `CreateRequest` | 201 `InstanceView`, Location | CREATE |
| POST | `/api/v1/core/workflow-instances/{id}/activate` | `ActivateRequest` | 200 `InstanceView` | ACTIVATE |
| POST | `/api/v1/core/workflow-instances/{id}/transitions` | `TransitionRequest` | 200 `TransitionView` | TRANSITION |
| GET | `/api/v1/core/workflow-instances/{id}` | none | 200 `InstanceView` | READ |
| GET | `/api/v1/core/workflow-instances/{id}/history` | none | 200 `HistoryView` | READ |

The actor comes only from a verified JWT through `CurrentPrincipal.requireVerified()`.
No request field or proxy-supplied identity header can set the actor or tenant.
The server must first resolve the exact resource and definition binding from
authoritative storage, then require current tenant membership and the exact
resource permission for the operation. Hidden or missing resources must have
the same 404 response. A role or token scope alone never grants resource access.
Do not call `WorkflowRuntime` until these checks are complete inside an
appropriate concurrency boundary.

`TransitionRequest.expectedVersion` is mandatory and maps to the existing
optimistic version check. `ActivateRequest.expectedVersion` is also mandatory
in this proposed contract, but `WorkflowRuntime.activateInstance` does not
yet accept it. The activation route must remain unregistered until that
version check and its tests exist. Create uses a caller-chosen unique instance
ID; duplicate IDs return 409. A write with `COMMIT_OUTCOME_UNKNOWN` must not
be retried automatically; clients reconcile through authorized reads.

| Condition | HTTP | Stable code |
| --- | ---: | --- |
| Missing/invalid verified authentication | 401 | `AUTHENTICATION_REQUIRED` |
| Visible resource without operation permission | 403 | `FORBIDDEN` |
| Hidden resource or missing instance/definition | 404 | `NOT_FOUND` |
| Duplicate instance or version conflict | 409 | `INSTANCE_ALREADY_EXISTS` / `VERSION_CONFLICT` |
| Unknown transition | 422 | `INVALID_TRANSITION` |
| Authoritative ACL unavailable | 503 | `AUTHORIZATION_UNAVAILABLE` |
| Uncertain write commit | 503 | `COMMIT_OUTCOME_UNKNOWN` |

## Dependency and database boundary

Core HTTP may depend on provider-neutral Workflow contracts, a trusted
principal port, and an authoritative resource-ACL port. It must not depend on
Helpdesk tickets, assignment rules, Helpdesk tables or a consumer-provided
`PostgresWorkflowPersistence`. Helpdesk will call Core over authenticated HTTP
only after the separate service and ACL adapter are implemented. Core alone
will own its Workflow schema and database role; the Helpdesk runtime role
must have no grants on Core tables. This is a required deployment design,
**not an implemented or live-database-verified condition**.

The current `TenantResourceWorkflowAccessPolicy` requires Helpdesk ACL facts
and explicitly does not make authorization and later writes transactional.
The legacy `HelpdeskService` also calls Core's JDBC adapter directly. These
are blockers to registering the routes. The original unregistered
`WorkflowController` remains unchanged. Existing Identity and negative tests
remain in `:backend`; no test of a proposed route is reported as passing.

## Open contract decisions from review A1–A4 (PR #159)

**Status: PROPOSED — CONTRACT DECISION REQUIRED (R28/R29).** The routes
above are **not extended** here. The constraints and tests are in
[ADR-010](../08-decisions/ADR-010-core-helpdesk-service-boundary.md#helpdesk-integration-constraints-adr-010-addition-review-a1a4).

- **A1:** decide whether CREATE and ACTIVATE become one Core-side composite
  command or stay two steps with recovery of `NOT_STARTED` instances. Either
  way, ACTIVATE stays unregistered until it validates `expectedVersion`.
- **A2:** the instance-ID 409 above is not idempotency. Decide the key
  transport, scope (tenant, caller, operation), payload-fingerprint conflict
  semantics, status codes and retention.
- **A3:** no Core ACL synchronization command exists for assignment. Its
  shape and authority require G0 (proposed ADR-015).
- **A4:** Resolve cannot be atomic across services. Decide the orchestration
  and the `COMMIT_OUTCOME_UNKNOWN` reconciliation.
