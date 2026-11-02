from pathlib import Path
import argparse
from hashlib import sha256
import json
import re
import shutil

from common import ROOT, WORK

MODULES = ('common', 'workstream_a', 'workstream_b', 'workstream_c', 'workstream_d',
           'a_budget_gate', 'headroom_refit', 'final_protocol', 'run_frozen_batch',
           'final_metrics', 'generate_visuals')

BOOTSTRAP = '''import importlib
import sys
from pathlib import Path
from hashlib import sha256
import shutil
import json

V2_ROOT = Path.cwd().resolve()
V2_WORK = V2_ROOT / 'v2_work'
V2_WORK.mkdir(exist_ok=True)
if str(V2_WORK) not in sys.path:
    sys.path.insert(0, str(V2_WORK))

def _v2_materialize(name, source):
    path = V2_WORK / (name + '.py')
    if path.exists():
        assert path.read_text(encoding='utf-8') == source, f'Embedded module differs from local file: {name}'
    else:
        path.write_text(source, encoding='utf-8', newline='')
    return path
'''

TEXT = {
    'V2 reproduction contract': '''## 10. Frozen enhancement protocol and self-contained reproduction
The nine original analysis code cells are preserved unchanged. They replay the already-evaluated v1 reference, not a new selection search on its test split. The following cells embed every enhancement module. Existing completed outputs are accepted only after source/output fingerprint verification; an absent analysis is reproduced locally in the prescribed A → B → C → D order.

**Four boundaries:** risk is not value; risk is not responsiveness; retrospective capture is not saved revenue; the approximately 49.56% supplied sample is not a 2% deployment population. The original test was evaluated for v1. Enhancement decisions use non-test rows, are frozen before one descriptive final batch, and are not confirmatory external validation.

The supplied dictionary does not specify the `_Mean` window and the CSVs have no `_Range` fields. Three-/six-month features use only verified `avg3`/`avg6` definitions. The unavailable volatility group is reported rather than reconstructed. No failed challenger proves an information ceiling.''',
    'V2 baseline replay assets': '''## 11. Preserve the original baseline evidence
A full existing immutable snapshot is never overwritten. On a fresh notebook reproduction only, essential baseline analysis assets are copied from the preceding original cells; this minimal replay cache is explicitly not a restorable submission snapshot. Keep the original supplied files alongside the notebook.''',
    'V2 non-test workstreams': '''## 12. A–D: non-test decisions first
A compares five parameter-free policies, three clipped calibrators, all declared budgets/costs, paired uncertainty, and four value proxies. B pre-registers disjoint pilot enrollment, two-stage costs, outcome simulations and exclusive routing. C audits excluded-attribute recoverability using fixed original-75k five-fold CV and descriptive subgroup/equity intervals. D uses two repeats of five-fold CV on exactly the original 75k, fold-local preprocessing and nested feature/blend selection.

D reports dependence-corrected paired intervals: `SE = sqrt((1/10 + test/train) × variance)`, with conservative four degrees of freedom. These are exploratory pointwise intervals, not multiplicity- or model-selection-adjusted guarantees. AUC gain must be at least 0.001 with a positive lower bound and nondegrading weighted top-tail calibration. Sensitive `asl_flag`/`area` ceilings cannot be deployed. Higher AUC without passing the calibration gate is rejected.''',
    'V2 final frozen evaluation': '''## 13. One frozen descriptive final batch
The model, calibrator, policy cutoffs, headline budget, pilot design and routing criteria are fingerprinted before final evaluation. Existing verified final results are replayed without rescoring. Prior shift assumes stable class-conditional distributions; deployment weights are scenario weights, not estimated real population counts. Costs and benefits are both weighted consistently.

Power for contribution and simulated covariate adjustment are cross-sectional planning proxies, not observed treatment effects or validated CUPED savings. Re-estimate using linked accounts and real pre-period billing logs before launch.''',
    'V2 results and governance': '''## 14. Evidence register and operational boundaries
The tables below retain both prior regimes, exact overlap/queue counts, failed calibrators and budget/model gates, corrected CV uncertainty, subgroup small-n flags, and simulated power assumptions. The calibration-selected budget dots are not test-selected profit optima.

**Service-Fix Floor:** remediate every verified billing/network defect regardless of plan price or discretionary-list selection. Value-aware ranking rations only scarce proactive discretionary outreach. Excluding demographic fields reduces direct reliance but does not guarantee statistical independence. This proposal is **audited**, not declared fair. Income is an ordinal 1–9 source code, not currency. No causal uplift, production churn prevalence or AI-chat URL is fabricated.'''
}


def embedded_cell(name):
    source = (WORK / f'{name}.py').read_text(encoding='utf-8')
    lines = ',\n'.join('    ' + repr(line) for line in source.splitlines(keepends=True))
    return f"_v2_materialize({name!r}, ''.join([\n{lines}\n]))\n"


def assemble():
    original = (ROOT / 'v1_frozen/analysis_pipeline.py').read_text(encoding='utf-8')
    additions = [('V2 reproduction contract', BOOTSTRAP)]
    additions.extend((f'V2 module {name}', embedded_cell(name)) for name in MODULES)
    essentials = ('analysis_outputs/summary.json', 'analysis_outputs/model_selection.json',
                  'analysis_outputs/feature_manifest.json', 'analysis_outputs/source_manifest.json',
                  'analysis_outputs/models/selected_model.joblib',
                  'analysis_outputs/tables/split_manifest.csv',
                  'analysis_outputs/tables/heldout_predictions.csv')
    baseline_cell = f'''_v2_baseline = V2_ROOT / 'v1_frozen'
if not _v2_baseline.exists():
    _v2_baseline.mkdir()
    (_v2_baseline / 'analysis_pipeline.py').write_text({original!r}, encoding='utf-8', newline='')
    for _relative in {essentials!r}:
        _destination = _v2_baseline / _relative
        _destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(V2_ROOT / _relative, _destination)
    (_v2_baseline / 'notebook_replay_baseline.json').write_text(json.dumps({{'purpose': 'minimal analytical replay cache; NOT a restorable v1 submission snapshot', 'v1_test_previously_evaluated': True}}, indent=2), encoding='utf-8')
assert (_v2_baseline / 'analysis_pipeline.py').read_text(encoding='utf-8') == {original!r}
import run_frozen_batch as v2_run
'''
    results_cell = '''v2_run.show_results()
import final_metrics
import runpy
final_metrics.publish_summary()
runpy.run_path(str(V2_WORK / 'generate_visuals.py'), run_name='__main__')
for _v2_chart in ('risk_value_tradeoff.png', 'value_capture_curve.png', 'scenario_waterfall.png'):
    shutil.copy2(V2_WORK / 'charts' / _v2_chart, V2_ROOT / 'analysis_outputs/charts' / _v2_chart)
'''
    additions.extend([
        ('V2 baseline replay assets', baseline_cell),
        ('V2 non-test workstreams', 'v2_run.non_test()\n'),
        ('V2 final frozen evaluation', 'v2_run.final_test()\n'),
        ('V2 results and governance', results_cell)])
    pipeline = original.rstrip() + '\n\n' + '\n\n'.join(f'# %% {title}\n{code.rstrip()}' for title, code in additions) + '\n'
    old_chunks = re.split(r'^# %% (.+)\n', original, flags=re.MULTILINE)[2::2]
    new_chunks = re.split(r'^# %% (.+)\n', pipeline, flags=re.MULTILINE)[2::2]
    assert [c.strip() for c in new_chunks[:9]] == [c.strip() for c in old_chunks]
    assert len(old_chunks) == 9
    texts = dict(TEXT)
    for name in MODULES:
        texts[f'V2 module {name}'] = f'### Embedded module: {name}\nSource is materialized byte-for-byte for auditable cache hashes. This cell does not run experiments.'
    builder = (ROOT / 'v1_frozen/build_notebook.py').read_text(encoding='utf-8')
    insertion = '\nTEXT.update(' + repr(texts) + ')\n'
    builder = builder.replace('\n\ndef build():', insertion + '\n\ndef build():')
    builder = builder.replace('timeout=2400, record_timing=True', 'timeout=86400, record_timing=True')
    (WORK / 'analysis_pipeline_v2.py').write_text(pipeline, encoding='utf-8', newline='')
    (WORK / 'build_notebook_v2.py').write_text(builder, encoding='utf-8', newline='')
    report = {'original_code_cells_preserved': 9, 'v2_code_cells': len(new_chunks),
              'pipeline_sha256': sha256(pipeline.encode()).hexdigest(),
              'builder_sha256': sha256(builder.encode()).hexdigest(),
              'embedded_modules': list(MODULES), 'root_modified': False}
    (WORK / 'canonical_build_spec.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return report


def promote():
    assert (WORK / 'checkpoint2_summary.md').exists(), 'Checkpoint 2 must precede root promotion.'
    import run_frozen_batch
    run_frozen_batch.verify_completed()
    report = assemble()
    shutil.copy2(WORK / 'analysis_pipeline_v2.py', ROOT / 'analysis_pipeline.py')
    shutil.copy2(WORK / 'build_notebook_v2.py', ROOT / 'build_notebook.py')
    shutil.copy2(WORK / 'references_v2.txt', ROOT / 'references.txt')
    shutil.copy2(WORK / 'export_and_verify_v2.py', ROOT / 'export_and_verify.py')
    report['root_modified'] = True
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--promote', action='store_true')
    args = parser.parse_args()
    print(json.dumps(promote() if args.promote else assemble(), indent=2))
