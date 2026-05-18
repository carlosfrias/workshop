# B-KR-001–003: Keyword Router Regression — Core Fix Complete

**Issue ID:** keyword-router-regression  
**Status:** ✅ COMPLETE — Core regression fixed. Remaining items tracked in BACKLOG-keyword-router.  
**Priority:** 🔴 High (was High; now residual items are Medium)  
**Created:** 2026-05-13  
**Completed:** 2026-05-14  
**Owner:** Technical Infrastructure  

---

## [S-TIGHT]

The `pi-keyword-router` extension persistently selected low-capacity local models (`qwen3.5:4b`) regardless of prompt complexity, never escalating to higher-capacity models. Root cause: commit `93e1d39` changed the default route from `ollama:gemma4:e4b` to `router:auto`. Fix applied: restored `gemma4:e4b` as default. Kill-switch, bisection, and regression test infrastructure also built. Three residual items remain (B-KR-004, B-KR-005, B-KR-006).

---

## Problem Statement

**Symptom:** All prompts, even complex reasoning ones like `"analyze risk for NVDA"`, routed to `qwen3.5:4b` (low-capacity) instead of `gemma4:e4b` (medium) or cloud models.

**Impact:** Impossible to use keyword routing for anything beyond trivial tasks.

**Root Cause:** Commit `93e1d39` (2026-05-08) changed `BUILT_IN_DEFAULTS` from `provider: "ollama", model: "gemma4:e4b"` to `provider: "router", model: "auto"`. When `pi-model-router` is not installed, `router:auto` cannot resolve and falls back to the lowest-capacity model.

**Fix:** One-line change in `lib/config.ts:39-42`. Restored `ollama:gemma4:e4b`.

---

## Acceptance Criteria

### B-KR-001: Kill-Switch (COMPLETE ✅)
- [x] Config flag `extensions.pi-keyword-router.enabled` exists and is read on every session start.
- [x] When `enabled = false`, extension registers no hooks and emits no events.
- [x] `routing-transparency` footer shows `keyword-router: disabled` when flag is false.
- [x] State survives session restart without user intervention.
- [x] Re-enabling requires manual config edit + session restart.
- [x] 20 test stubs written, TDD RED→GREEN across 7 lab nodes.

### B-KR-002: Bisection (COMPLETE ✅)
- [x] Exact regression commit identified: `93e1d39`.
- [x] Root cause documented: default route regression.
- [x] Bisection test created and validated.
- [x] Parallel bisection executed across 7 lab nodes.

### B-KR-003: Fix (COMPLETE ✅)
- [x] Default route restored to `provider: "ollama", model: "gemma4:e4b"`.
- [x] Regression test passes on HEAD.
- [x] KR-002 routes to `gemma4:e4b`.
- [x] KR-005 routes to `qwen3.5:4b`.
- [x] No regressions in other keyword routes.

### Residual Items (NOT STARTED)
- [ ] B-KR-004: Cloud escalation for deep research prompts.
- [ ] B-KR-005: Operational runbook.
- [ ] B-KR-006: CI regression test.

---

## Issue Home Navigation

| Need | Go To |
|------|-------|
| The master plan | [`1-PLAN.md`](./1-PLAN.md) |
| Orchestration guide | [`AGENTS.md`](./AGENTS.md) |
| Copy-paste prompts | [`INVOCATION-GUIDE-2026-05-13.md`](./INVOCATION-GUIDE-2026-05-13.md) |
| Critical backlog | [`BACKLOG-keyword-router.md`](./BACKLOG-keyword-router.md) |
| Decompositions | [`decompositions/`](./decompositions/) |
| Session notes | [`sessions/`](./sessions/) |
| Status reports | [`status/`](./status/) |
| Prompts that drove work | [`prompts/`](./prompts/) |
| Troubleshooting investigation | [`troubleshooting/`](./troubleshooting/) |
| Test artifacts | [`tests/`](./tests/) |
| Screenshots, logs, diffs | [`artifacts/`](./artifacts/) |

---

## Key Outputs

| Output | Location | Status |
|--------|----------|--------|
| Kill-switch implementation | `pi-keyword-router/lib/config.ts`, `lib/gatekeeper.ts` | ✅ Committed |
| 20 TDD test stubs | `pi-keyword-router/test/` | ✅ Committed |
| Bisection regression test | `pi-keyword-router/test/bisect/regression-test-v2.ts` | ✅ Committed |
| Root cause analysis | [`troubleshooting/1-analysis.md`](./troubleshooting/1-analysis.md) | ✅ |
| Fix completion report | [`troubleshooting/2-resolution.md`](./troubleshooting/2-resolution.md) | ✅ |

---

## Related Issues

- None created from this investigation.

---

**Kill-Switch Status:** Extension is ACTIVE (`enabled: true`). No need to disable — regression is fixed.

**Next Action:** Pick B-KR-004, B-KR-005, or B-KR-006 to start. See [`BACKLOG-keyword-router.md`](./BACKLOG-keyword-router.md) for details.

---

*This issue follows the issue-centric documentation standard. All work for this issue lives in this folder.*
