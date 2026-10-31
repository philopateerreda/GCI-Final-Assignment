# R0 — Release preflight

Status: COMPLETED_ACCEPTED

The v4 release directive's section-1 preconditions were run read-only and all pass. The work tree is a git repository with the expected `origin`, a set identity, no tracked raw data, intact frozen hashes, STATE ready for release and a clean boundary check. The release branch can be created; nothing has been committed or pushed at this point.

## Repository, remote and identity

```text
true
origin	https://github.com/philopateerreda/GCI-Final-Assignment.git (fetch)
origin	https://github.com/philopateerreda/GCI-Final-Assignment.git (push)
main
e8f6520 Initial commit: Company A churn targeting, frozen evaluation, and v3 audit
philopateer reda <filopateerredakamel2004@gmail.com>
core.autocrlf = true
```

Base commit: `e8f652013672c0a603338740425dba69bf663ba3` on `main`. The remote is the account holder's public repository.

## Working tree at preflight

```text
M .gitignore
 M README.md
 M v3_addons/HANDBACK.md
 M v3_addons/reports/WP7_report.md
?? v4_addons/
```

5 paths are dirty: the two release edits outside `v4_addons` (`README.md`, `.gitignore`), the two v3 status documents refreshed by D1, and the untracked `v4_addons/` tree. All are expected release inputs.

## Raw data guard

```text
$ git ls-files telecom
(empty)
$ git check-ignore -v telecom/Client.csv telecom/Record.csv
.gitignore:16:/telecom/*.csv	telecom/Client.csv
.gitignore:16:/telecom/*.csv	telecom/Record.csv
```

Tracked files under `telecom/`: 0. Both raw CSVs are ignored, so the provider's data cannot enter the public repository.

## Line endings

```text
# Hash-bound evidence bundle: keep file bytes exactly as produced.
* -text
```

`core.autocrlf` is `true`, but the existing `* -text` attribute already preserves bytes for every file. The directive's EOL fallback is therefore not needed; no `.gitattributes` change is planned.

## Frozen integrity against the receipt

| file | receipt value | sha256 | equals receipt |
|---|---:|---|---|
| `philopateer.pdf` | 846,608 | `a51d2c0ff8aa6ebb0f679e680d6424b01cd7b95b9a0d23ae7a2eecc56de210ea` | yes |
| `philopateer.pptx` | 1,310,666 | `a50a66fd77d062bdc45aeefb00ce8652b20b952de06dcb27e8ab4f15c37e46bc` | yes |
| `philopateer.ipynb` | 1,857,125 | `aaa170b19923c087f9b38f85b546626b7465a3d17f5ae7037812c6aed5736b35` | yes |
| `references.txt` | 18,843 | `b12fb18aafc83e2d599e15d04c689ee5cd85c10082c1761ab0c6f1d01606d361` | yes |
| `analysis_outputs/claims_ledger.csv` | 278 rows | `b4dce03b43f6bd1b9ef3142759e0cb88682527af2f9f8824902521d88729c5b4` | yes |

All four deliverables and the ledger match the release receipt: 5 of 5 entries match on bytes and SHA-256.

## Release state and boundary

- `STATE.md` says `READY_FOR_CEO_FALLBACK_A` (fallback A wording for the README).
- Boundary check (last R0 preflight run): clean, 4,571 files checked, 6 accepted changes, 0 unexpected, 2 gate files present.
- Accepted changes are the two D1-refreshed v3 documents, their `.pre_v4` backups, `README.md` and `.gitignore`.

## Size rule

- Push candidate set: 782 tracked or non-ignored untracked files.
- Files over 5 MB in the candidate set: 0 (excluded and listed here if any).
- Files over 50 MB: 0.

## Verdict

**PASS** — all section-1 preconditions hold. Proceed to README binding and staged checks.
