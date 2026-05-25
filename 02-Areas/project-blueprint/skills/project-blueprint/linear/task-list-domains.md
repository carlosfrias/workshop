# Linear Script: list-domains (Project Blueprint)

**Target Tier:** <8K (Low Capacity)
**Token Budget:** ~1KB
**Objective:** List all domains in an existing orchestrated project. Read-only — no files modified.

## Context
Domains are defined in the root `AGENTS.md` routing table. Each row maps keywords to `./<domain>/AGENTS.md`. The wiki domain entry is NOT a user domain.

## Steps

### Phase 1: Read Routing Table
Read root `AGENTS.md`. Find the "Domain Routing" or "Routing Table" section. Extract each row:
- Keywords (first column)
- Domain path (second column, e.g., `./bookkeeping/AGENTS.md` → domain name: `bookkeeping`)

Skip the wiki entry (not a user domain).

### Phase 2: Format Output
**Basic mode:**
```
Configured Domains (N):
  1. domain1 — keywords
  2. domain2 — keywords
```

**Verbose mode** (if user asks):
```
domain1
  Keywords: ...
  Agent: .pi/agents/domain1.md
  Directory: ./domain1/
  Context: ./domain1/AGENTS.md
```

### Phase 3: Handle Edge Cases
- 0 domains → suggest `/add-domain`
- 1 domain → "1 domain configured"
- Malformed table → show error, don't crash

### Phase 4: Offer Next Steps
After listing, suggest:
- `/add-domain <name>` to add a new domain
- `/rename-domain <old> <new>` to rename
- `/remove-domain <name>` to remove

## Verify
- [ ] Domain count matches routing table entries (excluding wiki)
- [ ] Domains listed alphabetically
- [ ] No files modified (read-only)
- [ ] Keywords display correctly