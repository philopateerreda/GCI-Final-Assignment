import json
import numpy as np
import pandas as pd
from common import WORK, SEED, dump
from workstream_a import scores, fit_thresholds, measure

spec=json.loads((WORK/'a_spec.json').read_text())
cal=pd.read_csv(WORK/'a_selected_calibration.csv')
cal['p_s']=cal.p_s_oof
rng=np.random.default_rng(SEED+180)
rows=[]
for choice in spec['optimal_budgets_calibration_only']:
    cost,fraction=choice['cost'],choice['fraction']
    thresholds=fit_thresholds(cal,fraction=fraction,cost=cost)
    benchmark=fit_thresholds(cal,fraction=.1,cost=cost)
    sc=scores(cal)['bayes']
    candidate=sc>=thresholds['bayes']
    baseline=sc>=benchmark['bayes']
    bootstrap=[]
    for _ in range(300):
        ix=rng.integers(0,len(cal),len(cal))
        frame=cal.iloc[ix].reset_index(drop=True)
        bootstrap.append(measure(frame,candidate[ix],cost=cost)['net']-measure(frame,baseline[ix],cost=cost)['net'])
    lower,upper=np.quantile(bootstrap,[.025,.975])
    difference=measure(cal,candidate,cost=cost)['net']-measure(cal,baseline,cost=cost)['net']
    rows.append({'cost':cost,'calibration_selected_fraction':fraction,'paired_net_gain_vs10':difference,'ci_lower':lower,'ci_upper':upper,'positive_net_under_assumptions':choice['launch_allowed_by_assumed_calibration_net'],'exploratory_conditional_interval_excludes0':lower>0,'eligible_for_headline_promotion':False,'reason':'Fraction optimized on same policy-calibration support; conditional interval omits search uncertainty. Retain predeclared10% headline; prospective experiment determines campaign size. Include no-contact option with0 net; grid endpoints are constrained optima.'})
pd.DataFrame(rows).to_csv(WORK/'a_budget_gate.csv',index=False)
spec['budget_gate']=rows
spec['promoted_headline_fraction']=.1
dump('a_spec.json',spec)
print(pd.DataFrame(rows)[['cost','calibration_selected_fraction','paired_net_gain_vs10','ci_lower','ci_upper']].to_string(index=False))
