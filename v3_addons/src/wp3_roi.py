"""WP3 code only: run explicitly after WP2 has published its terminal report.

The frozen-threshold ROI uses quoted G/K, never test rows. Budget replay uses
calibration-policy OOF scores only. New curves are conditional, non-test
scenarios, not a budget optimization or a promoted prospective policy.
"""

# Install the addons runtime/write guard and thread limits before numerical imports.
from common import (
    ADDONS, ROOT, rng, stored_constants, weights, population,
    write_json, verify_runtime, file_info,
)

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import integrate, special, stats

from reporting import write_report
from png_drafts import line_plot

TASK_INDEX = 3
DRAWS_PER_PRIOR = 1_000_000
PRIORS = ((6, 14), (6, 24), (2, 18))
COSTS = (.25, 1., 2., 5.)
LEGACY_SAMPLE_PRIOR = .4956  # Exact v2 replay; deliberately NOT addons' .49562.
DEPLOYMENT_PRIOR = .02
DEPLOYMENT_SIZE = 100_000
RETAINED_MONTHS = 6
MARGIN = .60
FIXED_COST = 5000.
HORIZON = 12
PROBABILITY_TOLERANCE = .005
DOLLAR_RELATIVE_TOLERANCE = .01
GRID_STEP = .01
GRID_FLOAT_EPSILON = 1e-12
NAME = 'prior-integrated net at the frozen 10% threshold'
BRIEF_REFERENCES = {
    (6, 14): dict(p_positive=.930, expected_net=13113., net_5pct=-1173., evpi_per_cohort=196.),
    (6, 24): dict(p_positive=.685, expected_net=3747., net_5pct=-6166., evpi_per_cohort=1093.),
    (2, 18): dict(p_positive=.168, expected_net=-5619., net_5pct=-13202., evpi_per_cohort=832.),
}
BRIEF_BUDGETS = {.25: .30, 1.: .18, 2.: .03, 5.: .01}


def record_check(checks, name, passed, **audit):
    checks[name] = dict(passed=bool(passed), **audit)


def compare(checks, name, actual, reference, probability=False):
    """Keep signed/absolute deviations; never alter an estimate to pass a check."""
    actual, reference = float(actual), float(reference)
    difference = actual - reference
    absolute = abs(difference)
    relative = absolute / abs(reference) if reference != 0 else None
    finite = np.isfinite(actual) and np.isfinite(reference)
    if probability:
        passed = finite and absolute <= PROBABILITY_TOLERANCE
        tolerance = dict(absolute=PROBABILITY_TOLERANCE)
    else:
        passed = finite and (relative <= DOLLAR_RELATIVE_TOLERANCE
                             if relative is not None else absolute == 0)
        tolerance = dict(relative=DOLLAR_RELATIVE_TOLERANCE, denominator='abs(reference)')
    record_check(checks, name, passed, actual=actual, reference=reference,
                 signed_deviation=difference, absolute_deviation=absolute,
                 relative_deviation=relative, tolerance=tolerance)


def require_wp2_finished():
    """Do not start WP3 while WP2 is running or has not published its report."""
    result_path = ADDONS / 'results/wp2_evsi.json'
    report_path = ADDONS / 'reports/WP2_report.md'
    if not result_path.is_file() or not report_path.is_file():
        raise RuntimeError('WP3 not started: WP2 must publish its result and terminal report first.')
    body = json.loads(result_path.read_text(encoding='utf-8'))
    status = body.get('status')
    report = report_path.read_text(encoding='utf-8')
    if status not in ('DONE', 'PARTIAL') or f'Status: {status}' not in report.splitlines():
        raise RuntimeError('WP3 not started: WP2 result/report do not agree on a terminal status.')
    return dict(status=status, result=file_info(result_path), report=file_info(report_path),
                note='Terminal completion establishes order, not approval of WP2 checks.')


def prior_metrics(a, b, constants, generator, checks):
    G, K = float(constants['G']), float(constants['K'])
    threshold = K / G
    distribution = stats.beta(a, b)
    mean = float(distribution.mean())
    probability = float(special.betaincc(a, b, threshold))
    eplus = float(mean * special.betaincc(a + 1, b, threshold) - threshold * probability)
    eplus_quad, quad_error = integrate.quad(
        lambda gamma: (gamma - threshold) * distribution.pdf(gamma),
        threshold, 1., epsabs=1e-12, epsrel=1e-12,
    )
    expected_net = G * mean - K
    expected_positive_net = G * eplus
    evpi = expected_positive_net - max(0., expected_net)  # Definition, not estimate clipping.
    closed = dict(p_positive=probability, expected_net=expected_net,
                  net_5pct=float(G * distribution.ppf(.05) - K),
                  eplus=eplus, expected_positive_net=expected_positive_net,
                  evpi_per_cohort=evpi, evpi_horizon12=HORIZON * evpi)
    prefix = f'a{a}_b{b}'
    quad_difference = abs(eplus - eplus_quad)
    record_check(checks, prefix + '.eplus_quad', quad_difference < 1e-9,
                 closed_form=eplus, quadrature=float(eplus_quad),
                 absolute_deviation=quad_difference, strict_absolute_tolerance=1e-9,
                 quadrature_error_estimate=float(quad_error))
    sf = float(distribution.sf(threshold))
    record_check(checks, prefix + '.beta_sf_vs_betaincc', abs(sf - probability) <= 1e-12,
                 beta_sf=sf, betaincc=probability, absolute_deviation=abs(sf - probability),
                 absolute_tolerance=1e-12)

    # Preregistered randomized stratification: one independent random location in
    # each uniform stratum, followed by the Beta inverse CDF. The resulting
    # ordered Beta draws are NOT iid. No iid MC SE or iid quantile CI is claimed.
    uniform = (np.arange(DRAWS_PER_PRIOR, dtype=float)
               + generator.random(DRAWS_PER_PRIOR)) / DRAWS_PER_PRIOR
    gamma = distribution.ppf(uniform)
    net = G * gamma - K
    mc_mean = float(net.mean())
    mc_eplus = float(np.maximum(gamma - threshold, 0.).mean())
    mc_positive_net = float(np.maximum(net, 0.).mean())
    mc_evpi = mc_positive_net - max(0., mc_mean)
    mc = dict(p_positive=float(np.mean(net > 0)), expected_net=mc_mean,
              net_5pct=float(np.quantile(net, .05, method='linear')),
              eplus=mc_eplus, expected_positive_net=mc_positive_net,
              evpi_per_cohort=mc_evpi, evpi_horizon12=HORIZON * mc_evpi)
    record_check(checks, prefix + '.stratified_draws',
                 DRAWS_PER_PRIOR >= 1_000_000 and np.isfinite(gamma).all()
                 and np.all((gamma >= 0) & (gamma <= 1)),
                 draws=DRAWS_PER_PRIOR, minimum_draws=1_000_000,
                 sampling='(arange(N) + rng(3).random(N)) / N, transformed by scipy.stats.beta.ppf; non-iid')
    for metric in ('p_positive', 'expected_net', 'net_5pct', 'expected_positive_net',
                   'evpi_per_cohort', 'evpi_horizon12'):
        compare(checks, prefix + '.mc_vs_closed.' + metric, mc[metric], closed[metric],
                probability=metric == 'p_positive')
    compare(checks, prefix + '.mc_vs_closed.eplus', mc_eplus, eplus)
    for metric, reference in BRIEF_REFERENCES[(a, b)].items():
        compare(checks, prefix + '.closed_vs_brief.' + metric, closed[metric], reference,
                probability=metric == 'p_positive')
        compare(checks, prefix + '.mc_vs_brief.' + metric, mc[metric], reference,
                probability=metric == 'p_positive')
    for method, values in (('closed', closed), ('mc', mc)):
        compare(checks, prefix + f'.{method}_vs_brief.evpi_horizon12',
                values['evpi_horizon12'], HORIZON * BRIEF_REFERENCES[(a, b)]['evpi_per_cohort'])
        record_check(checks, prefix + f'.{method}.finite_nonnegative_evpi',
                     all(np.isfinite(value) for value in values.values())
                     and values['evpi_per_cohort'] >= 0,
                     evpi=values['evpi_per_cohort'], no_clipping=True)
    return dict(a=a, b=b, label=f'Beta({a},{b})', gamma_mean=mean, g_star=threshold,
                closed_form=closed, monte_carlo=mc,
                quadrature=dict(eplus=float(eplus_quad), error_estimate=float(quad_error),
                                absolute_difference=quad_difference),
                brief_reference=BRIEF_REFERENCES[(a, b)],
                draws=DRAWS_PER_PRIOR, tag='[E] integration conditional on [A] prevention/economics')


def validate_frame(frame, expected_ids, expected_count, probability_column, partition=None):
    if len(frame) != expected_count or len(expected_ids) != expected_count:
        raise ValueError(f'Expected exactly {expected_count} eligible rows and split IDs.')
    if frame.Customer_ID.duplicated().any() or set(frame.Customer_ID.astype(int)) != expected_ids:
        raise ValueError('Customer IDs must be unique and exactly match the allowed split IDs.')
    if partition is not None and not frame.partition.eq(partition).all():
        raise ValueError('Calibration replay contains a non-calibration partition.')
    y = frame.y.to_numpy(dtype=float)
    p = frame[probability_column].to_numpy(dtype=float)
    value = frame.value.to_numpy(dtype=float)
    if not np.isin(y, (0., 1.)).all() or not 0 < y.sum() < len(y):
        raise ValueError('Binary churn outcomes with both classes are required; these are not treatment labels.')
    if not (np.isfinite(p).all() and np.all((p >= 0) & (p <= 1))
            and np.isfinite(value).all() and np.all(value >= 0)):
        raise ValueError('Invalid probabilities or recurring-value proxy; no imputation/tuning in WP3.')


def budget_grid(score, weight, y, value, percentages):
    """Exact v2 stable weighted cutoff; >= includes all boundary-score ties."""
    order = np.argsort(-np.asarray(score), kind='stable')
    cumulative = np.cumsum(np.asarray(weight)[order])
    total = float(np.sum(weight))
    rows = []
    for percentage in percentages:
        fraction = percentage / 100.
        index = min(np.searchsorted(cumulative, total * fraction), len(order) - 1)
        threshold = float(score[order[index]])
        selected = score >= threshold
        contacts = float(np.sum(weight * selected))
        actual_value = float(np.sum(weight * selected * y * value))
        rows.append(dict(intended_fraction=fraction, threshold=threshold,
                         achieved_contact_fraction=contacts / total, contacts=contacts,
                         raw_count=int(np.count_nonzero(selected)),
                         selected_churn_value=actual_value,
                         boundary_ties=int(np.count_nonzero(score == threshold))))
    return rows


def quote_budget_choices(checks):
    path = ROOT / 'v2_work/a_budget_choices.csv'
    frame = pd.read_csv(path)
    required = {'cost', 'fraction', 'calibration_oof_net', 'frozen_threshold', 'no_contact_net'}
    if not required <= set(frame.columns) or len(frame) != len(COSTS):
        raise ValueError('Stored budget table has an unexpected schema or row count.')
    if frame.cost.duplicated().any() or set(frame.cost) != set(COSTS):
        raise ValueError('Stored budget table does not contain the four preregistered costs.')
    numeric = frame[list(required)].to_numpy(dtype=float)
    if not np.isfinite(numeric).all():
        raise ValueError('Nonfinite stored budget quote.')
    quotes = frame.to_dict(orient='records')
    for row in quotes:
        cost = float(row['cost'])
        delta = float(row['fraction']) - BRIEF_BUDGETS[cost]
        record_check(checks, f'budget.stored_vs_brief.cost_{cost:g}',
                     abs(delta) <= GRID_STEP + GRID_FLOAT_EPSILON,
                     stored_fraction=float(row['fraction']), brief_fraction=BRIEF_BUDGETS[cost],
                     signed_deviation=delta, tolerance=GRID_STEP,
                     source=file_info(path), tag='[E] quoted stored calibration-only diagnostic')
        record_check(checks, f'budget.no_contact.cost_{cost:g}', row['no_contact_net'] == 0.,
                     quoted_no_contact_net=float(row['no_contact_net']), reference=0.,
                     note='No contact means no campaign and no startup charge; reported separately.')
    return quotes


def reproduce_budget(split, quotes, checks):
    audit = dict(passed=False, status='NOT_REPRODUCED', stored_choices=quotes,
                 no_contact_net=0., rows=0, replay_grid=[], winners=[],
                 legacy_sample_prior=LEGACY_SAMPLE_PRIOR, deployment_prior=DEPLOYMENT_PRIOR,
                 deployment_size=DEPLOYMENT_SIZE, success=.2, retained_months=RETAINED_MONTHS,
                 margin=MARGIN, fixed_startup=FIXED_COST,
                 score='expit(logit(clip(p_s_oof,1e-6,1-1e-6))+logit(.02)-logit(.4956))*value',
                 cutoff='Stable descending score; left searchsorted at fraction*sum(w); include all score >= cutoff ties.',
                 net='sum(w*mask*y*value)*.2*3.6 - cost*contacts - 5000',
                 prohibition='Stored frozen_threshold and in-sample p_s are not used for OOF budget replay.')
    try:
        frame = pd.read_csv(ROOT / 'v2_work/a_selected_calibration.csv',
                            usecols=['Customer_ID', 'partition', 'p_s_oof', 'y', 'value'],
                            dtype={'Customer_ID': 'int64'})
        audit['rows'] = len(frame)
        if split.Customer_ID.duplicated().any():
            raise ValueError('Split manifest contains duplicate IDs.')
        allowed = set(split.loc[split.partition.eq('calibration_policy'), 'Customer_ID'].astype(int))
        validate_frame(frame, allowed, 10_000, 'p_s_oof', partition='calibration_policy')
        record_check(checks, 'budget.calibration_ids', True, rows=len(frame),
                     expected_rows=10_000, split='calibration_policy', test_rows_used=0)
        y, value = frame.y.to_numpy(dtype=float), frame.value.to_numpy(dtype=float)
        p = frame.p_s_oof.to_numpy(dtype=float)
        shifted = special.expit(special.logit(np.clip(p, 1e-6, 1 - 1e-6))
                                + special.logit(DEPLOYMENT_PRIOR)
                                - special.logit(LEGACY_SAMPLE_PRIOR))
        weight = weights(y, prior=DEPLOYMENT_PRIOR, population_size=DEPLOYMENT_SIZE)
        record_check(checks, 'budget.weight_mass', abs(float(weight.sum()) - DEPLOYMENT_SIZE) <= 1e-8,
                     actual=float(weight.sum()), reference=DEPLOYMENT_SIZE, absolute_tolerance=1e-8)
        grid = budget_grid(shifted * value, weight, y, value, range(1, 31))
        for cost in COSTS:
            candidates = [dict(cost=cost, **row,
                               net=row['selected_churn_value'] * .2 * 3.6
                               - cost * row['contacts'] - FIXED_COST) for row in grid]
            # Python max returns the first maximum, matching the legacy 1..30% loop.
            winner = max(candidates, key=lambda row: row['net'])
            stored = next(row for row in quotes if row['cost'] == cost)
            delta = winner['intended_fraction'] - float(stored['fraction'])
            record_check(checks, f'budget.winner.cost_{cost:g}',
                         abs(delta) <= GRID_STEP + GRID_FLOAT_EPSILON,
                         reproduced_fraction=winner['intended_fraction'],
                         stored_fraction=float(stored['fraction']), signed_deviation=delta,
                         tolerance=GRID_STEP)
            matches = [row for row in candidates
                       if abs(row['intended_fraction'] - float(stored['fraction'])) <= GRID_FLOAT_EPSILON]
            if len(matches) != 1:
                raise ValueError('Stored fraction is not on the legacy 1..30% grid.')
            stored_fraction_net = matches[0]['net']
            net_difference = stored_fraction_net - float(stored['calibration_oof_net'])
            record_check(checks, f'budget.stored_fraction_net.cost_{cost:g}', abs(net_difference) <= 1e-6,
                         reproduced_net=stored_fraction_net,
                         quoted_net=float(stored['calibration_oof_net']),
                         signed_deviation=net_difference, absolute_tolerance=1e-6,
                         note='Additional exact-replay arithmetic audit, not a retuned winner criterion.')
            audit['winners'].append(dict(**winner, stored_fraction=float(stored['fraction']),
                                         fraction_deviation=delta,
                                         quoted_calibration_oof_net=float(stored['calibration_oof_net']),
                                         net_at_stored_fraction=stored_fraction_net,
                                         net_at_stored_fraction_deviation=net_difference,
                                         no_contact_net=0., tag='[E] legacy calibration-only diagnostic'))
            audit['replay_grid'].extend(candidates)
        audit['passed'] = all(item['passed'] for key, item in checks.items() if key.startswith('budget.'))
        audit['status'] = 'REPRODUCED' if audit['passed'] else 'NOT_REPRODUCED'
    except (FileNotFoundError, ValueError, KeyError, AssertionError, TypeError) as error:
        audit['error'] = f'{type(error).__name__}: {error}'
        record_check(checks, 'budget.replay_completed', False, error=audit['error'])
    audit['new_curve_rule'] = ('Eligible for conditional non-test curves; no promotion.' if audit['passed']
                               else 'Quote stored choices only; explicitly skip the new curve. No re-derivation or tuning.')
    return audit


def population_inputs():
    return [ROOT / f'v2_work/d_results/oof/baseline_lgbm_r{repeat}_f{fold}.npz'
            for repeat in range(2) for fold in range(5)] + [
                ROOT / 'telecom/Record.csv',
                ROOT / 'v1_frozen/analysis_outputs/tables/split_manifest.csv',
                ROOT / 'analysis_outputs/model_selection.json',
                ROOT / 'analysis_outputs/feature_manifest.json',
            ]


def write_curve(split, checks, artifacts):
    pop = population()  # Frozen baseline OOF sources only; no test observations or new model fit.
    allowed = set(split.loc[split.partition.isin(['train', 'validation']), 'Customer_ID'].astype(int))
    validate_frame(pop, allowed, 75_000, 'p_d')
    record_check(checks, 'curve.population_ids', True, rows=len(pop), expected_rows=75_000,
                 split='train + validation', test_rows_used=0)
    y, value = pop.y.to_numpy(dtype=float), pop.value.to_numpy(dtype=float)
    weight = weights(y, prior=DEPLOYMENT_PRIOR, population_size=DEPLOYMENT_SIZE)
    record_check(checks, 'curve.weight_mass', abs(float(weight.sum()) - DEPLOYMENT_SIZE) <= 1e-8,
                 actual=float(weight.sum()), reference=DEPLOYMENT_SIZE, absolute_tolerance=1e-8)
    # Retain common.population()'s .02 shift with sample prior .49562 here.
    # The .4956 override belongs only to exact legacy calibration replay above.
    score = pop.p_d.to_numpy(dtype=float) * value
    grid = budget_grid(score, weight, y, value, range(1, 41))
    rows = []
    for a, b in PRIORS:
        gamma_mean = a / (a + b)
        for cost in COSTS:
            for point in grid:
                gross = point['selected_churn_value'] * gamma_mean * RETAINED_MONTHS * MARGIN
                rows.append(dict(**point, prior_a=a, prior_b=b, prior=f'Beta({a},{b})',
                                 gamma_mean=gamma_mean, contact_cost=cost, scenario_gross=gross,
                                 scenario_net=gross - cost * point['contacts'] - FIXED_COST,
                                 fixed_startup_usd_equivalent=FIXED_COST, retained_months=RETAINED_MONTHS,
                                 margin=MARGIN, deployment_prior=DEPLOYMENT_PRIOR,
                                 probability_sample_prior=.49562, weighted_deployment_size=DEPLOYMENT_SIZE,
                                 source_population='75000 train+validation baseline OOF rows',
                                 scenario='conditional prior-mean budget sweep; not optimized/promoted',
                                 no_contact_net=0.,
                                 tag='[E] arithmetic conditional on [A] prevention, label shift and economics'))
    curve = pd.DataFrame(rows)
    record_check(checks, 'curve.complete_finite_cost_prior_grid',
                 len(curve) == 3 * 4 * 40 and np.isfinite(curve.scenario_net).all(),
                 rows=len(curve), expected_rows=480, fractions='1..40% in 1% steps',
                 costs=list(COSTS), priors=[list(prior) for prior in PRIORS])
    csv_path = ADDONS / 'results/wp3_net_curve.csv'
    curve.to_csv(csv_path, index=False, float_format='%.17g', lineterminator='\n')
    artifacts.append(file_info(csv_path))
    # The permitted $1-only draft keeps a short, unambiguous legend. All twelve
    # prior/cost curves remain in the SHA-bound CSV; no curves are silently lost.
    series = []
    for (a, b), color in zip(PRIORS, ((0, 126, 134), (189, 125, 20), (91, 110, 129))):
        subset = curve.loc[(curve.prior_a == a) & (curve.prior_b == b)
                           & (curve.contact_cost == 1.)]
        series.append(dict(label=f'B({a},{b}) $1', x=subset.intended_fraction.to_numpy() * 100,
                           y=subset.scenario_net.to_numpy(), color=color))
    png_path = ADDONS / 'figures/wp3_net_curve.png'
    line_plot(png_path, 'WP3: $1 COST ONLY; ALL 12 CURVES IN CSV',
              'INTENDED CONTACT FRACTION (%)', 'SCENARIO NET (USD-EQUIVALENT)',
              series, x_limits=(1., 40.))
    artifacts.append(file_info(png_path))
    record_check(checks, 'curve.artifact_hashes',
                 all(item['present'] and item['sha256'] for item in artifacts),
                 artifacts=artifacts)
    return dict(status='WRITTEN', source_rows=len(pop), csv_rows=len(curve),
                csv=file_info(csv_path), figure=file_info(png_path),
                figure_scope='$1 cost only, three prior curves; full four-cost/three-prior grid in CSV.',
                legend_labels=[item['label'] for item in series],
                legend='Three short one-line labels; helper legend height is below 600 pixels.',
                no_contact_net=0., budget_optimized=False, promoted=False)


def report_results(priors, band, reproduction, curve, artifacts, checks):
    results = ['| Prevention prior [A] | P(net>0) [E/A] | E[net] | Net 5th percentile | EVPI/cohort | EVPI x12 |',
               '|---|---:|---:|---:|---:|---:|']
    for row in priors:
        c = row['closed_form']
        results.append(f'| {row["label"]} | {c["p_positive"]:.6f} | ${c["expected_net"]:,.2f} | '
                       f'${c["net_5pct"]:,.2f} | ${c["evpi_per_cohort"]:,.2f} | ${c["evpi_horizon12"]:,.2f} |')
    if band:
        results.append('[E/A] ' + band['statement'])
    results += ['', '| Cost [A] | Stored fraction [E] | Replay winner [E] | Fraction deviation | Stored OOF net [E/A] |',
                '|---|---:|---:|---:|---:|']
    for quote in reproduction['stored_choices']:
        winner = next((row for row in reproduction['winners'] if row['cost'] == quote['cost']), None)
        fraction = f'{winner["intended_fraction"]:.0%}' if winner else 'not reproduced'
        delta = f'{winner["fraction_deviation"]:+.6f}' if winner else 'not available'
        results.append(f'| ${quote["cost"]:g} | {quote["fraction"]:.0%} | {fraction} | {delta} | '
                       f'${quote["calibration_oof_net"]:,.2f} |')
    results += ['[E/A] No-contact/no-campaign comparator is $0, separately from every campaign row and its $5,000 startup charge.',
                '[E] Budget reproduction: ' + reproduction['status'] + '. ' + reproduction['new_curve_rule'],
                '[E] Curve: ' + curve['status'] + '. ' + curve.get('figure_scope', curve.get('reason', ''))]
    results += [f'- [E] Artifact `{item["path"]}` — SHA-256 `{item["sha256"]}`.' for item in artifacts]
    results += ['', '[E] Actual deviations against the approximate brief (closed form; probability delta and USD-equivalent dollar deltas):']
    for row in priors:
        prefix = f'a{row["a"]}_b{row["b"]}.closed_vs_brief.'
        deltas = ', '.join(f'{metric}: {checks[prefix + metric]["signed_deviation"]:+.6f}'
                           for metric in BRIEF_REFERENCES[(row['a'], row['b'])])
        results.append(f'- [E] {row["label"]}: {deltas}.')
    results.append('[E] Every Monte Carlo/closed-form/brief comparison, signed and relative deviation, '
                   'quadrature error, tie count, and complete calibration replay grid is retained in the primary JSON; none is clipped or tuned.')
    return results


def main():
    verify_runtime()
    upstream = require_wp2_finished()  # Before any WP3 computation/output.
    for directory in ('results', 'figures', 'reports'):
        if not (ADDONS / directory).is_dir():
            raise FileNotFoundError(f'WP3 output directory is missing: {ADDONS / directory}')
    inputs = [ROOT / 'v2_work/final_metrics.json',
              ROOT / 'v2_work/a_selected_calibration.csv', ROOT / 'v2_work/a_budget_choices.csv',
              ROOT / 'v2_work/workstream_a.py', ROOT / 'v2_work/common.py',
              ROOT / 'v1_frozen/analysis_outputs/tables/split_manifest.csv',
              ADDONS / 'src/common.py', ADDONS / 'src/reporting.py', ADDONS / 'src/png_drafts.py',
              Path(__file__).resolve(), ADDONS / 'results/wp2_evsi.json', ADDONS / 'reports/WP2_report.md']
    checks, deviations, artifacts, priors = {}, [], [], []
    constants = stored_constants()  # Only quote frozen test-derived aggregate G/K through this helper.
    G, K = float(constants['G']), float(constants['K'])
    valid_constants = np.isfinite(G) and np.isfinite(K) and G > 0 and 0 < K / G < 1
    record_check(checks, 'roi.quoted_constants_valid', valid_constants, G=G, K=K,
                 source=file_info(ROOT / 'v2_work/final_metrics.json'), test_rows_used=0)
    if valid_constants:
        generator = rng(TASK_INDEX)
        for a, b in PRIORS:
            priors.append(prior_metrics(a, b, constants, generator, checks))
    else:
        deviations.append('[E] Invalid quoted G/K for full-support Beta integration; ROI calculations were skipped, not repaired.')
    band = None
    if priors:
        probabilities = [row['closed_form']['p_positive'] for row in priors]
        central = next(row for row in priors if (row['a'], row['b']) == (6, 24))['closed_form']['p_positive']
        low, high = min(probabilities), max(probabilities)
        band = dict(lower=low, upper=high, central=central, central_prior=[6, 24],
                    brief_approximation=dict(lower=.17, upper=.93, central=.69),
                    interpretation='Sensitivity across three assumed priors, not a confidence/credible interval.',
                    statement=f'P(net>0) between {low:.0%} and {high:.0%} depending on the prevention-rate prior; '
                              f'central {central:.0%} (Beta(6,24)); computed probabilities {low:.6f}/{high:.6f}/{central:.6f}.')
    quotes = []
    try:
        quotes = quote_budget_choices(checks)
        split = pd.read_csv(ROOT / 'v1_frozen/analysis_outputs/tables/split_manifest.csv',
                            usecols=['Customer_ID', 'partition'], dtype={'Customer_ID': 'int64'})
        reproduction = reproduce_budget(split, quotes, checks)
    except (FileNotFoundError, ValueError, KeyError, AssertionError, TypeError) as error:
        message = f'{type(error).__name__}: {error}'
        record_check(checks, 'budget.inputs_available', False, error=message)
        reproduction = dict(passed=False, status='NOT_REPRODUCED', stored_choices=quotes,
                            no_contact_net=0., rows=0, winners=[], replay_grid=[], error=message,
                            new_curve_rule='Quote readable stored choices only; explicitly skip new curve. No tuning.')
    curve = dict(status='SKIPPED', source_rows=0, csv_rows=0,
                 reason='Legacy budget reproduction failed; stored choices are quoted, new curve explicitly skipped.',
                 no_contact_net=0., budget_optimized=False, promoted=False)
    population_attempted = False
    if reproduction['passed']:
        population_attempted = True
        inputs.extend(population_inputs())  # Hash every dependency even if a later population/figure check fails.
        try:
            curve = write_curve(split, checks, artifacts)
        except (FileNotFoundError, ValueError, KeyError, AssertionError, TypeError) as error:
            message = f'{type(error).__name__}: {error}'
            record_check(checks, 'curve.completed', False, error=message)
            source_rows = checks.get('curve.population_ids', {}).get('rows', 0)
            curve = dict(status='FAILED', source_rows=source_rows, csv_rows=480 if artifacts else 0,
                         reason=message, artifacts_written=artifacts,
                         no_contact_net=0., budget_optimized=False, promoted=False)
            deviations.append('[E] New curve/figure failed: ' + message + '; any successfully written artifact is explicitly hashed.')
    else:
        record_check(checks, 'curve.completed', False, reason=curve['reason'])
        deviations.append('[E] ' + curve['reason'] + ' Existing WP3 curve files, if any, are not current-run artifacts.')
    record_check(checks, 'roi.three_priors_complete', len(priors) == len(PRIORS),
                 completed=len(priors), expected=len(PRIORS))
    status = 'DONE' if all(item['passed'] for item in checks.values()) else 'PARTIAL'
    for name, item in checks.items():
        if not item['passed']:
            deviations.append(f'[E] Failed check {name}: ' + json.dumps(item, sort_keys=True))
    deviations += ['[E] Preregistered randomized stratified inverse-CDF Monte Carlo replaces iid draws to reduce quantile uncertainty; '
                   'one million draws/prior are non-iid and no iid MCSE is reported.',
                   '[E] PNG deliberately shows only the three $1 curves; its title discloses that all twelve cost/prior curves remain in the full SHA-bound CSV '
                   '(when reproduction succeeds).',
                   '[E] Added a $0 no-campaign audit and $0.000001 absolute replay-net check at the stored fraction; no new budget selection criterion is tuned.']
    if upstream['status'] == 'PARTIAL':
        deviations.append('[E] WP2 completed with PARTIAL status. WP3 reports its own checks independently and does not upgrade WP2 evidence.')
    inputs = sorted({Path(path).resolve() for path in inputs}, key=lambda path: path.as_posix())
    assumptions = dict(
        gamma='Beta(6,14), Beta(6,24), Beta(2,18) prevention-rate priors are assumptions; '
              'uniform independent prevention across selected would-be churners is assumed, '
              'not inferred from churn risk or value. No treatment labels exist; response heterogeneity is not estimated.',
        economics='Six retained months, .60 incremental margin, assumed contact costs .25/1/2/5, '
                  'fixed startup 5000, USD-equivalent units; not verified operating facts.',
        frozen_roi='100000 hypothetical-customer frozen nominal 10% threshold: net(gamma)=G*gamma-K; '
                   'G and K are quoted aggregates via stored_constants, not recomputed from test rows. '
                   'K quotes the frozen $1/contact plus fixed startup assumption.',
        population='75000 non-test train+validation observations class-weighted to 100000 hypothetical customers at 2% prior; '
                   'label shift and within-class representativeness are unverified.',
        horizon12='12 identical future cohorts under the same gamma/economics; EVPI x12 is conditional arithmetic, not a discounted cash forecast.',
        value='Frozen capped recurring-charge proxy, not observed incremental contribution or treatment responsiveness.',
    )
    body = dict(status=status, name=NAME, upstream_wp2=upstream, quoted_constants=constants,
                constants_source=dict(file=file_info(ROOT / 'v2_work/final_metrics.json'),
                                      accessor='common.stored_constants', test_rows_recomputed=0),
                priors=priors, band=band, p_positive_band=band, assumptions=assumptions,
                method=dict(closed_form='scipy.stats.beta mean/ppf/sf, scipy.special.betaincc; '
                                        'eplus=mean*betaincc(a+1,b,g_star)-g_star*betaincc(a,b,g_star). '
                                        'E(net+)=G*eplus; EVPI=E(net+)-max(0,E(net)).',
                            quadrature='scipy.integrate.quad eplus on [g_star,1], abs difference strictly below 1e-9.',
                            monte_carlo='N=1000000 per prior, (arange(N)+rng(3).random(N))/N then beta.ppf; '
                                        'single sequential seeded generator, fixed prior order; non-iid randomized stratification. '
                                        'Linear empirical 5th percentile. No adaptive draws, tuning, clipping, or iid MCSE.',
                            tolerances=dict(probability_absolute=PROBABILITY_TOLERANCE,
                                            dollars_relative=DOLLAR_RELATIVE_TOLERANCE,
                                            budget_fraction_absolute=GRID_STEP),
                            references='User-supplied approximate brief values, retained as references, never substituted for computed estimates.'),
                audit_reproduction=reproduction, net_curve=curve, artifacts=artifacts,
                acceptance=checks, deviations=deviations, population_attempted=population_attempted,
                budget_optimized=False, prospective_policy_promoted=False,
                no_contact_net=0., tags_used=['[E]', '[A]', '[R]'])
    row_counts = dict(priors=len(priors), draws_per_prior=DRAWS_PER_PRIOR,
                      calibration_rows=reproduction['rows'],
                      population_rows=curve['source_rows'], curve_rows=curve['csv_rows'], test_rows_used=0)
    primary_path = ADDONS / 'results/wp3_roi_band.json'
    write_json('results/wp3_roi_band.json', body, __file__, TASK_INDEX, inputs, row_counts)
    results = report_results(priors, band, reproduction, curve, artifacts, checks)
    results.append(f'[E] Primary JSON `{primary_path.as_posix()}` — SHA-256 `{file_info(primary_path)["sha256"]}`; '
                   'its provenance hashes the input and baseline sources and its artifact entries bind the curve CSV/PNG.')
    acceptance = []
    for name, item in checks.items():
        detail = ''
        if 'signed_deviation' in item:
            detail = f'; actual signed deviation={item["signed_deviation"]:+.12g}'
            if item.get('relative_deviation') is not None:
                detail += f', absolute relative deviation={item["relative_deviation"]:.9g}'
        elif 'absolute_deviation' in item:
            detail = f'; actual absolute deviation={item["absolute_deviation"]:.12g}'
        acceptance.append(f'- [E] {"PASS" if item["passed"] else "FAIL"}: {name}{detail}.')
    write_report(
        3, NAME, status, inputs,
        ['- [A] Gamma is an assumed prevention rate: no treatment labels exist. The three Beta priors are not fitted to outcomes.',
         '- [A] Six retained months, .60 margin, contact costs and fixed startup are USD-equivalent assumptions, not verified economics.',
         '- [E/A] Frozen ROI quotes G/K at the nominal 10% threshold; non-test curves use 75000 eligible rows weighted to 100000 at a 2% prior.',
         '- [A] Twelve identical future cohorts and stable label shift/within-class representativeness are assumptions.'],
        '[E] Integrated Beta net at the frozen threshold using beta/betaincc and cross-checked eplus by quad. '
        'Used one million preregistered randomized stratified beta.ppf draws per prior (non-iid), fixed probability/dollar tolerances and untuned brief references. '
        'Replayed only calibration-policy p_s_oof/y/value with legacy .4956 shift, stable weighted cutoffs and all ties. '
        'Only a passing replay permits a 1..40% non-test prior-mean/cost scenario grid; no new optimum or policy is selected.',
        results, acceptance, deviations,
        '[E/A] Prior-sensitive profitability band and conditional information-value arithmetic at the frozen threshold; '
        'prospective budget curves are scenarios, not optimized or promoted policies.',
        '[R] Do not call this EMPC, actual causal profit, verified prevention, live ROI or approval to change the frozen 10% policy. '
        'No test recomputation, retraining, package installation or integration is authorized.',
    )
    print(f'[E] WP3 {status}: ROI JSON/report written; curve {curve["status"]}; integration remains off.', flush=True)


if __name__ == '__main__':
    main()
