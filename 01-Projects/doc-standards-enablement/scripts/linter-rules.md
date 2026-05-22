# Linter Rules for doc-standards v2.4
# ──────────────────────────────────────────────────────────────────────────
# This file defines the frontmatter schema for the Obsidian Linter plugin.
# Install the plugin from: https://github.com/platers/obsidian-linter
# Then import these rules.
#
# For now, enforcement is via the pre-commit git hook:
#   personal-vault/.git/hooks/pre-commit
# Which runs:
#   workshop/01-Projects/doc-standards-enablement/scripts/validate-frontmatter.sh
# ──────────────────────────────────────────────────────────────────────────

## FOCUS.md Schema

Required fields on ALL FOCUS.md files:

| Field       | Type    | Values                                              | Default          |
|-------------|---------|-----------------------------------------------------|------------------|
| name        | string  | (free text, matches project folder name)            | (folder name)    |
| summary     | string  | (one-line current state)                            | "Project setup required" |
| status      | enum    | active, blocked, ready, complete, paused, abandoned | active           |
| phase       | string  | (free text, e.g. "Phase 2: Implementation")          | "Phase 1: Setup" |
| progress    | integer | 0-100                                               | 10               |
| tracked     | boolean | true, false                                         | true             |

Validation rules:
- name: Must not be empty. Should match the project folder name.
- summary: Must not be empty. One sentence describing current state.
- status: Must be one of: active, blocked, ready, complete, paused, abandoned
- progress: Must be integer between 0 and 100
- tracked: Must be true or false (absent treated as true)

## PLAN.md Schema

Required fields on ALL PLAN.md files:

| Field       | Type    | Values                                              | Default          |
|-------------|---------|-----------------------------------------------------|------------------|
| name        | string  | (free text, matches project folder name)            | (folder name)    |
| phase       | string  | (free text, current phase name)                     | "Phase 1: Setup" |
| progress    | integer | 0-100 (average of completed items)                  | 0                |

## WORKBENCH.md Schema

Required fields on ALL WORKBENCH.md files:

| Field       | Type    | Values                                     | Default          |
|-------------|---------|--------------------------------------------|------------------|
| workbench   | boolean | true                                       | true             |
| updated     | date    | YYYY-MM-DD                                 | (current date)   |
| project     | string  | (free text, matches project folder name)   | (folder name)    |

## Folder Structure Rules

Every project in 01-Projects/ must contain:
- FOCUS.md (with valid frontmatter)
- PLAN.md (with valid frontmatter)
- AGENTS.md (with routing table)
- README.md (with project overview)
- WORKBENCH.md (with frontmatter)
- Overview.md (progress dashboard)
- threads/{project-name}/ (prompt thread home)
- threads/{project-name}/0-THREAD.md (thread definition)
- journal/ (session notes)
- refined-agents/ (versioned agent specs)
- status/ (point-in-time snapshots)

Forbidden:
- Standalone prompts/ folder at project root (use threads/{slug}/prompts/ instead)
- sessions/ folder (renamed to journal/ per vault-native mapping)
- .md files in project root that are not: FOCUS.md, PLAN.md, AGENTS.md, README.md, WORKBENCH.md, Overview.md

## CI/Git Hook Enforcement

The script `validate-frontmatter.sh` enforces these rules on every commit.
Run manually: ./validate-frontmatter.sh [--fix] [--path DIR]