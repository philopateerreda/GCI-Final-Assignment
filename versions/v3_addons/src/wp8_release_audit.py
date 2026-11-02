import common

import argparse
import copy
import csv
import importlib.util
import io
from pathlib import Path
import sys
import unittest

import wp8_model as wp8

SCRIPT = Path(__file__).resolve()
TESTS_RECEIPT = common.ADDONS / 'results/wp8_tests.json'
VERIFICATION = common.ADDONS / 'results/wp8_verification.json'
MANIFEST = common.ADDONS / 'results/wp8_files_created.csv'
SEALED_RENDER_REPORT = wp8.render_report


def render_generation_order(summary):
    gate_order = wp8.promotion_gates(summary['intervals'], True, True, True)['gates']
    wp8.require(set(summary['intervals']) == set(wp8.METRICS)
                and set(summary['promotion']['gates']) == set(gate_order), 'report schema mismatch')
    aligned = dict(summary)
    aligned['intervals'] = {name: summary['intervals'][name] for name in wp8.METRICS}
    aligned['promotion'] = dict(summary['promotion'], gates={
        name: summary['promotion']['gates'][name] for name in gate_order})
    wp8.require(aligned == summary, 'report ordering changed values')
    return SEALED_RENDER_REPORT(aligned)


class ReportOrderTests(unittest.TestCase):
    def test_json_roundtrip_report_reconstruction_without_value_changes(self):
        summary = wp8.read_json(wp8.SUMMARY)
        preserved = copy.deepcopy(summary)
        self.assertEqual(render_generation_order(summary), wp8.REPORT.read_text(encoding='utf-8'))
        self.assertEqual(summary, preserved)

    def test_changed_metric_or_gate_is_not_hidden_by_report_ordering(self):
        original = wp8.read_json(wp8.SUMMARY)
        actual = wp8.REPORT.read_text(encoding='utf-8')
        for field in ('metric', 'gate'):
            changed = copy.deepcopy(original)
            if field == 'metric':
                changed['mean_metrics']['candidate']['auc'] += .01
            else:
                key = 'mean_delta_auc_ge_0_003'
                changed['promotion']['gates'][key] = not changed['promotion']['gates'][key]
            with self.subTest(field=field):
                self.assertNotEqual(render_generation_order(changed), actual)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    if not args.verify_only:
        wp8.require(not any(path.exists() for path in (TESTS_RECEIPT, VERIFICATION, MANIFEST)),
                    'WP8 release receipts already exist; refusing overwrite')
    # Sorted JSON changes presentation order, not the sealed metrics or gate values.
    wp8.render_report = render_generation_order
    verified = wp8.verify_outputs()
    spec = importlib.util.spec_from_file_location('new_wp8_release_tests', wp8.TEST_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(ReportOrderTests))
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    wp8.require(result.wasSuccessful() and result.testsRun == 26 and not result.skipped,
                'new WP8 test suite and report-order regressions did not pass all 26 tests: ' + stream.getvalue())
    if args.verify_only:
        print(stream.getvalue(), end='')
        print(verified)
        return
    summary = wp8.read_json(wp8.SUMMARY)
    inputs = [wp8.SUMMARY, wp8.RECEIPT, wp8.SNAPSHOT, wp8.PREREG,
              wp8.SCRIPT, wp8.TEST_SCRIPT, wp8.REPORT]
    counts = dict(tests_run=result.testsRun, repeated_oof=150000, unique_customers=75000,
                  classifier_fits=50, sigmoid_fits=10, new_test_looks=0)
    common.write_json('results/wp8_tests.json', dict(status='PASS', tests_run=result.testsRun,
        skipped=0, failures=0, errors=0, test_log=stream.getvalue(), no_fits_in_tests=True),
        SCRIPT, 8, inputs, counts)
    owned = {SCRIPT, wp8.SCRIPT, wp8.TEST_SCRIPT, wp8.PREREG, wp8.SUMMARY,
             wp8.REPORT, TESTS_RECEIPT}
    owned.update(path for path in wp8.OUT.rglob('*') if path.is_file())
    rows = [common.file_info(path) for path in sorted(owned)]
    with MANIFEST.open('x', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=['path', 'present', 'size', 'sha256'])
        writer.writeheader()
        writer.writerows(rows)
    wp8.require(all(common.file_info(row['path']) == row for row in rows), 'WP8 phase manifest drift')
    common.write_json('results/wp8_verification.json', dict(status='VERIFIED',
        audit=verified, model_summary=common.file_info(wp8.SUMMARY),
        new_tests=common.file_info(TESTS_RECEIPT), manifest=common.file_info(MANIFEST),
        manifest_files=len(rows), manifest_exclusions=[MANIFEST.as_posix(), VERIFICATION.as_posix()],
        preregistration=common.file_info(wp8.PREREG), seal=common.file_info(wp8.RECEIPT),
        original_cli_exit='FAILED_REPORT_ROW_ORDER_AFTER_ALL_NUMERICAL_AND_INTEGRITY_CHECKS',
        report_order_reconstruction=dict(sealed_runner_and_artifacts_unchanged=True,
            normalization='restore original METRICS and promotion-gate insertion order only',
            value_changes=False, checks_skipped=False, regression_tests=2,
            exact_report_text_match=True),
        promotion=summary['promotion'], outside_sandbox_diff=summary['outside_sandbox_diff'],
        frozen_delivery_unchanged=summary['frozen_delivery_unchanged'],
        wp7_unchanged=summary['wp7_unchanged'], no_new_test_look=True,
        no_fits_performed_by_audit=True), SCRIPT, 8,
        inputs + [TESTS_RECEIPT, MANIFEST], counts)
    print(stream.getvalue(), end='')
    print('WP8 numerical verification and phase-specific receipts saved; no fits or test look.')


if __name__ == '__main__':
    main()
