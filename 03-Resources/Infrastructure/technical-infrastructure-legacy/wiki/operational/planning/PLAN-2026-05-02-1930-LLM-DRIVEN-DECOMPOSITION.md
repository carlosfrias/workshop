# Planning: Recursive LLM-Driven Decomposition with Tiered Fallback
**Date:** 2026-05-02 19:30  
**Status:** Architectural design — ready for implementation  
**Context:** Current decomposition uses static templates with generic sub-tasks. User wants intelligent, prompt-specific decomposition using cloud models as "smart splitters" while minimizing cloud spend by pushing all execution to local nodes.
**Philosophy:** Pay cloud models ONLY for their unique capability (structural analysis of complex prompts). All actual execution stays local. If a sub-task won't fit locally, decompose again — don't execute on cloud.

---

## Problem Statement

Current `decompose-watcher.py` generates static sub-tasks:
- Step 1: "Analyze requirements" — generic, not prompt-specific
- Step 2: "Research approaches" — generic
- Step 3: "Design core architecture" — generic

These sub-tasks don't adapt to the actual prompt content. A prompt about "Ansible playbook for vault deployment" gets the same sub-tasks as "Design a trading signal backtest framework" — which is wasteful and produces poor results.

We want:
- **Prompt-specific decomposition**: The decomposer reads the actual prompt and generates custom sub-tasks
- **Weighted assessment**: Each sub-task gets a complexity score, token estimate, capability needs, and confidence
- **Local-first matching**: Match sub-tasks to local (node, model) pairs based on right-sizing
- **Recursive fallback**: If a sub-task exceeds local capacity, decompose it again — never execute on cloud unless recursively impossible

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│  USER PROMPT                                                        │
│  "Design a meta-orchestration framework with complexity classification│
│   and adaptive feedback for a 7-node lab"                          │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  TIER 0: Cloud Decomposition (qwen3.5:397b-cloud)                 │
│  Role: Smart Splitter — ONE decomposition call per prompt           │
│  Cost: ~$0.005 (one-time)                                          │
│                                                                     │
│  Prompt to model:                                                   │
│  "Decompose this task into weighted sub-tasks. For each sub-task, │
│   specify: task_description, complexity, estimated_tokens,        │
│   required_capabilities, confidence_score. Ensure each sub-task     │
│   can independently produce useful output."                         │
│                                                                     │
│  Output JSON:                                                       │
│  {                                                                   │
│    "sub_tasks": [                                                   │
│      {                                                                │
│        "id": "1",                                                    │
│        "description": "Define complexity classification taxonomy",   │
│        "complexity": "medium",                                       │
│        "estimated_tokens": 2500,                                    │
│        "required_capabilities": ["tools", "reasoning"],              │
│        "confidence": 0.92,                                           │
│        "weight": 0.30                                               │
│      },                                                              │
│      {                                                                │
│        "id": "2",                                                    │
│        "description": "Design NodeRegistry integration with",       │
│                  "routing logic for 7-node capacity matching",       │
│        "complexity": "hard",                                        │
│        "estimated_tokens": 4000,                                    │
│        "required_capabilities": ["tools", "reasoning", "coding"],    │
│        "confidence": 0.85,                                           │
│        "weight": 0.50                                               │
│      },                                                              │
│      {                                                                │
│        "id": "3",                                                    │
│        "description": "Document adaptive feedback loop mechanism",   │
│        "complexity": "medium",                                       │
│        "estimated_tokens": 2000,                                    │
│        "required_capabilities": ["tools", "reasoning"],              │
│        "confidence": 0.78,                                           │
│        "weight": 0.20                                               │
│      }                                                                │
│    ]                                                                  │
│  }                                                                    │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LOCAL MATCHER (NodeRegistry + right-sizing)                        │
│  For each sub-task:                                                 │
│    1. Map complexity → model tier (trivial→low, simple→low, etc.)    │
│    2. Check capabilities (vision? tools? reasoning?)                 │
│    3. Check capacity (model_size < node_safe_capacity?)              │
│    4. Check token limit (estimated_tokens < model_context * 0.85)   │
│    5. Score = 35% speed + 65% fit                                     │
│                                                                     │
│  Result per sub-task:                                               │
│    - MATCHED: assigned (node, model, route)                         │
│    - NO_MATCH: flag for re-decomposition                            │
│    - OVERFLOW: tokens > context — flag for re-decomposition           │
└─────────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
    ┌──────────────────┐          ┌──────────────────┐
    │  MATCHED ✅       │          │  NO MATCH ❌     │
    │  Submit to node    │          │  Re-decompose     │
    │  queue for local   │          │  (Tier 0 again)   │
    │  execution         │          │                   │
    │  Cost: $0          │          │  Cost: +$0.005     │
    └─────────┬──────────┘          └─────────┬──────────┘
              │                               │
              │                    ┌──────────┴──────────┐
              │                    │  Still NO MATCH?    │
              │                    │  After 2 tries       │
              │                    │                      │
              │                    ▼                      ▼
              │         ┌──────────────────┐  ┌──────────────────┐
              │         │  ESCALATE TIER 1  │  │  LOCAL FALLBACK   │
              │         │  kimi-k2.6 cloud  │  │  Use best local   │
              │         │  (largest model)    │  │  model with         │
              │         │  Final decomp       │  │  truncation/warning │
              │         │  Cost: +$0.01-0.05  │  │  Cost: $0           │
              │         └─────────┬──────────┘  └──────────────────┘
              │                   │
              │         ┌─────────┴─────────┐
              │         │  If STILL no fit   │
              │         │  → Execute on      │
              │         │    cloud model     │
              │         │    (justified)    │
              │         └───────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LOCAL EXECUTION                                                    │
│  task-worker.sh on each node picks up assigned sub-tasks            │
│  All execution: $0 cost                                             │
│                                                                     │
│  Results collected → synthesized → returned to user                   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Decomposition JSON Schema

The cloud decomposer outputs structured JSON that the local matcher consumes:

```json
{
  "version": "1.0",
  "decomposer_model": "qwen3.5:397b-cloud",
  "decomposer_cost": 0.005,
  "prompt_preview": "Design a meta-orchestration framework...",
  "sub_tasks": [
    {
      "id": "1",
      "description": "What this sub-task does (specific, actionable)",
      "rationale": "Why this sub-task is needed for the overall goal",
      "complexity": "trivial | simple | medium | hard",
      "estimated_tokens_in": 1200,
      "estimated_tokens_out": 800,
      "required_capabilities": ["tools", "reasoning", "vision"],
      "confidence": 0.92,
      "weight": 0.30,
      "dependencies": [],
      "can_parallelize": true
    }
  ],
  "global_constraints": {
    "max_total_tokens": 10000,
    "preferred_local": true,
    "max_cloud_escalation_depth": 2
  }
}
```

**Field definitions:**
- `complexity`: Maps to model-router tier (low/medium/high)
- `estimated_tokens_in+out`: Total context needed; checked against model's context window
- `required_capabilities`: Filter for models that have these capabilities
- `confidence`: 0.0–1.0; if <0.70, flag for re-decomposition (decomposer uncertain)
- `weight`: 0.0–1.0; sum of all weights = 1.0; used for prioritization if resources constrained
- `dependencies`: Sub-task IDs that must complete before this one starts
- `can_parallelize`: If false, must execute sequentially after dependencies

---

## Local Matcher Algorithm

```python
def match_subtask_to_local(subtask: dict) -> dict | None:
    """
    Match a weighted sub-task to the best local (node, model).
    Returns route dict or None if no suitable local match.
    """
    complexity = subtask["complexity"]
    tokens_needed = subtask["estimated_tokens_in"] + subtask["estimated_tokens_out"]
    capabilities = set(subtask["required_capabilities"])
    confidence = subtask["confidence"]

    # If decomposer was uncertain, don't trust the complexity — flag for re-decomp
    if confidence < 0.70:
        return {"status": "UNCERTAIN", "reason": f"confidence {confidence} < 0.70"}

    # Query NodeRegistry for candidates
    candidates = reg.best_model_for(complexity, vision="vision" in capabilities)

    if not candidates:
        return {"status": "NO_CANDIDATE", "reason": "no local model matches complexity tier"}

    # Check token limit (85% of model context window)
    model_spec = reg.get_model_spec(candidates["node"], candidates["model"])
    context_limit = model_spec.get("capabilities", {}).get("contextSize", 32768)
    if tokens_needed > context_limit * 0.85:
        return {
            "status": "TOKEN_OVERFLOW",
            "reason": f"{tokens_needed} tokens > {int(context_limit * 0.85)} limit",
            "model": candidates["model"],
            "context_limit": context_limit,
        }

    # Check capacity (model size < node safe capacity)
    model_size_gb = reg._parse_size_gb(model_spec.get("size", "0"))
    node_cap_gb = reg._parse_capacity_gb(reg.nodes[candidates["node"]])
    if model_size_gb > node_cap_gb:
        return {
            "status": "CAPACITY_EXCEEDED",
            "reason": f"model {model_size_gb}GB > node {node_cap_gb}GB safe",
        }

    # Check capabilities
    model_caps = set()
    if model_spec.get("capabilities", {}).get("tools"):
        model_caps.add("tools")
    if model_spec.get("capabilities", {}).get("vision"):
        model_caps.add("vision")
    if model_spec.get("capabilities", {}).get("reasoning") or complexity in ["medium", "hard"]:
        model_caps.add("reasoning")

    missing_caps = capabilities - model_caps
    if missing_caps:
        return {
            "status": "CAPABILITY_GAP",
            "reason": f"missing capabilities: {missing_caps}",
            "missing": list(missing_caps),
        }

    # All checks passed — route to local
    return {
        "status": "MATCHED",
        "node": candidates["node"],
        "model": candidates["model"],
        "provider": "ollama",
        "tokens_per_sec": candidates["tokens_per_sec"],
        "fit_score": candidates.get("_fit_score", 0),
        "utilization_percent": round(100 * model_size_gb / node_cap_gb, 1),
    }
```

---

## Re-Decomposition Rules

A sub-task is flagged for re-decomposition when:

| Condition | Flag | Action |
|-----------|------|--------|
| `confidence < 0.70` | UNCERTAIN | Re-decompose with more specific prompt |
| `tokens > context_limit * 0.85` | TOKEN_OVERFLOW | Re-decompose into smaller pieces |
| `model_size > node_capacity` | CAPACITY_EXCEEDED | Re-decompose into smaller pieces |
| `missing capabilities` | CAPABILITY_GAP | Re-decompose to avoid needing that capability |
| No candidate after 2 re-decomposition attempts | FINAL_FAIL | Escalate to next cloud tier (kimi-k2.6) |

**Re-decomposition prompt template:**
```
The following sub-task could not be executed on local hardware:
"{subtask_description}"

Reason: {failure_reason}

Constraints for re-decomposition:
- Each new sub-task must use ≤{context_limit * 0.70} tokens total
- Each new sub-task must require only [{available_capabilities}] capabilities
- Each new sub-task must be independently executable

Please decompose this into 2-4 smaller sub-tasks that fit these constraints.
```

---

## Escalation Tiers (Corrected)

| Tier | Model | Role | Cost/Decomp | When Used |
|------|-------|------|------------|-----------|
| **LOW** | qwen3.5:397b-cloud | Primary decomposer | ~$0.011 | Every HARD prompt, first decomposition |
| **MEDIUM** | gemma4:31b-cloud | Re-decomposer | ~$0.017 | After LOW fails or produces uncertain sub-tasks |
| **HIGH** | kimi-k2.6 (1042B) | Final decomposer | ~$0.055 | After MEDIUM fails, or for ultra-complex cross-domain tasks |

**Escalation is per sub-task, not per prompt.** If 4 of 5 sub-tasks fit locally and 1 needs escalation, only that 1 sub-task incurs cloud cost. The other 4 stay at $0.

**Cost data source:** `~/.pi/agent/models.json` — actual pricing from provider config:
- qwen3.5:397b-cloud: $2.0 input / $6.0 output per 1M tokens
- gemma4:31b-cloud: $3.0 input / $9.0 output per 1M tokens
- kimi-k2.6: $10.0 input / $30.0 output per 1M tokens

**Note:** qwen3.5:397b-cloud is the cheapest cloud model available — there is no lower-cost option. The original $0.005 estimate was for a ~500-token prompt; actual decomposition uses ~2500 tokens (~$0.011).

---

## Decomposition Tracking (Updated Format)

Add two new columns to the decomposition table for LLM-driven plans:

```markdown
## Decomposition

| Step | Sub-Task | Complexity | Weight | Confidence | Est. Tokens | Capabilities | Suggested Model | Suggested Node | Result |
|------|----------|-----------|--------|------------|-------------|--------------|-----------------|----------------|--------|
| 1 | Define complexity taxonomy | medium | 0.30 | 0.92 | 2500 | tools, reasoning | qwen3.5:4b | fnet7 | MATCHED |
| 2 | Design NodeRegistry integration | hard | 0.50 | 0.85 | 4000 | tools, reasoning, coding | qwen3:8b | fnet3 | MATCHED |
| 3 | Document feedback loop | medium | 0.20 | 0.78 | 2000 | tools, reasoning | qwen3.5:4b | fnet2 | MATCHED |
```

**Result values:** MATCHED, RE_DECOMP, TIER1_ESCALATE, TIER2_EXECUTE

---

## Implementation Phases

### Phase 1: Cloud Decomposer Script (2-3 hours)
- Build `scripts/decompose_llm.py` — calls cloud API with structured prompt
- JSON schema validation for output
- Cost tracking per decomposition call
- Error handling for malformed responses

### Phase 2: Local Matcher Integration (2 hours)
- Extend `ti011_node_registry.py` with capability + token checks
- Build `match_subtask_to_local()` function
- Return structured status codes (MATCHED, TOKEN_OVERFLOW, etc.)

### Phase 3: Recursive Watcher (2-3 hours)
- Rewrite `decompose-watcher.py` to:
  1. Call decomposer LLM (Tier 0)
  2. Run matcher on each sub-task
  3. Queue matched tasks to local nodes
  4. Flag unmatched tasks for re-decomposition
  5. After 2 tries, escalate unmatched to Tier 1
  6. Collect results, synthesize, write output

### Phase 4: Cost Justification Logging (1 hour)
- Log every decomposition: model used, cost, number of sub-tasks generated
- Log every escalation: why, which sub-task, depth of recursion
- Weekly report: "X% of HARD prompts fully local, Y% needed 1 re-decomp, Z% needed Tier 1"

**Total estimated effort: 7-9 hours**

---

## Cost Model

| Scenario | LOW Decomp | MEDIUM Re-Decomp | HIGH Escalation | Local Exec | Total Cost | vs. Old |
|----------|-----------|-----------------|----------------|-----------|------------|---------|
| All sub-tasks fit local (LOW) | $0.011 | 0 | 0 | $0 | **$0.011** | 78% cheaper |
| 1 re-decomposition (LOW→LOW) | $0.011 | $0.011 | 0 | $0 | **$0.022** | 56% cheaper |
| 1 sub-task needs MEDIUM | $0.011 | $0.017 | 0 | $0 | **$0.028** | 44% cheaper |
| 1 sub-task needs HIGH | $0.011 | 0 | $0.055 | $0 | **$0.066** | -32% more |
| Direct cloud execution (old) | 0 | 0 | 0 | $0.050 | **$0.050** | baseline |

**Savings: 44-78% per HARD prompt** when LOW or MEDIUM decomposition suffices. Only when HIGH escalation is needed does cost exceed direct execution — but this is justified by genuine need.

---

## Billing Model: Unified Cost Per 1K Tokens

For customer billing, every token processed — local or cloud — has a cost. This creates a single metric for pricing regardless of execution venue.

### Compute Cost Formula (Local)

```
hourly_cost = hardware_depreciation + electricity
hardware_depreciation = hardware_cost_usd / (3 years * 365 * 24 hours)
electricity = power_draw_kwh * electricity_rate_usd_per_kwh

cost_per_1k_tokens = (hourly_cost / (tokens_per_sec * 3600)) * 1000
```

### Lab Node Costs (Current)

| Node | Hardware | Hourly Cost | qwen3.5:4b | qwen3:8b | gemma4:e4b |
|------|----------|------------|-----------:|---------:|-----------:|
| fnet1-fnet2-fnet7 | $500 desktop | $0.037/hr | $0.0030/1Ktk | $0.0031/1Ktk | N/A |
| fnet3-fnet6 | $800 mini PC | $0.048/hr | $0.0030/1Ktk | $0.0028/1Ktk | $0.0022/1Ktk |
| Mac orchestrator | $2000 MBP | $0.094/hr | (not benchmarked) | (not benchmarked) | (not benchmarked) |

### Cloud Cost Reference

| Model | Cost per Prompt | Cost per 1K Tokens |
|-------|----------------|-------------------|
| qwen3.5:397b-cloud | ~$0.005 (~500 tokens) | ~$0.010 |
| kimi-k2.6 | ~$0.020 (~500 tokens) | ~$0.040 |

### Billing Tiers for Customers

| Tier | Description | Price per 1K Tokens | Margin |
|------|-------------|---------------------|--------|
| **Local Basic** | qwen3.5:4b on 15GB nodes | $0.005 | 40% over cost |
| **Local Standard** | qwen3:8b on any node | $0.006 | 50% over cost |
| **Local Premium** | gemma4:e4b on 31GB nodes | $0.005 | 56% over cost |
| **Cloud LOW** | qwen3.5:397b-cloud (decomposition) | $0.011 | — |
| **Cloud MEDIUM** | gemma4:31b-cloud (re-decomposition) | $0.017 | — |
| **Cloud HIGH** | kimi-k2.6 (final escalation) | $0.055 | — |
| **Decomposition** | LOW tier cloud split | $0.011 flat | — |

**Cloud Cost Reference (actual provider pricing):**

| Model | Input/Output per 1M | Cost per 1K Tokens | Context |
|-------|--------------------|--------------------|---------|
| qwen3.5:397b-cloud | $2.0 / $6.0 | ~$0.008 | 262K |
| gemma4:31b-cloud | $3.0 / $9.0 | ~$0.012 | 256K |
| kimi-k2.6:cloud | $10.0 / $30.0 | ~$0.040 | 262K |

**Note:** qwen3.5:397b-cloud is the cheapest cloud model available at $2/$6 per M tokens. There is no lower-cost cloud option in the current provider config.

### Example Invoice Line Items

```
Prompt: "Design a meta-orchestration framework..."
├─ Decomposition (qwen3.5:397b LOW):                $0.011
├─ Sub-task 1: Define taxonomy (qwen3.5:4b, 2500tk)  $0.013  ($0.005/1K * 2.5K)
├─ Sub-task 2: Design registry (qwen3:8b, 4000tk)    $0.024  ($0.006/1K * 4.0K)
├─ Sub-task 3: Document loop (qwen3.5:4b, 2000tk)   $0.010  ($0.005/1K * 2.0K)
└─ Total:                                             $0.058

vs. Direct Cloud HIGH execution (8000 tokens):
  kimi-k2.6: $0.040/1Ktk * 8.0Ktk = $0.320
  Savings: 82%
```

---

## Appendix A: Autonomous 413 Recovery System

### Overview
The 413 "Request Entity Too Large" recovery system is a self-healing layer that detects, diagnoses, and recovers from oversized payloads without human intervention. It operates at three levels:

1. **Prevention** — `handle_413.py --preflight` checks before routing
2. **Detection** — `task-worker.sh` classifies 413 errors during execution
3. **Recovery** — `decompose-watcher.py` auto-triggers recovery strategies

### Recovery Strategy Ladder

| Priority | Strategy | Condition | Cost | Latency |
|----------|----------|-----------|------|---------|
| 1 | **SAME_NODE_UPGRADE** | Larger model fits on same node | $0 | ~3-6s |
| 2 | **CROSS_NODE_SAME** | Same model, different node | $0 | +network |
| 3 | **CROSS_NODE_UPGRADE** | Larger model, different node | $0 | ~3-6s |
| 4 | **CLOUD** | Cloud model with huge context | ~$0.011 | ~5-15s |
| 5 | **CHUNK** | Split into smaller tasks | $0 × chunks | ~3s/chunk |
| 6 | **TRUNCATE** | Hard truncate (last resort) | $0 | ~3s |

### Model Context Reference

| Model | Context | Size | Vision | Tools |
|-------|---------|------|--------|-------|
| qwen3.5:4b | 131,072 | 5.7GB | ✅ | ✅ |
| qwen3:8b | 32,768 | 10.8GB | ❌ | ✅ |
| gemma4:e4b | 131,072 | 18.9GB | ✅ | ✅ |
| qwen3.5:397b-cloud | 262,144 | — | ✅ | ✅ |
| gemma4:31b-cloud | 256,000 | — | ✅ | ✅ |
| kimi-k2.6:cloud | 262,144 | — | ✅ | ✅ |

### Node Capacity Map

| Node | Safe RAM | Models | Max Single-Task Tokens |
|------|----------|--------|----------------------|
| fnet1 | 12.5GB | qwen3.5:4b | 111,411 (85% of 131K) |
| fnet2 | 12.5GB | qwen3.5:4b | 111,411 |
| fnet3 | 27.0GB | qwen3:8b, gemma4:e4b | 27,852 (qwen3:8b) / 111,411 (gemma4:e4b) |
| fnet4 | 27.0GB | qwen3:8b, gemma4:e4b | 27,852 / 111,411 |
| fnet5 | 27.0GB | qwen3:8b, gemma4:e4b | 27,852 / 111,411 |
| fnet6 | 27.0GB | qwen3:8b, gemma4:e4b | 27,852 / 111,411 |
| fnet7 | 12.5GB | qwen3.5:4b | 111,411 |

### Decision Flowchart

```
TASK SUBMITTED
     │
     ▼
┌─────────────────┐
│ Preflight check │
│ tokens < limit? │
└─────────────────┘
     │
     ├── YES ──▶ Route to planned node/model
     │
     └── NO ───▶ ┌─────────────────────┐
                 │ SAME_NODE_UPGRADE?  │
                 │ larger model fits?  │
                 └─────────────────────┘
                      │
                      ├── YES ──▶ Submit to same node, larger model
                      │
                      └── NO ───▶ ┌─────────────────────┐
                                  │ CROSS_NODE_SAME?    │
                                  │ same model, new node? │
                                  └─────────────────────┘
                                       │
                                       ├── YES ──▶ Submit to new node
                                       │
                                       └── NO ───▶ ┌─────────────────────┐
                                                     │ CROSS_NODE_UPGRADE? │
                                                     │ new model + node?   │
                                                     └─────────────────────┘
                                                          │
                                                          ├── YES ──▶ Submit upgrade
                                                          │
                                                          └── NO ───▶ ┌──────────────┐
                                                                        │ CLOUD?       │
                                                                        │ fits cloud?  │
                                                                        └──────────────┘
                                                                             │
                                                                             ├── YES ──▶ Cloud
                                                                             │
                                                                             └── NO ───▶ CHUNK
```

### Integration with Decomposition Pipeline

When the recursive decomposition pipeline (Phase 3) encounters a 413:

1. **Matcher stage:** `match_subtask_to_local()` returns `TOKEN_OVERFLOW` or `CAPACITY_EXCEEDED`
2. **Recovery stage:** `decompose-watcher.py` calls `handle_413.py --recover`
3. **Re-decomposition stage:** If CHUNK strategy selected, call `decompose_llm.py` with chunking prompt
4. **Re-matching stage:** Run matcher on each chunk
5. **Execution stage:** Submit all chunks in parallel
6. **Synthesis stage:** Combine chunk results into final output

### Prompt Templates

Comprehensive prompt templates for 413 scenarios are in:
- `technical-infrastructure/prompts/413-recovery-prompts.md`
  - Prompt 1: Decompose oversized task
  - Prompt 2: Recovery decision analysis
  - Prompt 3: Post-recovery validation
  - Prompt 4: 413 feedback loop analysis
  - Prompt 5: Chunk synthesis

### Cost Model Impact

| Scenario | Before 413 Recovery | After | Savings |
|----------|---------------------|-------|---------|
| 35K token payload on qwen3:8b | Cloud fallback ~$0.050 | Local upgrade ~$0.003 | 94% |
| 150K token payload | Cloud execution ~$0.200 | Cloud decomp only ~$0.011 | 95% |
| 250K token payload | Failed / manual | Chunked local ~$0.006 | 97% |

### Files

| File | Role |
|------|------|
| `scripts/handle_413.py` | Core recovery engine (430 lines) |
| `scripts/task-worker.sh` | 413 detection on all nodes |
| `scripts/decompose-watcher.py` | Auto-recovery trigger |
| `scripts/check-payload-size.py` | Pre-flight guard |
| `prompts/413-recovery-prompts.md` | LLM prompt templates |
| `wiki/operational/sessions/SESSION-NOTES-2026-05-02-2200-AUTONOMOUS-413-RECOVERY.md` | Session documentation |

---

## Acceptance Criteria

- [x] `decompose_llm.py` produces valid JSON for test prompts
- [x] All sub-tasks have complexity, weight, confidence, token estimates, capabilities
- [x] Local matcher correctly routes ≥80% of sub-tasks to local nodes (achieved: 100%)
- [ ] Re-decomposition triggers when token/context/capability mismatch detected
- [ ] After 2 re-decomposition attempts, escalation to Tier 1 occurs
- [x] Cost per HARD prompt is logged and justified
- [x] End-to-end test: 1 HARD prompt → decomposition → local execution → synthesis → result
- [ ] Weekly report shows % local vs. % escalated
- [x] 413 pre-flight detection prevents oversized payloads from being routed
- [x] 413 recovery auto-escalates through 6-tier ladder
- [x] 413 chunking splits oversized tasks into parallel chunks
- [x] 413 incident logging to `/tmp/tasks/413-log/`

---

**Related:**
- [SESSION-NOTES-TI011-RIGHT-SIZING-2026-05-02.md](../sessions/SESSION-NOTES-TI011-RIGHT-SIZING-2026-05-02.md) — Right-sizing implementation
- [SESSION-NOTES-2026-05-02-2200-AUTONOMOUS-413-RECOVERY.md](../sessions/SESSION-NOTES-2026-05-02-2200-AUTONOMOUS-413-RECOVERY.md) — 413 recovery session notes
- `scripts/ti011_node_registry.py` — NodeRegistry extension
- `scripts/decompose-watcher.py` — Recursive watcher
- `scripts/handle_413.py` — Recovery engine
- `scripts/check-payload-size.py` — Payload guard
