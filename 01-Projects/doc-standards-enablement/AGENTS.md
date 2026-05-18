# AGENTS.md — doc-standards-enablement (Workshop)

**Documentation home:** `../../personal-vault/01-Projects/doc-standards-enablement/`  
**Workshop root:** `./` (this directory)

## [S-TIGHT]

Tooling and scripts for the doc-standards enablement project. Contains the project scaffold script, validation tools, and build automation. The doc-standards skill source code lives in its own package repo at `../../workshop/technical-infrastructure/packages/doc-standards/`.

## Tech Stack

| Component | Technology | Entry Point |
|-----------|-----------|-------------|
| Project scaffolding | Bash | `scripts/scaffold-project.sh` |
| Link validation | Python 3.14 | `validation/check-links.py` (to create) |
| Doc-standards skill | Markdown | `../../workshop/technical-infrastructure/packages/doc-standards/skills/doc-standards/` |

## Directory Structure

```
doc-standards-enablement/
├── AGENTS.md              ← YOU ARE HERE
├── scripts/
│   └── scaffold-project.sh    # Creates new project in both workspaces
├── validation/
│   └── check-links.py         # Validates cross-workspace links (to create)
```

## Entry Points

| Task | Command |
|------|---------|
| Scaffold new project | `./scripts/scaffold-project.sh <project-name>` |
| Validate cross-references | `python3 validation/check-links.py` (to create) |

## Conventions

- All scripts use bash (scaffolding) or Python 3.14 (validation)
- Idempotent: scripts must not overwrite existing files
- Dry-run: support `--dry-run` flag for preview
- Help: support `--help` flag

## Cross-Reference

| Need | Go Here |
|------|---------|
| Project overview, deliverables | `../../personal-vault/01-Projects/doc-standards-enablement/README.md` |
| Current state, priorities | `../../personal-vault/01-Projects/doc-standards-enablement/FOCUS.md` |
| Prompt history | `../../personal-vault/01-Projects/doc-standards-enablement/threads/doc-standards-enablement/0-THREAD.md` |
| Doc-standards skill source | `../../workshop/technical-infrastructure/packages/doc-standards/skills/doc-standards/` |

---

*Last updated: 2026-05-17*
