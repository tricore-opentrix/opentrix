<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# ADR-016 - S3-compatible object storage and module data ownership

**Status:** ACCEPTED — effective on merge with approvals from @lexuanbao258-collab and @ngang02012007-crypto, per `GOVERNANCE.md`

**Decision date:** 2026-11-12

**Author:** @phanyen06ym-ien · **Reviewers:** @lexuanbao258-collab, @ngang02012007-crypto

**Tracking:** [#181](https://github.com/tricore-opentrix/opentrix/issues/181) · Phase 4 [#216](https://github.com/tricore-opentrix/opentrix/issues/216) · adapter and provider selection [#192](https://github.com/tricore-opentrix/opentrix/issues/192)

**Supersedes:** [ADR-007 - MVP object storage provider](ADR-007-data-storage.md)

**AS-IS baseline:** `main@323b09b337e85474502f9021348708b5e91b0b0f`

## Tóm tắt

Dữ liệu có cấu trúc giữ trên **PostgreSQL 17**. Dữ liệu phi cấu trúc dùng **API tương thích S3** phía sau hợp đồng `ObjectStoragePort` hiện có; **bỏ hướng MinIO** của ADR-007. Ứng dụng đầu tiên dùng lưu trữ phi cấu trúc là **tệp đính kèm của yêu cầu Helpdesk** trong bản dự thi v1.0.0. Việc chọn **nhà cung cấp cụ thể**, viết adapter và API đính kèm thuộc #192, làm **sau vòng thi cấp trường 19/11/2026**. **Tách schema vật lý theo module để sau cuộc thi**; trước đó quyền sở hữu được ghi bằng bảng dưới đây và quyền SQL. ADR không chứng minh adapter hay nhà cung cấp nào đã chạy.

## Context

The OLP 2026 brief requires the Core to manage structured and unstructured data. ADR-007 selected local MinIO as the MVP target. The team later stopped using MinIO (#26 closed) and agreed on an S3-compatible API so that no vendor is locked into Core.

AS-IS on `main`:

- `core.data.ObjectStoragePort` defines `store(StoreObjectCommand)`, `read(ObjectKey)`, `metadata(ObjectKey)` and `delete(ObjectKey)` with documented semantics (`CREATE_ONLY`, `OVERWRITE`, exact content length, `NOT_FOUND` on missing or repeated delete, caller-owned input streams).
- Tests use `InMemoryObjectStorage` and `ObjectStoragePortTest`. No production adapter exists, and no real provider has been tested.
- `backend/` and `infra/` contain no MinIO configuration; MinIO remains only in documentation and historical records.
- PostgreSQL 17 is shared, and all backend tables currently live in **one configured schema** (`${flyway:defaultSchema}`; the local Helpdesk setup uses `helpdesk_demo`): workflow tables (`workflow_definitions`, `workflow_instances`, `workflow_transition_history`, …), authorization tables (`tenant_memberships`, `tenant_guards`, `resource_registry`, `resource_acl`, `workflow_policy_audit`) and Helpdesk tables (`helpdesk_requests`, `helpdesk_actors`). Migration and runtime database roles are separated (`runtime-grants.sql`, `docs/evidence/issue-25-*.sql`).
- Flyway `V1` creates `requests` and `request_status_history` from the first MVP; no backend Java code reads or writes them.

## Decision

1. **S3-compatible API behind `ObjectStoragePort`.** Application code calls the port only. One infrastructure adapter talks to an S3-compatible endpoint (configurable endpoint, region, path-style access, bucket). No vendor name appears in Core, application contracts, object keys or business records.
2. **The port contract is preserved.** The adapter must pass the existing `ObjectStoragePortTest` contract unchanged. `CREATE_ONLY` has one winner under concurrency and never overwrites; `OVERWRITE` replaces content and all metadata without compare-and-swap; `read` returns content and metadata of the same object version; `delete` keeps `NOT_FOUND` for missing keys; SDK exceptions and credentials never leak through the port. Changing any of these requires a versioned contract change, not an adapter shortcut.
3. **No cross-store transaction.** PostgreSQL cannot roll back an object write. The consuming application records the object binding, reconciles uncertain writes before retrying, and cleans orphans through an explicit job, never by destructive guessing.
4. **Authorization stays with the owning application.** Every object operation is preceded by the application's tenant/resource ACL check. Buckets are private; there is no public file endpoint.
5. **Module data ownership** follows the matrix below. Shared PostgreSQL does not give every module access to every table.
6. **Structured data stays on PostgreSQL 17 with versioned migrations.** Existing Flyway migrations, including the unused `V1` tables, are never edited or deleted; unused tables are documented as legacy and may be dropped only by a new migration after the competition.
7. **Physical schema separation is deferred until after the competition.** Until then all tables stay in the one configured schema; ownership is enforced by the matrix below, by ArchUnit module rules (#90) and by runtime grants. Splitting schemas now would change Flyway placeholders, grants and the `issue-25` privilege evidence during the final weeks. The Flowable tables of [ADR-009](ADR-009-modular-monolith-flowable.md) are the exception: they are new, so they start in their own `flowable` schema.
8. **First consumer: Helpdesk attachments (v1.0.0).** A ticket can carry attachments stored through `ObjectStoragePort`. The upload, list and download endpoints, size limit and allowed content types are defined as an API contract in #192 and reviewed by the application owner before implementation. Every attachment operation checks the ticket ACL first; object keys are opaque and never derived from file names. Work starts after the school round on 2026-11-19.

## Data ownership matrix

| Data                                                        | Owning module                  | Store                                                                                                         | Rules                                                                                             |
| ----------------------------------------------------------- | ------------------------------ | ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| Users, credentials, sessions                                | Identity (Keycloak)            | Keycloak database, outside the backend                                                                        | Backend consumes verified identity only; never copies passwords                                   |
| Workflow definitions, instances, transition history         | Workflow                       | PostgreSQL — current workflow tables; `flowable` schema after [ADR-009](ADR-009-modular-monolith-flowable.md) | Only the Workflow module migrates and writes these tables                                         |
| Tenant memberships, resource registry and ACL, policy audit | Workflow authorization (Core)  | PostgreSQL — shared schema                                                                                    | Written only through Core authorization code; applications query permissions through the Core API |
| Helpdesk requests, actors, attachment bindings              | Helpdesk                       | PostgreSQL — shared schema                                                                                    | Only Helpdesk writes them; other modules use `HelpdeskUseCase`                                    |
| Legacy MVP tables `requests`, `request_status_history`      | None (legacy)                  | PostgreSQL — shared schema                                                                                    | Read and written by no code; kept because migrations are immutable                                |
| Object bytes and object metadata                            | Data (via `ObjectStoragePort`) | S3-compatible bucket                                                                                          | Data stores bytes; it does not own business ACL                                                   |
| Object key ↔ business record, retention status              | The consuming application      | Its own PostgreSQL schema                                                                                     | Opaque keys; reconcile on uncertain writes                                                        |
| Future applications                                         | Each application module        | Its own schema                                                                                                | No cross-module SQL; communicate through published APIs                                           |

Each module's runtime role gets least-privilege grants on its own schema only. Grants are verified by tests when each schema is introduced.

## Provider selection (input to #192)

The provider is selected in #192, before the adapter is merged. The selection record must state:

- product and exact version; self-hosted or managed; license and NOTICE obligations (OSI-approved license required for anything distributed with the release);
- support for the operations the port needs (put, get, head, delete), conditional create for `CREATE_ONLY`, streaming with exact content length, user metadata, path-style endpoints;
- private buckets, least-privilege credentials, credential injection without committed secrets;
- reproducible clean install in Docker Compose for the competition build (`Building from source` criterion);
- results of the unchanged `ObjectStoragePortTest` contract against the real provider.

If a guarantee cannot be met, #192 records it as `BLOCKED` or proposes a versioned contract change. No S3-compatible product is assumed to behave exactly like AWS S3.

## Consequences

- **Benefits:** no vendor lock-in in Core; provider can change without touching applications; ownership of every data group is explicit.
- **Costs:** one adapter to validate per provider; explicit reconciliation; credentials and configuration to operate.
- **Documentation:** after merge, ADR-007 is marked `SUPERSEDED by ADR-016` (status line only). Active documents mention MinIO only as the replaced direction. Historical records keep MinIO unchanged: ADR-007, `docs/verification/`, `docs/00-project/`, `docs/01-architecture/`, `docs/02-core/data/`, `docs/06-deployment/`, `docs/09-evidence/`.
- **Compliance:** the provider's license, SDK dependencies and NOTICE obligations are checked in #192 and #138; this ADR's Apache-2.0 header does not license third-party code. No access keys, tokens or real user files in the repository or fixtures.
- **Out of scope for the competition:** physical schema split, new services, a generic public file API, event buses, migration between providers by configuration alone, and the brief's data-lifecycle principles (lakehouse offloading, IT/OT convergence, lineage and quality analytics). These are documented as future direction, not as implemented features.

## Alternatives considered

| Option                                   | Reason not selected                                                                                        |
| ---------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Keep ADR-007 (MinIO-specific)            | Contradicts the team decision (#181) and locks the design to one product                                   |
| Filesystem adapter as production storage | Does not provide S3-compatible behavior or a path to managed storage; acceptable only for tests            |
| Store files in PostgreSQL (`bytea`)      | Mixes binary objects with transactional data and grows the database used for workflow and business records |

## References

- [#181](https://github.com/tricore-opentrix/opentrix/issues/181), [#192](https://github.com/tricore-opentrix/opentrix/issues/192), [#216](https://github.com/tricore-opentrix/opentrix/issues/216), [#138](https://github.com/tricore-opentrix/opentrix/issues/138), [#190](https://github.com/tricore-opentrix/opentrix/issues/190)
- [ADR-007 - historical provider decision](ADR-007-data-storage.md) · [ADR-009 - Modular Monolith and Flowable](ADR-009-modular-monolith-flowable.md) · [ADR-017 - Helpdesk-first scope](ADR-017-helpdesk-first-scope.md)
- [Phase 2 Block B audit](../09-evidence/phase-2/block-b-backend-infra.md) (findings B-007, B-010)
- [Historical data architecture](../02-core/data/data-architecture.md) · [Historical storage adapters](../02-core/data/storage-adapters.md)
