# Keyword Router Debug - Master Backlog

**Project:** Keyword Router Regression Debug
**Status:** Core regression FIXED (B-KR-001 through B-KR-003 complete)
**Remaining items:** 3 backlog items need follow-up
**Created:** 2026-05-14
**Last updated:** 2026-05-14 — B-KR-004/005/006 decomposed into lab-routable sub-steps

---

## ✅ Completed (Do Not Touch - Reference Only)

| Item | Status | Summary | Key Output |
|------|--------|---------|----------|
| **B-KR-001** | ✅ Complete | Persistent kill-switch for pi-keyword-router | 20 tests, TDD RED→GREEN, kill-switch stays OFF until fixed |
| **B-KR-002** | ✅ Complete | Bisected regression commit | Commit `93e1d39` identified - changed default from `gemma4:e4b` to `router:auto` |
| **B-KR-003** | ✅ Complete | Applied one-line fix | `lib/config.ts:39-42` restored to `ollama:gemma4:e4b` |

**Reference documents:**
- [`DECOMP-B-KR-001-2026-05-13.md`](./DECOMP-B-KR-001-2026-05-13.md)
- [`DECOMP-B-KR-001-PHASE1-2026-05-13.md`](./DECOMP-B-KR-001-PHASE1-2026-05-13.md)
- [`DECOMP-B-KR-002-2026-05-13.md`](./DECOMP-B-KR-002-2026-05-13.md)
- [`B-KR-002-REFINED-DISPATCH-2026-05-13.md`](./B-KR-002-REFINED-DISPATCH-2026-05-13.md)
- [`ROOT-CAUSE-B-KR-002-2026-05-14.md`](../../sessions/ROOT-CAUSE-B-KR-002-2026-05-14.md)
- [`B-KR-003-COMPLETION-2026-05-14.md`](../../sessions/B-KR-003-COMPLETION-2026-05-14.md)

---

## 📋 Remaining Items - CRITICAL BACKLOG

These items must be completed before the keyword-router debug project can be closed. They are sorted by priority and effort.

---

### 📋 B-KR-004: Restore Cloud Model Escalation Path

**Priority:** 🔴 High
**Effort:** 4-6 hours
**Status:** Decomposed — ready for lab dispatch
**Decomposition:** [`DECOMP-B-KR-004-2026-05-14.md`](./decompositions/DECOMP-B-KR-004-2026-05-14.md) (16 steps, 4 waves, ~60 min wall-clock)
**Owner:** Technical Infrastructure
**Why critical:** The core regression (default route) is fixed, but cloud escalation for deep research prompts still needs implementation.

**What to do:**
- Add `cloudEscalation` config section to keyword-router config
- Implement `KR-004` route: `"deep research on macro trends"` → `kimi-k2.6:cloud`
- Add TUI confirmation prompt before cloud model invocation
- Add cost tracking in `routing-transparency` footer

**Reference:** [`1-PLAN.md`](./1-PLAN.md)

---

### 📋 B-KR-005: Operational Runbook

**Priority:** 🟡 Medium
**Effort:** 2-3 hours
**Status:** Decomposed — ready for lab dispatch
**Decomposition:** [`DECOMP-B-KR-005-2026-05-14.md`](./decompositions/DECOMP-B-KR-005-2026-05-14.md) (9 steps, 3 waves, ~35 min wall-clock)
**Owner:** Technical Infrastructure
**Why critical:** Without documentation, future regressions will be harder to diagnose. The bisection work in B-KR-002 must be captured.

**What to do:**
- Write `keyword-router-operational-runbook.md`
- Document: how keyword-router works, how to disable it (kill-switch), how to debug routing issues, how to run bisection, model tier mapping, common issues
- Include the 7 KR-* routes and their expected model selections

---

### 📋 B-KR-006: CI Regression Test

**Priority:** 🟡 Medium
**Effort:** 1-2 hours
**Status:** Decomposed — ready for lab dispatch
**Decomposition:** [`DECOMP-B-KR-006-2026-05-14.md`](./decompositions/DECOMP-B-KR-006-2026-05-14.md) (10 steps, 4 waves, ~25 min wall-clock)
**Owner:** Technical Infrastructure
**Why critical:** The `93e1d39` regression happened silently. A CI test would have caught it immediately.

**What to do:**
- Add `test/bisect/regression-test-v2.ts` to CI pipeline
- Test runs on every commit: verifies `KR-002` escalates to `gemma4:e4b`
- Test runs on every commit: verifies `KR-005` stays at `qwen3.5:4b`
- Fail the build if default route changes without explicit override

---

## 🧩 Plan Infrastructure (Meta)

| Item | Status | Summary |
|------|--------|---------|
| **1-PLAN Reusable Components** | Decomposed — ready for lab dispatch | Extract 15 reusable plan component templates from `1-PLAN.md` for use across all Trading Desk plans |

**Decomposition:** [`DECOMP-1-PLAN-REUSABLE-COMPONENTS-2026-05-14.md`](./decompositions/DECOMP-1-PLAN-REUSABLE-COMPONENTS-2026-05-14.md) (17 steps, 4 waves, ~40 min wall-clock)
**Output:** `technical-infrastructure/wiki/templates/plan-components/` (15 templates + README + assembly guide)

---

```
B-KR-006 (1-2 hrs) → B-KR-004 (4-6 hrs) → B-KR-005 (2-3 hrs)
     │                      │                      │
     │                      │                      └── Document everything
     │                      └── Cloud escalation (high value feature)
     └── Prevent regression from recurring (highest ROI)
```

**Total remaining effort:** ~7-11 hours across 3 items.

---

## 🚫 Kill-Switch Status

The kill-switch (`extensions.pi-keyword-router.enabled`) added in B-KR-001 is currently:
- **Config exists:** ✅ Yes (`lib/config.ts`)
- **Default value:** `true` (backward compatible)
- **Current state:** Extension is ACTIVE (regression is fixed, no need to disable)
- **How to disable:** Edit config, set `enabled: false`, restart session
- **When to disable:** If future regressions occur, use kill-switch immediately

---

## Navigation

| Need | Go To |
|------|-------|
| Full project plan | [`1-PLAN.md`](./1-PLAN.md) |
| Orchestration guide | [`AGENTS.md`](./AGENTS.md) |
| B-KR-004 decomposition | [`DECOMP-B-KR-004-2026-05-14.md`](./decompositions/DECOMP-B-KR-004-2026-05-14.md) |
| B-KR-005 decomposition | [`DECOMP-B-KR-005-2026-05-14.md`](./decompositions/DECOMP-B-KR-005-2026-05-14.md) |
| B-KR-006 decomposition | [`DECOMP-B-KR-006-2026-05-14.md`](./decompositions/DECOMP-B-KR-006-2026-05-14.md) |
| **1-PLAN reusable components** | [`DECOMP-1-PLAN-REUSABLE-COMPONENTS-2026-05-14.md`](./decompositions/DECOMP-1-PLAN-REUSABLE-COMPONENTS-2026-05-14.md) |
| Invocation guide (prompts) | [`INVOCATION-GUIDE-2026-05-13.md`](./INVOCATION-GUIDE-2026-05-13.md) |
| Node capacity map | [`node-capacity-map.md`](../../../reference/node-capacity-map.md) |
| Root cause analysis | [`ROOT-CAUSE-B-KR-002-2026-05-14.md`](../../sessions/ROOT-CAUSE-B-KR-002-2026-05-14.md) |
| B-KR-003 completion | [`B-KR-003-COMPLETION-2026-05-14.md`](../../sessions/B-KR-003-COMPLETION-2026-05-14.md) |
| Master backlog (this file) | [`BACKLOG-keyword-router.md`](./BACKLOG-keyword-router.md) |

---

**Next action required:** Pick B-KR-004, B-KR-005, or B-KR-006 to dispatch to lab nodes. All items are decomposed and ready for orchestration.
**Project status:** Core regression FIXED. Remaining items are feature additions and documentation.
