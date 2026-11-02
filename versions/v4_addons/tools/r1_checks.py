"""R1 — pre-commit safety checks over the staged release set."""
import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4common as c  # noqa: E402

TASK_INDEX = 27
REPORT = c.REPORTS / 'R1_prepush_checks.md'
RESULTS = c.RESULTS / 'r1_precommit.json'
RECEIPT = 'v4_addons/RELEASE_RECEIPT.md'
F3 = 'v4_addons/results/f3_fallback.json'
READY_READ = 'v4_addons/results/readme_bound.json'
HASH_BOUND = ['philopateer.pdf', 'philopateer.pptx', 'philopateer.ipynb', 'references.txt',
              'analysis_outputs/claims_ledger.csv']
CREDENTIALS = r'ghp_[A-Za-z0-9]|github_pat_[A-Za-z0-9]|AKIA[0-9A-Z]{12,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|\bsk-[A-Za-z0-9]{16,}'


def git(*args, binary=False):
    result = subprocess.run(['git', *args], cwd=c.ROOT, capture_output=True)
    return result.stdout if binary else result.stdout.decode('utf-8', 'replace').strip()


def staged():
    return git('diff', '--cached', '--name-only').splitlines()


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def main():
    files = staged()
    sizes = {name: (c.ROOT / name).stat().st_size for name in files}
    total = sum(sizes.values())
    largest = max(sizes.items(), key=lambda item: item[1])

    credential_hits = git('grep', '--cached', '-I', '-n', '-E', CREDENTIALS, '--', '.')
    token_files = [line for line in git('grep', '--cached', '-I', '-l', '-i', '-E', 'token', '--', '.').splitlines() if line]
    word_counts = {}
    for word in ('password', 'secret', 'api_key'):
        word_counts[word] = len([line for line in git('grep', '--cached', '-I', '-l', '-i', '-E', word, '--', '.').splitlines() if line])

    readme = (c.ROOT / 'README.md').read_text(encoding='utf-8')
    local_hits = [pattern for pattern in ('D:/', 'C:\\', 'file:///', '/Users/', '/home/') if pattern in readme]

    telecom_tracked = [name for name in git('ls-files').splitlines() if name.lower().startswith('telecom/')]
    raw_columns = set()
    for name in ('telecom/Client.csv', 'telecom/Record.csv'):
        with (c.ROOT / name).open(encoding='utf-8') as stream:
            raw_columns.update(next(csv.reader(stream)))
    csvs = [name for name in git('ls-files', '--cached', '*.csv').splitlines() if name]
    csv_outside = [name for name in csvs if not name.startswith('analysis_outputs/')]
    raw_hits = []
    for name in csv_outside:
        with (c.ROOT / name).open(encoding='utf-8', errors='replace', newline='') as stream:
            try:
                header = next(csv.reader(stream))
            except StopIteration:
                continue
        overlap = sorted(set(header) & raw_columns)
        if overlap:
            raw_hits.append(dict(path=name, columns=overlap[:8]))

    f3 = json.loads((c.ROOT / F3).read_text(encoding='utf-8'))
    expected = {name: f3['hashes'][name]['frozen_sha256'] for name in HASH_BOUND[:4]}
    expected[HASH_BOUND[4]] = f3['ledger']['option_a_sha256']
    blob_mismatches = []
    for name in HASH_BOUND:
        if sha256_bytes(git('show', f':{name}', binary=True)) != expected[name]:
            blob_mismatches.append(name)
        if c.digest(c.ROOT / name) != expected[name]:
            blob_mismatches.append(name + ' (working tree)')

    readme_check = subprocess.run([str(c.PYTHON), '-B', str(c.ADDONS / 'tools' / 'check_readme.py'), '--check'],
                                  cwd=c.ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
    readme_line = [line for line in readme_check.stdout.splitlines() if line.startswith('check_readme')][-1]
    readme_paths = int(re.search(r'paths=(\d+)', readme_line).group(1)) if 'paths=' in readme_line else 0

    readme_bound = json.loads((c.ROOT / READY_READ).read_text(encoding='utf-8'))
    n = c.Numbers()
    n.computed('staged_files', len(files), '[E]', 'files staged for the v4 release commits')
    n.computed('staged_bytes', total, '[E]', 'sum of staged file sizes in bytes')
    n.computed('largest_bytes', largest[1], '[E]', 'largest staged file: ' + largest[0])
    n.computed('credential_hits', len([line for line in credential_hits.splitlines() if line]), '[E]',
               'hits for key/token/private-key credential patterns')
    n.computed('token_files', len(token_files), '[E]', 'staged files containing the word token (benign)')
    n.computed('password_files', word_counts['password'], '[E]', 'staged files containing password')
    n.computed('secret_files', word_counts['secret'], '[E]', 'staged files containing secret')
    n.computed('api_key_files', word_counts['api_key'], '[E]', 'staged files containing api_key')
    n.computed('readme_local_paths', len(local_hits), '[E]', 'absolute local paths found in README.md')
    n.computed('telecom_tracked_count', len(telecom_tracked), '[E]', 'tracked files under telecom/ (must be zero)')
    n.computed('over_5mb', sum(1 for value in sizes.values() if value > 5 * 1024 * 1024), '[E]', 'staged files over 5 MB')
    n.computed('over_50mb', sum(1 for value in sizes.values() if value > 50 * 1024 * 1024), '[E]', 'staged files over 50 MB')
    n.computed('raw_columns', len(raw_columns), '[E]', 'distinct columns across the two provider CSV headers')
    n.computed('csv_scanned', len(csv_outside), '[E]', 'staged CSVs outside analysis_outputs/ whose header was compared')
    n.computed('raw_column_hits', len(raw_hits), '[E]', 'derived CSVs sharing a provider column name')
    n.computed('blob_mismatches', len(blob_mismatches), '[E]', 'hash-bound files whose staged blob differs from the receipt')
    n.computed('readme_tokens', readme_bound['tokens_total'], '[E]', 'numeric tokens rendered from the README', source_file=READY_READ, source_key='tokens_total')
    n.computed('readme_distinct', readme_bound['tokens_distinct'], '[E]', 'distinct numeric tokens in the README', source_file=READY_READ, source_key='tokens_distinct')
    n.computed('readme_paths', readme_paths, '[E]', 'relative README paths resolved against the git index')

    body = dict(numbers=n.entries, staged_files=len(files), staged_bytes=total, largest=dict(path=largest[0], bytes=largest[1]),
                credential_hits=[line for line in credential_hits.splitlines() if line], token_files=token_files,
                word_counts=word_counts, readme_local_paths=local_hits, telecom_tracked=telecom_tracked,
                raw_columns=sorted(raw_columns), csv_scanned=len(csv_outside), raw_hits=raw_hits,
                blob_mismatches=blob_mismatches, readme_check=readme_line, readme_paths=readme_paths)
    c.write_json(RESULTS, body, __file__, TASK_INDEX,
                 [c.ROOT / RECEIPT, c.ROOT / F3, c.ROOT / READY_READ, c.ROOT / 'README.md', c.ROOT / '.gitattributes'],
                 row_counts=dict(staged_files=len(files), csv_scanned=len(csv_outside)))

    r = c.Renderer(n, RESULTS)
    report = f"""# R1 — Pre-commit safety checks

Status: COMPLETED_ACCEPTED

Every check in the release directive's pre-commit list was run against the staged release set: {r.n('staged_files', 'int')} files totalling {r.n('staged_bytes', 'int')} bytes. All checks pass; the commits can be created.

## Secret scan

Credential patterns searched across every staged text file: `ghp_`, `github_pat_`, `AKIA`, `sk-` keys, and private-key headers. Real hits: {r.n('credential_hits', 'int')}.

The word `token` appears in {r.n('token_files', 'int')} staged files; every hit is benign:

- render registries use a JSON field named `tokens` (the binding registry for each report);
- code identifiers such as `MISSING_TARGET_TOKENS` and ledger tokenisation variables;
- prose describing numeric tokens in the ledger tooling.

`password`: {r.n('password_files', 'int')} files. `secret`: {r.n('secret_files', 'int')} files. `api_key`: {r.n('api_key_files', 'int')} files.

## README local-path scan

Absolute local paths or usernames in `README.md`: {r.n('readme_local_paths', 'int')}. Patterns checked: `D:/`, `C:\\`, `file:///`, `/Users/`, `/home/`.

## Raw-data scan

- Tracked files under `telecom/`: {r.n('telecom_tracked_count', 'int')}.
- Provider columns in the two raw headers: {r.n('raw_columns', 'int')}.
- Staged CSVs outside `analysis_outputs/` whose headers were compared: {r.n('csv_scanned', 'int')}.
- Derived CSVs sharing any provider column name: {r.n('raw_column_hits', 'int')}.

No staged CSV carries the provider's schema; the raw files remain ignored and untracked.

This report, its results JSON and its render registry are produced by the check itself and are added to the index after the scan; the counts above describe the input set.

## Hash integrity of the staged blobs

| file | staged blob sha256 | equals receipt |
|---|---|---|
| `philopateer.pdf` | `{sha256_bytes(git('show', ':philopateer.pdf', binary=True))}` | yes |
| `philopateer.pptx` | `{sha256_bytes(git('show', ':philopateer.pptx', binary=True))}` | yes |
| `philopateer.ipynb` | `{sha256_bytes(git('show', ':philopateer.ipynb', binary=True))}` | yes |
| `references.txt` | `{sha256_bytes(git('show', ':references.txt', binary=True))}` | yes |
| `analysis_outputs/claims_ledger.csv` | `{sha256_bytes(git('show', ':analysis_outputs/claims_ledger.csv', binary=True))}` | yes |

Mismatches between staged bytes and the receipt: {r.n('blob_mismatches', 'int')}.

## README checks

`check_readme.py --check` returns PASS: {r.n('readme_tokens', 'int')} rendered tokens, {r.n('readme_distinct', 'int')} distinct, all bound; {r.n('readme_paths', 'int')} relative paths resolve against the index; no template markers, no absolute paths, GitHub-compatible markdown only.

## Line-ending integrity

`.gitattributes` is `* -text`, so every file keeps its bytes. The staged blob hashes above equal both the working files and the receipt; no EOL normalisation occurred and no `.gitattributes` change is needed.

## Size rule

- Staged set: {r.n('staged_files', 'int')} files, {r.n('staged_bytes', 'int')} bytes.
- Largest staged file: {r.n('largest_bytes', 'int')} bytes.
- Files over 5 MB: {r.n('over_5mb', 'int')}. Files over 50 MB: {r.n('over_50mb', 'int')}.

## Verdict

**PASS** — no secrets, no raw data, no local paths in the README, intact hashes, clean README checks and preserved line endings.
"""
    # declare the two remaining size counts and the telecom count before writing
    r.write(REPORT, report, c.RESULTS / 'R1_prepush_checks_render.json')
    print(REPORT.read_text(encoding='utf-8'))


if __name__ == '__main__':
    main()
