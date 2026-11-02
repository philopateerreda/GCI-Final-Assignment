from pathlib import Path
from datetime import datetime
import argparse
import re
import shutil
import sys

import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager

ROOT = Path(__file__).resolve().parent
INTRO = """# Company A | Retain contribution, not just customers
## Original consulting proof of concept
**Omnicampus account:** philopateer  
**Data:** supplied Client.csv and Record.csv only.  
**Execution:** local Windows / Python 3.11 / CPU, six worker threads; no cloud runtime.

### Executive question
Can Company A use customer behavior to allocate a limited service-recovery budget more profitably than a generic highest-churn-risk campaign?

The business lever is **low-cost, customer-consented service recovery**, prioritized by recurring contribution at risk. A model selects whom to investigate; it does not prove that an offer prevents churn. Blanket discounts and automatic handset subsidies are not recommended. Cross-sell, credit decisions, and guaranteed uplift are deliberately outside the evidence this dataset can support.

### Read this distinction first
1. **Observed:** data quality, descriptive segments, held-out predictive scores, and retrospective value capture in this supplied sample.
2. **Assumed:** deployment churn prevalence, currency, contribution margin, retained months, intervention cost, and treatment effectiveness.
3. **To be measured:** causal retention lift, real cost, realized incremental contribution, complaint/opt-out rates, and current-population calibration.

The churn label concerns **days 31–60 after observation**, not a documented cumulative 60-day churn rate. The nearly balanced sample is not an estimate of Company A's actual churn rate. Geography suggests a US scenario, but the company, currency, sample selection, and observation dates are unverified. Historical handset and voice-service variables limit transfer to modern networks.

### Reproduce locally
Place this notebook in the folder containing `telecom/Client.csv` and `telecom/Record.csv`. Use the shared Python 3.11 environment. Package versions are printed below and recorded in `analysis_outputs/environment.json`; exact dependencies are supplied separately. Run all cells in order. All analysis code is embedded here; `analysis_pipeline.py` is a convenience copy, not a notebook dependency. Charts, numerical tables, model artifacts, and test predictions are written under `analysis_outputs/`. Joblib models must only be loaded from trusted sources.

### Contents
1. Environment and integrity; 2. Original EDA; 3. Operational features; 4. Model comparison and calibration; 5. Locked test; 6. Interpretation and robustness; 7. Conditional financial scenarios; 8. Randomized pilot.
"""

TEXT = {
'Setup': """## 1. Local environment
The seed and thread budget are fixed. The models run on the CPU; no GPU, remote notebook, telemetry integration, or external dataset is required. Library versions and raw-input fingerprints make this run auditable.""",
'Integrity and split': """## 2. Integrity and evaluation design
A validated one-to-one join prevents accidental customer multiplication. IDs, full duplicate predictor rows, label completeness, and matched customers are checked before analysis.

The fixed split is **60,000 training / 15,000 model-selection validation / 10,000 probability-calibration and policy-development / 15,000 final test** customers. Target-stratified random splits preserve the supplied sample balance. Model fitting and selection never use the test partition. After validation-only selection, the chosen model is refitted on training plus validation (75,000); its probabilities are calibrated on the separate 10,000. All transformations that learn distributions use training data only. Initial whole-dataset integrity summaries are not temporal validation.

No actual observation timestamps or household IDs are supplied, so future-period validation and household-disjoint splits cannot be claimed. ID-order and subgroup checks below are sensitivity diagnostics, not substitutes.""",
'Exploratory evidence': """## 3. Original EDA: find a business decision, not just a correlation
Business segments are calculated on the 60,000-customer training partition. Missingness and ID-order audits describe all supplied rows.

The central hypothesis is a **risk–value trade-off**: an older handset can coincide with greater churn risk but lower recurring charges. A risk-only list may consequently spend scarce contact capacity on less recurring value. Check the data below rather than assuming that replacing devices causes retention.

Usage decline and overage exposure are diagnostic signals, not proven causes. Customer-care contacts are especially easy to misinterpret: contact can indicate both dissatisfaction and successful service. The dataset dictionary describes change fields as percentages, but their scales and units are ambiguous; this analysis does not describe their raw values as percentage-point changes. Negative billing values may be adjustments, whereas negative handset age is treated as an invalid age.""",
'Operational features': """## 4. Use actionable operational information; minimize sensitive data
The model excludes customer ID, geography, demographic attributes, inferred wealth, credit classifications, and third-party household descriptors. These fields are not necessary to make a service-recovery decision, and many are sparsely populated. Exclusion reduces direct reliance on sensitive proxies; it does **not** establish fairness because operational features can still correlate with protected attributes.

Derived features summarize recent-versus-historical usage and charges, overage exposure, service-quality indices, and equipment age relative to tenure. Ratios are diagnostic features, not causal effects. Categorical vocabularies, imputation, scaling, and the monetary cap are learned on training data, not the test set. CatBoost uses an explicit missing sentinel for numeric input; other tree models handle numeric missingness natively.

**Conservative value proxy:** current recurring charge, floored at zero, missing values replaced by the training median, and extreme values capped at the training 99th percentile. We do not reward punitive overage windfalls, model unobserved cross-sell, or call this customer lifetime value. Currency is unspecified in the source; dollar projections later are explicit USD-equivalent scenarios.""",
'Model selection': """## 5. Compare alternatives, then calibrate
- **Logistic regression:** interpretable linear baseline with training-fitted preprocessing.
- **LightGBM, two predeclared capacities:** efficient nonlinear tabular models.
- **XGBoost:** independent boosted-tree implementation with categorical support.
- **CatBoost:** nonlinear model designed for mixed categorical/numeric inputs.

All comparisons use the same development split. Tree early stopping uses validation only. Highest validation ROC-AUC selects the classifier because the task first needs reliable risk ordering; no test metric or scenario profit is used for model selection. Commercial ranking is assessed separately. A sigmoid calibrator fitted to model log-odds uses the 10,000-customer calibration/policy partition. Neither calibration nor a high AUC converts risk into treatment benefit. Method references: [M1] scikit-learn; [M2] LightGBM; [M3] XGBoost; [M4] CatBoost; commercial decision rationale [S5–S6].""", 
'Locked test evaluation': """## 6. Final held-out evaluation and the equal-budget business comparison
ROC-AUC measures discrimination without a fixed threshold; average precision, log loss, Brier score, and threshold-0.5 accuracy/precision/recall show complementary behavior. Calibration is valid only for the supplied sample distribution. The constant-prior and logistic baselines are reported explicitly.

At equal historical contact budgets (5%, 10%, 20%), compare risk-only, recurring-value-only, risk-times-value, and an old-handset rule. **Recurring-value recall** is the share of observed churned recurring charges captured by the selected list. It is neither money saved nor measured uplift. The 10% budget is a declared comparison point, not a test-optimized winner.

A paired row bootstrap (300 replicates) quantifies uncertainty in test AUC and the risk-times-value improvement over risk-only ranking. Intervals are conditional on this fitted model and sample; they omit model-retraining, policy-effect, and deployment-shift uncertainty.""",
'Explanations and robustness': """## 7. Explain the model and check where it weakens
Permutation importance shuffles each feature on 4,000 held-out customers and measures the loss of ROC-AUC. Correlated features can share or hide importance, and importance is **not causality**. These diagnostics are descriptive after the model and policy specification are fixed; they are not used to retune the evaluated model.

Region, tenure, and ID-order subgroup scores flag transport and quality risks. A stable average does not guarantee a stable subgroup. Before any production rollout, validate on recent dates and linked households/accounts, monitor selection and service outcomes, and reassess features whose collection timing is uncertain.""",
'Transport-aware business scenarios': """## 8. Translate ranking into conditional economics—without pretending 50% churn is normal
This is a **scenario simulator**, not an estimate of Company A's current business results. There are no offer assignments, acceptance labels, treatment outcomes, true margins, campaign costs, actual currency, population sampling weights, or current churn baseline.

### Declared base scenario
- Hypothetical portfolio: 100,000 eligible deployment customers; one campaign cohort, not an annual claim.
- Churn in the modeled future-month window: 2%; stress tests use 1% and 5%.
- Prevention: 20% of contacted customers who would otherwise churn; stress tests use 10% and 30%.
- Six incremental retained months; 60% incremental contribution margin.
- $1 fully loaded variable cost per contacted customer and $5,000 fixed implementation cost; stress tests use $2 and $5 contacts. No handset subsidy or blanket discount is included.
- Capacity: target approximately 10% of the assumed deployment portfolio. Thresholds are learned on the calibration/policy partition, then applied unchanged to the test partition; achieved test coverage can differ.

**Formula:** net contribution = weighted would-be-churned recurring charges contacted × prevention fraction × retained months × margin − contacts × contact cost − fixed cost.

A prior-odds adjustment converts sample-calibrated risk to an assumed prevalence. Outcome-stratified evaluation weights also reweight the evaluation population, rather than applying a real-world churn prior while leaving the 50/50 test composition unchanged. This requires class-conditional representativeness / pure prior shift—an **unverified assumption**, not a correction guaranteed by these data. Test labels are used only for retrospective weighted evaluation, never as live policy inputs.

Risk-only, value-only, value-aware, and random policies share the same scenario assumptions. The optional positive-contribution gate additionally avoids contacts whose modeled variable benefit is below contact cost; fixed costs still have to be recovered. Success may differ by customer and action, so uniform prevention is only an auditable starting assumption. Savings must not be claimed until a randomized test measures incremental effects.""",
'Pilot design and final evidence': """## 9. Buy evidence before scaling
Offer a consent-based digital service check; route verified billing or network issues to resolution and aged devices to diagnostics. Do not automatically cut prices, subsidize devices, infer willingness to pay from sensitive fields, or train a cross-sell model on nonexistent product labels.

Randomize eligible linked households/accounts into **service recovery vs business-as-usual**, stratified by risk–value band. Household linkage must be acquired before launch. Keep a holdout, track costs and opt-outs, measure churn in the specified days-31–60 window (plus early adverse churn), and track actual contribution for at least six months. Pre-register the primary incremental-contribution decision and guardrails. Stop or revise on adverse customer outcomes; scale only after positive incremental contribution is credibly demonstrated.

The power calculation below is illustrative: two-sided 5% alpha, 80% power, normal-approximation two-proportion test, based on the assumed target-group baseline and 20% relative churn reduction. It must be updated using a prospective baseline and inflated for account clustering and multiple treatment arms. Power for profit needs its own variance estimate; churn power alone is not enough.

The final assertions verify source immutability, prediction counts, finite probabilities, and feature consistency. All headline results below come from this local run."""
}

TEXT.update({'V2 reproduction contract': '## 10. Frozen enhancement protocol and self-contained reproduction\nThe nine original analysis code cells are preserved unchanged. They replay the already-evaluated v1 reference, not a new selection search on its test split. The following cells embed every enhancement module. Existing completed outputs are accepted only after source/output fingerprint verification; an absent analysis is reproduced locally in the prescribed A → B → C → D order.\n\n**Four boundaries:** risk is not value; risk is not responsiveness; retrospective capture is not saved revenue; the approximately 49.56% supplied sample is not a 2% deployment population. The original test was evaluated for v1. Enhancement decisions use non-test rows, are frozen before one descriptive final batch, and are not confirmatory external validation.\n\nThe supplied dictionary does not specify the `_Mean` window and the CSVs have no `_Range` fields. Three-/six-month features use only verified `avg3`/`avg6` definitions. The unavailable volatility group is reported rather than reconstructed. No failed challenger proves an information ceiling.', 'V2 baseline replay assets': '## 11. Preserve the original baseline evidence\nA full existing immutable snapshot is never overwritten. On a fresh notebook reproduction only, essential baseline analysis assets are copied from the preceding original cells; this minimal replay cache is explicitly not a restorable submission snapshot. Keep the original supplied files alongside the notebook.', 'V2 non-test workstreams': '## 12. A–D: non-test decisions first\nA compares five parameter-free policies, three clipped calibrators, all declared budgets/costs, paired uncertainty, and four value proxies. B pre-registers disjoint pilot enrollment, two-stage costs, outcome simulations and exclusive routing. C audits excluded-attribute recoverability using fixed original-75k five-fold CV and descriptive subgroup/equity intervals. D uses two repeats of five-fold CV on exactly the original 75k, fold-local preprocessing and nested feature/blend selection.\n\nD reports dependence-corrected paired intervals: `SE = sqrt((1/10 + test/train) × variance)`, with conservative four degrees of freedom. These are exploratory pointwise intervals, not multiplicity- or model-selection-adjusted guarantees. AUC gain must be at least 0.001 with a positive lower bound and nondegrading weighted top-tail calibration. Sensitive `asl_flag`/`area` ceilings cannot be deployed. Higher AUC without passing the calibration gate is rejected.', 'V2 final frozen evaluation': '## 13. One frozen descriptive final batch\nThe model, calibrator, policy cutoffs, headline budget, pilot design and routing criteria are fingerprinted before final evaluation. Existing verified final results are replayed without rescoring. Prior shift assumes stable class-conditional distributions; deployment weights are scenario weights, not estimated real population counts. Costs and benefits are both weighted consistently.\n\nPower for contribution and simulated covariate adjustment are cross-sectional planning proxies, not observed treatment effects or validated CUPED savings. Re-estimate using linked accounts and real pre-period billing logs before launch.', 'V2 results and governance': '## 14. Evidence register and operational boundaries\nThe tables below retain both prior regimes, exact overlap/queue counts, failed calibrators and budget/model gates, corrected CV uncertainty, subgroup small-n flags, and simulated power assumptions. The calibration-selected budget dots are not test-selected profit optima.\n\n**Service-Fix Floor:** remediate every verified billing/network defect regardless of plan price or discretionary-list selection. Value-aware ranking rations only scarce proactive discretionary outreach. Excluding demographic fields reduces direct reliance but does not guarantee statistical independence. This proposal is **audited**, not declared fair. Income is an ordinal 1–9 source code, not currency. No causal uplift, production churn prevalence or AI-chat URL is fabricated.', 'V2 module common': '### Embedded module: common\nSource is materialized byte-for-byte for auditable cache hashes. This cell does not run experiments.', 'V2 module workstream_a': '### Embedded module: workstream_a\nSource is materialized byte-for-byte for auditable cache hashes. This cell does not run experiments.', 'V2 module workstream_b': '### Embedded module: workstream_b\nSource is materialized byte-for-byte for auditable cache hashes. This cell does not run experiments.', 'V2 module workstream_c': '### Embedded module: workstream_c\nSource is materialized byte-for-byte for auditable cache hashes. This cell does not run experiments.', 'V2 module workstream_d': '### Embedded module: workstream_d\nSource is materialized byte-for-byte for auditable cache hashes. This cell does not run experiments.', 'V2 module a_budget_gate': '### Embedded module: a_budget_gate\nSource is materialized byte-for-byte for auditable cache hashes. This cell does not run experiments.', 'V2 module headroom_refit': '### Embedded module: headroom_refit\nSource is materialized byte-for-byte for auditable cache hashes. This cell does not run experiments.', 'V2 module final_protocol': '### Embedded module: final_protocol\nSource is materialized byte-for-byte for auditable cache hashes. This cell does not run experiments.', 'V2 module run_frozen_batch': '### Embedded module: run_frozen_batch\nSource is materialized byte-for-byte for auditable cache hashes. This cell does not run experiments.', 'V2 module final_metrics': '### Embedded module: final_metrics\nSource is materialized byte-for-byte for auditable cache hashes. This cell does not run experiments.', 'V2 module generate_visuals': '### Embedded module: generate_visuals\nSource is materialized byte-for-byte for auditable cache hashes. This cell does not run experiments.'})


def build():
    source = (ROOT / 'analysis_pipeline.py').read_text(encoding='utf-8')
    chunks = re.split(r'^# %% (.+)\n', source, flags=re.MULTILINE)
    cells = [nbformat.v4.new_markdown_cell(INTRO)]
    for i in range(1, len(chunks), 2):
        title, code = chunks[i], chunks[i + 1]
        cells.append(nbformat.v4.new_markdown_cell(TEXT[title]))
        cells.append(nbformat.v4.new_code_cell(code.strip()))
    references = ROOT / 'references.txt'
    if references.exists():
        cells.append(nbformat.v4.new_markdown_cell('## References and evidence register\n\n' + references.read_text(encoding='utf-8')))
    notebook = nbformat.v4.new_notebook(cells=cells, metadata={
        'kernelspec': {'display_name': 'Python 3.11 (local)', 'language': 'python', 'name': 'python3'},
        'language_info': {'name': 'python', 'version': '3.11.9'},
        'title': 'Company A: contribution-focused service recovery',
        'authors': [{'name': 'philopateer'}]})
    return notebook


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    path = ROOT / 'philopateer.ipynb'
    if path.exists():
        backups = ROOT / 'analysis_outputs' / 'notebook_backups'
        backups.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backups / f'philopateer-{datetime.now():%Y%m%d-%H%M%S}.ipynb')
    nb = build()
    nbformat.write(nb, path)
    if args.execute:
        manager = KernelManager(kernel_name='python3')
        manager.kernel_spec.argv = [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}']
        client = NotebookClient(nb, km=manager, timeout=86400, record_timing=True,
            resources={'metadata': {'path': str(ROOT)}},
            on_cell_start=lambda cell, cell_index: print(f'Executing cell {cell_index}: {cell.source.splitlines()[0][:85]}', flush=True))
        try:
            client.execute()
        finally:
            nbformat.write(nb, path)
        assert not any(o.output_type == 'error' for c in nb.cells if c.cell_type == 'code' for o in c.get('outputs', []))
        print('Executed successfully:', path, flush=True)
    else:
        print('Created:', path)
