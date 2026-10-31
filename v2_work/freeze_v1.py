from pathlib import Path
from hashlib import sha256
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / 'v1_frozen'
assert not FROZEN.exists(), 'Do not overwrite an existing immutable snapshot'
FROZEN.mkdir()
files = [ROOT / name for name in ['philopateer.pdf', 'philopateer.pptx', 'philopateer.ipynb', 'references.txt', 'analysis_pipeline.py', 'build_notebook.py', 'export_and_verify.py', 'FINAL_ASSESSMENT_HANDOFF.md', 'FINAL_ASSESSMENT_READING_NOTE.md', 'requirements-python311.txt']]
files += sorted(p for p in (ROOT / 'analysis_outputs').rglob('*') if p.is_file())
manifest = {}
for path in files:
    relative = path.relative_to(ROOT).as_posix()
    destination = FROZEN / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, destination)
    digest = sha256(path.read_bytes()).hexdigest()
    assert sha256(destination.read_bytes()).hexdigest() == digest
    manifest[relative] = {'sha256': digest, 'bytes': path.stat().st_size}
(FROZEN / 'sha256_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print('Frozen:', len(manifest), 'files;', sum(x['bytes'] for x in manifest.values()), 'bytes')
