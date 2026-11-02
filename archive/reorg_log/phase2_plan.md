# Phase 2 — Design the tree, then stop (Gate 1)

**Status: plan complete; waiting for the word `approved`.** No project file has been moved and no project byte changed.

## 1. `move_plan.csv` (D1)

- 4,971 rows = every Phase-0 working-tree file, exactly once.
- 4,971 unique new paths; no collisions; longest new path 110 chars.
- 4,971 old paths match `hash_manifest_before.csv` exactly (0 missing, 0 extra).
- Tracked 791 / ignored 4,180 — both preserved in the plan.
- Categories: version 2,519; residue 2,372; evidence 60; course reference 3; doc 3; handin 3; pipeline entry 4; pipeline metadata 2; data 2; git config 2; superseded README 1.
- Every `.py` (92) is Tier C; `.gitattributes` needs no edit; `.gitignore` is staged per batch.

## 2. Final tree and sizes (originals only)

| Destination | Files | Bytes |
|---|---:|---:|
| `versions/` | 2,519 | 483,407,799 |
| `archive/` | 2,373 | 21,315,406 |
| `evidence/` | 60 | 15,473,401 |
| `docs/` | 6 | 2,761,409 |
| `data/` | 2 | 48,120,207 |
| `submission/` | 3 | 4,014,399 |
| `pipeline/` | 6 | 405,172 |
| root keeps | 2 | 1,630 |

```text
finalA/
├── README.md
├── .gitignore, .gitattributes
├── submission/        3 graded artifacts + README
├── pipeline/          4 historical scripts, references, requirements, README
├── data/telecom/      2 supplied CSVs (ignored)
├── evidence/          receipts, charts, tables, model, renders, backups
├── versions/          v1_frozen, v2_work, v3_addons, v4_addons, VERSIONS.md
├── docs/              3 FINAL_* notes + reference/ (2 docx + tutorial) + README
└── archive/           residue/, duplicates/, superseded/, unclear_status/, reorg_log/
```

`docs/` holds 3 notes + 3 course references + its README, so the seventh folder is justified. `archive/duplicates/` will contain a README only (0 separate duplicate moves). `archive/unclear_status/` will contain a README only (0 unclear files).

## 3. `.gitignore` diff and D4 proof

- Final text: `gitignore_after.txt`; exact diff: `gitignore_diff.md`.
- Per-batch stages: `gitignore_R1.txt` … `gitignore_R5.txt` (R6/R7 add no ignore anchors).
- Planned final proof: **4,180 ignored before / 4,180 after; 0 lost; 0 gained; 0 tracked newly ignored** (`gitignore_proof.md`).
- Per-batch proof: R0–R5 all **PASS** (`stage_ignore_proof.md`).
- The 8 pre-existing tracked `.log` files remain tracked; tracked status wins.
- `.gitattributes` (`* -text`) has no path anchor, so no edit.

## 4. Frozen set (current SHA256)

| ID | Item | SHA256 |
|---|---|---|
| F1 | `philopateer.ipynb` | `aaa170b19923c087f9b38f85b546626b7465a3d17f5ae7037812c6aed5736b35` |
| F1 | `philopateer.pdf` | `a51d2c0ff8aa6ebb0f679e680d6424b01cd7b95b9a0d23ae7a2eecc56de210ea` |
| F1 | `philopateer.pptx` | `a50a66fd77d062bdc45aeefb00ce8652b20b952de06dcb27e8ab4f15c37e46bc` |
| F1 | `README.docx` | `15328594161bb07cebefa73f643e04539c87a81ff4c2d76093c02f9c67f64aa2` |
| F1 | `ENG_Company _A_ Dataset Overview.docx` | `9953e825565d5278d2f65082e425be42d9a53b453fe84b35903bd9fc7ca4660b` |
| F2 | 67 manifest entries + manifest | 67/67 PASS; base `v1_frozen/`; manifest SHA256 `e1a154c4a230cb0df558453693b9eabcc89112947cff66261c1512db707729f9` |
| F3 | `telecom/Client.csv` | `264a58512dc857fff29e11ef43fd53bc4407be23aac9dcc2c0df23536c800778` |
| F3 | `telecom/Record.csv` | `5bd563bb77b357920832510b78d6842060d928cb5de8c0aaf79aa2a647e2271a` |

F2 coverage: 67 entries present, 67 pass, 0 missing, 0 v1 files uncovered. Full table: `frozen_before.csv`; summary: `frozen_coverage.json`.

## 5. Code edits (I-13)

**None.** All four root entry points are Tier C; see `code_edits.md`. Reasons: `analysis_pipeline.py` has 28 path-related lines; `restore_v1.py` needs a manifest-to-new-tree mapping; `build_notebook.py` / `export_and_verify.py` delegate to old-root helpers (`claim_checks`, `run_frozen_batch`). Editing only constants would produce a false “working” pipeline. The frozen snapshot's 3 `.py` files are F2 and never edited.

Tier C files with stale-by-design path records include `analysis_outputs/audit.json`, `delivery_checks.json`, `v2_work/final_metrics.json`, `v3_addons/results/wp8/outside_snapshot.json`, `v4_addons/MANIFEST_v4.json`, and the frozen protocol/receipts. `PATH_MAP.md` will list them.

## 6. Duplicate decisions (H7)

- 243 SHA256 groups / 510 files.
- 132 rows are tracked; 315 are smoke/cache copies that already move with residue.
- 0 files are sent to a separate `archive/duplicates/` action. The 4 non-obvious candidates (`a_bootstrap_test.csv`, `literature_Ascarza2016.pdf`, `ascarza_2016_source.pdf`, `c_subgroup_robustness.csv`) are path/hash-bound in v3 records and therefore evidence-bound.
- Full data: `duplicates.csv`, `duplicates.md`.

## 7. No `unclear_status` files

Every file has a role. `archive/unclear_status/README.md` will state “none”; it is not used as a dump.

## 8. Canonical version

**v2.0.0** produced the artifacts now in `submission/`; v4.0.0 is `RELEASED_FALLBACK_A` and did not change them. v1 is superseded; v3 adds audit only; v4 adds release/integrity only. Evidence: `canonical_version.md`, F1 hashes, `v4_addons/RELEASE_RECEIPT.md`, `v3_addons/HANDBACK.md`, `v4_addons/STATE.md`.

## 9. Link-break report (H11)

45 external URLs, 59 `file:///` absolute links, 655 repo-path refs, 202 distinct breaking paths. Frozen artifacts are not edited; old paths remain reachable via `pre-reorg`; `PATH_MAP.md` maps every top-level. Detail: `link_scan.md`.

## 10. Push preview

`main` = `origin/main` = `6b6f39a`, 0 ahead / 0 behind. No unpushed commit. `pre-reorg` is the remote old-layout restore point. G2 audit is delta-based. No push now; `push_preview.md`.

## 11. Batch order and commits

R1 `R1_archive` → R2 `R2_versions` → R3 `R3_evidence` → R4 `R4_docs` → R5 `R5_data` → R6 `R6_submission` → R7 `R7_pipeline` → R8 `R8_log`. Counts, bytes, per-batch ignore stage and the loop are in `batch_plan.md`.

## Decisions for you

1. **Course documents.** Text extraction proves `README.docx` is the assignment brief and `ENG_Company _A_ Dataset Overview.docx` is the supplied data dictionary. I propose both in `docs/reference/`, with `tutorial (2).ipynb`. This overrides the starting proposal's `submission/README.docx` and `data/ENG...docx`. Approve, or tell me to follow the original placement.
2. **No code edits.** All four root scripts are Tier C and stay byte-identical; current-layout reruns are not claimed. Approve, or ask for a separate runnable-pipeline scope (content changes, not this reorg).
3. **`references.txt`.** Target layout puts it in `pipeline/`; it is also a submission companion. Keep it in `pipeline/` (proposed), or move it to `submission/`?
4. **`data/` scope.** Only the two CSVs. The data dictionary stays in `docs/reference/`. Confirm.
5. **Residue volume.** 2,372 files (smoke dirs, 60 `.started`, 200 M1 caches, Python caches, lock) go to ignored `archive/residue/`; all are preserved. Confirm.
6. **Notebook outputs.** `philopateer.ipynb` is F1 and already public; it contains 60 outputs, 16 over 20 rows, with applicant-level column names. I will not strip or edit it. Pushing leaves this pre-existing exposure unchanged. Confirm you accept that, or stop the push.
7. **`docs/` as seventh folder.** 3 FINAL notes + 3 course references justify it; no fold-in. Confirm.

Reply **`approved`** for G1. No file will be moved before that.
