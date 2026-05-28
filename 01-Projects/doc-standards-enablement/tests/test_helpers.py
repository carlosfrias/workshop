"""Shared utilities for inline decomposition testing.

Parsing, link extraction, LOD detection, and tier budget calculations.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ── Tier Budgets (derived from Phase 6 validation) ──────────────────────────

@dataclass
class TierBudget:
    """Inline decomposition budget per model tier."""
    name: str
    max_context: int
    max_cross_refs: int
    max_path_depth: int
    max_section_size_kb: float

TIER_BUDGETS = {
    "low": TierBudget(
        name="Low (<4K)",
        max_context=4000,
        max_cross_refs=3,
        max_path_depth=2,
        max_section_size_kb=2.0,
    ),
    "medium": TierBudget(
        name="Medium (~8K)",
        max_context=8000,
        max_cross_refs=6,
        max_path_depth=3,
        max_section_size_kb=4.0,
    ),
    "high": TierBudget(
        name="High (~32K)",
        max_context=32000,
        max_cross_refs=12,
        max_path_depth=4,
        max_section_size_kb=10.0,
    ),
}

# Router files are allowed more cross-refs (they route, not contain)
ROUTER_MULTIPLIER = 2.0


# ── Parsing Utilities ───────────────────────────────────────────────────────

def extract_markdown_links(content: str) -> list[tuple[str, str]]:
    """Extract all [text](./path.md) markdown links.

    Returns list of (text, path) tuples. Excludes:
    - External URLs (http/https)
    - Anchor-only links (#section)
    - Image links (![alt](url))
    """
    pattern = r'(?<!\!)\[([^\]]+)\]\(([^)]+)\)'
    matches = re.findall(pattern, content)
    return [
        (text, path) for text, path in matches
        if not path.startswith(("http://", "https://", "#"))
    ]


def extract_wikilinks(content: str) -> list[str]:
    """Extract Obsidian [[wikilinks]]."""
    pattern = r'\[\[([^\]|#]+)(?:[|#][^\]]+)?\]\]'
    return re.findall(pattern, content)


def count_cross_references(content: str) -> int:
    """Total cross-reference count (markdown links + wikilinks)."""
    md_links = len(extract_markdown_links(content))
    wiki_links = len(extract_wikilinks(content))
    return md_links + wiki_links


def has_lod_header(content: str) -> bool:
    """Check if content has at least one [LOD: ...] header OR metadata-style LOD."""
    if re.search(r'\[LOD:\s*(Low|Medium|High)\]', content, re.IGNORECASE):
        return True
    # Also detect metadata-style: **LOD:** Low
    if re.search(r'\*\*LOD:\*\*\s*(Low|Medium|High)', content):
        return True
    return False


def has_s_tight_header(content: str) -> bool:
    """Check if content has [S-TIGHT] section marker."""
    return bool(re.search(r'##?\s*\[S-TIGHT\]', content))


def has_tier_loading_directive(content: str) -> bool:
    """Check if content has a model-tier-based loading table."""
    # Look for a table that maps model types to what to load
    tier_patterns = [
        r'Low.*local.*<',
        r'Medium.*local.*~',
        r'High.*local.*~',
        r'Cloud.*>',
        r'Low.*<.*4K',
        r'Medium.*~.*8K',
        r'High.*~.*32K',
    ]
    found = sum(1 for p in tier_patterns if re.search(p, content, re.IGNORECASE))
    # Also detect the Load Directive table pattern
    if re.search(r'\|.*Model Tier.*\|.*Load', content):
        return True
    return found >= 2  # At least 2 tiers mentioned


def has_path_prefix_rule(content: str) -> bool:
    """Check if content enforces ./ prefix for navigable links."""
    return bool(re.search(r'\./.*prefix', content, re.IGNORECASE)) or \
           bool(re.search(r'MUST use \`\./`', content))


def extract_relative_paths(content: str) -> list[str]:
    """Extract resolvable relative markdown paths (./ or ../)."""
    links = extract_markdown_links(content)
    return [
        path for _, path in links
        if path.startswith("./") or path.startswith("../")
    ]


def is_router_file(content: str) -> bool:
    """Detect if file is a routing file (maps keywords → target files)."""
    # Router files typically have keyword→file mapping tables
    router_indicators = [
        r'\|.*Keywords.*\|.*Route.*\|',  # Routing table header
        r'\|.*Broad Keywords.*\|.*Route To.*\|',
        r'keywords.*route.*to',
    ]
    return any(re.search(p, content, re.IGNORECASE) for p in router_indicators)


def extract_lod_sections(content: str) -> list[dict]:
    """Extract LOD-tagged sections with their metadata.

    Returns list of {level, header, start, end} dicts.
    """
    sections = []
    pattern = r'(?:^|\n)(#{1,3})\s+.*?\[LOD:\s*(Low|Medium|High)\].*$'
    matches = list(re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE))

    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        sections.append({
            "level": match.group(1),
            "lod": match.group(2).capitalize(),
            "header": match.group(0).strip(),
            "size_bytes": end - start,
        })

    return sections


def extract_section_headers(content: str) -> list[str]:
    """Extract all section headers (## or ### level)."""
    pattern = r'^#{2,3}\s+(.+)$'
    matches = re.findall(pattern, content, re.MULTILINE)
    return [m.strip() for m in matches]


@dataclass
class InlineFile:
    """Analysis result for a single file."""
    path: Path
    content: str = field(repr=False)
    size_bytes: int = 0
    cross_ref_count: int = 0
    has_lod: bool = False
    has_s_tight: bool = False
    has_tier_directive: bool = False
    has_path_rule: bool = False
    is_router: bool = False
    lod_sections: list[dict] = field(default_factory=list)
    section_headers: list[str] = field(default_factory=list)
    relative_paths: list[str] = field(default_factory=list)

    @classmethod
    def from_file(cls, path: Path) -> Optional["InlineFile"]:
        """Analyze a file and return InlineFile or None if unreadable."""
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return None

        return cls(
            path=path,
            content=content,
            size_bytes=len(content.encode("utf-8")),
            cross_ref_count=count_cross_references(content),
            has_lod=has_lod_header(content),
            has_s_tight=has_s_tight_header(content),
            has_tier_directive=has_tier_loading_directive(content),
            has_path_rule=has_path_prefix_rule(content),
            is_router=is_router_file(content),
            lod_sections=extract_lod_sections(content),
            section_headers=extract_section_headers(content),
            relative_paths=extract_relative_paths(content),
        )

    def cross_ref_budget(self, tier: str = "medium") -> int:
        """Get cross-reference budget for this file, adjusted for router files."""
        base = TIER_BUDGETS[tier].max_cross_refs
        return int(base * ROUTER_MULTIPLIER) if self.is_router else base

    def max_lod_section_size(self, tier: str = "medium") -> float:
        """Max section size in KB for this file's tier."""
        return TIER_BUDGETS[tier].max_section_size_kb

    @property
    def summary(self) -> str:
        """One-line summary for test output."""
        router = " [ROUTER]" if self.is_router else ""
        return (
            f"{self.path.name} ({self.size_bytes}B, "
            f"{self.cross_ref_count} refs, LOD={self.has_lod}, "
            f"TierDirective={self.has_tier_directive}){router}"
        )
