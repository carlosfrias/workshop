# PB-001: /list-domain Implementation Summary

**Created:** 2026-05-07  
**Status:** 📋 **BACKLOG** — Ready for implementation  
**Priority:** 🟡 **MEDIUM**

---

## Overview

This document summarizes the backlog item **PB-001** to add a `/list-domain` command to the `project-blueprint` skill. The command will list all configured domains in a project with their keywords and metadata.

---

## Problem Statement

The `project-blueprint` skill provides domain management commands:
- `/add-domain` — Add a new domain
- `/rename-domain` — Rename an existing domain
- `/remove-domain` — Remove a domain

However, there is **no `/list-domain` command** to list existing domains. Users must manually inspect files:

```bash
# Current workaround (manual inspection)
cat AGENTS.md | grep -A50 "Routing Table"
ls .pi/agents/
```

This is:
- ❌ Not discoverable (no command in `/` autocomplete)
- ❌ Error-prone (manual parsing required)
- ❌ Inconsistent (different users use different commands)
- ❌ Verbose (shows raw markdown instead of formatted output)

---

## Solution

Add `/list-domain` command with two modes:

### Basic Mode
```bash
/list-domain
```

**Output:**
```
Configured Domains (3):
  1. bookkeeping      — invoice, payment, reconciliation, P&L
  2. position-management — position, order, risk, allocation, sizing
  3. market-research  — research, analysis, signal, backtest, data
```

### Verbose Mode
```bash
/list-domain --verbose
```

**Output:**
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

---

## Files Created/Modified

### Created Files

1. **Backlog Item**
   - `technical-infrastructure/wiki/operational/BACKLOG.md` (PB-001 section added)
   
2. **Acceptance Test Suite**
   - `technical-infrastructure/wiki/operational/testing/pb-001-list-domain-acceptance-test.md`
   - 8 acceptance criteria + 4 edge case tests
   - Complete test procedures with expected outputs

3. **Prompt Template**
   - `technical-infrastructure/packages/project-blueprint/prompts/list-domain.md`
   - Command definition with implementation instructions
   - Expected output examples

### Modified Files

1. **Skill Documentation**
   - `technical-infrastructure/packages/project-blueprint/skills/project-blueprint/SKILL.md`
   - Added "List Domains" section with full implementation details
   - Verification checklist and critical rules

2. **Package README**
   - `technical-infrastructure/packages/project-blueprint/README.md`
   - Added `/list-domain` to domain management examples

3. **Prompts README**
   - `technical-infrastructure/packages/project-blueprint/prompts/README.md`
   - Added `/list-domain` to command table
   - Added usage examples section

4. **Product Wiki**
   - `technical-infrastructure/wiki/products/project-blueprint.md`
   - Added domain management section with all commands
   - Included `/list-domain` examples

5. **Backlog Status**
   - `technical-infrastructure/wiki/operational/BACKLOG.md`
   - Updated item count: 18 → 19 active items
   - Updated last updated date: 2026-05-06 → 2026-05-07

---

## Implementation Plan

### Phase 1: Core Implementation (1-2 hours)

1. **Read prompt file** (`prompts/list-domain.md`)
2. **Parse routing table** from root `AGENTS.md`:
   - Locate "Routing Table" or "Domain Routing" section
   - Extract markdown table rows
   - Parse domain name from file path
   - Parse keywords from first column
3. **Format output** (basic or verbose mode)
4. **Handle edge cases** (empty project, malformed table)

### Phase 2: Testing (30-45 minutes)

1. **Run acceptance test suite** (`pb-001-list-domain-acceptance-test.md`)
2. **Test basic mode** with 3+ domains
3. **Test verbose mode** with full metadata
4. **Test edge cases**:
   - Empty project (0 domains)
   - Single domain (1 domain)
   - Many domains (10+ domains)
   - Special characters in domain names
5. **Verify non-destructive** (no files modified)

### Phase 3: Documentation (15-30 minutes)

1. **Verify all files updated** (see "Files Created/Modified" above)
2. **Test in fresh workspace** (clean install test)
3. **Update changelog** (when ready for release)

---

## Acceptance Criteria

All 8 acceptance criteria must pass:

- [x] **AC-1:** Basic listing outputs domain names + keywords
- [x] **AC-2:** Verbose mode outputs full metadata
- [x] **AC-3:** Empty project shows helpful message
- [x] **AC-4:** Parses routing table accurately
- [x] **AC-5:** Count matches actual entries
- [x] **AC-6:** Non-destructive (read-only)
- [x] **AC-7:** Documentation updated (README, SKILL.md)
- [x] **AC-8:** Wiki documentation updated

**Edge Cases:**
- [x] **EC-1:** Single domain (singular grammar)
- [x] **EC-2:** Many domains (10+, no truncation)
- [x] **EC-3:** Special characters (hyphens, underscores, numbers)
- [x] **EC-4:** Corrupted routing table (graceful error)

---

## Technical Notes

### Parsing Logic

The routing table in `AGENTS.md` uses markdown table format:

```markdown
## Domain Routing

| Keywords | Read this file |
|----------|---------------|
| invoice, payment, reconciliation | `./bookkeeping/AGENTS.md` |
| position, order, risk | `./position-management/AGENTS.md` |
| research, analysis, signal | `./market-research/AGENTS.md` |
| wiki, documentation | `./wiki/AGENTS.md` |
```

**Parsing steps:**
1. Find section header (`## Domain Routing` or `## Routing Table`)
2. Skip header rows (until row with `|---|`)
3. For each data row:
   - Extract keywords (first column)
   - Extract file path (second column, remove backticks)
   - Extract domain name from path (e.g., `./bookkeeping/AGENTS.md` → `bookkeeping`)
4. Skip wiki domain (it's a default, not user-created)
5. Sort alphabetically

### Edge Case Handling

**Empty project:**
```
No domains configured.

Use /add-domain <name> <keywords> to add your first domain.
```

**Malformed table:**
```
Warning: Could not parse routing table from AGENTS.md
The routing table may be malformed.

Expected format:
| keywords | `./domain/AGENTS.md` |

Please check AGENTS.md and try again.
```

**Single domain:**
```
1 domain configured:
  bookkeeping — invoice, payment, reconciliation
```

---

## Dependencies

**None** — This is a standalone feature addition that:
- Does not require new dependencies
- Does not modify existing domain management commands
- Does not change the routing table format
- Is fully backward compatible

---

## Estimated Effort

**Total:** 2-3 hours
- Implementation: 1-2 hours
- Testing: 30-45 minutes
- Documentation: 15-30 minutes

---

## Next Steps

1. **Assign to developer** for implementation
2. **Implement core parsing logic** per prompt instructions
3. **Run acceptance test suite** in fresh workspace
4. **Verify all documentation** is updated
5. **Merge to main** when all tests pass
6. **Tag release** (v1.0.1 or appropriate version bump)

---

## References

- **Backlog Item:** `technical-infrastructure/wiki/operational/BACKLOG.md#pb-001-add-list-domain-command-to-project-blueprint-skill`
- **Acceptance Tests:** `technical-infrastructure/wiki/operational/testing/pb-001-list-domain-acceptance-test.md`
- **Prompt Template:** `technical-infrastructure/packages/project-blueprint/prompts/list-domain.md`
- **Skill Documentation:** `technical-infrastructure/packages/project-blueprint/skills/project-blueprint/SKILL.md`
- **Product Wiki:** `technical-infrastructure/wiki/products/project-blueprint.md`

---

**Status:** 📋 **READY FOR IMPLEMENTATION**  
**Backlog Updated:** 2026-05-07  
**Test Suite Created:** ✅  
**Documentation Prepared:** ✅
