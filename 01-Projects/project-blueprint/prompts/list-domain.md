---
description: List all configured domains in this project with keywords and metadata
argument-hint: "[--verbose]"
---
List all configured domains in this project.

Read the skill at ~/.pi/agent/skills/project-blueprint/SKILL.md for full instructions, specifically the "List Domains" section.

**Basic Usage:**
- Run without arguments to show domain names and keywords
- Run with `--verbose` flag to show full metadata (directory paths, agent files, domain context files)

**Implementation Steps:**

1. **Parse the routing table** from root `AGENTS.md`:
   - Locate the "Routing Table" or "Domain Routing" section
   - Extract each row from the markdown table
   - Parse domain name, keywords, and file path from each row
   - Skip the default wiki domain entry (not a user-created domain)

2. **Format the output**:
   - Show total count of domains
   - List domains alphabetically
   - Display keywords for each domain
   - In verbose mode, also show:
     - Directory path
     - Agent definition file path
     - Domain context file path

3. **Handle edge cases**:
   - Empty project (0 domains): Show helpful message suggesting `/add-domain`
   - Single domain: Use singular grammar ("1 domain")
   - Malformed routing table: Show helpful error, don't crash

**Expected Output (Basic):**
```
Configured Domains (3):
  1. bookkeeping      — invoice, payment, reconciliation, P&L
  2. position-management — position, order, risk, allocation, sizing
  3. market-research  — research, analysis, signal, backtest, data
```

**Expected Output (Verbose):**
```
Configured Domains (3):

bookkeeping
  Keywords: invoice, payment, reconciliation, P&L, trade logging
  Agent: bookkeeping
  Directory: ./bookkeeping/
  Agent File: .pi/agents/bookkeeping.md
  Domain Context: ./bookkeeping/AGENTS.md

position-management
  Keywords: position, order, risk, allocation, sizing, exits
  Agent: position-management
  Directory: ./position-management/
  Agent File: .pi/agents/position-management.md
  Domain Context: ./position-management/AGENTS.md

market-research
  Keywords: research, analysis, signal, backtest, data, indicators
  Agent: market-research
  Directory: ./market-research/
  Agent File: .pi/agents/market-research.md
  Domain Context: ./market-research/AGENTS.md
```

**Before proceeding:**
- Verify you are in a project-blueprint project root (check for `AGENTS.md` and `.pi/` directory)
- If not in a project-blueprint project, inform the user

**After listing:**
- Offer to help with domain management:
  - "Use `/add-domain <name> <keywords>` to add a new domain"
  - "Use `/rename-domain <old> <new>` to rename a domain"
  - "Use `/remove-domain <name>` to remove a domain"
