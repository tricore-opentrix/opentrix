<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# R27 Step 6B — Yến Git history / frozen blob technical evidence

**Date:** 2026-11-07  
**Repository:** `tricore-opentrix/opentrix`  
**Frozen R24 source:** `187dbd2ea6935966f5c4cceb95ad9c3c53708a2e`  
**Status:** `PARTIAL_TECHNICAL_VERIFICATION / HUNK_RECONCILIATION_PENDING / RIGHTS_PENDING`  
**Rights Register:** 347 tracked paths + 10 archive metadata rows; **357/357 RIGHTS_PENDING** (last recorded checkpoint).  
**Scope disclaimer:** This is a technical evidence report, **not** a 249-path exhaustive reconciliation, independent source-rights verdict, new contributor declaration or legal clearance. Draft PR publication of this report does not change frozen source or R24 acceptance.

## 1. Verified in this pass

- GitHub source files were fetched at the **exact frozen commit**; **15/15 S6-10 Group C paths returned blob SHA-1**, including 13 substantive files and two `.gitkeep` placeholders. Full blobs and immutable links are recorded in [Yến's crosswalk](yen-git-blob-crosswalk.csv).
- Additional frozen blobs: `CHANGELOG.md`, `LICENSE`, `NOTICE`, `REUSE.toml`, `README.md`, `.github/workflows/ci.yml`, `scripts/r24-release.py` — **7/7 found**.
- Fetched [commit `44283466`](https://github.com/tricore-opentrix/opentrix/commit/44283466f1747d55ed39e782d0600e8d09a28427). Its patch includes substantive Group C additions and CHANGELOG prose. Existing scoped evidence counts **126 changed paths**: Backend 23, Frontend 80, Portal BFF 14, Scripts 6, Docs 2, CHANGELOG 1. **Commit inventory is not surviving-hunk attribution or copyright evidence.**
- `backend/src/main/resources/db/helpdesk/policy-schema.sql` explicitly describes code **copied from the V5 physical candidate**; `schema.sql` describes reuse of V5 tables/constraints. This is source-lineage evidence requiring a clause-by-clause check, **not** proof of a complete match.
- `LICENSE` reproduces upstream Apache License 2.0; Yến's associated addition does not imply authorship of its text. `NOTICE` retains collective TRICORE attribution with unresolved individual authorization. `CHANGELOG` refers to Keep a Changelog / SemVer; references do not themselves prove copied prose.
- The later Draft PR #142 document `docs/verification/r27/identity-contributor-declaration-yen.md` was **not found at the earlier frozen source**, which does not mean an Identity source file is missing.

## 2. Case-by-case evidence boundaries

### S6-01/02/03 — Identity

[Draft PR #142](https://github.com/tricore-opentrix/opentrix/pull/142) reports a 39-record technical investigation with 37 Java blob matches at a separate earlier audit SHA and 14-file historical reconciliation. **This pass did not re-fetch all Identity paths at frozen `187dbd2…` or fully reconcile surviving hunks.** Fourteen historical Codex calls remain `PATCH_EXECUTION_UNKNOWN`; external examples, fixtures and NOTICE obligations remain unresolved. Bảo's two `package-info.java` and two Gateway test portions must not be assigned to Yến solely by file grouping.

### S6-10 — Backend Group C (15 paths)

All **15 frozen blobs found**; the Git/account association to `44283466` (13 substantive paths) and historical placeholder commits (two `.gitkeep`) was previously mapped in [Issue #138, comment 6707584039](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6707584039). **Yến's actual create/prompt/edit role remains `NOT_RECALLED`** under her direct consolidated statement, notwithstanding account attribution. Original and later expressive hunks and other participants were **not exhaustively reconciled**. Yến's narrower statement of noncreation in Application code must not be silently extrapolated to all other participation types or resolved without evidence. Prior technical accounting does not prove rights.

### S6-11 — Root docs / governance / CI / scripts / infra (82 paths)

[Historical Git path inventory](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6707439947) covers 82 paths: 13 root, 7 governance/CI, 33 project docs, 25 infrastructure, 4 release tooling. It is **not** 82 fully reconciled surviving portions. This check retrieved seven selected frozen blobs only, with overlap across S6-11/S6-13. Bảo separately described contributions in 46 paths. Keep mixed README, CI, NOTICE, CHANGELOG and Keycloak PoC per-hunk; Yến's `fa16f30d` SPDX additions must not be treated as original code authorship.

### S6-12 — Historical 37 exceptions

**No exhaustive fresh path-by-path candidate check** in this pass. Preserve Bảo's nine-path statement, Yến's `NOT_RECALLED` for the rest, Gradle upstream provenance, and Flyway V1–V4 immutable checksums. The Gradle Wrapper JAR is excluded from the R24 source-only archive; included wrapper scripts/properties still have upstream obligations.

### S6-13 — LICENSE / NOTICE / CHANGELOG and archive members

Directly fetched three tracked input blobs. The **ten archive metadata members** remain separate register records, not additional frozen tracked source paths. PRs [#151](https://github.com/tricore-opentrix/opentrix/pull/151) and [#152](https://github.com/tricore-opentrix/opentrix/pull/152) have routing-only review and exact-HEAD CI evidence recorded in [Issue #138](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6707336136); these **are not** rights approvals. Yến/Bảo/Ánh CHANGELOG prose boundaries, upstream notices and collective attribution authority remain pending.

## 3. Commit `44283466`: reviewer-independence boundaries

| Portion | Evidence already recorded | Current reviewer disposition |
| --- | --- | --- |
| Frontend (80) | Ánh reports AI/Codex-directed implementation; Yến expressly disclaims creating, prompting or editing Frontend including this commit | Yến **possible**, only after confirming no substantive involvement in exact hunk |
| Backend (23) | Yến actual creative role `NOT_RECALLED`; Ánh reports AI-directed corrections; Bảo `NOT_RECALLED` | `NEEDS_PORTION_MAPPING` |
| Portal BFF (14) | Ánh explicitly corrected prior account to **review-only**, no create/prompt/edit; Yến/Bảo roles unresolved | `REVIEW_ONLY_DECLARATION_RECORDED`; independence conditional |
| Scripts (6), Docs (2) | Yến confirms ChatGPT use without exact file activity; Ánh describes general AI workflow only for actual portions | `NEEDS_HUNK_MAPPING` |
| CHANGELOG (1) | Ánh confirms requesting AI prose; Yến/Bảo portions uncertain | `PORTION_INDEPENDENCE_PENDING`; outside reviewer may be needed |

**Do not use** author, squash or `Co-authored-by` metadata to substitute for actual participation or reviewer independence.

## 4. Nonduplicated blockers

| ID | Unresolved finding | Next evidence |
| --- | --- | --- |
| Y-GH-01 | `44283466` surviving-hunk mapping incomplete | Compare actual candidate portions to introduction and later modifications; reconcile Bảo/Ánh/Yến statements |
| Y-GH-02 | Group C 15-path creative role `NOT_RECALLED` | Independent documentary investigation; do not invent a recollection |
| Y-GH-03 | V5-to-Helpdesk SQL copy/reuse | Match exact source statements, clauses, historical commits and rights |
| Y-GH-04 | S6-11 82-path history lacks full surviving-hunk mapping | Differentiate code/prose changes, SPDX, reused/generated material |
| Y-GH-05 | Identity exact frozen-path, fixture and AI execution checks incomplete | Carry earlier evidence forward to candidate-specific portion checks |
| Y-GH-06 | Remaining historical exceptions and upstream obligations | Separate candidate-present, historical-only, archive-excluded and upstream metadata |
| Y-GH-07 | Collective NOTICE authorization / mixed CHANGELOG independence | Identify actual author/prompt/reviewer per surviving expression and seek noncontributor review |

## 5. Technical exit criteria

1. Each in-scope frozen path has a full candidate blob SHA or explicit absent/historical-only disposition; do not conflate candidate contents with archive membership.
2. Each **substantive surviving portion** is traced to actual historical content commits; metadata-only and file-mode changes are separated.
3. Each contributor assertion is constrained to a personally confirmed declaration. Preserve `UNKNOWN` and `NOT_RECALLED` with scoped blockers.
4. Reviewer independence is tested **per portion**, excluding actual substantive contributors; unresolved cases request an eligible outside reviewer.
5. Technical verification and source rights are separate gates. Do not change Rights Register `RIGHTS_PENDING` or R24 `BLOCKED` based on this document.

**Verdict:** `22/22 SELECTED FROZEN BLOBS FOUND / GROUP C 15/15 BLOB FOUND / SURVIVING-HUNK COMPLETENESS NOT ACHIEVED / RIGHTS_PENDING / NO CLEARED`.

## Evidence index

- [Issue #138](https://github.com/tricore-opentrix/opentrix/issues/138)
- [Yến Group C history mapping](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6707584039)
- [S6-11 82-path inventory](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6707439947)
- [Yến approved declaration](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6708631841)
- [Bảo declaration](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6707960117)
- [Ánh declaration and corrected Portal BFF role](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6708767215)
- [Draft rights register #143](https://github.com/tricore-opentrix/opentrix/pull/143)
- [Step-6 queue #149](https://github.com/tricore-opentrix/opentrix/pull/149)
