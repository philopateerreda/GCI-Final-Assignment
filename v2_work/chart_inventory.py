from hashlib import sha256
import json
from pathlib import Path

import pandas as pd
from pptx import Presentation

from common import ROOT, WORK


def inventory():
    definitions = {
        6: {'filename': 'operational_signals.png',
            'source_csv': 'operational_segments.csv',
            'axis_scale': {'sample_churn_percent_ticks': list(range(0, 61, 10)),
                           'sample_churn_percent_limits': [0, 65]},
            'predeclared_bin_edges': {'usage_change_finite': [-100, 0, 100],
                                    'overage_revenue_finite': [-1, 0, 5, 20, 100],
                                    'customer_care_calls_finite': [-1, 0, 1, 3]},
            'rendered_numeric_labels': ['0', '10', '20', '30', '40', '50', '60',
                                        '−100', '100', '5', '1', '3']},
        8: {'filename': 'model_validation.png', 'source_csv': 'test_metrics.csv',
            'axis_scale': {'probability_ticks': [0., .2, .4, .6, .8, 1.]},
            'reference_auc': .5,
            'rendered_numeric_labels': ['0.0', '0.2', '0.4', '0.6', '0.8', '1.0',
                                        '0.619', '0.698', '0.500']}}
    records = []
    for slide, definition in definitions.items():
        image = ROOT / 'v1_frozen/analysis_outputs/charts' / definition['filename']
        table = ROOT / 'v1_frozen/analysis_outputs/tables' / definition['source_csv']
        frame = pd.read_csv(table)
        data = frame.astype(object).where(frame.notna(), None).to_dict(orient='records')
        records.append({'slide_number': slide, **definition,
                        'sha256': sha256(image.read_bytes()).hexdigest(),
                        'source_sha256': sha256(table.read_bytes()).hexdigest(),
                        'source_records': data,
                        'scope': 'Unchanged v1 chart; labels inspected against full-size PowerPoint render and frozen source tables.'})
    target = WORK / 'unchanged_chart_claims.json'
    target.write_text(json.dumps(records, indent=2, allow_nan=False), encoding='utf-8')
    return records


def verify_embedded_images():
    records = inventory() + json.loads((WORK / 'chart_claims.json').read_text(encoding='utf-8'))
    by_slide = {row['slide_number']: row for row in records}
    deck = Presentation(ROOT / 'philopateer.pptx')
    checked = []
    for number, slide in enumerate(deck.slides, 1):
        images = [shape for shape in slide.shapes if shape.shape_type == 13]
        if not images:
            continue
        assert number in by_slide, f'Unregistered chart image on slide {number}.'
        assert len(images) == 1, f'Unexpected picture count on slide {number}.'
        expected = by_slide[number]['sha256']
        actual = sha256(images[0].image.blob).hexdigest()
        assert actual == expected, f'Chart bytes differ from registered source on slide {number}.'
        checked.append(number)
    assert checked == [5, 6, 8, 9, 11], checked
    return {'chart_slides_checked': checked, 'all_embedded_chart_sha256_match_sources': True}


def verify_plot_data(chart, frame, spec, curves=None, calibration=None):
    import numpy as np
    from common import SEED

    y, value = frame.y.to_numpy(), frame.value.to_numpy()
    weight = np.where(y == 1, 2000 / y.sum(), 98000 / (len(y) - y.sum()))
    np.testing.assert_allclose(frame.weight, weight, rtol=1e-12)
    probability = frame.p_d.to_numpy()
    risk = probability >= spec['thresholds']['0.02']['risk']
    bayes = probability * value >= spec['thresholds']['0.02']['bayes']
    np.testing.assert_array_equal(frame.selected_risk, risk)
    np.testing.assert_array_equal(frame.selected_bayes, bayes)
    expected_lines, expected_collections = {}, {}
    slide = chart['slide_number']
    if slide == 5:
        rng = np.random.default_rng(SEED)
        for name, mask in (('Agreed core', risk & bayes), ('Value-aware additions', bayes & ~risk),
                           ('Risk-only drops', risk & ~bayes)):
            indices = np.flatnonzero(mask)
            draw = indices if len(indices) < 1800 else rng.choice(indices, 1800, replace=False)
            mean_bill = np.average(value[indices], weights=weight[indices])
            mean_risk = np.average(probability[indices], weights=weight[indices])
            label = f'{name}: raw test n={len(indices):,}; bill {mean_bill:.1f}; risk {mean_risk:.1%}'
            expected_collections[label] = np.column_stack([probability[draw] * 100, value[draw]])
        x = np.linspace(.35, 18, 300)
        expected_lines['Deployment risk × value cutoff'] = (x, spec['thresholds']['0.02']['bayes'] / (x / 100))
        expected_lines['_risk_cutoff'] = ([spec['thresholds']['0.02']['risk'] * 100] * 2, [0, 1])
        np.testing.assert_allclose(chart['x_limits'], [0, 18])
        np.testing.assert_allclose(chart['y_limits'], [0, 125])
    elif slide == 9:
        for name, score in (('Deployment risk × value', probability * value), ('Risk only', probability),
                            ('Value only', value)):
            order = np.argsort(-score, kind='stable')
            coverage = np.cumsum(weight[order]) / weight.sum() * 100
            capture = np.cumsum(weight[order] * y[order] * value[order]) / np.sum(weight * y * value) * 100
            expected_lines[name] = (coverage, capture)
        expected_lines['Random contact'] = ([0, 100], [0, 100])
        np.testing.assert_allclose(chart['x_limits'], [0, 30])
        np.testing.assert_allclose(chart['y_limits'], [0, 70])
    elif slide == 11:
        assert curves is not None and calibration is not None
        cal_y = calibration.y.to_numpy()
        cal_weight = np.where(cal_y == 1, 2000 / cal_y.sum(), 98000 / (len(cal_y) - cal_y.sum()))
        cal_score = calibration.p_d.to_numpy() * calibration.value.to_numpy()
        order = np.argsort(-cal_score, kind='stable')
        cumulative = np.cumsum(cal_weight[order])
        for cost in (.25, 1., 2.):
            selected_curve = curves.loc[curves.cost.eq(cost)]
            for row in selected_curve.itertuples():
                position = min(np.searchsorted(cumulative, cal_weight.sum() * row.intended_fraction), len(order) - 1)
                threshold = cal_score[order[position]]
                np.testing.assert_allclose(row.threshold, threshold, rtol=1e-10)
                mask = probability * value >= threshold
                net = .2 * 6 * .6 * np.sum(weight * y * value * mask) - cost * np.sum(weight * mask) - 5000
                np.testing.assert_allclose(row.net, net, rtol=1e-10, atol=1e-8)
            expected_lines[f'${cost:.2f}/contact'] = (selected_curve.intended_fraction.to_numpy() * 100,
                                                     selected_curve.net.to_numpy() / 1000)
            choice = next(row for row in spec['optimal_budgets_calibration_only'] if row['cost'] == cost)
            match = selected_curve.loc[np.isclose(selected_curve.intended_fraction, choice['fraction'])].iloc[0]
            expected_collections[f'_budget_{cost:.2f}'] = [[choice['fraction'] * 100, match.net / 1000]]
        expected_lines['10% benchmark'] = ([10, 10], [0, 1])
        expected_lines['_zero_net'] = ([0, 1], [0, 0])
    else:
        raise AssertionError(f'Unexpected chart slide: {slide}')
    actual_lines = {row['label']: row for row in chart['plot_data']['lines']}
    actual_collections = {row['label']: row for row in chart['plot_data']['collections']}
    assert len(actual_lines) == len(chart['plot_data']['lines'])
    assert len(actual_collections) == len(chart['plot_data']['collections'])
    assert set(actual_lines) == set(expected_lines), slide
    assert set(actual_collections) == set(expected_collections), slide
    for label, (x, y_values) in expected_lines.items():
        np.testing.assert_allclose(actual_lines[label]['x'], x, rtol=1e-10, atol=1e-9, err_msg=label)
        np.testing.assert_allclose(actual_lines[label]['y'], y_values, rtol=1e-10, atol=1e-9, err_msg=label)
    for label, offsets in expected_collections.items():
        np.testing.assert_allclose(actual_collections[label]['offsets'], offsets, rtol=1e-10, atol=1e-9, err_msg=label)
    return {'slide_number': slide, 'independent_plotted_coordinates_verified': True}


def prepare_numeric_sources():
    import numpy as np
    from claim_checks import numeric_mentions

    records = inventory()
    charts = json.loads((WORK / 'chart_claims.json').read_text(encoding='utf-8'))
    frame = pd.read_csv(WORK / 'a_selected_test.csv')
    overlap = pd.read_csv(WORK / 'a_overlap_test.csv').set_index('region')
    spec = json.loads((WORK / 'a_spec.json').read_text(encoding='utf-8'))
    assert spec == json.loads((WORK / 'a_summary_test.json').read_text(encoding='utf-8'))['spec']
    curves = pd.read_csv(WORK / 'a_profit_curves_test.csv')
    calibration = pd.read_csv(WORK / 'a_selected_calibration.csv')
    numbers, plot_checks = [], []

    def add(slide, value, formatter, epistemic, regime, label=None, source_locator=None):
        displayed = formatter.format(value).replace('-', '−')
        if label is not None:
            assert displayed == label, (slide, displayed, label)
        numbers.append({'slide_number': slide, 'value': value, 'formatter': formatter,
                        'displayed_text': displayed, 'epistemic_type': epistemic,
                        'prior_regime': regime, 'unicode_minus': True,
                        'source_file_or_json_key': f'v2_work/chart_numeric_sources.json::{len(numbers)}.value',
                        'source_locator': source_locator or 'Source-checked axis tick, documented chart design constant or frozen metric.'})

    sample, deployment = 'sample_49.56%', 'deployment_2.0%'
    for value in range(0, 61, 10):
        add(6, value, '{:.0f}', 'assumed', sample)
    for value in (-100, 100, 5, 1, 3):
        add(6, value, '{:.0f}', 'assumed', sample)
    for value in (0., .2, .4, .6, .8, 1.):
        add(8, value, '{:.1f}', 'assumed', sample)
    metrics = pd.read_csv(ROOT / 'v1_frozen/analysis_outputs/tables/test_metrics.csv').set_index('model')
    for name in ('Logistic regression (60k train)', 'LightGBM wider leaves calibrated (75k refit)', 'Constant prior baseline'):
        add(8, float(metrics.loc[name, 'roc_auc']), '{:.3f}', 'observed', sample)

    for chart in charts:
        slide = chart['slide_number']
        image = WORK / 'charts' / chart['file']
        assert sha256(image.read_bytes()).hexdigest() == chart['sha256']
        assert chart['font']['family'] == 'Aptos', chart['font']
        assert sha256(Path(chart['font']['file']).read_bytes()).hexdigest() == chart['font']['sha256']
        required_sources = {'a_selected_test.csv', 'a_selected_calibration.csv', 'a_overlap_test.csv',
                            'a_profit_curves_test.csv', 'a_summary_test.json', 'a_spec.json'}
        assert required_sources.issubset(chart['source_sha256'])
        for source, digest in chart['source_sha256'].items():
            assert sha256((WORK / source).read_bytes()).hexdigest() == digest, source
        plot_checks.append(verify_plot_data(chart, frame, spec, curves, calibration))
        for axis in chart['axes']:
            for tick in axis['x_ticks'] + axis['y_ticks']:
                text = tick['text']
                if not text:
                    continue
                decimals = len(text.split('.')[-1]) if '.' in text else 0
                add(slide, tick['value'], '{:.' + str(decimals) + 'f}', 'assumed', deployment, text)
        if slide == 5:
            risk = frame.selected_risk.to_numpy(dtype=bool)
            bayes = frame.selected_bayes.to_numpy(dtype=bool)
            regions = (('Agreed core', 'both', risk & bayes),
                       ('Value-aware additions', 'rv_only', bayes & ~risk),
                       ('Risk-only drops', 'risk_only', risk & ~bayes))
            for name, key, mask in regions:
                count = int(mask.sum())
                mean_bill = float(np.average(frame.value[mask], weights=frame.weight[mask]))
                mean_risk = float(np.average(frame.p_d[mask], weights=frame.weight[mask]))
                assert np.isclose(mean_bill, overlap.loc[key, 'mean_value'])
                annotation = f'{name}: raw test n={count:,}; bill {mean_bill:.1f}; risk {mean_risk:.1%}'
                assert annotation in chart['rendered_text'], annotation
                add(slide, count, '{:,}', 'observed', sample,
                    source_locator=f'a_selected_test.csv: raw sample rows in {key}; selection uses frozen deployment thresholds.')
                add(slide, mean_bill, '{:.1f}', 'observed', deployment,
                    source_locator=f'a_selected_test.csv: deployment-weighted mean recurring value in {key}.')
                add(slide, mean_risk, '{:.1%}', 'observed', deployment,
                    source_locator=f'a_selected_test.csv: deployment-weighted mean prior-shifted model risk in {key}.')
        elif slide == 9:
            add(slide, .02, '{:.0%}', 'assumed', deployment)
        elif slide == 11:
            for cost in (.25, 1., 2.):
                assert f'${cost:.2f}/contact' in chart['rendered_text']
                add(slide, cost, '{:.2f}', 'assumed', deployment)
            add(slide, .1, '{:.0%}', 'assumed', deployment)
            add(slide, 0, '{:03d}', 'assumed', deployment)
        else:
            raise AssertionError(f'Unexpected new chart slide: {slide}')
        registered = {row['displayed_text'] for row in numbers if row['slide_number'] == slide}
        missing = [(text, token) for text in chart['rendered_text']
                   for token in numeric_mentions(text) if token not in registered]
        assert not missing, (slide, missing)
    for record in records:
        registered = {row['displayed_text'] for row in numbers if row['slide_number'] == record['slide_number']}
        assert set(record['rendered_numeric_labels']).issubset(registered), record['slide_number']
    target = WORK / 'chart_numeric_sources.json'
    target.write_text(json.dumps(numbers, indent=2, allow_nan=False), encoding='utf-8')
    (WORK / 'chart_data_checks.json').write_text(json.dumps(plot_checks, indent=2), encoding='utf-8')
    return numbers


if __name__ == '__main__':
    print(json.dumps(inventory(), indent=2))
