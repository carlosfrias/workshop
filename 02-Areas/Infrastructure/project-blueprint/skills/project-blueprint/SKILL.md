---
name: project-blueprint
description: Set up and manage orchestrated projects with domain routing, agent definitions, and self-documenting wikis.
license: MIT
compatibility: pi-coding-agent with pi-subagents, pi-intercom, pi-keyword-router, find-skill, librarian, and decompose-execute-verify packages
version: "0.1.0"
author: "Trading Laboratory"
distribution_gate: "Every pi package must complete commit→push→pi update. Workshop paths and symlinks are scaffolding only. See checklists.md § Distribution Gate."
---

# Orchestrated Project — Skill Manifest

## [S-TIGHT]

Tier-routed skill for project setup and domain management. Models <32K context: load the LINEAR script matching your task from `./linear/` — do NOT read this manifest further. Models ≥32K context: read this manifest, then load ONLY the sub-file matching your task.

---

## [LOD: Low] Architecture Summary

1. **Structural routing** — The routing table lives in the root `AGENTS.md`. Any harness that discovers `AGENTS.md` files can follow it.
2. **Self-contained domains** — Each domain folder has exactly one `AGENTS.md` containing all conventions, rules, quality checks, and instructions.
3. **`inheritProjectContext: false`** — Sub-agents discover context independently via `cwd` walk.

### Critical Architecture Rule: Agent vs Skill Deployment

Pi processes **4 resource types** from packages: `extensions`, `skills`, `prompts`, `themes`.
**Agents and chains are NOT processed.** They require manual deployment to the filesystem.

| Resource | Discovery Path | Package.json Key | Managed by `pi update`? |
|----------|---------------|-----------------|----------------------|
| **Skill** | `pi.skills` in package.json → auto-discovered from git clone | `pi.skills` | ✅ Yes |
| **Extension** | `pi.extensions` in package.json → auto-discovered | `pi.extensions` | ✅ Yes |
| **Prompt** | `pi.prompts` in package.json → auto-discovered | `pi.prompts` | ✅ Yes |
| **Theme** | `pi.themes` in package.json → auto-discovered | `pi.themes` | ✅ Yes |
| **Agent** | `~/.pi/agent/agents/*.md` ONLY — real files, never symlinks | *Not supported* | ❌ No |
| **Chain** | `~/.pi/agent/chains/*.md` ONLY — real files, never symlinks | *Not supported* | ❌ No |

**Never use `pi.agents` or `pi.chains` in package.json.** These fields are vestigial and are silently ignored by pi. Including them creates false confidence.

**Agent deployment rule:** After `pi update`, copy agent `.md` files from the git clone to `~/.pi/agent/agents/` as real files (not symlinks). Symlinks break when paths change.

**Skill deployment rule:** Declare in `pi.skills` and pi discovers them automatically from the git clone.

### Token Budget Target

| Role | Tokens | Content |
|------|--------|---------|
| Orchestrator (permanent) | ~1.2KB | Identity + routing table only |
| Sub-agent (ephemeral) | ~4-5KB | Full domain context, loaded once, released on completion |

---

## [LOD: Low] Tier-Based Routing

**Models with <32K context window MUST use linear scripts.** These are flat, self-contained files with no cross-references. Read the linear script that matches your task — it contains everything you need.

| Task keywords | Linear script (<32K models) | Decomposed file (≥32K models) |
|--------------|---------------------------|--------------------------|
| setup, create, new project, initialize, scaffold | `./linear/task-create-project.md` | `./setup.md` |
| add domain, new domain, create domain | `./linear/task-add-domain.md` | `./domain-management.md` § Add |
| list domains, show domains | `./linear/task-list-domains.md` | `./domain-management.md` § List |
| remove domain, delete domain | `./linear/task-remove-domain.md` | `./domain-management.md` § Remove |
| refine AGENTS, post-completion, golden path | `./linear/task-refine-agents.md` | `./post-completion.md` |
| rename domain, change domain name | *Not yet available as linear* | `./domain-management.md` § Rename |
| consolidate wiki, migrate wiki | *Not yet available as linear* | `./wiki-integrate.md` |
| extract domain, export domain | *Not yet available as linear* | `./domain-extract.md` |
| verify, check, checklist | *Not yet available as linear* | `./checklists.md` |

**Why two tracks?** Validation (Phase 6, doc-standards) proved that a 4B model with a linear script outperforms an 8B model with the decomposed approach. Cross-reference navigation overhead exhausts low-capacity context windows before task execution begins. See: `doc-standards/wiki/reference/linear-scripts/validation-results.md`

**Tier detection:** Run `check-model-tier.sh` from `local-model-pilot` to determine whether to use linear or decomposed scripts.

---

## [LOD: Low] Task Routing (Decomposed — ≥32K Models Only)

When a task matches one of these operations, read ONLY the corresponding file. Do not load the full skill.

| Task keywords | Read this file | Size |
|--------------|---------------|------|
| setup, create, new project, initialize, scaffold, bootstrap | `./setup.md` | ~12KB |
| add domain, new domain, create domain | `./domain-management.md` § Add | ~10KB |
| list domains, show domains, what domains | `./domain-management.md` § List | ~10KB |
| rename domain, change domain name | `./domain-management.md` § Rename | ~10KB |
| remove domain, delete domain, archive domain | `./domain-management.md` § Remove | ~10KB |
| refine AGENTS, post-completion, golden path, learning loop, distill session, close session | `./post-completion.md` | ~8KB |
| consolidate wiki, migrate wiki, fix wiki layout | `./wiki-integrate.md` | ~5KB |
| extract domain, export domain, split domain | `./domain-extract.md` | ~5KB |
| verify, check, checklist, quality, management check | `./checklists.md` | ~2KB |

---

## [LOD: Medium] Sub-File Index

| File | Purpose | Sections |
|------|---------|----------|
| `setup.md` | Full project creation walkthrough (≥32K) | Phases 1-10, Critical Rules, Templates, References |
| `domain-management.md` | Add, list, rename, remove domains (≥32K) | Sync Checklist, Add, List, Rename, Remove |
| `post-completion.md` | Transform session artifacts into optimized AGENTS files (≥32K) | Phases 1-5, Quality Gates, Merge Protocol |
| `wiki-integrate.md` | Consolidate scattered wiki content (≥32K) | When to Use, Interview, Steps, Output, Rules |
| `domain-extract.md` | Extract domain as standalone package (≥32K) | When to Use, Interview, Steps, Output, Rules |
| `checklists.md` | All verification checklists (≥32K) | Setup verify, Management verify, Critical Rules |
| `linear/task-create-project.md` | Flat script: create project (<32K) | Context, Steps, Templates, Verification Gate |
| `linear/task-add-domain.md` | Flat script: add domain (<32K) | Context, Steps, Templates, Verification Gate |
| `linear/task-list-domains.md` | Flat script: list domains (<32K) | Context, Steps, Output, Verification Gate |
| `linear/task-remove-domain.md` | Flat script: remove domain (<32K) | Context, Steps, Critical Rules, Verification Gate |
| `linear/task-refine-agents.md` | Flat script: refine AGENTS (<32K) | Context, Steps, Critical Rules, Verification Gate |
