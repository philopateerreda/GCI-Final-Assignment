import argparse
import json
from hashlib import sha256
from pathlib import Path
import runpy

import numpy as np
import pandas as pd

from common import ROOT, WORK
import final_metrics
from run_frozen_batch import verify_completed


def build():
    protocol = verify_completed()
    final_metrics.build()
    final = json.loads((WORK / 'final_metrics.json').read_text(encoding='utf-8'))
    frame = pd.read_csv(WORK / 'a_selected_test.csv')
    pilot = final['pilot_test']
    assert len(frame) == 15000
    assert np.isclose(frame.weight.sum(), 100000)
    assert sum(row['raw_count'] for row in pilot['queues']) == int(frame.selected_bayes.sum())
    assert pilot['disjoint_cells_and_exclusive_queues_verified']
    assert not pilot['design_selected_on_test']
    assert final['governance_test']['publishable'] and not final['governance_test']['smoke']
    assert not final['a_spec']['test_used_for_selection']
    d = final['d_summary']
    assert d['status'] == 'complete' and d['decision_allowed']
    assert d['original_test_rows_used'] == d['original_calibration_policy_rows_used'] == 0
    proxy = pd.read_csv(WORK / 'c_proxy_cv.csv')
    assert len(proxy) == 18 and not proxy.test_used.any()
    runpy.run_path(str(WORK / 'generate_visuals.py'), run_name='__main__')

    v1 = final['v1']
    bayes = final['deployment_policies']['bayes']
    risk = final['deployment_policies']['risk']
    v1_auc = v1['bootstrap_intervals']['auc']
    sample_ci = v1['bootstrap_intervals']['value_capture_relative_gain']
    deployment_ci = final['deployment_intervals']['relative_value_gain_vs_risk']
    net_ci = final['deployment_intervals']['net']
    candidate = final['strongest_nonpromoted_or_promoted_cv_candidate']
    model = final['selected_model_test']
    if protocol['gate_d_passed']:
        auc = model['v2_auc']
        auc_ci = model['v2_auc_95ci']
        test_difference = f"Paired frozen-test AUC gain {model['paired_auc_gain']:+.6f}; 95% CI [{model['paired_auc_gain_95ci'][0]:+.6f}, {model['paired_auc_gain_95ci'][1]:+.6f}]. Descriptive only; not used to reconsider promotion."
    else:
        auc = model['metrics']['roc_auc']
        auc_ci = [model['auc_95ci']['lower'], model['auc_95ci']['upper']]
        test_difference = 'No new classifier promoted; immutable v1 probabilities reused for the frozen descriptive policy batch.'
    spec = final['pilot_calibration']['spec']
    required = final['pilot_calibration']['simulated_required_enrolled_per_arm_grid']
    gates = pd.read_csv(WORK / 'd_results/gate_d.csv')
    gate_rows = '\n'.join(f"| {row.candidate} | {row.mean_auc_gain:+.6f} | [{row.corrected_auc_lower:+.6f}, {row.corrected_auc_upper:+.6f}] | {'pass' if row.pass_gate_d else 'reject'} | {row.reason} |" for row in gates.itertuples())
    calibrator_rows = '\n'.join(f"- {row['method']}: OOF log-loss improvement {row['paired_logloss_improvement']:+.7f}, CI [{row['ci_lower']:+.7f}, {row['ci_upper']:+.7f}]; {'eligible' if row['passes'] else 'not promoted'}." for row in final['a_spec']['calibration_candidates'] if row['method'] != 'sigmoid')
    stage1 = spec['stage1_cost']
    stage2 = spec['stage2_incremental_cost']
    plan = [
        'Retain the contribution-focused cover and supplied-data framing.',
        f"Separate sample +{v1['value_capture_relative_gain_over_risk']:.1%} from the 2% scenario ${bayes['net']/1000:.1f}k; add risk → value-aware → causal-profit maturity ladder and learning-only pilot caveat.",
        'Split T-Mobile [S1] and AT&T [S2] citations; show verified ARPU and distinct churn denominators; preserve intervention-specific backfire caveat.',
        'Retain integrity, sample prevalence and days-31–60 label boundaries.',
        'Replace chart with prior-shifted risk/value space, exact three-region counts/means and calibration cutoff; remove old handset comparison numbers; disclose plot cropping/subsampling.',
        'Keep the original operational-pattern chart and association-only interpretation.',
        f"Keep four original split counts; disclose prior v1 test evaluation and non-test repeated CV. Show audited proxy AUCs and actual Gate D {'pass' if protocol['gate_d_passed'] else 'failure'}; do not claim an information ceiling.",
        'Preserve the original ROC/calibration chart as an explicitly labeled v1 reference; disclose test reuse and selected-model status.',
        f"Replace value-capture chart with weighted deployment comparison: Bayes {bayes['value_recall']:.1%}, risk {risk['value_recall']:.1%}, relative {final['deployment_relative_value_gain']:+.1%} with CI; retain explicitly labeled v1 unweighted 1,500-row sample benchmark.",
        'Replace workflow panel with four exclusive operational queues, exact raw counts/weighted mean bills/value shares; residual digital-only queue is not uniformly known-low-usage. Prominent mandatory Service-Fix Floor.',
        f"Replace waterfall with three cost/fraction curves; dots are calibration-selected diagnostics, not test optima. Headline stays nominal10%, ${bayes['net']/1000:.1f}k conditional net; no optimized budget promoted.",
        'Keep editable native 3×3 sensitivity cells; update from frozen selection, break-even contact cost/prevention and prior stress. Include zero-contact alternative.',
        f"Replace pilot panel with disjoint core/additions, risk-only drops and below-cutoff exploration; linked-account randomization, logged propensities, Stage1 ${stage1:,.0f} and Stage2 +${stage2:,.0f}. Show negative profit-power/capacity finding and preregistered scale/extend/stop/harm rules.",
        'Remove unverified T-Mobile filing day; retain independently sourced market/vendor distinctions.',
        'Add verified prior-shift, cost-sensitive, CUPED and Cell2Cell references [M5–M8]; preserve data/method sources and truthful AI assistance disclosure without invented chat URL.'
    ]
    text = f'''# Checkpoint 2 — analytical freeze before root/deck promotion

All analyses were executed locally using Python 3.11, seed 20261028 and six threads. The original five supplied files and immutable v1 snapshot remain unchanged. No submission has been made.

## Headline evidence, with regimes kept separate

| Quantity | v1 reference | Frozen v2 |
|---|---:|---:|
| Selected classifier test AUC | {v1['selected_test_metrics']['roc_auc']:.6f} [{v1_auc['lower']:.6f}, {v1_auc['upper']:.6f}] | {auc:.6f} [{auc_ci[0]:.6f}, {auc_ci[1]:.6f}] |
| Sample10% relative value gain | {v1['value_capture_relative_gain_over_risk']:+.2%} [{sample_ci['lower']:+.2%}, {sample_ci['upper']:+.2%}] | {final['sample_relative_value_gain_v2']:+.2%} [{final['sample_intervals']['relative_value_gain_vs_risk']['lower']:+.2%}, {final['sample_intervals']['relative_value_gain_vs_risk']['upper']:+.2%}] |
| 2% scenario Bayes value recall | Same prior-consistent rule already used in v1 finance | {bayes['value_recall']:.2%}; risk {risk['value_recall']:.2%} |
| 2% scenario relative value gain vs risk | Not the +42.4% sample statistic | {final['deployment_relative_value_gain']:+.2%} [{deployment_ci['lower']:+.2%}, {deployment_ci['upper']:+.2%}] |
| 2% scenario conditional net | ${next(row for row in v1['base_business_scenario'] if row['policy']=='Value-aware')['net_contribution_scenario']:,.2f} | ${bayes['net']:,.2f} [${net_ci['lower']:,.2f}, ${net_ci['upper']:,.2f}] |

{test_difference}

All test intervals are descriptive paired-row intervals conditional on fitted models/lists. They do not measure treatment response or account for transport, retraining, selection or household clustering. The v1 test split was previously evaluated. The final v2 specification was frozen before one descriptive final batch; no test-selected decisions were made.

## Gates and rejected alternatives

- **Gate A:** prior-regime reconciliation qualifies; v1 already used deployment-consistent Bayes risk×value in its financial scenario. Clarify the original sample/weighted discrepancy, rather than claiming a new gain over that same rule.
- **Calibrator:** retain {protocol['calibrator']} after calibration-only five-fold comparison.
{calibrator_rows}
- **Budget:** retain nominal10%. Cost-specific calibration grid maxima remain diagnostics; their conditional intervals omit search uncertainty. At higher costs include no-contact with zero net.
- **Gate D:** {'PASSED' if protocol['gate_d_passed'] else 'FAILED'}; selected {protocol['model_candidate']}. Strongest corrected-lower-bound eligible candidate {candidate['candidate']}: mean ΔAUC {candidate['mean_auc_gain']:+.6f}, corrected95% CI [{candidate['corrected_auc_lower']:+.6f}, {candidate['corrected_auc_upper']:+.6f}]. Weighted top-tail calibration and convergence gates are mandatory. Sensitive variables are diagnostic only. Negative results do not prove an information ceiling.

| Challenger | Mean ΔAUC | Corrected95% CI | Decision | Reason |
|---|---:|---|---|---|
{gate_rows}

## Pilot feasibility — negative findings are retained

Stage1 requires {spec['allocation']['core_per_arm']:,}/arm ({spec['stage1_total_enrolled']:,} unique linked core accounts), with an assumed ${stage1:,.0f} contact/startup envelope. Stage2 adds {spec['allocation']['risk_only_per_arm_stage2']:,}/arm risk-only drops and {spec['allocation']['exploration_per_arm_stage2']:,}/arm below-union learning accounts at +${stage2:,.0f}. These are not fully quoted launch costs or powered policy comparisons. Only the agreed `both` region cancels in the Bayes-minus-risk contrast; additions-minus-drops is deployment-mass weighted.

Calibration-selected simulation grid requirements: binary {required['binary_churn']:,}/arm; adjusted contribution {required['adjusted_contribution'] if required['adjusted_contribution'] is not None else 'not established within the grid'}/arm; unadjusted contribution {required['unadjusted_contribution'] if required['unadjusted_contribution'] is not None else '80% power not established through160,000/arm'}. Cross-sectional covariance simulation is not validated CUPED or household-clustered power. The core account requirement exceeds a single approximately10,000-account list in the100,000-account financial scenario; use a larger eligible portfolio or successive cohorts and quote linkage/follow-up costs before launch.

## Exact slide-by-slide specification — fifteen pages, no additions

''' + '\n'.join(f'{number}. {instruction}' for number, instruction in enumerate(plan, 1)) + f'''

Exactly three existing chart replacements (slides5,9,11) and two focused panel replacements (slides10,13). Native heatmap remains editable. Navy/teal/amber/slate/pale and Aptos styles remain consistent.

## Frozen artifact and QA status

- Protocol SHA-256: `{final['protocol_sha256']}`.
- Final batch completion SHA-256: `{sha256((WORK/'final_batch_completion.json').read_bytes()).hexdigest()}`.
- All non-test/final source and artifact fingerprints verified; original75k proxy CV completed once; D used zero original calibration/test rows.
- Analytical assertions above passed. Root promotion, executed canonical notebook, Office geometry check, claims/citation audit, PowerPoint export and all15-slide visual review are still required.
- If a remaining QA failure cannot be resolved cleanly, use the tested v1 rollback. No external submission or fabricated AI-chat URL.
'''
    target = WORK / 'checkpoint2_summary.md'
    target.write_text(text, encoding='utf-8')
    return target


def final_report():
    protocol = verify_completed()
    final = json.loads((WORK / 'final_metrics.json').read_text(encoding='utf-8'))
    out = ROOT / 'analysis_outputs'
    checks = json.loads((out / 'delivery_checks.json').read_text(encoding='utf-8'))
    review = json.loads((WORK / 'visual_review.json').read_text(encoding='utf-8'))
    geometry = json.loads((WORK / 'office_geometry_check.json').read_text(encoding='utf-8'))
    assert checks['notebook_errors'] == 0 and checks['notebook_matches_pipeline']
    assert checks['original_nine_code_cells_preserved'] and checks['source_files_unchanged']
    assert checks['pdf_pages'] == checks['pptx_slides'] == geometry['slide_count'] == 15
    assert checks['pdf_bytes'] <= 10_000_000 and not checks['out_of_bounds_shapes']
    assert geometry['issue_count'] == checks['office_geometry_issue_count'] == 0
    assert checks['office_geometry_check_sha256'] == sha256((WORK / 'office_geometry_check.json').read_bytes()).hexdigest()
    assert checks['powerpoint_export'] == 'successful'
    assert checks['protocol_sha256'] == final['protocol_sha256']
    assert review['status'] == 'passed' and review['slides_reviewed'] == list(range(1, 16))
    assert review['clipped_text_or_unintended_overlaps'] == 0
    assert review['render_sha256'] == checks['render_sha256']
    for relative, digest in checks['render_sha256'].items():
        assert sha256((ROOT / relative).read_bytes()).hexdigest() == digest
    assert review['contact_sheet_sha256'] == sha256((out / 'deck_contact_sheet.png').read_bytes()).hexdigest()
    assert review['delivery_checks_sha256'] == sha256((out / 'delivery_checks.json').read_bytes()).hexdigest()
    hashes = {name: sha256((ROOT / name).read_bytes()).hexdigest()
              for name in ('philopateer.pdf', 'philopateer.pptx', 'philopateer.ipynb', 'references.txt')}
    assert checks['delivery_sha256'] == hashes
    assert checks['pdf_bytes'] == (ROOT / 'philopateer.pdf').stat().st_size
    assert geometry['pptx_sha256'] == hashes['philopateer.pptx']
    manifest = json.loads((ROOT / 'v1_frozen/sha256_manifest.json').read_text(encoding='utf-8'))
    for relative, info in manifest.items():
        frozen = ROOT / 'v1_frozen' / relative
        assert frozen.stat().st_size == info['bytes']
        assert sha256(frozen.read_bytes()).hexdigest() == info['sha256'], relative
    from claim_checks import verify_claims
    verify_claims(ROOT)
    v1 = final['v1']
    bayes = final['deployment_policies']['bayes']
    risk = final['deployment_policies']['risk']
    sample = final['sample_intervals']['relative_value_gain_vs_risk']
    deployment = final['deployment_intervals']['relative_value_gain_vs_risk']
    net = final['deployment_intervals']['net']
    candidate = final['strongest_nonpromoted_or_promoted_cv_candidate']
    model = final['selected_model_test']
    if protocol['gate_d_passed']:
        auc, auc_ci = model['v2_auc'], model['v2_auc_95ci']
        test = f"Paired test ΔAUC {model['paired_auc_gain']:+.6f} [{model['paired_auc_gain_95ci'][0]:+.6f}, {model['paired_auc_gain_95ci'][1]:+.6f}]."
    else:
        auc = model['metrics']['roc_auc']
        auc_ci = [model['auc_95ci']['lower'], model['auc_95ci']['upper']]
        test = 'Retained v1 classifier; cached v1 test probabilities reused, not rescored.'
    pilot = final['pilot_calibration']
    spec = pilot['spec']
    required = pilot['simulated_required_enrolled_per_arm_grid']
    gate_rows = pd.read_csv(WORK / 'd_results/gate_d.csv')
    rejected = ', '.join(gate_rows.loc[~gate_rows.pass_gate_d, 'candidate'])
    v1_auc = v1['bootstrap_intervals']['auc']
    v1_sample = v1['bootstrap_intervals']['value_capture_relative_gain']
    v1_net = next(row['net_contribution_scenario'] for row in v1['base_business_scenario'] if row['policy'] == 'Value-aware')
    adjusted = f"{required['adjusted_contribution']:,}/arm" if required['adjusted_contribution'] is not None else 'not established within the grid'
    calibration = '; '.join(f"{row['method']}: Δlog-loss {row['paired_logloss_improvement']:+.5f} [{row['ci_lower']:+.5f}, {row['ci_upper']:+.5f}]"
                            for row in final['a_spec']['calibration_candidates'] if row['method'] != 'sigmoid')
    text = f'''# Final v2 upgrade report — philopateer

**Completed locally; NOT submitted.** Gate A qualifies through prior-regime reconciliation: v1 already used deployment-consistent risk×value in finance. Gate D {'passed' if protocol['gate_d_passed'] else 'failed'}; selected `{protocol['model_candidate']}`. No optimized budget promoted; nominal 10% retained.

| Metric | v1 reference | Frozen v2 (95% CI) |
|---|---:|---:|
| Test AUC | {v1['selected_test_metrics']['roc_auc']:.4f} [{v1_auc['lower']:.4f}, {v1_auc['upper']:.4f}] | {auc:.4f} [{auc_ci[0]:.4f}, {auc_ci[1]:.4f}] |
| Sample 10% relative value gain | {v1['value_capture_relative_gain_over_risk']:+.1%} [{v1_sample['lower']:+.1%}, {v1_sample['upper']:+.1%}] | {final['sample_relative_value_gain_v2']:+.1%} [{sample['lower']:+.1%}, {sample['upper']:+.1%}] |
| Deployment 2% relative value gain vs risk | Separate from sample benchmark | {final['deployment_relative_value_gain']:+.1%} [{deployment['lower']:+.1%}, {deployment['upper']:+.1%}] |
| Deployment 2% conditional net | ${v1_net:,.2f} | ${bayes['net']:,.2f} [${net['lower']:,.2f}, ${net['upper']:,.2f}] |

**What changed:** separated sample and hypothetical deployment regimes; deployment value recall is {bayes['value_recall']:.1%} vs risk {risk['value_recall']:.1%}. Replaced three charts and two focused panels; kept fifteen slides and the native editable sensitivity cells. Added exclusive routing, mandatory Service-Fix Floor, linked-account randomization, proxy-recoverability and subgroup audits, verified citations, and exact source-bound claims/plot checks.

**Tests and rejections:** strongest eligible repeated-CV challenger `{candidate['candidate']}`: mean ΔAUC {candidate['mean_auc_gain']:+.6f}, corrected CI [{candidate['corrected_auc_lower']:+.6f}, {candidate['corrected_auc_upper']:+.6f}]. {test} Rejected: {rejected}. {calibration}; neither promoted. Calibration budget maxima lack selection-adjusted uncertainty. Complete diagnostics and every rejection are in `v2_work/checkpoint2_summary.md` and the executed notebook; negative results do not establish an information ceiling.

**Pilot and open assumptions:** Stage 1 {spec['allocation']['core_per_arm']:,}/arm, ${spec['stage1_cost']:,.0f} contact/startup envelope; Stage 2 +${spec['stage2_incremental_cost']:,.0f}. Binary simulation grid requires {required['binary_churn']:,}/arm; adjusted contribution {adjusted}; unadjusted 80% power not established through 160,000/arm. This is cross-sectional planning, not validated household-clustered CUPED power or a profit-powered list comparison. A larger portfolio/successive cohorts and quoted linkage/follow-up costs are required. Hypothetical 2% prior, 20% prevention, six months, 60% margin, and monetary interpretation remain unverified. Prior stability and live calibration require validation. Test intervals are descriptive and conditional; v1 previously evaluated this split, and all v2 decisions were frozen before the single final batch.

**QA:** notebook {checks['executed_notebook_code_cells']} executed code cells, zero errors, original nine preserved; fifteen-page PDF {checks['pdf_bytes']:,} bytes; Office geometry zero issues; all fifteen full-size renders and contact sheet reviewed; claims/citations/source hashes verified. Immutable v1 snapshot: {len(manifest)} files verified byte-for-byte. No data uploaded or AI-chat URL fabricated.

**Updated SHA-256**

''' + '\n'.join(f'- `{name}`: `{digest}`' for name, digest in hashes.items()) + f'''

Protocol: `{final['protocol_sha256']}`.

**Manual submission:** review the files, add a real shareable AI conversation link only if required and available, then upload `philopateer.pdf`, `philopateer.ipynb`, and `references.txt` to Omnicampus under `philopateer` before **28 November 2026, 11:30 UTC**. The editable PPTX is supplied as a supporting artifact. Nothing has been submitted automatically.
'''
    target = ROOT / 'FINAL_V2_UPGRADE_REPORT.md'
    target.write_text(text, encoding='utf-8')
    return target


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--final', action='store_true')
    args = parser.parse_args()
    print(final_report() if args.final else build())
