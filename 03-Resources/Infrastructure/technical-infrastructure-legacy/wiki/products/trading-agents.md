---
title: trading-agents
description: Reusable agent definitions for decompose-execute-verify
---

# trading-agents

**Type:** Agent Package  
**Install:** `pi install github:carlosfrias/trading-agents`

Reusable agent definitions for the **decompose-execute-verify** pattern.

## Agents

### decomposer

**Model:** `ollama/qwen3.5:cloud`  
**Role:** Break complex tasks into atomic sub-tasks for local model execution

Takes a complex prompt and produces a structured decomposition plan with:
- Atomic sub-tasks
- Target agent for each sub-task
- Dependencies between sub-tasks
- Verification criteria

### verifier

**Model:** `ollama/qwen3.5:cloud`  
**Role:** Validate local model output for correctness before it becomes authoritative

- Receives output from local model execution
- Checks against verification criteria
- Produces pass/fail/partial report
- Recommends action (accept, re-run with cloud, accept with caveats)

## Usage in Chains

```yaml
steps:
  - agent: decomposer
    task: "Decompose: {task}"
  - agent: position-monitor
    task: "Execute: {previous}"
  - agent: verifier
    task: "Verify: {previous}"
  - agent: bookkeeping
    task: "Log: {previous}"
```

## Repository

[github.com/carlosfrias/trading-agents](https://github.com/carlosfrias/trading-agents)
