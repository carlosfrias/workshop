#!/usr/bin/env python3
"""
TI-WIKI-LINKS Test Harness — Scan markdown for broken internal links.
Runs against source markdown (before build) to catch problems early.
Usage: python3 test-wiki-links.py [--fix]
"""

import os, re, sys, argparse

WORKSPACE = "/Users/friasc/Cloud/ai-trading-workspace"
WIKI_ROOT = os.path.join(WORKSPACE, "wiki")
BROKEN = []

# Known valid external prefixes
EXTERNAL = ("http://", "https://", "mailto:", "tel:")

# Map flat paths → actual paths under wiki/
PATH_MAP = {
    "/technical-infrastructure/model-routing-guide": "/technical-infrastructure/reference/model-routing-guide",
    "/technical-infrastructure/node-capacity-map": "/technical-infrastructure/reference/node-capacity-map",
    "/technical-infrastructure/ansible-playbook-index": "/technical-infrastructure/reference/ansible-playbook-index",
    "/technical-infrastructure/multi-node-setup-2026-04-26": "/technical-infrastructure/guides/multi-node-setup-2026-04-26",
    "/technical-infrastructure/network-troubleshooting-guide": "/technical-infrastructure/troubleshooting/network-troubleshooting-guide",
    "/technical-infrastructure/ollama-setup": "/technical-infrastructure/guides/ollama-setup",
    "/technical-infrastructure/wireguard-lab-vpn": "/technical-infrastructure/guides/wireguard-lab-vpn",
    "/technical-infrastructure/pi-intercom-setup": "/technical-infrastructure/guides/pi-intercom-setup",
    "/technical-infrastructure/decomposition-examples/systemd-mount-lock": "/technical-infrastructure/decomposition-examples/systemd-mount-lock/00-decomposition-plan",
}


def resolve_link(href, source_dir):
    """Return the absolute filesystem path a VitePress link resolves to."""
    if href.startswith(EXTERNAL):
        return None  # External — skip

    # Anchor-only link
    if href.startswith("#"):
        return None  # Same-page anchor

    # Strip leading /
    if href.startswith("/"):
        rel = href[1:]
        root = WIKI_ROOT
    else:
        # Relative path — resolve from source file's directory
        rel = href
        root = source_dir

    # Directory with trailing slash → resolve to index.md
    target = os.path.join(root, rel)
    if rel.endswith("/") and os.path.isdir(target):
        idx = os.path.join(target, "index.md")
        if os.path.isfile(idx):
            return idx

    # Markdown or directory → check .md file
    if os.path.isfile(target + ".md"):
        return target + ".md"
    if os.path.isfile(target):
        return target
    if os.path.isdir(target):
        idx = os.path.join(target, "index.md")
        if os.path.isfile(idx):
            return idx
    return None


def extract_links(path):
    """Return list of (line_no, href, text) from a markdown file."""
    links = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for i, line in enumerate(f, 1):
            for m in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', line):
                text, href = m.group(1), m.group(2)
                # Skip external and special schemes
                if not href.startswith(EXTERNAL) and not href.startswith("#"):
                    links.append((i, href, text))
            for m in re.finditer(r'<a[^>]+href="([^"]*)"[^>]*>(.*?)</a>', line):
                href, text = m.group(1), m.group(2)
                if not href.startswith(EXTERNAL) and not href.startswith("#"):
                    links.append((i, href, text))
    return links


def scan_file(filepath):
    """Scan one markdown file for broken internal links."""
    source_dir = os.path.dirname(filepath)
    for line_no, href, text in extract_links(filepath):
        # Skip external and known-good anchors
        if href.startswith(EXTERNAL):
            continue
        if href.startswith("#"):
            continue
        resolved = resolve_link(href, source_dir)
        if resolved is None:
            BROKEN.append({
                "file": filepath,
                "line": line_no,
                "href": href,
                "text": text,
                "resolved": None,
                "category": classify_broken(href),
            })
        elif not os.path.isfile(resolved):
            BROKEN.append({
                "file": filepath,
                "line": line_no,
                "href": href,
                "text": text,
                "resolved": resolved,
                "category": classify_broken(href),
            })


def classify_broken(href):
    """Classify why a link is broken."""
    if href.startswith("/"):
        flat = href.split("#")[0]
        if flat in PATH_MAP:
            return f"flat-path (should be {PATH_MAP[flat]})"
    if "#" in href:
        return "anchor-mismatch"
    if href.endswith("/"):
        return "directory-no-index"
    return "page-not-found"


def main():
    ap = argparse.ArgumentParser(description="TI-WIKI-LINKS Test Harness")
    ap.add_argument("--fix", action="store_true", help="Print sed commands to fix flat paths")
    args = ap.parse_args()

    print("=" * 60)
    print("TI-WIKI-LINKS Test Harness")
    print("=" * 60)

    count_files = 0
    for root, dirs, files in os.walk(WIKI_ROOT):
        # Skip node_modules and hidden
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "node_modules"]
        for fn in files:
            if fn.endswith(".md"):
                scan_file(os.path.join(root, fn))
                count_files += 1

    # Also scan technical-infrastructure/wiki/ (source mirror)
    ti_wiki = os.path.join(WORKSPACE, "technical-infrastructure", "wiki")
    if os.path.isdir(ti_wiki):
        for root, dirs, files in os.walk(ti_wiki):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for fn in files:
                if fn.endswith(".md"):
                    scan_file(os.path.join(root, fn))
                    count_files += 1

    print(f"Scanned {count_files} markdown files")
    print("")

    if not BROKEN:
        print("✅ All internal links valid — 0 broken")
        return 0

    # Group by category
    by_cat = {}
    for b in BROKEN:
        by_cat.setdefault(b["category"], []).append(b)

    total = len(BROKEN)
    print(f"❌ {total} broken internal link(s) found:")
    print("")

    for cat, items in sorted(by_cat.items(), key=lambda x: -len(x[1])):
        print(f"  [{cat}] — {len(items)} link(s)")
        for b in items[:5]:
            rel = b["file"].replace(WORKSPACE + "/", "")
            print(f"    {rel}:{b['line']}  [{b['text']}] → {b['href']}")
        if len(items) > 5:
            print(f"    ... and {len(items)-5} more")
        print("")

    if args.fix:
        print("--- Suggested fixes (sed commands) ---")
        for b in BROKEN:
            flat = b["href"].split("#")[0]
            if flat in PATH_MAP:
                new_href = b["href"].replace(flat, PATH_MAP[flat], 1)
                rel = b["file"].replace(WORKSPACE + "/", "")
                print(f"sed -i '' 's|{b['href']}|{new_href}|g' {rel}")

    return 1


if __name__ == "__main__":
    sys.exit(main())
