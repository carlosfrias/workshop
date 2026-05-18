# PB-001: /list-domain Command — Acceptance Test Suite

**Backlog Item:** PB-001 — Add /list-domain Command to project-blueprint Skill  
**Created:** 2026-05-07  
**Test Environment:** Fresh project-blueprint test workspace  
**Test Status:** 📋 **PENDING** (backlog item not yet implemented)

---

## Test Overview

This test suite validates the `/list-domain` command for the `project-blueprint` skill. The command should list all configured domains in a project with their keywords and metadata.

**Total Tests:** 8 acceptance criteria  
**Expected Duration:** 15-20 minutes  
**Prerequisites:** 
- `project-blueprint` skill installed
- Test workspace with at least 3 domains configured

---

## Test Setup

```bash
# Create fresh test workspace
mkdir -p ~/pb-list-domain-test
cd ~/pb-list-domain-test

# Initialize git (optional but recommended)
git init

# Install project-blueprint
pi install github:carlosfrias/project-blueprint

# Set up test project with 3 domains
pi skill project-blueprint

# Interview responses (for setup):
# Project name: "Test Project"
# Project description: "Testing /list-domain command"
# Domains: 
#   1. bookkeeping — "invoice, payment, reconciliation, P&L"
#   2. position-management — "position, order, risk, allocation, sizing"
#   3. market-research — "research, analysis, signal, backtest, data"
```

---

## Acceptance Criteria Tests

### AC-1: Basic Listing

**Test:** `/list-domain` outputs domain names and keywords in readable format

**Steps:**
1. Run `/list-domain` in test workspace
2. Verify output contains all 3 domain names
3. Verify output contains keywords for each domain
4. Verify output is formatted as a numbered list

**Expected Output:**
```
Configured Domains (3):
  1. bookkeeping      — invoice, payment, reconciliation, P&L
  2. position-management — position, order, risk, allocation, sizing
  3. market-research  — research, analysis, signal, backtest, data
```

**Pass Criteria:**
- [ ] All 3 domain names appear in output
- [ ] Keywords appear for each domain
- [ ] Output is numbered and readable
- [ ] No errors or warnings

**Result:** ⬜ PASS / ⬜ FAIL  
**Notes:** _______________

---

### AC-2: Verbose Mode

**Test:** `/list-domain --verbose` outputs full metadata

**Steps:**
1. Run `/list-domain --verbose` in test workspace
2. Verify output includes directory paths
3. Verify output includes agent file paths
4. Verify output includes domain context file paths

**Expected Output:**
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

**Pass Criteria:**
- [ ] Directory paths shown for all domains
- [ ] Agent file paths shown for all domains
- [ ] Domain context file paths shown for all domains
- [ ] Keywords shown for all domains

**Result:** ⬜ PASS / ⬜ FAIL  
**Notes:** _______________

---

### AC-3: Empty Project

**Test:** Returns "No domains configured" when routing table is empty

**Steps:**
1. Create fresh workspace: `mkdir ~/pb-empty-test && cd ~/pb-empty-test`
2. Install project-blueprint: `pi install github:carlosfrias/project-blueprint`
3. Do NOT run setup wizard
4. Run `/list-domain`

**Expected Output:**
```
No domains configured.

Use /add-domain <name> <keywords> to add your first domain.
```

**Pass Criteria:**
- [ ] Output indicates no domains exist
- [ ] Helpful message suggests adding a domain
- [ ] No errors or stack traces

**Result:** ⬜ PASS / ⬜ FAIL  
**Notes:** _______________

---

### AC-4: Parsing Accuracy

**Test:** Correctly parses routing table from root `AGENTS.md`

**Steps:**
1. Manually edit root `AGENTS.md` routing table to add a test domain
2. Add domain with unusual formatting (extra spaces, special characters)
3. Run `/list-domain`
4. Verify the test domain appears correctly

**Test AGENTS.md Entry:**
```markdown
| test-domain | "test, example, demo" | `./test-domain/AGENTS.md` |
```

**Pass Criteria:**
- [ ] Domain name parsed correctly (no extra spaces)
- [ ] Keywords parsed correctly (quotes handled)
- [ ] Path parsed correctly (backticks handled)
- [ ] No parsing errors

**Result:** ⬜ PASS / ⬜ FAIL  
**Notes:** _______________

---

### AC-5: Count Accuracy

**Test:** Domain count matches actual routing table entries

**Steps:**
1. Count domains manually: `grep -c "^\| " AGENTS.md` (exclude header rows)
2. Run `/list-domain`
3. Compare count in output to manual count
4. Verify they match (excluding wiki default entry)

**Pass Criteria:**
- [ ] Count in output matches actual domains
- [ ] Wiki default entry excluded from count (if present)
- [ ] Off-by-one errors absent

**Result:** ⬜ PASS / ⬜ FAIL  
**Notes:** _______________

---

### AC-6: Non-Destructive Operation

**Test:** Command does not modify any files

**Steps:**
1. Record file checksums before: `find . -type f -exec md5 {} \; > /tmp/before.md5`
2. Run `/list-domain`
3. Run `/list-domain --verbose`
4. Record file checksums after: `find . -type f -exec md5 {} \; > /tmp/after.md5`
5. Compare checksums: `diff /tmp/before.md5 /tmp/after.md5`

**Pass Criteria:**
- [ ] No files modified (diff shows no changes)
- [ ] No new files created
- [ ] No files deleted
- [ ] Command is read-only

**Result:** ⬜ PASS / ⬜ FAIL  
**Notes:** _______________

---

### AC-7: Documentation Updated

**Test:** README.md and SKILL.md include /list-domain examples

**Steps:**
1. Check `technical-infrastructure/packages/project-blueprint/README.md`
2. Search for `/list-domain` in Quick Start section
3. Search for `/list-domain` in Usage section
4. Check `technical-infrastructure/packages/project-blueprint/skills/project-blueprint/SKILL.md`
5. Search for "List Domains" or `/list-domain` section

**Pass Criteria:**
- [ ] README.md Quick Start mentions `/list-domain`
- [ ] README.md Usage section has example
- [ ] README.md Domain Management subsection lists command
- [ ] SKILL.md has dedicated "List Domains" section
- [ ] SKILL.md includes output format examples

**Result:** ⬜ PASS / ⬜ FAIL  
**Notes:** _______________

---

### AC-8: Wiki Documentation

**Test:** Product wiki page lists the new command

**Steps:**
1. Open `technical-infrastructure/wiki/products/project-blueprint.md`
2. Search for `/list-domain` in domain management section
3. Verify command is listed alongside `/add-domain`, `/rename-domain`, `/remove-domain`

**Pass Criteria:**
- [ ] Wiki page updated with `/list-domain`
- [ ] Command description accurate
- [ ] Example usage provided
- [ ] Cross-referenced with other domain management commands

**Result:** ⬜ PASS / ⬜ FAIL  
**Notes:** _______________

---

## Edge Case Tests

### EC-1: Single Domain

**Test:** Works correctly with only 1 domain configured

**Steps:**
1. Create workspace with single domain
2. Run `/list-domain`
3. Verify output shows "Configured Domains (1):"

**Pass Criteria:**
- [ ] Singular/plural grammar correct ("1 domain" vs "1 domains")
- [ ] Output formatted correctly

**Result:** ⬜ PASS / ⬜ FAIL

---

### EC-2: Many Domains (10+)

**Test:** Handles large number of domains gracefully

**Steps:**
1. Add 10+ domains to test workspace
2. Run `/list-domain`
3. Verify all domains listed without truncation

**Pass Criteria:**
- [ ] All domains listed
- [ ] No performance issues (<2s response time)
- [ ] Output remains readable

**Result:** ⬜ PASS / ⬜ FAIL

---

### EC-3: Domain with Special Characters

**Test:** Handles domains with hyphens, underscores, numbers

**Steps:**
1. Add domain: `/add-domain api-v2 "api, v2, version2"`
2. Add domain: `/add-domain user_auth "user, authentication, login"`
3. Run `/list-domain`
4. Verify names display correctly

**Pass Criteria:**
- [ ] Hyphens preserved
- [ ] Underscores preserved
- [ ] Numbers preserved
- [ ] No escaping issues

**Result:** ⬜ PASS / ⬜ FAIL

---

### EC-4: Corrupted Routing Table

**Test:** Graceful handling of malformed AGENTS.md

**Steps:**
1. Manually corrupt routing table (remove pipe characters, break markdown)
2. Run `/list-domain`
3. Verify error message is helpful, not a crash

**Expected Output:**
```
Warning: Could not parse routing table from AGENTS.md
The routing table may be malformed.

Expected format:
| keywords | `./domain/AGENTS.md` |

Please check AGENTS.md and try again.
```

**Pass Criteria:**
- [ ] No stack trace or crash
- [ ] Helpful error message shown
- [ ] Suggests fix

**Result:** ⬜ PASS / ⬜ FAIL

---

## Test Summary

| Test ID | Criterion | Status | Notes |
|---------|-----------|--------|-------|
| AC-1 | Basic Listing | ⬜ | |
| AC-2 | Verbose Mode | ⬜ | |
| AC-3 | Empty Project | ⬜ | |
| AC-4 | Parsing Accuracy | ⬜ | |
| AC-5 | Count Accuracy | ⬜ | |
| AC-6 | Non-Destructive | ⬜ | |
| AC-7 | Documentation | ⬜ | |
| AC-8 | Wiki Updated | ⬜ | |
| EC-1 | Single Domain | ⬜ | Edge case |
| EC-2 | Many Domains | ⬜ | Edge case |
| EC-3 | Special Characters | ⬜ | Edge case |
| EC-4 | Corrupted Table | ⬜ | Edge case |

**Total:** ⬜ / 12 tests passing

**Test Date:** _______________  
**Tested By:** _______________  
**Overall Status:** ⬜ PASS / ⬜ FAIL

---

## Regression Testing

After implementation, run this test suite:
1. After any changes to prompt parsing logic
2. After updates to AGENTS.md template format
3. Before releasing new version of project-blueprint
4. After fixing any reported bugs

**Regression Test Log:**

| Date | Version | Tester | Result | Notes |
|------|---------|--------|--------|-------|
| | | | | |

---

**Test Harness Location:** `technical-infrastructure/packages/project-blueprint/tests/list-domain-acceptance-test.js` (to be created)  
**Backlog Reference:** `technical-infrastructure/wiki/operational/BACKLOG.md#pb-001-add-list-domain-command-to-project-blueprint-skill`
