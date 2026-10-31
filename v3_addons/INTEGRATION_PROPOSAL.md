# Integration proposal — human decision required

[E] Nothing below is applied. Frozen model, notebook, presentation, PDF and references remain unchanged. Current presentation: **15 slides**; current claims ledger: **278 data rows**. [R] Replacements only; no extra page or slide. [E] WP5 terminal status: **PARTIAL**; acceptance failures, if any, are not repaired by changing a reporting threshold.

## Ranked candidates

### 1. Slide 13: capacity, two nulls and decision quality — highest value

[E] Replace the current right-hand heading and panel. Keep the left-hand enrollment/cost text, central propensity strip, scale/extend/stop rules and exact harm gate unchanged. [R] Use a compact native table in the existing top region; do not overlay the propensity strip or shrink text automatically. Geometry and all-slide visual QA are still required after approval.

**Exact heading before**
```text
Binary learning ≠ profit proof
```
**Exact heading after [R]**
```text
Capacity ≠ profit proof
```
**Exact panel before**
```text
Calibration simulation (planning proxy):
adjusted contribution needs 80,000/arm;
unadjusted not 80% powered through
160,000/arm. No validated longitudinal
CUPED or household-clustered power.
Re-estimate using live data.
```
**Exact panel after [E/A]** — slash pairs are effect / variable-profit power, in percent:

| n/arm [A] | γ=10% [A] | γ=16% [A] | γ=20% [A] | γ=30% [A] |
|---:|---:|---:|---:|---:|
| 5,000 | 19.8 / 2.6 | 42.9 / 7.9 | 59.7 / 19.9 | 93.6 / 60.7 |
| 7,872 | 27.5 / 2.1 | 59.9 / 11.5 | 78.6 / 27.9 | 99.3 / 79.8 |

```text
[E/A] E4 V-stratified; DEFF=1; 1,000 simulations/point.
[E/A] 80%-power γ MDE: 26.0% / 20.7% at 5,000 / 7,872 per arm; interpolated. Profit MDE not established through γ=30%.
[E/A] At 7,872/arm, γ=20%, DEFF=1.1: scale 7.6%, extend 91.9%, stop 0.5% (observable adjusted contribution; no harm assumed).
[A] $1 variable-cost null excludes $5,000 startup and unquoted implementation costs; no validated household-clustered or live power.
```

[E] Sources: `results/wp1_power.json → capacity_mde`, complete MC uncertainty in `power_rows`; `results/wp1_capacity_mde.csv`; `results/wp2_decision_quality.csv` row `n_per_arm=7872,gamma=.20,deff=1.1`; supporting method in `reports/WP1_report.md` and `reports/WP2_report.md`. [E] At γ=.20, first qualifying E4 declared grid is 10,000/arm for effect and 40,000/arm for variable-profit, not an exact minimum and not a resolution of v2's fully loaded 80,000/arm framing. [R] Keep those grid details supporting-only if the panel is crowded.

[E] Ledger impact: retire **C0137 / CSV line 138, C0139 / CSV line 140** from the old panel; retain the existing 80% planning target and enrollment/harm values. The 278-row file has no intrinsic IDs: `C0001` means first data row, and CSV line = data-row index+1; exact aliases/keys are captured in `results/wp7_readonly_deck_ledger.json`. Add new rows for every table cell, γ/n/DEFF/replicate/MDE and decision probability; do not reuse old source keys for new values. [R] Risk: low scientific risk, moderate layout/provenance QA. These are empirical conditional simulations, not measured treatment effects. Avoid claiming “powered” solely from 78.6% or rounding 79.8% into an established 80%.

### 2. Slide 12: prior-integrated net sensitivity — Option C

[E] Existing heatmap, break-even and prior-stress values remain unchanged. Replace only the existing footer; do not mislabel a sensitivity band as a confidence interval.

**Exact footer before**
```text
[D1, M5–M6] Editable scenario sensitivity, not a confidence interval. Prevention is assumed; break-even holds all other base assumptions fixed.     12
```
**Exact footer after [E/A]**
```text
[D1, M5–M6, M9] Prior-integrated net at the frozen 10% threshold: P(net>0)=17%–93% across assumed prevention priors; 69% under Beta(6,24), centered on 20%. Sensitivity, not a CI or EMPC; no treatment labels.     12
```

[E] Sources: `results/wp3_roi_band.json → priors[].closed_form.p_positive` and `band`; `results/wp6_citation_register.csv → M9`. [A] Beta(6,14) is a verified package default used as an assumption; Beta(6,24) centers on the existing 20% assumption; Beta(2,18) is the reviewer's pessimistic assumption. [E] No existing numeric ledger row is deleted by this footer replacement; all slide-12 heatmap/stress rows remain. Add the 10%, 17%, 93%, 69%, 6/24 and 20% tokens plus appropriate source/prior tags. [R] Risk: medium; reference and layout QA needed, prevention remains unidentified.

### 3. Slide 5 and M5 wording — optional diagnostic-only wording

[E] Preserve the chart and its original quantitative claims; do not replace a verified known-prior correction with an EM result. [R] No numeric live-prior estimate or automatic hold/proceed trigger belongs in this deck.

**Exact slide-5 sentence before**
```text
Value-aware triage adds higher-bill accounts and drops lower-bill ones—not a causal claim about who will respond.
```
**Exact slide-5 sentence after [R]**
```text
Value-aware triage is not a response model. EM is a label-shift diagnostic only; stable class-conditionals are unverified and day-60 labels remain ground truth.
```

**Exact slide-15 methods block before**
```text
[M1] scikit-learn: evaluation and calibration.
[M2] LightGBM: local CPU boosting.
[M5] Saerens et al. (2002): prior adjustment.
[M6] Elkan (2001): costs / known-prior correction.
```
**Exact slide-15 methods block after [E/R]**
```text
[M1] scikit-learn: evaluation and calibration.
[M2] LightGBM: local CPU boosting.
[M5] Saerens et al. (2002): prior adjustment; abstract-only.
[M6] Elkan (2001): costs / known-prior correction.
```

[E] Supporting M5 scope: “Implemented from the standard derivation and validated by simulation; paper read from abstract only.” `results/wp5_label_shift.json` and `results/wp6_citations.json → source_observations.m5` are the source keys. [E] Existing slide-5 numeric prior/chart rows and slide-15 year row are preserved; add day-60 token if this wording is approved. [R] Risk: medium and low priority. WP5 acceptance must be reviewed before any operational use; diagnostic wording does not imply recovery or calibrated live intervals. The brief's “lower bound below π* → hold” and “straddles π* → proceed” overlap; supporting-only conservative hold priority is a recommendation, not a protocol modification. Floor continues.

### 4. References — only sources actually used

[E] Root `references.txt` is untouched. [R] Options A/B require **no new external reference** for the locally computed WP1/WP2 results. [R] Option C with candidate 2 cites M9: preserve all existing reference text and append the exact block below. The corresponding References-field draft is `results/wp6_omnicampus_references_draft.txt`. Existing S4 accessible-copy and M5 abstract-only caveats stay; do not duplicate them.

**Exact append after [E/A/R]** — before: no M9 block
```text
V3 SUPPORTING ANALYSIS — APPLY ONLY IF OPTION C IS APPROVED

[M9] EMP package contributors. empChurn source code and documentation. Accessed 29 October 2026.
https://rdrr.io/cran/EMP/src/R/empChurn.R
Verified coverage: source-code and documentation pages; function defaults alpha=6, beta=14. Beta(6,14) is used only as an assumed prevention-prior sensitivity, not an empirical Company A prevention rate. The reported quantity is prior-integrated net at the frozen nominal 10% threshold, not EMPC; no threshold is optimized or promoted. Other priors are assumed: Beta(6,24), centered on 20%, and Beta(2,18), the reviewer's pessimistic stress prior.
```

**Exact slide-15 right methods block before**
```text
[M3] XGBoost; [M4] CatBoost: comparators.
[M7] Deng et al. (2013): pre-period adjustment.
[M8] Neslin et al. (2006): historical churn protocol.
No matched AUC ceiling or measured CUPED claimed.
```
**Exact block after [R]** — only if M9 is cited in slide 12
```text
[M3] XGBoost; [M4] CatBoost: comparators.
[M7] Deng et al. (2013): pre-period adjustment.
[M8] Neslin et al. (2006): historical churn protocol.
[M9] EMP source: assumed Beta(6,14) default.
```

[E] This removes no existing numeric ledger claim; add package-prior numeric tokens. [R] Supporting-only Nadeau/Bouckaert/ProfTree corrections are not new PDF references. Risk: low content risk, medium if reference-page typography needs adjustment.

### 5. Supporting-only material

[R] Keep WP4 ITT/Floor addendum, EVSI detail and horizons, queue assumption table, label-shift grid/coverage and trigger conflict in `v3_addons`, not new submission pages. [E/A] EVSI is $45–$531 per future cohort across priors; the $12,872 pilot also buys production contacts, so this is not a pure research-cost comparison or funding proof. No AUC/model claim changes.

## Human options — not selected

| Option [R] | Scope | Risk | Indicative effort [A] |
|---|---|---|---|
| A | Submit frozen v2 as-is; retain supporting analyses | None from integration | 0 |
| B | Slide 13 replacement only; no external reference append needed | Low/moderate QA | About 1 day |
| C | Slides 12/13; optional 5 and existing reference-page blocks; M9 if cited | Medium | About 1–1.5 days |
| GO v3-model | Separate WP8 and potential third test use | High; OFF | Separate approved project |

[R] Recommend **B first**: the capacity/profit distinction adds the most decision value without changing the model or economics. C is reasonable if the prior sensitivity earns its limited page space; the monitor is lower priority and diagnostic-only. A is safe if no integration QA is desired. Do not run WP8.

## Separate integration QA — only after approval

[R] Preserve the notebook's frozen execution cells; never Run All. A future integration decision must resolve how new supporting results are reproduced within the submitted notebook, if required by the rubric: the current frozen notebook does not contain WP1–WP5 code. Do not silently imply it does. Any notebook narrative/cache addition needs an explicitly approved scope, not a model retrain.

[R] Approved changes must follow source/claim → presentation → geometry → all-15-slide visual review → hash-bound receipt and refreshed hashes, with ≤15 PDF pages and <10,000,000 bytes. **User instruction overrides the brief's Office-PDF export step: any newly created/edited PDF must use LaTeX only**, with complete professional source, assets and compilation instructions. No PDF is generated now; the future PDF QA/export design needs separate approval. [E] Current unchanged slides are not newly visually certified in this v3 run.

## Reviewer calendar targets [R]

| Target date | Milestone |
|---|---|
| 3 November 2026 | WP0–WP3 done |
| 6 November 2026 | WP4–WP6 done; WP7 proposal delivered |
| 8 November 2026 | Human gate decision |
| 9–13 November 2026 | Integration and QA, only if B/C approved |
| 16 November 2026 | Artifact freeze; no further edits |
| 17–24 November 2026 | Human review, upload, References field and submission |
| 27 November 2026 | Hard backstop; deadline 28 November 2026, 11:30 UTC |

**[R] STOP here. Await A/B/C; no deliverable, reference, notebook, protocol, submission or WP8 action is authorized by this proposal.**
