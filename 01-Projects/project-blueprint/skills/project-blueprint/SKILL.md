---
name: project-blueprint
description: Set up and manage orchestrated projects with domain routing, agent definitions, and self-documenting wikis.
license: MIT
compatibility: pi-coding-agent with pi-subagents, pi-intercom, pi-keyword-router, find-skill, librarian, and decompose-execute-verify packages
version: "0.1.0"
author: "Trading Laboratory"
---

# Orchestrated Project — Skill Manifest

## [S-TIGHT]

Decomposed skill for project setup and domain management. Low-capacity models: read this manifest (~3KB), then load ONLY the sub-file matching your task. All sub-files live in this directory with relative paths.

---

## [LOD: Low] Architecture Summary

1. **Structural routing** — The routing table lives in the root `AGENTS.md`. Any harness that discovers `AGENTS.md` files can follow it.
2. **Self-contained domains** — Each domain folder has exactly one `AGENTS.md` containing all conventions, rules, quality checks, and instructions.
3. **`inheritProjectContext: false`** — Sub-agents discover context independently via `cwd` walk.

### Token Budget Target

| Role | Tokens | Content |
|------|--------|---------|
| Orchestrator (permanent) | ~1.2KB | Identity + routing table only |
| Sub-agent (ephemeral) | ~4-5KB | Full domain context, loaded once, released on completion |

---

## [LOD: Low] Task Routing

When a task matches one of these operations, read ONLY the corresponding file. Do not load the full skill.

| Task keywords | Read this file | Size |
|--------------|---------------|------|
| setup, create, new project, initialize, scaffold, bootstrap | `./setup.md` | ~12KB |
| add domain, new domain, create domain | `./domain-management.md` § Add | ~10KB |
| list domains, show domains, what domains | `./domain-management.md` § List | ~10KB |
| rename domain, change domain name | `./domain-management.md` § Rename | ~10KB |
| remove domain, delete domain, archive domain | `./domain-management.md` § Remove | ~10KB |
| refine AGENTS, post-completion, golden path, learning loop, distill session | `./post-completion.md` | ~8KB |
| consolidate wiki, migrate wiki, fix wiki layout | `./wiki-integrate.md` | ~5KB |
| extract domain, export domain, split domain | `./domain-extract.md` | ~5KB |
| verify, check, checklist, quality, management check | `./checklists.md` | ~2KB |

---

## [LOD: Medium] Sub-File Index

| File | Purpose | Sections |
|------|---------|----------|
| `setup.md` | Full project creation walkthrough | Phases 1-10, Critical Rules, Templates, References |
| `domain-management.md` | Add, list, rename, remove domains | Sync Checklist, Add, List, Rename, Remove |
| `post-completion.md` | Transform session artifacts into optimized AGENTS files | Phases 1-5, Quality Gates, Merge Protocol |
| `wiki-integrate.md` | Consolidate scattered wiki content | When to Use, Interview, Steps, Output, Rules |
| `domain-extract.md` | Extract domain as standalone package | When to Use, Interview, Steps, Output, Rules |
| `checklists.md` | All verification checklists | Setup verify, Management verify, Critical Rules |
