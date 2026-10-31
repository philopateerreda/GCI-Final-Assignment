# Workstream A — Non-test decisions completed

A1: Weighted evaluation mass is exactly 100,000 at each assumed1%,2%,5% prior; weights use the evaluation partition's actual observed class proportions to avoid normalization drift. Sample evaluation remains separately identified. Operational thresholds are fitted on the10k calibration partition; achieved evaluation coverage must be disclosed, not silently called exactly equal.

A2: All five requested policies have calibration-fitted cutoffs. At the2% calibration benchmark, Bayes recurring-value recall31.15%, risk-only26.98%, sample-probability-times-value27.59%. These are calibration diagnostics, not test headlines. Agreed core1,224 raw customers, value-aware additions508, risk-only drops764; raw and weighted counts, mean bills, precision, variable contribution and proportional fixed-cost allocation are preserved in the overlap table. Final test counts are evaluated only after model/policy freeze.

A3: Five-fold calibration OOF log loss: sigmoid0.622644, beta0.622797, clipped isotonic0.626225. Beta improvement CI crosses zero; isotonic worsens overall log loss despite slightly better top-tail Brier. Retain sigmoid.300 paired calibration resampling replicates propagate fitting/threshold uncertainty in addition to300 conditional paired evaluation resamples. These omit retraining, true treatment-response and transport uncertainty.

A4: Complete1–30% curves for unit costs0.25,1,2,5. Calibration-OOF constrained optima30%,18%,3%,1%, respectively. At$1 the18%-vs10% paired calibration improvement is979.93 dollars,95% interval[-23.65,2159.13]; it fails the exclusion-of-zero gate. Retain the10% headline. At$2/$5 even their best contact policy fails to cover fixed costs, so no-contact0 net is a real alternative. Grid-endpoint30% is only the optimum within the evaluated range; do not claim a global optimum. Same-data search uncertainty makes all budget intervals exploratory.

A5: Cumulative and1%-incremental model expected versus label-realized curves are generated separately. The gate does not bind because budget cutoff1.71149 exceeds gate1.38889; it does not itself demonstrate tail miscalibration. Calibration highest1% observed/expected churn ratio0.848, but cumulative10% is0.994; diagnose tail locally rather than extrapolating overconfidence to every targeted customer. Final slides use conservative label-realized financial values.

A6: All four available value proxies tested with original-training-fitted nonnegative median/p99 handling: totmrc_Mean,avg3rev,avg6rev,rev_Mean. Recurring charges remain the primary value proxy because no test result selects another proxy and overage/lifetime revenue is not equivalent to recurring contribution.

A7:300 paired resamples shared across all five policies and all prior regimes; sample comparisons run in parallel in the same resamples. Conditional intervals and calibration-propagated intervals are distinguished explicitly.

A8: Reconciliation promotion qualifies because v1 already used Bayes probabilities for financial valuation. Neither an unverified new calibrator nor the18% exploratory budget replaces the simpler verified10% baseline. Freeze specification and test comparisons follow the non-test model headroom work. No model/policy choice uses the test.
