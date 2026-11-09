<!--
SPDX-FileCopyrightText: NOASSERTION
SPDX-License-Identifier: Apache-2.0
-->

# R27B Step 02 / S02-01 ? contributor, surviving-portion and reviewer matrix

**Decision boundary:** evidence preparation only; no source-rights clearance, R27B completion, or release acceptance. All rows in the [machine-readable matrix](s02-01-contributor-portion-reviewer-matrix.csv) retain `PENDING` rights. The canonical register's legacy string remains `RIGHTS_PENDING` and was not edited.

**Repository:** `tricore-opentrix/opentrix`. **Preparation branch:** `docs/r27b-step02-s02-01-matrix`, branched from inventory PR [#164 at `481ef9e95d1891bd15deeb5cfea384b82de88b43`](https://github.com/tricore-opentrix/opentrix/pull/164). **Frozen source:** `187dbd2ea6935966f5c4cceb95ad9c3c53708a2e`. **Investigated commit:** [`44283466f1747d55ed39e782d0600e8d09a28427`](https://github.com/tricore-opentrix/opentrix/commit/44283466f1747d55ed39e782d0600e8d09a28427). This branch is separate from R27A and other Draft PR branches; this pass has no commit, push or PR.

## Evidence read and limits

- [Step 01 Markdown](../../../verification/r27/r27b-nine-package-inventory.md) and [CSV](../../../verification/r27/r27b-nine-package-inventory.csv) at #164's stated HEAD define the nine proposed navigation packages. They do not adjudicate authorship.
- Direct contributor disclosures on [Issue #138](https://github.com/tricore-opentrix/opentrix/issues/138): [Yen consolidated statement](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6708631841) and [S6-13 statement](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6706970135); [Bao consolidated statement](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6707960117); [Anh consolidated statement](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6708767215); [Anh's scoped S6-13 technical review](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6707061030). Statements posted on a contributor's behalf remain attributable only within their expressly confirmed scope.
- [#139](https://github.com/tricore-opentrix/opentrix/pull/139) source-only boundary; [#142](https://github.com/tricore-opentrix/opentrix/pull/142) historical Identity provenance; [#143](https://github.com/tricore-opentrix/opentrix/pull/143) canonical rights register, with [#151](https://github.com/tricore-opentrix/opentrix/pull/151) routing correction; [#149](https://github.com/tricore-opentrix/opentrix/pull/149) Step-6 queue, with [#152](https://github.com/tricore-opentrix/opentrix/pull/152) portion routing correction. Relevant current heads are in the Step 01 inventory; all were read as Draft evidence, not merged source.
- [#154 at `fcc146370b1c5f1dbbba0747143e9dc3b9184f23`](https://github.com/tricore-opentrix/opentrix/pull/154) reports a 126-path technical crosswalk and the same CHANGELOG frozen ranges; [#155 at `47ac885fcdf0cd09453aca1413753afaa47828cc`](https://github.com/tricore-opentrix/opentrix/pull/155) separately reconciles 13 `44283466` Group C paths plus two earlier placeholders. [#161 at `9aaff5854eb386d0602fb4575c4204d359881d73`](https://github.com/tricore-opentrix/opentrix/pull/161) supplies LIC-G1?LIC-G5 navigation, not a competing rights decision.
- The corrected [#151 register CSV](https://github.com/tricore-opentrix/opentrix/blob/146ff78f3ea0f177b5dbb712679971dbd61302e0/docs/verification/r27/r27-rights-remediation-register-187dbd2.csv) has blob `30148667c9a09c984222daf8063e748d50dc7cc1`. All 124 frozen paths in this matrix have blob SHA-1 values matching its tracked-path rows. Git metadata and a technical blob match do not prove human creative authorship or licensing authority.

## Method and result

The matrix covers **all 126 paths changed by `44283466`**: 23 Backend, 80 Frontend, 14 Portal BFF, six Scripts, two Docs and one CHANGELOG. It has **164 introduced-text hunk rows**, including one pure-deletion hunk with no added text. A hunk is a changed interval derived from ordered parent-to-commit line comparison; `parent:start+count; commit:start+count` uses one-based starts, and count zero means an insertion point. Nonblank added lines were aligned in order between the commit blob and frozen blob. `frozen_surviving_lines` records the exact aligned frozen line ranges. `ALL_EXACT_LINE_ALIGNED` means identical text is present in the frozen file; it does **not** establish uninterrupted causal ancestry, originality, or contributor identity. A later removal followed by identical reintroduction cannot be excluded by this bounded method.

| Group | Unique paths | Hunk rows | Contributor/reviewer boundary |
| --- | ---: | ---: | --- |
| Backend | 23 | 60 | Yen and Bao's exact `44283466` roles are `NOT_RECALLED`; Anh reports requirements/error-direction, not every code hunk. The 13 Group C paths have a separate content-survival check in #155, not a Yen authorship finding. |
| Frontend | 80 | 80 | Anh reports requirements and AI-directed work, with per-path roles incomplete. Yen expressly disclaims creating/prompting/editing Frontend, including this commit, but other participation and reviewer independence need exact-portion checking. |
| Portal BFF | 14 | 14 | Anh expressly reports **review-only** activity for BFF in this commit. Actual creator/prompt/editor remains unidentified; review-only is not code authorship or automatic reviewer eligibility. |
| Scripts | 6 | 6 | Yen confirms ChatGPT use for scripts/docs but not exact file actions; Bao's role is `NOT_RECALLED`, and Anh's exact portion scope is unallocated. |
| Docs | 2 | 2 | Same bounded script/doc contributor statements; no blanket attribution from commit metadata. |
| CHANGELOG | 1 | 2 | Seven exact added lines correspond at the frozen SHA; the human/AI prose contribution and independent rights reviewer remain unresolved. |

At the path level, **124 paths are present** at the frozen SHA and **two legacy controllers are absent**. Of present paths, 13 frozen blobs are byte-identical to the historical commit and 111 differ. Of the differing paths, 109 have all introduced nonblank lines aligned and two have partial alignment. At the hunk level: 13 `ALL_BYTE_IDENTICAL`, 146 `ALL_EXACT_LINE_ALIGNED`, two `PARTIAL_EXACT_LINE_ALIGNED`, two `HISTORICAL_ONLY`, and one `NO_ADDED_TEXT`. These are technical content observations, not evidence-verification PASS for source origin.

The two absent paths are `backend/src/main/java/com/tricore/dxos/request/controller/RequestController.java` and `backend/src/main/java/com/tricore/dxos/request/controller/RequestWorkflowController.java`. Git history shows removal by [`88162e9c3acbc8cad8ce7b15c2bd328226e1f545`](https://github.com/tricore-opentrix/opentrix/commit/88162e9c3acbc8cad8ce7b15c2bd328226e1f545); neither has a frozen blob or surviving portion in this candidate. Partial alignment affects four historical nonblank lines in `backend/src/test/java/com/tricore/dxos/infrastructure/workflow/HelpdeskHttpPostgresTest.java` (commit lines 147?148, 694, 788) and one in `portal-bff/build.gradle` (commit line 7). The matrix retains aligned ranges and does not count those five lines as surviving. The four Helpdesk SQL files in #155 are byte-identical; nine Group C Java/test files match their substantive historical content after later SPDX headers, consistent with that separate bounded review.

## CHANGELOG.md: exact surviving portion and unresolved contributors

Frozen blob SHA-1: `206411194805fc40c4ca544fd08e156e693cdd5c`. Historical `44283466` blob: `80c153460200491313907223e04ddfd70c3160e7`. The commit added two distinct nonblank intervals to `CHANGELOG.md`:

| Historical interval | Frozen interval | Surviving expression |
| --- | --- | --- |
| `commit:23+4` | `52?55` | Helpdesk HTTP 404/`NOT_FOUND` versus Generic Workflow `DEFINITION_NOT_FOUND` and `INSTANCE_NOT_FOUND`; Issue #105 reference. |
| `commit:32+3` | `61?63` | Missing CREATE authorities; uncertain Workflow commit returns HTTP 503/`COMMIT_OUTCOME_UNKNOWN` with no automatic retry. |

All seven lines align exactly. This also agrees with #154's technical CHANGELOG crosswalk. [Anh](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6708767215) says she asked AI to write or modify CHANGELOG, but her original prompt and allocation of these surviving words are unrecovered. [Yen](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6708631841) records her `44283466` role as `NOT_RECALLED`; her earlier [S6-13 statement](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6706970135) describes scoped AI prompting/review but does not assign exclusive authorship to these seven lines. [Bao](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6707960117) records `44283466` participation as `NOT_RECALLED` and does not claim independence for it. Later CHANGELOG commits at `0e789cff`, `88162e9c`, `e03fb1ae`, `92bd46bd` and `187dbd2e` alter the surrounding file; their Git account names are technical history, not an allocation of these surviving words.

**Reviewer result: `REVIEWER_CONFLICT ? REROUTING_REQUIRED`.** No one among Yen, Bao and Anh has been established as independent for the seven-line release-summary portion. Yen, as coordinator, should ask each participant whether they supplied substantive wording, prompts, edits or review of the *actual seven lines*, reconcile later edits, and record an eligible noncontributor. If all three participated or cannot establish nonparticipation, route to an outside reviewer. Do not infer eligibility from PR authorship, co-author trailers or review-only labels.

## Other source and rights blockers

- `backend/src/main/resources/db/helpdesk/policy-schema.sql` explicitly says it was copied from a V5 physical candidate, and `schema.sql` says it reuses V5 tables and constraints. That is an **internal** lineage lead; exact V5 source lines and authority remain unverified. Do not alter checksum-pinned Flyway material.
- Anh's favicon concept/ChatGPT statement and font/icon selection are contributor-process evidence. The [upstream reference supplement](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6706830005) does not verify exact package bytes, SVG geometry provenance or final NOTICE duties. The lockfile is generated dependency metadata, not an Anh-authored package.
- Bao's AI tool/model per commit, internal reuse and collaboration details include `NOT_RECALLED`; unknown AI output similarity and external inputs remain `UNKNOWN`. Yen's Group C role and exact `44283466` Backend/Portal/CHANGELOG actions remain `NOT_RECALLED`. Anh's exact surviving Frontend portions and any unallocated shared work remain unresolved.
- The nine original Data contracts and two original Data-test portions in Anh's declaration, Bao's later `fcc45fb` test changes, and #142 Identity evidence belong to other historical commits. They are relevant reviewer-boundary context but are **not** attributed to `44283466` rows in this matrix. Their own portion mapping and independent decisions remain separate.
- Proposed reviewer names in the CSV are **conditional routes**. `CONDITIONAL_NOT_ESTABLISHED` and `NOT_ESTABLISHED` are not independent approval. No matrix row is `CLEARED`, and no review-only activity is classified as code creation.

## Independent review requests

1. **Yen (coordinator):** obtain the seven-line CHANGELOG participation account from Anh, Bao and herself; document a genuinely noncontributing reviewer or request an outside reviewer. Reconcile the two historical-only controllers and V5 reuse separately.
2. **Bao:** check Backend blob/hunk mapping and his own declared scope, without reviewing rights for his own or unresolved `44283466` contributions. Confirm whether any particular Backend/Script/Doc portion was only reviewed, prompted or edited if genuinely recalled.
3. **Anh:** check Frontend and favicon mapping, the Portal BFF review-only boundary and the CHANGELOG wording map, without clearing her own directed portions. Her possible BFF reviewer eligibility requires an exact-portion participation check.
4. **Independent reviewer(s):** reproduce content alignment and assess contributor and upstream evidence per portion. Update the canonical rights register only through a separate authorized, reviewed decision; this preparation pass does not edit it.

**Current verdict:** `S02-01 PARTIAL ? REVIEWER CONFLICT OPEN`. The matrix is suitable for evidence review, while actual contributor allocation, reviewer independence, V5/third-party obligations and source rights remain pending.
