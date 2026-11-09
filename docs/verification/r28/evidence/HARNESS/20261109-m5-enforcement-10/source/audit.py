# SPDX-FileCopyrightText: 2026 TRICORE contributors
# SPDX-License-Identifier: Apache-2.0
"""Read-only evidence verification; --output writes a new audit, never historical artifacts."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]
BASELINE = 'ee048142c805b0a14324a3ed0557326d9880e653'
EVIDENCE = ROOT / 'docs/verification/r28/evidence'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.check_output(['git', '-c', f'safe.directory={ROOT.as_posix()}', *args], cwd=ROOT)


def audit(run_id):
    problems, manifests, cases = [], [], {}
    for manifest in sorted(EVIDENCE.glob(f'*/{run_id}/checksums.json')):
        listed = json.loads(manifest.read_text(encoding='utf-8'))
        actual = {p.relative_to(manifest.parent).as_posix() for p in manifest.parent.rglob('*')
                  if p.is_file() and p != manifest}
        if actual != set(listed):
            problems.append(f'{manifest}: unlisted or missing files')
        for name, expected in listed.items():
            file = manifest.parent / name
            if not file.is_file() or sha(file.read_bytes()) != expected:
                problems.append(f'{file}: checksum mismatch/missing')
        manifests.append({'path': manifest.relative_to(ROOT).as_posix(), 'payloads': len(listed)})
        summary_path = manifest.parent / 'result.json'
        if summary_path.exists():
            summary = json.loads(summary_path.read_text(encoding='utf-8'))
            counts = {'PASS': 0, 'FAIL': 0}
            for case in summary['cases']:
                artifact = json.loads((manifest.parent / (case['name'] + '.json')).read_text(encoding='utf-8'))
                if artifact['status'] != case['status'] or artifact['name'] != case['name']:
                    problems.append(f'{summary_path}: case summary mismatch')
                counts[case['status']] = counts.get(case['status'], 0) + 1
            if len(summary['cases']) != summary['database_cases_executed']:
                problems.append(f'{summary_path}: count mismatch')
            cases[summary['test_id']] = counts
    if not manifests:
        problems.append('no manifests found')
    return {'run_id': run_id, 'status': 'PASS' if not problems else 'FAIL',
            'problems': problems, 'manifests': manifests,
            'payloads_verified': sum(x['payloads'] for x in manifests), 'case_counts': cases}


def historical():
    result = audit('20261109-m5-isolated-05')
    paths = ['docs/verification/r28/r28-q03-m5-verification-report.md',
             *[p.relative_to(ROOT).as_posix() for p in EVIDENCE.glob('*/20261109-m5-isolated-05')]]
    changed = git('diff', '--name-only', BASELINE, '--', *paths).decode().strip()
    if changed:
        result['problems'].append('historical bytes changed from baseline: ' + changed)
    source = EVIDENCE / 'HARNESS/20261109-m5-isolated-05/source'
    result['source_snapshot_matches_baseline'] = {
        p.name: p.read_bytes() == git('show', BASELINE + ':tests/r28_m5/' + p.name)
        for p in source.iterdir() if p.is_file()}
    if not all(result['source_snapshot_matches_baseline'].values()):
        result['problems'].append('run05 source snapshot differs from baseline')
    old = ast.parse((source / 'run.py').read_text(encoding='utf-8'))
    new = ast.parse((ROOT / 'tests/r28_m5/run.py').read_text(encoding='utf-8'))
    names = ('case', 'x25', 'privileges', 'concurrent', 'snapshot', 'assignment', 'executor_sql', 'fault_sql')
    functions = lambda tree: {n.name: ast.dump(n, include_attributes=False) for n in ast.walk(tree)
                              if isinstance(n, ast.FunctionDef) and n.name in names}
    result['historical_oracles_unchanged'] = functions(old) == functions(new)
    if not result['historical_oracles_unchanged']:
        result['problems'].append('historical oracle changed')
    result['status'] = 'PASS' if not result['problems'] else 'FAIL'
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    value = {'baseline': BASELINE, 'head': git('rev-parse', 'HEAD').decode().strip(),
             'historical_run05': historical(), 'current_run': audit(args.run_id),
             'limitation': 'Saved-artifact integrity and oracle provenance only, not independent database execution/sign-off.'}
    text = json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        target = args.output.resolve()
        if not target.is_relative_to(EVIDENCE) or target.exists():
            raise ValueError('audit output must be a new file under evidence')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8')
    print(text)
    return 0 if value['historical_run05']['status'] == value['current_run']['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
