# Decompose → Execute → Verify Pattern

A cost-optimized architecture for running complex tasks using a mix of cloud and local models.

## Overview

Use a high-reasoning cloud model to **decompose** a complex task into simple sub-tasks, execute those sub-tasks on **local models**, then **verify** the output with a cloud model before it becomes authoritative.

```
┌────────────────┐     ┌──────────────────────┐     ┌──────────────┐
│  Decompose     │────▶│  Execute (local)     │────▶│  Verify      │
│  (cloud)       │     │  (gemma4/qwen3)      │     │  (cloud)     │
│                │     │                      │     │              │
│  Complex task  │     │  Sub-task 1          │     │  Check       │
│  → sub-tasks   │     │  Sub-task 2          │     │  correctness,│
│  → dependencies│     │  Sub-task 3          │     │  completeness│
│  → expected    │     │  ...                 │     │  accuracy    │
│    outputs     │     │                      │     │              │
└────────────────┘     └──────────────────────┘     └──────────────┘
   ~$0.03               ~$0.00                      ~$0.02
```

## Cost Comparison

| Approach                         | Relative Cost  | Token Profile                                             |
| -------------------------------- | -------------- | --------------------------------------------------------- |
| Cloud end-to-end                 | 1.0×           | Full task × every turn                                    |
| Static chains                    | 0.3–0.5×       | Only reasoning-heavy steps on cloud                       |
| **Decompose → Execute → Verify** | **0.15–0.25×** | Decomposition + verification on cloud, execution on local |

## When to Use

### ✅ Good Candidates

| Pattern | Example |
|---------|---------|
| Structured data pipelines | "Fetch April trades, compute P&L, flag violations" |
| Monitoring & reporting | "Give me portfolio risk summary with limit checks" |
| Multi-step workflows with clear steps | "Read positions, calculate exposure, compare to limits, log status" |
| Tasks where the path can be planned in advance | Any task with deterministic sub-steps |

### ❌ Poor Candidates

| Pattern | Why It Fails |
|---------|-------------|
| Tasks requiring judgment between steps | Step 2 depends on nuanced interpretation of Step 1 |
| Tightly coupled reasoning | Can't decompose without losing context |
| Exploratory analysis | The path isn't known in advance |
| Creative synthesis | Requires holistic understanding |

## Agents

| Agent | Model | Role |
|-------|-------|------|
| `decomposer` | `ollama/qwen3.5:cloud` | Breaks complex tasks into atomic sub-tasks |
| `verifier` | `ollama/qwen3.5:cloud` | Validates local model output before it becomes authoritative |

## Chains

| Chain | Pipeline | Cost Profile |
|-------|----------|--------------|
| `decomposed-monitor-to-log` | decomposer → position-monitor → verifier → bookkeeping | Local execution, cloud gates |
| `decomposed-trade-to-log` | decomposer → position-management → verifier → bookkeeping | Hybrid execution, cloud gates |

## Decomposition Output Format

The decomposer produces a structured plan:

```markdown
## Decomposition Plan

### Overview
[1-2 sentence summary]

### Sub-Tasks

| # | Task | Target Agent | Rationale | Expected Output |
|---|------|--------------|-----------|-----------------|
| 1 | [atomic instruction] | [agent] | [why] | [what good looks like] |

### Dependencies
[None or explicit dependencies]

### Verification Criteria
[What the verifier should check]
```

## Verification Output Format

The verifier produces a report:

```markdown
## Verification Report

### Task
[Original sub-task]

### Agent
[Which agent produced output]

### Checks

| Criterion | Status | Notes |
|-----------|--------|-------|
| [Criterion 1] | ✅ Pass / ❌ Fail / ⚠️ Partial | [finding] |

### Overall Result
**PASS** / **FAIL** / **PARTIAL**

### Recommended Action
[Accept, re-run with cloud, or accept with caveats]
```

## Local Model Failure Modes

The verifier watches for:

| Failure Mode | Example | Detection |
|-------------|---------|-----------|
| Hallucinated numbers | Made-up P&L figures | Cross-check against source data |
| Missing required fields | Trade log without timestamp | Schema validation |
| Format drift | Wrong date format, missing units | Pattern matching |
| Incomplete extraction | Skipped edge cases | Count verification |
| Arithmetic errors | Multi-step calculation mistakes | Spot-check math |

## Integration with Model Router

The model router (` .pi/model-router.json`) handles **automatic model selection** based on prompt keywords. The decomposition pattern adds **preprocessing** (decompose) and **postprocessing** (verify) around the router's execution flow.

```
User Prompt
     │
     ▼
┌─────────────┐
│  Model      │ ← Router selects model based on keywords
│  Router     │
└─────────────┘
     │
     ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  If complex │────▶│  Decompose   │────▶│  Execute    │
│  task       │     │  (cloud)     │     │  (routed)   │
└─────────────┘     └──────────────┘     └─────────────┘
                                                │
                                                ▼
                                         ┌─────────────┐
                                         │  Verify     │
                                         │  (cloud)    │
                                         └─────────────┘
                                                │
                                                ▼
                                           Final Output
```

For routine tasks, the router handles everything. For complex multi-step tasks, invoke a decomposed chain explicitly.

## Usage

### Direct Chain Invocation

```bash
# Use a decomposed chain explicitly
/subagent decomposed-monitor-to-log "Check portfolio exposure and log status"
```

### Via Orchestrator

The orchestrator can decide to use decomposition based on task complexity. This is typically done through prompt engineering or by having the orchestrator recognize when a task spans multiple domains.

## Design Notes

### Why Two Cloud Calls?

Decomposition and verification are each **single, short calls** (~$0.02–0.03 each). The bulk of token spend (long context, multi-turn tool use, iteration) moves to local models at near-zero cost.

### Why Not Just Use Cloud End-to-End?

For tasks that would require multiple cloud turns, the decomposed pattern is **4–6× cheaper** while maintaining quality through the verification gate.

### Why Not Skip Verification?

Without verification, local model errors propagate silently. The verification gate catches hallucinations, omissions, and formatting issues before they become authoritative — using a fraction of the tokens that full cloud execution would require.

## See Also

- [Model Assignment Strategy](/model-assignment-strategy) — Rationale for routing tasks to specific models
- [Trading Desk Wiki: Agent Definitions](/trading-desk/agents) — Full agent configurations
- [Trading Desk Wiki: Chain Files](/trading-desk/chains) — Multi-step workflow definitions