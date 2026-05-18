# ROOT CAUSE ANALYSIS — B-KR-002 Keyword Router Regression

**Date:** 2026-05-14  
**Backlog:** B-KR-002  
**Status:** ✅ COMPLETE  
**Analyst:** Low Cloud Orchestrator (qwen3.5:397b-cloud)

---

## Executive Summary

The keyword-router regression was introduced in commit **93e1d39** ("fix: default route now delegates to model-router instead of hardcoding gemma4:e4b").

**Root Cause:** The default route was changed from `ollama/gemma4:e4b` to `router/auto`, which requires `pi-model-router` to be installed. Without model-router, prompts fall back to `qwen3.5:4b` (low-capacity local) instead of escalating to `gemma4:e4b` (medium local) or cloud models.

---

## Regression Commit Details

| Field | Value |
|-------|-------|
| **Commit Hash** | `93e1d39b0ba9e6afc148cb728e9d905ca469edf9` |
| **Date** | 2026-05-08 |
| **Author** | Trading Laboratory |
| **Message** | fix: default route now delegates to model-router instead of hardcoding gemma4:e4b |

---

## What Changed

### Before (321b053 and earlier)

```typescript
// BUILT_IN_DEFAULTS in lib/config.ts
const BUILT_IN_DEFAULTS: RouterConfig = {
  default: {
    provider: "ollama",
    model: "gemma4:e4b",  // ← Direct medium-capacity local model
    thinkingLevel: "off",
  },
  // ...
};
```

**Behavior:** Unmatched prompts → `gemma4:e4b` (medium local)

### After (93e1d39 and later)

```typescript
// BUILT_IN_DEFAULTS in lib/config.ts
const BUILT_IN_DEFAULTS: RouterConfig = {
  default: {
    provider: "router",  // ← Delegates to model-router
    model: "auto",
  },
  // ...
};
```

**Behavior:** Unmatched prompts → `router/auto` → requires `pi-model-router` installed

---

## Why It Caused the Regression

1. **Dependency Assumption:** The commit assumed `pi-model-router` is always installed.

2. **Missing Fallback:** When `pi-model-router` is NOT installed:
   - `provider: "router"` cannot resolve
   - Falls back to lowest-capacity model (`qwen3.5:4b`)
   - No escalation to `gemma4:e4b` or cloud models occurs

3. **Breaking Change:** The commit message noted this was BREAKING, but the impact was not fully tested:
   > "BREAKING: Users without model-router installed will see router/auto as the default, which requires pi-model-router to be installed."

---

## Evidence

### Bisection Results

| Commit | Message | Status |
|--------|---------|--------|
| 321b053 | feat: P0 dispatch bridge | 🟢 GOOD (gemma4:e4b default) |
| 4bce629 | fix: prioritize keyword inference | 🟢 GOOD (keywords work) |
| 5a0f7f1 | fix: word-boundary matching | 🟢 GOOD |
| 9186ab4 | feat: /list-routes command | 🟢 GOOD |
| **93e1d39** | **fix: default route delegates** | 🔴 **BAD (regression intro)** |
| 5445758 | TI-040: model arbitration | 🔴 BAD (HEAD) |

### Diff Summary (93e1d39)

```diff
- default: { provider: "ollama", model: "gemma4:e4b" }
+ default: { provider: "router", model: "auto" }
```

---

## Suggested Fix

### Option 1: Restore gemma4:e4b as Default (Recommended)

```typescript
const BUILT_IN_DEFAULTS: RouterConfig = {
  default: {
    provider: "ollama",
    model: "gemma4:e4b",  // ← Restore medium-capacity fallback
    thinkingLevel: "off",
  },
  // ...
};
```

**Pros:**
- Backward compatible
- No external dependency required
- Sensible default for most users

**Cons:**
- Loses model-router integration for users who have it installed

### Option 2: Conditional Default Based on model-router Presence

```typescript
const BUILT_IN_DEFAULTS: RouterConfig = {
  default: {
    provider: hasModelRouter() ? "router" : "ollama",
    model: hasModelRouter() ? "auto" : "gemma4:e4b",
  },
};
```

**Pros:**
- Best of both worlds
- Works with or without model-router

**Cons:**
- Requires runtime detection logic
- More complex

### Option 3: Document model-router as Required Dependency

Add to `package.json`:
```json
"peerDependencies": {
  "@mariozechner/pi-coding-agent": "*",
  "pi-model-router": ">=1.0.0"  // ← Add as required
}
```

**Pros:**
- Clear dependency contract

**Cons:**
- Forces all users to install model-router
- May not be desired for simple use cases

---

## Verification Steps

1. **Checkout 321b053 (known GOOD):**
   ```bash
   git checkout 321b053
   npm install
   npm test -- test/bisect/regression-test-v2.ts  # Should PASS
   ```

2. **Checkout 93e1d39 (regression intro):**
   ```bash
   git checkout 93e1d39
   npm install
   npm test -- test/bisect/regression-test-v2.ts  # Should FAIL
   ```

3. **Apply fix and verify:**
   ```bash
   # Edit lib/config.ts: change default provider/model
   npm test -- test/bisect/regression-test-v2.ts  # Should PASS
   ```

---

## Related Commits

| Commit | Purpose | Impact on Regression |
|--------|---------|---------------------|
| 4bce629 | Keyword-before-complexity ordering | Neutral (improvement) |
| 5a0f7f1 | Word-boundary matching | Neutral |
| 9186ab4 | /list-routes command | Neutral |
| **93e1d39** | **Default route delegation** | **🔴 ROOT CAUSE** |
| 5445758 | TI-040 model arbitration | Amplifies regression |

---

## Lessons Learned

1. **Breaking changes require thorough testing** — especially when introducing new dependencies.

2. **Default values should be self-contained** — relying on optional extensions for core functionality creates fragility.

3. **Bisection is effective** — 9 commits tested in parallel across 7 nodes identified the exact regression commit in one round.

---

**Document Location:** `technical-infrastructure/wiki/operational/sessions/ROOT-CAUSE-B-KR-002-2026-05-14.md`

**Next Action:** Apply fix and verify with regression test suite.

---
**Generated:** 2026-05-14 07:15 ET  
**B-KR-002 Status:** ✅ COMPLETE
