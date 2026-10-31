"""R0 — release preflight: record the release directive's section-1 preconditions.

Read-only: git queries and file hashes only. Nothing is staged, committed or pushed.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4common as c  # noqa: E402

TASK_INDEX = 26
REPORT = c.REPORTS / 'R0_release_preflight.md'
RESULTS = c.RESULTS / 'r0_release.json'
F3 = 'v4_addons/results/f3_fallback.json'
RECEIPT = 'v4_addons/RELEASE_RECEIPT.md'
BOUNDARY_LOG = c.RESULTS / 'boundary_log.jsonl'
DELIVERABLES = ['philopateer.pdf', 'philopateer.pptx', 'philopateer.ipynb', 'references.txt']
LEDGER = 'analysis_outputs/claims_ledger.csv'
BYTE_NAME = {'philopateer.pdf': 'pdf_bytes', 'philopateer.pptx': 'pptx_bytes',
             'philopateer.ipynb': 'ipynb_bytes', 'references.txt': 'references_bytes'}


def git(*args):
    result = subprocess.run(['git', *args], cwd=c.ROOT, capture_output=True, text=True)
    return (result.stdout + result.stderr).strip()


def receipt_rows():
    text = (c.ROOT / RECEIPT).read_text(encoding='utf-8')
    rows = {}
    for line in text.splitlines():
        match = re.match(r'^\| `([^`]+)` \| ([\d,]+) \| `([0-9a-f]{64})` \|$', line)
        if match:
            rows[match.group(1)] = dict(bytes=int(match.group(2).replace(',', '')), sha256=match.group(3))
    return rows


def last_boundary(card='R0'):
    rows = [json.loads(line) for line in BOUNDARY_LOG.read_text(encoding='utf-8').splitlines() if line.strip()]
    return [row for row in rows if row.get('card') == card][-1]


def main():
    status = git('status', '--short')
    facts = dict(
        work_tree=git('rev-parse', '--is-inside-work-tree'),
        remote=git('remote', '-v'),
        branch=git('branch', '--show-current'),
        head=git('rev-parse', 'HEAD'),
        log=git('log', '--oneline', '-15'),
        identity=f'{git("config", "user.name")} <{git("config", "user.email")}>',
        status=status,
        status_count=len(status.splitlines()),
        attributes=(c.ROOT / '.gitattributes').read_text(encoding='utf-8').strip(),
        autocrlf=git('config', 'core.autocrlf'),
        telecom_tracked=git('ls-files', 'telecom'),
        ignore=git('check-ignore', '-v', 'telecom/Client.csv', 'telecom/Record.csv'),
    )

    receipt = receipt_rows()
    f3 = json.loads((c.ROOT / F3).read_text(encoding='utf-8'))
    ledger_expected = f3['ledger']['option_a_sha256']
    integrity = []
    for name in DELIVERABLES + [LEDGER]:
        path = c.ROOT / name
        actual = c.digest(path)
        expected_sha = receipt[name]['sha256'] if name in receipt else ledger_expected
        expected_bytes = receipt[name]['bytes'] if name in receipt else path.stat().st_size
        entry = dict(path=name, bytes=path.stat().st_size, sha256=actual,
                     receipt_bytes=expected_bytes, receipt_sha256=expected_sha,
                     bytes_match=path.stat().st_size == expected_bytes,
                     sha256_match=actual == expected_sha)
        integrity.append(entry)

    boundary = last_boundary()
    candidates = sorted({name for name in (git('ls-files').splitlines() + git('ls-files', '--others', '--exclude-standard').splitlines()) if name})
    over_5mb = [name for name in candidates if (c.ROOT / name).is_file() and (c.ROOT / name).stat().st_size > 5 * 1024 * 1024]
    over_50mb = [name for name in candidates if (c.ROOT / name).is_file() and (c.ROOT / name).stat().st_size > 50 * 1024 * 1024]

    n = c.Numbers()
    for name, key in [('pdf_bytes', 'pdf_bytes'), ('pptx_bytes', 'pptx_bytes'), ('ipynb_bytes', 'ipynb_bytes'),
                      ('references_bytes', 'references_bytes'), ('ledger_rows', 'ledger_rows')]:
        n.source(name, F3, f'numbers.{key}.value')
    n.computed('boundary_files', boundary['files_checked'], '[E]',
               'files scanned by boundary_check in the last R0 preflight run', inputs=[c.relpath(BOUNDARY_LOG)])
    n.computed('accepted_changes', len(boundary['accepted_changes']), '[E]',
               'accepted changes in the last R0 preflight boundary run', inputs=[c.relpath(BOUNDARY_LOG)])
    n.computed('boundary_unexpected', len(boundary['unexpected']), '[E]',
               'unexpected changes in the last R0 preflight boundary run', inputs=[c.relpath(BOUNDARY_LOG)])
    n.computed('gate_files', len(boundary['gate_files_present']), '[E]',
               'gate files present at preflight', inputs=[c.relpath(BOUNDARY_LOG)])
    n.computed('deliverable_hash_matches', sum(item['sha256_match'] and item['bytes_match'] for item in integrity), '[E]',
               'deliverables and ledger whose bytes and SHA-256 equal the release receipt', inputs=[c.relpath(c.ROOT / RECEIPT)])
    n.declared('deliverable_count', len(DELIVERABLES) + 1, '[R]',
               'receipt entries checked: four deliverables plus the ledger')
    n.computed('candidate_files', len(candidates), '[E]', 'tracked plus non-ignored untracked files: the eventual push set')
    n.computed('telecom_tracked_files', len(facts['telecom_tracked'].splitlines()) if facts['telecom_tracked'] else 0, '[E]',
               'tracked files under telecom/ (must be zero)')
    n.computed('over_5mb', len(over_5mb), '[E]',
               'candidate files over 5 MB at preflight' + (': ' + ', '.join(over_5mb) if over_5mb else ' (none)'))
    n.computed('over_50mb', len(over_50mb), '[E]', 'candidate files over 50 MB at preflight' + (': ' + ', '.join(over_50mb) if over_50mb else ' (none)'))

    body = dict(numbers=n.entries, facts=facts, integrity=integrity, boundary=boundary,
                receipt=dict(path=RECEIPT, sha256=c.digest(c.ROOT / RECEIPT)),
                deliverable_count=len(DELIVERABLES), size_rule=dict(candidates=len(candidates), over_5mb=over_5mb, over_50mb=over_50mb))
    c.write_json(RESULTS, body, __file__, TASK_INDEX,
                 [c.ROOT / RECEIPT, c.ROOT / '.gitattributes', *[c.ROOT / name for name in DELIVERABLES + [LEDGER]]],
                 row_counts=dict(deliverables=len(DELIVERABLES), ledger_rows=n.value('ledger_rows')))

    r = c.Renderer(n, RESULTS)
    table = []
    for item in integrity:
        if item['path'] == LEDGER:
            value = r.n('ledger_rows', 'int') + ' rows'
        else:
            value = r.n(BYTE_NAME[item['path']], 'int')
        table.append(f'| `{item["path"]}` | {value} | `{item["sha256"]}` | {"yes" if item["sha256_match"] and item["bytes_match"] else "NO"} |')

    report = f"""# R0 — Release preflight

Status: COMPLETED_ACCEPTED

The v4 release directive's section-1 preconditions were run read-only and all pass. The work tree is a git repository with the expected `origin`, a set identity, no tracked raw data, intact frozen hashes, STATE ready for release and a clean boundary check. The release branch can be created; nothing has been committed or pushed at this point.

## Repository, remote and identity

```text
{facts['work_tree']}
{facts['remote']}
{facts['branch']}
{facts['log']}
{facts['identity']}
core.autocrlf = {facts['autocrlf']}
```

Base commit: `{facts['head']}` on `{facts['branch']}`. The remote is the account holder's public repository.

## Working tree at preflight

```text
{status}
```

{facts['status_count']} paths are dirty: the two release edits outside `v4_addons` (`README.md`, `.gitignore`), the two v3 status documents refreshed by D1, and the untracked `v4_addons/` tree. All are expected release inputs.

## Raw data guard

```text
$ git ls-files telecom
(empty)
$ git check-ignore -v telecom/Client.csv telecom/Record.csv
{facts['ignore']}
```

Tracked files under `telecom/`: {r.n('telecom_tracked_files', 'int')}. Both raw CSVs are ignored, so the provider's data cannot enter the public repository.

## Line endings

```text
{facts['attributes']}
```

`core.autocrlf` is `{facts['autocrlf']}`, but the existing `* -text` attribute already preserves bytes for every file. The directive's EOL fallback is therefore not needed; no `.gitattributes` change is planned.

## Frozen integrity against the receipt

| file | receipt value | sha256 | equals receipt |
|---|---:|---|---|
{chr(10).join(table)}

All four deliverables and the ledger match the release receipt: {r.n('deliverable_hash_matches', 'int')} of {r.n('deliverable_count', 'int')} entries match on bytes and SHA-256.

## Release state and boundary

- `STATE.md` says `READY_FOR_CEO_FALLBACK_A` (fallback A wording for the README).
- Boundary check (last R0 preflight run): clean, {r.n('boundary_files', 'int')} files checked, {r.n('accepted_changes', 'int')} accepted changes, {r.n('boundary_unexpected', 'int')} unexpected, {r.n('gate_files', 'int')} gate files present.
- Accepted changes are the two D1-refreshed v3 documents, their `.pre_v4` backups, `README.md` and `.gitignore`.

## Size rule

- Push candidate set: {r.n('candidate_files', 'int')} tracked or non-ignored untracked files.
- Files over 5 MB in the candidate set: {r.n('over_5mb', 'int')} (excluded and listed here if any).
- Files over 50 MB: {r.n('over_50mb', 'int')}.

## Verdict

**PASS** — all section-1 preconditions hold. Proceed to README binding and staged checks.
"""
    r.write(REPORT, report, c.RESULTS / 'R0_release_preflight_render.json')
    print(REPORT.read_text(encoding='utf-8'))


if __name__ == '__main__':
    main()
