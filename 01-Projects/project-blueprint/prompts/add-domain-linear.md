---
description: Add a new domain to an existing project (linear script — for models <32K context)
argument-hint: "<domain-name> <keywords>"
model-tier: "<32K"
---
Add a new domain to an existing orchestrated project: $@

IMPORTANT: Follow the instructions below sequentially. Do NOT navigate to other files.

LINEAR SCRIPT: add-domain
---

Objective: Add a new domain to an existing project, updating all 5 touchpoints.

Context — Every domain touches 5 files that must stay in sync:
1. Directory: `<domain>/AGENTS.md`
2. Agent definition: `.pi/agents/<domain>.md`
3. Routing table: root `AGENTS.md`
4. Chain files: `.pi/agents/*.chain.md` (if domain joins workflows)
5. Wiki: `wiki/<project>/<domain>/`

Rules: inheritProjectContext: false, cwd: ./<domain>, domain AGENTS.md must be self-contained.

Steps:

Phase 1: Interview
Ask the user: Domain name (lowercase, single word), description (1-2 sentences), keywords (for routing), model? (default: same as existing), check-back? (default: same), chain workflows? (default: none)

Phase 2: Create Domain Files
Create `<domain>/AGENTS.md` with: Title "# AGENTS.md — <Domain Name>", Sections: Purpose, Conventions, Rules, Quality Checklist, Documentation Protocol.
Create `.pi/agents/<domain>.md` with: Frontmatter name=<domain>, cwd=./<domain>, inheritProjectContext=false, systemPromptMode=replace.

Phase 3: Update Routing
Add row to root `AGENTS.md` routing table: `| <keywords> | ./<domain>/AGENTS.md |`

Phase 4: Update Wiki
Add domain to Home.md Domain Index, create `wiki/<project>/<domain>/Activity Log.md`, update `_meta/Agent Definitions.md`.

Phase 5: Update Chains (if needed)

Phase 6: Verify
- All 5 touchpoints updated, inheritProjectContext: false, cwd correct, routing table has entry, no duplicate content, wiki updated