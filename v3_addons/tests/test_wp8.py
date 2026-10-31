"""Tests for NEW WP8 code only; no classifier or calibrator is fitted.

The actual-output test is skipped until a completed WP8 summary exists. It then
runs the read-only independent audit, never a batch, seal, or old test suite.
"""
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / 'src'
sys.path.insert(0, str(SRC))
import common  # Unchanged audit/runtime guard before numerical dependencies.
import wp8_model as wp8

import ast
import io
import json
import unittest
from unittest.mock import patch
from types import SimpleNamespace

import numpy as np
import pandas as pd
from scipy.special import expit, logit
from scipy.stats import t
from sklearn.model_selection import StratifiedKFold, train_test_split


EXPECTED_NEW = (
    'wp8_mou_3_6_contrast', 'wp8_mou_mean_3_contrast',
    'wp8_mou_contrast_difference', 'wp8_mou_log_curvature',
    'wp8_rev_3_6_contrast', 'wp8_rev_mean_3_contrast',
    'wp8_rev_contrast_difference', 'wp8_rev_log_curvature',
    'wp8_qty_3_6_contrast', 'wp8_qty_3_lifetime_contrast', 'wp8_qty_log_3_6',
    'wp8_tenure_equipment_gap', 'wp8_price_per_month', 'wp8_phones_per_month',
    'wp8_models_per_phone', 'wp8_days_per_model',
    'wp8_price_tenure_peer_ratio', 'wp8_days_tenure_peer_ratio',
    'wp8_recurring_usage_peer_ratio',
    'wp8_missing_total', 'wp8_missing_recent_history', 'wp8_missing_billing',
    'wp8_missing_care', 'wp8_missing_equipment', 'wp8_missing_tenure_lines',
    'wp8_missing_calls_usage')


def synthetic_raw(n=20):
    frame = pd.DataFrame({name: np.arange(n, dtype=float) + 2 for name in wp8.RAW_NUMERIC})
    for name in wp8.CATEGORICAL:
        frame[name] = ['N' if i % 2 else 'Y' for i in range(n)]
    frame['months'] = np.arange(n, dtype=float) + 6
    frame['eqpdays'] = np.arange(n, dtype=float) * 10 + 30
    frame['hnd_price'] = np.arange(n, dtype=float) * 3 + 20
    return frame.loc[:, list(wp8.RAW_FEATURES)]


class FeaturesTest(unittest.TestCase):
    def test_exact_frozen_87_and_new_26_names(self):
        manifest = json.loads((wp8.ROOT / 'analysis_outputs/feature_manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(list(wp8.FROZEN_FEATURES), manifest['features'])
        self.assertEqual(list(wp8.CATEGORICAL), manifest['categorical_features'])
        self.assertEqual(wp8.NEW_FEATURES, EXPECTED_NEW)
        self.assertEqual(len(wp8.FROZEN_FEATURES), 87)
        self.assertEqual(len(wp8.NEW_FEATURES), 26)
        self.assertEqual(len(wp8.FEATURES), 113)
        self.assertEqual(len(wp8.FEATURES), len(set(wp8.FEATURES)))
        self.assertFalse(set(manifest['excluded_features']) & set(wp8.FEATURES))
        raw = synthetic_raw()
        design = wp8.transform_features(raw, wp8.fit_reference(raw.iloc[:12]))
        self.assertEqual(tuple(design.columns), tuple(manifest['features']) + EXPECTED_NEW)
        self.assertTrue(all(design[c].dtype == np.float32 for c in design if c not in wp8.CATEGORICAL))

    def test_frozen_transformations_independent_reference(self):
        raw = synthetic_raw(5)
        raw.loc[0, 'eqpdays'] = -1
        raw.loc[1, 'eqpdays'] = np.nan
        raw.loc[2, 'months'] = 0
        raw.loc[3, 'avgmou'] = 0
        raw.loc[4, 'uniqsubs'] = 0
        raw.loc[4, 'actvsubs'] = 2
        raw.loc[1, 'new_cell'] = None
        actual = wp8.frozen_features(raw)
        expected = raw.copy()
        days = raw.eqpdays.where(raw.eqpdays >= 0)
        expected['eqpdays'] = days
        expected['equipment_age_invalid'] = (raw.eqpdays < 0).astype('int8')
        expected['usage_recent_to_lifetime'] = raw.avg3mou / np.maximum(raw.avgmou, 1)
        expected['usage_three_to_six_months'] = raw.avg3mou / np.maximum(raw.avg6mou, 1)
        expected['revenue_recent_to_lifetime'] = raw.avg3rev / np.maximum(raw.avgrev, 1)
        expected['revenue_three_to_six_months'] = raw.avg3rev / np.maximum(raw.avg6rev, 1)
        expected['overage_charge_share'] = raw.ovrrev_Mean / np.maximum(raw.rev_Mean, 1)
        expected['recurring_charge_share'] = raw.totmrc_Mean / np.maximum(raw.rev_Mean, 1)
        expected['failed_call_index'] = raw.drop_blk_Mean / np.maximum(raw.attempt_Mean, 1)
        expected['care_calls_per_100_attempts'] = 100 * raw.custcare_Mean / np.maximum(raw.attempt_Mean, 1)
        expected['equipment_age_to_tenure'] = days / (30.4375 * np.maximum(raw.months, 1))
        expected['inactive_household_lines'] = np.maximum(raw.uniqsubs - raw.actvsubs, 0)
        expected['usage_change_scaled'] = raw.change_mou / np.maximum(raw.avg3mou, 1)
        expected['revenue_change_scaled'] = raw.change_rev / np.maximum(raw.avg3rev, 1)
        for c in expected:
            expected[c] = (expected[c].fillna('__MISSING__').astype(str) if c in wp8.CATEGORICAL else
                           expected[c].replace([np.inf, -np.inf], np.nan).astype('float32'))
        pd.testing.assert_frame_equal(actual, expected)

    def test_synthetic_feature_formula_reference(self):
        raw = synthetic_raw(3)
        raw.loc[0, ['mou_Mean', 'avg3mou', 'avg6mou']] = [30, 20, 10]
        raw.loc[0, ['rev_Mean', 'avg3rev', 'avg6rev']] = [-4, 8, 2]
        raw.loc[0, ['avg3qty', 'avg6qty', 'avgqty']] = [9, 3, 12]
        raw.loc[0, ['months', 'eqpdays', 'hnd_price', 'phones', 'models']] = [12, 180, 90, 3, 2]
        X = wp8.transform_features(raw, wp8.fit_reference(raw))
        expected = [10/31, 10/51, 10/51 - 10/31, np.log(31) - 2*np.log(21) + np.log(11),
                    6/11, -12/13, -12/13 - 6/11, -2*np.log(9) + np.log(3),
                    6/13, -3/22, np.log(10) - np.log(4),
                    (30.4375*12-180)/(30.4375*12), 90/12, 3/12, 2/3, 180/2]
        np.testing.assert_allclose(X.loc[0, list(EXPECTED_NEW[:16])].to_numpy(dtype=float),
                                   np.asarray(expected, dtype=np.float32), rtol=0, atol=0)
        raw.loc[0, 'avg6mou'] = np.nan
        raw.loc[1, 'eqpdays'] = -9
        Y = wp8.transform_features(raw, wp8.fit_reference(raw))
        self.assertTrue(np.isnan(Y.loc[0, 'wp8_mou_3_6_contrast']))
        self.assertTrue(np.isnan(Y.loc[0, 'wp8_mou_contrast_difference']))
        self.assertTrue(np.isnan(Y.loc[0, 'wp8_mou_log_curvature']))
        self.assertTrue(np.isnan(Y.loc[1, 'wp8_days_per_model']))
        self.assertTrue(np.isnan(Y.loc[1, 'wp8_days_tenure_peer_ratio']))

    def test_peer_reference_training_only_and_scoring_batch_invariance(self):
        raw = synthetic_raw(30)
        raw.loc[0, 'months'] = np.nan
        raw.loc[1, 'hnd_price'] = np.nan
        reference = wp8.fit_reference(raw.iloc[:15])
        frozen = wp8.signature_hash(reference)
        self.assertEqual(reference['training_n'], 15)
        group = raw.months.iloc[:15].dropna().to_numpy()
        self.assertEqual(reference['peers']['price_tenure']['missing_group_median'], np.median(group))
        np.testing.assert_array_equal(reference['peers']['price_tenure']['edges'],
                                      np.unique(np.quantile(group, np.arange(.1, 1, .1))))
        batch = raw.iloc[15:].copy()
        batch.loc[16, 'new_cell'] = 'NEVER_IN_TRAIN'
        whole = wp8.transform_features(batch, reference)
        pieces = pd.concat([wp8.transform_features(batch.iloc[i:i+1], reference) for i in range(len(batch))])
        pd.testing.assert_frame_equal(whole, pieces)
        reverse = wp8.transform_features(batch.iloc[::-1], reference).loc[batch.index]
        pd.testing.assert_frame_equal(whole, reverse)
        extreme = batch.copy()
        extreme.loc[extreme.index[1:], list(wp8.RAW_NUMERIC)] = 1e8
        before = wp8.transform_features(batch.iloc[:1], reference)
        after = wp8.transform_features(extreme, reference).iloc[:1]
        pd.testing.assert_frame_equal(before, after)
        self.assertEqual(wp8.signature_hash(reference), frozen)
        self.assertTrue(pd.isna(whole.loc[16, 'new_cell']))
        self.assertNotIn('NEVER_IN_TRAIN', reference['category_vocabularies']['new_cell'])
        restored = json.loads(json.dumps(reference, allow_nan=False))
        pd.testing.assert_frame_equal(whole, wp8.transform_features(batch, restored))

    def test_peer_global_fallback_and_negative_validity(self):
        table = wp8.peer_table(np.array([0., 0., 10., 10.]), np.array([2., 4., np.nan, np.nan]))
        ratio = wp8.peer_ratio([100, np.nan], [6, np.nan], table)
        self.assertEqual(ratio[0], 2)
        self.assertTrue(np.isnan(ratio[1]))
        table = wp8.peer_table([np.nan, np.nan], [np.nan, np.nan])
        self.assertEqual(table['edges'], [])
        np.testing.assert_array_equal(wp8.peer_ratio([5], [4], table), [4])
        raw = synthetic_raw(5)
        raw.loc[0, 'totmrc_Mean'] = -7
        raw.loc[1, 'eqpdays'] = -4
        X = wp8.transform_features(raw, wp8.fit_reference(raw))
        self.assertEqual(X.loc[0, 'wp8_recurring_usage_peer_ratio'], 0)
        self.assertTrue(np.isnan(X.loc[1, 'wp8_days_tenure_peer_ratio']))

    def test_no_label_or_forbidden_reliance(self):
        raw = synthetic_raw()
        reference = wp8.fit_reference(raw.iloc[:10])
        expected = wp8.transform_features(raw, reference)
        manifest = json.loads((wp8.ROOT / 'analysis_outputs/feature_manifest.json').read_text(encoding='utf-8'))
        polluted = raw.copy()
        for c in manifest['excluded_features']:
            polluted[c] = object()
        actual = wp8.transform_features(polluted, wp8.fit_reference(polluted.iloc[:10]))
        pd.testing.assert_frame_equal(expected, actual)
        self.assertEqual(reference, wp8.fit_reference(polluted.iloc[:10]))

    def test_missingness_partition_original_numeric_only(self):
        families = wp8.missingness_families()
        columns = [c for cols in families.values() for c in cols]
        self.assertEqual(len(columns), len(set(columns)))
        self.assertEqual(set(columns), set(wp8.RAW_NUMERIC))
        self.assertEqual(tuple(families), wp8.FAMILY_NAMES)
        self.assertEqual(set(families['recent_history']), set(('change_mou change_rev avg3mou avg3rev avg3qty avg6mou avg6rev avg6qty').split()))
        self.assertEqual(set(families['billing']), set(('rev_Mean totmrc_Mean da_Mean ovrrev_Mean vceovr_Mean datovr_Mean roam_Mean totrev adjrev avgrev').split()))
        raw = synthetic_raw(3)
        for family in families:
            raw.loc[0, families[family][0]] = np.nan
        raw.loc[1, 'eqpdays'] = -1
        raw.loc[2, 'new_cell'] = None
        X = wp8.transform_features(raw, wp8.fit_reference(raw))
        self.assertEqual(X.loc[0, 'wp8_missing_total'], 6)
        self.assertEqual(X.loc[1, 'wp8_missing_total'], 1)
        self.assertEqual(X.loc[1, 'wp8_missing_equipment'], 1)
        self.assertEqual(X.loc[2, 'wp8_missing_total'], 0)
        for family in families:
            self.assertEqual(X.loc[0, 'wp8_missing_' + family], 1)
        np.testing.assert_array_equal(X['wp8_missing_total'], X[['wp8_missing_' + f for f in families]].sum(axis=1))


class PopulationAndFoldsTest(unittest.TestCase):
    def test_historical_csv_identity_rejects_predictor_only_drift_without_fits(self):
        client = b'Customer_ID,new_cell\n4,Y\n2,N\n'
        record = b'Customer_ID,churn,totmrc_Mean,avg3mou\n4,1,100,12\n2,0,100,9\n'
        expected = {'telecom\\Client.csv': wp8.sha256(client).hexdigest(),
                    'telecom\\Record.csv': wp8.sha256(record).hexdigest()}
        current = {'Client.csv': client, 'Record.csv': record}
        with patch.object(wp8, 'read_json', return_value={'source_sha256': expected}), \
             patch.object(wp8.common, 'digest', side_effect=lambda path: wp8.sha256(current[Path(path).name]).hexdigest()):
            self.assertEqual(wp8.verify_historical_source_identity(),
                             {name.replace('\\', '/'): digest for name, digest in expected.items()})
            current['Record.csv'] = record.replace(b'100,12', b'100,13')
            with self.assertRaisesRegex(RuntimeError, 'predictor identity mismatch'):
                wp8.verify_historical_source_identity()

    def test_csv_filter_before_value_conversion_and_forbidden_projection(self):
        source = ('Customer_ID,churn,rev_Mean,area\n'
                  '999,BAD_LABEL,BAD_TEST_FEATURE,BAD_AREA\n'
                  '4,1,12,IGNORED\n'
                  '2,0,NA,IGNORED\n'
                  '998,BAD_LABEL,BAD_CAL_FEATURE,BAD_AREA\n')
        with patch.object(Path, 'open', side_effect=lambda *a, **k: io.StringIO(source)):
            rows, order = wp8.filtered_source(wp8.OUT / '_synthetic.csv', {2, 4}, ['churn', 'rev_Mean'])
        self.assertEqual(order, [4, 2])
        self.assertEqual(set(rows), {2, 4})
        self.assertEqual(rows[4], dict(churn='1', rev_Mean='12'))
        self.assertNotIn('area', rows[2])
        frame = pd.DataFrame.from_records(list(rows.values()))
        frame['rev_Mean'] = pd.to_numeric(frame.rev_Mean.mask(frame.rev_Mean.isin(wp8.NA_TOKENS)), errors='raise')
        self.assertTrue(pd.isna(frame.rev_Mean.iloc[1]))
        with patch.object(Path, 'open', side_effect=lambda *a, **k: io.StringIO(source.replace('2,0', '4,0'))):
            with self.assertRaisesRegex(RuntimeError, 'duplicate'):
                wp8.filtered_source(wp8.OUT / '_synthetic.csv', {2, 4}, ['churn'])

    def test_exact_fold_seeds_order_and_inner_pairing(self):
        y = np.tile([0, 1], 37500)
        folds = wp8.outer_folds(y)
        self.assertEqual(len(folds), 10)
        for r in range(2):
            expected = list(StratifiedKFold(5, shuffle=True, random_state=20261028+r).split(np.zeros(75000), y))
            indices = []
            for f in range(5):
                fold = folds[r*5+f]
                train, test = expected[f]
                np.testing.assert_array_equal(fold.train, train)
                np.testing.assert_array_equal(fold.test, test)
                dev, cal = train_test_split(train, test_size=.2, stratify=y[train], random_state=20261028+1000+5*r+f)
                np.testing.assert_array_equal(fold.development, np.sort(dev))
                np.testing.assert_array_equal(fold.calibration, np.sort(cal))
                self.assertEqual([len(fold.train), len(fold.test), len(fold.development), len(fold.calibration)], [60000, 15000, 48000, 12000])
                inner = wp8.inner_folds(fold, y)
                expected_inner = StratifiedKFold(3, shuffle=True, random_state=20261028).split(np.zeros(48000), y[fold.development])
                for (tr, te), (etr, ete) in zip(inner, expected_inner):
                    np.testing.assert_array_equal(tr, fold.development[etr])
                    np.testing.assert_array_equal(te, fold.development[ete])
                    self.assertEqual(len(tr), 32000)
                    self.assertEqual(len(te), 16000)
                    self.assertFalse(np.intersect1d(tr, te).size)
                indices.extend(test)
            self.assertEqual(sorted(indices), list(range(75000)))
        self.assertEqual(wp8.indices_hash([1, 2, 3]), wp8.sha256(np.asarray([1, 2, 3], dtype='<i8').tobytes()).hexdigest())

    def test_import_inert_guard_first_and_fixed_parameters(self):
        tree = ast.parse(wp8.SCRIPT.read_text(encoding='utf-8'))
        first_import = next(node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom)))
        self.assertIsInstance(first_import, ast.Import)
        self.assertEqual(first_import.names[0].name, 'common')
        imports = [name.name for node in ast.walk(tree) if isinstance(node, ast.Import) for name in node.names]
        self.assertFalse(any(name.startswith(('v2_work', 'v1_frozen', 'workstream_d', 'analysis_pipeline')) for name in imports))
        self.assertEqual(wp8.LGBM_SPEC, dict(n_estimators=385, learning_rate=.03, num_leaves=31,
            min_child_samples=100, reg_lambda=12, subsample=.85, subsample_freq=1, colsample_bytree=.85,
            n_jobs=6, random_state=20261028, verbosity=-1, deterministic=True, force_col_wise=True))
        self.assertEqual(wp8.SIGMOID_SPEC, dict(C=1000, solver='lbfgs', max_iter=1000, random_state=20261028))
        self.assertNotIn('early_stopping', wp8.LGBM_SPEC)
        self.assertIs(common, wp8.common)

    def test_pool_record_order_train_then_validation(self):
        partitions = {8: 'validation', 5: 'train', 2: 'validation', 9: 'train'}
        np.testing.assert_array_equal(wp8.ordered_pool_ids([8, 5, 2, 9], partitions), [5, 9, 8, 2])

    def test_baseline_fold_pairing_rejects_ids_labels_indices_and_values(self):
        y = np.tile([0, 1], 37500)
        fold = wp8.outer_folds(y)[0]
        raw = pd.DataFrame({'totmrc_Mean': np.full(75000, 100.)})
        pool = wp8.Pool(raw, np.arange(1000, 76000), y)
        probability = np.linspace(.1, .9, 15000)
        prior = float(y[fold.calibration].mean())
        ps = wp8.sigmoid_probability(probability, 1.1, .03)
        pd_ = wp8.shift_probability(ps, prior)
        arrays = dict(Customer_ID=pool.ids[fold.test].copy(), y=y[fold.test].copy(),
            pool_index=fold.test.copy(), raw=probability, p_s=ps, p_d=pd_, value=np.full(15000, 100.),
            deployment_weight=wp8.deployment_weights(y[fold.test]), own_tail=pd_*100 >= 1.5, baseline_tail=pd_*100 >= 1.5)
        metric = dict(sample_prior=prior, calibration_slope=1.1, calibration_intercept=.03,
                      threshold=1.5, auc=wp8.roc_auc_score(y[fold.test], probability))
        recipe = dict(recipe=wp8.BASE_RECIPE, outer_training_value_limits=dict(median=100., p99=100.),
                      development_value_limits=dict(median=100., p99=100.))
        wp8.verify_baseline_pair(pool, fold, arrays, metric, recipe)
        for key in ('Customer_ID', 'y', 'pool_index', 'value'):
            bad = {name: value.copy() for name, value in arrays.items()}
            bad[key][0] += 1
            with self.assertRaises(RuntimeError):
                wp8.verify_baseline_pair(pool, fold, bad, metric, recipe)
        bad_recipe = dict(recipe=wp8.BASE_RECIPE, outer_training_value_limits=dict(median=101., p99=100.),
                          development_value_limits=dict(median=100., p99=100.))
        with self.assertRaisesRegex(RuntimeError, 'V limits'):
            wp8.verify_baseline_pair(pool, fold, arrays, metric, bad_recipe)


class SafetyReceiptsTest(unittest.TestCase):
    def test_prior_seal_required_and_mismatch_refused_without_writes(self):
        context = SimpleNamespace(signature={'code': 'fixed'}, binding='bound')
        with patch.object(Path, 'is_file', return_value=False):
            with self.assertRaisesRegex(RuntimeError, 'seal'):
                wp8.read_receipt(context)
        receipt = dict(signature=context.signature, signature_sha256='bound', outside_snapshot_sha256='hash',
                       provenance={}, status='SEALED_NO_FITS', fits_performed=0,
                       planned_classifier_fits=50, planned_sigmoid_fits=10)
        snapshot = dict(files={'a': {'sha256': 'x'}}, provenance={})
        with patch.object(Path, 'is_file', return_value=True), \
             patch.object(wp8, 'read_json', side_effect=lambda path: receipt if path == wp8.RECEIPT else snapshot), \
             patch.object(wp8.common, 'digest', return_value='hash'), \
             patch.object(wp8, 'check_provenance'), \
             patch.object(wp8.common, 'outside_snapshot', return_value=snapshot['files']):
            self.assertEqual(wp8.read_receipt(context), receipt)
            receipt['signature_sha256'] = 'changed'
            with self.assertRaisesRegex(RuntimeError, 'receipt mismatch'):
                wp8.read_receipt(context)

    def test_incomplete_cache_stops_never_refits(self):
        marker, prediction, started = wp8.cache_paths('r0_f0_inner0')
        for present in ({started}, {marker}, {prediction}, {started, prediction}, {marker, prediction}):
            with patch.object(Path, 'exists', side_effect=lambda path, p=present: path in p, autospec=True):
                with self.assertRaisesRegex(RuntimeError, 'incomplete/orphan'):
                    wp8.load_complete_cache(object(), 'r0_f0_inner0')
        with patch.object(Path, 'exists', return_value=False):
            self.assertIsNone(wp8.load_complete_cache(object(), 'r0_f0_inner0'))

    def test_provenance_task_seed_script_and_input_hashes(self):
        source = wp8.OUT / '_synthetic_input.npz'
        provenance = dict(script=wp8.SCRIPT.as_posix(), script_sha256='hash', seed=20261036,
            tags_used=['[E]', '[A]', '[R]'], python_version=sys.version, created_utc='2026-10-29T00:00:00+00:00',
            row_counts={'fit_count': 1}, input_files=[dict(path=source.as_posix(), present=True, sha256='hash')])
        with patch.object(Path, 'is_file', return_value=True), patch.object(wp8.common, 'digest', return_value='hash'):
            wp8.check_provenance({'provenance': provenance}, source)
            provenance['seed'] = 20261035
            with self.assertRaisesRegex(RuntimeError, 'provenance'):
                wp8.check_provenance({'provenance': provenance}, source)
            provenance['seed'] = 20261036
            provenance['input_files'][0]['sha256'] = 'changed'
            with self.assertRaisesRegex(RuntimeError, 'input hash'):
                wp8.check_provenance({'provenance': provenance}, source)

    def test_complete_cache_signature_hash_and_id_binding(self):
        tag = 'r0_f0_inner0'
        train, predict = np.array([0, 1, 2]), np.array([3, 4])
        pool = wp8.Pool(synthetic_raw(5), np.array([100, 200, 300, 400, 500]), np.array([0, 1, 0, 1, 0]))
        context = SimpleNamespace(pool=pool, binding='seal')
        signature = wp8.fit_signature(context, tag, 'classifier', train, predict)
        reference = wp8.fit_reference(pool.raw.iloc[train])
        metadata = dict(signature=signature, signature_sha256=wp8.signature_hash(signature), prediction_sha256='hash',
            fit_completed=True, fit_count=1, fit_started_utc='2026-10-29T01:00:00+00:00',
            converged=True, warnings=[], fitted_iterations=385, training_reference=reference, features=list(wp8.FEATURES))
        arrays = dict(Customer_ID=pool.ids[predict].copy(), y=pool.y[predict].copy(), pool_index=predict.copy(), raw=np.array([.2, .8]))
        with patch.object(Path, 'exists', return_value=True), \
             patch.object(wp8, 'check_provenance'), \
             patch.object(wp8, 'read_json', side_effect=lambda path: metadata if path != wp8.RECEIPT else {'provenance': {'created_utc': '2026-10-29T00:00:00+00:00'}}), \
             patch.object(Path, 'read_text', return_value=wp8.signature_hash(signature)), \
             patch.object(wp8.common, 'digest', return_value='hash'), \
             patch.object(wp8, 'arrays_at', return_value=arrays), \
             patch.object(wp8, 'plan', return_value={tag: ('classifier', train, predict)}):
            self.assertIsNotNone(wp8.load_complete_cache(context, tag, signature))
            wrong_signature = dict(signature, predict_ids_sha256='changed')
            with self.assertRaisesRegex(RuntimeError, 'signature mismatch'):
                wp8.load_complete_cache(context, tag, wrong_signature)
            metadata['prediction_sha256'] = 'changed'
            with self.assertRaisesRegex(RuntimeError, 'NPZ hash'):
                wp8.load_complete_cache(context, tag, signature)
            metadata['prediction_sha256'] = 'hash'
            arrays['Customer_ID'][0] += 1
            with self.assertRaisesRegex(RuntimeError, 'pairing'):
                wp8.load_complete_cache(context, tag, signature)


class MetricsAndBootstrapTest(unittest.TestCase):
    def test_fixed_numeric_tau_tail_losses_and_capture(self):
        y = np.array([0, 1, 0, 1])
        V = np.full(4, 100.)
        base = np.array([.01, .02, .03, .04])
        candidate = np.array([.018, .016, .025, .05])
        shared = base * V >= 1.711493684172072
        np.testing.assert_array_equal(shared, [False, True, True, True])
        cm = wp8.measure(y, candidate, candidate, candidate, V, shared)
        bm = wp8.measure(y, base, base, base, V, shared)
        self.assertAlmostEqual(cm['value_capture'], .5)
        self.assertAlmostEqual(bm['value_capture'], 1.)
        self.assertAlmostEqual(cm['contact_share'], .99)
        self.assertAlmostEqual(bm['contact_share'], .51)
        self.assertAlmostEqual(cm['baseline_tail_brier'], (.04*.984**2 + 1.96*.025**2 + .04*.95**2)/2.04)
        self.assertAlmostEqual(bm['baseline_tail_brier'], (.04*.98**2 + 1.96*.03**2 + .04*.96**2)/2.04)
        self.assertAlmostEqual(cm['own_tail_brier'], (1.96*.018**2 + 1.96*.025**2 + .04*.95**2)/3.96)
        self.assertAlmostEqual(cm['baseline_tail_logloss'], (-.04*np.log(.016) - 1.96*np.log(.975) - .04*np.log(.05))/2.04)
        self.assertAlmostEqual(cm['own_tail_logloss'], (-1.96*np.log(.982) - 1.96*np.log(.975) - .04*np.log(.05))/3.96)
        boundary = np.array([wp8.TAU/100, 0., 0., 0.])
        exact = wp8.measure(y, boundary, boundary, boundary, V, boundary*V >= wp8.TAU)
        self.assertEqual(exact['raw_contacts'], 1)
        self.assertAlmostEqual(exact['contact_share'], .49)
        empty = wp8.weighted_losses(y, candidate, wp8.deployment_weights(y), np.zeros(4, bool))
        self.assertTrue(all(np.isnan(v) for v in empty))

    def test_sigmoid_and_prior_shift_without_fit(self):
        raw = np.array([0., .2, .5, .8, 1.])
        ps = wp8.sigmoid_probability(raw, 1.2, -.1)
        expected = np.clip(expit(1.2 * logit(np.clip(raw, 1e-6, 1-1e-6)) - .1), 1e-6, 1-1e-6)
        np.testing.assert_array_equal(ps, expected)
        pd_ = wp8.shift_probability(ps, .49)
        odds = ps/(1-ps) * (.02/.98)/(.49/.51)
        np.testing.assert_allclose(pd_, odds/(1+odds), rtol=1e-12, atol=0)
        self.assertTrue(np.all(np.diff(ps) > 0))

    def test_deterministic_joint_bootstrap_reconstruction_and_envelope(self):
        vector = np.array([-.004, .008, .005, -.001, .006, .002, .01, -.002, .007, .003])
        matrix = np.c_[vector, 2*vector + .01]
        draws = wp8.bootstrap(matrix, draws=2048)
        repeated = wp8.bootstrap(matrix, draws=2048)
        for key in draws:
            np.testing.assert_array_equal(draws[key], repeated[key])
        rng = np.random.default_rng(20261036)
        rep = rng.integers(0, 2, size=(2048, 2))
        within = rng.integers(0, 5, size=(2048, 2, 5))
        hidx = (rep[:, :, None]*5 + within).reshape(2048, 10)
        iidx = rng.integers(0, 10, size=(2048, 10))
        np.testing.assert_array_equal(draws['hierarchical_indices'], hidx)
        np.testing.assert_array_equal(draws['iid_indices'], iidx)
        np.testing.assert_array_equal(draws['hierarchical'], matrix[hidx].mean(axis=1))
        np.testing.assert_array_equal(draws['iid'], matrix[iidx].mean(axis=1))
        np.testing.assert_allclose(draws['hierarchical'][:, 1], 2*draws['hierarchical'][:, 0]+.01, rtol=0, atol=1e-17)
        intervals = wp8.interval_summary(matrix, draws, names=('auc', 'value_capture'))
        for i, name in enumerate(('auc', 'value_capture')):
            se = np.sqrt(.35*np.var(matrix[:, i], ddof=1))
            corrected = matrix[:, i].mean() + np.array([-1, 1])*t.ppf(.975, 4)*se
            hierarchy = np.percentile(draws['hierarchical'][:, i], [2.5, 97.5], method='linear')
            np.testing.assert_array_equal(intervals[name]['corrected_t'], corrected)
            np.testing.assert_array_equal(intervals[name]['hierarchical'], hierarchy)
            self.assertEqual(intervals[name]['df'], 4)
            self.assertEqual(intervals[name]['conservative'], [min(corrected[0], hierarchy[0]), max(corrected[1], hierarchy[1])])
        bad = matrix.copy()
        bad[0, 0] = np.nan
        invalid = wp8.interval_summary(bad, wp8.bootstrap(bad, 100), names=('auc', 'value_capture'))
        self.assertFalse(invalid['auc']['complete'])
        self.assertIsNone(invalid['auc']['conservative'])

    def test_strict_preregistered_gates_and_all_four_upper_bounds(self):
        good = {name: dict(complete=True, mean=.004, conservative=[.001, .007]) for name in ('auc', 'value_capture')}
        good.update({name: dict(complete=True, mean=-.001, conservative=[-.002, 0.]) for name in wp8.TAIL_METRICS})
        self.assertTrue(wp8.promotion_gates(good, True, True)['passed'])
        good['auc']['mean'] = .003
        self.assertTrue(wp8.promotion_gates(good, True, True)['passed'])
        good['auc']['mean'] = np.nextafter(.003, 0)
        self.assertIn('mean_delta_auc_ge_0_003', wp8.promotion_gates(good, True, True)['failed_gates'])
        good['auc']['mean'] = .004
        for name in ('auc', 'value_capture'):
            previous = good[name]['conservative'][0]
            good[name]['conservative'][0] = 0.
            self.assertFalse(wp8.promotion_gates(good, True, True)['passed'])
            good[name]['conservative'][0] = previous
        good['value_capture']['mean'] = 0.
        self.assertFalse(wp8.promotion_gates(good, True, True)['passed'])
        good['value_capture']['mean'] = .004
        for name in wp8.TAIL_METRICS:
            good[name]['conservative'][1] = 1e-15
            self.assertIn(name + '_conservative_upper_le_0', wp8.promotion_gates(good, True, True)['failed_gates'])
            good[name]['conservative'][1] = 0.
        for complete, converged, protected in ((False, True, True), (True, False, True), (True, True, False)):
            self.assertFalse(wp8.promotion_gates(good, complete, converged, protected)['passed'])
        good['auc']['complete'] = False
        self.assertFalse(wp8.promotion_gates(good, True, True)['passed'])

    def test_independent_output_metric_formula_matches_synthetic(self):
        arrays = dict(y=np.array([0, 1, 0, 1]), V=np.full(4, 100.),
            raw=np.array([.018, .016, .025, .05]), p_s=np.array([.1, .3, .6, .9]),
            p_d=np.array([.018, .016, .025, .05]), baseline_raw=np.array([.01, .02, .03, .04]),
            baseline_p_s=np.array([.1, .2, .4, .8]), baseline_p_d=np.array([.01, .02, .03, .04]))
        shared = arrays['baseline_p_d'] * arrays['V'] >= wp8.TAU
        for baseline in (False, True):
            prefix = 'baseline_' if baseline else ''
            measured = wp8.measure(arrays['y'], arrays[prefix+'raw'], arrays[prefix+'p_s'], arrays[prefix+'p_d'], arrays['V'], shared)
            independent = wp8.independent_metrics(arrays, baseline)
            self.assertTrue(wp8.numerically_equal(measured, independent))

    def test_outside_diff_and_nonfinite_json_clean(self):
        before = {'a': dict(bytes=1, sha256='x'), 'b': dict(bytes=2, sha256='y')}
        after = {'a': dict(bytes=1, sha256='z'), 'c': dict(bytes=2, sha256='y')}
        delta = wp8.outside_diff(before, after)
        self.assertEqual(delta['added_outside'], ['c'])
        self.assertEqual(delta['removed_outside'], ['b'])
        self.assertEqual(delta['changed_outside'], ['a'])
        self.assertFalse(delta['passed'])
        self.assertEqual(json.dumps(wp8.clean(dict(x=np.nan, a=np.array([np.inf, 1.]))), allow_nan=False),
                         '{"x": null, "a": [null, 1.0]}')


@unittest.skipUnless(wp8.SUMMARY.is_file(), 'No completed WP8 output; no fit/seal is permitted by tests')
class ActualOutputTest(unittest.TestCase):
    def test_independent_actual_output_hashes_150k_ids_fits_bootstrap_and_protection(self):
        verified = wp8.verify_outputs()
        self.assertEqual(verified['status'], 'VERIFIED_READ_ONLY')
        self.assertEqual(verified['classifier_fits'], 50)
        self.assertEqual(verified['sigmoid_fits'], 10)
        self.assertEqual(verified['reused_baseline_caches'], 40)
        self.assertEqual(verified['repeated_oof_rows'], 150000)
        self.assertEqual(verified['unique_customers'], 75000)
        self.assertTrue(verified['no_new_test_look'])


if __name__ == '__main__':
    unittest.main()
