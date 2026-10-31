# WP1 — Pilot capacity and power: two nulls
Status: DONE [E], with literal-oracle caveat

Inputs: [E] Exact hashes are recorded in ../results/wp1_power.json.

Population / assumptions:
- [E] 12,990 selected unique non-test OOF customers; weighted control churn 4.842493%.
- [A] Uniform prevention, 6 retained months, .60 margin, $1 per treated contact, free controls; $5,000 startup excluded from the per-account variable-profit test.
- [A] IID account sampling; DEFF 1/1.1/1.25 only analytically inflates sampling errors. Household linkage and actual treatment labels do not exist.

Method (≤10 lines)
[E] 1,000 replicates per n/gamma point, seed 20261029. Multinomial record counts are exactly equivalent to sampling individual records with replacement. E1 uses observed churn; E2/E3 literal use the appendix latent prevented indicator; E2/E3 observed comparators use realized total contribution, OLS with V/p_d/fixed risk-value bands and HC1 errors; E4 uses fixed weighted V-decile contrasts. Positive crossings of two-sided 95% bounds are reported for both nulls; effect and variable-profit are kept separate.

Results: [E] all simulation outputs are conditional on the stated [A] inputs.
| n/arm [A] | prevention [A] | E4 effect power [E] | E4 variable-profit power [E] |
|---:|---:|---:|---:|
| 5,000 | 10% | 19.8% | 2.6% |
| 5,000 | 16% | 42.9% | 7.9% |
| 5,000 | 20% | 59.7% | 19.9% |
| 5,000 | 30% | 93.6% | 60.7% |
| 7,872 | 10% | 27.5% | 2.1% |
| 7,872 | 16% | 59.9% | 11.5% |
| 7,872 | 20% | 78.6% | 27.9% |
| 7,872 | 30% | 99.3% | 79.8% |

| Method [E] | Null [E] | First qualifying grid n/arm at 20% prevention [E/A] |
|---|---|---:|
| E1_churn | effect_power | 7872 |
| E2_literal_oracle | effect_power | 2500 |
| E2_literal_oracle | profit_power | 5000 |
| E3_literal_oracle | effect_power | 2500 |
| E3_literal_oracle | profit_power | 5000 |
| E4_V_stratified | effect_power | 10000 |
| E4_V_stratified | profit_power | 40000 |
| E2_observed | effect_power | 40000 |
| E2_observed | profit_power | Not established through 80,000 |
| E3_observed | effect_power | 10000 |
| E3_observed | profit_power | 40000 |

[E] Literal E2/E3 have access to which cancellations were prevented; real pilots observe only assignment and realized outcomes, not both counterfactuals. Their artificially strong power is not eligible for an integration claim.

[E] Gap from v2 80,000/arm (≤5 lines):
- [E] v2 tested net contribution after $1/contact plus $5,000/enrolled, not merely a positive gross effect.
- [E] v2 used .9×enrolled for random follow-up loss and fixed calibration-trained adjustment coefficients.
- [E] WP1 separates the zero-gross and $1-gross nulls, excludes startup from those per-account tests and uses trial OLS or V-decile contrasts.
- [R] Neither a different target nor an oracle statistic establishes a reduction of v2 profit-powered rollout requirements.

Acceptance checks:
- [E] PASS: legacy reference first qualifying grid 7,872/arm, within ±8% of 7,872; 20,000 replicates/reference point.
- [E] PASS: all observable gamma=0 effect rejection rates ≤5.5%; complete values and MC SE/intervals are retained.
- [E] PASS: v2 framing gap explained above; all 48 primary points have 1,000 replicates; test rows unused.

Capacity conclusions [E, conditional on A]:
- [E] At 7,872/arm and assumed 20% prevention, E4 has 78.6% power for any gross effect and 27.9% for variable-profit margin; this is not fully loaded profitability evidence.
- [E] One 10,000-account list provides at most 5,000/arm: E4 powers 59.7%/19.9% at 20% prevention, below the 80% planning target.
- [R] Treat Stage 1 as learning; price actual costs and validate clustered/live power before deciding rollout.

Deviations from brief: [E] Oracle E2/E3 preserved but labeled unusable; observable total-contribution comparators added, not substituted; legacy follow-up reference separated from the specified primary grid.
Claims now allowed: [E/A] Conditional simulated capacity, two distinct nulls, Monte Carlo uncertainty and oracle limitation.
Claims still forbidden: [R] Measured causal effect, live CUPAC/CUPED gains, identified profitability, or a solved 80,000/arm problem.
Open questions for human: [E] None; all mandatory STOP conditions remain clear.
