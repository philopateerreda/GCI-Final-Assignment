from pathlib import Path
import json
from hashlib import sha256

import numpy as np
import pandas as pd

from common import ROOT, WORK, dump
from final_protocol import verify
import workstream_a as a


def build():
    protocol = verify()
    frame = pd.read_csv(WORK / 'a_selected_test.csv')
    summary = json.loads((WORK / 'a_summary_test.json').read_text(encoding='utf-8'))
    v1 = json.loads((ROOT / 'v1_frozen/analysis_outputs/summary.json').read_text(encoding='utf-8'))
    d = json.loads((WORK / 'd_results/summary.json').read_text(encoding='utf-8'))
    gates = pd.read_csv(WORK / 'd_results/gate_d.csv')
    intervals = pd.read_csv(WORK / 'a_intervals_test.csv')
    policies = {row['policy']: row for row in summary['policies'] if row['prior'] == .02}
    bayes, risk = policies['bayes'], policies['risk']
    deployment_intervals = intervals.loc[intervals.regime.eq('deployment') & intervals.prior.eq(.02) & intervals.policy.eq('bayes')]
    sample_intervals = intervals.loc[intervals.regime.eq('sample') & intervals.policy.eq('sample_rv')]
    display = {'protocol_sha256': sha256((WORK / 'final_frozen_protocol.json').read_bytes()).hexdigest(),
               'v1': v1, 'protocol': protocol, 'd_summary': d,
               'd_gate_rows': gates.where(pd.notna(gates), None).to_dict(orient='records'),
               'deployment_policies': policies, 'a_spec': summary['spec'],
               'deployment_relative_value_gain': bayes['value_recall'] / risk['value_recall'] - 1,
               'deployment_net_gain': bayes['net'] - risk['net'],
               'deployment_intervals': {row.metric: {'lower': row.lower, 'upper': row.upper} for row in deployment_intervals.itertuples()},
               'sample_intervals': {row.metric: {'lower': row.lower, 'upper': row.upper} for row in sample_intervals.itertuples()},
               'deployment_retained_revenue': bayes['actual_value'] * .2 * 6,
               'deployment_prevented': bayes['actual_churners'] * .2,
               'pilot_calibration': json.loads((WORK / 'b_summary_calibration.json').read_text(encoding='utf-8')),
               'pilot_test': json.loads((WORK / 'b_summary_test.json').read_text(encoding='utf-8')),
               'governance_test': json.loads((WORK / 'c_test/c_summary.json').read_text(encoding='utf-8')),
               'heatmap': [], 'prior_stress': [],
               'sample_top10_v2': {name: a.sample_measure(frame, score)
                                  for name, score in a.scores(frame, prior=.4956).items()},
               'a_intervals': intervals.where(pd.notna(intervals), None).to_dict(orient='records')}
    display['sample_relative_value_gain_v2'] = display['sample_top10_v2']['sample_rv']['value_recall'] / display['sample_top10_v2']['risk']['value_recall'] - 1
    for prevention in (.1, .2, .3):
        for cost in (1., 2., 5.):
            row = a.measure(frame, frame.selected_bayes, cost=cost, success=prevention)
            display['heatmap'].append({'prevention': prevention, 'contact_cost': cost, **row})
    for prior in (.01, .02, .05):
        threshold = summary['spec']['thresholds'][str(prior)]['bayes']
        selected = a.scores(frame, prior)['bayes'] >= threshold
        display['prior_stress'].append({'prior': prior, 'threshold': threshold, **a.measure(frame, selected, prior=prior)})
    eligible = gates.loc[gates.eligible & ~gates.candidate.str.startswith('without_')]
    strongest = eligible.sort_values(['corrected_auc_lower', 'mean_auc_gain', 'candidate'], ascending=[False, False, True]).iloc[0]
    display['strongest_nonpromoted_or_promoted_cv_candidate'] = strongest.to_dict()
    if protocol['gate_d_passed']:
        display['selected_model_test'] = json.loads((WORK / 'd_final_test_comparison.json').read_text(encoding='utf-8'))
    else:
        display['selected_model_test'] = {'v1_reference_retained': True,
                                          'metrics': v1['selected_test_metrics'],
                                          'auc_95ci': v1['bootstrap_intervals']['auc']}
    proxy = pd.read_csv(WORK / 'c_proxy_cv.csv')
    display['proxy_recoverability'] = proxy.loc[proxy.scope.eq('pooled_oof')].where(pd.notna(proxy), None).to_dict(orient='records')
    display['source_sha256'] = {name: sha256((WORK / name).read_bytes()).hexdigest()
                               for name in ('a_selected_test.csv', 'a_summary_test.json', 'a_intervals_test.csv',
                                            'd_results/summary.json', 'd_results/gate_d.csv', 'c_proxy_cv.csv',
                                            'b_summary_calibration.json', 'b_summary_test.json', 'c_test/c_summary.json')}
    display['epistemic_boundary'] = 'Frozen retrospective metrics and assumed economics; no test-selected policy, measured treatment effect or claimed production baseline.'
    dump('final_metrics.json', display)
    return display


def publish_summary():
    build()
    final = json.loads((WORK / 'final_metrics.json').read_text(encoding='utf-8'))
    target = ROOT / 'analysis_outputs/summary.json'
    summary = json.loads(target.read_text(encoding='utf-8'))
    summary['v2_enhancement'] = {key: value for key, value in final.items() if key != 'v1'}
    summary['v2_enhancement']['final_metrics_sha256'] = sha256((WORK / 'final_metrics.json').read_bytes()).hexdigest()
    target.write_text(json.dumps(summary, indent=2, allow_nan=False), encoding='utf-8')
    return summary['v2_enhancement']


if __name__ == '__main__':
    result = build()
    print(json.dumps({'model': result['protocol']['model_candidate'],
                      'deployment_value_gain': result['deployment_relative_value_gain'],
                      'deployment_net': result['deployment_policies']['bayes']['net']}, indent=2))
