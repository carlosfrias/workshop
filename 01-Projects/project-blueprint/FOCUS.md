# Current Focus — project-blueprint

**Thread:** [threads/project-blueprint/0-THREAD.md](threads/project-blueprint/0-THREAD.md)
**Status:** active
**Last session:** 2026-05-18 — Post-completion AGENTS architecture implemented, vault project deployed

## [S-TIGHT]

Post-completion architecture fully implemented across agents, skills, and templates. Vault project scaffolded with domains, wiki, and routing. Next: pi install verification and Library UX design.

## Active work

1. **pi install verification** — Test that `pi install` registers all three agents, skills, prompts correctly
2. **Library UX design** — How to surface completed threads proactively (TUI overlay? message? command?)
3. **Version bump** — package.json at 1.2.1; needs bump for post-completion feature addition

## Session handoff

- Post-completion feature implemented: 2 agents, 1 skill, 1 template, thread structure extended
- Vault project deployed at `personal-vault/01-Projects/project-blueprint/` with full doc-standards structure
- auto-documenter synced between project-blueprint and decompose-execute-verify packages (conflict resolved)
- Workshop executor at `workshop/01-Projects/project-blueprint/` — pointer to code workspace

## Blocked / needs decision

- pi install test needs clean package state
- Library UX pattern — TBD
- Auto-invoke vs. manual-invoke for post-completion-architect — TBD

## Next agent joining

1. Read `AGENTS.md` for domain routing
2. Read this file for current focus
3. Read `threads/project-blueprint/0-THREAD.md` for intent arc
