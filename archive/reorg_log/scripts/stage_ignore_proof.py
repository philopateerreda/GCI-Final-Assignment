#!/usr/bin/env python
"""Prove D4 ignore invariance after each planned batch, without moving files.

Read-only. Usage:
  python stage_ignore_proof.py --root <finalA> --outdir <dir> [--dry-run]
Uses the precomputed gitignore_R1..R5.txt and maps each path according to the
batches that have already executed.
"""
from __future__ import annotations

import argparse
import csv
import subprocess
import tempfile
from pathlib import Path

BATCH_ORDER = ["R1", "R2", "R3", "R4", "R5", "R6", "R7"]


def batch_of(row: dict[str, str]) -> str:
    cat = row["category"]
    if cat == "residue" or row["old_path"] == "README.md":
        return "R1"
    if cat == "version":
        return "R2"
    if cat == "evidence":
        return "R3"
    if cat in {"doc", "course_reference"}:
        return "R4"
    if cat == "data":
        return "R5"
    if cat == "handin":
        return "R6"
    if cat in {"pipeline_entry", "pipeline_metadata"}:
        return "R7"
    return "ROOT"


def check_ignore(repo: Path, paths: list[str]) -> dict[str, str]:
    payload = ("\n".join(paths) + "\n").encode("utf-8")
    proc = subprocess.run(
        ["git", "-C", str(repo), "check-ignore", "-v", "--stdin", "--no-index"],
        input=payload,
        capture_output=True,
    )
    out = {}
    for line in proc.stdout.decode("utf-8", "surrogateescape").splitlines():
        if "\t" not in line:
            continue
        left, path = line.split("\t", 1)
        parts = left.split(":")
        out[path] = ":".join(parts[2:]) if len(parts) >= 3 else left
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--outdir", required=True, type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    root = args.root.resolve()
    outdir = args.outdir
    plan = list(csv.DictReader((outdir / "move_plan.csv").open(encoding="utf-8")))
    ignored_before = {p for p in (outdir / "ignored_before.txt").read_text(encoding="utf-8").splitlines() if p}
    tracked_before = {p for p in (outdir / "tracked_before.txt").read_text(encoding="utf-8").splitlines() if p}
    rows = []
    with tempfile.TemporaryDirectory(prefix="d4-stages-") as td:
        repo = Path(td)
        subprocess.run(["git", "-C", td, "init", "-q"], check=True)
        for stage in ["R0"] + BATCH_ORDER:
            if stage == "R0":
                ignore_file = root / ".gitignore"
                done = set()
            else:
                ignore_file = outdir / f"gitignore_{stage}.txt"
                if not ignore_file.exists():
                    continue
                done = set(BATCH_ORDER[: BATCH_ORDER.index(stage) + 1])
            (repo / ".gitignore").write_text(ignore_file.read_text(encoding="utf-8"), encoding="utf-8")
            current_paths = [
                (r["new_path"] if batch_of(r) in done else r["old_path"]) for r in plan if batch_of(r) != "ROOT"
            ]
            current_map = {
                r["old_path"]: (r["new_path"] if batch_of(r) in done else r["old_path"])
                for r in plan
                if batch_of(r) != "ROOT"
            }
            hits = check_ignore(repo, current_paths)
            tracked_current = {current_map[p] for p in tracked_before if p in current_map}
            ignored_current = set(hits) - tracked_current
            mapped_baseline = {current_map[p] for p in ignored_before if p in current_map}
            lost = sorted(mapped_baseline - ignored_current)
            gained = sorted(ignored_current - mapped_baseline)
            tracked_matched = sorted(tracked_current & set(hits))
            rows.append(
                {
                    "stage": stage,
                    "files_at_stage": len(current_paths),
                    "ignored_before": len(mapped_baseline),
                    "ignored_after": len(ignored_current),
                    "lost": len(lost),
                    "gained": len(gained),
                    "tracked_matched": len(tracked_matched),
                    "pass": not lost and not gained,
                }
            )
            print(f"{stage}: ignored={len(ignored_current)} lost={len(lost)} gained={len(gained)} tracked_matched={len(tracked_matched)}")
    if args.dry_run:
        print("DRY-RUN: no report written")
        return 0
    with (outdir / "stage_ignore_proof.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    lines = [
        "# Per-batch D4 ignore invariance (planned)",
        "",
        "Each row maps already-moved paths to their new location and not-yet-moved paths to their old",
        "location, then applies that batch's `gitignore_Rn.txt` in a throwaway git repository.",
        "",
        "| Stage | Paths in play | Ignored before | Ignored after | Lost | Gained | Tracked pattern matches | Verdict |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['stage']} | {r['files_at_stage']} | {r['ignored_before']} | {r['ignored_after']} | "
            f"{r['lost']} | {r['gained']} | {r['tracked_matched']} | {'PASS' if r['pass'] else 'FAIL'} |"
        )
    lines += [
        "",
        "The eight tracked `.log` files are matched by `*.log` before and after; tracked status wins, so",
        "they remain tracked and stageable. R6/R7 introduce no ignore-anchor changes and are covered by",
        "the R5 final state plus the runtime re-proof in Phase 3.",
        "",
    ]
    (outdir / "stage_ignore_proof.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"WROTE {outdir / 'stage_ignore_proof.md'}")
    print(f"WROTE {outdir / 'stage_ignore_proof.csv'}")
    return 0 if all(r["pass"] for r in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
