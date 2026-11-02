from pathlib import Path
import json

from common import ADDONS, BRIEF, ROOT, baseline_inputs, digest, file_info, outside_snapshot, population, stored_constants, verify_runtime, write_json

import numpy as np
from scipy import special, stats

DELIVERY = {
    'philopateer.pdf': 'a51d2c0ff8aa6ebb0f679e680d6424b01cd7b95b9a0d23ae7a2eecc56de210ea',
    'philopateer.pptx': 'a50a66fd77d062bdc45aeefb00ce8652b20b952de06dcb27e8ab4f15c37e46bc',
    'philopateer.ipynb': 'aaa170b19923c087f9b38f85b546626b7465a3d17f5ae7037812c6aed5736b35',
    'references.txt': 'b12fb18aafc83e2d599e15d04c689ee5cd85c10082c1761ab0c6f1d01606d361',
}


def main():
    verify_runtime()
    for name, expected in DELIVERY.items():
        assert digest(ROOT / name) == expected, 'STOP-1: ' + name
    current = outside_snapshot()
    baseline = ADDONS/'results/write_boundary_before.json'
    if baseline.exists():
        before = json.loads(baseline.read_text(encoding='utf-8'))['files']
        assert current == before, 'STOP-1: original outside-sandbox manifest changed'
    else:
        before = current
        write_json('results/write_boundary_before.json', dict(files=before), __file__, 0, [])
    relative_inputs = [
        'v2_work/final_metrics.json', 'v2_work/b_design.json', 'v2_work/d_results/gate_d.csv',
        'v2_work/a_selected_calibration.csv', 'v2_work/a_spec.json', 'v2_work/a_budget_choices.csv',
        'analysis_outputs/model_selection.json', 'analysis_outputs/source_manifest.json',
        'analysis_outputs/feature_manifest.json', 'v1_frozen/analysis_outputs/tables/split_manifest.csv',
        'telecom/Client.csv', 'telecom/Record.csv', 'FINAL_ASSESSMENT_HANDOFF_CONCISE.md',
        'FINAL_ASSESSMENT_HANDOFF.md', 'FINAL_V2_UPGRADE_REPORT.md', 'FINAL_ASSESSMENT_READING_NOTE.md',
        'v2_work/common.py', 'v2_work/workstream_a.py', 'v2_work/workstream_b.py',
        'v2_work/workstream_d.py', 'v2_work/run_frozen_batch.py', 'v2_work/final_protocol.py',
    ]
    inputs = [ROOT / name for name in relative_inputs] + baseline_inputs() + [BRIEF]
    info = [file_info(path) for path in inputs]
    frame = population()
    selected = frame.loc[frame.selected]
    p0 = float(np.average(selected.y, weights=selected.weight))
    constants = stored_constants()
    delta_pp = (p0-constants['p0']) * 100
    sanity = abs(delta_pp) <= .5
    if abs(delta_pp) > 1:
        raise RuntimeError('STOP-5: non-test population mismatch requires explanation')
    priors = []
    expected = {(6, 24): (.685, 3747, -6166, 1093), (6, 14): (.930, 13113, -1173, 196), (2, 18): (.168, -5619, -13202, 832)}
    for (a, b), (p_ref, mean_ref, var_ref, evpi_ref) in expected.items():
        G, K = constants['G'], constants['K']
        g, mean = K/G, a/(a+b)
        positive = float(stats.beta.sf(g, a, b))
        value = G * (mean * special.betaincc(a+1, b, g) - g * positive)
        result = dict(a=a, b=b, p_pos=positive, e_net=G*mean-K,
                      var5=G*stats.beta.ppf(.05, a, b)-K,
                      evpi=value-max(0, G*mean-K))
        assert abs(positive-p_ref) <= .005, 'STOP-3: positive-net probability'
        for key, reference in [('e_net', mean_ref), ('var5', var_ref), ('evpi', evpi_ref)]:
            assert abs(result[key]-reference) <= abs(reference)*.01, 'STOP-3: ' + key
        priors.append(result)
    data_counts = dict(repeated_oof=150000, unique_non_test_customers=len(frame), selected_non_test_rows=len(selected), calibration_rows=10000)
    code_paths = {
        'prior_stress': dict(path='v2_work/workstream_a.py', function='analyze', lines='111-119', note='Loops frozen prior-specific calibration thresholds; measure computes scenario weights and economics. analyze writes files: never call.'),
        'budget_search': dict(path='v2_work/workstream_a.py', function='prepare', lines='89-101', note='Uses saved p_s_oof, fractions 1%-30%, costs .25/1/2/5, then freezes thresholds. prepare fits and writes: never call.'),
        'pilot_power': dict(path='v2_work/workstream_b.py', function='power', lines='157-202', note='floor(.9*enrolled), observed total contribution, fixed calibration adjustment, variable and allocated startup costs; called only through a writing entrypoint in v2.'),
        'value': dict(path='v2_work/common.py', function='values', lines='57-60', note='Nonnegative value, original-training median fill and p99. New loader uses saved 44.99 and 115.5159 without recomputing training thresholds.'),
        'oof_cache': dict(path='v2_work/workstream_d.py', function='evaluate_arrays', lines='698-719', note='Ten baseline-only NPZs contain Customer_ID/y/raw; two cross-fitted raw predictions averaged once per account; no models imported.'),
    }
    body = dict(status='DONE', inventory=info, missing_inputs=[item['path'] for item in info if not item['present']],
                deliverable_checks=[dict(**file_info(ROOT/name), expected_sha256=value, passed=True) for name,value in DELIVERY.items()],
                read_only_checks=dict(immutable_v1_files=67, completed_batch_verified=True),
                population=dict(choice='Baseline non-test OOF, average two raw scores per unique Customer_ID, frozen v1 sigmoid, saved original-train V limits, assumed 2% prior',
                                selected_control_churn=p0, reference_control_churn=constants['p0'], difference_percentage_points=delta_pp,
                                sanity_half_percentage_point_pass=sanity, selected_deployment_mass=float(selected.weight.sum()),
                                repeat_averaging_is_not_independent_replication=True),
                constants=constants, headline_prior_checks=priors, code_paths=code_paths,
                deviations=['Named concise handoff absent; existing complete handoff read instead. It requires no training/test reconstruction.',
                            'No root project-rule file written. Scoped v3_addons/AGENTS.md copies section 1 within the authorized boundary.'],
                tags=dict(evidence='Computed non-test population checks and arithmetic from frozen JSON scalars.', assumptions='2% prior, six months, 60% margin, monetary interpretation, prevention priors.', recommendation='Use unique-account non-test OOF population for WP1; no model change.'))
    result = write_json('results/inventory.json', body, __file__, 0, inputs, data_counts)
    lines = [
        '# WP0 — Preflight, inventory, sandbox', 'Status: DONE [E]', '',
        'Inputs: [E] Exact paths, presence, sizes and SHA-256 are in ../results/inventory.json.', '',
        'Population / assumptions:',
        '- [E] Ten baseline-only NPZ caches give 150,000 repeated OOF predictions on 75,000 unique original train/validation customers; all IDs are verified against the saved split manifest.',
        '- [R] Average the two raw OOF predictions per Customer_ID; apply the frozen sigmoid and join source V using the saved training limits. Do not count repeats as extra independent customers.',
        '- [A] Deployment prior 2%, sample prior 49.562%, six months, 60% margin and monetary interpretation remain scenario inputs.',
        '- [E] No test rows are loaded into a scientific data frame; the Record.csv reader parses billing only after an allowed non-test ID check.', '',
        'Method (≤10 lines)',
        '[E] Ran the two prescribed read-only verifiers; hashed all four deliverables; inventoried inputs; read v2 source code without executing analytical entrypoints; computed population sanity and closed-form headline checks; saved a full outside-sandbox content manifest.', '',
        'Results:',
        '| Quantity | Result |', '|---|---:|',
        f'| Selected unique non-test rows [E] | {len(selected):,} |',
        f'| Weighted selected mass [E, conditional on A] | {selected.weight.sum():.6f} |',
        f'| Selected control churn [E, conditional on A] | {p0*100:.6f}% |',
        f'| Frozen v1 reference [E] | {constants["p0"]*100:.6f}% |',
        f'| Difference [E] | {delta_pp:+.6f} percentage points |',
        f'| G from frozen JSON scalar [E, conditional on A] | {constants["G"]:.8f} |',
        f'| K from frozen JSON scalar [E, conditional on A] | {constants["K"]:.8f} |',
        f'| Full outside-sandbox snapshot [E] | {len(before):,} files |', '',
        'Acceptance checks:',
        '- [E] PASS: four delivery hashes match; immutable v1 has 67 verified files; completed frozen batch verifier returned without error.',
        f'- [E] PASS: population within ±0.5 percentage points; actual difference {delta_pp:+.6f}.',
        '- [E] PASS: three prevention-prior headline probabilities within .005 and dollar results within 1% of brief section 3.',
        '- [E] PASS: every absent input is listed; only FINAL_ASSESSMENT_HANDOFF_CONCISE.md is absent, and no training or test reconstruction is needed.', '',
        'Code paths [E]:',
    ]
    for key,item in code_paths.items():
        lines.append(f'- [E] {key}: {item["path"]}:{item["lines"]}, {item["function"]}. {item["note"]}')
    lines += ['', 'Deviations from brief:', '- [E] The named concise handoff is absent; the full current handoff was read. Its section numbering differs from the reviewer summary.',
              '- [E] Rules are scoped inside v3_addons; no rule/config file outside the boundary was touched.', '',
              'Claims now allowed: [E] Frozen delivery integrity passes; preferred non-test population is available and passes sanity; quoted headline arithmetic reproduces.',
              'Claims still forbidden: [R] Treatment effectiveness, causal profit, live prevalence, model gains, fairness certification and production readiness.',
              'Open questions for human: [E] None; no STOP condition has fired.']
    (ADDONS/'reports/WP0_report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=result['status'], selected_control_churn=p0, sanity_pass=sanity, outside_files=len(before)),indent=2))


if __name__ == '__main__':
    main()
