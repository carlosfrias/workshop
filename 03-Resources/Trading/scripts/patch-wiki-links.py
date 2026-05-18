#!/usr/bin/env python3
"""
Wiki Link Auto-Patcher
Fixes common broken link patterns across all wiki markdown files.
"""

import re
import sys
from pathlib import Path

WIKI_DIR = Path("wiki")

def fix_file(filepath: Path) -> list:
    """Fix known broken link patterns in a single file. Returns list of changes."""
    changes = []
    content = filepath.read_text()
    original = content

    # Pattern 1: Old wiki/ path prefix inside wiki files (when linking to own tree)
    # e.g. `technical-infrastructure/wiki/` -> `technical-infrastructure/`
    content, n = re.subn(
        r'((?:^|["\'>\s])[^"\'>\s]*)(?<!/)technical-infrastructure/wiki/',
        r'\1technical-infrastructure/',
        content
    )
    if n:
        changes.append(f"  fixed {n} 'technical-infrastructure/wiki/' -> 'technical-infrastructure/'")

    # Pattern 2: Old wiki/ path prefix for operational
    content, n = re.subn(
        r'((?:^|["\'>\s])[^"\'>\s]*)(?<!/)operational/wiki/',
        r'\1operational/',
        content
    )
    if n:
        changes.append(f"  fixed {n} 'operational/wiki/' -> 'operational/'")

    # Pattern 3: Old wiki/ path prefix for trading-desk
    content, n = re.subn(
        r'((?:^|["\'>\s])[^"\'>\s]*)(?<!/)trading-desk/wiki/',
        r'\1trading-desk/',
        content
    )
    if n:
        changes.append(f"  fixed {n} 'trading-desk/wiki/' -> 'trading-desk/'")

    # Pattern 4: `wiki/technical-infrastructure/` → `technical-infrastructure/`
    # Only in markdown links/context, not in code blocks or inline code
    content, n = re.subn(
        r'wiki/technical-infrastructure/',
        r'technical-infrastructure/',
        content
    )
    if n:
        changes.append(f"  fixed {n} 'wiki/technical-infrastructure/' -> 'technical-infrastructure/'")

    # Pattern 5: `../../position-management/` delink
    content, n = re.subn(
        r'\[([^\]]+)\]\((../../position-management/[^)]+)\)',
        r'\1',
        content
    )
    if n:
        changes.append(f"  delinked {n} '../../position-management/' references")

    # Pattern 6: `../../market-research/` delink
    content, n = re.subn(
        r'\[([^\]]+)\]\((../../market-research/[^)]+)\)',
        r'\1',
        content
    )
    if n:
        changes.append(f"  delinked {n} '../../market-research/' references")

    # Pattern 7: `../../bookkeeping/` delink
    content, n = re.subn(
        r'\[([^\]]+)\]\((../../bookkeeping/[^)]+)\)',
        r'\1',
        content
    )
    if n:
        changes.append(f"  delinked {n} '../../bookkeeping/' references")

    # Pattern 8: `ansible/playbooks/` as markdown link -> code-fence if not already
    content, n = re.subn(
        r'\[([^\]]+)\]\((ansible/playbooks/[^)]+\.ya?ml)\)',
        r'`ansible/playbooks/\2`',
        content,
    )
    if n:
        changes.append(f"  code-fenced {n} 'ansible/playbooks/' link(s)")

    # Pattern 9: `scripts/` as markdown link -> code-fence
    # Only when scripts/ is relative (not absolute path starting with /)
    content, n = re.subn(
        r'(?<![`"])\[([^\]]+)\]\((scripts/[^)]+)\)',
        r'`\2`',
        content
    )
    if n:
        changes.append(f"  code-fenced {n} 'scripts/' link(s)")

    # Pattern 10: `../scripts/` as markdown link -> code-fence
    content, n = re.subn(
        r'(?<![`"])\[([^\]]+)\]\((../scripts/[^)]+)\)',
        r'`\2`',
        content
    )
    if n:
        changes.append(f"  code-fenced {n} '../scripts/' link(s)")

    # Pattern 11: `local-model-pilot/skills/` as link -> code-fence
    content, n = re.subn(
        r'(?<![`"])\[([^\]]+)\]\((local-model-pilot/skills/[^)]+)\)',
        r'`\2`',
        content
    )
    if n:
        changes.append(f"  code-fenced {n} 'local-model-pilot/skills/' link(s)")

    # Pattern 12: `operational/data/` as link -> code-fence
    content, n = re.subn(
        r'(?<![`"])\[([^\]]+)\]\((operational/data/[^)]+)\)',
        r'`\2`',
        content
    )
    if n:
        changes.append(f"  code-fenced {n} 'operational/data/' link(s)")

    # Pattern 13: `templates/PLAN-2026-05-01-0915` -> fix path
    # These are in templates dir linking to sibling templates
    content, n = re.subn(
        r'\[([^\]]+)\]\((PLAN-2026-05-01-0915)\)',
        r'[\1](/technical-infrastructure/templates/\2)',
        content
    )
    if n:
        changes.append(f"  fixed {n} template PLAN-2026-05-01-0915 links")

    content, n = re.subn(
        r'\[([^\]]+)\]\((PLAN-2026-05-01-1547)\)',
        r'[\1](/technical-infrastructure/operational/planning/\2)',
        content
    )
    if n:
        changes.append(f"  fixed {n} template PLAN-2026-05-01-1547 links")

    # Pattern 14: `technical-infrastructure/operational/sessions/BACKLOG` -> `/technical-infrastructure/operational/BACKLOG`
    content, n = re.subn(
        r'technical-infrastructure/operational/sessions/BACKLOG',
        r'technical-infrastructure/operational/BACKLOG',
        content
    )
    if n:
        changes.append(f"  fixed {n} 'sessions/BACKLOG' -> 'BACKLOG'")

    # Pattern 15: `technical-infrastructure/WIKI` -> `/` or delink
    content, n = re.subn(
        r'\[([^\]]+)\]\((technical-infrastructure/WIKI)\)',
        r'\1',
        content
    )
    if n:
        changes.append(f"  delinked {n} 'technical-infrastructure/WIKI' references")

    # Pattern 16: `technical-infrastructure/BACKLOG` -> `/technical-infrastructure/operational/BACKLOG`
    content, n = re.subn(
        r'(?!["\'>])(technical-infrastructure/BACKLOG)(?!["\'a-z])',
        r'technical-infrastructure/operational/BACKLOG',
        content
    )
    if n:
        changes.append(f"  fixed {n} 'technical-infrastructure/BACKLOG' paths")

    # Pattern 17: Fix `guides/pi-keyword-router` inside guides/getting-started.html context
    # This is wrong - products should be under /products/ not /guides/
    content, n = re.subn(
        r'guides/pi-keyword-router',
        r'products/pi-keyword-router',
        content
    )
    if n:
        changes.append(f"  fixed {n} 'guides/pi-keyword-router' -> 'products/pi-keyword-router'")

    content, n = re.subn(
        r'guides/project-blueprint',
        r'products/project-blueprint',
        content
    )
    if n:
        changes.append(f"  fixed {n} 'guides/project-blueprint' -> 'products/project-blueprint'")

    content, n = re.subn(
        r'guides/trading-agents',
        r'products/trading-agents',
        content
    )
    if n:
        changes.append(f"  fixed {n} 'guides/trading-agents' -> 'products/trading-agents'")

    # Pattern 18: `technical-infrastructure/prompts/` -> likely meant `technical-infrastructure/`
    content, n = re.subn(
        r'technical-infrastructure/prompts/',
        r'technical-infrastructure/',
        content
    )
    if n:
        changes.append(f"  fixed {n} 'technical-infrastructure/prompts/' -> 'technical-infrastructure/'")

    if content != original:
        filepath.write_text(content)
        return changes
    return []


def main():
    total_files = 0
    total_changes = 0

    for md_file in sorted(WIKI_DIR.rglob("*.md")):
        # Skip any node_modules or hidden dirs
        parts = md_file.parts
        if any(p.startswith(".") and p != "." for p in parts):
            continue

        changes = fix_file(md_file)
        if changes:
            total_files += 1
            total_changes += len(changes)
            print(f"{md_file}")
            for c in changes:
                print(f"  {c}")
            print()

    print(f"Modified {total_files} files with {total_changes} total fix categories")


if __name__ == "__main__":
    main()
