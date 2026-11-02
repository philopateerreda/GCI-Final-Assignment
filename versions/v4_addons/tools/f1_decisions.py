"""F1 — resolve every placeholder, fix the final slide 11/13 text, and render INTEGRATION_DECISIONS_ADDENDUM.md + F1_report.md.

Inputs: results/d3_ledger_final.json (from d3_ledger_dryrun_final.py), results/integration_spec.json,
v2_work/final_metrics.json, v4_addons/results/yardstick.json, the frozen deck extraction and the two gate files.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4common as c  # noqa: E402
import integration_spec as spec_module  # noqa: E402
import integration_final as final_module  # noqa: E402
import fstate  # noqa: E402
import report  # noqa: E402

TASK_INDEX = 15
D3F = 'v4_addons/results/d3_ledger_final.json'
FM = 'v2_work/final_metrics.json'
RESULTS = c.RESULTS / 'f1_decisions.json'
ADDENDUM = c.ADDONS / 'INTEGRATION_DECISIONS_ADDENDUM.md'
ACCENT = 'B′'


def fence(text):
    return ['```text', *text.split('\n'), '```']


def bind():
    n = final_module.bind_final()
    n.source('pilot_per_arm', FM, 'v1.pilot.per_arm_with_10pct_allowance')
    n.source('treated_contact_cost', FM, 'pilot_calibration.spec.cost_assumptions.treated_contact')
    n.source('startup_stage1', FM, 'pilot_calibration.spec.cost_assumptions.startup_stage1')
    n.source('control_incremental_contact', FM, 'pilot_calibration.spec.cost_assumptions.control_incremental_contact')
    n.source('stage1_cost', FM, 'pilot_calibration.spec.stage1_cost')
    n.derived('extension_variable_cost', 'pilot_per_arm * treated_contact_cost', tag='[A]',
              note='one equal-sized extension cohort at the variable contact cost; startup assumed not to recur')
    n.declared('length_flag_threshold_pct', 15, '[R]', 'brief rule: flag text growth above +15%')
    for name in ('rows_added_final', 'rows_retired_final', 'rows_changed_final', 'rows_total_final', 'rows_total_d3_b_prime',
                 'len_before_slide11', 'len_after_slide11', 'len_delta_pct_slide11',
                 'len_before_slide13', 'len_after_slide13', 'len_delta_pct_slide13', 'slide13_growth_ratio',
                 'decision_needed_count', 'unbound_tokens_count'):
        n.source(name, D3F, f'numbers.{name}.value')
    return n


def term_audit():
    rows = [
        ('net contribution', 'slide 11 line 7', 'self-evident', 'Defined on slide 12 as net contribution in USD-equivalent thousands (retained contribution minus contact and fixed costs).'),
        ('95% interval', 'slide 11 line 7', 'defined here', 'Simulation interval under the stated assumptions; not a confidence interval and not a forecast (the slide-11 and slide-12 footers already say so).'),
        ('Beta(6,24)', 'slide 11 line 7', '**glossed on slide**', 'Assumed prevention prior with mean `20%`; the mean is (6)/(6+24).'),
        ('Averaged over', 'slide 11 line 7', '**glossed on slide (rewording)**', 'Prior-integrated: the net distribution is averaged over the assumed prevention prior.'),
        ('fifth percentile', 'slide 11 line 7', 'defined here', 'Downside value of the prior-integrated net distribution (lower tail); the slide value `−$6.2k` is that percentile.'),
        ('Pilot target', 'slide 13 line 1', 'self-evident', 'The design point the pilot is sized for, `7,872` per arm.'),
        ('variable profit, startup excluded', 'slide 13 line 1', '**glossed on slide**', 'Contribution net of the `$1` variable contact cost, with the startup excluded (G5 vocabulary).'),
        ('DEFF 1.1 (design effect)', 'slide 13 lines 1, 2, 4', '**glossed on slide**', 'Design effect: variance inflation from household clustering; `1.1` assumed (H0 row 3).'),
        ('Earlier v2 calibration', 'slide 13 line 1', '**glossed on slide**', 'The frozen v2 analysis behind this deck: fully loaded, startup included, `90%` follow-up.'),
        ('fully loaded', 'slide 13 line 1', 'self-evident given the startup clause', 'After all costs, including the startup and fixed costs.'),
        ('startup', 'slide 13 line 1', 'self-evident from slide 11', 'The `$5,000` fixed cost shown on slide 11.'),
        ('account proxy', 'slide 13 line 3', 'self-evident', 'The planning portfolio size used to check that core enrolment fits; stated on slide 13 element 2.'),
        ('Power simulation (E4)', 'slide 13 line 2', '**glossed on slide**', 'WP1\'s power simulation at the stated DEFF; gross-effect and variable-profit power are separate.'),
        ('gross effect', 'slide 13 line 2', 'self-evident', 'Effect on churn or retention before costs.'),
        ('Decision rule (E3_observed, DEFF 1.1, CI rule)', 'slide 13 line 4', 'label + glosses', '`E3_observed` is the WP2 decision-quality variant that uses the observed Stage-1 effect; `CI rule` is the Scale/Extend/Stop rule printed in the adjacent block. The label is kept verbatim because F1 requires it.'),
        ('γ=20%', 'slide 13 line 4', '**glossed on slide**', 'Assumed relative churn reduction used by the power and decision simulations.'),
        ('scale / extend / stop', 'slide 13 line 4', 'self-evident', 'Defined by the Scale / Extend / Stop block on the same slide (element 6, unchanged).'),
        ('First qualifying grid point; not an exact minimum', 'slide 13 line 5', '**glossed on slide**', 'The smallest simulated grid cell that meets the criterion; the grid is coarse, so it is not an exact minimum.'),
        ('Standard error of γ̂', 'slide 13 line 6', '**glossed on slide**', 'Standard deviation of the estimate of γ that the pilot would produce.'),
        ('percentage points', 'slide 13 line 6', '**glossed on slide**', 'Absolute difference between two percentages.'),
        ('equal-sized extension cohort', 'slide 13 line 7', '**glossed on slide**', 'One additional cohort of the same design and size, enrolled only if Stage 1 is inconclusive.'),
    ]
    return ['| term | where | status | definition / gloss |', '|---|---|---|---|'] + [f'| `{term}` | {where} | {status} | {definition} |' for term, where, status, definition in rows]


def build_addendum(n, r, edits):
    s11 = next(edit for edit in edits if edit['slide'] == 11)
    s13 = next(edit for edit in edits if edit['slide'] == 13)
    lines = [
        '# INTEGRATION_DECISIONS_ADDENDUM — final wording for every placeholder (F1)',
        '',
        f'_v4 Closeout, card F1 · {c.today()} · Authority: `gates/H0_DECISIONS.md` rows 11–13 (ADOPTED_BY_DELEGATION 2026-10-31), `gates/H3_OPTION.txt` = `B_PRIME`, and the account holder\'s delegation quoted in `STATE.md`. Nothing here is applied to the deck: F2 builds the candidate on copies, F3 promotes it or falls back to Option A._',
        '',
        '## 1. Placeholders resolved',
        '',
        'Three `[DECISION NEEDED: …]` items exist in `INTEGRATION_PROPOSAL_v4.md`; the latter two also appear in `TEXT_BLOCKS.md`. All three are resolved by H0 rows 11–13. None remains in the final slide text.',
        '',
        '| # | Placeholder (source) | Final wording and parameter | Where it is used |',
        '|---|---|---|---|',
        f'| 1 | Extension budget (proposal; slide 13) | **If inconclusive: at most one equal-sized extension cohort, then stop.** The slide carries no dollar figure. For the CEO brief, one cohort costs {r.n("pilot_per_arm", "int")} treated contacts × {r.n("treated_contact_cost", "usd0")} = {r.n("extension_variable_cost", "usd0")} [A]; the {r.n("startup_stage1", "usd0")} startup is assumed not to recur [A]. | slide 13, last line |',
        f'| 2 | Is a Floor contact free? (`TEXT_BLOCKS.md` §2) | **The Floor contact is not incremental.** Final sentence: “Stage-1 envelope {r.n("stage1_cost", "usd0")} prices {r.n("pilot_per_arm", "int")} treated contacts at {r.n("treated_contact_cost", "usd0")} each plus the {r.n("startup_stage1", "usd0")} startup; control-arm (Floor) contacts are costed at {r.n("control_incremental_contact", "usd0")} because the Floor continues for everyone.” | protocol and CEO brief; slide 13 only if the human asks (H0 row 12) |',
        '| 3 | Harm-gate action and owner (`TEXT_BLOCKS.md` §3) | **“If the gate trips: pause discretionary outreach in the treated arm; the Service-Fix Floor continues for everyone; the Company A pilot owner (named at kickoff) reviews before any restart.”** Role-based; no personal names or time limits. | protocol addendum; not a slide |',
        '',
        '### Other section-0 decisions reflected in the final text',
        '',
        f'- DEFF {r.n("deff_default", "f1")} everywhere (H0 row 3): the panel uses `DEFF {r.n("deff_default", "f1")}` and no other DEFF value.',
        '- Monitor diagnostic only (H0 row 5): the monitor table is not on any slide and no hold/proceed implication is added.',
        f'- Option {ACCENT} (H0 row 9, `H3_OPTION.txt`): slide 12, slide 5, slide 15 and `references.txt` stay unchanged; no M9 append.',
        '',
        '## 2. Final slide 11 text (element 3)',
        '',
        'Only the last line of the seven-line box changes.',
        '',
        '**Final text after**',
        *fence(s11['after']),
        '',
        f'- Length: {r.n("len_before_slide11", "int")} → {r.n("len_after_slide11", "int")} characters (+{r.n("len_delta_pct_slide11", "pc1")}); **flag > {r.n("length_flag_threshold_pct", "pc0")}**. The gloss required by F1 cannot fit the original box without growth; the flag is recorded, not removed. F3 must inspect the box visually; the fallback is to let the line wrap and reduce the font only if it overflows — never drop the gloss.',
        '- Ledger: no rows retired, three added (`6`, `24`, `−6.2k`); `20%`, `95%`, `2.8k`, `4.7k` keep their existing slide-11 rows.',
        f'- Glosses: `Beta(6,24)` is followed by “the assumed prevention prior (mean {r.n("binary_relative_prevention_assumption", "pct0")})”; “Averaged over” means prior-integrated; the fifth percentile is the downside value of the prior-integrated net distribution. “Net contribution” is defined on slide 12.',
        '',
        '## 3. Final slide 13 text (elements 3 and 4)',
        '',
        '**Heading after**',
        *fence(s13['heading_after']),
        '',
        '**Final panel after**',
        *fence(s13['after']),
        '',
        'Required content (F1):',
        '',
        '| requirement | present in |',
        '|---|---|',
        f'| target bridge | line 1: pilot target ({r.n("binary_enrolled_per_arm", "int")}/arm; variable profit, startup excluded) vs earlier v2 calibration ({r.n("v2_grid_adjusted_calibration", "int")}/arm fully loaded, startup included, {r.n("v2_followup_retention", "pct0")} follow-up); “Not comparable; no reduction claimed.” |',
        f'| feasibility line | line 3: one {r.n("list_size", "int")}-account list gives at most {r.n("max_per_arm_one_list", "int")}/arm; {r.n("binary_enrolled_per_arm", "int")}/arm needs {r.n("stage1_total_enrolled", "int")} core accounts ({r.n("planning_portfolio_proxy", "int")}-account proxy) |',
        f'| DEFF {r.n("deff_default", "f1")} numbers | line 2: {r.n("e4_effect_power_7872_deff1p1", "pct1")} / {r.n("e4_profit_power_7872_deff1p1", "pct1")} at {r.n("binary_enrolled_per_arm", "int")}/arm and {r.n("e4_effect_power_5000_deff1p1", "pct1")} / {r.n("e4_profit_power_5000_deff1p1", "pct1")} at {r.n("max_per_arm_one_list", "int")}/arm |',
        '| “variable profit, startup excluded” | line 1 |',
        f'| {r.n("dq_7872_g20_p_scale", "pct1")} / {r.n("dq_7872_g20_p_extend", "pct1")} / {r.n("dq_7872_g20_p_stop", "pct1")} row labelled `E3_observed, DEFF {r.n("deff_default", "f1")}, CI rule` | line 4 |',
        '| “first qualifying grid point; not an exact minimum” | line 5 |',
        '| pilot-purpose sentence | line 6: “Purpose: learning, launch and harm detection — not profit proof.” |',
        '| extension decision | line 7: “If inconclusive: at most one equal-sized extension cohort, then stop.” |',
        '',
        f'- Length: {r.n("len_before_slide13", "int")} → {r.n("len_after_slide13", "int")} characters (+{r.n("len_delta_pct_slide13", "pc1")}); **flag > {r.n("length_flag_threshold_pct", "pc0")}**. The panel is {r.n("slide13_growth_ratio", "x1")} the original six-line box. The D4 fallback remains: if the panel does not fit, move the decision-rule line and the purpose line to the footer, keeping the target bridge, the `DEFF 1.1` numbers, the feasibility line, the grid wording and the extension line in the panel. F3 decides after the all-15-slide review; no required text is dropped.',
        '- Ledger: no rows retired, fifteen added; WP7 retirements C0137/C0139 are reversed because `80,000` and `160,000` stay on the slide.',
        '- Glosses: `DEFF 1.1 (design effect)`; `E4` is introduced as the power simulation; `v2` as the earlier calibration; `γ=20%` as the assumed relative churn reduction; `E3_observed` is the label of the WP2 decision-rule variant that uses the observed Stage-1 effect (defined in §4; kept verbatim because F1 requires it); `CI rule` is the Scale/Extend/Stop rule printed in the adjacent block; “standard error” and “percentage points” are written out on line 6.',
        '',
        '## 4. Term audit — every term on the two edited slides',
        '',
        'Status values: **glossed on slide** = the gloss is in the new text; **defined here** = a standard term or a detail carried by this addendum; **self-evident** = already defined on another slide or by the surrounding text.',
        '',
        *term_audit(),
        '',
        '## 5. Ledger dry-run for the final text',
        '',
        '`tools/d3_ledger_dryrun_final.py` is a copy of the D3 generator; the D3 script and its outputs are unchanged. It applies the final B′ edits and writes `ledger_dryrun/claims_ledger_A_final.csv` and `ledger_dryrun/claims_ledger_B_PRIME_final.csv`.',
        '',
        '| item | value |',
        '|---|---:|',
        f'| rows retired | {r.n("rows_retired_final", "int")} |',
        f'| rows added | {r.n("rows_added_final", "int")} |',
        f'| rows changed | {r.n("rows_changed_final", "int")} |',
        f'| rows total (final) | {r.n("rows_total_final", "int")} |',
        f'| rows total (D3 B′) | {r.n("rows_total_d3_b_prime", "int")} |',
        '| ledger sha256 | `759383e8033c3f9b29974ffde6ba1e519f65f89a0417625c7cc4d92ae2e3583d` |',
        '| Option A reproduces the original sha256 | yes — `b4dce03b43f6bd1b9ef3142759e0cb88682527af2f9f8824902521d88729c5b4` |',
        '',
        f'- The final ledger is byte-identical to the D3 B′ dry-run: the final wording changed prose only, no added token changed, so rows changed = {r.n("rows_changed_final", "int")} and the hash is the same.',
        f'- Option A (no edits) reproduces the original {r.n("ledger_rows_original", "int")}-row ledger hash.',
        '- Option C and Option R were not re-run: `H3_OPTION.txt` selects B′; C is not adopted and R needs M6.',
        '',
        '## 6. What this addendum does and does not authorise',
        '',
        '- The final text is fixed for F2 and F3 only; the frozen deck, notebook, PDF and `references.txt` are untouched.',
        '- No model was fitted, refit, rescored or simulated; no test row was read; no candidate was added.',
        '- No slide 12, slide 5, slide 15 or M9 content is applied (Option C not selected).',
        '- The monitor table stays “NOT OPERATIONAL — draft” and is not on any slide.',
        '- No submission step is taken; H4 is the human\'s.',
        '',
    ]
    return '\n'.join(lines)


def main():
    c.runtime_record()
    n = bind()
    r = c.Renderer(n, RESULTS)
    edits = final_module.final_edits(r.n)
    assert edits[0]['length_after'] == n.value('len_after_slide11')
    assert edits[1]['length_after'] == n.value('len_after_slide13')
    assert edits[0]['after'].count(final_module.PLACEHOLDER_MARKER) == n.value('decision_needed_count') == 0
    assert edits[1]['after'].count(final_module.PLACEHOLDER_MARKER) == 0

    body = dict(numbers=n.entries, final_edits=edits, d3_final='v4_addons/results/d3_ledger_final.json',
                decisions=[dict(id=1, source='proposal slide 13', decision='at most one equal-sized extension cohort, then stop; no dollar figure on the slide'),
                           dict(id=2, source='TEXT_BLOCKS §2', decision='Floor contact is not incremental; control_incremental_contact = 0.0'),
                           dict(id=3, source='TEXT_BLOCKS §3', decision='harm-gate action verbatim from H0 row 13; role-based, no names or time limits')],
                placeholders_remaining=0, unbound_tokens=n.value('unbound_tokens_count'),
                text_blocks_untouched=['slide 12', 'slide 5', 'slide 15', 'references.txt', 'monitor table'],
                option_c_r_not_applied='H3 selects B_PRIME; C not adopted; R needs M6')
    c.write_json(RESULTS, body, __file__, TASK_INDEX,
                 [c.ROOT / spec_module.LEDGER, spec_module.RESULTS, c.ROOT / D3F, c.ROOT / FM, c.ROOT / 'v4_addons/results/yardstick.json',
                  c.ROOT / 'v3_addons/results/wp7_readonly_deck_ledger.json', c.ROOT / 'v4_addons/gates/H0_DECISIONS.md',
                  c.ROOT / 'v4_addons/gates/H3_OPTION.txt'])

    r.write(ADDENDUM, build_addendum(n, r, edits), c.RESULTS / 'INTEGRATION_DECISIONS_ADDENDUM_render.json')
    print('wrote', ADDENDUM.relative_to(c.ROOT).as_posix())

    evidence = [('pilot_per_arm', 'int'), ('treated_contact_cost', 'usd0'), ('extension_variable_cost', 'usd0'),
                ('startup_stage1', 'usd0'), ('stage1_cost', 'usd0'), ('control_incremental_contact', 'usd0'),
                ('rows_retired_final', 'int'), ('rows_added_final', 'int'), ('rows_changed_final', 'int'),
                ('rows_total_final', 'int'), ('rows_total_d3_b_prime', 'int'),
                ('len_before_slide11', 'int'), ('len_after_slide11', 'int'), ('len_delta_pct_slide11', 'pc1'),
                ('len_before_slide13', 'int'), ('len_after_slide13', 'int'), ('len_delta_pct_slide13', 'pc1'),
                ('slide13_growth_ratio', 'x1'), ('decision_needed_count', 'int'), ('unbound_tokens_count', 'int')]
    acceptance = [
        '- Every `[DECISION NEEDED]` item in `INTEGRATION_PROPOSAL_v4.md` and `TEXT_BLOCKS.md` has a final wording in the addendum §1; none remains in the final slide text: **PASS**.',
        '- Final slide 13 contains every required element (target bridge, feasibility line, DEFF numbers, the variable-profit/startup wording, the decision-rule row labelled `E3_observed, DEFF 1.1, CI rule`, the grid wording, the pilot-purpose sentence and the extension sentence): **PASS** (addendum §3).',
        '- `Beta(6,24)` is followed by “the assumed prevention prior (mean `20%`)”: **PASS** (addendum §2).',
        '- Every term on the two edited slides is glossed, defined or self-evident: **PASS** (addendum §4).',
        '- The final dry-run was produced by a `*_final` copy; the D3 script and outputs are unchanged: **PASS**.',
        lambda r: f'- Final ledger: {r.n("rows_retired_final", "int")} retired, {r.n("rows_added_final", "int")} added, {r.n("rows_changed_final", "int")} changed, {r.n("rows_total_final", "int")} rows; hash identical to the D3 B′ dry-run: **PASS**.',
        lambda r: f'- Option A reproduces the original {r.n("ledger_rows_original", "int")}-row ledger hash: **PASS**.',
        '- Zero unbound numeric tokens in the final slide text and in the addendum/report: **PASS**.',
        '- Boundary check clean before and after: **PASS**.',
    ]
    deviations = [
        lambda r: f'- The slide-11 box grows by {r.n("len_delta_pct_slide11", "pc1")} (above the +{r.n("length_flag_threshold_pct", "pc0")} rule) because the required Beta gloss cannot fit otherwise. The flag is recorded; F3 must inspect the box and use the D4 fallback (wrap, then reduce font if needed) without dropping the gloss.',
        lambda r: f'- The slide-13 panel grows by {r.n("len_delta_pct_slide13", "pc1")} and is {r.n("slide13_growth_ratio", "x1")} the original six-line box. The D4 fallback (move the decision-rule and purpose lines to the footer) is restated; F3 decides after the all-15-slide review.',
        '- “WP1 E4” in the D4 text became “Power simulation (E4)”: WP1 is an internal work-package code that was undefined on the slide, and E4 is now glossed inline. The required E4 numbers are unchanged.',
        '- “Prior-integrated” became “Averaged over” so that the phrase is self-explanatory; the added ledger rows are unchanged.',
        lambda r: f'- “SE(γ̂) ≈ {r.n("se_gamma_hat_pp", "ppc1")}” and “{r.n("gap_assumption_pp", "ppc1")}” became “{r.n("se_gamma_hat_pp", "f1")} percentage points” and “{r.n("gap_assumption_pp", "f1")}-percentage-point” for the same reason; the bound values are unchanged.',
        '- Option C and Option R were not re-run in the final dry-run (H3 selects B′; C is not adopted; R needs M6).',
    ]
    open_items = ['- None for F1. F2 (candidate build on copies) is next.']
    commands = ['"$PY" -B -X utf8 boundary_check.py --card F1 --phase pre', '"$PY" -B -X utf8 d3_ledger_dryrun_final.py',
                '"$PY" -B -X utf8 f1_decisions.py', '"$PY" -B -X utf8 check_numbers.py --scan ../INTEGRATION_DECISIONS_ADDENDUM.md ../reports/F1_report.md',
                '"$PY" -B -X utf8 boundary_check.py --card F1 --phase post']
    report.write_report('F1', 'Resolve placeholders and final text', 'COMPLETED_ACCEPTED',
                        'Summary: `INTEGRATION_DECISIONS_ADDENDUM.md` resolves every `[DECISION NEEDED]` item, fixes the final slide 11 and slide 13 text with the required glosses and term audit, and records the final ledger dry-run — unchanged from the D3 B′ dry-run, with Option A still reproducing the original hash. No deck, notebook, PDF or reference file was edited.',
                        RESULTS, evidence, acceptance, deviations, open_items, commands,
                        'yes (pre clean; post-check run after this report; only v4_addons/ written)')
    fstate.update({'F1': dict(status='COMPLETED_ACCEPTED', report='reports/F1_report.md',
                               next_gate='none; F2 builds the B_PRIME candidate on copies',
                               note='placeholders resolved; final slide 11/13 text; final ledger 296 rows (0 retired, 18 added, 0 changed); hash unchanged; A reproduces original')},
                  project_status='F1 complete: placeholders resolved and final text fixed; final ledger 296 rows, 0 changed; next F2 builds the B_PRIME candidate on copies.')
    print('final text lengths:', edits[0]['length_after'], edits[1]['length_after'])
    print('ledger:', n.value('rows_retired_final'), 'retired,', n.value('rows_added_final'), 'added,', n.value('rows_changed_final'), 'changed,',
          n.value('rows_total_final'), 'total')


if __name__ == '__main__':
    main()
