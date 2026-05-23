# PLAN — test-tier-gemma4

## [S-TIGHT]
Threshold evidence research for gemma4:e4b as local high-tier model.

---

## Goal

**Validate gemma4:e4b (9.6 GB, 131K context) as the high-tier local model for decompose-execute-verify orchestrated workloads on M1 Pro / 16 GB RAM.**

## Context: Why This Test Exists

qwen3.5:4b failed catastrophically as the low-tier model (machine lockup, 1200s+). Gemma4 is the candidate for high-tier, but at 9.6 GB it's 2.8x heavier than qwen3.5. The open question: does its tighter 131K context window offset the larger model size?

## Key Threshold Questions

| # | Question | Current Config |
|---|----------|---------------|
| 1 | Can gemma4:e4b run DE orchestrated workloads on 16 GB without swapping? | `contextWindow: 131072`, `maxTokens: 32000` |
| 2 | Is `maxTokens: 32000` appropriate? (guide says 8192) | 4x over guide recommendation |
| 3 | Does thinking mode ("high") cause excessive token generation under DE? | `thinking: high` in auto profile |
| 4 | At what subagent count does memory pressure cross the critical threshold? | TBD |

## Baseline Health (Pre-Test Snapshot)

Captured 2026-05-22 11:52 — machine still recovering from qwen3.5 abort:
- RAM: 92.6%, Swap: 4,554 MB, CPU: 22.1%, Load: 30.92
- **HALT** — no model tests until health recovers

## Phases

| Phase | Status | Description |
|-------|--------|-------------|
| 0 | ✅ Done | Project scaffolded |
| 1 | ⏳ Blocked | Wait for health recovery (RAM <80%, swap 0) |
| 2 | Not started | Config audit: verify maxTokens, contextWindow vs guide |
| 3 | Not started | Single-model control test (no subagents, small prompt) |
| 4 | Not started | DE orchestrated test (2 subagents: decomposer + verifier) |
| 5 | Not started | DE full test (3 subagents: decomposer + dispatcher + verifier) |
| 6 | Not started | Results compilation + config fix recommendations |

## Config Under Test

From `models.json`:
- `id: gemma4:e4b`, 9.6 GB Q4_K_M, 131K context, maxTokens: 32000
- `reasoning: true`, `input: ["text", "image"]`

MAX-TOKENS-GUIDE recommendation for gemma4:e4b: `maxTokens: 8192`

## Related

- [test-tier-qwen35](../test-tier-qwen35/) — companion test (failed)
- [/Users/friasc/.pi/agent/models.json](/Users/friasc/.pi/agent/models.json)
- [health-monitor](/Users/friasc/.pi/agent/skills/health-monitor/)
