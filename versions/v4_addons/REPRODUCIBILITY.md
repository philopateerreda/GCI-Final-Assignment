# REPRODUCIBILITY — supporting analyses WP1–WP5 (v3_addons) and how to re-run them

_v4 Track D, card D5 · 2026-10-31 · the frozen notebook `philopateer.ipynb` is not edited; WP1–WP5 live in `v3_addons/src/` and are reproduced from their hash-bound outputs, not from the notebook._

## Environment (all work packages)

```bash
PY="C:/Users/FGstore/AppData/Local/Programs/Python/Python311/python.exe"   # pinned 3.11; not the py launcher
R="D:/progs/IDE/MainProjs/AI/GCI2026/finalA"
export OPENBLAS_NUM_THREADS=6 OMP_NUM_THREADS=6 MKL_NUM_THREADS=6 NUMEXPR_NUM_THREADS=6
# every script: "$PY" -B -X utf8 <script>   (-B: no bytecode writes; v3 common.py also installs a write hook confined to v3_addons/)
```

Seeds derive from SEED = 20261028 + task index (recorded per work package below). Local CPU only, six threads. The test split (15,000 rows) is never read by WP1–WP5; `row_counts.test_rows_used = 0` where recorded.

## Per work package

| WP | Command | Seed | Main output (sha256) | Wall time |
|---|---|---:|---|---|
| WP1 | `"$PY" -B -X utf8 "$R/v3_addons/src/wp1_power.py"` | 20,261,029 | `wp1_power.json` `1342bb553dfd24e4…` | not recorded in the artifact; start time unknown |
| WP2 | `"$PY" -B -X utf8 "$R/v3_addons/src/wp2_decisions.py"` | 20,261,030 | `wp2_evsi.json` `cd64fe05f11e9749…` | not recorded; ≤ 37.0 min (gap to previous WP completion) |
| WP3 | `"$PY" -B -X utf8 "$R/v3_addons/src/wp3_roi.py"` | 20,261,031 | `wp3_roi_band.json` `96aa9a75869c5307…` | not recorded; ≤ 4.7 min (gap to previous WP completion) |
| WP4 | `"$PY" -B -X utf8 "$R/v3_addons/src/wp4_protocol.py"` | 20,261,032 | `wp4_protocol.json` `1fd31cc4461349db…` | not recorded; ≤ 0.5 min (gap to previous WP completion) |
| WP5 | `"$PY" -B -X utf8 "$R/v3_addons/src/wp5_labelshift.py" --workers 6` | 20,261,033 | `wp5_label_shift.json` `3a4d94fe806c0042…` | not recorded; ≤ 37.2 min (gap to previous WP completion) |

Full expected output hashes (current files; a successful re-run must reproduce these byte-for-byte for deterministic outputs — PNG figures may differ by renderer):

**WP1** — script sha256 `cc9ac2c17be3c32d0c8cc1044467b9c3b0ed74dd0c7feb10e27c74ae8b0043f5` (matches the provenance-recorded hash: True); Python 3.11.9; inputs 19; row counts `{'population': 75000, 'replicates_per_point': 1000, 'selected': 12990, 'simulation_points': 48}`
- `v3_addons/results/wp1_power.json` — 542,362 bytes — `1342bb553dfd24e4697d210d141392f32f0ac8b43f66ea3627db95622d714305`
- `v3_addons/results/wp1_power.csv` — 167,320 bytes — `175374f8c495aa598915568c6d4686cba61bfd26d09f1672bc364bddc0228bea`
- `v3_addons/results/wp1_capacity_mde.csv` — 1,291 bytes — `fb9ea4470f3b77334d09dd4f1ac752609ce17c5ce0cd9f3aaf81c2f11da7f97a`
- `v3_addons/results/wp1_simulation_samples.npz` — 3,627,764 bytes — `b85da7f76a5c7562c3b207bad3b0b109913d62cd8575edf09580bb7753bfe068`
- `v3_addons/figures/wp1_power_curves.png` — 33,113 bytes — `a27cdb509efab749f76d971ef7577888b5b0addde073d4614ea7753915d7cae0`

**WP2** — script sha256 `a5a8eafe627124a74ef13b6398bb436901cb57f27852caecffdf771f0e68c221` (matches the provenance-recorded hash: True); Python 3.11.9; inputs 8; row counts `{'decision_rows': 72, 'pilots_per_scenario': 4096, 'scenarios': 6}`
- `v3_addons/results/wp2_evsi.json` — 60,310 bytes — `cd64fe05f11e974916e461d6f12764cff53ecd7f62fb8a1e461d966611c2e405`
- `v3_addons/results/wp2_decision_quality.csv` — 17,005 bytes — `1ad721f80356881cf37a4e5a1f15f7856760983d9aff0f5b7c1c750879423be0`
- `v3_addons/figures/wp2_decision_map.png` — 33,274 bytes — `ebbb3f677bdc724fbb61b84f31eee054d769b1c74a5c10e89cb9d58b9c3d7650`

**WP3** — script sha256 `ce71605f22204fa3326159ee4194064d298a12c6b8ad5401a0eb9dd39807bd48` (matches the provenance-recorded hash: True); Python 3.11.9; inputs 25; row counts `{'calibration_rows': 10000, 'curve_rows': 480, 'draws_per_prior': 1000000, 'population_rows': 75000, 'priors': 3, 'test_rows_used': 0}`
- `v3_addons/results/wp3_roi_band.json` — 96,482 bytes — `96aa9a75869c53079e1442a26f1f3d08f5261d735e61a5195a658955843a5dd1`
- `v3_addons/results/wp3_net_curve.csv` — 194,136 bytes — `f9148028b1a8158685de1556d82617d4f2750550084463ee88d13305283fabc1`
- `v3_addons/figures/wp3_net_curve.png` — 28,627 bytes — `7f36752025300149e1c6a46b1f5aaa705c4ff1ca89dd0ae3bf75dad40d5c370b`

**WP4** — script sha256 `84d96c8bec305e9d52a1d5f269f4738fc0a7a5a3c5d743435f3890b6fc145aca` (matches the provenance-recorded hash: True); Python 3.11.9; inputs 7; row counts `{'new_estimates': 0, 'quoted_queues': 4}`
- `v3_addons/results/wp4_protocol.json` — 6,653 bytes — `1fd31cc4461349db720ba88de079a0f0f7d15f3963b283b121af6e7af77676e9`
- `v3_addons/protocol_addendum.md` — 2,774 bytes — `9c36323f3823f051022e2445d8ede5937ceadbe04b8553a0d25de887a2ad683b`

**WP5** — script sha256 `c5d7df3f0e47795effc220aa35646e4d6f0d9f4ce018545cc273eca5acbc7f0a` (matches the provenance-recorded hash: True); Python 3.11.9; inputs 78; row counts `{'bootstrap_fits': 5000000, 'calibration_policy': 10000, 'grids': 20, 'original_batches': 10000, 'planning_grid': 251, 'planning_non_test': 75000, 'raw_csv': 10000, 'summary_csv': 20, 'test_rows_used': 0}`
- `v3_addons/results/wp5_label_shift.json` — 1,079,813 bytes — `3a4d94fe806c00421f53688c2000bfb2293ecc16320dbb795d9b8375a8a9338e`
- `v3_addons/results/wp5_label_shift_summary.csv` — 5,719 bytes — `7ff830d7a52f0392d25a9dc66bba4498d62c21d3d9dcfd9cad19b2c99ca929f7`
- `v3_addons/results/wp5_break_even_grid.csv` — 88,767 bytes — `fea512bd2b631e217327c4cbad34101d343f74f55e2ec37411a4dfae11ab4612`
- `v3_addons/results/wp5_calibration_oof.json` — 1,054,830 bytes — `a19d7ecadcc009b07806f3f78b7a4d016473656f0af545e5f102773d818f16b1`
- `v3_addons/figures/wp5_em_recovery.png` — 32,496 bytes — `390f433d202da86091be5389b94f2bdddde38e437a6713a0a816789970daf178`

## What was executed in v4 (light checks only)

- WP2 identities re-checked from `wp2_evsi.json` for all six scenarios: EVSI ≤ EVPI, EVSI ≥ 0, EVSI = EVPI − E[posterior regret] (max identity gap 0.00e+00), centered estimator within 3 MC standard errors (max 1.09 SE): passed = 1.
- WP3 closed forms (P(net>0), E[net], 5th percentile, EVPI for the three Beta priors) re-derived with scipy from G, K and γ* in D0 and compared with `wp3_roi_band.json`: passed = 1 (all gaps < 1e-6; see `results/d0_checks.json`).
- Wall time of these checks: 1.116 s.
- **Not re-run:** WP1 (48 points × 1,000 replicates), WP5 (10,000 batches / 5,000,000 bootstrap fits) and WP2's 4,096-pilot preposterior simulations. Their hash-bound outputs above are the evidence; re-running them is a separate approved scope.

## Relationship to the submitted notebook

- `philopateer.ipynb` reproduces the v1/v2 model, policy and economics (frozen; never "Run All"). It does not contain WP1–WP5 code. If the rubric requires the supporting analyses to be reproducible, cite this file and `v3_addons/src/` rather than editing frozen cells (section-3 decision 10).
- v4 Track D adds no new science: every v4 number is arithmetic on the artifacts listed here (`v4_addons/results/*.json`, checked by `tools/check_numbers.py`).
