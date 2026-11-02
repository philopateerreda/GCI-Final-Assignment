"""Release README check (v4 Release Directive, section 4.7).

usage:
  python -B -X utf8 check_readme.py --build   # bind every README number, write results/readme_bound.json
  python -B -X utf8 check_readme.py --check   # verify README, paths, markdown, numbers against the registry

Release-only tool: it is not part of the frozen v2/v3 evidence set and writes nothing outside v4_addons/results/.
"""
import argparse
import csv
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / 'README.md'
REGISTRY = ROOT / 'v4_addons/results/readme_bound.json'

JSON_SOURCES = [
    'analysis_outputs/summary.json',
    'analysis_outputs/model_selection.json',
    'analysis_outputs/feature_manifest.json',
    'analysis_outputs/bootstrap_intervals.json',
    'analysis_outputs/pilot_design.json',
    'analysis_outputs/delivery_checks.json',
    'analysis_outputs/environment.json',
    'v2_work/final_metrics.json',
    'v2_work/b_design.json',
    'v2_work/chart_claims.json',
    'v2_work/chart_numeric_sources.json',
    'v2_work/static_claim_sources.json',
    'v2_work/office_geometry_check.json',
    'v2_work/d_results/gate_d.json',
    'v2_work/d_results/learning_curve_summary.json',
    'v3_addons/results/wp1_power.json',
    'v3_addons/results/wp2_evsi.json',
    'v3_addons/results/wp3_roi_band.json',
    'v3_addons/results/wp4_protocol.json',
    'v3_addons/results/wp5_label_shift.json',
    'v3_addons/results/wp8_model.json',
    'v3_addons/results/inventory.json',
    'v3_addons/results/stop_report.json',
    'v4_addons/results/yardstick.json',
    'v4_addons/results/f0_closeout.json',
    'v4_addons/results/m1_baseline.json',
    'v4_addons/results/f3_fallback.json',
    'v4_addons/results/f5_ceo.json',
    'v4_addons/results/f6_disclosure.json',
    'v4_addons/results/f7_release.json',
    'v4_addons/results/d6_text_blocks.json',
]
CSV_SOURCES = [
    'analysis_outputs/claims_ledger.csv',
    'v2_work/d_results/gate_d.csv',
    'v2_work/d_results/learning_curve_summary.csv',
    'v3_addons/results/wp1_power.csv',
    'v3_addons/results/wp2_decision_quality.csv',
    'v3_addons/results/wp5_break_even_grid.csv',
]
TEXT_BINDINGS = [
    dict(token='31', file='FINAL_ASSESSMENT_HANDOFF.md', pattern=r'(?P<value>31) leaves'),
    dict(token='0.03', file='FINAL_ASSESSMENT_HANDOFF.md', pattern=r'learning rate (?P<value>0\.03)\b'),
]
COMPUTED = [
    dict(token='846608', rule='file_size', file='philopateer.pdf'),
    dict(token='278', rule='csv_rows', file='analysis_outputs/claims_ledger.csv'),
    dict(token='52', rule='notebook_cells', file='philopateer.ipynb'),
    dict(token='25', rule='notebook_code_cells', file='philopateer.ipynb'),
]
ALLOWED_ABSENT = {'Client.csv', 'Record.csv', 'telecom/'}
ALERTS = {'NOTE', 'TIP', 'IMPORTANT', 'WARNING', 'CAUTION'}

TOKEN = re.compile(r'(?<![A-Za-z_\u2212\-\d.])[\u2212\-+]?\$?\d[\d,]*(?:\.\d+)*(?:%|k| pp|\u00d7)?(?![A-Za-z_\d])')
STRUCTURAL = [
    r'^\d{4}-\d{2}-\d{2}$', r'^\d{1,2}:\d{2}$', r'^20\d\d$', r'^\d{1,2}$', r'^\d+\.\d+\.\d+$', r'^20261\d{3}$',
    r'^[CDGHMSWE]\d{1,4}$', r'^WP\d$', r'^B\u2032?$', r'^C0\d{3}$',
]
FILE_NAME = re.compile(r'[A-Za-z_][\w\-]*\.(?:py|json|csv|md|txt|ipynb|pdf|pptx)')
PATH_WITH_DIR = re.compile(r'(?<![\w/])([A-Za-z_][\w.\-]*(?:/[\w.\-]+)+/?)')
BARE_FILE = re.compile(r'(?<![\w/.\-])([A-Za-z_][\w.\-]*\.(?:py|json|csv|md|txt|ipynb|pdf|pptx))')
ABS_PATH = re.compile(r'(?:[A-Za-z]:[\\/]|file:///|/Users/|/home/|\\\\[A-Za-z0-9])')


def digest(path):
    import hashlib
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def canon(token):
    t = token.strip().rstrip(',')
    t = t.replace('\u2212', '-').replace('\u00d7', '')
    t = t.lstrip('+-')
    t = t.replace('$', '').replace(',', '').replace('%', '').replace(' pp', '').strip()
    return t


def variants(value):
    a = abs(float(value))
    out = set()
    for d in range(0, 7):
        out.add(f'{a:.{d}f}')
        out.add(f'{a:,.{d}f}')
        out.add(f'{a * 100:.{d}f}')
        out.add(f'${a:,.{d}f}')
    for d in range(0, 4):
        out.add(f'{a * 100:.{d}f}%')
    if a >= 1000:
        k = a / 1000
        if abs(k - round(k)) < 1e-12:
            out.add(f'{k:g}k')
    if isinstance(value, int):
        out.add(str(value))
    return out


def walk_json(node, source, wanted, bound):
    if isinstance(node, bool) or node is None:
        return
    if isinstance(node, (int, float)):
        for item in variants(node):
            if item in wanted:
                bound.setdefault(item, set()).add(source)
        return
    if isinstance(node, dict):
        for value in node.values():
            walk_json(value, source, wanted, bound)
        return
    if isinstance(node, list):
        for value in node:
            walk_json(value, source, wanted, bound)
        return
    if isinstance(node, str):
        for match in TOKEN.finditer(node):
            item = canon(match.group(0))
            if item in wanted:
                bound.setdefault(item, set()).add(source)


def readme_tokens():
    text = README.read_text(encoding='utf-8')
    items = []
    in_fence = False
    for number, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith('```'):
            in_fence = not in_fence
            continue
        if in_fence or line.startswith('#'):
            continue
        probe = re.sub(r'\[[^\]]*\]\([^)]*\)', '', line)
        probe = re.sub(r'https?://\S+', '', probe)
        probe = FILE_NAME.sub('', probe)
        for match in TOKEN.finditer(probe):
            items.append((number, match.group(0).rstrip(',')))
    return text, items


def is_structural(token):
    bare = canon(token)
    return any(re.match(pattern, bare) for pattern in STRUCTURAL)


def build_map(wanted):
    bound, sources = {}, {}
    for source in JSON_SOURCES:
        path = ROOT / source
        body = json.loads(path.read_text(encoding='utf-8'))
        walk_json(body, source, wanted, bound)
        sources[source] = digest(path)
    for source in CSV_SOURCES:
        path = ROOT / source
        with path.open(encoding='utf-8', newline='') as stream:
            for row in csv.reader(stream):
                for cell in row:
                    for match in TOKEN.finditer(cell):
                        item = canon(match.group(0))
                        if item in wanted:
                            bound.setdefault(item, set()).add(source)
        sources[source] = digest(path)
    for rule in TEXT_BINDINGS:
        path = ROOT / rule['file']
        text = path.read_text(encoding='utf-8')
        match = re.search(rule['pattern'], text)
        if not match:
            raise SystemExit(f'text binding lost: {rule["pattern"]!r} not in {rule["file"]}')
        if canon(match.group('value')) != canon(rule['token']):
            raise SystemExit(f'text binding moved: {rule["file"]} has {match.group("value")!r} for {rule["token"]!r}')
        bound.setdefault(canon(rule['token']), set()).add(rule['file'])
        sources[rule['file']] = digest(path)
    for rule in COMPUTED:
        path = ROOT / rule['file']
        rule_value = compute_rule(rule)
        if canon(rule['token']) != canon(rule_value):
            raise SystemExit(f'computed binding moved: {rule["file"]} {rule["rule"]} = {rule_value!r}, README has {rule["token"]!r}')
        bound.setdefault(canon(rule['token']), set()).add(rule['file'])
        sources[rule['file']] = digest(path)
    return bound, sources


def compute_rule(rule):
    path = ROOT / rule['file']
    if rule['rule'] == 'file_size':
        return str(path.stat().st_size)
    if rule['rule'] == 'csv_rows':
        with path.open(encoding='utf-8', newline='') as stream:
            return str(sum(1 for _ in csv.reader(stream)) - 1)
    if rule['rule'] == 'notebook_cells':
        return str(len(json.loads(path.read_text(encoding='utf-8'))['cells']))
    if rule['rule'] == 'notebook_code_cells':
        cells = json.loads(path.read_text(encoding='utf-8'))['cells']
        return str(sum(1 for cell in cells if cell.get('cell_type') == 'code'))
    raise SystemExit(f'unknown computed rule {rule["rule"]!r}')


def tracked_files():
    try:
        out = subprocess.check_output(['git', 'ls-files'], cwd=ROOT, text=True, encoding='utf-8')
    except Exception as error:  # noqa: BLE001
        raise SystemExit(f'git ls-files failed: {error}')
    return [line.strip() for line in out.splitlines() if line.strip()]


def readme_paths(text):
    paths = []
    for number, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith('```') or line.startswith('#'):
            continue
        probe = re.sub(r'https?://\S+', '', line)
        for match in PATH_WITH_DIR.finditer(probe):
            paths.append((number, match.group(1)))
        for match in BARE_FILE.finditer(probe):
            paths.append((number, match.group(1)))
    return paths


def check_structure(text, tracked, tokens, bound):
    problems = []
    if '\u27e6' in text or 'QODER:' in text:
        problems.append('template placeholder or QODER comment left in README')
    if text.startswith('---\n'):
        problems.append('README starts with YAML front matter')
    if '[[' in text:
        problems.append('Obsidian wikilink syntax found')
    for match in re.finditer(r'^>\s*\[!([A-Za-z]+)\]', text, re.M):
        if match.group(1).upper() not in ALERTS:
            problems.append(f'unknown alert type {match.group(1)!r}')
    for match in ABS_PATH.finditer(text):
        problems.append(f'absolute local path {match.group(0)!r}')
    tracked_set = set(tracked)
    for number, path in readme_paths(text):
        if path in ALLOWED_ABSENT:
            continue
        if path.endswith('/'):
            if not any(item.startswith(path) for item in tracked_set):
                problems.append(f'L{number}: directory {path!r} has no tracked files')
            continue
        if path in tracked_set:
            continue
        if '/' not in path:
            hits = [item for item in tracked_set if item.rsplit('/', 1)[-1] == path]
            if len(hits) == 1:
                continue
            problems.append(f'L{number}: {path!r} is not a unique tracked file')
        else:
            problems.append(f'L{number}: {path!r} is not tracked')
    unbound = []
    for number, token in tokens:
        item = canon(token)
        if item in bound or is_structural(token):
            continue
        unbound.append(f'L{number}:{token}')
    if unbound:
        problems.append(f'{len(unbound)} unbound numeric tokens: ' + ', '.join(unbound[:40]))
    return problems


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--build', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.build == args.check:
        raise SystemExit('choose exactly one of --build or --check')
    text, tokens = readme_tokens()
    wanted = {canon(token) for _, token in tokens}
    bound, sources = build_map(wanted)
    tracked = tracked_files()
    problems = check_structure(text, tracked, tokens, bound)
    if args.build:
        registry = dict(
            generated_utc=__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
            readme_sha256=digest(README),
            readme_words=len(text.split()),
            tokens_total=len(tokens),
            tokens_distinct=len(wanted),
            sources=sources,
            text_bindings=TEXT_BINDINGS,
            computed=COMPUTED,
            tokens={item: sorted(bound[item]) for item in sorted(bound) if item in wanted},
            structural=sorted({token for _, token in tokens if is_structural(token) and canon(token) not in bound}),
        )
        REGISTRY.write_text(json.dumps(registry, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    else:
        if not REGISTRY.exists():
            raise SystemExit('no registry; run --build first')
        registry = json.loads(REGISTRY.read_text(encoding='utf-8'))
        if registry.get('readme_sha256') != digest(README):
            problems.append('README changed since the binding registry was built')
        for source, expected in registry.get('sources', {}).items():
            if not (ROOT / source).is_file():
                problems.append(f'source missing: {source}')
            elif digest(ROOT / source) != expected:
                problems.append(f'source changed since binding: {source}')
    if problems:
        print(f'check_readme {args.build and "build" or "check"}: {len(problems)} problem(s)')
        for item in problems:
            print('  !!', item)
        return 1
    print(f'check_readme {args.build and "build" or "check"}: PASS; tokens={len(tokens)}; '
          f'distinct={len(wanted)}; bound={len(bound)}; paths={len(readme_paths(text))}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
