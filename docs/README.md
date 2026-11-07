<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors

SPDX-License-Identifier: Apache-2.0
-->

# DX-OS Open-Core — Documentation

Start with the [root README](../README.md) to build and run the project. This index lists the documents that exist on `main`.

| Section | Documents |
|---|---|
| 00-project | [Project overview](00-project/project-overview.md) · [Problem statement](00-project/problem-statement.md) · [Product vision](00-project/product-vision.md) · [Scope and MVP](00-project/scope-and-mvp.md) |
| 01-architecture | [System architecture](01-architecture/system-architecture.md) · [Core/application boundary](01-architecture/core-application-boundary.md) · [Dependency rules](01-architecture/dependency-rules.md) · [Deployment topology](01-architecture/deployment-topology.md) · [Repository layout (proposal)](01-architecture/repository-layout-and-ownership.md) |
| 02-core | [Identity](02-core/identity/identity-architecture.md) · [Workflow](02-core/workflow/workflow-architecture.md) · [Data](02-core/data/data-architecture.md) · [Storage adapters](02-core/data/storage-adapters.md) · [Gateway](02-core/gateway/gateway-architecture.md) |
| 06-deployment | [Runbook — Linux/macOS](06-deployment/runbook-linux.md) · [Prerequisites](06-deployment/prerequisites.md) · [R23 SBOM/licence plan](06-deployment/r23-plan.md) · [R24 release](06-deployment/r24-release.md) · [R26 repository cutover](06-deployment/r26-repository-cutover.md) |
| 08-decisions | [ADR-007 object storage](08-decisions/ADR-007-data-storage.md) · [ADR-008 dashboard tool](08-decisions/ADR-008-dashboard-tool.md) |
| verification | [Issue #53 Helpdesk integration](verification/issue53-java-helpdesk-mvp-integration-20261028.md) · [Issue #53 local closeout](verification/issue53-helpdesk-local-closeout-20261029.md) · [Issue #90 ArchUnit](verification/issue90-8a-archunit-foundation.md) |
| evidence | Pinned SQL review queries used by `scripts/` (Issue #25) |

Terminology is in the root [GLOSSARY.md](../GLOSSARY.md).

## Rules

1. Do not delete or rewrite historical evidence.
2. Do not move SQL fixtures referenced by Gradle or tests.
3. Do not change public contracts without approval.
4. Preserve existing Issue and PR traceability.
5. Architectural proposals are not implemented features.
6. Acceptance requires tests on a pinned commit.
