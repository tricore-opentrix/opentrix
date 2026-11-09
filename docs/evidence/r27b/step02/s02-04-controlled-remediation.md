<!--
SPDX-FileCopyrightText: NOASSERTION
SPDX-License-Identifier: Apache-2.0
-->

# R27B Step 02 / S02-04: controlled question-register remediation

**Post-owner-audit closeout:** The owner-audited [614-cell candidate](s02-04-question-register-candidate.csv) and its [change ledger](s02-04-question-register-change-ledger.csv) remain byte-for-byte historical evidence. After [Yến posted her confirmed self-declaration](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6736379070), a [closeout candidate](s02-04-question-register-closeout.csv) and separate [16-cell delta ledger](s02-04-post-audit-declaration-delta.csv) were prepared. The prior owner audit did **not** validate these 16 later edits. See the [Step 02 closeout report](s02-04-step02-closeout.md) for their fresh validation and remaining reviewer requirements. The original question register is still preserved and rights remain `PENDING`.

**Decision boundary:** candidate evidence correction for owner review. No contributor declaration is posted by this report, no reviewer is certified independent, and no source-rights disposition is upgraded. The original [S02-02 question register](s02-02-question-register.csv) is immutable comparison evidence for this pass. Its SHA-256 is `c43f441fccf602c18986f76225e34d22d26c6a4df83a8237a353279423458ac4`.

**Repository:** `tricore-opentrix/opentrix`; **branch:** `docs/r27b-step02-s02-01-matrix`; **starting HEAD:** `481ef9e95d1891bd15deeb5cfea384b82de88b43`; **historical commit:** [`44283466f1747d55ed39e782d0600e8d09a28427`](https://github.com/tricore-opentrix/opentrix/commit/44283466f1747d55ed39e782d0600e8d09a28427); **frozen source:** `187dbd2ea6935966f5c4cceb95ad9c3c53708a2e`.

## Inputs and output files

The [S02-03 character audit](s02-03-csv-character-audit.csv) and [reconciliation report](s02-03-evidence-reconciliation.md) define the repair scope. The [S02-01 matrix](s02-01-contributor-portion-reviewer-matrix.csv) supplies original hunk, blob and formal conflict values. The [candidate repaired CSV](s02-04-question-register-candidate.csv) has the original 23-column schema, 168 ordered question IDs and 164 source-hunk keys; its SHA-256 after preparation is `78aa6bbdb8cf967963ff0ae6812870319f9da1ad7a45cf4e12b1cd6a42f4682c`. The [cell change ledger](s02-04-question-register-change-ledger.csv) records **every changed cell**, its full old/new value, original one-based positions of replacement and legitimate question marks, method, justification and source evidence. Each new CSV has its own REUSE license sidecar.

| Measure | Original | Candidate | Result |
| --- | ---: | ---: | --- |
| Question rows / question IDs | 168 / 168 | 168 / 168 | Order and IDs retained. |
| CSV columns | 23 | 23 | Header and column order retained. |
| Historical hunk keys | 164 | 164 | Two CHANGELOG keys remain three questions each. |
| Literal `?` in question fields | 490 | 276 | 214 replacement marks removed; all 276 genuine interrogative marks retained. |
| Literal `?` across all fields | 1,330 | 276 | All 1,054 audit-classified replacement marks addressed. |
| Changed cells | 0 | 614 | 590 audited corrupt cells repaired; 24 additional declaration-reconciliation cells changed. |
| Rights status | 168 `PENDING` | 168 `PENDING` | No clearance. |
| Assigned independent reviewer | 0 | 0 | All routes remain `UNASSIGNED`; both CHANGELOG hunks retain conflict. |

The character repairs are bounded by the audit's **820 name marks, six formal-conflict separator marks and 228 punctuation marks**. Names Yến, Bảo and Ánh were restored from their [attributable declarations](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6708631841), [Bảo's latest CHANGELOG account](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6734494167) and [Ánh's latest CHANGELOG account](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6734448495). The six `REVIEWER_CONFLICT — REROUTING_REQUIRED` values were restored from the [S02-01 matrix](s02-01-contributor-portion-reviewer-matrix.csv), not inferred from a visual glyph. These are `EXACT_CHARACTER_RECOVERY` entries in the ledger.

The original glyph for **168 `UNASSIGNED ? document...` separators** and **60 possessives** was not independently retained. The candidate deliberately rewrites them as `UNASSIGNED; document...`, `the requirements and error direction reported by Ánh`, or `The creative role of Yến`. The ledger labels these `SEMANTIC_REWRITE`, including mixed cells where a contributor name was also recovered. These rewrites leave the reviewer unassigned, the questions intact and the factual conditions unchanged. They do **not** claim exact recovery of lost punctuation.

## CHANGELOG declaration reconciliation

The six question rows remain `S02-02-Q001` through `Q006` and cover frozen CHANGELOG lines 52–55 and 61–63 separately. The [Bảo clarification](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6734494167) now supports rows Q002/Q005: he reports AI prompting and content selection for all seven lines, does not claim hand-writing, has no prompt/draft available and leaves manual final editing `NOT_RECALLED`. He cannot independently review these portions.

The [Ánh clarification](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6734448495) supports Q003: she requested AI to write or modify the four HTTP 404 lines. For Q006 she confirms related CREATE **code** review, while a distinct AI request for the three CHANGELOG prose lines is `UNKNOWN`; final-wording acceptance and general review/edit activity do not identify exact edits. Her later [evidence-availability update](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6734763062) narrows prompt availability to `PROMPT_NOT_RECOVERED / ORIGINAL_TRANSCRIPT_NOT_VERIFIED`. The candidate cites both comments and does not treat a reconstructed prompt as historical evidence.

Rows Q001/Q004 retain [Yến's posted commit-specific `NOT_RECALLED`](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6708631841). At the S02-04 owner-audit snapshot, the user-supplied answers were recorded only in the [local Yến draft](s02-02-yen-contributor-attribution-draft.md), then labelled **`DRAFT — REQUIRES YẾN'S FINAL CONFIRMATION — NOT POSTED`**. That historical pre-publication status was later superseded by [Yến's personally confirmed, published self-declaration](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6736379070); publication does not independently verify attribution. For both passages, participation, CHANGELOG review and final-wording selection/editing remain `NOT_RECALLED`; prompt/draft availability is `UNKNOWN`. Her recollection that she supplied no AI inputs for these two passages is labelled `SELF_DECLARED_NO_INPUT`, **not independently verified**. That scoped recollection does not establish an absence of third-party influence on AI output or change participation to `NO`.

All six CHANGELOG rows retain `REVIEWER_CONFLICT — REROUTING_REQUIRED`, `PENDING` rights and an unassigned reviewer. Bảo is a reported substantive participant; Ánh is a participant for the HTTP 404 portion and her exact prose activity for CREATE remains unresolved; Yến's own independence remains unestablished. Technical content verification is separate from an independent source-rights decision.

## Validation and remaining gate

| Check executed locally | Result |
| --- | --- |
| Python CSV/ledger audit: 168 IDs, 164 hunk keys, six CHANGELOG rows, 614 exact old/new cell matches, 276 question marks retained per cell, no other `?`, all rights `PENDING`, reviewer unassigned | PASS, exit 0. |
| Git tree comparison at `44283466f1747d55ed39e782d0600e8d09a28427` and `187dbd2ea6935966f5c4cceb95ad9c3c53708a2e`: 126 historical paths, 124 frozen blobs, two absent paths; immutable candidate path/SHA fields | PASS, exit 0. |
| Change-ledger one-based character positions and S02-03 audit counts | PASS, exit 0. |
| Contributor Issue-comment links appearing in the candidate: eight distinct comment IDs checked against Issue #138 | PASS, 8/8 resolved through the GitHub connector. |
| UTF-8, rectangular CSV, local Markdown links and whitespace scan over new/updated files | PASS, exit 0. |
| `python -m reuse lint-file` over all 15 local Step 02 files | PASS, exit 0. |
| `git diff --check` | PASS, exit 0; the separate whitespace scan covers files still untracked by Git. |

The [seven surviving CHANGELOG lines](https://github.com/tricore-opentrix/opentrix/blob/187dbd2ea6935966f5c4cceb95ad9c3c53708a2e/CHANGELOG.md) remain a technical source anchor only. The corrected candidate has **zero unresolved CSV corruption cells**; attribution and reviewer independence remain open.

The prior owner audit checked the candidate and ledger together, particularly the 228 semantic rewrites and the six declaration rows. Yến subsequently confirmed and posted her bounded answers at the Issue comment linked above; the new references are isolated in the separate 16-cell delta. The original CSV remains immutable comparison evidence. This remediation record does not overwrite it, change the canonical Rights Register or mark R27B complete.
