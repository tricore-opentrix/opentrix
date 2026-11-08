<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors

SPDX-License-Identifier: Apache-2.0
-->

# Data storage adapters

**Status:** MinIO dropped 2026-11-05; SeaweedFS (S3 API) planned, ADR pending; no production adapter, real integration UNVERIFIED
**Baseline:** e06fa429cfd92b032c166eb3ebf32803d13191c2

## Ownership and baseline

Data Core owns ObjectStoragePort, keys, metadata, write modes, content lifetime and normalized errors. An Infrastructure S3-compatible adapter implements the port and depends inward on Core. Its S3-compatible SDK/protocol is an implementation detail, not an AWS S3 deployment.

The baseline has the Core contract and an in-memory test fake. The infrastructure.storage package has no production adapter. [PR #34](https://github.com/tricore-opentrix/opentrix/pull/34) is an unmerged Draft MinIO candidate (historical: MinIO was dropped on 2026-11-05). Its description reports Java compilation and unit/configuration tests, while **real MinIO integration tests were NOT VERIFIED**. Supabase and filesystem-only implementations are outside the new MVP implementation scope.

## Selected local target

Use a local S3-compatible object store (SeaweedFS planned) as a private object store, private PostgreSQL 17 for relational state, and Keycloak for identity. Select the reviewed adapter explicitly; keep the bucket non-public and credentials outside Git; fail closed on missing or ambiguous binding. This page does not invent configuration keys or claim provisioning is complete.

Applications authenticate and authorize, allocate opaque keys, and own attachment-to-business-record bindings. The adapter stores bytes through the Core port. Do not expose raw provider URLs, credentials, SDK errors or arbitrary object-key operations to clients.

## Acceptance evidence required

On the exact adapter commit, test the real store: store/read/metadata/delete, full metadata replacement, exact byte length, caller-owned input stream, deterministic read close, normalized lazy failures, and concurrent CREATE_ONLY with one winner. Exercise restart persistence, unavailable service, timeout and uncertain write outcomes. Reconcile uncertain writes through authoritative state, without blind replay. Verify private bucket/network configuration and no secret leakage.

Separately test Application authorization before object access and PostgreSQL-to-object consistency and orphan recovery. Preserve JUnit XML, command, Java and object-store versions, sanitized configuration and commit SHA. Mock or in-memory tests alone do not establish real integration PASS.

See [ADR-007](../../08-decisions/ADR-007-data-storage.md), [Data architecture](data-architecture.md), and the [canonical Data contract](https://github.com/tricore-opentrix/opentrix/blob/399108767c22b1d607bab7f5d3d072ea81005794/docs/contracts/data-core.md).
