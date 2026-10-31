from pathlib import Path
from hashlib import sha256
import argparse
import json
import math

import numpy as np
import pandas as pd
from scipy.stats import norm
from threadpoolctl import threadpool_limits

from common import ROOT, WORK, SEED, THREADS, load_data, dump

REPLICATES = 400
GRID = (1000, 2500, 5000, 7872, 10000, 20000, 40000, 80000, 160000)
COVARIATES = ('totmrc_Mean', 'avg3rev', 'p_d')


def routing_inputs(data):
    return pd.DataFrame({'billing_gap': ((data.avg3rev - data.avg6rev).abs() / data.avg6rev.clip(lower=1)).to_numpy(),
                         'absolute_change_rev': data.change_rev.abs().to_numpy(),
                         'failed_call_ratio': (data.drop_blk_Mean / data.attempt_Mean.clip(lower=1)).to_numpy(),
                         'mou': data.mou_Mean.to_numpy()}, index=data.Customer_ID)


def routing_spec(data, train):
    inputs = routing_inputs(data)
    return {'billing_gap_p90': float(inputs.billing_gap.iloc[train].quantile(.9)),
            'absolute_change_rev_p90': float(inputs.absolute_change_rev.iloc[train].quantile(.9)),
            'failed_call_ratio_p90': float(inputs.failed_call_ratio.iloc[train].quantile(.9)),
            'low_usage_p25': float(data.mou_Mean.iloc[train].quantile(.25)),
            'handset_days': 365, 'training_rows': len(train),
            'precedence': ['billing_check', 'network_check', 'handset_check', 'digital_only_residual'],
            'window_caveat': 'No Range columns. Billing uses verified 3/6-month comparisons and separately an ambiguously scaled change_rev flag, never an inferred Mean window or causal promo expiry.',
            'residual_caveat': 'The fourth queue is a low-usage DIGITAL CHECK plus all remaining cases; not every residual is demonstrably low usage. Missing diagnostics do not prove a defect.'}


def covariates(frame, data, train, limits=None):
    source = data.set_index('Customer_ID')
    if limits is None:
        limits = {}
        for column in COVARIATES[:-1]:
            training = data.iloc[train][column].clip(lower=0)
            limits[column] = {'median': float(training.median()), 'p99': float(training.quantile(.99))}
    columns = []
    for column in COVARIATES[:-1]:
        limits_c = limits[column]
        columns.append(source.loc[frame.Customer_ID, column].clip(lower=0).fillna(limits_c['median']).clip(upper=limits_c['p99']).to_numpy())
    columns.append(frame.p_d.to_numpy())
    return np.column_stack(columns), limits


def fit_adjustment(frame, X):
    core = frame.selected_bayes.to_numpy(dtype=bool)
    w = frame.weight.to_numpy()[core]
    Z = np.c_[np.ones(core.sum()), X[core]]
    outcome = 3.6 * frame.value.to_numpy()[core] * (1 - frame.y.to_numpy()[core])
    beta = np.linalg.lstsq(Z * np.sqrt(w[:, None]), outcome * np.sqrt(w), rcond=None)[0]
    return beta.tolist()


def cells(frame):
    risk = frame.selected_risk.to_numpy(dtype=bool)
    bayes = frame.selected_bayes.to_numpy(dtype=bool)
    labels = np.select([risk & bayes, bayes & ~risk, risk & ~bayes],
                       ['both', 'rv_only', 'risk_only'], default='exploration')
    assert len(labels) == len(frame)
    return labels


def cell_summary(frame):
    labels = cells(frame)
    w, y, v = frame.weight.to_numpy(), frame.y.to_numpy(), frame.value.to_numpy()
    records = []
    for label in ('both', 'rv_only', 'risk_only', 'exploration'):
        mask = labels == label
        mass = float(w[mask].sum())
        records.append({'cell': label, 'raw_count': int(mask.sum()), 'deployment_mass': mass,
                        'population_share': mass / float(w.sum()),
                        'mean_bill': float(np.average(v[mask], weights=w[mask])) if mass else None,
                        'deployment_churn_proxy': float(np.dot(w[mask], y[mask]) / mass) if mass else None,
                        'at_risk_value': float(np.dot(w[mask], y[mask] * v[mask]))})
    assert sum(r['raw_count'] for r in records) == len(frame)
    assert np.isclose(sum(r['deployment_mass'] for r in records), w.sum())
    return records


def design(frame, data, train):
    v1 = json.loads((ROOT / 'v1_frozen/analysis_outputs/summary.json').read_text(encoding='utf-8'))
    pilot = v1['pilot']
    p0, p1 = pilot['illustrative_control_churn'], pilot['illustrative_treatment_churn']
    average = (p0 + p1) / 2
    n_normal = math.ceil((norm.ppf(.975) * math.sqrt(2 * average * (1 - average)) + norm.ppf(.8) * math.sqrt(p0 * (1 - p0) + p1 * (1 - p1))) ** 2 / (p0 - p1) ** 2)
    n_core = math.ceil(n_normal / .9)
    assert n_normal == 7084 and n_core == 7872
    allocation = {'core_per_arm': n_core, 'risk_only_per_arm_stage2': 2000, 'exploration_per_arm_stage2': 1000}
    cost = {'treated_contact': 1., 'control_incremental_contact': 0., 'startup_stage1': 5000., 'incremental_stage2_fixed': 0.}
    stage1 = cost['startup_stage1'] + n_core * cost['treated_contact']
    stage2 = 3000 * cost['treated_contact'] + cost['incremental_stage2_fixed']
    counts = cell_summary(frame)
    share = {row['cell']: row['population_share'] for row in counts}
    required = max(2 * n_core / (share['both'] + share['rv_only']), 4000 / share['risk_only'], 2000 / share['exploration'])
    planning_portfolio = int(math.ceil(required / 1000) * 1000)
    X, limits = covariates(frame, data, train)
    enroll = {'both': min(1., 2 * n_core / (planning_portfolio * (share['both'] + share['rv_only']))),
              'rv_only': min(1., 2 * n_core / (planning_portfolio * (share['both'] + share['rv_only']))),
              'risk_only': min(1., 4000 / (planning_portfolio * share['risk_only'])),
              'exploration': min(1., 2000 / (planning_portfolio * share['exploration']))}
    assert all(0 < rate <= 1 for rate in enroll.values())
    return {'protocol': 'B1-B5 frozen calibration planning, not observed treatment evidence',
            'seed': SEED, 'threads': THREADS, 'selection_partition': 'calibration_policy', 'test_selected': False,
            'maturity_ladder': ['risk-only triage (benchmark)', 'value-aware service triage (PoC)', 'causal incremental-profit targeting (requires pilot labels)'],
            'normal_binary_reference': {'p0': p0, 'p1': p1, 'relative_prevention_assumption': .2,
                                        'alpha_two_sided': .05, 'power': .8, 'followup_loss_allowance': .1,
                                        'minimum_complete_per_arm': n_normal, 'enrolled_per_arm': n_core,
                                        'provenance': 'Previously published v1 planning reference, retained rather than retuned on v2 test.'},
            'allocation': allocation, 'cost_assumptions': cost,
            'stage1_cost': stage1, 'stage2_incremental_cost': stage2, 'total_staged_cost': stage1 + stage2,
            'stage1_total_enrolled': 2 * n_core, 'stage2_incremental_enrolled': 6000,
            'stage2_power_claim': '2000/arm risk-only and 1000/arm exploration are assumed learning allocations, NOT powered evidence of positive contribution.',
            'stage_cost_caveat': 'Illustrative contact/startup envelope only; shared measurement is assumed existing. Actual linkage, consent, engineering, clustering, follow-up and legal costs must be quoted before launch. No subsidy/discount.',
            'planning_portfolio_calibration_proxy': planning_portfolio,
            'capacity_caveat': 'Stage 1 needs 15744 core accounts, exceeding a single approximately10000-account top list in a100000-account scenario. Enroll across a larger eligible portfolio or successive cohorts; do not equate the pilot with one financial-scenario cohort.',
            'enrollment_probability_planning_proxy': enroll, 'treatment_probability_given_enrollment': .5,
            'randomization_unit': 'Linked household/account, linkage required before launch; Customer_ID is not claimed to be household-disjoint.',
            'stratification': 'Cell and pre-treatment risk-value band; account clusters stay in one arm.',
            'cell_disjointness': 'both+rv_only are stage1 core; rv_only is never enrolled twice. Stage2 adds risk_only and below-union exploration, each disjoint from stage1.',
            'logging': ['eligibility/consent', 'household linkage', 'cell/risk-value stratum', 'enrollment probability', 'treatment probability', 'assignment/contact', 'pre-period covariates', 'churn/contribution/costs', 'opt-out/complaint/harm'],
            'ipw_rule': 'Within eligible consented linked accounts use joint e_T=s*.5, e_C=s*.5; HT/IPW contrast T*Y/e_T-C*Y/e_C, including outcome-specific contact costs. Only the agreed region (both) cancels in the Bayes-minus-risk policy contrast: deployment-mass-weighted incremental contribution in rv_only minus that in risk_only; stage1 core includes rv_only and must not be cancelled as a whole. Exploration gives positive support below both cutoffs. Consent/nonresponse and household clustering require separate treatment; no unbiased claim for unconsented/unobserved accounts.',
            'routing': routing_spec(data, train), 'covariate_limits_train_only': limits,
            'calibration_only_adjustment_beta': fit_adjustment(frame, X),
            'simulation': {'replicates': REPLICATES, 'enrolled_n_grid': list(GRID), 'prevention': .2,
                           'retained_months': 6, 'margin': .6, 'variable_cost': 1., 'startup': 5000.,
                           'outcome': 'Simulated six-month contribution=3.6*V*(1-future_churn)-treatment_contact_cost; treatment prevents20% of otherwise churners. Assumes six-month contribution is lost when the specified future-month churn event occurs.',
                           'effective_n': 'floor(.9*enrolled), random missing follow-up proxy; full enrolled treatment cost and startup still charged.',
                           'adjustment': 'Fixed weighted OLS control-outcome coefficients fit on calibration rows only, covariate preprocessing on original60k; test never fits adjustment.',
                           'required_n_rule': 'Smallest preregistered grid point with simulated power>=.8; Monte Carlo Wilson95% interval reported. Beyond-grid requirements recorded unavailable. Final test required_n is descriptive, never a new enrollment decision.',
                           'honesty': 'No longitudinal pre/post contribution pairs or treatment/control labels. This cross-sectional independent-account proxy is NOT measured CUPED, causal lift or household-clustered profit power; re-estimate from live pre-period billing and clustering.'},
            'decision_gates': {'scale': 'Final cluster-robust95% LCB of incremental contribution after all contact/incentive/implementation costs >0 AND no guardrail breach; report policy value with logged enrollment/assignment propensities.',
                               'extend': 'Contribution CI overlaps0 with positive upper bound, no harm, and a prospectively approved maximum-sample/budget extension; no unplanned optional peeking.',
                               'stop': 'Contribution upper bound<=0, infeasible fully loaded costs, or customer-harm guardrail.',
                               'harm_stratum': 'mou_Mean<=original60k p25 AND ovrrev_Mean=0 AND custcare_Mean=0; missing diagnostic is not zero.',
                               'harm_looks': [0.5, 1.], 'one_sided_alpha_per_harm_look': .005,
                               'harm_stop': 'Positive treatment-minus-control churn and one-sided Fisher exact p<=.005 at either planned look; familywise alpha<=.01 for this stratum. Serious complaints/consent violations trigger immediate safety escalation independent of statistical significance.',
                               'source_scope': 'Ascarza2016 tested plan recommendations, not this exact stratum/action. The low-usage guardrail is a preregistered safety hypothesis, not an established backfire segment.'}}


def wilson(successes, total):
    p = successes / total
    z = norm.ppf(.975)
    denominator = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denominator
    half = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return centre - half, centre + half


def power(frame, X, spec, partition):
    core = frame.selected_bayes.to_numpy(dtype=bool)
    w = frame.weight.to_numpy()[core]
    p = w / w.sum()
    y = frame.y.to_numpy()[core]
    v = frame.value.to_numpy()[core]
    gross = 3.6 * v
    baseline = gross * (1 - y)
    beta = np.asarray(spec['calibration_only_adjustment_beta'])
    prediction = np.c_[np.ones(core.sum()), X[core]] @ beta
    residual = baseline - prediction
    p0 = float(np.dot(p, y))
    rng = np.random.default_rng(SEED + 2100)
    records = []
    for enrolled in GRID:
        n = int(math.floor(enrolled * .9))
        control_events = rng.binomial(n, p0, REPLICATES)
        treatment_events = rng.binomial(n, p0 * .8, REPLICATES)
        pool = (control_events + treatment_events) / (2 * n)
        se_binary = np.sqrt(2 * pool * (1 - pool) / n)
        binary_success = ((control_events - treatment_events) / n > norm.ppf(.975) * se_binary).sum()
        success = {'binary_churn': int(binary_success), 'unadjusted_contribution': 0, 'adjusted_contribution': 0}
        variance_ratios = []
        for first in range(0, REPLICATES, 20):
            batch = min(20, REPLICATES - first)
            ic = rng.choice(len(y), size=(batch, n), p=p)
            it = rng.choice(len(y), size=(batch, n), p=p)
            prevented = (rng.random((batch, n)) < .2) & y[it].astype(bool)
            yc = baseline[ic]
            yt = baseline[it] + gross[it] * prevented - 1.
            rc = residual[ic]
            rt = residual[it] + gross[it] * prevented - 1.
            for method, control, treatment in (('unadjusted_contribution', yc, yt), ('adjusted_contribution', rc, rt)):
                delta = treatment.mean(axis=1) - control.mean(axis=1) - 5000 / enrolled
                se = np.sqrt(control.var(axis=1, ddof=1) / n + treatment.var(axis=1, ddof=1) / n)
                success[method] += int((delta > norm.ppf(.975) * se).sum())
            variance_ratios.extend(((rc.var(axis=1) + rt.var(axis=1)) / (yc.var(axis=1) + yt.var(axis=1))).tolist())
        for method, count in success.items():
            lower, upper = wilson(count, REPLICATES)
            records.append({'partition': partition, 'method': method, 'enrolled_per_arm': enrolled,
                            'effective_per_arm': n, 'simulated_power': count / REPLICATES,
                            'mc_lower': lower, 'mc_upper': upper, 'replicates': REPLICATES,
                            'core_churn_proxy': p0, 'expected_variable_incremental_contribution': float(np.dot(p, y * gross) * .2 - 1),
                            'startup_per_treated_enrollee': 5000 / enrolled,
                            'mean_adjusted_to_unadjusted_variance_ratio': float(np.mean(variance_ratios)),
                            'test_selected_design': False, 'claim_type': 'cross-sectional simulated planning proxy'})
        print(f'B {partition} MC n={enrolled:,}/arm: ' + ', '.join(f'{method}={count/REPLICATES:.1%}' for method, count in success.items()), flush=True)
    return records


def route(frame, data, spec):
    indexed = data.set_index('Customer_ID').loc[frame.Customer_ID]
    r = spec['routing']
    inputs = routing_inputs(data).loc[frame.Customer_ID]
    billing = (inputs.billing_gap >= r['billing_gap_p90']) | (inputs.absolute_change_rev >= r['absolute_change_rev_p90'])
    network = (inputs.failed_call_ratio >= r['failed_call_ratio_p90']) & (inputs.failed_call_ratio > 0)
    handset = indexed.eqpdays > r['handset_days']
    labels = np.select([billing, network, handset], [1, 2, 3], default=4)
    selected = frame.selected_bayes.to_numpy(dtype=bool)
    low_usage = indexed.mou_Mean.le(r['low_usage_p25']).to_numpy()
    harm = low_usage & indexed.ovrrev_Mean.eq(0).to_numpy() & indexed.custcare_Mean.eq(0).to_numpy()
    w, y, v = frame.weight.to_numpy(), frame.y.to_numpy(), frame.value.to_numpy()
    total = float(np.dot(w[selected], y[selected] * v[selected]))
    rows = []
    for number, name in enumerate(r['precedence'], 1):
        mask = selected & (labels == number)
        mass = float(w[mask].sum())
        at_risk = float(np.dot(w[mask], y[mask] * v[mask]))
        rows.append({'queue': number, 'name': name, 'raw_count': int(mask.sum()), 'weighted_contacts': mass,
                     'mean_bill': float(np.average(v[mask], weights=w[mask])) if mass else None,
                     'at_risk_value': at_risk, 'share_at_risk_value': at_risk / total,
                     'raw_low_usage': int((mask & low_usage).sum()), 'raw_harm_stratum': int((mask & harm).sum()),
                     'operational_hypothesis_not_cause': True})
    assert sum(row['raw_count'] for row in rows) == int(selected.sum())
    assert np.isclose(sum(row['share_at_risk_value'] for row in rows), 1)
    assignments = pd.DataFrame({'Customer_ID': frame.Customer_ID, 'selected_bayes': selected,
                                'queue': labels, 'cell': cells(frame), 'harm_monitor_stratum': harm,
                                'low_usage': low_usage})
    return rows, assignments


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--partition', choices=('calibration', 'test'), default='calibration')
    args = parser.parse_args(argv)
    threadpool_limits(limits=THREADS)
    data, splits = load_data()
    frame = pd.read_csv(WORK / f'a_selected_{args.partition}.csv')
    expected = splits['calibration_policy' if args.partition == 'calibration' else 'test']
    assert set(frame.Customer_ID) == set(data.Customer_ID.iloc[expected])
    target = WORK / 'b_design.json'
    if args.partition == 'calibration':
        assert not (WORK / 'final_frozen_protocol.json').exists(), 'Do not alter a frozen pilot design.'
        spec = design(frame, data, splits['train'])
        dump('b_design.json', spec)
    else:
        from final_protocol import verify
        verify()
        spec = json.loads(target.read_text(encoding='utf-8'))
        assert not (WORK / 'b_summary_test.json').exists(), 'Do not rerun final test pilot diagnostics.'
    X, _ = covariates(frame, data, splits['train'], spec['covariate_limits_train_only'])
    simulation = power(frame, X, spec, args.partition)
    queues, assignments = route(frame, data, spec)
    cell_rows = cell_summary(frame)
    required = {}
    for method in ('binary_churn', 'unadjusted_contribution', 'adjusted_contribution'):
        passing = [row['enrolled_per_arm'] for row in simulation if row['method'] == method and row['simulated_power'] >= .8]
        required[method] = min(passing) if passing else None
    pd.DataFrame(simulation).to_csv(WORK / f'b_power_{args.partition}.csv', index=False)
    pd.DataFrame(queues).to_csv(WORK / f'b_queues_{args.partition}.csv', index=False)
    pd.DataFrame(cell_rows).to_csv(WORK / f'b_cells_{args.partition}.csv', index=False)
    assignments.to_csv(WORK / f'b_assignments_{args.partition}.csv', index=False)
    result = {'partition': args.partition, 'spec': spec, 'queues': queues, 'cells': cell_rows,
              'simulated_required_enrolled_per_arm_grid': required,
              'power_rows': simulation, 'design_selected_on_test': False,
              'a_selected_sha256': sha256((WORK / f'a_selected_{args.partition}.csv').read_bytes()).hexdigest(),
              'disjoint_cells_and_exclusive_queues_verified': True,
              'service_fix_floor': 'Verified billing/network defects must be remediated regardless of bill or proactive-list selection.',
              'simulation_scope': spec['simulation']['honesty']}
    dump(f'b_summary_{args.partition}.json', result)
    dump('b_summary.json', result)
    report = f"# B1–B5 — {args.partition} planning evidence\n\n" + '\n'.join([
        'Risk-only benchmark → value-aware service triage → causal incremental-profit targeting after pilot labels.',
        f"Stage 1: {spec['stage1_total_enrolled']:,} linked accounts, {spec['stage1_cost']:,.0f} assumed dollars. Stage 2 adds {spec['stage2_incremental_enrolled']:,} accounts and {spec['stage2_incremental_cost']:,.0f} dollars; total {spec['total_staged_cost']:,.0f}. These are contact/startup envelopes, not quoted fully loaded launch budgets.",
        spec['capacity_caveat'], spec['cell_disjointness'], spec['ipw_rule'],
        'Simulated minimum grid n/arm: ' + json.dumps(required) + '. Null means no80% power established through160000/arm.',
        spec['simulation']['honesty'], spec['routing']['window_caveat'], spec['routing']['residual_caveat'],
        spec['decision_gates']['scale'], spec['decision_gates']['harm_stop'], spec['decision_gates']['source_scope'],
        'Service-Fix Floor is mandatory. No household-disjoint analysis, actual treatment effect, unbiased live uplift/Qini, or production churn baseline is claimed.'])
    (WORK / f'b_report_{args.partition}.md').write_text(report + '\n', encoding='utf-8')
    print('B completed:', args.partition, required, flush=True)
    return result


if __name__ == '__main__':
    main()
