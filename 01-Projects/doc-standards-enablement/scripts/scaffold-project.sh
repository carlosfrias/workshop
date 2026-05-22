#!/usr/bin/env bash
# scaffold-project.sh — Create a new project in both documentation and execution workspaces
#
# Usage:
#   ./scaffold-project.sh <project-name>            # Create both sides
#   ./scaffold-project.sh --dry-run <project-name>  # Preview only
#   ./scaffold-project.sh --help                    # This message
#
# Creates:
#   personal-vault/01-Projects/{name}/
#     README.md, AGENTS.md, FOCUS.md, WORKBENCH.md, Overview.md
#     threads/{name}/0-THREAD.md, threads/{name}/prompts/001-initial-setup.md
#     journal/, refined-agents/, status/ (empty dirs)
#
#   workshop/01-Projects/{name}/
#     AGENTS.md
#     scripts/, data/ (empty dirs)
#
# Complies with doc-standards TOPOLOGY v2.3.0

set -euo pipefail

# ── Help ──────────────────────────────────────────────────────────────────

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  sed -n '2,21p' "$0"
  exit 0
fi

# ── Args ──────────────────────────────────────────────────────────────────

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
  shift
fi

PROJECT_NAME="${1:-}"
if [[ -z "$PROJECT_NAME" ]]; then
  echo "ERROR: Project name required"
  echo "Usage: $0 [--dry-run] <project-name>"
  exit 1
fi

if [[ ! "$PROJECT_NAME" =~ ^[a-z0-9-]+$ ]]; then
  echo "ERROR: Project name must be kebab-case (a-z, 0-9, hyphens only)"
  exit 1
fi

# ── Paths ─────────────────────────────────────────────────────────────────

# Resolve workspace roots relative to this script's location
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSHOP_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
CARLOS_DESKTOP="$(cd "$WORKSHOP_ROOT/.." && pwd)"
VAULT_PROJECTS="$CARLOS_DESKTOP/personal-vault/01-Projects"
WORKSHOP_PROJECTS="$WORKSHOP_ROOT/01-Projects"

VAULT_PROJECT="$VAULT_PROJECTS/$PROJECT_NAME"
WORKSHOP_PROJECT="$WORKSHOP_PROJECTS/$PROJECT_NAME"
THREAD_DIR="$VAULT_PROJECT/threads/$PROJECT_NAME"
PROMPTS_DIR="$THREAD_DIR/prompts"

# ── Safety check ──────────────────────────────────────────────────────────

if [[ -d "$VAULT_PROJECT" && -d "$WORKSHOP_PROJECT" ]]; then
  echo "✅ Project '$PROJECT_NAME' already exists in both workspaces — nothing to do"
  echo "   Docs:  $VAULT_PROJECT"
  echo "   Code:  $WORKSHOP_PROJECT"
  exit 0
fi

# ── Functions ─────────────────────────────────────────────────────────────

write_file() {
  local path="$1" content="$2"
  if [[ "$DRY_RUN" == true ]]; then
    echo "  [DRY-RUN] Would write: $path"
    return
  fi
  if [[ -f "$path" ]]; then
    echo "  ⏭️  Skipped (exists): $path"
    return
  fi
  mkdir -p "$(dirname "$path")"
  echo "$content" > "$path"
  echo "  ✅ Created: $path"
}

write_empty_dir() {
  local path="$1"
  if [[ "$DRY_RUN" == true ]]; then
    echo "  [DRY-RUN] Would create dir: $path"
    return
  fi
  if [[ -d "$path" ]]; then
    echo "  ⏭️  Skipped (exists): $path"
    return
  fi
  mkdir -p "$path"
  touch "$path/.gitkeep"
  echo "  ✅ Created: $path/"
}

# ── NOW ───────────────────────────────────────────────────────────────────

NOW=$(date +%Y-%m-%d)
DISPLAY_NAME=$(echo "$PROJECT_NAME" | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)}1')

echo ""
echo "════════════════════════════════════════════════"
echo "  Scaffolding: $DISPLAY_NAME"
echo "════════════════════════════════════════════════"
echo ""

# ═══════════════════════════════════════════════════════════════════════
#  PERSONAL-VAULT (Documentation)
# ═══════════════════════════════════════════════════════════════════════

echo "── Documentation (personal-vault) ──"

# README.md
write_file "$VAULT_PROJECT/README.md" "---
prompt_thread: active
project: $PROJECT_NAME
created: $NOW
---

# $DISPLAY_NAME

Prompt capture is active. See [threads/$PROJECT_NAME/0-THREAD.md](threads/$PROJECT_NAME/0-THREAD.md) for the prompt thread.

**Overview:** [[01-Projects/$PROJECT_NAME/Overview\|Overview.md]] — Progress dashboard and session history
**Workbench:** [[01-Projects/$PROJECT_NAME/WORKBENCH\|🔨 Workbench]] — Current working notes

## What

<!-- Describe what this project is building or solving -->

## Deliverables

<!-- List concrete outputs -->

## Where

- **Project Home:** \`personal-vault/01-Projects/$PROJECT_NAME/\`
- **🔨 Workbench:** [[01-Projects/$PROJECT_NAME/WORKBENCH\|WORKBENCH.md]]
- **Overview:** [[01-Projects/$PROJECT_NAME/Overview\|Overview.md]]
- **Thread:** [[01-Projects/$PROJECT_NAME/threads/$PROJECT_NAME/0-THREAD\|0-THREAD]]

**Executor workspace:** \`workshop/01-Projects/$PROJECT_NAME/\` — code, scripts, data
"

# AGENTS.md
write_file "$VAULT_PROJECT/AGENTS.md" "# AGENTS.md — $DISPLAY_NAME

## [S-TIGHT]

<!-- One-line summary of this project -->

## Domain Routing

| Keywords | Action |
|----------|--------|
| <!-- keyword, pattern, topic --> | This project |

## Conventions

- All dates: \`YYYY-MM-DD\`
- Wikilinks: path-based from vault root

## Must Always

- Update \`FOCUS.md\` at end of every session
- Append session notes to \`journal/\`
- Capture prompts in \`threads/$PROJECT_NAME/prompts/\`
- Keep WORKBENCH.md readable (migrate solid content to structural files)

## Key Files

| File | Purpose |
|------|---------|
| \`WORKBENCH.md\` | Human workspace — current thinking |
| \`README.md\` | Project overview and thread status |
| \`FOCUS.md\` | AI handoff — state, priorities, blockers |
| \`threads/$PROJECT_NAME/0-THREAD.md\` | Full prompt history and intent arc |

## Executor Workspace

Code, scripts, and data live in the **workshop**:

\`\`\`
../../workshop/01-Projects/$PROJECT_NAME/
├── AGENTS.md           # Tech stack, entry points, code conventions
├── scripts/            # Automation scripts
└── data/               # Structured data
\`\`\`

## Discovery Order

1. \`WORKBENCH.md\` — human's current context
2. \`AGENTS.md\` (this file) — conventions, routing, rules
3. \`FOCUS.md\` — current state, active work, session handoff
4. \`README.md\` — project overview and deliverables
5. \`threads/$PROJECT_NAME/0-THREAD.md\` — full prompt history
"

# FOCUS.md
write_file "$VAULT_PROJECT/FOCUS.md" "---
name: $DISPLAY_NAME
summary: Project scaffolded — define deliverables and priorities
status: active
phase: \"Phase 1: Setup\"
progress: 20
tracked: true
---

# Current Focus

**Thread:** [threads/$PROJECT_NAME/0-THREAD.md](threads/$PROJECT_NAME/0-THREAD.md)
**Last session:** $NOW — Project scaffolded

## Active work

1. **Project setup** — ✅ Complete. Project scaffolded with doc-standards structure.
2. **<!-- Next priority -->** — 🔜 NEXT

## Session handoff

- Project created with full doc-standards structure (v2.3.0)
- Documentation in personal-vault, code in workshop
- Prompt 001 captured in thread

## Blocked / needs decision

<!-- Add blockers here -->

## Next agent joining

1. Read \`WORKBENCH.md\` for human context
2. Read \`AGENTS.md\` for routing and conventions
3. Read this file for current state
"

# PLAN.md
write_file "$VAULT_PROJECT/PLAN.md" "---
name: $DISPLAY_NAME
phase: \"Phase 1: Setup\"
progress: 20
tracked: true
---

# Plan — $DISPLAY_NAME

## Phase 1: Setup
- [x] 1.1 Project scaffolded with doc-standards structure
- [ ] 1.2 Define deliverables and priorities
- [ ] 1.3 First working session
"
write_file "$VAULT_PROJECT/WORKBENCH.md" "---
workbench: true
updated: $NOW
project: $PROJECT_NAME
---

# Workbench — $DISPLAY_NAME

> Desk for this project. Notes, half-thoughts, current focus. Migrate to structural files when solid.

---

## 🔨 Current work

<!-- What are you actively thinking about or working on right now? -->

- [x] Project scaffolded — README, AGENTS, FOCUS, thread, WORKBENCH created
- [ ] <!-- Next task -->

---

## 💭 Working notes

<!-- Brain dumps, half-thoughts, sketches -->

---

## 📋 To sort

<!-- Stuff that needs a home -->

---

## ✅ Recently done

- ~~Project scaffolded~~ — full doc-standards structure, both workspaces
"

# Overview.md
write_file "$VAULT_PROJECT/Overview.md" "---
prompt_thread: active
thread: threads/$PROJECT_NAME/0-THREAD.md
tags:
  - project
---

# $DISPLAY_NAME

## Progress at a Glance

| Phase | Status | Completion |
|-------|--------|------------|
| **0. Setup** | ✅ Complete | Project scaffolded, both workspaces |
| **1. <!-- Phase name -->** | Not started | <!-- Description --> |

## Quick Links

| Resource | Purpose |
|----------|---------|
| [[01-Projects/$PROJECT_NAME/WORKBENCH\\|🔨 Workbench]] | Your desk — current thinking and working notes |
| [[01-Projects/$PROJECT_NAME/AGENTS\\|AGENTS.md]] | AI routing, conventions, rules |
| [[01-Projects/$PROJECT_NAME/FOCUS]] | Current state and handoff |
| [[01-Projects/$PROJECT_NAME/README]] | Project overview and deliverables |
| [[01-Projects/$PROJECT_NAME/threads/$PROJECT_NAME/0-THREAD\\|Thread]] | Prompt history and intent arc |

## Session History

| Date | Session | Summary |
|------|---------|---------|
| $NOW | Scaffold | Project created with full doc-standards structure |
"

# Thread
write_file "$THREAD_DIR/0-THREAD.md" "# Thread: $PROJECT_NAME

**Project:** [[01-Projects/$PROJECT_NAME|$PROJECT_NAME]] or [README.md](../../README.md)
**Status:** active
**Created:** $NOW
**Last updated:** $NOW

<!-- Project mission statement -->

## Prompt Sequence

| #   | Date     | Type    | Description          | File                                             |
| --- | -------- | ------- | -------------------- | ------------------------------------------------ |
| 1   | $NOW     | initial | Project scaffold     | [001-initial-setup.md](prompts/001-initial-setup.md) |

## Evolution

<!-- How the project scope and understanding evolved over time -->

## Aggregated Lessons

<!-- Key learnings applicable beyond this project -->
"

# First prompt
write_file "$PROMPTS_DIR/001-initial-setup.md" "# Prompt 001 — Initial Setup

**Date:** $NOW
**Type:** initial
**Thread:** [0-THREAD.md](../0-THREAD.md)

---

## Prompt

Create the $DISPLAY_NAME project with full doc-standards structure (v2.3.0). Documentation in personal-vault, code in workshop.

---

## Decision

<!-- Key decisions made during initial setup -->

## Output

- Project scaffolded at \`personal-vault/01-Projects/$PROJECT_NAME/\`
- Workshop counterpart at \`workshop/01-Projects/$PROJECT_NAME/\`
- Full doc-standards structure: README, AGENTS, FOCUS, WORKBENCH, Overview, thread, prompts, journal, status
"

# Empty dirs
write_empty_dir "$VAULT_PROJECT/journal"
write_empty_dir "$VAULT_PROJECT/refined-agents"
write_empty_dir "$VAULT_PROJECT/status"

# ═══════════════════════════════════════════════════════════════════════
#  WORKSHOP (Code)
# ═══════════════════════════════════════════════════════════════════════

echo ""
echo "── Execution (workshop) ──"

write_file "$WORKSHOP_PROJECT/AGENTS.md" "# AGENTS.md — $DISPLAY_NAME (Workshop)

**Documentation home:** \`../../personal-vault/01-Projects/$PROJECT_NAME/\`  
**Workshop root:** \`./\` (this directory)

## [S-TIGHT]

Execution side of the $DISPLAY_NAME project. Contains scripts, data processing, and build tooling. All planning and session documentation lives in personal-vault.

## Tech Stack

| Component | Technology | Entry Point |
|-----------|-----------|-------------|
| <!-- Component --> | <!-- Tech --> | <!-- Script path --> |

## Directory Structure

\`\`\`
$PROJECT_NAME/
├── AGENTS.md              ← YOU ARE HERE
├── scripts/               # Automation and build scripts
└── data/                  # Structured data and artifacts
\`\`\`

## Entry Points

| Task | Command |
|------|---------|
| <!-- Task --> | <!-- Command --> |

## Conventions

- **Credentials:** NEVER hardcode. Use environment variables or \`.env\` (gitignored).
- **Python:** Target 3.14. Use \`.venv\` in project root if needed.
- **Data format:** JSON in \`data/\`. One file per data source, named with date.

## Must Never

- Commit \`.env\` files, auth tokens, or passwords
- Store documentation here (docs live in personal-vault)

## Cross-Reference

| Need | Go Here |
|------|---------|
| Project overview, deliverables | \`../../personal-vault/01-Projects/$PROJECT_NAME/README.md\` |
| Current state, priorities | \`../../personal-vault/01-Projects/$PROJECT_NAME/FOCUS.md\` |
| Human workspace | \`../../personal-vault/01-Projects/$PROJECT_NAME/WORKBENCH.md\` |
| Prompt history | \`../../personal-vault/01-Projects/$PROJECT_NAME/threads/$PROJECT_NAME/0-THREAD.md\` |

---

*Last updated: $NOW*
"

write_empty_dir "$WORKSHOP_PROJECT/scripts"
write_empty_dir "$WORKSHOP_PROJECT/data"

# ═══════════════════════════════════════════════════════════════════════
#  ROUTING UPDATE REMINDER
# ═══════════════════════════════════════════════════════════════════════

echo ""
echo "────────────────────────────────────────────"
echo "  ⚠️  MANUAL STEP: Update routing tables"
echo "────────────────────────────────────────────"
echo ""
echo "  Add to personal-vault/AGENTS.md routing table:"
echo "    | <keywords> | 01-Projects/$PROJECT_NAME/AGENTS.md |"
echo ""
echo "  Add to workshop/AGENTS.md workshop map:"
echo "    | <keywords> | ./01-Projects/$PROJECT_NAME/AGENTS.md |"
echo ""
echo "════════════════════════════════════════════════"
echo "  ✅ Done — $DISPLAY_NAME scaffolded"
echo "  Docs:  $VAULT_PROJECT"
echo "  Code:  $WORKSHOP_PROJECT"
echo "════════════════════════════════════════════════"
