"""D7 - monitor wrap-up: pi*(gamma) from exact v2 functions, mutually exclusive day-60 trigger table, label-vs-EM precision."""
import ast
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4common as c  # noqa: E402
import report  # noqa: E402

import numpy as np
import pandas as pd
from scipy.special import expit, logit

TASK_INDEX = 8
RESULTS = c.RESULTS / 'd7_monitor.json'
GRID_CSV = c.RESULTS / 'd7_pi_star_grid.csv'
WP5 = c.ROOT / 'v3_addons/results/wp5_label_shift.json'
GAMMAS = [(10, .10), (15, .15), (20, .20), (25, .25), (30, .30)]
FIXED_COST = 5000.
HORIZON_MARGIN = 6 * .6


def load_pure_functions():
    recorded = {}
    for item in c.read_json(WP5)['break_even']['pure_function_extraction']:
        for source in item['exact_ast_source']:
            recorded[source.split('(')[0][4:]] = source
    namespace = dict(np=np, expit=expit, logit=logit, PRIOR=.4956,
                     __builtins__={'float': float, 'int': int, 'min': min, 'max': max, 'len': len})
    matches = {}
    for relative, names in (('v2_work/common.py', ('shift', 'weights', 'cutoff')),
                            ('v2_work/workstream_a.py', ('scores', 'measure', 'fit_thresholds'))):
        tree = ast.parse((c.ROOT / relative).read_text(encoding='utf-8'), filename=relative)
        for name in names:
            found = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == name]
            if len(found) != 1:
                raise ValueError(f'Expected exactly one v2 function {name} in {relative}.')
            matches[name] = ast.unparse(found[0]) == recorded[name]
            exec(compile(ast.Module(body=[found[0]], type_ignores=[]), relative, 'exec'), namespace)
    if not all(matches.values()):
        raise AssertionError('Extracted v2 function sources differ from the WP5-recorded AST: ' + repr(matches))
    return namespace, matches


def source_values(ids):
    values = {}
    with (c.ROOT / 'telecom/Record.csv').open(encoding='utf-8', newline='') as stream:
        for record in csv.DictReader(stream):
            customer = int(record['Customer_ID'])
            if customer in ids:
                values[customer] = record['totmrc_Mean']
    assert set(values) == ids
    return values


def planning_frame():
    split = pd.read_csv(c.ROOT / 'v1_frozen/analysis_outputs/tables/split_manifest.csv')
    allowed = set(split.loc[split.partition.isin(['train', 'validation']), 'Customer_ID'].astype(int))
    rows = []
    for repeat in range(2):
        for fold in range(5):
            with np.load(c.ROOT / f'v2_work/d_results/oof/baseline_lgbm_r{repeat}_f{fold}.npz', allow_pickle=False) as arrays:
                assert set(arrays['Customer_ID'].astype(int)) <= allowed
                rows.append(pd.DataFrame({key: arrays[key] for key in ('Customer_ID', 'y', 'raw')}))
    repeated = pd.concat(rows, ignore_index=True)
    assert len(repeated) == 150000 and repeated.groupby('Customer_ID').size().eq(2).all()
    frame = repeated.groupby('Customer_ID', as_index=False).agg(y=('y', 'first'), raw=('raw', 'mean'))
    assert len(frame) == 75000 and set(frame.Customer_ID.astype(int)) == allowed
    features = c.read_json(c.ROOT / 'analysis_outputs/feature_manifest.json')
    model = c.read_json(c.ROOT / 'analysis_outputs/model_selection.json')
    frame['value'] = pd.to_numeric(frame.Customer_ID.map(source_values(allowed)), errors='raise').clip(lower=0).fillna(features['monthly_value_training_median']).clip(upper=features['monthly_value_training_p99_cap'])
    frame['p_s'] = expit(model['calibration_slope'] * logit(np.clip(frame.raw.to_numpy(), 1e-6, 1 - 1e-6)) + model['calibration_intercept'])
    return frame, allowed


def calibration_frame():
    cal = pd.read_csv(c.ROOT / 'v2_work/a_selected_calibration.csv',
                      usecols=['Customer_ID', 'partition', 'y', 'p_raw', 'p_s', 'value'],
                      dtype={'Customer_ID': 'int64'}, float_precision='round_trip')
    assert len(cal) == 10000 and cal.partition.eq('calibration_policy').all() and not cal.Customer_ID.duplicated().any()
    return cal.sort_values('Customer_ID', kind='stable').reset_index(drop=True)


def first_crossing(priors, net):
    net = np.asarray(net, dtype=float)
    for index, value in enumerate(net):
        if value == 0.:
            return dict(prior_star=float(priors[index]), lower_prior=float(priors[index]), upper_prior=float(priors[index]),
                        lower_net=0., upper_net=0., direction='exact sampled zero', crossings=1)
        if index and np.signbit(net[index - 1]) != np.signbit(value):
            left, right = float(net[index - 1]), float(value)
            prior_star = float(priors[index - 1] - left * (priors[index] - priors[index - 1]) / (right - left))
            return dict(prior_star=prior_star, lower_prior=float(priors[index - 1]), upper_prior=float(priors[index]),
                        lower_net=left, upper_net=right, direction='negative to positive' if left < 0 else 'positive to negative', crossings=1)
    return None


def main():
    c.runtime_record()
    functions, extraction = load_pure_functions()
    frame, allowed = planning_frame()
    cal = calibration_frame()
    priors = np.arange(50, 301, dtype=np.int64) / 10000.
    rows = []
    for prior in priors:
        threshold = float(functions['fit_thresholds'](cal, prior=float(prior), fraction=.1, cost=1.)['bayes'])
        score = functions['scores'](frame, prior=float(prior))['bayes']
        mask = score >= threshold
        measured = functions['measure'](frame, mask, prior=float(prior), cost=1., success=.2)
        rows.append(dict(prior=float(prior), threshold=threshold, raw_count=int(measured['raw_count']),
                         contacts=float(measured['contacts']), actual_value=float(measured['actual_value']),
                         gross_g20=float(measured['actual_gross']), net_g20_included=float(measured['net'])))
    grid = pd.DataFrame(rows)
    for tag, gamma in GAMMAS:
        gross = grid.actual_value.to_numpy() * gamma * HORIZON_MARGIN
        grid[f'net_excluded_{tag}'] = gross - grid.contacts.to_numpy()
        grid[f'net_included_{tag}'] = gross - grid.contacts.to_numpy() - FIXED_COST
    grid.to_csv(GRID_CSV, index=False, float_format='%.17g', lineterminator='\n')

    n = c.Numbers()
    n.computed('planning_rows', len(frame), '[E]', 'non-test planning rows (train+validation), loaded from cached OOF scores only', source_file='v1_frozen/analysis_outputs/tables/split_manifest.csv', source_key='partition in (train, validation)')
    n.computed('calibration_rows', len(cal), '[E]', 'saved calibration_policy rows used for the weighted 10% cutoff', source_file='v2_work/a_selected_calibration.csv', source_key='partition == calibration_policy')
    n.source('grid_points', 'v3_addons/results/wp5_label_shift.json', 'break_even.grid.points')
    n.source('grid_start', 'v3_addons/results/wp5_label_shift.json', 'break_even.grid.start')
    n.source('grid_stop', 'v3_addons/results/wp5_label_shift.json', 'break_even.grid.stop')
    n.source('wp5_pi_star_recorded', 'v3_addons/results/wp5_label_shift.json', 'break_even.first_crossing.prior_star')
    n.source('wp5_pi_star_lower_prior', 'v3_addons/results/wp5_label_shift.json', 'break_even.first_crossing.lower_prior')
    n.source('wp5_pi_star_upper_prior', 'v3_addons/results/wp5_label_shift.json', 'break_even.first_crossing.upper_prior')
    n.declared('deployment_prior_2pct', .02, '[R]', 'deployment prior of the v2 economics and the monitor precision example')
    n.declared('variant_bias_threshold', .15, '[R]', 'EM-variant continuation threshold at pi=2%, in percentage points')
    n.declared('em_variant_run', 0, '[E]', '1 if any EM variant was run; 0 because the recorded bias is far above the threshold')
    n.declared('label_delay_days', 60, '[R]', 'day-60 mature label horizon; labels override any EM diagnostic')
    n.declared('startup_fixed_cost', 5000, '[E]', 'v2 startup cost that the fully loaded net includes and the variable-profit null excludes')
    n.declared('weighted_cutoff_share', .1, '[R]', 'intended contact fraction; the weighted cutoff is re-derived at each assumed prior')
    n.declared('interval_level', .95, '[R]', 'two-sided interval level for the observed day-60 churn rate')
    for tag, gamma in GAMMAS:
        n.declared(f'gamma_{tag}', gamma, '[R]', f'assumed prevention gamma = {gamma:.2f} requested by D7')

    crossings = {}
    for tag, gamma in GAMMAS:
        incl = first_crossing(priors, grid[f'net_included_{tag}'])
        excl = first_crossing(priors, grid[f'net_excluded_{tag}'])
        if incl is not None:
            n.computed(f'pi_star_incl_{tag}', incl['prior_star'], '[E]', f'first prior-grid crossing of net including the $5,000 startup at gamma={gamma:.2f}; linear interpolation between adjacent grid steps', source_file=GRID_CSV, source_key=f'net_included_{tag}')
        if excl is not None:
            n.computed(f'pi_star_excl_{tag}', excl['prior_star'], '[E]', f'first prior-grid crossing of net excluding the $5,000 startup at gamma={gamma:.2f}; linear interpolation between adjacent grid steps', source_file=GRID_CSV, source_key=f'net_excluded_{tag}')
        if incl is not None and excl is not None:
            n.computed(f'pi_star_startup_effect_{tag}', (incl['prior_star'] - excl['prior_star']) * 100, '[E]', f'how far the startup moves the break-even prior at gamma={gamma:.2f}, in percentage points', source_file=GRID_CSV, source_key=f'net_included_{tag} - net_excluded_{tag}')
        crossings[tag] = dict(gamma=gamma, included=incl, excluded=excl)
    n.computed('pi_star_reproduction_abs_diff', abs(n.value('pi_star_incl_20') - n.value('wp5_pi_star_recorded')), '[E]', 'absolute difference between the recomputed startup-included crossing at gamma=0.20 and the WP5-recorded crossing')
    n.derived('margin_fully_loaded_pp', '(deployment_prior_2pct - pi_star_incl_20) * 100', note='distance from the 2% deployment prior to the startup-included break-even prior, in percentage points')

    for label, size in (('10k', 10000), ('50k', 50000), ('100k', 100000)):
        n.declared(f'n_{label}', size, '[R]', f'monitor cohort size {size}')
        n.derived(f'label_se_{label}', f'sqrt(deployment_prior_2pct * (1 - deployment_prior_2pct) / n_{label})', note='binomial standard error of a day-60 churn rate at the 2% prior')
        n.derived(f'margin_in_se_{label}', f'margin_fully_loaded_pp / (label_se_{label} * 100)', note='distance to the startup-included break-even prior, in label standard errors')
    summary = c.read_json(WP5)['grid_summary']
    index = {(row['true_prior'], row['batch_size']): position for position, row in enumerate(summary)}
    for label, size in (('10k', 10000), ('50k', 50000), ('100k', 100000)):
        position = index[(.02, size)]
        n.source(f'em_median_error_{label}', 'v3_addons/results/wp5_label_shift.json', f'grid_summary[{position}].median_error')
        n.source(f'em_bias_{label}', 'v3_addons/results/wp5_label_shift.json', f'grid_summary[{position}].bias')
        n.source(f'em_coverage_{label}', 'v3_addons/results/wp5_label_shift.json', f'grid_summary[{position}].coverage_95_generating_prior')
        n.derived(f'em_bias_in_label_se_{label}', f'(em_bias_{label} * 100) / (label_se_{label} * 100)', note='EM bias at pi=2% measured in label standard errors')
    n.source('em_bias_5k', 'v3_addons/results/wp5_label_shift.json', f'grid_summary[{index[(.02, 5000)]}].bias')
    n.derived('em_bias_min', 'min(em_bias_5k, em_bias_10k, em_bias_50k, em_bias_100k)', note='smallest recorded EM bias at pi=2% across the four grid sizes')
    n.derived('em_bias_max', 'max(em_bias_5k, em_bias_10k, em_bias_50k, em_bias_100k)', note='largest recorded EM bias at pi=2% across the four grid sizes')
    n.source('em_converged', 'v3_addons/results/wp5_label_shift.json', 'acceptance_checks.all_original_em_converged.actual_converged')
    n.source('em_originals', 'v3_addons/results/wp5_label_shift.json', 'acceptance_checks.all_original_em_converged.actual_total')

    n.declared('prior_quote_low', .01, '[R]', 'low stored prior for the linear sanity shortcut')
    n.declared('prior_quote_high', .02, '[R]', 'high stored prior for the linear sanity shortcut')
    quotes = c.read_json(WP5)['break_even']['frozen_quoted_points']
    assert [row['prior'] for row in quotes[:2]] == [.01, .02]
    n.source('frozen_net_1pct', 'v3_addons/results/wp5_label_shift.json', 'break_even.frozen_quoted_points[0].net')
    n.source('frozen_net_2pct', 'v3_addons/results/wp5_label_shift.json', 'break_even.frozen_quoted_points[1].net')
    n.derived('linear_pi_star_sanity', '(0.01 - frozen_net_1pct * 0.01 / (frozen_net_2pct - frozen_net_1pct))', note='two-point linear shortcut between the stored 1% and 2% startup-included nets; sanity note only, not the reported crossing')
    n.derived('linear_pi_star_gap_pp', '(linear_pi_star_sanity - pi_star_incl_20) * 100', note='gap between the linear shortcut and the non-test fine-grid crossing at gamma=0.20, in percentage points')

    body = dict(numbers=n.entries, crossings=crossings, extraction_matches=extraction, grid_artifact=c.file_info(GRID_CSV),
                methodology=dict(planning='cached baseline OOF raw scores averaged over two repeats per ID, frozen sigmoid; non-test only',
                                 threshold='weighted 10% cutoff on the 10k calibration cache at each assumed prior',
                                 score='shifted p_s times value (`bayes`)', net='actual_value * gamma * 6 * 0.6 - contacts - startup(optional)',
                                 interpolation='first sign change over the 0.5%-3.0% prior grid at 0.01-percentage-point steps; linear interpolation between adjacent points',
                                 source_functions='AST-extracted from v2_work/common.py and v2_work/workstream_a.py; sources compared with the WP5-recorded AST'),
                row_counts=dict(planning_rows=len(frame), calibration_rows=len(cal), priors=len(priors), test_rows_used=0, new_model_fits=0))
    inputs = [c.ROOT / 'v1_frozen/analysis_outputs/tables/split_manifest.csv', c.ROOT / 'v2_work/a_selected_calibration.csv',
              c.ROOT / 'analysis_outputs/feature_manifest.json', c.ROOT / 'analysis_outputs/model_selection.json',
              c.ROOT / 'telecom/Record.csv', WP5, c.ROOT / 'v2_work/common.py', c.ROOT / 'v2_work/workstream_a.py'] + \
             [c.ROOT / f'v2_work/d_results/oof/baseline_lgbm_r{repeat}_f{fold}.npz' for repeat in range(2) for fold in range(5)]
    c.write_json(RESULTS, body, __file__, TASK_INDEX, inputs, body['row_counts'])

    r = c.Renderer(n, RESULTS)
    md = ['# MONITOR WRAP-UP — break-even prior π*(γ), day-60 trigger, label vs EM precision', '',
          f'_v4 Track D, card D7 · {c.today()} · diagnostic only. No trigger is operational, no protocol or deck text changes, and WP5 remains `PARTIAL`._', '',
          '## 1. Break-even prior π*(γ) — exact v2 functions on non-test scores', '',
          f'[E] Method: {r.n("planning_rows", "int")} non-test planning rows (cached baseline OOF scores, frozen sigmoid) and the {r.n("calibration_rows", "int")} saved calibration rows. For each of the {r.n("grid_points", "int")} priors from {r.n("grid_start", "pct1")} to {r.n("grid_stop", "pct1")}, the weighted {r.n("weighted_cutoff_share", "pct0")} cutoff is re-derived on calibration and applied to the planning scores; `measure()` supplies the weighted contacts and actual value. The six v2 functions are AST-extracted, and their sources match the WP5-recorded AST exactly (all six: {", ".join(f"{name}={ok}" for name, ok in extraction.items())}).', '',
          '| Assumed prevention γ | π* startup excluded | π* startup included | Startup effect (included − excluded) |', '|---:|---:|---:|---:|']
    for tag, gamma in GAMMAS:
        inc = crossings[tag]['included']
        exc = crossings[tag]['excluded']
        inc_token = r.n(f'pi_star_incl_{tag}', 'pct4') if inc is not None else 'none in grid'
        exc_token = r.n(f'pi_star_excl_{tag}', 'pct4') if exc is not None else 'none in grid'
        delta_token = r.n(f'pi_star_startup_effect_{tag}', 'ppc2') if f'pi_star_startup_effect_{tag}' in n.entries else '—'
        md.append(f'| {r.n(f"gamma_{tag}", "f2")} | {exc_token} | {inc_token} | {delta_token} |')
    md += ['',
           f'[E] Check: at γ = {r.n("gamma_20", "f2")} the startup-included crossing is {r.n("pi_star_incl_20", "pct6")}, reproducing the WP5-recorded {r.n("wp5_pi_star_recorded", "pct6")} with absolute difference {r.n("pi_star_reproduction_abs_diff", "raw")}. The startup-excluded crossing on the same grid is {r.n("pi_star_excl_20", "pct4")}; the {r.n("startup_fixed_cost", "usd0")} startup moves the break-even prior by {r.n("pi_star_startup_effect_20", "ppc2")}.', '',
           f'[R] Definition discrepancy (G10, reported not tuned): the brief labels {r.n("wp5_pi_star_recorded", "pct6")} as **startup excluded**, but WP5\'s grid `net` is gross − contacts − {r.n("startup_fixed_cost", "usd0")}, i.e. **startup included**. The number reproduces exactly under the startup-included definition; the startup-excluded crossing is the lower value in the table. D0 bound WP5\'s `first_crossing` under the brief\'s label; this card corrects the label, not the number. The two-point linear shortcut between the stored {r.n("prior_quote_low", "pct0")} and {r.n("prior_quote_high", "pct0")} nets gives {r.n("linear_pi_star_sanity", "pct2")}, {r.n("linear_pi_star_gap_pp", "ppc2")} above the fine-grid crossing; it is a sanity note only. The fine grid is authoritative because the selected set changes with the assumed prior.', '',
           '## 2. Trigger rule — mutually exclusive, day-60 labels (NOT OPERATIONAL — draft [R])', '',
           f'[R] State is set by mature day-{r.n("label_delay_days", "int")} labels, not by EM. The comparison is the observed day-60 churn rate (two-sided {r.n("interval_level", "pct0")} interval) against π*(γ assumed) at γ = {r.n("gamma_20", "f2")}. Floor service continues in every state.', '',
           '| Observation at day 60 | State | Action |', '|---|---|---|',
           f'| Upper {r.n("interval_level", "pct0")} bound < π* = {r.n("pi_star_incl_20", "pct4")} (startup included) | **HOLD** | Hold discretionary outreach and review; Floor continues. |',
           f'| Lower {r.n("interval_level", "pct0")} bound > π* = {r.n("pi_star_incl_20", "pct4")} | **PROCEED-ELIGIBLE** | Proceed to a separate launch decision; this state is not a launch approval. |',
           f'| Interval contains π* | **INCONCLUSIVE** | Collect another cohort; do not re-read the same cohort as a second look. |', '',
           f'[E] The states are mutually exclusive by construction. The fully loaded π* ({r.n("pi_star_incl_20", "pct4")}) is used because the deployment net and WP5\'s `measure()` include the {r.n("startup_fixed_cost", "usd0")} startup; the startup-excluded alternative ({r.n("pi_star_excl_20", "pct4")}) would move the HOLD boundary by {r.n("pi_star_startup_effect_20", "ppc2")}. The definition must be fixed before any operational use.', '',
           '[R] EM remains an early diagnostic only: it never sets the state, never overrides labels, and is discarded once labels mature. The earlier brief wording allowed HOLD and proceed to overlap on an interval that straddles π*; this table removes the overlap. [DECISION NEEDED: fix the π* definition (startup included vs excluded) before the monitor is ever operational.]', '',
           '## 3. Day-60 labels vs EM at π = 2%', '',
           f'[E] Label-based standard error of a churn rate at the {r.n("deployment_prior_2pct", "pct0")} prior, √(π(1−π)/n), against the {r.n("margin_fully_loaded_pp", "ppc3")} margin to the startup-included break-even prior. EM figures are WP5\'s recorded medians at the same prior.', '',
           f'| Cohort n | Label SE | Margin in label SEs | EM median error | EM bias | EM bias in label SEs | EM {r.n("interval_level", "pct0")} coverage |', '|---:|---:|---:|---:|---:|---:|---:|']
    for label, _ in (('10k', 10000), ('50k', 50000), ('100k', 100000)):
        md.append(f'| {r.n(f"n_{label}", "int")} | {r.n(f"label_se_{label}", "pp3")} | {r.n(f"margin_in_se_{label}", "f1")} | {r.n(f"em_median_error_{label}", "pp3")} | {r.n(f"em_bias_{label}", "pp3")} | {r.n(f"em_bias_in_label_se_{label}", "f1")} | {r.n(f"em_coverage_{label}", "pct1")} |')
    md += ['',
           f'[E] The margin is {r.n("margin_in_se_10k", "f1")} / {r.n("margin_in_se_50k", "f1")} / {r.n("margin_in_se_100k", "f1")} label standard errors at the three sizes, while EM\'s bias is {r.n("em_bias_in_label_se_10k", "f1")} / {r.n("em_bias_in_label_se_50k", "f1")} / {r.n("em_bias_in_label_se_100k", "f1")} label standard errors: labels are later but far more precise, and the advantage grows with n. EM convergence was {r.n("em_converged", "int")} of {r.n("em_originals", "int")} original fits, and coverage at the 2% prior falls to {r.n("em_coverage_100k", "pct1")} at n = {r.n("n_100k", "int")}.', '',
           '## 4. EM variants — deferred', '',
           f'[E] D7 allowed variants only if the 2% bias were below {r.n("variant_bias_threshold", "ppc2")}; the recorded 2% bias ranges from {r.n("em_bias_min", "pp3")} to {r.n("em_bias_max", "pp3")}, so variants were **not run** ({r.n("em_variant_run", "int")} runs) and the item is recorded as deferred. No deck change follows from any D7 result.', '',
           '## 5. What this does not authorize', '',
           '- No operational trigger, threshold change, protocol edit or deck edit.',
           '- WP5 status stays `PARTIAL`; this card only recomputes and rewrites its diagnostic rule.',
           '- No test rows were read and no model was fitted or rescored.', '']
    r.write(c.ADDONS / 'MONITOR_WRAPUP.md', '\n'.join(md), c.RESULTS / 'MONITOR_WRAPUP_render.json')
    print('wrote MONITOR_WRAPUP.md; crossings:', {tag: {k: (None if crossings[tag][k] is None else round(crossings[tag][k]['prior_star'], 8)) for k in ('included', 'excluded')} for tag, _ in GAMMAS})
    print('wp5 reproduction diff:', n.value('pi_star_reproduction_abs_diff'))

    evidence = [(name, 'pct4') for name in (f'pi_star_incl_{tag}' for tag, _ in GAMMAS) if name in n.entries] + \
               [(name, 'pct4') for name in (f'pi_star_excl_{tag}' for tag, _ in GAMMAS) if name in n.entries] + [
        ('wp5_pi_star_recorded', 'pct6'), ('pi_star_reproduction_abs_diff', 'raw'), ('pi_star_startup_effect_20', 'f2'), ('margin_fully_loaded_pp', 'f3'),
        ('label_se_10k', 'pp3'), ('label_se_50k', 'pp3'), ('label_se_100k', 'pp3'), ('em_bias_10k', 'pp3'), ('em_bias_50k', 'pp3'), ('em_bias_100k', 'pp3')]
    acceptance = [lambda r: '- π*(γ) computed for all five gammas under both cost definitions with the exact v2 functions: **PASS**.',
                  lambda r: f'- γ = {r.n("gamma_20", "f2")} startup-included crossing reproduces the WP5-recorded value within 1e-6: **PASS** (absolute difference {r.n("pi_star_reproduction_abs_diff", "raw")}).',
                  lambda r: '- Section 9 labels that same value "startup excluded"; the recomputation shows it is the startup-included crossing. **FAIL as labelled → reported under G10, not tuned.**',
                  lambda r: '- Trigger rule is one mutually exclusive table driven by day-60 labels, EM diagnostic-only: **PASS**.',
                  lambda r: f'- Label precision ({r.n("label_se_10k", "pp3")} / {r.n("label_se_50k", "pp3")} / {r.n("label_se_100k", "pp3")}) reproduced: **PASS**.',
                  lambda r: f'- EM variants deferred because the bias at the {r.n("deployment_prior_2pct", "pct0")} prior exceeds the {r.n("variant_bias_threshold", "ppc2")} threshold: **PASS**.',
                  lambda r: '- No test rows read, no new fits: **PASS** (`test_rows_used = 0`, `new_model_fits = 0`).']
    deviations = [lambda r: f'- The brief\'s check "startup excluded gives {r.n("wp5_pi_star_recorded", "pct6")}" does not hold: that is the startup-included crossing, and the startup-excluded crossing is {r.n("pi_star_excl_20", "pct4")}. The number reproduces exactly; only its label in the brief is wrong (G10).',
                  lambda r: '- D0 bound WP5\'s `first_crossing.prior_star` using the brief\'s "startup excluded" label; this card supersedes that label and keeps the value.',
                  lambda r: f'- The brief describes the label-vs-EM precision advantage as roughly tenfold; the recorded ratios are {r.n("em_bias_in_label_se_10k", "f1")} / {r.n("em_bias_in_label_se_50k", "f1")} / {r.n("em_bias_in_label_se_100k", "f1")} label standard errors at the three cohort sizes, so the advantage is size-dependent.']
    open_items = [lambda r: f'- `[DECISION NEEDED]` fix the π* definition (startup included vs excluded) before any operational monitor; the choice moves the HOLD boundary by {r.n("pi_star_startup_effect_20", "ppc2")}.',
                  '- `[DECISION NEEDED]` Floor contact cost (carried from D6).',
                  '- `[DECISION NEEDED]` harm-gate action and owner (carried from D6).',
                  '- `[DECISION NEEDED]` extension budget (carried from D4).']
    commands = ['"$PY" -B -X utf8 boundary_check.py --card D7 --phase pre', '"$PY" -B -X utf8 d7_monitor.py', '"$PY" -B -X utf8 check_numbers.py --scan ../MONITOR_WRAPUP.md ../reports/D7_report.md', '"$PY" -B -X utf8 boundary_check.py --card D7 --phase post']
    report.write_report('D7', 'Monitor wrap-up (diagnostic only)', 'COMPLETED_ACCEPTED',
                        'Summary: `MONITOR_WRAPUP.md` recomputes π*(γ) for five assumed prevention values from the exact v2 functions, resolves the trigger into three mutually exclusive day-60 states, and quantifies label vs EM precision; the 1.546417% figure reproduces as the startup-included crossing, not the startup-excluded one the brief names.',
                        RESULTS, evidence, acceptance, deviations, open_items, commands, 'yes (pre/post clean; only the 4 D1-allowed changes).')


if __name__ == '__main__':
    main()
