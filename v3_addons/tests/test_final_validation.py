import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from common import ADDONS, ROOT, SEED, audit_boundary, digest, file_info, stored_constants, verify_runtime, write_json
from wp7_handback import deck_text, handback, proposal

import csv
import json
import os
import unittest

import numpy as np
import pandas as pd
from scipy import integrate, special, stats

NAMES = ('inventory', 'wp1_power', 'wp2_evsi', 'wp3_roi_band', 'wp4_protocol', 'wp5_label_shift', 'wp6_citations')
RESULTS = {}
HASHES = {}


def current_hash(path):
    path = Path(path).resolve()
    if path not in HASHES:
        HASHES[path] = digest(path)
    return HASHES[path]


class FinalValidation(unittest.TestCase):
    def assert_receipt(self, receipt):
        path = Path(receipt['path'])
        self.assertTrue(path.is_file(), str(path))
        self.assertEqual(path.stat().st_size, receipt['size'], str(path))
        self.assertEqual(current_hash(path), receipt['sha256'], str(path))

    def test_provenance_and_artifact_bindings(self):
        paths = [ADDONS / f'results/{name}.json' for name in NAMES]
        paths += [ADDONS / f'results/wp{i}_tests.json' for i in (1, 2, 5)]
        paths += [ADDONS / 'results/wp5_calibration_oof.json']
        paths += [ADDONS / f'results/wp5_grid_{i:02d}.json' for i in range(20)]
        for path in paths:
            body = json.loads(path.read_text(encoding='utf-8'))
            provenance = body['provenance']
            for key in ('script', 'seed', 'python_version', 'input_files', 'created_utc', 'row_counts', 'tags_used'):
                self.assertIn(key, provenance, str(path))
            self.assertEqual(current_hash(provenance['script']), provenance['script_sha256'])
            self.assertTrue(all(1 <= pool['num_threads'] <= 6 for pool in provenance['runtime_pools']))
            for receipt in provenance['input_files']:
                if receipt.get('present'):
                    self.assert_receipt(receipt)
            for receipt in body.get('artifacts', []):
                self.assert_receipt(receipt)
            if 'artifact' in body:
                self.assert_receipt(body['artifact'])
        for index, name in enumerate(NAMES):
            allowed = ('DONE', 'PARTIAL', 'DONE_WITH_ORACLE_CAVEAT') if index == 1 else ('DONE', 'PARTIAL')
            self.assertIn(RESULTS[name]['status'], allowed)

    def test_saved_implementation_tests(self):
        for index, count in ((1, 5), (2, 4), (5, 6)):
            receipt = json.loads((ADDONS / f'results/wp{index}_tests.json').read_text(encoding='utf-8'))
            self.assertEqual(receipt['tests'], count)
            self.assertEqual(receipt['failures'], 0)
            self.assertEqual(receipt['errors'], 0)
            self.assertTrue(receipt.get('passed', receipt.get('status') == 'passed'))

    def test_wp1_cached_power_and_capacity(self):
        body = RESULTS['wp1_power']
        rows = body['power_rows']
        self.assertEqual(len(rows), 864)
        self.assertEqual(len(body['capacity_mde']), 8)
        self.assertTrue(body['acceptance']['reference_first_grid_matches'])
        with np.load(ADDONS / 'results/wp1_simulation_samples.npz', allow_pickle=False) as saved:
            self.assertEqual(len(saved.files), 288)
            for row in rows:
                key = f'n{row["n_per_arm"]}_g{round(row["gamma"] * 100):02d}_{row["method"]}'
                pairs = saved[key]
                self.assertEqual(pairs.shape, (1000, 2))
                self.assertTrue(np.isfinite(pairs).all())
                se = pairs[:, 1] * np.sqrt(row['deff'])
                power = float(np.mean(pairs[:, 0] > stats.norm.ppf(.975) * se))
                self.assertAlmostEqual(power, row['effect_power'], places=14)
                self.assertEqual(row['is_observable'], not row['method'].endswith('literal_oracle'))
                if row['method'] != 'E1_churn':
                    power = float(np.mean(pairs[:, 0] - 1 > stats.norm.ppf(.975) * se))
                    self.assertAlmostEqual(power, row['profit_power'], places=14)
                if row['gamma'] == 0 and row['is_observable']:
                    self.assertLessEqual(row['effect_power'], .055)
        expected = {5000: ((.198, .026), (.429, .079), (.597, .199), (.936, .607)),
                    7872: ((.275, .021), (.599, .115), (.786, .279), (.993, .798))}
        for n, pairs in expected.items():
            subset = sorted((row for row in body['capacity_mde'] if row['n_per_arm'] == n), key=lambda row: row['gamma'])
            np.testing.assert_allclose([(row['effect_power'], row['profit_power']) for row in subset], pairs, atol=1e-14)
            self.assertTrue(all(row['profit_gamma_mde_80_interpolated'] is None for row in subset))

    def test_wp2_evsi_and_decisions(self):
        body = RESULTS['wp2_evsi']
        self.assertEqual(len(body['scenarios']), 6)
        self.assertTrue(all(all(checks.values()) for checks in body['acceptance'].values()))
        for row in body['scenarios']:
            self.assertGreaterEqual(row['pilots'], 3000)
            self.assertTrue(all(size >= 200 for size in row['grid_size']))
            self.assertGreaterEqual(row['evsi_per_cohort'], 0)
            self.assertLessEqual(row['evsi_per_cohort'], row['evpi'])
            if row['n_per_arm'] == 1_000_000:
                self.assertLessEqual(row['evpi'] - row['evsi_per_cohort'], max(5., .05 * row['evpi']))
        frame = pd.read_csv(ADDONS / 'results/wp2_decision_quality.csv')
        self.assertEqual(len(frame), 72)
        np.testing.assert_allclose(frame[['p_scale', 'p_extend', 'p_stop']].sum(axis=1), 1., atol=1e-14)
        self.assertTrue(frame.loc[frame.ambiguity_zone, 'p_wrong_outside_ambiguity'].isna().all())
        target = frame.loc[frame.n_per_arm.eq(7872) & frame.gamma.eq(.2) & frame.deff.eq(1.1)]
        self.assertEqual(len(target), 1)
        np.testing.assert_allclose(target[['p_scale', 'p_extend', 'p_stop']].to_numpy(), [[.076, .919, .005]], atol=1e-14)

    def test_wp3_independent_closed_forms_and_curve(self):
        body = RESULTS['wp3_roi_band']
        self.assertEqual(len(body['acceptance']), 90)
        self.assertTrue(all(check['passed'] for check in body['acceptance'].values()))
        constants = stored_constants()
        G, K = constants['G'], constants['K']
        g = K / G
        for row in body['priors']:
            a, b = row['a'], row['b']
            self.assertGreaterEqual(row['draws'], 1_000_000)
            d = stats.beta(a, b)
            eplus = integrate.quad(lambda x: (x - g) * d.pdf(x), g, 1, epsabs=1e-12)[0]
            expected = dict(p_positive=special.betaincc(a, b, g), expected_net=G * a / (a + b) - K,
                            net_5pct=G * d.ppf(.05) - K, evpi_per_cohort=G * eplus - max(0., G * a / (a + b) - K))
            for key, value in expected.items():
                self.assertAlmostEqual(row['closed_form'][key], value, delta=1e-8)
        self.assertEqual(len(pd.read_csv(ADDONS / 'results/wp3_net_curve.csv')), 480)
        self.assertFalse(body['budget_optimized'])
        self.assertFalse(body['prospective_policy_promoted'])

    def test_wp5_complete_grid_statistics_and_status(self):
        body = RESULTS['wp5_label_shift']
        self.assertTrue(body['computation_complete'])
        self.assertEqual(body['simulation']['original_batches'], 10_000)
        self.assertEqual(body['simulation']['bootstrap_fits'], 5_000_000)
        self.assertEqual(body['calibration']['new_sigmoid_fits'], 5)
        self.assertEqual(body['calibration']['new_base_model_fits'], 0)
        self.assertEqual(body['numerical_output_counts']['test_score_or_outcome_rows_loaded'], 0)
        raw = pd.read_csv(ADDONS / 'results/wp5_label_shift_raw.csv')
        self.assertEqual(len(raw), 10_000)
        self.assertFalse(raw.duplicated(['grid_index', 'replicate']).any())
        self.assertEqual(len(body['grid_summary']), 20)
        for row in body['grid_summary']:
            index, pi = row['grid_index'], row['true_prior']
            receipt = json.loads((ADDONS / f'results/wp5_grid_{index:02d}.json').read_text(encoding='utf-8'))
            self.assertTrue(receipt['computation_complete'])
            self.assertEqual(receipt['identity']['folded_score_sha256'], body['identity']['folded_score_sha256'])
            with np.load(ADDONS / f'results/wp5_grid_{index:02d}.npz', allow_pickle=False) as saved:
                estimates, boots = saved['original_estimates'], saved['bootestimates']
                self.assertEqual(estimates.shape, (500,))
                self.assertEqual(boots.shape, (500, 500))
                self.assertTrue(np.isfinite(boots).all())
                np.testing.assert_array_equal(saved['replicate_ids'], np.arange(500))
                interval = np.quantile(boots, (.025, .975), axis=1, method='linear').T
                np.testing.assert_array_equal(interval, saved['intervals'])
                errors = estimates - pi
                self.assertAlmostEqual(row['bias'], float(errors.mean()), places=14)
                self.assertAlmostEqual(row['median_error'], float(np.median(errors)), places=14)
                self.assertAlmostEqual(row['rmse'], float(np.sqrt(np.mean(errors ** 2))), places=14)
                coverage = ((interval[:, 0] <= pi) & (pi <= interval[:, 1])).mean()
                self.assertAlmostEqual(row['coverage_95_generating_prior'], coverage, places=14)
                self.assertEqual(row['converged_originals'], int(saved['convergence'].sum()))
                self.assertEqual(row['bootstrap_failures'], int(np.count_nonzero(saved['solverflags'] >= 3)))
        accepted = all(check['passed'] for check in body['acceptance_checks'].values())
        self.assertEqual(body['statistical_acceptance'], accepted)
        self.assertEqual(body['status'], 'DONE' if accepted else 'PARTIAL')
        self.assertFalse(body['m5']['full_text_formula_verified'])
        self.assertFalse(body['trigger']['live_policy_changed'])

    def test_wp4_wp6_and_readonly_proposal(self):
        self.assertTrue(all(RESULTS['wp6_citations']['acceptance'].values()))
        with (ADDONS / 'results/wp6_citation_register.csv').open(encoding='utf-8', newline='') as stream:
            register = list(csv.DictReader(stream))
        self.assertEqual(len(register), 7)
        self.assertEqual([row['id'] for row in register if row['add_to_references'] == 'Y'], ['M9'])
        self.assertTrue(all(row['read_status'] for row in register))
        self.assertEqual(RESULTS['wp4_protocol']['status'], 'DONE')
        slides = deck_text()
        with (ROOT / 'analysis_outputs/claims_ledger.csv').open(encoding='utf-8-sig', newline='') as stream:
            ledger = [dict(claim_id=f'C{i:04d}', csv_line=i + 1, **row) for i, row in enumerate(csv.DictReader(stream), 1)]
        self.assertEqual(len(ledger), 278)
        text = proposal(slides, ledger, RESULTS['wp5_label_shift']['status'])
        self.assertIn('Calibration simulation (planning proxy):\nadjusted contribution', text)
        self.assertNotIn('through160,000', text)
        for token in ('C0137 / CSV line 138', 'C0139 / CSV line 140', '78.6 / 27.9', '99.3 / 79.8',
                      'abstract-only', 'LaTeX only', 'STOP here', '[M9] EMP'):
            self.assertIn(token, text)
        for token in ('+0.0030–0.0055', '9,200–11,500', '−0.6 to −1.2'):
            self.assertNotIn(token, text)
        statuses = {f'WP{i}': RESULTS[name]['status'] for i, name in enumerate(NAMES)}
        statuses['WP7'] = 'DONE'
        summary = handback(statuses, dict(files_before=4246, files_after=4246), 0, RESULTS['wp5_label_shift'])
        self.assertIn('10,000 batches / 5,000,000 bootstrap fits', summary)
        self.assertIn('failed checks', summary)

    def test_seed_determinism_runtime_and_boundary(self):
        self.assertTrue(all(1 <= pool['num_threads'] <= 6 for pool in verify_runtime()))
        fixture = 'tests/final_seed_determinism_fixture.json'
        value = dict(values=np.random.default_rng(SEED + 7).normal(size=16).tolist())
        write_json(fixture, value, __file__, 7, [])
        first = digest(ADDONS / fixture)
        write_json(fixture, value, __file__, 7, [])
        self.assertEqual(first, digest(ADDONS / fixture))
        with self.assertRaises(PermissionError):
            audit_boundary('open', (ROOT / 'forbidden_validation_probe.txt', 'w', os.O_WRONLY | os.O_CREAT))


if __name__ == '__main__':
    verify_runtime()
    RESULTS.update({name: json.loads((ADDONS / f'results/{name}.json').read_text(encoding='utf-8')) for name in NAMES})
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(FinalValidation)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    inputs = [ADDONS / f'results/{name}.json' for name in NAMES]
    inputs += [ADDONS / f'results/wp{i}_tests.json' for i in (1, 2, 5)]
    inputs += [ADDONS / 'tests/final_seed_determinism_fixture.json']
    wp5 = RESULTS['wp5_label_shift']
    write_json('results/final_new_code_tests.json', dict(
        passed=result.wasSuccessful(), tests=result.testsRun, failures=len(result.failures), errors=len(result.errors),
        existing_implementation_tests=15, heavy_simulations_rerun=False, old_suite_run=False,
        new_test_rows_used=0, wp5_scientific_status=wp5['status'],
        wp5_scientific_acceptance=wp5['statistical_acceptance'],
        verified_current_files=[file_info(path) for path in sorted(HASHES)],
        scope='New-code output verification; a PARTIAL scientific result is preserved, not counted as an implementation-test failure.'
    ), __file__, 7, inputs, dict(wp5_originals=10_000, wp5_bootstraps=5_000_000, old_tests_run=0, new_test_rows=0))
    raise SystemExit(0 if result.wasSuccessful() else 1)
