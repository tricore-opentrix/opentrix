<!--
SPDX-FileCopyrightText: NOASSERTION
SPDX-License-Identifier: Apache-2.0
-->

# R27 / #138 — SOURCE-ONLY REUSE × R25 exceptions crosswalk at exact main c515708c

**Status:** `CURRENT_BASELINE_TECHNICAL_CROSSWALK / RIGHTS_PENDING / INDEPENDENT_REVIEW_REQUIRED`. **No legal rights clearance, source freeze, final R4 acceptance or release authorization.**

**Audited source SHA:** `c515708c934f5bd9be86081b786bcb96f16a52a5` (the merged `#252` state; not a frozen release SHA). This is a **new independent snapshot**; the historical `bf3c377` crosswalk is preserved [unchanged except whitespace hygiene](r27-source-only-reuse-r25-crosswalk-bf3c377.md) with its [original CSV](r27-source-only-reuse-r25-crosswalk-bf3c377.csv).

**Evidence links:** [exact Git tree](https://github.com/tricore-opentrix/opentrix/tree/c515708c934f5bd9be86081b786bcb96f16a52a5) · [current packager](https://github.com/tricore-opentrix/opentrix/blob/c515708c934f5bd9be86081b786bcb96f16a52a5/scripts/r24-release.py) (Git blob `ffff873a135079144e150c69c665acffa06af3e1`) · [REUSE.toml](https://github.com/tricore-opentrix/opentrix/blob/c515708c934f5bd9be86081b786bcb96f16a52a5/REUSE.toml) (Git blob `36fbfe9949a7bf40ad2682e5703b83c832693d4a`) · [R25 historical exceptions](https://github.com/tricore-opentrix/opentrix/blob/35e90c47/docs/verification/r25/exception-review.csv) · [R27 rights register](https://github.com/tricore-opentrix/opentrix/blob/6cb5a32897563df018cf79dd66b92a20a3e823f1/docs/verification/r27/r27-rights-remediation-register-187dbd2.csv) · [compare old versus new main](https://github.com/tricore-opentrix/opentrix/compare/bf3c377bef5a320803b6202781f78a6f50ff0939...c515708c934f5bd9be86081b786bcb96f16a52a5).

**Machine-readable exact-current rows:** [`r27-source-only-reuse-r25-crosswalk-c515708c.csv`](r27-source-only-reuse-r25-crosswalk-c515708c.csv), 18 columns × 47 data rows; individual exact-current Git blobs, path modes, sizes, scope, historic references and evidence routing. Historical rights statuses remain **pending**.

## 1. F01 — refreshed baseline and exact blob reconciliation

| Recomputed item at `c515708` | Count |
| --- | ---: |
| Git-tracked blobs (recursive current commit tree; not directories) | **413** |
| Git-tracked SOURCE-ONLY text paths selected by packager suffix rule | **412** |
| Tracked binary `.jar` excluded by SOURCE-ONLY rule | **1** |
| REUSE.toml annotated paths total | **28** |
| Selected annotated REUSE paths | **27** |
| R25 historical exception paths total | **37** |
| Selected historical exceptions | **29** |
| Selected set intersection | **17** |
| Selected REUSE-only | **10** |
| Selected R25-only | **12** |
| **Distinct selected crosswalk subset** | **39** |
| Crosswalk blobs unchanged against historical R27 rights register | **30 / 39** |
| Crosswalk blobs differing against historical rights register | **9 / 39** |
| Excluded/absent historical R25 rows | **8** |
| **New CSV data rows (39 selected + 8 excluded/absent)** | **47** |

**Delta against previously reviewed `bf3c377` baseline:** Among the 39 selected rows, exactly **one** current Git blob changed: `README.md`: previous `599174c0bfe5be59cecc03a2698c3bdf30fc35d9` (15,480 bytes) → current `58d01ba0cd327489d6abafd47d8d84e5e77eb62a` (16,289 bytes), both mode `100644`. [Exact diff](https://github.com/tricore-opentrix/opentrix/compare/bf3c377bef5a320803b6202781f78a6f50ff0939...c515708c934f5bd9be86081b786bcb96f16a52a5). The change adds Vietnamese and English instructions explaining that the extracted SOURCE-ONLY archive omits `gradle-wrapper.jar` and requires **external Gradle 8.14.3 / JDK 21**. This documentation change must receive portion/author/attribution review; Git commits, SPDX tags or automated tests do **not** establish rights to each underlying contribution.

**Nine paths still differing from the historic R27 Rights Register:** these are *not nine changes since `bf3c377`*. The rights register is older; only README changed since the prior crosswalk baseline.

| Selected path | Historical R27 Git blob SHA-1 | Current exact-main Git blob SHA-1 | Rights |
| --- | --- | --- | --- |
| `.env.example` | `0d397fce3d637afa6b0a2510f2134f07a303e702` | `8b8c65ccb7c0bf7ac1abf0a4eb3ad941bb60a8d5` | `RIGHTS_PENDING` |
| `.github/CODEOWNERS` | `e95e855fa0232950152d412b1a6d8b24e9896b2c` | `b7078b322b968ba11a67f9d5bd5429013479ffe8` | `RIGHTS_PENDING` |
| `.gitignore` | `9438fc29158a0d655656787c8b7b6a7c3d45bff7` | `b36298fc6c2fa4fb25aaa14b31f912fce4282d7d` | `RIGHTS_PENDING` |
| `NOTICE` | `35e2751e39895078b241f3ef342c406adcc84856` | `8c81c700d4a7f36c0f4dd2bbcbe938f4efea693e` | `RIGHTS_PENDING` |
| `README.md` | `0a81dd3cc6a55efd288b0fe06213d62aa684cbfe` | `58d01ba0cd327489d6abafd47d8d84e5e77eb62a` | `RIGHTS_PENDING` |
| `frontend/.gitignore` | `326fe72a26da191eb1c68dd8eb017bec059043f0` | `aec2e870e33cce6801f94a42a976c714c602db46` | `RIGHTS_PENDING` |
| `frontend/index.html` | `2784caa91845578bfbbb00b8f60a55ae30e9636f` | `9934301557f0b4de9e20cb0f9126bdea1d33c3a4` | `RIGHTS_PENDING` |
| `frontend/package.json` | `5bdf1add8c67f25814ce914a0c8718bb28036a25` | `d8243e2dc72021745c9ac8ee2751ad6704c4d1a2` | `RIGHTS_PENDING` |
| `scripts/setup-github.sh` | `87ee8548df32bbbbc22baf18f3467748234d0177` | `d18f9573b4799792cac3b28689ed10bfe500d810` | `RIGHTS_PENDING` |

All **39/39** selected crosswalk rows remain `RIGHTS_PENDING`. `EXTERNAL_ORIGIN_UNKNOWN` remains unverified; preserve contributor `NOT_RECALLED` instead of silently converting it into `CLEARED`.

## 2. F02 — source-only selection re-executed against **current packager**

**Executed verification:** enumerated complete, **non-truncated** Git tree for commit `c515708c934f5bd9be86081b786bcb96f16a52a5` using the GitHub Git Trees API, matched every blob path against current `scripts/r24-release.py` selection rules (lines using `git ls-files --cached --stage -z`, Git blob content, `Path(name).suffix.lower()` binary exclusion), recomputed the two source path sets from exact `REUSE.toml` and historical R25 exceptions, and reconciled **all 47** CSV paths against tree presence, blob SHA-1, Git mode and size. **Result: PASS for deterministic tracked-path selection and 39-row crosswalk.** The current tree contains **413 blobs**, with precisely `backend/gradle/wrapper/gradle-wrapper.jar` filtered, leaving **412 expected source-member paths**. All 39 crosswalk paths are selected; none is unexpectedly missing or binary-excluded.

**Important boundary:** this re-executes the **selection algorithm at the exact Git commit**, *not* an actual complete SOURCE-ONLY archive build at this SHA. The packager requires a clean checkout of the same SHA and generated R23 dependency inventory plus three CycloneDX SBOMs. No completed publishable-format R4 artifact, `MANIFEST.json` hashes, archive member bytes or legal permission is claimed here. Full archive verify/build evidence must be produced separately after authorized preparation and later two independent final R4 runs. The source-selection finding is an exact-Git-tree technical PASS, not `RELEASE_ACCEPTED`.

**Reproduce on a clean local checkout at this exact commit** (read-only commands, no publication):

```bash
git checkout --detach c515708c934f5bd9be86081b786bcb96f16a52a5
git status --porcelain=v1
git ls-files --cached --stage -z > /tmp/r27-c515708c-index.bin
git ls-tree -r HEAD | wc -l
git ls-tree -r HEAD | grep 'backend/gradle/wrapper/gradle-wrapper.jar'
git ls-tree -r HEAD README.md REUSE.toml scripts/r24-release.py
python3 - <<'PY'
import pathlib, subprocess
blocked = {".jar",".war",".class",".zip",".gz",".tar",".png",".jpg",".jpeg",
           ".webp",".gif",".ico",".woff",".woff2",".ttf",".otf",".pdf",
           ".exe",".dll",".mp4"}
raw = subprocess.check_output(["git","ls-files","--cached","--stage","-z"])
entries = [v.split(b"\t",1) for v in raw.split(b"\0") if v]
names = [name.decode("utf-8") for _,name in entries]
selected = [p for p in names if pathlib.Path(p).suffix.lower() not in blocked]
excluded = sorted(set(names)-set(selected))
assert len(names)==413, len(names)
assert len(selected)==412, len(selected)
assert excluded==["backend/gradle/wrapper/gradle-wrapper.jar"], excluded
assert all(metadata.split()[0] in (b"100644",b"100755") for metadata,_ in entries)
assert not any(p==".env" or (p.startswith(".env.") and p!=".env.example") for p in names)
print("R27_CURRENT_MAIN_SOURCE_SELECTION_PASS",len(selected),excluded)
PY
```

**Tracked binary:** `backend/gradle/wrapper/gradle-wrapper.jar` is included in Git but deliberately *not* packaged as SOURCE-ONLY. Exclusion is not an upstream license or binary distribution clearance. Its recorded Git blob is `1b33c55baabb587c669f562ae36f953de2481846`.

**Generated packaging members (distinct from the 412 tracked `source/` members):** `LICENSE`, `NOTICE`, `THIRD-PARTY-NOTICES.md`, `CHANGELOG.md`, `compliance/backend.cdx.json`, `compliance/portal-bff.cdx.json`, `compliance/frontend.cdx.json`, `compliance/license-inventory.json`, `RELEASE-NOTES.md`, `MANIFEST.json` — **10 distinct additional archive members if packaging succeeds**. `SHA256SUMS` and the second standalone release-notes file are separate download/checksum outputs, **not extra tar members**. The R24 packager normalizes volatile CycloneDX metadata and hashes every archive member other than the manifest within its manifest; generated bytes were **not** attested at `c515708` by this static check.

**R25 historical exclusions/absence checked again at current main:**

| Path | Current source-only disposition | Git blob |
| --- | --- | --- |
| `backend/gradle/wrapper/gradle-wrapper.jar` | Tracked binary `.jar` omitted by suffix filter | `1b33c55baabb587c669f562ae36f953de2481846` |
| `docs/03-applications/facility/.gitkeep` | Absent from exact current Git tree | — |
| `docs/03-applications/helpdesk/.gitkeep` | Absent from exact current Git tree | — |
| `docs/04-integration/.gitkeep` | Absent from exact current Git tree | — |
| `docs/05-testing/.gitkeep` | Absent from exact current Git tree | — |
| `docs/07-open-source/.gitkeep` | Absent from exact current Git tree | — |
| `docs/10-reviews/.gitkeep` | Absent from exact current Git tree | — |
| `docs/11-poc/.gitkeep` | Absent from exact current Git tree | — |

## 3. Required file/portion rights review — not automatic clearance

1. **README (new current blob):** check added external Gradle/JDK guidance and surrounding bilingual/collectively edited README text, identify actual contributor/source/authority for each relevant portion, reconcile NOTICE/attribution without assuming that a commit author is the rights owner. The new text describes how to build an extracted archive, not a rights attestation.
2. **Gradle wrapper:** inspect `backend/gradlew`, `backend/gradlew.bat`, `backend/gradle/wrapper/gradle-wrapper.properties` as three packaged upstream-derived files; verify Apache upstream/license/NOTICE and check misleading `TRICORE contributors` annotation on `.properties`. Wrapper JAR excluded from SOURCE-ONLY is not `CLEARED`.
3. **Flyway V1–V4 and trigger manifest:** do **not** rewrite checksum-sensitive SQL/migration bytes. Verify exact origin and ownership independently; metadata/notice remediation must be separate and reviewed.
4. **Two nonempty application `.gitkeep` files:** historic routing assigned Bảo, but Bảo's #138 disclosure attributes their creation to Yến; route creator statement to Yến and independent review to a noncontributor (Ánh proposed). Do not infer authorship from old CSV.
5. **Frontend favicon:** `frontend/public/favicon.svg` retains Ánh's limited AI-assisted source disclosure; any third-party inputs and external attribution remain `UNKNOWN / RIGHTS_PENDING`. No need to repeat Q1–Q5 declarations.
6. **Mixed-origin docs, root files, fixtures and assets:** review file contents and contribution portions; REUSE/CI/identical blobs are technical evidence only. Reviewers must document `APPROVE / REQUEST_CHANGES / BLOCKED` against current exact blob and supported source/rights evidence.

**Additional actual selected SOURCE-ONLY assets outside the 39-row crosswalk:**

| Source-selected path | Git blob at `c515708` | Pending finding |
| --- | --- | --- |
| `frontend/src/assets/opentrix-clover.svg` | `db4a1fca27f3f4bb2f12873b6e290e48afa19a61` | Yến concept, Ánh AI-assisted generation; third-party inputs not independently cleared |
| `infra/keycloak/themes/opentrix/login/resources/img/opentrix-clover.svg` | `db4a1fca27f3f4bb2f12873b6e290e48afa19a61` | second packaged path, byte-identical with Portal SVG; origin unverified |
| `infra/keycloak/themes/opentrix/login/resources/img/opentrix-helpdesk-illustration.svg` | `d9232b10aa53858c7493f947ce57e42e78fe7ccc` | Ánh said NOT_RECALLED; do not conflate with screenshot |
| `frontend/src/fixtures/requests.ts` | `f62e2d02b9d2deba938bbcc7986af89776f72005` | UNKNOWN fixture origin |
| `frontend/src/test/helpdeskFixtures.ts` | `bb162b45e62307d9083e1acfcc36b92862da3ac8` | UNKNOWN fixture origin |
| `frontend/tests/integration-local-fixture.ts` | `e3cd20de98e17c46d4aa67f0a6770f5b8f9822fb` | UNKNOWN fixture origin |

The two Clover SVGs are byte-identical at this SHA but distinct packaged paths; the Helpdesk SVG remains `NOT_RECALLED`. Fixtures remain `UNKNOWN`. These six files are **not** magically cleared by their absence from the 39-row REUSE × R25 intersection/union.

**Independence routing is only proposed:** Yến coordinates #138 but cannot self-approve her own contributions. Ánh reviews portions by Yến where independent; Yến reviews Bảo/Ánh portions where independent; mixed-author portions require someone with no substantive contribution to those portions. A signed Q1–Q5 declaration is retained but does not substitute for file-level attribution evidence.

## 4. F03 — whitespace/traceability and disposition

The previous `bf3c377` CSV is preserved byte-for-byte; its Markdown received **whitespace-only cleanup** (trailing blanks/end of file) without rewriting historical findings. This new Markdown and current CSV contain no trailing whitespace; the PR should run `git diff --check` and REUSE/CI on the final HEAD. If a new PR changes `main`, regenerate this SHA-bound snapshot before claiming currency.

**Verification outcome:** `F01_EXACT_CURRENT_BLOB_PASS / F02_CURRENT_SOURCE_SELECTION_PASS / F03_WHITESPACE_NORMALIZED / RIGHTS_PENDING / SOURCE_FREEZE_BLOCKED / RELEASE_NOT_ACCEPTED`.

**Explicit nonauthorization:** do not close #138/#190, merge this PR without independent review, dispatch final R4, freeze source SHA, push tag/Release, distribute JAR/frontend dist/binary/GHCR or treat this documentation as legal clearance.
