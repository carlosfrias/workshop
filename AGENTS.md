# Workshop — Root Router Manifest

**Purpose:** Execution workspace for all code, scripts, scrapers, data processing, infrastructure, and build systems.  
**Counterpart:** `../personal-vault/` — documentation and knowledge management.

## [S-TIGHT]

Unified routing hub. Detects domain from prompt keywords, routes to section files in `routing/`, loads only the section and phase file needed. Do not load all sections at once.

---

## Routing Sections

| Section | File | Size | Load When |
|---------|------|------|-----------|
| Identity & Phases | [routing/identity-and-phases.md](routing/identity-and-phases.md) | ~2KB | Every session — workspace purpose + phase loading |
| Model Routing | [routing/model-routing.md](routing/model-routing.md) | ~1.2KB | Need to pick a model or understand execution tiers |
| Project Map | [routing/project-map.md](routing/project-map.md) | ~3KB | Routing to a specific project AGENTS.md |
| Domain Routing | [routing/domain-routing.md](routing/domain-routing.md) | ~1.5KB | Routing to Trading areas or Infrastructure resources |
| Execution & Skills | [routing/execution-and-skills.md](routing/execution-and-skills.md) | ~2.5KB | Starting work — execution pattern + mandatory skill auto-load |
| Workspace Structure | [routing/workspace-structure.md](routing/workspace-structure.md) | ~4KB | Need directory layout, cross-references, discovery path |

---

## Load Directive

| Model Tier | Max Context | Load These |
|------------|-------------|------------|
| Low local (<4K) | 4K | Identity & Phases ONLY. Then load 1 more section based on task. |
| Medium local (~8K) | 8K | Identity & Phases + 1-2 task-relevant sections. |
| High local (~32K) | 32K | Identity & Phases + up to 4 sections. |
| Cloud (>32K) | 32K+ | Load all sections if needed. Prefer targeted sections. |

---

## Quick Task Routing

| What are you trying to do? | Load these sections |
|----------------------------|---------------------|
| Start a new session | identity-and-phases.md |
| Pick which model to use | model-routing.md |
| Route to a project | project-map.md |
| Route to a Trading area | domain-routing.md |
| Begin execution | execution-and-skills.md → then phase files |
| Edit/create any .md file | execution-and-skills.md (skill auto-load is MANDATORY) |
| Navigate the workspace | workspace-structure.md |
| Find cross-reference paths | workspace-structure.md |

---

## Discovery Path

```
1. carlos-desktop/AGENTS.md              ← Pick workspace
2. workshop/AGENTS.md                    ← THIS FILE — pick section
3. routing/{section}.md                  ← Load only what you need
4. workshop/01-Projects/{project}/AGENTS.md ← Project rules
   OR workshop/02-Areas/Trading/{area}/AGENTS.md ← Domain rules
5. personal-vault/01-Projects/{project}/   ← Documentation, session history
```

---

*Last updated: 2026-05-21 — decomposed monolithic AGENTS.md into routing/ section files*