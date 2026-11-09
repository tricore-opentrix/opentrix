<!--
SPDX-FileCopyrightText: NOASSERTION
SPDX-License-Identifier: Apache-2.0
-->

# R27B Step 01 — proposed nine-package documentation inventory

**Scope decision:** `NINE_PACKAGE_SCOPE_PROPOSED — NOT YET APPROVED`
**Repository:** `tricore-opentrix/opentrix` · **inventory branch:** `docs/r27b-step01-canonical-inventory` · **base HEAD:** `187dbd2ea6935966f5c4cceb95ad9c3c53708a2e`
**Tracking:** [Issue #138](https://github.com/tricore-opentrix/opentrix/issues/138) (OPEN); R27B checklist owner Yến, reviewers Bảo and Ánh, milestone v0.2.0. R27A Core/Helpdesk service split is outside this inventory.
**Source baseline:** `187dbd2ea6935966f5c4cceb95ad9c3c53708a2e`. Historical Identity evidence also uses `5daa145d3b5f20f2f16fe0799c6d0808fd6c3e33`. Neither is a current documentation PR HEAD.

## Executive summary

The [Document Register](https://github.com/tricore-opentrix/opentrix/blob/8492abd20e3e7fe00ad18d687f4674fa339fe20c/docs/verification/r27/README.md) contains **17 table entries/IDs**, plus its own header ID `R27-REG-DOC-001`: **18 registered distinct IDs** in total. It does **not** approve nine mandatory deliverables. [PR #150](https://github.com/tricore-opentrix/opentrix/pull/150) adds `R27-EVD-007`, producing **19 identified IDs** after the Register snapshot. `R27-DEC-002` and `R27-EVD-003` name different purposes attached to one checkpoint file; neither ID is discarded. Source IDs `ID-01`–`ID-37`, `ID-D01`/`ID-D02`, and 357 remediation rows are not document IDs.

The companion [CSV](r27b-nine-package-inventory.csv) has **53 artifact rows**: 50 distinct files pinned to PR HEADs, one historical R25 file pinned to its commit, and two attributable Issue #138 comment records. The initial 50-path discovery was a PR-file snapshot; the R25 file was added later. Thus there are **51 unique file paths and 51 distinct pinned file revisions** (no repeated path at another SHA in the CSV). The three new inventory output files are excluded from these evidence counts. All 51 file paths were fetched at the specified immutable commit and have blob SHA values. The 50 PR files are absent from frozen `main`; the R25 file is historical and also absent. Two issue-comment records have no repository file path by design. Additional source statements and review links are cited as supporting evidence, not converted into invented files. All 15 inspected PRs remain Draft; #153 is CLOSED unmerged, the other 14 are OPEN. This is an inventory of evidence, not source-rights clearance or release acceptance.

```text
INITIAL_DISCOVERED_PATHS: 50 (distinct paths from inspected PR changed-file lists)
FINAL_UNIQUE_FILE_PATHS: 51
FINAL_PINNED_FILE_REVISIONS: 51
COMMENT_ONLY_RECORDS: 2
CURRENT_INVENTORY_OUTPUT_FILES: 3 (excluded from evidence CSV)
EXPLANATION_OF_50_VS_51: historical docs/verification/r25/exception-review.csv at commit 35e90c47 was added after the 50-PR-path snapshot; no repeated path is counted twice.
```

## Proposed packages and routing

| Group | Purpose, retained IDs, dependencies | Coordinator / evidence contributor | Proposed independent review |
| --- | --- | --- | --- |
| R27B-PKG-01 | Source/archive inventory: `R27-INV-001`, `R27-VER-001`; R24 technical source scope and [#157](https://github.com/tricore-opentrix/opentrix/pull/157) archive reproduction. Depends on frozen SHA, archive and #143 rows. | Yến coordinates; Bảo produced technical ledger/archive evidence. | Yến reproduces Bảo's method; Ánh cross-checks Frontend/assets. |
| R27B-PKG-02 | Contributor declarations: `R27-DEC-001`, `R27-DEC-002`, `R27-DEC-003`, plus `R27-EVD-003` on the same Bảo checkpoint file. Depends on direct attributable statements and per-portion scope. | Yến coordinates and states her own scope; Bảo and Ánh state only their own scopes. | Ánh for Yến; Yến for Bảo; Yến/Bảo for Ánh only where noncontributing. |
| R27B-PKG-03 | Canonical rights remediation register: `R27-REG-001`. [#151](https://github.com/tricore-opentrix/opentrix/pull/151) is the newer three-file S6-13 correction on #143; all 357 legacy `RIGHTS_PENDING` rows remain. | Bảo created the register; Yến coordinates the correction. | Ánh/Yến by actual portion; no Bảo self-review. |
| R27B-PKG-04 | Identity source provenance: `R27-EVD-001`, `R27-EVD-002`, newly added `R27-EVD-007`; historical prompt and 24-file matrix support these. Depends on Identity historical SHA, frozen source comparison, and Yến's attributable account. | Yến. | Ánh for Yến's portions; route any Ánh-contributed portion elsewhere. |
| R27B-PKG-05 | Backend/Frontend/Data and exception provenance: `R27-EVD-004`, `R27-EXC-001`; #139 Backend/Gateway, #154 Ánh crosswalk, #153/#155 Yến Group C are distinct technical evidence. Depends on 37 historical exceptions and per-hunk attribution. | Bảo (Backend), Ánh (Data/Frontend/Portal/assets), Yến (Group C coordination). | Yến/Bảo/Ánh separately by noncontributed portion. |
| R27B-PKG-06 | Contributor/portion review routing: `R27-EVD-005`, `R27-EVD-006` and its 13-case matrix. [#152](https://github.com/tricore-opentrix/opentrix/pull/152) updates #149 S6-13 routing. Depends on actual contribution boundaries and #151. | Yến coordinates; Bảo supplied initial routing evidence. | Bảo/Ánh on coordinator documents, with exact-portion conflict check. |
| R27B-PKG-07 | Third-party License & NOTICE assessment: `R27-LIC-001`. Depends on upstream texts, SBOM/generator provenance, Gradle Wrapper, fixtures, assets, and #143. | Yến coordinates; Bảo verifies build/backend, Ánh verifies frontend/assets. | Bảo/Ánh only outside their substantive contributions; third reviewer if needed. |
| R27B-PKG-08 | Register, vocabulary, review gates: `R27-REG-DOC-001`, `R27-REG-DOC-002`, `R27-REV-001`. Depends on exact PR revisions and separate status axes. | Yến coordinates index/vocabulary; Bảo drafted gates. | Bảo/Ánh review documentation excluding own portions. |
| R27B-PKG-09 | Final source-rights and release handoff: `R27-RPT-001`; #139 acceptance preflight/JSON are R24 dependencies, not an approved rights report. Depends on all preceding packages and separate R24 acceptance. | Yến prepares handoff. | Bảo/Ánh scope-specific review; independent source-rights decisions remain separate. |

Grouping IDs are navigation keys, not replacements for the original document IDs. Technical archive verification, a contributor statement, a rights disposition register, and a final handoff have different purposes even when they cite the same frozen source bytes.

## Exact ID-to-artifact mapping and three status axes

Values are `document_status / evidence_verification / rights_disposition`. `Approved` below means only scoped documentation review at the cited exact PR HEAD; it does not mean the Draft PR merged or the underlying source rights cleared. `PARTIAL` reflects bounded technical checks with unresolved provenance or rights. The CSV carries every supporting file's exact path, branch PR, HEAD, blob SHA, contributor, reviewer route, and next action.

| Package | Existing document ID | Exact path or record | Current PR | Status axes |
| --- | --- | --- | --- | --- |
| R27B-PKG-01 | `R27-INV-001` | `docs/verification/r27/v0.2.0-source-only-git-rights-ledger-187dbd2.csv` | [#139](https://github.com/tricore-opentrix/opentrix/pull/139) | In Review / PARTIAL / PENDING |
| R27B-PKG-01 | `R27-VER-001` | `docs/06-deployment/r24-v0.2.0-source-only-two-run-verification-187dbd2.md` | [#139](https://github.com/tricore-opentrix/opentrix/pull/139) | In Review / PARTIAL / PENDING |
| R27B-PKG-02 | `R27-DEC-001` | `docs/verification/r27/identity-contributor-declaration-yen.md` | [#142](https://github.com/tricore-opentrix/opentrix/pull/142) | In Review / PARTIAL / PENDING |
| R27B-PKG-02 | `R27-DEC-002; R27-EVD-003` | `docs/verification/r27/bao-backend-core-gateway-evidence-checkpoint-187dbd2.md` | [#139](https://github.com/tricore-opentrix/opentrix/pull/139) | In Review / PARTIAL / PENDING |
| R27B-PKG-02 | `R27-DEC-003` | `GitHub issue comment` | [#138](https://github.com/tricore-opentrix/opentrix/issues/138) | In Review / PARTIAL / PENDING |
| R27B-PKG-03 | `R27-REG-001` | `docs/verification/r27/r27-rights-remediation-register-187dbd2.csv` | [#151](https://github.com/tricore-opentrix/opentrix/pull/151) | In Review / PARTIAL / PENDING |
| R27B-PKG-04 | `R27-EVD-001` | `docs/verification/r27/identity-provenance-review-5daa145d.md` | [#142](https://github.com/tricore-opentrix/opentrix/pull/142) | In Review / PARTIAL / PENDING |
| R27B-PKG-04 | `R27-EVD-002` | `docs/verification/r27/identity-g3-g4-per-file-source-origin-matrix-5daa145d.csv` | [#142](https://github.com/tricore-opentrix/opentrix/pull/142) | In Review / PARTIAL / PENDING |
| R27B-PKG-04 | `R27-EVD-007` | `docs/verification/r27/r27-step6-s6-01-s6-02-identity-verification.md` | [#150](https://github.com/tricore-opentrix/opentrix/pull/150) | Approved / PARTIAL / PENDING |
| R27B-PKG-05 | `R27-EVD-004` | `docs/verification/r27/anh-source-rights-disposition-queue.md` | [#144](https://github.com/tricore-opentrix/opentrix/pull/144) | Approved / PARTIAL / PENDING |
| R27B-PKG-05 | `R27-EXC-001` | `docs/verification/r25/exception-review.csv` | [#138](https://github.com/tricore-opentrix/opentrix/issues/138) | UNKNOWN / PARTIAL / PENDING |
| R27B-PKG-06 | `R27-EVD-005` | `docs/verification/r27/r27-contributor-declarations-and-routing-187dbd2.md` | [#151](https://github.com/tricore-opentrix/opentrix/pull/151) | In Review / PARTIAL / PENDING |
| R27B-PKG-06 | `R27-EVD-006` | `docs/verification/r27/r27-step6-contributor-provenance-verification.md` | [#152](https://github.com/tricore-opentrix/opentrix/pull/152) | Approved / PARTIAL / PENDING |
| R27B-PKG-07 | `R27-LIC-001` | `docs/verification/r27/r27-third-party-license-notice-assessment.md` | [#148](https://github.com/tricore-opentrix/opentrix/pull/148) | Approved / PARTIAL / PENDING |
| R27B-PKG-08 | `R27-REG-DOC-001` | `docs/verification/r27/README.md` | [#146](https://github.com/tricore-opentrix/opentrix/pull/146) | Approved / PARTIAL / NOT_APPLICABLE |
| R27B-PKG-08 | `R27-REG-DOC-002` | `docs/verification/r27/r27-status-and-id-vocabulary.md` | [#147](https://github.com/tricore-opentrix/opentrix/pull/147) | Approved / PARTIAL / NOT_APPLICABLE |
| R27B-PKG-08 | `R27-REV-001` | `docs/verification/r27/r27-independent-review-gates-187dbd2.md` | [#151](https://github.com/tricore-opentrix/opentrix/pull/151) | In Review / PARTIAL / PENDING |
| R27B-PKG-09 | `R27-RPT-001` | `docs/verification/r27/r27-final-source-rights-handoff-report.md` | [#148](https://github.com/tricore-opentrix/opentrix/pull/148) | Approved / PARTIAL / PENDING |

The R25 exception row's **document approval status is UNKNOWN**: its historical blob is accessible, but a current independent document decision was not established. The `R27-DEC-003` record is an [Ánh-attributed Issue #138 statement](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6663564250), posted on her behalf with explicit confirmation, with a separate [109-path handoff](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6702734422). The Bảo checkpoint is explicitly unsigned; his [scoped reports](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6702663219) do not turn it into a signed declaration. The CSV preserves both IDs on that single file, so there is no ID collision or duplicate artifact row.

The **seven `Approved` ID records** are scoped documentation decisions at these exact commits: `R27-EVD-004` ([#144](https://github.com/tricore-opentrix/opentrix/pull/144), Bảo, `188969ada812e0016ed952b5ad422e210b9b0055`); `R27-REG-DOC-001` ([#146](https://github.com/tricore-opentrix/opentrix/pull/146), Bảo/Ánh, `8492abd20e3e7fe00ad18d687f4674fa339fe20c`); `R27-REG-DOC-002` ([#147](https://github.com/tricore-opentrix/opentrix/pull/147), Bảo/Ánh, `94a998978e811a546fdd7a8840af3e4b9686f286`); `R27-LIC-001` and `R27-RPT-001` ([#148](https://github.com/tricore-opentrix/opentrix/pull/148), Bảo/Ánh, `25faa214835093d591eb381be910e1efc1b8c085`); `R27-EVD-006` ([#149](https://github.com/tricore-opentrix/opentrix/pull/149), Bảo/Ánh, `329670d5768c34020828523c65a321494a5b1518`, with Ánh's subsequent routing-delta approval at [#152](https://github.com/tricore-opentrix/opentrix/pull/152) `4618777ce3525afe63a45cb67f99363f20ed26d1`); and `R27-EVD-007` ([#150](https://github.com/tricore-opentrix/opentrix/pull/150), Bảo/Ánh, `0b4c79f1935db6974ac7b425e586110a229a9036`). Formal reviews are on the linked PRs and name those exact HEADs. The #151 approval covers only the routing correction, so the underlying #143 register, declarations-routing document and gates remain `In Review`. These approvals do not decide source rights; later changes require fresh review.

## PR and immutable HEAD evidence

The table reflects live PR metadata inspected for this inventory; [#139's body](https://github.com/tricore-opentrix/opentrix/pull/139) still says its head was `315d6754…`, so that prose is historical. Each CSV source URL pins the actual file to the HEAD below and records the fetched Git blob SHA-1.

| PR | Containing branch | State | Draft | Current HEAD |
| --- | --- | --- | --- | --- |
| [#139](https://github.com/tricore-opentrix/opentrix/pull/139) | `docs/infra-r24-rc1-source-acceptance` | OPEN | Draft | `2f6b8d7608214983be92db1f5ba0e4b8703885db` |
| [#142](https://github.com/tricore-opentrix/opentrix/pull/142) | `docs/r27-identity-provenance-evidence` | OPEN | Draft | `2844530125ef884a047f976a91b3202103da3c91` |
| [#143](https://github.com/tricore-opentrix/opentrix/pull/143) | `docs/r27-rights-packages-20261107` | OPEN | Draft | `6cb5a32897563df018cf79dd66b92a20a3e823f1` |
| [#144](https://github.com/tricore-opentrix/opentrix/pull/144) | `docs/r27-anh-rights-disposition-20261107` | OPEN | Draft | `188969ada812e0016ed952b5ad422e210b9b0055` |
| [#146](https://github.com/tricore-opentrix/opentrix/pull/146) | `docs/r27-document-register-20261107` | OPEN | Draft | `8492abd20e3e7fe00ad18d687f4674fa339fe20c` |
| [#147](https://github.com/tricore-opentrix/opentrix/pull/147) | `docs/r27-step4-status-id-vocabulary-20261107` | OPEN | Draft | `94a998978e811a546fdd7a8840af3e4b9686f286` |
| [#148](https://github.com/tricore-opentrix/opentrix/pull/148) | `docs/r27-step5-license-notice-handoff-20261107` | OPEN | Draft | `25faa214835093d591eb381be910e1efc1b8c085` |
| [#149](https://github.com/tricore-opentrix/opentrix/pull/149) | `docs/r27-step6-contributor-provenance-20261107` | OPEN | Draft | `329670d5768c34020828523c65a321494a5b1518` |
| [#150](https://github.com/tricore-opentrix/opentrix/pull/150) | `docs/r27-s6-01-02-identity-evidence-20261107` | OPEN | Draft | `0b4c79f1935db6974ac7b425e586110a229a9036` |
| [#151](https://github.com/tricore-opentrix/opentrix/pull/151) | `docs/r27-s6-13-register-routing-20261107` | OPEN | Draft | `146ff78f3ea0f177b5dbb712679971dbd61302e0` |
| [#152](https://github.com/tricore-opentrix/opentrix/pull/152) | `docs/r27-s6-13-matrix-routing-20261107` | OPEN | Draft | `4618777ce3525afe63a45cb67f99363f20ed26d1` |
| [#153](https://github.com/tricore-opentrix/opentrix/pull/153) | `docs/r27-yen-git-blob-evidence-20261107` | CLOSED, unmerged | Draft | `fde4159d324bfe483aa083074923b3ad1bf94ecd` |
| [#154](https://github.com/tricore-opentrix/opentrix/pull/154) | `docs/r27-anh-git-blob-crosswalk-20261107` | OPEN | Draft | `fcc146370b1c5f1dbbba0747143e9dc3b9184f23` |
| [#155](https://github.com/tricore-opentrix/opentrix/pull/155) | `docs/r27-yen-group-c-content-reconciliation-20261107` | OPEN | Draft | `47ac885fcdf0cd09453aca1413753afaa47828cc` |
| [#157](https://github.com/tricore-opentrix/opentrix/pull/157) | `lexuanbao258-collab-patch-1` | OPEN | Draft | `59e66e570fda14ea050076cf67555faf76581db7` |

The Register's #143 links point to `6cb5a32897563df018cf79dd66b92a20a3e823f1`, while the three affected files now also exist in #151 at `146ff78f3ea0f177b5dbb712679971dbd61302e0`. Its #149 links point to `329670d5768c34020828523c65a321494a5b1518`, while the two affected files now also exist in #152 at `4618777ce3525afe63a45cb67f99363f20ed26d1`. All five successor blobs differ from their predecessor blobs; their routing changes are material to reviewer assignment while preserving pending rights. #146 does not include `R27-EVD-007` or the later #153–#157 records. #147's companion index link pins an older #146 revision. These links remain useful historical references but are not the latest affected revision. All files were independently fetched at their CSV commits; no pinned-file path failed. The current `main` tree at the frozen SHA contains none of the 51 listed repository files.

## Independence, blockers and ambiguous artifacts

**One active reviewer-conflict case:** the surviving release-summary prose portion of `CHANGELOG.md` associated with mixed commit `44283466f1747d55ed39e782d0600e8d09a28427`. [#151's independent routing review](https://github.com/tricore-opentrix/opentrix/pull/151) and [#152's companion correction](https://github.com/tricore-opentrix/opentrix/pull/152) leave Ánh eligible only if she did not contribute to that exact prose; otherwise retain `REVIEWER_CONFLICT — REROUTING_REQUIRED` and appoint another reviewer. **Yến, as R27B coordinator, owns the follow-up to identify the prose contributors and record the reroute.** Bảo must not review his own archive contribution, Yến must not clear hers, and Ánh must not clear hers. The [S6-13 Bảo statement](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6706817105), [Yến statement](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6706970135), and [Ánh's scoped review](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6707061030) provide routing evidence, not blanket clearance.

**UNMAPPED_OR_AMBIGUOUS_ARTIFACTS:** No inspected file is unassigned to a proposed package. Two Issue #138 contributor-evidence records have no repository path; they are intentionally represented as comment URLs. The historical R25 exception CSV exists at `35e90c47` but not frozen main, and its current approval status is unknown. The 35 supporting artifact rows without a distinct register ID retain blank `document_id`; they are not silently promoted to mandatory documents. #153 is closed unmerged, while #155 supplies a narrower Group C content successor; both remain traceable. Seven CSV REUSE sidecars share one byte-identical blob SHA (`a169633c210caee3c5423dc6a8a76de449ab87e3`); these are metadata companions, not duplicate substantive documents. Other artifact blobs are distinct. File content overlaps by reference (same frozen blobs and 357 rights rows), but technical ledger, declarations, decision queue, and final report have materially different functions.

Unresolved evidence includes first-person per-file/portion authority, external examples and fixtures, favicon/assets, Gradle Wrapper and build metadata, generated SBOM/NOTICE provenance, 37 R25 exceptions, and mixed-hunk independence. `UNKNOWN` and `NOT_RECALLED` remain unresolved. The latest rights register still has **357/357 `RIGHTS_PENDING`** according to [#151's exact-HEAD review](https://github.com/tricore-opentrix/opentrix/pull/151). [#157](https://github.com/tricore-opentrix/opentrix/pull/157) reports technical archive PASS but has Yến's changes-requested review; Step 2 acceptance remains pending. [#138](https://github.com/tricore-opentrix/opentrix/issues/138) remains OPEN and [#139](https://github.com/tricore-opentrix/opentrix/pull/139) remains Draft/BLOCKED.

## Status interpretation and completeness

Only these independent axes are used: document `Planned | Draft | In Review | Approved | Superseded`; evidence `NOT_VERIFIED | PARTIAL | PASS | FAIL`; rights `PENDING | REMEDIATION_REQUIRED | CLEARED | EXCLUDED | NOT_APPLICABLE`. Blank document status in the CSV means **UNKNOWN in these notes**, not a sixth approved value. The CSV preserves legacy `RIGHTS_PENDING` in blockers rather than rewriting the source register. CI/REUSE and SPDX metadata describe checks and labels, not ownership or redistribution authority. Git authorship and blob provenance are technical evidence only.

For the **19 identified IDs** (18 in the Register including its own header, plus `R27-EVD-007`), this inventory records **7 documentation Approved, 11 In Review, 1 UNKNOWN**, based on scoped current reviews and unresolved historical status. There are only **18 CSV rows carrying an ID** because the Bảo checkpoint row carries both `R27-DEC-002` and `R27-EVD-003`; status counts expand that cell into two IDs. All **53 rows** have exactly one proposed package. **51 file artifacts** have fetched immutable blob IDs; **2 issue-comment artifacts** have no file path. **0 duplicate distinct IDs**, **0 unsupported mapped file paths**, **0 unassigned artifacts**, and **1 active portion-level reviewer-conflict case** were found. The source-rights register remains unchanged, with **357 unresolved rights rows**; this count is a source-row measure and must not be added to the 53 artifact rows. There is no overall completion percentage.

### Reconciled audit findings

| Field | R27B-01 | R27B-02 |
| --- | --- | --- |
| FINDING_ID | R27B-01 | R27B-02 |
| FILE | This inventory and companion CSV | Companion CSV and this inventory |
| ROW_OR_LINE | Executive summary count; R25 exception row | Shared Bảo checkpoint row; completeness count |
| EXPECTED | Distinguish PR paths, historical paths and issue comments | Count distinct IDs separately from artifact rows |
| ACTUAL | 50 PR paths + one R25 path + two comment records | 19 IDs occupy 18 ID-bearing rows |
| EVIDENCE | Current PR file lists; historical R25 blob `613351b7cb62698308d0112fb57caa5537295abf` at `35e90c47`; 53 CSV records | Register's 17 table IDs + self ID, #150 `R27-EVD-007`; one checkpoint has `R27-DEC-002; R27-EVD-003` |
| FIX | State 51 unique paths / 51 pinned revisions and exclude three inventory output files | Preserve both IDs on the one actual file row and expand ID-level status counts |

Local validation for these inventory files: strict UTF-8 decode, rectangular 23-column CSV, ID/path/revision uniqueness, immutable URL structure, status enums, formula-prefix scan, and relative Markdown links passed. `python -m reuse lint-file` passed separately for the Markdown, CSV and CSV sidecar. Repository-wide `python -m reuse lint` fails on an invalid SPDX expression already present in frozen-baseline `scripts/r23-compliance.py`; this unrelated file was not changed. The three new files use `SPDX-FileCopyrightText: NOASSERTION` to avoid attributing copyright to a person or collective without evidence; the Apache-2.0 tag applies to these new inventory artifacts, not to source rights under review.

## Bảo and Ánh scope review checklist

- [ ] Reconcile all 17 Register table IDs, its self ID, and new `R27-EVD-007`; accept or correct the proposed grouping into exactly nine packages without renaming original IDs.
- [ ] Check each CSV path, blob, PR state and current HEAD; flag old #139 body and #143/#149/#146 cross-links before relying on them.
- [ ] Confirm which contributor made each substantive portion, especially Identity G3/G4, Backend/Gateway, mixed Data tests, favicon/templates, and `44283466` CHANGELOG.
- [ ] Independently reproduce bounded archive/blob evidence and identify missing direct declarations, upstream licenses, NOTICE and fixture provenance.
- [ ] Route each source-rights decision to a noncontributor for that exact portion; record rerouting when Bảo, Ánh or Yến contributed.
- [ ] Confirm the draft handoff and documentation approvals do not set `CLEARED`, close #138 or authorize the R24 release.

## Decision required

Yến, Bảo and Ánh need to review whether these nine **groupings of existing records** are the intended R27B package scope, whether any supporting artifact should receive its own formal document ID, and whether the mixed-portion reviewer route requires another person. Until an explicit scope decision is recorded, retain `NINE_PACKAGE_SCOPE_PROPOSED — NOT YET APPROVED`.

**Verdict:** `INVENTORY READY FOR INDEPENDENT REVIEW` — inventory readiness only; source rights and release remain pending.
