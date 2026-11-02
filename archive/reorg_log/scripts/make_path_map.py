#!/usr/bin/env python
"""Build archive/reorg_log/path_map.csv from the reorg receipts (read-only)."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / ".git").exists())
LOG = next(
    p
    for p in (ROOT / "archive" / "reorg_log", ROOT / "finalA_reorg_log")
    if (p / "moves.csv").is_file()
)


def read(name: str) -> list[dict]:
    with (LOG / name).open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


plan = read("move_plan.csv")
moves = {r["old_path"]: r["new_path"] for r in read("moves.csv")}
inventory = {r["path"]: r for r in read("inventory.csv")}
groups = {r["path"]: r["group_id"] for r in read("role_map.csv")}

rows = []
for row in plan:
    old = row["old_path"]
    new = moves.get(old, old)
    if old in moves:
        change = "moved"
    elif old == ".gitignore":
        change = "edited"
    else:
        change = "unchanged"
    inv = inventory.get(old, {})
    rows.append(
        {
            "old_path": old,
            "new_path": new,
            "change": change,
            "category": row["category"],
            "tier": row.get("tier", ""),
            "tracked": inv.get("tracked", ""),
            "group_id": groups.get(old, ""),
            "bytes": inv.get("bytes", ""),
            "sha256": inv.get("sha256", ""),
        }
    )

rows.sort(key=lambda r: r["old_path"])
out = LOG / "path_map.csv"
with out.open("w", newline="", encoding="utf-8") as fh:
    writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
print(f"WROTE {out} ({len(rows)} rows)")
