# WP0 — Preflight, inventory, sandbox
Status: DONE [E]

Inputs: [E] Exact paths, presence, sizes and SHA-256 are in ../results/inventory.json.

Population / assumptions:
- [E] Ten baseline-only NPZ caches give 150,000 repeated OOF predictions on 75,000 unique original train/validation customers; all IDs are verified against the saved split manifest.
- [R] Average the two raw OOF predictions per Customer_ID; apply the frozen sigmoid and join source V using the saved training limits. Do not count repeats as extra independent customers.
- [A] Deployment prior 2%, sample prior 49.562%, six months, 60% margin and monetary interpretation remain scenario inputs.
- [E] No test rows are loaded into a scientific data frame; the Record.csv reader parses billing only after an allowed non-test ID check.

Method (≤10 lines)
[E] Ran the two prescribed read-only verifiers; hashed all four deliverables; inventoried inputs; read v2 source code without executing analytical entrypoints; computed population sanity and closed-form headline checks; saved a full outside-sandbox content manifest.

Results:
| Quantity | Result |
|---|---:|
| Selected unique non-test rows [E] | 12,990 |
| Weighted selected mass [E, conditional on A] | 10249.982854 |
| Selected control churn [E, conditional on A] | 4.842493% |
| Frozen v1 reference [E] | 4.771148% |
| Difference [E] | +0.071344 percentage points |
| G from frozen JSON scalar [E, conditional on A] | 93660.01994886 |
| K from frozen JSON scalar [E, conditional on A] | 14984.92153411 |
| Full outside-sandbox snapshot [E] | 4,246 files |

Acceptance checks:
- [E] PASS: four delivery hashes match; immutable v1 has 67 verified files; completed frozen batch verifier returned without error.
- [E] PASS: population within ±0.5 percentage points; actual difference +0.071344.
- [E] PASS: three prevention-prior headline probabilities within .005 and dollar results within 1% of brief section 3.
- [E] PASS: every absent input is listed; only FINAL_ASSESSMENT_HANDOFF_CONCISE.md is absent, and no training or test reconstruction is needed.

Code paths [E]:
- [E] prior_stress: v2_work/workstream_a.py:111-119, analyze. Loops frozen prior-specific calibration thresholds; measure computes scenario weights and economics. analyze writes files: never call.
- [E] budget_search: v2_work/workstream_a.py:89-101, prepare. Uses saved p_s_oof, fractions 1%-30%, costs .25/1/2/5, then freezes thresholds. prepare fits and writes: never call.
- [E] pilot_power: v2_work/workstream_b.py:157-202, power. floor(.9*enrolled), observed total contribution, fixed calibration adjustment, variable and allocated startup costs; called only through a writing entrypoint in v2.
- [E] value: v2_work/common.py:57-60, values. Nonnegative value, original-training median fill and p99. New loader uses saved 44.99 and 115.5159 without recomputing training thresholds.
- [E] oof_cache: v2_work/workstream_d.py:698-719, evaluate_arrays. Ten baseline-only NPZs contain Customer_ID/y/raw; two cross-fitted raw predictions averaged once per account; no models imported.

Deviations from brief:
- [E] The named concise handoff is absent; the full current handoff was read. Its section numbering differs from the reviewer summary.
- [E] Rules are scoped inside v3_addons; no rule/config file outside the boundary was touched.

Claims now allowed: [E] Frozen delivery integrity passes; preferred non-test population is available and passes sanity; quoted headline arithmetic reproduces.
Claims still forbidden: [R] Treatment effectiveness, causal profit, live prevalence, model gains, fairness certification and production readiness.
Open questions for human: [E] None; no STOP condition has fired.
