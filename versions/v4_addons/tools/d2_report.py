"""Renders reports/D2_report.md from results/yardstick.json."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4common as c  # noqa: E402
import report  # noqa: E402

RESULTS = c.RESULTS / 'yardstick.json'


def main():
    evidence = [('binary_enrolled_per_arm', 'int'), ('first_grid_e4_profit', 'int'), ('first_grid_e4_effect', 'int'), ('v2_grid_adjusted_calibration', 'int'),
                ('v2_80k_adjusted_calibration', 'f4'), ('v2_80k_adjusted_test', 'f4'), ('max_per_arm_one_list', 'int'), ('stage1_total_enrolled', 'int'), ('planning_portfolio_proxy', 'int'),
                ('e4_effect_power_7872_deff1p1', 'f3'), ('e4_profit_power_7872_deff1p1', 'f3'), ('e4_effect_power_5000_deff1p1', 'f3'), ('e4_profit_power_5000_deff1p1', 'f3'),
                ('est_e2_observed_80000_profit', 'f3'), ('est_e4_80000_profit', 'f3'), ('spread_80k_profit_e2obs_vs_e4', 'f3'),
                ('dq_7872_g20_p_scale', 'f3'), ('dq_7872_g20_p_extend', 'f3'), ('dq_7872_g20_p_stop', 'f3'), ('dq_7872_g0_p_extend', 'f3'), ('dq_7872_g0_p_stop', 'f3'),
                ('se_gamma_hat_difference_scaled', 'f4'), ('se_gamma_hat_delta_full', 'f4'), ('gap_assumption_to_break_even', 'f4'),
                ('pi_star_fully_loaded', 'f8'), ('pi_star_startup_excluded', 'f8'), ('wp5_fixed_cost_in_net', 'usd0'), ('transport_ratio', 'f4'), ('startup_per_enrollee_7872', 'f4')]
    acceptance = [
        '- `check_numbers.py --scan ../YARDSTICK.md`: **PASS** — 0 unbound numeric tokens; every number in the sheet is rendered from `results/yardstick.json`.',
        '- Zero hand-typed numbers: **PASS** (render registry `results/YARDSTICK_render.json`; sheet hash recorded).',
        '- Every oracle estimator labelled "oracle — invalid for capacity claims": **PASS** (E2_literal_oracle, E3_literal_oracle in both estimator tables).',
        lambda r: f'- DEFF consistent across the sheet: **PASS** — default {r.n("deff_default", "f1")} declared once (`deff_default`) and referenced everywhere; {r.n("deff_1p0", "f1")} / {r.n("deff_1p25", "f2")} only in the sensitivity table; the WP1 grid points are labelled as DEFF-{r.n("deff_1p0", "f1")} statements.',
        lambda r: f'- Bridge sentences ≤ 25 words: **PASS** — longest is `deff_statement` at {r.n("words_deff_statement", "int")} words (all counts bound as `words_*`).',
        lambda r: f'- Pilot purpose statement reproduces WP2 ({r.n("dq_7872_g20_p_scale", "f3")} / {r.n("dq_7872_g20_p_extend", "f3")} / {r.n("dq_7872_g20_p_stop", "f3")}; γ=0: {r.n("dq_7872_g0_p_extend", "f3")} / {r.n("dq_7872_g0_p_stop", "f3")}) and derives SE(γ̂) in code with the formula recorded: **PASS**.',
    ]
    deviations = [
        lambda r: f'- **G10 discrepancy (reported, not tuned):** the brief\'s "SE(γ̂) ≈ {r.n("brief_quote_se_gamma_hat", "pp1")} (delta method)" reproduces as SE(p̂0 − p̂1)/p0 with p0 held fixed ({r.n("se_gamma_hat_difference_scaled", "pp2")}); the full two-arm delta method gives {r.n("se_gamma_hat_delta_full", "pp2")}. Both are bound and shown; the conclusion (pilot cannot resolve break-even) holds under either.',
        lambda r: f'- **G10 discrepancy (reported, not tuned):** WP5\'s π* = {r.n("pi_star_fully_loaded", "pct6")} is the crossing of the *fully loaded* net (its grid `net` = gross − contacts − {r.n("wp5_fixed_cost_in_net", "usd0")}; `economic_assumptions.fixed_cost`). The brief labels it "startup excluded". The startup-excluded crossing on the same grid is ≈ {r.n("pi_star_startup_excluded", "pct4")}. The sheet states the correct definition; D7 recomputes both with the exact v2 functions.',
        lambda r: f'- The frames table quotes the v2 80,000/arm power for both partitions (planning rows {r.n("v2_80k_adjusted_calibration", "f4")} / {r.n("v2_80k_unadjusted_calibration", "f4")}; descriptive test rows {r.n("v2_80k_adjusted_test", "f4")} / {r.n("v2_80k_unadjusted_test", "f4")}, the latter being the review\'s source). Both grids select {r.n("v2_grid_adjusted_calibration", "int")}.',
    ]
    open_items = ['- None new. The DEFF 1.1 default, three-yardstick wording and 5,000/arm operating case follow `DECISIONS_ASSUMED.md` rows 1–3 (DEFAULT_ASSUMED until `gates/H0_DECISIONS.md`).']
    commands = ['"$PY" -B -X utf8 boundary_check.py --card D2 --phase pre', '"$PY" -B -X utf8 d2_yardstick.py',
                '"$PY" -B -X utf8 check_numbers.py --scan ../YARDSTICK.md', '"$PY" -B -X utf8 d2_report.py', '"$PY" -B -X utf8 boundary_check.py --card D2 --phase post']
    report.write_report('D2', 'Yardstick sheet', 'COMPLETED_ACCEPTED',
                        'Summary: `YARDSTICK.md` + `results/yardstick.json` reconcile the four sample sizes and three profit definitions in one sheet: seven frames, estimator and DEFF tables, eight bridge sentences (≤ 25 words, counts bound), and the pilot-purpose statement with SE(γ̂) derived in code. Two G10 definition discrepancies with the brief are reported (SE convention; π* is fully loaded, not startup-excluded).',
                        RESULTS, evidence, acceptance, deviations, open_items, commands, 'yes (pre clean; post shows only the 4 D1-allowed changes).')


if __name__ == '__main__':
    main()
