from pathlib import Path
from hashlib import sha256
import json
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'v2_work'
summary = json.loads((ROOT / 'analysis_outputs/summary.json').read_text(encoding='utf-8'))
pred = pd.read_csv(ROOT / 'analysis_outputs/tables/heldout_predictions.csv')
y = pred.actual_churn.to_numpy()
p = pred.sample_calibrated_churn_probability.to_numpy()
v = pred.recurring_value_proxy.to_numpy()
base = next(r for r in summary['base_business_scenario'] if r['policy'] == 'Value-aware')
checks = {'auc': (roc_auc_score(y, p), 0.6978109022411016), 'contacts': (base['contacts'], 9984.921534106341), 'churners': (base['forecast_churners_contacted'], 476.3954270342972), 'prevented': (base['prevented_churn_scenario'], 95.27908540685945), 'retained_revenue': (base['retained_revenue_scenario'], 31220.006649619372), 'net': (base['net_contribution_scenario'], 3747.0824556652824), 'break_even_cost': ((base['gross_contribution_scenario'] - 5000) / base['contacts'], 1.3752741013403116), 'break_even_prevention': (base['break_even_success_rate'], 0.15999272199908424), 'pilot_per_arm': (summary['pilot']['per_arm_with_10pct_allowance'], 7872)}
for label, (actual, expected) in checks.items():
    assert np.isclose(actual, expected, rtol=1e-6, atol=1e-6), (label, actual, expected)
for name, expected_capture, expected_precision in [('Risk only', .1462370438945261, .8046666666666666), ('Risk × recurring value', .208296078201423, .6313333333333333)]:
    score = p if name == 'Risk only' else p * v
    chosen = np.argsort(-score, kind='stable')[:1500]
    assert np.isclose(np.sum(y[chosen] * v[chosen]) / np.sum(y * v), expected_capture)
    assert np.isclose(y[chosen].mean(), expected_precision)
assert np.isclose(summary['value_capture_relative_gain_over_risk'], .42437287197665974)
assert np.allclose(list(summary['bootstrap_intervals']['auc'].values()), [.689902981889822, .7054949137349805])
assert np.allclose(list(summary['bootstrap_intervals']['value_capture_relative_gain'].values()), [.363554223188793, .4899396334795961])
for relative, info in json.loads((ROOT / 'analysis_outputs/source_manifest.json').read_text()).items():
    assert sha256((ROOT / relative).read_bytes()).hexdigest() == info['sha256']
W = np.where(y == 1, 100000 * .02 / y.sum(), 100000 * .98 / (len(y) - y.sum()))
selected = pred.scenario_probability_at_2pct_prior.to_numpy() * v >= base['calibration_policy_threshold']
assert selected.sum() == 2505 and y[selected].sum() == 1771 and (1-y[selected]).sum() == 734
assert np.isclose(np.sum(W * selected), base['contacts'])
assert np.isclose(np.sum(W * selected * y), base['forecast_churners_contacted'])
assert np.isclose(np.sum(W * selected * y * v) * .2 * 6, base['retained_revenue_scenario'])
assert base['calibration_policy_threshold'] > 1 / (.2 * 6 * .6)
provenance = {'regression_checks': {k: a for k, (a, _) in checks.items()}, 'raw_test_rows': len(y), 'test_churners': int(y.sum()), 'test_nonchurners': int((1-y).sum()), 'W1': float(W[y==1][0]), 'W0': float(W[y==0][0]), 'selected_raw': int(selected.sum()), 'selected_churners': int(y[selected].sum()), 'selected_nonchurners': int((1-y[selected]).sum()), 'sample_slide9_score': 'p_s * V; top 1500 unweighted test rows', 'deployment_slide11_score': 'p_d * V; calibration-fitted weighted threshold; 2505 test rows', 'gate_threshold': 1 / (.2 * 6 * .6), 'budget_threshold': base['calibration_policy_threshold'], 'pilot_envelope_exact_assumed': 7872 + 5000}
(OUT / 'v1_regression_provenance.json').write_text(json.dumps(provenance, indent=2), encoding='utf-8')
doc_rows = json.loads((OUT / 'dataset_overview_tables.json').read_text(encoding='utf-8'))
lookup = {row[0].strip(): row[1] for row in doc_rows if len(row) >= 2}
records, windows = [], []
for name in ['Client.csv', 'Record.csv']:
    frame = pd.read_csv(ROOT / 'telecom' / name)
    print(name, frame.shape, 'Range columns:', [c for c in frame if '_Range' in c])
    for column in frame:
        series = frame[column]
        numeric = pd.api.types.is_numeric_dtype(series)
        record = {'source_file': name, 'column': column, 'dtype': str(series.dtype), 'missingness_pct': series.isna().mean()*100, 'min': series.min() if numeric else None, 'median': series.median() if numeric else None, 'p99': series.quantile(.99) if numeric else None, 'max': series.max() if numeric else None, 'exact_documentation': lookup.get(column, 'Not described in supplied overview'), 'window_status': 'not applicable'}
        if column.endswith('_Mean'):
            range_column = column.replace('_Mean', '_Range')
            max_ratio = float((frame[range_column] / series.where(series > 0)).max()) if range_column in frame else None
            record.update(window_status='Unspecified in supplied overview; corresponding _Range absent' if max_ratio is None else 'Empirical bound available; needs authoritative definition', empirical_range_mean_max=max_ratio)
            windows.append({'column': column, 'range_column_present': range_column in frame, 'max_range_mean_ratio': max_ratio})
        records.append(record)
pd.DataFrame(records).to_csv(OUT / 'schema_audit.csv', index=False)
(OUT / 'window_audit.json').write_text(json.dumps({'columns': windows, 'conclusion': 'The supplied overview never states a three- or four-month window for _Mean; no _Range fields exist in either CSV. avg3/avg6 windows are explicitly three/six months. Do not invent missing fields or claim the window is empirically proved. Even if a range/mean ratio equalled four, it would bound the window, not logically establish its length without nonnegativity and authoritative metadata.'}, indent=2), encoding='utf-8')
print(json.dumps(provenance, indent=2))
print('Step 0c–0e passed; schema audit:', len(records), 'source columns (shared ID counted twice)')
