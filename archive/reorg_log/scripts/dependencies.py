#!/usr/bin/env python
"""Static path-dependency scan for Python files and notebook code cells.

Read-only. Never imports project code. Usage:
  python dependencies.py --root <finalA> --manifest <csv> --out <csv> \
      --summary <md> [--dry-run]
"""
from __future__ import annotations

import argparse
import ast
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

PATH_HINTS = (
    "analysis_outputs",
    "telecom",
    "v1_frozen",
    "v2_work",
    "v3_addons",
    "v4_addons",
    "philopateer",
    "references.txt",
    "requirements-python311.txt",
    "README.docx",
    "tutorial",
    ".csv",
    ".json",
    ".npz",
    ".npy",
    ".joblib",
    ".png",
    ".pdf",
    ".pptx",
    ".ipynb",
    ".md",
    ".txt",
)

READ_CALLS = {
    "open",
    "read_csv",
    "read_json",
    "read_text",
    "read_bytes",
    "load",
    "loadtxt",
    "imread",
    "run_path",
}
WRITE_CALLS = {
    "write_text",
    "write_bytes",
    "to_csv",
    "to_json",
    "savefig",
    "savez",
    "savez_compressed",
    "dump",
    "copy",
    "copy2",
    "mkdir",
}
TOP_LEVEL = {
    "analysis_outputs",
    "telecom",
    "v1_frozen",
    "v2_work",
    "v3_addons",
    "v4_addons",
    "philopateer.ipynb",
    "philopateer.pdf",
    "philopateer.pptx",
    "README.md",
    "README.docx",
    "references.txt",
    "requirements-python311.txt",
    "tutorial (2).ipynb",
    "ENG_Company _A_ Dataset Overview.docx",
}


def tier_for(path: str) -> str:
    # All four delivery/pipeline entry points need path-mapping or cross-module
    # compatibility changes, so I-13 makes them Tier C historical snapshots.
    if path in {"analysis_pipeline.py", "build_notebook.py", "export_and_verify.py", "restore_v1.py"}:
        return "C"
    if path.startswith(("v2_work/", "v3_addons/", "v4_addons/")):
        return "C"
    return "C"


def anchor_for(expr: str) -> str:
    if re.match(r"^[A-Za-z]:[\\/]", expr) or expr.startswith("\\\\"):
        return "absolute"
    if "__file__" in expr:
        return "__file__-relative"
    if "Path.cwd" in expr or re.search(r"\bROOT\b|\bV2_ROOT\b|\bWORK\b|\bOUT\b|\bFROZEN\b", expr):
        return "cwd-relative"
    return "unknown"


def target_for(text: str) -> str:
    norm = text.replace("\\", "/").strip("'\"")
    parts = [p for p in norm.split("/") if p and p not in {".", ".."}]
    for p in parts:
        if p in TOP_LEVEL:
            return p
    for t in TOP_LEVEL:
        if t in norm:
            return t
    return ""


def literal_of(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def looks_path(value: str) -> bool:
    return any(h in value for h in PATH_HINTS)


def enclosing_call(node: ast.AST, parents: dict[ast.AST, ast.AST]) -> str:
    cur = node
    while cur in parents:
        cur = parents[cur]
        if isinstance(cur, ast.Call):
            fn = cur.func
            if isinstance(fn, ast.Name):
                return fn.id
            if isinstance(fn, ast.Attribute):
                return fn.attr
    return ""


def expression_of(node: ast.AST, src: str) -> str:
    try:
        return ast.unparse(node)
    except Exception:
        return ""


def scan_python(rel: str, text: str) -> list[dict[str, str]]:
    rows = []
    try:
        tree = ast.parse(text, filename=rel)
    except SyntaxError as exc:
        return [
            {
                "file": rel,
                "line": str(exc.lineno or 0),
                "kind": "parse_error",
                "expression": "",
                "anchor": "unknown",
                "target_top_level_item": "",
                "tier": tier_for(rel),
            }
        ]
    parents: dict[ast.AST, ast.AST] = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parents[child] = parent
    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
            continue
        value = node.value
        if not looks_path(value):
            continue
        call = enclosing_call(node, parents)
        kind = "read" if call in READ_CALLS else "write" if call in WRITE_CALLS else "path"
        if call in {"chdir"}:
            kind = "chdir"
        if call in {"insert", "append"} and "sys.path" in expression_of(parents.get(node, node), text):
            kind = "sys.path"
        expr = call or expression_of(parents.get(node, node), text)
        rows.append(
            {
                "file": rel,
                "line": str(node.lineno),
                "kind": kind,
                "expression": expr[:220],
                "anchor": anchor_for(expr),
                "target_top_level_item": target_for(value),
                "tier": tier_for(rel),
            }
        )
    return rows


def scan_notebook(rel: str, text: str) -> list[dict[str, str]]:
    rows = []
    nb = json.loads(text)
    for ci, cell in enumerate(nb.get("cells", []), 1):
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        lines = source.splitlines()
        for li, line in enumerate(lines, 1):
            stripped = line.lstrip()
            if stripped.startswith(("%", "!")):
                kind = "chdir" if stripped.startswith("%cd") else "shell" if stripped.startswith("!") else "magic"
                value = stripped
                rows.append(
                    {
                        "file": rel,
                        "line": f"cell{ci}:{li}",
                        "kind": kind,
                        "expression": value[:220],
                        "anchor": "cwd-relative" if stripped.startswith("%cd") else "unknown",
                        "target_top_level_item": target_for(value),
                        "tier": "C",
                    }
                )
        sanitized = []
        for line in lines:
            if line.lstrip().startswith(("%", "!")):
                sanitized.append("pass")
            else:
                sanitized.append(line)
        try:
            tree = ast.parse("\n".join(sanitized))
        except SyntaxError:
            continue
        parents = {}
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                parents[child] = parent
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and looks_path(node.value):
                rows.append(
                    {
                        "file": rel,
                        "line": f"cell{ci}:{node.lineno}",
                        "kind": "path",
                        "expression": expression_of(node, text)[:220],
                        "anchor": anchor_for(expression_of(node, text)),
                        "target_top_level_item": target_for(node.value),
                        "tier": "C",
                    }
                )
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--manifest", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--summary", required=True, type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    root = args.root.resolve()
    manifest = {r["path"]: r for r in csv.DictReader(args.manifest.open(encoding="utf-8"))}
    rows: list[dict[str, str]] = []
    py_count = nb_count = 0
    parse_errors = []
    for rel in sorted(manifest):
        p = root / rel
        if rel.endswith(".py"):
            py_count += 1
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            got = scan_python(rel, text)
            if any(r["kind"] == "parse_error" for r in got):
                parse_errors.append(rel)
            rows.extend(got)
        elif rel.endswith(".ipynb"):
            nb_count += 1
            try:
                got = scan_notebook(rel, p.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                parse_errors.append(f"{rel}: {type(exc).__name__}")
                continue
            rows.extend(got)
    key = lambda r: (r["file"], r["line"], r["kind"], r["expression"])
    rows.sort(key=key)
    tier_counts = Counter(r["tier"] for r in rows)
    target_counts = Counter(r["target_top_level_item"] or "(none)" for r in rows)
    reverse = defaultdict(lambda: {"read": 0, "write": 0, "chdir": 0, "sys.path": 0, "shell": 0, "path": 0, "magic": 0})
    for r in rows:
        reverse[r["target_top_level_item"] or "(none)"][r["kind"]] += 1
    print(f"PY_FILES={py_count} NOTEBOOKS={nb_count} ROWS={len(rows)} PARSE_ERRORS={len(parse_errors)}")
    print(f"TIERS={dict(tier_counts)}")
    print(f"TARGETS={dict(target_counts.most_common(12))}")
    if args.dry_run:
        print("DRY-RUN: no report written")
        return 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(
            fh,
            fieldnames=["file", "line", "kind", "expression", "anchor", "target_top_level_item", "tier"],
        )
        w.writeheader()
        w.writerows(rows)
    lines = [
        "# Dependency scan",
        "",
        f"- Python files parsed: **{py_count}**",
        f"- Notebooks parsed: **{nb_count}**",
        f"- Path/dependency rows: **{len(rows)}**",
        f"- Parse errors: **{len(parse_errors)}**" + (f" ({', '.join(parse_errors[:5])})" if parse_errors else ""),
        f"- Rows by tier: **A={tier_counts.get('A',0)}, B={tier_counts.get('B',0)}, C={tier_counts.get('C',0)}**",
        "",
        "## Reverse view — reader/writer counts by top-level target",
        "",
        "| Target | read | write | chdir | sys.path | shell | other |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for target, counts in sorted(reverse.items(), key=lambda kv: -sum(kv[1].values())):
        other = counts["path"] + counts["magic"]
        lines.append(
            f"| `{target}` | {counts['read']} | {counts['write']} | {counts['chdir']} | "
            f"{counts['sys.path']} | {counts['shell']} | {other} |"
        )
    lines += [
        "",
        "## Static findings",
        "",
        "- The scan is syntactic only: no project module is imported and no notebook is executed (I-5).",
        "- **No code edits are proposed.** All four root entry points are Tier C under I-13: `analysis_pipeline.py` has 28 path-related lines, `restore_v1.py` needs a manifest-to-new-tree mapping, and `build_notebook.py` / `export_and_verify.py` delegate to those old-root helpers.",
        "- Every path string in historical v2/v3/v4 code and notebooks is Tier C and will be documented as stale-by-design, not edited.",
        "- Full per-row data, including notebook cell/line references: `dependencies.csv`.",
        "",
    ]
    args.summary.write_text("\n".join(lines), encoding="utf-8")
    print(f"WROTE {args.out}")
    print(f"WROTE {args.summary}")
    return 0 if not parse_errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
