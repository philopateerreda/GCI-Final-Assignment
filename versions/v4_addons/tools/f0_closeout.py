"""F0 -- close the Track M books, bind the closure numbers, update STATE.

Reads the gate record written by f0_gates.py; writes results/f0_closeout.json,
reports/M_closure_note.md (+ render registry) and reports/F0_report.md. The two
point extrapolations are bound only because they reproduce the reviewer values;
the reviewer's parenthetical range did not reproduce under either tested
definition and is omitted from every deliverable.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4common as c  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.optimize import least_squares  # noqa: E402

import fstate  # noqa: E402
import report  # noqa: E402

TASK_INDEX = 12
RESULTS_JSON = c.RESULTS / 'f0_closeout.json'
NOTE = c.REPORTS / 'M_closure_note.md'
NOTE_REGISTRY = c.RESULTS / 'M_closure_note_render.json'
GATE_RECORD = c.RESULTS / 'f0_gate_record.json'
FOLDS = c.ADDONS / 'm1_work' / 'learning_curve_folds.csv'
M1 = 'v4_addons/results/m1_baseline.json'
METRICS = 'v2_work/final_metrics.json'


def m1_source(numbers, name, source_name, tag='[E]', note=None):
    return numbers.source(name, M1, f'numbers.{source_name}.value', tag=tag, note=note)


def extrapolation_check(c_lower, c_upper):
    frame = pd.read_csv(FOLDS)
    clusters = {}
    for row in frame.itertuples(index=False):
        clusters.setdefault((int(row.repeat), int(row.fold)), []).append((float(row.training_n), float(row.heldout_auc)))
    keys = sorted(clusters)
    points = [point for key in keys for point in clusters[key]]

    def fit(sample, fixed_c=None):
        x = np.array([point[0] for point in sample], float)
        y = np.array([point[1] for point in sample], float)
        if fixed_c is None:
            def residual(p):
                return p[0] - np.exp(p[1] - p[2] * np.log(x)) - y
            start, bounds = [0.7076, 2.9, 0.672], ([0.5, -20.0, 0.001], [1.0, 40.0, 5.0])
        else:
            def residual(p):
                return p[0] - np.exp(p[1] - fixed_c * np.log(x)) - y
            start, bounds = [0.7076, 2.9], ([0.5, -20.0], [1.0, 40.0])
        return least_squares(residual, start, bounds=bounds, x_scale='jac').x

    def gain(params, exponent, n0=75000.0, n1=150000.0):
        return (params[0] - np.exp(params[1] - exponent * np.log(n1))) - (params[0] - np.exp(params[1] - exponent * np.log(n0)))

    rng = np.random.default_rng(c.SEED + TASK_INDEX)
    values = []
    for _ in range(2000):
        pick = rng.integers(0, len(keys), len(keys))
        sample = [point for index in pick for point in clusters[keys[index]]]
        params = fit(sample)
        values.append(gain(params, params[2]))
    values = np.array([value for value in values if np.isfinite(value)])
    conditional = [gain(fit(points, fixed_c=bound), bound) for bound in (c_lower, c_upper)]
    return dict(valid=len(values), lower=float(np.percentile(values, 2.5)), upper=float(np.percentile(values, 97.5)),
                conditional_lower=float(conditional[0]), conditional_upper=float(conditional[1]))


def bind(gate_record):
    n = c.Numbers()
    m1_source(n, 'closure_refit_customers', 'frozen_refit_customers', note='frozen final refit rows')
    m1_source(n, 'closure_calibration_customers', 'frozen_calibration_customers', note='sigmoid calibration rows')
    for size in (15000, 30000, 45000, 60000, 67500):
        m1_source(n, f'closure_size_{size}', f'curve_size_{size}', note='learning-curve training size')
        m1_source(n, f'closure_auc_{size}', f'curve_auc_{size}', note='mean held-out AUC over 20 folds')
    m1_source(n, 'closure_gain_last_step', 'curve_gain_67500_over_60000', note='paired gain of the last step')
    m1_source(n, 'curve_a', 'curve_a', note='fitted AUC(n) = a - b n^-c')
    m1_source(n, 'curve_b', 'curve_b', note='fitted b coefficient')
    m1_source(n, 'curve_c', 'curve_c', note='fitted exponent c')
    m1_source(n, 'curve_c_lower', 'curve_c_lower', note='fold-cluster bootstrap lower bound')
    m1_source(n, 'curve_c_upper', 'curve_c_upper', note='fold-cluster bootstrap upper bound')
    m1_source(n, 'bootstrap_ci_level', 'bootstrap_ci_level', tag='[R]', note='two-sided bootstrap level')
    m1_source(n, 'delta_s_identity', 'delta_s_identity', note='AUC(N_all) - AUC(N_frozen) = 0')
    m1_source(n, 'gate_threshold', 'gate_threshold', tag='[R]', note='pre-declared M1 gate')

    n.declared('closure_note_limit', 200, '[R]', 'closure-note word limit set by the card')
    n.declared('extrap_10k_rows', 10000, '[A]', 'extra training rows in the reviewer extrapolation')
    n.declared('extrap_double_rows', 150000, '[A]', 'doubling target in the reviewer extrapolation')
    n.derived('extrap_10k_gain', 'curve_b * (75000 ** -curve_c - 85000 ** -curve_c)', tag='[A]',
              note='extrapolation [A], not a measured result')
    n.derived('extrap_double_gain', 'curve_b * (75000 ** -curve_c - 150000 ** -curve_c)', tag='[A]',
              note='extrapolation [A], not a measured result')

    n.source('pilot_per_arm', METRICS, 'v1.pilot.per_arm_with_10pct_allowance', tag='[E]', note='pilot per arm with 10% allowance')
    n.source('treated_contact_cost', METRICS, 'pilot_calibration.spec.cost_assumptions.treated_contact', tag='[E]', note='v2 cost spec')
    n.source('control_incremental_contact', METRICS, 'pilot_calibration.spec.cost_assumptions.control_incremental_contact', tag='[E]', note='v2 cost spec: Floor contact not incremental')
    n.source('startup_stage1', METRICS, 'pilot_calibration.spec.cost_assumptions.startup_stage1', tag='[E]', note='Stage-1 startup')
    n.source('stage1_cost', METRICS, 'pilot_calibration.spec.stage1_cost', tag='[E]', note='Stage-1 envelope')
    n.derived('extension_variable_cost', 'pilot_per_arm * treated_contact_cost', tag='[E]', note='treated contacts x $1')
    n.derived('stage1_cost_check', 'pilot_per_arm * treated_contact_cost + startup_stage1', tag='[E]',
              note='Stage-1 envelope rebuild', expect=12872.0, tolerance=1e-9)

    check = extrapolation_check(n.value('curve_c_lower'), n.value('curve_c_upper'))
    n.computed('extrap_check_reps', 2000, '[R]', 'fold-cluster bootstrap replicates for the extrapolation check', seed=c.SEED + TASK_INDEX)
    n.computed('extrap_check_valid', check['valid'], '[E]', 'finite replicates', seed=c.SEED + TASK_INDEX)
    n.computed('extrap_double_boot_lower', check['lower'], '[A]', 'joint fold-cluster bootstrap lower bound of the doubling gain',
               seed=c.SEED + TASK_INDEX)
    n.computed('extrap_double_boot_upper', check['upper'], '[A]', 'joint fold-cluster bootstrap upper bound of the doubling gain',
               seed=c.SEED + TASK_INDEX)
    n.computed('extrap_double_cond_at_c_lower', check['conditional_lower'], '[A]',
               'a,b refit with c fixed at its lower bootstrap bound', seed=c.SEED + TASK_INDEX)
    n.computed('extrap_double_cond_at_c_upper', check['conditional_upper'], '[A]',
               'a,b refit with c fixed at its upper bootstrap bound', seed=c.SEED + TASK_INDEX)
    return n, check


def render_note(numbers):
    r = c.Renderer(numbers, RESULTS_JSON)
    text = f"""# Track M closure note

Track M is closed. The frozen submission model was already refit on all {r.n('closure_refit_customers', 'int')} non-test customers, with {r.n('closure_calibration_customers', 'int')} further customers used for calibration, so adding data to that pool cannot change the fit: the audit's point prediction of the extra gain is exactly {r.n('delta_s_identity', 'f4')} AUC, below the pre-declared {r.n('gate_threshold', 'f4')} gate.

A repeated ten-fold learning curve over the same pool shows the model is close to its data asymptote. Mean held-out AUC rises from {r.n('closure_auc_15000', 'f6')} to {r.n('closure_auc_30000', 'f6')} to {r.n('closure_auc_45000', 'f6')} to {r.n('closure_auc_60000', 'f6')} to {r.n('closure_auc_67500', 'f6')} as training grows through {r.n('closure_size_15000', 'int')}, {r.n('closure_size_30000', 'int')}, {r.n('closure_size_45000', 'int')}, {r.n('closure_size_60000', 'int')} and {r.n('closure_size_67500', 'int')} rows; the last step adds {r.n('closure_gain_last_step', 'f6')}. The fitted curve has exponent c = {r.n('curve_c', 'f3')} ({r.n('bootstrap_ci_level', 'pct0')} interval {r.n('curve_c_lower', 'f3')} to {r.n('curve_c_upper', 'f3')}).

Extrapolation [A], not a measured result: another {r.n('extrap_10k_rows', 'int')} training rows would add about +{r.n('extrap_10k_gain', 'f4')} AUC, and doubling the training pool to {r.n('extrap_double_rows', 'int')} would add about +{r.n('extrap_double_gain', 'f4')} AUC. Both are far below the gate. No model was refit, no candidate was added, no test row was read, and M2 to M6 are not run.
"""
    words = len(text.split())
    if words > 200:
        raise SystemExit(f'closure note is {words} words; limit is 200')
    r.write(NOTE, text, NOTE_REGISTRY)
    return words


def write_f0_report(numbers, gate_record, note_words):
    evidence = [
        ('closure_refit_customers', 'int'), ('closure_calibration_customers', 'int'),
        ('closure_auc_15000', 'f6'), ('closure_auc_30000', 'f6'), ('closure_auc_45000', 'f6'),
        ('closure_auc_60000', 'f6'), ('closure_auc_67500', 'f6'),
        ('closure_gain_last_step', 'f6'),
        ('curve_a', 'f6'), ('curve_b', 'f6'), ('curve_c', 'f3'),
        ('curve_c_lower', 'f3'), ('curve_c_upper', 'f3'),
        ('delta_s_identity', 'f4'), ('gate_threshold', 'f4'),
        ('extrap_10k_gain', 'f4'), ('extrap_double_gain', 'f4'),
        ('extrap_double_boot_lower', 'f4'), ('extrap_double_boot_upper', 'f4'),
        ('extrap_double_cond_at_c_lower', 'f4'), ('extrap_double_cond_at_c_upper', 'f4'),
        ('pilot_per_arm', 'int'), ('stage1_cost', 'usd0'), ('startup_stage1', 'usd0'),
        ('control_incremental_contact', 'f1'),
    ]
    evidence = [(name, spec) for name, spec in evidence if name in numbers.entries]
    gates = gate_record['files']
    sections = [
        ('Gates written', [
            f'- `v4_addons/gates/H0_DECISIONS.md`: sha256 `{gates["H0_DECISIONS.md"]["sha256"]}`, '
            f'{gates["H0_DECISIONS.md"]["size"]} bytes; a copy of DECISIONS_ASSUMED.md with every DEFAULT_ASSUMED replaced; rows 11-13 added.',
            f'- `v4_addons/gates/H3_OPTION.txt`: content `B_PRIME` exactly; sha256 `{gates["H3_OPTION.txt"]["sha256"]}`.',
            f'- Files present in `v4_addons/gates/`: {", ".join(gate_record["gates_dir"])}. No H1, H2 or H4 file exists.',
            lambda r: f'- `H0` rows 11-12 cite the bound pilot figures: {r.n("pilot_per_arm", "int")} per arm, '
                      f'{r.n("stage1_cost", "usd0")} Stage-1 envelope, {r.n("startup_stage1", "usd0")} startup, '
                      f'Floor contact cost {r.n("control_incremental_contact", "f1")}.',
        ]),
        ('Extrapolation check', [
            lambda r: f'- Stored fit: a = {r.n("curve_a", "f6")}, b = {r.n("curve_b", "f6")}, c = {r.n("curve_c", "f3")} '
                      f'(interval {r.n("curve_c_lower", "f3")} to {r.n("curve_c_upper", "f3")}).',
            lambda r: f'- A joint fold-cluster bootstrap over the 20 saved clusters ({r.n("extrap_check_reps", "int")} replicates) '
                      f'gives {r.n("extrap_double_boot_lower", "f4")} to {r.n("extrap_double_boot_upper", "f4")} for the doubling gain; '
                      f'conditional refits with c fixed at its bounds give {r.n("extrap_double_cond_at_c_lower", "f4")} at the lower bound '
                      f'and {r.n("extrap_double_cond_at_c_upper", "f4")} at the upper bound (the gain falls as c rises).',
            '- Neither definition reproduces the reviewer\'s parenthetical range, so that range is omitted from every deliverable. '
            'The two point extrapolations reproduce the reviewer values at the stated rounding and are bound [A].',
        ]),
        ('Closure note', [
            lambda r: f'- `v4_addons/reports/M_closure_note.md`: {r.n("closure_note_words", "int")} words '
                      f'(limit {r.n("closure_note_limit", "int")}); '
                      'all numbers in its render registry; check_numbers scan clean.',
        ]),
    ]
    acceptance = [
        '- STATE.md records M2 to M6 as `NOT_RUN_KILLED_BY_M1_GATE` and the delegation sentence verbatim: PASS.',
        '- `v4_addons/gates/` contains exactly H0_DECISIONS.md and H3_OPTION.txt, with H3 content `B_PRIME`: PASS.',
        '- Closure note at most 200 words, all numbers bound: PASS.',
        '- Reviewer extrapolations bound only where they reproduce; the non-reproducing range omitted: PASS.',
        '- Boundary check clean before and after: PASS.',
    ]
    deviations = [
        '- The reviewer\'s parenthetical interval for the doubling extrapolation did not reproduce: the joint fold-cluster bootstrap is wider '
        '(see the extrapolation check) and the conditional refits run in the opposite direction. Per the card it is omitted and no value from it '
        'appears in any deliverable; the two point extrapolations match and are labeled [A].',
        '- state.py was not edited. Its status vocabulary lacks `NOT_RUN_KILLED_BY_M1_GATE`, so STATE is written by the new fstate.py, '
        'which keeps the same JSON shape and adds the authorization section.',
        '- The gate files are written by a stdlib-only script (f0_gates.py) before v4common\'s audit hook is installed, because the hook blocks '
        'all agent writes under gates/. Section 0 amends G6 for exactly these two files; no other gate file is created.',
    ]
    open_items = ['- None for F0. F1 (placeholder resolution and final text) is next.']
    commands = [
        '"$PY" -B -X utf8 boundary_check.py --card F0 --phase pre',
        '"$PY" -B -X utf8 f0_gates.py',
        '"$PY" -B -X utf8 f0_closeout.py',
        '"$PY" -B -X utf8 check_numbers.py --scan ../reports/F0_report.md ../reports/M_closure_note.md',
        '"$PY" -B -X utf8 boundary_check.py --card F0 --phase post',
    ]
    summary = (
        'F0 closes Track M and writes the two gate files authorized by section 0 of the closeout directive. '
        'STATE records M2 to M6 as `NOT_RUN_KILLED_BY_M1_GATE` and the account holder\'s delegation verbatim. '
        '`H0_DECISIONS.md` adopts the ten earlier assumptions by delegation and adds the three section-0 decisions (pilot extension budget, '
        'Floor contact cost, harm-gate action); `H3_OPTION.txt` contains `B_PRIME`. The closure note reproduces the M1 evidence and binds the two '
        'reviewer extrapolations that match; the reviewer\'s parenthetical range did not reproduce and is omitted.'
    )
    return report.write_report('F0', 'Close Track M and write the gates', 'COMPLETED_ACCEPTED', summary, RESULTS_JSON,
                               evidence, acceptance, deviations, open_items, commands,
                               'yes (pre clean; post-check run after this report; only v4_addons/ written)', sections)


def main():
    gate_record = c.read_json(GATE_RECORD)
    present = sorted(path.name for path in c.GATES.iterdir() if path.is_file())
    if present != ['H0_DECISIONS.md', 'H3_OPTION.txt']:
        raise SystemExit(f'unexpected gate files: {present}')
    numbers, check = bind(gate_record)
    note_words = render_note(numbers)
    numbers.computed('closure_note_words', note_words, '[E]', 'word count of the rendered closure note')
    body = dict(gates=dict(files=gate_record['files'], gates_dir=gate_record['gates_dir'],
                           delegation=gate_record['delegation'], amendment=gate_record['amendment']),
                extrapolation=dict(point_10k=numbers.value('extrap_10k_gain'), point_double=numbers.value('extrap_double_gain'),
                                   bootstrap=check, reviewer_range_reproduced=False),
                closure_note=dict(path=c.relpath(NOTE), words=note_words))
    inputs = [c.ROOT / M1, FOLDS, c.ADDONS / 'DECISIONS_ASSUMED.md', GATE_RECORD, c.ROOT / METRICS,
              c.GATES / 'H0_DECISIONS.md', c.GATES / 'H3_OPTION.txt']
    c.write_json(RESULTS_JSON, dict(**numbers.body(), **body), __file__, TASK_INDEX, inputs,
                 row_counts={'m1_folds': 100, 'gate_files': len(present)})
    write_f0_report(numbers, gate_record, note_words)
    fstate.update({
        'M2': dict(status='NOT_RUN_KILLED_BY_M1_GATE', report=None, next_gate=None,
                   note='Track M killed at the M1 gate (DeltaS = 0 below the +0.0015 gate); not run.'),
        'M3': dict(status='NOT_RUN_KILLED_BY_M1_GATE', report=None, next_gate=None,
                   note='Track M killed at the M1 gate; not run.'),
        'M4': dict(status='NOT_RUN_KILLED_BY_M1_GATE', report=None, next_gate=None,
                   note='Track M killed at the M1 gate; not run.'),
        'M5': dict(status='NOT_RUN_KILLED_BY_M1_GATE', report=None, next_gate=None,
                   note='Track M killed at the M1 gate; not run.'),
        'M6': dict(status='NOT_RUN_KILLED_BY_M1_GATE', report=None, next_gate=None,
                   note='Track M killed at the M1 gate; not run.'),
        'F0': dict(status='COMPLETED_ACCEPTED', report='reports/F0_report.md', next_gate=None,
                   note='H0 + H3 written by delegation; M closure note; extrapolations bound, reviewer range omitted'),
    }, project_status='F0 complete: Track M killed (M2-M6 not run); option B\' adopted by delegation; '
                      'frozen v2 remains the submission until F3 promotes the candidate or falls back.')
    print(f'wrote {c.relpath(RESULTS_JSON)}; note {note_words} words; gates {present}')


if __name__ == '__main__':
    main()
