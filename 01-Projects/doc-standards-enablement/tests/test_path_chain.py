"""Test downstream path chain files for inline decomposition.

When AGENTS.md → routing/section.md → phases/phase.md forms a chain,
every node in the chain must also be inline-decomposable. A chain is
only as strong as its weakest link.

From validation: "Navigation overhead in decomposed files exhausts
context window regardless of available system memory."
"""

from __future__ import annotations

from collections import deque
from pathlib import Path

import pytest

from .test_helpers import InlineFile, TIER_BUDGETS, extract_relative_paths


MAX_CHAIN_DEPTH = 3  # Medium tier budget


def _resolve_link(source: Path, link: str) -> Path | None:
    """Resolve a relative markdown link against the source file's directory."""
    base = source.parent
    resolved = (base / link).resolve()
    if resolved.exists() and resolved.suffix == ".md":
        return resolved
    return None


def _walk_chain(entry: Path, max_depth: int = MAX_CHAIN_DEPTH) -> list[tuple[int, Path]]:
    """BFS walk of cross-reference chain from entry point.

    Returns list of (depth, path) tuples.
    """
    visited: set[str] = set()
    result: list[tuple[int, Path]] = []
    queue: deque[tuple[int, Path]] = deque([(0, entry)])

    while queue:
        depth, current = queue.popleft()
        resolved = str(current.resolve())
        if resolved in visited or depth > max_depth:
            continue
        visited.add(resolved)
        result.append((depth, current))

        if depth >= max_depth:
            continue

        # Read and extract links
        try:
            content = current.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        for link in extract_relative_paths(content):
            target = _resolve_link(current, link)
            if target and str(target.resolve()) not in visited:
                queue.append((depth + 1, target))

    return result


def _find_chain_entries(inline_files: list[InlineFile]) -> list[Path]:
    """Find AGENTS.md files that have cross-references (chain entry points)."""
    entries = []
    for f in inline_files:
        if f.relative_paths:
            entries.append(f.path)
    return entries


# ── Tests ───────────────────────────────────────────────────────────────────


class TestPathChainDepth:
    """Chain depth from AGENTS.md to leaf files must stay within budget."""

    def test_workshop_chain_depth_within_budget(self, analyzed_agents: list[InlineFile]):
        """Workshop AGENTS.md → routing/ sections chain must not exceed 3 hops."""
        workshop_entries = [
            f.path for f in analyzed_agents
            if "workshop" in str(f.path) and f.relative_paths
        ]
        violations = []
        for entry in workshop_entries[:5]:  # Limit to 5 to keep test fast
            chain = _walk_chain(entry, max_depth=MAX_CHAIN_DEPTH + 1)
            max_depth_found = max(d for d, _ in chain) if chain else 0
            if max_depth_found > MAX_CHAIN_DEPTH:
                deepest = [(d, p) for d, p in chain if d == max_depth_found]
                violations.append((entry, max_depth_found, deepest))

        if violations:
            report = "\n  - ".join([
                f"{str(entry)} → depth {depth} (deepest: {', '.join(str(p.name) for _, p in deep)})"
                for entry, depth, deep in violations
            ])
            pytest.fail(
                f"{len(violations)} workshop AGENTS.md chains exceed "
                f"max depth {MAX_CHAIN_DEPTH}:\n  - {report}\n\n"
                f"Inline the deep chain content or add tier-based loading directives "
                f"so low-capacity models can stop early."
            )


class TestChainNodeLOD:
    """Every node in the path chain must have LOD headers."""

    def test_chain_nodes_have_lod(self, analyzed_agents: list[InlineFile]):
        """Files reached from AGENTS.md cross-references must also have LOD headers."""
        entries = _find_chain_entries(analyzed_agents)[:5]
        violations = []
        seen = set()

        for entry in entries:
            chain = _walk_chain(entry, max_depth=2)  # Only check first 2 levels
            for depth, path in chain:
                if depth == 0:
                    continue  # Skip the entry itself (tested elsewhere)
                resolved = str(path.resolve())
                if resolved in seen:
                    continue
                seen.add(resolved)
                f = InlineFile.from_file(path)
                if f is None:
                    continue
                if not f.has_lod:
                    violations.append((depth, path))

        if violations:
            report = "\n  - ".join([
                f"Depth {d}: {str(p)}"
                for d, p in sorted(violations)
            ])
            pytest.fail(
                f"{len(violations)} downstream chain files missing LOD headers:\n"
                f"  - {report}\n\n"
                f"Every file in the chain must have [LOD: ...] markers so "
                f"models can determine what to load at each step."
            )


class TestChainNodeIntegrity:
    """Chain nodes must have section markers and be independently loadable."""

    def test_chain_nodes_have_sections(self, analyzed_agents: list[InlineFile]):
        """Downstream files must have section headers for model navigation."""
        entries = _find_chain_entries(analyzed_agents)[:5]
        violations = []
        seen = set()

        for entry in entries:
            chain = _walk_chain(entry, max_depth=2)
            for depth, path in chain:
                if depth == 0:
                    continue
                resolved = str(path.resolve())
                if resolved in seen:
                    continue
                seen.add(resolved)
                f = InlineFile.from_file(path)
                if f is None:
                    continue
                if len(f.section_headers) < 2:
                    violations.append((depth, path, len(f.section_headers)))

        if violations:
            report = "\n  - ".join([
                f"Depth {d}: {str(p)} ({sections} sections)"
                for d, p, sections in violations
            ])
            pytest.fail(
                f"{len(violations)} chain files have <2 sections:\n  - {report}"
            )


class TestChainCrossRefLimits:
    """Chain nodes must respect cross-reference budgets at each hop."""

    def test_chain_nodes_within_budget(self, analyzed_agents: list[InlineFile]):
        """Downstream files should not exceed medium-tier cross-ref budget."""
        entries = _find_chain_entries(analyzed_agents)[:5]
        violations = []
        seen = set()
        budget = TIER_BUDGETS["medium"].max_cross_refs

        for entry in entries:
            chain = _walk_chain(entry, max_depth=2)
            for depth, path in chain:
                if depth == 0:
                    continue
                resolved = str(path.resolve())
                if resolved in seen:
                    continue
                seen.add(resolved)
                f = InlineFile.from_file(path)
                if f is None:
                    continue
                if f.cross_ref_count > budget:
                    violations.append((depth, path, f.cross_ref_count))

        if violations:
            report = "\n  - ".join([
                f"Depth {d}: {str(p)} ({refs} refs > {budget} budget)"
                for d, p, refs in violations
            ])
            pytest.fail(
                f"{len(violations)} chain files exceed medium-tier cross-ref "
                f"budget ({budget}):\n  - {report}"
            )


class TestLinkResolution:
    """All cross-reference links in the chain must resolve to existing files."""

    def test_chain_links_resolve(self, analyzed_agents: list[InlineFile]):
        """No broken links in the first 2 levels of the path chain."""
        entries = _find_chain_entries(analyzed_agents)[:5]
        broken = []
        seen_files = set()

        for entry in entries:
            chain = _walk_chain(entry, max_depth=2)
            for depth, path in chain:
                resolved_key = str(path.resolve())
                if resolved_key in seen_files:
                    continue
                seen_files.add(resolved_key)
                f = InlineFile.from_file(path)
                if f is None:
                    continue
                for link in f.relative_paths:
                    target = _resolve_link(path, link)
                    if target is None:
                        broken.append((path, link, depth))

        if broken:
            report = "\n  - ".join([
                f"{str(src)} → `{link}` (depth {d})"
                for src, link, d in broken[:10]  # Show first 10
            ])
            total = len(broken)
            suffix = f"\n  ... and {total - 10} more" if total > 10 else ""
            pytest.fail(
                f"{total} broken link(s) in path chain:{suffix}\n  - {report}"
            )


class TestChainSelfContainment:
    """Chain nodes must be independently understandable."""

    def test_chain_nodes_have_summary(self, analyzed_agents: list[InlineFile]):
        """Downstream files should have a Summary header or equivalent."""
        entries = _find_chain_entries(analyzed_agents)[:5]
        violations = []
        seen = set()

        for entry in entries:
            chain = _walk_chain(entry, max_depth=2)
            for depth, path in chain:
                if depth == 0:
                    continue
                resolved = str(path.resolve())
                if resolved in seen:
                    continue
                seen.add(resolved)
                try:
                    content = path.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    continue
                # Check for Summary or S-TIGHT or Purpose
                has_indicator = (
                    "## Summary" in content
                    or "[S-TIGHT]" in content
                    or "## Purpose" in content
                    or "**Purpose:**" in content
                )
                if not has_indicator:
                    violations.append((depth, path))

        if violations:
            report = "\n  - ".join([
                f"Depth {d}: {str(p)}"
                for d, p in violations
            ])
            pytest.fail(
                f"{len(violations)} chain files lack Summary/S-TIGHT/Purpose indicator:\n"
                f"  - {report}\n\n"
                f"Each file should have a brief summary so models can determine "
                f"relevance without reading the full content."
            )
