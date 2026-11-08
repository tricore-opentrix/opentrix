<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors

SPDX-License-Identifier: Apache-2.0
-->

# Scripts

Helper scripts for development and verification, added when needed.
Build and test currently use the Gradle Wrapper in `backend/`.

`check_md_links.py` checks relative links and `#anchor` fragments in every Markdown file tracked by Git. It does not check URLs that have a scheme (external URLs). It supports only simple inline links of the form `[label](target)`; reference-style links, angle-bracket destinations, destinations with spaces or parentheses, complex image/badge links, percent-encoded fragments and repeated-heading anchors (`-1`, `-2`) are not checked, and the heading-to-anchor conversion is an approximation of GitHub's. A clean run therefore means "no broken link detected within the supported subset", not a complete link audit. Run `python3 scripts/check_md_links.py`; it exits with code 1 if a broken link is detected.

`workflow-verify-local.ps1` creates a disposable PostgreSQL 17.11 on loopback, valid and
invalid CAs and random in-memory credentials, runs the full JDK 21 `test build`, then
removes the fixtures. It needs Docker, JDK 21 on PATH and OpenSSL (included in Git for
Windows). The script requires all nine Workflow integration suites to run with no
FAIL/SKIP, and it does not accept cloud endpoints. See `backend/README.md` for running a
local database that keeps its data and for booting the application from source.

Default Supabase flow for Issue #25: use the Direct Connection, the existing `postgres`
account, and `DB_*`/`PGSSLROOTCERT` from a secret environment; first run
`workflow-read-only-preflight.ps1` to check the connection read-only with JDBC
`verify-full`. Cloud migrations and smoke runs need a separate write approval and must not
be run in the connection step.

`workflow-stage-1a.ps1`, `workflow-stage-1b-1-readonly-audit.ps1` and
`workflow-provisioning-local-test.ps1` are historical or optional hardening tools, not
default setup steps. Keep the two existing custom roles at `NOLOGIN`.
The runtime-privilege, SECURITY DEFINER and event-trigger audit launchers are also
optional review tools; the guards in the adapter and migrations, and the integration
tests, stay in place.
The list of files to keep or that may be dropped from the PR is in
[`issue-25-readiness.md`](https://github.com/tricore-opentrix/opentrix/blob/2b4989054c99821ca1347d15da4600af4f9ce4cb/docs/evidence/issue-25-readiness.md).

`workflowDevelopmentSmoke` is a separate backend task. It requires the exact argument and
development opt-in, a fixed schema, the postgres account, a Direct `verify-full`
connection, and a separate approval for write commands. The production runner does not
enable this mode through environment or profile. The local fixtures check the development
path and the production regression; see the preflight and cloud-approval commands in
`backend/README.md`.

`workflow-schema-bootstrap.ps1 -ExecuteApprovedBootstrap -CaCertificate <CA file>`
only executes a CREATE of an empty schema that the owner has approved, with a conditional
commit and a fresh read-only audit. It does not ask for approval again; the password comes
through a secure environment or a hidden prompt. If the configuration is wrong or the
precheck fails, it stops and does not fix or clean up on its own. Do not use this launcher
for Flyway or for write smoke runs.

The schema bootstrap is complete according to the owner report (COMMITTED_PASS,
POSTCOMMIT_AUDIT=PASS, BOOTSTRAP_EXIT=0): do not run workflow-schema-bootstrap.ps1 or
CREATE SCHEMA again. The owner approved the pinned V3/V4 separately; see the
inventory, precheck, postcheck and recovery sections in the Issue #25 plan. Do not run
smoke in the same batch when only the migration is approved.

`workflow-approved-migrations.ps1 -ExecuteApprovedMigrations` is a single-purpose launcher
for that approval: fixed Direct endpoint and project, WARP IPv6, JDK 21, `verify-full`,
a secure password prompt, fail-closed prechecks and a fresh read-only audit.
No bootstrap, smoke, role changes, recovery or retry. Codex has not run the cloud step
because credentials and the CA were not available. A missing child report after handoff
is always COMMIT_UNKNOWN.

The owner reported V3/V4 COMMITTED_PASS, with checksum, inventory, seed and post-commit
audit PASS and MIGRATIONS_EXIT=0. Do not run the bootstrap or the migrations launcher again.
The owner accepted the cloud smoke as COMMITTED_PASS, run-id cloud-20261015-01, with
precheck, postcheck and fresh-JVM PASS, 2 instances / 4 history rows, exit 0.
Do not run the smoke again and do not delete the test data. The historical evidence and
plan are in the section "Cloud smoke after migrations" of `docs/evidence/issue-25-readiness.md`.
`workflow-approved-smoke.ps1` only allows `-ExecuteApprovedSmoke` after approval, or a
read-only `-AuditOnly` to reconcile after a failure. The run-id is fixed in the launcher;
the password always comes through a hidden prompt and is never accepted as a parameter or
written to a file.
