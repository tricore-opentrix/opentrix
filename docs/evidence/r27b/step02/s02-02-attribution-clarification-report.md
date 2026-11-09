<!--
SPDX-FileCopyrightText: NOASSERTION
SPDX-License-Identifier: Apache-2.0
-->

# R27B Step 02 / S02-02: contribution and reviewer clarification requests

**Closeout evidence update:** These questions were prepared before the later attributable statements. [Yến's posted self-declaration](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6736379070) retains `NOT_RECALLED` for her exact CHANGELOG participation, final-wording review and selection/editing; prompt/draft availability is `UNKNOWN`, and `SELF_DECLARED_NO_INPUT` is limited to inputs she supplied for the two passages. [Bảo](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6734494167) now reports AI prompting and content selection for all seven lines. [Ánh](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6734448495) reports AI direction for the HTTP 404 passage and related CREATE code review; her [later update](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6734763062) records `PROMPT_NOT_RECOVERED / ORIGINAL_TRANSCRIPT_NOT_VERIFIED`. The preserved [original register](s02-02-question-register.csv), audited [repair candidate](s02-04-question-register-candidate.csv), and [post-publication closeout candidate](s02-04-question-register-closeout.csv) are distinct revisions; the [delta ledger](s02-04-post-audit-declaration-delta.csv) records the last step. All rights remain `PENDING` and both CHANGELOG hunks retain `REVIEWER_CONFLICT — REROUTING_REQUIRED`.

**Status:** prepared questions, not contributor answers or an independent rights decision. The [question register](s02-02-question-register.csv) covers every row of the unchanged [S02-01 matrix](s02-01-contributor-portion-reviewer-matrix.csv). All rights dispositions remain `PENDING`; the canonical Rights Register retains its historical `RIGHTS_PENDING` values. `UNKNOWN` and `NOT_RECALLED` are unresolved, not negative answers.

**Repository:** `tricore-opentrix/opentrix`; **frozen source:** `187dbd2ea6935966f5c4cceb95ad9c3c53708a2e`; **historical integration commit:** [`44283466f1747d55ed39e782d0600e8d09a28427`](https://github.com/tricore-opentrix/opentrix/commit/44283466f1747d55ed39e782d0600e8d09a28427). This is a preparation pass on `docs/r27b-step02-s02-01-matrix`, based on the [nine-package inventory at `481ef9e95d1891bd15deeb5cfea384b82de88b43`](https://github.com/tricore-opentrix/opentrix/pull/164). No GitHub question has been posted.

## Evidence and method

The starting register contains 164 historical hunk records across 126 paths: 60 Backend, 80 Frontend, 14 Portal BFF, six Scripts, two Docs and two CHANGELOG hunks. The question register retains one row per starting hunk except that each CHANGELOG hunk has a separate question for Yến, Bảo and Ánh, resulting in 168 question rows and exactly 164 covered original `(source_path, historical_hunk)` keys. It preserves each original path, frozen blob, historical hunk, surviving-line range and technical survival status. A byte match or exact-line alignment is technical evidence, not proof of creative contribution, originality, copyright ownership or authority to redistribute. Two deleted legacy controller paths have no frozen blob and are marked historical-only; they are not presented as surviving source.

The direct declarations are [Yến's consolidated answers](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6708631841), [Yến's earlier S6-13 statement](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6706970135), [Bảo's consolidated answers](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6707960117), and [Ánh's consolidated answers](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6708767215). [Ánh's S6-13 technical review](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6707061030) verifies a commit map with scope limits; it does not establish contributor allocation or rights for these seven lines. [PR #154](https://github.com/tricore-opentrix/opentrix/pull/154) is a technical crosswalk. [PR #155 at `47ac885fcdf0cd09453aca1413753afaa47828cc`](https://github.com/tricore-opentrix/opentrix/pull/155) identifies 13 Group C paths introduced by `44283466` plus two earlier placeholders. [PR #161](https://github.com/tricore-opentrix/opentrix/pull/161) supplies license-evidence navigation, not clearance. Declaration claims are attributed to the named contributor, never treated as independent review.

## Exact CHANGELOG survival

Git comparison of the parent and `44283466` CHANGELOG blobs yields historical insertions `parent:23+0; commit:23+4` and `parent:28+0; commit:32+3`. The historical blob is `80c153460200491313907223e04ddfd70c3160e7`; the frozen blob is `206411194805fc40c4ca544fd08e156e693cdd5c`. Each introduced line occurs exactly at the frozen position shown below:

| Historical lines | Frozen lines | Topic |
| --- | --- | --- |
| 23–26 | 52–55 | Helpdesk versus Generic Workflow error codes. |
| 32–34 | 61–63 | CREATE authorities and uncertain commit response. |

Exact surviving text, in frozen line order:

```text
- The Helpdesk HTTP API uses a scoped HTTP 404 / `NOT_FOUND` response for
  hidden or missing resources; the Generic Workflow HTTP API retains its
  pre-existing distinct `DEFINITION_NOT_FOUND` / `INSTANCE_NOT_FOUND` public
  codes and messages. Generic contract evolution is tracked in Issue #105.
- Helpdesk CREATE rejects missing exact technical authorities before protected
  definition/binding lookups; uncertain Workflow commits return HTTP 503 with
  `COMMIT_OUTCOME_UNKNOWN` and must not be retried automatically.
```

Line correspondence does not prove uninterrupted textual ancestry or who composed, prompted, edited or selected these words. Ánh reports AI direction for HTTP 404, related CREATE code review, final-wording acceptance and unrecovered original prompt; exact prose-edit allocation remains unknown. Yến's posted commit-specific answer remains `NOT_RECALLED`; her scoped `SELF_DECLARED_NO_INPUT` is not independently verified. Bảo now reports AI prompting and content selection for all seven lines; his earlier `NOT_RECALLED` account remains historical context. Git metadata and later commit associations do not allocate exact human/AI edits. The reviewer route remains **`REVIEWER_CONFLICT — REROUTING_REQUIRED`** for both hunks.

## Clarification request for Yến

1. For **each** of frozen CHANGELOG lines 52–55 and 61–63, what requirements, draft wording, prompts, revisions, human edits, content selection, review or testing did you personally perform? Identify what you can substantiate, and answer `NOT_RECALLED` for the rest. Were any facts or words supplied by Ánh, Bảo or another person?
2. Your [S6-13 statement](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6706970135) describes prompt/review work, while your [commit-specific clarification](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6708631841) says `NOT_RECALLED`. Can you connect any surviving line to a recovered draft, prompt or review record, or confirm that the allocation remains unknown? What, if anything, did you do in subsequent CHANGELOG revisions that affected the seven lines themselves?
3. For the 13 `44283466` Group C paths identified by [#155](https://github.com/tricore-opentrix/opentrix/pull/155), and for the other Backend, Portal BFF, Scripts and Docs hunks in the register, distinguish your prompt, direct edit, selection, integration, testing and review roles by exact portion. Your account association and SPDX updates alone cannot allocate underlying content. Identify any V5/internal or external input you supplied, or preserve `UNKNOWN`/`NOT_RECALLED`.
4. As coordinator, obtain exact-portion participation statements from all three people and identify a reviewer with documented noncontribution for each portion. If no such person is established for CHANGELOG, seek an outside reviewer. Do not self-review your own substantive portion.

## Clarification request for Bảo

1. Bảo's [later personal clarification](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6734494167) answers the prompt/selection question for all seven lines. Manual final editing remains `NOT_RECALLED`; his historical [consolidated statement](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6707960117) is retained. Distinguish later CHANGELOG edits from these surviving insertions.
2. For each Backend, Group C, Portal BFF, Scripts and Docs hunk in the question register, identify any prompt, AI-generated output you directed, manual edit, substantive selection or review you performed. Clarify whether any project file or V5 material was reused, if known. The prior Q5/Q6 answers are `NOT_RECALLED`; do not replace them with a blanket no.
3. Identify any exact portion for which you can document nonparticipation before being considered as an independent reviewer. Your Frontend nonparticipation claim explicitly excludes `44283466`; it is not an automatic reviewer route for these 80 Frontend hunks.

## Clarification request for Ánh

1. Ánh's [later declaration](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6734448495) confirms AI direction for the HTTP 404 passage, related CREATE code review and final-wording acceptance, without exact edit allocation. Her [availability update](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6734763062) says the historical prompt/draft was not recovered. If a genuine historical record becomes available later, compare it with the seven lines; do not reconstruct one.
2. For the 80 Frontend hunks, distinguish requirements, AI prompt preparation, AI execution, selected alternatives, direct edits, tests and review by exact portion. Identify font, icon, template or package input when known. The favicon process statement is a separate path and does not prove upstream SVG/NOTICE provenance.
3. For the 14 Portal BFF hunks, confirm the declared **review-only** scope at the exact portions and identify any substantive change request or supplied wording, if any. Do not turn review into code authorship; identify who actually prompted, created, edited or selected BFF code if known, otherwise say `UNKNOWN`.
4. For Backend/Group C hunks, identify the portions, if any, that arose from your requirements or AI-directed error corrections. Your product-level direction does not automatically allocate implementation authorship. Identify any exact portion you did not substantively contribute to before independent review is considered.

## Priority routing and open blockers

| Priority | Portions | Current claim and gap | Independent review route |
| --- | --- | --- | --- |
| P0 | CHANGELOG 52–55, 61–63 | Bảo reports AI prompting/selection for all seven; Ánh reports AI direction for HTTP 404 and CREATE code review; Yến's exact actions remain `NOT_RECALLED`. Exact prose edits and AI-output origin remain `UNKNOWN`. | Unassigned. `REVIEWER_CONFLICT — REROUTING_REQUIRED`; Yến coordinates a documented noncontributor or an outside reviewer. |
| P1 | 14 Portal BFF hunks | Ánh says review-only; creator/prompt/editor and Yến/Bảo roles unresolved. One build.gradle line lacks exact frozen alignment. | Unassigned pending exact participation map, including whether Ánh's review supplied substantive changes. |
| P1 | 13 `44283466` Group C paths | #155 verifies technical survival, while Yến's creative role is `NOT_RECALLED`; V5 lineage remains open for SQL. | Unassigned pending all participants' portion statements and independent reviewer noncontribution. |
| P1 | 80 Frontend hunks | Ánh's AI-assisted direction is disclosed, but exact per-hunk role and external inputs are `UNKNOWN`; Yến disclaims create/prompt/edit, and Bảo's general Frontend nonparticipation excludes this commit. | Unassigned pending exact-portion check; an outside reviewer if no eligible internal reviewer is documented. |
| P2 | Other Backend, Scripts, Docs and historical-only controllers | Mixed roles and inputs unresolved; two controllers have no surviving frozen blob. | Unassigned pending portion and survival-specific triage. |

Technical verification can establish that text appears at a pinned blob and line. A source-rights disposition requires separate contributor, upstream and independent-review evidence. The seven CHANGELOG lines, all other unresolved rows, AI-output originality, V5 reuse and third-party NOTICE duties remain open. The questions were prepared before the later contributor replies linked above; those replies do not establish independent rights clearance.
