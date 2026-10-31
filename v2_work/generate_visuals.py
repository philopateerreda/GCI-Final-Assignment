from pathlib import Path
from hashlib import sha256
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from common import ROOT, WORK, COLORS, SEED
from final_protocol import verify

verify()
for font in (Path.home()/'AppData/Local/Microsoft/FontCache').glob('*/CloudFonts/Aptos/*.ttf'):
    font_manager.fontManager.addfont(str(font))
font_file = Path(font_manager.findfont(font_manager.FontProperties(family='Aptos')))
font_family = font_manager.FontProperties(fname=str(font_file)).get_name()
DEST = WORK / 'charts'
DEST.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'Aptos','figure.dpi':110,'savefig.dpi':300,'axes.spines.top':False,'axes.spines.right':False,'font.size':11,'text.color':COLORS['ink'],'axes.labelcolor':COLORS['ink'],'text.parse_math':False})
frame = pd.read_csv(WORK/'a_selected_test.csv')
summary = json.loads((WORK/'a_summary_test.json').read_text())
spec = summary['spec']
assert spec == json.loads((WORK/'a_spec.json').read_text())
risk, bayes = frame.selected_risk.to_numpy(dtype=bool),frame.selected_bayes.to_numpy(dtype=bool)
regions = {'Agreed core':risk&bayes,'Value-aware additions':bayes&~risk,'Risk-only drops':risk&~bayes}
rows = pd.read_csv(WORK/'a_overlap_test.csv').set_index('region')
chart_claims = []


def record_chart(fig, slide_number, filename):
    fig.canvas.draw()
    text = []
    for axis in fig.axes:
        text.extend(t.get_text() for t in axis.get_xticklabels()+axis.get_yticklabels())
        text.extend([axis.get_title(),axis.get_xlabel(),axis.get_ylabel()])
        text.extend(t.get_text() for t in axis.texts)
        if axis.get_legend() is not None:
            text.extend(t.get_text() for t in axis.get_legend().get_texts())
    chart_claims.append({'slide_number':slide_number,'file':filename,
                         'sha256':sha256((DEST/filename).read_bytes()).hexdigest(),
                         'font':{'family':font_family,'file':str(font_file),
                                 'sha256':sha256(font_file.read_bytes()).hexdigest()},
                         'rendered_text':text,
                         'axes':[{'x_ticks':[{'value':float(value),'text':label.get_text()}
                                            for value,label in zip(axis.get_xticks(),axis.get_xticklabels())],
                                  'y_ticks':[{'value':float(value),'text':label.get_text()}
                                            for value,label in zip(axis.get_yticks(),axis.get_yticklabels())]}
                                 for axis in fig.axes],
                         'x_limits':list(fig.axes[0].get_xlim()),
                         'y_limits':list(fig.axes[0].get_ylim()),
                         'plot_data':{
                             'lines':[{'label':line.get_label(),
                                       'x':np.asarray(line.get_xdata(),dtype=float).tolist(),
                                       'y':np.asarray(line.get_ydata(),dtype=float).tolist()}
                                      for line in fig.axes[0].lines],
                             'collections':[{'label':collection.get_label(),
                                             'offsets':np.asarray(collection.get_offsets(),dtype=float).tolist()}
                                            for collection in fig.axes[0].collections]},
                         'source_tables':['a_selected_test.csv','a_selected_calibration.csv','a_overlap_test.csv',
                                          'a_profit_curves_test.csv','a_summary_test.json','a_spec.json'],
                         'source_sha256':{name:sha256((WORK/name).read_bytes()).hexdigest()
                                          for name in ['a_selected_test.csv','a_selected_calibration.csv','a_overlap_test.csv',
                                                       'a_profit_curves_test.csv','a_summary_test.json','a_spec.json']}})


fig,ax = plt.subplots(figsize=(11,4.4))
rng = np.random.default_rng(SEED)
for (name,mask),color,marker,key in zip(regions.items(),[COLORS['teal'],COLORS['amber'],COLORS['muted']],['o','^','x'],['both','rv_only','risk_only']):
    ix=np.flatnonzero(mask)
    draw=ix if len(ix)<1800 else rng.choice(ix,1800,replace=False)
    row=rows.loc[key]
    average_risk=np.average(frame.p_d.to_numpy()[ix],weights=frame.weight.to_numpy()[ix])
    ax.scatter(frame.p_d.to_numpy()[draw]*100,frame.value.to_numpy()[draw],s=10,alpha=.4,c=color,marker=marker,label=f'{name}: raw test n={len(ix):,}; bill {row.mean_value:.1f}; risk {average_risk:.1%}')
x=np.linspace(.35,18,300)
ax.plot(x,spec['thresholds']['0.02']['bayes']/(x/100),color=COLORS['ink'],lw=1.8,label='Deployment risk × value cutoff')
ax.axvline(spec['thresholds']['0.02']['risk']*100,color=COLORS['muted'],ls='--',lw=1.2,label='_risk_cutoff')
ax.set(xlim=(0,18),ylim=(0,125),xlabel='Assumed deployment churn risk (%)',ylabel='Monthly recurring charge (units)')
ax.legend(loc='upper right',fontsize=9,framealpha=.95)
fig.tight_layout()
fig.savefig(DEST/'risk_value_tradeoff.png',bbox_inches='tight',facecolor='white')
record_chart(fig,5,'risk_value_tradeoff.png')
plt.close(fig)

fig,ax=plt.subplots(figsize=(8,5.1))
w=frame.weight.to_numpy();y=frame.y.to_numpy();v=frame.value.to_numpy()
for name,score,color,style in [('Deployment risk × value',frame.p_d.to_numpy()*v,COLORS['teal'],'-'),('Risk only',frame.p_d.to_numpy(),COLORS['muted'],'--'),('Value only',v,COLORS['amber'],':')]:
    order=np.argsort(-score,kind='stable')
    coverage=np.cumsum(w[order])/w.sum()*100
    gain=np.cumsum(w[order]*y[order]*v[order])/np.sum(w*y*v)*100
    ax.plot(coverage,gain,style,color=color,lw=2,label=name)
ax.plot([0,100],[0,100],color='#CCCCCC',ls='--',label='Random contact')
ax.set(xlim=(0,30),ylim=(0,70),xlabel='Weighted deployment population contacted (%)',ylabel='Churned recurring value captured (%)',title='2% prior scenario; retrospective value capture')
ax.legend(loc='lower right',fontsize=10)
fig.tight_layout()
fig.savefig(DEST/'value_capture_curve.png',bbox_inches='tight',facecolor='white')
record_chart(fig,9,'value_capture_curve.png')
plt.close(fig)

curves=pd.read_csv(WORK/'a_profit_curves_test.csv')
fig,ax=plt.subplots(figsize=(9.7,4.5))
for cost,color,style in [(.25,COLORS['teal'],'-'),(1.,COLORS['ink'],'-'),(2.,COLORS['amber'],'--')]:
    f=curves.loc[curves.cost.eq(cost)]
    ax.plot(f.intended_fraction*100,f.net/1000,color=color,ls=style,lw=2,label=f'${cost:.2f}/contact')
    choice=next(r for r in spec['optimal_budgets_calibration_only'] if r['cost']==cost)
    match=f.loc[np.isclose(f.intended_fraction,choice['fraction'])].iloc[0]
    ax.scatter(choice['fraction']*100,match.net/1000,s=70,c=color,marker='o',edgecolors='white',zorder=4,label=f'_budget_{cost:.2f}')
ax.axvline(10,color=COLORS['muted'],ls=':',lw=1.5,label='10% benchmark')
ax.axhline(0,color=COLORS['muted'],lw=.8,label='_zero_net')
ax.set(xlabel='Calibration-targeted contact fraction (%)',ylabel='Conditional net contribution ($000)',title='Dots: calibration-selected budgets, not test optima')
ax.legend(loc='upper left',fontsize=10,ncol=2)
fig.tight_layout()
fig.savefig(DEST/'scenario_waterfall.png',bbox_inches='tight',facecolor='white')
record_chart(fig,11,'scenario_waterfall.png')
plt.close(fig)
(WORK/'chart_claims.json').write_text(json.dumps(chart_claims,indent=2),encoding='utf-8')
print('Three frozen-data visuals generated at300DPI:',str(DEST))
