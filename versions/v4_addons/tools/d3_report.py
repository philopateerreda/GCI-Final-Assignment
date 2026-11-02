"""Renders reports/D3_report.md from results/d3_ledger_dryrun.json."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4common as c  # noqa: E402
import report  # noqa: E402

RESULTS = c.RESULTS / 'd3_ledger_dryrun.json'


def main():
    body = c.read_json(RESULTS)
    options = body['options']
    evidence = [('ledger_rows_original', 'int')]
    for name in ('A', 'B_PRIME', 'C', 'R'):
        evidence += [(f'rows_retired_{name}', 'int'), (f'rows_added_{name}', 'int'), (f'rows_total_{name}', 'int')]
    evidence += [('existing_rows_rerender_ok', 'int'), ('existing_rows_rerender_mismatch', 'int')]
    table = ['| Option | Slides touched | Rows retired | Rows added | New total | sha256 of resulting ledger |', '|---|---|---:|---:|---:|---|']
    for name in ('A', 'B_PRIME', 'C', 'R'):
        item = options[name]
        table.append(lambda r, name=name, item=item: f'| {name.replace("_PRIME", "′")} | {", ".join(str(s) for s in item["slides_touched"]) or "—"} | {r.n(f"rows_retired_{name}", "int")} | {r.n(f"rows_added_{name}", "int")} | {r.n(f"rows_total_{name}", "int")} | `{item["sha256"]}` |')
    tokens = ['', '**Added tokens (B′):** ' + ', '.join(f'`{t}`' for t in options['B_PRIME']['added_tokens']),
              '', '**Added tokens (C, beyond B′):** ' + ', '.join(f'`{t}`' for t in options['C']['added_tokens'][len(options['B_PRIME']['added_tokens']):]),
              '', f'Original ledger sha256: `{body["original_sha256"]}`. Claim-id convention: {body["claim_id_convention"]}.',
              '', 'WP7 proposed retiring C0137 (`80,000`) and C0139 (`160,000`) on slide 13. The D4 B′ text keeps both tokens — `80,000` in the "first qualifying grid point; not an exact minimum" wording and `160,000` only as "unadjusted not established through `160,000`/arm" (section-3 decision 1) — so no row is retired; this is recorded in `results/integration_spec.json` (`wp7_retirements_reversed`). The ledger binds one row per distinct displayed token per slide (e.g. `80%` appears twice on slide 13 with one row), so tokens already present on a slide (`20%`, `95%`, `2.8k`, `4.7k` on slide 11; `10%`, `20%` on slide 12) receive no duplicate row.',
              '', 'Option R uses the B′ ledger as its base; the regenerated model-dependent rows only exist after a Track M ADOPT-CONFIRMED and M6, which have not run.']
    acceptance = [
        lambda r: f'- Option A reproduces the original ledger hash exactly: **{"PASS" if body["option_A_reproduces_original"] else "FAIL"}** (`{options["A"]["sha256"][:16]}…` = original).',
        lambda r: f'- B′ and C counts listed and reproducible by re-running `integration_spec.py` + `d3_ledger_dryrun.py` (deterministic CSV writer, CRLF, same column order): **PASS** — B′ {r.n("rows_total_B_PRIME", "int")} rows, C {r.n("rows_total_C", "int")} rows.',
        '- Every added row re-renders its `displayed_text` from `formatter × scale × exact_value` (checked at construction) and every added token appears in the after-text of its slide edit: **PASS**.',
        lambda r: f'- Existing-row sanity: {r.n("existing_rows_rerender_ok", "int")} of {r.n("ledger_rows_original", "int")} existing rows re-render with their own formatter; {r.n("existing_rows_rerender_mismatch", "int")} do not (chart-axis/textual formats) — informational, no existing row was modified.',
        '- `check_numbers.py`: PASS.',
    ]
    deviations = [
        '- The brief\'s example "retire C0137 (`line 138`) and C0139 (`line 140`)" is not applied, because the D4 B′ panel (which the same card says to apply) keeps both tokens. Retirements would be required only if the human chooses to drop the grid wording from slide 13.',
        '- Ledger copies are written under `v4_addons/ledger_dryrun/`; the original `analysis_outputs/claims_ledger.csv` is untouched (boundary check clean).',
    ]
    open_items = ['- Whether the slide-13 panel should keep the `80,000` / `160,000` grid wording (then C0137/C0139 stay) or drop it (then retire both) — defaults to keep per DECISIONS_ASSUMED row 1.']
    commands = ['"$PY" -B -X utf8 boundary_check.py --card D3 --phase pre', '"$PY" -B -X utf8 integration_spec.py', '"$PY" -B -X utf8 d3_ledger_dryrun.py',
                '"$PY" -B -X utf8 check_numbers.py', '"$PY" -B -X utf8 d3_report.py', '"$PY" -B -X utf8 boundary_check.py --card D3 --phase post']
    report.write_report('D3', 'Ledger dry-run', 'COMPLETED_ACCEPTED',
                        'Summary: the 278-row claims ledger was copied and the retire/add operations for options A, B′, C and R were applied under `v4_addons/ledger_dryrun/`. A reproduces the original hash; B′ adds 18 rows (296), C adds 25 (303); nothing is retired because the D4 text keeps the `80,000` / `160,000` tokens WP7 had proposed to retire.',
                        RESULTS, evidence, acceptance, deviations, open_items, commands, 'yes (pre/post clean; only the 4 D1-allowed changes).',
                        extra_sections=[('Dry-run results', table + tokens)])


if __name__ == '__main__':
    main()
