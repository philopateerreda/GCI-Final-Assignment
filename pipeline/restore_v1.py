from pathlib import Path
from hashlib import sha256
import argparse
import json
import os
import shutil
import tempfile

ROOT = Path(__file__).resolve().parent
FROZEN = ROOT / 'v1_frozen'


def verify():
    manifest = json.loads((FROZEN / 'sha256_manifest.json').read_text(encoding='utf-8'))
    for relative, info in manifest.items():
        path = FROZEN / relative
        assert path.stat().st_size == info['bytes']
        assert sha256(path.read_bytes()).hexdigest() == info['sha256'], relative
    return manifest


def restore(target):
    manifest = verify()
    with tempfile.TemporaryDirectory(prefix='v1-restore-', dir=target.parent) as staging:
        staging = Path(staging)
        applied, absent = [], []
        for relative in manifest:
            staged = staging / 'incoming' / relative
            staged.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(FROZEN / relative, staged)
            destination = target / relative
            if destination.exists():
                prior = staging / 'prior' / relative
                prior.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(destination, prior)
            else:
                absent.append(relative)
        try:
            for relative in manifest:
                destination = target / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                os.replace(staging / 'incoming' / relative, destination)
                applied.append(relative)
        except Exception:
            for relative in reversed(applied):
                destination = target / relative
                if relative in absent:
                    destination.unlink()
                else:
                    os.replace(staging / 'prior' / relative, destination)
            raise
    for relative, info in manifest.items():
        assert sha256((target / relative).read_bytes()).hexdigest() == info['sha256'], relative
    return len(manifest)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify-only', action='store_true')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    manifest = verify()
    if args.self_test:
        from unittest.mock import patch
        with tempfile.TemporaryDirectory(prefix='restore-self-test-', dir=ROOT / 'v2_work') as temporary:
            target = Path(temporary) / 'target'
            target.mkdir()
            altered = b'intentionally altered sandbox copy'
            (target / 'philopateer.pdf').write_bytes(altered)
            real_replace, calls = os.replace, [0]
            def fail_once(source, destination):
                calls[0] += 1
                if calls[0] == 4:
                    raise OSError('Injected sandbox replacement failure')
                return real_replace(source, destination)
            with patch('os.replace', side_effect=fail_once):
                try:
                    restore(target)
                except OSError:
                    pass
                else:
                    raise AssertionError('Injected failure did not occur')
            assert (target / 'philopateer.pdf').read_bytes() == altered
            assert [p.relative_to(target).as_posix() for p in target.rglob('*') if p.is_file()] == ['philopateer.pdf']
            count = restore(target)
            assert len(list(target.rglob('*'))) >= count
        print('Sandbox rollback and injected-failure recovery passed:', count, 'byte-identical files')
    elif args.verify_only:
        print('Immutable v1 verified:', len(manifest), 'files')
    else:
        print('Restored v1 byte-for-byte:', restore(ROOT), 'files; unrelated files retained')
