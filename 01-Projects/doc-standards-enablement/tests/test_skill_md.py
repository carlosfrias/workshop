"""Test SKILL.md-specific inline decomposition properties.

SKILL.md files are skill manifests that must work for both:
- <32K models (via linear/ flat scripts)
- ≥32K models (via decomposed sections)

From validation: linear scripts enable low-capacity models to follow
instructions correctly where decomposed approach causes improvisation.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from .test_helpers import InlineFile


class TestSkillManifestStructure:
    """SKILL.md must have a proper manifest structure for tier-routing."""

    def test_skill_has_frontmatter(self, analyzed_skills: list[InlineFile]):
        """Every SKILL.md should have YAML frontmatter with a name."""
        failures = []
        for f in analyzed_skills:
            if not f.content.strip().startswith("---"):
                failures.append(f)

        if failures:
            names = "\n  - ".join([str(f.path) for f in failures])
            pytest.fail(
                f"{len(failures)}/{len(analyzed_skills)} SKILL.md files missing "
                f"YAML frontmatter:\n  - {names}"
            )

    def test_skill_has_lod_loading_directive(self, analyzed_skills: list[InlineFile]):
        """SKILL.md must have a loading directive table for model tiers."""
        missing = [f for f in analyzed_skills if not f.has_tier_directive]
        if missing:
            names = "\n  - ".join([str(f.path) for f in missing])
            pytest.fail(
                f"{len(missing)}/{len(analyzed_skills)} SKILL.md files missing "
                f"tier-based loading directive:\n  - {names}"
            )

    def test_skill_lists_sections(self, analyzed_skills: list[InlineFile]):
        """SKILL.md should list its decomposed sections in a table."""
        failures = []
        for f in analyzed_skills:
            content = f.content
            has_section_table = "| Section | File |" in content or \
                                "| Section | File | Size |" in content
            if not has_section_table:
                failures.append(f)

        if failures:
            names = "\n  - ".join([str(f.path) for f in failures])
            pytest.fail(
                f"{len(failures)}/{len(analyzed_skills)} SKILL.md files missing "
                f"section listing table:\n  - {names}"
            )


class TestSkillManifestJson:
    """Skills with MANIFEST.json enable programmatic section loading."""

    def test_skill_has_manifest_json(self, analyzed_skills: list[InlineFile]):
        """Skills with >3 sections should have a MANIFEST.json."""
        missing = []
        for f in analyzed_skills:
            if len(f.lod_sections) < 3:
                continue  # Small enough without JSON
            manifest = f.path.parent / "MANIFEST.json"
            if not manifest.exists():
                missing.append(f)

        if missing:
            names = "\n  - ".join([str(f.path) for f in missing])
            pytest.fail(
                f"{len(missing)} SKILL.md files with >3 LOD sections but no "
                f"MANIFEST.json:\n  - {names}\n\n"
                f"Create MANIFEST.json with section metadata for programmatic loading."
            )

    def test_manifest_json_valid(self, analyzed_skills: list[InlineFile]):
        """MANIFEST.json files must be valid JSON with required fields."""
        invalid = []
        for f in analyzed_skills:
            manifest_path = f.path.parent / "MANIFEST.json"
            if not manifest_path.exists():
                continue
            try:
                data = json.loads(manifest_path.read_text())
                # Check required fields
                if "skill" not in data:
                    invalid.append((f, "missing 'skill' field"))
                elif "sections" not in data:
                    invalid.append((f, "missing 'sections' field"))
                elif "task_to_sections" not in data:
                    invalid.append((f, "missing 'task_to_sections' field"))
            except json.JSONDecodeError as e:
                invalid.append((f, f"invalid JSON: {e}"))

        if invalid:
            report = "\n  - ".join([
                f"{str(f.path)} → {reason}" for f, reason in invalid
            ])
            pytest.fail(
                f"{len(invalid)} MANIFEST.json files invalid:\n  - {report}"
            )


class TestSkillSizeEstimates:
    """SKILL.md size estimates must be accurate (±20%)."""

    def test_size_estimates_within_tolerance(self, analyzed_skills: list[InlineFile]):
        """Size estimates in section tables should match actual file sizes."""
        import re

        mismatches = []
        for f in analyzed_skills:
            skill_dir = f.path.parent
            # Find ~XKB estimates and verify
            pattern = r'\|\s*(?:\[.*?\]\(([^)]+)\))\s*\|\s*~(\d+(?:\.\d+)?)KB\s*\|'
            for match in re.finditer(pattern, f.content):
                filename = match.group(1)
                estimated_kb = float(match.group(2))
                actual_path = skill_dir / filename
                if actual_path.exists():
                    actual_kb = actual_path.stat().st_size / 1024
                    tolerance = estimated_kb * 0.20
                    if abs(actual_kb - estimated_kb) > tolerance:
                        mismatches.append((
                            f, filename, estimated_kb, round(actual_kb, 1)
                        ))

        if mismatches:
            report = "\n  - ".join([
                f"{str(f.path)} → {name}: est ~{est}KB, actual ~{act}KB (diff {abs(est-act):.1f}KB)"
                for f, name, est, act in mismatches
            ])
            pytest.fail(
                f"{len(mismatches)} size estimate(s) deviate >20% from actual:\n  - {report}\n\n"
                f"Update size estimates to reflect actual file sizes."
            )


class TestLinearScriptAvailability:
    """Skills must provide linear scripts for <32K models."""

    def test_skill_linear_dir_exists(self, analyzed_skills: list[InlineFile]):
        """Skills >4KB must have a linear/ directory with task scripts."""
        missing = []
        for f in analyzed_skills:
            if f.size_bytes <= 4000:
                continue  # Small enough as-is
            linear_dir = f.path.parent / "linear"
            if not linear_dir.exists():
                missing.append(f)
            elif not list(linear_dir.glob("*.md")):
                missing.append(f)

        if missing:
            names = "\n  - ".join([
                f"{str(f.path)} ({f.size_bytes}B)"
                for f in missing
            ])
            pytest.fail(
                f"{len(missing)} SKILL.md files >4KB without linear/ task scripts:\n"
                f"  - {names}\n\n"
                f"Create ./linear/ directory with flat, self-contained scripts "
                f"for low-capacity models. Follow the project-blueprint pattern: "
                f"one file per task with all templates inlined."
            )

    def test_linear_scripts_have_verification_gate(self, analyzed_skills: list[InlineFile]):
        """Linear scripts must end with a verification gate checklist."""
        missing_gate = []
        for f in analyzed_skills:
            linear_dir = f.path.parent / "linear"
            if not linear_dir.exists():
                continue
            for script in linear_dir.glob("*.md"):
                content = script.read_text(encoding="utf-8")
                if "Verification" not in content and "verification" not in content.lower():
                    missing_gate.append((f, script))

        if missing_gate:
            report = "\n  - ".join([
                f"{str(s)} (for {str(f.path).split('/')[-1]})"
                for f, s in missing_gate
            ])
            pytest.fail(
                f"{len(missing_gate)} linear scripts missing verification gate:\n"
                f"  - {report}\n\n"
                f"Add a '## Verification Gate' section with a checklist."
            )

    def test_linear_scripts_have_token_budget(self, analyzed_skills: list[InlineFile]):
        """Linear scripts should declare their token budget."""
        missing_budget = []
        for f in analyzed_skills:
            linear_dir = f.path.parent / "linear"
            if not linear_dir.exists():
                continue
            for script in linear_dir.glob("*.md"):
                content = script.read_text(encoding="utf-8")
                if "Token Budget" not in content and "Target Tier" not in content:
                    missing_budget.append((f, script))

        if missing_budget:
            report = "\n  - ".join([
                f"{str(s)} ({len(s.read_text().split())} words)"
                for f, s in missing_budget
            ])
            pytest.fail(
                f"{len(missing_budget)} linear scripts missing token budget declaration:\n"
                f"  - {report}\n\n"
                f"Add '**Target Tier:** <8K (Low Capacity)' or similar."
            )
