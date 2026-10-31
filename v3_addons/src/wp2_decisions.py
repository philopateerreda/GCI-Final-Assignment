from common import ADDONS, ROOT, file_info, rng, stored_constants, verify_runtime, write_json
from png_drafts import line_plot
from reporting import write_report
from wp1_power import DEFF_GRID, GAMMA_GRID, Z95

import json
import numpy as np
import pandas as pd
from scipy import special, stats

PRIORS = ((6,14), (6,24), (2,18))
PILOTS = 4096
GRID_SIZE = 400


def decision_quality():
    power = json.loads((ADDONS/'results/wp1_power.json').read_text(encoding='utf-8'))
    assert power['status'] == 'DONE_WITH_ORACLE_CAVEAT'
    constants = stored_constants()
    coefficient = power['population']['gross_effect_coefficient']
    rows = []
    with np.load(ADDONS/'results/wp1_simulation_samples.npz', allow_pickle=False) as arrays:
        for n in (5000,7872,10000,20000):
            for gamma in GAMMA_GRID:
                pairs = arrays[f'n{n}_g{int(round(gamma*100)):02d}_E3_observed']
                gamma_estimate = pairs[:,0]/coefficient
                for deff in DEFF_GRID:
                    net = constants['G']*gamma_estimate-constants['K']
                    margin = Z95*constants['G']/coefficient*pairs[:,1]*np.sqrt(deff)
                    lower,upper = net-margin,net+margin
                    scale,stop = lower>0,upper<=0
                    extend = ~(scale|stop)
                    ambiguity = .14 <= gamma <= .18
                    wrong = np.zeros(len(pairs),dtype=bool) if ambiguity else (stop if gamma>constants['g_star'] else scale)
                    rows.append(dict(n_per_arm=n,gamma=gamma,deff=deff,replicates=len(pairs),
                                     p_scale=float(scale.mean()),p_extend=float(extend.mean()),p_stop=float(stop.mean()),
                                     p_wrong_outside_ambiguity=None if ambiguity else float(wrong.mean()),
                                     wrong_mc_se=None if ambiguity else float(np.sqrt(wrong.mean()*(1-wrong.mean())/len(pairs))),
                                     ambiguity_zone=ambiguity,truth_scale=gamma>constants['g_star'],method='E3_observed',
                                     guardrail_breach_assumed=False,
                                     net_scale='100k frozen cohort: G*(observed trial effect/non-test gross coefficient)-K',
                                     tag='[E] simulation conditional on [A]; DEFF and economic transfer are assumptions'))
    pd.DataFrame(rows).to_csv(ADDONS/'results/wp2_decision_quality.csv',index=False)
    series=[]
    for n,color in ((5000,(0,126,134)),(7872,(189,125,20)),(10000,(91,110,129)),(20000,(24,43,65))):
        subset=[row for row in rows if row['n_per_arm']==n and row['deff']==1.1]
        series.append(dict(label=f'{n:,}/ARM SCALE, DEFF 1.1',x=[row['gamma'] for row in subset],
                           y=[row['p_scale'] for row in subset],color=color))
    line_plot(ADDONS/'figures/wp2_decision_map.png','WP2: CONDITIONAL COHORT-NET SCALE DECISIONS',
              'ASSUMED PREVENTION RATE','PROBABILITY OF SCALE DECISION',series,x_limits=(0,.3),y_limits=(0,1))
    return rows


def prior_metrics(a,b,constants):
    G,K = constants['G'],constants['K']
    threshold = K/G
    mean = a/(a+b)
    positive = float(stats.beta.sf(threshold,a,b))
    net_mean = G*mean-K
    evpi = G*(mean*special.betaincc(a+1,b,threshold)-threshold*positive)-max(0,net_mean)
    return dict(a=a,b=b,p_positive=positive,prior_net_mean=net_mean,evpi=float(evpi))


def posterior_moments(control,treatment,n,a,b,constants,grid_size=GRID_SIZE):
    gamma = (np.arange(grid_size)+.5)/grid_size
    centre = constants['p0']
    p0 = centre-.02+(np.arange(grid_size)+.5)*.04/grid_size
    q = p0[None,:]*(1-gamma[:,None])
    log_q,log_one_q = np.log(q),np.log1p(-q)
    log_c,log_one_c = np.log(p0),np.log1p(-p0)
    log_prior = stats.beta.logpdf(gamma,a,b)
    net = constants['G']*gamma-constants['K']
    result = np.empty((len(control),3))
    for first in range(0,len(control),8):
        c = control[first:first+8,None,None]
        t = treatment[first:first+8,None,None]
        log_weight = t*log_q+(n-t)*log_one_q+c*log_c+(n-c)*log_one_c+log_prior[None,:,None]
        log_weight -= np.max(log_weight,axis=(1,2),keepdims=True)
        weight = np.exp(log_weight)
        marginal = weight.sum(axis=2)
        marginal /= marginal.sum(axis=1,keepdims=True)
        result[first:first+8,0] = marginal@net
        result[first:first+8,1] = marginal@np.maximum(net,0)
        result[first:first+8,2] = marginal@np.maximum(-net,0)
    return result


def evsi_scenario(a,b,n,generator,constants):
    prior = prior_metrics(a,b,constants)
    gamma = generator.beta(a,b,PILOTS)
    p0 = generator.uniform(constants['p0']-.02,constants['p0']+.02,PILOTS)
    control = generator.binomial(n,p0)
    treatment = generator.binomial(n,p0*(1-gamma))
    moments = posterior_moments(control,treatment,n,a,b,constants)
    refined = posterior_moments(control[:64],treatment[:64],n,a,b,constants,800)
    refinement_error = float(np.max(np.abs(refined-moments[:64])))
    grid_size = GRID_SIZE
    if refinement_error>5:
        moments = posterior_moments(control,treatment,n,a,b,constants,800)
        grid_size = 800
        further = posterior_moments(control[:64],treatment[:64],n,a,b,constants,1600)
        refinement_error = float(np.max(np.abs(further-moments[:64])))
    posterior_net,positive,negative = moments.T
    regret = np.where(posterior_net>=0,negative,positive)
    centered_gain = np.maximum(-posterior_net,0) if prior['prior_net_mean']>=0 else np.maximum(posterior_net,0)
    direct = float(np.maximum(posterior_net,0).mean()-max(0,prior['prior_net_mean']))
    evsi = float(prior['evpi']-regret.mean())
    mc_se = float(regret.std(ddof=1)/np.sqrt(PILOTS))
    centered = float(centered_gain.mean())
    discrepancy_values = centered_gain+regret-prior['evpi']
    discrepancy_se = float(discrepancy_values.std(ddof=1)/np.sqrt(PILOTS))
    identity_pass = abs(centered-evsi)<=4*discrepancy_se+5
    large_gap = float(regret.mean())
    limit_pass = n!=1000000 or large_gap+1.96*mc_se+refinement_error<=max(5,.05*prior['evpi'])
    sample_path = ADDONS/f'results/wp2_posterior_a{a}_b{b}_n{n}.npz'
    np.savez_compressed(sample_path,gamma=gamma,p0=p0,control=control,treatment=treatment,moments=moments)
    return dict(**prior,n_per_arm=n,pilots=PILOTS,grid_size=[grid_size,grid_size],
                evsi_per_cohort=evsi,evsi_mc_se=mc_se,centered_evsi_per_cohort=centered,
                direct_formula_evsi_per_cohort=direct,
                direct_formula_mc_se=float(np.maximum(posterior_net,0).std(ddof=1)/np.sqrt(PILOTS)),
                centered_evsi_mc_se=float(centered_gain.std(ddof=1)/np.sqrt(PILOTS)),
                identity_discrepancy_mc_se=discrepancy_se,posterior_net_mean=float(posterior_net.mean()),
                posterior_regret_mean=large_gap,grid_refinement_max_dollars=refinement_error,
                horizons={str(h):dict(evsi=h*evsi,mc_se=h*mc_se,evpi=h*prior['evpi']) for h in (1,6,12)},
                acceptance=dict(nonnegative_evsi=evsi>=0,evsi_at_most_evpi=evsi<=prior['evpi'],
                                centered_identity_mc_agreement=identity_pass,grid_refinement_within_5_dollars=refinement_error<=5,
                                large_n_gap_upper_bound_within_5percent_or_5dollars=bool(limit_pass)),
                sample_artifact=file_info(sample_path),tag='[E] numerical preposterior value conditional on [A]')


def main():
    verify_runtime()
    constants = stored_constants()
    decisions = decision_quality()
    generator = rng(2)
    scenarios=[]
    for a,b in PRIORS:
        for n in (7872,1000000):
            row = evsi_scenario(a,b,n,generator,constants)
            scenarios.append(row)
            print(f'[E] WP2 Beta({a},{b}), n={n:,}: EVSI={row["evsi_per_cohort"]:.2f}; EVPI={row["evpi"]:.2f}',flush=True)
    acceptance = {f'a{row["a"]}_b{row["b"]}_n{row["n_per_arm"]}':row['acceptance'] for row in scenarios}
    passed = all(all(checks.values()) for checks in acceptance.values())
    status = 'DONE' if passed else 'PARTIAL'
    inputs=[ROOT/'v2_work/final_metrics.json',ADDONS/'results/wp1_power.json',ADDONS/'results/wp1_simulation_samples.npz']
    primary=[row for row in scenarios if row['n_per_arm']==7872]
    body=dict(status=status,decision_quality=decisions,scenarios=scenarios,acceptance=acceptance,
              assumptions=dict(p0=f'Uniform({constants["p0"]-.02:.12f}, {constants["p0"]+.02:.12f}) generative and inference prior; half-width 2 percentage points [A]',
                               prevention='Beta priors and uniform independent prevention are unverified [A]',
                               net='Frozen 100k cohort G*gamma-K; pilot coefficient maps observed outcomes to gamma. Economic transfer is assumed.',
                               guardrails='No breach is assumed for decision simulation, not observed safety.',horizons='1, 6, 12 identical future cohorts [A]'),
              method=dict(posterior='Midpoint quadrature on full support with exact Beta density and flat bounded p0 density; log stabilized binomial likelihood.',
                          primary_evsi='EVPI - E[posterior decision regret], mathematically equivalent to required preposterior formula; no clipping.',
                          cross_checks='Required direct formula and centered-gain identity retained with MCSE. Grid refined on first 64 pilots; full refinement if >$5.',
                          wrong_call='Wrong decisive scale/stop only; extend is not a wrong call; gamma .14-.18 excluded.',
                          large_n_tolerance='Posterior-regret mean + 1.96 MCSE + grid discrepancy <= max($5, 5% EVPI).'),
              artifacts=[file_info(ADDONS/'results/wp2_decision_quality.csv'),file_info(ADDONS/'figures/wp2_decision_map.png')])
    write_json('results/wp2_evsi.json',body,__file__,2,inputs,dict(decision_rows=len(decisions),pilots_per_scenario=PILOTS,scenarios=len(scenarios)))
    lo,hi=min(row['evsi_per_cohort'] for row in primary),max(row['evsi_per_cohort'] for row in primary)
    results=['| Prevention prior [A] | EVSI/cohort [E/A] | MC SE [E] | EVPI [E/A] |','|---|---:|---:|---:|']
    results += [f'| Beta({row["a"]},{row["b"]}) | ${row["evsi_per_cohort"]:,.2f} | ${row["evsi_mc_se"]:.2f} | ${row["evpi"]:,.2f} |' for row in primary]
    selected=next(row for row in decisions if row['n_per_arm']==7872 and row['gamma']==.2 and row['deff']==1.1)
    results += [f'[E/A] At 7,872/arm, 20% prevention and DEFF 1.1, scale/extend/stop probabilities are {selected["p_scale"]:.1%}/{selected["p_extend"]:.1%}/{selected["p_stop"]:.1%}; no guardrail breach is assumed.',
                f'[R] The pilot can be framed as the first production wave plus an option whose simulated information value is ${lo:,.0f}–${hi:,.0f} per future cohort across these priors. This is not approval to spend: the illustrative $12,872 also buys production contacts, so it is not a like-for-like pure research cost comparison.']
    checks=[f'- [E] {"PASS" if value else "FAIL"}: {key}, {criterion}.' for key,checks in acceptance.items() for criterion,value in checks.items()]
    write_report(2,'Pilot decision quality and EVSI',status,inputs,
                 ['- [A] Independent account trials, uniform prevention, assumed economics; no live treatment or household data.',
                  '- [A] Flat p0 prior centered on stored 4.7711%, half-width 2 pp; horizons 1/6/12 are assumptions.'],
                 '[E] Reused observable WP1 HC1 contrasts; mapped effects to frozen cohort net and inflated SE by DEFF. Applied scale/extend/stop rules and the ambiguity zone. Integrated full-support two-dimensional posteriors for 4,096 pilots per prior/sample size; computed regret, centered and direct EVSI identities, refinement and large-n checks.',
                 results,checks,
                 ['[E] Cohort economic transfer normalizes by the non-test gross-effect coefficient, preventing inconsistent fixed-cost allocation across sample sizes.',
                  '[E] Primary EVSI uses the equivalent posterior-regret identity for variance reduction, not clipping or optimistic bound adjustment.'],
                 '[E/A] Conditional decision probabilities, prior-sensitive information values and assumed cohort-horizon arithmetic.',
                 '[R] Actual causal profit, live clustered power, observed safety, or a claim that EVSI pays for the pilot.')
    print(f'[E] WP2 {status}: all outputs written; integration remains off.',flush=True)


if __name__ == '__main__':
    main()
