# Keyword Router Debug — Master Backlog

**Project:** Keyword Router Regression Debug  
**Status:** Core regression FIXED (B-KR-001 through B-KR-003 complete)  
**Remaining items:** 3 backlog items need follow-up  
**Created:** 2026-05-14  
**Last updated:** 2026-05-14  

---

## ✅ Completed (Do Not Touch — Reference Only)

| Item | Status | Summary | Key Output |
|------|--------|---------|----------|
| **B-KR-001** | ✅ Complete | Persistent kill-switch for pi-keyword-router | 20 tests, TDD RED→GREEN, kill-switch stays OFF until fixed |
| **B-KR-002** | ✅ Complete | Bisected regression commit | Commit `93e1d39` identified — changed default from `gemma4:e4b` to `router:auto` |
| **B-KR-003** | ✅ Complete | Applied one-line fix | `lib/config.ts:39-42` restored to `ollama:gemma4:e4b` |

**Reference documents:**
- [`DECOMP-B-KR-001-2026-05-13.md`](./DECOMP-B-KR-001-2026-05-13.md)
- [`DECOMP-B-KR-001-PHASE1-2026-05-13.md`](./DECOMP-B-KR-001-PHASE1-2026-05-13.md)
- [`DECOMP-B-KR-002-2026-05-13.md`](./DECOMP-B-KR-002-2026-05-13.md)
- [`B-KR-002-REFINED-DISPATCH-2026-05-13.md`](./B-KR-002-REFINED-DISPATCH-2026-05-13.md)
- [`ROOT-CAUSE-B-KR-002-2026-05-14.md`](../../wiki/operational/sessions/ROOT-CAUSE-B-KR-002-2026-05-14.md)
- [`B-KR-003-COMPLETION-2026-05-14.md`](../../wiki/operational/sessions/B-KR-003-COMPLETION-2026-05-14.md)

---

## 📋 Remaining Items — CRITICAL BACKLOG

These items must be completed before the keyword-router debug project can be closed. They are sorted by priority and effort.

---

### 📋 B-KR-004: Restore Cloud Model Escalation Path

**Priority:** 🔴 High  
**Effort:** 4–6 hours  
**Status:** Ready to start  
**Owner:** Technical Infrastructure  
**Why critical:** The core regression (default route) is fixed, but cloud escalation for deep research prompts still needs implementation.

**What to do:**
- Add `cloudEscalation` config section to keyword-router config
- Implement `KR-004` route: `"deep research on macro trends"` → `kimi-k2.6:cloud`
- Add TUI confirmation prompt before cloud model invocation
- Add cost tracking in `routing-transparency` footer

**Reference:** [`PLAN-2026-05-13-1926.md`](./PLAN-2026-05-13-1926.md)

---

### 📋 B-KR-005: Operational Runbook

**Priority:** 🟡 Medium  
**Effort:** 2–3 hours  
**Status:** Ready to start  
**Owner:** Technical Infrastructure  
**Why critical:** Without documentation, future regressions will be harder to diagnose. The bisection work in B-KR-002 must be captured.

**What to do:**
- Write `keyword-router-operational-runbook.md`
- Document: how keyword-router works, how to disable it (kill-switch), how to debug routing issues, how to run bisection, model tier mapping, common issues
- Include the 7 KR-* routes and their expected model selections

---

### 📋 B-KR-006: CI Regression Test

**Priority:** 🟡 Medium  
**Effort:** 1–2 hours  
**Status:** Ready to start  
**Owner:** Technical Infrastructure  
**Why critical:** The `93e1d39` regression happened silently. A CI test would have caught it immediately.

**What to do:**
- Add `test/bisect/regression-test-v2.ts` to CI pipeline
- Test runs on every commit: verifies `KR-002` escalates to `gemma4:e4b`
- Test runs on every commit: verifies `KR-005` stays at `qwen3.5:4b`
- Fail the build if default route changes without explicit override

---

## 🎯 Recommended Execution Order

```
B-KR-006 (1–2 hrs) → B-KR-004 (4–6 hrs) → B-KR-005 (2–3 hrs)
     │                      │                      │
     │                      │                      └── Document everything
     │                      └── Cloud escalation (high value feature)
     └── Prevent regression from recurring (highest ROI)
```

**Total remaining effort:** ~7–11 hours across 3 items.

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
| Full project plan | [`PLAN-2026-05-13-1926.md`](./PLAN-2026-05-13-1926.md) |
| Orchestration guide | [`AGENTS.md`](./AGENTS.md) |
| Invocation guide (prompts) | [`INVOCATION-GUIDE-2026-05-13.md`](./INVOCATION-GUIDE-2026-05-13.md) |
| Node capacity map | [`node-capacity-map.md`](../../wiki/reference/node-capacity-map.md) |
| Root cause analysis | [`ROOT-CAUSE-B-KR-002-2026-05-14.md`](../../wiki/operational/sessions/ROOT-CAUSE-B-KR-002-2026-05-14.md) |
| B-KR-003 completion | [`B-KR-003-COMPLETION-2026-05-14.md`](../../wiki/operational/sessions/B-KR-003-COMPLETION-2026-05-14.md) |
| Master backlog (this file) | [`BACKLOG-MASTER.md`](./BACKLOG-MASTER.md) |

---

**Next action required:** Pick B-KR-004, B-KR-005, or B-KR-006 to start.  
**Project status:** Core regression FIXED. Remaining items are feature additions and documentation.
