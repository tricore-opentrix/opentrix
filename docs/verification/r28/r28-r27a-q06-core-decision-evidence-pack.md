<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# R28 → R27A — Q06 Core producer decision/evidence package

**Status: PROPOSED CORE CONTRACT DIRECTION — HUMAN OWNER / INDEPENDENT REVIEW REQUIRED.**
**Decision candidate:** Protocol **S**, conditional and disabled until proof. This document is an AI-assisted technical preparation for Bảo's sign-off, **not Bảo's independent personal approval**, not a G0 acceptance, and not permission to implement a production resend path.

## Pinned sources and scope

| Source | Full commit SHA | Scope |
| --- | --- | --- |
| [#168 dependency package](https://github.com/tricore-opentrix/opentrix/pull/168) | d6be1d5e95404470919a0e15071421ba1cf0b53b (parent HEAD) | P0 contract / Q01–Q09 / test plan |
| [#165 Core assessment](https://github.com/tricore-opentrix/opentrix/pull/165) | 2335a0858b6eafeacdff82bf157b44df116145bc | Proposed command/ledger/PG serialization |
| [#160 ADR-015](https://github.com/tricore-opentrix/opentrix/pull/160) | 5618091dc205b196b551465d2c52def9313ed1fb | PROPOSED G0 ACL authority |
| [#145 R29](https://github.com/tricore-opentrix/opentrix/pull/145) | 5d577dd4a0a8efa830459cf35cb1868e52a9de2f | Consumer currently requires authoritative non-commit before resend |
| [Ánh Q06 response](https://github.com/tricore-opentrix/opentrix/pull/168#issuecomment-6734942421) | #168 parent HEAD | Consumer prefers S, conditional |
| [Ánh Q08 response](https://github.com/tricore-opentrix/opentrix/pull/168#issuecomment-6735029269) | #168 parent HEAD | Durable reservation, cancellation authority OPEN |
| [Core source-backed feasibility review](https://github.com/tricore-opentrix/opentrix/pull/168#issuecomment-6735141938) | #160 source SHA above | Existing monolith transaction != implemented Core key serialization |

**Scope boundary:** Q06 S path below applies to Core **ACL-admin assignment commands**. It does not silently cover Core Workflow CREATE/ACTIVATE/TRANSITION, Helpdesk ticket creation, independent business idempotency, or distributed exactly-once delivery. R27A may use this to design interfaces/tests only; no P0 is presently READY FOR IMPLEMENTATION.

## 1. Proposed Q06 decision: S rather than N

- **Why S:** same scoped key + semantic payload can safely be replayed if *all* originals, concurrent resends, delayed originals, recovery jobs and cleanup/admission paths serialize through an approved Core transaction/unique-key fence. There must be no side effect outside the atomic Core commit.
- **Why not N as current direction:** a negative status lookup, absent receipt, expired row or released lock does **not** prove a delayed original cannot later commit. A valid N alternative would require a durable authoritative closure/admission barrier, not yet designed or verified.
- **Consumer protocol:** Helpdesk must durably persist original tenant/verified service principal/operation scope, resource identity, key, exact canonical semantic payload, expectedPolicyGeneration, incoming fencingSequence and separate business/assignment/Workflow version tokens **before first dispatch**. On lost ACK/timeout/unknown commit: authenticated status lookup **first**, verify original scope + current entitlement, match original fingerprint/attempt and then conditional CAS of current intent. A historical receipt is not current ACL authorization.
- **Conditional resend:** only the **same key + identical semantics/G/fence/versions**, after lookup, within *approved* admission/retention, with independently proved Core same-key serialization; no refreshed key/G/fence or reinterpretation of old canonical bytes. A missing/in-flight status is NOT non-commit proof.
- **Fail-closed default:** until shared contract and actual mechanism are reviewed/proven, **resend DISABLED**. Missing/unauthorized/ambiguous/expired/unavailable status or unmatched receipt keeps Helpdesk in RECONCILIATION_REQUIRED; escalate under separately approved operations policy. Never timeout-convert to SYNCHRONIZATION_FAILED, release Q08 reservation, or auto-switch to unsafe N.

## 2. Q02–Q05, Q07 — selected *candidate* mechanisms, not approved choices

| Q | Preferred conditional mechanism | Mandatory unresolved owner decisions / blocking proof |
| --- | --- | --- |
| **Q02 — terminal rejection** | Persist a keyed, immutable **terminal no-op receipt** for *authorized, deterministic semantic rejection*, in an atomic transaction; historical same-key replay returns that result, not a fresh success after policy change. Different semantic fingerprint conflicts only when key identity was durably bound. | Enumerate rejection classes, status/error/wire precedence and audit differences. Invalid authentication, hidden resource, malformed request, SQL rollback, timeout, crash and ambiguous commit must not fabricate a terminal receipt. Policy G/fence/ACL/success-audit remain unchanged on no-op. **X-24 BLOCKED**. |
| **Q03 — atomic complete receipt** | Prefer *uncommitted scoped-key reservation* followed by ACL replacement + accepted fence + G + audit + complete terminal receipt in **one Core DB transaction**. If early reservation is used, choose commit-time completeness enforcement (candidate DEFERRABLE constraint trigger) plus trusted-writer coverage. | Required outcome/identity fields, FK/uniqueness, complete-schema validation and effective privileges OPEN. Ledger-row-only triggers do **not** detect ACL writer bypassing ledger entirely; close all writer paths/role grants or require a stronger DB invariant. Compare final-only alternative with proven key serialization before mutation. **X-25 / T07 BLOCKED**. |
| **Q04 — canonical fingerprint** | Strict **versioned server-derived** semantic projection; key scoped by tenant + verified canonical service identity + operation class + idempotency key. Bind exact resource/incarnation, actors/operation sets, business token, expected G, incoming fence, optional selected expected-accepted-fence and relevant version tokens; exclude trace/correlation from semantic equality. | Define JSON/wire field presence, null/default/unknown/duplicate handling, set ordering, canonical service mapping/identity migration, integer range/decimal encoding, exact bytes/domain/version/hash/encoding and V-01..V-09 golden digests. Don't assume binary64 preserves large integers; supplied digest is untrusted. **Golden vectors NOT RUN**. |
| **Q05 — retention/admission/restore** | Prefer immutable retired-key/tombstone identity after full outcome retention so stale original/resend cannot execute anew; no unqualified TTL-based key reuse. A separately approved authenticated admission floor may replace tombstones only if it excludes all late originals across restore/incarnation/issuer rotation. | Full-receipt retention duration, tombstone schema, expiry/status code, admission window, cleanup lock order, restore/reconciliation snapshot and operational authority OPEN. Expired/absent identity is **not** fresh. Replay original **Create and Assign** after cleanup/restore. **X-23 BLOCKED**. |
| **Q07 — guard and privilege** | Prefer shared-reader/exclusive-writer **tenant guard** with fixed lock order: guard → scoped key/receipt → current authority/ACL/resource facts → instance if relevant → mutation/audit/receipt. Consider narrowly scoped, hardened SECURITY DEFINER **lock-only** helper for reader acquisition without direct tenant guard generation UPDATE. | Exact helper signature, owner/search_path/pg_temp, role inheritance/EXECUTE grants/publication transaction, tenant guard authorization, all-writer lock coverage, connection pool and direct-DML denial OPEN. PostgreSQL SELECT FOR SHARE requires UPDATE on at least one column; **do not** grant readers UPDATE(acl_revision). Advisory lock alternative requires independent all-writer/namespace proof. **X-09/T08 BLOCKED**. |

**D-01 Option A remains baseline:** required expectedPolicyGeneration **plus** strictly increasing accepted resource fence. **OD-06 Option A** is a different, already direction-confirmed assignment-lag decision. Neither means emergency revocation is immediately effective: Q01 managed slice/admin deny/regrant invalidation and X-14/X-15 remain separate blockers.

### Core atomic execution/replay oracle (proposed)

1. Verify exact authenticated caller, tenant/resource scope and current authority for the requested *lookup*; no status/receipt disclosure before it. Fail closed on tenant mismatch, hidden resource or revoked service scope.
2. In a fresh command transaction, acquire tenant exclusive guard **before any key/ACL mutation**, then serialize/reserve exact scoped identity with database uniqueness. Under READ COMMITTED, conflict/no RETURNING needs a **fresh statement** to read committed state; same-statement empty result is not a license to execute.
3. If a matching terminal receipt exists, return historical result under current lookup permission, without re-evaluating old execution G/fence preconditions or writing ACL/G/fence/audit again. If fingerprint differs, conflict/no mutation.
4. If no committed receipt wins and identity is *currently admissible*, independently re-authorize the requested execution, check fresh expected G and incoming resource fence, then atomic replace managed grant slice + fence + G + audit + **complete keyed terminal result**. SQL/transaction failure before commit rolls back all; commit uncertainty stays unknown.
5. Serialize **every** original/resend/delayed arrival through the same protocol, including independently authorized maintenance/cleanup writers. Retired keys cannot become fresh after archive/restore. No network call inside Core transaction; Helpdesk only finalizes separate local current-intent CAS.

## 3. Concrete evidence plan before runtime enablement/cutover

**Repro environment (future authorized test task):** disposable PostgreSQL 17 with pinned image digest/minor, actual Core ACL-admin A, reader R, Workflow writer W, Helpdesk H, observer O and separate migration owner. Capture exact source/schema/OpenAPI/fixture SHAs, effective grants and SET ROLE reachability, isolation and driver versions. Use named concurrent *barriers*, not sleeps; capture SQLSTATE, session-tagged timeline/lock graph, transaction end, before/after snapshots and exact command output. No production DDL/DSN.

| Case | Deterministic schedules and pass/fail oracle | Status now |
| --- | --- | --- |
| **X-12** | Hold first command before guard / after guard / after mutation-before-COMMIT; start same-key resend first/second and delay original; vary original commit vs rollback and suppress ACK. At most one committed ACL/G/fence/success-audit effect; matched terminal replay or one fresh eligible execution after actual rollback. No new key or stale regrant. | NOT RUN; Q02–Q05/Q07 dependencies |
| **X-13** | Authorized status lookup after commit, in-flight first command and after revoke; wrong tenant/principal/expired status. No existence/G/fence/receipt leak; NOT_FOUND while original in flight is not proof of non-commit. | NOT RUN; auth/status wire OPEN |
| **X-23** | Cleanup first vs resend first under same guard; resend original Create **and** Assign after receipt archive/expiry and restore. Retired scope/key cannot create duplicate instance or ACL effect; missing restored identity must fail closed. | BLOCKED; Q05 |
| **X-24** | Commit deterministic authorized no-op rejection, replay same key after policy change and conflicting payload, compare no-op/rejection audit vs no ACL/G/fence success mutation. Auth/malformed/infrastructure failure cannot create fake terminal receipt. | BLOCKED; Q02/Q04 |
| **X-25 / T07** | Fault after reservation/ACL revoke/grant/G/fence/audit/receipt, including skip receipt finalize, savepoint, validator bypass and role escalation. Incomplete terminal outcome fails COMMIT and reverts *all* policy/ledger/audit mutation. Positive control succeeds with full receipt. | BLOCKED; Q03/Q07 |
| **X-09 / T08** | Shared reader acquired first → writer blocks; exclusive policy writer first → fresh READ/HISTORY waits and reauthorizes after revoke. Actual R/W cannot directly UPDATE guard/ACL or SET ROLE to A/owner; H cannot Core DML. Test lock helper and timeout/deadlock graph/full rollback. | BLOCKED; Q07 |
| **X-16 / X-26 (consumer)** | Core commit + Helpdesk CAS fail/supersede, lost ACK/restart, Resolve/Confirm reservation and conflicting assignment at barrier. No false success, no silent release/reversal, matching current intent can finalize once; unresolved disposition persists for operator. | BLOCKED; Q06/Q08 |

**Exit criteria are not merely docs lint or a green unit test.** Require exact commands, nonzero executed test count (no hidden skipped suites), actual role/grant evidence, artifact digests and independent security review. Test plan != runtime proof; no PostgreSQL, T07/T08, two-service E2E, migration or grants executed by this document.

## 4. Gate/owner closure record — to be completed by humans

| Closure item | Current status |
| --- | --- |
| **Core owner (Bảo)** personal choice of S, scoped to ACL-admin and Q02–Q05/Q07 selected details | **PENDING explicit owner confirmation**; design analysis and repository comments are not signatures |
| **Helpdesk owner (Ánh)** consumer preference for conditional S and Q08 reservation | **RECORDED AS CONDITIONAL PREFERENCE**, not implementation approval |
| **Security/architecture (Yến)** independent review of the *new exact package SHA*, auth/status disclosure, all-writer serialization, cancellation and retention | **PENDING new-head review** |
| **R29 #145** producer/consumer amendment replacing non-commit-before-resend rule | **PENDING** on separate owner branch; must pin new reviewed R29 SHA |
| **Q06 contract freeze** | **BLOCKED** until owner-selected details, exact API/security/ledger/retention/admission text, R29 amendment and reviewed SHAs align |
| **R27A implementation permission** | **0/6 P0 READY**; no runtime/DDL/cutover from this package |
| **ADR-015/G0 / R27 Step 03** | ADR-015 PROPOSED; G0-CONTRACT BLOCKED; G0-DESIGN NOT ACCEPTED; Step 03 IN PROGRESS |

**Owner review format:** record selected and rejected options with rationale, exact full producer/consumer/package SHAs, explicit authorization boundaries, pending proof/test applicability, operation permission and residual risks. Acceptance of a *direction* is not acceptance of an executable schema or runtime evidence.
