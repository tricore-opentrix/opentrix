<!-- SPDX-FileCopyrightText: 2026 TRICORE contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

Metadata applies to the report under the repository convention; it does not resolve attribution or grant rights over quoted source portions. All source rights remain RIGHTS_PENDING.

# R27 Step 6B — Ánh Git history and blob crosswalk

**Frozen candidate:** `187dbd2ea6935966f5c4cceb95ad9c3c53708a2e`
**Prepared:** 7 November 2026
**Type:** read-only technical reconciliation; no rights clearance.
**Rights disposition:** RIGHTS_PENDING.
**Companion:** `anh-git-blob-crosswalk.csv` (UTF-8 BOM, multiline quoted CSV).

## 1. Scope and technical verdict

Full non-shallow clone inspected at the frozen commit. All **140 candidate paths** in this audit scope were read as Git blobs and rehashed using the Git object header and SHA-1; all matched their tree object IDs. Scope includes all **80 Frontend + 14 Portal BFF paths**, all **126 paths** changed by `44283466f1747d55ed39e782d0600e8d09a28427`, nine Data contracts/two tests, README, and the two separate Data/Storage package boundaries (deduplicated).

The CSV contains **602 records**: 140 FILE_SUMMARY records and 462 HUNK_MAPPING records. Hunk records cover 37 distinct anchor/history commits. A file can have many rows; row counts are not file or rightsholder counts. Historical absent paths appear only in hunk rows.

**Verdict:** CANDIDATE_BLOB_IDENTITIES_PASS; HISTORY_AND_ORDERED_LINE_MAPPING_COMPLETE_FOR_DECLARED_SCOPE; ACTUAL_PARTICIPATION_PARTIAL; INDEPENDENT_RIGHTS_PENDING. The technical deliverable is complete within the method below. Complete causal provenance, AI/manual allocation and lawful rights remain unresolved. No production tests, browser sessions, archive download/rehashing or public similarity audit were run.

## 2. Reproducible method and limitations

1. `git ls-tree -r` enumerated the frozen tree. Raw bytes were read with `git show SHA:path` and Git blob SHA-1 recalculated. No checkout or source modification was needed.
2. `git diff-tree` enumerated the joint commit and named historic anchors; `git log --follow` traced each scoped path up to the frozen candidate. CSV origin is the earliest commit on that path history reachable from the candidate, not necessarily the original creative source.
3. Each relevant commit diff is parsed into hunks, retaining added/deleted text and historical line ranges. Historical post-change file lines are aligned with candidate lines using Python SequenceMatcher, autojunk disabled. Surviving ranges are ordered exact-line correspondences.
4. ALL_ADDED_LINES_MATCH means every added line can be aligned in order; it does not mean the complete hunk including context/deletions survived unchanged, nor that no independent repetition or reintroduction occurred. Partial and absent mappings are explicit. Deleted text is retained for review; no assumption that a deleted phrase never appears elsewhere.
5. Candidate-reachable integration history and recovered pre-squash commits are separate evidence. Git author is recorded as account/text association only. A squash can hide pre-integration development history.
6. Actual-participation cells carry the contributor’s **scope-level declaration**, not an inferred author assignment to every historical row. Exact prompt-to-hunk matching is UNKNOWN unless a separate statement/evidence identifies it. Review-only BFF status is personal recollection, not a Git-proven negative.

### Historical anchors

- [44283466f1747d55ed39e782d0600e8d09a28427](https://github.com/tricore-opentrix/opentrix/commit/44283466f1747d55ed39e782d0600e8d09a28427): feat(helpdesk): integrate backend, BFF and Portal for v0.1.0
- [40f0d71c9b54b0ac993bd48c375d3e740d6c20c1](https://github.com/tricore-opentrix/opentrix/commit/40f0d71c9b54b0ac993bd48c375d3e740d6c20c1): feat(data): define object storage and metadata contracts
- [973d39567335e41cb421f04cb6fed5b48f0a9b8d](https://github.com/tricore-opentrix/opentrix/commit/973d39567335e41cb421f04cb6fed5b48f0a9b8d): feat(data): define normalized storage errors and contract tests
- [fcc45fb65dc6c39ee5f75fd32f99f2a4de05241f](https://github.com/tricore-opentrix/opentrix/commit/fcc45fb65dc6c39ee5f75fd32f99f2a4de05241f): fix(data): sanitize runtime input read failures in contract fake
- [6f96719f249fe982826a84315443bc576697e378](https://github.com/tricore-opentrix/opentrix/commit/6f96719f249fe982826a84315443bc576697e378): Update contributor name in README.md
- [660d3e8793df303553e2253adead375d44fd7bbc](https://github.com/tricore-opentrix/opentrix/commit/660d3e8793df303553e2253adead375d44fd7bbc): feat(portal): establish mock confirmation baseline
- [482f9797896973153f75dea8670c71f1e5828e31](https://github.com/tricore-opentrix/opentrix/commit/482f9797896973153f75dea8670c71f1e5828e31): feat(portal): add Helpdesk HTTP adapter and DTO mapping
- [2315229fc8ec5bee85fe4f7dfad606f6f03d2d66](https://github.com/tricore-opentrix/opentrix/commit/2315229fc8ec5bee85fe4f7dfad606f6f03d2d66): feat(portal): integrate Helpdesk assignment and MVP flow
- [c73bbc306a698141169304e5da848ea0686700db](https://github.com/tricore-opentrix/opentrix/commit/c73bbc306a698141169304e5da848ea0686700db): fix(portal): harden MVP session lifecycle and regressions

### Ordered added-line mapping results

| Result | Hunk rows |
| --- | ---: |
| ALL_ADDED_LINES_MATCH | 400 |
| HISTORICAL_PATH_ABSENT | 18 |
| PARTIAL_ADDED_LINE_MATCH | 29 |
| NO_ADDED_LINE_MATCH | 4 |
| NO_ADDITIONS_DELETION_ONLY | 11 |

## 3. S6-06 Data contracts and mixed tests

Nine contracts introduced at 40f0d71 and two original tests at 973d395 are separate from Bảo’s two fcc45fb modifications. Candidate includes later metadata, so introduction blob equality is not presumed. The CSV captures full candidate history and hunk correspondence.

| File | Candidate blob | Relevant mapping |
| --- | --- | --- |
| `backend/src/main/java/com/tricore/dxos/core/data/ObjectContent.java` | `ed0219e987ffe5fef4762e8feb467d6254e7ff5a` | Original Ánh scope; later edits separately mapped |
| `backend/src/main/java/com/tricore/dxos/core/data/ObjectKey.java` | `0b93e68383aced826251620bc99ec56c94cb174f` | Original Ánh scope; later edits separately mapped |
| `backend/src/main/java/com/tricore/dxos/core/data/ObjectMetadata.java` | `9355cd158919bf6dc10e2e7d77146fc5059c90f1` | Original Ánh scope; later edits separately mapped |
| `backend/src/main/java/com/tricore/dxos/core/data/ObjectStoragePort.java` | `20b495e6bb74074b69ae5c97edc6b94b6f0f7a80` | Original Ánh scope; later edits separately mapped |
| `backend/src/main/java/com/tricore/dxos/core/data/StorageErrorCode.java` | `42d40baab52652d87626e86a32eb086a943c4731` | Original Ánh scope; later edits separately mapped |
| `backend/src/main/java/com/tricore/dxos/core/data/StorageException.java` | `d47e3666f6ee28a7172f1fe65f94bfcc1a42b057` | Original Ánh scope; later edits separately mapped |
| `backend/src/main/java/com/tricore/dxos/core/data/StorageValues.java` | `ad9870cf377a55ccf3f2f9b2cf50d91a9b7d3f3d` | Original Ánh scope; later edits separately mapped |
| `backend/src/main/java/com/tricore/dxos/core/data/StoreMode.java` | `a199c68d78863c09b475e5a8c39baa84425a5062` | Original Ánh scope; later edits separately mapped |
| `backend/src/main/java/com/tricore/dxos/core/data/StoreObjectCommand.java` | `1933fe012e5a46c415313e3700989c85ea9ca198` | Original Ánh scope; later edits separately mapped |
| `backend/src/main/java/com/tricore/dxos/core/data/package-info.java` | `95db14f4555b73463030b1cf384f74ce1aca07c4` | Separate Bảo-associated package boundary; not part of nine contracts |
| `backend/src/test/java/com/tricore/dxos/core/data/InMemoryObjectStorage.java` | `364010e2943a67f77b2076e546be45520ef112be` | Original Ánh scope; later edits separately mapped |
| `backend/src/test/java/com/tricore/dxos/core/data/ObjectStoragePortTest.java` | `c4b064741adf6bfe9b2c6f267343bee3c31278a7` | Original Ánh scope; later edits separately mapped |
| `backend/src/main/java/com/tricore/dxos/infrastructure/storage/package-info.java` | `cb61abba92b0686fd505a79cb02145699f2d3549` | Separate Bảo-associated package boundary |

### Bảo fcc45fb hunks — excluded from Ánh’s original-content declaration

- `backend/src/test/java/com/tricore/dxos/core/data/InMemoryObjectStorage.java` @@ -22,7 +22,7 @@ final class InMemoryObjectStorage implements ObjectStoragePort {: 1/1 added lines align; candidate ranges `29`. ALL_ADDED_LINES_MATCH.
- `backend/src/test/java/com/tricore/dxos/core/data/ObjectStoragePortTest.java` @@ -182,6 +182,37 @@ class ObjectStoragePortTest {: 31/31 added lines align; candidate ranges `189-219`. ALL_ADDED_LINES_MATCH.

The fake broadens IOException to IOException | RuntimeException. The regression test checks sanitized errors, caller-owned stream handling and preservation of content/metadata. This observation does not license Bảo’s code or independently establish his external sources.

## 4. S6-08 Frontend/Portal surviving-hunk mapping

All 94 paths have FILE_SUMMARY rows and every relevant reachable history commit is expanded into HUNK_MAPPING rows; four recovered pre-squash Portal commits are also included. Filter the CSV by file_path prefix and change_commit. Candidate histories show subsequent SPDX and compliance changes; these do not transfer ownership.

| Scope | Paths | Declared personal role | Reviewer boundary |
| --- | ---: | --- | --- |
| Frontend | 80 | Ánh requirements / AI prompts / Codex; some label changes not exactly recalled | No self-independent rights review of directed portions |
| Portal BFF | 14 | Ánh confirms review-only, no creation/prompt modification/code edits | Potential eligibility only after exact-portion check; no automatic blanket independence |

Git metadata cannot prove the absence of undocumented prompts. BFF review-only is supported by the corrected direct declaration, not by absence of Ánh’s Git name. Integration commits do not prove Yến or Bảo created every BFF line.

## 5. S6-09 favicon and source asset references

`frontend/public/favicon.svg` blob `2faa0e08edb86261c960119f997703f70849477b` matches expected `2faa0e08edb86261c960119f997703f70849477b`.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40"><rect width="40" height="40" rx="12" fill="#172650"/><path d="M10 11h9l11 18h-9zm11 0h9l-5 8h-9zM10 29l5-8h9l-5 8z" fill="#6de3ce"/></svg>
```

This is inline geometric SVG; the contributor reports ChatGPT text-directed creation without external images. Static geometry is not proof of originality. Source references and package declarations are assessed separately from bundled binaries.

Source scan found Be Vietnam Pro CSS imports in `frontend/src/main.tsx` (Vietnamese and Latin 400/500/600/700) and `frontend/tests/mvp-preview.tsx` (Vietnamese 400/500/600/700). Lucide imports occur in App, ui, AssignmentForm, Auth, Dashboard, Requests, NewRequest, RequestDetail and System.

- `@fontsource/be-vietnam-pro`: locked version `5.3.0`, declared license `OFL-1.1`. Lock metadata is not verification of exact-package LICENSE/NOTICE satisfaction.
- `lucide-react`: locked version `1.59.0`, declared license `ISC`. Lock metadata is not verification of exact-package LICENSE/NOTICE satisfaction.

Image/font-extension scan over the 94 tracked paths: 1 match(es): `frontend/public/favicon.svg`. This does not prove no indirectly referenced assets or dependency binaries exist. Exact npm package license texts and downstream distribution notices remain NOT_VERIFIED in this audit.

## 6. S6-11 README name hunk

Candidate blob `0a81dd3cc6a55efd288b0fe06213d62aa684cbfe`; candidate ranges `261`; ALL_ADDED_LINES_MATCH.

```diff
-| Phan Ngọc Ánh | Data / Storage, Portal, integration review |
+| Nguyễn Ngọc Ánh | Data / Storage, Portal, integration review |
```

Ánh confirms personally editing this name correction. Responsibility wording is unchanged. No whole-README authorship or self-independent disposition follows.

## 7. Joint integration: Backend, scripts, docs and CHANGELOG

126 changed paths: 23 Backend, 80 Frontend, 14 BFF, six scripts, two docs, one CHANGELOG. All are in the CSV. Unmapped substantive prompting/editing remains NOT_REC/UNKNOWN.

### CHANGELOG surviving expression

- @@ -20,11 +20,18 @@ User-visible DX-OS Open Core changes are recorded here. The format follows: ALL_ADDED_LINES_MATCH; candidate ranges `52-55;61-63`.

```text
- The Helpdesk HTTP API uses a scoped HTTP 404 / `NOT_FOUND` response for
  hidden or missing resources; the Generic Workflow HTTP API retains its
  pre-existing distinct `DEFINITION_NOT_FOUND` / `INSTANCE_NOT_FOUND` public
  codes and messages. Generic contract evolution is tracked in Issue #105.
- Helpdesk CREATE rejects missing exact technical authorities before protected
  definition/binding lookups; uncertain Workflow commits return HTTP 503 with
  `COMMIT_OUTCOME_UNKNOWN` and must not be retried automatically.
```

Ánh confirms AI direction for CHANGELOG, not exclusive authorship of the shared prose. A different eligible reviewer must assess these portions.

**Internal reuse finding:** `backend/src/main/resources/db/helpdesk/policy-schema.sql` explicitly states it was copied from the V5 physical candidate. Ánh’s statement that she did not request internal reuse must not be converted into no-reuse proof. Exact V5 source/portion and its contributor/notice lineage require separate reconciliation.

## 8. Actual participation and reviewer conflicts

| Portion | Evidence / role | Independent review |
| --- | --- | --- |
| Nine Data contracts and original tests | Ánh AI-assisted disclosure; introduction and candidate blobs mapped | Someone other than Ánh; exclude Bảo fcc45fb hunks |
| fcc45fb test changes | Bảo Git-associated and separately declared | Separate noncontributing reviewer; no blanket test ownership |
| Frontend AI-directed portions | Ánh prompts/requirements; exact roles incomplete per hunk | Ánh cannot self-approve rights |
| Portal BFF | Ánh confirms review-only | Eligibility conditional on exact portion; no blanket clearance |
| Favicon | Ánh concept and text-prompted ChatGPT asset | Noncontributing reviewer and asset/notice assessment |
| README name correction | Ánh manual name edit | Noncontributing reviewer |
| CHANGELOG / Backend corrections in joint commit | Ánh direction disclosed; surviving allocation incomplete | Avoid assigning Ánh independent rights for her own directions |
| Other scripts/docs/shared portions | General method disclosed; exact contribution NOT_REC | Routing unresolved until scoped evidence |

Evidence: [Ánh consolidated declaration](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6708767215), [earlier role clarification](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6708125085), [Yến declaration](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6708631841), [Bảo declaration](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6707960117). These are statements, not independent title proof.

## 9. Open source/attribution items and blockers

| Item | Missing evidence / action |
| --- | --- |
| Frontend / joint implementation | Match actual contributors to surviving portions; do not equate all 94 paths with Ánh ownership |
| Portal BFF | Preserve corrected review-only declaration; check exact-portion substantive involvement before reviewer assignment |
| Fonts/icons | Verify exact locked package source/license/NOTICE and actual source-only inclusion; preserve upstream terms |
| Favicon | Independent exact-blob origin/attribution assessment; no inferred originality from simple geometry |
| Data and tests | Independent assessment of originals vs Bảo modifications; fixture/example lineage if identified |
| V5 reuse | Locate referenced physical candidate and map copied portions/licensing |
| SPDX/REUSE and generated files | Separate metadata / lockfile generation from substantive rights; do not claim upstream license text |
| Unrecoverable prompts/origin | Record scoped UNKNOWN/NOT_REC and seek exception/remediation assessment; no invented provenance |

R29 HelpdeskUseCase five-line manual edit is outside this candidate and is not included as an R24 surviving hunk. No RIGHTS_PENDING entry was changed, no source edited, and no GitHub comment/PR posted in this task.

## 10. Complete candidate path/blob index

| Case | Path | Candidate blob | Earliest candidate-reachable history commit |
| --- | --- | --- |
| S6-11/S6-13 | `CHANGELOG.md` | `206411194805fc40c4ca544fd08e156e693cdd5c` | `af21ae5ff59d8eb9b3c0fef0bc8a78295aeb588d` |
| S6-11 / shared integration investigation | `README.md` | `0a81dd3cc6a55efd288b0fe06213d62aa684cbfe` | `244ad2c8505916dc4f037c95fbf8318073a55534` |
| S6-11 / shared integration investigation | `backend/src/main/java/com/tricore/dxos/application/authorization/TenantResourceWorkflowAccessPolicy.java` | `53eaa287463d9b34e184ba7d116bf1ee9143b8f2` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-11 / shared integration investigation | `backend/src/main/java/com/tricore/dxos/application/authorization/WorkflowAccessException.java` | `53e78fd1d7c1f016cf8cc6c9266b0bec1e743123` | `fd5469ef6a6607c6940c5c22e61d4c078fda13d9` |
| S6-11 / shared integration investigation | `backend/src/main/java/com/tricore/dxos/application/authorization/WorkflowAclSnapshotReader.java` | `b77bbf862840d0eadd912ad6a91813faeaafda42` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-06 | `backend/src/main/java/com/tricore/dxos/core/data/ObjectContent.java` | `ed0219e987ffe5fef4762e8feb467d6254e7ff5a` | `40f0d71c9b54b0ac993bd48c375d3e740d6c20c1` |
| S6-06 | `backend/src/main/java/com/tricore/dxos/core/data/ObjectKey.java` | `0b93e68383aced826251620bc99ec56c94cb174f` | `40f0d71c9b54b0ac993bd48c375d3e740d6c20c1` |
| S6-06 | `backend/src/main/java/com/tricore/dxos/core/data/ObjectMetadata.java` | `9355cd158919bf6dc10e2e7d77146fc5059c90f1` | `40f0d71c9b54b0ac993bd48c375d3e740d6c20c1` |
| S6-06 | `backend/src/main/java/com/tricore/dxos/core/data/ObjectStoragePort.java` | `20b495e6bb74074b69ae5c97edc6b94b6f0f7a80` | `40f0d71c9b54b0ac993bd48c375d3e740d6c20c1` |
| S6-06 | `backend/src/main/java/com/tricore/dxos/core/data/StorageErrorCode.java` | `42d40baab52652d87626e86a32eb086a943c4731` | `40f0d71c9b54b0ac993bd48c375d3e740d6c20c1` |
| S6-06 | `backend/src/main/java/com/tricore/dxos/core/data/StorageException.java` | `d47e3666f6ee28a7172f1fe65f94bfcc1a42b057` | `40f0d71c9b54b0ac993bd48c375d3e740d6c20c1` |
| S6-06 | `backend/src/main/java/com/tricore/dxos/core/data/StorageValues.java` | `ad9870cf377a55ccf3f2f9b2cf50d91a9b7d3f3d` | `40f0d71c9b54b0ac993bd48c375d3e740d6c20c1` |
| S6-06 | `backend/src/main/java/com/tricore/dxos/core/data/StoreMode.java` | `a199c68d78863c09b475e5a8c39baa84425a5062` | `40f0d71c9b54b0ac993bd48c375d3e740d6c20c1` |
| S6-06 | `backend/src/main/java/com/tricore/dxos/core/data/StoreObjectCommand.java` | `1933fe012e5a46c415313e3700989c85ea9ca198` | `40f0d71c9b54b0ac993bd48c375d3e740d6c20c1` |
| S6-11 / shared integration investigation | `backend/src/main/java/com/tricore/dxos/core/data/package-info.java` | `95db14f4555b73463030b1cf384f74ce1aca07c4` | `d53a273f63fa07af424825f8775b030d94344fd5` |
| S6-11 / shared integration investigation | `backend/src/main/java/com/tricore/dxos/gateway/helpdesk/HelpdeskController.java` | `b6738c5cbc89e4a29ef9b27ca4444661e207c223` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-11 / shared integration investigation | `backend/src/main/java/com/tricore/dxos/gateway/helpdesk/HelpdeskExceptionHandler.java` | `1627692ae174bb36738e8eb1f3c4a1048b37f1da` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-11 / shared integration investigation | `backend/src/main/java/com/tricore/dxos/gateway/workflow/WorkflowJsonConfiguration.java` | `d73f8b4d7effe7818e08a70a189cd23b338ec1fb` | `d85cf6858869347a1eb0f677ee63ea1e2f9f0619` |
| S6-11 / shared integration investigation | `backend/src/main/java/com/tricore/dxos/gateway/workflow/controller/WorkflowExceptionHandler.java` | `564d0b505879101e9343b40fe57fa93db0b1ac9d` | `9d375e00fe81231e652a90e6dd099d434e558e74` |
| S6-11 / shared integration investigation | `backend/src/main/java/com/tricore/dxos/infrastructure/storage/package-info.java` | `cb61abba92b0686fd505a79cb02145699f2d3549` | `d53a273f63fa07af424825f8775b030d94344fd5` |
| S6-11 / shared integration investigation | `backend/src/main/java/com/tricore/dxos/infrastructure/workflow/HelpdeskConfiguration.java` | `c42b025696096c98ffbc166efda800f83d6adc1f` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-11 / shared integration investigation | `backend/src/main/java/com/tricore/dxos/infrastructure/workflow/HelpdeskService.java` | `e95395a2374e5abdf16a2c87273f6cc2640f25ac` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-11 / shared integration investigation | `backend/src/main/java/com/tricore/dxos/infrastructure/workflow/PostgresWorkflowPersistence.java` | `c91bb96158b2a510276b3623a6f6f442c83cb33a` | `899ef1132d9b1ff01d6db6f1efc2ea3a5c0d7aa0` |
| S6-11 / shared integration investigation | `backend/src/main/java/com/tricore/dxos/request/controller/RequestController.java` | `ABSENT` | `daa62d5ca5d421d662cd8c3c6a0cb4923dbcc3bc` |
| S6-11 / shared integration investigation | `backend/src/main/java/com/tricore/dxos/request/controller/RequestWorkflowController.java` | `ABSENT` | `a6ec84ef5b0d0a8e6fbea8f57a732edcf8970dab` |
| S6-11 / shared integration investigation | `backend/src/main/resources/db/helpdesk/definition.sql` | `9ddc4bc02d4e8eb98e011d89a7cbfdb9c9ab2933` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-11 / shared integration investigation | `backend/src/main/resources/db/helpdesk/policy-schema.sql` | `c591506a289d9793dd84c4df76ac780b09122800` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-11 / shared integration investigation | `backend/src/main/resources/db/helpdesk/runtime-grants.sql` | `6a1ca1a5460318f8007f4c33d22eceefec4ef039` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-11 / shared integration investigation | `backend/src/main/resources/db/helpdesk/schema.sql` | `d194672649b031a661785806701f35d0537b9f9b` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-11 / shared integration investigation | `backend/src/test/java/com/tricore/dxos/application/authorization/TenantResourceWorkflowAccessPolicyTest.java` | `2c344c7088a8306a498dc5f926a33dd869260a98` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-06/S6-07 | `backend/src/test/java/com/tricore/dxos/core/data/InMemoryObjectStorage.java` | `364010e2943a67f77b2076e546be45520ef112be` | `973d39567335e41cb421f04cb6fed5b48f0a9b8d` |
| S6-06/S6-07 | `backend/src/test/java/com/tricore/dxos/core/data/ObjectStoragePortTest.java` | `c4b064741adf6bfe9b2c6f267343bee3c31278a7` | `973d39567335e41cb421f04cb6fed5b48f0a9b8d` |
| S6-11 / shared integration investigation | `backend/src/test/java/com/tricore/dxos/core/workflow/WorkflowHttpRuntimeTest.java` | `9ac13bb573d247592645b43117b7dbfdf5689bbb` | `9d375e00fe81231e652a90e6dd099d434e558e74` |
| S6-11 / shared integration investigation | `backend/src/test/java/com/tricore/dxos/gateway/helpdesk/HelpdeskErrorContractTest.java` | `3d5018b682e1addbeb862542ebfa4ca662cdbba7` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-11 / shared integration investigation | `backend/src/test/java/com/tricore/dxos/gateway/workflow/controller/WorkflowControllerTest.java` | `8eff5776bd18090115bf5f8513632589a8f77ad3` | `9d375e00fe81231e652a90e6dd099d434e558e74` |
| S6-11 / shared integration investigation | `backend/src/test/java/com/tricore/dxos/infrastructure/workflow/HelpdeskConfigurationTest.java` | `fe5a94e5812e2ec5ac59efafcc4b51c3292cb8d4` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-11 / shared integration investigation | `backend/src/test/java/com/tricore/dxos/infrastructure/workflow/HelpdeskHttpPostgresTest.java` | `97b16de2ceb88eae5efe75d9da3e22dcd3805aa9` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-11 / shared integration investigation | `backend/src/test/java/com/tricore/dxos/infrastructure/workflow/PostgresWorkflowPersistenceIntegrationTest.java` | `46aa4d2fe82c032c042af4e0ccb551b29025f4a7` | `899ef1132d9b1ff01d6db6f1efc2ea3a5c0d7aa0` |
| S6-11 / shared integration investigation | `docs/verification/issue53-helpdesk-local-closeout-20261029.md` | `3b7559a1e5df67a9309e083b1013518e937d494a` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-11 / shared integration investigation | `docs/verification/issue53-java-helpdesk-mvp-integration-20261028.md` | `c2a2c769599fcc51a52cc4774f4dd533e1cb90e4` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/.gitignore` | `326fe72a26da191eb1c68dd8eb017bec059043f0` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/DEMO_GUIDE.md` | `304205d8db39a8fafcb81b4049247d9c70dbb126` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/DRAFT_PR.md` | `6161930e8f8e93aa39c20212136fdcb9f7a38350` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/README.md` | `a14a8e1f2b2bd405cb08dae4ebfc240afc3232b1` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/index.html` | `2784caa91845578bfbbb00b8f60a55ae30e9636f` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/package-lock.json` | `3154103be5f919482b5c5b59d51260d51ff24ef9` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/package.json` | `5bdf1add8c67f25814ce914a0c8718bb28036a25` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/playwright.config.ts` | `ce1e656689f0b825dfd77d70407b9e9503c03ed7` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-09 | `frontend/public/favicon.svg` | `2faa0e08edb86261c960119f997703f70849477b` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/scripts/check-security.mjs` | `7796c71403541eed5f0f00fe70abacc9bdaacc48` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/App.test.tsx` | `c66c21b1b9459aff1c0f2c498d956cfc18a717d0` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/App.tsx` | `63bb763797f6cebddd5745541e28ecd699c8f1ee` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/components/AssignmentForm.integration.test.tsx` | `1969b086c6cc11b9aeff087fbfa138ac333b4a0a` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/components/AssignmentForm.test.tsx` | `5b3e53d3f7422f3563b1ffca6de8b65f395e9c7d` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/components/AssignmentForm.tsx` | `4327193956448bcb70a195c823a0e92033d0887b` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/components/ui.tsx` | `efb9b43c675f6d4c1691d306a3f7a5d09ba5052e` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/context.service.test.tsx` | `75f84ac6f3b006c86d1c4889ec83ebaab000393e` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/context.tsx` | `cabdb3efb3be5a8bf7587f97a3a4f33dcd0f5118` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/domain/request.test.ts` | `65e11c8b43da2bd1e787046d8b9a7ef577e9a241` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/domain/request.ts` | `8a2af07abea5afcac91b101d23bcf75d6d6339c4` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/features/helpdesk/HelpdeskPortal.test.tsx` | `e615e4877aed11a3e18974b34cd92a5c202c93fc` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/features/helpdesk/HelpdeskPortal.tsx` | `c410412f4844b29f847d28943229327c6769e002` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/features/helpdesk/LocalHelpdeskIntegration.test.tsx` | `be86c6a5f4dca11a35fa30b07f43567822bf525f` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/features/helpdesk/LocalHelpdeskIntegration.tsx` | `ec9d687da2a34416ef43d6e007361d2ad01a214d` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/features/helpdesk/useHelpdeskRead.ts` | `9e2e82d2be3300e100cc3b703da364dd7567ac78` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/fixtures/requests.ts` | `f62e2d02b9d2deba938bbcc7986af89776f72005` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/hooks/useRequests.ts` | `9c0992c75302c8d866383744fb3f9a7ee73873b5` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/hooks/useSessionOperation.ts` | `b704e83c2cef2701c0caeedaf98294fcc75fe74e` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/main.tsx` | `2189e83adca276e0b9de25a4750aa338fae65206` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/pages/Auth.test.tsx` | `fd33eb30ad77f439a86f5eb3921b0d8f3d9a686c` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/pages/Auth.tsx` | `c6cfa598b5ca67c3f25b717159bdcb61130f54ff` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/pages/Dashboard.tsx` | `791869773c48b5d3ccce74179f130a52373761a3` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/pages/NewRequest.test.tsx` | `7a03a1805263d263e3357409e4194f8f1c767ecd` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/pages/NewRequest.tsx` | `125eb1aac558722c93007aa36a19840ea88c435c` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/pages/RequestDetail.tsx` | `6672d00034dd14560c33f7ae02ed8d7db20a8783` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/pages/Requests.tsx` | `a834a29a3ac94ed47f865127d287f02cd3e20d00` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/pages/System.tsx` | `27adc2d278988fe69a0e51a9250b3bc660375a69` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/pages/auth.css` | `2ac2191f43d5d9428c61663dd514433d3bcd55f0` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/services/HttpApiClient.ts` | `93fb05dc64a5955ecfe9d69b57205936447e6c7d` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/services/MockRequestService.ts` | `b1d6c96444d28b16bde5647868b6173086025f1f` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/services/RequestService.ts` | `88413e7c4aa05a1fbddc61b2ca88127f83bb1154` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/services/mvp/HelpdeskRequestService.ts` | `9f7c1bae362e6a8df78874141a46a8d1fe93642a` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/services/mvp/assignmentBinding.ts` | `321b9172f8f565c6b0793cf737c462f8fee52178` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/services/mvp/commands.ts` | `2af2cf9164a9e2c4aa2f80dce7f6089a1eccd8b6` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/services/mvp/errors.ts` | `bc209a48972518a8a47087e2ac1db04f6ba749c1` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/services/mvp/foundation.test.ts` | `b442f6e89532df57b3ff2a50a6c59e56d7b29f28` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/services/mvp/helpdeskPortalPort.ts` | `2de5150b300166a0c5468ab6d103af713373c406` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/services/mvp/helpdeskPresentation.test.ts` | `70828693ff32427372b7ebaf343d035db3aac6b8` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/services/mvp/helpdeskPresentation.ts` | `13e0b03a02afd08f459e99c1f3065e29ecb3d716` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/services/mvp/http/HelpdeskApiClient.test.ts` | `93618b43edcf50bd24c2e10084a6afb15a1dcf07` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/services/mvp/http/HelpdeskApiClient.ts` | `975c042724a0d3b171f34b114885c331ae5bec2c` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/services/mvp/http/codecs.ts` | `2ba494e88e9a6b29e7e9d4fdb3272503abfb80bc` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/services/mvp/http/errors.ts` | `2827b0397f6b00a7880dd03e3cd448836898ea4e` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/services/mvp/http/liveGate.test.ts` | `06dd18794f6c34750eae5b73d676c9f13368a773` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/services/mvp/http/sameOriginTransport.test.ts` | `55278e55217334077627663af61b51682c820c38` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/services/mvp/http/sameOriginTransport.ts` | `6f8813dd4ddd9952f47e506d20b26e54da1c2ddf` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/services/mvp/http/transport.ts` | `3294a00b59c67f990e45987a3860a17c43f7e9fb` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/services/mvp/http/types.ts` | `d6a0110809b1edc3354d9291a2a96886f60a4674` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/services/mvp/port.ts` | `7dc0904b9529a8a7cc4d9e55985f955fc0c8388d` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/services/mvp/presentation.test.ts` | `ea25c3e5986ff1c709aeb435bfbca0dde56c3f7f` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/services/mvp/presentation.ts` | `afc3ed6df7d09dc5e3bdc82800621bf810326916` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/services/mvp/projections.ts` | `cb6775f7c33fcb819a0b83599fd2ba333aa0cb80` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/services/mvp/types.ts` | `4fc707bc62eebb7145a2c28b5940b11230300d4b` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/services/portalService.ts` | `1d7582c51357c96ea9355f3c40a0cb08ef5210c6` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/services/services.test.ts` | `491ff966c9de4096269e91835e1bfedd77b4b13c` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/styles.css` | `bfbe0b4efccab7c77e57bdea283dddb69db7683d` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/test/fakeHelpdeskTransport.ts` | `43d8ef0075044e63ad7f4b6c81e8caa0f4215bf8` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/test/helpdeskFixtures.ts` | `bb162b45e62307d9083e1acfcc36b92862da3ac8` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/test/setup.ts` | `e6e64ea3cbf41ddbd3a8fe420bf0f0b3cb944fad` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/tokens.css` | `faf2817a40d9cf69ba9b527e3f8edafb1cf1956d` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/src/university-theme.css` | `fe8e814e4f0b7c7d5fa38637204fc892cc148891` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/tests/auth.spec.ts` | `d9707d405d972a3fc41f4ea3249de28d072a2ffd` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/tests/helpdesk-mvp.spec.ts` | `cec26bad100844a66f8ec21b34d312be6e39e4cd` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/tests/mvp-preview.html` | `1b1ca350f7c2c22c030a52522ae7950f7d11a5be` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/tests/mvp-preview.tsx` | `183c67852674bb094974ee335ecf3448a51a207e` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/tests/mvp.playwright.config.ts` | `1323a07294a3f846f180b8e2263fe24871a60315` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/tests/portal.spec.ts` | `9b1d037a46a2516eebe260270c9927ec24406bf9` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/tests/session.spec.ts` | `7303c1d63e91bac9a8bfe8d7c21dd68b5d9dd639` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/tsconfig.json` | `46e2b38a05400793d5f48e69e9532bddfed265cb` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `frontend/vite.config.ts` | `8cd38a5adff5e9d7d72a408f75963571ceeff193` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `portal-bff/.gitignore` | `9f2a078806e1b8600d753f53ee7437b168a1b55b` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `portal-bff/Caddyfile.local` | `a93711ce79d3a43287ca2295b426eb884fcda99f` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `portal-bff/README.md` | `7abc5c499c458a8385ca0e8d363a027a8844c0ad` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `portal-bff/build.gradle` | `4ed140592af53595a9eb992e11471b7fdd15e78a` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `portal-bff/settings.gradle` | `930099ab4833b2d1bc94adc6fabbf4c104929dd1` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `portal-bff/src/main/java/com/tricore/dxos/portal/PortalAuthorization.java` | `2f053377b04b738f02023f309e02605db10569aa` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `portal-bff/src/main/java/com/tricore/dxos/portal/PortalBackendClient.java` | `9e0d50fd3f568fc9c8ffbf22a20b4a58f2b81d6d` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `portal-bff/src/main/java/com/tricore/dxos/portal/PortalBffApplication.java` | `5886306f6b798d6f9cfcadd3293a95e3e58d02d0` | `30597dab62b0602fd59e3617c0701f7b0d059c7b` |
| S6-08 | `portal-bff/src/main/java/com/tricore/dxos/portal/PortalOrigin.java` | `ad905bc7eab4c0e15fe02c27455d2d69242ee2ea` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `portal-bff/src/main/java/com/tricore/dxos/portal/PortalSecurity.java` | `abf532cd76a62bc6e5a8ef24403352d5893d07c9` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `portal-bff/src/main/java/com/tricore/dxos/portal/PortalSessionController.java` | `752794ec2611dcfed7d48d5d8a511b3a8a24ed29` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `portal-bff/src/main/resources/application.yml` | `8ad9c60264c3920da1aa99f3c67d00f6431ca91c` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `portal-bff/src/test/java/com/tricore/dxos/portal/PortalBackendClientTest.java` | `9e270028124f320c2f089e95878aa0c53e6b2641` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-08 | `portal-bff/src/test/java/com/tricore/dxos/portal/PortalSecurityTest.java` | `69545a85f4e8aa0fd83307b7c383b414ed47e6c3` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-11 / shared integration investigation | `scripts/README-helpdesk-local.md` | `f79e5e4fd88dca23582647f5fc94ade34ac313db` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-11 / shared integration investigation | `scripts/helpdesk-b06-local.ps1` | `f234a27a576ac930b0b29fb50e8b6d87789285b9` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-11 / shared integration investigation | `scripts/helpdesk-local-actor-seed.ps1` | `7af3bde6add9292bc729116d3b1161966605b912` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-11 / shared integration investigation | `scripts/helpdesk-local-setup.ps1` | `3fcfcb4d151731c197ec0ac56d091f22f2ba34d4` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-11 / shared integration investigation | `scripts/helpdesk-negative-local.ps1` | `0110875d44da576a217ead1c5dcee4081796bd76` | `44283466f1747d55ed39e782d0600e8d09a28427` |
| S6-11 / shared integration investigation | `scripts/test-helpdesk-local-actor-seed.ps1` | `a097a9a4f537ae611a72112c11b85b1d3408c924` | `44283466f1747d55ed39e782d0600e8d09a28427` |
