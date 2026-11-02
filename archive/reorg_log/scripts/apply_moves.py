#!/usr/bin/env python
"""Execute one reorganization batch, resumably.

Every move is verified against the Phase-0 manifest and appended to moves.csv
immediately, so an interrupted run can resume without repeating a move.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

TICKS_EPOCH_OFFSET = 116444736000000000
FIELDS = [
    "seq", "batch", "old_path", "new_path", "sha256_before", "bytes",
    "mtime_utc_ticks", "tracked", "moved_utc", "recovered",
]


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


def read_moves(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def record_for(root: Path, row: dict[str, str], meta: dict[str, str],
               batch: str, seq: int, sha: str | None = None) -> dict[str, str]:
    new = root / row["new_path"]
    st = new.stat()
    digest = sha if sha is not None else sha256(new)
    return {
        "seq": str(seq),
        "batch": batch,
        "old_path": row["old_path"],
        "new_path": row["new_path"],
        "sha256_before": digest,
        "bytes": str(st.st_size),
        "mtime_utc_ticks": str(st.st_mtime_ns // 100 + TICKS_EPOCH_OFFSET),
        "tracked": row["tracked"],
        "moved_utc": datetime.now(timezone.utc).isoformat(),
        "recovered": "no",
    }


def verify_destination(root: Path, row: dict[str, str], meta: dict[str, str]) -> list[str]:
    errors: list[str] = []
    new = root / row["new_path"]
    if not new.is_file():
        return [f"missing destination {row['new_path']}"]
    if (root / row["old_path"]).exists():
        errors.append(f"source still exists {row['old_path']}")
    if new.stat().st_size != int(meta["size_bytes"]):
        errors.append(f"size mismatch {row['new_path']}")
    if sha256(new) != meta["sha256"]:
        errors.append(f"sha mismatch {row['new_path']}")
    expected_ns = iso_to_ns(meta["mtime_utc"])
    if abs(new.stat().st_mtime_ns - expected_ns) > 1000:
        errors.append(f"mtime mismatch {row['new_path']}")
    return errors


def do_move(root: Path, row: dict[str, str]) -> None:
    old = root / row["old_path"]
    new = root / row["new_path"]
    new.parent.mkdir(parents=True, exist_ok=True)
    if row["tracked"] == "yes":
        proc = subprocess.run(
            ["git", "-C", str(root), "-c", "core.quotepath=off",
             "mv", "--", row["old_path"], row["new_path"]],
            capture_output=True, text=True,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"git mv failed: {row['old_path']} -> {row['new_path']}: "
                               f"{proc.stdout}{proc.stderr}")
    else:
        last: Exception | None = None
        for _ in range(3):
            try:
                os.rename(old, new)
                last = None
                break
            except OSError as exc:
                last = exc
                time.sleep(0.5)
        if last is not None:
            raise RuntimeError(f"rename failed: {row['old_path']} -> {row['new_path']}: {last}")


def union_gitignore(root: Path, target: Path) -> None:
    current = (root / ".gitignore").read_text(encoding="utf-8")
    extra = target.read_text(encoding="utf-8")
    if extra not in current:
        (root / ".gitignore").write_text(
            current.rstrip("\n") + "\n\n# reorg batch safety union\n" + extra,
            encoding="utf-8",
        )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--logdir", required=True, type=Path)
    ap.add_argument("--batch", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    root = args.root.resolve()
    logdir = args.logdir.resolve()
    batch = args.batch

    plan = list(csv.DictReader((logdir / "move_plan.csv").open(encoding="utf-8-sig")))
    manifest = {
        r["path"]: r
        for r in csv.DictReader((logdir / "hash_manifest_before.csv").open(encoding="utf-8-sig"))
    }
    rows = [r for r in plan if batch_of(r) == batch]
    if not rows:
        print(f"no rows for {batch}", file=sys.stderr)
        return 2
    moves_path = logdir / "moves.csv"
    existing = read_moves(moves_path)
    logged = {m["old_path"]: m for m in existing}
    logged_new = {m["new_path"] for m in existing}
    seq = max((int(m["seq"]) for m in existing), default=0)

    if not args.dry_run and batch in {"R1", "R2", "R3", "R4", "R5"}:
        stage = logdir / f"gitignore_{batch}.txt"
        if not stage.is_file():
            print(f"missing ignore stage {stage}", file=sys.stderr)
            return 1
        union_gitignore(root, stage)

    counts = {"already": 0, "recovered": 0, "move": 0, "dry": 0}
    errors: list[str] = []
    bytes_total = 0
    for i, row in enumerate(rows, 1):
        old = root / row["old_path"]
        new = root / row["new_path"]
        meta = manifest.get(row["old_path"])
        if not meta:
            errors.append(f"no manifest row {row['old_path']}")
            break
        if row["old_path"] in logged or row["new_path"] in logged_new:
            if not new.is_file() or old.exists():
                errors.append(f"logged but state wrong {row['old_path']}")
                break
            counts["already"] += 1
            bytes_total += int(meta["size_bytes"])
            continue
        if new.is_file() and not old.exists():
            errs = verify_destination(root, row, meta)
            if errs:
                errors.extend(errs)
                break
            seq += 1
            rec = record_for(root, row, meta, batch, seq, sha=meta["sha256"])
            rec["recovered"] = "yes"
            existing.append(rec)
            logged[row["old_path"]] = rec
            logged_new.add(row["new_path"])
            counts["recovered"] += 1
            bytes_total += int(meta["size_bytes"])
            if not args.dry_run:
                _append(moves_path, rec)
            continue
        if old.is_file() and not new.exists():
            if args.dry_run:
                counts["dry"] += 1
                bytes_total += int(meta["size_bytes"])
                continue
            try:
                do_move(root, row)
            except Exception as exc:  # noqa: BLE001 - stop with a precise message
                errors.append(str(exc))
                break
            errs = verify_destination(root, row, meta)
            if errs:
                errors.extend(errs)
                break
            seq += 1
            rec = record_for(root, row, meta, batch, seq, sha=meta["sha256"])
            rec["moved_utc"] = datetime.now(timezone.utc).isoformat()
            existing.append(rec)
            logged[row["old_path"]] = rec
            logged_new.add(row["new_path"])
            counts["move"] += 1
            bytes_total += int(meta["size_bytes"])
            _append(moves_path, rec)
            if i % 100 == 0:
                print(f"progress {i}/{len(rows)} moved={counts['move']} "
                      f"recovered={counts['recovered']} bytes={bytes_total}")
            continue
        errors.append(f"unexpected state {row['old_path']} old={old.exists()} new={new.exists()}")
        break

    print(f"batch={batch} rows={len(rows)} already={counts['already']} "
          f"recovered={counts['recovered']} moved={counts['move']} "
          f"would_move={counts['dry']} bytes={bytes_total} errors={len(errors)}")
    for e in errors[:10]:
        print("ERROR", e)
    if errors:
        return 1
    if args.dry_run:
        print("DRY-RUN: no filesystem changes")
        return 0

    # Final ignore state for the batch; the union above kept both layouts safe
    # during the move, this restores the exact planned stage.
    if batch in {"R1", "R2", "R3", "R4", "R5"}:
        stage = logdir / f"gitignore_{batch}.txt"
        if not stage.is_file():
            print(f"missing ignore stage {stage}", file=sys.stderr)
            return 1
        shutil.copyfile(stage, root / ".gitignore")

    proc = subprocess.run(
        ["git", "-C", str(root), "-c", "core.quotepath=off", "add", "-A", "--",
         ".", ":(exclude)finalA_reorg_log"],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        print(f"git add failed: {proc.stdout}{proc.stderr}", file=sys.stderr)
        return 1
    print("STAGED: review with batch_verify.py before committing.")
    return 0


def _append(path: Path, rec: dict[str, str]) -> None:
    exists = path.is_file()
    with path.open("a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        if not exists:
            w.writeheader()
        w.writerow({k: rec.get(k, "") for k in FIELDS})
        fh.flush()
        os.fsync(fh.fileno())


if __name__ == "__main__":
    raise SystemExit(main())
