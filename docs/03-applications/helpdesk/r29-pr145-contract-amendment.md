<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# Proposed amendment to R29 PR #145 — cross-service command outcomes

**Status:** PROPOSED — amendment for Ánh's review; not applied to PR #145.
**Decision owner:** Yến. **Application contract owner:** Ánh. **Core/security review:** Bảo.
**Applicable PR #145 head reviewed:** `6e6e91e2e0f1f68f196eeb492dec371c52f402db`.
**Related:** [PR #145](https://github.com/tricore-opentrix/opentrix/pull/145), [ADR-015 / PR #160](https://github.com/tricore-opentrix/opentrix/pull/160), [PR #159 Core HTTP contract](https://github.com/tricore-opentrix/opentrix/pull/159), [Issue #138](https://github.com/tricore-opentrix/opentrix/issues/138) (rights tracking only; unrelated to G0 approval).

This document proposes exact R29 contract corrections for review. PR #145 remains Ánh's branch and is not modified by this remediation. The typed commands are still transport-neutral values; none of the behavior below is claimed as implemented.

## 1. Cross-service transaction boundary

Helpdesk business state and Core Workflow/ACL state are owned by separate services and transactions. A request spanning them is a recoverable workflow, not one atomic transaction. A local commit followed by a remote call must use durable intent/idempotency and reconciliation; unknown outcomes are never treated as rollback.

### Create + Activate

- Core may expose a reviewed composite create-and-activate operation that creates the Core instance and activates its initial state in one Core transaction.
- Helpdesk ticket creation is a separate Helpdesk transaction. Persist a durable create intent and scoped idempotency identity; correlate the result to the Core command/instance; reconcile an uncertain Core outcome by authenticated status before retrying.
- A Helpdesk failure after Core commit leaves a recoverable unmatched intent. Do not claim cross-service rollback or delete the committed Core instance without an explicit compensation contract.
- Same-key/same-payload replays the historical result; same-key/different-payload conflicts. Concurrent calls must not create duplicate tickets or instances. Actual retention and replay expiry remain R28/G0-DESIGN decisions.

### Assign / Reassign

- `Assign` first records Helpdesk's business intent and `assignmentVersion` in a Helpdesk transaction. The business assignment is pending until the exact Core ACL replacement command has committed and Helpdesk has finalized the matching acknowledgment.
- Keep `assignmentVersion`, Core ACL `policyGeneration`, and Workflow `workflowRuntimeVersion` separate. Core treats the Helpdesk version token as opaque correlation. A distinct monotonic per-resource fencing sequence is compared by Core only to reject stale/out-of-order commands; idempotency does not provide this ordering.
- Use the four Helpdesk synchronization states, event transitions, UI guarantees, error/retry policy, and lag decision in ADR-015 §8. A pending assignment is not authorization and the UI cannot claim that either actor's permissions have changed before Core confirmation.
- Atomic Core replacement means revoke-old + grant-new + audit + policy generation + committed ledger/fence in one Core transaction. It does not eliminate the pre-commit authorization-lag window.

### Resolve

Replace the current candidate wording “Atomic resolution write with Core workflow transition” with this sequence:

`PENDING_RESOLUTION → CORE_TRANSITION → RECONCILIATION → HELPDESK_FINALIZATION`

1. In a Helpdesk transaction, validate the expected business version and persist a durable resolution intent, idempotency key, correlation ID and pending outcome. This is not yet a resolved business outcome.
2. Send the authenticated Core transition command with the expected Workflow runtime version and stable idempotency identity. Core atomically authorizes and commits the Workflow transition/history within Core.
3. On success, timeout, disconnect or lost ACK, query authenticated Core command status before retry. A confirmed Core commit followed by failed Helpdesk finalization remains `RECONCILIATION`; do not report success or issue a new command key.
4. Helpdesk finalizes the resolution in its own transaction only after authoritative Core state/command evidence confirms the intended resource is `RESOLVED` and the resolution intent/version still matches. CAS protects against concurrent Helpdesk edits.
5. A definitive Core rejection produces a safe Helpdesk failure state with no claim of resolution. An unknown Core outcome remains pending/reconciling and is operationally visible; timeout budget exhaustion alerts but does not invent success/failure.

If Core committed `RESOLVED` but Helpdesk finalization fails or ACK is lost, Core remains committed. Reconciliation must recover that historical result and complete or explicitly reject Helpdesk finalization. This is a partial cross-service outcome, not a rollback or a distributed atomic write. Any compensation (for example a reverse Core transition) requires a separate business rule and is not implied.

### Confirm

Confirm is permitted only when both conditions hold at the time of the authorized operation:

1. An authoritative Core read/status, under current Core authorization, confirms the intended Workflow resource is `RESOLVED` (and uses the required expected Workflow version/concurrency check).
2. Helpdesk has durably finalized the matching resolution intent for the same ticket/resource and business version.

A pending intent, an unverified cached Core state, an old successful command replay, or Core `RESOLVED` without Helpdesk finalization is insufficient. Confirm's own Helpdesk mutation is conditional on the expected business version; its cross-service read/write consistency and retry response must be specified in R28 before handler integration.

## 2. Proposed error and retry mapping

Semantic codes below are candidates for R28 transport mapping. No HTTP implementation is claimed.

| Condition | Proposed result | Helpdesk action |
|---|---|---|
| Missing/invalid user or service authentication | `AUTHENTICATION_REQUIRED` (401 candidate) | Do not mutate; surface safe authentication failure. |
| Tenant/resource not visible | `NOT_FOUND` (404 candidate) | Do not disclose existence or retry unchanged authorization. |
| Visible resource but business/Core operation denied | `FORBIDDEN` / `ACL_ADMIN_FORBIDDEN` (403 candidate) | Do not retry without authorized state change. |
| Stale assignment/business version, Core policy generation, fence or Workflow version | `STALE_*` / `VERSION_CONFLICT` (409 candidate) | Reread authoritative state; create a new business intent only after conflict resolution. |
| Invalid Workflow transition | `INVALID_TRANSITION` (422 candidate) | No blind retry; refresh state and require a valid business decision. |
| ACL/Core authority unavailable, lock timeout or deadlock | `AUTHORIZATION_UNAVAILABLE` (503 candidate) | Fail closed. If commit definitely rolled back, bounded retry of the same command/key may follow policy; if uncertain, status lookup first. |
| Duplicate key with same canonical fingerprint | Original historical status/result | Do not execute another mutation; reconcile whether it is current. |
| Same idempotency scope/key with different fingerprint | `IDEMPOTENCY_PAYLOAD_CONFLICT` (409 candidate) | Do not mutate; correct client/key handling. |
| Possible commit but no ACK | `COMMIT_OUTCOME_UNKNOWN` (503 candidate) | Persist/retain reconciliation state; authenticated status lookup before any retry. |
| Definitive durable rejection | Stable specific rejection | Record terminal failure for this attempt; a corrected intent needs an explicit new version/key. |

Retries use bounded exponential backoff with jitter for transport/availability errors, honoring retry hints where defined. A status lookup is attempted before resending after any outcome that could have committed. The exact attempt limit, backoff, retention window and terminal escalation are **DECISION REQUIRED** in R28/G0-DESIGN; exhaustion leaves an observable reconciliation state rather than converting unknown into failure/success.

## 3. Observable intermediate states

R29 API/read models should expose safe business lifecycle states sufficient for clients/operators to distinguish pending from complete:

- Create: durable creation intent / Core creation reconciling / Helpdesk ticket finalized.
- Assign: `PENDING_SYNCHRONIZATION`, `SYNCHRONIZED`, `RECONCILIATION_REQUIRED`, `SYNCHRONIZATION_FAILED` (ADR-015 §8 defines semantics).
- Resolve: `PENDING_RESOLUTION`, `CORE_TRANSITION`, `RECONCILIATION`, `HELPDESK_FINALIZATION`, finalized or definitively rejected.
- Confirm: only report complete after both Core `RESOLVED` and finalized Helpdesk resolution checks succeed.

Status responses must not expose raw ACL internals or another tenant's command. Correlation IDs support tracing, not authorization. Logs/metrics should distinguish confirmed rollback, committed result, retry, stale/fenced rejection, and unknown outcome; never log bearer tokens or sensitive resolution text.

## 4. Contract test design (NOT RUN)

Before handler integration, add contract/integration tests for: Create + Activate partial failure and same-key replay; Assign state transitions and UI-safe status; lost ACK before/after Core commit; Helpdesk finalization failure after Core commit; duplicate/same-key-different-payload/concurrent commands; late older fenced assignment; atomic ACL replacement; cross-tenant denial and hidden 404 vs visible 403; Resolve partial failure and recovery; Confirm before finalization denial; Core `RESOLVED` plus Helpdesk finalized success; rollback/no partial writes; READ/HISTORY vs revoke; lock timeout/deadlock fail-closed. The [G0 verification matrix](../../verification/r27/adr015-g0-contract-verification-matrix.md) records each case and actual current status.

All these tests are **NOT RUN** for this documentation amendment. PostgreSQL, service handlers, ACL command API, ledgers, and cross-service E2E are not implemented/verified at the reviewed commits. This list does not convert PR #145 from candidate to R29 complete.

## 5. Required review actions

- **Ánh:** apply or amend these R29 changes on the PR #145 branch; confirm the recorded Option A pending-state/UI behavior is reflected in R29; resolve remaining API-visible intermediate-status and retry/retention choices; run R29 contract tests when handlers exist. Option A was selected by Yến and confirmed by Ánh and Bảo at reviewed SHA `af7506d26fbe33f4e634012389bde9c6553c31ab` (evidence linked in ADR-015 §8.3).
- **Bảo:** review Core command fencing/ledger/atomic replacement and the proposed Core-vs-Helpdesk transaction/error boundary; confirm PostgreSQL design only after actual disposable-DB verification.
- **Yến:** reconcile the amendments with ADR-010/ADR-015 and record any decision only after independent review. No reviewer verdict is inferred from this proposal.

Issue #138 remains the source-rights record and is not evidence of G0 acceptance or implementation authority.
