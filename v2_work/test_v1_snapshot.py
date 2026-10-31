from pathlib import Path
from hashlib import sha256
import importlib.util
import json
import unittest

ROOT=Path(__file__).resolve().parents[1]


class SnapshotTests(unittest.TestCase):
    def test_all_required_artifacts_are_frozen(self):
        manifest=json.loads((ROOT/'v1_frozen/sha256_manifest.json').read_text())
        required=['philopateer.pdf','philopateer.pptx','philopateer.ipynb','references.txt','analysis_pipeline.py','build_notebook.py','export_and_verify.py']
        for name in required:
            self.assertIn(name,manifest)
        for relative, info in manifest.items():
            frozen=ROOT/'v1_frozen'/relative
            self.assertTrue(frozen.is_file(),relative)
            self.assertEqual(sha256(frozen.read_bytes()).hexdigest(),info['sha256'],relative)

    def test_original_notebook_cell_sources_match_frozen_pipeline(self):
        import re
        notebook=json.loads((ROOT/'v1_frozen/philopateer.ipynb').read_text(encoding='utf-8'))
        sources=[''.join(c['source']).strip() for c in notebook['cells'] if c['cell_type']=='code']
        pipeline=(ROOT/'v1_frozen/analysis_pipeline.py').read_text(encoding='utf-8')
        cells=re.split(r'^# %% (.+)\n',pipeline,flags=re.MULTILINE)[2::2]
        self.assertEqual(sources,[s.strip() for s in cells])


if __name__=='__main__':
    unittest.main()
