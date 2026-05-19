# Phase 0 Decomposition — 1-PLAN: Extract Reusable Plan Component Templates (v1 — Multi-Node Parallel)

**Date:** 2026-05-14
**Phase:** Phase 0
**Backlog Item:** Extract reusable plan components from `1-PLAN.md`
**Decomposed by:** High Cloud Model (`ollama/kimi-k2.6`)
**Handoff to:** Low Cloud Model (`ollama/qwen3.5:397b`)
**Skill:** `decompose-execute-verify`
**Reference:** [`AGENTS.md`](./AGENTS.md)

---

## [S-TIGHT]

The `1-PLAN.md` document contains 15+ distinct structural components that recur across all Trading Desk planning documents. These components are currently embedded inline and must be extracted into standalone, reusable template files with `{{PLACEHOLDER}}` variables. The extraction is decomposed into 17 local-model-sized sub-steps grouped into 4 waves. **Wave 0 is sequential:** scaffold the output directory and create the library README. **Waves 1–3 run in parallel** across the lab node pool (fnet1–fnet7). Each wave contains 4–6 sub-steps that can run concurrently on different nodes. Total estimated effort: 2 hours, wall-clock time: ~40 minutes with full parallelism.

---

## Parallel Execution Overview

```
Wave 0 (Sequential)          Wave 1 (Parallel)              Wave 2 (Parallel)              Wave 3 (Parallel)
┌──────────────────┐        ┌──────────────────┐           ┌──────────────────┐           ┌──────────────────┐
│ SCAFFOLD-001     │   →    │ COMP-002         │   →       │ COMP-001         │   →       │ COMP-007         │
│ SCAFFOLD-002     │        │ COMP-010         │           │ COMP-003         │           │ COMP-008         │
│                  │        │ COMP-012         │           │ COMP-004         │           │ COMP-014         │
│                  │        │ COMP-011         │           │ COMP-005         │           │ COMP-015         │
│                  │        │ COMP-013         │           │ COMP-006         │           │                  │
│                  │        │ COMP-009         │           │                  │           │                  │
└──────────────────┘        └──────────────────┘           └──────────────────┘           └──────────────────┘
       fnet3                 fnet1  fnet2  fnet7             fnet3  fnet4  fnet5             fnet5  fnet6  fnet3
```

**Dependency rule:** Nothing in Wave N+1 starts until **all** Wave N steps are complete AND verified.

---

## Wave 0 — Directory Scaffold + README (Sequential, Prerequisite)

### Step 0A: 1-PLAN-SCAFFOLD-001 — Create Output Directory

| Field | Value |
|-------|-------|
| `step_id` | `1-PLAN-SCAFFOLD-001` |
| `title` | Create `technical-infrastructure/wiki/templates/plan-components/` directory |
| `workspace` | `trading-desk` |
| `target_file` | `technical-infrastructure/wiki/templates/plan-components/` |
| `target_node` | **fnet3** |
| `acceptance_criteria` | Directory exists at `/mnt/trading-desk/technical-infrastructure/wiki/templates/plan-components/` (or equivalent path on the target node). Directory is empty except for what Wave 0 creates. |
| `estimated_effort` | 2 min |
| `recommended_model` | `low-local` |

### Step 0B: 1-PLAN-SCAFFOLD-002 — Write README.md

| Field | Value |
|-------|-------|
| `step_id` | `1-PLAN-SCAFFOLD-002` |
| `title` | Write `README.md` explaining the plan component library structure and usage |
| `workspace` | `trading-desk` |
| `target_file` | `technical-infrastructure/wiki/templates/plan-components/README.md` |
| `target_node` | **fnet3** (same session as 0A — runs immediately after) |
| `acceptance_criteria` | File exists with: (a) a heading "Plan Component Template Library", (b) a table listing all 15 components with filename and description, (c) usage instructions showing how to `{{include}}` or copy-paste components into a new plan, (d) placeholder conventions documented, (e) reference to `PLAN-template.md` and `SESSION-NOTES-template.md` as related templates. |
| `estimated_effort` | 15 min |
| `recommended_model` | `medium-local` |

**Wave 0 Dispatch (pi-intercom):**
```typescript
intercom({
  action: "ask",
  to: "fnet3",
  message: "Wave 0: Execute SCAFFOLD-001 and SCAFFOLD-002 in sequence on this node. Create the plan-components output directory and write README.md with the component library index. Verify both files exist. Report back."
})
```

---

## Wave 1 — Simple Templates (Parallel, 6 sub-steps)

**All Wave 1 sub-steps can run concurrently** on different nodes. The output directory exists; each template is independent.

### Step 1A: 1-PLAN-COMP-002 — Anti-Hallucination Safeguards Template

| Field | Value |
|-------|-------|
| `step_id` | `1-PLAN-COMP-002` |
| `title` | Extract "Anti-Hallucination Safeguards" section into standalone template with placeholders |
| `workspace` | `trading-desk` |
| `target_file` | `technical-infrastructure/wiki/templates/plan-components/anti-hallucination-safeguards.md` |
| `target_node` | **fnet1** |
| `acceptance_criteria` | File exists with: (a) heading, (b) numbered safeguard list from 1-PLAN.md Section "Anti-Hallucination Safeguards", (c) `{{EVIDENCE_TYPE}}`, `{{VERIFIER_ROLE}}`, `{{REJECTION_ACTION}}` placeholders, (d) reference to `{{AGENTS_MD_PATH}}`. |
| `estimated_effort` | 5 min |
| `recommended_model` | `low-local` |

### Step 1B: 1-PLAN-COMP-010 — Decision Log Template

| Field | Value |
|-------|-------|
| `step_id` | `1-PLAN-COMP-010` |
| `title` | Extract "Decision Log" section entry format into standalone template with placeholders |
| `workspace` | `trading-desk` |
| `target_file` | `technical-infrastructure/wiki/templates/plan-components/decision-log.md` |
| `target_node` | **fnet1** (same session as 1A) |
| `acceptance_criteria` | File exists with: (a) heading, (b) decision entry template from 1-PLAN.md Section "Decision Log" with `{{DATE}}`, `{{DECISION}}`, `{{RATIONALE}}`, `{{REFERENCE}}` placeholders, (c) instruction that entries are append-only. |
| `estimated_effort` | 5 min |
| `recommended_model` | `low-local` |

### Step 2A: 1-PLAN-COMP-012 — Status Summary Table Template

| Field | Value |
|-------|-------|
| `step_id` | `1-PLAN-COMP-012` |
| `title` | Extract "Project Status Summary" table into standalone template with placeholders |
| `workspace` | `trading-desk` |
| `target_file` | `technical-infrastructure/wiki/templates/plan-components/status-summary-table.md` |
| `target_node` | **fnet2** |
| `acceptance_criteria` | File exists with: (a) heading, (b) markdown table with columns `| {{PHASE_COL}} | {{STATUS_COL}} | {{DELIVERABLE_COL}} |`, (c) 2+ example rows showing ✅ Complete / 📋 Ready patterns, (d) placeholder row for critical backlog reference. |
| `estimated_effort` | 5 min |
| `recommended_model` | `low-local` |

### Step 2B: 1-PLAN-COMP-011 — Session Notes Template

| Field | Value |
|-------|-------|
| `step_id` | `1-PLAN-COMP-011` |
| `title` | Extract "Session Notes" format into standalone template with placeholders |
| `workspace` | `trading-desk` |
| `target_file` | `technical-infrastructure/wiki/templates/plan-components/session-notes.md` |
| `target_node` | **fnet2** (same session as 2A) |
| `acceptance_criteria` | File exists with: (a) heading, (b) fields from 1-PLAN.md bottom section: `{{PLAN_OWNER}}`, `{{ORCHESTRATOR}}`, `{{PRIMARY_EXECUTOR}}`, `{{SECONDARY_EXECUTORS}}`, `{{ANTI_HALLUCINATION}}`, `{{REVIEW_REQUIRED}}`, `{{NEXT_ACTION}}`, (c) cross-reference to existing `SESSION-NOTES-template.md` for extended model-performance tracking. |
| `estimated_effort` | 5 min |
| `recommended_model` | `low-local` |

### Step 3A: 1-PLAN-COMP-013 — Navigation Pattern Template

| Field | Value |
|-------|-------|
| `step_id` | `1-PLAN-COMP-013` |
| `title` | Extract TOC-with-anchor-links navigation pattern into standalone template |
| `workspace` | `trading-desk` |
| `target_file` | `technical-infrastructure/wiki/templates/plan-components/navigation-pattern.md` |
| `target_node` | **fnet7** |
| `acceptance_criteria` | File exists with: (a) heading, (b) the exact navigation block from 1-PLAN.md with `## Navigation` header and bulleted links `[Section Name](#section-anchor)`, (c) `{{SECTION_COUNT}}`, `{{SECTION_1_NAME}}`, `{{SECTION_1_ANCHOR}}`, etc. placeholders, (d) instruction to keep anchors in kebab-case matching heading text. |
| `estimated_effort` | 5 min |
| `recommended_model` | `low-local` |

### Step 3B: 1-PLAN-COMP-009 — Backlog Item Template

| Field | Value |
|-------|-------|
| `step_id` | `1-PLAN-COMP-009` |
| `title` | Extract backlog item format from "Backlog Items" section into standalone template with placeholders |
| `workspace` | `trading-desk` |
| `target_file` | `technical-infrastructure/wiki/templates/plan-components/backlog-item-template.md` |
| `target_node` | **fnet7** (same session as 3A) |
| `acceptance_criteria` | File exists with: (a) heading, (b) metadata block from 1-PLAN.md backlog items: `{{ID}}`, `{{TITLE}}`, `{{CREATED}}`, `{{PRIORITY}}`, `{{PHASE}}`, `{{STATUS}}`, `{{OWNER}}`, `{{EFFORT}}`, `{{DEPENDENCIES}}`, (c) `{{TDD_ENTRY_POINT}}` field, (d) `### Acceptance Criteria` subsection with checkbox list, (e) example based on B-KR-001 structure. |
| `estimated_effort` | 10 min |
| `recommended_model` | `low-local` |

**Wave 1 Parallel Dispatch (pi-intercom):**
```typescript
// All dispatched simultaneously to different nodes
intercom({ action: "ask", to: "fnet1", message: "Wave 1: Execute COMP-002 and COMP-010 in sequence. Report file contents + git diff." })
intercom({ action: "ask", to: "fnet2", message: "Wave 1: Execute COMP-012 and COMP-011 in sequence. Report file contents + git diff." })
intercom({ action: "ask", to: "fnet7", message: "Wave 1: Execute COMP-013 and COMP-009 in sequence. Report file contents + git diff." })
```

---

## Wave 2 — Complex Templates with Diagrams (Parallel, 5 sub-steps)

**All Wave 2 sub-steps can run concurrently** on different nodes. They depend only on Wave 0 (directory exists).

### Step 4A: 1-PLAN-COMP-001 — Model Responsibility Matrix Template

| Field | Value |
|-------|-------|
| `step_id` | `1-PLAN-COMP-001` |
| `title` | Extract "Model Responsibility" section into standalone template with tier table and escalation flow |
| `workspace` | `trading-desk` |
| `target_file` | `technical-infrastructure/wiki/templates/plan-components/model-responsibility.md` |
| `target_node` | **fnet3** |
| `acceptance_criteria` | File exists with: (a) heading, (b) `### Responsibility Matrix` table with `{{TIER}}`, `{{MODEL}}`, `{{ROLE}}`, `{{EXECUTES_CODE}}`, `{{TYPICAL_ASSIGNMENT}}` columns, (c) `### Decomposition & Escalation Flow` ASCII diagram from 1-PLAN.md with `{{HIGH_CLOUD_MODEL}}`, `{{MEDIUM_CLOUD_MODEL}}`, `{{LOW_CLOUD_MODEL}}`, `{{LOCAL_MODEL}}` placeholders, (d) `### Rules` subsection with Must Always/Must Never lists per tier. |
| `estimated_effort` | 15 min |
| `recommended_model` | `medium-local` |

### Step 4B: 1-PLAN-COMP-003 — Local Node Recovery Template

| Field | Value |
|-------|-------|
| `step_id` | `1-PLAN-COMP-003` |
| `title` | Extract "Local Node Recovery" section into standalone template with playbook-executor dispatch |
| `workspace` | `trading-desk` |
| `target_file` | `technical-infrastructure/wiki/templates/plan-components/local-node-recovery.md` |
| `target_node` | **fnet3** (same session as 4A) |
| `acceptance_criteria` | File exists with: (a) heading, (b) numbered recovery protocol from 1-PLAN.md, (c) `playbook-executor` command block with `{{FAILED_NODE}}`, `{{REASON}}`, `{{SERVICE}}` placeholders, (d) `{{AGENTS_MD_PATH}}` reference. |
| `estimated_effort` | 10 min |
| `recommended_model` | `medium-local` |

### Step 5A: 1-PLAN-COMP-004 — High-Frequency Decomposition Template

| Field | Value |
|-------|-------|
| `step_id` | `1-PLAN-COMP-004` |
| `title` | Extract "High-Frequency Decomposition Detection" section into standalone template with ratio thresholds |
| `workspace` | `trading-desk` |
| `target_file` | `technical-infrastructure/wiki/templates/plan-components/high-frequency-decomposition.md` |
| `target_node` | **fnet4** |
| `acceptance_criteria` | File exists with: (a) heading, (b) Roles table with `{{MEDIUM_CLOUD_MODEL}}`, `{{LOW_CLOUD_MODEL}}`, (c) Detection Protocol numbered list, (d) Threshold table with `> 60%`, `40–60%`, `< 40%` rows and `{{WINDOW}}`, `{{ACTION}}`, `{{OWNER}}` columns, (e) `{{RATIO_FORMULA}}` placeholder, (f) High-Frequency Mode Behavior list. |
| `estimated_effort` | 15 min |
| `recommended_model` | `medium-local` |

### Step 5B: 1-PLAN-COMP-005 — Node Health Report Template

| Field | Value |
|-------|-------|
| `step_id` | `1-PLAN-COMP-005` |
| `title` | Extract "5-Minute Node Health Report" section into standalone template with report format |
| `workspace` | `trading-desk` |
| `target_file` | `technical-infrastructure/wiki/templates/plan-components/node-health-report.md` |
| `target_node` | **fnet4** (same session as 5A) |
| `acceptance_criteria` | File exists with: (a) heading, (b) `### Report Location` with `{{SESSION_PREFIX}}`, `{{DATE_PATTERN}}` placeholders, (c) `### Report Contents` bulleted list of 5 required sections from 1-PLAN.md, (d) `### User Discovery` with `ls` command and `{{GLOB_PATTERN}}` placeholder, (e) `{{AGENTS_MD_PATH}}` reference. |
| `estimated_effort` | 10 min |
| `recommended_model` | `medium-local` |

### Step 6A: 1-PLAN-COMP-006 — TDD Methodology Template

| Field | Value |
|-------|-------|
| `step_id` | `1-PLAN-COMP-006` |
| `title` | Extract "TDD Methodology" section into standalone template with RED→GREEN→REFACTOR rules and test layers |
| `workspace` | `trading-desk` |
| `target_file` | `technical-infrastructure/wiki/templates/plan-components/tdd-methodology.md` |
| `target_node` | **fnet5** |
| `acceptance_criteria` | File exists with: (a) heading, (b) `### Rules` numbered list from 1-PLAN.md with `{{WORKSPACE_1}}`, `{{WORKSPACE_2}}`, `{{UNIT_DIR}}`, `{{INTEGRATION_DIR}}`, `{{ACCEPTANCE_DIR}}` placeholders, (c) `### Test Layer Definitions` table with Layer/Scope/Location/When/Pass Gate columns, (d) explicit `stub-*` / `mock-*` naming convention with `// TODO: implement` comment. |
| `estimated_effort` | 15 min |
| `recommended_model` | `medium-local` |

**Wave 2 Parallel Dispatch (pi-intercom):**
```typescript
intercom({ action: "ask", to: "fnet3", message: "Wave 2: Execute COMP-001 and COMP-003 in sequence. Report file contents + git diff." })
intercom({ action: "ask", to: "fnet4", message: "Wave 2: Execute COMP-004 and COMP-005 in sequence. Report file contents + git diff." })
intercom({ action: "ask", to: "fnet5", message: "Wave 2: Execute COMP-006. Report file contents + git diff." })
```

---

## Wave 3 — Complex Templates with Cross-References (Parallel, 4 sub-steps)

**All Wave 3 sub-steps can run concurrently** on different nodes.

### Step 7A: 1-PLAN-COMP-007 — Test Architecture Template

| Field | Value |
|-------|-------|
| `step_id` | `1-PLAN-COMP-007` |
| `title` | Extract "Test Architecture" section into standalone template with directory layouts for both workspaces |
| `workspace` | `trading-desk` |
| `target_file` | `technical-infrastructure/wiki/templates/plan-components/test-architecture.md` |
| `target_node` | **fnet5** (same session as 6A) |
| `acceptance_criteria` | File exists with: (a) heading, (b) `### Workspace 1` and `### Workspace 2` subsections with `{{WORKSPACE_NAME}}`, `{{PACKAGE_PATH}}` placeholders, (c) tree-structured directory layout from 1-PLAN.md showing `test/unit/`, `test/integration/`, `test/acceptance/` with `← NEW` / `← EXISTING` / `← EXTEND` annotations as placeholders, (d) prerequisite note about harness mirroring. |
| `estimated_effort` | 15 min |
| `recommended_model` | `medium-local` |

### Step 8A: 1-PLAN-COMP-008 — Phase Plan Structure Template

| Field | Value |
|-------|-------|
| `step_id` | `1-PLAN-COMP-008` |
| `title` | Extract phase plan structure with RED/GREEN/REFACTOR subsections into standalone template |
| `workspace` | `trading-desk` |
| `target_file` | `technical-infrastructure/wiki/templates/plan-components/phase-plan-structure.md` |
| `target_node` | **fnet6** |
| `acceptance_criteria` | File exists with: (a) heading, (b) `### {{PHASE_NAME}}` template with `{{GOAL}}`, `{{LOCATION}}` placeholders, (c) `#### RED — Write Failing Test Stubs` subsection with numbered stub list format, (d) `#### GREEN — Implement to Pass` subsection with checklist format, (e) `#### REFACTOR` subsection with checklist format, (f) `#### Verification` subsection with pass-gate checklist, (g) `**Effort:** {{EFFORT_RANGE}}` and `**Risk:** {{RISK_LEVEL}}` footer. |
| `estimated_effort` | 15 min |
| `recommended_model` | `medium-local` |

### Step 8B: 1-PLAN-COMP-014 — Lab Node Dispatch Rules Template

| Field | Value |
|-------|-------|
| `step_id` | `1-PLAN-COMP-014` |
| `title` | Extract "Lab Node Dispatch Rules" section into standalone template with node capacity and dispatch protocol |
| `workspace` | `trading-desk` |
| `target_file` | `technical-infrastructure/wiki/templates/plan-components/lab-node-dispatch-rules.md` |
| `target_node` | **fnet6** (same session as 8A) |
| `acceptance_criteria` | File exists with: (a) heading, (b) `### Node Capacity Reference` table from 1-PLAN.md with `{{NODE}}`, `{{CPU}}`, `{{RAM}}`, `{{SAFE_CAPACITY}}`, `{{INSTALLED_MODELS}}`, `{{ASSIGN_WHEN}}` columns, (c) `### Orchestrator Dispatch Protocol` with `pi-intercom` and SSH fallback code blocks, (d) `### Node Selection Algorithm` numbered list, (e) `### Health Check Before Dispatch` with `echo OK` check, (f) `### Acceptance Test Execution on Lab Node` example. |
| `estimated_effort` | 15 min |
| `recommended_model` | `medium-local` |

### Step 9A: 1-PLAN-COMP-015 — Master Assembly Guide Template

| Field | Value |
|-------|-------|
| `step_id` | `1-PLAN-COMP-015` |
| `title` | Write "Master Assembly Guide" showing how to compose a full plan from component templates |
| `workspace` | `trading-desk` |
| `target_file` | `technical-infrastructure/wiki/templates/plan-components/master-assembly-guide.md` |
| `target_node` | **fnet3** |
| `acceptance_criteria` | File exists with: (a) heading, (b) `### Recommended Assembly Order` numbered list showing which component templates to include and in what order for a typical plan, (c) `### Include Pattern` showing how to reference component templates from a parent plan (e.g., via file path or copy-paste), (d) `### Minimal Plan` example assembling only essential components, (e) `### Full Plan` example assembling all components, (f) `{{PLAN_TITLE}}`, `{{DATE}}`, `{{BACKLOG_ID}}` placeholders. |
| `estimated_effort` | 15 min |
| `recommended_model` | `medium-local` |

**Wave 3 Parallel Dispatch (pi-intercom):**
```typescript
intercom({ action: "ask", to: "fnet5", message: "Wave 3: Execute COMP-007. Report file contents + git diff." })
intercom({ action: "ask", to: "fnet6", message: "Wave 3: Execute COMP-008 and COMP-014 in sequence. Report file contents + git diff." })
intercom({ action: "ask", to: "fnet3", message: "Wave 3: Execute COMP-015. Report file contents + git diff." })
```

---

## Node Allocation Map

| Node | Models | Assigned Waves | Rationale |
|------|--------|---------------|-----------|
| fnet1 | qwen3.5:4b, qwen3:8b | Wave 1: COMP-002, COMP-010 | Low-capacity; simple text extraction, bullet lists |
| fnet2 | qwen3.5:4b, qwen3:8b | Wave 1: COMP-012, COMP-011 | Low-capacity; table formatting, metadata blocks |
| fnet3 | qwen3.5:4b, qwen3:8b, gemma4:e4b | Wave 0: SCAFFOLD + Wave 2: COMP-001, COMP-003 + Wave 3: COMP-015 | Highest capacity; runs scaffold first, then complex templates with diagrams |
| fnet4 | qwen3.5:4b, qwen3:8b, gemma4:e4b | Wave 2: COMP-004, COMP-005 | Medium capacity; threshold tables and report formats |
| fnet5 | qwen3.5:4b, qwen3:8b, gemma4:e4b | Wave 2: COMP-006 + Wave 3: COMP-007 | Medium capacity; methodology + architecture trees |
| fnet6 | qwen3.5:4b, qwen3:8b, gemma4:e4b | Wave 3: COMP-008, COMP-014 | Medium capacity; phase structure + dispatch rules |
| fnet7 | qwen3.5:4b, qwen3:8b | Wave 1: COMP-013, COMP-009 | Low-capacity; TOC patterns, backlog item formatting |

**Utilization:** 7/7 nodes active across 3 parallel waves. fnet3 is the most heavily utilized (scaffold + 3 complex templates). fnet1, fnet2, fnet7 handle simple formatting extraction.

---

## Parallel Dispatch Protocol

### For Each Wave, the Low Cloud Must:

1. **Verify all target nodes are online** via pi-intercom before dispatching:
   ```typescript
   intercom({ action: "ask", to: "fnet1", message: "echo OK" })
   intercom({ action: "ask", to: "fnet2", message: "echo OK" })
   intercom({ action: "ask", to: "fnet3", message: "echo OK" })
   intercom({ action: "ask", to: "fnet4", message: "echo OK" })
   intercom({ action: "ask", to: "fnet5", message: "echo OK" })
   intercom({ action: "ask", to: "fnet6", message: "echo OK" })
   intercom({ action: "ask", to: "fnet7", message: "echo OK" })
   ```

2. **Dispatch all sub-steps simultaneously** via pi-intercom:
   ```typescript
   intercom({ action: "ask", to: "fnet1", message: "Wave 1: COMP-002..." })
   intercom({ action: "ask", to: "fnet2", message: "Wave 1: COMP-012..." })
   intercom({ action: "ask", to: "fnet7", message: "Wave 1: COMP-013..." })
   // etc.
   ```

3. **Collect all replies** as they arrive. Do not wait for one to finish before starting the next wave.

4. **Verify each sub-step** before marking the wave complete:
   - Check that the target file exists via SSH: `ssh {node} "ls -l /mnt/trading-desk/{target_file}"`.
   - Read file contents via SSH to confirm all required sections and placeholders are present.
   - Verify no source text was copied verbatim without `{{PLACEHOLDER}}` substitution points.

5. **Only proceed to the next wave** when ALL sub-steps in the current wave are verified.

### SSHFS Path References

All lab nodes write template files via the mounted workspace path:
```
/mnt/trading-desk/technical-infrastructure/wiki/templates/plan-components/
```

If SSHFS is not mounted, the dispatch message must include a mount command or fallback to the node's local clone path.

---

## Dependency Graph

```
SCAFFOLD-001 ─┐
SCAFFOLD-002 ─┼→ Wave 0 complete → Wave 1, 2, 3 can start
              │
COMP-002  ─┐  │
COMP-010  ─┤  │
COMP-012  ─┤  │
COMP-011  ─┼→ Wave 1 complete (parallel with Waves 2, 3)
COMP-013  ─┤  │
COMP-009  ─┘  │
              │
COMP-001  ─┐  │
COMP-003  ─┤  │
COMP-004  ─┼→ Wave 2 complete (parallel with Waves 1, 3)
COMP-005  ─┤  │
COMP-006  ─┘  │
              │
COMP-007  ─┐  │
COMP-008  ─┼→ Wave 3 complete (parallel with Waves 1, 2)
COMP-014  ─┤  │
COMP-015  ─┘  │
```

**Note:** Waves 1, 2, and 3 are independent of each other. They can all start simultaneously once Wave 0 completes. The wave grouping is for orchestration convenience, not hard dependencies.

---

## Handoff Checklist

- [x] 17 sub-steps decomposed across 4 waves.
- [x] Wave 0 (scaffold + README) is sequential prerequisite.
- [x] Waves 1–3 are parallel and distribute across 7 nodes.
- [x] Each sub-step has `step_id`, `workspace`, `target_file`, `target_node`, `acceptance_criteria`.
- [x] Each sub-step has `recommended_model` per node-capacity rules.
- [x] No sub-step exceeds 15 min estimated effort.
- [x] All templates use `{{PLACEHOLDER}}` variables for reusability.
- [x] Node allocation map shows 7/7 nodes utilized.
- [x] Parallel dispatch protocol is defined using pi-intercom with SSHFS path references.
- [x] README.md is included in Wave 0 as the library index.
- [x] Master assembly guide (COMP-015) documents how to compose a full plan from components.

---

**Next Action:** Low Cloud Model (`qwen3.5:397b`) reads this decomposition, reads [`AGENTS.md`](./AGENTS.md), and begins orchestration.

**Wave 0 dispatch:** Send to `fnet3` via pi-intercom: "Execute SCAFFOLD-001, SCAFFOLD-002."

**Plan Owner:** High Cloud Model (`kimi-k2.6`) — decomposition complete. Standing by for user escalation requests only.
**No further action from high cloud model. Passing control to low cloud model.**
