"""Shared task-report writer (section 8 template). Numbers in the evidence table come from a results JSON via Renderer."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4common as c  # noqa: E402


def environment_line(body):
    prov = body['provenance']
    pools = ', '.join(f'{pool["internal_api"]} {pool["version"]} num_threads={pool["num_threads"]}' for pool in prov['runtime']['pools'])
    return f'Environment: Python {prov["python_version"].split()[0]}; verify_runtime pools: {pools}; seed {prov["seed"]}.'


def write_report(card, title, status, summary, results_json, evidence, acceptance, deviations, open_items, commands, boundary, extra_sections=None):
    """evidence: list of (number_name, spec). acceptance/deviations/open_items: lists of markdown lines. commands: list of shell lines."""
    results_json = Path(results_json)
    body = json.loads(results_json.read_text(encoding='utf-8'))
    numbers = body['numbers']
    r = c.Renderer(numbers, results_json)
    lines = [f'# {card} — {title}', f'Status: {status}', '', summary, '', '## Evidence table', '',
             '| number | value | source_file | source_key / formula | tag |', '|---|---:|---|---|---|']
    for name, spec in evidence:
        entry = numbers[name]
        source = ('`' + entry['source_file'] + '`') if entry.get('source_file') else ''
        key = '`' + str(entry.get('source_key') or entry.get('formula') or entry.get('note', '')) + '`'
        lines.append(f'| {name} | {r.n(name, spec)} | {source} | {key} | {entry["tag"]} |')
    for heading, content in (extra_sections or []):
        lines += ['', f'## {heading}', ''] + [line(r) if callable(line) else line for line in content]
    lines += ['', '## Acceptance checks', ''] + [line(r) if callable(line) else line for line in acceptance]
    lines += ['', '## Deviations from the brief', ''] + ([line(r) if callable(line) else line for line in deviations] or ['- none'])
    lines += ['', '## Open questions / [DECISION NEEDED] items', ''] + ([line(r) if callable(line) else line for line in open_items] or ['- none'])
    lines += ['', '## Commands run', '', '```bash', 'PY="C:/Users/FGstore/AppData/Local/Programs/Python/Python311/python.exe"; R="D:/progs/IDE/MainProjs/AI/GCI2026/finalA"',
              'cd "$R/v4_addons/tools"'] + commands + ['```', '', environment_line(body), '', f'Boundary check: before/after hashes clean? {boundary}', '']
    target = c.REPORTS / f'{card}_report.md'
    r.write(target, '\n'.join(lines), c.RESULTS / f'{card}_report_render.json')
    print('wrote', target.relative_to(c.ROOT).as_posix())
    return target
