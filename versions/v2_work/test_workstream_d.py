"""Focused synthetic unit tests for D; no real-data boosting fits or locked-test reads.

Invoke this file with the shared Python 3.11 interpreter. The separate
workstream_d.py --smoke command exercises real model integrations on an original
non-test subset with every decision disabled. Neither command is run on import.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
from scipy import sparse
from scipy.special import expit

try:
    from . import workstream_d as d
except ImportError:
    import workstream_d as d


def synthetic_schema(n=120):
    """Only the frozen column manifest is read, never the customer CSVs."""
    manifest = json.loads((d.common.ROOT / "v1_frozen/analysis_outputs/feature_manifest.json").read_text(
        encoding="utf-8"))
    frame = pd.DataFrame({c: 1 + np.arange(n, dtype=float) / 10 for c in manifest["features"]})
    for c in manifest["excluded_features"]:
        frame[c] = 0
    for c in manifest["categorical_features"]:
        frame[c] = "known"
    frame["Customer_ID"] = np.arange(n) + 1000
    frame["churn"] = np.arange(n) % 2
    frame["months"] = 1 + np.arange(n) % 24
    frame["hnd_price"] = (np.arange(n) % 3) * 50.0
    frame["totmrc_Mean"] = 10 + np.arange(n) % 17
    frame["area"] = "market_A"
    frame["asl_flag"] = "N"
    return frame


class SplitTests(unittest.TestCase):
    def test_exact_original_pool_and_forbidden_overlap(self):
        frame = pd.DataFrame({"Customer_ID": np.arange(100000), "churn": np.arange(100000) % 2})
        splits = {"train": np.arange(60000), "validation": np.arange(60000, 75000),
                  "calibration_policy": np.arange(75000, 85000), "test": np.arange(85000, 100000)}
        pool = d.non_test_pool(frame, splits)
        self.assertEqual(len(pool), 75000)
        self.assertLess(pool.Customer_ID.max(), 75000)
        self.assertEqual(pool._original_partition.value_counts().to_dict(),
                         {"train": 60000, "validation": 15000})
        bad = {key: value.copy() for key, value in splits.items()}
        bad["validation"][0] = 85000
        with self.assertRaises(AssertionError):
            d.non_test_pool(frame, bad)

    def test_two_repeats_five_stratified_folds_and_nested_disjointness(self):
        y = np.arange(75000) % 2
        folds = list(d.outer_folds(y))
        self.assertEqual(len(folds), 10)
        for repeat in range(2):
            coverage = np.zeros(len(y), dtype=int)
            for fold in [f for f in folds if f.repeat == repeat]:
                self.assertEqual((len(fold.train), len(fold.test)), (60000, 15000))
                self.assertEqual((len(fold.development), len(fold.calibration)), (48000, 12000))
                self.assertEqual(np.intersect1d(fold.train, fold.test).size, 0)
                self.assertEqual(np.intersect1d(fold.development, fold.calibration).size, 0)
                self.assertEqual(set(np.r_[fold.development, fold.calibration]), set(fold.train))
                self.assertAlmostEqual(y[fold.test].mean(), .5)
                coverage[fold.test] += 1
            np.testing.assert_array_equal(coverage, np.ones(len(y), dtype=int))
        again = list(d.outer_folds(y))
        for first, second in zip(folds, again):
            np.testing.assert_array_equal(first.test, second.test)
            np.testing.assert_array_equal(first.calibration, second.calibration)
        self.assertFalse(np.array_equal(folds[0].test, folds[5].test))

    def test_stratified_learning_prefixes_are_nested(self):
        y = np.arange(60000) % 2
        order = d._stratified_order(np.arange(len(y)), y, d.SEED)
        for n in (10000, 25000, 50000, 60000):
            self.assertEqual(len(np.unique(order[:n])), n)
            self.assertAlmostEqual(y[order[:n]].mean(), .5, places=3)
        self.assertTrue(set(order[:10000]) < set(order[:25000]))


class FeatureTests(unittest.TestCase):
    def setUp(self):
        self.frame = synthetic_schema()
        self.train, self.heldout = np.arange(90), np.arange(90, 120)

    def test_baseline_exactly_87_and_categories_fit_training_only(self):
        self.frame.loc[self.heldout, "new_cell"] = "never_seen_in_training"
        X_train, X_hold, cats, metadata = d.design(self.frame, self.train, self.heldout, d.Recipe())
        self.assertEqual(X_train.shape[1], 87)
        self.assertEqual(len(cats), 4)
        self.assertNotIn("never_seen_in_training", metadata["category_vocabularies"]["new_cell"])
        self.assertTrue(X_hold.new_cell.isna().all())
        self.assertFalse({"asl_flag", "area", "Customer_ID", "churn"}.intersection(X_train.columns))

    def test_all_available_groups_and_explicit_range_rejection(self):
        for group in d.AVAILABLE_GROUPS:
            X_train, _, _, metadata = d.design(self.frame, self.train, self.heldout,
                                              d.Recipe(groups=(group,)))
            self.assertGreater(X_train.shape[1], 87)
            self.assertFalse({"asl_flag", "area"}.intersection(metadata["features"]))
        self.assertEqual(len(d.GROUPS), 6)
        self.assertEqual(d.GROUP_NOTES["g2_range"]["status"], "unavailable")
        with self.assertRaises(ValueError):
            d.design(self.frame, self.train, self.heldout, d.Recipe(groups=("g2_range",)))

    def test_outer_targets_do_not_affect_training_encoding_or_transform_statistics(self):
        recipe = d.Recipe(groups=("g5_equipment_cycle", "g6_tenure_pricing"))
        train, heldout, _, metadata = d.design(self.frame, self.train, self.heldout, recipe)
        changed = self.frame.copy()
        changed.loc[self.heldout, "churn"] = 1 - changed.loc[self.heldout, "churn"]
        train2, heldout2, _, metadata2 = d.design(changed, self.train, self.heldout, recipe)
        pd.testing.assert_frame_equal(train, train2)
        pd.testing.assert_frame_equal(heldout, heldout2)
        self.assertEqual(d._clean(metadata), d._clean(metadata2))

    def test_unique_price_training_values_are_oof_not_in_sample(self):
        y = np.arange(120) % 2
        keys = pd.Series([f"unique_{i}" for i in range(len(y))])
        encoded = d.oof_m_estimate(keys, y)
        # Every price is unseen in its fitting fold; fallback comes from inner train.
        np.testing.assert_allclose(encoded, .5)
        mapping, _ = d.m_estimate_map(keys, y)
        in_sample = keys.map(mapping).to_numpy()
        self.assertTrue(np.all(np.abs(encoded - in_sample) > .001))

    def test_tenure_quantiles_and_medians_ignore_extreme_outer_prices(self):
        _, metadata = d.tenure_pricing(self.frame, self.train)
        changed = self.frame.copy()
        changed.loc[self.heldout, "totmrc_Mean"] = 1e12
        changed.loc[self.heldout, "months"] = 1e9
        _, metadata2 = d.tenure_pricing(changed, self.train)
        self.assertEqual(d._clean(metadata), d._clean(metadata2))

    def test_sensitive_attributes_only_in_explicit_design_ceiling(self):
        X, _, cats, _ = d.design(self.frame, self.train, self.heldout, d.Recipe(sensitive=True))
        self.assertEqual(X.shape[1], 89)
        self.assertTrue({"area", "asl_flag"}.issubset(cats))
        families = d.feature_families([c for c in X if c not in ("area", "asl_flag")])
        flat = [c for columns in families.values() for c in columns]
        self.assertEqual(len(flat), 87)
        self.assertEqual(len(set(flat)), 87)

    def test_quantile_splines_handle_constants_tied_quantiles_and_outer_extremes(self):
        X = np.c_[np.zeros(100), np.arange(100) % 2, np.linspace(0, 10, 100)]
        transformer = d.TrainQuantileSplines(n_knots=5).fit(X)
        knots = [array.copy() for array in transformer.quantile_knots_]
        output = transformer.transform(np.array([[999.0, 999.0, 1e9], [0.0, 0.0, -1e9]]))
        self.assertTrue(sparse.issparse(output))
        self.assertTrue(np.isfinite(output.data).all())
        for before, after in zip(knots, transformer.quantile_knots_):
            np.testing.assert_array_equal(before, after)
        self.assertIsNone(transformer.transformers_[0])
        self.assertEqual(len(transformer.quantile_knots_[1]), 3)

    def test_spline_imputer_and_one_hot_fit_training_only(self):
        train = pd.DataFrame({"amount": [1.0, 2.0, np.nan, 4.0] * 10,
                              "category": ["known"] * 40})
        heldout = pd.DataFrame({"amount": [1e12, np.nan], "category": ["unseen", "unseen"]})
        pipeline = d.spline_pipeline(train, ["category"], d.model_spec("spline_logistic"))
        preprocessing = pipeline.named_steps["preprocessing"].fit(train)
        numeric = preprocessing.named_transformers_["numeric"]
        self.assertEqual(numeric.named_steps["imputer"].statistics_[0], 2.0)
        self.assertEqual(preprocessing.named_transformers_["category"].categories_[0].tolist(), ["known"])
        output = preprocessing.transform(heldout)
        self.assertTrue(np.isfinite(output.data).all())
        self.assertEqual(numeric.named_steps["imputer"].statistics_[0], 2.0)


class StatisticsAndPolicyTests(unittest.TestCase):
    def test_corrected_interval_is_not_iid_and_uses_conservative_df(self):
        delta = np.linspace(.001, .003, 10)
        result = d.corrected_interval(delta, .25)
        expected = np.sqrt((.1 + .25) * np.var(delta, ddof=1))
        self.assertAlmostEqual(result["corrected_se"], expected)
        self.assertEqual(result["df"], 4)
        self.assertGreater(result["corrected_se"], np.std(delta, ddof=1) / np.sqrt(10))
        self.assertFalse(d.corrected_interval([0, np.nan], [.25, .25])["complete"])

    def test_blend_weights_are_nonnegative_sum_one_and_deterministic(self):
        y = np.arange(120) % 2
        strong = np.where(y, .8, .2)
        weak = np.full(len(y), .5)
        probabilities = np.c_[strong, weak, 1 - strong, weak]
        weights, metadata = d.fit_blend(probabilities, y)
        weights2, _ = d.fit_blend(probabilities, y)
        self.assertTrue(metadata["success"])
        self.assertGreater(weights[0], .99)
        self.assertGreaterEqual(weights.min(), 0)
        self.assertAlmostEqual(weights.sum(), 1)
        np.testing.assert_array_equal(weights, weights2)
        self.assertTrue(np.isfinite(d.blend_predict(probabilities, weights)).all())

    def test_threshold_depends_on_inner_calibration_not_outer_scores(self):
        y_cal = np.arange(120) % 2
        raw_cal = .15 + .7 * y_cal
        value_cal = np.linspace(10, 100, 120)
        first = d.calibrated_predictions(raw_cal, y_cal, np.array([.2, .8]), value_cal, np.array([10, 100]))
        second = d.calibrated_predictions(raw_cal, y_cal, np.array([.99, .01]), value_cal, np.array([1e6, 1]))
        self.assertEqual(first["threshold"], second["threshold"])
        self.assertEqual(first["sample_risk_threshold"], second["sample_risk_threshold"])
        self.assertEqual(first["sample_prior"], .5)

    def test_weighted_losses_use_weights_and_common_baseline_tail(self):
        y, p, w = np.array([0, 1, 1]), np.array([.1, .6, .9]), np.array([10, 1, 1])
        brier, _ = d.weighted_losses(y, p, w, np.array([True, True, False]))
        self.assertAlmostEqual(brier, (10 * .01 + .16) / 11)
        empty, _ = d.weighted_losses(y, p, w, np.zeros(3, bool))
        self.assertTrue(np.isnan(empty))

    @staticmethod
    def gate_fixture(name="nested_blend", value_gain=.01):
        records = [dict(candidate=name, repeat=r, fold=f, converged=True,
                        sensitive_diagnostic=False) for r in range(2) for f in range(5)]
        intervals = []
        for metric, gain in (("auc", .002), ("baseline_tail_brier", -.001),
                             ("baseline_tail_logloss", -.001), ("own_tail_brier", -.001),
                             ("own_tail_logloss", -.001), ("weighted_value_capture", value_gain)):
            intervals.append(dict(candidate=name, metric=metric,
                                  **d.corrected_interval(np.full(10, gain), .25)))
        return intervals, records

    def test_gate_d_and_smoke_never_promotes(self):
        intervals, records = self.gate_fixture()
        self.assertTrue(d.gate_tables(intervals, records)[0]["pass_gate_d"])
        smoke_gate = d.gate_tables(intervals, records, smoke=True)[0]
        self.assertFalse(smoke_gate["pass_gate_d"])
        self.assertFalse(smoke_gate["decision_allowed"])
        degraded = [row.copy() for row in intervals]
        next(row for row in degraded if row["metric"] == "baseline_tail_logloss")["upper"] = .001
        self.assertFalse(d.gate_tables(degraded, records)[0]["pass_gate_d"])
        records[0]["converged"] = False
        self.assertFalse(d.gate_tables(intervals, records)[0]["pass_gate_d"])

    def test_weighted_challenger_also_requires_positive_value_capture(self):
        intervals, records = self.gate_fixture("nested_value_weighted_lgbm", value_gain=-.01)
        gate = d.gate_tables(intervals, records)[0]
        self.assertTrue(gate["auc_gate"])
        self.assertFalse(gate["value_gate"])
        self.assertFalse(gate["pass_gate_d"])

    def test_sensitive_ceiling_is_ineligible_even_with_positive_metrics(self):
        intervals, records = self.gate_fixture("diagnostic_ceiling_asl_area")
        for row in records:
            row["sensitive_diagnostic"] = True
        gate = d.gate_tables(intervals, records)[0]
        self.assertFalse(gate["eligible"])
        self.assertFalse(gate["pass_gate_d"])

    def test_frozen_baseline_budget_and_smoke_budget_are_separate(self):
        full = d.model_spec("lgbm")
        smoke = d.model_spec("lgbm", smoke=True)
        self.assertEqual((full["n_estimators"], full["num_leaves"], full["n_jobs"]), (385, 31, 6))
        self.assertEqual(full["random_state"], 20261028)
        self.assertEqual(smoke["n_estimators"], 8)
        self.assertEqual(d.MODEL_SPECS["lgbm"]["n_estimators"], 385)


class RecoveryTests(unittest.TestCase):
    def test_transient_windows_reader_lock_preserves_atomic_replace(self):
        with tempfile.TemporaryDirectory(dir=d.common.WORK) as temporary:
            store = d.Artifacts(temporary)
            source = store.path('incoming.json')
            target = store.path('target.json')
            source.write_text('{"new":true}', encoding='utf-8')
            target.write_text('{"old":true}', encoding='utf-8')
            locked = PermissionError('temporary reader lock')
            locked.winerror = 5
            real_replace = d.os.replace
            calls = []
            def replace(incoming, destination):
                calls.append((incoming, destination))
                if len(calls) == 1:
                    raise locked
                real_replace(incoming, destination)
            with patch.object(d.os, 'replace', side_effect=replace), patch.object(d.time, 'sleep') as pause:
                store.replace(source, target)
            self.assertEqual(len(calls), 2)
            self.assertEqual(json.loads(target.read_text(encoding='utf-8')), {'new': True})
            pause.assert_called_once_with(.02)

    def test_atomic_artifacts_resume_binding_and_path_guard(self):
        with tempfile.TemporaryDirectory(dir=d.common.WORK) as temporary:
            store = d.Artifacts(temporary)
            store.bind({"smoke": True, "input_hash": "same"})
            store.bind({"smoke": True, "input_hash": "same"})
            with self.assertRaises(RuntimeError):
                store.bind({"smoke": False, "input_hash": "different"})
            with self.assertRaises(ValueError):
                store.json("../escape.json", {})
            store.table("folds/synthetic", [dict(auc=.7, decision_allowed=False)])
            self.assertTrue(store.path("folds/synthetic.csv").exists())
            self.assertEqual(store.read_json("folds/synthetic.json")[0]["auc"], .7)
            self.assertFalse(list(Path(temporary).rglob("*.tmp")))

    def test_completed_fit_is_reused_without_training_again(self):
        class FakeLGBM:
            fits = 0

            def __init__(self, **parameters):
                self.parameters = parameters

            def fit(self, X, y):
                type(self).fits += 1
                return self

            def predict_proba(self, X):
                p = expit(X.iloc[:, 0].to_numpy())
                return np.c_[1 - p, p]

        frame = pd.DataFrame({"Customer_ID": np.arange(30), "churn": np.arange(30) % 2})

        def fake_design(data, train, predict, recipe):
            X = pd.DataFrame({"x": np.arange(len(data)) / 30})
            metadata = dict(base_features=["x"], category_vocabularies={},
                            feature_statistics={}, features=["x"], categorical_features=[])
            return X.iloc[train], X.iloc[predict], [], metadata

        with tempfile.TemporaryDirectory(dir=d.common.WORK) as temporary:
            runner = d.Runner(frame, d.Artifacts(temporary), smoke=True)
            with patch.object(d, "design", side_effect=fake_design), patch.dict(
                    sys.modules, {"lightgbm": types.SimpleNamespace(LGBMClassifier=FakeLGBM)}):
                first, _ = runner.fit(np.arange(20), np.arange(20, 30), d.Recipe(), "unit")
                second, _ = runner.fit(np.arange(20), np.arange(20, 30), d.Recipe(), "unit_resume")
            self.assertEqual(FakeLGBM.fits, 1)
            self.assertEqual((runner.new_fits, runner.cache_hits), (1, 1))
            np.testing.assert_array_equal(first["raw"], second["raw"])
            with self.assertRaises(AssertionError):
                runner.fit(np.arange(20), np.arange(10), d.Recipe(), "bad_overlap")
            with self.assertRaises(AssertionError):
                runner.fit(np.arange(20), np.arange(20, 30), d.Recipe(sensitive=True), "deployable")


if __name__ == "__main__":
    d.validate_environment()
    unittest.main()
