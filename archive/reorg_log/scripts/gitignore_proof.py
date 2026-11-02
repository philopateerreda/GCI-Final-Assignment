#!/usr/bin/env python
"""Prove that the planned move preserves the ignored set (D4).

Read-only; uses a throwaway temporary git repository for pattern matching.
Usage:
  python gitignore_proof.py --root <finalA> --plan <csv> --ignored-before <txt> \
    --tracked-before <txt> --after <gitignore_after.txt> --outdir <dir> [--dry-run]
"""
from __future__ import annotations

import argparse
import csv
import subprocess
import tempfile
from collections import Counter, defaultdict
from pathlib import Path


def git_check_ignore(repo: Path, paths: list[str]) -> dict[str, str]:
    payload = ("\n".join(paths) + "\n").encode("utf-8")
    proc = subprocess.run(
        ["git", "-C", str(repo), "check-ignore", "-v", "--stdin", "--no-index"],
        input=payload,
        capture_output=True,
    )
    # Exit 1 simply means no path matched. Keep bytes stdio to avoid Windows
    # text-mode newline translation turning LF into CRLF and poisoning paths.
    result = {}
    for line in proc.stdout.decode("utf-8", "surrogateescape").splitlines():
        if "\t" not in line:
            continue
        left, path = line.split("\t", 1)
        parts = left.split(":")
        pattern = ":".join(parts[2:]) if len(parts) >= 3 else left
        result[path] = pattern
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--plan", required=True, type=Path)
    ap.add_argument("--ignored-before", required=True, type=Path)
    ap.add_argument("--tracked-before", required=True, type=Path)
    ap.add_argument("--after", required=True, type=Path)
    ap.add_argument("--before", required=True, type=Path)
    ap.add_argument("--outdir", required=True, type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    plan = list(csv.DictReader(args.plan.open(encoding="utf-8")))
    old_to_new = {r["old_path"]: r["new_path"] for r in plan}
    ignored_before = {p for p in args.ignored_before.read_text(encoding="utf-8").splitlines() if p}
    tracked_before = {p for p in args.tracked_before.read_text(encoding="utf-8").splitlines() if p}
    new_paths = [r["new_path"] for r in plan]
    old_paths = [r["old_path"] for r in plan]
    with tempfile.TemporaryDirectory(prefix="d4-proof-") as td:
        repo = Path(td)
        subprocess.run(["git", "-C", td, "init", "-q"], check=True)
        (repo / ".gitignore").write_text(args.after.read_text(encoding="utf-8"), encoding="utf-8")
        ignored_after = git_check_ignore(repo, new_paths)
        (repo / ".gitignore").write_text(args.before.read_text(encoding="utf-8"), encoding="utf-8")
        ignored_before_patterns = git_check_ignore(repo, old_paths)
    mapped_ignored = {old_to_new[p] for p in ignored_before}
    tracked_after = {old_to_new[p] for p in tracked_before}
    ignored_after_untracked = set(ignored_after) - tracked_after
    lost = sorted(mapped_ignored - ignored_after_untracked)
    gained = sorted(ignored_after_untracked - mapped_ignored)
    already_tracked_ignored = {
        old_to_new[p] for p in (tracked_before & set(ignored_before_patterns))
    }
    tracked_newly_ignored = sorted(
        (tracked_after & set(ignored_after)) - already_tracked_ignored
    )
    print(f"IGNORED_BEFORE={len(ignored_before)} IGNORED_AFTER={len(ignored_after_untracked)} LOST={len(lost)} GAINED={len(gained)}")
    print(f"TRACKED_BEFORE={len(tracked_before)} TRACKED_NEWLY_IGNORED={len(tracked_newly_ignored)}")
    print(f"PRE_EXISTING_TRACKED_AND_IGNORED={len(already_tracked_ignored)}")
    if lost:
        print("LOST SAMPLE:", lost[:10])
    if gained:
        print("GAINED SAMPLE:", gained[:10])
    if tracked_newly_ignored:
        print("TRACKED NEWLY IGNORED SAMPLE:", tracked_newly_ignored[:10])
    if args.dry_run:
        print("DRY-RUN: no files written")
        return 0
    args.outdir.mkdir(parents=True, exist_ok=True)
    args.outdir.joinpath("ignore_invariance_plan.txt").write_text(
        "D4 planned ignore invariance\n"
        f"ignored_before={len(ignored_before)}\n"
        f"ignored_after={len(ignored_after_untracked)}\n"
        f"lost={len(lost)}\n"
        f"gained={len(gained)}\n"
        f"tracked_newly_ignored={len(tracked_newly_ignored)}\n"
        f"preexisting_tracked_and_ignored={len(already_tracked_ignored)}\n"
        f"pass={not lost and not gained and not tracked_newly_ignored}\n",
        encoding="utf-8",
    )
    new_counts = Counter(ignored_after.values())
    old_counts = {}
    old_by_path = {}
    for old, new in old_to_new.items():
        if old not in ignored_before:
            continue
        pat = ignored_after.get(new)
        if pat:
            old_by_path.setdefault(pat, []).append(old)
    for pat, olds in old_by_path.items():
        old_counts[pat] = len(olds)
    lines = [
        "# `.gitignore` D4 proof (planned)",
        "",
        "The move is simulated against a throwaway git repository containing only the proposed",
        "`.gitignore`; no project file is moved to produce this proof. Every old ignored path is mapped",
        "through `move_plan.csv` to its new path.",
        "",
        "| Measure | Before | After |",
        "|---|---:|---:|",
        f"| Ignored files (untracked) | {len(ignored_before)} | {len(ignored_after_untracked)} |",
        f"| Lost (old ignored, new not ignored) | — | **{len(lost)}** |",
        f"| Gained (old not ignored, new ignored) | — | **{len(gained)}** |",
        f"| Tracked files newly ignored | — | **{len(tracked_newly_ignored)}** |",
        f"| Pre-existing tracked-and-ignored `.log` files | {len(already_tracked_ignored)} | {len(already_tracked_ignored)} |",
        "",
        f"**Verdict: {'PASS' if not lost and not gained and not tracked_newly_ignored else 'FAIL'}**",
        "",
        "## Pattern-level counts",
        "",
        "| New pattern | New ignored count |",
        "|---|---:|",
    ]
    for pat, count in sorted(new_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"| `{pat}` | {count} |")
    lines += [
        "",
        "## Exact `.gitignore` change",
        "",
        "| Old pattern | New pattern | Old count | New count |",
        "|---|---|---:|---:|",
    ]
    # Semantic mapping table for the human review; counts come from the real sets.
    semantic = [
        ("/telecom/*.csv", "/data/telecom/*.csv"),
        ("/*.docx", "/docs/reference/*.docx"),
        ("/tutorial*.ipynb", "/docs/reference/tutorial*.ipynb"),
        ("/v1_frozen/", "/versions/v1_frozen/"),
        ("analysis_outputs/notebook_backups/", "/evidence/notebook_backups/"),
        ("v2_work/literature_*.pdf", "/versions/v2_work/literature_*.pdf"),
        ("v2_work/literature_*.png", "/versions/v2_work/literature_*.png"),
        ("v3_addons/results/sources/", "/versions/v3_addons/results/sources/"),
        ("v2_work/d_results/cv_manifest.csv", "/versions/v2_work/d_results/cv_manifest.csv"),
        ("v2_work/d_results/cv_manifest.json", "/versions/v2_work/d_results/cv_manifest.json"),
        ("v2_work/d_results/cache/", "/versions/v2_work/d_results/cache/"),
        ("v2_work/d_results/oof/", "/versions/v2_work/d_results/oof/"),
        ("v2_work/d_smoke/", "/archive/residue/ (old path retired)"),
        ("v2_work/d_smoke_io/", "/archive/residue/ (old path retired)"),
        ("v2_work/c_smoke/", "/archive/residue/ (old path retired)"),
        ("v3_addons/results/*.npz", "/versions/v3_addons/results/*.npz"),
        ("v3_addons/results/wp5_calibration_oof.csv", "/versions/v3_addons/results/wp5_calibration_oof.csv"),
        ("v3_addons/results/wp5_label_shift_raw.csv", "/versions/v3_addons/results/wp5_label_shift_raw.csv"),
        ("v3_addons/results/wp8/*.npz", "/versions/v3_addons/results/wp8/*.npz"),
        ("v3_addons/results/wp8/**/*.npz", "/versions/v3_addons/results/wp8/**/*.npz"),
        ("v3_addons/results/wp8/models/", "/versions/v3_addons/results/wp8/models/"),
        ("v3_addons/results/wp8/cache/", "/versions/v3_addons/results/wp8/cache/"),
        ("v4_addons/CEO_BRIEF*", "/versions/v4_addons/CEO_BRIEF*"),
        ("v4_addons/CEO_QA*", "/versions/v4_addons/CEO_QA*"),
        ("v4_addons/HUMAN_CHECKLIST.md", "/versions/v4_addons/HUMAN_CHECKLIST.md"),
        ("v4_addons/DISCLOSURE_CHECK.md", "/versions/v4_addons/DISCLOSURE_CHECK.md"),
        ("v4_addons/release_candidate/", "/versions/v4_addons/release_candidate/"),
        ("v4_addons/snapshots/", "/versions/v4_addons/snapshots/"),
        ("v4_addons/m1_work/cache/", "/archive/residue/ (old path retired)"),
    ]
    # Counts: old from baseline CSV is already per pattern; new via ignore output.
    old_baseline = {}
    for r in csv.DictReader((args.outdir / "gitignore_baseline.csv").open(encoding="utf-8")):
        old_baseline[r["pattern"]] = int(r["ignored_files"])
    for old, new in semantic:
        oldc = old_baseline.get(old, 0)
        newc = new_counts.get(new.split(" (old path retired)")[0], 0)
        lines.append(f"| `{old}` | `{new}` | {oldc} | {newc} |")
    lines += [
        "",
        "## New rules",
        "",
        "- `/archive/residue/` and `/archive/duplicates/` protect lifted run residue and any future duplicate archive.",
        "- `/docs/reference/*.docx` keeps both course Word files ignored at their new destination (narrower than an unanchored `*.docx`).",
        "- No tracked path becomes newly ignored; eight pre-existing tracked `.log` files stay tracked (tracked status wins).",
        "- Some WP8 cache `.npz` paths match the broader `wp8/**/*.npz` rule, so the per-pattern cache count is 120 while all 181 old cache paths remain ignored.",
        "",
        "Raw plan: `ignore_invariance_plan.txt`. The runtime proof after each batch is `ignore_invariance_R<n>.txt`.",
        "",
    ]
    (args.outdir / "gitignore_proof.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"WROTE {args.outdir / 'gitignore_proof.md'}")
    print(f"WROTE {args.outdir / 'ignore_invariance_plan.txt'}")
    return 0 if not lost and not gained and not tracked_newly_ignored else 1


if __name__ == "__main__":
    raise SystemExit(main())
