from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from common import ADDONS, stored_constants, verify_runtime, write_json
from wp2_decisions import posterior_moments, prior_metrics

import numpy as np
from scipy import integrate, stats


class DecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        verify_runtime()
        cls.constants=stored_constants()

    def test_evpi_independent_quadrature(self):
        G,K=self.constants['G'],self.constants['K']
        for a,b in ((6,14),(6,24),(2,18)):
            positive=integrate.quad(lambda gamma:max(0,G*gamma-K)*stats.beta.pdf(gamma,a,b),K/G,1,epsabs=1e-8)[0]
            expected=positive-max(0,G*a/(a+b)-K)
            self.assertAlmostEqual(prior_metrics(a,b,self.constants)['evpi'],expected,places=6)

    def test_no_data_recovers_prior(self):
        for a,b in ((6,14),(6,24),(2,18)):
            moments=posterior_moments(np.array([0]),np.array([0]),0,a,b,self.constants)
            expected=self.constants['G']*a/(a+b)-self.constants['K']
            self.assertLess(abs(moments[0,0]-expected),1.)
            self.assertAlmostEqual(moments[0,1]-moments[0,2],moments[0,0],places=8)

    def test_single_survivor_matches_analytic_posterior(self):
        a,b=6,24
        c=self.constants['p0']
        second=c*c+.02*.02/3
        A=1-2*c+second
        B=c-second
        mean=a/(a+b)
        gamma_second=a*(a+1)/((a+b)*(a+b+1))
        posterior_gamma=(A*mean+B*gamma_second)/(A+B*mean)
        expected=self.constants['G']*posterior_gamma-self.constants['K']
        actual=posterior_moments(np.array([0]),np.array([0]),1,a,b,self.constants)[0,0]
        self.assertLess(abs(actual-expected),.05)

    def test_conditional_jensen_bound(self):
        moments=posterior_moments(np.array([390,450,350]),np.array([310,440,220]),7872,6,24,self.constants)
        self.assertTrue((np.maximum(moments[:,0],0)<=moments[:,1]+1e-8).all())
        np.testing.assert_allclose(moments[:,1]-moments[:,2],moments[:,0],atol=1e-8)


if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(DecisionTests))
    write_json('results/wp2_tests.json',dict(status='passed' if result.wasSuccessful() else 'failed',tests=result.testsRun,
               failures=len(result.failures),errors=len(result.errors)),__file__,2,[ADDONS/'src/wp2_decisions.py'])
    raise SystemExit(0 if result.wasSuccessful() else 1)
