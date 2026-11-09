<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# ADR-015 G0 Contract Verification Matrix

**Status:** Test design only; no test result is claimed.
**Contract source:** `docs/08-decisions/ADR-015-core-workflow-acl-v3-g0.md` at remediation HEAD (see Git commit).
**Related contract amendment:** `docs/03-applications/helpdesk/r29-pr145-contract-amendment.md`.
**Reviewed source commits:** PR #160 `eb6d7b0effbd9ebdc467a4a197097db37a5f9cd8`; PR #159 `ef4b9484369c94ed7e5674e4b056b0d8f673e1ba`; PR #145 `6e6e91e2e0f1f68f196eeb492dec371c52f402db`.
**Status vocabulary:** `PASS`/`FAIL` require a reproducible execution record; `NOT RUN` means no execution evidence; `BLOCKED` means the required implementation/environment is absent; `NOT APPLICABLE` requires a documented rationale. No row is PASS in this document.

## Decision and reviewer traceability

| Decision/evidence | Status | Scope and boundary |
|---|---|---|
| Yến, Decision Owner: select OD-06 Option A | CONTRACT_DIRECTION_CONFIRMED | R27 MVP, Helpdesk assignment/reassignment; owner decision is recorded at reviewed SHA `af7506d26fbe33f4e634012389bde9c6553c31ab` in [comment 6731860971](https://github.com/tricore-opentrix/opentrix/pull/163#issuecomment-6731860971). It is not ADR-015 acceptance or G0-CONTRACT PASS. |
| Ánh: ACCEPT Option A contract direction | CONTRACT_DIRECTION_CONFIRMED | [Confirmation 6731987954](https://github.com/tricore-opentrix/opentrix/pull/163#issuecomment-6731987954); UI/action gating and no immediate-revocation claim. |
| Bảo: CONFIRM Option A contract direction | CONTRACT_DIRECTION_CONFIRMED | [Confirmation 6732025189](https://github.com/tricore-opentrix/opentrix/pull/163#issuecomment-6732025189); no PostgreSQL/runtime verification. |
| Prior independent review | CONTRACT_DIRECTION_CONFIRMED | [Bảo](https://github.com/tricore-opentrix/opentrix/pull/163#issuecomment-6731595550) and [Ánh](https://github.com/tricore-opentrix/opentrix/pull/163#issuecomment-6731716719). |

These are contract decision/review statuses, not test statuses. PR #145 remains an Ánh-owned dependency: its R29 amendment is still proposed and must be applied/reviewed there before handler integration.

| ID | Scenario | Required assertion | Status | Evidence / gate |
|---|---|---|---|---|
| C-01 | Assignment intent commit | Helpdesk commits intent, `assignmentVersion`, fence, command ID and outbox before Core call; failed Helpdesk transaction sends no Core command | NOT RUN | Requires Helpdesk persistence/handler; R27/R29 implementation |
| C-02 | Assignment state transitions | Pending → synchronized only after authoritative Core committed status and Helpdesk CAS; timeout/finalization failure → reconciliation; durable rejection → failed | NOT RUN | Requires Core status API and Helpdesk handler |
| C-03 | Lost ACK before Core commit | Status lookup must not falsely report committed; while outcome is unresolved, do not duplicate execution; after authoritative rollback/not-committed evidence, retry same key/payload at most once | NOT RUN | Requires Core command-status behavior + fault injection; persistent `IN_PROGRESS` is not assumed |
| C-04 | Lost ACK after Core commit | Reconciliation finds historical commit and finalizes matching Helpdesk intent without a second mutation | NOT RUN | Requires Core ledger + fault injection |
| C-05 | Assignment authorization lag under Option A | Before Core replacement commit, old grant may remain effective and new actor is not yet authorized by this assignment; no immediate-revocation or completion claim | NOT RUN | Option A contract direction confirmed; runtime behavior and monitoring not implemented/tested |
| C-06 | Option B fail-closed assignment fence | No MVP fence protocol is asserted or tested | NOT APPLICABLE | Option A is selected for R27 MVP; Option B is not selected. Any future fence needs separate approval and tests. |
| C-07 | Duplicate same idempotency key and payload | Concurrent/replayed request returns one historical outcome; no duplicate grants, audit or generation increments | NOT RUN | Requires disposable PostgreSQL and concurrency harness |
| C-08 | Same key, different canonical payload | Conflict; no mutation, audit success or generation change | NOT RUN | Canonicalization/hash rule remains a G0-DESIGN decision |
| C-09 | Concurrent same-key commands | One command applies at most one mutation; competitors safely wait or receive an in-progress/terminal response | NOT RUN | Requires ledger uniqueness and concurrent database execution; persistent `IN_PROGRESS` is not assumed |
| C-10 | Older assignment command arrives late | Core rejects fence ≤ last accepted; newer assignment remains effective | NOT RUN | Requires fence persistence/command API |
| C-11 | Idempotency vs version fencing | Distinct keys do not bypass stale-fence rejection; same-key replay is not treated as current ACL proof | NOT RUN | Requires C-07 and C-10 implementation |
| C-12 | Atomic ACL revoke/grant replacement | Tenant/resource admin authorization + fence check + old revoke + new grant + audit + policy generation + durable COMMITTED outcome + accepted fence commit together or all roll back | NOT RUN | Requires Core ACL persistence under effective runtime role |
| C-13 | Cross-tenant ACL command | Authenticated service principal cannot grant/revoke in another tenant; no cross-tenant data disclosure | NOT RUN | Requires Core auth policy and tenant fixtures |
| C-14 | Hidden/nonexistent vs visible denied resource | Hidden/nonexistent returns indistinguishable 404; visible resource without operation grant returns 403 | NOT RUN | Requires authenticated Core route and security tests |
| C-15 | Create + Activate partial failure | Core instance create+activation may be atomic in Core; separate Helpdesk intent recovers after remote failure without duplicate or false rollback | NOT RUN | PR #159/#145 remain documentation/candidate boundaries; E2E absent |
| C-16 | Resolve Core success, Helpdesk finalization failure | Core transition remains committed; Helpdesk stays reconciling and later finalizes only matching intent/version | NOT RUN | Requires two services and injected Helpdesk failure |
| C-17 | Resolve lost ACK/unknown outcome | Authenticated status lookup precedes retry; no new key or false failure/success; caller uncertainty need not be a persistent ledger state | NOT RUN | Requires authoritative Core outcome/status lookup |
| C-18 | Confirm before resolution finalization | Deny/no mutation when Core is RESOLVED but matching Helpdesk resolution is still pending | NOT RUN | Requires R29 handler and authoritative Core read |
| C-19 | Confirm after both finalization checks | Succeed only when authorized Core state is RESOLVED and matching Helpdesk resolution is finalized at expected version | NOT RUN | Requires R29 handler + contract test |
| C-20 | READ/HISTORY vs REVOKE | A read serialized after committed revoke cannot expose protected data; use a transactionally consistent Core authorization/data snapshot | NOT RUN | T08, disposable PostgreSQL, two-connection barrier |
| C-21 | Transaction rollback | Failure at each ACL/audit/ledger write leaves no partial policy, generation, fence or success audit | NOT RUN | Requires PostgreSQL fault injection |
| C-22 | `lock_timeout` / `statement_timeout` | Timeout fails closed with no partial data and stable error; caller does not continue under stale authorization | NOT RUN | Requires effective runtime roles + PostgreSQL |
| C-23 | Deadlock | Victim transaction rolls back completely, returns fail-closed outcome, and any retry follows idempotent reconciliation | NOT RUN | Requires deterministic competing transactions |
| C-24 | Ledger retention/expiry | Committed deduplication identity/fingerprint/outcome/fence are retained per an approved policy; expired keys cannot replay as new mutations | BLOCKED | Retention/tombstone policy and rejected-command replay semantics remain G0-DESIGN decisions |
| C-25 | READ/HISTORY lock privilege | Selected lock does not grant request-path authority to mutate `acl_revision`; verify least privilege | BLOCKED | Bảo's G0-DESIGN note; no PostgreSQL verification at review HEAD |
| C-26 | Cutover ownership edges | No cross-service FK or Helpdesk trigger reaches Core `tenant_guards` after approved split | BLOCKED | Requires separate reviewed database cutover; no migration authorized |
| C-27 | Timeout monitoring and escalation | Delayed/unknown synchronization is monitored and escalated without claiming a hard revocation bound | BLOCKED | Timeout thresholds, alerting and escalation are OPEN — OWNER DECISION REQUIRED before runtime acceptance; no numeric SLA selected. |
| C-28 | Emergency revocation | An urgent access removal follows a separately approved emergency-revocation procedure | BLOCKED | Procedure/authority/evidence are not defined here; Option A is not immediate revocation. |
| C-29 | R29 PR #145 alignment | Create+Activate, Assign, Resolve and Confirm use the reviewed cross-service boundary before handlers are integrated | BLOCKED | Separate amendment exists; Ánh must apply/review it on PR #145. This task does not edit that branch. |
| C-30 | Pending-state action gating | Helpdesk blocks business operations requiring synchronized assignment until durable authoritative ACK yields `SYNCHRONIZED` | NOT RUN | Contract direction confirmed; Helpdesk UI/handlers are not implemented/verified here. |

## Evidence recording protocol

For each future execution, record exact source SHA, PostgreSQL version, migration state, runtime role, test command, exit code, raw log/artifact link, and reviewer. Do not replace this design matrix with a green aggregate CI badge. A test requiring unimplemented routes, migrations or schemas remains NOT RUN/BLOCKED and cannot be inferred from documentation lint or unit tests.

No PostgreSQL test was run as part of the ADR-015 contract remediation. R27, G0 implementation/runtime and release acceptance remain separate gates. PR #163's base branch is PR #160's feature branch; the review confirmed no applicable GitHub Actions run for the PR, so CI is NOT RUN/NOT VERIFIED for this remediation SHA.
