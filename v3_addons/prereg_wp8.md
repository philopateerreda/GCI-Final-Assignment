# WP8 preregistration — one new fixed feature bundle

[E] Authorized by the account holder's explicit **GO v3-model** on 29 October 2026. This file must have a SHA-256 receipt timestamped before the first fit. Existing v2 decisions, receipts and rejected experiments are not reopened. [R] No automatic delivery integration or submission.

## Population, runtime and boundary

- [E] Exactly the original 60,000 training plus 15,000 validation customers, in Record-file order within each partition, training followed by validation. Read the original split manifest. Filter by allowed Customer_ID before converting source feature/label values; no test or original calibration-policy observations enter feature processing, fitting or selection.
- [A] Use the identical Workstream D folds: 2 repetitions, 5 stratified outer folds, shuffle seeds 20261028 + repetition. Each outer training set has 60,000 rows; held-out set 15,000. Sorted 48,000 development / 12,000 internal-calibration indices use seed 20261028 + 1000 + 5*repetition + fold. Three development inner folds use StratifiedKFold(shuffle=True, random_state=20261028).
- [E] Reuse only cached eligible baseline predictions and their signatures; never refit baseline or any rejected challenger. Verify all ten outer held-out IDs, labels, indices and fold-local V against the baseline cache. The 30 inner baseline caches supply paired diagnostic comparisons.
- [R] GO authorizes the existing LightGBM/scikit-learn/threadpoolctl runtime needed for this new model batch; no dependency is installed or upgraded. Use only the shared Python 3.11 interpreter with -B -X utf8, local CPU, sequential fits, six threads maximum. Bootstrap seed = 20261028 + 8. Preserve model/split seeds to pair with Workstream D.
- [R] All computation outputs remain under v3_addons. The separately requested new Obsidian notes and LaTeX presentation will be exported to the specified details/v3 directory by a separate bounded document process; the stable common.py write guard is not weakened.

## Single candidate: wp8_fixed_contrasts

[A] One fixed bundle adds the following 26 operational features to the frozen 87. This is not a rerun of a rejected v2 singleton or nested-selection recipe. There is no search, retuning, early stopping, feature promotion from outer labels, or second batch.

Define S(a,b)=(a-b)/(abs(a)+abs(b)+1); L(a)=log1p(max(a,0)). Missing operands remain missing.

1. For each of mou and rev: S(avg3,avg6), S(unspecified_Mean,avg3), their difference S(Mean,avg3)-S(avg3,avg6), and L(Mean)-2*L(avg3)+L(avg6): 8 features.
2. qty: S(avg3qty,avg6qty), S(avg3qty,avgqty), and L(avg3qty)-L(avg6qty): 3 features.
3. With days=eqpdays if nonnegative, otherwise missing: (30.4375*months-days)/(30.4375*max(months,1)); hnd_price/max(months,1); phones/max(months,1); models/max(phones,1); days/max(models,1): 5 features. The existing baseline equipment-age/tenure ratio is retained, not duplicated.
4. Frozen fit-reference peer ratios: hnd_price / max(training tenure-decile median hnd_price,1); days / max(training tenure-decile median valid days,1); nonnegative totmrc_Mean / max(training avg3mou-decile median nonnegative totmrc_Mean,1): 3 features. Quantile edges, missing grouping-value median, group medians and global fallback medians are learned on the current fit's training rows only and serialized. Scored-batch statistics never enter the reference table.
5. Missingness counts from original allowed numeric operational columns only: total; recent history (change_mou/change_rev/avg3*/avg6*); billing (rev_Mean/totmrc_Mean/da_Mean/ovrrev_Mean/vceovr_Mean/datovr_Mean/roam_Mean/totrev/adjrev/avgrev); care (custcare_Mean/ccrndmou_Mean/cc_mou_Mean); equipment (hnd_price/phones/models/eqpdays, with invalid age missing); tenure/lines (months/uniqsubs/actvsubs); calls/usage (all remaining allowed numeric columns): 7 features. These six families partition the original numeric columns.

[A] avg3/avg6 mean three/six months; the _Mean window is unspecified. The four-window expressions are undated curvature/contrast proxies, not verified time-normalized acceleration or temporal validation. Customer_ID, churn, area, asl_flag, demographic and credit fields are never features. No target encoding. No monotone constraints because no preregistered OOF partial-dependence sign evidence exists. No blending or stacking.

## Fits and calibration

[A] Frozen baseline LightGBM configuration: n_estimators=385, learning_rate=0.03, num_leaves=31, min_child_samples=100, reg_lambda=12, subsample=0.85, subsample_freq=1, colsample_bytree=0.85, n_jobs=6, random_state=20261028, verbosity=-1, deterministic=True, force_col_wise=True. No value weights.

[A] Exactly 50 new classifier fits: three fixed-bundle inner fits per outer fold for non-adaptive diagnostic OOF evidence (30); one development-to-internal-calibration fit (10); one outer-training-to-outer-holdout fit (10). The feature bundle is fixed in advance, so inner diagnostics do not select or change it. This retains the nested partition/calibration design while intentionally avoiding v2 adaptive group screening. Also exactly ten sigmoid calibrator fits on each 12,000 internal-calibration slice; LogisticRegression(C=1000, solver=lbfgs, max_iter=1000, random_state=20261028). Capture convergence warnings.

[A] Follow D's split-calibrate/refit convention: calibrator trained from the 48k development model's held-out predictions is applied to the 60k outer-refit predictions. This fit-size shift remains a limitation. Value fill/cap comes from development rows for internal calibration and outer-training rows for outer evaluation, following the original median/p99 rule. Categories are learned from fitting rows only. Serialize all peer reference tables and ten outer models; prediction caches are signature-bound and resumable without resetting markers.

## Evaluation and intervals

- [E] Primary AUC: raw-score ROC-AUC in each of the ten paired outer held-out folds; report equal-weight mean and difference from cached baseline, not a new final-test AUC.
- [A] Primary policy uses the unchanged numeric tau=1.711493684172072 for BOTH candidate and cached baseline, on prior-shifted calibrated risk times fold-local V. Deployment prior 0.02 is hypothetical; use each internal-calibration sample prior, following D. Outcome weights give each holdout its 2%/98% class mass. Weighted value capture = sum(w*y*V*selected)/sum(w*y*V). Do not recalibrate tau or equalize contact counts on held-out outcomes.
- [E] Report paired fixed-tau value-capture difference and weighted contact shares. Secondary D-style thresholds may be described only as diagnostics, never replacing the fixed-tau gate.
- [A] Four primary calibration differences (candidate minus baseline): weighted Brier and log loss on the SAME baseline-fixed-tau tail, plus weighted Brier and log loss on each model's own fixed-tau tail. No noninferiority margin.
- [A] Save 100,000 hierarchical bootstrap draws: resample two repetitions with replacement, then five paired folds within each sampled repetition with replacement, retaining all paired metrics together. Percentile interval uses linear 2.5/97.5 percentiles. Repeated folds share customers/training rows; this bootstrap is an exploratory variance heuristic, not independently sampled cohort uncertainty.
- [A] Report a liberal IID-fold percentile interval (100,000 draws), hierarchical percentile interval, and Nadeau-Bengio-style corrected-t interval: SE=sqrt((1/10+0.25)*sample_variance), df=4. Conservative interval is the envelope of hierarchical and corrected-t endpoints, fixed before fitting. With only two repetitions, no calibrated coverage or post-selection guarantee is claimed.

## Promotion and kill rule

[R] All ten paired folds must be complete, finite, ID-matched and converged. Mean delta AUC must be >=0.003 and its conservative lower bound strictly >0. Fixed-tau mean weighted value-capture gain and its conservative lower bound must both be >0. All four conservative upper bounds for tail-loss degradation must be <=0. No promotion based on the liberal interval alone.

[R] If any gate fails, retain frozen v2, report every result and failed gate, and stop this model track without a new test look. No further candidate, feature revision or seed sweep is permitted. Completed OOF diagnostics are not a deployable improvement.

[R] Only if all gates pass may one separately safeguarded confirmatory 15k test look be considered, disclosed as the third use. Full model-delivery integration and claim/ledger/hash regeneration require their own explicit brief; this batch never silently edits the frozen submission.

## Verification and publication

[E] New-code tests cover source-row exclusion, exact fold/cache pairing, training-only peer references and batch invariance, deterministic features/bootstrap, missingness families, sigmoid/fixed-tau losses, gate rejection, provenance, and current output hashes. Record preregistration hash, fit count, 150,000 repeated OOF rows / 75,000 unique customers, actual outcomes and complete outside-sandbox directory diff. The previous WP7 receipt and 118-file manifest remain historical and unchanged.
