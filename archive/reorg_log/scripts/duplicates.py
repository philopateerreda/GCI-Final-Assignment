#!/usr/bin/env python
"""Group working-tree files by SHA256 and classify duplicate decisions.

Read-only. Re-runnable. Usage:
  python duplicates.py --root <finalA> --manifest <csv> --out <csv> \
    --summary <md> [--dry-run]
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import subprocess
from collections import defaultdict
from pathlib import Path

EVIDENCE_PREFIXES = (
    "v1_frozen/",
    "v4_addons/release_candidate/",
    "v4_addons/ledger_dryrun/",
    "v4_addons/snapshots/",
    "v3_addons/results/wp8/",
    "v3_addons/results/sources/",
    "v2_work/d_results/",
)
EVIDENCE_EXACT = {
    "analysis_outputs/claims_ledger.csv",
    "analysis_outputs/delivery_checks.json",
    "analysis_outputs/audit.json",
    "v2_work/final_metrics.json",
    "v2_work/final_batch_completion.json",
    "v2_work/a_summary.json",
    "v2_work/a_summary_calibration.json",
    "v2_work/a_summary_test.json",
    "v2_work/a_bootstrap_test.csv",
    "v2_work/c_subgroup_robustness.csv",
    "v2_work/literature_Ascarza2016.pdf",
}


def git_set(root: Path, *args: str) -> set[str]:
    out = subprocess.check_output(["git", "-C", str(root), *args], text=False)
    return {p.decode("utf-8", "surrogateescape") for p in out.split(b"\0") if p}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--manifest", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--summary", required=True, type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    root = args.root.resolve()
    tracked = git_set(root, "ls-files", "-z")
    rows = list(csv.DictReader(args.manifest.open(encoding="utf-8")))
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[row["sha256"]].append(row)
    duplicate_groups = {h: g for h, g in groups.items() if len(g) > 1}
    out_rows = []
    for h, group in sorted(duplicate_groups.items(), key=lambda kv: (-int(kv[1][0]["size_bytes"]), kv[0])):
        paths = [r["path"] for r in group]
        evidence = any(
            p.startswith(EVIDENCE_PREFIXES) or p in EVIDENCE_EXACT for p in paths
        )
        is_tracked = any(p in tracked for p in paths)
        for p in paths:
            residue = p.startswith(
                (
                    "v2_work/c_smoke/",
                    "v2_work/d_smoke/",
                    "v2_work/d_smoke_io/",
                    "v2_work/__pycache__/",
                    "v4_addons/m1_work/cache/",
                    "__pycache__/",
                )
            ) or p.endswith((".started", ".lock"))
            tracked_file = p in tracked
            if residue:
                recommendation = "move_with_residue"
                reason = "smoke/cache/started copy moves to archive/residue; not a separate duplicate action"
            elif evidence or tracked_file:
                recommendation = "keep_with_evidence_copy" if evidence else "keep_tracked"
                reason = (
                    "frozen snapshot / gate / receipt or manifest binds this copy"
                    if evidence
                    else "tracked duplicate cannot cross a new ignore anchor without breaking D4"
                )
            else:
                recommendation = "archive_duplicate"
                reason = "byte-identical duplicate not referenced by a frozen record"
            out_rows.append(
                {
                    "sha256": h,
                    "size_bytes": group[0]["size_bytes"],
                    "group_size": len(paths),
                    "path": p,
                    "evidence_bound": "yes" if evidence else "no",
                    "tracked": "yes" if tracked_file else "no",
                    "recommendation": recommendation,
                    "reason": reason,
                }
            )
    out_rows.sort(key=lambda r: (r["sha256"], r["path"]))
    archive = [r for r in out_rows if r["recommendation"] == "archive_duplicate"]
    residue = [r for r in out_rows if r["recommendation"] == "move_with_residue"]
    print(f"FILES={len(rows)} HASH_GROUPS={len(groups)} DUPLICATE_GROUPS={len(duplicate_groups)} DUPLICATE_FILES={len(out_rows)}")
    print(f"TRACKED_DUPLICATE_ROWS={sum(1 for r in out_rows if r['tracked']=='yes')} RESIDUE_COPY_ROWS={len(residue)} ARCHIVE_CANDIDATES={len(archive)}")
    if args.dry_run:
        print("DRY-RUN: no report written")
        return 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)
    lines = [
        "# Duplicate scan",
        "",
        f"- Working-tree files scanned: **{len(rows)}**",
        f"- Distinct SHA256: **{len(groups)}**",
        f"- SHA256 groups with >1 path: **{len(duplicate_groups)}**",
        f"- Files in duplicate groups: **{len(out_rows)}**",
        f"- Rows tracked by git: **{sum(1 for r in out_rows if r['tracked']=='yes')}**",
        f"- Rows that move with smoke/cache residue: **{len(residue)}**",
        f"- Separate archive candidates (untracked, unreferenced, not residue): **{len(archive)}**",
        "",
        "H7 rule: frozen/evidence-bound duplicates stay with their version and are flagged;",
        "tracked duplicates stay tracked; smoke/cache copies move only with their residue batch.",
        "No file is deleted.",
        "",
        "## Largest duplicate groups",
        "",
        "| SHA256 (first 12) | Bytes | Copies | Evidence-bound | Tracked copies | Paths |",
        "|---|---:|---:|---|---:|---|",
    ]
    for h, group in sorted(duplicate_groups.items(), key=lambda kv: (-int(kv[1][0]["size_bytes"]), kv[0]))[:25]:
        paths = [r["path"] for r in group]
        evidence = any(p.startswith(EVIDENCE_PREFIXES) or p in EVIDENCE_EXACT for p in paths)
        lines.append(
            f"| `{h[:12]}` | {int(group[0]['size_bytes']):,} | {len(paths)} | "
            f"{'yes' if evidence else 'no'} | {sum(1 for p in paths if p in tracked)} | "
            + "<br>".join(f"`{p}`" for p in paths[:6])
            + (" …" if len(paths) > 6 else "")
            + " |"
        )
    lines += [
        "",
        "## Decision",
        "",
        "The duplicate groups are frozen/evidence-bound copies, tracked duplicates, or smoke/cache",
        "copies that already move with residue. The proposal therefore sends **no file to a separate",
        "`archive/duplicates/` action**. Tracked copies stay tracked (D4); the frozen/receipt-bound copies",
        "stay with their version. Full per-file data: `duplicates.csv`.",
        "",
    ]
    args.summary.write_text("\n".join(lines), encoding="utf-8")
    print(f"WROTE {args.out}")
    print(f"WROTE {args.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
