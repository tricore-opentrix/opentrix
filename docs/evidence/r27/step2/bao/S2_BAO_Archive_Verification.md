<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# R27 Step 2 — Bảo Archive Verification Report (S2-01, S2-03)

**Repository:** `tricore-opentrix/opentrix`
**Frozen SHA:** `187dbd2ea6935966f5c4cceb95ad9c3c53708a2e`
**Executor:** Lê Xuân Bảo (@lexuanbao258-collab)
**Reviewer:** Phan Hải Yến (@phanyen06ym-ien) — independent review pending; Ánh supports Frontend/assets cross-check
**Date:** 2026-11-08
**Status:** `TECHNICAL_PASS_PENDING_REVIEW` (S2-01 PASS, S2-03 PASS with 1 documented exception) — **not** a Step 2 PASS until reviewed

> Technical evidence only. Does not establish source ownership, licensing rights or release approval. All 357 Rights Register entries remain `RIGHTS_PENDING`; R24 remains BLOCKED.

## 1. Archive Identity (S2-01)

| Field | Value | Evidence |
|---|---|---|
| Archive filename | `dxos-open-core-0.2.0.tar.gz` (632,415 bytes) | Extracted from both artifacts |
| Archive source / location | Run [42244683510](https://github.com/tricore-opentrix/opentrix/actions/runs/42244683510) → artifact [`r24-source-only-candidate-42244683510`](https://github.com/tricore-opentrix/opentrix/actions/runs/42244683510/artifacts/13516853708) (ID 13516853708); Run [42245290247](https://github.com/tricore-opentrix/opentrix/actions/runs/42245290247) → artifact [`r24-source-only-candidate-42245290247`](https://github.com/tricore-opentrix/opentrix/actions/runs/42245290247/artifacts/13517790376) (ID 13517790376). Both `workflow_dispatch` on `187dbd2e`, conclusion success, retention to 2026-12-06. | GitHub API; artifacts downloaded 2026-11-08 |
| Artifact container SHA-256 (zip) | Run 1 `08e0e60c9baa9f80b5196eb9ca911656a862887a829dad13c03a3c2727f69f47`; Run 2 `48958dad89de2894b56441be625214eb585f53b1c249046646cfd8bdaf5ad041` — each equals the digest printed by `actions/upload-artifact` in the job log | Downloaded files re-hashed |
| **Archive SHA-256** | **`93e6e0ba5d708120c6ec494af3e50c8959cccb4c442a8bba9a2e9c617c2d448f`** — identical in both runs (`cmp` byte-equal); equals each artifact's `SHA256SUMS`; `sha256sum -c` OK | Re-hashed independently |
| Archive creation command | `python3 scripts/r24-release.py package --mode source-only --tag v0.2.0 --sha 187dbd2ea6935966f5c4cceb95ad9c3c53708a2e --output dist/r24-source-only`, then `r24-release.py verify …` and `sha256sum -c SHA256SUMS` | Job logs 127983695490 / 127985806541; script at frozen SHA |
| Manifest | `dxos-v0.2.0/MANIFEST.json`, SHA-256 `e842a90ad2e84ea62035dc05a579f59e713404170fc431cf5c89d1f60ff40d19`; `tag=v0.2.0`, `source_sha=187dbd2e…`, `mode=source-only`, 355 `files_sha256` entries (all members except itself) | Extracted |
| Other artifact files | `SHA256SUMS` (94 B); `RELEASE-NOTES.md` SHA-256 `e39a667c998f9d5b3e23d1d7c96f2507bd2c608fac061f9b4fb71e394d877a24` (same in both runs) | Extracted |
| Source-only packaging rules | `scripts/r24-release.py` @ frozen SHA: all `git ls-files` paths; skip suffixes `.jar .war .class .zip .gz .tar .png .jpg .jpeg .webp .gif .ico .woff .woff2 .ttf .otf .pdf .exe .dll .mp4`; block tracked `.env*` except `.env.example`; reject NUL / non-UTF-8; prefix `dxos-v0.2.0/source/`; add 10 metadata members; deterministic tar (sorted, mode 0644, uid/gid/mtime 0); R23 inventory must be `APPROVED` | Read from frozen script |
| Availability | `AVAILABLE` (GitHub Actions artifacts, signed-in download, expire 2026-12-06). Recommend preserving a copy before expiry. | — |

**S2-01 verdict: `PASS`** — the actual R24 source-only archive at the frozen SHA is identified, hashed independently, and both CI builds produced a byte-identical archive.

## 2. Verification Method

1. Downloaded both artifacts from the GitHub web UI (signed in); confirmed zip SHA-256 equals the CI-logged upload digest.
2. Unzipped; `sha256sum` archive; `sha256sum -c SHA256SUMS`; `cmp` the two archives.
3. Read every tar member (name, type, mode, uid/gid, mtime, bytes, SHA-256).
4. For each `source/<path>` member compared with: (a) raw Git blob at `187dbd2` (`git show`), (b) Git checkout bytes with repository attributes applied (`git cat-file --filters 187dbd2:<path>`), (c) `MANIFEST.json`, (d) Rights Register #143 `git_blob_sha1` and `git ls-tree` blob SHA-1.
5. For each metadata member compared with `MANIFEST.json`, register #143 archive rows and, where a tracked twin exists, the frozen file.
6. Listed tracked paths absent from the archive and checked them against the packaging rules.

Full member table: [`S2_BAO_Archive_Members.csv`](S2_BAO_Archive_Members.csv) (357 rows). Commands: [`S2_BAO_Reproduction.md`](S2_BAO_Reproduction.md).

## 3. Verification Results (S2-03)

| Check | Expected | Actual | Verdict |
|---|---|---|---|
| Frozen Git blob scope | 347 tracked paths | 347 in `git ls-tree`; **347/347** blob SHA-1 equal register #143 | **PASS** |
| Rights Register scope | 357 entries | 347 tracked + 10 `ARCHIVE_METADATA`; every register row accounted for (346 in archive as `source/`, 1 excluded JAR, 10 metadata) | **PASS** |
| Archive-only scope | 10 metadata entries | Exactly 10: `CHANGELOG.md`, `LICENSE`, `MANIFEST.json`, `NOTICE`, `RELEASE-NOTES.md`, `THIRD-PARTY-NOTICES.md`, `compliance/{backend,frontend,portal-bff}.cdx.json`, `compliance/license-inventory.json`; all 10 present in register; 0 missing, 0 extra | **PASS** |
| Archive member paths | Match approved manifest | 356 members = 346 source + 10 metadata; `MANIFEST.json` lists the other 355; no member outside `dxos-v0.2.0/`; no manifest entry without member | **PASS** |
| Archive member hashes | Match expected content | 355/355 equal `MANIFEST.json`; **346/346** source members equal Git checkout bytes at frozen SHA; 330 also equal raw Git blob; 16 differ from raw blob only by CRLF (F-01); 4 root metadata files byte-identical to tracked twins | **PASS with exception F-01** |
| Excluded Gradle Wrapper JAR | Consistent with source-only rules | Only tracked path absent: `backend/gradle/wrapper/gradle-wrapper.jar` (binary, `.jar` suffix rule); no other binary in tree | **PASS** |
| Unexpected files | No unexplained files | 0 unexpected; no `.env`; all tar headers normalized (regular file, 0644, uid/gid/mtime 0) | **PASS** |
| Two-build reproducibility | Same archive | Byte-identical (`93e6e0ba…448f`) | **PASS** |

## 4. Findings and Exceptions

**F-01 — CRLF line endings in 16 script files**
- Affected path: `backend/gradlew.bat` and 15 `scripts/**/*.ps1` (listed in CSV with verdict `PASS_WITH_EXCEPTION`)
- Expected result: member bytes = frozen content
- Actual result: member bytes = Git checkout bytes (CRLF), not raw blob bytes (LF). `.gitattributes` at frozen SHA sets `*.bat text eol=crlf` and `*.ps1 text eol=crlf`; the packager reads the CI working tree. After CRLF→LF the content equals the Git blob; register blob SHA-1 and `MANIFEST.json` both match.
- Evidence: `git cat-file --filters 187dbd2:<path>` reproduces the member bytes 16/16
- Proposed disposition: accept as expected checkout normalization; note in register that archive bytes for these 16 paths are the CRLF checkout form (blob SHA-1 unchanged)
- Reviewer decision: _pending_

**F-02 — Four files appear twice**
- Affected path: `LICENSE`, `NOTICE`, `THIRD-PARTY-NOTICES.md`, `CHANGELOG.md`
- Expected result: one copy each
- Actual result: by design, once under `source/` and once at archive root; both byte-identical to the tracked file
- Evidence: CSV rows; `scripts/r24-release.py`
- Proposed disposition: informational; count as one work each in rights review
- Reviewer decision: _pending_

**F-03 — Build-generated compliance files**
- Affected path: `compliance/backend.cdx.json`, `compliance/portal-bff.cdx.json`, `compliance/frontend.cdx.json`, `compliance/license-inventory.json`
- Expected result: reproducible content
- Actual result: hashes match `MANIFEST.json` and are identical in both builds; content depends on resolved dependencies and cannot be regenerated from Git alone
- Evidence: CSV rows; job steps 8–10
- Proposed disposition: accept as build artifacts verified by manifest + two-build equality
- Reviewer decision: _pending_

## 5. Technical Verdict

**`PASS` (technical, pending independent review)**

Verified: actual archive identity and SHA-256; two-build byte equality; 356/356 members accounted for; 355/355 manifest hashes; 346/346 source members equal Git checkout bytes at frozen SHA; 347/347 register blob SHA-1; 10/10 archive-only rows; JAR exclusion consistent with source-only rules; no unexpected files.

Remaining unknown: content correctness of the 4 build-generated compliance files beyond manifest/two-build consistency (F-03). Rights, authorship and third-party provenance are out of scope.

This technical verdict does not establish source ownership, licensing rights or release approval. Step 2 as a whole is **not** marked PASS until Yến's independent review.

## 6. Evidence Links

- Archive / manifest: artifacts [13516853708](https://github.com/tricore-opentrix/opentrix/actions/runs/42244683510/artifacts/13516853708), [13517790376](https://github.com/tricore-opentrix/opentrix/actions/runs/42245290247/artifacts/13517790376)
- Member inventory CSV: [`S2_BAO_Archive_Members.csv`](S2_BAO_Archive_Members.csv)
- Reproduction script or command log: [`S2_BAO_Reproduction.md`](S2_BAO_Reproduction.md)
- Rights Register reference: [PR #143 @ `6cb5a328`](https://github.com/tricore-opentrix/opentrix/pull/143)
- Reviewer verdict: _pending — Yến_
