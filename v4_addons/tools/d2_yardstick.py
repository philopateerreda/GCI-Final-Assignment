"""D2 — yardstick sheet: results/yardstick.json (bound numbers) + YARDSTICK.md (rendered, no hand-typed numbers)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4common as c  # noqa: E402

TASK_INDEX = 2
FM = 'v2_work/final_metrics.json'
WP1 = 'v3_addons/results/wp1_power.csv'
WP1J = 'v3_addons/results/wp1_power.json'
WP2DQ = 'v3_addons/results/wp2_decision_quality.csv'
WP2EVSI = 'v3_addons/results/wp2_evsi.json'
WP3 = 'v3_addons/results/wp3_roi_band.json'
WP5 = 'v3_addons/results/wp5_label_shift.json'
WP5G = 'v3_addons/results/wp5_break_even_grid.csv'
INV = 'v3_addons/results/inventory.json'
D0 = 'v4_addons/results/d0_checks.json'
RESULTS = c.RESULTS / 'yardstick.json'
DEFF_DEFAULT = 1.1  # section-3 decision 3 default


def e4(n, arm, deff, col):
    return n.source(f'e4_{col}_{arm}_deff{str(deff).replace(".", "p")}', WP1, f'where(method=E4_V_stratified;n_per_arm={arm};gamma=0.2;deff={deff}).{col}')


def bind(n):
    fm = c.read_json(c.ROOT / FM)
    spec = 'pilot_calibration.spec.'
    # frame 1: frozen binary pilot
    for key in ('p0', 'p1', 'relative_prevention_assumption', 'alpha_two_sided', 'power', 'followup_loss_allowance', 'minimum_complete_per_arm', 'enrolled_per_arm'):
        n.source(f'binary_{key}', FM, spec + 'normal_binary_reference.' + key, tag='[A]' if key in ('p0', 'p1', 'relative_prevention_assumption', 'followup_loss_allowance') else '[E]')
    for index, row in enumerate(fm['pilot_calibration']['power_rows']):
        if row['enrolled_per_arm'] == 7872 and row['method'] == 'binary_churn':
            n.source('v2_binary_power_7872_calibration', FM, f'pilot_calibration.power_rows[{index}].simulated_power')
    n.source('e1_power_7872', WP1, 'where(method=E1_churn;n_per_arm=7872;gamma=0.2;deff=1.0).effect_power')
    n.source('e1_power_7872_deff1p1', WP1, 'where(method=E1_churn;n_per_arm=7872;gamma=0.2;deff=1.1).effect_power')
    # frame 2: v2 adjusted contribution (fully loaded)
    for part in ('pilot_calibration', 'pilot_test'):
        short = part.split('_')[1]
        n.source(f'v2_grid_adjusted_{short}', FM, f'{part}.simulated_required_enrolled_per_arm_grid.adjusted_contribution')
        for index, row in enumerate(fm[part]['power_rows']):
            if row['enrolled_per_arm'] == 80000 and row['method'] in ('adjusted_contribution', 'unadjusted_contribution'):
                n.source(f'v2_80k_{row["method"].split("_")[0]}_{short}', FM, f'{part}.power_rows[{index}].simulated_power')
            if row['enrolled_per_arm'] == 160000 and row['method'] == 'unadjusted_contribution':
                n.source(f'v2_160k_unadjusted_{short}', FM, f'{part}.power_rows[{index}].simulated_power')
            if row['enrolled_per_arm'] == 80000 and row['method'] == 'adjusted_contribution':
                n.source(f'v2_80k_startup_per_enrollee_{short}', FM, f'{part}.power_rows[{index}].startup_per_treated_enrollee')
                n.source(f'v2_80k_effective_{short}', FM, f'{part}.power_rows[{index}].effective_per_arm')
    n.source('v2_grid_top', FM, 'pilot_calibration.power_rows[26].enrolled_per_arm', note='top of the v2 grid (160,000)')
    n.source('startup_cost', FM, spec + 'cost_assumptions.startup_stage1', tag='[A]')
    n.source('treated_contact_cost', FM, spec + 'cost_assumptions.treated_contact', tag='[A]')
    n.source('control_incremental_contact_cost', FM, spec + 'cost_assumptions.control_incremental_contact', tag='[A]')
    # frame 3/4: WP1 E4 variable profit and gross effect
    reqs = c.read_json(c.ROOT / WP1J)['requirements_at_gamma_20']
    for index, req in enumerate(reqs):
        if req['method'] in ('E4_V_stratified', 'E3_observed', 'E2_observed', 'E1_churn'):
            name = f'first_grid_{req["method"].split("_")[0].lower()}_{req["null"].split("_")[0]}'
            if req['first_qualifying_grid_n'] is None:
                n.computed(name, None, '[E]', 'not established through the WP1 grid (80,000/arm)', source_file=WP1J, source_key=f'requirements_at_gamma_20[{index}].first_qualifying_grid_n')
            else:
                n.source(name, WP1J, f'requirements_at_gamma_20[{index}].first_qualifying_grid_n')
    for arm in (5000, 7872, 10000, 40000, 80000):
        for deff in (1.0, 1.1, 1.25):
            if arm in (5000, 7872) or deff == 1.0:
                e4(n, arm, deff, 'effect_power')
                e4(n, arm, deff, 'profit_power')
    # estimator table at 7,872 and 80,000, gamma 0.2, DEFF 1.0
    for arm in (7872, 80000):
        for method in ('E1_churn', 'E2_literal_oracle', 'E3_literal_oracle', 'E2_observed', 'E3_observed', 'E4_V_stratified'):
            short = method.replace('_V_stratified', '').replace('_literal_oracle', '_oracle').lower()
            n.source(f'est_{short}_{arm}_effect', WP1, f'where(method={method};n_per_arm={arm};gamma=0.2;deff=1.0).effect_power')
            if method != 'E1_churn':
                n.source(f'est_{short}_{arm}_profit', WP1, f'where(method={method};n_per_arm={arm};gamma=0.2;deff=1.0).profit_power')
    n.derived('spread_80k_profit_e2obs_vs_e4', 'est_e4_80000_profit - est_e2_observed_80000_profit', note='estimator spread at 80,000/arm, variable-profit null')
    # frame 5: 100k cohort economics (from D0 bound values -> rebind to primary sources)
    n.source('bayes_actual_gross', FM, 'deployment_policies.bayes.actual_gross')
    n.source('bayes_contacts', FM, 'deployment_policies.bayes.contacts')
    n.source('bayes_net', FM, 'deployment_policies.bayes.net')
    n.derived('G', 'bayes_actual_gross / binary_relative_prevention_assumption')
    n.derived('K', 'bayes_contacts + startup_cost')
    n.derived('g_star', 'K / G')
    n.derived('net_at_20', 'G * binary_relative_prevention_assumption - K')
    n.source('slide11_net_lower', FM, 'deployment_intervals.net.lower')
    n.source('slide11_net_upper', FM, 'deployment_intervals.net.upper')
    n.declared('cohort_size', 100000, '[A]', 'hypothetical 100,000-account deployment cohort (final_metrics epistemic boundary / weights population_size)')
    n.source('headline_fraction', FM, 'protocol.headline_fraction', tag='[A]')
    n.derived('list_size', 'cohort_size * headline_fraction', note='one nominal 10% list in the 100k cohort')
    n.derived('max_per_arm_one_list', 'list_size / 2', note='one 10k list split across two arms')
    # frame 6: planning portfolio
    n.source('planning_portfolio_proxy', FM, spec + 'planning_portfolio_calibration_proxy')
    n.source('stage1_total_enrolled', FM, spec + 'stage1_total_enrolled')
    n.source('stage1_cost', FM, spec + 'stage1_cost', tag='[A]')
    n.source('stage2_incremental_cost', FM, spec + 'stage2_incremental_cost', tag='[A]')
    n.derived('startup_per_enrollee_7872', 'startup_cost / stage1_total_enrolled', note='$5,000 / 15,744')
    # frame 7: prior-integrated net
    for index, (a, b) in enumerate(((6, 14), (6, 24), (2, 18))):
        key = f'{a}_{b}'
        n.source(f'prior_{key}_a', WP3, f'priors[{index}].a', tag='[A]')
        n.source(f'prior_{key}_b', WP3, f'priors[{index}].b', tag='[A]')
        n.source(f'prior_{key}_mean', WP3, f'priors[{index}].gamma_mean', tag='[A]')
        for field in ('p_positive', 'expected_net', 'net_5pct', 'evpi_per_cohort', 'evpi_horizon12'):
            n.source(f'{field}_{key}', WP3, f'priors[{index}].closed_form.{field}', tag='[A]' if field == 'evpi_horizon12' else '[E]')
    scenarios = c.read_json(c.ROOT / WP2EVSI)['scenarios']
    for index, scenario in enumerate(scenarios):
        if scenario['n_per_arm'] == 7872:
            n.source(f'evsi_7872_{scenario["a"]}_{scenario["b"]}', WP2EVSI, f'scenarios[{index}].evsi_per_cohort')
    n.derived('evsi_7872_min', 'min(evsi_7872_6_14, evsi_7872_6_24, evsi_7872_2_18)')
    n.derived('evsi_7872_max', 'max(evsi_7872_6_14, evsi_7872_6_24, evsi_7872_2_18)')
    n.derived('evsi12_min', '12 * evsi_7872_min', tag='[A]')
    n.derived('evsi12_max', '12 * evsi_7872_max', tag='[A]')
    n.derived('p_positive_min', 'min(p_positive_6_14, p_positive_6_24, p_positive_2_18)')
    n.derived('p_positive_max', 'max(p_positive_6_14, p_positive_6_24, p_positive_2_18)')
    # transport
    n.source('selected_control_churn', INV, 'population.selected_control_churn')
    n.declared('deployment_prior', 0.02, '[A]', 'hypothetical 2% deployment prior (final_metrics prior_stress row 2; WP3 assumptions)')
    n.derived('transport_ratio', 'selected_control_churn / deployment_prior', tag='[A]')
    # decision quality (DEFF 1.1 default)
    for gamma, tag in ((0.2, 'g20'), (0.0, 'g0')):
        for col in ('p_scale', 'p_extend', 'p_stop'):
            n.source(f'dq_7872_{tag}_{col}', WP2DQ, f'where(n_per_arm=7872;gamma={gamma};deff=1.1).{col}')
    n.declared('deff_default', DEFF_DEFAULT, '[A]', 'section-3 decision 3 default: one DEFF = 1.1 everywhere (household clustering assumed; ICC unverified)')
    n.declared('deff_1p0', 1.0, '[A]', 'WP1 grid DEFF value (independent accounts)')
    n.declared('deff_1p25', 1.25, '[A]', 'WP1 grid DEFF stress value')
    n.derived('v2_followup_retention', 'v2_80k_effective_calibration / 80000', note='effective / enrolled per arm in the v2 simulation = 1 - follow-up loss')
    n.source('margin', WP5, 'break_even.economic_assumptions.margin', tag='[A]')
    n.source('retained_months', WP5, 'break_even.economic_assumptions.months', tag='[A]')
    n.declared('interval_level', 0.95, '[E]', 'nominal level of the v2 descriptive bootstrap intervals')
    n.declared('arm_80k', 80000, '[E]', 'WP1/v2 grid point used in the estimator table')
    n.declared('brief_quote_se_gamma_hat', 0.068, '[R]', 'v4 brief section 9 quote: SE(gamma-hat) ~ 6.8 pp')
    # SE(gamma-hat) both conventions (reproduced from D0 formulas)
    n.derived('se_gamma_hat_difference_scaled', 'sqrt(binary_p0 * (1 - binary_p0) / binary_enrolled_per_arm + binary_p1 * (1 - binary_p1) / binary_enrolled_per_arm) / binary_p0',
              note='SE(p0hat - p1hat) / p0, p0 fixed; matches the brief\'s ~6.8 pp')
    n.derived('se_gamma_hat_delta_full', 'sqrt((binary_p1 * (1 - binary_p1) / binary_enrolled_per_arm) / binary_p0**2 + (binary_p1**2 / binary_p0**4) * (binary_p0 * (1 - binary_p0) / binary_enrolled_per_arm))',
              note='full two-arm delta method')
    n.derived('se_gamma_hat_difference_scaled_deff', 'se_gamma_hat_difference_scaled * sqrt(deff_default)', tag='[A]')
    n.derived('gap_assumption_to_break_even', 'binary_relative_prevention_assumption - g_star')
    # pi* (WP5): fully loaded crossing; startup-excluded crossing recomputed from the grid
    n.source('pi_star_fully_loaded', WP5, 'break_even.first_crossing.prior_star', note='WP5 net = gross - contacts - 5000 (fixed_cost in economic_assumptions); i.e. startup INCLUDED')
    n.source('wp5_fixed_cost_in_net', WP5, 'break_even.economic_assumptions.fixed_cost', tag='[A]')
    n.derived('fully_loaded_margin_pp', 'deployment_prior - pi_star_fully_loaded', note='2% prior minus fully loaded pi*')
    return n


def pi_star_startup_excluded():
    import pandas as pd
    import numpy as np
    grid = pd.read_csv(c.ROOT / WP5G)
    net = (grid.actual_gross - grid.contacts).to_numpy()
    index = int(np.where((net[:-1] < 0) & (net[1:] >= 0))[0][0])
    lo, hi = grid.prior.iloc[index], grid.prior.iloc[index + 1]
    return float(lo + (hi - lo) * (-net[index]) / (net[index + 1] - net[index])), float(lo), float(hi), float(net[index]), float(net[index + 1])


def words(text):
    return len(text.split())


def main():
    c.runtime_record()
    n = c.Numbers()
    bind(n)
    pi_ex, lo, hi, net_lo, net_hi = pi_star_startup_excluded()
    n.computed('pi_star_startup_excluded', pi_ex, '[E]', 'linear interpolation of gross - contacts (no startup) between adjacent WP5 grid priors; same grid, same method as WP5 first_crossing',
               source_file=WP5G, source_key='actual_gross,contacts (interpolated zero crossing)', inputs=['wp5_break_even_grid.csv'])
    n.computed('pi_star_excluded_lower_prior', lo, '[E]', 'grid prior below the startup-excluded crossing', source_file=WP5G, source_key='prior')
    n.computed('pi_star_excluded_upper_prior', hi, '[E]', 'grid prior above the startup-excluded crossing', source_file=WP5G, source_key='prior')
    v = n.values()

    r = c.Renderer(n, RESULTS)
    bridges = {
        'target_bridge_slide13': f'WP1 E4 target: variable profit, startup excluded, DEFF {r.n("deff_default", "f1")}. v2 {r.n("v2_grid_adjusted_calibration", "int")}: fully loaded, startup included, {r.n("v2_followup_retention", "pct0")} follow-up. Not comparable; no reduction claimed.',
        'feasibility_line': f'One {r.n("list_size", "int")}-account list gives at most {r.n("max_per_arm_one_list", "int")}/arm ({r.n("e4_effect_power_5000_deff1p1", "pct1")} / {r.n("e4_profit_power_5000_deff1p1", "pct1")}). {r.n("binary_enrolled_per_arm", "int")}/arm needs {r.n("stage1_total_enrolled", "int")} core accounts; {r.n("planning_portfolio_proxy", "int")}-account proxy.',
        'deff_statement': f'All pilot power and decision figures use DEFF {r.n("deff_default", "f1")} for assumed household clustering [A]; ICC unverified. DEFF {r.n("deff_1p0", "f1")} / {r.n("deff_1p25", "f2")} appear only as sensitivity.',
        'variable_profit_definition': f'Variable profit = gross contribution minus {r.n("treated_contact_cost", "usd0")} per treated contact; the {r.n("startup_cost", "usd0")} startup is excluded ({r.n("startup_per_enrollee_7872", "usd4")} per enrollee at {r.n("binary_enrolled_per_arm", "int")}/arm).',
        'transport_line': f'The {r.n("deployment_prior", "pct0")} deployment prior is an assumption; selected non-test control churn is {r.n("selected_control_churn", "pct6")} ({r.n("transport_ratio", "x2")}). Assumption, not measurement.',
        'cohort_line': f'Prior-integrated values are per {r.n("cohort_size", "int")}-account cohort; ×12 figures assume 12 identical cohorts [A], not a portfolio guarantee.',
        'evsi_line': f'EVSI {r.n("evsi_7872_min", "usd0")}–{r.n("evsi_7872_max", "usd0")} per cohort at {r.n("binary_enrolled_per_arm", "int")}/arm is value of information under assumed priors; not funding proof.',
        'grid_wording': f'{r.n("v2_grid_adjusted_calibration", "int")}/arm is the first qualifying grid point for v2 fully loaded contribution; not an exact minimum. Unadjusted: not established through {r.n("v2_grid_top", "int")}.',
    }
    word_counts = {key: words(text) for key, text in bridges.items()}
    for key, count in word_counts.items():
        n.computed(f'words_{key}', count, '[E]', 'word count of the bridge sentence (limit 25)')
    deff_rows = []
    for deff in (1.0, 1.1, 1.25):
        tag = str(deff).replace('.', 'p')
        deff_rows.append(f'| {r.n("deff_default" if deff == DEFF_DEFAULT else f"deff_{tag}", "f2")}{" (default)" if deff == DEFF_DEFAULT else ""} | {r.n(f"e4_effect_power_7872_deff{tag}", "pct1")} | {r.n(f"e4_profit_power_7872_deff{tag}", "pct1")} | {r.n(f"e4_effect_power_5000_deff{tag}", "pct1")} | {r.n(f"e4_profit_power_5000_deff{tag}", "pct1")} |')

    def est_row(label, short, arm, oracle=False):
        eff = r.n(f'est_{short}_{arm}_effect', 'pct1')
        prof = r.n(f'est_{short}_{arm}_profit', 'pct1') if f'est_{short}_{arm}_profit' in n.entries else '—'
        status = '**oracle — invalid for capacity claims** (uses latent prevented outcomes)' if oracle else ('binary churn; no profit null' if short == 'e1_churn' else 'observable')
        return f'| {label} | {eff} | {prof} | {status} |'

    md = [
        '# YARDSTICK — one sheet for every sample size and profit definition in the Company A package',
        '',
        f'_v4 Track D, card D2 · generated {c.today()} from frozen artifacts · every number bound in `results/yardstick.json` · DEFF default {r.n("deff_default", "f1")} (section-3 decision 3, DEFAULT_ASSUMED)_',
        '',
        '> Vocabulary (G5). **Gross effect** = any positive effect on contribution, startup excluded. **Variable profit** = gross minus the per-contact cost, startup excluded. **Fully loaded net** = includes the startup. "First qualifying grid point" ≠ exact minimum.',
        '',
        '## 1. Frames table — seven frames, seven different questions',
        '',
        '| Frame | Question answered | Unit | Null / target | Key assumptions | Numbers | Source file / key |',
        '|---|---|---|---|---|---|---|',
        f'| Frozen binary pilot | Can a {r.n("binary_relative_prevention_assumption", "pct0")} relative churn reduction be detected? | enrolled accounts per arm | binary churn, two-sided α {r.n("binary_alpha_two_sided", "f2")}, power {r.n("binary_power", "pct0")} | p0 {r.n("binary_p0", "pct4")}, p1 {r.n("binary_p1", "pct4")}, {r.n("binary_followup_loss_allowance", "pct0")} follow-up loss, independent accounts | **{r.n("binary_enrolled_per_arm", "int")}/arm** ({r.n("binary_minimum_complete_per_arm", "int")} complete); v2 simulated {r.n("v2_binary_power_7872_calibration", "pct2")}; WP1 E1 {r.n("e1_power_7872", "pct1")} (DEFF {r.n("deff_1p0", "f1")}), {r.n("e1_power_7872_deff1p1", "pct1")} (DEFF {r.n("deff_default", "f1")}) | `final_metrics.json` `pilot_calibration.spec.normal_binary_reference`; `wp1_power.csv` E1_churn |',
        f'| v2 adjusted contribution (fully loaded) | Can fully loaded net contribution be detected? | enrolled accounts per arm | net after {r.n("treated_contact_cost", "usd0")}/contact and startup, covariate-adjusted | {r.n("v2_followup_retention", "pct0")} follow-up, startup included, fixed calibration-trained adjustment, independent accounts | **{r.n("v2_grid_adjusted_calibration", "int")}/arm first qualifying grid point**; simulated power there {r.n("v2_80k_adjusted_calibration", "pct2")} (planning rows) / {r.n("v2_80k_adjusted_test", "pct2")} (descriptive test rows); unadjusted {r.n("v2_80k_unadjusted_calibration", "pct2")} / {r.n("v2_80k_unadjusted_test", "pct2")} at {r.n("arm_80k", "kint")} and {r.n("v2_160k_unadjusted_calibration", "pct2")} / {r.n("v2_160k_unadjusted_test", "pct2")} at {r.n("v2_grid_top", "int")} → not established; startup {r.n("v2_80k_startup_per_enrollee_calibration", "usd4")} per treated enrollee | `final_metrics.json` `pilot_calibration.power_rows`, `pilot_test.power_rows`, `simulated_required_enrolled_per_arm_grid` |',
        f'| WP1 E4 variable profit | Can positive variable profit be detected? | enrolled accounts per arm | variable profit > 0 (gross − {r.n("treated_contact_cost", "usd0")}/contact; **startup excluded**) | value-stratified contrast, γ = {r.n("binary_relative_prevention_assumption", "pct0")}, DEFF {r.n("deff_1p0", "f1")} in the grid search | **{r.n("first_grid_e4_profit", "int")}/arm first qualifying grid point**; E4 variable-profit power {r.n("e4_profit_power_40000_deff1p0", "pct1")} there, {r.n("e4_profit_power_80000_deff1p0", "pct1")} at {r.n("arm_80k", "kint")}, {r.n("e4_profit_power_7872_deff1p0", "pct1")} at {r.n("binary_enrolled_per_arm", "int")} (DEFF {r.n("deff_1p0", "f1")}) | `wp1_power.json` `requirements_at_gamma_20`; `wp1_power.csv` E4_V_stratified |',
        f'| WP1 E4 gross effect | Can any positive gross effect be detected? | enrolled accounts per arm | gross effect > 0 (startup excluded) | as above | **{r.n("first_grid_e4_effect", "int")}/arm first qualifying grid point**; E4 gross power {r.n("e4_effect_power_10000_deff1p0", "pct1")} there, {r.n("e4_effect_power_7872_deff1p0", "pct1")} at {r.n("binary_enrolled_per_arm", "int")} (DEFF {r.n("deff_1p0", "f1")}) | same |',
        f'| {r.n("cohort_size", "kint")}-cohort economics | What is the conditional business case? | USD per {r.n("cohort_size", "int")}-account cohort | net = G·γ − K | γ = {r.n("binary_relative_prevention_assumption", "pct0")} assumed, {r.n("deployment_prior", "pct0")} prior, {r.n("retained_months", "int")} months, {r.n("margin", "pct0")} margin, {r.n("treated_contact_cost", "usd0")}/contact, {r.n("startup_cost", "usd0")} startup | G = {r.n("G", "usd2")}; K = {r.n("K", "usd2")}; γ* = {r.n("g_star", "pct4")}; net at γ = 20% = {r.n("net_at_20", "usd2")}; conditional {r.n("interval_level", "pct0")} interval {r.n("slide11_net_lower", "usd2")} – {r.n("slide11_net_upper", "usd2")} **at prevention = {r.n("binary_relative_prevention_assumption", "f1")}** | `final_metrics.json` `deployment_policies.bayes`, `deployment_intervals.net` |',
        f'| Planning portfolio | Is the pilot feasible from the available lists? | accounts | enrol {r.n("binary_enrolled_per_arm", "int")}/arm | one list = {r.n("headline_fraction", "pct0")} of {r.n("cohort_size", "int")} = {r.n("list_size", "int")} accounts | one list → at most **{r.n("max_per_arm_one_list", "int")}/arm**; Stage 1 needs **{r.n("stage1_total_enrolled", "int")} core accounts**; **{r.n("planning_portfolio_proxy", "int")}-account** planning proxy; Stage 1 envelope {r.n("stage1_cost", "usd0")}, Stage 2 +{r.n("stage2_incremental_cost", "usd0")} | `final_metrics.json` `pilot_calibration.spec` (`planning_portfolio_calibration_proxy`, `stage1_total_enrolled`, `capacity_caveat`) |',
        f'| Prior-integrated net | How uncertain is the business case under assumed prevention priors? | probability / USD per cohort | P(net > 0), E[net], 5th percentile, EVPI | three Beta priors on γ; same G, K | P(net > 0) {r.n("p_positive_6_14", "pct1")} / {r.n("p_positive_6_24", "pct1")} / {r.n("p_positive_2_18", "pct1")} for Beta({r.n("prior_6_14_a", "int")}, {r.n("prior_6_14_b", "int")}) / Beta({r.n("prior_6_24_a", "int")}, {r.n("prior_6_24_b", "int")}) / Beta({r.n("prior_2_18_a", "int")}, {r.n("prior_2_18_b", "int")}); 5th pct {r.n("net_5pct_6_14", "usd2")} / {r.n("net_5pct_6_24", "usd2")} / {r.n("net_5pct_2_18", "usd2")}; EVPI/cohort {r.n("evpi_per_cohort_6_14", "usd2")} / {r.n("evpi_per_cohort_6_24", "usd2")} / {r.n("evpi_per_cohort_2_18", "usd2")}; EVSI/cohort at 7,872 {r.n("evsi_7872_6_14", "usd2")} / {r.n("evsi_7872_6_24", "usd2")} / {r.n("evsi_7872_2_18", "usd2")} | `wp3_roi_band.json` `priors[].closed_form`; `wp2_evsi.json` `scenarios[]` |',
        '',
        f'**The three authoritative yardsticks (section-3 decision 1):** **{r.n("binary_enrolled_per_arm", "int")}/arm** = learning-pilot design point (binary churn, {r.n("binary_relative_prevention_assumption", "pct0")} relative reduction); **{r.n("first_grid_e4_profit", "int")}/arm** = first qualifying grid point for variable profit (WP1 E4, γ = 20%, DEFF {r.n("deff_1p0", "f1")}); **{r.n("v2_grid_adjusted_calibration", "int")}/arm** = v2 fully loaded first qualifying grid point. {r.n("v2_grid_top", "int")} appears only as "unadjusted not established through {r.n("v2_grid_top", "int")}". None replaces another.',
        '',
        f'## 2. Estimator table — γ = 20%, DEFF {r.n("deff_1p0", "f1")} (the WP1 grid)',
        '',
        f'### At {r.n("binary_enrolled_per_arm", "int")}/arm',
        '',
        '| Estimator | Gross-effect power | Variable-profit power | Status |',
        '|---|---:|---:|---|',
        est_row('E1_churn', 'e1_churn', 7872),
        est_row('E2_literal_oracle', 'e2_oracle', 7872, oracle=True),
        est_row('E3_literal_oracle', 'e3_oracle', 7872, oracle=True),
        est_row('E2_observed', 'e2_observed', 7872),
        est_row('E3_observed', 'e3_observed', 7872),
        est_row('E4_V_stratified', 'e4', 7872),
        '',
        f'### At {r.n("arm_80k", "int")}/arm',
        '',
        '| Estimator | Gross-effect power | Variable-profit power | Status |',
        '|---|---:|---:|---|',
        est_row('E1_churn', 'e1_churn', 80000),
        est_row('E2_literal_oracle', 'e2_oracle', 80000, oracle=True),
        est_row('E3_literal_oracle', 'e3_oracle', 80000, oracle=True),
        est_row('E2_observed', 'e2_observed', 80000),
        est_row('E3_observed', 'e3_observed', 80000),
        est_row('E4_V_stratified', 'e4', 80000),
        '',
        f'A single "80,000" hides a **{r.n("spread_80k_profit_e2obs_vs_e4", "pp1")}** spread in variable-profit power between E2_observed ({r.n("est_e2_observed_80000_profit", "pct1")}) and E3_observed / E4 ({r.n("est_e3_observed_80000_profit", "pct1")} / {r.n("est_e4_80000_profit", "pct1")}). Any slide must name the estimator. The WP2 decision-quality row uses **E3_observed**; the WP1 power table uses **E4**.',
        '',
        f'## 3. DEFF table — E4, γ = 20%',
        '',
        f'| DEFF | {r.n("binary_enrolled_per_arm", "int")}/arm gross effect | {r.n("binary_enrolled_per_arm", "int")}/arm variable profit | {r.n("max_per_arm_one_list", "int")}/arm gross effect | {r.n("max_per_arm_one_list", "int")}/arm variable profit |',
        '|---|---:|---:|---:|---:|',
        *deff_rows,
        '',
        f'DEFF {r.n("deff_default", "f1")} is used everywhere in v4 text (decision 3). The WP1 first-qualifying-grid search was run at DEFF {r.n("deff_1p0", "f1")}; the {r.n("first_grid_e4_profit", "int")}/arm and {r.n("first_grid_e4_effect", "int")}/arm grid points are therefore DEFF-{r.n("deff_1p0", "f1")} statements and are labelled as such.',
        '',
        '## 4. Bridge sentences (≤ 25 words each; word counts bound)',
        '',
        '| Key | Sentence | Words |',
        '|---|---|---:|',
        *[f'| `{key}` | {text} | {r.n(f"words_{key}", "int")} |' for key, text in bridges.items()],
        '',
        '## 5. Pilot purpose statement',
        '',
        f'At {r.n("binary_enrolled_per_arm", "int")}/arm, γ = 20%, DEFF {r.n("deff_default", "f1")} (E3_observed, CI rule): **scale {r.n("dq_7872_g20_p_scale", "pct1")} / extend {r.n("dq_7872_g20_p_extend", "pct1")} / stop {r.n("dq_7872_g20_p_stop", "pct1")}**. At γ = 0 (no effect): extend {r.n("dq_7872_g0_p_extend", "pct1")} / stop {r.n("dq_7872_g0_p_stop", "pct1")} — the stop rule is not a clean stop.',
        '',
        f'The standard error of the estimated prevention γ̂ at {r.n("binary_enrolled_per_arm", "int")}/arm (p0 = {r.n("binary_p0", "pct4")}, {r.n("binary_relative_prevention_assumption", "pct0")} relative reduction) is **{r.n("se_gamma_hat_difference_scaled", "pp1")}** by SE(p̂0 − p̂1)/p0 (the convention behind the brief\'s ≈ 6.8 pp), **{r.n("se_gamma_hat_delta_full", "pp2")}** by the full two-arm delta method, and {r.n("se_gamma_hat_difference_scaled_deff", "pp1")} with DEFF {r.n("deff_default", "f1")}. The gap between the {r.n("binary_relative_prevention_assumption", "pct0")} assumption and the {r.n("g_star", "pct1")} break-even is **{r.n("gap_assumption_to_break_even", "pp1")}** — well under one standard error. **The pilot cannot resolve break-even; it is a learning / launch and harm-detection step**, not a profit proof.',
        '',
        'Formulas (recorded): `SE_diff/p0 = sqrt(p0(1−p0)/n + p1(1−p1)/n) / p0`; `SE_delta = sqrt([p1(1−p1)/n]/p0² + [p1²/p0⁴]·p0(1−p0)/n)`; `gap = γ_assumed − K/G`.',
        '',
        '## 6. Monitor break-even prior π* — definition check (G10)',
        '',
        f'WP5 reports π* = **{r.n("pi_star_fully_loaded", "pct6")}** (γ = 20%, {r.n("treated_contact_cost", "usd0")}/contact). Its grid `net` equals gross − contacts − {r.n("wp5_fixed_cost_in_net", "usd0")}, i.e. the startup is **included** (fully loaded), contrary to the brief\'s "startup excluded" label. The startup-excluded crossing on the same grid is ≈ **{r.n("pi_star_startup_excluded", "pct4")}** (between grid priors {r.n("pi_star_excluded_lower_prior", "pct2")} and {r.n("pi_star_excluded_upper_prior", "pct2")}). The fully loaded margin to the 2% prior is {r.n("fully_loaded_margin_pp", "pp3")}. D7 recomputes π*(γ) for both definitions with the exact v2 functions.',
        '',
        '## 7. Transport',
        '',
        f'Selected non-test control churn {r.n("selected_control_churn", "pct6")} vs the {r.n("deployment_prior", "pct0")} deployment prior = **{r.n("transport_ratio", "x2")}** — an assumption, not a measurement; the 5th-percentile nets above inherit it.',
        '',
    ]
    body = dict(numbers=n.entries, bridges=bridges, bridge_word_counts=word_counts, deff_default=DEFF_DEFAULT,
                pi_star_startup_excluded_detail=dict(lower_prior=lo, upper_prior=hi, lower_net=net_lo, upper_net=net_hi, method='linear interpolation of (actual_gross - contacts) between adjacent 0.01-pp grid priors'))
    inputs = [c.ROOT / p for p in (FM, WP1, WP1J, WP2DQ, WP2EVSI, WP3, WP5, WP5G, INV)]
    c.write_json(RESULTS, body, __file__, TASK_INDEX, inputs)
    r.write(c.ADDONS / 'YARDSTICK.md', '\n'.join(md), c.RESULTS / 'YARDSTICK_render.json')
    print('bridge word counts:', word_counts)
    print('pi* startup excluded:', pi_ex)
    print('wrote YARDSTICK.md and results/yardstick.json with', len(n.entries), 'numbers')


if __name__ == '__main__':
    main()
