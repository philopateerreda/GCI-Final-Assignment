import ast
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from common import ADDONS, ROOT, SEED, digest, population, verify_runtime, write_json
from wp1_power import METHODS, adjusted, simulate, summaries

import numpy as np


class PilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        verify_runtime()
        frame = population()
        cls.pop = frame.loc[frame.selected].reset_index(drop=True)

    def test_hc1_matches_expanded_rows(self):
        generator = np.random.default_rng(SEED+1)
        F = np.column_stack((np.ones(8), generator.normal(size=(8,2))))
        C = np.array([[3,2,2,3,2,3,2,3]])
        T = np.array([[2,3,3,2,3,2,3,2]])
        prevented = np.array([[0,1,0,1,1,0,1,0]])
        gross = generator.uniform(10,100,8)
        base = generator.uniform(0,100,8)
        xc = np.column_stack((np.repeat(F,C[0],axis=0),np.zeros(20)))
        xt = np.column_stack((np.repeat(F,T[0],axis=0),np.ones(20)))
        yt = np.concatenate([np.r_[np.repeat(base[i]+gross[i],prevented[0,i]),
                            np.repeat(base[i],T[0,i]-prevented[0,i])] for i in range(8)])
        X = np.vstack((xc,xt))
        Y = np.r_[np.repeat(base,C[0]),yt]
        inverse = np.linalg.inv(X.T@X)
        beta = inverse@X.T@Y
        residual = Y-X@beta
        covariance = inverse@(X.T@(X*residual[:,None]**2))@inverse*40/(40-X.shape[1])
        estimate,se = adjusted(C,T,prevented,F,gross,base,inverse[None,:,:],20)
        np.testing.assert_allclose(estimate[0],beta[-1],rtol=1e-11,atol=1e-11)
        np.testing.assert_allclose(se[0],np.sqrt(covariance[-1,-1]),rtol=1e-11)

    def test_syntax(self):
        for source in (ADDONS/'src').glob('*.py'):
            ast.parse(source.read_text(encoding='utf-8'))

    def test_seed_determinism(self):
        first = simulate(self.pop, 2500, .2, np.random.default_rng(SEED+1), replicates=4)
        second = simulate(self.pop, 2500, .2, np.random.default_rng(SEED+1), replicates=4)
        for method in METHODS:
            np.testing.assert_array_equal(first[method], second[method])
            self.assertTrue(np.isfinite(first[method]).all())
            self.assertTrue((first[method][:, 1]>=0).all())

    def test_zero_prevention_literal_oracle(self):
        samples = simulate(self.pop, 2500, 0., np.random.default_rng(SEED+1), replicates=4)
        np.testing.assert_array_equal(samples['E2_literal_oracle'], np.zeros((4,2)))
        np.testing.assert_array_equal(samples['E3_literal_oracle'], np.zeros((4,2)))
        rows = summaries(samples, 2500, 0.)
        for row in rows:
            if row['method'].endswith('literal_oracle'):
                self.assertEqual(row['effect_power'],0.)

    def test_json_determinism(self):
        relative = 'tests/seed_determinism_fixture.json'
        write_json(relative, dict(value=np.random.default_rng(SEED+1).normal(size=10).tolist()), __file__, 1, [])
        before = digest(ADDONS/relative)
        write_json(relative, dict(value=np.random.default_rng(SEED+1).normal(size=10).tolist()), __file__, 1, [])
        self.assertEqual(before, digest(ADDONS/relative))


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(PilotTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    write_json('results/wp1_tests.json',dict(status='passed' if result.wasSuccessful() else 'failed', tests=result.testsRun,
               errors=len(result.errors), failures=len(result.failures), tag='[E] new-code checks only'),
               __file__,1,[ADDONS/'src/common.py',ADDONS/'src/wp1_power.py'])
    raise SystemExit(0 if result.wasSuccessful() else 1)
