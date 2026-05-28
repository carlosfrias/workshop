"""Pytest fixtures: file discovery for inline decomposition testing."""

from __future__ import annotations

from pathlib import Path
from typing import Generator

import pytest

from .test_helpers import InlineFile


# ── Root paths ──────────────────────────────────────────────────────────────

WORKSHOP_ROOT = Path(__file__).resolve().parents[4]  # .../carlos-desktop/workshop/
VAULT_ROOT = WORKSHOP_ROOT.parent / "personal-vault"
CARLOS_DESKTOP_ROOT = WORKSHOP_ROOT.parent  # .../carlos-desktop/
SKILLS_ROOT = Path.home() / ".pi" / "agent" / "git" / "github.com"


# ── Discovery ───────────────────────────────────────────────────────────────

def _discover_agents_md(root: Path, max_depth: int = 5) -> list[Path]:
    """Recursively find all AGENTS.md files under root."""
    if not root.exists():
        return []
    return sorted(root.rglob("AGENTS.md"))[:50]  # cap at 50


def _discover_skill_md(root: Path, max_depth: int = 8) -> list[Path]:
    """Find all SKILL.md files under skill directories."""
    if not root.exists():
        return []
    return sorted(root.rglob("SKILL.md"))[:50]


def _discover_workshop_agents() -> list[Path]:
    """Workshop: carlos-desktop/AGENTS.md + workshop/AGENTS.md + all project AGENTS.md."""
    files = []
    # Root carlos-desktop AGENTS.md
    root_agents = CARLOS_DESKTOP_ROOT / "AGENTS.md"
    if root_agents.exists():
        files.append(root_agents)
    # Workshop AGENTS.md and all sub-project AGENTS.md
    for f in _discover_agents_md(WORKSHOP_ROOT):
        # Exclude legacy merged workspace
        if "ai-trading-workspace" in str(f):
            continue
        files.append(f)
    # Also check workshop/02-Areas/
    areas = WORKSHOP_ROOT / "02-Areas"
    if areas.exists():
        for f in _discover_agents_md(areas):
            if "ai-trading-workspace" in str(f):
                continue
            files.append(f)
    # workshop/03-Resources/
    resources = WORKSHOP_ROOT / "03-Resources"
    if resources.exists():
        for f in _discover_agents_md(resources):
            if "ai-trading-workspace" in str(f):
                continue
            files.append(f)
    return files


def _discover_vault_agents() -> list[Path]:
    """Personal vault AGENTS.md files."""
    return _discover_agents_md(VAULT_ROOT)


def _discover_skill_manifests() -> list[Path]:
    """All SKILL.md files from installed skill packages."""
    files = []
    # git-cloned skills
    files.extend(_discover_skill_md(SKILLS_ROOT))
    # npm-installed skills
    npm_skills = Path.home() / ".pi" / "agent" / "npm" / "node_modules"
    if npm_skills.exists():
        for skill_dir in npm_skills.iterdir():
            if skill_dir.is_dir():
                skill_md = skill_dir / "skills"
                if skill_md.exists():
                    files.extend(_discover_skill_md(skill_md))
    return files


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def all_agents_md() -> list[Path]:
    """All AGENTS.md files across workshop and vault."""
    files = _discover_workshop_agents() + _discover_vault_agents()
    # deduplicate
    seen = set()
    unique = []
    for f in files:
        resolved = str(f.resolve())
        if resolved not in seen:
            seen.add(resolved)
            unique.append(f)
    return unique


@pytest.fixture(scope="session")
def all_skill_md() -> list[Path]:
    """All SKILL.md files from installed skill packages."""
    return _discover_skill_manifests()


@pytest.fixture(scope="session")
def analyzed_agents(all_agents_md: list[Path]) -> list[InlineFile]:
    """Pre-analyzed AGENTS.md files."""
    results = []
    for path in all_agents_md:
        f = InlineFile.from_file(path)
        if f is not None:
            results.append(f)
    return results


@pytest.fixture(scope="session")
def analyzed_skills(all_skill_md: list[Path]) -> list[InlineFile]:
    """Pre-analyzed SKILL.md files."""
    results = []
    for path in all_skill_md:
        f = InlineFile.from_file(path)
        if f is not None:
            results.append(f)
    return results


# ── Utility fixtures ────────────────────────────────────────────────────────

@pytest.fixture
def workshop_agents(analyzed_agents: list[InlineFile]) -> list[InlineFile]:
    """Workshop-side AGENTS.md files only."""
    return [
        f for f in analyzed_agents
        if "workshop" in str(f.path) or "carlos-desktop/AGENTS.md" in str(f.path)
    ]


@pytest.fixture
def vault_agents(analyzed_agents: list[InlineFile]) -> list[InlineFile]:
    """Vault-side AGENTS.md files only."""
    return [
        f for f in analyzed_agents
        if "personal-vault" in str(f.path)
    ]
