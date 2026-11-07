<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# R27 Step 6B — Yến Group C exact content reconciliation

**Scope:** S6-10 Group C, 15 previously enumerated Yến-account-associated paths  
**Candidate frozen SHA:** `187dbd2ea6935966f5c4cceb95ad9c3c53708a2e`  
**Comparison reference:** commit `44283466f1747d55ed39e782d0600e8d09a28427` for 13 code/SQL paths; `adcd1f72` and `05f01472` for the two placeholders.  
**Evidence source:** Direct GitHub `fetch_file` at each reference (full content, not just file-name inventory).  
**Status:** `CONTENT_COMPARISON_VERIFIED_15_OF_15 / CONTRIBUTOR_ROLE_NOT_RECALLED / RIGHTS_PENDING`

## Result

| Technical comparison | Files | What was verified |
| --- | ---: | --- |
| Exact byte-equal blob across references | **6** | Four Helpdesk SQL files, two historical `.gitkeep` placeholders |
| Identical substantive file content after removing the exact *new leading SPDX header* | **9** | Four Helpdesk Java, two Authorization Java and three corresponding Java test files |
| **Total compared** | **15** | All 15 Group C paths previously listed in Yến's technical crosswalk |

The **nine Java/test** files have changed frozen blobs **only** because of the four-line leading SPDX comment + separator relative to commit `44283466`; the rest of their text compares byte-for-byte identical. The **four SQL** files and **two `.gitkeep`** files have identical historical/frozen blob hashes. Full historic/frozen blob pairs and GitHub links are in [the 15-row CSV](yen-group-c-15-path-content-reconciliation.csv).

The result supports **technical survival of the exact historic *content*** for these fifteen paths at the frozen commit. It does **not** establish which human prompted, generated, authored, edited, tested, integrated or reviewed those bytes. In particular, a Git account associated with `44283466` is not copyright title. Yến's first-person Group C creative role remains `NOT_RECALLED` per [her approved declaration](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6708631841).

## Important source-lineage blockers

- `backend/src/main/resources/db/helpdesk/policy-schema.sql` explicitly says it was **copied from the V5 physical candidate**, and `schema.sql` notes V5 table/constraint reuse. **The original V5 lines and licensing authority have not yet been compared clause by clause**.
- The `44283466` integration contains other Backend/Frontend/Portal/Scripts/Docs/CHANGELOG paths outside these fifteen. **No clearance or comprehensive per-line blame claim is made** for those portions.
- Full Step-6 scope still includes Identity S6-01/02/03, S6-11 history, 37 S6-12 exceptions, and S6-13/upstream obligations; no completeness claim extends to them.
- Bảo's [fresh technical crosswalk](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6709387409) is **separate evidence**, not automatically adopted as a human-author attribution. It describes mixed portions and two historical-only controllers outside this 15-path group; these still require joint portion-level reconciliation.
- Ánh's corrected **Portal BFF review-only** declaration remains in force for the portions she identified. This technical check does not evaluate her reviewer eligibility.

## Independent technical review requests

1. Recompute historic and frozen blob SHA-1 for all 15 rows from the two refs; reproduce the four-line SPDX stripping match for nine Java/test paths.
2. Trace `policy-schema.sql` and `schema.sql` to actual V5 source blobs and exact reused lines, without mutating checksum-pinned Flyway migrations.
3. Check reviewer conflicts by *actual participation* and source history, not by Git author or Co-authored-by trailer. If unavailable, retain `UNKNOWN` / `NOT_RECALLED`.
4. Keep the matrix/register `RIGHTS_PENDING` until a separately evidenced, independent rights decision.

**R27 disposition:** `GROUP_C_CONTENT_SURVIVAL_TECHNICALLY_VERIFIED / V5_SOURCE_LINEAGE_PENDING / CONTRIBUTOR_INDEPENDENCE_PENDING / RIGHTS_PENDING`. No source change, merge, tag, legal rights clearance or R24 release authorization is implied.

**Related:** [Issue #138](https://github.com/tricore-opentrix/opentrix/issues/138), [Bảo crosswalk](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6709387409), [Yến initial 22-blob technical evidence](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6709537553), [PR #143](https://github.com/tricore-opentrix/opentrix/pull/143), [PR #149](https://github.com/tricore-opentrix/opentrix/pull/149).
