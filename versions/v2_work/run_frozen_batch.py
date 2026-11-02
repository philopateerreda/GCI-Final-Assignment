from pathlib import Path
from hashlib import sha256
import json
import runpy

import pandas as pd

from common import ROOT, WORK, dump
import workstream_a as a
import workstream_b as b
import workstream_c as c
import workstream_d as d
from final_protocol import freeze, verify

SOURCES = ('common.py', 'workstream_a.py', 'workstream_b.py', 'workstream_c.py', 'workstream_d.py',
           'a_budget_gate.py', 'headroom_refit.py', 'final_protocol.py', 'run_frozen_batch.py',
           'final_metrics.py', 'generate_visuals.py')


def fingerprints(paths):
    return {str(path.relative_to(ROOT)).replace('\\', '/'): sha256(path.read_bytes()).hexdigest()
            for path in sorted(set(paths))}


def check_fingerprints(record):
    for relative, digest in record.items():
        assert sha256((ROOT / relative).read_bytes()).hexdigest() == digest, relative


def refresh_a_spec():
    spec = json.loads((WORK / 'a_spec.json').read_text(encoding='utf-8'))
    summary = json.loads((WORK / 'a_summary_calibration.json').read_text(encoding='utf-8'))
    summary['spec'] = spec
    dump('a_summary_calibration.json', summary)
    if not (WORK / 'a_summary_test.json').exists():
        dump('a_summary.json', summary)


def verify_non_test():
    record = json.loads((WORK / 'non_test_completion.json').read_text(encoding='utf-8'))
    check_fingerprints(record['source_hashes'])
    check_fingerprints(record['artifact_hashes'])
    assert record['test_used_for_selection'] is False
    return record


def non_test():
    if (WORK / 'non_test_completion.json').exists():
        record = verify_non_test()
        print('Verified completed non-test decisions; no new fits or selection search.')
        return record
    assert not (WORK / 'final_test_started.json').exists()
    if not (WORK / 'a_spec.json').exists():
        a.prepare()
    if not (WORK / 'a_budget_gate.csv').exists():
        runpy.run_path(str(WORK / 'a_budget_gate.py'), run_name='__main__')
    refresh_a_spec()
    if not (WORK / 'b_summary_calibration.json').exists():
        b.main(['--partition', 'calibration'])
    if not (WORK / 'c_calibration/c_summary.json').exists():
        c.main(['--partition', 'calibration', '--proxy-cv'])
    if not (WORK / 'd_results/summary.json').exists():
        d.main(['--run'])
    result = json.loads((WORK / 'd_results/summary.json').read_text(encoding='utf-8'))
    assert result['status'] == 'complete' and result['decision_allowed']
    assert result['original_test_rows_used'] == result['original_calibration_policy_rows_used'] == 0
    ceiling = str(WORK / 'd_results/diagnostic_ceiling_summary.csv')
    if result['gate_d_passed']:
        import headroom_refit
        if not (WORK / 'd_promoted_model.joblib').exists():
            headroom_refit.prepare()
        a.frozen_predictions = headroom_refit.calibration_predictions
        a.prepare()
        runpy.run_path(str(WORK / 'a_budget_gate.py'), run_name='__main__')
        refresh_a_spec()
        b.main(['--partition', 'calibration'])
        c.main(['--partition', 'calibration', '--proxy-cv', '--ceiling-results', ceiling])
    else:
        c.main(['--partition', 'calibration', '--bridge-only', '--ceiling-results', ceiling])
    sources = [WORK / name for name in SOURCES]
    sources.extend(ROOT / 'telecom' / name for name in ('Client.csv', 'Record.csv'))
    sources.extend(ROOT / 'v1_frozen' / name for name in ('analysis_pipeline.py', 'analysis_outputs/models/selected_model.joblib', 'analysis_outputs/tables/split_manifest.csv', 'analysis_outputs/tables/heldout_predictions.csv'))
    artifacts = [WORK / name for name in ('a_spec.json', 'a_calibrator.joblib', 'a_selected_calibration.csv',
                 'a_summary_calibration.json', 'a_budget_gate.csv', 'b_design.json', 'b_summary_calibration.json',
                 'b_power_calibration.csv', 'b_queues_calibration.csv', 'c_proxy_cv.csv',
                 'c_calibration/c_summary.json', 'c_calibration/c_subgroup_robustness.csv',
                 'c_calibration/c_equity.csv', 'd_results/summary.json', 'd_results/run_spec.json',
                 'd_results/selected_model_recipe.json', 'd_results/gate_d.csv',
                 'd_results/paired_corrected_intervals.csv', 'd_results/ablation_summary.csv',
                 'd_results/feature_group_decisions.csv')]
    if result['gate_d_passed']:
        artifacts.extend([WORK / 'd_promoted_model.joblib', WORK / 'd_promoted_refit.json'])
    record = {'test_used_for_selection': False, 'model': result['selected_candidate'],
              'gate_d_passed': result['gate_d_passed'], 'source_hashes': fingerprints(sources),
              'artifact_hashes': fingerprints(artifacts),
              'stage_order': 'A calibration → B calibration → C original75k proxy audit → D repeated75k CV → conditional final-model calibration refresh → freeze'}
    dump('non_test_completion.json', record)
    return record


def verify_completed():
    verify_non_test()
    protocol = verify()
    record = json.loads((WORK / 'final_batch_completion.json').read_text(encoding='utf-8'))
    assert record['protocol_sha256'] == sha256((WORK / 'final_frozen_protocol.json').read_bytes()).hexdigest()
    check_fingerprints(record['artifact_hashes'])
    assert record['new_test_decisions'] is False
    return protocol


def final_test():
    if (WORK / 'final_batch_completion.json').exists():
        protocol = verify_completed()
        print('Verified frozen final results; no test rescoring or decision search.')
        return protocol
    non_test()
    protocol = freeze()
    if not (WORK / 'final_test_started.json').exists():
        if protocol['gate_d_passed']:
            import headroom_refit
            headroom_refit.evaluate_test()
        else:
            a.evaluate_test()
    else:
        started = json.loads((WORK / 'final_test_started.json').read_text(encoding='utf-8'))
        assert started['protocol_sha256'] == sha256((WORK / 'final_frozen_protocol.json').read_bytes()).hexdigest()
        assert (WORK / 'a_selected_test.csv').exists(), 'A prior test attempt stopped before cached predictions. Investigate; never blindly rescore.'
        if not (WORK / 'a_summary_test.json').exists():
            from common import load_data
            data, splits = load_data()
            a.analyze(pd.read_csv(WORK / 'a_selected_calibration.csv'), pd.read_csv(WORK / 'a_selected_test.csv'), data, splits, 'test')
        if protocol['gate_d_passed'] and not all((WORK / name).exists() for name in ('d_final_test_comparison.json', 'd_final_test_bootstrap.csv')):
            import headroom_refit
            headroom_refit.paired_test_comparison(pd.read_csv(WORK / 'a_selected_test.csv'))
    if not (WORK / 'b_summary_test.json').exists():
        b.main(['--partition', 'test'])
    if not (WORK / 'c_test/c_summary.json').exists():
        c.main(['--partition', 'test', '--ceiling-results', str(WORK / 'd_results/diagnostic_ceiling_summary.csv')])
    artifacts = [WORK / name for name in ('a_selected_test.csv', 'a_summary_test.json', 'a_policies_test.csv',
                 'a_profit_curves_test.csv', 'a_overlap_test.csv', 'a_dual_valuation_test.csv',
                 'a_value_proxy_sensitivity_test.csv', 'a_intervals_test.csv',
                 'a_calibration_uncertainty_test.csv', 'b_summary_test.json', 'b_power_test.csv',
                 'b_queues_test.csv', 'b_cells_test.csv', 'b_assignments_test.csv',
                 'c_test/c_summary.json', 'c_test/c_subgroup_robustness.csv', 'c_test/c_equity.csv')]
    if protocol['gate_d_passed']:
        artifacts.extend([WORK / 'd_final_test_comparison.json', WORK / 'd_final_test_bootstrap.csv'])
    dump('final_batch_completion.json', {'protocol_sha256': sha256((WORK / 'final_frozen_protocol.json').read_bytes()).hexdigest(),
         'artifact_hashes': fingerprints(artifacts), 'v1_test_previously_evaluated': True,
         'new_test_decisions': False, 'completed_one_frozen_descriptive_batch': True})
    return protocol


def show_results():
    verify_completed()
    names = ('a_calibration_cv.csv', 'a_budget_gate.csv', 'a_policies_test.csv', 'a_overlap_test.csv',
             'a_intervals_test.csv', 'a_value_proxy_sensitivity_test.csv', 'b_power_test.csv',
             'b_queues_test.csv', 'b_cells_test.csv', 'c_proxy_cv.csv',
             'd_results/feature_group_decisions.csv', 'd_results/gate_d.csv')
    for name in names:
        print('\n' + name)
        print(pd.read_csv(WORK / name).to_string(index=False))
    for name in ('d_results/paired_corrected_intervals.csv', 'd_results/ablation_summary.csv',
                 'd_results/diagnostic_ceiling_summary.csv'):
        frame = pd.read_csv(WORK / name)
        print('\n' + name + ' — AUC intervals; all other metrics retained in the file')
        print(frame.loc[frame.metric.eq('auc')].to_string(index=False))
    learning = pd.read_csv(WORK / 'd_results/learning_curve_summary.csv')
    print('\nLearning curve (75k row is explicitly training-only):')
    print(learning.to_string(index=False))
    print('\nSubgroup/equity audit tables: c_test/c_subgroup_robustness.csv and c_test/c_equity.csv; descriptive paired intervals and small-n suppression retained.')
    print('Mandatory Service-Fix Floor; no measured uplift, production prevalence, validated CUPED gain or guaranteed profit.')


if __name__ == '__main__':
    non_test()
    final_test()
    show_results()
