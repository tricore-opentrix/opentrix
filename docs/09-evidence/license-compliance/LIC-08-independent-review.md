<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# LIC-08 — Independent review procedure

Evidence group: LIC-G4.

Status: **NOT_VERIFIED**.

Evidence source: [canonical review gates](../../verification/r27/r27-independent-review-gates-187dbd2.md), [R27 vocabulary](../../verification/r27/r27-status-and-id-vocabulary.md), [PR #161](https://github.com/tricore-opentrix/opentrix/pull/161).

Applicable source SHA: `9aaff5854eb386d0602fb4575c4204d359881d73` (verified #161 integration base). These are living instructions; later generated reports name their own analyzed commit in `generation-manifest.json`. This document is not an assertion that future commits are covered.

Owner: Yến coordinates routing; reviewers provide their own scoped decisions.

Reviewer: Bảo/Ánh proposed for framework checks; actual source portions require independent noncontributors; proposed routing, no signature or approval recorded here.

Blockers: No formal review of this Phase-2 framework recorded here; #157 unresolved findings and source-rights gaps remain.

Update conditions: Any substantive change to reviewed content, source SHA, obligation, scope or reviewer participation.

## Review record requirements

Review the exact PR HEAD and source SHA named by each generated report. Inspect the generator, policy reuse, external metadata precedence, full lint failures, CSV keys/counts/determinism and input provenance. Check manual obligations independently; generator output is not a legal decision.

An actual record must identify: reviewer and review URL; reviewed SHA and path/portion; relevant group LIC-G1..G5; technical checks and exit codes; documentation/provenance/rights scope; conflicts or substantive participation; findings and disposition. Link formal GitHub reviews separately from discussion comments. Do not prefill signatures, review dates or PASS rows.

Historical approvals apply only to their stated SHAs and scope. #161 being Draft or its CI being green does not approve Phase 2. Reviews of contributor-authored portions cannot be self-approval; if all three team members substantively contributed, obtain an eligible outside reviewer.

## Proposed routing, not completed reviews

- Bảo: Git/ref isolation, R23 projection/CI, deterministic outputs, archive-source boundary.
- Ánh: effective-metadata fixtures, unknown/portion/declaration semantics, CSV/link integrity.
- Yến: coordinate policy/NOTICE/rights review and contributor follow-up; do not approve own authored evidence or infer authority from coordination.

Independent review status for this framework: NOT_VERIFIED. No release review or rights signature is created here.
