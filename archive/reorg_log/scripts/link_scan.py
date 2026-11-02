#!/usr/bin/env python
"""Scan hand-in text, READMEs, docs and notebook sources for links and repo paths.

Read-only. Re-runnable. Usage:
  python link_scan.py --root <finalA> --manifest <csv> --out <md> --csv <csv> [--dry-run]
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

URL_RE = re.compile(r"https?://[^\s)\]>\"']+")
BACKTICK_RE = re.compile(r"`([^`\n]{2,240})`")
FILEURL_RE = re.compile(r"file:///[^\s)\]>\"']+")
TOP_PAT = re.compile(
    r"(?:^|[`'\"(])((?:analysis_outputs|telecom|v1_frozen|v2_work|v3_addons|v4_addons|philopateer\.(?:ipynb|pdf|pptx)|references\.txt|README\.docx|tutorial \(2\)\.ipynb)(?:/[^\s`'\"()]+)?)"
)
TEXT_EXT = {".md", ".txt", ".ipynb"}


def clean_url(u: str) -> str:
    return u.rstrip(".,;:!?)]}'\"'")


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
    urls: dict[str, set[str]] = defaultdict(set)
    paths: list[dict[str, str]] = []
    file_urls: list[dict[str, str]] = []
    for row in rows:
        rel = row["path"]
        p = root / rel
        if p.suffix.lower() not in TEXT_EXT:
            continue
        try:
            if p.suffix.lower() == ".ipynb":
                nb = json.loads(p.read_text(encoding="utf-8"))
                text = "\n".join(
                    "".join(c.get("source", [])) for c in nb.get("cells", []) if c.get("cell_type") in {"markdown", "code"}
                )
            else:
                text = p.read_text(encoding="utf-8", errors="replace")
        except (OSError, json.JSONDecodeError):
            continue
        for m in URL_RE.finditer(text):
            u = clean_url(m.group(0))
            line = text.count("\n", 0, m.start()) + 1
            urls[u].add(f"{rel}:{line}")
        for m in FILEURL_RE.finditer(text):
            line = text.count("\n", 0, m.start()) + 1
            file_urls.append({"file": rel, "line": str(line), "url": clean_url(m.group(0))})
        for m in BACKTICK_RE.finditer(text):
            value = m.group(1)
            if not TOP_PAT.search(value) and "file:///" not in value:
                continue
            line = text.count("\n", 0, m.start()) + 1
            pm = TOP_PAT.search(value)
            paths.append(
                {
                    "file": rel,
                    "line": str(line),
                    "referenced_path": (pm.group(1) if pm else value)[:220],
                    "risk": "breaks_when_moved" if pm else "external_absolute",
                }
            )
    print(f"UNIQUE_URLS={len(urls)} FILE_URLS={len(file_urls)} REPO_PATH_REFS={len(paths)}")
    if args.dry_run:
        print("DRY-RUN: no report written")
        return 0
    with args.csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["kind", "file", "line", "value", "risk"])
        w.writeheader()
        for u, refs in sorted(urls.items()):
            w.writerow({"kind": "external_url", "file": sorted(refs)[0].rsplit(":", 1)[0], "line": sorted(refs)[0].rsplit(":", 1)[1], "value": u, "risk": "external"})
        for r in file_urls:
            w.writerow({"kind": "file_url", "file": r["file"], "line": r["line"], "value": r["url"], "risk": "stale_absolute"})
        for r in paths:
            w.writerow({"kind": "repo_path", "file": r["file"], "line": r["line"], "value": r["referenced_path"], "risk": r["risk"]})
    unique_breaks = sorted({r["referenced_path"] for r in paths if r["risk"] == "breaks_when_moved"})
    lines = [
        "# Link scan (H11)",
        "",
        "Read-only scan of hand-in text, READMEs, docs and notebook **sources**; URLs were not fetched.",
        "",
        f"- Unique external URLs: **{len(urls)}**",
        f"- `file:///` absolute links: **{len(file_urls)}**",
        f"- Repo-path references in backticks: **{len(paths)}**",
        f"- Distinct repo paths that break on move: **{len(unique_breaks)}**",
        "",
        "## External URLs (unique, with first reference)",
        "",
        "| URL | First reference |",
        "|---|---|",
    ]
    for u, refs in sorted(urls.items(), key=lambda kv: (-len(kv[1]), kv[0].lower()))[:60]:
        first = sorted(refs)[0]
        lines.append(f"| <{u}> | `{first}` |")
    if len(urls) > 60:
        lines.append(f"| … {len(urls)-60} more | see `link_scan.csv` |")
    lines += [
        "",
        "## Repo paths that break when their top-level folder moves",
        "",
        "| Old path reference | Files mentioning it |",
        "|---|---:|",
    ]
    for pth in unique_breaks[:80]:
        files = sorted({r["file"] for r in paths if r["referenced_path"] == pth})
        lines.append(f"| `{pth}` | {len(files)} |")
    if len(unique_breaks) > 80:
        lines.append(f"| … {len(unique_breaks)-80} more | see `link_scan.csv` |")
    lines += [
        "",
        "## Absolute `file:///` links",
        "",
        "These are historical editor links into the pre-reorg absolute path. They are stale after the move;",
        "the frozen artifacts that contain them cannot be edited. `PATH_MAP.md` records the mapping and",
        "`submission/README.md` records the assumptions.",
        "",
        "| File | Line | URL host/path shape |",
        "|---|---:|---|",
    ]
    for r in file_urls[:40]:
        # Keep the shape, mask the personal path segment.
        safe = re.sub(r"file:///[A-Za-z]:/[^\s)]*", "file:///<absolute-local-path>", r["url"])
        lines.append(f"| `{r['file']}` | {r['line']} | `{safe}` |")
    if len(file_urls) > 40:
        lines.append(f"| … {len(file_urls)-40} more | — | see `link_scan.csv` |")
    lines += [
        "",
        "## Mitigation",
        "",
        "- `pre-reorg` is the restore ref for the old layout; the old paths remain reachable there.",
        "- `PATH_MAP.md` maps every old top-level to its new location.",
        "- Frozen artifacts (F1/F2) are **not edited** to chase links; stale links are disclosed, not silently fixed.",
        "",
        "Full rows: `link_scan.csv`.",
        "",
    ]
    args.out.write_text("\n".join(lines), encoding="utf-8")
    print(f"WROTE {args.out}")
    print(f"WROTE {args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
