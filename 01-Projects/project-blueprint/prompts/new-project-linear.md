---
description: Set up a new orchestrated project (linear script — for models <32K context)
argument-hint: "<project-description>"
model-tier: "<32K"
---
Create an orchestrated project structure for: $@

IMPORTANT: Follow the instructions below sequentially. Do NOT navigate to other files. Everything you need is inlined here.

LINEAR SCRIPT: create-project
---

Target Tier: <8K (Low Capacity)
Objective: Initialize a full orchestrated project structure (Vault + Workshop) without navigation overhead.

Context:
- Vault Root: `personal-vault/01-Projects/`
- Workshop Root: `workshop/01-Projects/`
- Core Rules: Use vault-native terms (Plan not issue, journal/ not sessions/). Two Locations Mandate: Docs in Vault, Code in Workshop. S-TIGHT headers on operational files.

Execution Steps:

Phase 1: Interview
Ask the user for: Project Name, Project Description, Domains (Name, Description, Keywords), Wiki Location (default ./wiki/), HTML Wiki? (default Yes), Models (Orchestrator, Reasoning, Fast), Intercom check-back? (default Yes)

Phase 2: Workshop Infrastructure
Create `workshop/01-Projects/<project-name>/` with: AGENTS.md (Identity + Routing Table), .pi/APPEND_SYSTEM.md, .pi/agents/<domain>.md (inheritProjectContext: false, cwd: ./<domain>), <domain>/AGENTS.md, wiki/<project-name>/

Phase 3: Vault Documentation
Create in `personal-vault/01-Projects/<project-name>/`: WORKBENCH.md, AGENTS.md, FOCUS.md, README.md, Overview.md, threads/<project-name>/0-THREAD.md

Phase 4: Wiki Content
Initialize wiki at `personal-vault/01-Projects/<project-name>/wiki/`: Home.md, <domain>/Activity Log.md, _meta/ (Architecture, Agent Definitions, Doc Standards)

Phase 5: HTML Build (If requested)
Create `wiki/<project-name>/wiki-build/` with .vitepress/config.js, package.json, README.md

Verification Gate:
1. No domain content in root AGENTS.md
2. All agent definitions have inheritProjectContext: false
3. All cwd paths correctly point to domain directories
4. S-TIGHT headers present on FOCUS.md and AGENTS.md
5. Two Locations Mandate: No docs in workshop, no code in vault
6. All files created in the correct personal-vault vs workshop paths