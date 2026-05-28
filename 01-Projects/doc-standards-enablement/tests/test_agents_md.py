"""Test AGENTS.md-specific inline decomposition properties.

AGENTS.md files serve as entry points for both humans and AI agents.
They must be routable without exhausting context windows.
"""

from __future__ import annotations

import pytest

from .test_helpers import InlineFile


class TestSTightHeaders:
    """Every AGENTS.md must have an [S-TIGHT] summary section."""

    def test_all_agents_have_s_tight(self, analyzed_agents: list[InlineFile]):
        """S-TIGHT headers enable models to extract the essence without reading full file."""
        failures = [f for f in analyzed_agents if not f.has_s_tight]
        if failures:
            names = "\n  - ".join([str(f.path) for f in failures])
            pytest.fail(
                f"{len(failures)}/{len(analyzed_agents)} AGENTS.md files missing "
                f"[S-TIGHT] header:\n  - {names}\n\n"
                f"Add: '## [S-TIGHT]' section with a 1-3 sentence summary that "
                f"a low-capacity model can use without reading the full file."
            )


class TestTierLoadingTable:
    """AGENTS.md files with sections should specify what to load per tier."""

    def test_tier_table_maps_model_to_sections(self, analyzed_agents: list[InlineFile]):
        """Files referencing sections should have a tier→sections mapping table."""
        missing = [
            f for f in analyzed_agents
            if f.cross_ref_count >= 2 and not f.has_tier_directive
        ]
        if missing:
            names = "\n  - ".join([str(f.path) for f in missing])
            pytest.fail(
                f"{len(missing)} AGENTS.md files with ≥2 cross-references lack "
                f"tier loading directive:\n  - {names}\n\n"
                f"Add a table:\n"
                f"| Model Tier | Max Context | Load These |\n"
                f"|------------|-------------|------------|\n"
                f"| Low (<4K)  | 4K          | ...        |\n"
                f"| Medium (~8K)| 8K         | ...        |"
            )


class TestRouterFiles:
    """Router AGENTS.md files are intentional link-dense files — verify their pattern."""

    def test_router_files_are_identified(self, analyzed_agents: list[InlineFile]):
        """At least the root AGENTS.md files should be identified as routers."""
        routers = [f for f in analyzed_agents if f.is_router]
        assert len(routers) > 0, "No router files detected — check detection logic"

    def test_router_files_have_routing_table(self, analyzed_agents: list[InlineFile]):
        """Every router file must have a keyword→target routing table."""
        for f in analyzed_agents:
            if not f.is_router:
                continue
            # Router files should have a table with keyword→file mapping
            has_table = "|" in f.content and "---" in f.content
            assert has_table, (
                f"Router file {f.path} has no markdown table — "
                f"router files must have keyword→target routing tables"
            )

    def test_router_files_use_dot_slash_prefix(self, analyzed_agents: list[InlineFile]):
        """Router file links must use ./ prefix for path resolution."""
        violations = []
        for f in analyzed_agents:
            if not f.is_router:
                continue
            # Check that relative links use ./ prefix
            for link_path in f.relative_paths:
                if not link_path.startswith("./"):
                    violations.append((f, link_path))

        if violations:
            report = "\n  - ".join([
                f"{str(f.path)} → `{path}` (should be `./{path}` or `./{path.lstrip('../')}`)"
                for f, path in violations
            ])
            pytest.fail(
                f"{len(violations)} router file links missing ./ prefix:\n  - {report}"
            )


class TestAgentsSizeLimits:
    """AGENTS.md files must stay within practical size limits by tier."""

    def test_agents_under_4kb(self, analyzed_agents: list[InlineFile]):
        """AGENTS.md files should target <4KB for low-tier compatibility."""
        oversized = [f for f in analyzed_agents if f.size_bytes > 4000]
        if oversized:
            # This is informational — not all AGENTS.md files can be <4KB
            names = "\n  - ".join([
                f"{str(f.path)} ({f.size_bytes}B)"
                for f in oversized
            ])
            pytest.fail(
                f"{len(oversized)}/{len(analyzed_agents)} AGENTS.md files exceed "
                f"4KB target size:\n  - {names}\n\n"
                f"Consider decomposing into routing/ section files with tier-based loading."
            )


class TestPathResolution:
    """AGENTS.md cross-references must be resolvable."""

    def test_workshop_links_use_relative_paths(self, workshop_agents: list[InlineFile]):
        """Workshop AGENTS.md links must use relative (not absolute) paths."""
        violations = []
        for f in workshop_agents:
            for link_path in f.relative_paths:
                if link_path.startswith("/Users/") or link_path.startswith("/home/"):
                    violations.append((f, link_path))

        if violations:
            report = "\n  - ".join([
                f"{str(f.path)} → `{path}` (use relative path instead)"
                for f, path in violations
            ])
            pytest.fail(
                f"{len(violations)} absolute path references found in workshop AGENTS.md:\n"
                f"  - {report}"
            )

    def test_vault_links_use_relative_paths(self, vault_agents: list[InlineFile]):
        """Vault AGENTS.md links must use relative (not absolute) paths."""
        violations = []
        for f in vault_agents:
            for link_path in f.relative_paths:
                if link_path.startswith("/Users/") or link_path.startswith("/home/"):
                    violations.append((f, link_path))

        if violations:
            report = "\n  - ".join([
                f"{str(f.path)} → `{path}`"
                for f, path in violations
            ])
            pytest.fail(
                f"{len(violations)} absolute path references found:\n  - {report}"
            )
