# Root Cause Analysis: Keyword Router Regression

**Issue:** keyword-router-regression  
**Investigation Phase:** B-KR-002 — Lab Node Bisection  
**Date:** 2026-05-13  
**Analyst:** Low Cloud Orchestrator + Lab Nodes fnet1–fnet7

---

## [S-TIGHT]

Regression commit `93e1d39` changed `BUILT_IN_DEFAULTS` from `ollama:gemma4:e4b` to `router:auto`, causing unresolvable default route fallback to `qwen3.5:4b` when `pi-model-router` is absent.

---

## Regression Commit

```
commit 93e1d39b0ba9e6afc148cb728e9d905ca469edf9
Author: [redacted]
Date:   2026-05-08

    fix: default route now delegates to model-router instead of hardcoding gemma4:e4b
```

## What Changed

### Before (GOOD)
```typescript
const BUILT_IN_DEFAULTS: RouterConfig = {
    default: {
        provider: "ollama",
        model: "gemma4:e4b",
        thinkingLevel: "off",
    },
    routes: { ... }
};
```

### After (BAD)
```typescript
const BUILT_IN_DEFAULTS: RouterConfig = {
    default: {
        provider: "router",
        model: "auto",
        thinkingLevel: "off",
    },
    routes: { ... }
};
```

## Why It Caused the Regression

**Design assumption that failed:**
> "If we default to `router:auto`, the model-router will handle all default routing automatically."

**Reality:**
- `pi-model-router` is an optional extension, not required.
- When `provider: "router"` is specified but `pi-model-router` is not installed, the resolution fails silently.
- The fallback mechanism in pi's routing layer selects the lowest-capacity available model (`qwen3.5:4b`) as a safe default.
- Result: ALL prompts, regardless of complexity, get `qwen3.5:4b`.

**Impact scope:**
- All keyword routes that fall through to the default (which is most of them, since only exact matches get keyword-routed).
- Reasoning prompts (`"analyze risk for NVDA"`) that should get `gemma4:e4b` or cloud models.
- Infrastructure prompts that should get `gemma4:e4b`.
- Only explicitly-matched keyword routes (structured, monitoring with exact keyword matches) still work correctly.

## Evidence

### Bisection Results

| Commit | Status | Model for "analyze risk" |
|--------|--------|--------------------------|
| 321b053 | 🟢 GOOD | gemma4:e4b |
| 4bce629 | 🟢 GOOD | gemma4:e4b |
| 5a0f7f1 | 🟢 GOOD | gemma4:e4b |
| 9186ab4 | 🟢 GOOD | gemma4:e4b |
| **93e1d39** | **🔴 BAD** | **qwen3.5:4b** |
| 5445758 | 🔴 BAD | qwen3.5:4b |

### Git Diff

```diff
diff --git a/lib/config.ts b/lib/config.ts
index c81b8fd..b8be58f 100644
--- a/lib/config.ts
+++ b/lib/config.ts
@@ -37,8 +37,8 @@ function projectConfigPath(cwd: string): string {
  */
 const BUILT_IN_DEFAULTS: RouterConfig = {
 	default: {
-		provider: "router",
-		model: "auto",
+		provider: "ollama",
+		model: "gemma4:e4b",
 		thinkingLevel: "off",
 	},
 	routes: {
```

## Suggested Prevention

1. **CI Regression Test:** Add a test that verifies the default model for a reasoning prompt is NOT `qwen3.5:4b`.
2. **Config Guard:** Validate `provider: "router"` only if `pi-model-router` is installed; otherwise fall back to `ollama:gemma4:e4b`.
3. **Deprecate `router:auto`:** Remove the option or make it explicitly opt-in.

## Related

- **Troubleshooting Plan:** [0-PLAN.md](0-PLAN.md)
- **Resolution:** [2-resolution.md](2-resolution.md)
- **Bisection Decomposition:** [decompositions/DECOMP-B-KR-002-2026-05-13.md](../decompositions/DECOMP-B-KR-002-2026-05-13.md)
- **Fix Commit:** `ee1e679` in `pi-keyword-router` repo

---

*This analysis follows the doc-standards protocol. All evidence is in this folder or linked.*
