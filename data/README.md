# data — the supplied inputs

**What it answers:** which input data the frozen run used, and what condition it was in.

**Contents**

| File | Bytes | SHA256 |
|---|---:|---|
| `telecom/Client.csv` | 17,937,775 | `264a58512dc857fff29e11ef43fd53bc4407be23aac9dcc2c0df23536c800778` |
| `telecom/Record.csv` | 30,182,432 | `5bd563bb77b357920832510b78d6842060d928cb5de8c0aaf79aa2a647e2271a` |

Hashes: `evidence/audit.json` (`source_sha256`). Data dictionary: `docs/reference/ENG_Company _A_ Dataset Overview.docx` (git-ignored, course-supplied).

**Who reads it:** only the frozen pipeline (`pipeline/analysis_pipeline.py`), which joins the two files one-to-one on `Customer_ID`.

**Current?** Supplied and frozen (F3). Git-ignored: **do not redistribute**. The supplied files are not modified.

**How it is regenerated:** not regenerable. They are course-supplied inputs; the repository carries hashes and profiles, not the data.

**Caveats**

- 100,000 rows × 100 columns after the join; sample churn 49.562%; one-to-one ID join; zero duplicate predictor rows (`evidence/audit.json`).
- Data-quality anomalies are recorded, not repaired: 133 negative equipment ages, 23 negative recurring charges, 357 missing recurring charges (`evidence/audit.json`).
- Never commit the CSVs or sample rows. `.gitignore` blocks `/data/telecom/*.csv`; the pre-push audit checks that no tracked CSV exists under `data/`.
- The old path `telecom/Client.csv` in frozen records is stale by design; resolve it through `archive/reorg_log/path_map.csv`.
