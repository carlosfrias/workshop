---
name: project-blueprint/domain-management
description: Add, list, rename, and remove domains in orchestrated projects.
---

# Domain Management — Post-Setup Operations

After a project has been set up, domains may need to be added, renamed, or removed. Each of these operations touches multiple files that must stay in sync. Follow the steps below precisely to maintain consistency with the structural routing architecture.


## [S-TIGHT]

Domain lifecycle operations: add, list, rename, and remove domains. Every operation must update all 5 touchpoints (directory, agent def, routing table, chains, wiki).
## Management Principle: The Sync Checklist

Every domain management operation must update **all five** of these touchpoints. Missing any one breaks the routing:

| Touchpoint | File | What It Contains |
|-----------|------|------------------|
| 1. Domain directory | `./<domain>/` | Folder + `AGENTS.md` with all domain context |
| 2. Agent definition | `.pi/agents/<domain>.md` | `name`, `cwd: ./<domain>`, system prompt |
| 3. Routing table | Root `AGENTS.md` | Keywords → `./<domain>/AGENTS.md` entry |
| 4. Chain files | `.pi/agents/*.chain.md` | Any chains that reference this domain's agent |
| 5. Wiki | `wiki/<project>/` | Structure map, agent docs, sample prompts |

After every management operation, verify the token budget and confirm no broken references.

---

## Add a Domain

Adds a new domain to an existing project. Does not modify existing domains.

### Add: Interview

Ask the user:
1. **Domain name** — lowercase, single word preferred (e.g., `compliance`)
2. **Domain description** — 1-2 sentences
3. **Domain keywords** — for routing table (e.g., "regulations, compliance, audit")
4. **Who uses this domain?** — e.g., "compliance officers"
5. **Model** — which model for this domain's agent? (default: same as existing sub-agents)
6. **Check-back?** — Should this domain's agent check back via intercom? (default: same as existing agents)
7. **Chain workflows?** — Does this domain participate in any multi-step workflows with other domains?

### Add: Steps

1. **Create `./<domain>/AGENTS.md`** — Use the `AGENTS-domain.md` template from `./templates/`. Customize with domain name, description, conventions, rules, quality checklist, common mistakes.
2. **Create `.pi/agents/<domain>.md`** — Use the `agent-domain.md` template. Set `name: <domain>`, `cwd: ./<domain>`, `inheritProjectContext: false`. Choose model and tools.
3. **Update root `AGENTS.md` routing table** — Add a row to the routing table: `| <keywords> | \`./<domain>/AGENTS.md\` |`
4. **Create chain files if needed** — If the domain joins multi-step workflows, create or update chain files in `.pi/agents/`. Use the `chain-basic.md` template.
5. **Update the wiki** — Add the new domain to: home page Domain Index table, `_meta/Agent Definitions` page, `_meta/Sample Prompts` page. Create `wiki/<project>/<domain>/Activity Log.md` using the `wiki-activity-log.md` template.
6. **Verify** — Confirm all five touchpoints are consistent. Run `ls -la` on the domain folder and `.pi/agents/`. Check the routing table renders correctly.

##Loo# Add: Critical Rules

- The new domain's `AGENTS.md` must be fully self-contained (no supplementary files).
- The agent definition must have `inheritProjectContext: false` and `cwd: ./<domain>`.
- Never duplicate an existing domain's content into the new domain's `AGENTS.md`.
- If the domain shares conventions with another domain, state that in the routing references section of the new `AGENTS.md`, not by copying content.

---

## List Domains

Lists all configured domains in the project with their keywords and metadata. This is a **read-only** operation — no files are modified.

### List: Usage

**Basic listing** (domain names + keywords):
```
/list-domain
```

**Verbose listing** (full metadata):
```
/list-domain --verbose
```

### List: Implementation Steps

1. **Parse the routing table** from root `AGENTS.md`:
   - Locate the "Routing Table" or "Domain Routing" section
   - Extract each row from the markdown table (format: `| keywords | \`./<domain>/AGENTS.md\` |`)
   - Parse domain name from the file path (e.g., `./bookkeeping/AGENTS.md` → `bookkeeping`)
   - Parse keywords from the first column
   - Skip the default wiki domain entry (it's not a user-created domain)

2. **Format the output**:
   - Show total count of domains at the top
   - List domains alphabetically for consistency
   - **Basic mode**: Show numbered list with domain name and keywords
   - **Verbose mode**: Show full metadata for each domain:
     - Domain name
     - Keywords
     - Directory path (`./<domain>/`)
     - Agent definition file (`.pi/agents/<domain>.md`)
     - Domain context file (`./<domain>/AGENTS.md`)

3. **Handle edge cases**:
   - **Empty project** (0 domains): Show helpful message suggesting `/add-domain`
   - **Single domain**: Use singular grammar ("1 domain configured")
   - **Malformed routing table**: Show helpful error message, don't crash

### List: Expected Output

**Basic mode:**
```
Configured Domains (3):
  1. bookkeeping      — invoice, payment, reconciliation, P&L
  2. position-management — position, order, risk, allocation, sizing
  3. market-research  — research, analysis, signal, backtest, data
```

**Verbose mode:**
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

**Empty project:**
```
No domains configured.

Use /add-domain <name> <keywords> to add your first domain.
```

### List: Verification Checklist

After listing domains, verify:
- [ ] Domain count matches actual routing table entries (excluding wiki default)
- [ ] All domains listed alphabetically
- [ ] Keywords displayed correctly (no parsing errors)
- [ ] In verbose mode, all file paths are accurate
- [ ] No files were modified (read-only operation)
- [ ] Helpful follow-up suggestions offered (`/add-domain`, `/rename-domain`, `/remove-domain`)

### List: Critical Rules

- **Read-only operation**: Never modify files when listing
- **Parse accurately**: Handle markdown table format correctly (pipes, backticks, quotes)
- **Exclude wiki default**: The wiki domain entry is not a user-created domain
- **Helpful errors**: If routing table is malformed, guide the user to fix it
- **Offer next steps**: After listing, suggest domain management commands

---

## Rename a Domain

Renames an existing domain across all five touchpoints. The old name ceases to exist.

### Rename: Interview

Ask the user:
1. **Old domain name** — Which domain to rename?
2. **New domain name** — What should it be called now?
3. **New keywords** — Do the routing table keywords need updating? (e.g., if renaming `bookkeeping` to `accounting`, keywords might change from "trade logging, reconciliation" to "financial records, ledgers, accounting")
4. **New description** — Does the domain description need updating, or just the name?

### Rename: Steps

1. **Rename the directory** — `mv ./<old> ./<new>`
2. **Update `./<new>/AGENTS.md`** — Change the title and any internal references from the old name to the new name.
3. **Rename the agent definition** — `mv .pi/agents/<old>.md .pi/agents/<new>.md`. Update the frontmatter: `name: <new>`, `cwd: ./<new>`. Update the system prompt body to reflect the new name.
4. **Update the root `AGENTS.md` routing table** — Change the keywords and/or path in the routing table row: `| <new-keywords> | \`./<new>/AGENTS.md\` |`. Remove the old row.
5. **Update chain files** — Search all `.pi/agents/*.chain.md` files for references to the old domain name (agent names, `cwd` paths). Replace with the new name.
6. **Update the wiki** — Rename `wiki/<project>/<old>/` to `wiki/<project>/<new>/`. Update: home page Domain Index table, `_meta/Agent Definitions` page, `_meta/Sample Prompts` page, any cross-references.
7. **Verify** — Run `ls -la` on `./<new>/` and `.pi/agents/`. Confirm routing table points to `./<new>/AGENTS.md`. Grep for the old name across the project root to confirm no stale references remain.

### Rename: Critical Rules

- Never rename just the folder without updating all five touchpoints. A folder rename alone breaks the agent `cwd`, routing table, chains, and wiki.
- After renaming, the old name must not appear anywhere in the project (except in session/history files).
- Chain files are the most likely place for stale references — always check them.
- If the domain had sample prompts in the wiki, update those too (users copy-paste them).

---

## Remove a Domain

Removes a domain entirely from the project. The folder, agent definition, routing entry, chains, and wiki references are all deleted or updated.

### Remove: Confirmation

Before removing, confirm with the user:
1. **Which domain?** — Name of the domain to remove.
2. **Should chain files be removed?** — If any chains only involve this domain's agent, they should be removed. If the domain participates in chains with other domains, those chains need updating (not removal).
3. **Should wiki content be removed?** — Remove the domain from wiki pages, or leave historical documentation?
4. **Has the domain's data been preserved?** — If the domain folder contains data files (not just `AGENTS.md`), confirm the user wants to delete them.

### Remove: Steps

1. **Remove the directory** — `rm -rf ./<domain>/` (after confirming data preservation if needed).
2. **Remove the agent definition** — `rm .pi/agents/<domain>.md`.
3. **Remove chain files** — Delete any chains that only involve this domain. For chains where this domain is one step among others, remove the step that references this domain's agent.
4. **Update the root `AGENTS.md` routing table** — Remove the row for this domain from the routing table.
5. **Update the wiki** — Remove the domain's wiki directory: `wiki/<project>/<domain>/`. Remove the domain from: home page Domain Index table, `_meta/Agent Definitions` page, `_meta/Sample Prompts` page.
6. **Verify** — Run `ls -la` on the project root and `.pi/agents/`. Confirm the routing table has no entry for the removed domain. Grep for the domain name to check for stale references.

### Remove: Critical Rules

- Always confirm before deleting. Removing a domain is destructive and cannot be undone without version control.
- Chain file updates are critical — a chain that references a removed agent will fail at runtime.
- The routing table must not contain entries pointing to deleted folders. A stale routing entry causes the orchestrator to attempt reading a nonexistent file.
- After removal, recalculate the token budget (the orchestrator's permanent load shrinks if the routing table gets shorter).

---

## Management Verification Checklist

After any add/rename/remove operation, run through this checklist:

- [ ] Every domain folder has exactly one `AGENTS.md` (no supplementary files)
- [ ] Every domain has an agent definition in `.pi/agents/` with `inheritProjectContext: false` and correct `cwd`
- [ ] The routing table in root `AGENTS.md` has exactly one row per domain (no extras, no missing)
- [ ] All chain files reference agents that exist
- [ ] Wiki home page reflects domain-centric layout (domains at root, `_meta/` for reference)
- [ ] Wiki Domain Index table lists all current domains with accurate links
- [ ] Each domain has its own wiki directory at wiki root with Activity Log.md
- [ ] `_meta/` reference pages are accurate and up to date
- [ ] Sample prompts reference current domain names
- [ ] Grep for any stale old names (after rename/remove) — none should remain
- [ ] Token budget recalculated and reported
