# Notebook output scan

All **15** notebooks were parsed as JSON. No notebook was executed and no output body is reproduced here (H5).

| Notebook | Code cells | Outputs | Max table rows | >20-row outputs | Applicant tokens | Images | Errors |
|---|---:|---:|---:|---:|---|---:|---:|
| `analysis_outputs/notebook_backups/philopateer-20261028-121046.ipynb` | 9 | 5 | 74 | 2 | none | 0 | 1 |
| `analysis_outputs/notebook_backups/philopateer-20261028-121454.ipynb` | 9 | 42 | 859 | 14 | `Customer_ID`, `hnd_price`, `income`, `mou_Mean`, `ownrent`, `totmrc_Mean` | 9 | 1 |
| `analysis_outputs/notebook_backups/philopateer-20261028-121816.ipynb` | 9 | 42 | 859 | 14 | `Customer_ID`, `hnd_price`, `income`, `mou_Mean`, `ownrent`, `totmrc_Mean` | 9 | 0 |
| `analysis_outputs/notebook_backups/philopateer-20261028-122457.ipynb` | 9 | 42 | 859 | 14 | `Customer_ID`, `hnd_price`, `income`, `mou_Mean`, `ownrent`, `totmrc_Mean` | 9 | 0 |
| `analysis_outputs/notebook_backups/philopateer-20261028-123510.ipynb` | 9 | 43 | 859 | 14 | `Customer_ID`, `hnd_price`, `income`, `mou_Mean`, `ownrent`, `totmrc_Mean` | 9 | 0 |
| `analysis_outputs/notebook_backups/philopateer-20261028-205244.ipynb` | 9 | 42 | 859 | 14 | `Customer_ID`, `hnd_price`, `income`, `mou_Mean`, `ownrent`, `totmrc_Mean` | 9 | 0 |
| `philopateer.ipynb` | 25 | 60 | 859 | 16 | `Customer_ID`, `hnd_price`, `income`, `mou_Mean`, `ownrent`, `totmrc_Mean` | 9 | 0 |
| `tutorial (2).ipynb` | 16 | 17 | 803 | 2 | `Customer_ID`, `churn`, `creditcd`, `ethnic`, `hnd_price`, `income`, `marital`, `mou_Mean`, `ownrent`, `rev_Mean`, `totmrc_Mean` | 5 | 0 |
| `v1_frozen/analysis_outputs/notebook_backups/philopateer-20261028-121046.ipynb` | 9 | 5 | 74 | 2 | none | 0 | 1 |
| `v1_frozen/analysis_outputs/notebook_backups/philopateer-20261028-121454.ipynb` | 9 | 42 | 859 | 14 | `Customer_ID`, `hnd_price`, `income`, `mou_Mean`, `ownrent`, `totmrc_Mean` | 9 | 1 |
| `v1_frozen/analysis_outputs/notebook_backups/philopateer-20261028-121816.ipynb` | 9 | 42 | 859 | 14 | `Customer_ID`, `hnd_price`, `income`, `mou_Mean`, `ownrent`, `totmrc_Mean` | 9 | 0 |
| `v1_frozen/analysis_outputs/notebook_backups/philopateer-20261028-122457.ipynb` | 9 | 42 | 859 | 14 | `Customer_ID`, `hnd_price`, `income`, `mou_Mean`, `ownrent`, `totmrc_Mean` | 9 | 0 |
| `v1_frozen/analysis_outputs/notebook_backups/philopateer-20261028-123510.ipynb` | 9 | 43 | 859 | 14 | `Customer_ID`, `hnd_price`, `income`, `mou_Mean`, `ownrent`, `totmrc_Mean` | 9 | 0 |
| `v1_frozen/philopateer.ipynb` | 9 | 42 | 859 | 14 | `Customer_ID`, `hnd_price`, `income`, `mou_Mean`, `ownrent`, `totmrc_Mean` | 9 | 0 |
| `v4_addons/release_candidate/philopateer.ipynb` | 25 | 60 | 859 | 16 | `Customer_ID`, `hnd_price`, `income`, `mou_Mean`, `ownrent`, `totmrc_Mean` | 9 | 0 |

## Findings

- Outputs with more than 20 visible table rows or applicant-level tokens: **178**.
- The graded notebook and its backups contain executed analysis outputs, including prediction-table summaries.
  Those outputs are part of the frozen F1 artifact and are **not stripped**.
- The `v1_frozen/` copies are frozen by F2; the release copy is receipt-bound. No output was edited.
- Per-notebook detail: `notebook_output_scan.csv`.

## Decision

Report only. No notebook output was removed or rewritten. If a future publication requires smaller
notebooks, that is a new artifact decision, not a reorg action.
