import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from common import ADDONS, write_json, verify_runtime

import ast
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
from scipy.optimize import brentq
from scipy.special import expit, logit
import wp5_labelshift as wp5


def expanded_em(scores, counts, tol=1e-13):
    rows = np.repeat(scores, counts)
    pi = wp5.SAMPLE_PRIOR
    for iteration in range(100_000):
        positive = (pi / wp5.SAMPLE_PRIOR) * rows
        negative = ((1 - pi) / (1 - wp5.SAMPLE_PRIOR)) * (1 - rows)
        updated = np.mean(positive / (positive + negative))
        if abs(updated - pi) < tol:
            return updated
        pi = updated
    raise AssertionError('Independent expanded EM did not converge')


class WP5Tests(unittest.TestCase):
    def test_syntax_and_worker_constraints(self):
        path = ADDONS / 'src/wp5_labelshift.py'
        tree = ast.parse(path.read_text(encoding='utf-8'))
        workers = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                   and node.name in ('simulate_replicate', 'bootstrap_batch', 'safeguarded_newton', 'count_em')]
        self.assertEqual(len(workers), 4)
        for function in workers:
            for node in ast.walk(function):
                self.assertFalse(isinstance(node, ast.BinOp) and isinstance(node.op, ast.MatMult))
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    self.assertNotIn(node.func.attr, ('dot', 'matmul', 'to_csv', 'write_text', 'open'))
        self.assertEqual(wp5.ORIGINAL_REPLICATES, 500)
        self.assertEqual(wp5.BOOTSTRAP_REPLICATES, 500)
        self.assertEqual(len(wp5.GRID), 20)

    def test_counted_em_matches_expanded_rows(self):
        scores = np.array([.18, .35, .55, .83])
        counts = np.array([19, 22, 17, 12], dtype=np.int64)
        actual, iterations, converged = wp5.count_em(wp5.score_likelihood_ratio(scores), counts, tol=1e-13, max_iter=100_000)
        self.assertTrue(converged)
        self.assertGreater(iterations, 1)
        self.assertAlmostEqual(actual, expanded_em(scores, counts), places=11)

    def test_newton_matches_converged_em_and_boundaries(self):
        scores = np.array([.15, .3, .7, .9])
        matrix = np.array([[20, 18, 25, 15], [12, 24, 19, 20], [30, 5, 18, 22]], dtype=np.int64)
        ratio = wp5.score_likelihood_ratio(scores)
        estimates, _, flags, _ = wp5.safeguarded_newton(ratio - 1, matrix, .5, tol=1e-12)
        for counts, estimate, flag in zip(matrix, estimates, flags):
            self.assertEqual(flag, wp5.SOLVER_INTERIOR)
            self.assertAlmostEqual(estimate, expanded_em(scores, counts), places=9)
        a = np.array([-.6, .8])
        counts = np.array([[9, 0], [0, 9], [5, 4]], dtype=np.int64)
        estimates, _, flags, _ = wp5.safeguarded_newton(a, counts, .5)
        self.assertEqual(estimates[0], 0)
        self.assertEqual(estimates[1], 1)
        self.assertEqual(flags[0], wp5.SOLVER_LOWER_KKT)
        self.assertEqual(flags[1], wp5.SOLVER_UPPER_KKT)
        _, _, flat_flags, _ = wp5.safeguarded_newton(np.zeros(2), counts, .5)
        self.assertTrue(np.all(flat_flags == wp5.SOLVER_FLAT))

    def test_exact_multinomial_bootstrap_against_independent_roots(self):
        counts = np.array([30, 18, 25, 20], dtype=np.int64)
        a = np.array([-.7, -.25, .4, 2.0])
        actual, _, flags, _, interval = wp5.bootstrap_batch(np.random.default_rng(567), a, counts, int(counts.sum()), .3)
        draws = np.random.default_rng(567).multinomial(int(counts.sum()), counts / counts.sum(), size=500)
        expected = []
        for row in draws:
            def derivative(pi):
                return np.sum(row * a / (1 + pi * a))
            if derivative(0) <= 0:
                expected.append(0.)
            elif derivative(1) >= 0:
                expected.append(1.)
            else:
                expected.append(brentq(derivative, 0, 1, xtol=1e-13))
        np.testing.assert_allclose(actual, expected, rtol=0, atol=2e-8)
        self.assertTrue(np.all(flags <= wp5.SOLVER_UPPER_KKT))
        np.testing.assert_array_equal(interval, np.quantile(actual, [.025, .975]))

    def test_heldout_scores_never_enter_fit(self):
        raw = expit(np.linspace(-2, 2, 50))
        labels = np.tile([0, 1], 25)
        frame = pd.DataFrame({'Customer_ID': np.arange(50), 'y': labels, 'p_raw': raw})
        assignment = wp5.stratified_fold_assignment(labels)
        calls = []
        def fake_minimize(function, start, args, **kwargs):
            calls.append((args[0].copy(), args[1].copy()))
            return SimpleNamespace(success=True, x=np.array([1.2, .1]), fun=2., nit=1,
                                   jac=np.zeros(2), message='synthetic test double')
        with patch.object(wp5, 'minimize', side_effect=fake_minimize), patch.object(wp5, 'CALIBRATION_ROWS', 50):
            output, parameters = wp5.fold_sigmoids(frame)
            wp5.validate_folded(output, frame, parameters)
        self.assertEqual(len(calls), 5)
        for fold, (x, y) in enumerate(calls):
            np.testing.assert_array_equal(x, logit(raw[assignment != fold]))
            np.testing.assert_array_equal(y, labels[assignment != fold])
            self.assertTrue(set(parameters[fold]['training_ids']).isdisjoint(parameters[fold]['heldout_ids']))
            expected_prior = labels[assignment != fold].mean()
            self.assertEqual(parameters[fold]['training_prevalence'], expected_prior)

    def test_seed_schedule_independence_and_pure_replay(self):
        scores = np.linspace(.12, .91, 40)
        wp5.initialize_worker(scores, np.arange(20, 40), np.arange(20))
        jobs = [(0, i, .02, 100) for i in range(3)]
        serial = {job[1]: wp5.simulate_replicate(job) for job in jobs}
        with ThreadPoolExecutor(max_workers=3) as executor:
            parallel = {row['replicate']: row for row in executor.map(wp5.simulate_replicate, reversed(jobs))}
        for index in serial:
            for key in serial[index]:
                np.testing.assert_array_equal(serial[index][key], parallel[index][key])
        functions, audit = wp5.safe_v2_functions()
        self.assertEqual(len(functions), 6)
        self.assertTrue(all(not item['top_level_imports_executed'] for item in audit))
        data = pd.DataFrame({'p_s': [.3, .65, .4, .8], 'y': [0, 1, 0, 1], 'value': [20., 30., 40., 50.]})
        thresholds = functions['fit_thresholds'](data)
        selected = functions['scores'](data)['bayes'] >= thresholds['bayes']
        measured = functions['measure'](data, selected)
        self.assertTrue(np.isfinite(measured['net']))
        self.assertFalse(any(name.startswith(('sklearn', 'joblib', 'lightgbm')) for name in sys.modules))


if __name__ == '__main__':
    verify_runtime()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(WP5Tests))
    write_json('results/wp5_tests.json', dict(passed=result.wasSuccessful(), tests=result.testsRun,
               failures=len(result.failures), errors=len(result.errors), synthetic_only=True,
               real_sigmoid_fits=0, model_fits=0), __file__, 5,
               [ADDONS / 'src/wp5_labelshift.py'])
    raise SystemExit(0 if result.wasSuccessful() else 1)
