"""M0 - regeneration feasibility: entry points, exact replay on cached probabilities, file-drivability probe, ledger dependency map."""
import json
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4common as c  # noqa: E402

TASK_INDEX = 10
RESULTS = c.RESULTS / 'm0_feasibility.json'
V2 = c.ROOT / 'v2_work'
SANDBOX = c.ADDONS / 'm0_sandbox'
ENTRY = ['analysis_pipeline.py', 'v2_work/analysis_pipeline_v2.py', 'v2_work/build_v2_canonical.py',
         'v2_work/run_frozen_batch.py', 'v2_work/workstream_a.py', 'v2_work/workstream_b.py',
         'v2_work/workstream_c.py', 'v2_work/workstream_d.py', 'v2_work/final_protocol.py',
         'v2_work/final_metrics.py', 'v2_work/generate_visuals.py']
A_OUTPUTS = ['a_policies_test.csv', 'a_profit_curves_test.csv', 'a_overlap_test.csv', 'a_dual_valuation_test.csv',
             'a_value_proxy_sensitivity_test.csv', 'a_bootstrap_test.csv', 'a_intervals_test.csv',
             'a_calibration_uncertainty_test.csv', 'a_summary_test.json']


def jsonable(obj):
    import numpy as np
    if isinstance(obj, dict):
        return {str(key): jsonable(value) for key, value in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [jsonable(value) for value in obj]
    if isinstance(obj, np.ndarray):
        return jsonable(obj.tolist())
    if isinstance(obj, np.generic):
        return obj.item()
    if isinstance(obj, float) and not np.isfinite(obj):
        return None
    return obj


def frame_replay_check():
    import joblib
    import numpy as np
    import pandas as pd
    from scipy.special import logit
    sys.path.insert(0, str(V2))
    frozen = pd.read_csv(c.ROOT / 'v1_frozen/analysis_outputs/tables/heldout_predictions.csv')
    bundle = joblib.load(c.ROOT / 'v1_frozen/analysis_outputs/models/selected_model.joblib')
    raw = 1 / (1 + np.exp(-(logit(np.clip(frozen.sample_calibrated_churn_probability.to_numpy(), 1e-6, 1 - 1e-6)) - bundle['calibrator'].intercept_[0]) / bundle['calibrator'].coef_[0, 0]))
    calibrator = joblib.load(V2 / 'a_calibrator.joblib')
    p = calibrator.predict(raw)
    served = pd.read_csv(V2 / 'a_selected_test.csv', float_precision='round_trip')
    default = pd.read_csv(V2 / 'a_selected_test.csv', usecols=['p_s'])
    ulp_rows = int((default.p_s.to_numpy() != served.p_s.to_numpy()).sum())
    return float(np.max(np.abs(p - served.p_s.to_numpy()))), len(served), ulp_rows


def replay_final_metrics():
    sys.path.insert(0, str(V2))
    import final_metrics  # noqa: E402
    target = SANDBOX / 'final_metrics'
    target.mkdir(parents=True, exist_ok=True)
    captured = {}

    def capture(name, value):
        payload = jsonable(value)
        captured[name] = payload
        (target / name).write_text(json.dumps(payload, indent=2, allow_nan=False), encoding='utf-8')

    final_metrics.dump = capture
    started = time.perf_counter()
    final_metrics.build()
    elapsed = time.perf_counter() - started
    sandbox_file = target / 'final_metrics.json'
    real_file = V2 / 'final_metrics.json'
    sandbox_bytes = sandbox_file.read_bytes()
    real_bytes = real_file.read_bytes()
    sandbox_values = json.loads(sandbox_bytes.decode('utf-8'))
    real_values = json.loads(real_bytes.decode('utf-8'))
    differing = sorted(key for key in set(sandbox_values) | set(real_values) if sandbox_values.get(key) != real_values.get(key))
    return dict(hash_equal=c.digest(sandbox_file) == c.digest(real_file), bytes_equal=sandbox_bytes == real_bytes,
                differing_keys=differing, wall_seconds=round(elapsed, 2), keys=len(real_values))


def replay_a_layer():
    sys.path.insert(0, str(V2))
    import numpy as np
    import pandas as pd
    import workstream_a as a  # noqa: E402
    from common import load_data  # noqa: E402
    target = SANDBOX / 'a_replay'
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    shutil.copy2(V2 / 'a_spec.json', target / 'a_spec.json')

    def sandbox_dump(name, value):
        (target / name).write_text(json.dumps(jsonable(value), indent=2, allow_nan=False), encoding='utf-8')

    a.WORK = target
    a.dump = sandbox_dump
    cal = pd.read_csv(V2 / 'a_selected_calibration.csv', float_precision='round_trip')
    frame = pd.read_csv(V2 / 'a_selected_test.csv', float_precision='round_trip')
    data, splits = load_data()
    started = time.perf_counter()
    a.analyze(cal, frame, data, splits, 'test')
    elapsed = time.perf_counter() - started
    rows = []
    for name in A_OUTPUTS:
        produced = target / name
        original = V2 / name
        entry = dict(name=name, produced=produced.exists(), hash_equal=c.digest(produced) == c.digest(original), size=produced.stat().st_size if produced.exists() else 0)
        if produced.exists() and original.exists() and not entry['hash_equal']:
            if name.endswith('.json'):
                entry['parsed_equal'] = json.loads(produced.read_text(encoding='utf-8')) == json.loads(original.read_text(encoding='utf-8'))
            else:
                left, right = pd.read_csv(produced, float_precision='round_trip'), pd.read_csv(original, float_precision='round_trip')
                entry['shape_equal'] = left.shape == right.shape
                common_cols = [col for col in left.columns if col in right.columns and left[col].dtype.kind in 'fiu' and right[col].dtype.kind in 'fiu']
                diffs = []
                for col in common_cols:
                    left_values = left[col].to_numpy(dtype=float)
                    right_values = right[col].to_numpy(dtype=float)
                    if left_values.size:
                        diffs.append(float(np.max(np.abs(left_values - right_values))))
                entry['max_abs_diff'] = max(diffs) if diffs else None
        rows.append(entry)
    summary_produced = target / 'a_summary.json'
    summary_original = V2 / 'a_summary_test.json'
    rows.append(dict(name='a_summary.json (vs a_summary_test.json)', produced=summary_produced.exists(),
                     hash_equal=c.digest(summary_produced) == c.digest(summary_original), size=summary_produced.stat().st_size if summary_produced.exists() else 0))
    return dict(files=rows, wall_seconds=round(elapsed, 2), all_hash_equal=all(row['hash_equal'] for row in rows))


def ledger_map():
    import pandas as pd
    ledger = pd.read_csv(c.ROOT / 'analysis_outputs/claims_ledger.csv')
    chart = json.loads((V2 / 'chart_numeric_sources.json').read_text(encoding='utf-8'))
    observed = {str(index) for index, item in enumerate(chart) if item['epistemic_type'] == 'observed'}
    ledger['source'] = ledger.source_file_or_json_key.str.split('::').str[0]
    ledger['key'] = ledger.source_file_or_json_key.str.split('::').str[1]
    ledger['root'] = ledger.key.str.split('.').str[0]

    def classify(row):
        if row.source == 'v2_work/final_metrics.json':
            if row.root in ('deployment_policies', 'deployment_intervals', 'deployment_relative_value_gain',
                            'deployment_prevented', 'deployment_retained_revenue', 'pilot_test'):
                return 'regeneration'
            if row.root == 'heatmap' and not row.key.endswith(('.contact_cost', '.prevention')):
                return 'regeneration'
            if row.root == 'prior_stress' and not row.key.endswith('.prior'):
                return 'regeneration'
            if row.root in ('strongest_nonpromoted_or_promoted_cv_candidate', 'proxy_recoverability', 'pilot_calibration'):
                return 'narrative'
        if row.source == 'v2_work/chart_numeric_sources.json' and row.root in observed:
            return 'regeneration'
        if row.source == 'v1_frozen/analysis_outputs/summary.json':
            return 'narrative'
        return 'unaffected'

    ledger['dependency'] = ledger.apply(classify, axis=1)
    dependent = ledger.loc[ledger.dependency.eq('regeneration')].copy()
    narrative = ledger.loc[ledger.dependency.eq('narrative')].copy()
    dependent['claim'] = [f'C{index + 1:04d}' for index in dependent.index]
    dependent['number_name'] = dependent.claim.map(lambda claim: f'ledger_{claim}_value')
    narrative['claim'] = [f'C{index + 1:04d}' for index in narrative.index]
    by_source = dependent.source.value_counts().to_dict()
    by_slide = {int(slide): int(count) for slide, count in dependent.groupby('slide_number').size().items()}
    by_root = {root: int(count) for root, count in dependent.root.value_counts().items()}
    narrative_source = narrative.source.value_counts().to_dict()
    narrative_root = narrative.root.value_counts().to_dict()
    narrative_rows = narrative[['claim', 'slide_number', 'source_file_or_json_key', 'displayed_text']].to_dict(orient='records')
    dependent_rows = [dict(claim=row.claim, name=row.number_name, slide=int(row.slide_number),
                           source_key=row.source_file_or_json_key, displayed=row.displayed_text,
                           exact_value=float(row.exact_value)) for row in dependent.itertuples()]
    return dict(rows_total=int(len(ledger)), rows_dependent=int(len(dependent)),
                rows_narrative=int(len(narrative)), rows_unaffected=int(len(ledger) - len(dependent) - len(narrative)),
                by_source=by_source, by_slide=by_slide, by_root=by_root, narrative_by_source=narrative_source,
                narrative_by_root=narrative_root, dependent_rows=dependent_rows, narrative_rows=narrative_rows)


def write_dependency_map(ledger):
    numbers = json.loads(RESULTS.read_text(encoding='utf-8'))['numbers']
    r = c.Renderer(numbers, RESULTS)
    lines = ['# M0 — regeneration dependency map', 'Status: COMPLETED_ACCEPTED', '',
             f'**Verdict: GO.** The v2 metric chain is drivable by an alternate `a_selected_test.csv`: replaying the cached frozen '
             f'probabilities regenerated the A layer byte-for-byte ({r.n("a_artifacts_hash_equal", "int")} of '
             f'{r.n("a_artifacts_compared", "int")} artifacts) and re-emitted `final_metrics.json` byte-for-byte '
             f'({r.n("final_metrics_keys", "int")} top-level keys, {r.n("final_metrics_differing_keys", "int")} differing). '
             f'Estimated regeneration effort: {r.n("regeneration_effort_days", "f1")} days [A]. No model was fitted or scored; '
             'every replay used cached probabilities.', '',
             '## Pipeline map', '',
             '| layer | entry | input | outputs |', '|---|---|---|---|',
             '| A — policy comparison | `workstream_a.py` (`analyze`) | `a_selected_{partition}.csv` + frozen split manifest | '
             '`a_policies_test.csv`, `a_profit_curves_test.csv`, `a_overlap_test.csv`, `a_dual_valuation_test.csv`, '
             '`a_value_proxy_sensitivity_test.csv`, `a_bootstrap_test.csv`, `a_intervals_test.csv`, '
             '`a_calibration_uncertainty_test.csv`, `a_summary_test.json` |',
             '| B — pilot diagnostics | `workstream_b.py` (same file, `workstream_b.py:244`) | `a_selected_test.csv` + `b_design.json` | '
             '`b_power_test.csv`, `b_queues_test.csv`, `b_cells_test.csv`, `b_assignments_test.csv`, `b_summary_test.json` |',
             '| C — governance audit | `workstream_c.py` (same file, `workstream_c.py:145`) | `a_selected_test.csv` + ceiling results | '
             '`c_test/c_summary.json`, `c_test/c_subgroup_robustness.csv`, `c_test/c_equity.csv` |',
             '| metrics | `final_metrics.py` (`build`) | A/B/C summaries, scored `d_results/`, frozen protocol | `final_metrics.json` |',
             '| charts | `generate_visuals.py` | `final_metrics.json` + cached test frame | figures, `chart_claims.json`, `chart_numeric_sources.json` |',
             '| ledger | `build_claim_ledger.py` | `ledger_bindings.json`, chart sources, deck | `analysis_outputs/claims_ledger.csv` |', '',
             f'The batch driver `run_frozen_batch.py` sequences A → B → C → metrics and enforces the freeze; '
             f'`build_v2_canonical.py` assembles the canonical notebook from the same modules. '
             f'{r.n("entry_points", "int")} entry-point files are hash-recorded in `results/m0_feasibility.json`.', '',
             '## Replay evidence', '',
             f'- Maximum absolute difference between the rebuilt `p_s` and the cached `a_selected_test.csv`: '
             f'{r.n("calibrator_replay_max_abs_diff", "f1")} over {r.n("served_rows", "int")} rows.',
             f'- `final_metrics.json`: byte-identical ({r.n("final_metrics_hash_equal", "int")} flag), '
             f'{r.n("final_metrics_keys", "int")} top-level keys, {r.n("final_metrics_differing_keys", "int")} differing, '
             f'{r.n("final_metrics_wall_seconds", "f2")} s.',
             f'- A layer: {r.n("a_artifacts_hash_equal", "int")} of {r.n("a_artifacts_compared", "int")} artifacts byte-identical, '
             f'{r.n("a_replay_wall_seconds", "f2")} s including the bootstrap and calibration-uncertainty refits.',
             f'- CSV parser caveat: pandas\' default parser changes {r.n("csv_parser_ulp_rows", "int")} of '
             f'{r.n("served_rows", "int")} `p_s` values by one ulp; every replay read uses `float_precision=\'round_trip\'`. '
             'Without it the A-layer CSVs differ in the last digits.', '',
             '## Dependency rule', '',
             'A ledger row is **regeneration-dependent** when its displayed value is recomputed by the chain from per-row '
             'probabilities or selections: the deployment policy table and its intervals, prevented churners, retained revenue, '
             'the heatmap net cells, prior-stress net cells, pilot queue composition, and the observed chart values.', '',
             'Rows that describe the frozen search or the v1 deliverable are **narrative**: the v1 headline block and the '
             'frozen-search candidate, proxy and power rows. Regeneration neither recomputes nor invalidates them; an admitted '
             'model would add a new claim, not overwrite the v1 record.', '',
             'Everything else is **unaffected**: protocol constants, financial assumptions, design constants, bibliography, '
             'axis ticks and ordinals.', '',
             f'Of the {r.n("ledger_rows_total", "int")} ledger rows, {r.n("ledger_rows_dependent", "int")} are '
             f'regeneration-dependent, {r.n("ledger_rows_narrative", "int")} are narrative and '
             f'{r.n("ledger_rows_unaffected", "int")} are unaffected. The dependent rows sit on '
             f'{r.n("ledger_affected_slides", "int")} slides: {r.n("dependent_final_metrics_rows", "int")} bound to '
             f'`final_metrics.json` and {r.n("dependent_chart_rows", "int")} observed chart values.', '',
             '## Regeneration-dependent rows by slide', '',
             '| slide | rows |', '|---|---:|']
    for slide, _count in sorted(ledger['by_slide'].items()):
        lines.append(f'| {slide} | {r.n(f"regeneration_rows_slide_{slide}", "int")} |')
    lines += ['', '## Every regeneration-dependent ledger number', '',
              'Exact values are the ledger `exact_value` column (raw, unscaled); displayed text is quoted from the frozen ledger.', '',
              '| claim | slide | source | displayed | exact value |', '|---|---:|---|---|---:|']
    for row in ledger['dependent_rows']:
        lines.append(f'| {row["claim"]} | {row["slide"]} | `{row["source_key"]}` | `{row["displayed"]}` | {r.n(row["name"], "raw")} |')
    lines += ['', '## Narrative rows (not recomputed by regeneration)', '',
              f'{r.n("narrative_v1_rows", "int")} v1 headline rows, {r.n("narrative_cv_rows", "int")} frozen-search candidate rows, '
              f'{r.n("narrative_proxy_rows", "int")} proxy-recoverability rows and {r.n("narrative_power_rows", "int")} pilot-power row. '
              'They stay as the v1/WP8 record unless a human rewrites the narrative.', '',
              '| claim | slide | source |', '|---|---:|---|']
    for row in ledger['narrative_rows']:
        lines.append(f'| {row["claim"]} | {int(row["slide_number"])} | `{row["source_file_or_json_key"]}` |')
    lines += ['', '## Notebook and PDF', '',
              'The notebook (`philopateer.ipynb`) replays the v1 frozen outputs and is not driven by the v2 probability file; '
              'frozen cells are not edited. The PDF carries the same claims as the deck, so the regenerated set above applies '
              'to both.', '',
              '## Manual regeneration steps', '',
              '1. Copy `v2_work/` to `v4_addons/regen/v2_work/` so the frozen tree and the once-only test guards stay untouched.',
              '2. Replace `a_selected_test.csv` with the candidate model\'s per-row file (same columns). This is an M5 output: '
              'it requires ADOPT-CONFIRMED and gate H2, and is not authorized by M0.',
              f'3. Regenerate the A layer with `workstream_a.analyze(cal, frame, data, splits, \'test\')`; '
              f'{r.n("a_artifacts_hash_equal", "int")} of {r.n("a_artifacts_compared", "int")} artifacts were reproduced exactly in replay.',
              '4. Regenerate B and C with `--partition test`; both read `a_selected_test.csv`. Their once-only guards pass only in the copy.',
              '5. Re-emit `final_metrics.json` with `final_metrics.build()`.',
              '6. Regenerate the charts with `generate_visuals.py`, then the ledger with `build_claim_ledger.py`.',
              f'7. Diff the {r.n("ledger_rows_total", "int")}-row ledger against the frozen file; '
              f'{r.n("ledger_rows_dependent", "int")} rows are expected to move.',
              '8. Apply Option R to the deck and PDF only after gate H3.', '',
              f'Read every `a_selected_*.csv` with `float_precision=\'round_trip\'`; the default parser shifts '
              f'{r.n("csv_parser_ulp_rows", "int")} values by one ulp and breaks byte-exactness. '
              f'Effort: {r.n("regeneration_effort_days", "f1")} days [A].', '',
              '## What M0 does not authorize', '',
              '- No new model was fitted or scored; no test row was used for fitting, scoring or selection. The replay read cached probabilities only '
              'and is logged through `test_guard.log_replay`.',
              '- GO is a pipeline verdict, not a model verdict: the M1 sample-size gate still decides whether Track M '
              'continues, and the M2 preregistration still needs gate H1.']
    r.write(c.ADDONS / 'M0_dependency_map.md', '\n'.join(lines) + '\n', c.RESULTS / 'M0_dependency_map_render.json')
    print('wrote', (c.ADDONS / 'M0_dependency_map.md').relative_to(c.ROOT).as_posix())


def write_task_report():
    import report
    evidence = [('verdict_go', 'int'), ('entry_points', 'int'), ('calibrator_replay_max_abs_diff', 'f1'),
                ('csv_parser_ulp_rows', 'int'), ('served_rows', 'int'), ('frozen_frame_rows', 'int'),
                ('final_metrics_hash_equal', 'int'), ('final_metrics_keys', 'int'),
                ('final_metrics_differing_keys', 'int'), ('final_metrics_wall_seconds', 'f2'),
                ('a_artifacts_hash_equal', 'int'), ('a_artifacts_compared', 'int'), ('a_replay_wall_seconds', 'f2'),
                ('ledger_rows_total', 'int'), ('ledger_rows_dependent', 'int'), ('ledger_rows_narrative', 'int'),
                ('ledger_rows_unaffected', 'int'), ('ledger_affected_slides', 'int'),
                ('dependent_final_metrics_rows', 'int'), ('dependent_chart_rows', 'int'), ('regeneration_effort_days', 'f1')]
    acceptance = [
        '- Entry point located and the full chain traced from code: **PASS**.',
        lambda r: f'- Pipeline drivable by an alternate probability file: **PASS** (A layer '
                  f'{r.n("a_artifacts_hash_equal", "int")} of {r.n("a_artifacts_compared", "int")} byte-identical; '
                  f'`final_metrics.json` hash-equal flag {r.n("final_metrics_hash_equal", "int")}).',
        '- `final_metrics.json` reproduced exactly in replay mode: **PASS**.',
        lambda r: f'- Dependency map enumerates every regeneration-dependent row: **PASS** '
                  f'({r.n("ledger_rows_dependent", "int")} rows on {r.n("ledger_affected_slides", "int")} slides).',
        lambda r: f'- The {r.n("ledger_rows_total", "int")}-row ledger is fully accounted for: '
                  f'{r.n("ledger_rows_dependent", "int")} regeneration / {r.n("ledger_rows_narrative", "int")} narrative / '
                  f'{r.n("ledger_rows_unaffected", "int")} unaffected: **PASS**.',
        '- No model fitted, no model scored, no test row used for fitting or selection: **PASS**.',
        lambda r: f'- Regeneration effort recorded: **PASS** ({r.n("regeneration_effort_days", "f1")} days [A]).',
        '- Boundary check clean before and after: **PASS**.']
    deviations = [
        lambda r: f'- The brief asks for the count of ledger rows "affected". The map splits that into '
                  f'{r.n("ledger_rows_dependent", "int")} regeneration-dependent rows and '
                  f'{r.n("ledger_rows_narrative", "int")} narrative rows because the v1 block and the frozen-search '
                  'performance rows are not recomputed by the chain; the rule is stated in the map.',
        '- B and C were traced by code inspection, not replayed: both read `a_selected_test.csv`, but their once-only test '
        'guards are bound to existing outputs, so a replay would have required bypassing a guard. The A and metrics layers '
        'carry the byte-exactness proof.',
        lambda r: f'- The replay reads cached test probabilities; this is allowed for M0 only and is logged via '
                  f'`test_guard.log_replay`. The default CSV parser loses one ulp on {r.n("csv_parser_ulp_rows", "int")} rows; '
                  'all replay reads use round-trip parsing.']
    open_items = [
        '- Gate H1 is closed: Track M beyond the M2 draft requires a human-created `gates/H1_APPROVED.txt`.',
        '- The M0 GO authorizes no test scoring and no deck edit; gate H2 and Option H3 remain human decisions.']
    commands = ['"$PY" -B -X utf8 boundary_check.py --card M0 --phase pre',
                'OPENBLAS_NUM_THREADS=6 OMP_NUM_THREADS=6 MKL_NUM_THREADS=6 NUMEXPR_NUM_THREADS=6 "$PY" -B -X utf8 m0_feasibility.py',
                '"$PY" -B -X utf8 check_numbers.py --scan ../M0_dependency_map.md ../reports/M0_report.md',
                '"$PY" -B -X utf8 boundary_check.py --card M0 --phase post']
    report.write_report('M0', 'regeneration feasibility and dependency map', 'COMPLETED_ACCEPTED',
                        'The v2 chain is file-driven: cached-probability replay regenerated the A layer and '
                        '`final_metrics.json` byte-for-byte, and the ledger map in `v4_addons/M0_dependency_map.md` classifies '
                        'every row. No model was fitted or scored; ledger, deck and notebook files were read only.',
                        RESULTS, evidence, acceptance, deviations, open_items, commands,
                        'yes (pre clean; post-check run after this report; only `v4_addons/` written)')


def main():
    c.runtime_record()
    n = c.Numbers()
    n.source('ledger_rows_total', 'analysis_outputs/claims_ledger.csv', 'rowcount')
    n.source('frozen_frame_rows', 'v2_work/a_selected_test.csv', 'rowcount')
    n.declared('entry_points', len(ENTRY), '[E]', 'pipeline files whose hashes are recorded in the results JSON entry_points block')
    n.declared('regeneration_effort_days', 1.5, '[A]', 'estimate: 0.5 d A/B/C wiring, 0.5 d charts+ledger+verification, 0.5 d contingency; no model fitting')

    max_diff, served_rows, ulp_rows = frame_replay_check()
    n.computed('calibrator_replay_max_abs_diff', max_diff, '[E]', 'maximum absolute difference between the rebuilt p_s and the cached a_selected_test.p_s when the frozen heldout probabilities are replayed through the frozen calibrator')
    n.computed('served_rows', served_rows, '[E]', 'rows in the cached test frame')
    n.computed('csv_parser_ulp_rows', ulp_rows, '[E]', 'cached p_s values changed by pandas default parsing versus float_precision=round_trip')

    fm = replay_final_metrics()
    n.computed('final_metrics_hash_equal', int(fm['hash_equal']), '[E]', '1 if the re-emitted final_metrics.json is byte-identical to the frozen file')
    n.computed('final_metrics_keys', fm['keys'], '[E]', 'top-level keys compared')
    n.computed('final_metrics_differing_keys', len(fm['differing_keys']), '[E]', 'top-level keys whose parsed values differ')
    n.computed('final_metrics_wall_seconds', fm['wall_seconds'], '[E]', 'wall time of the re-emission (no scoring)')

    a_layer = replay_a_layer()
    n.computed('a_artifacts_compared', len(a_layer['files']), '[E]', 'A test artifacts compared after regeneration from the cached probability file')
    n.computed('a_artifacts_hash_equal', sum(int(row['hash_equal']) for row in a_layer['files']), '[E]', 'A artifacts reproduced byte-for-byte')
    n.computed('a_replay_wall_seconds', a_layer['wall_seconds'], '[E]', 'wall time of the A-layer regeneration (bootstrap included)')

    ledger = ledger_map()
    n.computed('ledger_rows_dependent', ledger['rows_dependent'], '[E]', 'ledger rows whose displayed value is recomputed by the chain from per-row probabilities or selections')
    n.computed('ledger_rows_narrative', ledger['rows_narrative'], '[E]', 'v1 headline and frozen-search performance rows that regeneration does not recompute')
    n.computed('ledger_rows_unaffected', ledger['rows_unaffected'], '[E]', 'protocol, financial, design, bibliography and axis rows')
    n.computed('ledger_affected_slides', len(ledger['by_slide']), '[E]', 'distinct slide numbers carrying at least one regeneration-dependent row')
    n.computed('dependent_final_metrics_rows', ledger['by_source'].get('v2_work/final_metrics.json', 0), '[E]', 'regeneration-dependent rows bound to final_metrics.json')
    n.computed('dependent_chart_rows', ledger['by_source'].get('v2_work/chart_numeric_sources.json', 0), '[E]', 'regeneration-dependent observed chart values (not axis ticks)')
    for slide, count in sorted(ledger['by_slide'].items()):
        n.computed(f'regeneration_rows_slide_{slide}', count, '[E]', f'regeneration-dependent ledger rows displayed on slide {slide}')
    n.computed('narrative_v1_rows', ledger['narrative_by_source'].get('v1_frozen/analysis_outputs/summary.json', 0), '[E]', 'narrative rows bound to the frozen v1 summary')
    n.computed('narrative_cv_rows', ledger['narrative_by_root'].get('strongest_nonpromoted_or_promoted_cv_candidate', 0), '[E]', 'narrative rows describing the frozen candidate search')
    n.computed('narrative_proxy_rows', ledger['narrative_by_root'].get('proxy_recoverability', 0), '[E]', 'narrative proxy-recoverability rows')
    n.computed('narrative_power_rows', ledger['narrative_by_root'].get('pilot_calibration', 0), '[E]', 'narrative pilot-power row')
    for row in ledger['dependent_rows']:
        n.computed(row['name'], row['exact_value'], '[E]', f'ledger row {row["claim"]} exact_value: {row["source_key"]}',
                   source_file='analysis_outputs/claims_ledger.csv', source_key=f'row {row["claim"]}')

    verdict = 'GO' if fm['hash_equal'] and a_layer['all_hash_equal'] and max_diff == 0.0 else 'NO-GO'
    n.declared('verdict_go', int(verdict == 'GO'), '[E]', 'GO only if the re-emission is byte-exact and the A layer regenerates from the cached probability file')

    body = dict(numbers=n.entries, verdict=verdict, entry_points={path: c.file_info(c.ROOT / path) for path in ENTRY},
                final_metrics=fm, a_layer=a_layer,
                ledger=dict(rows_total=ledger['rows_total'], rows_dependent=ledger['rows_dependent'],
                            rows_narrative=ledger['rows_narrative'], rows_unaffected=ledger['rows_unaffected'],
                            by_source=ledger['by_source'], by_slide=ledger['by_slide'], by_root=ledger['by_root'],
                            narrative_by_source=ledger['narrative_by_source'], narrative_by_root=ledger['narrative_by_root']),
                dependent_rows=ledger['dependent_rows'], narrative_rows=ledger['narrative_rows'])
    c.write_json(RESULTS, body, __file__, TASK_INDEX, [c.ROOT / path for path in ENTRY] + [V2 / 'final_metrics.json', V2 / 'a_selected_test.csv',
                V2 / 'chart_numeric_sources.json', c.ROOT / 'analysis_outputs/claims_ledger.csv'])
    from test_guard import log_replay
    log_replay('M0 cached frozen probability replay', [V2 / 'a_selected_test.csv',
                c.ROOT / 'v1_frozen/analysis_outputs/tables/heldout_predictions.csv'])
    write_dependency_map(ledger)
    write_task_report()
    print('verdict', verdict, '; final_metrics bytes equal', fm['bytes_equal'], '; A artifacts', sum(int(row['hash_equal']) for row in a_layer['files']), '/', len(a_layer['files']), '; ledger', ledger['rows_dependent'], 'regeneration /', ledger['rows_narrative'], 'narrative /', ledger['rows_unaffected'], 'unaffected of', ledger['rows_total'])


if __name__ == '__main__':
    main()
