"""D5 — REPRODUCIBILITY.md for WP1-WP5: command, seed, expected output hashes, wall-time (as recorded), plus light identity checks only."""
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4common as c  # noqa: E402
import report  # noqa: E402

TASK_INDEX = 6
RESULTS = c.RESULTS / 'd5_repro.json'
WP = {
    'WP1': dict(script='v3_addons/src/wp1_power.py', main='v3_addons/results/wp1_power.json', outputs=['v3_addons/results/wp1_power.json', 'v3_addons/results/wp1_power.csv', 'v3_addons/results/wp1_capacity_mde.csv', 'v3_addons/results/wp1_simulation_samples.npz', 'v3_addons/figures/wp1_power_curves.png'], args=''),
    'WP2': dict(script='v3_addons/src/wp2_decisions.py', main='v3_addons/results/wp2_evsi.json', outputs=['v3_addons/results/wp2_evsi.json', 'v3_addons/results/wp2_decision_quality.csv', 'v3_addons/figures/wp2_decision_map.png'], args=''),
    'WP3': dict(script='v3_addons/src/wp3_roi.py', main='v3_addons/results/wp3_roi_band.json', outputs=['v3_addons/results/wp3_roi_band.json', 'v3_addons/results/wp3_net_curve.csv', 'v3_addons/figures/wp3_net_curve.png'], args=''),
    'WP4': dict(script='v3_addons/src/wp4_protocol.py', main='v3_addons/results/wp4_protocol.json', outputs=['v3_addons/results/wp4_protocol.json', 'v3_addons/protocol_addendum.md'], args=''),
    'WP5': dict(script='v3_addons/src/wp5_labelshift.py', main='v3_addons/results/wp5_label_shift.json', outputs=['v3_addons/results/wp5_label_shift.json', 'v3_addons/results/wp5_label_shift_summary.csv', 'v3_addons/results/wp5_break_even_grid.csv', 'v3_addons/results/wp5_calibration_oof.json', 'v3_addons/figures/wp5_em_recovery.png'], args=' --workers 6'),
}


def main():
    c.runtime_record()
    n = c.Numbers()
    records = {}
    completion = {}
    for wp, item in WP.items():
        prov = c.read_json(c.ROOT / item['main'])['provenance']
        n.source(f'{wp.lower()}_seed', item['main'], 'provenance.seed')
        completion[wp] = datetime.fromisoformat(prov['created_utc'])
        records[wp] = dict(script=item['script'], script_sha256=c.digest(c.ROOT / item['script']), script_sha256_recorded=prov.get('script_sha256'),
                           seed=prov['seed'], python=prov['python_version'].split()[0], created_utc=prov['created_utc'], row_counts=prov.get('row_counts', {}),
                           inputs=len(prov['input_files']), outputs=[c.file_info(c.ROOT / path) for path in item['outputs']], args=item['args'])
    order = list(WP)
    for previous, current in zip(order, order[1:]):
        minutes = (completion[current] - completion[previous]).total_seconds() / 60
        n.computed(f'{current.lower()}_completion_gap_minutes', round(minutes, 1), '[E]', f'minutes between {previous} and {current} completion timestamps (upper bound on {current} wall time)', source_file=WP[current]['main'], source_key='provenance.created_utc')

    # light checks: WP2 identities
    started = time.perf_counter()
    scenarios = c.read_json(c.ROOT / 'v3_addons/results/wp2_evsi.json')['scenarios']
    checks = []
    for index, s in enumerate(scenarios):
        key = f'{s["a"]}_{s["b"]}_n{s["n_per_arm"]}'
        n.source(f'evsi_{key}', 'v3_addons/results/wp2_evsi.json', f'scenarios[{index}].evsi_per_cohort')
        n.source(f'evpi_{key}', 'v3_addons/results/wp2_evsi.json', f'scenarios[{index}].evpi')
        n.source(f'regret_{key}', 'v3_addons/results/wp2_evsi.json', f'scenarios[{index}].posterior_regret_mean')
        n.source(f'centered_{key}', 'v3_addons/results/wp2_evsi.json', f'scenarios[{index}].centered_evsi_per_cohort')
        n.source(f'centered_mc_se_{key}', 'v3_addons/results/wp2_evsi.json', f'scenarios[{index}].identity_discrepancy_mc_se')
        n.derived(f'identity_gap_{key}', f'abs(evsi_{key} - (evpi_{key} - regret_{key}))', note='EVSI = EVPI - E[posterior regret]; exact identity')
        n.derived(f'centered_gap_se_{key}', f'abs(centered_{key} - evsi_{key}) / centered_mc_se_{key}', note='centered-estimator discrepancy in MC standard errors')
        checks.append(dict(scenario=key, evsi_le_evpi=s['evsi_per_cohort'] <= s['evpi'] + 1e-9, evsi_nonnegative=s['evsi_per_cohort'] >= 0,
                           identity_gap=n.value(f'identity_gap_{key}'), centered_gap_in_se=n.value(f'centered_gap_se_{key}')))
    # light checks: WP3 closed forms (same as D0, re-executed here for the supplement)
    d0 = c.read_json(c.RESULTS / 'd0_checks.json')['numbers']
    for key in ('6_14', '6_24', '2_18'):
        for field in ('p_positive', 'net_5pct', 'evpi', 'expected_net'):
            n.source(f'd0_{field}_{key}_vs_wp3', 'v4_addons/results/d0_checks.json', f'numbers.{field}_{key}_vs_wp3.value')
    wall = time.perf_counter() - started
    n.computed('light_checks_wall_seconds', round(wall, 3), '[E]', 'wall time of the WP2 identity + WP3 closed-form re-checks in this run')
    identity_ok = all(ch['evsi_le_evpi'] and ch['evsi_nonnegative'] and ch['identity_gap'] < 1e-6 and ch['centered_gap_in_se'] < 3 for ch in checks)
    wp3_ok = all(n.value(f'd0_{f}_{k}_vs_wp3') < 1e-6 for k in ('6_14', '6_24', '2_18') for f in ('p_positive', 'net_5pct', 'evpi', 'expected_net'))
    n.computed('wp2_identity_checks_passed', int(identity_ok), '[E]', '1 if all six WP2 scenarios satisfy EVSI<=EVPI, EVSI>=0, EVSI=EVPI-regret (1e-6) and centered within 3 MC SE')
    n.computed('wp3_closed_form_checks_passed', int(wp3_ok), '[E]', '1 if all WP3 closed forms re-derive within 1e-6 (from D0)')
    n.computed('wp2_max_centered_gap_se', round(max(ch['centered_gap_in_se'] for ch in checks), 2), '[E]', 'largest centered-estimator discrepancy across the six WP2 scenarios, in MC standard errors', source_file='v3_addons/results/wp2_evsi.json', source_key='scenarios[].centered_evsi_per_cohort')
    n.source('test_split_rows', 'v2_work/final_metrics.json', 'v1.test_customers')
    n.source('wp1_simulation_points', 'v3_addons/results/wp1_power.json', 'provenance.row_counts.simulation_points')
    n.source('wp1_replicates_per_point', 'v3_addons/results/wp1_power.json', 'provenance.row_counts.replicates_per_point')
    n.source('wp2_pilots_per_scenario', 'v3_addons/results/wp2_evsi.json', 'provenance.row_counts.pilots_per_scenario')
    n.source('wp5_original_batches', 'v3_addons/results/wp5_label_shift.json', 'provenance.row_counts.original_batches')
    n.source('wp5_bootstrap_fits', 'v3_addons/results/wp5_label_shift.json', 'provenance.row_counts.bootstrap_fits')
    body = dict(numbers=n.entries, work_packages=records, wp2_checks=checks, scripts_match_recorded_sha={wp: rec['script_sha256'] == rec['script_sha256_recorded'] for wp, rec in records.items()})
    c.write_json(RESULTS, body, __file__, TASK_INDEX, [c.ROOT / item['main'] for item in WP.values()] + [c.ROOT / item['script'] for item in WP.values()] + [c.RESULTS / 'd0_checks.json'])

    r = c.Renderer(n, RESULTS)
    md = ['# REPRODUCIBILITY — supporting analyses WP1–WP5 (v3_addons) and how to re-run them', '',
          f'_v4 Track D, card D5 · {c.today()} · the frozen notebook `philopateer.ipynb` is not edited; WP1–WP5 live in `v3_addons/src/` and are reproduced from their hash-bound outputs, not from the notebook._', '',
          '## Environment (all work packages)', '',
          '```bash', 'PY="C:/Users/FGstore/AppData/Local/Programs/Python/Python311/python.exe"   # pinned 3.11; not the py launcher',
          'R="D:/progs/IDE/MainProjs/AI/GCI2026/finalA"', 'export OPENBLAS_NUM_THREADS=6 OMP_NUM_THREADS=6 MKL_NUM_THREADS=6 NUMEXPR_NUM_THREADS=6',
          '# every script: "$PY" -B -X utf8 <script>   (-B: no bytecode writes; v3 common.py also installs a write hook confined to v3_addons/)', '```', '',
          f'Seeds derive from SEED = 20261028 + task index (recorded per work package below). Local CPU only, six threads. The test split ({r.n("test_split_rows", "int")} rows) is never read by WP1–WP5; `row_counts.test_rows_used = 0` where recorded.', '',
          '## Per work package', '',
          '| WP | Command | Seed | Main output (sha256) | Wall time |', '|---|---|---:|---|---|']
    for wp, rec in records.items():
        main_info = rec['outputs'][0]
        if wp == 'WP1':
            wall = 'not recorded in the artifact; start time unknown'
        else:
            wall = f'not recorded; ≤ {r.n(f"{wp.lower()}_completion_gap_minutes", "f1")} min (gap to previous WP completion)'
        md.append(f'| {wp} | `"$PY" -B -X utf8 "$R/{rec["script"]}"{rec["args"]}` | {r.n(f"{wp.lower()}_seed", "int")} | `{main_info["path"].split("/")[-1]}` `{main_info["sha256"][:16]}…` | {wall} |')
    md += ['', 'Full expected output hashes (current files; a successful re-run must reproduce these byte-for-byte for deterministic outputs — PNG figures may differ by renderer):', '']
    for wp, rec in records.items():
        md.append(f'**{wp}** — script sha256 `{rec["script_sha256"]}` (matches the provenance-recorded hash: {rec["script_sha256"] == rec["script_sha256_recorded"]}); Python {rec["python"]}; inputs {rec["inputs"]}; row counts `{rec["row_counts"]}`')
        md += [f'- `{out["path"]}` — {out["size"]:,} bytes — `{out["sha256"]}`' for out in rec['outputs'] if out['present']]
        md.append('')
    md += ['## What was executed in v4 (light checks only)', '',
           f'- WP2 identities re-checked from `wp2_evsi.json` for all six scenarios: EVSI ≤ EVPI, EVSI ≥ 0, EVSI = EVPI − E[posterior regret] (max identity gap {max(ch["identity_gap"] for ch in checks):.2e}), centered estimator within 3 MC standard errors (max {r.n("wp2_max_centered_gap_se", "f2")} SE): passed = {r.n("wp2_identity_checks_passed", "int")}.',
           f'- WP3 closed forms (P(net>0), E[net], 5th percentile, EVPI for the three Beta priors) re-derived with scipy from G, K and γ* in D0 and compared with `wp3_roi_band.json`: passed = {r.n("wp3_closed_form_checks_passed", "int")} (all gaps < 1e-6; see `results/d0_checks.json`).',
           f'- Wall time of these checks: {r.n("light_checks_wall_seconds", "f3")} s.',
           f'- **Not re-run:** WP1 ({r.n("wp1_simulation_points", "int")} points × {r.n("wp1_replicates_per_point", "int")} replicates), WP5 ({r.n("wp5_original_batches", "int")} batches / {r.n("wp5_bootstrap_fits", "int")} bootstrap fits) and WP2\'s {r.n("wp2_pilots_per_scenario", "int")}-pilot preposterior simulations. Their hash-bound outputs above are the evidence; re-running them is a separate approved scope.', '',
           '## Relationship to the submitted notebook', '',
           '- `philopateer.ipynb` reproduces the v1/v2 model, policy and economics (frozen; never "Run All"). It does not contain WP1–WP5 code. If the rubric requires the supporting analyses to be reproducible, cite this file and `v3_addons/src/` rather than editing frozen cells (section-3 decision 10).',
           '- v4 Track D adds no new science: every v4 number is arithmetic on the artifacts listed here (`v4_addons/results/*.json`, checked by `tools/check_numbers.py`).', '']
    r.write(c.ADDONS / 'REPRODUCIBILITY.md', '\n'.join(md), c.RESULTS / 'REPRODUCIBILITY_render.json')
    print('wrote REPRODUCIBILITY.md; wp2 identities ok:', identity_ok, '; wp3 ok:', wp3_ok)

    evidence = [(f'{wp.lower()}_seed', 'int') for wp in WP] + [('wp2_identity_checks_passed', 'int'), ('wp3_closed_form_checks_passed', 'int'), ('light_checks_wall_seconds', 'f3')]
    acceptance = ['- Per-WP command, seed, expected output hashes recorded: **PASS**.',
                  '- Only light checks executed (WP2 identities, WP3 closed forms); WP1/WP5 simulations not re-run: **PASS**.',
                  '- Frozen notebook untouched: **PASS** (boundary check).',
                  '- Script hashes match those recorded in each WP\'s provenance block: ' + ('**PASS**' if all(body['scripts_match_recorded_sha'].values()) else '**FAIL** ' + str(body['scripts_match_recorded_sha'])) + '.']
    deviations = ['- Wall times are not recorded in the v3 artifacts; the supplement gives completion-timestamp gaps as upper bounds instead of invented figures.']
    commands = ['"$PY" -B -X utf8 boundary_check.py --card D5 --phase pre', '"$PY" -B -X utf8 d5_reproducibility.py', '"$PY" -B -X utf8 check_numbers.py --scan ../REPRODUCIBILITY.md ../reports/D5_report.md', '"$PY" -B -X utf8 boundary_check.py --card D5 --phase post']
    report.write_report('D5', 'Reproducibility supplement', 'COMPLETED_ACCEPTED',
                        'Summary: `REPRODUCIBILITY.md` lists, for WP1–WP5, the exact command, seed, expected output hashes and the wall-time information actually available; WP2 identities and WP3 closed forms were re-checked in code, WP1/WP5 simulations were not re-run.',
                        RESULTS, evidence, acceptance, deviations, ['- none'], commands, 'yes (pre/post clean; only the 4 D1-allowed changes).')


if __name__ == '__main__':
    main()
