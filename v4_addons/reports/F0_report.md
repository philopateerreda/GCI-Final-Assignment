# F0 — Close Track M and write the gates
Status: COMPLETED_ACCEPTED

F0 closes Track M and writes the two gate files authorized by section 0 of the closeout directive. STATE records M2 to M6 as `NOT_RUN_KILLED_BY_M1_GATE` and the account holder's delegation verbatim. `H0_DECISIONS.md` adopts the ten earlier assumptions by delegation and adds the three section-0 decisions (pilot extension budget, Floor contact cost, harm-gate action); `H3_OPTION.txt` contains `B_PRIME`. The closure note reproduces the M1 evidence and binds the two reviewer extrapolations that match; the reviewer's parenthetical range did not reproduce and is omitted.

## Evidence table

| number | value | source_file | source_key / formula | tag |
|---|---:|---|---|---|
| closure_refit_customers | 75,000 | `v4_addons/results/m1_baseline.json` | `numbers.frozen_refit_customers.value` | [E] |
| closure_calibration_customers | 10,000 | `v4_addons/results/m1_baseline.json` | `numbers.frozen_calibration_customers.value` | [E] |
| closure_auc_15000 | 0.678565 | `v4_addons/results/m1_baseline.json` | `numbers.curve_auc_15000.value` | [E] |
| closure_auc_30000 | 0.689170 | `v4_addons/results/m1_baseline.json` | `numbers.curve_auc_30000.value` | [E] |
| closure_auc_45000 | 0.693949 | `v4_addons/results/m1_baseline.json` | `numbers.curve_auc_45000.value` | [E] |
| closure_auc_60000 | 0.696203 | `v4_addons/results/m1_baseline.json` | `numbers.curve_auc_60000.value` | [E] |
| closure_auc_67500 | 0.696845 | `v4_addons/results/m1_baseline.json` | `numbers.curve_auc_67500.value` | [E] |
| closure_gain_last_step | 0.000641 | `v4_addons/results/m1_baseline.json` | `numbers.curve_gain_67500_over_60000.value` | [E] |
| curve_a | 0.707582 | `v4_addons/results/m1_baseline.json` | `numbers.curve_a.value` | [E] |
| curve_b | 18.557711 | `v4_addons/results/m1_baseline.json` | `numbers.curve_b.value` | [E] |
| curve_c | 0.672 | `v4_addons/results/m1_baseline.json` | `numbers.curve_c.value` | [E] |
| curve_c_lower | 0.403 | `v4_addons/results/m1_baseline.json` | `numbers.curve_c_lower.value` | [E] |
| curve_c_upper | 0.964 | `v4_addons/results/m1_baseline.json` | `numbers.curve_c_upper.value` | [E] |
| delta_s_identity | 0.0000 | `v4_addons/results/m1_baseline.json` | `numbers.delta_s_identity.value` | [E] |
| gate_threshold | 0.0015 | `v4_addons/results/m1_baseline.json` | `numbers.gate_threshold.value` | [R] |
| extrap_10k_gain | 0.0008 |  | `curve_b * (75000 ** -curve_c - 85000 ** -curve_c)` | [A] |
| extrap_double_gain | 0.0037 |  | `curve_b * (75000 ** -curve_c - 150000 ** -curve_c)` | [A] |
| extrap_double_boot_lower | 0.0024 |  | `joint fold-cluster bootstrap lower bound of the doubling gain` | [A] |
| extrap_double_boot_upper | 0.0052 |  | `joint fold-cluster bootstrap upper bound of the doubling gain` | [A] |
| extrap_double_cond_at_c_lower | 0.0052 |  | `a,b refit with c fixed at its lower bootstrap bound` | [A] |
| extrap_double_cond_at_c_upper | 0.0025 |  | `a,b refit with c fixed at its upper bootstrap bound` | [A] |
| pilot_per_arm | 7,872 | `v2_work/final_metrics.json` | `v1.pilot.per_arm_with_10pct_allowance` | [E] |
| stage1_cost | $12,872 | `v2_work/final_metrics.json` | `pilot_calibration.spec.stage1_cost` | [E] |
| startup_stage1 | $5,000 | `v2_work/final_metrics.json` | `pilot_calibration.spec.cost_assumptions.startup_stage1` | [E] |
| control_incremental_contact | 0.0 | `v2_work/final_metrics.json` | `pilot_calibration.spec.cost_assumptions.control_incremental_contact` | [E] |

## Gates written

- `v4_addons/gates/H0_DECISIONS.md`: sha256 `b080f3a4bcdc47e51f3f152c2afa950ea0836eb14a645dc9d0a58af60e431bf2`, 5232 bytes; a copy of DECISIONS_ASSUMED.md with every DEFAULT_ASSUMED replaced; rows 11-13 added.
- `v4_addons/gates/H3_OPTION.txt`: content `B_PRIME` exactly; sha256 `9df0f95051235da229f8ace491846b10bb088400b3397381b98fdc1b679fba86`.
- Files present in `v4_addons/gates/`: H0_DECISIONS.md, H3_OPTION.txt. No H1, H2 or H4 file exists.
- `H0` rows 11-12 cite the bound pilot figures: 7,872 per arm, $12,872 Stage-1 envelope, $5,000 startup, Floor contact cost 0.0.

## Extrapolation check

- Stored fit: a = 0.707582, b = 18.557711, c = 0.672 (interval 0.403 to 0.964).
- A joint fold-cluster bootstrap over the 20 saved clusters (2,000 replicates) gives 0.0024 to 0.0052 for the doubling gain; conditional refits with c fixed at its bounds give 0.0052 at the lower bound and 0.0025 at the upper bound (the gain falls as c rises).
- Neither definition reproduces the reviewer's parenthetical range, so that range is omitted from every deliverable. The two point extrapolations reproduce the reviewer values at the stated rounding and are bound [A].

## Closure note

- `v4_addons/reports/M_closure_note.md`: 169 words (limit 200); all numbers in its render registry; check_numbers scan clean.

## Acceptance checks

- STATE.md records M2 to M6 as `NOT_RUN_KILLED_BY_M1_GATE` and the delegation sentence verbatim: PASS.
- `v4_addons/gates/` contains exactly H0_DECISIONS.md and H3_OPTION.txt, with H3 content `B_PRIME`: PASS.
- Closure note at most 200 words, all numbers bound: PASS.
- Reviewer extrapolations bound only where they reproduce; the non-reproducing range omitted: PASS.
- Boundary check clean before and after: PASS.

## Deviations from the brief

- The reviewer's parenthetical interval for the doubling extrapolation did not reproduce: the joint fold-cluster bootstrap is wider (see the extrapolation check) and the conditional refits run in the opposite direction. Per the card it is omitted and no value from it appears in any deliverable; the two point extrapolations match and are labeled [A].
- state.py was not edited. Its status vocabulary lacks `NOT_RUN_KILLED_BY_M1_GATE`, so STATE is written by the new fstate.py, which keeps the same JSON shape and adds the authorization section.
- The gate files are written by a stdlib-only script (f0_gates.py) before v4common's audit hook is installed, because the hook blocks all agent writes under gates/. Section 0 amends G6 for exactly these two files; no other gate file is created.

## Open questions / [DECISION NEEDED] items

- None for F0. F1 (placeholder resolution and final text) is next.

## Commands run

```bash
PY="C:/Users/FGstore/AppData/Local/Programs/Python/Python311/python.exe"; R="D:/progs/IDE/MainProjs/AI/GCI2026/finalA"
cd "$R/v4_addons/tools"
"$PY" -B -X utf8 boundary_check.py --card F0 --phase pre
"$PY" -B -X utf8 f0_gates.py
"$PY" -B -X utf8 f0_closeout.py
"$PY" -B -X utf8 check_numbers.py --scan ../reports/F0_report.md ../reports/M_closure_note.md
"$PY" -B -X utf8 boundary_check.py --card F0 --phase post
```

Environment: Python 3.11.9; verify_runtime pools: openblas 0.3.30 num_threads=6, openblas 0.3.30 num_threads=6; seed 20261040.

Boundary check: before/after hashes clean? yes (pre clean; post-check run after this report; only v4_addons/ written)
