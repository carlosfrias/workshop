# Resolution: Keyword Router Regression Fix

**Issue:** keyword-router-regression  
**Fix ID:** B-KR-003  
**Date:** 2026-05-14  
**Applied by:** Low Cloud Orchestrator → fnet3

---

## [S-TIGHT]

One-line fix: restored `provider: "ollama", model: "gemma4:e4b"` in `lib/config.ts`. Verified with 3 test scenarios: reasoning → gemma4:e4b, monitoring → qwen3.5:4b, simple → qwen3.5:4b. All pass. Fix committed and pushed.

---

## Fix Applied

| Item | Detail |
|------|--------|
| File | `lib/config.ts` |
| Line | 39–42 (`BUILT_IN_DEFAULTS.default`) |
| Change | `provider: "router"` → `provider: "ollama"`; `model: "auto"` → `model: "gemma4:e4b"` |
| Commits | `ee1e679` (fix), `183eded` (tests) |
| Repo | `github.com/carlosfrias/pi-keyword-router` |

## Verification

| Test | Input | Expected | Result | Status |
|------|-------|----------|--------|--------|
| Default Config | — | gemma4:e4b | gemma4:e4b | ✅ PASS |
| KR-002 | "analyze risk for NVDA" | gemma4:e4b or higher | gemma4:e4b | ✅ PASS |
| KR-005 | "status check" | qwen3.5:4b (monitoring) | qwen3.5:4b | ✅ PASS |

**All 3 verification tests: PASSING ✅**

## Behavior Comparison

| Scenario | Before Fix | After Fix |
|----------|-----------|-----------|
| Default route | router/auto (requires model-router) | ollama/gemma4:e4b (self-contained) |
| Reasoning prompt | qwen3.5:4b 🔴 | gemma4:e4b ✅ |
| Monitoring prompt | qwen3.5:4b | qwen3.5:4b ✅ |
| Keyword-matched | Route-specific | Route-specific ✅ |

## Files Modified

- `lib/config.ts` — Default route fix (2 lines)
- `vitest.config.ts` — NEW test configuration
- `test/unit/fix-verification.test.ts` — NEW verification tests
- `package.json` — Added vite dependency

## Push Status

All changes pushed to `github.com/carlosfrias/pi-keyword-router`:
- `ee1e679 fix(keyword-router): restore gemma4:e4b as default fallback`
- `183eded test(keyword-router): add TDD kill-switch tests + bisection harness`

## Remaining Items

The core regression is fixed. Three items remain in the backlog:

| Item | Priority | Effort | What |
|------|----------|--------|------|
| B-KR-004 | 🟡 Medium | 4–6 hrs | Cloud escalation for deep research |
| B-KR-005 | 🟡 Medium | 2–3 hrs | Operational runbook |
| B-KR-006 | 🟡 Medium | 1–2 hrs | CI regression test |

See [`BACKLOG-keyword-router.md`](../BACKLOG-keyword-router.md) for details.

## Kill-Switch Status

- **Config exists:** ✅ Yes (`lib/config.ts`)
- **Default value:** `true` (backward compatible)
- **Current state:** Extension is ACTIVE (regression is fixed, no need to disable)
- **How to disable:** Edit config, set `enabled: false`, restart session
- **When to disable:** If future regressions occur, use kill-switch immediately

## Related

- **Troubleshooting Plan:** [0-PLAN.md](0-PLAN.md)
- **Root Cause Analysis:** [1-analysis.md](1-analysis.md)
- **Backlog:** [BACKLOG-keyword-router.md](../BACKLOG-keyword-router.md)

---

*This resolution follows the doc-standards protocol. All verification evidence is in this folder.*
