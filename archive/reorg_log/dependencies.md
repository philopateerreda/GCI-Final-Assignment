# Dependency scan

- Python files parsed: **92**
- Notebooks parsed: **15**
- Path/dependency rows: **3049**
- Parse errors: **0**
- Rows by tier: **A=0, B=0, C=3049**

## Reverse view — reader/writer counts by top-level target

| Target | read | write | chdir | sys.path | shell | other |
|---|---:|---:|---:|---:|---:|---:|
| `(none)` | 126 | 105 | 1 | 0 | 0 | 1771 |
| `analysis_outputs` | 14 | 5 | 0 | 0 | 0 | 190 |
| `v2_work` | 9 | 0 | 0 | 0 | 0 | 168 |
| `v3_addons` | 1 | 0 | 0 | 0 | 0 | 142 |
| `v1_frozen` | 32 | 3 | 0 | 0 | 0 | 87 |
| `v4_addons` | 0 | 0 | 0 | 0 | 0 | 119 |
| `telecom` | 5 | 2 | 0 | 0 | 0 | 91 |
| `references.txt` | 1 | 3 | 0 | 0 | 0 | 60 |
| `philopateer.ipynb` | 0 | 0 | 0 | 0 | 0 | 35 |
| `philopateer.pptx` | 0 | 0 | 0 | 0 | 0 | 35 |
| `philopateer.pdf` | 2 | 1 | 0 | 0 | 0 | 30 |
| `README.md` | 1 | 0 | 0 | 0 | 0 | 7 |
| `README.docx` | 0 | 0 | 0 | 0 | 0 | 2 |
| `requirements-python311.txt` | 0 | 0 | 0 | 0 | 0 | 1 |

## Static findings

- The scan is syntactic only: no project module is imported and no notebook is executed (I-5).
- **No code edits are proposed.** All four root entry points are Tier C under I-13: `analysis_pipeline.py` has 28 path-related lines, `restore_v1.py` needs a manifest-to-new-tree mapping, and `build_notebook.py` / `export_and_verify.py` delegate to those old-root helpers.
- Every path string in historical v2/v3/v4 code and notebooks is Tier C and will be documented as stale-by-design, not edited.
- Full per-row data, including notebook cell/line references: `dependencies.csv`.
