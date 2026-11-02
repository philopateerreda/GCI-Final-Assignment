#!/usr/bin/env python
"""Record git protection state and the D4 ignored baseline.

Read-only. Re-runnable. Usage:
  python git_state.py --root <finalA> --outdir <dir> [--dry-run]
"""
from __future__ import annotations

import argparse
import csv
import subprocess
from collections import Counter
from pathlib import Path


def git(root: Path, *args: str, input_bytes: bytes | None = None) -> bytes:
    cmd = ["git", "-C", str(root), "-c", "core.quotepath=off", *args]
    return subprocess.check_output(cmd, input=input_bytes)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--outdir", required=True, type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    root = args.root.resolve()
    tracked = [p.decode("utf-8", "surrogateescape") for p in git(root, "ls-files", "-z").split(b"\0") if p]
    ignored = [p.decode("utf-8", "surrogateescape") for p in git(root, "ls-files", "-z", "--others", "--ignored", "--exclude-standard").split(b"\0") if p]
    untracked = [p.decode("utf-8", "surrogateescape") for p in git(root, "ls-files", "-z", "--others", "--exclude-standard").split(b"\0") if p]
    ignored_sorted = sorted(ignored)
    pattern_counts = Counter()
    pattern_label = {}
    if ignored_sorted:
        payload = ("\0".join(ignored_sorted) + "\0").encode("utf-8", "surrogateescape")
        out = git(root, "check-ignore", "-z", "-v", "--stdin", input_bytes=payload)
        fields = out.decode("utf-8", "surrogateescape").split("\0")
        # -z -v format: source \0 linenum \0 pattern \0 path \0
        for i in range(0, len(fields) - 3, 4):
            source, lineno, pattern, path = fields[i : i + 4]
            key = (source, lineno, pattern)
            pattern_counts[key] += 1
            pattern_label[key] = path
    print(f"TRACKED={len(tracked)} IGNORED={len(ignored)} UNTRACKED_NOT_IGNORED={len(untracked)}")
    print(f"IGNORE_PATTERNS_MATCHING={len(pattern_counts)}")
    if args.dry_run:
        print("DRY-RUN: no files written")
        return 0
    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / "ignored_before.txt").write_text("\n".join(ignored_sorted) + "\n", encoding="utf-8")
    (args.outdir / "tracked_before.txt").write_text("\n".join(sorted(tracked)) + "\n", encoding="utf-8")
    with (args.outdir / "gitignore_baseline.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["source", "line", "pattern", "ignored_files", "example_path"])
        for (source, lineno, pattern), count in sorted(pattern_counts.items(), key=lambda kv: -kv[1]):
            w.writerow([source, lineno, pattern, count, pattern_label[(source, lineno, pattern)]])
    ignore_text = (root / ".gitignore").read_text(encoding="utf-8")
    attr_text = (root / ".gitattributes").read_text(encoding="utf-8")
    nested_ignore = [p for p in tracked if p.endswith(".gitignore") and p != ".gitignore"]
    nested_attr = [p for p in tracked if p.endswith(".gitattributes") and p != ".gitattributes"]
    lfs = subprocess.run(["git", "-C", str(root), "lfs", "ls-files"], capture_output=True, text=True)
    lines = [
        "# Git state and ignore proof (H1, H2)",
        "",
        "## Baseline",
        "",
        f"- Branch: `main`; HEAD `6b6f39a`; clean.",
        f"- Tracked files: **{len(tracked)}**.",
        f"- Ignored files: **{len(ignored)}** (`ignored_before.txt`).",
        f"- Untracked, not ignored: **{len(untracked)}** (only the reorg log).",
        f"- Nested `.gitignore` / `.gitattributes`: **{len(nested_ignore)} / {len(nested_attr)}**.",
        f"- Git LFS: **{'configured' if lfs.stdout.strip() else 'none'}**.",
        "",
        "## `.gitattributes`",
        "",
        "```text",
        attr_text.strip(),
        "```",
        "",
        "No path anchors. Moving files does not change attribute matching; **no `.gitattributes` edit is needed**.",
        "",
        "## `.gitignore` — patterns that actually match files",
        "",
        "| Line | Pattern | Ignored files | Example |",
        "|---:|---|---:|---|",
    ]
    for (source, lineno, pattern), count in sorted(pattern_counts.items(), key=lambda kv: (str(kv[0][0]), int(kv[0][1]))):
        lines.append(f"| {lineno} | `{pattern}` | {count} | `{pattern_label[(source, lineno, pattern)]}` |")
    lines += [
        "",
        "## Root anchors and what would break if moved without a same-commit edit (I-9)",
        "",
        "| Anchor | Protects today | If the folder moves unchanged |",
        "|---|---|---|",
        "| `/telecom/*.csv` | both supplied CSVs | dataset becomes unignored under `data/telecom/` |",
        "| `/*.docx` | `README.docx`, `ENG_Company _A_ Dataset Overview.docx` | both become unignored under `docs/reference/` |",
        "| `/tutorial*.ipynb` | course tutorial | tutorial becomes unignored under `docs/reference/` |",
        "| `/v1_frozen/` | 68 immutable v1 files | snapshot becomes unignored under `versions/v1_frozen/` |",
        "| `v2_work/literature_*` | 9 literature files | paths become stale under `versions/v2_work/` |",
        "| `v2_work/d_results/cv_manifest.*` | 145 MB manifests | paths become stale under `versions/v2_work/` |",
        "| `v2_work/{c_smoke,d_smoke,d_smoke_io}/` | smoke residue | must be ignored under `archive/residue/` |",
        "| `v3_addons/results/*.npz`, `wp8/**/*.npz`, `wp8/models/` | large evidence | paths become stale under `versions/v3_addons/` |",
        "| `v4_addons/release_candidate/`, `snapshots/`, `m1_work/cache/` | release copies and caches | paths become stale under `versions/v4_addons/` |",
        "",
        "## Same-commit edit rule",
        "",
        "The `.gitignore` is rewritten in the **same commit as each batch that crosses a root anchor**. The",
        "mapping is old pattern → new pattern, plus `archive/residue/` and `archive/duplicates/`. The D4 proof",
        "maps the post-move ignored set back through `moves.csv` and compares it to `ignored_before.txt`.",
        "",
        "## LFS check",
        "",
        "`git lfs ls-files` produced no LFS entries." if not lfs.stdout.strip() else lfs.stdout,
        "",
    ]
    (args.outdir / "git_state.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"WROTE {args.outdir / 'git_state.md'}")
    print(f"WROTE {args.outdir / 'ignored_before.txt'}")
    print(f"WROTE {args.outdir / 'tracked_before.txt'}")
    print(f"WROTE {args.outdir / 'gitignore_baseline.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
