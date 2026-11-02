"""D0 — preflight: deliverable hashes vs handoff; section-9 self-checks reproduced from artifacts (G10: report, never tune)."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4common as c  # noqa: E402
import state  # noqa: E402

TASK_INDEX = 0
FM = 'v2_work/final_metrics.json'
WP1 = 'v3_addons/results/wp1_power.csv'
WP2DQ = 'v3_addons/results/wp2_decision_quality.csv'
WP2EVSI = 'v3_addons/results/wp2_evsi.json'
WP3 = 'v3_addons/results/wp3_roi_band.json'
WP5 = 'v3_addons/results/wp5_label_shift.json'
INV = 'v3_addons/results/inventory.json'
HANDOFF = c.ROOT / 'FINAL_ASSESSMENT_HANDOFF.md'
DELIVERABLES = ('philopateer.pdf', 'philopateer.pptx', 'philopateer.ipynb', 'references.txt')


def handoff_hashes():
    text = HANDOFF.read_text(encoding='utf-8')
    found = {}
    for name in DELIVERABLES:
        match = re.search(r'^\|\s*' + re.escape(name) + r'\s*\|\s*`([0-9a-f]{64})`\s*\|', text, re.M)
        if not match:
            raise SystemExit('handoff hash row missing for ' + name)
        found[name] = match.group(1)
    return found


def main():
    runtime = c.runtime_record()
    print('verify_runtime pools:', runtime['pools'])
    n = c.Numbers()

    # --- economics constants (final_metrics.json)
    n.source('bayes_actual_gross', FM, 'deployment_policies.bayes.actual_gross')
    n.source('bayes_contacts', FM, 'deployment_policies.bayes.contacts')
    n.source('bayes_net', FM, 'deployment_policies.bayes.net')
    n.source('bayes_break_even_success', FM, 'deployment_policies.bayes.break_even_success')
    n.source('prevention_assumption', FM, 'pilot_calibration.spec.normal_binary_reference.relative_prevention_assumption', tag='[A]')
    n.source('startup_cost', FM, 'pilot_calibration.spec.cost_assumptions.startup_stage1', tag='[A]')
    n.source('treated_contact_cost', FM, 'pilot_calibration.spec.cost_assumptions.treated_contact', tag='[A]')
    n.source('control_incremental_contact_cost', FM, 'pilot_calibration.spec.cost_assumptions.control_incremental_contact', tag='[A]')
    n.derived('G', 'bayes_actual_gross / prevention_assumption', expect=93660.01994886, tolerance=1e-6,
              note='gross contribution per unit prevention, 100k cohort, nominal 10% contact (brief section 9)')
    n.derived('K', 'bayes_contacts + startup_cost', expect=14984.92153411, tolerance=1e-6,
              note='variable contact cost at $1 per weighted contact plus $5,000 startup')
    n.derived('g_star', 'K / G', expect=0.159992722, tolerance=1e-6, note='break-even prevention = K/G')
    n.derived('g_star_vs_stored', 'abs(g_star - bayes_break_even_success)', note='closed form vs stored break_even_success')
    n.derived('net_at_20', 'G * 0.2 - K', expect=3747.082456, tolerance=1e-6)
    n.derived('net_at_20_vs_stored', 'abs(net_at_20 - bayes_net)')
    n.source('slide11_net_lower', FM, 'deployment_intervals.net.lower', note='conditional on prevention = 0.2; descriptive row-resampling interval')
    n.source('slide11_net_upper', FM, 'deployment_intervals.net.upper', note='conditional on prevention = 0.2')
    n.derived('slide11_lower_vs_expected', 'abs(slide11_net_lower - 2761.37)', expect=0.0, tolerance=0.005)
    n.derived('slide11_upper_vs_expected', 'abs(slide11_net_upper - 4660.64)', expect=0.0, tolerance=0.005)

    # --- prior table (WP3) recomputed in closed form
    expected = {'6_14': (0.930004, -1172.92, 195.71, 2348.56), '6_24': (0.685037, -6166.36, 1093.29, 13119.44), '2_18': (0.168233, -13202.28, 832.36, 9988.30)}
    for index, (a, b) in enumerate(((6, 14), (6, 24), (2, 18))):
        key = f'{a}_{b}'
        n.source(f'prior_{key}_a', WP3, f'priors[{index}].a', tag='[A]')
        n.source(f'prior_{key}_b', WP3, f'priors[{index}].b', tag='[A]')
        n.derived(f'p_positive_{key}', f'beta_sf(g_star, prior_{key}_a, prior_{key}_b)', expect=expected[key][0], tolerance=1e-6)
        n.source(f'p_positive_{key}_wp3', WP3, f'priors[{index}].closed_form.p_positive')
        n.derived(f'p_positive_{key}_vs_wp3', f'abs(p_positive_{key} - p_positive_{key}_wp3)', expect=0.0, tolerance=1e-9)
        n.derived(f'expected_net_{key}', f'G * beta_mean(prior_{key}_a, prior_{key}_b) - K')
        n.source(f'expected_net_{key}_wp3', WP3, f'priors[{index}].closed_form.expected_net')
        n.derived(f'expected_net_{key}_vs_wp3', f'abs(expected_net_{key} - expected_net_{key}_wp3)', expect=0.0, tolerance=1e-6)
        n.derived(f'net_5pct_{key}', f'G * beta_ppf(0.05, prior_{key}_a, prior_{key}_b) - K', expect=expected[key][1], tolerance=0.005)
        n.source(f'net_5pct_{key}_wp3', WP3, f'priors[{index}].closed_form.net_5pct')
        n.derived(f'net_5pct_{key}_vs_wp3', f'abs(net_5pct_{key} - net_5pct_{key}_wp3)', expect=0.0, tolerance=1e-6)
        n.derived(f'evpi_{key}', f'G * beta_mean(prior_{key}_a, prior_{key}_b) * beta_sf(g_star, prior_{key}_a + 1, prior_{key}_b) '
                                 f'- K * beta_sf(g_star, prior_{key}_a, prior_{key}_b) - max(expected_net_{key}, 0)',
                  expect=expected[key][2], tolerance=0.005, note='EVPI per cohort = E[(G*gamma-K)^+] - (E[net])^+ for Beta prior, closed form')
        n.source(f'evpi_{key}_wp3', WP3, f'priors[{index}].closed_form.evpi_per_cohort')
        n.derived(f'evpi_{key}_vs_wp3', f'abs(evpi_{key} - evpi_{key}_wp3)', expect=0.0, tolerance=1e-6)
        n.derived(f'evpi12_{key}', f'12 * evpi_{key}', expect=expected[key][3], tolerance=0.005, tag='[A]', note='12 identical cohorts assumed')
    # --- EVSI (WP2) at 7,872/arm
    scenarios = c.read_json(c.ROOT / WP2EVSI)['scenarios']
    for index, scenario in enumerate(scenarios):
        if scenario['n_per_arm'] == 7872:
            key = f'{scenario["a"]}_{scenario["b"]}'
            n.source(f'evsi_7872_{key}', WP2EVSI, f'scenarios[{index}].evsi_per_cohort', seed=None,
                     note='numerical preposterior value per cohort; not funding proof')
    n.derived('evsi_7872_6_14_vs_expected', 'abs(evsi_7872_6_14 - 45.27)', expect=0.0, tolerance=0.005)
    n.derived('evsi_7872_6_24_vs_expected', 'abs(evsi_7872_6_24 - 531.22)', expect=0.0, tolerance=0.005)
    n.derived('evsi_7872_2_18_vs_expected', 'abs(evsi_7872_2_18 - 455.45)', expect=0.0, tolerance=0.005)

    # --- WP1 E4 power
    e4 = {(7872, 1.0): (0.786, 0.279), (7872, 1.1): (0.760, 0.254), (7872, 1.25): (0.725, 0.216), (5000, 1.1): (0.556, 0.179)}
    for (arm, deff), (eff, prof) in e4.items():
        tag = f'{arm}_deff{str(deff).replace(".", "p")}'
        n.source(f'e4_effect_{tag}', WP1, f'where(method=E4_V_stratified;n_per_arm={arm};gamma=0.2;deff={deff}).effect_power', value=eff)
        n.source(f'e4_profit_{tag}', WP1, f'where(method=E4_V_stratified;n_per_arm={arm};gamma=0.2;deff={deff}).profit_power', value=prof)
    n.source('e1_binary_power_7872', WP1, 'where(method=E1_churn;n_per_arm=7872;gamma=0.2;deff=1.0).effect_power', value=0.832)
    n.source('p0', FM, 'pilot_calibration.spec.normal_binary_reference.p0', tag='[A]')
    n.source('p1', FM, 'pilot_calibration.spec.normal_binary_reference.p1', tag='[A]')
    n.source('enrolled_per_arm', FM, 'pilot_calibration.spec.normal_binary_reference.enrolled_per_arm')
    n.derived('e1_normal_approx_7872', 'norm_cdf((p0 - p1) / sqrt(p0 * (1 - p0) / enrolled_per_arm + p1 * (1 - p1) / enrolled_per_arm) - norm_ppf(0.975))',
              expect=0.84, tolerance=0.01, note='two-sample normal approximation, no follow-up loss')

    # --- WP2 decision quality
    for col, exp in (('p_scale', 0.076), ('p_extend', 0.919), ('p_stop', 0.005)):
        n.source(f'dq_7872_g20_deff1p1_{col}', WP2DQ, f'where(n_per_arm=7872;gamma=0.2;deff=1.1).{col}', value=exp)
    for col, exp in (('p_extend', 0.475), ('p_stop', 0.525)):
        n.source(f'dq_7872_g0_deff1p1_{col}', WP2DQ, f'where(n_per_arm=7872;gamma=0.0;deff=1.1).{col}', value=exp)

    # --- transport, pi*, queues
    n.source('selected_control_churn', INV, 'population.selected_control_churn')
    n.source('deployment_prior', FM, 'a_spec.deployment_prior', tag='[A]') if 'deployment_prior' in c.read_json(c.ROOT / FM).get('a_spec', {}) else n.declared('deployment_prior', 0.02, '[A]', 'hypothetical 2% deployment prior (final_metrics prior_stress row 2 / a_spec)')
    n.derived('transport_ratio', 'selected_control_churn / deployment_prior', expect=2.42, tolerance=0.005, tag='[A]', note='assumption, not measurement')
    n.source('pi_star_g20_startup_excluded', WP5, 'break_even.first_crossing.prior_star', note='gamma=0.2, $1 variable cost, startup excluded; exact v2 functions on non-test scores')
    n.derived('pi_star_vs_expected', 'abs(pi_star_g20_startup_excluded - 0.01546417)', expect=0.0, tolerance=1e-8)
    names = ('billing', 'network', 'handset', 'residual')
    for index, name in enumerate(names):
        n.source(f'queue_{name}_count', FM, f'pilot_test.queues[{index}].raw_count')
        n.source(f'queue_{name}_value_share', FM, f'pilot_test.queues[{index}].share_at_risk_value')
    n.derived('queue_total', 'queue_billing_count + queue_network_count + queue_handset_count + queue_residual_count', expect=2505, tolerance=0)
    for name, lift in zip(names, (1.007, 0.979, 0.972, 1.027)):
        n.derived(f'queue_{name}_count_share', f'queue_{name}_count / queue_total')
        n.derived(f'queue_{name}_lift_exact', f'queue_{name}_value_share / queue_{name}_count_share',
                  note='exact value share / count share from final_metrics')
        n.derived(f'queue_{name}_lift_quoted', f'round(queue_{name}_value_share, 3) / queue_{name}_count_share', expect=lift, tolerance=0.0005,
                  note='reviewer arithmetic: published one-decimal percentage share / exact count share')

    # --- SE(gamma-hat) at 7,872/arm
    n.derived('se_gamma_hat_delta_full', 'sqrt((p1 * (1 - p1) / enrolled_per_arm) / p0**2 + (p1**2 / p0**4) * (p0 * (1 - p0) / enrolled_per_arm))',
              expect=0.068, tolerance=0.0015, note='full delta method for gamma-hat = 1 - p1hat/p0hat, both arms random, n=7,872/arm, DEFF 1',
              discrepancy_note='the 6.8 pp quote corresponds to SE(p0hat-p1hat)/p0 with p0 held fixed (see se_gamma_hat_difference_scaled); the full two-arm delta method gives 6.06 pp; conclusion unchanged (both exceed the 4.0 pp gap several-fold)')
    n.derived('se_gamma_hat_difference_scaled', 'sqrt(p0 * (1 - p0) / enrolled_per_arm + p1 * (1 - p1) / enrolled_per_arm) / p0',
              expect=0.068, tolerance=0.0015, note='SE of the absolute churn difference divided by p0 (p0 treated as known); this is the convention that reproduces the 6.8 pp quote')
    n.derived('gap_assumption_to_break_even', 'prevention_assumption - g_star', note='20% assumed prevention minus break-even')
    n.derived('se_over_gap_full', 'se_gamma_hat_delta_full / gap_assumption_to_break_even', note='standard errors per gap, full delta method')
    n.derived('se_over_gap_difference_scaled', 'se_gamma_hat_difference_scaled / gap_assumption_to_break_even')

    # --- v2 80,000/arm power rows, both partitions (review quoted the descriptive test rows)
    fm = c.read_json(c.ROOT / FM)
    for part in ('pilot_calibration', 'pilot_test'):
        for index, row in enumerate(fm[part]['power_rows']):
            if row['enrolled_per_arm'] == 80000 and row['method'] in ('adjusted_contribution', 'unadjusted_contribution'):
                n.source(f'v2_80k_{row["method"].split("_")[0]}_power_{part.split("_")[1]}', FM, f'{part}.power_rows[{index}].simulated_power',
                         note=f'{part}: {"planning (calibration partition)" if part.endswith("calibration") else "descriptive (test partition, reused v1 probabilities)"}')
        n.source(f'v2_grid_adjusted_{part.split("_")[1]}', FM, f'{part}.simulated_required_enrolled_per_arm_grid.adjusted_contribution')

    # --- quotes from the v4 brief section 9 that the reproductions are compared with (declared, not measured)
    n.declared('brief_quote_se_gamma_hat', 0.068, '[R]', 'v4 brief section 9: "SE(gamma-hat) at 7,872/arm (delta method) ~ 6.8 pp"')
    n.declared('brief_quote_queue_network_lift', 0.979, '[R]', 'v4 brief section 9 reviewer arithmetic')
    n.declared('brief_quote_queue_handset_lift', 0.972, '[R]', 'v4 brief section 9 reviewer arithmetic')
    n.source('v3_outside_file_count', 'v3_addons/results/wp7_final_verification.json', 'directory_diff.files_after', note='v3 directory diff excluded v3_addons/')
    n.source('v3_manifest_file_count', 'v3_addons/results/wp7_final_verification.json', 'file_count', note='old v3 manifest size (predates WP8)')
    n.source('seed', FM, 'pilot_calibration.spec.seed')
    n.source('threads', FM, 'pilot_calibration.spec.threads')

    # --- deliverable hashes
    expected_hashes = handoff_hashes()
    hashes = {name: dict(handoff=expected_hashes[name], actual=c.digest(c.ROOT / name), size=(c.ROOT / name).stat().st_size)
              for name in DELIVERABLES}
    for name in hashes:
        hashes[name]['match'] = hashes[name]['handoff'] == hashes[name]['actual']
    all_match = all(item['match'] for item in hashes.values())

    checks = {name: entry for name, entry in n.entries.items() if 'expected' in entry}
    failures = [name for name, entry in checks.items() if not entry['matches_expected']]
    body = dict(numbers=n.entries, deliverable_hashes=hashes, deliverable_hashes_all_match=all_match,
                section9_checks=len(checks), section9_failures=failures,
                notes=[
                    'G, K, g_star, net_at_20 recomputed from deployment_policies.bayes with prevention 0.2 and startup 5000.',
                    'Prior table recomputed in closed form (scipy beta sf/ppf) and compared with WP3 closed_form values.',
                    'SE(gamma-hat): two formulas reported; see matches_expected flags (G10 - discrepancy reported, not tuned).',
                    'v2 80,000/arm adjusted power: pilot_test rows give 0.9525/0.3725 (review quote); pilot_calibration rows give 0.9725/0.5025. Both grids select 80,000.',
                ])
    inputs = [c.ROOT / p for p in (FM, WP1, WP2DQ, WP2EVSI, WP3, WP5, INV)] + [HANDOFF] + [c.ROOT / name for name in DELIVERABLES]
    c.write_json(c.RESULTS / 'd0_checks.json', body, __file__, TASK_INDEX, inputs)
    print(f'section 9 checks: {len(checks)}; failures: {failures}')
    print('deliverable hashes all match:', all_match)
    for name, item in hashes.items():
        print(f'  {name}: {"MATCH" if item["match"] else "MISMATCH"} {item["actual"][:16]}... size={item["size"]}')
    for name in failures:
        entry = checks[name]
        print(f'  DISCREPANCY {name}: value={entry["value"]!r} expected={entry["expected"]!r} tol={entry["expected_tolerance"]!r}')
    return 0 if all_match else 1


if __name__ == '__main__':
    sys.exit(main())
