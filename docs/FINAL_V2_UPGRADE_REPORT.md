# Final v2 upgrade report — philopateer

**Completed locally; NOT submitted.** Gate A qualifies through prior-regime reconciliation: v1 already used deployment-consistent risk×value in finance. Gate D failed; selected `baseline_lgbm`. No optimized budget promoted; nominal 10% retained.

| Metric | v1 reference | Frozen v2 (95% CI) |
|---|---:|---:|
| Test AUC | 0.6978 [0.6899, 0.7055] | 0.6978 [0.6899, 0.7055] |
| Sample 10% relative value gain | +42.4% [+36.4%, +49.0%] | +42.4% [+35.7%, +48.6%] |
| Deployment 2% relative value gain vs risk | Separate from sample benchmark | +15.4% [+11.3%, +19.7%] |
| Deployment 2% conditional net | $3,747.08 | $3,747.08 [$2,761.37, $4,660.64] |

**What changed:** separated sample and hypothetical deployment regimes; deployment value recall is 29.5% vs risk 25.6%. Replaced three charts and two focused panels; kept fifteen slides and the native editable sensitivity cells. Added exclusive routing, mandatory Service-Fix Floor, linked-account randomization, proxy-recoverability and subgroup audits, verified citations, and exact source-bound claims/plot checks.

**Tests and rejections:** strongest eligible repeated-CV challenger `nested_blend`: mean ΔAUC +0.001085, corrected CI [-0.000032, +0.002203]. Retained v1 classifier; cached v1 test probabilities reused, not rescored. Rejected: g1_temporal, g3_billing_gaps, g4_call_care, g5_equipment_cycle, g6_tenure_pricing, nested_blend, nested_catboost, nested_lgbm, nested_spline_logistic, nested_value_weighted_lgbm, nested_xgboost. beta: Δlog-loss -0.00015 [-0.00035, +0.00005]; isotonic: Δlog-loss -0.00358 [-0.00745, -0.00089]; neither promoted. Calibration budget maxima lack selection-adjusted uncertainty. Complete diagnostics and every rejection are in `v2_work/checkpoint2_summary.md` and the executed notebook; negative results do not establish an information ceiling.

**Pilot and open assumptions:** Stage 1 7,872/arm, $12,872 contact/startup envelope; Stage 2 +$3,000. Binary simulation grid requires 7,872/arm; adjusted contribution 80,000/arm; unadjusted 80% power not established through 160,000/arm. This is cross-sectional planning, not validated household-clustered CUPED power or a profit-powered list comparison. A larger portfolio/successive cohorts and quoted linkage/follow-up costs are required. Hypothetical 2% prior, 20% prevention, six months, 60% margin, and monetary interpretation remain unverified. Prior stability and live calibration require validation. Test intervals are descriptive and conditional; v1 previously evaluated this split, and all v2 decisions were frozen before the single final batch.

**QA:** notebook 25 executed code cells, zero errors, original nine preserved; fifteen-page PDF 846,608 bytes; Office geometry zero issues; all fifteen full-size renders and contact sheet reviewed; claims/citations/source hashes verified. Immutable v1 snapshot: 67 files verified byte-for-byte. No data uploaded or AI-chat URL fabricated.

**Updated SHA-256**

- `philopateer.pdf`: `a51d2c0ff8aa6ebb0f679e680d6424b01cd7b95b9a0d23ae7a2eecc56de210ea`
- `philopateer.pptx`: `a50a66fd77d062bdc45aeefb00ce8652b20b952de06dcb27e8ab4f15c37e46bc`
- `philopateer.ipynb`: `aaa170b19923c087f9b38f85b546626b7465a3d17f5ae7037812c6aed5736b35`
- `references.txt`: `b12fb18aafc83e2d599e15d04c689ee5cd85c10082c1761ab0c6f1d01606d361`

Protocol: `700ca4446024aeb1d844e46513c2a4118f698035cd50c4e9a5b0f6f07218c66a`.

**Manual submission:** review the files, add a real shareable AI conversation link only if required and available, then upload `philopateer.pdf`, `philopateer.ipynb`, and `references.txt` to Omnicampus under `philopateer` before **28 November 2026, 11:30 UTC**. The editable PPTX is supplied as a supporting artifact. Nothing has been submitted automatically.
