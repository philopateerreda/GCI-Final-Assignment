from hashlib import sha256
import json
from pathlib import Path
from datetime import datetime, timezone

from common import ROOT, WORK, SEED, THREADS


FILES = ('a_spec.json', 'a_calibrator.joblib', 'a_selected_calibration.csv',
         'c_proxy_cv.csv', 'd_results/selected_model_recipe.json',
         'd_results/gate_d.json', 'd_results/run_spec.json',
         'common.py', 'workstream_a.py', 'workstream_b.py', 'workstream_c.py',
         'workstream_d.py', 'a_budget_gate.py', 'headroom_refit.py',
         'final_protocol.py', 'run_frozen_batch.py', 'final_metrics.py', 'generate_visuals.py')
BASELINE_FILES = ('v1_frozen/analysis_pipeline.py',
                  'v1_frozen/analysis_outputs/models/selected_model.joblib',
                  'v1_frozen/analysis_outputs/tables/split_manifest.csv',
                  'v1_frozen/analysis_outputs/tables/heldout_predictions.csv',
                  'v1_frozen/analysis_outputs/source_manifest.json')


def freeze():
    target = WORK / 'final_frozen_protocol.json'
    if target.exists():
        verify()
        return json.loads(target.read_text(encoding='utf-8'))
    d_summary = json.loads((WORK / 'd_results/summary.json').read_text(encoding='utf-8'))
    assert d_summary['status'] == 'complete' and d_summary['decision_allowed']
    assert d_summary['original_test_rows_used'] == 0
    assert d_summary['original_calibration_policy_rows_used'] == 0
    assert not (WORK / 'a_selected_test.csv').exists(), 'Freeze must precede final test evaluation.'
    spec = json.loads((WORK / 'a_spec.json').read_text(encoding='utf-8'))
    assert not spec['test_used_for_selection']
    assert spec['promoted_headline_fraction'] == .1
    paths = list(FILES)
    if d_summary['gate_d_passed']:
        paths.extend(['d_promoted_model.joblib', 'd_promoted_refit.json'])
    paths.extend(p.name for p in WORK.glob('b*spec*.json'))
    paths.extend(p.name for p in WORK.glob('b*design*.json'))
    assert any(name.startswith('b') for name in paths), 'Pilot design must be frozen before test.'
    originals = json.loads((ROOT / 'v1_frozen/analysis_outputs/source_manifest.json').read_text(encoding='utf-8'))
    protected_hashes = {relative.replace('\\', '/'): info['sha256'] for relative, info in originals.items()}
    assert len(protected_hashes) == 5
    for relative, digest in protected_hashes.items():
        assert sha256((ROOT / relative).read_bytes()).hexdigest() == digest, relative
    baseline_hashes = {name: sha256((ROOT / name).read_bytes()).hexdigest() for name in BASELINE_FILES}
    record = {'seed': SEED, 'threads': THREADS,
              'frozen_utc': datetime.now(timezone.utc).isoformat(),
              'v1_test_previously_evaluated': True, 'test_selected_decisions': False,
              'model_candidate': d_summary['selected_candidate'],
              'gate_d_passed': d_summary['gate_d_passed'],
              'calibrator': spec['calibrator'], 'headline_fraction': .1,
              'hashes': {name: sha256((WORK / name).read_bytes()).hexdigest() for name in sorted(set(paths))},
              'baseline_hashes': baseline_hashes, 'protected_original_hashes': protected_hashes,
              'final_test_rule': 'One frozen descriptive batch; no model, calibrator, budget, routing or pilot selection on final test. Canonical notebook replay may reuse verified results without a second decision search.',
              'service_fix_floor': 'Remediate every verified billing/network defect irrespective of bill size or discretionary selection.',
              'financial_assumptions': {'population': 100000, 'prior': .02, 'prevention': .2,
                                       'retained_months': 6, 'margin': .6, 'contact_cost': 1., 'fixed_cost': 5000.}}
    target.write_text(json.dumps(record, indent=2), encoding='utf-8')
    return record


def verify():
    record = json.loads((WORK / 'final_frozen_protocol.json').read_text(encoding='utf-8'))
    for name, digest in record['hashes'].items():
        assert sha256((WORK / name).read_bytes()).hexdigest() == digest, name
    for name, digest in {**record['baseline_hashes'], **record['protected_original_hashes']}.items():
        assert sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    return record


def begin_test(promoted):
    record = verify()
    assert record['gate_d_passed'] == promoted, 'Use the frozen model route.'
    assert not (WORK / 'a_selected_test.csv').exists(), 'Do not rescore a completed final test.'
    with (WORK / 'final_test_started.json').open('x', encoding='utf-8') as handle:
        json.dump({'protocol_sha256': sha256((WORK / 'final_frozen_protocol.json').read_bytes()).hexdigest(),
                   'model_route': 'promoted' if promoted else 'v1_cached',
                   'started_utc': datetime.now(timezone.utc).isoformat()}, handle, indent=2)
    return record


if __name__ == '__main__':
    print(json.dumps(freeze(), indent=2))
