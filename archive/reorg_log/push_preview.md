# Push preview (no push performed)

## Sync status

| Check | Result |
|---|---|
| Branch | `main` |
| HEAD | `6b6f39a` — `chore(release): record v4.0.0 verification and final state` |
| `origin/main` | `6b6f39a96d0b9f34f05dcc437fa6e9fcacd9b0d9` |
| Ahead / behind | **0 / 0** |
| Remote | `https://github.com/philopateerreda/GCI-Final-Assignment.git` (no embedded credentials) |
| Public readability | not proven here; `git ls-remote` exited 0 but a credential helper may have supplied auth. Recheck anonymously at G2. |
| `release/v4` | `6b6f39a`; not pushed or rewritten |
| Tag `v4.0.0` | annotated object `ea15eb0…`, points at `6b6f39a`; untouched |
| `pre-reorg` | local branch at `6b6f39a`; **not pushed** |

**No pre-existing unpushed commit.** After G2, the only commits ahead of `origin/main` will be the eight R-commits. No third-party commit rides along.

## Purpose of `pre-reorg`

It is the remote restore point for the old layout. Push it **before** `main` at G2 (unless the user says skip). Old-layout links and `release/v4` references can then be resolved by ref even after `main` changes.

- `pre-reorg` contains the exact pre-move tree at `6b6f39a`.
- `main` will contain the reorganized tree plus new documentation.
- `release/v4` remains at `6b6f39a` and is not modified.

## Push commands planned (only after “push”)

```powershell
git push origin pre-reorg
git push origin main
```

Plain pushes only: no `--force`, `--force-with-lease`, `--mirror`, `--all`, `--tags`, no `release/v4`, no credential handling. If rejected or authentication is requested: stop and report.

## Post-push verification planned

1. `git ls-remote origin refs/heads/main` equals `git rev-parse main`.
2. Fresh clone outside the tree; compare its file list to `git ls-files` at `HEAD`.
3. Root listing, count and size; no dataset, docx, notebook backups, caches or smoke material.
4. `post_push_verify.md` with repo URL, pushed SHA and old-layout URLs that no longer resolve on `main` (reachable via `pre-reorg`).

## G2 will re-check

- 20 largest tracked files; no newly pushed blob >25 MB (GitHub warns at 50, rejects at 100).
- No tracked CSV under `data/`; no tracked `*.docx`; no tracked file matching residue patterns.
- No tracked file whose SHA256 equals the dataset or an F1 artifact.
- Secret scan on the push delta; notebook-output scan restated for tracked notebooks.
- `git push --dry-run origin main`.
