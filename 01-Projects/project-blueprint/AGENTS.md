# AGENTS.md — Project Blueprint (Workshop)

**Documentation home:** `../../personal-vault/01-Projects/project-blueprint/`  
**Code workspace:** `./`  
**Workshop root:** `./` (this directory)

## [S-TIGHT]

Execution side of Project Blueprint. Scripts, data, and build tooling. All planning and documentation lives in personal-vault. The authoritative code lives in workshop — this workspace is for scripts and data processing that support the project.

## Tech Stack

| Component | Technology | Entry Point |
|-----------|-----------|-------------|
| Package build/install | Node.js / npm | `../../workshop/technical-infrastructure/packages/project-blueprint/package.json` |
| Scaffold scripts | Bash | `scripts/` (extend as needed) |

## Directory Structure

```
project-blueprint/
├── AGENTS.md              ← YOU ARE HERE
├── scripts/               # Automation and build scripts
└── data/                  # Structured data and artifacts
```

## Entry Points

| Task | Command |
|------|---------|
| pi install test | `cd ../../workshop/technical-infrastructure/packages/project-blueprint && pi install .` |
| Scaffold a new project | `bash scripts/scaffold-project.sh <project-name>` |

## Conventions

- **Credentials:** NEVER hardcode. Use environment variables or `.env` (gitignored).
- **Bash scripts:** Shebang `#!/usr/bin/env bash`, `set -euo pipefail`
- **Data format:** JSON in `data/`. One file per data source.

## Must Never

- Commit `.env` files, auth tokens, or passwords
- Store documentation here (docs live in personal-vault)
- Modify code in workshop from this workspace (use implementation domain)

## Cross-Reference

| Need | Go Here |
|------|---------|
| Project overview, deliverables | `../../personal-vault/01-Projects/project-blueprint/README.md` |
| Current state, priorities | `../../personal-vault/01-Projects/project-blueprint/FOCUS.md` |
| Human workspace | `../../personal-vault/01-Projects/project-blueprint/WORKBENCH.md` |
| Prompt history | `../../personal-vault/01-Projects/project-blueprint/threads/project-blueprint/0-THREAD.md` |
| Code implementation | `../../workshop/technical-infrastructure/packages/project-blueprint/` |

---

*Last updated: 2026-05-18*
