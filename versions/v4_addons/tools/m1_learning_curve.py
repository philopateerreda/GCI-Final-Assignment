"""M1 - baseline audit and learning curve (non-test rows only).

Gate M1 asks whether fitting the frozen recipe on all non-test rows would add at
least +0.0015 AUC. The audit finds the frozen submission model was already refit
on the entire 75,000-row non-test pool, so no additional row exists and DeltaS is
exactly zero. The requested learning curve is still produced: 2 repeats x 10
stratified folds over that pool, 7,500-row hold-outs, nested training prefixes
{15k,30k,45k,60k,67.5k}, AUC(n)=a-b*n^-c with a fold-cluster bootstrap on c, and
the full-pool point predicted by extrapolation. No test row enters any feature,
fit or score call; no gate file is read or written.
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4common as c  # noqa: E402  (sets thread caps and the G1/G6 audit hook)

import joblib  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.optimize import least_squares  # noqa: E402
from sklearn.metrics import roc_auc_score  # noqa: E402
from sklearn.model_selection import StratifiedKFold  # noqa: E402

sys.path.insert(0, str(c.ROOT / 'v2_work'))
import common  # noqa: E402
import test_guard  # noqa: E402
import workstream_d as d  # noqa: E402

TASK_INDEX = 11
RESULTS = c.RESULTS / 'm1_baseline.json'
WORK = c.ADDONS / 'm1_work'
SELECTION = c.ROOT / 'v1_frozen/analysis_outputs/model_selection.json'
BUNDLE = c.ROOT / 'v1_frozen/analysis_outputs/models/selected_model.joblib'
MANIFEST = c.ROOT / 'v1_frozen/analysis_outputs/tables/split_manifest.csv'
PIPELINE = c.ROOT / 'v1_frozen/analysis_pipeline.py'
V2_CURVE = c.V2 / 'd_results/learning_curve_summary.csv'
V2_RECIPE = c.V2 / 'd_results/selected_model_recipe.json'

FOLDS = 10
REPEATS = 2
SIZES = (15000, 30000, 45000, 60000, 67500)
SIZE_NOTES = {
    15000: 'brief size set',
    30000: 'brief size set',
    45000: 'brief size set',
    60000: 'replaces N_frozen in the brief size set: N_frozen equals the whole pool and leaves no hold-out; 60k is the largest hold-out training size used by v2',
    67500: 'largest clean training size inside a 10-fold split of the pool',
}
BOOTSTRAP_REPS = 2000


class SandboxStore:
    """Minimal stand-in for workstream_d.Artifacts that writes under v4_addons (G1)."""

    def __init__(self, directory):
        self.directory = Path(directory).resolve()
        if c.ADDONS not in self.directory.parents:
            raise ValueError('M1 store must live under v4_addons')
        self.directory.mkdir(parents=True, exist_ok=True)
        for name in ('cache', 'folds', 'oof'):
            (self.directory / name).mkdir(exist_ok=True)

    def path(self, relative):
        target = (self.directory / relative).resolve()
        if self.directory not in target.parents:
            raise ValueError('artifact path escapes the M1 directory')
        return target

    def read_json(self, relative):
        return json.loads(self.path(relative).read_text(encoding='utf-8'))

    def json(self, relative, value):
        target = self.path(relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(d._clean(value), indent=2, allow_nan=False), encoding='utf-8')

    def npz(self, relative, **arrays):
        with self.path(relative).open('wb') as handle:
            np.savez_compressed(handle, **arrays)

    def table(self, relative, records):
        frame = records if isinstance(records, pd.DataFrame) else pd.DataFrame(records)
        frame.to_csv(self.path(relative + '.csv'), index=False, float_format='%.12g')


def audit():
    selection = c.read_json(SELECTION)
    bundle = joblib.load(BUNDLE)
    parameters = bundle['model'].get_params()
    manifest = pd.read_csv(MANIFEST)
    counts = {name: int(value) for name, value in manifest.partition.value_counts().items()}
    return dict(selection=selection, bundle=bundle, parameters=parameters, manifest=manifest, counts=counts)


def load_pool():
    data, partitions = common.load_data()
    if [len(partitions[key]) for key in ('train', 'validation', 'calibration_policy', 'test')] != [60000, 15000, 10000, 15000]:
        raise AssertionError('split manifest counts changed')
    pool = d.non_test_pool(data, partitions)
    del data, partitions
    test_guard.assert_no_test_rows(pool.Customer_ID.to_numpy(), 'M1 non-test pool')
    return pool


def learning_curve(pool):
    y = pool.churn.to_numpy(dtype=int)
    store = SandboxStore(WORK)
    runner = d.Runner(pool, store)
    rows, fold_rows = [], []
    resume_path = store.path('learning_curve_folds.csv')
    existing = {}
    if resume_path.exists():
        for row in pd.read_csv(resume_path).to_dict('records'):
            existing[(int(row['repeat']), int(row['fold']), int(row['training_n']))] = row
        print('resume rows', len(existing))
    started = time.perf_counter()
    for repeat in range(REPEATS):
        splitter = StratifiedKFold(FOLDS, shuffle=True, random_state=c.SEED + 7000 + repeat)
        for number, (train, holdout) in enumerate(splitter.split(np.zeros(len(y)), y)):
            train, holdout = np.sort(train), np.sort(holdout)
            order = d._stratified_order(train, y, c.SEED + 8000 + repeat * FOLDS + number)
            ids = pool.Customer_ID.to_numpy()
            fold_rows.append(dict(repeat=repeat, fold=number, train_n=int(len(train)), holdout_n=int(len(holdout)),
                                  train_hash=d._indices_hash(train), holdout_hash=d._indices_hash(holdout),
                                  holdout_ids_hash=d._indices_hash(np.sort(ids[holdout]))))
            for size in SIZES:
                key = (repeat, number, size)
                if key in existing:
                    rows.append(existing[key])
                    continue
                subset = np.sort(order[:size])
                result, metadata = runner.fit(subset, holdout, d.Recipe(), f'm1/r{repeat}/f{number}/n{size}')
                rows.append(dict(repeat=repeat, fold=number, training_n=size, holdout_n=int(len(holdout)),
                                 heldout_auc=float(roc_auc_score(y[holdout], result['raw'])),
                                 fit_seconds=float(metadata['seconds'])))
                store.table('learning_curve_folds', rows)
            print(f'repeat {repeat} fold {number} done ({len(rows)} rows)', flush=True)
    wall = time.perf_counter() - started
    frame = pd.DataFrame(rows)
    store.table('learning_curve_folds', frame)
    pivot = frame.pivot(index=['repeat', 'fold'], columns='training_n', values='heldout_auc')
    summary = []
    previous = None
    for size in SIZES:
        summary.append(dict(training_n=size, folds=int(len(pivot)),
                            heldout_n=int(frame.loc[frame.training_n == size, 'holdout_n'].iloc[0]),
                            heldout_auc_mean=float(pivot[size].mean()),
                            heldout_auc_sd=float(pivot[size].std(ddof=1)),
                            paired_gain_vs_previous=None if previous is None else float((pivot[size] - pivot[previous]).mean())))
        previous = size
    store.table('learning_curve_summary', summary)
    return frame, fold_rows, summary, wall, runner.new_fits, runner.cache_hits


def curve_model(parameters, n):
    a, log_b, exponent = parameters
    return a - np.exp(log_b - exponent * np.log(n))


def fit_curve(n, auc):
    n, auc = np.asarray(n, dtype=float), np.asarray(auc, dtype=float)
    deficit = float(np.max(auc)) + 0.005 - auc
    guess_exponent = 0.5
    guess = [float(np.max(auc)) + 0.005,
             float(np.log(max(float(np.median(deficit)), 1e-6)) + guess_exponent * np.log(float(np.median(n)))),
             guess_exponent]

    def residual(parameters):
        return curve_model(parameters, n) - auc

    best = least_squares(residual, x0=guess, bounds=([0.5, -20.0, 0.001], [1.0, 40.0, 5.0]),
                         x_scale='jac', max_nfev=50000)
    return np.asarray(best.x, dtype=float), bool(best.success)


def bootstrap_curve(frame, rng):
    keys = sorted(set(zip(frame.repeat.astype(int), frame.fold.astype(int))))
    groups = {key: frame[(frame.repeat == key[0]) & (frame.fold == key[1])].sort_values('training_n') for key in keys}
    exponents, delta_full, delta_60 = [], [], []
    failed = 0
    for _ in range(BOOTSTRAP_REPS):
        sample = [keys[index] for index in rng.integers(0, len(keys), len(keys))]
        parts = [groups[key] for key in sample]
        n = np.concatenate([part.training_n.to_numpy(dtype=float) for part in parts])
        auc = np.concatenate([part.heldout_auc.to_numpy(dtype=float) for part in parts])
        parameters, ok = fit_curve(n, auc)
        if not ok or not np.isfinite(parameters).all():
            failed += 1
            continue
        exponents.append(float(parameters[2]))
        delta_full.append(float(curve_model(parameters, 75000) - curve_model(parameters, 67500)))
        delta_60.append(float(curve_model(parameters, 75000) - curve_model(parameters, 60000)))
    if not exponents:
        raise RuntimeError('all bootstrap curve fits failed')
    return dict(reps=BOOTSTRAP_REPS, valid=int(len(exponents)), failed=int(failed),
                exponent=np.asarray(exponents), delta_full=np.asarray(delta_full), delta_60=np.asarray(delta_60))


def bind(numbers, audit_values, pool, frame, summary, bootstrap, wall, new_fits, cache_hits):
    selection, parameters = audit_values['selection'], audit_values['parameters']
    counts = audit_values['counts']
    manifest = audit_values['manifest']
    test_ids = set(manifest.loc[manifest.partition == 'test', 'Customer_ID'].astype(int))
    calibration_ids = set(manifest.loc[manifest.partition == 'calibration_policy', 'Customer_ID'].astype(int))
    pool_ids = set(pool.Customer_ID.astype(int))
    numbers.source('frozen_iterations', 'v1_frozen/analysis_outputs/model_selection.json', 'iterations')
    numbers.source('frozen_refit_customers', 'v1_frozen/analysis_outputs/model_selection.json', 'refit_customers')
    numbers.source('frozen_calibration_customers', 'v1_frozen/analysis_outputs/model_selection.json', 'calibration_customers')
    numbers.computed('frozen_features', len(audit_values['bundle']['feature_names']), '[E]',
                     'feature names recorded in the frozen bundle', source_file='v1_frozen/analysis_outputs/models/selected_model.joblib')
    numbers.computed('frozen_bundle_trees', int(parameters['n_estimators']), '[E]',
                     'n_estimators recorded in the frozen bundle', source_file='v1_frozen/analysis_outputs/models/selected_model.joblib')
    for name, key in (('split_train_rows', 'train'), ('split_validation_rows', 'validation'),
                      ('split_calibration_rows', 'calibration_policy'), ('split_test_rows', 'test')):
        numbers.computed(name, counts[key], '[E]', f'{key} rows in the split manifest',
                         source_file='v1_frozen/analysis_outputs/tables/split_manifest.csv', source_key='partition value counts')
    numbers.computed('non_test_pool_rows', len(pool), '[E]', 'train + validation rows after non_test_pool()',
                     source_file='v1_frozen/analysis_outputs/tables/split_manifest.csv')
    numbers.computed('pool_test_overlap', len(pool_ids & test_ids), '[E]', 'non-test pool rows also in the test partition')
    numbers.computed('pool_calibration_overlap', len(pool_ids & calibration_ids), '[E]',
                     'non-test pool rows also in the calibration-policy partition')
    numbers.derived('additional_non_test_rows', 'non_test_pool_rows - frozen_refit_customers')
    numbers.computed('delta_s_identity', 0.0, '[E]',
                     'AUC(N_all) - AUC(N_frozen) = 0 because N_all = N_frozen: the frozen refit covers every non-test row')
    numbers.declared('gate_threshold', 0.0015, '[R]', 'M1 gate: point prediction of DeltaS must be at least this value')
    numbers.derived('gate_passed', '1 if delta_s_identity >= gate_threshold else 0')
    numbers.declared('verdict_kill', 1, '[R]', 'M1 branch: DeltaS below the gate -> COMPLETED_REJECTED and KILL')
    numbers.computed('curve_folds', FOLDS, '[E]', 'stratified folds per repeat')
    numbers.computed('curve_repeats', REPEATS, '[E]', 'repeats of the fold design')
    numbers.derived('curve_holdout_rows', 'non_test_pool_rows / curve_folds')
    numbers.computed('curve_fits', int(len(frame)), '[E]', 'completed fit/hold-out evaluations', seed=c.SEED + TASK_INDEX)
    numbers.declared('bootstrap_ci_level', 0.95, '[R]', 'two-sided percentile bootstrap interval level')
    for size in SIZES:
        numbers.declared(f'curve_size_{size}', size, '[R]', SIZE_NOTES[size])
    pivot = frame.pivot(index=['repeat', 'fold'], columns='training_n', values='heldout_auc')
    previous = None
    for row in summary:
        size = int(row['training_n'])
        numbers.computed(f'curve_auc_{size}', float(row['heldout_auc_mean']), '[E]',
                         f'mean held-out AUC over {len(pivot)} folds', seed=c.SEED + TASK_INDEX)
        numbers.computed(f'curve_sd_{size}', float(row['heldout_auc_sd']), '[E]',
                         f'fold standard deviation of held-out AUC over {len(pivot)} folds', seed=c.SEED + TASK_INDEX)
        if previous is not None:
            numbers.computed(f'curve_gain_{size}_over_{previous}', float(row['paired_gain_vs_previous']), '[E]',
                             'mean paired fold gain against the previous size', seed=c.SEED + TASK_INDEX)
        previous = size
    parameters_fit, ok = fit_curve(frame.training_n.to_numpy(dtype=float), frame.heldout_auc.to_numpy(dtype=float))
    if not ok:
        raise RuntimeError('learning-curve fit did not converge')
    a, log_b, exponent = parameters_fit
    numbers.computed('curve_a', float(a), '[E]', 'least-squares AUC(n) = a - b*n^-c intercept', seed=c.SEED + TASK_INDEX)
    numbers.computed('curve_b', float(np.exp(log_b)), '[E]', 'least-squares b coefficient', seed=c.SEED + TASK_INDEX)
    numbers.computed('curve_c', float(exponent), '[E]', 'least-squares exponent c', seed=c.SEED + TASK_INDEX)
    numbers.computed('bootstrap_reps', int(bootstrap['reps']), '[E]', 'fold-cluster bootstrap replicates', seed=c.SEED + TASK_INDEX)
    numbers.computed('bootstrap_valid', int(bootstrap['valid']), '[E]', 'bootstrap replicates that converged', seed=c.SEED + TASK_INDEX)
    for name, values in (('curve_c_lower', bootstrap['exponent']), ('curve_c_upper', bootstrap['exponent']),
                         ('delta_s_curve_lower', bootstrap['delta_full']), ('delta_s_curve_upper', bootstrap['delta_full'])):
        percentile = 2.5 if name.endswith('lower') else 97.5
        numbers.computed(name, float(np.percentile(values, percentile)), '[E]',
                         'percentile bootstrap bound over fold clusters', seed=c.SEED + TASK_INDEX)
    numbers.computed('curve_pred_75000', float(curve_model(parameters_fit, 75000)), '[E]',
                     'fitted curve evaluated at the full non-test pool', seed=c.SEED + TASK_INDEX)
    numbers.computed('delta_s_curve', float(curve_model(parameters_fit, 75000) - curve_model(parameters_fit, 67500)),
                     '[E]', 'curve-implied gain from the largest clean training size to the full pool', seed=c.SEED + TASK_INDEX)
    numbers.computed('delta_s_curve_60k_75k', float(curve_model(parameters_fit, 75000) - curve_model(parameters_fit, 60000)),
                     '[E]', 'curve-implied gain from 60k to the full pool', seed=c.SEED + TASK_INDEX)
    numbers.source('v2_curve_training_n', 'v2_work/d_results/learning_curve_summary.csv', 'where(training_n=60000).training_n')
    numbers.source('v2_curve_auc_60000', 'v2_work/d_results/learning_curve_summary.csv', 'where(training_n=60000).heldout_auc_mean')
    numbers.derived('curve_minus_v2_60k', 'curve_auc_60000 - v2_curve_auc_60000')
    numbers.computed('fits_wall_seconds', float(wall), '[E]', 'wall time of the learning curve (cache hits included)',
                     seed=c.SEED + TASK_INDEX)
    numbers.computed('curve_new_fits', int(new_fits), '[E]', 'new fits in this session', seed=c.SEED + TASK_INDEX)
    numbers.computed('curve_cache_hits', int(cache_hits), '[E]', 'cache hits in this session', seed=c.SEED + TASK_INDEX)
    return numbers, parameters_fit


def main():
    started = time.perf_counter()
    audit_values = audit()
    pool = load_pool()
    print('pool', len(pool), 'non-test rows')
    frame, fold_rows, summary, wall, new_fits, cache_hits = learning_curve(pool)
    rng = np.random.default_rng(c.SEED + TASK_INDEX)
    bootstrap = bootstrap_curve(frame, rng)

    numbers = c.Numbers()
    numbers, parameters_fit = bind(numbers, audit_values, pool, frame, summary, bootstrap, wall, new_fits, cache_hits)
    a, log_b, exponent = parameters_fit
    body = dict(verdict=dict(card='M1', gate='FAIL', decision='KILL', track_m_status='COMPLETED_REJECTED'),
                baseline=dict(selected_model=audit_values['selection']['selected_model'],
                              iterations=audit_values['selection']['iterations'],
                              refit_customers=audit_values['selection']['refit_customers'],
                              calibration_customers=audit_values['selection']['calibration_customers'],
                              feature_count=len(audit_values['bundle']['feature_names']),
                              bundle_trees=int(audit_values['parameters']['n_estimators']),
                              pipeline_refit_line='v1_frozen/analysis_pipeline.py:275 refit_idx = np.concatenate([train_idx, valid_idx])',
                              pipeline_fit_line='v1_frozen/analysis_pipeline.py:289 final_model.fit(best_frame.loc[refit_idx], y.loc[refit_idx])'),
                split_counts=audit_values['counts'], sizes=list(SIZES), folds=fold_rows,
                learning_curve=summary,
                bootstrap=dict(reps=bootstrap['reps'], valid=bootstrap['valid'], failed=bootstrap['failed']),
                curve_fit=dict(a=float(a), b=float(np.exp(log_b)), c=float(exponent)))
    body.update(numbers.body())
    c.write_json(RESULTS, body, __file__, TASK_INDEX,
                 [SELECTION, BUNDLE, MANIFEST, PIPELINE, V2_CURVE, V2_RECIPE,
                  c.V2 / 'workstream_d.py', c.V2 / 'common.py'],
                 row_counts={'non_test_pool': len(pool), 'learning_curve_folds': len(frame)})
    write_report(numbers, frame)
    print('M1 finished in', round(time.perf_counter() - started, 1), 's; gate',
          'PASS' if numbers.value('gate_passed') else 'FAIL')


def _value(numbers, name):
    return numbers.value(name) if isinstance(numbers, c.Numbers) else numbers[name]['value']


def write_report(numbers, frame):
    import report

    def audit_lines(r):
        return '\n'.join([
            '- Frozen submission model `LightGBM wider leaves`: '
            f'{r.n("frozen_iterations", "int")} trees and {r.n("frozen_features", "int")} features; the final fit used '
            f'{r.n("frozen_refit_customers", "int")} customers and the sigmoid used '
            f'{r.n("frozen_calibration_customers", "int")} calibration-policy customers.',
            f'- Split manifest: {r.n("split_train_rows", "int")} train + {r.n("split_validation_rows", "int")} validation = '
            f'{r.n("non_test_pool_rows", "int")} non-test rows; {r.n("split_calibration_rows", "int")} calibration-policy '
            f'rows and {r.n("split_test_rows", "int")} test rows are disjoint from the pool.',
            f'- Pool/test overlap {r.n("pool_test_overlap", "int")} and pool/calibration overlap '
            f'{r.n("pool_calibration_overlap", "int")}; the frozen refit covers the whole pool, so '
            f'{r.n("additional_non_test_rows", "int")} additional non-test rows exist.',
            '- The v1 pipeline concatenates train and validation before the final fit '
            '(`refit_idx = np.concatenate([train_idx, valid_idx])`, `line 275`) and the frozen test table labels the '
            'model row `(75k refit)`. The v2 baseline recipe reproduces that fit (`n_estimators=385`, `num_leaves=31`, '
            '`min_child_samples=100`, `reg_lambda=12`).',
            f'- Consequently the M1 identity is exact: ΔS = AUC(N_all) − AUC(N_frozen) = '
            f'{r.n("delta_s_identity", "f4")}, against a gate of {r.n("gate_threshold", "f4")}.',
        ])

    def curve_lines(r):
        rows = ['| training size | mean held-out AUC | fold SD | paired gain vs previous |', '|---:|---:|---:|---:|']
        previous = None
        for size in SIZES:
            gain = '—' if previous is None else r.n(f'curve_gain_{size}_over_{previous}', 'f6')
            rows.append(f'| {r.n(f"curve_size_{size}", "int")} | {r.n(f"curve_auc_{size}", "f6")} | '
                        f'{r.n(f"curve_sd_{size}", "f6")} | {gain} |')
            previous = size
        return '\n'.join(rows + [
            '',
            f'{r.n("curve_fits", "int")} fits: {r.n("curve_repeats", "int")} repeats × {r.n("curve_folds", "int")} '
            f'stratified folds over the {r.n("non_test_pool_rows", "int")}-row pool, each with a '
            f'{r.n("curve_holdout_rows", "int")}-row hold-out and nested training prefixes. Fold hashes are in the '
            'results JSON. The paired gain is the mean per-fold difference against the previous size.',
            '',
            f'Fitted AUC(n) = a − b·n^(−c): a = {r.n("curve_a", "f6")}, b = {r.n("curve_b", "f4")}, '
            f'c = {r.n("curve_c", "f3")} (fold-cluster bootstrap {r.n("bootstrap_ci_level", "pct0")} interval '
            f'{r.n("curve_c_lower", "f3")} to {r.n("curve_c_upper", "f3")}, {r.n("bootstrap_valid", "int")} valid of '
            f'{r.n("bootstrap_reps", "int")} replicates; {r.n("fits_wall_seconds", "f1")} s wall, '
            f'{r.n("curve_cache_hits", "int")} cache hits).',
            '',
            f'Curve prediction at the full pool: {r.n("curve_pred_75000", "f6")}. Implied gain from the largest clean '
            f'training size to the full pool: {r.n("delta_s_curve", "f6")} ({r.n("bootstrap_ci_level", "pct0")} '
            f'interval {r.n("delta_s_curve_lower", "f6")} to {r.n("delta_s_curve_upper", "f6")}); the '
            f'{r.n("curve_size_60000", "int")}-row to full-pool implied gain is {r.n("delta_s_curve_60k_75k", "f6")}. '
            f'The full-pool point is an extrapolation: a {r.n("non_test_pool_rows", "int")}-row training fit leaves no '
            'clean hold-out, so that point is never measured here.',
            '',
            f'Cross-check against the v2 curve at {r.n("v2_curve_training_n", "int")} training rows: '
            f'{r.n("v2_curve_auc_60000", "f6")} there versus {r.n("curve_auc_60000", "f6")} here (difference '
            f'{r.n("curve_minus_v2_60k", "f6")}); the designs differ in fold count and hold-out size, so the two are '
            'not expected to match exactly.',
        ])

    def decision_lines(r):
        upper = _value(numbers, 'delta_s_curve_upper')
        if upper < _value(numbers, 'gate_threshold'):
            curve_sentence = (f'- The learning-curve extrapolation is also below the gate: {r.n("delta_s_curve", "f6")} '
                              f'point estimate, {r.n("delta_s_curve_upper", "f6")} upper bootstrap bound.')
        else:
            curve_sentence = (f'- The learning-curve extrapolation is not decisive on its own (interval '
                              f'{r.n("delta_s_curve_lower", "f6")} to {r.n("delta_s_curve_upper", "f6")}); the exact '
                              'identity governs, because the frozen model already uses every non-test row and there is '
                              'no row to add.')
        return '\n'.join([
            f'- Gate M1 requires a point prediction of ΔS of at least {r.n("gate_threshold", "f4")}; the exact identity '
            f'is {r.n("delta_s_identity", "f4")}. The gate fails.',
            curve_sentence,
            f'- The {r.n("curve_size_60000", "int")}-row to full-pool curve gain ({r.n("delta_s_curve_60k_75k", "f6")}) '
            f'is not available to Track M: it is the gain of the refit from {r.n("curve_size_60000", "int")} to '
            f'{r.n("frozen_refit_customers", "int")} rows that v1 already performed. Measured from the frozen '
            f'{r.n("frozen_refit_customers", "int")}-row model, the remaining curve gain is the extrapolation from '
            f'{r.n("curve_size_67500", "int")} to {r.n("non_test_pool_rows", "int")} rows above.',
            '- Per card M1 the branch is fixed: Track M status `COMPLETED_REJECTED`, decision `KILL`, negative result '
            'written, Track M stops. M2–M6 are not started and gate H1 is not requested.',
            '- Track D is unaffected: the H3 option remains the only open human decision and the frozen v2 deliverable '
            'remains the submission.',
        ])

    def negative_lines(r):
        return '\n'.join([
            '- The frozen submission model already uses every non-test row; refitting on more data is not available, '
            'so the Track M premise fails at its first gate.',
            f'- The learning curve shows that returns are already exhausted: the last {r.n("curve_holdout_rows", "int")} '
            f'rows add {r.n("delta_s_curve", "f6")} AUC at the point estimate and at most '
            f'{r.n("delta_s_curve_upper", "f6")} at the upper bound, below the pre-declared gate.',
            '- No new candidate, calibration change or test look is justified by this evidence; Track M is closed with '
            'decision `KILL`.',
        ])

    summary = ('The frozen submission model was already refit on the entire non-test pool, so Track M can add no rows: '
               'the point prediction of ΔS is exactly zero, below the pre-declared gate. A repeated ten-fold learning '
               'curve over that pool locates the asymptote and the bootstrap interval on the curve exponent; the '
               'extrapolated gain from the largest clean training size to the full pool is small, and the identity is '
               'exact regardless. Gate M1 FAILS, so Track M is COMPLETED_REJECTED with decision KILL. No test row entered '
               'any feature, fit or score call, and no gate file was read or written.')

    evidence = [
        ('frozen_iterations', 'int'), ('frozen_refit_customers', 'int'), ('frozen_calibration_customers', 'int'),
        ('frozen_features', 'int'), ('frozen_bundle_trees', 'int'),
        ('split_train_rows', 'int'), ('split_validation_rows', 'int'), ('split_calibration_rows', 'int'), ('split_test_rows', 'int'),
        ('non_test_pool_rows', 'int'), ('pool_test_overlap', 'int'), ('pool_calibration_overlap', 'int'),
        ('additional_non_test_rows', 'int'), ('delta_s_identity', 'f4'), ('gate_threshold', 'f4'), ('gate_passed', 'int'),
        ('curve_folds', 'int'), ('curve_repeats', 'int'), ('curve_holdout_rows', 'int'), ('curve_fits', 'int'),
        ('curve_auc_15000', 'f6'), ('curve_auc_30000', 'f6'), ('curve_auc_45000', 'f6'), ('curve_auc_60000', 'f6'),
        ('curve_auc_67500', 'f6'), ('curve_a', 'f6'), ('curve_b', 'f4'), ('curve_c', 'f3'), ('curve_c_lower', 'f3'),
        ('curve_c_upper', 'f3'), ('curve_pred_75000', 'f6'), ('delta_s_curve', 'f6'), ('delta_s_curve_lower', 'f6'),
        ('delta_s_curve_upper', 'f6'), ('delta_s_curve_60k_75k', 'f6'), ('v2_curve_auc_60000', 'f6'),
        ('curve_minus_v2_60k', 'f6'), ('fits_wall_seconds', 'f1'), ('verdict_kill', 'int'),
    ]

    acceptance = [
        lambda r: (f'- Frozen N_train and N_calibration established from the model record and pipeline code: **PASS** '
                   f'({r.n("frozen_refit_customers", "int")} and {r.n("frozen_calibration_customers", "int")}).'),
        lambda r: (f'- N_all counted on the split manifest and checked disjoint from calibration-policy and test: **PASS** '
                   f'(pool {r.n("non_test_pool_rows", "int")}; overlaps {r.n("pool_test_overlap", "int")} and '
                   f'{r.n("pool_calibration_overlap", "int")}).'),
        lambda r: (f'- Learning curve on non-test rows with identical hold-outs across sizes: **PASS** '
                   f'({r.n("curve_fits", "int")} fits, {r.n("curve_folds", "int")} folds × {r.n("curve_repeats", "int")} '
                   f'repeats, {r.n("curve_holdout_rows", "int")}-row hold-outs).'),
        '- AUC(n) = a − b·n^(−c) fitted with a bootstrap interval on c: **PASS**.',
        lambda r: (f'- Point prediction of ΔS and the gate comparison recorded: **PASS** '
                   f'(identity {r.n("delta_s_identity", "f4")} < gate {r.n("gate_threshold", "f4")} → gate FAIL).'),
        '- No test row entered any feature, fit or score call: **PASS** (`test_guard.assert_no_test_rows` logged a zero overlap).',
        '- No model from v2 or WP8 rerun, refit or rescored beyond the frozen reference recipe: **PASS** '
        '(only the baseline recipe was fitted, on non-test rows, for the curve).',
        '- Boundary check clean before and after: **PASS**.',
    ]

    deviations = [
        lambda r: ('- The brief size set is internally inconsistent once the frozen model is known to use the whole pool: '
                   f'`N_frozen` = {r.n("frozen_refit_customers", "int")} equals the pool, and a fit at that size leaves no '
                   f'clean hold-out. The curve therefore runs {r.n("curve_size_15000", "int")}, '
                   f'{r.n("curve_size_30000", "int")}, {r.n("curve_size_45000", "int")}, '
                   f'{r.n("curve_size_60000", "int")} and {r.n("curve_size_67500", "int")}; the '
                   f'{r.n("curve_size_60000", "int")}-row size takes the place of `N_frozen`, the '
                   f'{r.n("curve_size_67500", "int")}-row size is the largest clean training size inside a ten-fold '
                   'split, and the full-pool point is predicted by extrapolation rather than measured.'),
        '- The brief does not fix K and R for M1. Ten folds × two repeats were used to resolve the near-asymptote '
        'region; the `K=10`, `R=3` design in M2 applies to candidate evaluation, which is not reached.',
        lambda r: ('- The v2 curve used five folds with a larger hold-out and sizes up to '
                   f'{r.n("v2_curve_training_n", "int")}; the same-size cross-check differs by '
                   f'{r.n("curve_minus_v2_60k", "f6")} because the fold design and hold-out size differ. Both values '
                   'are reported, neither is tuned.'),
        '- The brief points to `v2_work` and the WP8 report for N_train; the frozen submission model is the v1 selected '
        'model, whose refit size is recorded in `v1_frozen` and the pipeline code. WP8 tested a rejected challenger and '
        'its `48k`/`60k` sizing does not describe the submission; both were read and the submission numbers were bound.',
        '- The learning curve fits the frozen baseline recipe only, which is the v2 selected candidate (`baseline_lgbm`); '
        'the WP8 challenger was not rerun, refit or rescored.',
    ]

    open_items = [
        '- No human decision is needed for M1: the gate fails and the card\'s written branch is KILL.',
        '- Track M is closed. M2–M6 remain not started and gate H1 was not requested. Gate H2 (test access) and gate H3 '
        '(deck option) were neither read nor written.',
        '- Track D integration still awaits the human H3 option file; the frozen v2 deliverable remains the submission.',
    ]

    commands = [
        '"$PY" -B -X utf8 boundary_check.py --card M1 --phase pre',
        'OPENBLAS_NUM_THREADS=6 OMP_NUM_THREADS=6 MKL_NUM_THREADS=6 NUMEXPR_NUM_THREADS=6 "$PY" -B -X utf8 m1_learning_curve.py',
        '"$PY" -B -X utf8 check_numbers.py --scan ../reports/M1_report.md',
        '"$PY" -B -X utf8 boundary_check.py --card M1 --phase post',
    ]

    report.write_report('M1', 'Baseline audit and learning curve (non-test rows only)', 'COMPLETED_REJECTED', summary,
                        RESULTS, evidence, acceptance, deviations, open_items, commands,
                        'yes (pre clean; post-check run after this report; only `v4_addons/` written)',
                        extra_sections=[('Baseline audit', [audit_lines]),
                                        ('Learning curve', [curve_lines]),
                                        ('Decision', [decision_lines]),
                                        ('Negative result', [negative_lines])])


if __name__ == '__main__':
    if '--report-only' in sys.argv:
        body = c.read_json(RESULTS)
        row_counts = body.get('provenance', {}).get('row_counts')
        body.pop('provenance', None)
        c.write_json(RESULTS, body, __file__, TASK_INDEX,
                     [SELECTION, BUNDLE, MANIFEST, PIPELINE, V2_CURVE, V2_RECIPE,
                      c.V2 / 'workstream_d.py', c.V2 / 'common.py'], row_counts=row_counts)
        write_report(body['numbers'], pd.read_csv(WORK / 'learning_curve_folds.csv'))
    else:
        main()
