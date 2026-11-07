#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 TRICORE contributors
# SPDX-License-Identifier: Apache-2.0
"""R27 Step 2 (S2-01, S2-03) — Bảo: verify the R24 source-only archive against the
frozen Git tree and Rights Register #143, and write S2_BAO_Archive_Members.csv.

This single script produces the committed CSV byte-for-byte; there is no manual or
separate post-processing step. It exits non-zero on any missing, extra, duplicate or
mismatched item.

Usage (all paths absolute or relative to the current directory):
  python3 -I S2_BAO_verify_archive.py --repo REPO --archive RUN1_TGZ --archive2 RUN2_TGZ --out CSV
"""
import argparse, csv, hashlib, json, os, subprocess, sys, tarfile

FROZEN_SHA = '187dbd2ea6935966f5c4cceb95ad9c3c53708a2e'
REGISTER_COMMIT = '6cb5a32897563df018cf79dd66b92a20a3e823f1'          # PR #143 head used
REGISTER_PATH = 'docs/verification/r27/r27-rights-remediation-register-187dbd2.csv'
REGISTER_SHA256 = '4b90d48f4b5b8591c16226468282695075ef07da4703996590490072d54f85f2'
ARCHIVE_SHA256 = '93e6e0ba5d708120c6ec494af3e50c8959cccb4c442a8bba9a2e9c617c2d448f'
PFX = 'dxos-v0.2.0/'
EXCLUDED_SUFFIXES = {".jar", ".war", ".class", ".zip", ".gz", ".tar", ".png", ".jpg", ".jpeg", ".webp", ".gif",
                     ".ico", ".woff", ".woff2", ".ttf", ".otf", ".pdf", ".exe", ".dll", ".mp4"}   # scripts/r24-release.py @ frozen SHA
TWINS = {'LICENSE', 'NOTICE', 'THIRD-PARTY-NOTICES.md', 'CHANGELOG.md'}
FIELDS = ['member', 'kind', 'frozen_path', 'member_sha256', 'frozen_git_content_sha256', 'checkout_content_sha256',
          'manifest_sha256', 'frozen_blob_sha1', 'register_143_blob_sha1', 'register_entry_type',
          'register_distribution_status', 'tar_header_normalized', 'bytes', 'verdict', 'note']
F01_NOTE = ('CRLF per .gitattributes (*.ps1/*.bat eol=crlf); equals git checkout bytes and MANIFEST; '
            'register blob SHA-1 matches; LF-normalized content equals Git blob')

errors = []
def check(cond, msg):
    if not cond:
        errors.append(msg)
    return cond

def sha256(b):
    return hashlib.sha256(b).hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', required=True)
    ap.add_argument('--archive', required=True)
    ap.add_argument('--archive2', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    git = lambda *x: subprocess.run(('git',) + x, cwd=a.repo, capture_output=True, check=True).stdout

    # --- S2-01: archive identity
    b1, b2 = open(a.archive, 'rb').read(), open(a.archive2, 'rb').read()
    check(sha256(b1) == ARCHIVE_SHA256, f'run1 archive sha256 {sha256(b1)} != {ARCHIVE_SHA256}')
    check(b1 == b2, 'run1 and run2 archives are not byte-identical')

    # --- inputs: frozen tree + pinned register
    check(git('rev-parse', FROZEN_SHA).decode().strip() == FROZEN_SHA, 'frozen SHA not present in repo')
    tree = {}
    for line in git('ls-tree', '-r', '-l', FROZEN_SHA).decode().splitlines():
        meta, path = line.split('\t', 1)
        tree[path] = meta.split()[2]
    reg_bytes = git('show', f'{REGISTER_COMMIT}:{REGISTER_PATH}')
    check(sha256(reg_bytes) == REGISTER_SHA256, f'register sha256 {sha256(reg_bytes)} != pinned {REGISTER_SHA256}')
    reg = list(csv.DictReader(reg_bytes.decode('utf-8').splitlines()))
    regt = {r['tracked_git_path']: r for r in reg if r['tracked_git_path'] not in ('', 'NOT_A_NEW_TRACKED_PATH')}
    rega = {r['archive_member']: r for r in reg if r['tracked_git_path'] == 'NOT_A_NEW_TRACKED_PATH'}
    check(len(reg) == 357, f'register rows {len(reg)} != 357')
    check(len(tree) == 347, f'frozen tracked paths {len(tree)} != 347')
    check(len(regt) + len(rega) == len(reg), 'register has rows that are neither tracked nor archive metadata, or duplicates')
    check(set(regt) == set(tree), f'register vs tree path sets differ: {sorted(set(regt) ^ set(tree))[:10]}')
    check(all(regt[p]['git_blob_sha1'] == tree[p] for p in tree if p in regt), 'register blob SHA-1 mismatch')

    # --- read archive members
    tf = tarfile.open(fileobj=__import__('io').BytesIO(b1), mode='r:gz')
    names = [m.name for m in tf.getmembers()]
    check(len(names) == len(set(names)), 'duplicate archive member names')
    check(all(n.startswith(PFX) for n in names), 'archive member outside dxos-v0.2.0/')
    mem, hdr = {}, {}
    for m in tf.getmembers():
        hdr[m.name] = (m.type == tarfile.REGTYPE and m.mode == 0o644 and m.uid == m.gid == m.mtime == 0)
        mem[m.name] = tf.extractfile(m).read() if m.isfile() else b''
    man = json.loads(mem[PFX + 'MANIFEST.json'])
    check((man.get('tag'), man.get('source_sha'), man.get('mode')) == ('v0.2.0', FROZEN_SHA, 'source-only'), 'MANIFEST header mismatch')
    rel_all = {n[len(PFX):] for n in names}
    check(set(man['files_sha256']) == rel_all - {'MANIFEST.json'}, 'MANIFEST path set != archive members (minus MANIFEST)')

    src = {n[len(PFX) + 7:] for n in names if n.startswith(PFX + 'source/')}
    meta = {n for n in names if not n.startswith(PFX + 'source/')}
    expected_excl = {p for p in tree if os.path.splitext(p)[1].lower() in EXCLUDED_SUFFIXES}
    check(src == set(tree) - expected_excl, f'source members != tree minus excluded: {sorted(src ^ (set(tree) - expected_excl))[:10]}')
    check(expected_excl == {'backend/gradle/wrapper/gradle-wrapper.jar'}, f'unexpected exclusion set {sorted(expected_excl)}')
    check(meta == set(rega), f'metadata members != register archive rows: {sorted(meta ^ set(rega))}')
    check(len(names) == 356, f'archive members {len(names)} != 356')

    # --- per-member rows
    rows = []
    for name in sorted(mem):
        rel = name[len(PFX):]
        data = mem[name]; s = sha256(data); mf = man['files_sha256'].get(rel, '')
        if rel.startswith('source/'):
            p = rel[7:]
            raw = git('show', f'{FROZEN_SHA}:{p}'); chk = git('cat-file', '--filters', f'{FROZEN_SHA}:{p}')
            r = regt.get(p, {})
            ok = mf == s and r.get('git_blob_sha1') == tree.get(p) and hdr[name]
            if ok and sha256(raw) == s:
                v, note = 'PASS', ''
            elif ok and sha256(chk) == s:
                v, note = 'PASS_WITH_EXCEPTION', F01_NOTE
            else:
                v, note = 'FAIL', ''
            rows.append(dict(member=name, kind='SOURCE', frozen_path=p, member_sha256=s, frozen_git_content_sha256=sha256(raw),
                             checkout_content_sha256=sha256(chk), manifest_sha256=mf, frozen_blob_sha1=tree.get(p, ''),
                             register_143_blob_sha1=r.get('git_blob_sha1', ''), register_entry_type=r.get('entry_type', ''),
                             register_distribution_status=r.get('distribution_status', ''), tar_header_normalized=hdr[name],
                             bytes=len(data), verdict=v, note=note))
        else:
            r = rega.get(name, {})
            tsha = sha256(git('show', f'{FROZEN_SHA}:{rel}')) if rel in TWINS else ''
            if rel in TWINS:
                note = ('byte-identical to tracked ' if tsha == s else 'DIFFERS from tracked ') + rel
            elif rel == 'MANIFEST.json':
                note = f"tag={man['tag']} source_sha={man['source_sha']} mode={man['mode']} entries={len(man['files_sha256'])}"
            elif rel == 'RELEASE-NOTES.md':
                note = 'generated from CHANGELOG [0.2.0] by r24-release.py'
            else:
                note = 'build-generated (CycloneDX / R23 inventory); content not reproducible from Git alone; matches MANIFEST'
            ok = (rel == 'MANIFEST.json' or mf == s) and bool(r) and hdr[name] and (rel not in TWINS or tsha == s)
            rows.append(dict(member=name, kind='ARCHIVE_METADATA', frozen_path=rel if rel in TWINS else '', member_sha256=s,
                             frozen_git_content_sha256=tsha, checkout_content_sha256='',
                             manifest_sha256='(self)' if rel == 'MANIFEST.json' else mf, frozen_blob_sha1='',
                             register_143_blob_sha1='', register_entry_type=r.get('entry_type', 'NOT_IN_REGISTER'),
                             register_distribution_status=r.get('distribution_status', ''), tar_header_normalized=hdr[name],
                             bytes=len(data), verdict='PASS' if ok else 'FAIL', note=note))
    for p in sorted(set(tree) - src):
        r = regt.get(p, {})
        rows.append(dict(member='', kind='TRACKED_NOT_IN_ARCHIVE', frozen_path=p, member_sha256='', frozen_git_content_sha256='',
                         checkout_content_sha256='', manifest_sha256='', frozen_blob_sha1=tree[p],
                         register_143_blob_sha1=r.get('git_blob_sha1', ''), register_entry_type=r.get('entry_type', ''),
                         register_distribution_status=r.get('distribution_status', ''), tar_header_normalized='', bytes='',
                         verdict='PASS (expected exclusion)' if p in expected_excl else 'FAIL (missing)',
                         note='excluded by source-only binary-suffix rule' if p in expected_excl else ''))

    # --- completeness / verdict assertions
    check(len(rows) == 357, f'output rows {len(rows)} != 357')
    check(len({r['frozen_path'] for r in rows if r['kind'] != 'ARCHIVE_METADATA'}) == 347, 'tracked paths not covered exactly once')
    fails = [r['member'] or r['frozen_path'] for r in rows if r['verdict'].startswith('FAIL')]
    check(not fails, f'FAIL rows: {fails[:10]}')
    exc = [r['frozen_path'] for r in rows if r['verdict'] == 'PASS_WITH_EXCEPTION']

    with open(a.out, 'w', newline='', encoding='utf-8') as f:     # csv default line terminator: CRLF
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(rows)

    print(json.dumps(dict(archive_sha256=sha256(b1), runs_identical=b1 == b2, members=len(names), source=len(src),
                          metadata=len(meta), excluded=sorted(set(tree) - src), manifest_entries=len(man['files_sha256']),
                          register_sha256=sha256(reg_bytes), rows=len(rows), pass_with_exception=len(exc),
                          output_sha256=sha256(open(a.out, 'rb').read()), errors=errors), indent=1))
    sys.exit(1 if errors else 0)

if __name__ == '__main__':
    main()
