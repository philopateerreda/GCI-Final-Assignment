# Literature verification — 28 October 2026

## Executive report

Research only: no model, data, notebook, deck, configuration, or references edits, and no local data upload. The full blueprint and existing `references.txt` were read. Public source PDFs were inspected locally using the specified Python 3.11 interpreter when PDF rendering was unavailable.

The seven papers' identities and relevant core findings are verified, but coverage differs: Saerens and Lemmens/Gupta are verified through original abstracts and bibliographic records, not accessible full papers. Blocked supplied URLs are not represented as inspected full text.

Verified: Ascarza's 6% control versus 10% treatment churn over **three months**, for cost-minimizing plan recommendations; risk is not responsiveness; CUPED uses pre-experiment data; profit targeting considers incremental effects and campaign size.

Issuer annual-report Form 10-K copies verify T-Mobile's **0.93%, 2.72%, $50.37** and AT&T's **0.90%**. AT&T uses beginning-of-month subscribers; T-Mobile uses average customers and reporting months, with stated exclusions.

Do not assert a universal **~0.684 Cell2Cell benchmark**, an information ceiling, **SE≈0.004 from N alone**, or that a 0.0014 paired difference is noise. Local results and live pilot power remain Main's responsibility.

Known-prior correction and the $1.3889 gate are conditional mathematics, not causal retention evidence. The four-month-window claim remains unverified; range/mean extrema do not prove exact window length.

**Confidence:** high for inspected excerpts and arithmetic; unknown for Company A transport, causal effectiveness, and local results. **Next:** use only verified, actually used sources; estimate paired uncertainty and validate dictionary, economic, and pilot assumptions.

## Evidence appendix

Quoted excerpts normalize PDF line breaks/ligatures. A table transcription is explicitly labeled. PDF page ordinals are distinguished from printed journal/report pages. The JSON contains the detailed access log, structured claim audit, assumptions, and next actions.

### 1. Saerens2002 — metadata and original abstract verified; full text unavailable

**Bibliography:** Marco Saerens, Patrice Latinne, Christine Decaestecker. “Adjusting the outputs of a classifier to new a priori probabilities: a simple procedure.” *Neural Computation* 14(1), 21–41 (January 2002). DOI: `10.1162/089976602753284446`.

- Supplied: https://direct.mit.edu/neco/article/14/1/21/6577/Adjusting-the-Outputs-of-a-Classifier-to-New-a — HTTP 403.
- Accessed evidence: https://pubmed.ncbi.nlm.nih.gov/11747533/ — bibliographic record and original abstract.
- Verified excerpt: “adjusting the outputs of the trained classifier with respect to these new a priori probabilities without having to refit the model, even when these probabilities are not known in advance.” **Locator:** abstract; no inspected full-text page.
- **Caveat:** the abstract's unknown-prior EM procedure is not identical to a fixed-prior odds correction. No equation/page from the blocked article is claimed as inspected. Elkan's official theorem independently supports the blueprint's known-prior formula under pure prior shift. Company A's 2% prior and transportability are not established.

### 2. Neslin2006 — published article copy inspected

**Bibliography:** Scott A. Neslin, Sunil Gupta, Wagner Kamakura, Junxiang Lu, Charlotte H. Mason. “Defection Detection: Measuring and Understanding the Predictive Accuracy of Customer Churn Models.” *Journal of Marketing Research* 43(2), 204–211 (May 2006). DOI: `10.1509/jmkr.43.2.204`.

- Supplied: https://cdr.lib.unc.edu/concern/articles/v692th53r — fetch failed.
- Accessed copy: http://www.2lvw.nl/blog/wp-content/uploads/2020/05/20200514_Neslin_model_0fb0fc3d857c4c8f9ff6a84aec5e197fe8cb-1.pdf — public third-party copy with published title/pagination.
- Verified excerpt: “The calibration data contained 171 potential predictor variables for 100,000 customers. The predictors were calculated over a three-month period, and churn was measured in the fifth month.” **Locator:** printed p. 205 / PDF p. 2.
- Printed pp. 205–206: calibration churn 50%; company monthly churn 1.8%; current validation 51,306 customers and future validation 100,462, both 1.80% churn. Future data were compiled roughly three months later. Criteria were top-decile lift and Gini.
- **Table 1 transcription, printed p. 207 / PDF p. 4:** current Gini mean/max 0.269/0.41; future Gini mean/max 0.265/0.40. Current lift mean/max 2.140/2.90; future 2.130/3.01.
- **Caveat:** no universal 0.684 ROC-AUC benchmark was verified. Different predictors, enriched calibration, separate low-prevalence validation, temporal protocol, and metrics prevent a matched comparison with the local 0.6978. A conventional Gini-to-AUC conversion would be a conditional derivation, not the paper's reported universal benchmark. The broad three-month description does not resolve each assignment column's window.

### 3. CUPED2013 — supplied manuscript inspected

**Bibliography:** Alex Deng, Ya Xu, Ron Kohavi, Toby Walker. “Improving the Sensitivity of Online Controlled Experiments by Utilizing Pre-Experiment Data.” *WSDM ’13*, 123–132 (2013). DOI: `10.1145/2433396.2433413`. Published page range/date are corroborated by the indexed ACM record; the supplied PDF is labeled “To appear in WSDM 2013.”

- Supplied/accessed: https://exp-platform.com/Documents/2013-02-CUPED-ImprovingSensitivityOfControlledExperiments.pdf
- Verified excerpt: “utilizes data from the pre-experiment period to reduce metric variability and hence achieve better sensitivity.” **Locator:** PDF p. 1, abstract.
- Section 3.2.1, **PDF p. 4**, equations (4)–(5): optimal coefficient `cov(Y,X)/var(X)`; adjusted-mean variance is original-mean variance times `1−rho²`. Sections 3.2.1–3.2.2 connect this to regression and pre-treatment covariates; **PDF p. 5** specifies a common coefficient for both arms.
- The roughly 50% variance reduction is a reported **Bing** result, not a universal guarantee.
- **Caveat:** cross-sectional simulated billing/risk adjustment does not validate live pre/post contribution power or savings. Obtain actual pre-period/outcome pairs and address household clustering, outcome tails, and monitoring. Do not invent printed published-page locators for this prepublication copy.

### 4. LemmensGupta2020 — university metadata and original abstract verified

**Bibliography:** Aurelie Lemmens, Sunil Gupta. “Managing churn to maximize profits.” *Marketing Science* 39(5), 956–973 (2020); online 27 August 2020. DOI: `10.1287/mksc.2020.1229`.

- Supplied/accessed: https://pure.eur.nl/en/publications/managing-churn-to-maximize-profits/
- Verified excerpt: “customers are ranked based on the incremental impact of the intervention on churn and post-campaign cash flows, after accounting for the cost of the intervention”. The abstract also states: “it provides a method to optimize the size of the retention campaign.” **Locator:** publication-record abstract; no inspected full-text page.
- **Caveat:** the linked public PDF returned 403. Exact full-text equations/effect sizes were not verified. This supports an incremental-profit objective, not a claim that churn probability times a bill is causal profit or that an observational contact-fraction optimum transports to Company A.

### 5. Ascarza2018 — published article abstract and relevant introduction inspected

**Bibliography:** Eva Ascarza. “Retention Futility: Targeting High-Risk Customers Might Be Ineffective.” *Journal of Marketing Research* 55(1), 80–98 (February 2018). DOI: `10.1509/jmr.16.0163`.

- Supplied: https://www.hbs.edu/faculty/Pages/item.aspx?num=54936 — HTTP 403.
- Accessed: https://evaascarza.com/papers/ascarza_18.pdf — exact Paper link discovered on the author's public site, not a guessed filename.
- Verified excerpt: “Combining two field experiments with machine learning techniques, the author demonstrates that customers identified as having the highest risk of churning are not necessarily the best targets for proactive churn programs.” **Locator:** printed p. 80 / PDF p. 1; introduction continues on p. 81.
- **Caveat:** risk and intervention sensitivity are different; this is not a theorem that every high-risk customer is unresponsive. An observational churn model remains a risk/stratification tool, not an uplift model. Company A responsiveness needs randomized outcomes.

### 6. Ascarza2016 — published article numerical abstract inspected

**Bibliography:** Eva Ascarza, Raghuram Iyengar, Martin Schleicher. “The Perils of Proactive Churn Prevention Using Plan Recommendations: Evidence from a Field Experiment.” *Journal of Marketing Research* 53(1), 46–60 (February 2016). DOI: `10.1509/jmr.13.0483`.

- Supplied: https://www.hbs.edu/faculty/Pages/item.aspx?num=54941 — HTTP 403.
- Accessed: https://business.columbia.edu/sites/default/files-efs/pubfiles/12782/Perils_Ascarza.pdf — discovered university-hosted published reprint, with supplementary pages.
- Verified excerpt: “whereas only 6% of customers in the control condition churned during the three months following the intervention, 10% did so in the treatment group.” **Locator:** printed p. 46 / PDF p. 1.
- The abstract identifies reduced switching inertia and increased salience of past usage as proposed explanations supported by the data.
- **Caveat:** the treatment was proactive **cost-minimizing plan recommendations**, not every service or technical fix. Rates are rounded three-month group rates, not monthly churn. The exact low-usage/zero-overage/zero-care-call stratum was not verified as a reported subgroup; it is a proposed harm-monitoring hypothesis. Avoid presenting “global plan re-evaluation” as a proven Company A mechanism.

### 7. Elkan2001 — official paper and theorem verified

**Bibliography:** Charles Elkan. “The Foundations of Cost-Sensitive Learning.” *IJCAI 2001*, **973–978**. No DOI was verified. The proceedings landing page lists 973–977, but the primary six-page PDF visibly ends at 978.

- Supplied: https://www.researchgate.net/publication/2365611_The_Foundations_of_Cost-Sensitive_Learning — HTTP 403.
- Discovery: https://ijcai.org/proceedings/2001/133
- Accessed official PDF: https://ijcai.org/proceedings/2001/0133.pdf
- Verified excerpt: “the class that leads to the lowest expected cost” using conditional class probabilities. **Locator:** printed p. 973 / PDF p. 1.
- Section 3 / Theorem 2: “the shift in base rate is the only change in the population”; within positive and negative subpopulations, example probabilities are unchanged. **Locator:** printed p. 975 / PDF p. 3, also visually inspected. The theorem is algebraically equivalent to the blueprint's prior-odds correction.
- **Caveat:** true-probability prior correction does not establish calibration/transportability of estimated probabilities, treatment response, or universal optimality of `p×V` for retention profit.

### 8. TMobile2025 / existing S1 — issuer Form 10-K copy inspected

**Bibliography:** T-Mobile US, Inc. *2025 Annual Report*, including Form 10-K, year ended 31 December 2025 (2026). Exact filing date was not independently read beyond indexed metadata; the existing reference's 11 February date is not inferred from a filename.

- Original references URL: https://www.sec.gov/Archives/edgar/data/1283699/000128369926000010/tmus-20251231.htm — truncated/XBRL-dominated WebFetch content; direct retrieval 403.
- Accessed issuer report: https://s29.q4cdn.com/310188824/files/doc_financials/2025/ar/2025-TMUS-Annual-Report-Final-Web.pdf
- **Verified table transcriptions:** FY2025 postpaid phone churn **0.93%**, prepaid churn **2.72%**, postpaid ARPA **$148.97** — printed p. 43 / PDF p. 55. Postpaid phone ARPU **$50.37** — printed p. 44 / PDF p. 56.
- Verified denominator excerpt: “the average number of customers during the specified period further divided by the number of months in the period.” Deactivations are net of certain restorations and exclude customers with service shorter than a minimum period. **Locator:** printed p. 43.
- **Caveat:** monthly carrier/segment context, not Company A prevalence or margin. ARPU is per customer/month; ARPA is per account/month. Attribute these figures to **S1**, not AT&T's denominator definition.

### 9. ATT2025 / existing S2 — issuer Form 10-K copy inspected

**Bibliography:** AT&T Inc. *2025 Annual Report*, including Form 10-K, year ended 31 December 2025; filed 9 February 2026. Filing date is explicitly corroborated in the accessible report, PDF p. 103.

- Original references URL: https://www.sec.gov/Archives/edgar/data/732717/000073271726000120/t-20251231.htm — inconsistent/truncated WebFetch content; direct retrieval 403.
- Accessed issuer report: https://investors.att.com/~/media/Files/A/ATT-IR-V2/financial-reports/annual-reports/2025/2025-annual-report-complete.pdf
- **Verified table transcription:** postpaid **phone** churn **0.90% in 2025 / 0.76% in 2024**. Total postpaid churn is different: 1.05% / 0.92%. **Locator:** printed p. 23 / PDF p. 32, Mobility table.
- Verified footnote 4: “wireless subscribers at the beginning of that month. The churn rate for the period is equal to the average of the churn rate for each month of that period.” **Locator:** same page.
- Management links part of the 2025 increase to customers reaching the end of device financing periods. **Locator:** printed p. 24 / PDF p. 33.
- **Caveat:** the beginning-of-month denominator belongs to **S2**. Financing maturity is not handset age or a causal Company A effect. Carrier denominator/exclusion differences preclude a controlled 0.90% versus 0.93% performance comparison.

### 10. DeLong1988 — additional methodological abstract verified

**Bibliography:** E. R. DeLong, D. M. DeLong, D. L. Clarke-Pearson. “Comparing the areas under two or more correlated receiver operating characteristic curves: a nonparametric approach.” *Biometrics* 44(3), 837–845 (1988). DOI not verified.

- Discovered/accessed: https://pubmed.ncbi.nlm.nih.gov/3203132/
- Verified excerpt: “statistical analysis on differences between curves must take into account the correlated nature of the data” when tests use the same individuals. **Locator:** original abstract; full article not inspected.
- **Caveat:** supports paired inference, not an actual Company A SE or a claim that DeLong was run. A paired bootstrap is an alternative if actually implemented appropriately.

## Numerical and scope corrections for Main

1. **AUC:** N alone is insufficient; class counts, scores/ties, and paired covariance matter. `(0.7055−0.6899)/3.92 = 0.0039796` is only a normal-equivalent reading of a supplied CI, not independent verification. Do not compare a 0.0014 model difference to one model's marginal SE.
2. **Prior example:** using `pi_s=0.49562`, `pi_d=0.02`, `gamma=0.0207688741`. Customer A's deployment risk is **2.03463%**, rounding to **2.03%**, not 2.04%; expected value **$1.83117**. B is **7.67033%**, expected value **$4.21868**. The ranking reversal is correct; risk-only order remains monotonic.
3. **Weights:** from the blueprint's asserted counts only, `W1=0.2689979825`, `W0=12.9543952412`; selected churners **476.395427**, weighted contacts **9984.921534**. The nonchurner subtotal rounds to **9508.53**, not 9508.52. Actual counts, scores, and threshold provenance remain unverified.
4. **Economics:** `$1/(0.20×6×0.60)=$1.3888889` is a conditional variable-cost gate. For a cohort-weighted realized total, weight contact costs too: sum selected `W_y×(y×tau×M×m×V−c)`, minus fixed cost. The written unweighted `−c` expression could otherwise mix raw rows and population mass; no implementation bug was verified. A nonbinding gate or aggregate discrepancy does not alone prove tail overconfidence.
5. **Pilot:** illustrative binary-rate planning from the supplied weighted counts, two-sided alpha 0.05 and 80% power, gives approximately 7083.76/arm before loss allowance, or **7870.85/arm after division by 0.9**. This supports only the stated order of magnitude, not exact local provenance or live net-contribution power. Multiplication by 1.1 is not the same as 10% attrition adjustment. About 7900 treated contacts at $1 plus $5000 fixed cost is ~$12,900 only before additional delivery/measurement/learning-cell costs.
6. **Windows:** the assignment's exact `_Mean/_Range` windows remain unknown. A secondary indexed upload claims four months but its content/provenance was not inspectable: https://www.scribd.com/document/437911415/Data-Documentation-2. With n equal-weight nonnegative observations, `Range/Mean≤n`; observing 3 or 4 does not prove n equals that value. Four observations `[3,1,0,0]` yield ratio 3; five `[4,1,0,0,0]` yield ratio 4. Negative values, missing months, scaling, rounding, or different windows require additional caution.
7. **Local/proposed claims:** local AUC/CI, +42.4% value capture, precision, prevention, financial results, fairness/proxy effects, and tail calibration were not audited. Uniform prevention, retained months, margin, costs, 2% deployment prevalence, service-fix floor, diagnostic mechanisms, and harm-monitor strata must remain assumptions or proposed policies. Failed challengers do not prove a predictive information ceiling.

## Artifact paths

- `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/literature_verification.json`
- `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/literature_verification.md`

Supporting public PDFs and the Elkan theorem image are recorded by absolute path in the JSON. No slide references or AI chat URL were added or fabricated.
