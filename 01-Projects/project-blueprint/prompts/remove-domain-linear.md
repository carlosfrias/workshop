---
description: Remove a domain from an existing project (linear script — for models <32K context)
argument-hint: "<domain-name>"
model-tier: "<32K"
---
Remove a domain from the current orchestrated project: $@

IMPORTANT: Follow the instructions below sequentially. Do NOT navigate to other files. REMOVING A DOMAIN IS DESTRUCTIVE.

LINEAR SCRIPT: remove-domain
---

Objective: Remove a domain entirely, updating all 5 touchpoints.

Context — Removing a domain touches the same 5 files as adding:
1. Directory: `<domain>/AGENTS.md` → DELETE
2. Agent definition: `.pi/agents/<domain>.md` → DELETE
3. Routing table: root `AGENTS.md` → REMOVE row
4. Chain files: `.pi/agents/*.chain.md` → UPDATE or DELETE
5. Wiki: `wiki/<project>/<domain>/` → DELETE

Steps:

Phase 1: Confirmation
Confirm with user: Which domain? Delete chain files? (Y/N), Delete wiki content? (Y/N), Domain has data files? (confirm deletion)

Phase 2: Remove Domain Files
Delete `./<domain>/` directory. Delete `.pi/agents/<domain>.md`.

Phase 3: Remove Chain References
Chain only involves this domain → delete chain. Domain is one step in multi-domain chain → remove that step.

Phase 4: Update Routing Table
Remove domain's row from root `AGENTS.md`.

Phase 5: Update Wiki
Remove `wiki/<project>/<domain>/`, update Home.md, _meta/Agent Definitions.md, _meta/Sample Prompts.md.

Phase 6: Verify
- Domain directory deleted, agent definition deleted, routing table has no stale entry, chains updated, wiki updated, grep for domain name shows no stale references, token budget recalculated.