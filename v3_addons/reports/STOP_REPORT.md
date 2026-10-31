# Mandatory stop — v3 decision-grade add-ons
Status: BLOCKED [E]; waiting for the human

## Reason
[E] NumPy/SciPy were initialized before common.py applied thread environment variables. Data-free np.show_runtime inspection confirmed both OpenBLAS pools configured for 12 threads, exceeding the six-thread maximum.

[E] The authoritative brief section 1 says any hard-guardrail violation requires a stop and report. WP2–WP7 have not started; WP8 remains OFF.

## Current status
| Package | Status [E] |
|---|---|
| WP0 | BLOCKED: integrity/input checks passed; numerical outputs quarantined for runtime compliance |
| WP1 | BLOCKED: draft numerical grid saved; figure export failed; outputs quarantined |
| WP2 | NOT_STARTED |
| WP3 | NOT_STARTED |
| WP4 | NOT_STARTED |
| WP5 | NOT_STARTED |
| WP6 | NOT_STARTED |
| WP7 | NOT_REACHED |
| WP8 | OFF |

## Other findings
- [E] WP1 ran all 48 n/prevention points but then failed because the concurrently prepared PNG helper was not yet available. No full WP1 completion is claimed.
- [E] The draft report wrote DONE before figure generation. Its status and the affected JSON statuses are now marked BLOCKED.
- [E] Literal Appendix C E2/E3 use latent prevented outcomes, unavailable to actual randomized trials. They are explicitly oracle diagnostics, not valid pilot-capacity claims.
- [E] CSV source scanning filters non-test IDs before parsing numeric V; no test outcomes or values enter a scientific data frame or new metric. The reviewer strict no-read concern is stronger than the brief actual no-new-test-computation rule.
- [E] Full handoff exists; the named concise handoff is missing. No input required training or test-split reconstruction.
- [E] The PNG helper agent was stopped. Its helper source and a validation-only PNG inside src are retained as unfinished drafts.
- [E] All task-owned analytical/background work has stopped; no package was installed and no submission was made.

## Frozen-file integrity
[E] Full content-hash directory diff: 4,246 files before, 4,246 after; 0 additions, 0 removals, 0 modifications outside v3_addons. PASS.
[E] No final deliverable, notebook, references, protocol, execution marker, supplied original or v1 snapshot has changed.

## Required decision
[R] Authorize sandbox-only import-order correction, explicit six-thread launch environment, runtime verification before numerics, helper validation, and compliant WP0/WP1 rerun; or retain the stop.
[R] Keep all current WP1 numbers as unapproved audit drafts; do not put them into the submission or interpret the oracle estimators as observed trial evidence.

## Files created [E]
- AGENTS.md
- reports/STOP_REPORT.md
- reports/WP0_report.md
- reports/WP1_report.md
- results/inventory.json
- results/stop_report.json
- results/wp1_capacity_mde.csv
- results/wp1_power.csv
- results/wp1_power.json
- results/wp1_simulation_samples.npz
- results/wp1_tests.json
- results/write_boundary_before.json
- src/__validation_only__.png
- src/common.py
- src/png_drafts.py
- src/stop_report.py
- src/wp0_preflight.py
- src/wp1_power.py
- tests/seed_determinism_fixture.json
- tests/test_wp1.py

[E] Machine evidence and input fingerprints: ../results/stop_report.json. No work continues without the human response.
