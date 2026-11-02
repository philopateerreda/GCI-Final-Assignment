# docs — human context

**What it answers:** how to read the package and what the v2 upgrade changed.

**Contents**

| File | Bytes | What it is |
|---|---:|---|
| `FINAL_ASSESSMENT_HANDOFF.md` | 54,432 | Technical handoff: model, policy, economics, audit, QA |
| `FINAL_ASSESSMENT_READING_NOTE.md` | 13,912 | Short reading guide with the headline tables |
| `FINAL_V2_UPGRADE_REPORT.md` | 3,824 | What v2 changed, what it rejected, exact hashes |
| `reference/README.docx` | 791,212 | Course assignment brief (git-ignored) |
| `reference/ENG_Company _A_ Dataset Overview.docx` | 787,254 | Course data dictionary (git-ignored) |
| `reference/tutorial (2).ipynb` | 1,110,775 | Course tutorial notebook (git-ignored) |

**Who reads it:** the author, the assessor, and anyone who needs the reasoning behind a number.

**Current?** The three `FINAL_*` notes are v2-era context and remain accurate for the model and economics. v4 notes deliberately stay in `versions/v4_addons/` (I-12); they are not duplicated here.

**How it is regenerated:** authored, not generated. The numbers they quote come from `evidence/` and `versions/v2_work/final_metrics.json`.

**Caveats**

- The three reference files are course-supplied and git-ignored; they are not redistributed.
- 202 repo-path references in the docs point at the old layout (e.g. `analysis_outputs/…`, `v1_frozen/…`). They are stale by design; resolve them with `archive/reorg_log/path_map.csv`.
- The handoff contains `file:///D:/…` absolute links from the authoring machine; they are provenance, not portable links.
- Do not edit the frozen hashes quoted here; the primary receipts are in `evidence/` and `versions/v4_addons/`.
