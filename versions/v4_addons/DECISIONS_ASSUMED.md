# v4 — decisions assumed (section 3 of the v4 brief)

Status of every row: **DEFAULT_ASSUMED** unless `v4_addons/gates/H0_DECISIONS.md` (human-created) overrides it. Checked at the start of every card; no such file existed when this table was written (2026-10-31).

| # | Question (review §7) | Default applied [R] | Rationale | Status |
|---|---|---|---|---|
| 1 | Authoritative sample-size yardsticks | Exactly three, each named: **7,872/arm = learning-pilot design point (binary churn, 20% relative reduction)**; **40,000/arm = first qualifying grid point for variable profit (WP1 E4, γ=20%, DEFF 1)**; **80,000/arm = v2 fully loaded first qualifying grid point**. 160,000 appears only as "unadjusted not established through 160,000". | Each answers a different question; none replaces another. | DEFAULT_ASSUMED |
| 2 | Operating case | **5,000/arm (one 10k list)** is the feasible operating case; 7,872/arm needs 15,744 core accounts (158,000-account planning proxy). | WP1 capacity conclusion. | DEFAULT_ASSUMED |
| 3 | DEFF | **One DEFF = 1.1 everywhere** (household clustering assumed; ICC unverified [A]). DEFF 1.0 and 1.25 shown only in the YARDSTICK sensitivity table. | Removes the 1.0 vs 1.1 incoherence. | DEFAULT_ASSUMED |
| 4 | Slide 11 interval | Relabel as conditional (exact text in D4). | Highest integrity value, lowest risk. | DEFAULT_ASSUMED |
| 5 | Monitor | **Diagnostic only**; keep M5 abstract-only wording; no hold/proceed implication. | WP5 acceptance failures. | DEFAULT_ASSUMED |
| 6 | "80,000" wording | "first qualifying grid point; not an exact minimum". | Grid is coarse; at 80,000 the adjusted power row is above 0.80 (0.9525 descriptive test rows; 0.9725 planning rows). | DEFAULT_ASSUMED |
| 7 | Queue table | Relabel as **queue composition / feasibility**, not value triage (lift ≈ 1.0; D6). | Value shares track counts. | DEFAULT_ASSUMED |
| 8 | WP8 | Final; model track for the *WP8 challenger* stays closed. | Preregistered negative. | DEFAULT_ASSUMED |
| 9 | Integration option | **B′** (slide 11 relabel + slide 13 bridge). If Track M is adopted: **R** = B′ + full regeneration. | Review ranks B′ above B. | DEFAULT_ASSUMED |
| 10 | Notebook reproducibility | Do not edit frozen cells; provide a supplement (D5). | Preserves audit state. | DEFAULT_ASSUMED |

Additional human decisions flagged inside cards as `[DECISION NEEDED: …]`: extension budget (D4), Floor contact cost (D6), harm-gate action and owner (D6), Track M thresholds (M2, gate H1).

Track M itself reopens the model track in a different form; that is a human decision (gate H1). Until `gates/H1_APPROVED.txt` exists, only M0 (feasibility, no fitting), M1 (non-test learning curve) and the M2 draft are executed; nothing is sealed and no test row is touched.
