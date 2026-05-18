#!/usr/bin/env python3
"""
Wiki Link Tester — Reusable Test Harness
========================================

Validates all internal links in a VitePress-built wiki site.
Checks:
1. All sidebar navigation links resolve to existing HTML files
2. All in-page anchor links resolve within the same page
3. All cross-page links resolve to existing HTML files
4. No orphaned markdown files (no corresponding HTML in dist/)

Usage:
    python3 scripts/test-wiki-links.py [--dist-dir PATH] [--verbose]

Requirements:
    - Wiki must be built first: npm run build
    - Checks against .vitepress/dist/ directory

Exit codes:
    0 = All links valid
    1 = Broken links found
    2 = Build output not found
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse


class WikiLinkTester:
    """Test harness for validating VitePress wiki internal links."""

    def __init__(self, dist_dir: str, verbose: bool = False, silent: bool = False):
        self.dist_dir = Path(dist_dir).resolve()
        self.verbose = verbose
        self.silent = silent
        self.broken = []
        self.checked = 0
        self.html_files = set()
        self.page_content = {}

    def log(self, msg: str):
        if self.verbose and not self.silent:
            print(f"  {msg}")

    def emit(self, msg: str):
        if not self.silent:
            print(msg)

    def load_html_files(self):
        """Index all HTML files in the dist directory."""
        self.log(f"Indexing HTML files in {self.dist_dir}")
        for f in self.dist_dir.rglob("*.html"):
            rel = f.relative_to(self.dist_dir)
            # Normalize VitePress clean-url paths
            self.html_files.add(str(rel))
        self.log(f"Found {len(self.html_files)} HTML files")

    def load_page_content(self):
        """Load content of all HTML files for anchor checking."""
        self.log("Loading page content for anchor validation...")
        for f in self.dist_dir.rglob("*.html"):
            rel = str(f.relative_to(self.dist_dir))
            with open(f, "r", encoding="utf-8", errors="ignore") as fh:
                self.page_content[rel] = fh.read()
        self.log(f"Loaded content for {len(self.page_content)} pages")

    def get_targets_from_links(self, html: str, current_page: str) -> list:
        """Extract all internal href targets from HTML."""
        targets = []
        # Find all <a href="..."> links
        for match in re.finditer(r'<a[^>]*?href=["\']([^"\']+)["\']', html):
            href = match.group(1)
            # Skip template variable placeholders (intentionally unresolved)
            if '{' in href or '}' in href:
                self.log(f"SKIPPED template placeholder: {href}")
                continue
            # Skip external links
            if href.startswith("http://") or href.startswith("https://") or href.startswith("mailto:"):
                continue
            # Skip anchor-only self-links (handled separately)
            if href.startswith("#"):
                targets.append(("anchor", href[1:], current_page))
                continue
            # Skip JavaScript
            if href.startswith("javascript:"):
                continue
            # Resolve relative to absolute path within dist
            current_dir = str(Path(current_page).parent) if current_page else ""
            if href.startswith("/"):
                resolved = href.lstrip("/")
            else:
                raw = str(Path(current_dir) / href).lstrip("/")
                import os
                resolved = os.path.normpath(raw)
                # os.path.normpath leaves leading ./ or ../ — strip those too
                while resolved.startswith("./"):
                    resolved = resolved[2:]
                while resolved.startswith("../"):
                    resolved = resolved[3:]
            # VitePress clean URLs: /foo/bar → foo/bar.html or foo/bar/index.html
            # Try both
            targets.append(("page", resolved, current_page))
        return targets

    def resolve_page_path(self, path: str) -> str | None:
        """Resolve a page path to its HTML file, or None if not found."""
        candidates = [
            path,
            path + ".html",
            path + "/index.html",
        ]
        if path.endswith("/"):
            candidates.append(path + "index.html")
        for c in candidates:
            c = c.lstrip("/")
            if c in self.html_files:
                return c
        # Check if path matches any file (handles trailing slashes)
        base = path.rstrip("/")
        for c in [base + ".html", base + "/index.html"]:
            if c in self.html_files:
                return c
        return None

    def check_anchor_exists(self, page_path: str, anchor: str) -> bool:
        """Check if a named anchor exists in an HTML file's content."""
        content = self.page_content.get(page_path, "")
        # VitePress anchors: <h1 id="anchor-name">...</h1> or <a name="anchor-name">
        patterns = [
            rf'id=["\']{re.escape(anchor)}["\']',
            rf'name=["\']{re.escape(anchor)}["\']',
        ]
        for pat in patterns:
            if re.search(pat, content):
                return True
        return False

    def check_sidebar_nav(self):
        """Check all sidebar navigation links from VP_SITE_DATA."""
        self.log("Checking sidebar navigation links...")
        errors = []
        # Find any page that contains VP_SITE_DATA with sidebar
        for page_path, content in self.page_content.items():
            if '"sidebar"' not in content:
                continue
            # Extract sidebar links — this is complex in JSON-in-JS
            # Simpler: search for link patterns in the sidebar JSON
            for m in re.finditer(r'"link":\s*"([^"]+)"', content):
                link = m.group(1)
                if not link or link.startswith("http"):
                    continue
                resolved = self.resolve_page_path(link.lstrip("/"))
                self.checked += 1
                if resolved is None:
                    msg = f"Sidebar nav: '{link}' → 404 (from {page_path})"
                    errors.append(msg)
                    self.broken.append(("sidebar", link, page_path))
        self.log(f"Checked {self.checked} sidebar links, {len(errors)} broken")
        return errors

    def check_cross_page_links(self):
        """Check all <a href> links between pages."""
        self.log("Checking cross-page links...")
        errors = []
        for page_path, content in self.page_content.items():
            targets = self.get_targets_from_links(content, page_path)
            for kind, target, source in targets:
                self.checked += 1
                if kind == "anchor":
                    # Check anchor in source page
                    if not self.check_anchor_exists(source, target):
                        # Some anchors might be generated dynamically; skip known false positives
                        if target not in ["VPContent", "app", ""]:
                            self.broken.append(("anchor", f"#{target} in {source}", source))
                else:
                    resolved = self.resolve_page_path(target)
                    if resolved is None:
                        # Deduplicate
                        existing = [b for b in self.broken if b[0] == "page" and b[1] == target]
                        if not existing:
                            msg = f"Dead link: '{target}' (from {source})"
                            errors.append(msg)
                            self.broken.append(("page", target, source))
        self.log(f"Checked {self.checked} total links, {len(errors)} broken")
        return errors

    def check_orphan_markdown(self):
        """Check for markdown files in wiki/ that have no corresponding HTML in dist/."""
        self.log("Checking for orphaned markdown files...")
        errors = []
        wiki_dir = self.dist_dir.parent.parent / "wiki"
        if not wiki_dir.exists():
            self.log("wiki/ directory not found, skipping orphan check")
            return errors
        for md in wiki_dir.rglob("*.md"):
            rel = str(md.relative_to(wiki_dir)).replace(".md", ".html")
            # Map to possible HTML paths
            html_path = rel
            index_alternative = str(md.relative_to(wiki_dir)).replace("index.md", "index.html")
            if (
                html_path not in self.html_files
                and index_alternative not in self.html_files
                and rel.rstrip("/") not in [p.rstrip("/") for p in self.html_files]
            ):
                # Try more patterns
                base = str(md.relative_to(wiki_dir)).replace(".md", "")
                found = False
                for candidate in [base + ".html", base + "/index.html"]:
                    if candidate in self.html_files:
                        found = True
                        break
                if not found and "README" not in str(md):
                    msg = f"Orphan: '{md.relative_to(wiki_dir)}' has no HTML output"
                    errors.append(msg)
                    self.broken.append(("orphan", str(md.relative_to(wiki_dir)), ""))
        self.log(f"Checked orphans, {len(errors)} issues")
        return errors

    def run(self) -> dict:
        """Run all tests and return results."""
        self.emit(f"🔍 Wiki Link Tester")
        self.emit(f"   Dist directory: {self.dist_dir}")
        self.emit(f"   Verbose: {self.verbose}")
        self.emit("")

        if not self.dist_dir.exists():
            self.emit(f"❌ Error: {self.dist_dir} does not exist.")
            self.emit("   Run 'npm run build' first.")
            return {"status": "error", "code": 2, "broken": []}

        self.load_html_files()
        self.load_page_content()

        all_errors = []
        all_errors.extend(self.check_sidebar_nav())
        all_errors.extend(self.check_cross_page_links())
        all_errors.extend(self.check_orphan_markdown())

        # Report
        self.emit(f"\n{'=' * 60}")
        self.emit(f"RESULTS: {len(self.broken)} broken out of {self.checked} checked")
        self.emit(f"{'=' * 60}")

        if not self.broken:
            self.emit("✅ All links valid!")
            return {"status": "pass", "code": 0, "broken": [], "total": self.checked}

        # Group by type
        by_type = {}
        for t, link, source in self.broken:
            by_type.setdefault(t, []).append((link, source))

        for t, items in by_type.items():
            self.emit(f"\n❌ {t.upper()} ({len(items)}):")
            for link, source in items[:20]:
                src = f" (from {source})" if source else ""
                self.emit(f"   - {link}{src}")
            if len(items) > 20:
                self.emit(f"   ... and {len(items) - 20} more")

        return {"status": "fail", "code": 1, "broken": self.broken, "total": self.checked}


def main():
    parser = argparse.ArgumentParser(description="Wiki Link Tester")
    parser.add_argument(
        "--dist-dir",
        default=".vitepress/dist",
        help="Path to VitePress dist directory (default: .vitepress/dist)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    tester = WikiLinkTester(args.dist_dir, verbose=args.verbose, silent=args.json)
    result = tester.run()

    if args.json:
        print(json.dumps(result, indent=2))

    sys.exit(result["code"])


if __name__ == "__main__":
    main()
