# Workstream C governance: audited, not a certification

Partition: calibration. Smoke fixture/subsample: False.
Selected input: `D:\progs\IDE\MainProjs\AI\GCI2026\finalA\v2_work\a_selected_calibration.csv`. Policy selections are consumed unchanged from A.
Proxy status: completed_once_original_75k. Ceiling status: D_outputs_available_read_only_unverified.

## Mandatory service-fix floor
Any customer with a verified network fault or billing error receives technical or
billing remediation regardless of plan price, estimated income, credit, housing,
marital status, social-group code, model score or proactive-contact selection.
Risk x Value rations only scarce, discretionary proactive outreach. Failure to
select an account never removes access to support, complaint handling, defect
remediation or consent/opt-out protections. This floor is a mandatory launch
requirement, not an implemented service guarantee in this retrospective dataset.

## C1: frozen, post-hoc subgroup diagnostics
Income, ownrent, marital, creditcd and prizm_social_one are audit-only attributes;
none is an input to the deployed baseline. Income is an estimated ordinal 1-9
code, not income in currency. Literal unknown category codes remain visible;
missing groups and groups absent from the audited partition have explicit rows.
Reference categories come from the original 75k train+validation. Newly observed
categories are flagged rather than pooled or hidden. Counts are never suppressed.

Calibration observed/expected is sum(y)/sum(p_s) in the sample and
sum(weight*y)/sum(weight*p_d) in the declared 2% deployment scenario. Ratios
near one do not prove calibration in every score band. The model classification
threshold is the predeclared sample p_s >= 0.5; its Bayes deployment equivalent is
0.02034789905118441.
Policy capture TPR/FPR, selection, precision and churn-value capture use A's
frozen risk and Bayes lists, not a classifier threshold or a test-derived budget.
TPR/FPR are conditional-class rates and consequently coincide across these two
regimes under A's constant-within-outcome weights; they are not two independent
replications. A's deployment weights are scenario population mass, not observed
customer counts or demographic prevalence estimates. Deployment interpretation
assumes prior/label shift with stable class-conditional feature and group
distributions; this assumption is not verified by reweighting the sample.

There are 300 paired within-subgroup row bootstrap draws, shared across
both policies, the classifier and both prior regimes. Policy differences are
Bayes minus risk on each identical draw. Weights, predictions and selections
remain fixed. CIs are descriptive percentile intervals, conditional on fitted
models, calibration and cutoffs; they exclude refitting/prior uncertainty and
have no multiplicity adjustment. Point estimates and CIs are suppressed for
n<200; TPR/value-capture/calibration also require >=30 observed positives, FPR
requires >=30 negatives, and precision additionally requires adequate selected
rows and both selected classes. Undefined denominators and inadequate finite
bootstrap coverage are suppressed. Raw counts and scenario masses remain shown.
These are audit diagnostics, not Equal Opportunity or other legal compliance
certification. Suppressed rows: 182.

## C2: recoverability, not deployed sensitive-attribute modeling
An explicit --proxy-cv run fits three diagnostic binary models once, using only
the original 60k train plus 15k validation. It never uses calibration or test for
training or selection. The 87 frozen operational features are the only inputs;
category vocabularies are fitted inside each training fold, unknown held-out
categories become native missing values, and numeric missingness is handled
natively. Missing targets are dropped, not imputed. creditcd maps N=0,Y=1;
ownrent maps R=0,O=1. All observed non-test values must be verified against these
codings before any fit. Positive probabilities are read from classes_==1;
AUC is never flipped after seeing a result, including negative results.

Income's original-60k observed median is a fixed non-test reporting reference.
Every income CV fold independently fits its own observed training median and
codes strictly-above-median as high=1, ties/at-or-below as low=0 on both its train
and held-out rows. Fold-local definitions may differ, so pooled income OOF AUC
is descriptive and must be read with all five fold results. Median ties are not
randomly split to manufacture balanced labels. The reference threshold never
uses test and is not substituted for fold-training thresholds.

The model is fixed regularized small-capacity LightGBM, six threads, seed
20261028, five folds, no hyperparameter search or early-stopping selection.
Training class balancing uses training labels only; balanced accuracy uses the
fixed 0.5 positive-probability cutoff. Constant-score baseline ROC-AUC and
balanced accuracy are 0.5. Paired differences from these constants and 300
stratified held-out-row bootstrap CIs are descriptive, not confidence intervals
for independent refitted folds. Operational proxy recoverability would support
only the caveat that excluding demographic columns reduces direct reliance but
does not guarantee statistical independence; no result is asserted before fit.
Cached CV results are reused, never retrained by a test audit or smoke run.

## C3: exact list-composition shifts
c_equity.csv records population, risk, Bayes and Bayes-minus-risk group counts,
shares and within-group selections in both the unweighted sample and A's
weighted deployment scenario. Denominators are explicit; absent/missing groups
stay visible. Income-code and bill distributions include means, inverse-empirical
CDF quantiles and observed/missing masses. The raw totmrc_Mean distribution is
unimputed and uncapped; A's value distribution is separately labeled as the
training-capped/imputed policy value. Weighted masses can be fractional and
are not raw counts. These are exact retrospective descriptions, not causal
retention, saved revenue, model-quality inference or a parity certification.

## C4: diagnostic ceiling boundary
asl_flag (Account Spending Limit) and area (geographic market) remain governance-
sensitive and prohibited in the deployed baseline and C's proxy features.
D owns all sensitive-ceiling fits. C only attaches local, read-only D results
with hashes, separately quarantined in c_summary.json; it neither validates nor
promotes numerical delta-AUC claims automatically. Pending outputs mean pending,
not zero loss. --bridge-only can attach later D tables without rescoring test.
Main must verify D's paired non-test CV comparison, sensitivity coding and CIs
before citing any ceiling claim. No web citations are fetched or fabricated here.

## Partition and claim boundaries
All policy/model choices are frozen outside test. v1 previously evaluated the
locked 15k test; this historical reuse must remain disclosed. This script guards
against repeating a completed or started C test audit and forbids proxy training
or smoke on test. Test is reporting only, not a source of thresholds, encoders,
feature selection, sensitive ceiling fitting or policy promotion. Risk is not
value or responsiveness; retrospective capture is not saved revenue; sample
and deployment priors are labeled separately. Pilot treatment/control evidence,
service-floor operational enforcement and legal review remain prerequisites to
scaling. Root deliverables and v1_frozen are read-only to this workstream.
