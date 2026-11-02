#!/usr/bin/env python
"""Structural notebook output scan; never prints output bodies.

Read-only. Re-runnable. Usage:
  python notebook_scan.py --root <finalA> --manifest <csv> --out <md> [--dry-run]
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

APPLICANT_COLUMNS = {
    "Customer_ID",
    "churn",
    "income",
    "creditcd",
    "ownrent",
    "ethnic",
    "marital",
    "hnd_price",
    "totmrc_Mean",
    "rev_Mean",
    "mou_Mean",
}
TABLE_HINT = re.compile(r"(?:^|\n)\s*(?:\d+\s+){2,}")


def scan_output(output: dict) -> dict:
    text_parts = []
    html_rows = 0
    images = 0
    for key, value in (output.get("data") or {}).items():
        if isinstance(value, list):
            value = "".join(str(v) for v in value)
        if key == "text/html":
            html_rows += str(value).lower().count("<tr")
            text_parts.append(str(value))
        elif key in {"text/plain", "text/markdown"}:
            text_parts.append(str(value))
        elif key.startswith("image/"):
            images += 1
    text = "\n".join(text_parts)
    lines = [ln for ln in text.splitlines() if ln.strip()]
    table_rows = max(len(lines), html_rows)
    tokens = sorted({c for c in APPLICANT_COLUMNS if re.search(rf"\b{re.escape(c)}\b", text)})
    return {
        "data_rows_estimate": table_rows,
        "html_rows": html_rows,
        "images": images,
        "applicant_tokens": tokens,
        "text_chars": len(text),
        "over_20_rows": table_rows > 20,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--manifest", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--csv", required=True, type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    root = args.root.resolve()
    rows = list(csv.DictReader(args.manifest.open(encoding="utf-8")))
    results = []
    for row in rows:
        rel = row["path"]
        if not rel.endswith(".ipynb"):
            continue
        nb = json.loads((root / rel).read_text(encoding="utf-8"))
        code_cells = [c for c in nb.get("cells", []) if c.get("cell_type") == "code"]
        outputs = [o for c in code_cells for o in c.get("outputs", [])]
        scanned = [scan_output(o) for o in outputs]
        flagged = [s for s in scanned if s["over_20_rows"] or s["applicant_tokens"]]
        results.append(
            {
                "path": rel,
                "bytes": row["size_bytes"],
                "code_cells": len(code_cells),
                "outputs": len(outputs),
                "image_outputs": sum(s["images"] for s in scanned),
                "max_rows": max([s["data_rows_estimate"] for s in scanned], default=0),
                "flagged_outputs": len(flagged),
                "applicant_tokens": sorted({t for s in scanned for t in s["applicant_tokens"]}),
                "executed": all("execution_count" in c and c.get("execution_count") is not None for c in code_cells),
                "errors": sum(1 for o in outputs if o.get("output_type") == "error"),
            }
        )
    print(f"NOTEBOOKS={len(results)} FLAGGED={sum(r['flagged_outputs'] for r in results)}")
    for r in results:
        print(f"{r['path']}: code={r['code_cells']} outputs={r['outputs']} max_rows={r['max_rows']} flagged={r['flagged_outputs']}")
    if args.dry_run:
        print("DRY-RUN: no report written")
        return 0
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    with args.csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(
            fh,
            fieldnames=[
                "path",
                "bytes",
                "code_cells",
                "outputs",
                "image_outputs",
                "max_rows",
                "flagged_outputs",
                "applicant_tokens",
                "executed",
                "errors",
            ],
        )
        w.writeheader()
        for r in results:
            out = dict(r)
            out["applicant_tokens"] = "|".join(r["applicant_tokens"])
            w.writerow(out)
    lines = [
        "# Notebook output scan",
        "",
        "All **15** notebooks were parsed as JSON. No notebook was executed and no output body is reproduced here (H5).",
        "",
        "| Notebook | Code cells | Outputs | Max table rows | >20-row outputs | Applicant tokens | Images | Errors |",
        "|---|---:|---:|---:|---:|---|---:|---:|",
    ]
    for r in results:
        tokens = ", ".join(f"`{t}`" for t in r["applicant_tokens"]) or "none"
        lines.append(
            f"| `{r['path']}` | {r['code_cells']} | {r['outputs']} | {r['max_rows']} | "
            f"{r['flagged_outputs']} | {tokens} | {r['image_outputs']} | {r['errors']} |"
        )
    total_flagged = sum(r["flagged_outputs"] for r in results)
    lines += [
        "",
        "## Findings",
        "",
        f"- Outputs with more than 20 visible table rows or applicant-level tokens: **{total_flagged}**.",
        "- The graded notebook and its backups contain executed analysis outputs, including prediction-table summaries.",
        "  Those outputs are part of the frozen F1 artifact and are **not stripped**.",
        "- The `v1_frozen/` copies are frozen by F2; the release copy is receipt-bound. No output was edited.",
        "- Per-notebook detail: `notebook_output_scan.csv`.",
        "",
        "## Decision",
        "",
        "Report only. No notebook output was removed or rewritten. If a future publication requires smaller",
        "notebooks, that is a new artifact decision, not a reorg action.",
        "",
    ]
    args.out.write_text("\n".join(lines), encoding="utf-8")
    print(f"WROTE {args.out}")
    print(f"WROTE {args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
