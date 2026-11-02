"""G4 number-provenance check.

Every entry under "numbers" in v4_addons/results/*.json must either
  * name a source_file + source_key whose current content equals the stored value (and whose sha256 matches), or
  * carry a formula over other entries that re-evaluates to the stored value, or
  * be marked computed=True (produced by a seeded script; the script/seed are the provenance).
--scan <report.md> additionally checks that every numeric token in a rendered report is in its render registry
(results/<name>_render.json) or matches the structural allowlist (dates, IDs, section numbers).
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4common as c  # noqa: E402

STRUCTURAL = [
    r'^\d{4}-\d{2}-\d{2}$', r'^\d{1,2}:\d{2}$', r'^20\d\d$', r'^\d{1,2}$', r'^\d+\.\d+\.\d+$', r'^20261\d{3}$',   # dates, times, years, small ordinals, versions, seeds
    r'^[CDGHMSWE]\d{1,4}$', r'^WP\d$', r'^B\u2032?$', r'^C0\d{3}$',                             # card / gate / claim identifiers
]
TOKEN = re.compile(r'(?<![A-Za-z_\u2212\-\d.])[\u2212\-+]?\$?\d[\d,]*(?:\.\d+)*(?:%|k| pp|\u00d7)?(?![A-Za-z_\d])')
SKIP_LINE = re.compile(r'sha256|[0-9a-f]{40,}|file:///', re.I)


def check_results(verbose):
    failures, warnings, count = [], [], 0
    for path in sorted(c.RESULTS.glob('*.json')):
        body = json.loads(path.read_text(encoding='utf-8'))
        numbers = body.get('numbers')
        if not isinstance(numbers, dict):
            continue
        values = {name: entry['value'] for name, entry in numbers.items()}
        for name, entry in numbers.items():
            count += 1
            label = f'{path.name}:{name}'
            if entry.get('tag') not in c.TAGS:
                failures.append(f'{label}: missing/invalid tag {entry.get("tag")!r}')
            if entry.get('source_file'):
                source = c.ROOT / entry['source_file']
                if not source.is_file():
                    failures.append(f'{label}: source missing {entry["source_file"]}')
                    continue
                if c.digest(source) != entry.get('sha256_of_source'):
                    failures.append(f'{label}: source sha256 changed for {entry["source_file"]}')
                if entry.get('computed'):
                    continue
                try:
                    found = c.read_source(entry['source_file'], entry['source_key'],
                                          entry.get('source_encoding', 'utf-8'))
                except Exception as error:  # noqa: BLE001
                    failures.append(f'{label}: cannot re-read {entry["source_key"]}: {error}')
                    continue
                if not c.close(found, entry['value']):
                    failures.append(f'{label}: source value {found!r} != stored {entry["value"]!r}')
            elif entry.get('formula') is not None:
                try:
                    recomputed = c.evaluate(entry['formula'], values)
                except Exception as error:  # noqa: BLE001
                    failures.append(f'{label}: formula failed: {error}')
                    continue
                if not c.close(recomputed, entry['value']):
                    failures.append(f'{label}: formula {entry["formula"]} -> {recomputed!r} != stored {entry["value"]!r}')
                if 'expected' in entry and not entry.get('matches_expected'):
                    if entry.get('discrepancy_note'):
                        warnings.append(f'{label}: section-9 expectation {entry["expected"]!r} not matched; value {entry["value"]!r}; acknowledged: {entry["discrepancy_note"]}')
                    else:
                        failures.append(f'{label}: does not match section-9 expectation {entry["expected"]!r} (reported, not tuned)')
            elif entry.get('computed'):
                if 'seed' not in entry and entry.get('stochastic'):
                    failures.append(f'{label}: stochastic computed value without seed')
            else:
                failures.append(f'{label}: no source_file, formula or computed marker')
            if verbose:
                print(f'  ok {label} = {entry["value"]!r}')
    return count, failures, warnings


def scan_report(report):
    report = Path(report)
    registry_path = c.RESULTS / (report.stem + '_render.json')
    if not registry_path.exists():
        return [f'{report.name}: no render registry {registry_path.name}']
    registry = json.loads(registry_path.read_text(encoding='utf-8'))
    text = report.read_text(encoding='utf-8')
    problems = []
    if c.text_digest(text) != registry['report_sha256']:
        problems.append(f'{report.name}: text changed since it was rendered (hash mismatch)')
    results = json.loads((c.ROOT / registry['results_json']).read_text(encoding='utf-8'))['numbers']
    tokens = {}
    for item in registry['tokens']:
        tokens.setdefault(item['token'], set()).add(item['name'])
        if not c.close(results[item['name']]['value'], item['value']):
            problems.append(f'{report.name}: token {item["token"]} bound to {item["name"]} but results value moved')
    unbound = []
    in_fence = False
    for line_number, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith('```'):
            in_fence = not in_fence
            continue
        if in_fence or line.startswith('#') or SKIP_LINE.search(line):
            continue
        probe = re.sub(r'`[^`]*`', '', line)
        probe = re.sub(r'\[\[[^\]]*\]\]|\]\([^)]*\)|[A-Za-z_][\w\-]*\.(?:py|json|csv|md|txt|ipynb|pdf|pptx)', '', probe)
        for match in TOKEN.finditer(probe):
            token = match.group(0).rstrip(',')
            bare = token.strip('+')
            if bare in tokens or bare.lstrip('+\u2212-') in tokens:
                continue
            if any(re.match(pattern, bare.lstrip('+\u2212-')) for pattern in STRUCTURAL):
                continue
            unbound.append((line_number, token))
    if unbound:
        problems.append(f'{report.name}: {len(unbound)} unbound numeric tokens: ' + ', '.join(f'L{n}:{t}' for n, t in unbound[:40]))
    return problems


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scan', nargs='*', default=[])
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()
    count, failures, warnings = check_results(args.verbose)
    for report in args.scan:
        failures.extend(scan_report(report))
    print(f'check_numbers: {count} bound numbers checked; {len(failures)} problems; {len(warnings)} acknowledged discrepancies')
    for item in warnings:
        print('  WARN', item)
    for item in failures:
        print('  !!', item)
    sys.exit(1 if failures else 0)


if __name__ == '__main__':
    main()
