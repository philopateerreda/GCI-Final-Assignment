#!/usr/bin/env python
"""Phase 4 verification (V1-V10). Read-only; writes phase4_verify.json/.md.

Run before R8 (docs absent) and again after R8 (docs present). Each check
reports PASS / FAIL / PENDING plus the evidence used.
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT_DOCS_FOLDERS = {"submission", "pipeline", "data", "evidence", "versions", "docs", "archive"}
ROOT_FILES = {"README.md", ".gitignore", ".gitattributes"}
FORBIDDEN_TOP = {
    "analysis_outputs", "telecom", "v1_frozen", "v2_work", "v3_addons", "v4_addons",
    "philopateer.ipynb", "philopateer.pdf", "philopateer.pptx",
    "README.docx", "ENG_Company _A_ Dataset Overview.docx",
    "references.txt", "analysis_pipeline.py", "build_notebook.py",
    "export_and_verify.py", "restore_v1.py",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def walk_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for name in filenames:
            yield Path(dirpath) / name


def walk_dirs(root: Path):
    for dirpath, dirnames, _ in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for name in dirnames:
            yield Path(dirpath) / name


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace")


def git(*args: str) -> str:
    return run("git", "-c", "core.quotepath=off", *args).stdout


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


ROOT = next(p for p in Path(__file__).resolve().parents if (p / ".git").exists())
LOG = next(
    p
    for p in (ROOT / "archive" / "reorg_log", ROOT / "finalA_reorg_log")
    if (p / "moves.csv").is_file()
)


def check_v1() -> dict:
    entries = sorted(p.name for p in ROOT.iterdir())
    expected = sorted(ROOT_DOCS_FOLDERS | ROOT_FILES | {".git", "finalA_reorg_log"})
    missing = [e for e in sorted(ROOT_FILES | ROOT_DOCS_FOLDERS | {".git"}) if e not in entries]
    extra = [e for e in entries if e not in expected]
    pending = "README.md" in missing
    status = "PENDING" if pending and not extra else ("PASS" if not missing and not extra else "FAIL")
    return {
        "id": "V1",
        "status": status,
        "detail": f"root={entries}; missing={missing}; extra={extra}; finalA_reorg_log exempt until R8",
        "evidence": "directory listing",
    }


def check_v2() -> dict:
    plan = read_csv(LOG / "move_plan.csv")
    inventory = {r["path"]: r for r in read_csv(LOG / "inventory.csv")}
    moves = {r["old_path"]: r for r in read_csv(LOG / "moves.csv")}
    errors: list[str] = []
    unchanged = edited = 0
    reconciled_bytes = 0
    for row in plan:
        old = row["old_path"]
        base = inventory.get(old)
        if base is None:
            errors.append(f"not in inventory: {old}")
            continue
        new = moves[old]["new_path"] if old in moves else old
        p = ROOT / new
        if not p.is_file():
            errors.append(f"missing {new}")
            continue
        # The only approved content edit is .gitignore (ignore-path rewrite).
        if new == ".gitignore" and old not in moves:
            edited += 1
            reconciled_bytes += p.stat().st_size
            continue
        if p.stat().st_size != int(base["bytes"]):
            errors.append(f"size {new}")
            continue
        digest = sha256(p)
        if digest != base["sha256"]:
            errors.append(f"sha {new}")
            continue
        if old not in moves:
            unchanged += 1
        reconciled_bytes += int(base["bytes"])
    baseline = read_csv(LOG / "hash_manifest_before.csv")
    baseline_bytes = sum(int(r["size_bytes"]) for r in baseline)
    plan_bytes = sum(int(inventory[r["old_path"]]["bytes"]) for r in plan if r["old_path"] in inventory)
    return {
        "id": "V2",
        "status": "PASS" if not errors and len(plan) == len(baseline) == len(inventory) else "FAIL",
        "detail": (
            f"plan_rows={len(plan)} baseline_rows={len(baseline)} inventory_rows={len(inventory)} "
            f"unchanged={unchanged} moved={len(plan)-unchanged} edited_on_purpose={edited} errors={len(errors)}; "
            f"baseline_bytes={baseline_bytes} plan_bytes={plan_bytes} reconciled_bytes={reconciled_bytes}"
        ),
        "errors": errors[:20],
        "evidence": "move_plan.csv + moves.csv + inventory.csv + hash_manifest_before.csv",
    }


def check_v3() -> dict:
    frozen = read_csv(LOG / "frozen_before.csv")
    moves = {r["old_path"]: r["new_path"] for r in read_csv(LOG / "moves.csv")}
    errors = []
    checked = 0
    for row in frozen:
        old = row["path"]
        new = moves.get(old, old)
        p = ROOT / new
        if not p.is_file():
            errors.append(f"missing {new}")
            continue
        if sha256(p) != row["sha256"]:
            errors.append(f"sha {new}")
            continue
        checked += 1
    return {
        "id": "V3",
        "status": "PASS" if not errors else "FAIL",
        "detail": f"frozen_rows={len(frozen)} byte_identical={checked} errors={len(errors)} F1/F2/F3",
        "errors": errors[:20],
        "evidence": "frozen_before.csv",
    }


def check_v4() -> dict:
    status = git("status", "--porcelain")
    status_lines = [l for l in status.splitlines() if l.strip()]
    problems = [l for l in status_lines if "finalA_reorg_log" not in l]
    probes = [
        "data/telecom/Client.csv",
        "data/telecom/Record.csv",
        "docs/reference/README.docx",
        "docs/reference/ENG_Company _A_ Dataset Overview.docx",
        "versions/v1_frozen/sha256_manifest.json",
        "evidence/notebook_backups/philopateer-20261028-121046.ipynb",
        "archive/residue/__pycache__",
    ]
    probes = [p for p in probes if (ROOT / p).exists()]
    not_ignored = [p for p in probes if run("git", "check-ignore", "-q", p).returncode != 0]
    tracked_ignored = set(git("ls-files", "-ci", "--exclude-standard").splitlines())
    # Compare with pre-reorg: tracked files that also match an ignore pattern.
    pre_logs = set(git("ls-tree", "-r", "--name-only", "pre-reorg").splitlines())
    pre_ignored = {
        p for p in pre_logs
        if run("git", "check-ignore", "-q", "--no-index", p).returncode == 0
    }
    moves = {r["old_path"]: r["new_path"] for r in read_csv(LOG / "moves.csv")}
    pre_mapped = {moves.get(p, p) for p in pre_ignored}
    new_tracked_ignored = sorted(tracked_ignored - pre_mapped)
    lost_tracked_ignored = sorted(pre_mapped - tracked_ignored)
    found_ignored = [
        p.relative_to(ROOT).as_posix()
        for p in walk_files(ROOT)
        if "cv_manifest" in p.name and run("git", "check-ignore", "-q", p.relative_to(ROOT).as_posix()).returncode == 0
    ]
    pass_ = not problems and not not_ignored and not new_tracked_ignored and not lost_tracked_ignored
    return {
        "id": "V4",
        "status": "PASS" if pass_ else "FAIL",
        "detail": (
            f"status_lines={len(status_lines)} (log-only) probes={len(probes)} "
            f"not_ignored={not_ignored} tracked_but_ignored_before={len(pre_mapped)} "
            f"after={len(tracked_ignored)} new={new_tracked_ignored} lost={lost_tracked_ignored} "
            f"cv_manifest_ignored={len(found_ignored)}"
        ),
        "errors": problems[:20],
        "evidence": "git status --porcelain --ignored; git check-ignore; git ls-files -ci; pre-reorg comparison",
    }


def check_v5() -> dict:
    diff = git("diff", "-M", "--name-status", "pre-reorg..HEAD").splitlines()
    renames, adds, deletes, modifies, other = [], [], [], [], []
    for line in diff:
        if not line.strip():
            continue
        parts = line.split("\t")
        code = parts[0]
        if code.startswith("R100"):
            renames.append((parts[1], parts[2]))
        elif code == "A":
            adds.append(parts[1])
        elif code == "D":
            deletes.append(parts[1])
        elif code == "M":
            modifies.append(parts[1])
        else:
            other.append(line)
    bad_mods = [m for m in modifies if m != ".gitignore"]

    def allowed_add(p: str) -> bool:
        if p == "README.md" or p.endswith("/README.md") or p.endswith("VERSIONS.md"):
            return True
        if p.startswith("archive/reorg_log/"):
            return True
        return False

    bad_adds = [a for a in adds if not allowed_add(a)]
    pending_docs = "README.md" not in adds and not (ROOT / "README.md").exists()
    status = "FAIL" if bad_mods or bad_adds or deletes or other else ("PENDING" if pending_docs else "PASS")
    return {
        "id": "V5",
        "status": status,
        "detail": (
            f"renames_R100={len(renames)} additions={len(adds)} modifications={modifies} "
            f"deletions={len(deletes)} other={len(other)}; bad_mods={bad_mods} bad_adds={bad_adds[:10]}"
        ),
        "evidence": "git diff -M --name-status pre-reorg..HEAD",
    }


def check_v6() -> dict:
    py_files = sorted(walk_files(ROOT))
    py_files = [p for p in py_files if p.suffix == ".py"]
    compile_errors = []
    for p in py_files:
        try:
            ast.parse(p.read_text(encoding="utf-8", errors="replace"), filename=str(p))
        except SyntaxError as exc:
            compile_errors.append(f"{p.relative_to(ROOT).as_posix()}: {exc.msg} line {exc.lineno}")
    notebooks = sorted(p for p in walk_files(ROOT) if p.suffix == ".ipynb")
    nb_errors = []
    code_cells = 0
    for p in notebooks:
        try:
            nb = json.loads(p.read_text(encoding="utf-8"))
            code_cells += sum(1 for c in nb.get("cells", []) if c.get("cell_type") == "code")
        except Exception as exc:  # noqa: BLE001
            nb_errors.append(f"{p.relative_to(ROOT).as_posix()}: {exc}")
    return {
        "id": "V6",
        "status": "PASS" if not compile_errors and len(notebooks) == 15 and not nb_errors else "FAIL",
        "detail": (
            f"py_parsed={len(py_files)} parse_errors={len(compile_errors)} "
            f"notebooks={len(notebooks)} code_cells={code_cells} notebook_errors={len(nb_errors)} "
            "nothing imported or executed"
        ),
        "errors": (compile_errors + nb_errors)[:20],
        "evidence": "ast.parse in memory; json.loads on every .ipynb",
    }


def check_v7() -> dict:
    tracked = git("ls-files").splitlines()
    pre_tracked = set(git("ls-tree", "-r", "--name-only", "pre-reorg").splitlines())
    moves = {r["new_path"]: r["old_path"] for r in read_csv(LOG / "moves.csv")}
    big, pre_big = [], []
    for rel in tracked:
        p = ROOT / rel
        if p.is_file() and p.stat().st_size > 25 * 1024 * 1024:
            was = moves.get(rel, rel) in pre_tracked
            (pre_big if was else big).append(f"{rel}={p.stat().st_size}")
    frozen = read_csv(LOG / "frozen_before.csv")
    dataset_hashes = {r["sha256"] for r in frozen if r["id"] == "F3"}
    f1_by_hash = {r["sha256"]: r["path"] for r in frozen if r["id"] == "F1"}
    f1_expected = {
        "submission/philopateer.ipynb",
        "submission/philopateer.pdf",
        "submission/philopateer.pptx",
        "docs/reference/README.docx",
        "docs/reference/ENG_Company _A_ Dataset Overview.docx",
    }
    collisions, pre_collisions = [], []
    for rel in tracked:
        p = ROOT / rel
        if not p.is_file():
            continue
        digest = sha256(p)
        if digest in dataset_hashes:
            tag = f"dataset:{rel}"
        elif digest in f1_by_hash and rel not in f1_expected:
            tag = f"f1:{rel}=={f1_by_hash[digest]}"
        else:
            continue
        old = moves.get(rel, rel)
        (pre_collisions if old in pre_tracked else collisions).append(tag)
    return {
        "id": "V7",
        "status": "PASS" if not big and not collisions else "FAIL",
        "detail": (
            f"tracked={len(tracked)} new_over_25MB={big} pre_existing_over_25MB={pre_big} "
            f"new_frozen_or_dataset_duplicates={collisions[:10]} "
            f"pre_existing_duplicates={pre_collisions[:10]} (F1 originals excluded)"
        ),
        "evidence": "git ls-files + SHA256; pre-reorg tracked set",
    }


def check_v8() -> dict:
    def changes(pattern: str, filt: str) -> list[str]:
        return [
            p
            for p in git("diff", "-M", "--name-status", f"--diff-filter={filt}", "pre-reorg..HEAD", "--", pattern).splitlines()
            if p
        ]

    def reorg_tooling(line: str) -> bool:
        parts = line.split("\t")
        return len(parts) > 1 and parts[-1].startswith("archive/reorg_log/")

    py_mods = changes("*.py", "M")
    ps_mods = changes("*.ps1", "M")
    nb_mods = changes("*.ipynb", "M")
    py_adds = [p for p in changes("*.py", "A") if not reorg_tooling(p)]
    ps_adds = [p for p in changes("*.ps1", "A") if not reorg_tooling(p)]
    nb_adds = [p for p in changes("*.ipynb", "A") if not reorg_tooling(p)]
    code_dels = changes("*.py", "D") + changes("*.ps1", "D") + changes("*.ipynb", "D")
    return {
        "id": "V8",
        "status": "PASS" if not (py_mods or ps_mods or nb_mods or py_adds or ps_adds or nb_adds or code_dels) else "FAIL",
        "detail": (
            "G1-approved code edits: 0 (all project scripts Tier C, byte-identical); "
            f"py_modified={len(py_mods)} ps1_modified={len(ps_mods)} ipynb_modified={len(nb_mods)} "
            f"py_added_outside_log={len(py_adds)} ps1_added_outside_log={len(ps_adds)} "
            f"ipynb_added_outside_log={len(nb_adds)} code_deleted={len(code_dels)} "
            "(new reorg tooling under archive/reorg_log is documentation, not project code)"
        ),
        "evidence": "git diff -M --diff-filter=M/A/D pre-reorg..HEAD by extension",
    }


def check_v9() -> dict:
    fsck = run("git", "fsck", "--no-dangling")
    undo = run(
        "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
        "-File", str(LOG / "scripts" / "undo_moves.ps1"), "-WhatIf",
    )
    tail = "\n".join((undo.stdout or "").strip().splitlines()[-3:])
    return {
        "id": "V9",
        "status": "PASS" if fsck.returncode == 0 and undo.returncode == 0 else "FAIL",
        "detail": (
            f"fsck_rc={fsck.returncode} fsck_errors={len(fsck.stderr.strip().splitlines())} "
            f"undo_whatif_rc={undo.returncode} undo_tail={tail!r}"
        ),
        "evidence": "git fsck --no-dangling; undo_moves.ps1 -WhatIf",
    }


def check_v10() -> dict:
    present = [p for p in sorted(FORBIDDEN_TOP) if (ROOT / p).exists()]
    empty = []
    for p in walk_dirs(ROOT):
        try:
            next(p.iterdir())
        except StopIteration:
            empty.append(p.relative_to(ROOT).as_posix())
    return {
        "id": "V10",
        "status": "PASS" if not present and not empty else "FAIL",
        "detail": f"old_paths_present={present} empty_dirs={empty[:10]}",
        "evidence": "directory listing after prune_empty_dirs.py",
    }


CHECKS = [check_v1, check_v2, check_v3, check_v4, check_v5, check_v6, check_v7, check_v8, check_v9, check_v10]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=LOG / "phase4_verify")
    args = ap.parse_args()
    results = [fn() for fn in CHECKS]
    import datetime

    payload = {
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "head": git("rev-parse", "HEAD").strip(),
        "counts": {s: sum(1 for r in results if r["status"] == s) for s in ("PASS", "FAIL", "PENDING")},
        "checks": results,
    }
    args.out.with_suffix(".json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Phase 4 verification",
        "",
        f"HEAD `{payload['head']}`; generated {payload['generated_utc']}",
        "",
        "| # | Result | Evidence |",
        "|---|---|---|",
    ]
    for r in results:
        lines.append(f"| {r['id']} | **{r['status']}** | {r['detail']} |")
    lines.append("")
    for r in results:
        if r.get("errors"):
            lines.append(f"## {r['id']} errors")
            lines += [f"- {e}" for e in r["errors"]]
            lines.append("")
    args.out.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(payload["counts"], indent=2))
    for r in results:
        print(f"{r['id']}: {r['status']} — {r['detail']}")
    return 0 if payload["counts"]["FAIL"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
