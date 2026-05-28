---
name: Workflow Orchestration Research
summary: Evaluate workflow orchestration options for single-user lab — Temporal, Cadence, pi orchestration, Taskwarrior
status: active
phase: "Phase 2: Evaluation"
progress: 15
tracked: true
---

# Workflow Orchestration Research — FOCUS

**Status:** Active research
**Started:** 2025-05-19
**Goal:** Determine the best approach for managing personal workload as projects with durable execution in a single-user lab.

## Current Focus

Initial scaffold complete. Ready to run the research-evaluate chain.

## Key Questions

1. Is Cadence (or Temporal) worth the operational overhead for a single-user lab?
2. Can existing pi orchestration fill the gap with minor enhancements?
3. Is a lightweight tool like Taskwarrior + SQLite sufficient for tracking, with pi handling execution?
4. What hybrid approach gets the best of durability + simplicity?

## Alternatives Being Evaluated

| # | Alternative | Category |
|---|------------|----------|
| 1 | Temporal | Workflow engine (Cadence successor) |
| 2 | Cadence | Workflow engine (Uber original) |
| 3 | pi orchestration | Existing setup (chains, decompose, intercom) |
| 4 | Taskwarrior | CLI task manager |
| 5 | SQLite + cron | Custom automation |
| 6 | Notion API | SaaS project management |

## Next Steps

- [ ] Run `research-evaluate` chain to produce research briefs and evaluation matrix
- [ ] Review evaluation matrix and recommendation
- [ ] Decide on approach and potentially create an implementation project

---

> 📋 **Checkbox states:** `[ ]` To Do | `[/]` In Progress | `[~]` Good Enough | `[x]` Done | `[>]` Deferred | `[!]` Blocked | `[-]` Cancelled — [full legend](../../../personal-vault/01-Projects/doc-standards/wiki/doc-standards/reference/Checkbox-State-Legend.md)
*Last updated: 2026-05-27*
