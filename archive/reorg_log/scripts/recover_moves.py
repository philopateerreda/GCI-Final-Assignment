#!/usr/bin/env python
"""Rebuild moves.csv for a batch that was interrupted after filesystem moves.

Read-only unless --write is given. Verifies every destination against the
Phase-0 manifest (size, SHA256, mtime) before recording it.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path

TICKS_EPOCH_OFFSET = 116444736000000000


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


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


def iso_to_ns(value: str) -> int:
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    delta = dt - datetime(1970, 1, 1, tzinfo=timezone.utc)
    return (delta.days * 86400 + delta.seconds) * 10**9 + delta.microseconds * 1000


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--logdir", required=True, type=Path)
    ap.add_argument("--batch", required=True)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    root = args.root.resolve()
    logdir = args.logdir.resolve()

    plan = list(csv.DictReader((logdir / "move_plan.csv").open(encoding="utf-8-sig")))
    manifest = {
        r["path"]: r
        for r in csv.DictReader((logdir / "hash_manifest_before.csv").open(encoding="utf-8-sig"))
    }
    rows = [r for r in plan if batch_of(r) == args.batch]
    errors: list[str] = []
    records: list[dict[str, str]] = []
    recovered_at = datetime.now(timezone.utc).isoformat()

    for seq, r in enumerate(rows, 1):
        old = root / r["old_path"]
        new = root / r["new_path"]
        old_exists = old.is_file()
        new_exists = new.is_file()
        if old_exists and not new_exists:
            errors.append(f"NOT MOVED: {r['old_path']}")
            continue
        if old_exists and new_exists:
            errors.append(f"BOTH EXIST: {r['old_path']} | {r['new_path']}")
            continue
        if not old_exists and not new_exists:
            errors.append(f"NEITHER EXISTS: {r['old_path']} | {r['new_path']}")
            continue

        m = manifest.get(r["old_path"])
        if not m:
            errors.append(f"NO MANIFEST ROW: {r['old_path']}")
            continue
        size = new.stat().st_size
        if size != int(m["size_bytes"]):
            errors.append(f"SIZE MISMATCH: {r['new_path']}")
            continue
        if sha256(new) != m["sha256"]:
            errors.append(f"SHA MISMATCH: {r['new_path']}")
            continue
        expected_ns = iso_to_ns(m["mtime_utc"])
        actual_ns = new.stat().st_mtime_ns
        # Windows stores 100 ns ticks; the ISO manifest keeps microseconds.
        if abs(actual_ns - expected_ns) > 1000:
            errors.append(
                f"MTIME MISMATCH: {r['new_path']} expected {expected_ns} got {actual_ns}"
            )
            continue
        records.append(
            {
                "seq": str(seq),
                "batch": args.batch,
                "old_path": r["old_path"],
                "new_path": r["new_path"],
                "sha256_before": m["sha256"],
                "bytes": str(size),
                "mtime_utc_ticks": str(actual_ns // 100 + TICKS_EPOCH_OFFSET),
                "tracked": r["tracked"],
                "moved_utc": recovered_at,
                "recovered": "yes",
            }
        )

    total_bytes = sum(int(x["bytes"]) for x in records)
    print(f"batch={args.batch} plan_rows={len(rows)} recovered={len(records)} "
          f"bytes={total_bytes} errors={len(errors)}")
    for e in errors[:20]:
        print("ERROR", e)

    if args.write and records:
        moves_path = logdir / "moves.csv"
        if moves_path.exists():
            existing = list(csv.DictReader(moves_path.open(encoding="utf-8")))
            existing_old = {x["old_path"] for x in existing}
            records = [x for x in records if x["old_path"] not in existing_old]
        else:
            existing = []
        fields = [
            "seq", "batch", "old_path", "new_path", "sha256_before", "bytes",
            "mtime_utc_ticks", "tracked", "moved_utc", "recovered",
        ]
        mode = "a" if existing else "w"
        with moves_path.open(mode, newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            if not existing:
                w.writeheader()
            for rec in records:
                rec = {k: rec.get(k, "") for k in fields}
                w.writerow(rec)
        print(f"WROTE {moves_path} rows={len(existing) + len(records)}")
    elif args.write:
        print("NO RECORDS WRITTEN")

    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
