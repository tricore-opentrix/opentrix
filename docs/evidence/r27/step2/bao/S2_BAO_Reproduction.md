<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# R27 Step 2 — Bảo: reproduction (S2-01, S2-03)

Read-only. Linux, bash, Python 3, `git`, `gh` (signed in). Re-run and confirmed 2026-11-08 from a fresh clone.

**One working directory for everything.** Every command below uses absolute paths under `$WORKDIR`; nothing depends on the current directory.

```bash
export WORKDIR="$HOME/r27-s2-bao"          # choose any empty directory
mkdir -p "$WORKDIR/run1" "$WORKDIR/run2"
```

## 1. Inputs

### 1.1 Repository at the frozen SHA and the pinned register commit

```bash
git clone https://github.com/tricore-opentrix/opentrix "$WORKDIR/opentrix"
git -C "$WORKDIR/opentrix" fetch origin 6cb5a32897563df018cf79dd66b92a20a3e823f1
git -C "$WORKDIR/opentrix" rev-parse 187dbd2ea6935966f5c4cceb95ad9c3c53708a2e
```

### 1.2 Rights Register #143 (pinned, not "latest")

| Field | Value |
|---|---|
| Commit (PR #143 head used) | `6cb5a32897563df018cf79dd66b92a20a3e823f1` |
| Path | `docs/verification/r27/r27-rights-remediation-register-187dbd2.csv` |
| SHA-256 | `4b90d48f4b5b8591c16226468282695075ef07da4703996590490072d54f85f2` |

```bash
git -C "$WORKDIR/opentrix" show 6cb5a32897563df018cf79dd66b92a20a3e823f1:docs/verification/r27/r27-rights-remediation-register-187dbd2.csv \
  > "$WORKDIR/register143.csv"
sha256sum "$WORKDIR/register143.csv"        # expect 4b90d48f…54f85f2
```

The verification script reads the register **directly from that commit** and aborts if its SHA-256 differs; `register143.csv` above is only for inspection.

### 1.3 The two candidate archives

```bash
gh run download 42244683510 -R tricore-opentrix/opentrix -n r24-source-only-candidate-42244683510 -D "$WORKDIR/run1"
gh run download 42245290247 -R tricore-opentrix/opentrix -n r24-source-only-candidate-42245290247 -D "$WORKDIR/run2"
```

(Browser download alternative: the zip files must hash to `08e0e60c9baa9f80b5196eb9ca911656a862887a829dad13c03a3c2727f69f47` and `48958dad89de2894b56441be625214eb585f53b1c249046646cfd8bdaf5ad041` — the digests printed by `actions/upload-artifact` in job logs 127983695490 / 127985806541 — then `unzip` each into `$WORKDIR/run1` / `$WORKDIR/run2`.)

## 2. S2-01 — archive identity

```bash
sha256sum "$WORKDIR/run1/dxos-open-core-0.2.0.tar.gz" "$WORKDIR/run2/dxos-open-core-0.2.0.tar.gz"
(cd "$WORKDIR/run1" && sha256sum -c SHA256SUMS); (cd "$WORKDIR/run2" && sha256sum -c SHA256SUMS)
cmp "$WORKDIR/run1/dxos-open-core-0.2.0.tar.gz" "$WORKDIR/run2/dxos-open-core-0.2.0.tar.gz" && echo IDENTICAL
tar -xzOf "$WORKDIR/run1/dxos-open-core-0.2.0.tar.gz" dxos-v0.2.0/MANIFEST.json | sha256sum
tar -tzf "$WORKDIR/run1/dxos-open-core-0.2.0.tar.gz" | wc -l
```

Expected: both `93e6e0ba5d708120c6ec494af3e50c8959cccb4c442a8bba9a2e9c617c2d448f`; `OK`, `OK`; `IDENTICAL`; MANIFEST `e842a90ad2e84ea62035dc05a579f59e713404170fc431cf5c89d1f60ff40d19`; `356`.

## 3. S2-03 — member verification and CSV

The script that produced the committed CSV is [`S2_BAO_verify_archive.py`](S2_BAO_verify_archive.py) (same directory). It is the **only** step: no manual edits or separate post-processing.

```bash
cp "$WORKDIR/opentrix/docs/evidence/r27/step2/bao/S2_BAO_verify_archive.py" "$WORKDIR/"   # or download from PR #157
python3 -I "$WORKDIR/S2_BAO_verify_archive.py" \
  --repo     "$WORKDIR/opentrix" \
  --archive  "$WORKDIR/run1/dxos-open-core-0.2.0.tar.gz" \
  --archive2 "$WORKDIR/run2/dxos-open-core-0.2.0.tar.gz" \
  --out      "$WORKDIR/S2_BAO_Archive_Members.csv"
echo "exit=$?"
cmp "$WORKDIR/S2_BAO_Archive_Members.csv" "$WORKDIR/opentrix/docs/evidence/r27/step2/bao/S2_BAO_Archive_Members.csv" && echo BYTE_IDENTICAL
```

(If the evidence directory is not yet on your checkout, fetch the PR branch first: `git -C "$WORKDIR/opentrix" fetch origin pull/157/head && git -C "$WORKDIR/opentrix" checkout FETCH_HEAD -- docs/evidence/r27/step2/bao`.)

Expected output (recorded 2026-11-08):

```
archive_sha256      93e6e0ba5d708120c6ec494af3e50c8959cccb4c442a8bba9a2e9c617c2d448f
runs_identical      true
members 356, source 346, metadata 10, manifest_entries 355
excluded            ["backend/gradle/wrapper/gradle-wrapper.jar"]
register_sha256     4b90d48f4b5b8591c16226468282695075ef07da4703996590490072d54f85f2
rows 357, pass_with_exception 16
output_sha256       e16f5450d4505ec5560e55bfed8593f9ab6a2507d81d192f1e49151154e74436
errors              []
exit=0
BYTE_IDENTICAL
```

### Assertions enforced by the script (exit 1 on any failure)

1. Run-1 archive SHA-256 equals the expected value; run-1 and run-2 archives are byte-identical.
2. Register read from the pinned commit; SHA-256 matches; exactly 357 rows; no duplicates or unclassified rows.
3. Frozen tree has 347 paths; register tracked path set **equals** tree path set (both directions); every blob SHA-1 matches.
4. Archive member names unique and all under `dxos-v0.2.0/`; exactly 356 members.
5. MANIFEST header = `v0.2.0` / frozen SHA / `source-only`; MANIFEST path set **equals** archive members minus `MANIFEST.json` (both directions).
6. `source/` members **equal** tree paths minus the binary-suffix exclusions (both directions); the exclusion set is exactly `{backend/gradle/wrapper/gradle-wrapper.jar}`.
7. Metadata members **equal** register archive rows (both directions).
8. Per member: MANIFEST hash, register blob SHA-1, normalized tar header; content equals raw Git blob (`PASS`) or Git checkout bytes with repository attributes (`PASS_WITH_EXCEPTION`, F-01); otherwise `FAIL`.
9. Output has 357 rows, covers each tracked path exactly once, and contains no `FAIL`.

Negative check performed: removing `source/README.md` from a copy of the archive makes the script report the missing member, the count/set mismatches and exit `1`.

### CSV columns (15)

`member, kind, frozen_path, member_sha256, frozen_git_content_sha256, checkout_content_sha256, manifest_sha256, frozen_blob_sha1, register_143_blob_sha1, register_entry_type, register_distribution_status, tar_header_normalized, bytes, verdict, note` — UTF-8, CRLF row terminator (Python `csv` default).

## 4. F-01 spot check (independent of the script)

```bash
SHA=187dbd2ea6935966f5c4cceb95ad9c3c53708a2e
for p in backend/gradlew.bat $(git -C "$WORKDIR/opentrix" ls-tree -r --name-only $SHA scripts | grep '\.ps1$'); do
  a=$(tar -xzOf "$WORKDIR/run1/dxos-open-core-0.2.0.tar.gz" "dxos-v0.2.0/source/$p" | sha256sum | cut -c1-64)
  c=$(git -C "$WORKDIR/opentrix" cat-file --filters "$SHA:$p" | sha256sum | cut -c1-64)
  [ "$a" = "$c" ] && echo "OK   $p" || echo "DIFF $p"
done
# expect 16 × OK; .gitattributes @ frozen SHA: *.bat / *.ps1 text eol=crlf
```
