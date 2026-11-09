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

| ID | Scenario | Required assertion | Status | Evidence / gate |
|---|---|---|---|---|
| C-01 | Assignment intent commit | Helpdesk commits intent, `assignmentVersion`, fence, command ID and outbox before Core call; failed Helpdesk transaction sends no Core command | NOT RUN | Requires Helpdesk persistence/handler; R27/R29 implementation |
| C-02 | Assignment state transitions | Pending → synchronized only after authoritative Core committed status and Helpdesk CAS; timeout/finalization failure → reconciliation; durable rejection → failed | NOT RUN | Requires Core status API and Helpdesk handler |
| C-03 | Lost ACK before Core commit | Status lookup reports in-progress/not committed; same key/payload retry causes at most one mutation | NOT RUN | Requires Core ledger + fault injection |
| C-04 | Lost ACK after Core commit | Reconciliation finds historical commit and finalizes matching Helpdesk intent without a second mutation | NOT RUN | Requires Core ledger + fault injection |
| C-05 | Assignment authorization lag | Before replacement commit, assert actual old/new Core access matches the policy decision selected by Ánh/Bảo/Yến; no UI completion claim | BLOCKED | Authorization lag option is DECISION REQUIRED in ADR-015 §8.3 |
| C-06 | Fail-closed resource fence (if selected) | Protected Core operations are denied while fence is active; fence clears atomically only with approved replacement | BLOCKED | Applies only if Option B is selected; not selected or implemented |
| C-07 | Duplicate same idempotency key and payload | Concurrent/replayed request returns one historical outcome; no duplicate grants, audit or generation increments | NOT RUN | Requires disposable PostgreSQL and concurrency harness |
| C-08 | Same key, different canonical payload | Conflict; no mutation, audit success or generation change | NOT RUN | Canonicalization/hash rule remains a G0-DESIGN decision |
| C-09 | Concurrent same-key commands | One command owns processing; competitors observe in-progress or identical terminal outcome | NOT RUN | Requires ledger uniqueness and two/multi-connection execution |
| C-10 | Older assignment command arrives late | Core rejects fence ≤ last accepted; newer assignment remains effective | NOT RUN | Requires fence persistence/command API |
| C-11 | Idempotency vs version fencing | Distinct keys do not bypass stale-fence rejection; same-key replay is not treated as current ACL proof | NOT RUN | Requires C-07 and C-10 implementation |
| C-12 | Atomic ACL revoke/grant replacement | Old revoke + new grant + audit + policy generation + COMMITTED ledger + accepted fence commit together or all roll back | NOT RUN | Requires Core ACL persistence under effective runtime role |
| C-13 | Cross-tenant ACL command | Authenticated service principal cannot grant/revoke in another tenant; no cross-tenant data disclosure | NOT RUN | Requires Core auth policy and tenant fixtures |
| C-14 | Hidden/nonexistent vs visible denied resource | Hidden/nonexistent returns indistinguishable 404; visible resource without operation grant returns 403 | NOT RUN | Requires authenticated Core route and security tests |
| C-15 | Create + Activate partial failure | Core instance create+activation may be atomic in Core; separate Helpdesk intent recovers after remote failure without duplicate or false rollback | NOT RUN | PR #159/#145 remain documentation/candidate boundaries; E2E absent |
| C-16 | Resolve Core success, Helpdesk finalization failure | Core transition remains committed; Helpdesk stays reconciling and later finalizes only matching intent/version | NOT RUN | Requires two services and injected Helpdesk failure |
| C-17 | Resolve lost ACK/unknown outcome | Authenticated status lookup precedes retry; no new key or false failure/success | NOT RUN | Requires Core command ledger/status endpoint |
| C-18 | Confirm before resolution finalization | Deny/no mutation when Core is RESOLVED but matching Helpdesk resolution is still pending | NOT RUN | Requires R29 handler and authoritative Core read |
| C-19 | Confirm after both finalization checks | Succeed only when authorized Core state is RESOLVED and matching Helpdesk resolution is finalized at expected version | NOT RUN | Requires R29 handler + contract test |
| C-20 | READ/HISTORY vs REVOKE | A read serialized after committed revoke cannot expose protected data; use a transactionally consistent Core authorization/data snapshot | NOT RUN | T08, disposable PostgreSQL, two-connection barrier |
| C-21 | Transaction rollback | Failure at each ACL/audit/ledger write leaves no partial policy, generation, fence or success audit | NOT RUN | Requires PostgreSQL fault injection |
| C-22 | `lock_timeout` / `statement_timeout` | Timeout fails closed with no partial data and stable error; caller does not continue under stale authorization | NOT RUN | Requires effective runtime roles + PostgreSQL |
| C-23 | Deadlock | Victim transaction rolls back completely, returns fail-closed outcome, and any retry follows idempotent reconciliation | NOT RUN | Requires deterministic competing transactions |
| C-24 | Ledger retention/expiry | Active/unknown commands are not deleted; expired key/fence cannot be replayed as a new mutation | BLOCKED | Retention/tombstone policy not selected in G0-DESIGN |
| C-25 | READ/HISTORY lock privilege | Selected lock does not grant request-path authority to mutate `acl_revision`; verify least privilege | BLOCKED | Bảo's G0-DESIGN note; no PostgreSQL verification at review HEAD |
| C-26 | Cutover ownership edges | No cross-service FK or Helpdesk trigger reaches Core `tenant_guards` after approved split | BLOCKED | Requires separate reviewed database cutover; no migration authorized |

## Evidence recording protocol

For each future execution, record exact source SHA, PostgreSQL version, migration state, runtime role, test command, exit code, raw log/artifact link, and reviewer. Do not replace this design matrix with a green aggregate CI badge. A test requiring unimplemented routes, migrations or schemas remains NOT RUN/BLOCKED and cannot be inferred from documentation lint or unit tests.

No PostgreSQL test was run as part of the ADR-015 contract remediation. R27, G0 implementation/runtime and release acceptance remain separate gates.
