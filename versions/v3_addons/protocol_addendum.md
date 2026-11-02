# Protocol addendum — supporting proposal only

[R] **ITT estimand.** Randomize linked-household clusters after operational linkage is validated; analyze every enrolled account by assignment. Primary outcome: realized incremental contribution net of all contact, incentive, remediation and implementation costs. Secondary outcomes: days 31–60 churn, V-weighted churn, opt-outs and complaints. Existing data contain no household linkage or treatment labels.

[R] **Service-Fix Floor.** Fix every verified billing/network defect regardless of bill, rank or randomized arm. Ranking rations discretionary proactive outreach only. Both arms receive the Floor, so the estimand is discretionary outreach on top of the Floor—not the effect of the Floor. Log Floor-triggered control contacts and associated costs; do not exclude those controls.

[E/R] **Unchanged harm gate.** Preregister low usage (`mou_Mean` at/below original-training p25), zero overage revenue and zero care; missing values are not zero. At 50% and 100% information, stop for positive treatment-minus-control churn with one-sided Fisher p≤0.005 at either look; familywise bound ≤0.01 for this stratum. Serious complaints or consent violations escalate immediately regardless of significance. Household-clustered live safety design still requires validation.

[R] Small-stratum monitoring is a safety tripwire, not powered subgroup inference. [E] Ascarza, Iyengar and Schleicher (2016), accessible full-text abstract and experiment sections, report 6% control versus 10% treated churn over three months after cost-minimizing plan recommendations. [R] The sleeping-dog hypothesis is preregistered, not verified for Company A or all service contact.

## Assumption table for the pitch — not estimable in Stage 1
[E] Counts/shares below are quotations from frozen `final_metrics.json → pilot_test.queues`, not new test-row computation. [A] Monetary interpretation, costs and prevention remain assumptions; no queue-specific prevention effects are findings.
| Queue hypothesis [R] | Frozen raw rows [E] | Selected at-risk value share [E/A] |
|---|---:|---:|
| Billing check | 582 | 23.4% |
| Network check | 266 | 10.4% |
| Handset check | 791 | 30.7% |
| Digital-only residual | 866 | 35.5% |

[R] Routing flags are hypotheses, not verified causes. The digital residual includes all remaining cases, not only proven low usage. No queue allocation or causal effect is changed.

[E] Sources: frozen handoff §9 and `pilot_test.spec.decision_gates`; existing Ascarza (2016) reference S4, https://business.columbia.edu/sites/default/files-efs/pubfiles/12782/Perils_Ascarza.pdf. HBS item access returned 403; the accessible paper—not that inaccessible page—supports the quotation.
