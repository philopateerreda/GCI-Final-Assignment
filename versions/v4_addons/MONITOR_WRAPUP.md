# MONITOR WRAP-UP — break-even prior π*(γ), day-60 trigger, label vs EM precision

_v4 Track D, card D7 · 2026-10-31 · diagnostic only. No trigger is operational, no protocol or deck text changes, and WP5 remains `PARTIAL`._

## 1. Break-even prior π*(γ) — exact v2 functions on non-test scores

[E] Method: 75,000 non-test planning rows (cached baseline OOF scores, frozen sigmoid) and the 10,000 saved calibration rows. For each of the 251 priors from 0.5% to 3.0%, the weighted 10% cutoff is re-derived on calibration and applied to the planning scores; `measure()` supplies the weighted contacts and actual value. The six v2 functions are AST-extracted, and their sources match the WP5-recorded AST exactly (all six: shift=True, weights=True, cutoff=True, scores=True, measure=True, fit_thresholds=True).

| Assumed prevention γ | π* startup excluded | π* startup included | Startup effect (included − excluded) |
|---:|---:|---:|---:|
| 0.10 | 2.0918% | none in grid | — |
| 0.15 | 1.3855% | 2.0748% | 0.69 pp |
| 0.20 | 1.0361% | 1.5464% | 0.51 pp |
| 0.25 | 0.8276% | 1.2331% | 0.41 pp |
| 0.30 | 0.6892% | 1.0252% | 0.34 pp |

[E] Check: at γ = 0.20 the startup-included crossing is 1.546417%, reproducing the WP5-recorded 1.546417% with absolute difference 0.0. The startup-excluded crossing on the same grid is 1.0361%; the $5,000 startup moves the break-even prior by 0.51 pp.

[R] Definition discrepancy (G10, reported not tuned): the brief labels 1.546417% as **startup excluded**, but WP5's grid `net` is gross − contacts − $5,000, i.e. **startup included**. The number reproduces exactly under the startup-included definition; the startup-excluded crossing is the lower value in the table. D0 bound WP5's `first_crossing` under the brief's label; this card corrects the label, not the number. The two-point linear shortcut between the stored 1% and 2% nets gives 1.60%, 0.05 pp above the fine-grid crossing; it is a sanity note only. The fine grid is authoritative because the selected set changes with the assumed prior.

## 2. Trigger rule — mutually exclusive, day-60 labels (NOT OPERATIONAL — draft [R])

[R] State is set by mature day-60 labels, not by EM. The comparison is the observed day-60 churn rate (two-sided 95% interval) against π*(γ assumed) at γ = 0.20. Floor service continues in every state.

| Observation at day 60 | State | Action |
|---|---|---|
| Upper 95% bound < π* = 1.5464% (startup included) | **HOLD** | Hold discretionary outreach and review; Floor continues. |
| Lower 95% bound > π* = 1.5464% | **PROCEED-ELIGIBLE** | Proceed to a separate launch decision; this state is not a launch approval. |
| Interval contains π* | **INCONCLUSIVE** | Collect another cohort; do not re-read the same cohort as a second look. |

[E] The states are mutually exclusive by construction. The fully loaded π* (1.5464%) is used because the deployment net and WP5's `measure()` include the $5,000 startup; the startup-excluded alternative (1.0361%) would move the HOLD boundary by 0.51 pp. The definition must be fixed before any operational use.

[R] EM remains an early diagnostic only: it never sets the state, never overrides labels, and is discarded once labels mature. The earlier brief wording allowed HOLD and proceed to overlap on an interval that straddles π*; this table removes the overlap. [DECISION NEEDED: fix the π* definition (startup included vs excluded) before the monitor is ever operational.]

## 3. Day-60 labels vs EM at π = 2%

[E] Label-based standard error of a churn rate at the 2% prior, √(π(1−π)/n), against the 0.454 pp margin to the startup-included break-even prior. EM figures are WP5's recorded medians at the same prior.

| Cohort n | Label SE | Margin in label SEs | EM median error | EM bias | EM bias in label SEs | EM 95% coverage |
|---:|---:|---:|---:|---:|---:|---:|
| 10,000 | 0.140 pp | 3.2 | 0.568 pp | 0.578 pp | 4.1 | 90.2% |
| 50,000 | 0.063 pp | 7.2 | 0.499 pp | 0.505 pp | 8.1 | 82.8% |
| 100,000 | 0.044 pp | 10.2 | 0.521 pp | 0.515 pp | 11.6 | 69.0% |

[E] The margin is 3.2 / 7.2 / 10.2 label standard errors at the three sizes, while EM's bias is 4.1 / 8.1 / 11.6 label standard errors: labels are later but far more precise, and the advantage grows with n. EM convergence was 8,604 of 10,000 original fits, and coverage at the 2% prior falls to 69.0% at n = 100,000.

## 4. EM variants — deferred

[E] D7 allowed variants only if the 2% bias were below 0.15 pp; the recorded 2% bias ranges from 0.453 pp to 0.578 pp, so variants were **not run** (0 runs) and the item is recorded as deferred. No deck change follows from any D7 result.

## 5. What this does not authorize

- No operational trigger, threshold change, protocol edit or deck edit.
- WP5 status stays `PARTIAL`; this card only recomputes and rewrites its diagnostic rule.
- No test rows were read and no model was fitted or rescored.
