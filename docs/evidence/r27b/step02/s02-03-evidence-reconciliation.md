<!--
SPDX-FileCopyrightText: NOASSERTION
SPDX-License-Identifier: Apache-2.0
-->

# R27B Step 02 / S02-03: declaration and CSV evidence reconciliation

**Later closeout update:** [Yến's six-answer self-declaration](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6736379070) is now posted. The [S02-04 closeout report](s02-04-step02-closeout.md) and [post-publication candidate](s02-04-question-register-closeout.csv) supersede this report's earlier publication-status snapshot. This S02-03 character audit and the original CSV remain unchanged comparison evidence; `RIGHTS_PENDING` and the CHANGELOG reviewer conflict remain open.

**Purpose:** an independent-review preparation record. It neither amends a contributor's declaration nor changes source rights. The original [S02-02 question register](s02-02-question-register.csv) is preserved unchanged; its SHA-256 at this audit is `c43f441fccf602c18986f76225e34d22d26c6a4df83a8237a353279423458ac4`.

**Repository:** `tricore-opentrix/opentrix`; **worktree branch:** `docs/r27b-step02-s02-01-matrix` at `481ef9e95d1891bd15deeb5cfea384b82de88b43`; **frozen source:** `187dbd2ea6935966f5c4cceb95ad9c3c53708a2e`; **investigated commit:** [`44283466f1747d55ed39e782d0600e8d09a28427`](https://github.com/tricore-opentrix/opentrix/commit/44283466f1747d55ed39e782d0600e8d09a28427). The source matrix has 164 historical hunk rows. The S02-02 register has 168 question rows, because the two CHANGELOG hunks each have separate questions for Yến, Bảo and Ánh.

Preflight found **seven** pre-existing, uncommitted Step 02 files: the S02-01 Markdown/CSV/CSV license, the S02-02 report/CSV/CSV license, and the later Yến personal-confirmation draft. They remain untouched. This pass adds only this report, the cell audit and its CSV license sidecar.

## CSV character audit

The [cell audit](s02-03-csv-character-audit.csv) provides **the exact original CSV row number (header = row 1), column name and full current value for every cell containing `?`**, including cells with legitimate question punctuation. It has 604 data rows: 590 cells contain at least one apparent replacement character and 14 contain only legitimate question punctuation. Across these cells, there are 1,330 literal `?` bytes: **1,054 apparent replacements** and **276 legitimate interrogative marks**. This is a content defect in otherwise decodable UTF-8, not a failure to decode the CSV. No character was changed in the source register.

| Column in `s02-02-question-register.csv` | Affected CSV rows / cells | Replacement marks | Legitimate question marks | Evidence and recovery boundary |
| --- | ---: | ---: | ---: | --- |
| `person_required_to_answer` | 2–169 / 168 | 492 | 0 | `Y?n`, `B?o`, `?nh` and combinations: names recoverable from the attributable declarations. |
| `human_edit_or_content_selection` | 70–163 / 94 | 174 | 0 | Frontend/Portal names recoverable from the declarations and [S02-01 matrix](s02-01-contributor-portion-reviewer-matrix.csv). |
| `remaining_factual_question` | 8–163 / 154 replacement-bearing cells; 14 other cells have only real questions | 214 | 276 | Names are recoverable; 60 possessive punctuation glyphs are not independently retained. Preserve real question marks. |
| `proposed_independent_reviewer` | 2–169 / 168 | 168 | 0 | `UNASSIGNED ? document...` has an unrecoverable original separator glyph. A future reviewed revision can deliberately rewrite the separator in plain ASCII. |
| `reviewer_conflict_status` | 2–7 / 6 | 6 | 0 | `REVIEWER_CONFLICT ? REROUTING_REQUIRED` is recoverable from the exact [S02-01 conflict value](s02-01-contributor-portion-reviewer-matrix.csv) and the independently documented routing rule. |

The exact range `8–163` above is a bounding range, **not** a claim that every row in it is affected; the audit CSV identifies each of the 154 cells. The five column counts total 590 corrupted cells. Of the 1,054 apparent replacement marks, **820 are in contributor names**, **six are in the formally defined conflict string**, and **228 are punctuation whose original glyph is not independently recoverable** (168 separators and 60 possessive marks). Names and the conflict string can be restored from cited evidence; punctuation should be rewritten explicitly, not represented as a recovered original character. All 276 interrogative marks must be left intact.

### Correction plan, without modifying the original

1. Review every `REPLACEMENT_MARKS_ONLY` or `REPLACEMENT_MARKS_AND_LEGITIMATE_QUESTION_PUNCTUATION` row in the audit. Use the [Yến](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6708631841), [Bảo](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6734494167) and [Ánh](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6734448495) declarations, plus the S02-01 source row, to restore **names**; preserve row IDs, hunk keys, paths and blob SHAs.
2. Restore the six conflict-field values only by comparing the S02-01 exact string `REVIEWER_CONFLICT — REROUTING_REQUIRED`; verify that the same two CHANGELOG hunks are involved. Rewrite other separators and possessives in deliberate, unambiguous ASCII wording after review; do not claim to know their original glyph.
3. Preserve the 276 genuine question marks. Update the six CHANGELOG question rows to cite Bảo's and Ánh's **newer** attributable clarifications while preserving Yến's `NOT_RECALLED` and each earlier statement as historical evidence. This is a separately reviewable factual amendment, not a source-rights upgrade.
4. Only after line-by-line approval, create a corrected revision with a before/after cell log and rerun UTF-8, CSV, Git blob, REUSE and reviewer-conflict checks. The original CSV remains untouched in this pass.

## Contributor declaration reconciliation

| Portion | Bảo's current attributable statement | Ánh's current attributable statement | Yến's attributable statement and decision boundary |
| --- | --- | --- | --- |
| A — CHANGELOG frozen lines 52–55, HTTP 404 / `NOT_FOUND` | [Prompted AI and selected content for all seven lines](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6734494167); manual final edit `NOT_RECALLED`; prompt/draft unavailable to him. | [Requested AI to write or modify this four-line passage](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6734448495); reports final-wording acceptance and review/edit activity, without per-line allocation or a submitted draft. | [Commit-specific role `NOT_RECALLED`](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6708631841). Her [earlier S6-13 method statement](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6706970135) is broader and cannot be converted into a four-line participation claim. |
| B — CHANGELOG frozen lines 61–63, CREATE / `COMMIT_OUTCOME_UNKNOWN` | Same reported prompting and selection of all seven lines; no available prompt/draft; manual final edit `NOT_RECALLED`. | Confirms review of related **code**; has not verified a distinct AI request for these three CHANGELOG lines. Reports final-wording acceptance and review/edit generally; exact prose edits remain `UNKNOWN`. | Same commit-specific `NOT_RECALLED`, independently of Portion A. Technical code review and Git association do not answer whether she worked on this release-note prose. |

These statements can coexist; no exclusive authorship is inferred. No prompt transcript has been submitted for this reconciliation. External inputs and AI-output lineage remain `UNKNOWN / NOT_VERIFIED`. All rights remain `PENDING` in the matrices and `RIGHTS_PENDING` in the canonical register. The new statements make the existing six CHANGELOG question-row claims **stale**, but this report does not overwrite them.

At the S02-03 audit snapshot, the [Yến personal-confirmation draft](s02-02-yen-contributor-attribution-draft.md) was expressly labelled **`DRAFT — REQUIRES YẾN'S PERSONAL CONFIRMATION — NOT A POSTED DECLARATION`**. This historical pre-publication status was later superseded by [Yến's personally confirmed, published self-declaration](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6736379070), which remains a self-declaration rather than independent attribution verification. At S02-03, the draft recorded her earlier answer as `NOT_RECALLED` for both portions, attributed Bảo's and Ánh's accounts to them, and asked Yến separate questions about prompting, drafting, editing, selection, CHANGELOG review versus code review and known inputs. It contained no new first-person answer or rights consent by Yến; personal confirmation was still required before a new statement could be attributed to her.

## Independent review checklist: two separate portions

| Check | A: 52–55 | B: 61–63 |
| --- | --- | --- |
| Technical anchor | Historical `parent:23+0; commit:23+4`, frozen blob `206411194805fc40c4ca544fd08e156e693cdd5c`. | Historical `parent:28+0; commit:32+3`, same frozen blob. |
| Contributor facts to verify | Bảo's all-seven prompt/selection; Ánh's specific AI request; Yến's own exact actions, if personally recalled. | Bảo's all-seven prompt/selection; distinguish Ánh's code review from prose direction/edit; Yến's separate exact actions. |
| Missing material | Ánh's possible prompt/draft has not been submitted; Bảo has none available; Yến prompt/edit/selection/review record `UNKNOWN`. | Same prompt gap, with Ánh's prose-prompt question additionally unresolved. |
| Source inputs | Ask for actual project or external text supplied for this passage; preserve `UNKNOWN / NOT_VERIFIED`. | Ask independently for CREATE/Workflow source material; preserve `UNKNOWN / NOT_VERIFIED`. |
| Independent route | Bảo is a contributor; Ánh reports AI direction; Yến's independence unestablished. | Bảo is a contributor; Ánh may have selected/edited prose; Yến's independence unestablished. |
| Current status | `REVIEWER_CONFLICT — REROUTING_REQUIRED`; `PENDING`. | `REVIEWER_CONFLICT — REROUTING_REQUIRED`; `PENDING`. |

Technical reproduction of lines or Git blob identity is distinct from source-rights authorization. No reviewer within the three is certified independent here. If exact nonparticipation cannot be established, the coordinator should seek an external reviewer without naming one prematurely.

## Draft PR preparation gate

The evidence report and cell audit can be reviewed locally now. Before a Draft PR is proposed, obtain review of the cell-level repair plan, prepare a justified corrected question-register revision, reconcile the six stale CHANGELOG statements against the newer Issue comments, and obtain Yến's personal answer or retain `NOT_RECALLED`. Then rerun the full path/blob, CSV, link, REUSE and whitespace checks at the proposed head. Keep the PR Draft and retain the conflict and `PENDING` rights. This pass makes no commit, push, Issue comment or change to the canonical Rights Register.
