---
title: decomposition-skill
description: Cost-optimized task execution via decompose-execute-verify
---

# decomposition-skill

**Type:** Skill  
**Install:** `pi install github:carlosfrias/decomposition-skill`

Cost-optimized task execution through intelligent decomposition and verification. Reduce cloud model costs by **75-85%**.

## Pattern

```
User Prompt → Decomposer (cloud) → Local Model Execution → Verifier (cloud) → Final Output
    ~$0.03                    ~$0.00                      ~$0.02         Total: ~$0.05
```

Compare to cloud end-to-end: **~$0.25–0.30** for multi-turn complex tasks.

## Agents

| Agent | Model | Role |
|-------|-------|------|
| `decomposer` | `ollama/qwen3.5:cloud` | Break tasks into atomic sub-tasks |
| `verifier` | `ollama/qwen3.5:cloud` | Validate local model output |

## Chains

| Chain | Purpose |
|-------|---------|
| `decomposed-monitor-to-log` | Monitor positions and log status |
| `decomposed-trade-to-log` | Execute trades and log them |

## When to Use

✅ **Good:** Structured data pipelines, monitoring, multi-step workflows with clear steps  
❌ **Poor:** Tasks requiring judgment between steps, exploratory analysis, creative synthesis

## Repository

[github.com/carlosfrias/decomposition-skill](https://github.com/carlosfrias/decomposition-skill)
