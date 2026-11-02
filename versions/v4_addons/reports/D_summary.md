# TRACK D SUMMARY — status, open decisions and check outputs

_v4 Track D, card D8 · 2026-10-31 · summary only; no deliverable was edited and no analysis was run._

## Project status (one line)

**Model track rejected (WP8); monitor non-operational (WP5); integration unapproved (WP7); frozen v2 remains the submission.**

## Card status D0–D7

| Card | Deliverable | Status | Outcome |
|---|---|---|---|
| D0 | `results/d0_checks.json` | COMPLETED_ACCEPTED | Hashes match; section-9 checks reproduced, with one SE-convention discrepancy acknowledged. |
| D1 | `WP8_status_addendum.md, MANIFEST_v4.json` | COMPLETED_ACCEPTED | Two stale v3 documents refreshed with backups; status addendum and manifest written. |
| D2 | `YARDSTICK.md` | COMPLETED_ACCEPTED | Yardstick sheet built; two definition discrepancies reported, not tuned. |
| D3 | `ledger_dryrun/` | COMPLETED_ACCEPTED | Ledger dry-run for all four options; no rows retired. |
| D4 | `INTEGRATION_PROPOSAL_v4.md` | COMPLETED_ACCEPTED | Integration proposal written; one option recommended; three decision placeholders. |
| D5 | `REPRODUCIBILITY.md` | COMPLETED_ACCEPTED | Reproducibility supplement for all work packages; identity and closed-form checks passed. |
| D6 | `TEXT_BLOCKS.md` | COMPLETED_ACCEPTED | Text blocks for queue composition, Floor cost, harm gate and reference access. |
| D7 | `MONITOR_WRAPUP.md` | COMPLETED_ACCEPTED | Break-even prior replayed from the exact functions; monitor rule rewritten as exclusive states. |

## Open [DECISION NEEDED] items

1. **π* definition — startup included vs excluded** (D2, D7). The recorded 1.546417% is the startup-included crossing; the startup-excluded alternative is 1.0361%. The choice moves the monitor HOLD boundary by 0.51 pp.
2. **Floor contact cost** (D6). Control-arm contacts are costed at zero, so the Stage-1 envelope is $12,872; if a Floor contact costs the same as a treated one, the envelope becomes $20,744.
3. **Harm-gate action and owner** (D6). Who stops outbound contact, who signs resumption, and what happens to already-scheduled contacts.
4. **Extension budget** (D4). Maximum number of extensions and cost per extension; the WP2 decision simulation gives an extend probability of 91.9% at the design point, so this sets the real envelope of the pilot.

## Gates awaiting the human

| Gate | File | Present | Consequence while closed |
|---|---|---|---|
| H0 | `gates/H0_DECISIONS.md` | no | The three `DECISIONS_ASSUMED.md` rows stay DEFAULT_ASSUMED |
| H1 | `gates/H1_APPROVED.txt` | no | Track M cannot seal its preregistration; no fitting beyond M1 |
| H2 | `gates/H2_APPROVED.txt` | no | No test scoring and no model swap |
| H3 | `gates/H3_OPTION.txt` | no | No integration option selected; the deck keeps its current text |

## Machine checks

### `check_numbers.py` — provenance and scan

```text
check_numbers: 595 bound numbers checked; 0 problems; 1 acknowledged discrepancies
  WARN d0_checks.json:se_gamma_hat_delta_full: section-9 expectation 0.068 not matched; value 0.0605922379589923; acknowledged: the 6.8 pp quote corresponds to SE(p0hat-p1hat)/p0 with p0 held fixed (see se_gamma_hat_difference_scaled); the full two-arm delta method gives 6.06 pp; conclusion unchanged (both exceed the 4.0 pp gap several-fold)
```

[E] 595 bound numbers, 0 problems and 1 acknowledged discrepancy (the D0 SE-convention note; conclusions unaffected) at the time this summary was generated. The scan covers the 6 Track D deliverable documents and their render registries; this card's own registry is added after the table above.

### `boundary_check.py` — write boundary

```text
boundary D8/pre: CLEAN; files=4571; accepted=4; unexpected=0; gates=[]
```

[E] 4,571 files outside `v4_addons/` hashed against the baseline; 4 accepted changes (the D1 in-place edits and their `.pre_v4` backups); 0 unexpected. `gates/` holds 0 files.

## What Track D changed

- New tree: `v4_addons/` (tools, results, reports, snapshots, deliverables).
- In-place: `v3_addons/HANDBACK.md` and `v3_addons/reports/WP7_report.md`, each backed up as `*.pre_v4`; `MANIFEST_v4.json` regenerated.
- Everything else untouched: the frozen notebook, PDF and deck, `references.txt`, `v2_work/`, and the other `v3_addons/` artifacts.

## What Track D did not do

- No test rows read and no model scored, fitted or rescored; the WP8 challenger was never rerun (G2, G8).
- No deck, PDF or notebook edit; WP5 remains `PARTIAL`; the WP7 integration remains unapproved.
- No gate file created: the four gates above are the human's to open.
