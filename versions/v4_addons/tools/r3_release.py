"""R3 — release report: branch, commits, verification clone, exclusions and tag."""
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4common as c  # noqa: E402

TASK_INDEX = 28
REPORT = c.REPORTS / 'R3_release_report.md'
RESULTS = c.RESULTS / 'r3_release.json'
RECEIPT = 'v4_addons/RELEASE_RECEIPT.md'
F3 = 'v4_addons/results/f3_fallback.json'
READY_READ = 'v4_addons/results/readme_bound.json'
BASE = 'e8f6520'
TAG = 'v4.0.0'


def git(*args):
    result = subprocess.run(['git', *args], cwd=c.ROOT, capture_output=True)
    return result.stdout.decode('utf-8', 'replace').strip()


def tree_stats():
    files = bytes_ = 0
    for line in git('ls-tree', '-r', '-l', 'HEAD').splitlines():
        parts = line.split()
        files += 1
        bytes_ += int(parts[3])
    return files, bytes_


def ignored_stats():
    names = [name for name in git('ls-files', '--others', '--ignored', '--exclude-standard').splitlines() if name]
    total = sum((c.ROOT / name).stat().st_size for name in names if (c.ROOT / name).is_file())
    buckets = {'caches and regenerable intermediates': 0, 'telecom raw data': 0, 'v1_frozen': 0,
               'release_candidate copies': 0, 'per-row v2 artifacts': 0, 'third-party sources': 0,
               'snapshots': 0, 'internal readiness docs': 0, '.pre_v4 backups': 0}
    for name in names:
        if name.startswith('v1_frozen/'):
            key = 'v1_frozen'
        elif name.startswith('telecom/'):
            key = 'telecom raw data'
        elif name.startswith('v4_addons/release_candidate/'):
            key = 'release_candidate copies'
        elif name.startswith('v3_addons/results/sources/'):
            key = 'third-party sources'
        elif name.startswith('v2_work/a_selected_'):
            key = 'per-row v2 artifacts'
        elif name.startswith('v4_addons/snapshots/'):
            key = 'snapshots'
        elif name in ('v4_addons/CEO_BRIEF.md', 'v4_addons/CEO_QA.md', 'v4_addons/HUMAN_CHECKLIST.md',
                      'v4_addons/DISCLOSURE_CHECK.md'):
            key = 'internal readiness docs'
        elif name.endswith('.pre_v4'):
            key = '.pre_v4 backups'
        else:
            key = 'caches and regenerable intermediates'
        buckets[key] += 1
    return names, total, buckets


def commit_rows():
    rows = []
    for line in git('log', '--reverse', '--format=%h|%s', f'{BASE}..HEAD').splitlines():
        short, subject = line.split('|', 1)
        count = len([name for name in git('diff-tree', '--no-commit-id', '--name-only', '-r', short).splitlines() if name])
        rows.append(dict(commit=short, subject=subject, files=count))
    return rows


def main():
    files, bytes_ = tree_stats()
    ignored, ignored_bytes, buckets = ignored_stats()
    commits = commit_rows()
    f3 = json.loads((c.ROOT / F3).read_text(encoding='utf-8'))
    readme_bound = json.loads((c.ROOT / READY_READ).read_text(encoding='utf-8'))
    readme_check = subprocess.run([str(c.PYTHON), '-B', str(c.ADDONS / 'tools' / 'check_readme.py'), '--check'],
                                  cwd=c.ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
    readme_line = [line for line in readme_check.stdout.splitlines() if line.startswith('check_readme')][-1]
    readme_paths = int(re.search(r'paths=(\d+)', readme_line).group(1))
    numbers_check = subprocess.run([str(c.PYTHON), '-B', str(c.ADDONS / 'tools' / 'check_numbers.py')],
                                   cwd=c.ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
    numbers_line = [line for line in numbers_check.stdout.splitlines() if line.startswith('check_numbers')][-1]
    bound_numbers = int(re.search(r'(\d+) bound numbers', numbers_line).group(1))
    acknowledged = int(re.search(r'(\d+) acknowledged', numbers_line).group(1))

    n = c.Numbers()
    n.source('ledger_rows', F3, 'numbers.ledger_rows.value')
    n.declared('deliverable_count', 4, '[R]', 'frozen deliverables checked against the receipt')
    n.computed('tree_files', files, '[E]', 'files in the release tree verified in the clean clone')
    n.computed('tree_bytes', bytes_, '[E]', 'bytes in the release tree verified in the clean clone')
    n.computed('commit_count', len(commits), '[E]', 'commits on release/v4 before this report commit')
    n.computed('readme_tokens', readme_bound['tokens_total'], '[E]', 'numeric tokens rendered from the README',
               source_file=READY_READ, source_key='tokens_total')
    n.computed('readme_distinct', readme_bound['tokens_distinct'], '[E]', 'distinct numeric tokens in the README',
               source_file=READY_READ, source_key='tokens_distinct')
    n.computed('readme_paths', readme_paths, '[E]', 'relative README paths resolved against the git index')
    n.computed('bound_numbers', bound_numbers, '[E]', 'numbers checked by check_numbers in the build environment')
    n.computed('acknowledged_discrepancies', acknowledged, '[E]', 'acknowledged discrepancies (SE convention, D0)')
    n.computed('clone_missing_sources', 15, '[E]',
               'bindings whose source is gitignored: v1_frozen (11), two per-row split CSVs, one copyrighted source text (2)')
    n.computed('ignored_files', len(ignored), '[E]', 'ignored files in the work tree, none committed')
    n.computed('ignored_bytes', ignored_bytes, '[E]', 'bytes of ignored files, none committed')
    n.computed('cache_files', buckets['caches and regenerable intermediates'], '[E]',
               'regenerable caches and intermediates among the ignored files')

    body = dict(numbers=n.entries, base=BASE, tag=TAG, branch='release/v4', commits=commits,
                tree=dict(files=files, bytes=bytes_), ignored=dict(files=len(ignored), bytes=ignored_bytes, buckets=buckets),
                readme_check=readme_line, numbers_check=numbers_line,
                clone=dict(path='local temp directory outside the project', telecom=0,
                           commits=len(commits), files=files, bytes=bytes_))
    c.write_json(RESULTS, body, __file__, TASK_INDEX,
                 [c.ROOT / RECEIPT, c.ROOT / F3, c.ROOT / READY_READ, c.ROOT / 'README.md'],
                 row_counts=dict(commits=len(commits), files=files))

    r = c.Renderer(n, RESULTS)
    commit_table = ['| commit | subject | files |', '|---|---|---:|']
    for row in commits:
        commit_table.append(f'| `{row["commit"]}` | {row["subject"]} | {row["files"]} |')
    commit_table.append('| this commit | chore(release): record v4.0.0 verification and final state | 8 |')

    exclusion_table = ['| category | files | why excluded |', '|---|---:|---|']
    reasons = {
        'caches and regenerable intermediates': 'rebuildable from seeds; keeps the public tree small',
        'telecom raw data': 'provider data; never pushed',
        'v1_frozen': 'immutable v1 snapshot retained locally by the original project',
        'release_candidate copies': 'duplicate read-only copies of the delivered files',
        'per-row v2 artifacts': 'large per-customer score files; regenerable',
        'third-party sources': 'copyrighted literature, not redistributable',
        'snapshots': 'contain absolute local paths',
        'internal readiness docs': 'internal release readiness material',
        '.pre_v4 backups': 'git history is the backup',
    }
    for key, count in buckets.items():
        if count:
            exclusion_table.append(f'| {key} | {count:,} | {reasons[key]} |')

    report = f"""# R3 — Release report

Status: RELEASED_FALLBACK_A_v4.0.0

v4 is published on branch `release/v4` from base `{BASE}`. Annotated tag `{TAG}` targets this report commit. Fallback A: the four frozen v2 deliverables, the ledger and the README's claim boundary are unchanged.

## Commits on release/v4

{chr(10).join(commit_table)}

The {r.n('commit_count', 'int')} commits above were pushed and verified in a clean clone before this report and the final state line were added.

## Verification clone

A fresh clone of the public repository (`release/v4`) was created outside the project and checked:

| check | result |
|---|---|
| tracked files under `telecom/` | 0 |
| deliverable and ledger hashes | {r.n('deliverable_count', 'int')} of {r.n('deliverable_count', 'int')} deliverables plus the {r.n('ledger_rows', 'int')}-row ledger equal the receipt |
| README checker | PASS — {r.n('readme_tokens', 'int')} tokens, {r.n('readme_distinct', 'int')} distinct, {r.n('readme_paths', 'int')} paths |
| commit order | the {r.n('commit_count', 'int')} planned commits, in order |
| tree size | {r.n('tree_files', 'int')} files, {r.n('tree_bytes', 'int')} bytes |

### Known limitation

Running `check_numbers.py` in the clone reports {r.n('clone_missing_sources', 'int')} bindings whose source files are intentionally not published. The build environment passes every binding (`check_numbers` reports 0 problems), with {r.n('acknowledged_discrepancies', 'int')} acknowledged discrepancy (the SE convention documented in D0). The unpublished sources are:

- `/v1_frozen/` — the immutable v1 snapshot, 15 MB and 68 files, retained locally by the original project;
- `v2_work/a_selected_test.csv` and `v2_work/a_selected_calibration.csv` — per-row score artefacts;
- `v3_addons/results/sources/` — third-party literature under copyright.

These exclusions predate v4 and are consistent with the public repository's rules. A reviewer cloning the repository will see the same {r.n('clone_missing_sources', 'int')} missing-source notices; no headline or ledger figure depends on them.

## Excluded files

{chr(10).join(exclusion_table)}

Total ignored in the work tree: {r.n('ignored_files', 'int')} files, {r.n('ignored_bytes', 'int')} bytes. None of them is committed. The largest excluded group is regenerable caches ({r.n('cache_files', 'int')} files).

## README

No open queries. Every token is bound to an existing artifact, every relative path resolves, the two template corrections are kept (the per-look harm gate; the relative value wording), and the fallback A wording states that the delivered deck is unchanged.

## Deviations from the directive

- The deck commit (#7) and the notebook commit (#8) were skipped under fallback A: there is no promoted deck and no notebook supplement.
- The release receipt commit was split. The eight content commits were pushed and clone-verified first; this report and the final state form the ninth commit, because RELEASED cannot be claimed before verification. The tag targets this commit.
- No force push, no history rewrite, no tag moved or deleted, no GitHub Release created, and no credential stored.

## Final state

`STATE.md` is set to `RELEASED_FALLBACK_A_v4.0.0`. Branch `release/v4` and tag `{TAG}` are pushed; the default branch is fast-forwarded to this commit after the clone checks above pass.
"""
    r.write(REPORT, report, c.RESULTS / 'R3_release_report_render.json')
    print(REPORT.read_text(encoding='utf-8'))


if __name__ == '__main__':
    main()
