# D5 — Reproducibility supplement
Status: COMPLETED_ACCEPTED

Summary: `REPRODUCIBILITY.md` lists, for WP1–WP5, the exact command, seed, expected output hashes and the wall-time information actually available; WP2 identities and WP3 closed forms were re-checked in code, WP1/WP5 simulations were not re-run.

## Evidence table

| number | value | source_file | source_key / formula | tag |
|---|---:|---|---|---|
| wp1_seed | 20,261,029 | `v3_addons/results/wp1_power.json` | `provenance.seed` | [E] |
| wp2_seed | 20,261,030 | `v3_addons/results/wp2_evsi.json` | `provenance.seed` | [E] |
| wp3_seed | 20,261,031 | `v3_addons/results/wp3_roi_band.json` | `provenance.seed` | [E] |
| wp4_seed | 20,261,032 | `v3_addons/results/wp4_protocol.json` | `provenance.seed` | [E] |
| wp5_seed | 20,261,033 | `v3_addons/results/wp5_label_shift.json` | `provenance.seed` | [E] |
| wp2_identity_checks_passed | 1 |  | `1 if all six WP2 scenarios satisfy EVSI<=EVPI, EVSI>=0, EVSI=EVPI-regret (1e-6) and centered within 3 MC SE` | [E] |
| wp3_closed_form_checks_passed | 1 |  | `1 if all WP3 closed forms re-derive within 1e-6 (from D0)` | [E] |
| light_checks_wall_seconds | 1.116 |  | `wall time of the WP2 identity + WP3 closed-form re-checks in this run` | [E] |

## Acceptance checks

- Per-WP command, seed, expected output hashes recorded: **PASS**.
- Only light checks executed (WP2 identities, WP3 closed forms); WP1/WP5 simulations not re-run: **PASS**.
- Frozen notebook untouched: **PASS** (boundary check).
- Script hashes match those recorded in each WP's provenance block: **PASS**.

## Deviations from the brief

- Wall times are not recorded in the v3 artifacts; the supplement gives completion-timestamp gaps as upper bounds instead of invented figures.

## Open questions / [DECISION NEEDED] items

- none

## Commands run

```bash
PY="C:/Users/FGstore/AppData/Local/Programs/Python/Python311/python.exe"; R="D:/progs/IDE/MainProjs/AI/GCI2026/finalA"
cd "$R/v4_addons/tools"
"$PY" -B -X utf8 boundary_check.py --card D5 --phase pre
"$PY" -B -X utf8 d5_reproducibility.py
"$PY" -B -X utf8 check_numbers.py --scan ../REPRODUCIBILITY.md ../reports/D5_report.md
"$PY" -B -X utf8 boundary_check.py --card D5 --phase post
```

Environment: Python 3.11.9; verify_runtime pools: openblas 0.3.30 num_threads=6, openblas 0.3.30 num_threads=6; seed 20261034.

Boundary check: before/after hashes clean? yes (pre/post clean; only the 4 D1-allowed changes).
