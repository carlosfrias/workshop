# PLAN — test-tier-qwen35

## [S-TIGHT]
Retroactive plan — project scaffolded 2026-05-22, test executed same day, results captured post-hoc.

---

## Goal

**Validate qwen3.5:4b as the low-tier model in model-router.json for decompose-execute-verify orchestrated workloads on M1 Pro / 16 GB RAM.**

## What We Were Testing

The `models.json` had qwen3.5:4b configured with:
- `contextWindow: 262144` (matches ollama show — technically correct per MODELS-SPEC)
- `maxTokens: 16000` (4x the MAX-TOKENS-GUIDE recommendation of 4096)
- `reasoning: true`, `thinking: off` in the low tier

The test was to determine whether these settings produce stable, usable behavior when qwen3.5:4b is called as the low-tier model in a decompose-execute-verify pipeline with subagent spawning (decomposer → fleet-dispatcher → verifier).

The specific threshold questions:
1. Can qwen3.5:4b handle 262K context on 16 GB RAM under orchestrated load?
2. Is `maxTokens: 16000` appropriate, or should it be lowered per the guide's 4096 recommendation?
3. Does the model remain responsive when spawned as a subagent in the DE framework?

## Phases

| Phase | Status | Notes |
|-------|--------|-------|
| 1. Config audit | ✅ Done | Identified discrepancy: maxTokens 16000 vs guide's 4096 |
| 2. Orchestrated DE test | ❌ ABORTED | Machine unresponsive for 1200s+ — qwen3.5 saturated RAM |
| 3. Config correction | ✅ Done | maxTokens lowered to 4096 |
| 4. RETEST (maxTokens 4096) | ✅ PASSED | 3/3 agents completed 81-424s, machine responsive |
| 5. Cross-model comparison | ✅ Done | gemma4:e4b also tested — 3/3 completed 134-222s |
| 6. qwen3:14b test | ❌ NON-VIABLE | 1.4 tok/s, mandatory reasoning, 116s for "hello" — dead end |
| 7. qwen3:8b staged test | ✅ COMPLETE | 3-stage: baseline 71.7s, single subagent 115.9s, concurrent 625-664s |

## Results

### Phase 4: RETEST with maxTokens 4096 — PASSED ✅

- **Machine:** Apple M1 Pro, 16 GB unified memory (baseline: 87% RAM, 5.2 GB swap)
- **Model:** qwen3.5:4b (3.4 GB, 262K context, maxTokens: 4096)
- **Framework:** DE full — 3 concurrent subagents
- **Outcome:** All 3 agents completed (81s, 368s, 424s). Machine responsive throughout.
- **Key finding:** maxTokens was the root cause of original freeze, NOT context window.
  - Context window usage never exceeded 6% of 262K
  - Excessive maxTokens (16000) caused memory allocation spikes during output
  - With maxTokens 4096, qwen3.5 is viable but 59% slower than gemma4 on average

### Cross-Model Comparison (Phase 5)

| | qwen3.5 (old) | qwen3.5 (fixed) | gemma4:e4b |
|---|-------------|-----------------|------------|
| Completed | 0/3 ❌ | 3/3 ✅ | 3/3 ✅ |
| Avg duration | ∞ | 291s | 183s |
| Model size | 3.4 GB | 3.4 GB | 9.6 GB |
| Context window | 262K | 262K | 131K |

**Recommendation:** gemma4:e4b for primary DE workloads; qwen3.5:4b as fallback low-tier.

## Next Steps

1. ~~qwen3.5 control test~~ — SKIPPED (retest proved maxTokens was the issue, not concurrency)
2. ✅ gemma4:e4b evaluated — recommended as primary
3. ✅ qwen3:14b tested — NON-VIABLE (1.4 tok/s, 116s for "hello")
4. ✅ qwen3:8b tested — viable single-threaded (22.2 tok/s), 5.4× concurrency slowdown
5. model-router.json updated: gemma4:e4b → high tier, qwen3:8b → auto medium tier
6. Consider removing qwen3:14b from disk to free 9.3 GB

## Related

- [journal/2026-05-22-0928.md](journal/2026-05-22-0928.md) — session log with full findings
- [journal/2026-05-22-1500.md](journal/2026-05-22-1500.md) — qwen3:14b and qwen3:8b test session
- [domain-validation/Activity Log.md](domain-validation/Activity Log.md) — evidence recorded
- [/Users/friasc/.pi/agent/models.json](/Users/friasc/.pi/agent/models.json) — config fix applied, qwen3:14b flagged non-viable
- [/Users/friasc/.pi/agent/model-router.json](/Users/friasc/.pi/agent/model-router.json) — tier assignments updated
- [MAX-TOKENS-GUIDE.md](../local-model-pilot/skills/local-model-pilot/MAX-TOKENS-GUIDE.md) — threshold reference

---

### Phase 6: qwen3:14b test — NON-VIABLE ❌

- **Machine:** Apple M1 Pro, 16 GB unified memory (baseline: 15G used, 79M free)
- **Model:** qwen3:14b (9.3 GB, 40K context, maxTokens: 8192)
- **Result:** 1.4 tok/s, mandatory built-in reasoning cannot be disabled
  - 116s for "say hello" (161 tokens, 75% wasted on thinking)
  - 300s+ timeout on code analysis (never escaped thinking phase)
  - ~63× slower than gemma4:e4b for equivalent tasks
- **Root cause:** qwen3:14b has forced reasoning that consumes ~75% of output tokens. On M1 Pro 16GB, the model is compute-bound at 1.4 tok/s.
- **Verdict:** Dead end. Remove from disk to free 9.3 GB.

### Phase 7: qwen3:8b staged test — VIABLE (with caveats) ✅

**Machine state:** 15G used, 234M free at start. Ollama runner shared 7GB between concurrent instances.

| Stage | Test | Time | Tokens | Tool Uses | Result |
|-------|------|------|--------|-----------|--------|
| 1. Baseline | Direct API (code analysis) | 71.7s | 1,565 | — | 22.2 tok/s, good quality |
| 2. Single subagent | 1 agent + tools | 115.9s | 25.4k | 4 | All tools worked |
| 3. Concurrent (2) | 2 parallel subagents | 625s / 664s | 40.4k / 28.6k | 5 / 4 | Stable, no crashes |

**Key findings:**
- **Speed:** 22.2 tok/s single-threaded — 16× faster than qwen3:14b, comparable to gemma4
- **Thinking tax:** Mandatory thinking phase consumes ~79% of generated tokens before response output
- **Concurrency degradation:** 5.4× slowdown from single (115s) to concurrent (~640s). Both agents compete for the same ollama runner compute.
- **Stability:** Machine responsive throughout all stages. No swap explosion. Ollama runner at 7GB shared.
- **Quality:** Code analysis identified 6 valid bugs/optimizations. Structured output, no hallucinations.

**Recommendation:** qwen3:8b assigned to `auto` medium tier (single-threaded moderate tasks). Not suitable for concurrent DE workloads — gemma4:e4b remains primary. Also serves as `fast` profile high tier.

### Updated Cross-Model Comparison

| | qwen3:14b | qwen3:8b | qwen3.5:4b (fixed) | gemma4:e4b |
|---|-----------|----------|--------------------|-------------|
| Stage 1 (baseline) | 300s+ ❌ | 71.7s ✅ | N/A | N/A |
| Stage 2 (single agent) | N/A | 115.9s ✅ | ~291s avg* | ~183s avg* |
| Stage 3 (concurrent) | N/A | 625-664s ⚠️ | 81-424s ✅ | 134-222s ✅ |
| Speed (tok/s) | 1.4 | 22.2 | N/A | N/A |
| Thinking overhead | 75% (forced) | 79% (forced) | None (opt-in) | None |
| Model size | 9.3 GB | 5.2 GB | 3.4 GB | 9.6 GB |
| Viability | ❌ | ⚠️ (single only) | ✅ (low tier) | ✅ (primary) |

*Full DE pipeline: decomposer → 3 concurrent agents → verifier
