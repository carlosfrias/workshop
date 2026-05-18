# Troubleshooting Plan: Keyword Router Bisection

**Issue:** keyword-router-regression  
**Date:** 2026-05-13  
**Status:** ✅ Complete — regression identified and fixed  
**Investigator:** Low Cloud Orchestrator (qwen3.5:397b)

---

## [S-TIGHT]

Parallel git bisection across 7 lab nodes to identify the exact commit where keyword-router stopped escalating to higher-capacity models. Range: 9 commits between known-good (`ffc3c2f`) and known-bad (`5445758`). Result: commit `93e1d39` introduced the regression.

---

## Hypotheses

### H1: Regression in pi-keyword-router classifier logic
The classifier that maps keywords to models was modified to always select the lowest tier.

### H2: Regression in pi-keyword-router config defaults
The default fallback model was changed from a medium-tier to a low-tier model.

### H3: Regression in routing-transparency display
The footer shows the wrong model even if the router selected the correct one.

### H4: Regression in orchestrator config
The Mac's runtime config overrides the package defaults.

---

## Investigation Steps

### Step 1: Establish Baseline (fnet3)
- Find known-good commit
- List commits in regression range
- Define deterministic regression test

### Step 2: Parallel Bisection (fnet1–fnet7)
- Round 1: 7 commits → all showed GOOD for model selection
- Round 2: Narrowed range (321b053 → 4bce629) → all still GOOD
- Round 3: Identified `93e1d39` as first BAD commit

### Step 3: Root Cause Analysis (fnet3)
- Diff `93e1d39` to see what changed
- Identify exact function/line: `lib/config.ts:39-42`
- What changed: `provider: "router", model: "auto"` → fell back to `qwen3.5:4b`

---

## Evidence

| Commit | Message | Status | Notes |
|--------|---------|--------|-------|
| 321b053 | feat: P0 dispatch bridge | 🟢 GOOD | Selects gemma4:e4b for reasoning |
| 4bce629 | fix: prioritize keyword inference | 🟢 GOOD | Selects gemma4:e4b for reasoning |
| 5a0f7f1 | fix: word-boundary matching | 🟢 GOOD | Selects gemma4:e4b for reasoning |
| 9186ab4 | feat: /list-routes command | 🟢 GOOD | Selects gemma4:e4b for reasoning |
| **93e1d39** | **fix: default route delegates** | **🔴 BAD** | **First commit where model falls back to qwen3.5:4b** |
| 5445758 | TI-040: model arbitration | 🔴 BAD | Current HEAD (also broken) |

---

## Key Finding

**Hypothesis H2 was correct.** The regression was in the config defaults, not the classifier logic.

```diff
  const BUILT_IN_DEFAULTS: RouterConfig = {
     default: {
-        provider: "ollama",
-        model: "gemma4:e4b",
+        provider: "router",
+        model: "auto",
         thinkingLevel: "off",
     },
```

When `provider: "router"` is used but `pi-model-router` is not installed, the resolution fails and falls back to the lowest-capacity model (`qwen3.5:4b`).

---

## Related Documents

- **Analysis:** [1-analysis.md](1-analysis.md)
- **Resolution:** [2-resolution.md](2-resolution.md)
- **Decomposition:** [decompositions/DECOMP-B-KR-002-2026-05-13.md](../decompositions/DECOMP-B-KR-002-2026-05-13.md)
- **Refined dispatch:** [decompositions/B-KR-002-REFINED-DISPATCH-2026-05-13.md](../decompositions/B-KR-002-REFINED-DISPATCH-2026-05-13.md)

---

*This troubleshooting plan follows the doc-standards protocol. All investigation artifacts are in this folder.*
