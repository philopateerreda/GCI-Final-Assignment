# Planned final tree

Built from `move_plan.csv` + `inventory.csv`: **4971** original files / **575,499,423 bytes**. New READMEs/log files are additional.

## Top level

| Destination | Files | Bytes | MiB |
|---|---:|---:|---:|
| `versions/` | 2519 | 483,407,799 | 461.01 |
| `data/` | 2 | 48,120,207 | 45.89 |
| `archive/` | 2373 | 21,315,406 | 20.33 |
| `evidence/` | 60 | 15,473,401 | 14.76 |
| `submission/` | 3 | 4,014,399 | 3.83 |
| `docs/` | 6 | 2,761,409 | 2.63 |
| `pipeline/` | 6 | 405,172 | 0.39 |
| `(root file)/` | 2 | 1,630 | 0.00 |

## Two-level view

| Destination prefix | Files | Bytes |
|---|---:|---:|
| `(root files)` | 2 | 1,630 |
| `archive/residue` | 2372 | 21,305,518 |
| `archive/superseded` | 1 | 9,888 |
| `data/telecom` | 2 | 48,120,207 |
| `docs/(files)` | 3 | 72,168 |
| `docs/reference` | 3 | 2,689,241 |
| `evidence/(files)` | 15 | 1,096,061 |
| `evidence/charts` | 9 | 1,635,187 |
| `evidence/models` | 1 | 1,375,735 |
| `evidence/notebook_backups` | 6 | 6,905,591 |
| `evidence/slide_renders` | 15 | 1,621,376 |
| `evidence/tables` | 14 | 2,839,451 |
| `pipeline/(files)` | 6 | 405,172 |
| `submission/(files)` | 3 | 4,014,399 |
| `versions/v1_frozen` | 68 | 15,477,684 |
| `versions/v2_work` | 1990 | 348,393,099 |
| `versions/v3_addons` | 283 | 111,699,239 |
| `versions/v4_addons` | 178 | 7,837,777 |

## Shape

```text
finalA/
├── README.md
├── .gitignore, .gitattributes
├── submission/       3 graded artifacts + README
├── pipeline/         4 historical scripts + references + requirements + README
├── data/telecom/     2 supplied CSVs (ignored)
├── evidence/         receipts, charts, tables, model, renders, backups
├── versions/         v1_frozen, v2_work, v3_addons, v4_addons + VERSIONS.md
├── docs/             3 FINAL_* notes + reference/ (2 docx + tutorial) + README
└── archive/          residue/, duplicates/, superseded/, unclear_status/, reorg_log/
```

The empty `.qoder-office-pptx-locks/` contains no file and is removed only after the move; no byte is deleted.
