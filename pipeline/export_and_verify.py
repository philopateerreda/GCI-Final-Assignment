from pathlib import Path
from hashlib import sha256
import json
import re
import sys

import pymupdf as fitz
import nbformat
from PIL import Image, ImageDraw, ImageOps
from pptx import Presentation
import win32com.client

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'analysis_outputs'
WORK = ROOT / 'v2_work'
PPTX = ROOT / 'philopateer.pptx'
PDF = ROOT / 'philopateer.pdf'
RENDER = OUT / 'slide_renders'
sys.path.insert(0, str(WORK))
from claim_checks import verify_claims
from run_frozen_batch import verify_completed

protocol = verify_completed()
claims = verify_claims(ROOT)
assert (WORK / 'checkpoint2_summary.md').exists()
geometry = json.loads((WORK / 'office_geometry_check.json').read_text(encoding='utf-8'))
assert geometry['issue_count'] == 0 and geometry['slide_count'] == 15
assert geometry['pptx_sha256'] == sha256(PPTX.read_bytes()).hexdigest()

nb = nbformat.read(ROOT / 'philopateer.ipynb', as_version=4)
nbformat.validate(nb)
code_cells = [c for c in nb.cells if c.cell_type == 'code']
assert all(c.execution_count is not None for c in code_cells)
assert not [o for c in code_cells for o in c.get('outputs', []) if o.output_type == 'error']
pipeline = (ROOT / 'analysis_pipeline.py').read_text(encoding='utf-8')
chunks = re.split(r'^# %% (.+)\n', pipeline, flags=re.MULTILINE)[2::2]
assert [c.source.strip() for c in code_cells] == [s.strip() for s in chunks]
original = (ROOT / 'v1_frozen/analysis_pipeline.py').read_text(encoding='utf-8')
original_chunks = re.split(r'^# %% (.+)\n', original, flags=re.MULTILINE)[2::2]
assert len(original_chunks) == 9
assert [c.source.strip() for c in code_cells[:9]] == [s.strip() for s in original_chunks]

summary = json.loads((OUT / 'summary.json').read_text(encoding='utf-8'))
final = json.loads((WORK / 'final_metrics.json').read_text(encoding='utf-8'))
assert summary['v2_enhancement']['protocol_sha256'] == final['protocol_sha256']
assert summary['v2_enhancement']['deployment_policies'] == final['deployment_policies']
manifest = json.loads((OUT / 'source_manifest.json').read_text(encoding='utf-8'))
assert len(manifest) == 5
for relative, info in manifest.items():
    assert sha256((ROOT / relative).read_bytes()).hexdigest() == info['sha256'], relative
pred_hash = sha256((OUT / 'tables/heldout_predictions.csv').read_bytes()).hexdigest()
assert pred_hash == (OUT / 'first_prediction_digest.txt').read_text().strip()
assert pred_hash == sha256((ROOT / 'v1_frozen/analysis_outputs/tables/heldout_predictions.csv').read_bytes()).hexdigest()

prs = Presentation(PPTX)
assert len(prs.slides) == 15
shape_bounds = []
for i, slide in enumerate(prs.slides, 1):
    for shape in slide.shapes:
        if shape.left < -12700 or shape.top < -12700 or shape.left + shape.width > prs.slide_width + 12700 or shape.top + shape.height > prs.slide_height + 12700:
            shape_bounds.append({'slide': i, 'shape': shape.name})
assert not shape_bounds, shape_bounds

RENDER.mkdir(parents=True, exist_ok=True)
before_hash = sha256(PPTX.read_bytes()).hexdigest()
app = win32com.client.DispatchEx('PowerPoint.Application')
existing = app.Presentations.Count
presentation = None
try:
    presentation = app.Presentations.Open(str(PPTX), ReadOnly=True, Untitled=False, WithWindow=False)
    assert presentation.Slides.Count == 15
    presentation.SaveAs(str(PDF), 32)
    presentation.Export(str(RENDER), 'PNG', 1600, 900)
finally:
    if presentation is not None:
        presentation.Close()
    if existing == 0 and app.Presentations.Count == 0:
        app.Quit()
assert sha256(PPTX.read_bytes()).hexdigest() == before_hash

pdf = fitz.open(PDF)
assert len(pdf) == 15
assert PDF.stat().st_size <= 10_000_000
text = '\n'.join(p.get_text() for p in pdf)
for required in ('philopateer', 'LightGBM', '0.6978', 'References', 'Service-Fix Floor'):
    assert required in text, required
assert 'placeholder' not in text.lower()
assert f"+{summary['value_capture_relative_gain_over_risk']:.1%}" in text
assert f"{summary['ranking_top10']['Risk only']['recurring_value_recall']:.1%}" in text
assert f"{summary['ranking_top10']['Risk × recurring value']['recurring_value_recall']:.1%}" in text
assert f"{summary['selected_test_metrics']['roc_auc']:.4f}" in pdf[7].get_text()
assert f"{summary['selected_test_metrics']['accuracy']:.2%}" in pdf[7].get_text()
bayes = final['deployment_policies']['bayes']
assert f"{final['deployment_relative_value_gain']:+.1%}" in pdf[8].get_text()
for name in ('risk', 'bayes'):
    assert f"{final['deployment_policies'][name]['value_recall']:.1%}" in pdf[8].get_text()
assert f"${bayes['net'] / 1000:.1f}k" in pdf[10].get_text()
assert f"${bayes['break_even_contact_cost']:.2f}" in pdf[11].get_text()
assert f"{bayes['break_even_success']:.1%}" in pdf[11].get_text()
pilot = json.loads((WORK / 'b_design.json').read_text(encoding='utf-8'))
assert f"{pilot['allocation']['core_per_arm']:,}" in pdf[12].get_text()
assert f"${pilot['stage1_cost']:,.0f}" in pdf[12].get_text()
assert f"${pilot['stage2_incremental_cost']:,.0f}" in pdf[12].get_text()

thumb_w, thumb_h = 480, 286
contact = Image.new('RGB', (thumb_w * 3, thumb_h * 5), '#E7EBED')
draw = ImageDraw.Draw(contact)
render_hashes = {}
for i, page in enumerate(pdf):
    png = RENDER / f'Slide{i + 1}.PNG'
    with Image.open(png) as exported:
        assert exported.size == (1600, 900), png
    render_hashes[str(png.relative_to(ROOT)).replace('\\', '/')] = sha256(png.read_bytes()).hexdigest()
    pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    im = ImageOps.contain(im, (thumb_w - 12, thumb_h - 24))
    x, y = (i % 3) * thumb_w, (i // 3) * thumb_h
    draw.text((x + 8, y + 4), f'Slide {i + 1}', fill='#132D3A')
    contact.paste(im, (x + 6, y + 22))
contact.save(OUT / 'deck_contact_sheet.png')
(OUT / 'presentation_text.txt').write_text(text, encoding='utf-8')
report = {'pdf_pages': len(pdf), 'pdf_bytes': PDF.stat().st_size, 'pptx_slides': len(prs.slides),
          'pptx_bytes': PPTX.stat().st_size, 'executed_notebook_code_cells': len(code_cells),
          'notebook_errors': 0, 'notebook_matches_pipeline': True, 'original_nine_code_cells_preserved': True,
          'slide_headlines_match_analysis': True, 'source_files_unchanged': True,
          'deterministic_v1_prediction_sha256': pred_hash, 'powerpoint_export': 'successful',
          'out_of_bounds_shapes': shape_bounds, 'protocol_sha256': final['protocol_sha256'],
          'gate_d_passed': protocol['gate_d_passed'], 'claims_check': claims,
          'office_geometry_issue_count': geometry['issue_count'],
          'office_geometry_check_sha256': sha256((WORK / 'office_geometry_check.json').read_bytes()).hexdigest(),
          'render_sha256': render_hashes,
          'delivery_sha256': {name: sha256((ROOT / name).read_bytes()).hexdigest()
                              for name in ('philopateer.pdf', 'philopateer.pptx', 'philopateer.ipynb', 'references.txt')},
          'visual_review': 'Pending full-size review of all fifteen rendered slides and contact sheet.',
          'submission_note': 'Not submitted. No AI conversation URL was supplied or fabricated.'}
(OUT / 'delivery_checks.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
