---
name: test-tier-9b-mlx
summary: Benchmark 9B + MLX variants for local model tier classification
status: active
phase: "Phase 1: Testing"
progress: 0
tracked: true
---

# Current Focus — test-tier-9b-mlx

**Last session:** 2026-05-22 — Cleanup complete, testing starts now

### Active work
1. **Test qwen3.5:9b** (GGUF, Q4_K_M, 6.6 GB, 262K ctx)
2. **Test qwen3.5:9b-mlx** (MLX, nvfp4, 8.9 GB, 262K ctx)
3. **Test gemma4:e4b-mlx** (MLX, nvfp4, 9.6 GB, 131K ctx— no vision)

### Cleanup done
- ✅ Removed qwen3:14b from models.json (already deleted from ollama)
- ✅ Fixed cloud model contextWindow values against actual ollama show specs
- ✅ Fixed cloud model input arrays (added image where vision capability exists)
- ✅ models.json validated

### Blocked / needs decision
- 262K context on 9b models may cause same freeze as qwen3.5:4b. Using maxTokens 4096 as mitigation.

---

> 📋 **Checkbox states:** `[ ]` To Do | `[/]` In Progress | `[~]` Good Enough | `[x]` Done | `[>]` Deferred | `[!]` Blocked | `[-]` Cancelled — [full legend](../../../personal-vault/01-Projects/doc-standards/wiki/doc-standards/reference/Checkbox-State-Legend.md)
*Last updated: 2026-05-27*
