"""Final B' slide text after F1 placeholder resolution: one source for the final dry-run and the F1 addendum.

Every number is rendered from Numbers entries bound by integration_spec.bind(); nothing here writes files.
"""
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4common as c  # noqa: E402
import integration_spec as spec  # noqa: E402

SLIDE11_OLD_TAIL = 'Net 95% interval: $2.8k–$4.7k'
EXTENSION_LINE = 'If inconclusive: at most one equal-sized extension cohort, then stop.'
PLACEHOLDER_MARKER = '[DECISION NEEDED'


def bind_final():
    n = spec.bind()
    n.derived('se_gamma_hat_pp', 'se_gamma_hat_difference_scaled * 100', tag='[E]',
              note='SE(gamma-hat) in percentage points (yardstick value x 100)')
    n.derived('gap_assumption_pp', 'gap_assumption_to_break_even * 100', tag='[E]',
              note='assumed-to-break-even gap in percentage points (yardstick value x 100)')
    return n


def slide11_after(fmt):
    before = spec.deck_text(11, 3)
    assert before.endswith(SLIDE11_OLD_TAIL), before
    tail = (f'Net {fmt("interval_level", "pct0")} interval at {fmt("binary_relative_prevention_assumption", "pct0")} prevention: '
            f'{fmt("slide11_net_lower", "usdk1")}–{fmt("slide11_net_upper", "usdk1")}. '
            f'Averaged over Beta({fmt("prior_6_24_a", "int")},{fmt("prior_6_24_b", "int")}), the assumed prevention prior '
            f'(mean {fmt("binary_relative_prevention_assumption", "pct0")}), the fifth percentile of net contribution is {fmt("net_5pct_6_24", "usdk1")}.')
    assert PLACEHOLDER_MARKER not in tail
    return before[: -len(SLIDE11_OLD_TAIL)] + tail


def slide13_panel(fmt):
    lines = [
        (f'Pilot target ({fmt("binary_enrolled_per_arm", "int")}/arm): variable profit, startup excluded, '
         f'DEFF {fmt("deff_default", "f1")} (design effect). Earlier v2 calibration: {fmt("v2_grid_adjusted_calibration", "int")}/arm fully loaded, '
         f'startup included, {fmt("v2_followup_retention", "pct0")} follow-up. Not comparable; no reduction claimed.'),
        (f'Power simulation (E4) at DEFF {fmt("deff_default", "f1")} — {fmt("binary_enrolled_per_arm", "int")}/arm: '
         f'{fmt("e4_effect_power_7872_deff1p1", "pct1")} gross effect / {fmt("e4_profit_power_7872_deff1p1", "pct1")} variable profit; '
         f'{fmt("max_per_arm_one_list", "int")}/arm: {fmt("e4_effect_power_5000_deff1p1", "pct1")} / {fmt("e4_profit_power_5000_deff1p1", "pct1")}.'),
        (f'One {fmt("list_size", "int")}-account list gives at most {fmt("max_per_arm_one_list", "int")}/arm; '
         f'{fmt("binary_enrolled_per_arm", "int")}/arm needs {fmt("stage1_total_enrolled", "int")} core accounts '
         f'({fmt("planning_portfolio_proxy", "int")}-account proxy).'),
        (f'Decision rule (E3_observed, DEFF {fmt("deff_default", "f1")}, CI rule), {fmt("binary_enrolled_per_arm", "int")}/arm, '
         f'γ={fmt("binary_relative_prevention_assumption", "pct0")} (assumed relative churn reduction): '
         f'scale {fmt("dq_7872_g20_p_scale", "pct1")} / extend {fmt("dq_7872_g20_p_extend", "pct1")} / stop {fmt("dq_7872_g20_p_stop", "pct1")}.'),
        (f'{fmt("v2_grid_adjusted_calibration", "int")}/arm: v2 fully loaded contribution — first qualifying grid point; not an exact minimum. '
         f'Unadjusted not established through {fmt("v2_grid_top", "int")}/arm.'),
        (f'Purpose: learning, launch and harm detection — not profit proof. Standard error of γ̂ ≈ {fmt("se_gamma_hat_pp", "f1")} '
         f'percentage points vs a {fmt("gap_assumption_pp", "f1")}-percentage-point gap to break-even.'),
        EXTENSION_LINE,
    ]
    text = '\n'.join(lines)
    assert PLACEHOLDER_MARKER not in text
    return text


def final_edits(fmt):
    base = c.read_json(c.ROOT / spec.RESULTS)['spec']['options']['B_PRIME']['edits']
    edits = []
    for edit in base:
        item = copy.deepcopy(edit)
        if item['slide'] == 11:
            item['after'] = slide11_after(fmt)
        elif item['slide'] == 13:
            item['after'] = slide13_panel(fmt)
        item['length_before'] = len(item['before'])
        item['length_after'] = len(item['after'])
        item['length_delta_pct'] = round(100.0 * (len(item['after']) - len(item['before'])) / len(item['before']), 1)
        item['length_flag_over_15pct'] = item['length_delta_pct'] > 15.0
        edits.append(item)
    return edits


def plain_formatter(n):
    return lambda name, spec_name: c.format_number(n.value(name), spec_name)
