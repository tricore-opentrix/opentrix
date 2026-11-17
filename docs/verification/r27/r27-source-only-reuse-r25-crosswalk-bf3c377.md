<!--
SPDX-FileCopyrightText: NOASSERTION
SPDX-License-Identifier: Apache-2.0
-->

# R27 / #138 — REUSE annotations × R25 historical exceptions, current SOURCE-ONLY file/blob crosswalk

**Document state:** `DRAFT_TECHNICAL_CROSSWALK / RIGHTS_PENDING / INDEPENDENT_REVIEW_REQUIRED` — **not a legal clearance, not independent approval, not release authorization**.

**Reference:** [Issue #138](https://github.com/tricore-opentrix/opentrix/issues/138) · [release gate #190](https://github.com/tricore-opentrix/opentrix/issues/190).
**Exact audited main SHA:** `bf3c377bef5a320803b6202781f78a6f50ff0939` (not a frozen release SHA).
**Sources:** [current REUSE.toml](https://github.com/tricore-opentrix/opentrix/blob/bf3c377bef5a320803b6202781f78a6f50ff0939/REUSE.toml) (Git blob `36fbfe9949a7bf40ad2682e5703b83c832693d4a`), [R25 37-path historical exceptions](https://github.com/tricore-opentrix/opentrix/blob/35e90c47/docs/verification/r25/exception-review.csv) (blob `613351b7cb62698308d0112fb57caa5537295abf`), [historical R27 357-row Rights Register](https://github.com/tricore-opentrix/opentrix/blob/6cb5a32897563df018cf79dd66b92a20a3e823f1/docs/verification/r27/r27-rights-remediation-register-187dbd2.csv) (blob `db9a7e3af8f577a1bc11c72c03c37b833d3b21d1`), [current Git tree](https://github.com/tricore-opentrix/opentrix/tree/bf3c377bef5a320803b6202781f78a6f50ff0939).
**Machine-readable, file-specific evidence:** [r27-source-only-reuse-r25-crosswalk-bf3c377.csv](r27-source-only-reuse-r25-crosswalk-bf3c377.csv) — full 40-hex `main_git_blob_sha1`, historical `git_blob_sha1`, Git mode, path sets, scope, reviewer routing, pending disposition and evidence URLs.

## 1. Exact set reconciliation

| Criterion | Exact count |
| --- | ---: |
| `REUSE.toml` file annotations at audited HEAD | **28** |
| REUSE-annotated paths in planned SOURCE-ONLY tracked text archive | **27** |
| R25 historical exception paths | **37** |
| R25 historical exceptions still included in planned SOURCE-ONLY tracked text archive | **29** |
| Intersection: current REUSE-annotated ∩ R25 historical included | **17** |
| Current REUSE-only, not among R25 included exceptions | **10** |
| R25 historical-only, not in current included REUSE annotations | **12** |
| **Total distinct current in-scope paths, file-by-file row required** | **39** |
| Old R27 rights register blob unchanged at current SHA | **30 / 39** |
| Old R27 rights register blob **changed** at current SHA | **9 / 39** |
| R25 historical paths excluded/absent from current source archive | **8** |
| **Total CSV rows = 39 in scope + 8 historical excluded** | **47** |

**Scope method:** Used current Git tree at the exact above SHA, Git-tracked file paths, and `scripts/r24-release.py` SOURCE-ONLY extension exclusions (the original `main` packager). `EXPECTED_SELECTED_SOURCE` means *expected by the source selection algorithm*, not evidence of a final release tarball or frozen SHA. The current `main` tracked tree has **413 blob paths**; one non-text Gradle Wrapper JAR is omitted by the SOURCE-ONLY filter, yielding **412 expected source paths** and **10 generated archive-only ancillary members**. The 39-path crosswalk is a **subset** of that package, not a completeness determination for all 412 or metadata members.

### 1.1 Nine historical blob revisions replaced since R27 register

| Current path | R27 historical Git blob SHA-1 | Git blob SHA-1 at `main@bf3c377` | Rights consequence |
| --- | --- | --- | --- |
| `.env.example` | `0d397fce3d637afa6b0a2510f2134f07a303e702` | `8b8c65ccb7c0bf7ac1abf0a4eb3ad941bb60a8d5` | `RIGHTS_PENDING` — require renewed current-content review |
| `.github/CODEOWNERS` | `e95e855fa0232950152d412b1a6d8b24e9896b2c` | `b7078b322b968ba11a67f9d5bd5429013479ffe8` | `RIGHTS_PENDING` — require renewed current-content review |
| `.gitignore` | `9438fc29158a0d655656787c8b7b6a7c3d45bff7` | `b36298fc6c2fa4fb25aaa14b31f912fce4282d7d` | `RIGHTS_PENDING` — require renewed current-content review |
| `NOTICE` | `35e2751e39895078b241f3ef342c406adcc84856` | `8c81c700d4a7f36c0f4dd2bbcbe938f4efea693e` | `RIGHTS_PENDING` — require renewed current-content review |
| `README.md` | `0a81dd3cc6a55efd288b0fe06213d62aa684cbfe` | `599174c0bfe5be59cecc03a2698c3bdf30fc35d9` | `RIGHTS_PENDING` — require renewed current-content review |
| `frontend/.gitignore` | `326fe72a26da191eb1c68dd8eb017bec059043f0` | `aec2e870e33cce6801f94a42a976c714c602db46` | `RIGHTS_PENDING` — require renewed current-content review |
| `frontend/index.html` | `2784caa91845578bfbbb00b8f60a55ae30e9636f` | `9934301557f0b4de9e20cb0f9126bdea1d33c3a4` | `RIGHTS_PENDING` — require renewed current-content review |
| `frontend/package.json` | `5bdf1add8c67f25814ce914a0c8718bb28036a25` | `d8243e2dc72021745c9ac8ee2751ad6704c4d1a2` | `RIGHTS_PENDING` — require renewed current-content review |
| `scripts/setup-github.sh` | `87ee8548df32bbbbc22baf18f3467748234d0177` | `d18f9573b4799792cac3b28689ed10bfe500d810` | `RIGHTS_PENDING` — require renewed current-content review |

The old blob evidence is **historical** for these nine paths. Review exact live content/current deltas before assigning source-rights/NOTICE disposition; matching Git authorship or CI does not prove authority.

### 1.2 Eight original R25 paths not packaged in the current source-only boundary

| R25 path | Reason | Current Git blob |
| --- | --- | --- |
| `backend/gradle/wrapper/gradle-wrapper.jar` | tracked binary excluded by packager | `1b33c55baabb587c669f562ae36f953de2481846` |
| `docs/03-applications/facility/.gitkeep` | absent from current HEAD | — |
| `docs/03-applications/helpdesk/.gitkeep` | absent from current HEAD | — |
| `docs/04-integration/.gitkeep` | absent from current HEAD | — |
| `docs/05-testing/.gitkeep` | absent from current HEAD | — |
| `docs/07-open-source/.gitkeep` | absent from current HEAD | — |
| `docs/10-reviews/.gitkeep` | absent from current HEAD | — |
| `docs/11-poc/.gitkeep` | absent from current HEAD | — |

**Important:** Gradle Wrapper JAR is excluded from v0.2.0 SOURCE-ONLY, but still has third-party/upstream license obligations if distributed separately or in binary modes; no global rights clearance is asserted. The seven removed documentation placeholders are historical evidence only and not release inputs at this SHA.

## 2. Required source-rights review, not automatic `CLEARED`

Every one of the **39 expected packaged crosswalk paths** remains `RIGHTS_PENDING`. The historical R27 register does not contain a verified legal disposition to carry forward. This technical row-level crosswalk records **path/blob existence, scope, historical category and reviewer routing**, but no new first-person licensing grant or acceptance. Historical `EXTERNAL_ORIGIN_UNKNOWN` stays `UNKNOWN`; contributor `NOT_RECALLED` facts remain `NOT_RECALLED`.

1. **Gradle upstream — 3 packaged paths:** `backend/gradlew`, `backend/gradlew.bat`, `backend/gradle/wrapper/gradle-wrapper.properties`. Verify actual upstream source/Apache license and NOTICE, check `TRICORE contributors` REUSE copyright attribution on properties, confirm appropriate metadata correction through reviewed PR. Wrapper JAR itself is *excluded*, not `CLEARED`. [Bảo's scoped statement](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6706884881).
2. **Flyway V1–V4 + workflow manifest:** Do **not** edit checksum-sensitive migration SQL bytes. Check the exact blob SHA for each and original/prompt/upstream origin with Bảo's scoped disclosure; resolve Apache/NOTICE via separate metadata/review where needed. AI-assisted origin reported ≠ independent copyright clearance.
3. **Two nonempty Backend application `.gitkeep`:** The historical R27 register routes these to Bảo, but [Bảo's S6-12 statement](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6706884881) says **Yến created** them. Route creator evidence to Yến with Ánh as *proposed* independent reviewer; do not silently copy the old ownership assumption. Other empty placeholders require verification but should not be assigned unearned authorship.
4. **Frontend favicon:** `frontend/public/favicon.svg` at blob `2faa0e08edb86261c960119f997703f70849477b` matches Ánh's prior inspected exact blob. Reuse Ánh's existing statement of ChatGPT text-prompt generation and limited authorization **only within her rights**; external fragment origin/NOTICE remain `UNKNOWN / RIGHTS_PENDING`. [Ánh's statement](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6924596147). Do not ask her to re-attest Q1–Q5.
5. **Other REUSE-only paths (10), R25-only paths (12):** Inspect actual files and contributors separately; REUSE annotations do not substitute for third-party rights findings. In particular root README/NOTICE, frontend package metadata, scripts, offline Helpdesk SQL and root configuration may require updated attribution and exact-hunk routing. The original R27 source registers are unmerged **historical evidence**, not live approved dispositions.

**Reviewer assignment is proposed routing, not proof of independence.** Yến coordinates #138; Yến reviews Bảo/Ánh portions where independent; Ánh reviews Yến-created portions; Bảo reviews Yến-coordinated metadata only where he did not substantively contribute. For mixed portions, route to a genuine noncontributor. Independent reviewer must record a concrete `APPROVE / REQUEST_CHANGES / BLOCKED` finding on the **exact current blob and portion** with evidence and any remediation PR. Do not silently mark `CLEARED`.

## 3. Additional SOURCE-ONLY assets/fixtures outside the 27 × 29 set

These **are selected tracked text paths in the planned archive**, but **not members of the 39-path crosswalk**. Their absence from R25 exceptions/REUSE annotations **does not clear their rights**. Findings from [Ánh's asset review](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6923805209) and [supplement](https://github.com/tricore-opentrix/opentrix/issues/138#issuecomment-6924596147):

| Current file | Exact current blob SHA-1 | Origin/rights status | Grounded finding |
| --- | --- | --- | --- |
| `frontend/src/assets/opentrix-clover.svg` | `db4a1fca27f3f4bb2f12873b6e290e48afa19a61` | UNKNOWN / RIGHTS_PENDING | Ánh AI-assisted; Yến supplied concept; input references unverified |
| `infra/keycloak/themes/opentrix/login/resources/img/opentrix-clover.svg` | `db4a1fca27f3f4bb2f12873b6e290e48afa19a61` | UNKNOWN / RIGHTS_PENDING | Byte-identical Clover asset; shared-portion attribution requires independent review |
| `infra/keycloak/themes/opentrix/login/resources/img/opentrix-helpdesk-illustration.svg` | `d9232b10aa53858c7493f947ce57e42e78fe7ccc` | NOT_RECALLED / RIGHTS_PENDING | Ánh explicitly does not recall provenance |
| `frontend/src/fixtures/requests.ts` | `f62e2d02b9d2deba938bbcc7986af89776f72005` | UNKNOWN / RIGHTS_PENDING | Fixture author and dataset provenance not substantiated |
| `frontend/src/test/helpdeskFixtures.ts` | `bb162b45e62307d9083e1acfcc36b92862da3ac8` | UNKNOWN / RIGHTS_PENDING | Fixture author and dataset provenance not substantiated |
| `frontend/tests/integration-local-fixture.ts` | `e3cd20de98e17c46d4aa67f0a6770f5b8f9822fb` | UNKNOWN / RIGHTS_PENDING | Fixture author and dataset provenance not substantiated |

Treat both Clover SVG copies as the same current blob but distinct packaged paths. Yến's role in ideation and Ánh's AI-assisted generation are reported, not a verified upstream/originality clearance. `infra/keycloak/.../opentrix-helpdesk-illustration.svg` specifically remains `NOT_RECALLED`. Fixtures remain `UNKNOWN` until actual contributors/inputs are verified. User-supplied screenshot is not assumed to be the illustration SVG.

## 4. Next actions, gates, and baseline drift

- **Yến / #138:** coordinate file-level source rights and attribution decisions, verify `TRICORE contributors` label authority, NOTICE, source library/fixture lineage, and distinguish authorship vs Git history; do not re-collect Q1–Q5.
- **Bảo:** supply exact current-blob crosswalk, upstream Gradle/Flyway findings and evidence; verify which updates changed the nine paths; independent sign-off is required.
- **Ánh:** independently review Yến-owned portions she did not contribute, and route Frontend/asset/fixture rights to a truly independent reviewer.
- **Before any `CLEARED`:** attach license/source authority evidence **or** reviewed attribution change / replacement / explicit exclusion for the *actual source-archive member*; update full Git SHA and blob after any PR merge. Unknowns are not legalized by omission.
- **If PR #249 or another PR changes `main`:** regenerate crosswalk against the new exact HEAD before source freeze; this document is **HEAD-bound evidence**, not evergreen release authorization.
- **No release action:** `SOURCE_FREEZE_BLOCKED / RELEASE_NOT_ACCEPTED`; keep #138/#190 open, source-only/binary scopes distinct; no final R4 candidates, no tag, Release or GHCR.
