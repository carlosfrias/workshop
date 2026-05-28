---
name: test-tier-qwen35
summary: Validate qwen3.5:4b as low-tier model for decompose-execute-verify workloads
status: complete
phase: "Phase 1: Testing"
progress: 100
tracked: false
---

# Current Focus — test-tier-qwen35

**Status:** complete
**Last session:** 2026-05-22 15:30

## Active Work

- ✅ **qwen3:14b tested — NON-VIABLE**
  - 1.4 tok/s, mandatory reasoning, 116s for "say hello"
  - Removed from all model-router high-tier slots
  - See: [journal/2026-05-22-1500.md](journal/2026-05-22-1500.md)
- ✅ **qwen3:8b staged test complete — VIABLE (single-threaded)**
  - Stage 1 (baseline): 71.7s, 22.2 tok/s, good quality
  - Stage 2 (single subagent): 115.9s, 4 tool uses, all worked
  - Stage 3 (2 concurrent): 625-664s, stable but 5.4× slowdown
- ✅ **model-router.json updated** — gemma4:e4b → high tier, qwen3:8b → auto medium tier

## Session Handoff

- qwen3:14b is a dead end on M1 Pro 16GB — model-router.json purged of all references
- qwen3:8b works but the mandatory thinking phase (79% token overhead) limits it to single-threaded use
- gemma4:e4b confirmed as primary local model — no thinking overhead, proven concurrent performance
- Full local tier lineup: gemma4:e4b (high), qwen3:8b (medium-single), qwen3.5:4b (low)

## Key Findings for Next Agent

1. **qwen3 series has forced reasoning** — both 14b and 8b models burn 75-79% of tokens on thinking before response
2. **14b is unusable, 8b is marginal** — usable only when concurrency isn't needed
3. **gemma4:e4b dominates** — no thinking tax, 183s avg for 3-agent concurrent DE
4. Consider removing qwen3:14b (`ollama rm qwen3:14b`) to free 9.3 GB disk

## Blocked / Needs Decision

{Nothing — project findings complete. Route to close session if done.}


---

> 📋 **Checkbox states:** `[ ]` To Do | `[/]` In Progress | `[~]` Good Enough | `[x]` Done | `[>]` Deferred | `[!]` Blocked | `[-]` Cancelled — [full legend](../../../personal-vault/01-Projects/doc-standards/wiki/doc-standards/reference/Checkbox-State-Legend.md)
*Last updated: 2026-05-27*
