"""G1 write-boundary check: hash the project tree and compare with the baseline snapshot.

usage:
  python -B -X utf8 boundary_check.py --snapshot            # create snapshots/baseline_<date>.json (once)
  python -B -X utf8 boundary_check.py --card D1 --phase pre # compare and append to results/boundary_log.jsonl
Changes outside v4_addons/ are accepted only when snapshots/allowed_changes.json lists the file with the
current sha256 as post_sha256. Anything else -> exit 1 (STOP).
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4common as c  # noqa: E402

EXCLUDED_DIRS = ('.git', '__pycache__')
LOG = c.RESULTS / 'boundary_log.jsonl'
ALLOWED = c.SNAPSHOTS / 'allowed_changes.json'


def tree(include_addons):
    files = {}
    for path in sorted(c.ROOT.rglob('*')):
        if not path.is_file():
            continue
        parts = path.relative_to(c.ROOT).parts
        if any(part in EXCLUDED_DIRS for part in parts):
            continue
        if not include_addons and parts[0] == 'v4_addons':
            continue
        files[path.relative_to(c.ROOT).as_posix()] = dict(size=path.stat().st_size, sha256=c.digest(path))
    return files


def baseline_path():
    candidates = sorted(c.SNAPSHOTS.glob('baseline_*.json'))
    if not candidates:
        raise SystemExit('no baseline snapshot; run --snapshot first')
    return candidates[0]


def snapshot():
    target = c.SNAPSHOTS / f'baseline_{c.today()}.json'
    if target.exists():
        raise SystemExit(f'{target} exists; refusing to overwrite the baseline')
    files = tree(include_addons=True)
    body = dict(created_utc=c.utc_now(), root=c.ROOT.as_posix(), excluded_dirs=list(EXCLUDED_DIRS),
                file_count=len(files), total_bytes=sum(item['size'] for item in files.values()), files=files)
    target.write_text(json.dumps(body, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    print(f'baseline written: {target.relative_to(c.ROOT).as_posix()} files={len(files)} bytes={body["total_bytes"]}')
    return target


def compare(card, phase):
    base = json.loads(baseline_path().read_text(encoding='utf-8'))
    baseline_files = {key: value for key, value in base['files'].items() if not key.startswith('v4_addons/')}
    current = tree(include_addons=False)
    allowed = json.loads(ALLOWED.read_text(encoding='utf-8')) if ALLOWED.exists() else {}
    added = sorted(set(current) - set(baseline_files))
    removed = sorted(set(baseline_files) - set(current))
    changed = sorted(key for key in set(current) & set(baseline_files) if current[key]['sha256'] != baseline_files[key]['sha256'])
    accepted, unexpected = [], []
    for key in changed:
        rule = allowed.get(key)
        if rule and rule.get('post_sha256') == current[key]['sha256'] and rule.get('pre_sha256') == baseline_files[key]['sha256']:
            accepted.append(key)
        else:
            unexpected.append(dict(path=key, kind='changed', baseline=baseline_files[key]['sha256'], current=current[key]['sha256']))
    for key in added:
        rule = allowed.get(key)
        if rule and rule.get('kind') == 'added' and rule.get('post_sha256') == current[key]['sha256']:
            accepted.append(key)
        else:
            unexpected.append(dict(path=key, kind='added', current=current[key]['sha256']))
    unexpected.extend(dict(path=key, kind='removed', baseline=baseline_files[key]['sha256']) for key in removed)
    gates = sorted(path.name for path in c.GATES.iterdir() if path.is_file()) if c.GATES.exists() else []
    record = dict(card=card, phase=phase, checked_utc=c.utc_now(), baseline=baseline_path().name,
                  files_checked=len(current), accepted_changes=accepted, unexpected=unexpected,
                  clean=not unexpected, gate_files_present=gates)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(record, sort_keys=True) + '\n')
    status = 'CLEAN' if record['clean'] else 'UNEXPECTED DIFF'
    print(f'boundary {card}/{phase}: {status}; files={len(current)}; accepted={len(accepted)}; unexpected={len(unexpected)}; gates={gates}')
    for item in unexpected:
        print('  !!', item)
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--snapshot', action='store_true')
    parser.add_argument('--card', default='adhoc')
    parser.add_argument('--phase', default='check')
    args = parser.parse_args()
    if args.snapshot:
        snapshot()
        return
    record = compare(args.card, args.phase)
    sys.exit(0 if record['clean'] else 1)


if __name__ == '__main__':
    main()
