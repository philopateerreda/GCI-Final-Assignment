# Company A — Churn Prediction & Retention Targeting

**Retain contribution, not just customers.**

A churn model is only half the decision. This project pairs a calibrated LightGBM risk model with a value-weighted contact policy, freezes the evaluation protocol before the final batch, and then stress-tests its own conclusions in a separate audit layer.

> **Test ROC-AUC 0.6978** [0.6899, 0.7055] · **+42.4%** more churn value captured than risk-only at the same contact volume · **+15.4%** relative value under a 2% deployment prior

`Frozen v2 delivery · v3 audit complete · economics conditional, not causal`

---

## The decision

Company A can make roughly 10,000 low-cost, consented service-recovery contacts across 100,000 clients. The practical question is not *who is most likely to churn*, but **where expected retained contribution exceeds the cost of the contact**.

The model ranks risk. The policy prices it: contact when `p(churn) × recurring value` clears a threshold. Test outcomes never choose the model, the threshold, or the route.

## Approach

| Layer | Design |
|---|---|
| Population | 100,000 clients; 87 usage, revenue, equipment, and care features |
| Target | Churn in days 31–60 |
| Model | LightGBM — 385 trees, 31 leaves, learning rate 0.03; sigmoid calibration |
| Policy | `p(churn) × max(recurring revenue, 0) ≥ 1.7115`; nominal 10% budget |
| Split | 75k train · 10k calibration · 15k test |
| Uncertainty | 300-replicate bootstrap; design-effect sensitivity 1.0–1.25 |
| Economics | $1 variable contact cost · $5,000 startup · 6 months · 60% margin |

## Results

| Metric | Frozen result |
|---|---:|
| Test ROC-AUC | **0.6978** [0.6899, 0.7055] |
| Average precision | 0.6883 |
| Value capture vs risk-only, nominal 10% | **+42.4%** [+35.7%, +48.6%] |
| Relative value gain, 2% deployment prior | **+15.4%** [+11.3%, +19.7%] |
| Conditional net, 100k cohort at γ = 20% | **+$3,747** [$2,761, $4,661] |
| Break-even prevention rate | **16.0%** |

**Read the boundary.** The churn ranking is measured. The policy gain is a retrospective value-capture comparison. The dollar net is a conditional scenario built on assumed prevention, cost, margin, and horizon. No offer was tested: there is no causal retention lift and no measured profit.

## The v3 audit

A second work package asked whether the frozen delivery survives stronger scrutiny. It ran read-only and is published here even where it weakens the headline.

| WP | Question | Outcome |
|---|---|---|
| WP1 | Is the pilot powered? | 7,872/arm: **78.6%** power on gross effect, **27.9%** on variable profit (DEFF 1.0) |
| WP2 | Would it decide well? | DEFF 1.1: **91.9% extend**, 7.6% scale, 0.5% stop |
| WP3 | How prior-sensitive is the net? | P(net > 0) spans **17%–93%**; 69% under the central prior |
| WP4 | What is the causal estimand? | ITT protocol and $0.005-per-look harm gate — written, not run |
| WP5 | Can label shift be monitored? | **Partial**: median prior error 0.50–0.57 pp vs 0.30 pp tolerance |
| WP6 | Are the sources real? | Access and identities verified; M5 abstract-only; no root reference edit |
| WP7 | Should this be integrated? | Proposal written; **not applied** |
| WP8 | Does a stronger challenger win? | **Rejected** — ΔAUC +0.000276 vs +0.003 required; 7 of 11 gates fail |

The audit's conclusion is part of the deliverable: keep the frozen model, treat the pilot as learning rather than proof, and do not promote the challenger.

## Repository map

| Path | What it contains |
|---|---|
| `philopateer.ipynb` | Submitted notebook — 52 cells, all 25 code cells executed |
| `philopateer.pdf` · `philopateer.pptx` | 15-slide executive deck, PDF and editable PowerPoint |
| `analysis_pipeline.py` | Frozen v2 pipeline in script form |
| `build_notebook.py` · `export_and_verify.py` | Notebook builder and delivery QA |
| `analysis_outputs/` | Selected model, 87-feature manifest, tables, charts, 278-claim ledger |
| `v2_work/` | Frozen v2 protocol, summaries, governance audits, pilot design |
| `v3_addons/` | Independent audit WP0–WP8: reports, tests, evidence, integration proposal |
| `FINAL_ASSESSMENT_HANDOFF.md` · `FINAL_ASSESSMENT_READING_NOTE.md` | Technical handoff and short reading guide |
| `references.txt` | Verified bibliography |

## Reproduce

```bash
python -m pip install -r requirements-python311.txt
```

Place the supplied `Client.csv` and `Record.csv` in `telecom/`, then open `philopateer.ipynb`. The raw data is not redistributed here: the dataset belongs to the case provider and this repository is public. Every frozen result can be inspected in `analysis_outputs/` and `v2_work/final_metrics.json` without re-running the model.

The run is pinned to Python 3.11, six threads, and seed `20261028`.

## Integrity notes

- The final test batch was **descriptive**. No model, calibrator, budget, route, or pilot decision used test outcomes. The split had already been scored in v1; v2 reused those cached probabilities and discloses the reuse.
- Every headline figure is bound to a source in the 278-row claim ledger.
- v3 did not modify the delivery: a 4,246-file directory diff confirmed no changes outside `v3_addons/`.
- WP8 was pre-registered, executed, independently verified, and rejected by its own gates. It is reported, not buried.
- Economic outputs are tagged as assumptions, not measurements; the notebook and reports separate `[E]` evidence from `[A]` assumptions.

## Author

**Philopateer Reda** · Omnicampus `philopateer`
GCI 2026 — Company A case.
