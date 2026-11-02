# v4 — decisions adopted by delegation (H0_DECISIONS.md, 2026-10-31)

**Gate file created by the agent on 2026-10-31 under section 0 of the v4 Closeout Directive; G6 is amended for exactly two files (this one and `H3_OPTION.txt`).** The account holder's delegation, quoted verbatim:

> I don't want to take decisions, just tell him what you see is the smartest move.

Source: a verbatim copy of `v4_addons/DECISIONS_ASSUMED.md` with every `DEFAULT_ASSUMED` replaced by `ADOPTED_BY_DELEGATION 2026-10-31`, the stale preamble and closing paragraph refreshed (this file now exists; Track M is closed), and the three decisions not previously tabled added as rows 11-13. No row content was otherwise changed. If the account holder later creates, edits or deletes any gate file, their file wins.

Status of every row: **ADOPTED_BY_DELEGATION 2026-10-31**. This file is the gate; a later edit by the account holder wins. Checked at the start of every card.

| # | Question (review §7) | Default applied [R] | Rationale | Status |
|---|---|---|---|---|
| 1 | Authoritative sample-size yardsticks | Exactly three, each named: **7,872/arm = learning-pilot design point (binary churn, 20% relative reduction)**; **40,000/arm = first qualifying grid point for variable profit (WP1 E4, γ=20%, DEFF 1)**; **80,000/arm = v2 fully loaded first qualifying grid point**. 160,000 appears only as "unadjusted not established through 160,000". | Each answers a different question; none replaces another. | ADOPTED_BY_DELEGATION 2026-10-31 |
| 2 | Operating case | **5,000/arm (one 10k list)** is the feasible operating case; 7,872/arm needs 15,744 core accounts (158,000-account planning proxy). | WP1 capacity conclusion. | ADOPTED_BY_DELEGATION 2026-10-31 |
| 3 | DEFF | **One DEFF = 1.1 everywhere** (household clustering assumed; ICC unverified [A]). DEFF 1.0 and 1.25 shown only in the YARDSTICK sensitivity table. | Removes the 1.0 vs 1.1 incoherence. | ADOPTED_BY_DELEGATION 2026-10-31 |
| 4 | Slide 11 interval | Relabel as conditional (exact text in D4). | Highest integrity value, lowest risk. | ADOPTED_BY_DELEGATION 2026-10-31 |
| 5 | Monitor | **Diagnostic only**; keep M5 abstract-only wording; no hold/proceed implication. | WP5 acceptance failures. | ADOPTED_BY_DELEGATION 2026-10-31 |
| 6 | "80,000" wording | "first qualifying grid point; not an exact minimum". | Grid is coarse; at 80,000 the adjusted power row is above 0.80 (0.9525 descriptive test rows; 0.9725 planning rows). | ADOPTED_BY_DELEGATION 2026-10-31 |
| 7 | Queue table | Relabel as **queue composition / feasibility**, not value triage (lift ≈ 1.0; D6). | Value shares track counts. | ADOPTED_BY_DELEGATION 2026-10-31 |
| 8 | WP8 | Final; model track for the *WP8 challenger* stays closed. | Preregistered negative. | ADOPTED_BY_DELEGATION 2026-10-31 |
| 9 | Integration option | **B′** (slide 11 relabel + slide 13 bridge). If Track M is adopted: **R** = B′ + full regeneration. | Review ranks B′ above B. | ADOPTED_BY_DELEGATION 2026-10-31 |
| 10 | Notebook reproducibility | Do not edit frozen cells; provide a supplement (D5). | Preserves audit state. | ADOPTED_BY_DELEGATION 2026-10-31 |

The `[DECISION NEEDED: …]` items previously flagged in cards D4, D6 and M2 are resolved by rows 11-13 and by the Track M closure below.

## Additional decisions adopted (section 0, 2026-10-31)

The directive's other section-0 choices are already rows 3 (DEFF 1.1), 5 (monitor diagnostic only) and 9 (integration option B', recorded in `H3_OPTION.txt`). The three decisions not previously tabled are:

| # | Question | Decision [R] | Rationale | Status |
|---|---|---|---|---|
| 11 | Pilot extension budget (slide 13 placeholder) | **At most one equal-sized extension cohort, then stop.** Slide 13 carries no dollar figure; the CEO brief carries the bound variable cost (expected treated contacts x $1 = $7,872; startup assumed not to recur [A]). | A second extension would double the cost and still not resolve break-even. | ADOPTED_BY_DELEGATION 2026-10-31 |
| 12 | Floor (control-arm) contact cost | **Not an incremental pilot cost.** Floor fixes occur in both arms, are logged, and the v2 cost spec sets `control_incremental_contact = 0.0`. Counted pilot cost = discretionary outreach to treated accounts only; the Stage-1 envelope $12,872 = 7,872 treated contacts at $1 plus the $5,000 startup. | Consistent with ITT and the $12,872 envelope. | ADOPTED_BY_DELEGATION 2026-10-31 |
| 13 | Harm-gate action | **"If the gate trips: pause discretionary outreach in the treated arm; the Service-Fix Floor continues for everyone; the Company A pilot owner (named at kickoff) reviews before any restart."** No time limits, no personal names. | Role-based, no invented parameters. | ADOPTED_BY_DELEGATION 2026-10-31 |

Track M is closed at the M1 gate (KILL): the frozen model was already refit on all 75,000 non-test rows, so the point prediction of the extra gain is exactly zero against the +0.0015 gate. M2 to M6 are `NOT_RUN_KILLED_BY_M1_GATE`; `H1_APPROVED.txt` and `H2_APPROVED.txt` are not created. Under this closeout no model is fitted, refit, rescored or simulated, no candidate is added, and no new test row is read.
