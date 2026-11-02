# WP4 — ITT, Floor contamination and harm gate
Status: DONE

Inputs:
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/final_metrics.json` — SHA-256 `1d14a4fea10ab391631379f82cd6a82e5a65ede4f01db5b540c9aec3612eea1e`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/FINAL_ASSESSMENT_HANDOFF.md` — SHA-256 `07c3965e8a5730e895164e5ac18c3b0a1cadf5f4f026214e868c18d1585ec6ab`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/references.txt` — SHA-256 `b12fb18aafc83e2d599e15d04c689ee5cd85c10082c1761ab0c6f1d01606d361`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/results/sources/ascarza_2016_source.txt` — SHA-256 `0cfda524a29346e7db5640034deda927f4150d2f2b1eaa86688a0fd504aea326`.

Population / assumptions:
- [R] Linked-household ITT is a prospective design requirement; current linkage and treatment outcomes do not exist.
- [A] Queue economics are pitch assumptions, not estimable prevention rates.

Method (≤10 lines)
[E] Quoted the frozen gate and queue scalars, checked them against the handoff, and read the accessible Ascarza paper abstract/experiment sections. Wrote a concise supporting addendum without changing the protocol or any numerical estimate.

Results:
| Queue hypothesis [R] | Frozen raw rows [E] | Selected at-risk value share [E/A] |
|---|---:|---:|
| Billing check | 582 | 23.4% |
| Network check | 266 | 10.4% |
| Handset check | 791 | 30.7% |
| Digital-only residual | 866 | 35.5% |
[E] Addendum contains 368 words; no new numerical estimates.

Acceptance checks:
- [E] PASS: exact queue counts 582/266/791/866 and rounded shares 23.4/10.4/30.7/35.5%.
- [E] PASS: unchanged .005 per-look harm threshold and .5/1.0 planned looks.
- [E] PASS: zero new estimates; concise ≤550-word one-page content target.

Deviations from brief:
[E] HBS access was blocked; the existing accessible full-paper copy supports the intervention-specific quote.

Claims now allowed:
[R] A proposed ITT estimand, logged Floor contamination, and a preregistered safety tripwire.

Claims still forbidden:
[R] Company A causal effects, queue-specific prevention findings, powered subgroup inference or generalized service-contact harm.

Open questions for human: [E] None; integration remains a separate human decision.
