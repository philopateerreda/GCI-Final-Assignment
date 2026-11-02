# WP2 — Pilot decision quality and EVSI
Status: DONE

Inputs:
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/final_metrics.json` — SHA-256 `1d14a4fea10ab391631379f82cd6a82e5a65ede4f01db5b540c9aec3612eea1e`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/results/wp1_power.json` — SHA-256 `1342bb553dfd24e4697d210d141392f32f0ac8b43f66ea3627db95622d714305`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/results/wp1_simulation_samples.npz` — SHA-256 `b85da7f76a5c7562c3b207bad3b0b109913d62cd8575edf09580bb7753bfe068`.

Population / assumptions:
- [A] Independent account trials, uniform prevention, assumed economics; no live treatment or household data.
- [A] Flat p0 prior centered on stored 4.7711%, half-width 2 pp; horizons 1/6/12 are assumptions.

Method (≤10 lines)
[E] Reused observable WP1 HC1 contrasts; mapped effects to frozen cohort net and inflated SE by DEFF. Applied scale/extend/stop rules and the ambiguity zone. Integrated full-support two-dimensional posteriors for 4,096 pilots per prior/sample size; computed regret, centered and direct EVSI identities, refinement and large-n checks.

Results:
| Prevention prior [A] | EVSI/cohort [E/A] | MC SE [E] | EVPI [E/A] |
|---|---:|---:|---:|
| Beta(6,14) | $45.27 | $4.83 | $195.71 |
| Beta(6,24) | $531.22 | $7.56 | $1,093.29 |
| Beta(2,18) | $455.45 | $8.15 | $832.36 |
[E/A] At 7,872/arm, 20% prevention and DEFF 1.1, scale/extend/stop probabilities are 7.6%/91.9%/0.5%; no guardrail breach is assumed.
[R] The pilot can be framed as the first production wave plus an option whose simulated information value is $45–$531 per future cohort across these priors. This is not approval to spend: the illustrative $12,872 also buys production contacts, so it is not a like-for-like pure research cost comparison.

Acceptance checks:
- [E] PASS: a6_b14_n7872, nonnegative_evsi.
- [E] PASS: a6_b14_n7872, evsi_at_most_evpi.
- [E] PASS: a6_b14_n7872, centered_identity_mc_agreement.
- [E] PASS: a6_b14_n7872, grid_refinement_within_5_dollars.
- [E] PASS: a6_b14_n7872, large_n_gap_upper_bound_within_5percent_or_5dollars.
- [E] PASS: a6_b14_n1000000, nonnegative_evsi.
- [E] PASS: a6_b14_n1000000, evsi_at_most_evpi.
- [E] PASS: a6_b14_n1000000, centered_identity_mc_agreement.
- [E] PASS: a6_b14_n1000000, grid_refinement_within_5_dollars.
- [E] PASS: a6_b14_n1000000, large_n_gap_upper_bound_within_5percent_or_5dollars.
- [E] PASS: a6_b24_n7872, nonnegative_evsi.
- [E] PASS: a6_b24_n7872, evsi_at_most_evpi.
- [E] PASS: a6_b24_n7872, centered_identity_mc_agreement.
- [E] PASS: a6_b24_n7872, grid_refinement_within_5_dollars.
- [E] PASS: a6_b24_n7872, large_n_gap_upper_bound_within_5percent_or_5dollars.
- [E] PASS: a6_b24_n1000000, nonnegative_evsi.
- [E] PASS: a6_b24_n1000000, evsi_at_most_evpi.
- [E] PASS: a6_b24_n1000000, centered_identity_mc_agreement.
- [E] PASS: a6_b24_n1000000, grid_refinement_within_5_dollars.
- [E] PASS: a6_b24_n1000000, large_n_gap_upper_bound_within_5percent_or_5dollars.
- [E] PASS: a2_b18_n7872, nonnegative_evsi.
- [E] PASS: a2_b18_n7872, evsi_at_most_evpi.
- [E] PASS: a2_b18_n7872, centered_identity_mc_agreement.
- [E] PASS: a2_b18_n7872, grid_refinement_within_5_dollars.
- [E] PASS: a2_b18_n7872, large_n_gap_upper_bound_within_5percent_or_5dollars.
- [E] PASS: a2_b18_n1000000, nonnegative_evsi.
- [E] PASS: a2_b18_n1000000, evsi_at_most_evpi.
- [E] PASS: a2_b18_n1000000, centered_identity_mc_agreement.
- [E] PASS: a2_b18_n1000000, grid_refinement_within_5_dollars.
- [E] PASS: a2_b18_n1000000, large_n_gap_upper_bound_within_5percent_or_5dollars.

Deviations from brief:
[E] Cohort economic transfer normalizes by the non-test gross-effect coefficient, preventing inconsistent fixed-cost allocation across sample sizes.
[E] Primary EVSI uses the equivalent posterior-regret identity for variance reduction, not clipping or optimistic bound adjustment.

Claims now allowed:
[E/A] Conditional decision probabilities, prior-sensitive information values and assumed cohort-horizon arithmetic.

Claims still forbidden:
[R] Actual causal profit, live clustered power, observed safety, or a claim that EVSI pays for the pilot.

Open questions for human: [E] None; integration remains a separate human decision.
