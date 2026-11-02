from pathlib import Path
import argparse
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, brier_score_loss, log_loss
from sklearn.model_selection import StratifiedKFold
from common import ROOT, WORK, SEED, Calibrator, frozen_predictions, shift, weights, cutoff, values, dump

POLICIES = ['risk', 'value', 'sample_rv', 'bayes', 'profit_gate']
PRIORS = [.01, .02, .05]
COSTS = [.25, 1., 2., 5.]
FRACTIONS = np.arange(1, 31) / 100


def scores(frame, prior=.02, proxy=None):
    p = frame.p_s.to_numpy()
    value = frame.value.to_numpy() if proxy is None else np.asarray(proxy)
    pd_ = shift(p, prior)
    return {'risk': pd_, 'value': value, 'sample_rv': p * value, 'bayes': pd_ * value, 'profit_gate': pd_ * value}


def measure(frame, selected, prior=.02, cost=1., success=.2, proxy=None):
    y = frame.y.to_numpy()
    v = frame.value.to_numpy() if proxy is None else np.asarray(proxy)
    w = weights(y, prior)
    pd_ = shift(frame.p_s.to_numpy(), prior)
    selected = np.asarray(selected, dtype=float)
    contacts = float(np.sum(w * selected))
    actual_churners = float(np.sum(w * selected * y))
    actual_value = float(np.sum(w * selected * y * v))
    expected_churners = float(np.sum(w * selected * pd_))
    expected_value = float(np.sum(w * selected * pd_ * v))
    gross = actual_value * success * 6 * .6
    return {'raw_count': int(np.count_nonzero(selected)), 'contacts': contacts, 'achieved_contact_fraction': contacts/100000, 'mean_value': float(np.sum(w*selected*v)/contacts) if contacts else 0., 'sample_precision': float(np.sum(selected*y)/np.sum(selected)) if np.sum(selected) else 0., 'deployment_precision': actual_churners/contacts if contacts else 0., 'actual_churners': actual_churners, 'actual_value': actual_value, 'value_recall': actual_value/float(np.sum(w*y*v)), 'model_expected_churners': expected_churners, 'model_expected_value': expected_value, 'model_expected_net': expected_value*success*6*.6-contacts*cost-5000, 'actual_gross': gross, 'net': gross-contacts*cost-5000, 'break_even_contact_cost': (gross-5000)/contacts if contacts else None, 'break_even_success': (contacts*cost+5000)/(actual_value*6*.6) if actual_value else None, 'observed_expected_churn_ratio': actual_churners/expected_churners if expected_churners else None}


def fit_thresholds(frame, prior=.02, fraction=.1, cost=1., proxy=None):
    w = weights(frame.y.to_numpy(), prior)
    thresholds = {name: cutoff(score, w, fraction) for name, score in scores(frame, prior, proxy).items()}
    thresholds['profit_gate'] = max(thresholds['profit_gate'], cost/(.2*6*.6))
    return thresholds


def sample_measure(frame, score, fraction=.1):
    selected = np.argsort(-score, kind='stable')[:int(round(len(frame)*fraction))]
    y, v = frame.y.to_numpy(), frame.value.to_numpy()
    return {'raw_count': len(selected), 'value_recall': float(np.sum(y[selected]*v[selected])/np.sum(y*v)), 'precision': float(y[selected].mean())}


def prepare():
    data, splits, cal = frozen_predictions()
    methods = ['sigmoid', 'beta', 'isotonic']
    oof = {method: np.zeros(len(cal)) for method in methods}
    fold_rows = []
    cv = StratifiedKFold(5, shuffle=True, random_state=SEED)
    for fold, (train, validation) in enumerate(cv.split(cal, cal.y)):
        for method in methods:
            model = Calibrator(method).fit(cal.p_raw.to_numpy()[train], cal.y.to_numpy()[train])
            prediction = model.predict(cal.p_raw.to_numpy()[validation])
            oof[method][validation] = prediction
            for fraction in [.1, .25]:
                value = cal.value.to_numpy()[validation]
                order = np.argsort(-shift(prediction)*value, kind='stable')
                w = weights(cal.y.to_numpy()[validation])
                boundary = cutoff(shift(prediction)*value, w, fraction)
                mask = shift(prediction)*value >= boundary
                fold_rows.append({'fold': fold, 'method': method, 'tail_fraction': fraction, 'auc': roc_auc_score(cal.y.to_numpy()[validation], prediction), 'log_loss': log_loss(cal.y.to_numpy()[validation], prediction), 'brier': brier_score_loss(cal.y.to_numpy()[validation], prediction), 'tail_log_loss': log_loss(cal.y.to_numpy()[validation][mask], prediction[mask]), 'tail_brier': brier_score_loss(cal.y.to_numpy()[validation][mask], prediction[mask]), 'deployment_tail_ratio': float(np.sum(w[mask]*cal.y.to_numpy()[validation][mask])/np.sum(w[mask]*shift(prediction)[mask]))})
    pd.DataFrame(fold_rows).to_csv(WORK / 'a_calibration_cv.csv', index=False)
    baseline_loss = -(cal.y*np.log(oof['sigmoid'])+(1-cal.y)*np.log1p(-oof['sigmoid']))
    rng = np.random.default_rng(SEED+10)
    calibration_tests = []
    for method in methods:
        loss = -(cal.y*np.log(oof[method])+(1-cal.y)*np.log1p(-oof[method]))
        paired = np.asarray(baseline_loss-loss)
        boot = [float(paired[rng.integers(0,len(cal),len(cal))].mean()) for _ in range(300)]
        tails = pd.DataFrame(fold_rows).query('tail_fraction == .1')
        baseline_tail = float(tails.query('method == "sigmoid"').tail_brier.mean())
        candidate_tail = float(tails.loc[tails.method.eq(method), 'tail_brier'].mean())
        calibration_tests.append({'method': method, 'oof_log_loss': log_loss(cal.y, oof[method]), 'paired_logloss_improvement': float(paired.mean()), 'ci_lower': float(np.quantile(boot,.025)), 'ci_upper': float(np.quantile(boot,.975)), 'tail_brier': candidate_tail, 'passes': method!='sigmoid' and np.quantile(boot,.025)>0 and candidate_tail<=baseline_tail})
    eligible = [r for r in calibration_tests if r['passes']]
    selected = min(eligible,key=lambda r:r['oof_log_loss'])['method'] if eligible else 'sigmoid'
    final_calibrator = Calibrator(selected).fit(cal.p_raw.to_numpy(),cal.y.to_numpy())
    joblib.dump(final_calibrator, WORK/'a_calibrator.joblib')
    cal['p_s_oof'] = oof[selected]
    cal['p_s'] = final_calibrator.predict(cal.p_raw.to_numpy())
    cal['p_d'] = shift(cal.p_s.to_numpy())
    decision = cal.copy()
    decision['p_s'] = cal.p_s_oof
    decision['p_d'] = shift(decision.p_s.to_numpy())
    choices = []
    for cost in COSTS:
        candidate = []
        for fraction in FRACTIONS:
            t = fit_thresholds(decision,fraction=fraction,cost=cost)
            selected_mask = scores(decision)['bayes']>=t['bayes']
            candidate.append({'cost': cost, 'fraction': float(fraction), **measure(decision,selected_mask,cost=cost)})
        winner = max(candidate,key=lambda r:r['net'])
        choices.append({'cost':cost,'fraction':winner['fraction'],'calibration_oof_net':winner['net'],'frozen_threshold':fit_thresholds(cal,fraction=winner['fraction'],cost=cost)['bayes'], 'no_contact_net':0., 'launch_allowed_by_assumed_calibration_net':winner['net']>0})
    pd.DataFrame(choices).to_csv(WORK/'a_budget_choices.csv',index=False)
    spec = {'calibrator':selected,'calibration_candidates':calibration_tests,'base_fraction':.1,'optimal_budgets_calibration_only':choices,'test_used_for_selection':False,'value_proxy':'totmrc_Mean','gate_a':'Prior-regime reconciliation qualifies: v1 already used Bayes deployment score in financial scenario. New calibrator and budgets require non-test evidence; test empirical maxima remain diagnostic only.', 'thresholds':{str(prior):fit_thresholds(cal,prior=prior) for prior in PRIORS}}
    dump('a_spec.json',spec)
    cal['selected_risk'] = scores(cal)['risk']>=spec['thresholds']['0.02']['risk']
    cal['selected_bayes'] = scores(cal)['bayes']>=spec['thresholds']['0.02']['bayes']
    cal.to_csv(WORK/'a_selected_calibration.csv',index=False)
    print('A calibration selection:',selected,'; fixed base budget10%; optimal fractions chosen on calibration OOF only',flush=True)
    analyze(cal,cal,data,splits,'calibration')


def analyze(cal,frame,data,splits,label):
    spec = json.loads((WORK/'a_spec.json').read_text())
    policy_rows, curve_rows, overlap_rows, dual_rows = [], [], [], []
    for prior in PRIORS:
        threshold = spec['thresholds'][str(prior)]
        score = scores(frame,prior)
        for name in POLICIES:
            selected = score[name]>=threshold[name]
            policy_rows.append({'partition':label,'prior':prior,'policy':name,'intended_fraction':.1,'threshold':threshold[name], **measure(frame,selected,prior)})
        if prior==.02:
            risk = score['risk']>=threshold['risk']
            bayes = score['bayes']>=threshold['bayes']
            regions = {'both':risk & bayes,'rv_only':bayes & ~risk,'risk_only':risk & ~bayes}
            for name,mask in regions.items():
                result = measure(frame,mask)
                result['variable_net_without_allocated_fixed'] = result['net']+5000
                result['net_with_proportional_fixed_allocation'] = result['net']+5000 - 5000*result['contacts']/measure(frame,risk|bayes)['contacts']
                overlap_rows.append({'region':name,**result})
            for cost in COSTS:
                for fraction in FRACTIONS:
                    threshold_f = fit_thresholds(cal,fraction=float(fraction),cost=cost)['bayes']
                    mask = score['bayes']>=threshold_f
                    curve_rows.append({'prior':prior,'cost':cost,'intended_fraction':float(fraction),'threshold':threshold_f,**measure(frame,mask,cost=cost)})
            previous = np.zeros(len(frame),dtype=bool)
            for fraction in np.arange(1,26)/100:
                t = fit_thresholds(cal,fraction=float(fraction))['bayes']
                selected = score['bayes']>=t
                increment = selected & ~previous
                r = measure(frame,increment)
                r['realized_marginal_net_per_contact'] = (r['actual_gross']-r['contacts'])/r['contacts'] if r['contacts'] else None
                r['predicted_marginal_net_per_contact'] = (r['model_expected_value']*.2*6*.6-r['contacts'])/r['contacts'] if r['contacts'] else None
                dual_rows.append({'intended_fraction':float(fraction), **r})
                previous = selected
    pd.DataFrame(policy_rows).to_csv(WORK/f'a_policies_{label}.csv',index=False)
    pd.DataFrame(curve_rows).to_csv(WORK/f'a_profit_curves_{label}.csv',index=False)
    pd.DataFrame(overlap_rows).to_csv(WORK/f'a_overlap_{label}.csv',index=False)
    pd.DataFrame(dual_rows).to_csv(WORK/f'a_dual_valuation_{label}.csv',index=False)
    proxy_rows = []
    ids = data.set_index('Customer_ID')
    for proxy in ['totmrc_Mean','avg3rev','avg6rev','rev_Mean']:
        v,limits = values(data,splits['train'],proxy)
        by_id = pd.Series(v,index=data.Customer_ID)
        vc,vf = by_id.loc[cal.Customer_ID].to_numpy(),by_id.loc[frame.Customer_ID].to_numpy()
        threshold = fit_thresholds(cal,proxy=vc)
        score = scores(frame,proxy=vf)
        for name in POLICIES:
            proxy_rows.append({'proxy':proxy,'policy':name,**limits,**measure(frame,score[name]>=threshold[name],proxy=vf)})
    pd.DataFrame(proxy_rows).to_csv(WORK/f'a_value_proxy_sensitivity_{label}.csv',index=False)
    rng = np.random.default_rng(SEED+100)
    bootstrap_rows = []
    for rep in range(300):
        ix = rng.integers(0,len(frame),len(frame))
        evaluation = frame.iloc[ix].reset_index(drop=True)
        for prior in PRIORS:
            threshold = spec['thresholds'][str(prior)]
            score = scores(evaluation,prior)
            results = {name:measure(evaluation,score[name]>=threshold[name],prior) for name in POLICIES}
            for name in POLICIES:
                bootstrap_rows.append({'replicate':rep,'regime':'deployment','prior':prior,'policy':name,'value_recall':results[name]['value_recall'],'net':results[name]['net'],'value_difference_vs_risk':results[name]['value_recall']-results['risk']['value_recall'],'relative_value_gain_vs_risk':results[name]['value_recall']/results['risk']['value_recall']-1,'net_difference_vs_risk':results[name]['net']-results['risk']['net']})
        result = {name:sample_measure(evaluation,score) for name,score in scores(evaluation,prior=.4956).items()}
        for name in POLICIES:
            bootstrap_rows.append({'replicate':rep,'regime':'sample','prior':.4956,'policy':name,'value_recall':result[name]['value_recall'],'net':None,'value_difference_vs_risk':result[name]['value_recall']-result['risk']['value_recall'],'relative_value_gain_vs_risk':result[name]['value_recall']/result['risk']['value_recall']-1,'net_difference_vs_risk':None})
    bootstrap = pd.DataFrame(bootstrap_rows)
    bootstrap.to_csv(WORK/f'a_bootstrap_{label}.csv',index=False)
    intervals = []
    for keys,group in bootstrap.groupby(['regime','prior','policy']):
        for metric in ['value_recall','net','value_difference_vs_risk','relative_value_gain_vs_risk','net_difference_vs_risk']:
            vals = group[metric].dropna()
            if len(vals):
                intervals.append({'regime':keys[0],'prior':keys[1],'policy':keys[2],'metric':metric,'lower':float(vals.quantile(.025)),'upper':float(vals.quantile(.975))})
    pd.DataFrame(intervals).to_csv(WORK/f'a_intervals_{label}.csv',index=False)
    uncertainty = []
    for rep in range(300):
        ci = rng.integers(0,len(cal),len(cal))
        ei = rng.integers(0,len(frame),len(frame))
        calibration = cal.iloc[ci].copy().reset_index(drop=True)
        evaluation = frame.iloc[ei].copy().reset_index(drop=True)
        model = Calibrator(spec['calibrator']).fit(calibration.p_raw.to_numpy(),calibration.y.to_numpy())
        calibration['p_s'] = model.predict(calibration.p_raw.to_numpy())
        evaluation['p_s'] = model.predict(evaluation.p_raw.to_numpy())
        t = fit_thresholds(calibration)
        sc = scores(evaluation)
        a = measure(evaluation,sc['bayes']>=t['bayes'])
        b = measure(evaluation,sc['risk']>=t['risk'])
        uncertainty.append({'replicate':rep,'net':a['net'],'net_difference_vs_risk':a['net']-b['net'],'value_recall':a['value_recall'],'relative_value_gain_vs_risk':a['value_recall']/b['value_recall']-1})
    pd.DataFrame(uncertainty).to_csv(WORK/f'a_calibration_uncertainty_{label}.csv',index=False)
    curves = pd.DataFrame(curve_rows)
    optimal = []
    for choice in spec['optimal_budgets_calibration_only']:
        match = curves.loc[(curves.cost==choice['cost']) & np.isclose(curves.intended_fraction,choice['fraction'])].iloc[0].to_dict()
        oracle = curves.loc[curves.cost==choice['cost']].sort_values('net').iloc[-1]
        optimal.append({**choice,'evaluation_at_frozen_fraction':match,'posthoc_empirical_max_fraction_diagnostic_only':float(oracle.intended_fraction),'posthoc_empirical_max_net_diagnostic_only':float(oracle.net)})
    summary = {'partition':label,'spec':spec,'policies':policy_rows,'overlap':overlap_rows,'optimal_budget_results':optimal,'paired_intervals':intervals,'calibration_uncertainty_intervals':{c:{'lower':float(pd.DataFrame(uncertainty)[c].quantile(.025)),'upper':float(pd.DataFrame(uncertainty)[c].quantile(.975))} for c in ['net','net_difference_vs_risk','value_recall','relative_value_gain_vs_risk']},'warning':'All deployment dollars use unverified prior shift, uniform20% prevention,6 months60% margin,$1 contact,$5k fixed. Test achieved budget differs from calibration target: report actual contact mass; posthoc quota curves/optima are diagnostics, never test-selected policy. Calibration-CV uncertainty excludes refitting base classifier and real treatment effects.'}
    dump(f'a_summary_{label}.json',summary)
    dump('a_summary.json',summary)
    print(label,'A policy comparison:',[(r['policy'],round(r['value_recall']*100,2),round(r['net'],2)) for r in policy_rows if r['prior']==.02],flush=True)


def evaluate_test():
    from common import load_data, operational_features
    from scipy.special import logit
    from final_protocol import begin_test
    begin_test(promoted=False)
    data,splits = load_data()
    cal = pd.read_csv(WORK/'a_selected_calibration.csv')
    frozen = pd.read_csv(ROOT/'v1_frozen/analysis_outputs/tables/heldout_predictions.csv')
    order = pd.Series(np.arange(len(data)),index=data.Customer_ID).loc[frozen.Customer_ID].to_numpy()
    bundle = joblib.load(ROOT/'v1_frozen/analysis_outputs/models/selected_model.joblib')
    raw = 1/(1+np.exp(-(logit(np.clip(frozen.sample_calibrated_churn_probability.to_numpy(),1e-6,1-1e-6))-bundle['calibrator'].intercept_[0])/bundle['calibrator'].coef_[0,0]))
    calibrator = joblib.load(WORK/'a_calibrator.joblib')
    p = calibrator.predict(raw)
    frame = pd.DataFrame({'Customer_ID':frozen.Customer_ID,'y':frozen.actual_churn,'p_raw':raw,'p_s':p,'p_d':shift(p),'value':frozen.recurring_value_proxy,'weight':weights(frozen.actual_churn.to_numpy()),'partition':'test'})
    spec = json.loads((WORK/'a_spec.json').read_text())
    sc = scores(frame)
    frame['selected_risk'] = sc['risk']>=spec['thresholds']['0.02']['risk']
    frame['selected_bayes'] = sc['bayes']>=spec['thresholds']['0.02']['bayes']
    frame.to_csv(WORK/'a_selected_test.csv',index=False)
    analyze(cal,frame,data,splits,'test')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--test',action='store_true')
    args=parser.parse_args()
    if args.prepare:
        prepare()
    elif args.test:
        evaluate_test()
    else:
        parser.error('choose --prepare or --test')
