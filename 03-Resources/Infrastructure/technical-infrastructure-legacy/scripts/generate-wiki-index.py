#!/usr/bin/env python3
"""
generate-wiki-index.py — Auto-generate operational index for Trading Desk wiki

Scans operational directories and produces a markdown index page.
Run this after adding new STATUS, SESSION-NOTES, PLAN, or RECOMMENDATION files.

Usage:
    python3 scripts/generate-wiki-index.py
    python3 scripts/generate-wiki-index.py --max 10

Output: wiki/operational-index.md (overwritten)
"""
import os
import re
import argparse
from pathlib import Path
from datetime import datetime

WIKI_BASE = Path("wiki")
OPERATIONAL_BASE = WIKI_BASE / "technical-infrastructure" / "operational"
OUTPUT = WIKI_BASE / "operational-index.md"

MAX_DEFAULT = 20


def extract_title(filepath: Path) -> str:
    """Extract first H1 from markdown file, or return cleaned filename."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("# "):
                    return line[2:].strip()
    except Exception:
        pass
    # Fallback: clean filename
    name = filepath.stem
    name = re.sub(r'^(STATUS|SESSION-NOTES|PLAN|RECOMMENDATION)-', '', name)
    name = re.sub(r'-', ' ', name)
    return name.strip()


def parse_date_from_filename(filename: str) -> str:
    """Extract YYYY-MM-DD from filenames like STATUS-2026-05-03-1020.md"""
    m = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    return m.group(1) if m else ""


def list_docs(directory: Path, pattern: str, max_items: int) -> list:
    """List markdown files matching pattern, sorted newest first."""
    if not directory.exists():
        return []
    files = sorted(
        [f for f in directory.glob(pattern) if f.is_file()],
        key=lambda p: p.name,
        reverse=True
    )
    results = []
    for f in files[:max_items]:
        rel_path = str(f.relative_to(WIKI_BASE)).replace(".md", "")
        date = parse_date_from_filename(f.name)
        title = extract_title(f)
        results.append({
            "path": f"/{rel_path}",
            "filename": f.name,
            "date": date,
            "title": title,
        })
    return results


def build_table(rows: list, cols: list) -> str:
    """Build a markdown table from rows."""
    if not rows:
        return "_No documents found._\n"

    header = "| " + " | ".join(cols) + " |"
    separator = "|" + "|".join([" --- " for _ in cols]) + "|"

    lines = [header, separator]
    for r in rows:
        line = "| " + " | ".join(str(r.get(c, "")) for c in cols) + " |"
        lines.append(line)
    return "\n".join(lines) + "\n"


def generate_index(max_items: int) -> str:
    lines = [
        "# Operational Index",
        "",
        f"**Auto-generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}",
        "",
        "This page lists all operational documents — status reports, session notes, plans, and recommendations.",
        "",
        "---",
        "",
    ]

    # ── Status Reports ──
    statuses = list_docs(OPERATIONAL_BASE / "status", "STATUS-*.md", max_items)
    lines.append("## Status Reports")
    lines.append("")
    lines.append(build_table(statuses, ["Date", "Document", "Title"]))
    lines.append(f"[All status documents →](/technical-infrastructure/operational/status/)\n")

    # ── Session Notes ──
    sessions = list_docs(OPERATIONAL_BASE / "sessions", "SESSION-NOTES-*.md", max_items)
    lines.append("## Session Notes")
    lines.append("")
    lines.append(build_table(sessions, ["Date", "Document", "Title"]))
    lines.append(f"[All session notes →](/technical-infrastructure/operational/sessions/)\n")

    # ── Plans ──
    plans = list_docs(OPERATIONAL_BASE / "planning", "PLAN-*.md", max_items)
    lines.append("## Plans")
    lines.append("")
    lines.append(build_table(plans, ["Date", "Document", "Title"]))
    lines.append(f"[All plans →](/technical-infrastructure/operational/planning/)\n")

    # ── Recommendations ──
    recs = list_docs(OPERATIONAL_BASE / "recommendations", "RECOMMENDATION-*.md", max_items)
    lines.append("## Recommendations")
    lines.append("")
    lines.append(build_table(recs, ["Date", "Document", "Title"]))
    lines.append(f"[All recommendations →](/technical-infrastructure/operational/recommendations/)\n")

    # ── Backlog ──
    backlog = OPERATIONAL_BASE / "BACKLOG.md"
    if backlog.exists():
        lines.append("## Backlog")
        lines.append("")
        lines.append(f"[View full backlog →](/technical-infrastructure/operational/BACKLOG)\n")

    lines.append("---")
    lines.append("")
    lines.append("*To regenerate this page: `python3 scripts/generate-wiki-index.py`*")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate wiki operational index")
    parser.add_argument("--max", type=int, default=MAX_DEFAULT, help=f"Max items per section (default {MAX_DEFAULT})")
    args = parser.parse_args()

    content = generate_index(args.max)
    OUTPUT.write_text(content, encoding="utf-8")
    print(f"✅ Generated {OUTPUT}")
    print(f"   Sections: status, sessions, plans, recommendations")
    print(f"   Max per section: {args.max}")


if __name__ == "__main__":
    main()
