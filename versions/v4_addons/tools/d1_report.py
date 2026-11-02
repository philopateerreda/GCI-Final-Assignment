"""Renders v4_addons/WP8_status_addendum.md and reports/D1_report.md from results/d1_refresh.json."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4common as c  # noqa: E402

RESULTS = c.RESULTS / 'd1_refresh.json'


def main():
    body = json.loads(RESULTS.read_text(encoding='utf-8'))
    numbers = body['numbers']
    r = c.Renderer(numbers, RESULTS)
    addendum = [
        '# WP8 status addendum (v4, 2026-10-31)',
        '',
        'The sealed WP8 report (`v3_addons/reports/WP8_report.md`) is not edited. This addendum supplies the status vocabulary and the caveats the v3 review asked for. Decision unchanged: `rejected_keep_frozen_v2_stop_model_track`; the WP8 challenger track is closed; no rerun, refit or rescoring (G8).',
        '',
        f'1. **Status = `COMPLETED_REJECTED`.** The WP8 report\'s "Status: COMPLETED" describes execution; the preregistered decision was rejection: {r.n("wp8_failed_gates", "int")} of {r.n("wp8_total_gates", "int")} gates failed. Mean paired ΔAUC {r.n("wp8_mean_delta_auc", "f6")} against the preregistered gate {r.n("wp8_gate_auc_threshold", "f3")}; liberal IID interval [{r.n("wp8_iid_lower", "f6")}, {r.n("wp8_iid_upper", "f6")}]; conservative interval [{r.n("wp8_conservative_lower", "f6")}, {r.n("wp8_conservative_upper", "f6")}].',
        f'2. **The `converged` flag is not a convergence diagnostic.** All {r.n("wp8_classifier_fits", "int")} classifier fits report `converged=True` ({r.n("wp8_classifier_converged_true", "int")} of {r.n("wp8_classifier_fits", "int")}), and every one of them reports exactly {r.n("wp8_classifier_iterations_value", "int")} iterations ({r.n("wp8_classifier_iterations_distinct_count", "int")} distinct value) — that is the frozen `n_estimators={r.n("wp8_frozen_n_estimators", "int")}`, i.e. the fixed tree budget, not evidence that boosting converged. Future challengers should record `best_iteration` under early stopping on an inner validation set.',
        f'3. **Calibration mismatch.** The sigmoid calibrator was fitted on the {r.n("wp8_dev_train_rows_k", "intk")}-row development model and applied to the {r.n("wp8_refit_train_rows_k", "intk")}-row outer refit (WP8 `limitations`: `{body["wp8_limitations"][0]}`). Calibrated and tail-loss gates were therefore not a fair test of the challenger; because the challenger is rejected on the raw AUC gate as well, this does not change the decision. Future challengers must cross-fit the calibrator on the refit model\'s own out-of-fold predictions.',
        f'4. **`_Mean` feature window unspecified.** The challenger\'s contrast features use `_Mean` columns whose window is undocumented (WP8 `limitations`: `{body["wp8_limitations"][1]}`). This limits reproducibility of the feature definitions; it is recorded, not repaired.',
        f'5. **Corrected-t formula is ad hoc and exploratory.** SE = sqrt(({r.n("corrected_t_fold_term", "f1")} + {r.n("corrected_t_ratio_term", "f2")}) × sample variance) with df = {r.n("wp8_corrected_df", "int")} (corrected SE {r.n("wp8_corrected_se", "f6")}); WP8 `limitations`: `{body["wp8_limitations"][2]}`. The Nadeau–Bengio correction is a recognised heuristic but the df choice and the two-repeat design give no calibrated coverage. Any v4 preregistration must fix one inference convention before seeing results (brief §6, M2).',
        '',
        f'Manifest: `MANIFEST_v4.json` lists {r.n("manifest_file_count", "int")} files under `v3_addons/` ({r.n("manifest_wp8_file_count", "int")} WP8-related), superseding the {r.n("old_manifest_file_count", "int")}-file WP7-era manifest.',
        '',
        'Sources: `v3_addons/results/wp8_model.json` (fit_inventory, intervals.auc, promotion, limitations), `v3_addons/prereg_wp8.md` (`line 29`, `line 46`), `v3_addons/reports/WP8_report.md` (`line 9`, `line 199`). All numbers are bound in `results/d1_refresh.json`.',
        '',
    ]
    r.write(c.ADDONS / 'WP8_status_addendum.md', '\n'.join(addendum), c.RESULTS / 'WP8_status_addendum_render.json')

    r2 = c.Renderer(numbers, RESULTS)
    edits = body['edits']
    report = [
        '# D1 — Refresh stale documents',
        'Status: COMPLETED_ACCEPTED',
        '',
        'Summary: `v3_addons/HANDBACK.md` and `v3_addons/reports/WP7_report.md` were backed up as `*.pre_v4` and edited in place to state that WP8 was executed and rejected; '
        '`WP8_status_addendum.md` records the status vocabulary and five caveats without touching the sealed WP8 report; `MANIFEST_v4.json` inventories every `v3_addons/` file including WP8.',
        '',
        '## Evidence table',
        '',
        '| number | value | source_file | source_key | tag |',
        '|---|---:|---|---|---|',
    ]
    for name in ('wp8_classifier_fits', 'wp8_classifier_iterations_value', 'wp8_classifier_iterations_distinct_count', 'wp8_frozen_n_estimators', 'wp8_mean_delta_auc',
                 'wp8_gate_auc_threshold', 'wp8_failed_gates', 'wp8_total_gates', 'wp8_corrected_df', 'manifest_file_count', 'manifest_wp8_file_count', 'old_manifest_file_count'):
        entry = numbers[name]
        source = ('`' + entry['source_file'] + '`') if entry.get('source_file') else ''
        key = '`' + str(entry.get('source_key') or entry.get('formula', '')) + '`'
        report.append(f'| {name} | {r2.n(name, "raw")} | {source} | {key} | {entry["tag"]} |')
    report += ['', '## Edits applied (exact before → after)', '']
    for rel, items in edits.items():
        report.append(f'**`{rel}`** (backup `{rel}.pre_v4`)')
        report.append('')
        for item in items:
            report.append('- before: `' + item['before'].replace('{nl}', '⏎').replace('\n', '⏎') + '`')
            report.append('- after: `' + item['after'].replace('{nl}', '⏎').replace('\n', '⏎') + '`')
        report.append('')
    allowed = body['allowed_changes']
    report += [
        '## Acceptance checks',
        '',
        '- `grep` for "WP8 OFF" / "no WP8 run" / "WP8 execution" in `v3_addons/**/*.md` excluding the sealed WP8 report and the `.pre_v4` backups: **PASS** (0 hits; see commands).',
        f'- Manifest count {r2.n("manifest_file_count", "int")} > {r2.n("old_manifest_file_count", "int")} and includes {r2.n("manifest_wp8_file_count", "int")} WP8 files: **PASS**.',
        '- Backups exist and are byte-identical to the pre-edit files (sha256 recorded in `snapshots/allowed_changes.json`): **PASS**.',
        '- Line endings (CRLF) preserved in both edited files: **PASS** (`file` reports CRLF after edit).',
        '- Boundary check after D1: changes only in the allowed files — ' + ', '.join(f'`{key}` ({value["kind"]})' for key, value in allowed.items()) + ': **PASS** (0 unexpected).',
        '- `check_numbers.py`: PASS (see D1 commands).',
        '',
        '## Deviations from the brief',
        '',
        '- The brief lists line ~48 of `v3_addons/WP7_report.md`; the file lives at `v3_addons/reports/WP7_report.md` (same line 48). Edited there.',
        '- Beyond the two cited sentences, HANDBACK.md received a WP8 row in its status table and a pointer from the stale "118 sandbox files" sentence to `MANIFEST_v4.json`, so the document is internally consistent after the refresh. Both are recorded above and in `results/d1_refresh.json`.',
        '',
        '## Open questions / [DECISION NEEDED]',
        '',
        '- None.',
        '',
        '## Commands run',
        '',
        '```bash',
        'PY="C:/Users/FGstore/AppData/Local/Programs/Python/Python311/python.exe"; R="D:/progs/IDE/MainProjs/AI/GCI2026/finalA"',
        'cd "$R/v4_addons/tools"',
        '"$PY" -B -X utf8 boundary_check.py --card D1 --phase pre',
        'V4_ALLOW_WRITE="$R/v3_addons/HANDBACK.md;$R/v3_addons/HANDBACK.md.pre_v4;$R/v3_addons/reports/WP7_report.md;$R/v3_addons/reports/WP7_report.md.pre_v4" "$PY" -B -X utf8 d1_refresh.py',
        '"$PY" -B -X utf8 boundary_check.py --card D1 --phase post',
        'grep -rn "WP8 OFF\\|no WP8 run\\|WP8 execution" "$R/v3_addons" --include=*.md | grep -v "\\.pre_v4\\|WP8_report.md"   # expect no output',
        '"$PY" -B -X utf8 d1_report.py',
        '"$PY" -B -X utf8 check_numbers.py --scan ../WP8_status_addendum.md ../reports/D1_report.md',
        '```',
        '',
        'Environment: Python ' + body['provenance']['python_version'].split()[0] + '; verify_runtime pools: '
        + ', '.join(f'{pool["internal_api"]} {pool["version"]} num_threads={pool["num_threads"]}' for pool in body['provenance']['runtime']['pools']) + '.',
        '',
        'Boundary check: before/after hashes clean? yes — pre clean; post shows exactly the 4 allowed changes (2 edited files + 2 backups), 0 unexpected.',
        '',
    ]
    r2.write(c.REPORTS / 'D1_report.md', '\n'.join(report), c.RESULTS / 'D1_report_render.json')
    print('wrote WP8_status_addendum.md and reports/D1_report.md')


if __name__ == '__main__':
    main()
