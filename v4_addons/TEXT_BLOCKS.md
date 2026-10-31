# TEXT_BLOCKS — copy-ready replacement text and corrections (Track D)

_v4 Track D, card D6 · 2026-10-31 · every number below is bound in `results/d6_text_blocks.json`; no deck, notebook, protocol or reference file was edited._

## 1. Queue table — composition and feasibility, not value triage

**Replacement label (use verbatim):**

> Queue composition / feasibility (value per account ≈ flat)

| Queue | Selected accounts | Count share | At-risk value share | Lift (value share ÷ count share) | Section-9 quoted lift |
|---|---:|---:|---:|---:|---:|
| `billing_check` | 582 | 23.23% | 23.4% | 1.007 | 1.007 |
| `network_check` | 266 | 10.62% | 10.4% | 0.980 | 0.979 |
| `handset_check` | 791 | 31.58% | 30.7% | 0.971 | 0.972 |
| `digital_only_residual` | 866 | 34.57% | 35.5% | 1.027 | 1.027 |
| **total** | **2,505** | 100.00% | 100.0% | — | — |

[E] Value per account is flat: the largest absolute deviation of any lift from 1.000 is 2.9% (the residual queue). Rounding the published one-decimal value shares reproduces the section-9 quoted lifts; the exact-share lifts differ from those quotes by at most 0.0009.

**Copy-ready caption:**

> Queue composition / feasibility (value per account ≈ flat): 2,505 selected accounts; count shares 23.23% / 10.62% / 31.58% / 34.57% vs at-risk value shares 23.4% / 10.4% / 30.7% / 35.5%; lift 1.007 / 0.979 / 0.972 / 1.027.

[R] Do not call this table value triage, targeting lift or value capture: the shares differ from parity by at most a few percent, so the queue split is a feasibility/composition statement about where selected accounts sit, not evidence that the policy concentrates value.

## 2. Floor (control-arm) contact cost

[E] The v2 cost spec sets `control_incremental_contact` to $0: control-arm contacts are costed at zero, so the $12,872 Stage-1 envelope is 7,872 treated contacts at $1 plus the $5,000 startup (rebuild $12,872).

**Draft sentence for the deck/protocol:**

> Stage-1 envelope $12,872 prices 7,872 treated contacts at $1 each plus the $5,000 startup; control-arm (Floor) contacts are costed at $0.

[DECISION NEEDED: is a Floor contact free? If not, the $12,872 envelope is understated — at $1 per control contact it becomes $20,744 (+$7,872, covering all 15,744 Stage-1 enrollees).]

## 3. Harm gate — action text

[E] The gate stays as sealed in v2: harm stratum `mou_Mean<=original60k p25 AND ovrrev_Mean=0 AND custcare_Mean=0`; planned looks at 0.5 and 1.0 of exposure; one-sided Fisher exact alpha 0.005 per look, familywise 0.01; serious complaints or consent violations escalate immediately regardless of p-value.

**Draft action text (fill the owner):**

> If the harm gate trips at either planned look: stop outbound service contact for the harm stratum immediately, retain both arms under observation, preserve the assigned control comparison, and escalate to [owner] within one business day. Resumption requires a written review that names the observed harm, the changed contact design and the stopping rule for the next look. Serious complaints or consent violations escalate immediately, independent of statistical significance.

[DECISION NEEDED: action if the gate trips; owner — who stops the contact, who signs resumption, and what happens to already-scheduled contacts?]

## 4. Reference link access — report only, no edit

| Ref | `references.txt` line | URL | Default client | Browser user-agent | Verified page |
|---|---:|---|---:|---:|---|
| [S4] Ascarza et al. (2016) | 36 | `https://www.hbs.edu/faculty/Pages/item.aspx?num=54941` | 403 | 200 | The Perils of Proactive Churn Prevention Using Plan Recommendations |
| [S5] Ascarza (2018) | 40 | `https://www.hbs.edu/faculty/Pages/item.aspx?num=54936` | 403 | 200 | Retention Futility: Targeting High-Risk Customers Might Be Ineffective |
| [S4] accessible copy | 86 | `https://business.columbia.edu/sites/default/files-efs/pubfiles/12782/Perils_Ascarza.pdf` | 200 | 200 | Columbia PDF (application/pdf) |
| [S5] accessible copy | 89 | `https://evaascarza.com/papers/ascarza_18.pdf` | 200 | 200 | Author PDF (application/pdf) |

[E] Both HBS faculty pages answer 403 to a default scripted client and 200 to a browser user-agent; the pages resolve to the two cited articles, so the 2 HBS links are bot-blocked rather than dead. The Columbia copy at line 86 returns 200 with `application/pdf` for every client and remains the accessible evidence copy for S4.

[R] `references.txt` is untouched: the root reference file is outside the G1 write boundary and no citation change is proposed. The existing [S4]/[S5] coverage notes stay as written.
