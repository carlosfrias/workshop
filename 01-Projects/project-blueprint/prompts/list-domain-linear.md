---
description: List all domains in an existing project (linear script — for models <32K context)
argument-hint: "[--verbose]"
model-tier: "<32K"
---
List all domains in the current orchestrated project.

IMPORTANT: Follow the instructions below sequentially. Do NOT navigate to other files.

LINEAR SCRIPT: list-domains
---

Objective: List all domains. Read-only — no files modified.

Steps:

Phase 1: Read Routing Table
Read root `AGENTS.md`. Find the "Domain Routing" section. Extract each row: keywords (first column), domain path (second column, e.g. ./bookkeeping/AGENTS.md → domain name: bookkeeping). Skip the wiki entry (not a user domain).

Phase 2: Format Output
Basic: "Configured Domains (N): 1. domain1 — keywords 2. domain2 — keywords"
Verbose (if requested): Show full metadata per domain (keywords, agent file, directory, context file).

Phase 3: Handle Edge Cases
0 domains → suggest /add-domain. 1 domain → "1 domain configured". Malformed table → show error.

Phase 4: Offer Next Steps
Suggest: /add-domain, /rename-domain, /remove-domain.

Verify: Domain count matches routing entries (excluding wiki), alphabetical, no files modified.