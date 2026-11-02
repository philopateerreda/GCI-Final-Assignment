# R1 — Pre-commit safety checks

Status: COMPLETED_ACCEPTED

Every check in the release directive's pre-commit list was run against the staged release set: 162 files totalling 2,886,094 bytes. All checks pass; the commits can be created.

## Secret scan

Credential patterns searched across every staged text file: `ghp_`, `github_pat_`, `AKIA`, `sk-` keys, and private-key headers. Real hits: 0.

The word `token` appears in 74 staged files; every hit is benign:

- render registries use a JSON field named `tokens` (the binding registry for each report);
- code identifiers such as `MISSING_TARGET_TOKENS` and ledger tokenisation variables;
- prose describing numeric tokens in the ledger tooling.

`password`: 1 files. `secret`: 1 files. `api_key`: 1 files.

## README local-path scan

Absolute local paths or usernames in `README.md`: 0. Patterns checked: `D:/`, `C:\`, `file:///`, `/Users/`, `/home/`.

## Raw-data scan

- Tracked files under `telecom/`: 0.
- Provider columns in the two raw headers: 100.
- Staged CSVs outside `analysis_outputs/` whose headers were compared: 116.
- Derived CSVs sharing any provider column name: 0.

No staged CSV carries the provider's schema; the raw files remain ignored and untracked.

This report, its results JSON and its render registry are produced by the check itself and are added to the index after the scan; the counts above describe the input set.

## Hash integrity of the staged blobs

| file | staged blob sha256 | equals receipt |
|---|---|---|
| `philopateer.pdf` | `a51d2c0ff8aa6ebb0f679e680d6424b01cd7b95b9a0d23ae7a2eecc56de210ea` | yes |
| `philopateer.pptx` | `a50a66fd77d062bdc45aeefb00ce8652b20b952de06dcb27e8ab4f15c37e46bc` | yes |
| `philopateer.ipynb` | `aaa170b19923c087f9b38f85b546626b7465a3d17f5ae7037812c6aed5736b35` | yes |
| `references.txt` | `b12fb18aafc83e2d599e15d04c689ee5cd85c10082c1761ab0c6f1d01606d361` | yes |
| `analysis_outputs/claims_ledger.csv` | `b4dce03b43f6bd1b9ef3142759e0cb88682527af2f9f8824902521d88729c5b4` | yes |

Mismatches between staged bytes and the receipt: 0.

## README checks

`check_readme.py --check` returns PASS: 149 rendered tokens, 105 distinct, all bound; 24 relative paths resolve against the index; no template markers, no absolute paths, GitHub-compatible markdown only.

## Line-ending integrity

`.gitattributes` is `* -text`, so every file keeps its bytes. The staged blob hashes above equal both the working files and the receipt; no EOL normalisation occurred and no `.gitattributes` change is needed.

## Size rule

- Staged set: 162 files, 2,886,094 bytes.
- Largest staged file: 646,624 bytes.
- Files over 5 MB: 0. Files over 50 MB: 0.

## Verdict

**PASS** — no secrets, no raw data, no local paths in the README, intact hashes, clean README checks and preserved line endings.
