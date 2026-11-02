# YARDSTICK — one sheet for every sample size and profit definition in the Company A package

_v4 Track D, card D2 · generated 2026-10-31 from frozen artifacts · every number bound in `results/yardstick.json` · DEFF default 1.1 (section-3 decision 3, DEFAULT_ASSUMED)_

> Vocabulary (G5). **Gross effect** = any positive effect on contribution, startup excluded. **Variable profit** = gross minus the per-contact cost, startup excluded. **Fully loaded net** = includes the startup. "First qualifying grid point" ≠ exact minimum.

## 1. Frames table — seven frames, seven different questions

| Frame | Question answered | Unit | Null / target | Key assumptions | Numbers | Source file / key |
|---|---|---|---|---|---|---|
| Frozen binary pilot | Can a 20% relative churn reduction be detected? | enrolled accounts per arm | binary churn, two-sided α 0.05, power 80% | p0 4.7711%, p1 3.8169%, 10% follow-up loss, independent accounts | **7,872/arm** (7,084 complete); v2 simulated 85.75%; WP1 E1 83.2% (DEFF 1.0), 80.8% (DEFF 1.1) | `final_metrics.json` `pilot_calibration.spec.normal_binary_reference`; `wp1_power.csv` E1_churn |
| v2 adjusted contribution (fully loaded) | Can fully loaded net contribution be detected? | enrolled accounts per arm | net after $1/contact and startup, covariate-adjusted | 90% follow-up, startup included, fixed calibration-trained adjustment, independent accounts | **80,000/arm first qualifying grid point**; simulated power there 97.25% (planning rows) / 95.25% (descriptive test rows); unadjusted 50.25% / 37.25% at 80k and 79.25% / 69.50% at 160,000 → not established; startup $0.0625 per treated enrollee | `final_metrics.json` `pilot_calibration.power_rows`, `pilot_test.power_rows`, `simulated_required_enrolled_per_arm_grid` |
| WP1 E4 variable profit | Can positive variable profit be detected? | enrolled accounts per arm | variable profit > 0 (gross − $1/contact; **startup excluded**) | value-stratified contrast, γ = 20%, DEFF 1.0 in the grid search | **40,000/arm first qualifying grid point**; E4 variable-profit power 86.8% there, 98.8% at 80k, 27.9% at 7,872 (DEFF 1.0) | `wp1_power.json` `requirements_at_gamma_20`; `wp1_power.csv` E4_V_stratified |
| WP1 E4 gross effect | Can any positive gross effect be detected? | enrolled accounts per arm | gross effect > 0 (startup excluded) | as above | **10,000/arm first qualifying grid point**; E4 gross power 90.1% there, 78.6% at 7,872 (DEFF 1.0) | same |
| 100k-cohort economics | What is the conditional business case? | USD per 100,000-account cohort | net = G·γ − K | γ = 20% assumed, 2% prior, 6 months, 60% margin, $1/contact, $5,000 startup | G = $93,660.02; K = $14,984.92; γ* = 15.9993%; net at γ = 20% = $3,747.08; conditional 95% interval $2,761.37 – $4,660.64 **at prevention = 0.2** | `final_metrics.json` `deployment_policies.bayes`, `deployment_intervals.net` |
| Planning portfolio | Is the pilot feasible from the available lists? | accounts | enrol 7,872/arm | one list = 10% of 100,000 = 10,000 accounts | one list → at most **5,000/arm**; Stage 1 needs **15,744 core accounts**; **158,000-account** planning proxy; Stage 1 envelope $12,872, Stage 2 +$3,000 | `final_metrics.json` `pilot_calibration.spec` (`planning_portfolio_calibration_proxy`, `stage1_total_enrolled`, `capacity_caveat`) |
| Prior-integrated net | How uncertain is the business case under assumed prevention priors? | probability / USD per cohort | P(net > 0), E[net], 5th percentile, EVPI | three Beta priors on γ; same G, K | P(net > 0) 93.0% / 68.5% / 16.8% for Beta(6, 14) / Beta(6, 24) / Beta(2, 18); 5th pct −$1,172.92 / −$6,166.36 / −$13,202.28; EVPI/cohort $195.71 / $1,093.29 / $832.36; EVSI/cohort at 7,872 $45.27 / $531.22 / $455.45 | `wp3_roi_band.json` `priors[].closed_form`; `wp2_evsi.json` `scenarios[]` |

**The three authoritative yardsticks (section-3 decision 1):** **7,872/arm** = learning-pilot design point (binary churn, 20% relative reduction); **40,000/arm** = first qualifying grid point for variable profit (WP1 E4, γ = 20%, DEFF 1.0); **80,000/arm** = v2 fully loaded first qualifying grid point. 160,000 appears only as "unadjusted not established through 160,000". None replaces another.

## 2. Estimator table — γ = 20%, DEFF 1.0 (the WP1 grid)

### At 7,872/arm

| Estimator | Gross-effect power | Variable-profit power | Status |
|---|---:|---:|---|
| E1_churn | 83.2% | — | binary churn; no profit null |
| E2_literal_oracle | 100.0% | 99.1% | **oracle — invalid for capacity claims** (uses latent prevented outcomes) |
| E3_literal_oracle | 100.0% | 99.1% | **oracle — invalid for capacity claims** (uses latent prevented outcomes) |
| E2_observed | 26.8% | 8.8% | observable |
| E3_observed | 78.2% | 28.3% | observable |
| E4_V_stratified | 78.6% | 27.9% | observable |

### At 80,000/arm

| Estimator | Gross-effect power | Variable-profit power | Status |
|---|---:|---:|---|
| E1_churn | 100.0% | — | binary churn; no profit null |
| E2_literal_oracle | 100.0% | 100.0% | **oracle — invalid for capacity claims** (uses latent prevented outcomes) |
| E3_literal_oracle | 100.0% | 100.0% | **oracle — invalid for capacity claims** (uses latent prevented outcomes) |
| E2_observed | 99.1% | 52.7% | observable |
| E3_observed | 100.0% | 98.8% | observable |
| E4_V_stratified | 100.0% | 98.8% | observable |

A single "80,000" hides a **46.1 pp** spread in variable-profit power between E2_observed (52.7%) and E3_observed / E4 (98.8% / 98.8%). Any slide must name the estimator. The WP2 decision-quality row uses **E3_observed**; the WP1 power table uses **E4**.

## 3. DEFF table — E4, γ = 20%

| DEFF | 7,872/arm gross effect | 7,872/arm variable profit | 5,000/arm gross effect | 5,000/arm variable profit |
|---|---:|---:|---:|---:|
| 1.00 | 78.6% | 27.9% | 59.7% | 19.9% |
| 1.10 (default) | 76.0% | 25.4% | 55.6% | 17.9% |
| 1.25 | 72.5% | 21.6% | 51.1% | 14.9% |

DEFF 1.1 is used everywhere in v4 text (decision 3). The WP1 first-qualifying-grid search was run at DEFF 1.0; the 40,000/arm and 10,000/arm grid points are therefore DEFF-1.0 statements and are labelled as such.

## 4. Bridge sentences (≤ 25 words each; word counts bound)

| Key | Sentence | Words |
|---|---|---:|
| `target_bridge_slide13` | WP1 E4 target: variable profit, startup excluded, DEFF 1.1. v2 80,000: fully loaded, startup included, 90% follow-up. Not comparable; no reduction claimed. | 22 |
| `feasibility_line` | One 10,000-account list gives at most 5,000/arm (55.6% / 17.9%). 7,872/arm needs 15,744 core accounts; 158,000-account proxy. | 17 |
| `deff_statement` | All pilot power and decision figures use DEFF 1.1 for assumed household clustering [A]; ICC unverified. DEFF 1.0 / 1.25 appear only as sensitivity. | 24 |
| `variable_profit_definition` | Variable profit = gross contribution minus $1 per treated contact; the $5,000 startup is excluded ($0.3176 per enrollee at 7,872/arm). | 20 |
| `transport_line` | The 2% deployment prior is an assumption; selected non-test control churn is 4.842493% (2.42×). Assumption, not measurement. | 17 |
| `cohort_line` | Prior-integrated values are per 100,000-account cohort; ×12 figures assume 12 identical cohorts [A], not a portfolio guarantee. | 17 |
| `evsi_line` | EVSI $45–$531 per cohort at 7,872/arm is value of information under assumed priors; not funding proof. | 16 |
| `grid_wording` | 80,000/arm is the first qualifying grid point for v2 fully loaded contribution; not an exact minimum. Unadjusted: not established through 160,000. | 21 |

## 5. Pilot purpose statement

At 7,872/arm, γ = 20%, DEFF 1.1 (E3_observed, CI rule): **scale 7.6% / extend 91.9% / stop 0.5%**. At γ = 0 (no effect): extend 47.5% / stop 52.5% — the stop rule is not a clean stop.

The standard error of the estimated prevention γ̂ at 7,872/arm (p0 = 4.7711%, 20% relative reduction) is **6.8 pp** by SE(p̂0 − p̂1)/p0 (the convention behind the brief's ≈ 6.8 pp), **6.06 pp** by the full two-arm delta method, and 7.1 pp with DEFF 1.1. The gap between the 20% assumption and the 16.0% break-even is **4.0 pp** — well under one standard error. **The pilot cannot resolve break-even; it is a learning / launch and harm-detection step**, not a profit proof.

Formulas (recorded): `SE_diff/p0 = sqrt(p0(1−p0)/n + p1(1−p1)/n) / p0`; `SE_delta = sqrt([p1(1−p1)/n]/p0² + [p1²/p0⁴]·p0(1−p0)/n)`; `gap = γ_assumed − K/G`.

## 6. Monitor break-even prior π* — definition check (G10)

WP5 reports π* = **1.546417%** (γ = 20%, $1/contact). Its grid `net` equals gross − contacts − $5,000, i.e. the startup is **included** (fully loaded), contrary to the brief's "startup excluded" label. The startup-excluded crossing on the same grid is ≈ **1.0361%** (between grid priors 1.03% and 1.04%). The fully loaded margin to the 2% prior is 0.454 pp. D7 recomputes π*(γ) for both definitions with the exact v2 functions.

## 7. Transport

Selected non-test control churn 4.842493% vs the 2% deployment prior = **2.42×** — an assumption, not a measurement; the 5th-percentile nets above inherit it.
