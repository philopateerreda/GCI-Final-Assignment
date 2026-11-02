import unittest
import numpy as np
import pandas as pd
from common import shift, weights, cutoff
from workstream_a import measure, fit_thresholds


class PolicyTests(unittest.TestCase):
    def test_prior_shift_preserves_risk_order_and_can_reverse_value_order(self):
        p = np.array([.5,.8])
        v = np.array([90.,55.])
        self.assertLess(p[0],p[1])
        self.assertLess(shift(p)[0],shift(p)[1])
        self.assertGreater((p*v)[0],(p*v)[1])
        self.assertLess((shift(p)*v)[0],(shift(p)*v)[1])

    def test_weighted_population_is_exact(self):
        y = np.array([0,1,0,1,1])
        w = weights(y)
        self.assertAlmostEqual(w.sum(),100000.)
        self.assertAlmostEqual(w[y==1].sum(),2000.)
        self.assertAlmostEqual(w[y==0].sum(),98000.)

    def test_gate_never_increases_contact_count(self):
        frame = pd.DataFrame({'y':[0,1,0,1],'p_s':[.2,.8,.4,.6],'value':[10.,100.,20.,30.]})
        t = fit_thresholds(frame,fraction=.25,cost=5)
        self.assertGreaterEqual(t['profit_gate'],t['bayes'])

    def test_value_measure_deducts_fixed_cost_once(self):
        frame = pd.DataFrame({'y':[0,1],'p_s':[.2,.8],'value':[10.,100.]})
        row = measure(frame,np.ones(2,dtype=bool))
        self.assertAlmostEqual(row['contacts'],100000.)
        self.assertAlmostEqual(row['actual_value'],200000.)
        self.assertAlmostEqual(row['net'],200000.*.2*6*.6-100000.-5000.)


class FrozenTestGuardTests(unittest.TestCase):
    def test_second_final_test_start_is_rejected(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from unittest.mock import patch
        import final_protocol
        with TemporaryDirectory() as directory:
            work = Path(directory)
            (work / 'final_frozen_protocol.json').write_text('{}', encoding='utf-8')
            with patch.object(final_protocol, 'WORK', work), patch.object(final_protocol, 'verify', return_value={'gate_d_passed': False}):
                final_protocol.begin_test(promoted=False)
                self.assertTrue((work / 'final_test_started.json').exists())
                with self.assertRaises(FileExistsError):
                    final_protocol.begin_test(promoted=False)

    def test_wrong_model_route_cannot_start(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from unittest.mock import patch
        import final_protocol
        with TemporaryDirectory() as directory:
            with patch.object(final_protocol, 'WORK', Path(directory)), patch.object(final_protocol, 'verify', return_value={'gate_d_passed': True}):
                with self.assertRaises(AssertionError):
                    final_protocol.begin_test(promoted=False)
                self.assertFalse((Path(directory) / 'final_test_started.json').exists())

    def test_frozen_baseline_cache_tampering_is_rejected(self):
        from pathlib import Path
        from hashlib import sha256
        import json
        from tempfile import TemporaryDirectory
        from unittest.mock import patch
        import final_protocol
        with TemporaryDirectory() as directory:
            root = Path(directory)
            work = root / 'work'
            work.mkdir()
            cache = root / 'heldout.csv'
            cache.write_bytes(b'locked baseline predictions')
            record = {'hashes': {}, 'baseline_hashes': {'heldout.csv': sha256(cache.read_bytes()).hexdigest()},
                      'protected_original_hashes': {}}
            (work / 'final_frozen_protocol.json').write_text(json.dumps(record), encoding='utf-8')
            with patch.object(final_protocol, 'WORK', work), patch.object(final_protocol, 'ROOT', root):
                self.assertEqual(final_protocol.verify(), record)
                cache.write_bytes(b'altered predictions')
                with self.assertRaises(AssertionError):
                    final_protocol.verify()

    def test_claim_tokens_do_not_split_identifiers_or_citations(self):
        from claim_checks import numeric_mentions
        self.assertEqual(numeric_mentions('FY2025 Q3 [S1–S4] seed 20261028, 20.8%'), ['20261028', '20.8%'])
        self.assertEqual(numeric_mentions('−5.6 +3.7k 7,872 0.6978'), ['−5.6', '+3.7k', '7,872', '0.6978'])


if __name__=='__main__':
    unittest.main()
