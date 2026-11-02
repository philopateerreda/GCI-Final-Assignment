# INTEGRATION_DECISIONS_ADDENDUM — final wording for every placeholder (F1)

_v4 Closeout, card F1 · 2026-10-31 · Authority: `gates/H0_DECISIONS.md` rows 11–13 (ADOPTED_BY_DELEGATION 2026-10-31), `gates/H3_OPTION.txt` = `B_PRIME`, and the account holder's delegation quoted in `STATE.md`. Nothing here is applied to the deck: F2 builds the candidate on copies, F3 promotes it or falls back to Option A._

## 1. Placeholders resolved

Three `[DECISION NEEDED: …]` items exist in `INTEGRATION_PROPOSAL_v4.md`; the latter two also appear in `TEXT_BLOCKS.md`. All three are resolved by H0 rows 11–13. None remains in the final slide text.

| # | Placeholder (source) | Final wording and parameter | Where it is used |
|---|---|---|---|
| 1 | Extension budget (proposal; slide 13) | **If inconclusive: at most one equal-sized extension cohort, then stop.** The slide carries no dollar figure. For the CEO brief, one cohort costs 7,872 treated contacts × $1 = $7,872 [A]; the $5,000 startup is assumed not to recur [A]. | slide 13, last line |
| 2 | Is a Floor contact free? (`TEXT_BLOCKS.md` §2) | **The Floor contact is not incremental.** Final sentence: “Stage-1 envelope $12,872 prices 7,872 treated contacts at $1 each plus the $5,000 startup; control-arm (Floor) contacts are costed at $0 because the Floor continues for everyone.” | protocol and CEO brief; slide 13 only if the human asks (H0 row 12) |
| 3 | Harm-gate action and owner (`TEXT_BLOCKS.md` §3) | **“If the gate trips: pause discretionary outreach in the treated arm; the Service-Fix Floor continues for everyone; the Company A pilot owner (named at kickoff) reviews before any restart.”** Role-based; no personal names or time limits. | protocol addendum; not a slide |

### Other section-0 decisions reflected in the final text

- DEFF 1.1 everywhere (H0 row 3): the panel uses `DEFF 1.1` and no other DEFF value.
- Monitor diagnostic only (H0 row 5): the monitor table is not on any slide and no hold/proceed implication is added.
- Option B′ (H0 row 9, `H3_OPTION.txt`): slide 12, slide 5, slide 15 and `references.txt` stay unchanged; no M9 append.

## 2. Final slide 11 text (element 3)

Only the last line of the seven-line box changes.

**Final text after**
```text
2% deployment churn
20% of would-be churners
prevented
6 months × 60% margin
$1 per contact; $5k fixed
No blanket subsidy
Net 95% interval at 20% prevention: $2.8k–$4.7k. Averaged over Beta(6,24), the assumed prevention prior (mean 20%), the fifth percentile of net contribution is −$6.2k.
```

- Length: 151 → 289 characters (+91.4%); **flag > 15%**. The gloss required by F1 cannot fit the original box without growth; the flag is recorded, not removed. F3 must inspect the box visually; the fallback is to let the line wrap and reduce the font only if it overflows — never drop the gloss.
- Ledger: no rows retired, three added (`6`, `24`, `−6.2k`); `20%`, `95%`, `2.8k`, `4.7k` keep their existing slide-11 rows.
- Glosses: `Beta(6,24)` is followed by “the assumed prevention prior (mean 20%)”; “Averaged over” means prior-integrated; the fifth percentile is the downside value of the prior-integrated net distribution. “Net contribution” is defined on slide 12.

## 3. Final slide 13 text (elements 3 and 4)

**Heading after**
```text
Capacity ≠ profit proof
```

**Final panel after**
```text
Pilot target (7,872/arm): variable profit, startup excluded, DEFF 1.1 (design effect). Earlier v2 calibration: 80,000/arm fully loaded, startup included, 90% follow-up. Not comparable; no reduction claimed.
Power simulation (E4) at DEFF 1.1 — 7,872/arm: 76.0% gross effect / 25.4% variable profit; 5,000/arm: 55.6% / 17.9%.
One 10,000-account list gives at most 5,000/arm; 7,872/arm needs 15,744 core accounts (158,000-account proxy).
Decision rule (E3_observed, DEFF 1.1, CI rule), 7,872/arm, γ=20% (assumed relative churn reduction): scale 7.6% / extend 91.9% / stop 0.5%.
80,000/arm: v2 fully loaded contribution — first qualifying grid point; not an exact minimum. Unadjusted not established through 160,000/arm.
Purpose: learning, launch and harm detection — not profit proof. Standard error of γ̂ ≈ 6.8 percentage points vs a 4.0-percentage-point gap to break-even.
If inconclusive: at most one equal-sized extension cohort, then stop.
```

Required content (F1):

| requirement | present in |
|---|---|
| target bridge | line 1: pilot target (7,872/arm; variable profit, startup excluded) vs earlier v2 calibration (80,000/arm fully loaded, startup included, 90% follow-up); “Not comparable; no reduction claimed.” |
| feasibility line | line 3: one 10,000-account list gives at most 5,000/arm; 7,872/arm needs 15,744 core accounts (158,000-account proxy) |
| DEFF 1.1 numbers | line 2: 76.0% / 25.4% at 7,872/arm and 55.6% / 17.9% at 5,000/arm |
| “variable profit, startup excluded” | line 1 |
| 7.6% / 91.9% / 0.5% row labelled `E3_observed, DEFF 1.1, CI rule` | line 4 |
| “first qualifying grid point; not an exact minimum” | line 5 |
| pilot-purpose sentence | line 6: “Purpose: learning, launch and harm detection — not profit proof.” |
| extension decision | line 7: “If inconclusive: at most one equal-sized extension cohort, then stop.” |

- Length: 219 → 941 characters (+329.7%); **flag > 15%**. The panel is 4.3× the original six-line box. The D4 fallback remains: if the panel does not fit, move the decision-rule line and the purpose line to the footer, keeping the target bridge, the `DEFF 1.1` numbers, the feasibility line, the grid wording and the extension line in the panel. F3 decides after the all-15-slide review; no required text is dropped.
- Ledger: no rows retired, fifteen added; WP7 retirements C0137/C0139 are reversed because `80,000` and `160,000` stay on the slide.
- Glosses: `DEFF 1.1 (design effect)`; `E4` is introduced as the power simulation; `v2` as the earlier calibration; `γ=20%` as the assumed relative churn reduction; `E3_observed` is the label of the WP2 decision-rule variant that uses the observed Stage-1 effect (defined in §4; kept verbatim because F1 requires it); `CI rule` is the Scale/Extend/Stop rule printed in the adjacent block; “standard error” and “percentage points” are written out on line 6.

## 4. Term audit — every term on the two edited slides

Status values: **glossed on slide** = the gloss is in the new text; **defined here** = a standard term or a detail carried by this addendum; **self-evident** = already defined on another slide or by the surrounding text.

| term | where | status | definition / gloss |
|---|---|---|---|
| `net contribution` | slide 11 line 7 | self-evident | Defined on slide 12 as net contribution in USD-equivalent thousands (retained contribution minus contact and fixed costs). |
| `95% interval` | slide 11 line 7 | defined here | Simulation interval under the stated assumptions; not a confidence interval and not a forecast (the slide-11 and slide-12 footers already say so). |
| `Beta(6,24)` | slide 11 line 7 | **glossed on slide** | Assumed prevention prior with mean `20%`; the mean is (6)/(6+24). |
| `Averaged over` | slide 11 line 7 | **glossed on slide (rewording)** | Prior-integrated: the net distribution is averaged over the assumed prevention prior. |
| `fifth percentile` | slide 11 line 7 | defined here | Downside value of the prior-integrated net distribution (lower tail); the slide value `−$6.2k` is that percentile. |
| `Pilot target` | slide 13 line 1 | self-evident | The design point the pilot is sized for, `7,872` per arm. |
| `variable profit, startup excluded` | slide 13 line 1 | **glossed on slide** | Contribution net of the `$1` variable contact cost, with the startup excluded (G5 vocabulary). |
| `DEFF 1.1 (design effect)` | slide 13 lines 1, 2, 4 | **glossed on slide** | Design effect: variance inflation from household clustering; `1.1` assumed (H0 row 3). |
| `Earlier v2 calibration` | slide 13 line 1 | **glossed on slide** | The frozen v2 analysis behind this deck: fully loaded, startup included, `90%` follow-up. |
| `fully loaded` | slide 13 line 1 | self-evident given the startup clause | After all costs, including the startup and fixed costs. |
| `startup` | slide 13 line 1 | self-evident from slide 11 | The `$5,000` fixed cost shown on slide 11. |
| `account proxy` | slide 13 line 3 | self-evident | The planning portfolio size used to check that core enrolment fits; stated on slide 13 element 2. |
| `Power simulation (E4)` | slide 13 line 2 | **glossed on slide** | WP1's power simulation at the stated DEFF; gross-effect and variable-profit power are separate. |
| `gross effect` | slide 13 line 2 | self-evident | Effect on churn or retention before costs. |
| `Decision rule (E3_observed, DEFF 1.1, CI rule)` | slide 13 line 4 | label + glosses | `E3_observed` is the WP2 decision-quality variant that uses the observed Stage-1 effect; `CI rule` is the Scale/Extend/Stop rule printed in the adjacent block. The label is kept verbatim because F1 requires it. |
| `γ=20%` | slide 13 line 4 | **glossed on slide** | Assumed relative churn reduction used by the power and decision simulations. |
| `scale / extend / stop` | slide 13 line 4 | self-evident | Defined by the Scale / Extend / Stop block on the same slide (element 6, unchanged). |
| `First qualifying grid point; not an exact minimum` | slide 13 line 5 | **glossed on slide** | The smallest simulated grid cell that meets the criterion; the grid is coarse, so it is not an exact minimum. |
| `Standard error of γ̂` | slide 13 line 6 | **glossed on slide** | Standard deviation of the estimate of γ that the pilot would produce. |
| `percentage points` | slide 13 line 6 | **glossed on slide** | Absolute difference between two percentages. |
| `equal-sized extension cohort` | slide 13 line 7 | **glossed on slide** | One additional cohort of the same design and size, enrolled only if Stage 1 is inconclusive. |

## 5. Ledger dry-run for the final text

`tools/d3_ledger_dryrun_final.py` is a copy of the D3 generator; the D3 script and its outputs are unchanged. It applies the final B′ edits and writes `ledger_dryrun/claims_ledger_A_final.csv` and `ledger_dryrun/claims_ledger_B_PRIME_final.csv`.

| item | value |
|---|---:|
| rows retired | 0 |
| rows added | 18 |
| rows changed | 0 |
| rows total (final) | 296 |
| rows total (D3 B′) | 296 |
| ledger sha256 | `759383e8033c3f9b29974ffde6ba1e519f65f89a0417625c7cc4d92ae2e3583d` |
| Option A reproduces the original sha256 | yes — `b4dce03b43f6bd1b9ef3142759e0cb88682527af2f9f8824902521d88729c5b4` |

- The final ledger is byte-identical to the D3 B′ dry-run: the final wording changed prose only, no added token changed, so rows changed = 0 and the hash is the same.
- Option A (no edits) reproduces the original 278-row ledger hash.
- Option C and Option R were not re-run: `H3_OPTION.txt` selects B′; C is not adopted and R needs M6.

## 6. What this addendum does and does not authorise

- The final text is fixed for F2 and F3 only; the frozen deck, notebook, PDF and `references.txt` are untouched.
- No model was fitted, refit, rescored or simulated; no test row was read; no candidate was added.
- No slide 12, slide 5, slide 15 or M9 content is applied (Option C not selected).
- The monitor table stays “NOT OPERATIONAL — draft” and is not on any slide.
- No submission step is taken; H4 is the human's.
