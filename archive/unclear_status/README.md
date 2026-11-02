# unclear status — none

No file was left with `unclear_status`. The Phase-1 classification assigned every one of the
4,971 working-tree files to exactly one group and one `move_plan.csv` row; the 56 groups are
listed in `archive/reorg_log/role_map.md` (reorg log), and the per-file evidence is in
`archive/reorg_log/role_map.csv`.

The two cases that could have landed here were resolved by evidence:

- The `ENG_Company _A_ Dataset Overview.docx` is course-supplied (its text and the course
  manifest identify it), so it went to `docs/reference/`, not `submission/`.
- The nine literature files are third-party research, so they stay with `versions/v2_work/`
  and remain git-ignored.

Nothing is pending a human decision in this folder. If a later review finds a file with unclear
ownership, add it here with a one-line reason; do not delete it.
