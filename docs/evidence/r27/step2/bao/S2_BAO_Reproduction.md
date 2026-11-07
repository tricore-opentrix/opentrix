<!--
SPDX-FileCopyrightText: 2026 TRICORE contributors
SPDX-License-Identifier: Apache-2.0
-->

# R27 Step 2 — Bảo: reproduction commands (S2-01, S2-03)

Read-only. Tested on Linux (bash, Python 3). Results recorded 2026-11-08.

## 1. Obtain the two candidate artifacts

```bash
# signed-in gh CLI (or download both from the run pages in a browser)
gh run download 42244683510 -R tricore-opentrix/opentrix -n r24-source-only-candidate-42244683510 -D run1
gh run download 42245290247 -R tricore-opentrix/opentrix -n r24-source-only-candidate-42245290247 -D run2
```

Browser download gives zip files; their SHA-256 must equal the `actions/upload-artifact` digest in the job logs:

```
08e0e60c9baa9f80b5196eb9ca911656a862887a829dad13c03a3c2727f69f47  r24-source-only-candidate-42244683510.zip
48958dad89de2894b56441be625214eb585f53b1c249046646cfd8bdaf5ad041  r24-source-only-candidate-42245290247.zip
```

## 2. Archive identity

```bash
for d in run1 run2; do (cd $d && sha256sum dxos-open-core-0.2.0.tar.gz && sha256sum -c SHA256SUMS); done
cmp run1/dxos-open-core-0.2.0.tar.gz run2/dxos-open-core-0.2.0.tar.gz && echo IDENTICAL
# expected: 93e6e0ba5d708120c6ec494af3e50c8959cccb4c442a8bba9a2e9c617c2d448f (both) / OK / IDENTICAL
tar -xzOf run1/dxos-open-core-0.2.0.tar.gz dxos-v0.2.0/MANIFEST.json | sha256sum
# expected: e842a90ad2e84ea62035dc05a579f59e713404170fc431cf5c89d1f60ff40d19
tar -tzf run1/dxos-open-core-0.2.0.tar.gz | wc -l      # expected: 356
```

CI log digests (read-only API):

```bash
gh api repos/tricore-opentrix/opentrix/actions/jobs/127983695490/logs | grep -E 'R24_CANDIDATE_BUILT|SHA256 digest|: OK'
gh api repos/tricore-opentrix/opentrix/actions/jobs/127985806541/logs | grep -E 'R24_CANDIDATE_BUILT|SHA256 digest|: OK'
```

## 3. Frozen tree and register

```bash
git clone https://github.com/tricore-opentrix/opentrix && cd opentrix
SHA=187dbd2ea6935966f5c4cceb95ad9c3c53708a2e
git ls-tree -r -l $SHA | wc -l                           # 347
# Register #143 CSV at commit 6cb5a328 (R27-REG-001); compare git_blob_sha1 with ls-tree blob column
```

## 4. Member verification

The script used is embedded below (save as `verify_members.py`). It writes `S2_BAO_Archive_Members.csv` and prints counts.

```bash
python3 -I verify_members.py run1/dxos-open-core-0.2.0.tar.gz ./opentrix register143.csv S2_BAO_Archive_Members.csv
# expected: archive_members 356, source 346, metadata 10, tracked_not_in_archive [gradle-wrapper.jar],
#           16 raw-blob mismatches (CRLF, F-01)
```

Then confirm F-01 (CRLF) against Git checkout bytes:

```bash
cd opentrix
for p in backend/gradlew.bat $(git ls-tree -r --name-only $SHA scripts | grep '\.ps1$'); do
  a=$(tar -xzOf ../run1/dxos-open-core-0.2.0.tar.gz "dxos-v0.2.0/source/$p" | sha256sum | cut -c1-64)
  c=$(git cat-file --filters "$SHA:$p" | sha256sum | cut -c1-64)
  [ "$a" = "$c" ] && echo "OK  $p" || echo "DIFF $p"
done
# expected: 16 × OK ; .gitattributes: *.bat / *.ps1 text eol=crlf
```

All 346 source members were also checked with `git cat-file --filters` → 346/346 equal.

### verify_members.py

```python
#!/usr/bin/env python3
"""R27 S2-03: verify every member of the R24 source-only archive against frozen Git and register #143."""
import tarfile, hashlib, json, csv, subprocess, sys, os, collections
ARCH, REPO, REG, OUT = sys.argv[1:5]
SHA = '187dbd2ea6935966f5c4cceb95ad9c3c53708a2e'; PFX = 'dxos-v0.2.0/'
git = lambda *a: subprocess.run(('git',) + a, cwd=REPO, capture_output=True, check=True).stdout
h = lambda b: hashlib.sha256(b).hexdigest()
tree = {}
for l in git('ls-tree', '-r', '-l', SHA).decode().splitlines():
    meta, p = l.split('\t', 1); tree[p] = meta.split()[2]
reg = list(csv.DictReader(open(REG)))
regt = {r['tracked_git_path']: r for r in reg if r['tracked_git_path'] not in ('', 'NOT_A_NEW_TRACKED_PATH')}
rega = {r['archive_member']: r for r in reg if r['tracked_git_path'] == 'NOT_A_NEW_TRACKED_PATH'}
tf = tarfile.open(ARCH, 'r:gz')
mem, meta = {}, {}
for m in tf.getmembers():
    meta[m.name] = (m.type, m.mode, m.uid, m.gid, m.mtime)
    mem[m.name] = tf.extractfile(m).read() if m.isfile() else None
man = json.loads(mem[PFX + 'MANIFEST.json'])
DIS = {".jar",".war",".class",".zip",".gz",".tar",".png",".jpg",".jpeg",".webp",".gif",".ico",".woff",".woff2",".ttf",".otf",".pdf",".exe",".dll",".mp4"}
rows, seen = [], set()
for name in sorted(mem):
    rel = name[len(PFX):]; data = mem[name]; s = h(data)
    t, mode, uid, gid, mt = meta[name]
    norm = t == tarfile.REGTYPE and mode == 0o644 and uid == gid == mt == 0
    mf = man['files_sha256'].get(rel, '')
    if rel.startswith('source/'):
        p = rel[7:]; seen.add(p)
        raw = git('show', f'{SHA}:{p}'); chk = git('cat-file', '--filters', f'{SHA}:{p}')
        r = regt.get(p, {})
        ok = mf == s and r.get('git_blob_sha1') == tree.get(p) and norm
        v = ('PASS' if h(raw) == s else 'PASS_WITH_EXCEPTION' if h(chk) == s else 'FAIL') if ok else 'FAIL'
        rows.append(dict(member=name, kind='SOURCE', frozen_path=p, member_sha256=s, frozen_git_content_sha256=h(raw),
                         checkout_content_sha256=h(chk), manifest_sha256=mf, frozen_blob_sha1=tree.get(p, ''),
                         register_143_blob_sha1=r.get('git_blob_sha1', ''), verdict=v))
    else:
        r = rega.get(name, {})
        ok = (rel == 'MANIFEST.json' or mf == s) and bool(r) and norm
        rows.append(dict(member=name, kind='ARCHIVE_METADATA', member_sha256=s, manifest_sha256=mf,
                         register_entry_type=r.get('entry_type', 'NOT_IN_REGISTER'), verdict='PASS' if ok else 'FAIL'))
for p in sorted(set(tree) - seen):
    rows.append(dict(kind='TRACKED_NOT_IN_ARCHIVE', frozen_path=p, frozen_blob_sha1=tree[p],
                     verdict='PASS (expected exclusion)' if os.path.splitext(p)[1].lower() in DIS else 'FAIL (missing)'))
fields = sorted({k for r in rows for k in r})
with open(OUT, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
print(collections.Counter((r['kind'], r['verdict']) for r in rows))
```
