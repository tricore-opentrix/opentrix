<!--
SPDX-FileCopyrightText: NOASSERTION
SPDX-License-Identifier: Apache-2.0
-->

# R27B Step 02: S02-01 through S02-04 evidence closeout

**Decision boundary:** `DATA_AUDIT_PASS / EVIDENCE_READY_FOR_REVIEW / ATTRIBUTION_PENDING / RIGHTS_PENDING`. This is a documentation evidence package, not an accepted contributor-rights conclusion, legal clearance, nine-package scope change, Issue #138 closure or release approval.

**Repository:** `tricore-opentrix/opentrix`. **Frozen source:** `187dbd2ea6935966f5c4cceb95ad9c3c53708a2e`. **Historical integration:** [`44283466f1747d55ed39e782d0600e8d09a28427`](https://github.com/tricore-opentrix/opentrix/commit/44283466f1747d55ed39e782d0600e8d09a28427). **Parent inventory:** [Draft PR #164](https://github.com/tricore-opentrix/opentrix/pull/164), branch `docs/r27b-step01-canonical-inventory`, verified HEAD `481ef9e95d1891bd15deeb5cfea384b82de88b43`. This Step 02 branch starts at that commit and is intended as a **stacked Draft PR against the PR #164 branch**, while #164 remains open and unmerged. Comparing Step 02 directly to `main` would also show the Step 01 inventory and is not the intended review scope.

## Evidence sequence and immutable comparison points

| Step | Local evidence | Bounded result |
| --- | --- | --- |
| S02-01 | [Technical report](s02-01-contributor-reviewer-matrix.md) and [164-row source/hunk matrix](s02-01-contributor-portion-reviewer-matrix.csv) | `44283466` changed 126 paths; 164 hunk records cover Backend, Frontend, Portal BFF, Scripts, Docs and CHANGELOG. At the frozen SHA, 124 paths have blobs and two historical controllers are absent. Git text alignment is not legal authorship. |
| S02-02 | [Question report](s02-02-attribution-clarification-report.md), preserved [168-row original question CSV](s02-02-question-register.csv), and [Yến evidence summary](s02-02-yen-contributor-attribution-draft.md) | Two CHANGELOG hunk keys produce six contributor-specific questions. The original CSV remains untouched despite its character defects. The summary retains its historical filename but now points to Yến's published declaration. |
| S02-03 | [Character-audit report](s02-03-evidence-reconciliation.md) and [604-cell audit](s02-03-csv-character-audit.csv) | Classified 1,054 replacement `?` characters and 276 legitimate question marks. Exact old CSV values and row/column positions are retained. |
| S02-04 owner-audited remediation | [614-cell candidate](s02-04-question-register-candidate.csv), [614-cell change ledger](s02-04-question-register-change-ledger.csv), and [controlled-remediation report](s02-04-controlled-remediation.md) | Original-to-candidate repair preserved 168 IDs, 164 hunk keys, 276 legitimate question marks, all `PENDING` rights and the CHANGELOG conflict. Owner acceptance audit covered this exact candidate only. |
| S02-04 post-publication closeout | [168-row closeout candidate](s02-04-question-register-closeout.csv) and [16-cell post-audit delta](s02-04-post-audit-declaration-delta.csv) | A separate, fresh delta links Yến's published self-declaration into all six CHANGELOG question rows. The 614-cell candidate and ledger remain byte-for-byte historical evidence; this 16-cell delta requires its own review. |

The original question CSV SHA-256 is `c43f441fccf602c18986f76225e34d22d26c6a4df83a8237a353279423458ac4`. The owner-audited 614-cell candidate SHA-256 is `78aa6bbdb8cf967963ff0ae6812870319f9da1ad7a45cf4e12b1cd6a42f4682c`. The post-publication closeout candidate SHA-256 is `703ba3f87f78a521c9c18aae68227e37bf4e01046a0652dc836b92a53629b662`. The closeout candidate is the proposed working register; neither earlier CSV is overwritten.

## Contributor declarations and unresolved attribution

- [Yến's personally confirmed, posted self-declaration](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6736379070) applies separately to CHANGELOG frozen lines 52–55 and 61–63: exact participation, final-wording review and selection/manual editing are `NOT_RECALLED`; prompt/draft availability is `UNKNOWN`; `SELF_DECLARED_NO_INPUT` concerns only inputs she recalls not supplying to AI for these two passages. Her [older declaration](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6708631841) remains historical context. This self-report is not independent provenance verification or proof of no external influence.
- [Bảo's own clarification](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6734494167) reports AI prompting and content selection for all seven lines, no claim of hand-writing, manual final editing `NOT_RECALLED` and no available prompt/draft. He is not independent for rights review of these passages.
- [Ánh's clarification](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6734448495) reports an AI request for the four HTTP 404 lines, related CREATE code review, final-wording acceptance and review/edit activity without exact edit mapping. Her later [availability update](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6734763062) records `PROMPT_NOT_RECOVERED / ORIGINAL_TRANSCRIPT_NOT_VERIFIED`; it does not establish a separate AI request for the three CREATE prose lines.

All seven CHANGELOG lines survive in frozen blob `206411194805fc40c4ca544fd08e156e693cdd5c`. This is technical content correspondence, not an allocation of expressive authorship. The two portions retain **`REVIEWER_CONFLICT — REROUTING_REQUIRED`**. No internal person is certified independent for their source-rights disposition; route to a documented noncontributor or an external reviewer if exact-portion independence cannot be established. Backend Group C, Frontend, Portal BFF, AI-output lineage, V5/internal reuse and third-party/NOTICE obligations remain portion-specific open evidence.

## Validation and independent review gate

The closeout candidate was **freshly** checked against the preserved original and the two separate ledgers: 168 unique question IDs, 164 historical hunk keys, six CHANGELOG question rows, 614 original-to-owner-audited changes plus exactly 16 post-audit declaration-reference edits, and 626 unique original-to-closeout changed cells. All 276 legitimate question marks remain, while path and Git blob fields, `PENDING` rights, unassigned reviewers and exact conflict strings are unchanged. UTF-8, rectangular CSV and relative Markdown links passed; 12 distinct Issue-comment references in the Step 02 evidence directory resolved against Issue #138. SPDX/REUSE and Git whitespace results are recorded at the exact local package before commit. The prior owner acceptance audit did **not** constitute verification of the new 16 cells.

Scoped review requested after publication of the Draft PR:

1. **Bảo:** reproduce Git path/blob and archive consistency, 164/168 coverage and the two-ledger lineage. He may review documentation accuracy, but cannot independently clear rights for CHANGELOG content he reports prompting/selecting or any other substantive portion of his own.
2. **Ánh:** review Frontend/Portal/Data contribution boundaries, asset and upstream-provenance questions, the 16-cell Yến-reference delta and reviewer routing. She may review documentation accuracy, but cannot clear rights for content she substantively directed or edited.
3. **Yến and an eligible noncontributor:** verify the posted self-declaration is represented faithfully and establish a source-rights reviewer by exact expressive portion. If no eligible internal reviewer is established, seek an external reviewer. Self-declaration, technical verification, documentation review and rights disposition are separate decisions.

**Current limitations:** `ATTRIBUTION_PENDING / RIGHTS_PENDING`. The canonical 357-row Rights Register is unchanged, Issue #138 remains tracking only, and R24/R39 publication gates remain blocked pending their own acceptance. No merge, public release or source-rights clearance follows from this evidence package.
