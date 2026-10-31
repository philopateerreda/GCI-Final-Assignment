# Company A — Churn Prediction & Retention Targeting

**Retain contribution, not just customers.**

A calibrated LightGBM risk model, a value-weighted contact policy, an evaluation protocol frozen before the final batch — and a separate audit layer that stress-tests the conclusions, including the ones it weakens.

> **Test ROC-AUC 0.6978** [0.6899, 0.7055] · in the supplied sample, value-aware targeting captures **20.8%** of churned recurring value vs **14.6%** for risk-only (**+42.4%** relative) · **+15.4%** relative under a 2% deployment prior

`Frozen v2 model · v3 audit · v4 integrity pass v4.0.0 · economics conditional, not causal`

---

## At a glance

| | |
|---|---|
| **Model** | LightGBM, 385 trees, 31 leaves, learning rate 0.03, sigmoid calibration — refit on all 75,000 non-test rows |
| **Policy** | Contact when `p(churn) × max(recurring revenue, 0) ≥ 1.7115`, nominal 10% budget |
| **What is measured** | The churn ranking and a retrospective value-capture comparison |
| **What is assumed** | Prevention rate, cost, margin, horizon, and the 2% deployment churn rate |
| **What is not claimed** | Causal retention lift, measured profit, or a validated production system |

## The decision

Company A can make roughly 10,000 low-cost, consented service-recovery contacts across 100,000 clients. The practical question is not *who is most likely to churn*, but **where expected retained contribution exceeds the cost of the contact**.

The model ranks risk. The policy prices it. Test outcomes never choose the model, the threshold, or the route. Every verified billing error or network fault is fixed for everyone regardless of ranking (the *Service-Fix Floor*); the ranking only rations discretionary outreach.

## Approach

| Layer | Design |
|---|---|
| Population | 100,000 clients; 87 usage, revenue, equipment, and care features |
| Target | Churn in days 31–60 |
| Model | LightGBM, sigmoid calibration |
| Split | 75k train · 10k calibration · 15k test |
| Uncertainty | 300-replicate bootstrap; design-effect sensitivity 1.0–1.25 |
| Economics | $1 variable contact cost · $5,000 startup · 6 months · 60% margin |

## Results

| Metric | Frozen result |
|---|---:|
| Test ROC-AUC | **0.6978** [0.6899, 0.7055] |
| Average precision | 0.6883 |
| Value captured, value-aware vs risk-only (supplied sample, 1,500 of 15,000 rows per list) | 20.83% vs 14.62% → **+42.4%** [+35.7%, +48.6%] |
| Relative value gain, 2% deployment prior | **+15.4%** [+11.3%, +19.7%] |
| Conditional net, 100k cohort at 20% prevention | **+$3,747** [$2,761, $4,661] — interval conditional on 20% prevention |
| Break-even prevention rate | **16.0%** |

> [!IMPORTANT]
> **Read the boundary.** The churn ranking is measured. The policy gain is a retrospective value-capture comparison. The dollar net is a conditional scenario built on assumed prevention, cost, margin, and horizon. No offer was tested: there is no causal retention lift and no measured profit. The +42.4% and +15.4% answer different questions and must not be mixed.

## Three meanings of "profit"

| Term | Includes | Used for |
|---|---|---|
| **Gross effect** | Any positive effect on retained contribution | Pilot power for "does it work at all" |
| **Variable profit** | Gross minus $1 per treated contact; **startup excluded** | Pilot power for "is it profitable per account" |
| **Fully loaded net** | Variable profit minus the $5,000 startup | The v2 economics and the 100k-cohort scenario |

## The pilot, honestly

Four sample sizes appear in the project. Each answers a different question; none replaces another.

| Per arm | What it is |
|---|---|
| **5,000** | What one 10,000-account top list can supply |
| **7,872** | Learning-pilot design point: detect a 20% relative churn reduction (needs 15,744 core accounts) |
| **40,000** | First qualifying grid point for *variable* profit (value-stratified estimator, γ = 20%, startup excluded) |
| **80,000** | v2 fully loaded first qualifying grid point (not an exact minimum; adjusted power 0.9525 there) |

At 7,872 per arm and design effect 1.1: **76.0%** power to detect a gross effect and **25.4%** to show positive variable profit (55.6% / 17.9% at 5,000). A confidence-interval decision rule gives **7.6% scale · 91.9% extend · 0.5% stop**.

> [!NOTE]
> The pilot is a **learning and harm-detection step, not proof of profit**. Its most likely outcome is "inconclusive — extend once, then stop". It can detect harm and a large effect; it cannot resolve break-even.

## How sensitive is the money?

| Prevention prior (assumption) | P(net > 0) | 5th-percentile net |
|---|---:|---:|
| Beta(6,14), mean 30% (software default) | 0.930 | −$1,173 |
| Beta(6,24), mean 20% (central) | 0.685 | −$6,166 |
| Beta(2,18), mean 10% (stress) | 0.168 | −$13,202 |

A sensitivity band, **not** a confidence interval. The 2% churn rate is an assumption; the selected sample shows 4.84% (a 2.42× gap).

## The audit trail

| Stage | Question | Outcome |
|---|---|---|
| WP1 | Is the pilot powered? | 78.6% / 27.9% at 7,872 per arm, design effect 1.0 (76.0% / 25.4% at 1.1) |
| WP2 | Would it decide well? | 91.9% extend, 7.6% scale, 0.5% stop |
| WP3 | How prior-sensitive is the net? | P(net > 0) spans 17%–93% |
| WP4 | What is the causal estimand? | Intention-to-treat protocol and a 0.005-per-look harm gate — written, not run |
| WP5 | Can label shift be monitored? | **Partial**: median prior error 0.50–0.57 pp vs 0.30 pp tolerance; diagnostic only |
| WP6 | Are the sources real? | Access and identities verified; one source abstract-only |
| WP7 | Should changes be integrated? | Proposal written; resolved in v4 (below) |
| WP8 | Does a stronger challenger win? | **Rejected** — ΔAUC +0.000276 vs +0.003 required; 7 of 11 gates fail |
| **v4 · Track D** | Is the package internally coherent? | One yardstick sheet reconciles every sample size, design effect and profit definition; stale status text refreshed; 278-row ledger dry-run; integration proposal with exact text |
| **v4 · M0–M1** | Can more training data lift AUC? | **No** — the frozen model already uses all 75,000 non-test rows; track closed by its own gate |
| **v4 · Integration** | Apply the proposal? | Not applied (fallback to frozen v2): the corrections are documented in v4_addons/INTEGRATION_PROPOSAL_v4.md; the delivered deck is unchanged. |

## Did we try to improve the model?

Yes — three times, and the answer was consistent.

| Attempt | Result |
|---|---|
| v2: 11 eligible challengers (696 fits, repeated out-of-fold) | Best mean gain +0.001085 (nested blend); none passed all preregistered gates |
| v3 WP8: preregistered challenger | ΔAUC +0.000276 vs +0.003 gate; value capture +0.000346; rejected |
| v4 M1: data-volume audit | Frozen model already refit on all 75,000 non-test rows; learning curve flattens |

| Training rows | 15,000 | 30,000 | 45,000 | 60,000 | 67,500 |
|---|---:|---:|---:|---:|---:|
| Mean held-out AUC | 0.6786 | 0.6892 | 0.6939 | 0.6962 | 0.6968 |

Fitted curve exponent c = 0.672 (95% CI 0.403–0.964). Extrapolation, not a measured result: roughly doubling the training customers might add about +0.004 AUC — a data-strategy point rather than a modelling fix.

## Repository map

| Path | What it contains |
|---|---|
| `philopateer.ipynb` | Submitted notebook — 52 cells, 25 code cells executed, zero errors |
| `philopateer.pdf` · `philopateer.pptx` | 15-slide executive deck — PDF (846,608 bytes) and editable PowerPoint |
| `analysis_pipeline.py` | Frozen v2 pipeline in script form |
| `build_notebook.py` · `export_and_verify.py` | Notebook builder and delivery QA |
| `analysis_outputs/` | Selected model, 87-feature manifest, tables, charts, 278-claim ledger |
| `v2_work/` | Frozen v2 protocol, summaries, governance audits, pilot design |
| `v3_addons/` | Independent audit WP0–WP8: reports, tests, evidence, integration proposal |
| `v4_addons/` | v4 integrity pass: `YARDSTICK.md`, `INTEGRATION_PROPOSAL_v4.md`, `REPRODUCIBILITY.md`, `TEXT_BLOCKS.md`, ledger dry-run, provenance tools, Track M feasibility and closure reports, `STATE.md` |
| `FINAL_ASSESSMENT_HANDOFF.md` · `FINAL_ASSESSMENT_READING_NOTE.md` | Technical handoff and short reading guide |
| `references.txt` | Verified bibliography and AI-use disclosure |

## Reproduce

```bash
python -m pip install -r requirements-python311.txt
```

Place the supplied `Client.csv` and `Record.csv` in `telecom/`, then open `philopateer.ipynb`. The raw data is not redistributed: the dataset belongs to the case provider and this repository is public. Every frozen result can be inspected in `analysis_outputs/` and `v2_work/final_metrics.json` without re-running the model. The run is pinned to Python 3.11, six threads, and seed `20261028`.

## Integrity notes

- The final test batch was **descriptive**. No model, calibrator, budget, route, or pilot decision used test outcomes. The split had been scored in v1; v2 reused those cached probabilities and discloses the reuse. v3 and v4 scored **no new model** on it.
- Every headline figure is bound to a source in the 278-row claim ledger; v4 numbers are bound by a checker and not typed by hand.
- v3 changed nothing outside `v3_addons/`. v4 edited only two stale v3 status documents (`HANDBACK.md`, `WP7_report.md`; the refreshed file list is `v4_addons/MANIFEST_v4.json`) and, no delivered file.
- WP8 was preregistered, executed, independently verified, and rejected by its own gates. It is reported, not buried.
- Economic outputs are tagged as assumptions, not measurements; reports separate `[E]` evidence, `[A]` assumptions and `[R]` recommendations.
- Analysis planning, review and implementation were AI-assisted; the full disclosure is in `references.txt`.

## Author

**Philopateer Reda** · Omnicampus `philopateer`
GCI 2026 — Company A case.
