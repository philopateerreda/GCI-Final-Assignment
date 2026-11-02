---
title: Company A - Final v2 Reading Note
subtitle: GCI World 2026 - results, experiments, and the honest conclusion
account: philopateer
updated: 2026-10-29
status: frozen_v2_complete_local_not_submitted
cssclasses: wide-page
tags:
  - gci2026
  - telecom
  - churn
  - retention
  - obsidian
---

# Company A — What we achieved
*Final v2 · updated 29 October 2026 · reading note for `philopateer`*

> [!quote] The thesis
> **Retain contribution, not just customers.** Use churn risk and recurring value to prioritize discretionary service outreach — then test whether that outreach actually helps.

> [!abstract] The honest headline
> - **Final model AUC: 0.6978 → 0.6978. Adopted improvement: 0.0000.**
> - Small cross-validation gains appeared, but **none of the 11 eligible challengers passed all promotion gates**.
> - The upgrade improved the evidence, operational safeguards, pilot design, and presentation — **not the final classifier's predictive performance**.
> - The result is a **professionally evaluated prototype with moderate predictive power**, not a production-proven retention system.
> - Everything is complete locally. **Nothing has been submitted.**

## Contents

| Section | Question |
|---|---|
| [[#1. The business problem]] | What are we trying to solve? |
| [[#2. Is the model good?]] | What does 0.6978 actually mean? |
| [[#3. What the new experiments found]] | Why did the final AUC stay unchanged? |
| [[#4. Two value-capture results — not one]] | What do +42.4% and +15.4% mean? |
| [[#5. The money is conditional]] | Could this make money? |
| [[#6. The pilot needs more than a small budget]] | What must happen before rollout? |
| [[#7. What is finished]] | What files should I use? |
| [[#8. Five things to remember]] | What is the shortest honest summary? |

---

## 1. The business problem

Company A has customer data but limited analytics capacity. The question is **how to allocate scarce proactive retention contacts**, not simply how to maximize churn predictions.

| Distinction | Meaning |
|---|---|
| **Risk ≠ value** | A highly likely churner may represent little recurring contribution. |
| **Risk ≠ responsiveness** | A high-risk customer is not necessarily persuadable; there are no treatment labels here. |
| **Value capture ≠ saved revenue** | Finding churned value retrospectively does not prove an intervention would save it. |

**Our proposal:** calibrated risk × capped recurring-charge proxy → opt-in service checks → randomized evaluation. Deployment-scenario risk is adjusted for the assumed 2% churn prior; that prior is not an observed company fact. No blanket discount or automatic handset subsidy is proposed.

> [!important] Mandatory Service-Fix Floor
> **Every verified billing error or network fault must be fixed regardless of bill size, list selection, or pilot arm.** The ranking rations only discretionary proactive outreach, never essential remediation.

The operational queues are exclusive: **billing → network → handset → digital residual**. A flag suggests what to investigate; it does not prove a defect or the cause of churn. The residual queue is not uniformly low-usage.

---

## 2. Is the model good?

| Item | Frozen result |
|---|---:|
| Supplied customers / operational features | 100,000 / 87 |
| Sample churn / label window | 49.56% / days 31–60 after observation |
| Model | LightGBM wider leaves + sigmoid calibration |
| Test ROC-AUC | **0.6978** |
| 95% AUC interval | **0.6899–0.7055** |
| Logistic-regression test AUC | 0.6193 |
| Test accuracy at threshold 0.5 | 64.02% |
| Test Brier score | 0.2195 |

> [!tip] AUC in plain English
> In roughly **70% of random churner/non-churner pairs**, the model ranks the churner higher. Random ranking scores 0.50; perfect ranking scores 1.00. **AUC 0.6978 does not mean 69.78% accuracy.**

**Verdict:** credible for a consulting proof of concept and worth testing as a triage tool; not an outstanding classifier or a validated production system. The professional part is the evaluation discipline, reproducibility, safeguards, and honest uncertainty — not a claim that 0.6978 is universally “good enough.”

> [!warning] Test reuse matters
> v1 already evaluated the 15,000-row test split. v2 froze its decisions before one final descriptive batch and reused the cached v1 probabilities. This is **not a fresh independent test**, and no rejected challenger received a new final-test score.

---

## 3. What the new experiments found

The model-headroom work ran **696 unique fits** and produced **150,000 repeated out-of-fold rows** using the original 75,000 train/validation customers. Those are measures of computational work, **not predictive improvement**.

| Eligible challenger | Mean CV AUC change | Outcome |
|---|---:|---|
| Nested blend | **+0.001085** | Rejected: interval crosses zero, tail-calibration gate fails, convergence warning |
| Nested LightGBM | +0.000415 | Rejected: insufficient AUC and tail-calibration evidence |
| Call/care features | +0.000159 | Rejected |
| Billing-gap features | +0.000117 | Rejected |
| Nested XGBoost | +0.000116 | Rejected |
| Other eligible candidates | Small gain or losses | None passed all gates |

> [!note] Why the best observed gain was not adopted
> The blend's corrected 95% interval was **−0.000032 to +0.002203**. Its mean gain was about **0.109 percentage points on the AUC percentage scale**, but the evidence did not establish a reliable improvement and it also failed other required checks. **Small observed CV gain ≠ approved final-model gain.**

Other findings:

- **Learning curves:** mean held-out CV AUC rose from **0.6712 at 10,000 training rows to 0.6960 at 60,000**. This supports the value of more training data within the experiment; it does not guarantee future gains or prove a ceiling.
- **Feature-removal tests:** removing recent-history features reduced mean CV AUC by **0.0186**; removing equipment features reduced it by **0.0143**. Existing signals matter, even though the new features did not qualify for promotion.
- **Calibration:** beta and isotonic did not qualify; sigmoid was retained. Their reported log-loss “improvements” were negative, meaning worse overall out-of-fold log loss than sigmoid.
- **Budget:** calibration suggested cost-dependent contact fractions, but search uncertainty was not resolved. **Nominal 10% retained; no optimized budget promoted.**
- **Governance:** excluded credit-card, home-ownership and high-income labels were partly recoverable from operational features: AUC **0.657 / 0.607 / 0.627**. Excluding attributes does not establish fairness.
- **Evidence quality:** the work separated sample and deployment calculations, exposed the pilot's profit-power shortfall, and strengthened routing, citations, and source-bound numerical checks.

**What did the hours buy?** A more defensible proposal and documented rejection of alternatives — **not a higher final AUC or demonstrated additional profit**. These experiments do not prove that further improvement is impossible.

---

## 4. Two value-capture results — not one

| Regime | Value-aware | Risk-only | Relative gain |
|---|---:|---:|---:|
| **Supplied sample:** 1,500 of 15,000 rows per list | 20.83% | 14.62% | **+42.44%** |
| **Hypothetical 2% deployment:** weighted, frozen nominal-10% thresholds | 29.51% | 25.58% | **+15.37%** |

These percentages measure the **share of observed churned recurring value captured**. Frozen v2 descriptive 95% intervals for relative gain are **+35.66% to +48.56%** for the sample and **+11.26% to +19.67%** for the deployment scenario.

> [!warning] Do not mix the regimes
> **+42.4% is not the gain used in the 2% financial scenario. +15.4% is not a new model improvement over v1.** v1 already used the deployment-consistent risk × value rule in its finance calculation; v2 reconciled and explained the difference.

In the sample, value-aware targeting accepts lower churn precision: **63.13% vs 80.47%**. In the weighted scenario, the frozen lists achieve about **9,985 value-aware contacts vs 10,431 risk-only contacts**; both were calibrated to a nominal 10%, not forced to identical test counts. There are **2,505 actual test rows** in the value-aware deployment list, not 9,985 observed customers.

---

## 5. The money is conditional

> [!example] Assumptions — not measured company facts
> 100,000 hypothetical customers · 2% churn · 20% of would-be churners prevented · six retained months · 60% margin · $1/contact · $5,000 fixed cost · USD-equivalent interpretation.

| Scenario quantity | Value |
|---|---:|
| Weighted contacts / assumed prevented cancellations | 9,985 / 95 |
| Retained revenue / gross contribution | $31.2k / $18.7k |
| **Net contribution** | **+$3,747.08** |
| Descriptive conditional 95% net interval | $2,761.37–$4,660.64 |
| Break-even contact cost / prevention | **$1.38 / 16.0%** |

### Sensitivity: net contribution ($000)

| Prevention | $1/contact | $2/contact | $5/contact |
|---:|---:|---:|---:|
| 10% | −5.6 | −15.6 | −45.6 |
| **20%** | **+3.7** | **−6.2** | **−36.2** |
| 30% | +13.1 | +3.1 | −26.8 |

> [!danger] A positive interval is not proof of profitable outreach
> The net point estimate is **unchanged from v1**. Its interval excludes uncertainty about whether contact works, real costs, transport to live customers, and household clustering. At 1% assumed churn the base case loses about **$5.6k**; at 2% churn and $2/contact it loses about **$6.2k**. **Not launching is a zero-net alternative.**

---

## 6. The pilot needs more than a small budget

Randomize linked households/accounts to opt-in service recovery or usual care, log selection and treatment probabilities, and measure **incremental contribution after all costs**. The Service-Fix Floor applies to both arms.

| Stage / power finding | Requirement |
|---|---|
| **Stage 1:** value-aware core | **7,872/arm**, 15,744 unique linked accounts; **$12,872** contact/startup envelope |
| **Stage 2:** additional learning | 2,000/arm risk-only + 1,000/arm below both cutoffs; **+$3,000** |
| Binary churn simulation | First qualifying grid point: **7,872/arm** |
| Covariate-adjusted contribution simulation | First qualifying grid point: **80,000/arm** |
| Unadjusted contribution simulation | **80% power not established through 160,000/arm** |

> [!warning] The important new negative finding
> This small pilot is for **learning**, not profit-powered rollout proof or a powered comparison of targeting policies. The simulations are cross-sectional proxies, **not validated longitudinal CUPED or household-clustered power**. Stage 1 also exceeds one approximately 10,000-account list in the illustrative portfolio: a larger eligible portfolio or successive cohorts are needed.

Actual linkage, consent, engineering and follow-up costs must be quoted. Preregister **scale / extend / stop** rules and customer-harm monitoring; do not reinterpret an inconclusive experiment as a success.

---

## 7. What is finished

| File | Current state |
|---|---|
| [philopateer.pdf](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/philopateer.pdf) | **15 pages; 846,608 bytes** (about 0.85 MB) |
| [philopateer.ipynb](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/philopateer.ipynb) | **25 executed code cells; 0 errors; original nine preserved** |
| [philopateer.pptx](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/philopateer.pptx) | 15 editable slides; three charts and two focused panels replaced; native sensitivity cells retained |
| [references.txt](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/references.txt) | Sources D1–D2, S1–S8, M1–M8, assumptions and truthful AI disclosure |
| [FINAL_ASSESSMENT_HANDOFF.md](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/FINAL_ASSESSMENT_HANDOFF.md) | Detailed successor guide, all 11 rejections, methods, hashes and freeze rules |
| [FINAL_V2_UPGRADE_REPORT.md](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/FINAL_V2_UPGRADE_REPORT.md) | Concise final upgrade/QA report |

**QA:** 278 claim-ledger rows checked; zero Office geometry issues; all 15 final renders and contact sheet reviewed; 67 frozen v1 files verified. The four deliverable hashes were checked again for this documentation update; no models were rerun and no submission artifacts were changed.

> [!todo] Remaining actions — account holder only
> - [ ] Review the PDF, notebook, and references.
> - [ ] Fill the Omnicampus References field and handle the requested AI chat-history URL truthfully; **never invent a URL**.
> - [ ] Upload the PDF, notebook, and required references under **philopateer**.
> - [ ] Submit before **28 November 2026, 11:30 UTC**.

---

## 8. Five things to remember

1. **The final AUC did not improve.** 0.6978 is moderate predictive performance; rejected CV gains are not final-test gains.
2. **+42.4% and +15.4% answer different questions.** Sample vs hypothetical deployment; neither is causal retention lift.
3. **$3.7k is conditional and unchanged from v1.** It is not demonstrated profit or guaranteed savings.
4. **Fix verified defects for everyone.** Ranking only prioritizes discretionary outreach.
5. **Pilot first — with realistic power and capacity.** Current data cannot validate treatment response, live calibration, or production profitability.

> [!summary] One sentence
> We built and stress-tested a credible value-aware retention proof of concept, retained the original model when alternatives failed, and made the proposal more honest and operationally defensible — **without claiming predictive gains we did not achieve**.

Numerical source: [v2_work/final_metrics.json](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/final_metrics.json). For exact experiment results, see [v2_work/d_results/gate_d.csv](file:///D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/d_results/gate_d.csv).
