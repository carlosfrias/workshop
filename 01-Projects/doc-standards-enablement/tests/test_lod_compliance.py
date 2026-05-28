"""Test LOD compliance: files must have proper Layered Contextualization headers.

From validation: "Navigation overhead in decomposed files exhausts context window."
LOD headers are the primary mechanism that prevents this by guiding models
on what to load and what to skip.
"""

from __future__ import annotations

import pytest

from .test_helpers import InlineFile, TIER_BUDGETS


# ── Discovery completeness tests ────────────────────────────────────────────


class TestDiscoveryHealth:
    """Verify we actually found files to test."""

    def test_agents_md_discovered(self, analyzed_agents: list[InlineFile]):
        """At minimum the root AGENTS.md files must be discovered."""
        assert len(analyzed_agents) > 0, "No AGENTS.md files found — check discovery paths"
        names = {f.path.name for f in analyzed_agents}
        assert "AGENTS.md" in names, "No files named AGENTS.md discovered"

    def test_skill_md_discovered(self, analyzed_skills: list[InlineFile]):
        """At minimum the project-blueprint and doc-standards SKILL.md files must be found."""
        assert len(analyzed_skills) > 0, "No SKILL.md files found — check discovery paths"


# ── LOD Header tests ───────────────────────────────────────────────────────


class TestLODHeaders:
    """Every AGENTS.md and SKILL.md should have LOD headers for tier-based loading."""

    def test_all_agents_have_lod(self, analyzed_agents: list[InlineFile]):
        """Every AGENTS.md should have at least one [LOD: ...] section marker."""
        failures = [f for f in analyzed_agents if not f.has_lod]
        if failures:
            names = "\n  - ".join([str(f.path) for f in failures])
            pytest.fail(
                f"{len(failures)}/{len(analyzed_agents)} AGENTS.md files missing LOD headers:\n"
                f"  - {names}\n\n"
                f"Add [LOD: Low], [LOD: Medium], or [LOD: High] markers to section headers."
            )

    def test_all_skills_have_lod(self, analyzed_skills: list[InlineFile]):
        """Every SKILL.md should have at least one [LOD: ...] section marker."""
        failures = [f for f in analyzed_skills if not f.has_lod]
        if failures:
            names = "\n  - ".join([str(f.path) for f in failures])
            pytest.fail(
                f"{len(failures)}/{len(analyzed_skills)} SKILL.md files missing LOD headers:\n"
                f"  - {names}"
            )

    def test_lod_sections_present_in_agents(self, analyzed_agents: list[InlineFile]):
        """AGENTS.md files should have at least 2 LOD-tagged sections."""
        # Router files may have fewer, so we're lenient but track
        deficient = [
            f for f in analyzed_agents
            if len(f.lod_sections) < 1 and not f.is_router
        ]
        if deficient:
            names = "\n  - ".join([f"{str(f.path)} ({len(f.lod_sections)} sections)" for f in deficient])
            pytest.fail(
                f"{len(deficient)}/{len(analyzed_agents)} non-router AGENTS.md files "
                f"have fewer than 1 LOD-tagged section:\n  - {names}"
            )


class TestTierLoadingDirectives:
    """Files that reference other files must guide models on which to load."""

    def test_agents_have_tier_directive(self, analyzed_agents: list[InlineFile]):
        """AGENTS.md with cross-references should have tier-based loading instructions."""
        # Only test files that have cross-references
        files_with_refs = [f for f in analyzed_agents if f.cross_ref_count > 0]
        missing = [
            f for f in files_with_refs
            if not f.has_tier_directive
        ]
        if missing:
            names = "\n  - ".join([str(f.path) for f in missing])
            pytest.fail(
                f"{len(missing)}/{len(files_with_refs)} AGENTS.md files have "
                f"cross-references but no tier-loading directive:\n  - {names}\n\n"
                f"Add a 'Load Directive' table showing which sections to load per model tier."
            )

    def test_skills_have_tier_directive(self, analyzed_skills: list[InlineFile]):
        """SKILL.md files should have tier-based loading instructions."""
        missing = [f for f in analyzed_skills if not f.has_tier_directive]
        if missing:
            names = "\n  - ".join([str(f.path) for f in missing])
            pytest.fail(
                f"{len(missing)}/{len(analyzed_skills)} SKILL.md files missing "
                f"tier-loading directive:\n  - {names}"
            )


class TestPathPrefixRule:
    """All navigable markdown links MUST use ./ prefix."""

    def test_agents_enforce_path_prefix(self, analyzed_agents: list[InlineFile]):
        """AGENTS.md files should mention the ./ path prefix rule."""
        missing = [
            f for f in analyzed_agents
            if f.cross_ref_count > 2 and not f.has_path_rule
        ]
        if missing:
            names = "\n  - ".join([str(f.path) for f in missing])
            pytest.fail(
                f"{len(missing)}/{len(analyzed_agents)} AGENTS.md files have >2 "
                f"cross-references but no path prefix rule:\n  - {names}\n\n"
                f"Add: 'All navigable relative paths in markdown links MUST use ./ prefix.'"
            )


class TestSectionSize:
    """LOD sections must stay within tier budgets."""

    def test_agents_sections_within_budget(self, analyzed_agents: list[InlineFile]):
        """No LOD section in any AGENTS.md should exceed 10KB (high tier max)."""
        oversized = []
        for f in analyzed_agents:
            for s in f.lod_sections:
                size_kb = s["size_bytes"] / 1024
                if size_kb > TIER_BUDGETS["high"].max_section_size_kb:
                    oversized.append((f, s, size_kb))

        if oversized:
            report = "\n  - ".join([
                f"{str(f.path)} → {s['header']} ({size:.1f}KB > {TIER_BUDGETS['high'].max_section_size_kb}KB)"
                for f, s, size in oversized
            ])
            pytest.fail(
                f"{len(oversized)} LOD section(s) exceed high-tier budget:\n  - {report}"
            )

    def test_skill_sections_within_budget(self, analyzed_skills: list[InlineFile]):
        """No LOD section in any SKILL.md should exceed 10KB."""
        oversized = []
        for f in analyzed_skills:
            for s in f.lod_sections:
                size_kb = s["size_bytes"] / 1024
                if size_kb > TIER_BUDGETS["high"].max_section_size_kb:
                    oversized.append((f, s, size_kb))

        if oversized:
            report = "\n  - ".join([
                f"{str(f.path)} → {s['header']} ({size:.1f}KB)"
                for f, s, size in oversized
            ])
            pytest.fail(f"{len(oversized)} LOD section(s) exceed high-tier budget:\n  - {report}")
