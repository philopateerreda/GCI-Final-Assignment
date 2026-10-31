"""Shared integration specification for options A / B' / C / R: exact before/after slide text and ledger operations.

Every number in the after-text is rendered from bound sources (results/integration_spec.json). Before-text is taken
verbatim from the read-only deck extraction in v3_addons/results/wp7_readonly_deck_ledger.json.
"""
import csv
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4common as c  # noqa: E402

TASK_INDEX = 3
DECK = 'v3_addons/results/wp7_readonly_deck_ledger.json'
LEDGER = 'analysis_outputs/claims_ledger.csv'
FM = 'v2_work/final_metrics.json'
WP3 = 'v3_addons/results/wp3_roi_band.json'
WP2DQ = 'v3_addons/results/wp2_decision_quality.csv'
WP1 = 'v3_addons/results/wp1_power.csv'
YARD = 'v4_addons/results/yardstick.json'
WP7P = 'v3_addons/INTEGRATION_PROPOSAL.md'
RESULTS = c.RESULTS / 'integration_spec.json'
PLACEHOLDER_EXTENSIONS = '[DECISION NEEDED: maximum number of extensions and cost per extension]'
LEDGER_COLUMNS = ['slide_number', 'source_file_or_json_key', 'epistemic_type', 'prior_regime', 'formatter', 'scale', 'location', 'displayed_text', 'exact_value', 'unicode_minus']


def deck_text(slide, index):
    deck = c.read_json(c.ROOT / DECK)
    element = next(item for item in deck['slides'] if item['slide_number'] == slide)['text_elements'][index]
    return element


def ledger_rows():
    raw = (c.ROOT / LEDGER).read_bytes()
    rows = list(csv.reader(io.StringIO(raw.decode('utf-8'), newline='')))
    assert rows[0] == LEDGER_COLUMNS, rows[0]
    return rows[0], rows[1:], raw


def render_ledger_display(formatter, scale, exact, unicode_minus):
    value = float(exact) if exact not in ('', None) else None
    if scale not in ('', None):
        value = value * float(scale)
    if formatter.endswith('d}'):
        text = formatter.format(int(round(value)))
    else:
        text = formatter.format(value)
    if unicode_minus == 'True':
        text = text.replace('-', c.MINUS)
    return text


def new_row(slide, source_key, epistemic, formatter, scale, exact, unicode_minus='', regime='deployment_2.0%', location='native'):
    displayed = render_ledger_display(formatter, scale, exact, unicode_minus)
    return [str(slide), source_key, epistemic, regime, formatter, scale, location, displayed, repr(float(exact)) if not isinstance(exact, int) else str(exact), unicode_minus]


def bind():
    n = c.Numbers()
    y = c.read_json(c.ROOT / YARD)['numbers']
    for name in ('deff_default', 'e4_effect_power_7872_deff1p1', 'e4_profit_power_7872_deff1p1', 'e4_effect_power_5000_deff1p1', 'e4_profit_power_5000_deff1p1',
                 'max_per_arm_one_list', 'list_size', 'stage1_total_enrolled', 'planning_portfolio_proxy', 'binary_enrolled_per_arm', 'v2_grid_adjusted_calibration', 'v2_grid_top',
                 'dq_7872_g20_p_scale', 'dq_7872_g20_p_extend', 'dq_7872_g20_p_stop', 'se_gamma_hat_difference_scaled', 'gap_assumption_to_break_even', 'v2_followup_retention',
                 'slide11_net_lower', 'slide11_net_upper', 'p_positive_6_14', 'p_positive_6_24', 'p_positive_2_18', 'net_5pct_6_24', 'prior_6_24_a', 'prior_6_24_b', 'prior_6_14_a', 'prior_6_14_b',
                 'binary_relative_prevention_assumption', 'interval_level', 'headline_fraction', 'g_star'):
        n.source(name, YARD, f'numbers.{name}.value', tag=y[name]['tag'])
    n.source('ledger_rows_original', LEDGER, 'rowcount')
    return n


def build(n):
    r = c.Renderer(n, RESULTS)
    spec = dict(options={}, placeholders=[PLACEHOLDER_EXTENSIONS])

    # ---------- slide 11 (B', C, R): relabel the conditional interval; the first six lines of the box are unchanged
    s11_before = deck_text(11, 3)
    old_line = 'Net 95% interval: $2.8k–$4.7k'
    assert s11_before.endswith(old_line)
    s11_new_line = (f'Net {r.n("interval_level", "pct0")} interval at {r.n("binary_relative_prevention_assumption", "pct0")} prevention: '
                    f'{r.n("slide11_net_lower", "usdk1")}–{r.n("slide11_net_upper", "usdk1")}. '
                    f'Prior-integrated 5th percentile (Beta({r.n("prior_6_24_a", "int")},{r.n("prior_6_24_b", "int")})): {r.n("net_5pct_6_24", "usdk1")}.')
    s11_after = s11_before[: -len(old_line)] + s11_new_line
    s11_rows = [
        new_row(11, 'v3_addons/results/wp3_roi_band.json::priors.1.a', 'assumed', '{:d}', '1.0', 6),
        new_row(11, 'v3_addons/results/wp3_roi_band.json::priors.1.b', 'assumed', '{:d}', '1.0', 24),
        new_row(11, 'v3_addons/results/wp3_roi_band.json::priors.1.closed_form.net_5pct', 'simulated', '{:.1f}k', '0.001', n.value('net_5pct_6_24'), 'True'),
    ]
    slide11 = dict(slide=11, element_index=3, before=s11_before, after=s11_after, retire=[], add=s11_rows, placeholders=[],
                   note='tokens `20%`, `95%`, `2.8k`, `4.7k` already have slide-11 rows (C0092, C0097, C0098, C0099) and are kept; three new distinct tokens added')

    # ---------- slide 13 (B', C, R): heading + capacity panel
    s13_head_before = deck_text(13, 3)
    assert s13_head_before == 'Binary learning ≠ profit proof'
    s13_head_after = 'Capacity ≠ profit proof'
    s13_panel_before = deck_text(13, 4)
    assert s13_panel_before.startswith('Calibration simulation (planning proxy)')
    s13_panel_after = '\n'.join([
        f'WP1 E4 target: variable profit, startup excluded, DEFF {r.n("deff_default", "f1")}. v2 {r.n("v2_grid_adjusted_calibration", "int")}: fully loaded, startup included, {r.n("v2_followup_retention", "pct0")} follow-up. Not comparable; no reduction claimed.',
        f'E4 at DEFF {r.n("deff_default", "f1")} — {r.n("binary_enrolled_per_arm", "int")}/arm: {r.n("e4_effect_power_7872_deff1p1", "pct1")} gross / {r.n("e4_profit_power_7872_deff1p1", "pct1")} variable profit; {r.n("max_per_arm_one_list", "int")}/arm: {r.n("e4_effect_power_5000_deff1p1", "pct1")} / {r.n("e4_profit_power_5000_deff1p1", "pct1")}.',
        f'One {r.n("list_size", "int")}-account list gives at most {r.n("max_per_arm_one_list", "int")}/arm; {r.n("binary_enrolled_per_arm", "int")}/arm needs {r.n("stage1_total_enrolled", "int")} core accounts ({r.n("planning_portfolio_proxy", "int")}-account proxy).',
        f'Decision rule (E3_observed, DEFF {r.n("deff_default", "f1")}, CI rule), {r.n("binary_enrolled_per_arm", "int")}/arm, γ={r.n("binary_relative_prevention_assumption", "pct0")}: scale {r.n("dq_7872_g20_p_scale", "pct1")} / extend {r.n("dq_7872_g20_p_extend", "pct1")} / stop {r.n("dq_7872_g20_p_stop", "pct1")}.',
        f'{r.n("v2_grid_adjusted_calibration", "int")}/arm = first qualifying grid point for v2 fully loaded contribution, not an exact minimum; unadjusted not established through {r.n("v2_grid_top", "int")}/arm.',
        f'Purpose: learning, launch and harm detection — not profit proof. SE(γ̂) ≈ {r.n("se_gamma_hat_difference_scaled", "pp1")} vs a {r.n("gap_assumption_to_break_even", "pp1")} gap to break-even.',
        PLACEHOLDER_EXTENSIONS,
    ])
    yard = 'v4_addons/results/yardstick.json::numbers.'
    s13_rows = [
        new_row(13, yard + 'deff_default.value', 'assumed', '{:.1f}', '1.0', n.value('deff_default')),
        new_row(13, yard + 'v2_followup_retention.value', 'assumed', '{:.0%}', '', n.value('v2_followup_retention')),
        new_row(13, yard + 'e4_effect_power_7872_deff1p1.value', 'simulated', '{:.1%}', '', n.value('e4_effect_power_7872_deff1p1')),
        new_row(13, yard + 'e4_profit_power_7872_deff1p1.value', 'simulated', '{:.1%}', '', n.value('e4_profit_power_7872_deff1p1')),
        new_row(13, yard + 'max_per_arm_one_list.value', 'assumed', '{:,d}', '1.0', int(n.value('max_per_arm_one_list'))),
        new_row(13, yard + 'e4_effect_power_5000_deff1p1.value', 'simulated', '{:.1%}', '', n.value('e4_effect_power_5000_deff1p1')),
        new_row(13, yard + 'e4_profit_power_5000_deff1p1.value', 'simulated', '{:.1%}', '', n.value('e4_profit_power_5000_deff1p1')),
        new_row(13, yard + 'list_size.value', 'assumed', '{:,d}', '1.0', int(n.value('list_size'))),
        new_row(13, 'v2_work/final_metrics.json::pilot_calibration.spec.planning_portfolio_calibration_proxy', 'assumed', '{:,d}', '1.0', int(n.value('planning_portfolio_proxy'))),
        new_row(13, 'v2_work/final_metrics.json::protocol.financial_assumptions.prevention', 'assumed', '{:.0%}', '', n.value('binary_relative_prevention_assumption')),
        new_row(13, yard + 'dq_7872_g20_p_scale.value', 'simulated', '{:.1%}', '', n.value('dq_7872_g20_p_scale')),
        new_row(13, yard + 'dq_7872_g20_p_extend.value', 'simulated', '{:.1%}', '', n.value('dq_7872_g20_p_extend')),
        new_row(13, yard + 'dq_7872_g20_p_stop.value', 'simulated', '{:.1%}', '', n.value('dq_7872_g20_p_stop')),
        new_row(13, yard + 'se_gamma_hat_difference_scaled.value', 'simulated', '{:.1f}', '100.0', n.value('se_gamma_hat_difference_scaled')),
        new_row(13, yard + 'gap_assumption_to_break_even.value', 'simulated', '{:.1f}', '100.0', n.value('gap_assumption_to_break_even')),
    ]
    slide13 = dict(slide=13, element_index=4, heading_element_index=3, heading_before=s13_head_before, heading_after=s13_head_after,
                   before=s13_panel_before, after=s13_panel_after, retire=[], add=s13_rows, placeholders=[PLACEHOLDER_EXTENSIONS],
                   wp7_retirements_reversed=['C0137', 'C0139'],
                   note='WP7 retired C0137 (`80,000`) and C0139 (`160,000`); the D4 text keeps both tokens (grid wording / "not established through `160,000`"), so they are retained. `80%` (C0138) stays via the footer. Fifteen new distinct tokens added.')

    # ---------- slide 12 footer (C only)
    s12_before = deck_text(12, 21)
    assert s12_before.startswith('[D1, M5–M6] Editable scenario sensitivity')
    s12_after = (f'[D1, M5–M6, M9] Prior-integrated net at the frozen {r.n("headline_fraction", "pct0")} threshold: P(net>0)={r.n("p_positive_2_18", "pct0")}–{r.n("p_positive_6_14", "pct0")} across assumed prevention priors; '
                 f'{r.n("p_positive_6_24", "pct0")} under Beta({r.n("prior_6_24_a", "int")},{r.n("prior_6_24_b", "int")}), centered on {r.n("binary_relative_prevention_assumption", "pct0")}. Sensitivity, not a CI or EMPC; no treatment labels.     12')
    s12_rows = [
        new_row(12, 'v3_addons/results/wp3_roi_band.json::band.lower', 'simulated', '{:.0%}', '', n.value('p_positive_2_18')),
        new_row(12, 'v3_addons/results/wp3_roi_band.json::band.upper', 'simulated', '{:.0%}', '', n.value('p_positive_6_14')),
        new_row(12, 'v3_addons/results/wp3_roi_band.json::band.central', 'simulated', '{:.0%}', '', n.value('p_positive_6_24')),
        new_row(12, 'v3_addons/results/wp3_roi_band.json::priors.1.a', 'assumed', '{:d}', '1.0', 6),
        new_row(12, 'v3_addons/results/wp3_roi_band.json::priors.1.b', 'assumed', '{:d}', '1.0', 24),
    ]
    slide12 = dict(slide=12, element_index=21, before=s12_before, after=s12_after, retire=[], add=s12_rows, placeholders=[],
                   note='`10%`, `20%` and `12` already have slide-12 rows; five new distinct tokens. Keep the exact wording "Sensitivity, not a CI or EMPC."')

    # ---------- slide 5 sentence and slide 15 blocks (C optional, from WP7 proposal)
    s5_before = deck_text(5, 2)
    s5_after = 'Value-aware triage is not a response model. EM is a label-shift diagnostic only; stable class-conditionals are unverified and day-60 labels remain ground truth.'
    slide5 = dict(slide=5, element_index=2, before=s5_before, after=s5_after, retire=[], add=[], placeholders=[], optional=True,
                  note='no new distinct token: `60` already has a slide-5 row')
    s15_left_before = deck_text(15, 4)
    s15_left_after = s15_left_before.replace('[M5] Saerens et al. (2002): prior adjustment.', '[M5] Saerens et al. (2002): prior adjustment; abstract-only.')
    assert s15_left_after != s15_left_before
    s15_right_before = deck_text(15, 5)
    s15_right_after = s15_right_before.replace('No matched AUC ceiling or measured CUPED claimed.', f'[M9] EMP source: assumed Beta({r.n("prior_6_14_a", "int")},{r.n("prior_6_14_b", "int")}) default.')
    assert s15_right_after != s15_right_before
    s15_rows = [
        new_row(15, 'v3_addons/results/wp3_roi_band.json::priors.0.a', 'assumed', '{:d}', '1.0', 6, regime='external_context'),
        new_row(15, 'v3_addons/results/wp3_roi_band.json::priors.0.b', 'assumed', '{:d}', '1.0', 14, regime='external_context'),
    ]
    slide15 = dict(slide=15, element_index=4, before=s15_left_before, after=s15_left_after, right_element_index=5, right_before=s15_right_before, right_after=s15_right_after,
                   retire=[], add=s15_rows, placeholders=[], optional=True, note='M5 abstract-only wording (no token); M9 line adds tokens `6` and `14` (not previously on slide 15). Drops the sentence "No matched AUC ceiling or measured CUPED claimed." to hold the line count; flag for human review.')

    spec['options'] = {
        'A': dict(edits=[], description='No change. Frozen v2 remains the submission; v4 material stays in v4_addons/.'),
        'B_PRIME': dict(edits=[slide11, slide13], description='Slide 11 conditional-interval relabel + slide 13 capacity/target bridge (recommended).'),
        'C': dict(edits=[slide11, slide13, slide12, slide5, slide15], description='B\' plus slide 12 prior-band footer (M9), optional slide 5 diagnostic wording, slide 15 M5/M9 blocks, and the references.txt M9 append.'),
        'R': dict(edits=[slide11, slide13], description='B\' plus full regeneration of every model-dependent number after a Track M ADOPT-CONFIRMED (M6). Regenerated ledger not available until M6 runs.'),
    }
    for option in spec['options'].values():
        for edit in option['edits']:
            edit['length_before'] = len(edit['before'])
            edit['length_after'] = len(edit['after'])
            edit['length_delta_pct'] = round(100.0 * (len(edit['after']) - len(edit['before'])) / len(edit['before']), 1)
            edit['length_flag_over_15pct'] = edit['length_delta_pct'] > 15.0
    return spec, r


def main():
    c.runtime_record()
    n = bind()
    spec, r = build(n)
    body = dict(numbers=n.entries, spec=spec)
    inputs = [c.ROOT / p for p in (DECK, LEDGER, YARD, WP3, FM, WP7P)]
    c.write_json(RESULTS, body, __file__, TASK_INDEX, inputs)
    (c.RESULTS / 'integration_spec_render.json').write_text(json.dumps(dict(report='v4_addons/results/integration_spec.json', report_sha256=c.digest(RESULTS), **r.registry()), indent=2) + '\n', encoding='utf-8')
    for name, option in spec['options'].items():
        adds = sum(len(edit['add']) for edit in option['edits'])
        print(f'{name}: edits={len(option["edits"])} rows added={adds} retired={sum(len(e["retire"]) for e in option["edits"])} flags={[e["slide"] for e in option["edits"] if e["length_flag_over_15pct"]]}')


if __name__ == '__main__':
    main()
