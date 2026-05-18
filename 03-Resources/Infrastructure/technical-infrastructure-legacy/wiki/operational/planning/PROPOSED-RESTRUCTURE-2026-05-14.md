# Issue-Centric Documentation Architecture (v2)

**Purpose:** Replaces the type-based folder model (`planning/`, `sessions/`, `status/`, `testing/`) with an **issue-based model** where every issue, product, or domain has a persistent, unified home that never changes during or between sessions.

**Scope:** `technical-infrastructure/operational/` and all workspace documentation.

**Date:** 2026-05-14  
**Status:** Proposed — awaiting user confirmation before restructuring existing docs.

---

## The Problem

The current type-based model scatters a single issue across:
```
planning/PLAN-2026-05-13-1926.md          ← the plan
status/STATUS-2026-05-13-2300.md          ← a status report
sessions/SESSION-NOTES-2026-05-13.md      ← session notes
testing/TEST-FAILURES-LOG.md              ← test results
wiki/products/keyword-router-debug/...   ← wiki docs
```

This makes it impossible to:
- See the full lifecycle of an issue at a glance
- Understand what prompts led to what decisions
- Find the troubleshooting that happened during a session
- Preserve context across multiple sessions

---

## The Solution: Issue-Based Homes

Every issue gets a **persistent, dedicated folder** that contains **everything** related to that issue for its entire lifecycle. The folder name never changes.

### Top-Level Structure

```
technical-infrastructure/operational/
├── README.md                    # Operational area guide + conventions
├── BACKLOG.md                   # Master index — points to active issues
├── issues/                      # 🏠 Active issue homes (never deleted)
│   ├── keyword-router-regression/
│   │   ├── 0-ISSUE.md           # The canonical issue definition
│   │   ├── 1-PLAN.md            # The active plan (or link to latest)
│   │   ├── prompts/             # All user prompts for this issue
│   │   │   ├── 2026-05-13-1926-kickoff.md
│   │   │   ├── 2026-05-13-2100-followup.md
│   │   │   └── 2026-05-14-0800-bisection-refinement.md
│   │   ├── sessions/            # Session notes (chronological)
│   │   │   ├── 2026-05-13-1926.md
│   │   │   ├── 2026-05-13-2100.md
│   │   │   └── 2026-05-14-0800.md
│   │   ├── status/              # Status reports (point-in-time snapshots)
│   │   │   ├── 2026-05-13-2300-phase0-red.md
│   │   │   └── 2026-05-14-0900-phase1-green.md
│   │   ├── tests/               # Test plans, results, evidence
│   │   │   ├── regression-test-v2.ts
│   │   │   └── test-results.md
│   │   ├── troubleshooting/     # Troubleshooting plans + findings
│   │   │   ├── 0-PLAN.md        # Troubleshooting plan
│   │   │   ├── 1-analysis.md    # Root cause analysis
│   │   │   └── 2-resolution.md  # Fix applied + verification
│   │   ├── decompositions/      # Decomposition docs
│   │   │   ├── DECOMP-PHASE0.md
│   │   │   └── DECOMP-PHASE1.md
│   │   ├── AGENTS.md            # Issue-specific orchestration guide
│   │   └── artifacts/           # Screenshots, logs, diffs, etc.
│   │       └── bisection-heatmap.png
│   ├── playbook-executor-nl-triggers/
│   │   ├── 0-ISSUE.md
│   │   ├── 1-PLAN.md
│   │   └── ...
│   └── trading-lab-deployment/
│       ├── 0-ISSUE.md
│       └── ...
├── archived/                    # Completed issues (pruned from issues/)
│   └── keyword-router-regression/
│       ├── 0-ISSUE.md
│       └── ... (full copy)
├── meta/                        # Templates, conventions, standards
│   ├── ISSUE-TEMPLATE.md
│   ├── PLAN-TEMPLATE.md
│   ├── PROMPT-TEMPLATE.md
│   └── TROUBLESHOOTING-TEMPLATE.md
└── data/                        # Shared data (benchmarks, configs)
    └── ... (unchanged)
```

---

## File Naming Convention

### Issue Home Folders

| Format | Example |
|--------|---------|
| `kebab-case-issue-name/` | `keyword-router-regression/`, `playbook-executor-nl-triggers/` |

### Within an Issue Home

| File | Purpose | Template |
|------|---------|----------|
| `0-ISSUE.md` | Canonical issue definition — problem, acceptance criteria, status, links to everything | `meta/ISSUE-TEMPLATE.md` |
| `1-PLAN.md` | Soft-link (or copy) of the active plan. Updated when plan changes. | `meta/PLAN-TEMPLATE.md` |
| `prompts/*.md` | Every user prompt that initiated work on this issue, timestamped | `meta/PROMPT-TEMPLATE.md` |
| `sessions/*.md` | Session notes in chronological order | existing Activity Log format |
| `status/*.md` | Point-in-time status snapshots | existing STATUS format |
| `tests/*.md` | Test plans, test results, regression tests | existing testing format |
| `troubleshooting/0-PLAN.md` | Troubleshooting plan if needed | `meta/TROUBLESHOOTING-TEMPLATE.md` |
| `troubleshooting/1-analysis.md` | Root cause analysis | existing format |
| `troubleshooting/2-resolution.md` | Fix applied + verification | existing format |
| `decompositions/*.md` | Decomposition docs | existing format |
| `AGENTS.md` | Issue-specific orchestration guide (optional) | `AGENTS.md` pattern |
| `artifacts/*` | Logs, screenshots, diffs, JSON, etc. | — |

**Why `0-` prefix?** Sorts the most important files to the top of a directory listing.

---

## Navigation Hierarchy

The hierarchy is explicit and link-based. No implicit knowledge required.

```
BACKLOG.md
    │ "[TI-036] ..." → link to issues/playbook-executor-nl-triggers/0-ISSUE.md
    │
    ▼
0-ISSUE.md
    │ "Plan: 1-PLAN.md" → link to 1-PLAN.md
    │ "Sessions: sessions/" → link to sessions/
    │ "Troubleshooting: troubleshooting/" → link to troubleshooting/0-PLAN.md
    │ "Prompts: prompts/" → link to prompts/
    │
    ├─→ 1-PLAN.md
    │       │ "Decomposition: decompositions/DECOMP-PHASE0.md"
    │       │ "Troubleshooting plan: troubleshooting/0-PLAN.md"
    │       ▼
    ├─→ sessions/2026-05-13-1926.md
    ├─→ status/2026-05-13-2300.md
    ├─→ troubleshooting/0-PLAN.md
    │       │ "Analysis: 1-analysis.md"
    │       │ "Resolution: 2-resolution.md"
    │       ▼
    ├─→ prompts/2026-05-13-1926-kickoff.md
    └─→ artifacts/
```

**Rule:** Every file in the hierarchy **links upward** (to its parent) and **links downward** (to its children). You can navigate in both directions without guessing.

---

## The Prompts Folder

### Why Prompts Matter

Your prompts are the **input artifacts** that produced everything else. Without them, you can't:
- Understand why a decision was made
- Refine prompts based on outcomes
- Reproduce results
- Train future interactions

### Prompt File Format

```markdown
# Prompt: {brief description}

**Date:** YYYY-MM-DD HH:MM  
**Issue:** [link to 0-ISSUE.md]  
**Session:** [link to sessions/ file]  
**Status after this prompt:** [link to status/ file]

---

## User Prompt (verbatim)

{The exact prompt the user wrote}

---

## Outcome

{What happened as a result of this prompt}

## Decisions Made

- Decision 1
- Decision 2

## Files Created/Modified

- `path/to/file` — what changed

## Lessons for Future Prompts

{What you learned about phrasing, context, or structure from this interaction}

## Follow-up Prompts

- [link to next prompt in sequence]
```

### Prompt Versioning

If you revise a prompt and re-run it, create a **new file** with a new timestamp. Do not overwrite old prompts. The history matters.

| Scenario | Action |
|----------|--------|
| First prompt on an issue | `prompts/2026-05-13-1926-kickoff.md` |
| Follow-up in same session | `prompts/2026-05-13-2100-followup.md` |
| Next-day continuation | `prompts/2026-05-14-0800-phase1-green.md` |
| Revised prompt for same task | `prompts/2026-05-14-0900-revised-bisection.md` |

---

## The Troubleshooting Folder

### When to Create It

Create `troubleshooting/` inside an issue when:
- The issue has a **diagnostic or debugging phase** (like B-KR-002 bisection)
- Something unexpected happened and you had to **investigate** (not just implement)
- You need to **isolate a root cause** before you can fix it

### Troubleshooting Structure

```
troubleshooting/
├── 0-PLAN.md      # What you're going to investigate and how
├── 1-analysis.md  # What you found
├── 2-resolution.md # How you fixed it + verification
└── artifacts/     # Evidence (logs, diffs, screenshots)
```

**If troubleshooting reveals a SEPARATE issue** (not just a sub-task), create a **new issue home** and link it:
```markdown
## Related Issue
- [Found during troubleshooting: routing-transparency override bug](../../routing-transparency-override/0-ISSUE.md)
```

---

## The BACKLOG.md as Index

`BACKLOG.md` is the **only** cross-issue index. It does not contain details — it contains **links**.

```markdown
# Technical Infrastructure — Active Backlog

## 🔴 High Priority

### [TI-036] Playbook-Executor Natural-Language Trigger Expansion
**Status:** 📋 In Progress  
**Issue Home:** [issues/playbook-executor-nl-triggers/0-ISSUE.md](../../issues/playbook-executor-nl-triggers/0-ISSUE.md)  
**Active Plan:** [1-PLAN.md](../../issues/playbook-executor-nl-triggers/1-PLAN.md)  
**Acceptance Criteria:** See 0-ISSUE.md

### [B-KR-001–003] Keyword Router Regression (COMPLETE)
**Status:** ✅ Complete  
**Issue Home:** [archived/keyword-router-regression/0-ISSUE.md](../../archived/keyword-router-regression/0-ISSUE.md)  
**Completion Report:** [status/2026-05-14-0900-phase1-green.md](../../archived/keyword-router-regression/status/2026-05-14-0900-phase1-green.md)
```

**Rule:** BACKLOG.md contains **zero details** beyond status and links. All details live in the issue homes.

---

## Migration from Type-Based to Issue-Based

### For New Issues

1. Create `issues/{issue-name}/`
2. Copy `meta/ISSUE-TEMPLATE.md` to `0-ISSUE.md`
3. Fill it in
4. Create subfolders as needed
5. Add entry to `BACKLOG.md`

### For Existing Issues (like keyword-router)

**Do not delete old files yet.** Instead:

1. Create `issues/keyword-router-regression/`
2. Move (or copy) relevant files into the issue home
3. Update `0-ISSUE.md` to point to the new locations
4. Update `BACKLOG.md` to point to the issue home
5. Leave old files in place with a **deprecation notice** at the top:
   ```markdown
   > **DEPRECATED:** This file has moved to [new location]. This copy is kept for reference only.
   ```
6. After 30 days, delete the deprecated copies.

---

## Quality Checklist for Issue Homes

Before declaring an issue home complete, verify:
- [ ] `0-ISSUE.md` exists and links to all subfolders
- [ ] `1-PLAN.md` exists (or link to it exists)
- [ ] Every session has a `sessions/` entry
- [ ] Every user prompt that initiated work is in `prompts/`
- [ ] Status reports are in `status/` (not just chat logs)
- [ ] If troubleshooting happened, `troubleshooting/` exists with 0-PLAN/1-analysis/2-resolution
- [ ] All links are relative and work
- [ ] `BACKLOG.md` points to this issue home
- [ ] No orphaned files exist in type-based folders for this issue

---

## Comparison: Before vs After

| Concern | Before (type-based) | After (issue-based) |
|---------|---------------------|---------------------|
| Where is everything for keyword-router? | Scattered across 5 folders | `issues/keyword-router-regression/` |
| What prompts led to the bisection? | Lost in chat history | `issues/keyword-router-regression/prompts/` |
| What was the troubleshooting plan? | Nowhere formalized | `issues/keyword-router-regression/troubleshooting/0-PLAN.md` |
| How do I find the root cause? | Search across wiki + sessions | `issues/keyword-router-regression/troubleshooting/1-analysis.md` |
| Can I reproduce this session? | No — prompts not saved | Yes — prompts + plans + sessions all together |
| How do I refine my prompt style? | No mechanism | Review `prompts/` → `lessons` section → iterate |
| What context do I give the AI? | "Read the wiki" (scattered) | "Read `issues/X/0-ISSUE.md`" (one file) |

---

## Immediate Next Steps

1. **Create the new folder structure** in `technical-infrastructure/operational/issues/`
2. **Create templates** in `technical-infrastructure/operational/meta/`
3. **Migrate the keyword-router regression** as the pilot issue (move existing docs into `issues/keyword-router-regression/`)
4. **Update `BACKLOG.md`** to point to issue homes instead of scattered files
5. **Capture this prompt** as the first entry in `issues/doc-standards-restructure/prompts/`

**Shall I create the folder structure, templates, and migrate keyword-router now?**
