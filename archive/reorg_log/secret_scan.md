# Secret and PII scan

**Never echo a matched value.** Every finding below is represented by a masked SHA256 fingerprint.

| Type | Matches |
|---|---:|
| `absolute_project_path` | 10000 |
| `absolute_user_path` | 73 |
| `email` | 12 |

- Credential-shaped findings: **0**.
- Files skipped for size: **1** (schema-only treatment; no body printed).
- Applicant-level CSV profiles written without rows: **16**.

## What the scan covered

All `.md`, `.txt`, `.py`, `.json`, `.ipynb`, `.csv` (header only), `.log` and `.pre_v4` files under
the Phase-0 manifest, up to 20 MB per file. Large model/data JSON and NPZ were treated structurally.
The two supplied CSVs were profiled as row count and column count only; no sample rows were written
or printed (H9).

## Files with most findings

| File | Matches |
|---|---:|
| `v3_addons/results/wp8_model.json` | 345 |
| `v3_addons/results/wp8/prereg_receipt.json` | 222 |
| `v3_addons/results/final_new_code_tests.json` | 138 |
| `v3_addons/results/wp5_label_shift.json` | 137 |
| `v3_addons/results/wp8/r0_f0.json` | 114 |
| `v3_addons/results/wp8/r0_f1.json` | 114 |
| `v3_addons/results/wp8/r0_f2.json` | 114 |
| `v3_addons/results/wp8/r0_f3.json` | 114 |
| `v3_addons/results/wp8/r0_f4.json` | 114 |
| `v3_addons/results/wp8/r1_f0.json` | 114 |
| `v3_addons/results/wp8/r1_f1.json` | 114 |
| `v3_addons/results/wp8/r1_f2.json` | 114 |
| `v3_addons/results/wp8/r1_f3.json` | 114 |
| `v3_addons/results/wp8/r1_f4.json` | 114 |
| `v3_addons/results/wp8/cache/r0_f0_outer.json` | 109 |
| `v3_addons/results/wp8/cache/r0_f1_outer.json` | 109 |
| `v3_addons/results/wp8/cache/r0_f2_outer.json` | 109 |
| `v3_addons/results/wp8/cache/r0_f3_outer.json` | 109 |
| `v3_addons/results/wp8/cache/r0_f4_outer.json` | 109 |
| `v3_addons/results/wp8/cache/r1_f0_outer.json` | 109 |

## Interpretation

- No live API key, access token, private-key block or password assignment was found.
- The `absolute_user_path` / `absolute_project_path` hits are historical build paths and file URLs;
  they are stale-by-design after the move and are listed in `PATH_MAP.md`. They are not credentials.
- Email addresses are counted but not echoed; they are disclosure/contact context, not authentication.
- This is a pattern scan, not a guarantee. The G2 audit re-runs it on the push delta.

Full masked rows: `secret_scan.csv`; applicant-level profiles: `applicant_csv_profile.csv`.
