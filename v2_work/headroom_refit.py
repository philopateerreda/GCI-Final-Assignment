from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.special import logit
from sklearn.model_selection import train_test_split

import common
import workstream_d as d


ROOT, WORK = common.ROOT, common.WORK


def fit_backend(X, y, cats, backend, weight=None):
    specification = d.model_spec(backend)
    medians = None
    if backend == 'lgbm':
        from lightgbm import LGBMClassifier
        model = LGBMClassifier(**specification)
    elif backend == 'xgboost':
        from xgboost import XGBClassifier
        model = XGBClassifier(**specification)
    elif backend == 'catboost':
        from catboost import CatBoostClassifier
        numeric = [c for c in X if c not in cats]
        medians = X[numeric].median().fillna(0)
        X = catboost_inputs(X, cats, medians)
        model = CatBoostClassifier(**specification, cat_features=cats)
    elif backend == 'spline_logistic':
        model = d.spline_pipeline(X, cats, specification)
    else:
        raise ValueError(backend)
    import warnings
    from sklearn.exceptions import ConvergenceWarning
    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter('always', ConvergenceWarning)
        if weight is None:
            model.fit(X, y)
        else:
            model.fit(X, y, sample_weight=weight)
    assert not any(issubclass(item.category, ConvergenceWarning) for item in recorded), 'Final refit did not converge.'
    return model, medians


def catboost_inputs(X, cats, medians):
    X = X.copy()
    X[medians.index] = X[medians.index].fillna(medians)
    for column in cats:
        X[column] = X[column].astype(object).where(X[column].notna(), '__UNKNOWN__').astype(str)
    return X


def prepare():
    recipe_path = WORK / 'd_results/selected_model_recipe.json'
    selected = json.loads(recipe_path.read_text(encoding='utf-8'))
    assert selected['gate_d_passed'] and selected['decision_allowed']
    assert not (WORK / 'final_frozen_protocol.json').exists()
    assert not (WORK / 'a_selected_test.csv').exists()
    target = WORK / 'd_promoted_model.joblib'
    assert not target.exists(), 'Do not repeat a completed production refit.'
    data, splits = common.load_data()
    train = np.r_[splits['train'], splits['validation']]
    pool = d.non_test_pool(data, splits)
    development, calibration = train_test_split(np.arange(len(pool)), test_size=.2,
        stratify=pool.churn, random_state=common.SEED + 3000)
    groups = tuple(selected['selected_feature_groups']) if not selected['selected_candidate'].startswith('nested_') else ()
    blend_weights = None
    if selected['selected_candidate'].startswith('nested_'):
        store = d.Artifacts(WORK / 'd_final_screen')
        store.bind({'recipe_sha256': sha256(recipe_path.read_bytes()).hexdigest(),
                    'seed': common.SEED + 3000, 'rows': 75000, 'test_rows_used': 0})
        runner = d.Runner(pool, store)
        fold = d.Fold(0, 0, np.arange(len(pool)), np.array([], dtype=int),
                      np.sort(development), np.sort(calibration))
        groups, inner, screen = runner.nested_screen(fold)
        if selected['backend'] == 'blend':
            oof = np.column_stack([runner.inner_oof(fold, inner, backend, groups)
                                   for backend in d.BLEND_MODELS])
            blend_weights, optimizer = d.fit_blend(oof, pool.churn.iloc[fold.development])
            store.json('final_blend_spec.json', {'weights': blend_weights, 'optimizer': optimizer,
                                                'groups': groups, 'screen': screen})
    components = d.BLEND_MODELS if selected['backend'] == 'blend' else (selected['backend'],)
    fitted = []
    for backend in components:
        recipe = d.Recipe(backend=backend, groups=groups,
                          value_weighted=selected['weighted_training'])
        X, _, cats, statistics = d.design(data, train, splits['calibration_policy'], recipe)
        weight = None
        if recipe.value_weighted:
            value, _ = common.values(data, train)
            weight = np.maximum(value[train], 1e-6)
            weight /= weight.mean()
        model, medians = fit_backend(X, data.churn.iloc[train].to_numpy(), cats, backend, weight)
        fitted.append({'model': model, 'recipe': asdict(recipe), 'cats': cats,
                       'catboost_medians': medians, 'statistics': statistics})
    bundle = {'selected_candidate': selected['selected_candidate'], 'train_indices': train,
              'components': fitted, 'blend_weights': blend_weights,
              'test_scored': False, 'recipe_sha256': sha256(recipe_path.read_bytes()).hexdigest()}
    joblib.dump(bundle, target)
    common.dump('d_promoted_refit.json', {'candidate': bundle['selected_candidate'],
                'training_rows': len(train), 'groups': groups, 'test_rows_used': 0,
                'model_sha256': sha256(target.read_bytes()).hexdigest(),
                'value_proxy_limits_source': 'Original 60000 train for comparable policy valuation; model weights use final fitting rows.',
                'feature_statistics': [row['statistics'] for row in fitted]})
    return bundle


def raw_predict(data, indices):
    bundle = joblib.load(WORK / 'd_promoted_model.joblib')
    outputs = []
    for component in bundle['components']:
        spec = component['recipe'].copy()
        spec['groups'], spec['drop'] = tuple(spec['groups']), tuple(spec['drop'])
        recipe = d.Recipe(**spec)
        _, X, cats, statistics = d.design(data, bundle['train_indices'], indices, recipe)
        assert d._clean(statistics) == d._clean(component['statistics'])
        if recipe.backend == 'catboost':
            X = catboost_inputs(X, cats, component['catboost_medians'])
        outputs.append(component['model'].predict_proba(X)[:, 1])
    raw = d.blend_predict(np.column_stack(outputs), bundle['blend_weights']) if bundle['blend_weights'] is not None else outputs[0]
    assert np.isfinite(raw).all()
    return raw


def calibration_predictions(partition='calibration_policy'):
    assert partition == 'calibration_policy'
    data, splits = common.load_data()
    indices = splits[partition]
    raw = raw_predict(data, indices)
    value, _ = common.values(data, splits['train'])
    frame = pd.DataFrame({'Customer_ID': data.Customer_ID.iloc[indices].to_numpy(),
                          'y': data.churn.iloc[indices].to_numpy(), 'p_raw': raw,
                          'p_s': raw, 'p_d': common.shift(raw), 'value': value[indices],
                          'weight': common.weights(data.churn.iloc[indices].to_numpy()),
                          'partition': partition})
    return data, splits, frame


def evaluate_test():
    import workstream_a as a
    from final_protocol import begin_test
    begin_test(promoted=True)
    data, splits = common.load_data()
    indices = splits['test']
    raw = raw_predict(data, indices)
    calibrator = joblib.load(WORK / 'a_calibrator.joblib')
    probability = calibrator.predict(raw)
    value, _ = common.values(data, splits['train'])
    frame = pd.DataFrame({'Customer_ID': data.Customer_ID.iloc[indices].to_numpy(),
                          'y': data.churn.iloc[indices].to_numpy(), 'p_raw': raw,
                          'p_s': probability, 'p_d': common.shift(probability),
                          'value': value[indices], 'weight': common.weights(data.churn.iloc[indices].to_numpy()),
                          'partition': 'test'})
    spec = json.loads((WORK / 'a_spec.json').read_text(encoding='utf-8'))
    scores = a.scores(frame)
    frame['selected_risk'] = scores['risk'] >= spec['thresholds']['0.02']['risk']
    frame['selected_bayes'] = scores['bayes'] >= spec['thresholds']['0.02']['bayes']
    frame.to_csv(WORK / 'a_selected_test.csv', index=False)
    a.analyze(pd.read_csv(WORK / 'a_selected_calibration.csv'), frame, data, splits, 'test')
    paired_test_comparison(frame)
    return frame


def paired_test_comparison(frame):
    from sklearn.metrics import roc_auc_score, log_loss, brier_score_loss, accuracy_score
    import workstream_a as a

    frozen = pd.read_csv(ROOT / 'v1_frozen/analysis_outputs/tables/heldout_predictions.csv').set_index('Customer_ID')
    reference = frozen.loc[frame.Customer_ID]
    y = frame.y.to_numpy()
    assert np.array_equal(y, reference.actual_churn.to_numpy())
    v1 = reference.sample_calibrated_churn_probability.to_numpy()
    probability = frame.p_s.to_numpy()
    raw = frame.p_raw.to_numpy()
    rng = np.random.default_rng(common.SEED + 4000)
    draws = []
    for replicate in range(300):
        ix = rng.integers(0, len(y), len(y))
        baseline_auc = roc_auc_score(y[ix], v1[ix])
        candidate_auc = roc_auc_score(y[ix], raw[ix])
        draws.append({'replicate': replicate, 'v1_auc': baseline_auc,
                      'v2_auc': candidate_auc, 'paired_auc_gain': candidate_auc - baseline_auc})
    draws = pd.DataFrame(draws)
    draws.to_csv(WORK / 'd_final_test_bootstrap.csv', index=False)
    common.dump('d_final_test_comparison.json', {
        'test_rows': len(frame), 'v1_test_previously_evaluated': True,
        'decisions_frozen_before_scoring': True, 'test_used_for_selection': False,
        'v1_auc': float(roc_auc_score(y, v1)), 'v2_auc': float(roc_auc_score(y, raw)),
        'paired_auc_gain': float(roc_auc_score(y, raw) - roc_auc_score(y, v1)),
        'paired_auc_gain_95ci': [float(draws.paired_auc_gain.quantile(.025)), float(draws.paired_auc_gain.quantile(.975))],
        'v2_auc_95ci': [float(draws.v2_auc.quantile(.025)), float(draws.v2_auc.quantile(.975))],
        'v2_calibrated_metrics': {'auc': float(roc_auc_score(y, probability)),
                                  'log_loss': float(log_loss(y, probability)),
                                  'brier': float(brier_score_loss(y, probability)),
                                  'accuracy_at_half': float(accuracy_score(y, probability >= .5))},
        'sample_top10': {name: a.sample_measure(frame, score) for name, score in a.scores(frame, prior=.4956).items()},
        'interval_scope': '300 paired IID row resamples of the same heldout rows, conditional on locked models; no retraining, external validation or post-selection guarantee.',
        'promotion_rule': 'Gate D non-test results determine promotion, never this heldout comparison.'})
