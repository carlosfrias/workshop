"""Test core inline decomposition properties.

Tests that files minimize navigation overhead by staying within
cross-reference budgets and being self-contained enough for
low-capacity models to understand without reading referenced files.

From validation: "A 4B model with the linear script produced MORE correct
output than an 8B model with the decomposed approach."
"""

from __future__ import annotations

import pytest

from .test_helpers import InlineFile, TIER_BUDGETS


class TestCrossReferenceBudget:
    """Cross-references are the primary source of navigation overhead."""

    def test_agents_low_tier_budget(self, analyzed_agents: list[InlineFile]):
        """AGENTS.md files that claim to support low-tier models must stay within budget."""
        failures = []
        for f in analyzed_agents:
            budget = f.cross_ref_budget("low")
            if f.cross_ref_count > budget:
                failures.append((f, budget))

        if failures:
            report = "\n  - ".join([
                f"{str(f.path)} → {f.cross_ref_count} refs (budget: {budget})"
                for f, budget in failures
            ])
            pytest.fail(
                f"{len(failures)}/{len(analyzed_agents)} AGENTS.md files exceed "
                f"low-tier cross-ref budget ({TIER_BUDGETS['low'].max_cross_refs}):\n  - {report}"
            )

    def test_agents_medium_tier_budget(self, analyzed_agents: list[InlineFile]):
        """All AGENTS.md files should stay within medium-tier cross-ref budget."""
        failures = []
        for f in analyzed_agents:
            budget = f.cross_ref_budget("medium")
            if f.cross_ref_count > budget:
                failures.append((f, budget))

        if failures:
            report = "\n  - ".join([
                f"{str(f.path)} → {f.cross_ref_count} refs (budget: {budget})"
                for f, budget in failures
            ])
            pytest.fail(
                f"{len(failures)}/{len(analyzed_agents)} AGENTS.md files exceed "
                f"medium-tier cross-ref budget ({TIER_BUDGETS['medium'].max_cross_refs}):\n  - {report}"
            )

    def test_skills_cross_ref_budget(self, analyzed_skills: list[InlineFile]):
        """SKILL.md files should stay within high-tier cross-ref budget."""
        failures = []
        for f in analyzed_skills:
            budget = f.cross_ref_budget("high")
            if f.cross_ref_count > budget:
                failures.append((f, budget))

        if failures:
            report = "\n  - ".join([
                f"{str(f.path)} → {f.cross_ref_count} refs (budget: {budget})"
                for f, budget in failures
            ])
            pytest.fail(
                f"{len(failures)}/{len(analyzed_skills)} SKILL.md files exceed "
                f"high-tier cross-ref budget ({TIER_BUDGETS['high'].max_cross_refs}):\n  - {report}"
            )


class TestSelfContainment:
    """Files must be understandable without reading referenced files."""

    def test_agents_not_shell_files(self, analyzed_agents: list[InlineFile]):
        """AGENTS.md files should not be pure-link shells (links > 80% of links+content ratio)."""
        shells = []
        for f in analyzed_agents:
            if f.cross_ref_count == 0:
                continue
            # Heuristic: if more than 80% of "meaningful blocks" are links,
            # the file is a shell that requires cross-referencing to understand
            lines = f.content.split("\n")
            non_empty = [l for l in lines if l.strip() and not l.strip().startswith("```")]
            link_lines = [l for l in non_empty if "[" in l and "](" in l]
            if len(non_empty) > 3 and len(link_lines) / len(non_empty) > 0.5:
                shells.append((f, len(link_lines), len(non_empty)))

        if shells:
            report = "\n  - ".join([
                f"{str(f.path)} → {links}/{total} lines are links ({links/total*100:.0f}%)"
                for f, links, total in shells
            ])
            pytest.fail(
                f"{len(shells)} AGENTS.md files are >50% links (link-shell anti-pattern):\n"
                f"  - {report}\n\n"
                f"These files require navigation to understand. Inline the essential content."
            )

    def test_agents_have_summary_or_s_tight(self, analyzed_agents: list[InlineFile]):
        """AGENTS.md should have at least one of: S-TIGHT header, Summary section, or Purpose line."""
        missing = [
            f for f in analyzed_agents
            if not f.has_s_tight and "purpose" not in f.content[:500].lower()
        ]
        if missing:
            names = "\n  - ".join([str(f.path) for f in missing])
            pytest.fail(
                f"{len(missing)}/{len(analyzed_agents)} AGENTS.md files lack both "
                f"[S-TIGHT] header and purpose statement:\n  - {names}\n\n"
                f"A model reading this file cannot determine its purpose without "
                f"reading further or following links."
            )


class TestWorkshopVaultSplit:
    """Workshop and vault AGENTS.md files should both be inline-decomposable."""

    def test_workshop_agents_compliant(self, workshop_agents: list[InlineFile]):
        """All workshop AGENTS.md files must have LOD headers."""
        failures = [f for f in workshop_agents if not f.has_lod]
        assert len(failures) == 0, (
            f"{len(failures)} workshop AGENTS.md files missing LOD headers:\n  "
            + "\n  - ".join(str(f.path) for f in failures)
        )

    def test_vault_agents_compliant(self, vault_agents: list[InlineFile]):
        """All vault AGENTS.md files must have LOD headers."""
        failures = [f for f in vault_agents if not f.has_lod]
        assert len(failures) == 0, (
            f"{len(failures)} vault AGENTS.md files missing LOD headers:\n  "
            + "\n  - ".join(str(f.path) for f in failures)
        )


class TestLinearScriptPresence:
    """Skills that serve <32K models must provide linear (flat) scripts."""

    def test_skill_has_linear_directory(self, analyzed_skills: list[InlineFile]):
        """SKILL.md files above 4KB should have a linear/ directory."""
        results = []
        for f in analyzed_skills:
            if f.size_bytes < 4000:
                continue  # Small enough to be its own linear script
            linear_dir = f.path.parent / "linear"
            if not linear_dir.exists() or not list(linear_dir.glob("*.md")):
                results.append(f)

        if results:
            names = "\n  - ".join([f"{str(f.path)} ({f.size_bytes}B)" for f in results])
            pytest.fail(
                f"{len(results)} SKILL.md files >4KB without linear/ scripts:\n  - {names}\n\n"
                f"Create ./linear/ directory with flat, self-contained task scripts "
                f"for low-capacity models."
            )

    def test_linear_scripts_are_flat(self, analyzed_skills: list[InlineFile]):
        """Linear scripts should be self-contained (no cross-references)."""
        violations = []
        for f in analyzed_skills:
            linear_dir = f.path.parent / "linear"
            if not linear_dir.exists():
                continue
            for script in linear_dir.glob("*.md"):
                content = script.read_text(encoding="utf-8")
                refs = 0
                for line in content.split("\n"):
                    if "](" in line and not line.strip().startswith("http"):
                        refs += 1
                if refs > 3:  # Allow a few (e.g., reference to itself)
                    violations.append((script, refs))

        if violations:
            report = "\n  - ".join([
                f"{str(s)} → {refs} cross-refs (linear scripts should have ≤3)"
                for s, refs in violations
            ])
            pytest.fail(
                f"{len(violations)} linear scripts have >3 cross-references:\n  - {report}\n\n"
                f"Linear scripts must be flat and self-contained. Inline the referenced content."
            )
