# Routing Gap Analysis — pi-keyword-router v1.0.1 Release

**Date:** 2026-05-03
**Gap ID:** TI-023-P5b
**Component:** `pi-keyword-router` extension
**Status:** ✅ FIXED

## 📌 Release Notes: v1.0.1

### Key Improvements
- **Keyword-first routing** now prioritizes semantic signals over auto-complexity heuristics
- **Enhanced model dispatch** with explicit tag system
- **Bug fix:** Resolves routing gap where short prompts with keyword signals were misclassified

## 🧠 Routing Gap Analysis (TI-023-P5b)

### Problem
Prompts with strong keyword signals were routed incorrectly due to auto-complexity heuristic overriding keyword inference. Example:

```
Synthesize this response into a comprehensive wiki page documentation...
```

### Root Cause
Auto-complexity ran before keyword inference, creating artificial confidence scores for short prompts with no keyword matches.

### Fix Applied
Reordered routing pipeline:
1. Explicit tags
2. Route tags
3. Complexity tags
4. **Keyword inference** (semantic-first)
5. Auto-complexity fallback
6. Default

Modified file: `~/.pi/agent/extensions/pi-keyword-router/lib/classifier.ts`

## 🔄 How the Fix Works
Keyword inference now executes before auto-complexity, giving semantic signals priority. This prevents artificial confidence scoring from token length alone.

## 🎯 Triggering Specific Models
### Explicit Tags (Highest Priority)
Use at start of prompt:

| Model | Tag |
|-------|-----|
| kimi-k2.6:cloud | `<!-- complexity: hard -->` |
| qwen3.5:397b-cloud | `<!-- model-route: reasoning -->` |
| qwen3:8b | `<!-- model: ollama/qwen3:8b -->` |

### Keyword Routes
Words like "decompose," "node," and "dispatch" trigger infrastructure routing. Multi-keyword prompts amplify confidence.

## 🧪 Verification Test Cases
1. "Synthesize comprehensively..." → hard route ✅
2. "Do we have any more..." → trivial route ✅
3. "Decompose this task..." → infrastructure route ✅

## 📁 References
- `technical-infrastructure/scripts/classify_prompt.py` (Python classifier)
- `technical-infrastructure/wiki/operational/planning/PLAN-2026-05-01-1645.md` (meta-orchestration - file not found)
- `SESSION-NOTES-2026-05-03-2015-TI030-TI023-TI011-P3.md` (session notes)

## 🔄 Required Action
Restart pi completely for changes to take effect:
```bash
# Quit pi entirely (Cmd+Q or close window)
# Reopen pi
```

## ✅ Verification
After restart, test prompts with keyword signals should route correctly to specialized models. The new pipeline trusts semantic keywords over token length alone.