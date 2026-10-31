---
title: GCI World 2026 Final Assignment - Frozen v2 Handoff
assignment: Consulting proof of concept for anonymous telecom Company A
account: philopateer
prepared: 2026-10-28
updated: 2026-10-29
deadline: 2026-11-28T11:30:00Z
status: frozen_v2_complete_local_not_submitted
project_root: D:/progs/IDE/MainProjs/AI/GCI2026/finalA
primary_submission_files:
  - philopateer.pdf
  - philopateer.ipynb
  - references.txt
editable_source: philopateer.pptx
selected_model: baseline_lgbm
calibrator: sigmoid
nominal_contact_fraction: 0.1
gate_d_passed: false
protocol_sha256: 700ca4446024aeb1d844e46513c2a4118f698035cd50c4e9a5b0f6f07218c66a
---

# GCI World 2026 — Frozen v2 handoff

**Updated:** 29 October 2026  
**Account / submission basename:** `philopateer`  
**Project:** [D:/progs/IDE/MainProjs/AI/GCI2026/finalA](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA)  
**Deadline:** **28 November 2026, 11:30 UTC**  
**Status:** Completed and verified locally. **NOT submitted.**

This replaces the v1-era handoff. It is intended for a successor model or human with no previous conversation context. It records the completed work, negative experiments, current artifacts, remaining user actions, and boundaries that must survive any subsequent editing.

> [!important] Read this before touching the project
> **Final test AUC is unchanged: 0.6978 → 0.6978; adopted gain 0.0000.** No eligible challenger passed Gate D, so the original LightGBM, sigmoid calibration, and nominal 10% budget remain. The upgrade improved the proposal's evidence and operational design; it did not deliver a higher final AUC or demonstrated incremental profit over v1.
>
> The v2 analytical decisions are frozen. **Do not retrain, rescore rejected challengers, rerun the final evaluation, or reset execution markers to “finish” this completed work.** The 15,000-row test split was already evaluated in v1. v2 reused cached v1 probabilities for one frozen descriptive policy batch, not a new independent model test.

## Contents

| Section | Purpose |
|---|---|
| [[#0. Source-of-truth map]] | Where to confirm current evidence |
| [[#1. Assignment and business decision]] | Requirements, objective, user constraints |
| [[#2. Data and feature boundaries]] | Inputs, definitions, exclusions |
| [[#3. Model development and test history]] | Original model and v2 evaluation design |
| [[#4. Workstream D — every model-headroom result]] | Challengers, ablations, learning curves, limits |
| [[#5. Workstream A — calibration, prior shift, budgets]] | What qualified and what did not |
| [[#6. Final model and policy results]] | Sample vs deployment, with intervals |
| [[#7. Conditional economics]] | Scenario, sensitivity, no-contact alternative |
| [[#8. Workstream B — routing and pilot feasibility]] | Queues, disjoint cells, power, decision rules |
| [[#9. Workstream C — governance and proxy audits]] | What was audited, not certified |
| [[#10. Final presentation and artifacts]] | Current fifteen-slide narrative and file sizes |
| [[#11. QA, hashes, and completed status]] | Verification records and receipt dependencies |
| [[#12. Reproduction and successor safety]] | Notebook dependencies, read-only checks, change controls |
| [[#13. Sources and claim discipline]] | Verified references and prohibited interpretations |
| [[#14. Remaining user actions]] | Manual submission and disclosure |

---

## 0. Source-of-truth map

Read these before making claims or changes:

| Priority | File | Role |
|---:|---|---|
| 1 | [README.docx](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/README.docx) | Authoritative assignment and submission requirements |
| 2 | [qoder_ultimate_enhancement_blueprint.md](file:///D:/progs/obsidian/Obsidian%20Vault/01_Projects/GCI2026/2-%20final%20A/2-second%20iteration/qoder_ultimate_enhancement_blueprint.md) | User-approved enhancement scope, order, constraints and rationale |
| 3 | [FINAL_V2_UPGRADE_REPORT.md](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/FINAL_V2_UPGRADE_REPORT.md) | Guarded final report: retained decisions, results, QA, delivery hashes |
| 4 | [v2_work/final_metrics.json](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/final_metrics.json) | Consolidated frozen v2 numbers, v1 reference, protocol and source fingerprints |
| 5 | [v2_work/d_results/gate_d.csv](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/d_results/gate_d.csv) | Exact eligible-challenger results and rejection reasons |
| 6 | [references.txt](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/references.txt) | D1–D2, S1–S8, M1–M8, assumptions, provenance and AI disclosure |
| 7 | [analysis_outputs/delivery_checks.json](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/analysis_outputs/delivery_checks.json) | Numerical, notebook, export, geometry, source and delivery checks |
| 8 | [v2_work/visual_review.json](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/visual_review.json) | Separate passed visual-review receipt bound to the final render and delivery hashes |
| 9 | [philopateer.ipynb](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/philopateer.ipynb) and [philopateer.pdf](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/philopateer.pdf) | Executed analysis and actual fifteen-page submission story |

**Historical sources are not current status reports.** [analysis_outputs/summary.json](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/analysis_outputs/summary.json) retains baseline context; use the consolidated v2 metrics for new policy/pilot findings. [v2_work/checkpoint2_summary.md](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/checkpoint2_summary.md) is the pre-promotion checkpoint: its “QA still required” and cropping/subsampling wording are historical, not unfinished work. The final slide-5 disclosure is **“No point subsampling; axes crop the display.”**

The delivery receipt's `visual_review` string still says “Pending” because export creates it before inspection. The separate, hash-matched `visual_review.json` records the completed inspection. **Do not edit the delivery receipt just to change that string:** doing so invalidates its hash in the visual receipt.

---

## 1. Assignment and business decision

### Requirements

Company A is an anonymous telecom client with substantial data and limited internal analytics. The assignment requires original EDA, at least one appropriate statistical/ML model, its metric and measured score, external market/comparable-implementation research, multiple visualizations, and an executive-readable quantified business proposal.

| Requirement | Current interpretation |
|---|---|
| Submission identity | `philopateer` |
| Slides | PDF, at most 15 pages including cover and references; enhancement retains exactly 15 |
| Size cap | 10,000,000 bytes |
| Analysis | Executed, reproducible notebook; original analysis, not the supplied tutorial |
| References | Citations on slides matched by the register and Omnicampus References field |
| AI assistance | Permitted; README requests a chat-history URL; disclosure must be truthful |
| Deadline | 28 November 2026, 11:30 UTC; explicit date overrides inconsistent seasonal document labels |

### Chosen business problem

> Given limited discretionary retention contact capacity, which customers should receive opt-in service outreach to put the most recurring contribution within reach — and does the outreach actually work?

The proposal is **value-aware triage plus a randomized service-recovery pilot**, not “predict churn and automatically offer discounts.” Churn probability is multiplied by a capped recurring-charge proxy. Deployment-scenario probabilities are prior-adjusted. There are no treatment labels, so risk cannot identify responsiveness or causal profit.

**Mandatory Service-Fix Floor:** remediate every verified billing/network defect irrespective of bill size, campaign selection, or pilot arm. Ranking allocates scarce proactive discretionary outreach only. No blanket discount, automatic handset subsidy, credit decision, or demographic targeting is proposed.

### User constraints

- All data processing and training must remain on this Windows device, using local CPU/RAM; no cloud, Colab, GPU training, or data upload.
- Use only `C:/Users/FGstore/AppData/Local/Programs/Python/Python311/python.exe`; the `py` launcher defaults to another Python version.
- Keep **SEED=20261028**, **six threads / n_jobs=6**. Approved packages belong in the shared Python 3.11 environment, never a project venv.
- Preserve the five supplied originals, all backups, the original nine notebook code cells, and the immutable 67-file v1 snapshot.
- Enhancement scope was exactly three chart replacements (5, 9, 11), two focused panel replacements (10, 13), and fifteen slides; retain native editable sensitivity cells.
- No submission, portal credential use, or fabricated AI-chat URL.
- For future progress reporting, distinguish **compute activity**, **observed CV deltas**, and **adopted final improvements**. More fits do not imply a better delivered model.

---

## 2. Data and feature boundaries

### Protected inputs

| File | Shape / role |
|---|---|
| [telecom/Client.csv](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/telecom/Client.csv) | 100,000 × 50 |
| [telecom/Record.csv](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/telecom/Record.csv) | 100,000 × 51 |
| README.docx | Assignment brief |
| [ENG_Company _A_ Dataset Overview.docx](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/ENG_Company%20_A_%20Dataset%20Overview.docx) | Feature documentation |
| [tutorial (2).ipynb](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/tutorial%20%282%29.ipynb) | Supplied reference, not original submitted analysis |

Original byte sizes and SHA-256 values are in [analysis_outputs/source_manifest.json](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/analysis_outputs/source_manifest.json). Never modify these originals.

### Integrity and interpretation

- One-to-one join on `Customer_ID`: **100,000 customers, 100 merged columns**, no unmatched customers or duplicate predictor rows.
- Sample churn **49.562%**; this nearly balanced sample is not a live company prevalence estimate.
- Churn label is **days 31–60 after observation**, not cumulative 60-day churn.
- Negative equipment ages: **133**; negative recurring charges: **23**; missing recurring charges: **357**.
- Invalid handset ages are not treated as genuine ages. Negative billing amounts can be credits and are not automatically errors.
- No timestamps, household linkage, sampling-design weights, treatment assignments, actual currency, costs, or margins are supplied. Customer-ID order is not a date or household identifier.
- No `_Range` columns exist. Do not invent range/volatility features. `avg3`/`avg6` have verified three-/six-month meanings; exact `_Mean` windows remain unspecified. `change_mou`/`change_rev` scale is ambiguous; do not relabel them as verified absolute changes or percentage-point effects.

### Retained features and value proxy

The retained model uses **87 operational features**, including four categorical inputs: `new_cell`, `dualband`, `refurb_new`, `hnd_webcap`. ID, target, region, demographic, credit and third-party household-classification fields are excluded as predictive decision inputs. See [analysis_outputs/feature_manifest.json](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/analysis_outputs/feature_manifest.json) for the exact list.

Derived features cover usage/revenue relationships, overage shares, failed-call/care ratios, equipment/tenure and household-line measures. Preprocessing and feature-specific thresholds are fitted only on the appropriate training rows; v2 fold-local encodings do not use outer validation labels.

```text
V = max(totmrc_Mean, 0)
Missing V → original training median 44.99
Upper cap → original training p99 115.5159
```

`V` is a recurring-charge proxy, **not lifetime value or verified profit**. Tenure is available, but future cash flows, margins, response effects and monetary interpretation are not established. Excluding sensitive attributes is not a fairness certificate.

---

## 3. Model development and test history

### v1 development, retained in v2

| Partition | Rows | Original use |
|---|---:|---|
| Training | 60,000 | Candidate fitting and preprocessing |
| Validation | 15,000 | Model selection by ROC-AUC and early stopping |
| Calibration / policy | 10,000 | Sigmoid calibration and contact thresholds |
| Test | 15,000 | Previously evaluated in v1; descriptive v2 reuse disclosed |
| Winner refit | 75,000 | Original training + validation after selection |

The split is stratified random, not forward-in-time or household-disjoint validation.

| v1 candidate | Validation ROC-AUC |
|---|---:|
| LightGBM wider leaves | **0.699931** |
| LightGBM small leaves | 0.698989 |
| XGBoost | 0.698798 |
| CatBoost | 0.698495 |
| Logistic regression | 0.628164 |

Retained LightGBM settings include **385 trees**, 31 leaves, learning rate 0.03, minimum child samples 100, L2 regularization 12, row/column sampling 0.85, deterministic CPU execution and six threads. The separate sigmoid calibration has slope **1.119221** and intercept **0.008001**. Exact baseline selection is recorded in [analysis_outputs/model_selection.json](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/analysis_outputs/model_selection.json).

### v2 separation of selection and final description

- Workstream D uses only the original **75,000 train/validation rows**; zero original calibration-policy or test rows enter that model-headroom comparison.
- Calibrator and budget decisions use the separate original 10,000 calibration-policy rows, not test outcomes.
- The protocol froze at **2026-10-28 17:50:06 UTC** with `baseline_lgbm`, `sigmoid`, and fraction `0.1`.
- Gate D failure means no challenger was refitted/scored on the final test for promotion. Cached v1 probabilities were reused for the frozen final descriptive policy batch.
- Test bootstrap intervals condition on fitted models and selected lists. They do not cover model-selection, retraining, transport, treatment-effect or household-clustering uncertainty.

**Model assessment:** a professionally evaluated proof of concept with **moderate discrimination**, not an exceptional or production-proven model. AUC 0.6978 means approximately 70% correct ordering of random churner/non-churner pairs, not 69.78% classification accuracy. Live usefulness needs contemporary data, temporal validation, live calibration, and randomized evidence.

---

## 4. Workstream D — every model-headroom result

Sources: `gate_d.csv`, [v2_work/d_results/run_spec.json](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/d_results/run_spec.json), and [v2_work/d_results/summary.json](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/d_results/summary.json).

### Design and gates

- **2 × 5 repeated outer CV**, each with 60,000 outer-training / 15,000 outer-held-out rows.
- Inside each outer training set: 48,000 development / 12,000 internal calibration, with **three-fold inner screening**.
- Feature groups are selected within outer training for nested candidates; global group summaries are diagnostic, not a shortcut around nesting.
- Corrected standard error: `sqrt((1/10 + heldout/train) × variance of paired fold differences)`; heldout/train = 0.25; conservative **df=4**.
- The intervals are **pointwise exploratory corrected intervals**, not simultaneous or selection-adjusted guarantees.
- Promotion requires complete paired folds, **mean ΔAUC ≥ 0.001**, **corrected lower bound > 0**, convergence, and corrected upper bounds **≤ 0** for all four weighted top-tail Brier/log-loss degradations (baseline-fixed and own-policy tails).
- The explicitly value-weighted LightGBM additionally needs positive weighted value-capture mean and lower bound. `value_gate=True` for other candidates is not proof of significant business gain.

Work performed: **696 unique fits**, **150,000 repeated out-of-fold rows**, approximately **7,797 seconds of cumulative completed fit time** (~2.2 hours). This is not the whole wall-clock session and is not a performance metric. Prediction-cache file counts are not unique fit counts.

### All eleven eligible challengers — none promoted

All rows below failed the AUC gate and weighted-tail non-degradation gate. The “additional issue” column lists failures beyond those common ones.

| Candidate | Mean ΔAUC vs paired baseline | Corrected 95% interval | Additional issue |
|---|---:|---|---|
| `g1_temporal` | +0.000012 | [−0.001987, +0.002010] | None |
| `g3_billing_gaps` | +0.000117 | [−0.000470, +0.000705] | None |
| `g4_call_care` | +0.000159 | [−0.001072, +0.001391] | None |
| `g5_equipment_cycle` | −0.000132 | [−0.000854, +0.000589] | None |
| `g6_tenure_pricing` | −0.000142 | [−0.001028, +0.000744] | None |
| `nested_blend` | **+0.001085** | **[−0.000032, +0.002203]** | Convergence warning |
| `nested_catboost` | −0.003635 | [−0.006467, −0.000803] | None |
| `nested_lgbm` | +0.000415 | [−0.000360, +0.001191] | None |
| `nested_spline_logistic` | −0.025530 | [−0.030427, −0.020633] | Convergence warning |
| `nested_value_weighted_lgbm` | −0.004487 | [−0.006911, −0.002064] | Value-capture improvement not established |
| `nested_xgboost` | +0.000116 | [−0.001546, +0.001778] | None |

**Result:** Gate D failed; `baseline_lgbm` retained. The blend's mean gain was **0.1085 percentage points on the AUC percentage scale**, not +0.01 AUC. Its interval crosses zero and its other failures remain. Do not add this CV delta to 0.6978 and report a fabricated challenger test AUC.

Feature-group details:
- `g1_temporal`: verified avg3/avg6/lifetime relationships; its name does not imply temporal validation or known `_Mean` windows.
- `g2_range`: **unavailable, not tested**, because the columns do not exist.
- `g3`: billing/usage adjustment gaps; `g4`: call completion/care relationships.
- `g5`: equipment/tenure and fold-local handset-price encoding; `g6`: training-local tenure-adjusted pricing.
- [feature_group_decisions.csv](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/d_results/feature_group_decisions.csv) marks g1/g3/g4 `keep=True` for positive diagnostic means. **That is not final promotion**; the deployed feature set remains the baseline.

### Feature-removal experiments

[ablation_summary.csv](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/d_results/ablation_summary.csv) measures loss/gain after removing each baseline family. These are diagnostic ablations, not additional promoted candidates.

| Removed family | Mean ΔAUC | Corrected 95% interval |
|---|---:|---|
| Recent history | −0.018558 | [−0.022295, −0.014821] |
| Equipment | −0.014335 | [−0.017976, −0.010694] |
| Tenure / household-line measures | −0.008461 | [−0.010432, −0.006489] |
| Billing / revenue | −0.004847 | [−0.006103, −0.003591] |
| Calls / network | −0.003045 | [−0.004476, −0.001614] |
| Care | −0.000678 | [−0.001386, +0.000030] |
| Usage volume | +0.000215 | [−0.000623, +0.001053] |

Recent-history and equipment information clearly mattered within this design. The small gain from removing usage volume was inconclusive. These are predictive associations, not causal effects of changing customer behavior or replacing equipment.

### Learning curves and baseline variability

| Training rows | Mean outer-held-out AUC |
|---:|---:|
| 10,000 | 0.671175 |
| 25,000 | 0.687104 |
| 50,000 | 0.694511 |
| 60,000 | 0.696037 |

Source: [learning_curve_summary.csv](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/d_results/learning_curve_summary.csv). The 75,000-row point is **training-only**, not a held-out AUC. More training data helped within the evaluated range; extrapolation beyond it is not established.

[noise_floor.csv](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/d_results/noise_floor.csv) reports baseline fold AUC SD **0.002528**. It is a variability diagnostic, not a substitute for paired challenger comparisons or proof that all smaller improvements are meaningless.

A separate `diagnostic_ceiling_asl_area` experiment used quarantined `asl_flag`/`area` inputs. It is ineligible for deployment; the C bridge labels its raw D outputs **read-only/unverified**, with no approved numerical claims. Do not treat it as a deployable improvement, proxy-audit result, or an established information ceiling.

**Interpretation:** several observed CV gains were positive, but none met all predeclared adoption requirements. Failure to promote does not prove that the dataset or model has reached a universal AUC ceiling.

---

## 5. Workstream A — calibration, prior shift, budgets

### What Gate A actually established

Gate A qualifies through **prior-regime reconciliation**: v1 already used deployment-consistent risk × value in its financial scenario. v2 corrected the interpretation and presentation of sample vs deployment evidence; it did not create a new financial gain over the same v1 rule.

Let `p_s` denote sample-calibrated churn risk, `pi_s` the sample prior, and `pi_d` the assumed deployment prior:

```text
p_d = expit(logit(p_s) + logit(pi_d) − logit(pi_s))
Sample benchmark score = p_s × V
Deployment scenario score = p_d × V

For an evaluated partition of N rows, n1 churners and n0 non-churners:
w(y=1) = 100000 × pi_d / n1
w(y=0) = 100000 × (1 − pi_d) / n0
```

Probabilities are clipped as implemented before logit evaluation. Prior adjustment preserves pure-risk ordering but need not preserve risk × value ordering. Outcome-stratified weights are **retrospective evaluation weights**, not inputs requiring future labels when live customers are ranked.

The assumed 2% prior, within-class representativeness and stable class-conditional distributions remain unverified. External carrier churn does not validate them.

### Calibration candidates — sigmoid retained

Five-fold comparisons used only the calibration-policy partition. In this table, **improvement = sigmoid log loss − candidate log loss**, so negative means worse, not better.

| Method | OOF log loss | Improvement vs sigmoid | 95% interval for improvement | Decision |
|---|---:|---:|---|---|
| Sigmoid | 0.622644 | 0 | Reference | Retain |
| Beta | 0.622797 | −0.0001529 | [−0.0003457, +0.0000509] | Not promoted |
| Isotonic | 0.626225 | −0.0035814 | [−0.0074541, −0.0008886] | Not promoted |

Isotonic's better tail Brier alone was insufficient: it worsened overall OOF log loss. These calibration tests did not produce a new final-model AUC gain.

### Budget search — nominal 10% retained

| Assumed contact cost | Calibration-selected diagnostic fraction | Calibration OOF net | Headline promotion |
|---:|---:|---:|---|
| $0.25 | 30% | $25,920.97 | No |
| $1 | 18% | $6,009.39 | No |
| $2 | 3% | −$1,891.44 | No; no-contact is better under these assumptions |
| $5 | 1% | −$5,732.58 | No; no-contact is better under these assumptions |

Conditional intervals omit the uncertainty from searching over fractions on the same calibration support. Grid endpoints are constrained optima, not universal campaign sizes. Even at $1/contact, the paired calibration gain over 10% had an interval crossing zero. **No optimized budget was promoted.** Chart dots are calibration-selected diagnostics, not test-selected optima.

At the assumed 2% prior, the frozen risk × value threshold is **1.711493684172072**; the risk-only threshold is **0.036833373400463214**. The marginal positive-contribution gate is non-binding in the base case; that does not prove calibration quality or guarantee positive total profit after fixed costs.

---

## 6. Final model and policy results

### Retained classifier

| Metric | Calibrated LightGBM test result |
|---|---:|
| ROC-AUC | **0.6978109022** |
| 95% AUC interval | **[0.6899029819, 0.7054949137]** |
| Average precision | 0.6882568171 |
| Accuracy at 0.5 | 0.640200 |
| Precision at 0.5 | 0.635758 |
| Recall at 0.5 | 0.641829 |
| Log loss | 0.627897 |
| Brier score | 0.219463 |

The logistic-regression test AUC was **0.619329**; constant risk gives 0.5. These are sample metrics, not deployment precision or live accuracy. The original AUC interval used 300 bootstrap replicates and is retained with the original fitted classifier.

### Unweighted sample benchmark — equal 1,500-row lists

| Policy | Churned recurring value captured | Churn precision |
|---|---:|---:|
| Risk only | 14.62% | 80.47% |
| Recurring value only | 17.57% | 42.93% |
| Risk × recurring value | **20.83%** | **63.13%** |
| Old-handset rule (v1 reference) | 9.56% | 59.73% |

Value-aware vs risk-only: **+6.21 percentage points**, **+42.44% relative**. Same point estimate as v1.

| Interval version | 95% interval for sample relative gain |
|---|---|
| Original v1 bootstrap | +36.36% to +48.99% |
| Frozen v2 descriptive batch | **+35.66% to +48.56%** |

The different interval endpoints do not represent improved predictions. Do not silently combine one version's interval with claims about another evaluation protocol.

### Hypothetical 2% deployment — weighted frozen thresholds

| Policy | Actual test rows selected | Weighted contacts per 100,000 | Achieved fraction | Value recall |
|---|---:|---:|---:|---:|
| Risk only | 2,891 | 10,431.26 | 10.431% | 25.58% |
| Recurring value only | 1,295 | 10,014.63 | 10.015% | 15.03% |
| Bayes / prior-adjusted risk × value | **2,505** | **9,984.92** | **9.985%** | **29.51%** |

The deployment relative value-recall gain is **+15.37%**, descriptive 95% interval **[+11.26%, +19.67%]**. Both list thresholds target nominal 10% on calibration data; their achieved test masses are not exactly equal. Do not relabel these as exactly equal-sized deployment lists.

**Critical distinction:** +42.4% is the unweighted sample statistic; +15.4% is the weighted hypothetical deployment comparison. Neither is causal retention lift, neither is a new AUC result, and the latter is not a gain over the already-consistent v1 financial policy.

---

## 7. Conditional economics

Base assumptions: **100,000 hypothetical customers; 2% future-window churn; 20% prevention of would-be churners; six retained months; 60% incremental margin; $1/contact; $5,000 fixed cost; USD-equivalent interpretation.** None of these financial or treatment assumptions is a verified Company A operating fact.

```text
Gross contribution = weighted churned recurring value contacted
                     × prevention × retained months × margin
Net contribution   = gross − weighted contacts × contact cost − fixed cost
```

| Base value-aware scenario | Amount |
|---|---:|
| Weighted contacts | 9,984.92 |
| Weighted would-be churners contacted | 476.40 |
| Assumed prevented cancellations | 95.28 |
| Assumed retained revenue | $31,220.01 |
| Gross contribution | $18,732.00 |
| Variable contact cost | $9,984.92 |
| Fixed cost | $5,000.00 |
| **Conditional net** | **$3,747.08** |
| Descriptive conditional net 95% interval | **[$2,761.37, $4,660.64]** |
| All-in break-even contact cost | **$1.3753** (~$1.38) |
| Break-even prevention | **15.9993%** (~16.0%) |

**The net point estimate is unchanged from v1.** Risk-only net is $804.57; value-only net is −$5,477.77. These comparisons inherit all assumptions and their unequal achieved frozen-threshold contact masses.

### Sensitivity: net contribution in $000

| Prevention | $1/contact | $2/contact | $5/contact |
|---:|---:|---:|---:|
| 10% | −5.6 | −15.6 | −45.6 |
| 20% | **+3.7** | −6.2 | −36.2 |
| 30% | +13.1 | +3.1 | −26.8 |

At 20% prevention and $1/contact, prior stress gives approximately **−$5.6k at 1%**, **+$3.7k at 2%**, and **+$30.7k at 5%**.

**No contact / no launch = zero net.** An empty list after launching can still incur fixed startup cost; it is not the same decision. A lower loss than a 10% campaign does not justify launching when no contact is better.

The positive base-case interval is a conditional row-resampling interval. It excludes uncertainty in the treatment effect, real margin/costs, currency, future population, household clustering and policy selection. It is not proof of profitable outreach, a forecast, or annualized savings.

---

## 8. Workstream B — routing and pilot feasibility

Source: [v2_work/b_design.json](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/b_design.json) and the `pilot_calibration` / `pilot_test` sections of final metrics. Planning decisions use calibration evidence; final test summaries are descriptive, not new design decisions.

### Four exclusive operational queues

Precedence is **billing → network → handset → digital residual**. These sum to the 2,505 raw test rows selected by the frozen deployment value-aware policy.

| Queue | Raw rows | Weighted mean bill, dataset units | Share of selected at-risk value |
|---|---:|---:|---:|
| Billing check | 582 | 68.7 | 23.4% |
| Network check | 266 | 59.7 | 10.4% |
| Handset check | 791 | 62.9 | 30.7% |
| Digital-only residual | 866 | 64.7 | 35.5% |

The digital residual includes remaining cases, not only proven low-usage customers. Missing diagnostics are not zeros or verified faults. Routing flags are operational hypotheses, not established churn causes or treatment effects. The **Service-Fix Floor remains mandatory for everyone**.

### Disjoint policy cells

| Cell | Meaning | Raw test rows |
|---|---|---:|
| `both` | Selected by both risk and value-aware policies | 1,774 |
| `rv_only` | Value-aware additions | 731 |
| `risk_only` | Risk-only selections dropped by value-aware | 1,117 |
| `exploration` | Below both cutoffs | 11,378 |

Stage 1 core is `both + rv_only`; value-aware additions must not be enrolled twice. Stage 2 separately samples `risk_only` and below-union exploration.

Only the common **`both`** region cancels in a Bayes-minus-risk policy-value comparison. The contrast is deployment-mass-weighted incremental contribution in additions minus that in drops. **Do not cancel the whole Stage 1 core**, which also contains additions.

### Staged enrollment and cost envelope

| Stage | Enrollment | Assumed incremental cost |
|---|---|---:|
| Stage 1 core | **7,872 per arm; 15,744 unique linked accounts** | **$12,872** |
| Stage 2 risk-only learning | 2,000 per arm | Included below |
| Stage 2 below-cutoff exploration | 1,000 per arm | **+$3,000** total Stage 2 |
| Combined staged plan | 21,744 enrolled accounts | **$15,872** contact/startup envelope |

Costs assume $1 per treated contact, zero incremental control contact cost, $5,000 Stage 1 startup and no additional Stage 2 fixed charge. **They are not fully quoted launch costs.** Household linkage, consent, engineering, follow-up, legal and measurement costs must be priced.

A single roughly 10,000-account top list in the 100,000-account financial scenario cannot provide 15,744 unique core accounts. Enrollment requires a larger eligible portfolio or successive cohorts; repeated appearances of the same account do not create independent new participants.

### Power findings — do not suppress the negative result

The retained v1 planning reference assumed 4.7711% control churn, 3.8169% treated churn, two-sided alpha 0.05, 80% power and a 10% follow-up allowance: 7,084 complete / **7,872 enrolled per arm**.

The v2 calibration-planning simulation used 400 replicates per grid point, with enrolled sizes from 1,000 through 160,000 per arm. The selected size is the first preregistered grid point achieving simulated power ≥80%, not an exact analytically determined minimum.

| Outcome | Calibration-selected simulation requirement |
|---|---|
| Binary churn | **7,872/arm** |
| Covariate-adjusted contribution | **80,000/arm** |
| Unadjusted contribution | **80% power not established through 160,000/arm** |

These are **cross-sectional, independent-account planning proxies**, not observed longitudinal pre/post pairs, measured CUPED variance reduction, household-clustered power, or validated causal effects. Stage 2 allocations are learning allocations, **not powered policy comparisons**. The small contact/startup envelope is not profit-powered rollout proof.

### Randomization, logging and rules

- Acquire household/account linkage; keep each linked cluster in one arm. `Customer_ID` is not established as household-disjoint.
- Stratify by disjoint cell and pre-treatment risk-value band. Among enrolled accounts, treatment probability is 0.5.
- Log eligibility/consent, linkage, enrollment probability, treatment probability, assignment/contact, pre-period covariates, contribution/costs and harm.
- Use joint inclusion-and-assignment propensities for policy evaluation. Claims do not automatically extend to unconsented/unobserved accounts; clustering and nonresponse require treatment.
- Primary decision outcome: realized incremental contribution after all costs. Monitor early churn, days 31–60 churn, opt-outs, complaints and six-month contribution.
- **Scale:** final cluster-robust 95% lower bound on incremental contribution >0 and no guardrail breach.
- **Extend:** interval overlaps zero with positive upper bound, no harm, and a prospectively approved maximum sample/budget extension.
- **Stop:** upper bound ≤0, infeasible fully loaded costs, or customer-harm guardrail.
- Proposed low-usage/zero-overage/zero-care harm stratum: one-sided Fisher checks at 50% and 100% information, p≤0.005 per planned look, familywise bound ≤0.01 for that stratum. Serious consent violations/complaints trigger immediate escalation regardless of significance. Live household clustering/sequential design still needs validation.

The exact harm stratum is a preregistered operational hypothesis, not a subgroup effect verified in the cited plan-recommendation experiment.

---

## 9. Workstream C — governance and proxy audits

The completed non-smoke audit includes **244 equity-table rows**, visible selection/population denominators, and both unweighted sample and deployment-weighted regimes. It distinguishes capped/imputed policy value from raw source billing. Income is an ordinal **1–9 code**, not currency.

Five-fold proxy prediction uses the original 75,000 non-test operational-feature rows, with missing targets excluded and labels explicitly coded. It tests whether excluded information remains recoverable from retained predictors.

| Excluded target | Pooled OOF AUC | Descriptive 95% interval |
|---|---:|---|
| Credit-card present (`creditcd`) | **0.6569** | [0.6525, 0.6613] |
| Home owner (`ownrent`) | **0.6070** | [0.5928, 0.6204] |
| High income code (`income_high`) | **0.6273** | [0.6227, 0.6316] |

Source: [v2_work/c_proxy_cv.csv](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/c_proxy_cv.csv), 18 rows covering folds and pooled summaries. The high-income threshold is learned from each fold's training labels; pooled OOF interpretation retains that caveat. Missingness and severe target imbalance also matter.

**Conclusion:** excluding these columns does not erase proxy information. This is an audit, not proof of demographic parity, equalized odds, legality, or fair treatment outcomes. Do not import quarantined `asl_flag`/`area` diagnostic models into the deployable feature set.

---

## 10. Final presentation and artifacts

### Current files

| File | Current verified state |
|---|---|
| philopateer.pdf | **15 pages; 846,608 bytes** |
| [philopateer.pptx](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/philopateer.pptx) | **15 slides; 1,310,666 bytes**; editable supporting source |
| philopateer.ipynb | **52 cells total; 25 executed code cells; zero errors; 1,857,125 bytes** |
| references.txt | **18,843 bytes**; expanded method/evidence register and disclosure |
| [FINAL_ASSESSMENT_READING_NOTE.md](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/FINAL_ASSESSMENT_READING_NOTE.md) | Concise Obsidian reading note; current v2 interpretation |
| FINAL_ASSESSMENT_HANDOFF.md | This detailed successor document; not a submission file |

The original nine code cells are preserved. The notebook is larger because it now contains the v2 implementation and outputs; “9 executed code cells” is obsolete as a final-artifact count.

### Fifteen-slide narrative

| Slide | Frozen content / change |
|---:|---|
| 1 | Contribution-focused cover: “Retain contribution. Not just customers.” |
| 2 | Separate +42.4% sample result from conditional $3.7k; risk → value-aware → causal-profit maturity ladder; pilot first |
| 3 | Verified operator context with separate T-Mobile [S1] and AT&T [S2] definitions; intervention-specific backfire warning |
| 4 | 100,000 customers, 49.56% sample churn, days 31–60 label; sample/production boundary |
| 5 | **Replaced chart:** prior-shifted risk/value scatter, disjoint cells and calibration cutoff; no point subsampling, display axes cropped |
| 6 | Original operational-pattern chart; associations and diagnostic questions, not causal remedies |
| 7 | Original splits, disclosed test reuse, proxy audit and actual Gate D failure; no information-ceiling claim |
| 8 | Retained v1 ROC/calibration chart explicitly labeled as reference; AUC 0.6978 and retained-model status |
| 9 | **Replaced chart:** deployment value recall 29.5% vs risk 25.6%, +15.4%; separately labeled sample benchmark |
| 10 | **Replaced panel:** four exclusive queues, raw counts/weighted summaries and mandatory Service-Fix Floor |
| 11 | **Replaced chart:** cost/fraction curves, diagnostic calibration-selected dots, nominal-10% conditional $3.7k; no promoted optimal budget |
| 12 | Native editable 3×3 sensitivity cells, break-even values, prior stress and zero-contact option |
| 13 | **Replaced panel:** disjoint staged enrollment, linked-account randomization, logged propensities, cost/power/capacity limits, decision/harm rules |
| 14 | Market/vendor references; unverified T-Mobile filing day removed |
| 15 | Methods/data references including M5–M8 and truthful Qoder-assistance disclosure |

Exactly **three chart replacements and two focused panel replacements**; fifteen slides remain. Navy/teal/amber/slate/pale and Aptos styling are retained. Text/shapes and sensitivity cells are editable; chart PNGs are raster images, **not native editable chart data**.

No live scoring API, deployed system, uplift model, external-data enrichment, or production contact campaign was created.

---

## 11. QA, hashes, and completed status

### Completed checks

- Notebook: **25 executed code cells, zero errors**, pipeline agreement, original nine preserved.
- PDF/PPTX: **15 pages/slides**, PDF within the 10,000,000-byte cap; local PowerPoint export successful.
- Geometry: **zero Office issues** and no out-of-bounds shapes.
- Claims: **278 ledger rows**, native/chart numeric coverage, exact source/regime bindings, independently checked new plotted coordinates, matching slide citations and source hashes.
- Visual review: all **15 final 1600×900 slide renders** plus contact sheet inspected; zero recorded clipped text or unintended overlaps. The final receipt is hash-bound to those exact images and delivery receipt.
- Immutable v1 snapshot: **67 files verified byte-for-byte**; original supplied sources unchanged.
- The earlier analytical test run passed **57 tests**. That run preceded the final slide-5 footer correction; the final export/claims/geometry/hash-bound visual QA covered the later delivered artifacts. This documentation update does not claim a new test-suite run.

Current geometry receipt: [v2_work/office_geometry_check.json](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/office_geometry_check.json). Final contact sheet: [analysis_outputs/deck_contact_sheet.png](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/analysis_outputs/deck_contact_sheet.png). [analysis_outputs/slide_renders](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/analysis_outputs/slide_renders) contains the full-size exports.

### Current delivery SHA-256

These values were rechecked against the actual files for the 29 October documentation update. Updating these two explanatory documents does not change the four delivery files.

| File | SHA-256 |
|---|---|
| philopateer.pdf | `a51d2c0ff8aa6ebb0f679e680d6424b01cd7b95b9a0d23ae7a2eecc56de210ea` |
| philopateer.pptx | `a50a66fd77d062bdc45aeefb00ce8652b20b952de06dcb27e8ab4f15c37e46bc` |
| philopateer.ipynb | `aaa170b19923c087f9b38f85b546626b7465a3d17f5ae7037812c6aed5736b35` |
| references.txt | `b12fb18aafc83e2d599e15d04c689ee5cd85c10082c1761ab0c6f1d01606d361` |

| Other receipt / artifact | SHA-256 |
|---|---|
| Frozen protocol | `700ca4446024aeb1d844e46513c2a4118f698035cd50c4e9a5b0f6f07218c66a` |
| Final-batch completion | `80bc9bfd1ff2b4ca559e5cc4ba3b85e27b5d590413ad3fbe45a44d62a633a9dc` |
| Cached v1 held-out predictions | `c525318b3e589a60054ad6d33eeefe9456c5c9c874e7565efc5495672b170d8d` |
| Office geometry receipt | `31569f42fac021a6790e23ff56092b2913680d33cbb701ec407de1e61bd938a7` |
| Claims ledger | `b4dce03b43f6bd1b9ef3142759e0cb88682527af2f9f8824902521d88729c5b4` |

Use the machine receipts for all individual render hashes. A successful export or matching file hash does not by itself establish visual quality; the actual inspection is recorded separately.

---

## 12. Reproduction and successor safety

### Environment and important paths

Windows 10, i7-8850H, 32 GiB RAM, Python **3.11.9**, local CPU only, six threads, seed 20261028. Package versions and dependencies are recorded in [analysis_outputs/environment.json](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/analysis_outputs/environment.json), the D run specification, and [requirements-python311.txt](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/requirements-python311.txt). The workspace is **not a git repository**.

| Path | Purpose / caution |
|---|---|
| [analysis_pipeline.py](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/analysis_pipeline.py) | Canonical v1+v2 code represented in the notebook; running it is not read-only |
| [build_notebook.py](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/build_notebook.py) | Builds/optionally executes the canonical notebook; writes artifacts |
| [v2_work/build_v2_canonical.py](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/build_v2_canonical.py) | Assembles preserved v1 code and embedded v2 modules |
| [v2_work/run_frozen_batch.py](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/run_frozen_batch.py) | Non-test/final-batch orchestration and fingerprint verifiers; use verifier functions, not execution entrypoints, for checking |
| [v2_work/final_protocol.py](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/final_protocol.py) | Frozen specification and verification; do not replace/reset it |
| [v2_work/final_metrics.py](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/final_metrics.py) | Recomputes/writes consolidated summaries from existing evidence |
| [v2_work/generate_visuals.py](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/generate_visuals.py) | Regenerates chart assets; not read-only |
| [v2_work/build_claim_ledger.py](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/build_claim_ledger.py) | Claims ledger assembly |
| [v2_work/claim_checks.py](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/claim_checks.py) | Claims verification also invokes chart-evidence writers; not strictly read-only |
| [export_and_verify.py](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/export_and_verify.py) | PowerPoint COM export; rewrites PDF, renders, text, contact sheet and delivery receipt |
| [v2_work/prepare_checkpoint2.py](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/prepare_checkpoint2.py) | Default mode regenerates checkpoint/visuals; `--final` validates final dependencies and writes the final report |
| [v1_frozen/sha256_manifest.json](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v1_frozen/sha256_manifest.json) | Authoritative 67-file immutable snapshot manifest |
| [restore_v1.py](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/restore_v1.py) | `--verify-only` checks snapshot; default restoration overwrites root files, including these assessment documents |

Other v2 artifacts include calibration specifications, selected calibration/test policy rows, B planning/test summaries, C audit tables, D paired folds/ablations/learning curves, protocol/completion receipts and caches. Preserve them: the delivered notebook is not the entire provenance bundle. Keep [analysis_outputs/notebook_backups](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/analysis_outputs/notebook_backups) and the immutable snapshot; do not treat cache cleanup as harmless.

### Notebook portability — correct the old handoff's claim

The notebook embeds analytical module code; it does not need to import the root pipeline file at execution time. Its 25 code cells comprise nine preserved v1 cells, a bootstrap, eleven embedded-module cells, baseline-cache setup, non-test orchestration, final-batch orchestration, and results publication.

**Embedded code does not mean standalone reproduction from just the two CSVs.** Frozen replay depends on local source/baseline artifacts and completion records. The five protected originals and source manifest participate in provenance checks. In particular, fresh baseline setup expects `analysis_outputs/source_manifest.json`, which the original nine cells do not create. A newly constructed minimal baseline cache is not the restorable 67-file v1 snapshot. Keep the full local project when handing off reproducibility; do not claim that notebook + two CSVs alone reproduces the entire frozen QA chain.

**Do not use “Run All” as a harmless verification step.** The preserved v1 cells retrain/refit and predict; later cells can republish metrics and regenerate charts. Frozen orchestration can reuse verified results, but not every notebook cell is cache-only. Exact visual reproduction also needs local fonts; PDF export requires installed PowerPoint/COM.

### Read-only integrity verification

These commands validate the snapshot and completed analytical batch without calling training or evaluation entrypoints. `-B` avoids Python bytecode writes. They are not a replacement for all delivery/visual checks.

```bash
PY="C:/Users/FGstore/AppData/Local/Programs/Python/Python311/python.exe"
R="D:/progs/IDE/MainProjs/AI/GCI2026/finalA"
"$PY" -B "$R/restore_v1.py" --verify-only
"$PY" -B -X utf8 -c "import sys; sys.path.insert(0,sys.argv[1]); from run_frozen_batch import verify_completed; verify_completed()" "$R/v2_work"
```

Separately hash the four delivery files and compare with `delivery_checks.json`; verify the visual receipt's delivery, contact-sheet and all fifteen render hashes. Never clear started/completed markers or rewrite expected hashes to make a failed verifier pass.

Tests are not automatically read-only: integration-test setup assembles canonical files. Do not rerun them or builders for a documentation-only update. The 29 October update changed only the two assessment documents, not models, protocol, scientific outputs or submission artifacts.

### If a later change is requested

1. **Documentation-only correction:** update the explanatory documents from verified frozen evidence; leave analytical and delivery artifacts untouched.
2. **Narrative/deck change:** retain claim boundaries and the fifteen-slide scope. Read the current deck through the Presentations skill/Office tools; do not hand-edit PPTX XML. Changing a chart means regenerating its source image and updating bindings, not claiming native chart editability.
3. **Scientific change:** requires explicit new scope/version, a defensible non-test selection design, and disclosure of additional test reuse. Do not silently reopen the frozen v2 comparison or optimize on its test outcomes.
4. **Full delivery reverification after an authorized artifact change:** synchronize canonical notebook and source summaries/charts; update native/chart claim bindings and citations; edit/save the deck; obtain geometry checks tied to the saved PPTX hash; export; inspect all fifteen final renders and contact sheet; create a new honest hash-bound visual receipt; only then regenerate the guarded final report and refresh this handoff's sizes/hashes.

Dependency chain: **canonical code/results → chart/claim/deck agreement → saved deck + geometry → export/delivery receipt → actual visual inspection/receipt → final report**. Re-export changes the receipt/render hashes; an earlier visual approval cannot simply be carried forward.

If a future QA failure cannot be resolved cleanly, the blueprint provides v1 rollback. That is **not needed now**. Obtain appropriate approval and preserve the current v2 state first: default restore overwrites manifest-listed root files, including these two documents, while leaving unrelated v2 files. Its temporary recovery mechanism is not a durable v2 backup or a guarantee against every interrupted restore.

---

## 13. Sources and claim discipline

The complete URLs, publication details and verification limits live in `references.txt`; use that register rather than reintroducing superseded dates or unsupported claims.

| IDs | Evidence and permitted use |
|---|---|
| D1–D2 | Supplied data, assignment and feature definitions; tutorial is context, not measured original work |
| S1 | T-Mobile FY2025: 0.93% postpaid phone churn, 2.72% prepaid, $50.37 phone ARPU, $148.97 account ARPA; different populations/units; no unverified filing day |
| S2 | AT&T FY2025 postpaid phone churn 0.90%; beginning-of-month subscriber denominator differs from T-Mobile; financing maturity is not handset age |
| S3 | Verizon management-reported 30% retention promotional-cost improvement; aggregate context, not causal savings imported into Company A |
| S4 | Ascarza et al. (2016): specific randomized plan-recommendation intervention, 6% control vs 10% treated churn over three months; not proof that all service contact harms customers |
| S5–S6 | Risk vs responsiveness and incremental-profit targeting; motivate causal pilot and no-contact alternative |
| S7–S8 | Vodafone Turkey/UK vendor/operator workflow precedents; feasibility, not transferable causal effects or delivery costs |
| M1–M4 | scikit-learn, LightGBM, XGBoost and CatBoost methods |
| M5 | Saerens et al. prior adjustment; verified metadata/abstract only, not a falsely claimed inspected full-text equation |
| M6 | Elkan cost-sensitive learning and known-prior correction; conditional mathematics, not evidence of intervention effectiveness |
| M7 | CUPED pre-experiment adjustment rationale; no imported Bing variance reduction or fabricated longitudinal Company A data |
| M8 | Neslin et al. Cell2Cell tournament context; **no verified universal 0.684 AUC ceiling or matched performance benchmark** |

External evidence was accessed/verified during the 28 October work. The 29 October documentation update did not perform a new web-verification pass.

### Non-negotiable claim boundaries

| Avoid | Say instead |
|---|---|
| “v2 improved AUC” | Final AUC unchanged; small CV gains did not pass promotion gates |
| “No experiment improved anything” | Some CV means were positive; none qualified for final-model adoption |
| “The model reached the data ceiling” | These specified experiments failed; an information ceiling is not established |
| “AUC means 69.78% accuracy” | AUC describes pairwise ranking; threshold-0.5 sample accuracy is 64.02% |
| “+42.4% retention lift” | Sample relative value-capture gain, not causal retention lift |
| “+15.4% is new profit over v1” | Deployment-scenario value-recall comparison vs risk, with v1 already using the same financial rule |
| “The model saves $3.7k” | Conditional scenario net, unchanged from v1; no measured treatment savings |
| “A fresh untouched test proves v2” | Previously evaluated v1 split; frozen v2 descriptive reuse and conditional intervals |
| “$13k buys proof of positive profit” | Contact/startup learning envelope; profit-power, capacity and full costs remain unresolved |
| “Sensitive columns are excluded, so it is fair” | Proxy recoverability and subgroup differences were audited; fairness not certified |
| “The residual queue is low-usage” | It contains low-usage and other residual cases; flags require diagnosis |
| “A rejected calibrator had negative log loss change, so it helped” | Reported improvement is baseline minus candidate loss; negative means worse |

Additional limits: no temporal validation, household linkage or randomized treatment data; unverified pure prior shift; unknown company currency/margins/costs; recurring-charge proxy is not lifetime value; model comparison margins are small; chart images are raster. None should be hidden to make the presentation sound stronger.

---

## 14. Remaining user actions

No assigned analytical, authoring or QA task remains. Negative experimental results, production-validation needs, and pilot feasibility requirements are disclosed findings, not unfinished model-promotion work.

1. Review the frozen PDF, executed notebook, and references as account holder `philopateer`.
2. Use the assignment's [Omnicampus page](https://edu.omnicamp.us/en/courses/170/reports/125/) and upload `philopateer.pdf`, `philopateer.ipynb`, and the required references; populate the References field from the matching register. The PPTX is supporting editable material, not a substitute for the PDF.
3. Handle the README's AI chat-history URL request truthfully. Qoder assistance is already disclosed. Add a real shareable link only if available; otherwise state that no public link is available and resolve any portal requirement with course staff. **Never fabricate a URL.** Any edit to the delivered references file changes its hash and requires corresponding delivery QA updates.
4. Confirm filenames and the final upload, then submit before **28 November 2026, 11:30 UTC**. No automatic submission has been made.

**Final verdict:** a credible, professionally evaluated consulting proof of concept with moderate predictive performance and a more defensible v2 business/pilot package. **Not a higher-AUC v2 classifier, a causal savings estimate, or a production-ready retention system.**
