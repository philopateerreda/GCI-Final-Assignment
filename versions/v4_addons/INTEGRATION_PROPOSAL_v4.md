# Integration proposal v4 — supersedes `v3_addons/INTEGRATION_PROPOSAL.md`

_v4 Track D, card D4 · 2026-10-31 · nothing below is applied; the frozen deck, notebook, PDF and references are unchanged. Human gate: `gates/H3_OPTION.txt` containing `A`, `B_PRIME`, `C` or `R`._

## Placeholders requiring a human decision (listed first)

- `[DECISION NEEDED: maximum number of extensions and cost per extension]` — appears in the slide-13 panel (options B′, C, R). Extend-rule budget: the WP2 decision simulation gives a 91.9% "extend" probability at the design point, so the number of permitted extensions and their cost determine the pilot's real envelope.
- `[DECISION NEEDED: is a Floor contact free? if not, the $12,872 envelope is understated]` — D6 text block; affects slide 13 left panel only if the human wants it on the slide.
- `[DECISION NEEDED: action if the harm gate trips; owner]` — D6 text block; protocol addendum, not a slide.

## Common rules for every option

- QA chain, in order: source/claim (ledger from D3) → presentation text → geometry → **all-15-slide visual review** → hash-bound receipt (refresh the four deliverable hashes and the ledger). PDF: **LaTeX-only**, no Office export, ≤ 15 pages, < 10,000,000 bytes. Do not claim visual QA unless performed. Frozen notebook cells untouched. Never submit.
- Text-length deltas are measured on the whole text element that contains the change; growth above 15% is flagged. Flags mean layout QA is mandatory, not that the edit is rejected.
- Ledger: original 278 rows; counts below are from the D3 dry-run (`ledger_dryrun/claims_ledger_<option>.csv`).
- Vocabulary: gross effect / variable profit (startup excluded) / fully loaded net; "first qualifying grid point; not an exact minimum"; status values only from the G5 list.

## Option A

No change. Frozen v2 remains the submission; v4 material stays in v4_addons/.

- Slides touched: none
- Ledger impact: 0 retired, 0 added → 278 rows; sha256 `b4dce03b43f6bd1b9ef3142759e0cb88682527af2f9f8824902521d88729c5b4`
- Time estimate [A]: 0.0 day(s)
- Risks: none from integration. The slide-11 interval stays labelled as if unconditional and slide 13 keeps the unbridged `80,000` / `160,000` wording — the two integrity findings of the v3 review remain in the submission.

## Option B′ (recommended)

Slide 11 conditional-interval relabel + slide 13 capacity/target bridge (recommended).

- Slides touched: 11, 13
- Ledger impact: 0 retired, 18 added → 296 rows; sha256 `759383e8033c3f9b29974ffde6ba1e519f65f89a0417625c7cc4d92ae2e3583d`
- Time estimate [A]: 1.0 day(s)
### Slide 11 — text element 3

Length 151 → 224 characters (48.3%) **FLAG > 15%**.

**Exact text before**
```text
2% deployment churn
20% of would-be churners
prevented
6 months × 60% margin
$1 per contact; $5k fixed
No blanket subsidy
Net 95% interval: $2.8k–$4.7k
```
**Exact text after**
```text
2% deployment churn
20% of would-be churners
prevented
6 months × 60% margin
$1 per contact; $5k fixed
No blanket subsidy
Net 95% interval at 20% prevention: $2.8k–$4.7k. Prior-integrated 5th percentile (Beta(6,24)): −$6.2k.
```

Ledger rows added (slide, source key, type, displayed):

- `11` · `v3_addons/results/wp3_roi_band.json::priors.1.a` · assumed · `6`
- `11` · `v3_addons/results/wp3_roi_band.json::priors.1.b` · assumed · `24`
- `11` · `v3_addons/results/wp3_roi_band.json::priors.1.closed_form.net_5pct` · simulated · `−6.2k`

Note: tokens `20%`, `95%`, `2.8k`, `4.7k` already have slide-11 rows (C0092, C0097, C0098, C0099) and are kept; three new distinct tokens added

### Slide 13 — text element 4

Length 219 → 790 characters (260.7%) **FLAG > 15%**.

**Heading before**
```text
Binary learning ≠ profit proof
```
**Heading after**
```text
Capacity ≠ profit proof
```

**Exact text before**
```text
Calibration simulation (planning proxy):
adjusted contribution needs 80,000/arm;
unadjusted not 80% powered through
160,000/arm. No validated longitudinal
CUPED or household-clustered power.
Re-estimate using live data.
```
**Exact text after**
```text
WP1 E4 target: variable profit, startup excluded, DEFF 1.1. v2 80,000: fully loaded, startup included, 90% follow-up. Not comparable; no reduction claimed.
E4 at DEFF 1.1 — 7,872/arm: 76.0% gross / 25.4% variable profit; 5,000/arm: 55.6% / 17.9%.
One 10,000-account list gives at most 5,000/arm; 7,872/arm needs 15,744 core accounts (158,000-account proxy).
Decision rule (E3_observed, DEFF 1.1, CI rule), 7,872/arm, γ=20%: scale 7.6% / extend 91.9% / stop 0.5%.
80,000/arm = first qualifying grid point for v2 fully loaded contribution, not an exact minimum; unadjusted not established through 160,000/arm.
Purpose: learning, launch and harm detection — not profit proof. SE(γ̂) ≈ 6.8 pp vs a 4.0 pp gap to break-even.
[DECISION NEEDED: maximum number of extensions and cost per extension]
```

Ledger rows added (slide, source key, type, displayed):

- `13` · `v4_addons/results/yardstick.json::numbers.deff_default.value` · assumed · `1.1`
- `13` · `v4_addons/results/yardstick.json::numbers.v2_followup_retention.value` · assumed · `90%`
- `13` · `v4_addons/results/yardstick.json::numbers.e4_effect_power_7872_deff1p1.value` · simulated · `76.0%`
- `13` · `v4_addons/results/yardstick.json::numbers.e4_profit_power_7872_deff1p1.value` · simulated · `25.4%`
- `13` · `v4_addons/results/yardstick.json::numbers.max_per_arm_one_list.value` · assumed · `5,000`
- `13` · `v4_addons/results/yardstick.json::numbers.e4_effect_power_5000_deff1p1.value` · simulated · `55.6%`
- `13` · `v4_addons/results/yardstick.json::numbers.e4_profit_power_5000_deff1p1.value` · simulated · `17.9%`
- `13` · `v4_addons/results/yardstick.json::numbers.list_size.value` · assumed · `10,000`
- `13` · `v2_work/final_metrics.json::pilot_calibration.spec.planning_portfolio_calibration_proxy` · assumed · `158,000`
- `13` · `v2_work/final_metrics.json::protocol.financial_assumptions.prevention` · assumed · `20%`
- `13` · `v4_addons/results/yardstick.json::numbers.dq_7872_g20_p_scale.value` · simulated · `7.6%`
- `13` · `v4_addons/results/yardstick.json::numbers.dq_7872_g20_p_extend.value` · simulated · `91.9%`
- `13` · `v4_addons/results/yardstick.json::numbers.dq_7872_g20_p_stop.value` · simulated · `0.5%`
- `13` · `v4_addons/results/yardstick.json::numbers.se_gamma_hat_difference_scaled.value` · simulated · `6.8`
- `13` · `v4_addons/results/yardstick.json::numbers.gap_assumption_to_break_even.value` · simulated · `4.0`

WP7 retirements reversed: C0137, C0139 (tokens kept by the new text).

Note: WP7 retired C0137 (`80,000`) and C0139 (`160,000`); the D4 text keeps both tokens (grid wording / "not established through `160,000`"), so they are retained. `80%` (C0138) stays via the footer. Fifteen new distinct tokens added.

**B′ risks.** Slide 11: low scientific risk; the box grows and may need a smaller font or a split line — layout QA. Slide 13: the replacement panel is several times longer than the original six lines; if it does not fit the existing panel region, the recommended fallback is to move the decision-rule line and the purpose line into the footer, keeping the target bridge, the DEFF-1.1 numbers, the feasibility line and the grid wording in the panel. Do not shrink text automatically; do not overlay the propensity strip. All numbers are conditional simulations, not measured treatment effects; "powered" must not be claimed from 76.0% / 25.4%.

## Option C

B' plus slide 12 prior-band footer (M9), optional slide 5 diagnostic wording, slide 15 M5/M9 blocks, and the references.txt M9 append.

- Slides touched: 11, 13, 12, 5, 15
- Ledger impact: 0 retired, 25 added → 303 rows; sha256 `d9b8884a5bf3f2185e0dc4c658a8b8bf39d3d231487879925ae38c23c23e2ae8`
- Time estimate [A]: 1.5 day(s)
### Slide 11 — text element 3

Length 151 → 224 characters (48.3%) **FLAG > 15%**.

**Exact text before**
```text
2% deployment churn
20% of would-be churners
prevented
6 months × 60% margin
$1 per contact; $5k fixed
No blanket subsidy
Net 95% interval: $2.8k–$4.7k
```
**Exact text after**
```text
2% deployment churn
20% of would-be churners
prevented
6 months × 60% margin
$1 per contact; $5k fixed
No blanket subsidy
Net 95% interval at 20% prevention: $2.8k–$4.7k. Prior-integrated 5th percentile (Beta(6,24)): −$6.2k.
```

Ledger rows added (slide, source key, type, displayed):

- `11` · `v3_addons/results/wp3_roi_band.json::priors.1.a` · assumed · `6`
- `11` · `v3_addons/results/wp3_roi_band.json::priors.1.b` · assumed · `24`
- `11` · `v3_addons/results/wp3_roi_band.json::priors.1.closed_form.net_5pct` · simulated · `−6.2k`

Note: tokens `20%`, `95%`, `2.8k`, `4.7k` already have slide-11 rows (C0092, C0097, C0098, C0099) and are kept; three new distinct tokens added

### Slide 13 — text element 4

Length 219 → 790 characters (260.7%) **FLAG > 15%**.

**Heading before**
```text
Binary learning ≠ profit proof
```
**Heading after**
```text
Capacity ≠ profit proof
```

**Exact text before**
```text
Calibration simulation (planning proxy):
adjusted contribution needs 80,000/arm;
unadjusted not 80% powered through
160,000/arm. No validated longitudinal
CUPED or household-clustered power.
Re-estimate using live data.
```
**Exact text after**
```text
WP1 E4 target: variable profit, startup excluded, DEFF 1.1. v2 80,000: fully loaded, startup included, 90% follow-up. Not comparable; no reduction claimed.
E4 at DEFF 1.1 — 7,872/arm: 76.0% gross / 25.4% variable profit; 5,000/arm: 55.6% / 17.9%.
One 10,000-account list gives at most 5,000/arm; 7,872/arm needs 15,744 core accounts (158,000-account proxy).
Decision rule (E3_observed, DEFF 1.1, CI rule), 7,872/arm, γ=20%: scale 7.6% / extend 91.9% / stop 0.5%.
80,000/arm = first qualifying grid point for v2 fully loaded contribution, not an exact minimum; unadjusted not established through 160,000/arm.
Purpose: learning, launch and harm detection — not profit proof. SE(γ̂) ≈ 6.8 pp vs a 4.0 pp gap to break-even.
[DECISION NEEDED: maximum number of extensions and cost per extension]
```

Ledger rows added (slide, source key, type, displayed):

- `13` · `v4_addons/results/yardstick.json::numbers.deff_default.value` · assumed · `1.1`
- `13` · `v4_addons/results/yardstick.json::numbers.v2_followup_retention.value` · assumed · `90%`
- `13` · `v4_addons/results/yardstick.json::numbers.e4_effect_power_7872_deff1p1.value` · simulated · `76.0%`
- `13` · `v4_addons/results/yardstick.json::numbers.e4_profit_power_7872_deff1p1.value` · simulated · `25.4%`
- `13` · `v4_addons/results/yardstick.json::numbers.max_per_arm_one_list.value` · assumed · `5,000`
- `13` · `v4_addons/results/yardstick.json::numbers.e4_effect_power_5000_deff1p1.value` · simulated · `55.6%`
- `13` · `v4_addons/results/yardstick.json::numbers.e4_profit_power_5000_deff1p1.value` · simulated · `17.9%`
- `13` · `v4_addons/results/yardstick.json::numbers.list_size.value` · assumed · `10,000`
- `13` · `v2_work/final_metrics.json::pilot_calibration.spec.planning_portfolio_calibration_proxy` · assumed · `158,000`
- `13` · `v2_work/final_metrics.json::protocol.financial_assumptions.prevention` · assumed · `20%`
- `13` · `v4_addons/results/yardstick.json::numbers.dq_7872_g20_p_scale.value` · simulated · `7.6%`
- `13` · `v4_addons/results/yardstick.json::numbers.dq_7872_g20_p_extend.value` · simulated · `91.9%`
- `13` · `v4_addons/results/yardstick.json::numbers.dq_7872_g20_p_stop.value` · simulated · `0.5%`
- `13` · `v4_addons/results/yardstick.json::numbers.se_gamma_hat_difference_scaled.value` · simulated · `6.8`
- `13` · `v4_addons/results/yardstick.json::numbers.gap_assumption_to_break_even.value` · simulated · `4.0`

WP7 retirements reversed: C0137, C0139 (tokens kept by the new text).

Note: WP7 retired C0137 (`80,000`) and C0139 (`160,000`); the D4 text keeps both tokens (grid wording / "not established through `160,000`"), so they are retained. `80%` (C0138) stays via the footer. Fifteen new distinct tokens added.

### Slide 12 — text element 21

Length 150 → 214 characters (42.7%) **FLAG > 15%**.

**Exact text before**
```text
[D1, M5–M6] Editable scenario sensitivity, not a confidence interval. Prevention is assumed; break-even holds all other base assumptions fixed.     12
```
**Exact text after**
```text
[D1, M5–M6, M9] Prior-integrated net at the frozen 10% threshold: P(net>0)=17%–93% across assumed prevention priors; 69% under Beta(6,24), centered on 20%. Sensitivity, not a CI or EMPC; no treatment labels.     12
```

Ledger rows added (slide, source key, type, displayed):

- `12` · `v3_addons/results/wp3_roi_band.json::band.lower` · simulated · `17%`
- `12` · `v3_addons/results/wp3_roi_band.json::band.upper` · simulated · `93%`
- `12` · `v3_addons/results/wp3_roi_band.json::band.central` · simulated · `69%`
- `12` · `v3_addons/results/wp3_roi_band.json::priors.1.a` · assumed · `6`
- `12` · `v3_addons/results/wp3_roi_band.json::priors.1.b` · assumed · `24`

Note: `10%`, `20%` and `12` already have slide-12 rows; five new distinct tokens. Keep the exact wording "Sensitivity, not a CI or EMPC."

### Slide 5 (optional) — text element 2

Length 113 → 160 characters (41.6%) **FLAG > 15%**.

**Exact text before**
```text
Value-aware triage adds higher-bill accounts and drops lower-bill ones—not a causal claim about who will respond.
```
**Exact text after**
```text
Value-aware triage is not a response model. EM is a label-shift diagnostic only; stable class-conditionals are unverified and day-60 labels remain ground truth.
```

Note: no new distinct token: `60` already has a slide-5 row

### Slide 15 (optional) — text element 4

Length 178 → 193 characters (8.4%).

**Exact text before**
```text
[M1] scikit-learn: evaluation and calibration.
[M2] LightGBM: local CPU boosting.
[M5] Saerens et al. (2002): prior adjustment.
[M6] Elkan (2001): costs / known-prior correction.
```
**Exact text after**
```text
[M1] scikit-learn: evaluation and calibration.
[M2] LightGBM: local CPU boosting.
[M5] Saerens et al. (2002): prior adjustment; abstract-only.
[M6] Elkan (2001): costs / known-prior correction.
```

**Right block before**
```text
[M3] XGBoost; [M4] CatBoost: comparators.
[M7] Deng et al. (2013): pre-period adjustment.
[M8] Neslin et al. (2006): historical churn protocol.
No matched AUC ceiling or measured CUPED claimed.
```
**Right block after**
```text
[M3] XGBoost; [M4] CatBoost: comparators.
[M7] Deng et al. (2013): pre-period adjustment.
[M8] Neslin et al. (2006): historical churn protocol.
[M9] EMP source: assumed Beta(6,14) default.
```

Ledger rows added (slide, source key, type, displayed):

- `15` · `v3_addons/results/wp3_roi_band.json::priors.0.a` · assumed · `6`
- `15` · `v3_addons/results/wp3_roi_band.json::priors.0.b` · assumed · `14`

Note: M5 abstract-only wording (no token); M9 line adds tokens `6` and `14` (not previously on slide 15). Drops the sentence "No matched AUC ceiling or measured CUPED claimed." to hold the line count; flag for human review.

### References — M9 append (only with option C)

Exactly the block in `v3_addons/INTEGRATION_PROPOSAL.md` §4 ("V3 SUPPORTING ANALYSIS — APPLY ONLY IF OPTION C IS APPROVED … [M9] EMP package contributors …"); `references.txt` is otherwise untouched. Any edit changes its hash → delivery QA refresh. Keep M5 abstract-only wording; the slide-12 footer must keep the exact phrase **"Sensitivity, not a CI or EMPC."**

**C risks.** Medium: reference-page typography (M9 block ≈ 8 lines), the slide-15 right block drops one sentence to keep its line count, prevention remains unidentified, and the prior band must never be read as a confidence interval. Slide 5 wording is optional and adds no ledger row.

## Option R

B' plus full regeneration of every model-dependent number after a Track M ADOPT-CONFIRMED (M6). Regenerated ledger not available until M6 runs.

- Slides touched: 11, 13
- Ledger impact: 0 retired, 18 added → 296 rows; sha256 `759383e8033c3f9b29974ffde6ba1e519f65f89a0417625c7cc4d92ae2e3583d`
- Time estimate [A]: 4.0 day(s)
- Pre-condition: Track M reaches `ADOPT-CONFIRMED` at M5 and M6 produces the regenerated-numbers diff; the human reviews that diff (H3b) before any deck edit. Until then R is B′.
- Risks: every model-dependent number in the deck, PDF, notebook outputs and ledger changes (see `M0_dependency_map.md` once M0 runs); calendar hard freeze 18 Nov; third use of the test split must be disclosed.

### Slide 11 — text element 3

Length 151 → 224 characters (48.3%) **FLAG > 15%**.

**Exact text before**
```text
2% deployment churn
20% of would-be churners
prevented
6 months × 60% margin
$1 per contact; $5k fixed
No blanket subsidy
Net 95% interval: $2.8k–$4.7k
```
**Exact text after**
```text
2% deployment churn
20% of would-be churners
prevented
6 months × 60% margin
$1 per contact; $5k fixed
No blanket subsidy
Net 95% interval at 20% prevention: $2.8k–$4.7k. Prior-integrated 5th percentile (Beta(6,24)): −$6.2k.
```

Ledger rows added (slide, source key, type, displayed):

- `11` · `v3_addons/results/wp3_roi_band.json::priors.1.a` · assumed · `6`
- `11` · `v3_addons/results/wp3_roi_band.json::priors.1.b` · assumed · `24`
- `11` · `v3_addons/results/wp3_roi_band.json::priors.1.closed_form.net_5pct` · simulated · `−6.2k`

Note: tokens `20%`, `95%`, `2.8k`, `4.7k` already have slide-11 rows (C0092, C0097, C0098, C0099) and are kept; three new distinct tokens added

### Slide 13 — text element 4

Length 219 → 790 characters (260.7%) **FLAG > 15%**.

**Heading before**
```text
Binary learning ≠ profit proof
```
**Heading after**
```text
Capacity ≠ profit proof
```

**Exact text before**
```text
Calibration simulation (planning proxy):
adjusted contribution needs 80,000/arm;
unadjusted not 80% powered through
160,000/arm. No validated longitudinal
CUPED or household-clustered power.
Re-estimate using live data.
```
**Exact text after**
```text
WP1 E4 target: variable profit, startup excluded, DEFF 1.1. v2 80,000: fully loaded, startup included, 90% follow-up. Not comparable; no reduction claimed.
E4 at DEFF 1.1 — 7,872/arm: 76.0% gross / 25.4% variable profit; 5,000/arm: 55.6% / 17.9%.
One 10,000-account list gives at most 5,000/arm; 7,872/arm needs 15,744 core accounts (158,000-account proxy).
Decision rule (E3_observed, DEFF 1.1, CI rule), 7,872/arm, γ=20%: scale 7.6% / extend 91.9% / stop 0.5%.
80,000/arm = first qualifying grid point for v2 fully loaded contribution, not an exact minimum; unadjusted not established through 160,000/arm.
Purpose: learning, launch and harm detection — not profit proof. SE(γ̂) ≈ 6.8 pp vs a 4.0 pp gap to break-even.
[DECISION NEEDED: maximum number of extensions and cost per extension]
```

Ledger rows added (slide, source key, type, displayed):

- `13` · `v4_addons/results/yardstick.json::numbers.deff_default.value` · assumed · `1.1`
- `13` · `v4_addons/results/yardstick.json::numbers.v2_followup_retention.value` · assumed · `90%`
- `13` · `v4_addons/results/yardstick.json::numbers.e4_effect_power_7872_deff1p1.value` · simulated · `76.0%`
- `13` · `v4_addons/results/yardstick.json::numbers.e4_profit_power_7872_deff1p1.value` · simulated · `25.4%`
- `13` · `v4_addons/results/yardstick.json::numbers.max_per_arm_one_list.value` · assumed · `5,000`
- `13` · `v4_addons/results/yardstick.json::numbers.e4_effect_power_5000_deff1p1.value` · simulated · `55.6%`
- `13` · `v4_addons/results/yardstick.json::numbers.e4_profit_power_5000_deff1p1.value` · simulated · `17.9%`
- `13` · `v4_addons/results/yardstick.json::numbers.list_size.value` · assumed · `10,000`
- `13` · `v2_work/final_metrics.json::pilot_calibration.spec.planning_portfolio_calibration_proxy` · assumed · `158,000`
- `13` · `v2_work/final_metrics.json::protocol.financial_assumptions.prevention` · assumed · `20%`
- `13` · `v4_addons/results/yardstick.json::numbers.dq_7872_g20_p_scale.value` · simulated · `7.6%`
- `13` · `v4_addons/results/yardstick.json::numbers.dq_7872_g20_p_extend.value` · simulated · `91.9%`
- `13` · `v4_addons/results/yardstick.json::numbers.dq_7872_g20_p_stop.value` · simulated · `0.5%`
- `13` · `v4_addons/results/yardstick.json::numbers.se_gamma_hat_difference_scaled.value` · simulated · `6.8`
- `13` · `v4_addons/results/yardstick.json::numbers.gap_assumption_to_break_even.value` · simulated · `4.0`

WP7 retirements reversed: C0137, C0139 (tokens kept by the new text).

Note: WP7 retired C0137 (`80,000`) and C0139 (`160,000`); the D4 text keeps both tokens (grid wording / "not established through `160,000`"), so they are retained. `80%` (C0138) stays via the footer. Fifteen new distinct tokens added.

## Recommendation [R]

**B′.** It fixes the two integrity findings with the smallest surface: slide 11 states the condition (prevention = 20%) and shows the central-prior downside (−$6.2k vs the conditional $2.8k–$4.7k); slide 13 bridges the targets and uses one DEFF (76.0% / 25.4% at 7,872/arm; 55.6% / 17.9% at 5,000/arm). C only if the prior band earns its page space; R only after a Track M ADOPT-CONFIRMED. A remains safe.

**STOP here.** No deliverable, reference, notebook, protocol or submission action is authorised by this proposal. The human writes `gates/H3_OPTION.txt`.
