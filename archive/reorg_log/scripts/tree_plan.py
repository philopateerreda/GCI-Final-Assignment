#!/usr/bin/env python
"""Summarize the planned tree from move_plan.csv.

Read-only. Re-runnable. Usage:
  python tree_plan.py --plan <csv> --outdir <dir> [--dry-run]
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True, type=Path)
    ap.add_argument("--outdir", required=True, type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    rows = list(csv.DictReader(args.plan.open(encoding="utf-8")))
    top = defaultdict(lambda: {"files": 0, "bytes": 0})
    children = defaultdict(lambda: {"files": 0, "bytes": 0})
    for r in rows:
        parts = r["new_path"].split("/")
        t = parts[0] if len(parts) > 1 else "(root file)"
        b = int(next(x for x in [])) if False else None
    # Need bytes from the plan? move_plan has no bytes; join inventory.
    inv = {}
    inv_path = args.plan.with_name("inventory.csv")
    for r in csv.DictReader(inv_path.open(encoding="utf-8")):
        inv[r["path"]] = int(r["bytes"])
    for r in rows:
        b = inv[r["old_path"]]
        parts = r["new_path"].split("/")
        t = parts[0] if len(parts) > 1 else "(root file)"
        top[t]["files"] += 1
        top[t]["bytes"] += b
        if len(parts) > 2:
            child = f"{parts[0]}/{parts[1]}"
        elif len(parts) == 2:
            child = f"{parts[0]}/(files)"
        else:
            child = "(root files)"
        children[child]["files"] += 1
        children[child]["bytes"] += b
    print(f"TOP_LEVEL={len(top)} FILES={len(rows)} BYTES={sum(v['bytes'] for v in top.values()):,}")
    for k, v in sorted(top.items(), key=lambda kv: -kv[1]["bytes"]):
        print(f"{k}: {v['files']} files / {v['bytes']:,} bytes")
    if args.dry_run:
        print("DRY-RUN: no report written")
        return 0
    args.outdir.mkdir(parents=True, exist_ok=True)
    with (args.outdir / "final_tree.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["prefix", "files", "bytes"])
        for k, v in sorted(children.items()):
            w.writerow([k, v["files"], v["bytes"]])
    lines = [
        "# Planned final tree",
        "",
        f"Built from `move_plan.csv` + `inventory.csv`: **{len(rows)}** original files / "
        f"**{sum(v['bytes'] for v in top.values()):,} bytes**. New READMEs/log files are additional.",
        "",
        "## Top level",
        "",
        "| Destination | Files | Bytes | MiB |",
        "|---|---:|---:|---:|",
    ]
    for k, v in sorted(top.items(), key=lambda kv: (-kv[1]["bytes"], kv[0])):
        lines.append(f"| `{k}/` | {v['files']} | {v['bytes']:,} | {v['bytes']/1024/1024:.2f} |")
    lines += [
        "",
        "## Two-level view",
        "",
        "| Destination prefix | Files | Bytes |",
        "|---|---:|---:|",
    ]
    for k, v in sorted(children.items(), key=lambda kv: (kv[0])):
        if v["files"] >= 1:
            lines.append(f"| `{k}` | {v['files']} | {v['bytes']:,} |")
    lines += [
        "",
        "## Shape",
        "",
        "```text",
        "finalA/",
        "├── README.md",
        "├── .gitignore, .gitattributes",
        "├── submission/       3 graded artifacts + README",
        "├── pipeline/         4 historical scripts + references + requirements + README",
        "├── data/telecom/     2 supplied CSVs (ignored)",
        "├── evidence/         receipts, charts, tables, model, renders, backups",
        "├── versions/         v1_frozen, v2_work, v3_addons, v4_addons + VERSIONS.md",
        "├── docs/             3 FINAL_* notes + reference/ (2 docx + tutorial) + README",
        "└── archive/          residue/, duplicates/, superseded/, unclear_status/, reorg_log/",
        "```",
        "",
        "The empty `.qoder-office-pptx-locks/` contains no file and is removed only after the move; no byte is deleted.",
        "",
    ]
    (args.outdir / "final_tree.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"WROTE {args.outdir / 'final_tree.md'}")
    print(f"WROTE {args.outdir / 'final_tree.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
