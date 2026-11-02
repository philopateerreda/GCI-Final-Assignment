import json
from hashlib import sha256
from pathlib import Path
import re
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import build_v2_canonical as canonical
from common import ROOT, WORK


class CanonicalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = canonical.assemble()
        cls.pipeline = (WORK / 'analysis_pipeline_v2.py').read_text(encoding='utf-8')

    def test_original_nine_cells_remain_unchanged(self):
        original = (ROOT / 'v1_frozen/analysis_pipeline.py').read_text(encoding='utf-8')
        old = re.split(r'^# %% (.+)\n', original, flags=re.MULTILINE)[2::2]
        new = re.split(r'^# %% (.+)\n', self.pipeline, flags=re.MULTILINE)[2::2]
        self.assertEqual(len(old), 9)
        self.assertEqual([code.strip() for code in old], [code.strip() for code in new[:9]])
        self.assertEqual(len(new), self.report['v2_code_cells'])
        for code in new:
            compile(code, 'notebook-cell', 'exec')

    def test_report_fingerprints_actual_candidate_bytes(self):
        for key, filename in (('pipeline_sha256', 'analysis_pipeline_v2.py'),
                              ('builder_sha256', 'build_notebook_v2.py')):
            self.assertEqual(self.report[key], sha256((WORK / filename).read_bytes()).hexdigest())

    def test_materializer_preserves_bytes_and_refuses_different_source(self):
        with TemporaryDirectory() as directory:
            namespace = {'__name__': 'materializer_test'}
            exec(canonical.BOOTSTRAP, namespace)
            namespace['V2_WORK'] = Path(directory)
            source = 'x = 1\nprint(x)\n'
            target = namespace['_v2_materialize']('example', source)
            self.assertEqual(target.read_bytes(), source.encode('utf-8'))
            namespace['_v2_materialize']('example', source)
            with self.assertRaises(AssertionError):
                namespace['_v2_materialize']('example', 'x = 2\n')

    def test_candidate_builder_has_markdown_for_every_cell(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'analysis_pipeline.py').write_text(self.pipeline, encoding='utf-8', newline='')
            namespace = {'__name__': 'builder_test', '__file__': str(WORK / 'build_notebook_v2.py')}
            exec(compile((WORK / 'build_notebook_v2.py').read_text(encoding='utf-8'), 'builder', 'exec'), namespace)
            namespace['ROOT'] = root
            notebook = namespace['build']()
            codes = [cell for cell in notebook.cells if cell.cell_type == 'code']
            self.assertEqual(len(codes), self.report['v2_code_cells'])
            self.assertEqual([cell.source for cell in codes],
                             [code.strip() for code in re.split(r'^# %% (.+)\n', self.pipeline, flags=re.MULTILINE)[2::2]])

    def test_calibration_summary_uses_authoritative_budget_spec(self):
        spec = json.loads((WORK / 'a_spec.json').read_text(encoding='utf-8'))
        summary = json.loads((WORK / 'a_summary_calibration.json').read_text(encoding='utf-8'))
        self.assertEqual(summary['spec'], spec)
        self.assertEqual(spec['promoted_headline_fraction'], .1)
        self.assertFalse(spec['test_used_for_selection'])

    def test_final_reporting_contract_with_synthetic_rows_only(self):
        import pandas as pd
        from unittest.mock import patch
        import final_metrics
        from common import shift, weights
        import workstream_a as a
        with TemporaryDirectory() as directory:
            root = Path(directory)
            work = root / 'v2_work'
            (work / 'd_results').mkdir(parents=True)
            (work / 'c_test').mkdir()
            (root / 'v1_frozen/analysis_outputs').mkdir(parents=True)
            (root / 'analysis_outputs').mkdir()
            frame = pd.DataFrame({key: values * 3 for key, values in {
                'y': [0, 1, 0, 1], 'p_s': [.2, .8, .4, .6],
                'value': [10., 100., 20., 30.], 'selected_bayes': [False, True, False, True]}.items()})
            frame['p_d'] = shift(frame.p_s)
            frame['weight'] = weights(frame.y)
            frame.to_csv(work / 'a_selected_test.csv', index=False)
            policies = [{'prior': .02, 'policy': name, **a.measure(frame, frame.selected_bayes)}
                        for name in ('risk', 'bayes')]
            spec = {'thresholds': {str(prior): {'bayes': 0.} for prior in (.01, .02, .05)}}
            v1 = {'selected_test_metrics': {'roc_auc': .7}, 'bootstrap_intervals': {'auc': {'lower': .6, 'upper': .8}}}
            fixtures = {'a_summary_test.json': {'policies': policies, 'spec': spec},
                        'd_results/summary.json': {'selected_candidate': 'baseline_lgbm'},
                        'b_summary_calibration.json': {'synthetic_fixture': True},
                        'b_summary_test.json': {'synthetic_fixture': True},
                        'c_test/c_summary.json': {'synthetic_fixture': True},
                        'final_frozen_protocol.json': {'synthetic_fixture': True}}
            for name, value in fixtures.items():
                (work / name).write_text(json.dumps(value), encoding='utf-8')
            for target in (root / 'v1_frozen/analysis_outputs/summary.json', root / 'analysis_outputs/summary.json'):
                target.write_text(json.dumps(v1), encoding='utf-8')
            pd.DataFrame([{'candidate': 'synthetic_challenger', 'eligible': True,
                           'corrected_auc_lower': -.01, 'mean_auc_gain': .0}]).to_csv(work / 'd_results/gate_d.csv', index=False)
            pd.DataFrame([{'regime': regime, 'prior': prior, 'policy': policy,
                           'metric': 'relative_value_gain_vs_risk', 'lower': .1, 'upper': .3}
                          for regime, prior, policy in (('deployment', .02, 'bayes'), ('sample', .4956, 'sample_rv'))]).to_csv(work / 'a_intervals_test.csv', index=False)
            pd.DataFrame([{'scope': 'pooled_oof', 'target': 'synthetic_attribute', 'auc': .6}]).to_csv(work / 'c_proxy_cv.csv', index=False)
            def write_fixture(name, value):
                (work / name).write_text(json.dumps(value, allow_nan=False), encoding='utf-8')
            with patch.object(final_metrics, 'ROOT', root), patch.object(final_metrics, 'WORK', work), \
                 patch.object(final_metrics, 'verify', return_value={'gate_d_passed': False, 'model_candidate': 'baseline_lgbm'}), \
                 patch.object(final_metrics, 'dump', side_effect=write_fixture):
                result = final_metrics.build()
                self.assertTrue(result['selected_model_test']['v1_reference_retained'])
                self.assertEqual(result['deployment_intervals']['relative_value_gain_vs_risk']['lower'], .1)
                self.assertEqual(result['deployment_prevented'], policies[0]['actual_churners'] * .2)
                published = final_metrics.publish_summary()
                self.assertEqual(published['deployment_policies'], result['deployment_policies'])


class FinalReportGuardTests(unittest.TestCase):
    def setUp(self):
        import pandas as pd
        import prepare_checkpoint2

        self.reporter = prepare_checkpoint2
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.work = self.root / 'v2_work'
        self.out = self.root / 'analysis_outputs'
        self.work.mkdir()
        (self.out / 'slide_renders').mkdir(parents=True)
        (self.root / 'v1_frozen').mkdir()
        self.target = self.root / 'FINAL_V2_UPGRADE_REPORT.md'
        self.checks_path = self.out / 'delivery_checks.json'
        self.review_path = self.work / 'visual_review.json'
        self.geometry_path = self.work / 'office_geometry_check.json'

        self.delivery = {name: f'synthetic delivery: {name}\n'.encode('utf-8')
                         for name in ('philopateer.pdf', 'philopateer.pptx',
                                      'philopateer.ipynb', 'references.txt')}
        for name, content in self.delivery.items():
            (self.root / name).write_bytes(content)
        delivery_hashes = {name: sha256(content).hexdigest() for name, content in self.delivery.items()}
        render_hashes = {}
        for number in range(1, 16):
            relative = f'analysis_outputs/slide_renders/Slide{number}.PNG'
            content = f'synthetic full-size render {number}'.encode('utf-8')
            (self.root / relative).write_bytes(content)
            render_hashes[relative] = sha256(content).hexdigest()
        contact = b'synthetic contact sheet for all fifteen slides'
        (self.out / 'deck_contact_sheet.png').write_bytes(contact)
        frozen = b'synthetic immutable v1 bytes'
        (self.root / 'v1_frozen/baseline.bin').write_bytes(frozen)
        self._write_json(self.root / 'v1_frozen/sha256_manifest.json', {
            'baseline.bin': {'bytes': len(frozen), 'sha256': sha256(frozen).hexdigest()}})

        interval = {'lower': .1, 'upper': .3}
        auc_interval = {'lower': .6, 'upper': .8}
        self.final = {
            'protocol_sha256': sha256(b'synthetic frozen protocol').hexdigest(),
            'v1': {'selected_test_metrics': {'roc_auc': .7},
                   'bootstrap_intervals': {'auc': auc_interval, 'value_capture_relative_gain': interval},
                   'value_capture_relative_gain_over_risk': .2,
                   'base_business_scenario': [{'policy': 'Value-aware', 'net_contribution_scenario': 100.}]},
            'deployment_policies': {'bayes': {'value_recall': .6, 'net': 200.},
                                    'risk': {'value_recall': .5}},
            'sample_intervals': {'relative_value_gain_vs_risk': interval},
            'deployment_intervals': {'relative_value_gain_vs_risk': interval,
                                     'net': {'lower': 100., 'upper': 300.}},
            'sample_relative_value_gain_v2': .2, 'deployment_relative_value_gain': .2,
            'strongest_nonpromoted_or_promoted_cv_candidate': {
                'candidate': 'synthetic_challenger', 'mean_auc_gain': 0.,
                'corrected_auc_lower': -.01, 'corrected_auc_upper': .01},
            'selected_model_test': {'metrics': {'roc_auc': .7}, 'auc_95ci': auc_interval},
            'pilot_calibration': {
                'spec': {'allocation': {'core_per_arm': 100},
                         'stage1_cost': 1000., 'stage2_incremental_cost': 500.},
                'simulated_required_enrolled_per_arm_grid': {
                    'binary_churn': 1000, 'adjusted_contribution': None}},
            'a_spec': {'calibration_candidates': [
                {'method': 'beta', 'paired_logloss_improvement': 0., 'ci_lower': -.01, 'ci_upper': .01}]}}
        self._write_json(self.work / 'final_metrics.json', self.final)
        self.geometry = {'slide_count': 15, 'issue_count': 0,
                         'pptx_sha256': delivery_hashes['philopateer.pptx']}
        self.checks = {
            'notebook_errors': 0, 'notebook_matches_pipeline': True,
            'original_nine_code_cells_preserved': True, 'source_files_unchanged': True,
            'executed_notebook_code_cells': 10, 'pdf_pages': 15, 'pptx_slides': 15,
            'pdf_bytes': len(self.delivery['philopateer.pdf']), 'out_of_bounds_shapes': [],
            'office_geometry_issue_count': 0, 'powerpoint_export': 'successful',
            'protocol_sha256': self.final['protocol_sha256'],
            'render_sha256': render_hashes, 'delivery_sha256': delivery_hashes}
        self.review = {
            'status': 'passed', 'slides_reviewed': list(range(1, 16)),
            'clipped_text_or_unintended_overlaps': 0, 'render_sha256': render_hashes.copy(),
            'contact_sheet_sha256': sha256(contact).hexdigest()}
        self._save_receipts()

        self.enterContext(patch.object(self.reporter, 'ROOT', self.root))
        self.enterContext(patch.object(self.reporter, 'WORK', self.work))
        self.completed = self.enterContext(patch.object(
            self.reporter, 'verify_completed', autospec=True,
            return_value={'gate_d_passed': False, 'model_candidate': 'synthetic_baseline'}))
        self.claims = self.enterContext(patch('claim_checks.verify_claims', autospec=True,
                                             return_value={'synthetic_fixture': True}))
        self.gates = self.enterContext(patch.object(
            self.reporter.pd, 'read_csv', autospec=True,
            return_value=pd.DataFrame({'candidate': ['synthetic_challenger'], 'pass_gate_d': [False]})))

    def _write_json(self, path, document):
        path.write_text(json.dumps(document, allow_nan=False), encoding='utf-8')

    def _save_receipts(self):
        # Rebind receipts after intentional fixture changes, isolating the guard under test.
        self._write_json(self.geometry_path, self.geometry)
        self.checks['office_geometry_check_sha256'] = sha256(self.geometry_path.read_bytes()).hexdigest()
        self._write_json(self.checks_path, self.checks)
        self.review['delivery_checks_sha256'] = sha256(self.checks_path.read_bytes()).hexdigest()
        self._write_json(self.review_path, self.review)

    def _run_report(self, error=None, claims_checked=False):
        self.completed.reset_mock()
        self.claims.reset_mock()
        self.gates.reset_mock()
        self.report_reads = []
        real_open = Path.open

        def synthetic_read_only(path, mode='r', *args, **kwargs):
            if not path.resolve().is_relative_to(self.root) or any(flag in mode for flag in 'wax+'):
                raise RuntimeError(f'Unexpected non-synthetic read or file write: {path}')
            self.report_reads.append(path)
            return real_open(path, mode, *args, **kwargs)

        with patch.object(Path, 'open', autospec=True, side_effect=synthetic_read_only), \
             patch.object(Path, 'write_text', autospec=True) as write:
            if error is not None:
                with self.assertRaises(error):
                    self.reporter.final_report()
                write.assert_not_called()
                text = None
            else:
                self.assertEqual(self.reporter.final_report(), self.target)
                write.assert_called_once()
                path, text = write.call_args.args
                self.assertEqual(path, self.target)
                self.assertEqual(write.call_args.kwargs, {'encoding': 'utf-8'})
        self.assertFalse(self.target.exists())
        self.completed.assert_called_once_with()
        if error is None or claims_checked:
            self.claims.assert_called_once_with(self.root)
        else:
            self.claims.assert_not_called()
        if error is None:
            self.gates.assert_called_once_with(self.work / 'd_results/gate_d.csv')
        else:
            self.gates.assert_not_called()
        return text

    def test_verified_final_batch_required_before_artifact_reads(self):
        self.completed.side_effect = AssertionError('synthetic final batch not verified')
        self._run_report(AssertionError)
        self.assertEqual(self.report_reads, [])

    def test_missing_visual_approval_blocks_report(self):
        self.review_path.unlink()
        self._run_report(FileNotFoundError)

    def test_pending_visual_approval_blocks_report(self):
        self.review['status'] = 'pending'
        self._write_json(self.review_path, self.review)
        self._run_report(AssertionError)

    def test_all_fifteen_slides_require_unclipped_approval(self):
        original = self.review.copy()
        for key, value in (('slides_reviewed', list(range(1, 15))),
                           ('clipped_text_or_unintended_overlaps', 1)):
            with self.subTest(key=key):
                self.review = {**original, key: value}
                self._write_json(self.review_path, self.review)
                self._run_report(AssertionError)

    def test_notebook_and_export_prerequisites_block_report(self):
        original = self.checks.copy()
        for key, value in (('notebook_errors', 1), ('notebook_matches_pipeline', False),
                           ('original_nine_code_cells_preserved', False), ('source_files_unchanged', False),
                           ('pdf_pages', 14), ('pptx_slides', 14), ('pdf_bytes', 10_000_001),
                           ('pdf_bytes', original['pdf_bytes'] + 1), ('out_of_bounds_shapes', ['synthetic_shape']),
                           ('office_geometry_issue_count', 1), ('powerpoint_export', 'pending'),
                           ('protocol_sha256', sha256(b'other synthetic protocol').hexdigest())):
            with self.subTest(key=key, value=value):
                self.checks = {**original, key: value}
                self._save_receipts()
                self._run_report(AssertionError)

    def test_geometry_requires_fifteen_issue_free_slides(self):
        original = self.geometry.copy()
        for key, value in (('slide_count', 14), ('issue_count', 1)):
            with self.subTest(key=key):
                self.geometry = {**original, key: value}
                self._save_receipts()
                self._run_report(AssertionError)

    def test_stale_render_approval_hash_rejected(self):
        relative = 'analysis_outputs/slide_renders/Slide15.PNG'
        self.review['render_sha256'][relative] = sha256(b'old synthetic render').hexdigest()
        self._write_json(self.review_path, self.review)
        self._run_report(AssertionError)

    def test_render_bytes_changed_after_approval_rejected(self):
        (self.out / 'slide_renders/Slide15.PNG').write_bytes(b'changed synthetic render')
        self._run_report(AssertionError)

    def test_stale_geometry_pptx_hash_rejected(self):
        self.geometry['pptx_sha256'] = sha256(b'old synthetic pptx').hexdigest()
        self._save_receipts()
        self._run_report(AssertionError)

    def test_geometry_receipt_changed_after_export_rejected(self):
        self.geometry_path.write_bytes(self.geometry_path.read_bytes() + b'\n')
        self._run_report(AssertionError)

    def test_contact_sheet_changed_after_approval_rejected(self):
        (self.out / 'deck_contact_sheet.png').write_bytes(b'changed synthetic contact sheet')
        self._run_report(AssertionError)

    def test_delivery_receipt_changed_after_approval_rejected(self):
        # Even semantically identical receipt JSON must retain its approved byte hash.
        self.checks_path.write_bytes(self.checks_path.read_bytes() + b'\n')
        self._run_report(AssertionError)

    def test_delivery_bytes_changed_after_export_rejected(self):
        for name, original in self.delivery.items():
            with self.subTest(name=name):
                changed = b'X' + original[1:]
                (self.root / name).write_bytes(changed)
                if name == 'philopateer.pptx':
                    # Keep geometry current so only the stale delivery digest rejects this PPTX.
                    self.geometry['pptx_sha256'] = sha256(changed).hexdigest()
                self._save_receipts()
                self._run_report(AssertionError)
                (self.root / name).write_bytes(original)
                self.geometry['pptx_sha256'] = self.checks['delivery_sha256']['philopateer.pptx']
                self._save_receipts()

    def test_immutable_v1_size_and_hash_required(self):
        frozen = self.root / 'v1_frozen/baseline.bin'
        original = frozen.read_bytes()
        for content in (original[:-1], b'X' + original[1:]):
            with self.subTest(size=len(content)):
                frozen.write_bytes(content)
                self._run_report(AssertionError)

    def test_claim_verification_failure_blocks_report_write(self):
        self.claims.side_effect = AssertionError('synthetic claims not verified')
        self._run_report(AssertionError, claims_checked=True)

    def test_valid_synthetic_receipts_allow_report_without_file_write(self):
        text = self._run_report()
        self.assertIn('# Final v2 upgrade report', text)
        self.assertIn('Completed locally; NOT submitted.', text)
        self.assertIn('Retained v1 classifier;', text)
        self.assertIn('Immutable v1 snapshot: 1 files verified byte-for-byte.', text)
        for name, digest in self.checks['delivery_sha256'].items():
            self.assertIn(f'- `{name}`: `{digest}`', text)
        self.assertIn(f"Protocol: `{self.final['protocol_sha256']}`.", text)


class ChartVerificationTests(unittest.TestCase):
    def test_ledger_preserves_integer_formatting_and_scales_money(self):
        import pandas as pd
        from pptx import Presentation
        import build_claim_ledger
        import chart_inventory
        from claim_checks import verify_claims
        with TemporaryDirectory() as directory:
            root = Path(directory)
            work = root / 'v2_work'
            work.mkdir()
            (root / 'analysis_outputs').mkdir()
            (root / 'values.json').write_text(json.dumps({'ordinal': 1, 'money': 1200, 'zero': 0}), encoding='utf-8')
            (work / 'static_claim_sources.json').write_text('{}', encoding='utf-8')
            (root / 'references.txt').write_text('', encoding='utf-8')
            bindings = [
                {'slide_number': 1, 'source_file_or_json_key': 'values.json::ordinal',
                 'epistemic_type': 'assumed', 'prior_regime': 'external_context',
                 'formatter': '{:02d}', 'scale': 1, 'location': 'native'},
                {'slide_number': 1, 'source_file_or_json_key': 'values.json::money',
                 'epistemic_type': 'simulated', 'prior_regime': 'deployment_2.0%',
                 'formatter': '{:.1f}k', 'scale': .001, 'location': 'native'}]
            (work / 'ledger_bindings.json').write_text(json.dumps(bindings), encoding='utf-8')
            number = {'slide_number': 1, 'source_file_or_json_key': 'values.json::zero',
                      'epistemic_type': 'assumed', 'prior_regime': 'external_context',
                      'formatter': '{:03d}', 'unicode_minus': False, 'value': 0, 'displayed_text': '000'}
            deck = Presentation()
            slide = deck.slides.add_slide(deck.slide_layouts[6])
            slide.shapes.add_textbox(0, 0, 1000000, 1000000).text = '01 1.2k'
            deck.save(root / 'philopateer.pptx')
            with patch.object(build_claim_ledger, 'ROOT', root), patch.object(build_claim_ledger, 'WORK', work), \
                 patch.object(chart_inventory, 'prepare_numeric_sources', return_value=[number]), \
                 patch.object(chart_inventory, 'verify_embedded_images', return_value={}):
                self.assertEqual(build_claim_ledger.build()['rows'], 3)
                result = verify_claims(root)
            self.assertEqual(result['ledger_rows'], 3)
            ledger = pd.read_csv(root / 'analysis_outputs/claims_ledger.csv', keep_default_na=False)
            self.assertEqual(ledger.displayed_text.tolist(), ['01', '1.2k', '000'])

    def test_chart_ledger_rejects_equal_tokens_with_wrong_provenance(self):
        import pandas as pd
        from claim_checks import verify_chart_ledger
        number = {'slide_number': 5, 'value': 10, 'formatter': '{:,}', 'displayed_text': '10',
                  'epistemic_type': 'observed', 'prior_regime': 'sample_49.56%', 'unicode_minus': True,
                  'source_file_or_json_key': 'v2_work/chart_numeric_sources.json::0.value'}
        ledger = pd.DataFrame([{**number, 'exact_value': '10', 'location': 'chart'}])
        self.assertTrue(verify_chart_ledger(ledger, [number]))
        for key, wrong in (('prior_regime', 'deployment_2.0%'), ('exact_value', '10.1'),
                           ('source_file_or_json_key', 'unrelated.json::same_rounded_token'),
                           ('epistemic_type', 'assumed'), ('formatter', '{:.0f}')):
            altered = ledger.copy()
            altered.loc[0, key] = wrong
            with self.subTest(key=key), self.assertRaises(AssertionError):
                verify_chart_ledger(altered, [number])

    def test_generated_charts_validate_synthetic_coordinates_and_reject_tampering(self):
        from copy import deepcopy
        import runpy
        from unittest.mock import patch
        import numpy as np
        import pandas as pd
        import common
        import final_protocol
        import chart_inventory
        with TemporaryDirectory() as directory:
            root = Path(directory)
            work = root / 'v2_work'
            work.mkdir()
            baseline_tables = root / 'v1_frozen/analysis_outputs/tables'
            baseline_tables.mkdir(parents=True)
            pd.DataFrame({'model': ['Logistic regression (60k train)',
                                   'LightGBM wider leaves calibrated (75k refit)', 'Constant prior baseline'],
                          'roc_auc': [.6, .7, .5]}).to_csv(baseline_tables / 'test_metrics.csv', index=False)
            frame = pd.DataFrame({'y': [0, 1, 0, 1, 0, 1] * 3,
                                  'p_d': [.02, .10, .06, .005, .04, .08] * 3,
                                  'value': [10., 100., 20., 30., 100., 40.] * 3})
            frame['weight'] = common.weights(frame.y)
            frame['selected_risk'] = frame.p_d >= .05
            frame['selected_bayes'] = frame.p_d * frame.value >= 3.
            spec = {'thresholds': {'0.02': {'risk': .05, 'bayes': 3.}},
                    'optimal_budgets_calibration_only': [{'cost': cost, 'fraction': .2} for cost in (.25, 1., 2.)]}
            for name in ('a_selected_test.csv', 'a_selected_calibration.csv'):
                frame.to_csv(work / name, index=False)
            for name, document in (('a_spec.json', spec), ('a_summary_test.json', {'spec': spec})):
                (work / name).write_text(json.dumps(document), encoding='utf-8')
            overlaps = []
            for name, mask in (('both', frame.selected_risk & frame.selected_bayes),
                               ('rv_only', frame.selected_bayes & ~frame.selected_risk),
                               ('risk_only', frame.selected_risk & ~frame.selected_bayes)):
                overlaps.append({'region': name, 'mean_value': np.average(frame.value[mask], weights=frame.weight[mask])})
            pd.DataFrame(overlaps).to_csv(work / 'a_overlap_test.csv', index=False)
            curve_rows = []
            for cost in (.25, 1., 2.):
                for fraction in (.1, .2, .3):
                    threshold = common.cutoff(frame.p_d * frame.value, frame.weight, fraction)
                    mask = frame.p_d * frame.value >= threshold
                    net = .2 * 6 * .6 * np.sum(frame.weight * frame.y * frame.value * mask) - cost * np.sum(frame.weight * mask) - 5000
                    curve_rows.append({'cost': cost, 'intended_fraction': fraction, 'threshold': threshold, 'net': net})
            curves = pd.DataFrame(curve_rows)
            curves.to_csv(work / 'a_profit_curves_test.csv', index=False)
            with patch.object(common, 'ROOT', root), patch.object(common, 'WORK', work), \
                 patch.object(final_protocol, 'verify', return_value={'synthetic_fixture': True}):
                runpy.run_path(str(WORK / 'generate_visuals.py'), run_name='chart_fixture')
            with patch.object(chart_inventory, 'ROOT', root), patch.object(chart_inventory, 'WORK', work), \
                 patch.object(chart_inventory, 'inventory', return_value=[]):
                numbers = chart_inventory.prepare_numeric_sources()
            raw_counts = [row for row in numbers if 'raw sample rows' in row['source_locator']]
            self.assertEqual(len(raw_counts), 3)
            self.assertTrue(all(row['prior_regime'] == 'sample_49.56%' for row in raw_counts))
            charts = json.loads((work / 'chart_claims.json').read_text(encoding='utf-8'))
            self.assertEqual([chart['slide_number'] for chart in charts], [5, 9, 11])
            for chart in charts:
                altered = deepcopy(chart)
                altered['plot_data']['lines'][0]['y'][0] += 1
                with self.subTest(slide=chart['slide_number']), self.assertRaises(AssertionError):
                    chart_inventory.verify_plot_data(altered, frame, spec, curves, frame)
                self.assertIn('a_summary_test.json', chart['source_sha256'])
                self.assertIn('a_spec.json', chart['source_sha256'])


if __name__ == '__main__':
    unittest.main()
