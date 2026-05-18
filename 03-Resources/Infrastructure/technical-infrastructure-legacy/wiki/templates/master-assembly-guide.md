# Master Assembly Guide

**Template ID:** COMP-015  
**Purpose:** Shows how to compose a full plan from the 15 reusable component templates.

---

## Recommended Assembly Order

For a typical complex plan, include components in this order:

1. `status-summary-table.md` — Give the reader an immediate view of where things stand.
2. `navigation-pattern.md` — Let them jump to any section.
3. `model-responsibility.md` — Define who does what before any work starts.
4. `anti-hallucination-safeguards.md` — Set the quality bar upfront.
5. `tdd-methodology.md` — Establish the development rules.
6. `test-architecture.md` — Show the test harness before any code is written.
7. `phase-plan-structure.md` — One or more phase blocks (repeat for each phase).
8. `backlog-item-template.md` — Track outstanding work items.
9. `lab-node-dispatch-rules.md` — Document how work reaches the lab nodes.
10. `local-node-recovery.md` — Define what happens when things go wrong.
11. `high-frequency-decomposition.md` — Set up decomposition health monitoring.
12. `node-health-report.md` — Define how status is communicated.
13. `decision-log.md` — Record key decisions as they are made.
14. `session-notes.md` — Close with who owns what and what happens next.

## Include Pattern

Components are **standalone markdown files**. Use one of two patterns:

**Pattern A — Copy-paste (recommended for single-file plans):**
Copy the component content into your plan, then replace `{{PLACEHOLDER}}` values inline.

**Pattern B — Reference by path (recommended for multi-file wikis):**
```markdown
## Model Responsibility
See [`model-responsibility.md`](./model-responsibility.md).
```
This keeps the plan file lean but requires the reader to follow links.

## Minimal Plan

A minimal plan needs only 5 components:

| Component | Why Required |
|-----------|-------------|
| `status-summary-table.md` | Context: what is this about? |
| `model-responsibility.md` | Who does the work? |
| `tdd-methodology.md` | How is quality enforced? |
| `phase-plan-structure.md` | What steps will be taken? |
| `session-notes.md` | Who owns the plan and what's next? |

## Full Plan

A full plan includes all 15 components in the order listed above. This is the pattern used by `1-PLAN.md`.

---

## Quick-Start: Assemble a New Plan

1. Copy this header:
   ```markdown
   # {{PLAN_TITLE}}
   **Date:** {{DATE}}
   **Status:** {{STATUS}}
   **Scope:** {{SCOPE}}
   **Session Context:** {{CONTEXT}}
   ```
2. Include `status-summary-table.md` with your phases/items.
3. Include `navigation-pattern.md` with your section names.
4. Fill in the body using the component templates above.
5. Close with `session-notes.md`.

---

## Placeholder Reference

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{PLAN_TITLE}}` | Plan document title | `Keyword Router Debug Plan — Routing Transparency Side Effects` |
| `{{DATE}}` | Plan creation date | `2026-05-13` |
| `{{STATUS}}` | Current plan status | `EXECUTION COMPLETE — Core regression fixed` |
| `{{SCOPE}}` | What systems are affected | `` `pi-keyword-router`, `routing-transparency`, model selection pipeline `` |
| `{{CONTEXT}}` | What triggered this plan | `Side effects from routing-transparency fixes caused pi-keyword-router to consistently select low-capacity local models regardless of prompt intent.` |
