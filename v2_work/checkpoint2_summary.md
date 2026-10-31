# Checkpoint 2 — analytical freeze before root/deck promotion

All analyses were executed locally using Python 3.11, seed 20261028 and six threads. The original five supplied files and immutable v1 snapshot remain unchanged. No submission has been made.

## Headline evidence, with regimes kept separate

| Quantity | v1 reference | Frozen v2 |
|---|---:|---:|
| Selected classifier test AUC | 0.697811 [0.689903, 0.705495] | 0.697811 [0.689903, 0.705495] |
| Sample10% relative value gain | +42.44% [+36.36%, +48.99%] | +42.44% [+35.66%, +48.56%] |
| 2% scenario Bayes value recall | Same prior-consistent rule already used in v1 finance | 29.51%; risk 25.58% |
| 2% scenario relative value gain vs risk | Not the +42.4% sample statistic | +15.37% [+11.26%, +19.67%] |
| 2% scenario conditional net | $3,747.08 | $3,747.08 [$2,761.37, $4,660.64] |

No new classifier promoted; immutable v1 probabilities reused for the frozen descriptive policy batch.

All test intervals are descriptive paired-row intervals conditional on fitted models/lists. They do not measure treatment response or account for transport, retraining, selection or household clustering. The v1 test split was previously evaluated. The final v2 specification was frozen before one descriptive final batch; no test-selected decisions were made.

## Gates and rejected alternatives

- **Gate A:** prior-regime reconciliation qualifies; v1 already used deployment-consistent Bayes risk×value in its financial scenario. Clarify the original sample/weighted discrepancy, rather than claiming a new gain over that same rule.
- **Calibrator:** retain sigmoid after calibration-only five-fold comparison.
- beta: OOF log-loss improvement -0.0001529, CI [-0.0003457, +0.0000509]; not promoted.
- isotonic: OOF log-loss improvement -0.0035814, CI [-0.0074541, -0.0008886]; not promoted.
- **Budget:** retain nominal10%. Cost-specific calibration grid maxima remain diagnostics; their conditional intervals omit search uncertainty. At higher costs include no-contact with zero net.
- **Gate D:** FAILED; selected baseline_lgbm. Strongest corrected-lower-bound eligible candidate nested_blend: mean ΔAUC +0.001085, corrected95% CI [-0.000032, +0.002203]. Weighted top-tail calibration and convergence gates are mandatory. Sensitive variables are diagnostic only. Negative results do not prove an information ceiling.

| Challenger | Mean ΔAUC | Corrected95% CI | Decision | Reason |
|---|---:|---|---|---|
| g1_temporal | +0.000012 | [-0.001987, +0.002010] | reject | AUC mean/CI gate failed; weighted tail non-degradation not established |
| g3_billing_gaps | +0.000117 | [-0.000470, +0.000705] | reject | AUC mean/CI gate failed; weighted tail non-degradation not established |
| g4_call_care | +0.000159 | [-0.001072, +0.001391] | reject | AUC mean/CI gate failed; weighted tail non-degradation not established |
| g5_equipment_cycle | -0.000132 | [-0.000854, +0.000589] | reject | AUC mean/CI gate failed; weighted tail non-degradation not established |
| g6_tenure_pricing | -0.000142 | [-0.001028, +0.000744] | reject | AUC mean/CI gate failed; weighted tail non-degradation not established |
| nested_blend | +0.001085 | [-0.000032, +0.002203] | reject | AUC mean/CI gate failed; weighted tail non-degradation not established; model convergence warning |
| nested_catboost | -0.003635 | [-0.006467, -0.000803] | reject | AUC mean/CI gate failed; weighted tail non-degradation not established |
| nested_lgbm | +0.000415 | [-0.000360, +0.001191] | reject | AUC mean/CI gate failed; weighted tail non-degradation not established |
| nested_spline_logistic | -0.025530 | [-0.030427, -0.020633] | reject | AUC mean/CI gate failed; weighted tail non-degradation not established; model convergence warning |
| nested_value_weighted_lgbm | -0.004487 | [-0.006911, -0.002064] | reject | AUC mean/CI gate failed; weighted tail non-degradation not established; weighted value-capture improvement not established |
| nested_xgboost | +0.000116 | [-0.001546, +0.001778] | reject | AUC mean/CI gate failed; weighted tail non-degradation not established |

## Pilot feasibility — negative findings are retained

Stage1 requires 7,872/arm (15,744 unique linked core accounts), with an assumed $12,872 contact/startup envelope. Stage2 adds 2,000/arm risk-only drops and 1,000/arm below-union learning accounts at +$3,000. These are not fully quoted launch costs or powered policy comparisons. Only the agreed `both` region cancels in the Bayes-minus-risk contrast; additions-minus-drops is deployment-mass weighted.

Calibration-selected simulation grid requirements: binary 7,872/arm; adjusted contribution 80000/arm; unadjusted contribution 80% power not established through160,000/arm. Cross-sectional covariance simulation is not validated CUPED or household-clustered power. The core account requirement exceeds a single approximately10,000-account list in the100,000-account financial scenario; use a larger eligible portfolio or successive cohorts and quote linkage/follow-up costs before launch.

## Exact slide-by-slide specification — fifteen pages, no additions

1. Retain the contribution-focused cover and supplied-data framing.
2. Separate sample +42.4% from the 2% scenario $3.7k; add risk → value-aware → causal-profit maturity ladder and learning-only pilot caveat.
3. Split T-Mobile [S1] and AT&T [S2] citations; show verified ARPU and distinct churn denominators; preserve intervention-specific backfire caveat.
4. Retain integrity, sample prevalence and days-31–60 label boundaries.
5. Replace chart with prior-shifted risk/value space, exact three-region counts/means and calibration cutoff; remove old handset comparison numbers; disclose plot cropping/subsampling.
6. Keep the original operational-pattern chart and association-only interpretation.
7. Keep four original split counts; disclose prior v1 test evaluation and non-test repeated CV. Show audited proxy AUCs and actual Gate D failure; do not claim an information ceiling.
8. Preserve the original ROC/calibration chart as an explicitly labeled v1 reference; disclose test reuse and selected-model status.
9. Replace value-capture chart with weighted deployment comparison: Bayes 29.5%, risk 25.6%, relative +15.4% with CI; retain explicitly labeled v1 unweighted 1,500-row sample benchmark.
10. Replace workflow panel with four exclusive operational queues, exact raw counts/weighted mean bills/value shares; residual digital-only queue is not uniformly known-low-usage. Prominent mandatory Service-Fix Floor.
11. Replace waterfall with three cost/fraction curves; dots are calibration-selected diagnostics, not test optima. Headline stays nominal10%, $3.7k conditional net; no optimized budget promoted.
12. Keep editable native 3×3 sensitivity cells; update from frozen selection, break-even contact cost/prevention and prior stress. Include zero-contact alternative.
13. Replace pilot panel with disjoint core/additions, risk-only drops and below-cutoff exploration; linked-account randomization, logged propensities, Stage1 $12,872 and Stage2 +$3,000. Show negative profit-power/capacity finding and preregistered scale/extend/stop/harm rules.
14. Remove unverified T-Mobile filing day; retain independently sourced market/vendor distinctions.
15. Add verified prior-shift, cost-sensitive, CUPED and Cell2Cell references [M5–M8]; preserve data/method sources and truthful AI assistance disclosure without invented chat URL.

Exactly three existing chart replacements (slides5,9,11) and two focused panel replacements (slides10,13). Native heatmap remains editable. Navy/teal/amber/slate/pale and Aptos styles remain consistent.

## Frozen artifact and QA status

- Protocol SHA-256: `700ca4446024aeb1d844e46513c2a4118f698035cd50c4e9a5b0f6f07218c66a`.
- Final batch completion SHA-256: `80bc9bfd1ff2b4ca559e5cc4ba3b85e27b5d590413ad3fbe45a44d62a633a9dc`.
- All non-test/final source and artifact fingerprints verified; original75k proxy CV completed once; D used zero original calibration/test rows.
- Analytical assertions above passed. Root promotion, executed canonical notebook, Office geometry check, claims/citation audit, PowerPoint export and all15-slide visual review are still required.
- If a remaining QA failure cannot be resolved cleanly, use the tested v1 rollback. No external submission or fabricated AI-chat URL.
