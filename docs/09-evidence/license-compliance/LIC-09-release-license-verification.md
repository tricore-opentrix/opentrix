<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# LIC-09 — Release license verification gate

Evidence group: LIC-G5.

Status: **BLOCKED**.

Evidence source: [R24 release tooling](../../../scripts/r24-release.py), [Draft #139](https://github.com/tricore-opentrix/opentrix/pull/139), [R24 acceptance JSON](https://github.com/tricore-opentrix/opentrix/blob/2f6b8d7608214983be92db1f5ba0e4b8703885db/docs/06-deployment/r24-acceptances/v0.2.0.json), [Issue #138](https://github.com/tricore-opentrix/opentrix/issues/138).

Applicable source SHA: `9aaff5854eb386d0602fb4575c4204d359881d73` (verified #161 integration base). These are living instructions; later generated reports name their own analyzed commit in `generation-manifest.json`. This document is not an assertion that future commits are covered.

Owner: Bảo implements R24 tooling; Yến coordinates separate compliance/release acceptance.

Reviewer: Actual independent release reviewers; no signature recorded here; proposed routing, no signature or approval recorded here.

Blockers: #138 rights unresolved; #139 acceptance fields null/empty; actual upstream/NOTICE and scoped reviews incomplete.

Update conditions: A candidate SHA is frozen, source/distribution inputs change, or an actual authorized release review occurs.

## Required freeze sequence

1. Identify the real proposed release source SHA and distribution mode. A documentation HEAD is not automatically the release source.
2. Reconcile development deltas against the frozen R27 register/queue without overwriting historical evidence. Obtain direct contributor/portion evidence and genuine independent rights decisions.
3. Regenerate canonical R23 SBOMs and inventory from that exact source. Generate immutable LIC snapshots into a new `build/license-evidence/snapshots/<full-sha>` directory. Never overwrite an existing snapshot.
4. Preserve tool versions, commands, timestamps, exit codes, input/output digests and CI artifact links. Resolve metadata failures; do not replace failed output with a success label.
5. Apply existing R24 verification, upstream license/NOTICE, rights, independent review and exact-source reproducibility gates. Validate actual delivered bytes and exclusions; changes to source/packaging require a new freeze and affected reruns.
6. Populate acceptance records only from genuine evidence and authorized review. This framework does not fill #139's null fields, close #138, grant approval, or run publication.

Historical two-run archive evidence at 187dbd2 remains scoped to that source and artifact. Living reports, CI green and a PR-template checkbox cannot establish release readiness. Existing Windows R24 failures remain recorded in the #161 audit; they are not suppressed by this framework.

Current release verification: BLOCKED. No tag, release, package, container or source archive is published by these instructions or generators.
