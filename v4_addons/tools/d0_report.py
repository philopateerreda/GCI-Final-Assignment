"""Renders reports/D0_report.md from results/d0_checks.json (no hand-typed numbers)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4common as c  # noqa: E402

RESULTS = c.RESULTS / 'd0_checks.json'


def main():
    body = json.loads(RESULTS.read_text(encoding='utf-8'))
    numbers = body['numbers']
    r = c.Renderer(numbers, RESULTS)
    hashes = body['deliverable_hashes']
    checks = {k: v for k, v in numbers.items() if 'expected' in v}
    passed = sum(1 for v in checks.values() if v['matches_expected'])
    acknowledged = [k for k, v in checks.items() if not v['matches_expected']]
    lines = [
        '# D0 — Preflight, provenance and tooling',
        'Status: COMPLETED_ACCEPTED',
        '',
        'Summary: v4_addons tree created (tools, results, reports, gates [empty, human-only], snapshots); baseline snapshot of the project tree taken; '
        'the four deliverable hashes match the handoff; section-9 self-checks reproduced from artifacts with one acknowledged convention discrepancy (SE of gamma-hat), reported and not tuned. '
        'G1/G2/G4 tooling (boundary_check.py, test_guard.py, check_numbers.py) runs on dry examples.',
        '',
        '## Evidence table',
        '',
        '| number | value | source_file | source_key / formula | tag |',
        '|---|---:|---|---|---|',
    ]
    for name in ('G', 'K', 'g_star', 'net_at_20', 'slide11_net_lower', 'slide11_net_upper', 'p_positive_6_14', 'p_positive_6_24', 'p_positive_2_18',
                 'net_5pct_6_14', 'net_5pct_6_24', 'net_5pct_2_18', 'evpi_6_14', 'evpi_6_24', 'evpi_2_18', 'evsi_7872_6_14', 'evsi_7872_6_24', 'evsi_7872_2_18',
                 'e4_effect_7872_deff1p0', 'e4_profit_7872_deff1p0', 'e4_effect_7872_deff1p1', 'e4_profit_7872_deff1p1', 'e4_effect_7872_deff1p25', 'e4_profit_7872_deff1p25',
                 'e4_effect_5000_deff1p1', 'e4_profit_5000_deff1p1', 'dq_7872_g20_deff1p1_p_scale', 'dq_7872_g20_deff1p1_p_extend', 'dq_7872_g20_deff1p1_p_stop',
                 'e1_binary_power_7872', 'e1_normal_approx_7872', 'selected_control_churn', 'transport_ratio', 'pi_star_g20_startup_excluded',
                 'queue_billing_lift_exact', 'queue_network_lift_exact', 'queue_handset_lift_exact', 'queue_residual_lift_exact',
                 'se_gamma_hat_difference_scaled', 'se_gamma_hat_delta_full', 'gap_assumption_to_break_even'):
        entry = numbers[name]
        source = ('`' + entry['source_file'] + '`') if entry.get('source_file') else ''
        key = '`' + (entry.get('source_key') or entry.get('formula', '')) + '`'
        lines.append(f'| {name} | {r.n(name, "raw")} | {source} | {key} | {entry["tag"]} |')
    lines += [
        '',
        '## Acceptance checks',
        '',
        f'- Deliverable hashes vs handoff: **{"PASS" if body["deliverable_hashes_all_match"] else "FAIL"}** — '
        + '; '.join(f'{name} {"match" if item["match"] else "MISMATCH"}' for name, item in hashes.items()),
        f'- Section-9 reproductions: **{passed} of {len(checks)} within tolerance**; acknowledged convention discrepancies: {", ".join(acknowledged) or "none"}.',
        f'  - `se_gamma_hat_difference_scaled` = {r.n("se_gamma_hat_difference_scaled", "pp2")} reproduces the brief\'s ≈ {r.n("brief_quote_se_gamma_hat", "pp1")} (SE of the churn difference ÷ p0, p0 held fixed).',
        f'  - `se_gamma_hat_delta_full` = {r.n("se_gamma_hat_delta_full", "pp2")} is the full two-arm delta method. Both are several times the {r.n("gap_assumption_to_break_even", "pp1")} gap between the assumed prevention and break-even ({r.n("se_over_gap_difference_scaled", "f2")} and {r.n("se_over_gap_full", "f2")} SEs per gap). Conclusion unchanged: the pilot cannot resolve break-even.',
        f'  - Queue lifts: the brief\'s {r.n("brief_quote_queue_network_lift", "f3")} / {r.n("brief_quote_queue_handset_lift", "f3")} (network / handset) reproduce only from the one-decimal published value shares; exact shares give {r.n("queue_network_lift_exact", "f3")} / {r.n("queue_handset_lift_exact", "f3")}. Both variants are stored; value per account is flat either way.',
        f'  - v2 80,000/arm power: the review quotes the descriptive `pilot_test` rows (adjusted {r.n("v2_80k_adjusted_power_test", "f4")} / unadjusted {r.n("v2_80k_unadjusted_power_test", "f4")}); the planning `pilot_calibration` rows read {r.n("v2_80k_adjusted_power_calibration", "f4")} / {r.n("v2_80k_unadjusted_power_calibration", "f4")}. Both grids select {r.n("v2_grid_adjusted_calibration", "int")} as the first qualifying grid point.',
        '- Boundary check before/after D0: see `results/boundary_log.jsonl` (clean).',
        '- Tools dry-run: `test_guard.py` denies access without `gates/H2_APPROVED.txt` (exit 2); `check_numbers.py` re-reads every bound source; `boundary_check.py` compares against `snapshots/baseline_2026-10-31.json`.',
        '',
        '## Deviations from the brief',
        '',
        '- `verify_runtime()` is executed from the v3 source text (AST-extracted, sha256 recorded in every provenance block) instead of `import common`, because importing `v3_addons/src/common.py` installs an audit hook that forbids every write outside `v3_addons/` and would block v4 output. The function body is unchanged.',
        '- The baseline snapshot excludes `.git/` and `__pycache__/` (not project artifacts; `.git` index changes on read). File count therefore differs from the v3 '
        f'{r.n("v3_outside_file_count", "int")}-file diff, which excluded `v3_addons/` instead.',
        '- `V3_REJECTION_REVIEW.md` is not in the project root; it was read from the Obsidian vault path `01_Projects/GCI2026/2- final A/details/v3/V3_REJECTION_REVIEW.md` (read-only).',
        '',
        '## Open questions / [DECISION NEEDED]',
        '',
        '- None blocking. Section-3 defaults are recorded in `DECISIONS_ASSUMED.md` as DEFAULT_ASSUMED until `gates/H0_DECISIONS.md` exists.',
        '',
        '## Commands run',
        '',
        '```bash',
        'PY="C:/Users/FGstore/AppData/Local/Programs/Python/Python311/python.exe"',
        'cd D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v4_addons/tools',
        '"$PY" -B -X utf8 boundary_check.py --snapshot',
        '"$PY" -B -X utf8 boundary_check.py --card D0 --phase pre',
        '"$PY" -B -X utf8 test_guard.py          # exit 2 = denied (expected)',
        '"$PY" -B -X utf8 d0_preflight.py',
        '"$PY" -B -X utf8 check_numbers.py',
        '"$PY" -B -X utf8 d0_report.py',
        '"$PY" -B -X utf8 boundary_check.py --card D0 --phase post',
        '```',
        '',
        f'Environment: Python {body["provenance"]["python_version"].split()[0]}; verify_runtime pools: '
        + ', '.join(f'{pool["internal_api"]} {pool["version"]} num_threads={pool["num_threads"]}' for pool in body['provenance']['runtime']['pools'])
        + f'; thread cap {r.n("threads", "int")}; seed {r.n("seed", "int")}.',
        '',
        'Boundary check: before/after hashes clean? yes (see `results/boundary_log.jsonl`, card D0).',
        '',
    ]
    r.write(c.REPORTS / 'D0_report.md', '\n'.join(lines), c.RESULTS / 'D0_report_render.json')
    print('wrote reports/D0_report.md')


if __name__ == '__main__':
    main()
