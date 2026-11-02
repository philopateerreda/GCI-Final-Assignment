# D6 — Text blocks and small corrections
Status: COMPLETED_ACCEPTED

Summary: `TEXT_BLOCKS.md` gives copy-ready queue-composition text (lift recomputed and matching section 9), a Floor-cost sentence with its open question, harm-gate action text with an owner placeholder, and a reference-access table; no external file was edited.

## Evidence table

| number | value | source_file | source_key / formula | tag |
|---|---:|---|---|---|
| queue_billing_lift | 1.007 |  | `queue_billing_value_share / queue_billing_count_share` | [E] |
| queue_network_lift | 0.980 |  | `queue_network_value_share / queue_network_count_share` | [E] |
| queue_handset_lift | 0.971 |  | `queue_handset_value_share / queue_handset_count_share` | [E] |
| queue_residual_lift | 1.027 |  | `queue_residual_value_share / queue_residual_count_share` | [E] |
| queue_billing_lift_s9 | 1.007 |  | `round(queue_billing_value_share, 3) / queue_billing_count_share` | [E] |
| queue_network_lift_s9 | 0.979 |  | `round(queue_network_value_share, 3) / queue_network_count_share` | [E] |
| queue_handset_lift_s9 | 0.972 |  | `round(queue_handset_value_share, 3) / queue_handset_count_share` | [E] |
| queue_residual_lift_s9 | 1.027 |  | `round(queue_residual_value_share, 3) / queue_residual_count_share` | [E] |
| queue_total | 2,505 |  | `queue_billing_count + queue_network_count + queue_handset_count + queue_residual_count` | [E] |
| queue_max_abs_lift_deviation_pct | 2.9% |  | `largest |lift - 1| across the four queues, in percent` | [E] |
| stage1_cost | $12,872 | `v2_work/final_metrics.json` | `pilot_calibration.spec.stage1_cost` | [E] |
| stage1_cost_if_floor_paid | $20,744 |  | `stage1_total_enrolled * treated_contact_rate + startup_stage1` | [E] |
| floor_understatement | $7,872 |  | `stage1_cost_if_floor_paid - stage1_cost` | [E] |
| harm_alpha_per_look | 0.005 | `v2_work/final_metrics.json` | `pilot_calibration.spec.decision_gates.one_sided_alpha_per_harm_look` | [E] |
| harm_familywise_alpha | 0.01 |  | `harm_alpha_per_look * harm_look_count` | [E] |
| http_status_blocked | 403 |  | `403` | [E] |
| http_status_ok | 200 |  | `200` | [E] |

## Acceptance checks

- Queue lift recomputed from the published shares and matching section 9 (1.007 / 0.979 / 0.972 / 1.027): **PASS**.
- Replacement label uses only artifact values and states value per account is flat: **PASS**.
- Floor cost sentence states the zero control-contact cost and flags the envelope risk: **PASS** (`[DECISION NEEDED]` present).
- Harm gate keeps the sealed alpha/looks and adds action text with a `[DECISION NEEDED]` owner: **PASS**.
- Reference access confirmed; no edit to `references.txt`: **PASS** (boundary check).

## Deviations from the brief

- The brief expected both HBS links to return 403. They return 403 only to a default scripted client; with a browser user-agent they return 200 and show the cited titles. Recorded as a refinement, not a discrepancy in the references.
- `references.txt` line numbers are current-file positions; the file was not edited.

## Open questions / [DECISION NEEDED] items

- `[DECISION NEEDED]` Floor contact cost: is a control-arm contact free, or does the Stage-1 envelope need to cover it?
- `[DECISION NEEDED]` harm-gate action and owner.
- `[DECISION NEEDED]` extension budget (carried from D4; still open).

## Commands run

```bash
PY="C:/Users/FGstore/AppData/Local/Programs/Python/Python311/python.exe"; R="D:/progs/IDE/MainProjs/AI/GCI2026/finalA"
cd "$R/v4_addons/tools"
"$PY" -B -X utf8 boundary_check.py --card D6 --phase pre
"$PY" -B -X utf8 d6_text_blocks.py
"$PY" -B -X utf8 check_numbers.py --scan ../TEXT_BLOCKS.md ../reports/D6_report.md
"$PY" -B -X utf8 boundary_check.py --card D6 --phase post
```

Environment: Python 3.11.9; verify_runtime pools: openblas 0.3.30 num_threads=6, openblas 0.3.30 num_threads=6; seed 20261035.

Boundary check: before/after hashes clean? yes (pre/post clean; only the 4 D1-allowed changes).
