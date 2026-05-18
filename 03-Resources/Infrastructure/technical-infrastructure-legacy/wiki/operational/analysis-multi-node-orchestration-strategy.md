# Multi-Node Orchestration Strategy Analysis

| | |
|---|---|
| **Date** | 2026-05-15 |
| **Status** | Analysis — Decision Framework |
| **Context** | 7-node trading lab (fnet1–fnet7) with local Ollama models + cloud model access. Goal: use high-cost cloud models for reasoning/planning and low-cost local models for execution, achieving substantial cost savings. |

---

## Executive Summary

Your current architecture — cloud decomposer → local execution → cloud verifier — is **theoretically sound** but **practically fragile** for the types of tasks a trading desk requires. The cost savings exist, but they are **concentrated in a narrow band of tasks** (structured data extraction, formatting, simple classification). For the majority of your actual workload (coding, analysis, reasoning, judgment-based tasks), the **verification failure rate + retry overhead consumes the savings or produces worse outcomes than cloud-only execution**.

This document diagnoses why, then proposes **6 alternative architectural patterns** that better match your hardware, your models, and your actual task mix.

---

## Part 1: Diagnosis — Why the Current Approach Underperforms

### 1.1 The Fundamental Category Error

Your architecture treats **pi (interactive AI assistant)** as a **batch execution engine**. Pi is designed for:
- Interactive coding assistance
- Tool use in a single session context
- Human-in-the-loop workflows

It is **not** designed for:
- Stateless task execution across 7 nodes
- Deterministic batch processing
- Sub-millisecond coordination

**The result:** Every "execution" on a lab node spins up a full pi session with model loading, context construction, tool registration, and intercom handshakes. The overhead per sub-task is **30–120 seconds** before any actual work begins. Compare this to a cloud model that starts reasoning immediately.

### 1.2 Small Model Failure Modes (The Hidden Tax)

Research on models ≤30B parameters in agentic workflows shows **systematic failure categories** that your verifier catches, but catching them doesn't prevent them from happening:

| Failure Mode | Frequency in Local Execution | Cost Impact |
|--------------|------------------------------|-------------|
| **Context drift** — working from stale/hallucinated file state | Very high (#1) | Re-read + re-execute cycles |
| **Phantom APIs** — calling functions that don't exist | High | Re-run with cloud model |
| **Scope creep / cascade edits** — one edit spirals into multi-file refactor | Medium-high | Full rollback + restart |
| **Partial generation** — truncated output, broken syntax | Medium | Re-generate entire file |
| **Echo errors** — accepts own mistake as ground truth, compounds it | Medium | Silent corruption until verifier catches it |
| **Multi-step logic errors** — individual steps work, composition fails | Medium | Debug + retry loop |
| **Off-by-one / boundary errors** | Medium | Test failures, re-implementation |

**The verifier catches these, but at what cost?**
- Verifier call: ~$0.02–0.03
- Re-run with cloud model: ~$0.10–0.30
- **Per sub-task failure rate:** 15–40% for coding tasks, 5–15% for structured data tasks

**Net result:** For tasks where local models fail more than ~15% of the time, you pay the cloud rate **plus** the local overhead **plus** the verification cost. This is **more expensive than cloud-only**.

### 1.3 Coordination Overhead Saturation

Multi-agent research shows that each inter-agent handoff adds **100–500ms of serialization + latency**, plus token reconstruction overhead. Your pipeline has:

1. Orchestrator → decomposer (cloud call)
2. Decomposer output parsing (local)
3. Orchestrator → pi-intercom dispatch to lab node (network + intercom protocol)
4. Lab node → local model load + context construction
5. Local model execution (the actual work)
6. Lab node → intercom reply to orchestrator
7. Orchestrator → verifier (cloud call)
8. Verifier output parsing (local)
9. If fail: repeat steps 3–8

**Total overhead per sub-task:** 45–300 seconds depending on model load time, network latency, and retry count.

For a task that a cloud model completes in 60 seconds, your pipeline takes 3–8 minutes even when it works on the first try.

### 1.4 The Task Mix Mismatch

Your model-router routes by keyword. But keywords are a **poor proxy for local-model suitability**:

| Task Type | Looks Simple? | Actually Suitable for Local? | Why |
|-----------|-------------|------------------------------|-----|
| "Format this JSON" | ✅ Yes | ✅ Yes | Deterministic, schema-constrained |
| "Check portfolio status" | ✅ Yes | ⚠️ Partial | Needs arithmetic accuracy, risk limit judgment |
| "Fix this bug" | ⚠️ Medium | ❌ No | Requires understanding codebase context, testing |
| "Refactor this module" | ❌ No | ❌ No | Multi-file dependencies, holistic reasoning |
| "Analyze Q1 performance" | ❌ No | ❌ No | Requires synthesis across multiple data sources |
| "Generate test stubs" | ✅ Yes | ✅ Yes | Template-driven, bounded scope |
| "Implement retry logic" | ⚠️ Medium | ❌ No | Requires understanding of async patterns, error handling |

**The pattern:** Local models excel at **bounded, schema-driven, single-file, non-judgmental** tasks. They fail at **unbounded, context-dependent, multi-step, judgmental** tasks. Your trading desk's actual workload skews heavily toward the latter.

---

## Part 2: Six Alternative Architectural Patterns

### Pattern A: Ollama-as-Inference-Server (Not Pi-as-Agent)

**Core idea:** Stop running `pi` on lab nodes. Run `ollama serve` only. The orchestrator's model-router calls lab node Ollama APIs directly via HTTP.

```
┌─────────────────────────────────────────────────────────────┐
│  Orchestrator (Mac) — runs pi                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │ Model       │───▶│ Local task  │───▶│ HTTP call   │     │
│  │ Router      │    │ classified  │    │ to fnet5    │     │
│  └─────────────┘    └─────────────┘    │ Ollama API  │     │
│                                         │ (localhost  │     │
│                                         │  via SSH    │     │
│                                         │  tunnel)    │     │
│                                         └─────────────┘     │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
    ┌─────────┐
    │ fnet5   │  ← Ollama API only, no pi session
    │ Ollama  │
    └─────────┘
```

**Advantages:**
- Eliminates pi session startup overhead (30–120s → 0s)
- Eliminates intercom coordination overhead
- Eliminates SSHFS mount complexity
- Local model inference is a single HTTP round-trip
- No context reconstruction across sessions

**Disadvantages:**
- Requires SSH tunnel or direct network access to Ollama ports
- Local models still have the same failure modes (but now fail faster)
- Loss of tool use on lab nodes (no file editing, no git, no bash)

**When to use:** For **inference-only** tasks — classification, summarization, simple extraction — where the orchestrator handles all tool use. The local model just answers questions.

**Implementation:**
```bash
# On each lab node — only Ollama, no pi
sudo systemctl enable ollama
ollama serve --host 0.0.0.0  # or restrict to LAN

# On orchestrator — SSH tunnel
ssh -L 11434:fnet5:11434 friasc@fnet5.local -N -f
# Then configure model-router.json to point to localhost:11434 for local tier
```

---

### Pattern B: Task Classification Gate (Not Decomposition)

**Core idea:** Don't decompose every task. Use a fast local model to **classify** incoming tasks into "local-suitable" vs "cloud-required" **before** any decomposition happens.

```
User Prompt
     │
     ▼
┌─────────────────┐
│ Classifier      │  ← qwen3.5:4b local, single-turn
│ (local model)   │
└─────────────────┘
     │
     ├─► "Simple: bounded, schema-driven" ──▶ Local execution (Ollama API)
     │
     └─► "Complex: judgment, multi-step" ──▶ Cloud execution (no decomposition overhead)
```

**Classifier prompt template:**
```
Classify this task for execution suitability:

Task: {user_prompt}

Return exactly one of:
- LOCAL: Bounded scope, deterministic output, single file, no judgment needed
- CLOUD: Requires synthesis, multi-step reasoning, cross-file context, or nuanced judgment
- DECOMPOSE: Complex but separable into independent local-suitable sub-tasks

Be conservative. If uncertain, return CLOUD.
```

**Advantages:**
- Eliminates decomposition overhead for tasks that are obviously cloud-only
- Fast classification (~1–2s on local model)
- Avoids wasting decomposer calls on tasks that will fail local execution anyway

**Disadvantages:**
- Classifier can miscategorize (mitigate by being conservative)
- Doesn't help when tasks genuinely need decomposition

**When to use:** As a **pre-filter** before the existing decompose-execute-verify pipeline. Expected distribution for a trading desk:
- ~40% CLOUD (complex analysis, coding, judgment)
- ~35% LOCAL (status checks, formatting, simple extraction)
- ~25% DECOMPOSE (structured workflows: "monitor, check, log")

**Cost impact:** Saves ~40% of decomposition calls and ~60% of verification retries.

---

### Pattern C: The Compiler Pattern (Cloud Generates Scripts, Local Runs Them)

**Core idea:** Instead of asking local models to "execute a sub-task," ask the cloud model to **generate a deterministic script** (Python, bash, JavaScript) that performs the sub-task. Local execution is just running the script. Local models don't do reasoning — they do inference.

```
Cloud Decomposer
     │
     ▼
┌─────────────────────────────────────────┐
│ Script Generation                       │
│ "Generate a Python script that:          │
│  1. Reads positions.csv                  │
│  2. Calculates exposure by asset class   │
│  3. Compares to limits in limits.json    │
│  4. Outputs JSON with status + details" │
└─────────────────────────────────────────┘
     │
     ▼
Lab Node (no pi, no local model reasoning)
┌─────────────────────────────────────────┐
│ Script Runner                           │
│ python3 /tmp/generated_script.py        │
│ → deterministic output                  │
└─────────────────────────────────────────┘
```

**Advantages:**
- Local execution is **deterministic** — same script + same input = same output
- No local model failure modes (hallucination, context drift, etc.)
- Script is **inspectable and auditable**
- Can cache scripts by task type ("portfolio exposure check" script is reusable)
- Lab nodes don't even need Ollama loaded if the script is pure Python

**Disadvantages:**
- Requires the cloud model to understand your data schemas well enough to generate correct scripts
- Script generation fails if task requires judgment that can't be codified
- Security: generated scripts run on lab nodes — need sandboxing

**When to use:** For **repetitive structured workflows** that happen daily:
- Portfolio monitoring
- Risk limit checking
- Trade reconciliation
- Report generation

**Implementation sketch:**
```python
# Orchestrator side
def compile_task(task_description):
    # Cloud model generates script
    script = cloud_model.generate(
        f"Generate a Python script that: {task_description}\n"
        f"Data schemas: {schema_docs}\n"
        f"Output format: JSON with fields X, Y, Z"
    )
    return script

# Dispatch to lab node via SSH (not pi-intercom)
def execute_on_node(script, node):
    ssh(node, f"cat > /tmp/task.py << 'EOF'\n{script}\nEOF")
    result = ssh(node, "python3 /tmp/task.py")
    return result

# Verify deterministically (no model needed)
def verify_output(output, expected_schema):
    jsonschema.validate(output, expected_schema)
    return True
```

---

### Pattern D: Parallel Batch Processing (Embarrassingly Parallel Workloads)

**Core idea:** Stop trying to decompose **sequential dependent tasks** across nodes. Instead, use the 7 nodes for **parallel independent workloads** — the same task applied to different data.

**Examples for a trading desk:**

| Workload | Parallelization Strategy | Node Assignment |
|----------|--------------------------|-----------------|
| Backtest 10 years of data | Each node gets 1.4 years | fnet1: 2016–2017, fnet2: 2018–2019, etc. |
| Analyze 50 stocks | Each node gets 7–8 stocks | Round-robin by symbol |
| Run portfolio risk on 5 asset classes | Each node gets 1 class | fnet5: equities, fnet6: bonds, etc. |
| Run same prompt on 3 model sizes | Each node runs one size | Ensemble results for quality |

**Advantages:**
- No inter-node coordination needed (embarrassingly parallel)
- Linear speedup with node count (7 nodes = ~7× faster)
- Each node operates independently with full context
- No decomposition overhead, no verification chains

**Disadvantages:**
- Only works for workloads that are **naturally parallelizable**
- Requires a merge/aggregation step at the end
- Not applicable to single-task workflows

**When to use:** For your highest-volume batch operations:
- Historical backtesting across time periods
- Multi-asset screening and scoring
- Monte Carlo simulations (each node runs N iterations)
- Multi-model ensemble inference (same prompt, different models)

---

### Pattern E: Canned Decomposition Plans (Cache the Reasoning)

**Core idea:** If you find yourself decomposing the same types of tasks repeatedly, **pre-generate and cache the decomposition plans**. The cloud model only runs once per task type, not once per task instance.

**Example — "Monitor Portfolio and Log Status":**

```json
{
  "task_type": "portfolio_monitor_and_log",
  "cached_plan": {
    "steps": [
      {"id": "read_positions", "agent": "position-monitor", "prompt_template": "Read all current positions from {data_source}"},
      {"id": "calculate_exposure", "agent": "position-monitor", "prompt_template": "Calculate exposure by asset class for: {previous_output}"},
      {"id": "check_limits", "agent": "position-monitor", "prompt_template": "Compare exposure to limits in {limits_file}"},
      {"id": "log_status", "agent": "bookkeeping", "prompt_template": "Log monitoring results: {previous_output}"}
    ],
    "verification_criteria": ["All positions present", "Math checks", "Timestamps valid"],
    "expected_cost": "$0.05"
  }
}
```

**When a user asks:** "Monitor my portfolio and log status"

1. Classifier matches to cached plan (local, ~0 cost)
2. Execute cached steps on lab nodes (local models, ~$0)
3. Run verifier once (cloud, ~$0.02)
4. **Total cost: ~$0.02** vs. **~$0.05** with full decomposition

**Advantages:**
- Eliminates repeated decomposition calls
- Plans can be hand-tuned for quality after initial generation
- Deterministic execution path

**Disadvantages:**
- Requires upfront investment to generate and validate plans
- Doesn't handle novel task types
- Plans may drift as data schemas change

**When to use:** For your **high-frequency recurring workflows** (daily/weekly tasks that follow the same pattern).

---

### Pattern F: Model Ensemble with Differential Execution (Not Decomposition)

**Core idea:** Instead of decomposing a task across models, **run the same task on both a local model and a cloud model simultaneously**. Compare outputs. Use the cloud output only when they disagree (or for critical tasks). The local model output is "free" and used as a first draft.

```
User Prompt
     │
     ├─► Local Model (gemma4:e4b on fnet6) ──▶ Output A ─┐
     │                                                    │
     │                                                    ▼
     │                                             ┌─────────────┐
     │                                             │  Diff       │
     └─► Cloud Model (kimi-k2.6) ──▶ Output B ────▶│  Comparator │
                                                   └─────────────┘
                                                          │
                                    ├─► Match ──▶ Return Output A (free)
                                    │
                                    └─► Mismatch ──▶ Return Output B (paid) + log diff
```

**Advantages:**
- For tasks where local and cloud models agree (~60–70% for simple tasks), cost = $0
- Differential logging reveals **where** local models fail — useful for targeting improvement
- No decomposition overhead, no coordination complexity

**Disadvantages:**
- Requires running two inferences per task (local is free but takes time)
- For tasks where they always disagree, you pay double
- Diff comparison for non-deterministic outputs (creative tasks) is hard

**When to use:** For **draft-quality tasks** where you can afford occasional local model errors:
- Initial code scaffolding
- Documentation drafts
- Data extraction (where you can spot-check samples)
- Brainstorming and ideation

---

## Part 3: Decision Framework — Which Pattern for Which Task

Use this matrix to route each task type to the appropriate architecture:

| Task Characteristic | Pattern | Rationale |
|---------------------|---------|-----------|
| **Repetitive structured workflow** (daily monitoring, reconciliation) | **C — Compiler** | Cloud generates script once, local runs it deterministically. Highest reliability, lowest ongoing cost. |
| **High-volume batch analysis** (backtesting, screening, simulation) | **D — Parallel Batch** | Natural parallelism across 7 nodes. Linear speedup. No coordination needed. |
| **High-frequency same-pattern task** ("Check X and log Y") | **E — Cached Plans** | Skip decomposition. Execute cached plan. Verification only. |
| **Draft-quality creative work** (scaffolding, docs, brainstorming) | **F — Ensemble** | Local first, cloud only when diff detected. ~60% free. |
| **Simple deterministic task** (formatting, classification, status) | **B — Classifier → Local** | Single local call, no decomposition. Fast, essentially free. |
| **Complex novel coding/analysis** | **Cloud direct** | Don't decompose. Local models will fail. Save the overhead. |
| **Multi-step judgment task** | **Cloud direct** | Decomposition won't help. The steps are coupled, not separable. |
| **Inference-only Q&A** (no file editing, no tools) | **A — Ollama Server** | HTTP API call to lab node. No pi overhead. |

---

## Part 4: Recommended Migration Path

### Phase 0: Measure (This Week)

Before changing anything, instrument your current pipeline:

```bash
# Add to your decompose-execute-verify flow
# Track per-task:
# 1. Decomposition cost ($)
# 2. Number of sub-tasks generated
# 3. Local execution failure rate (%)
# 4. Verification failure rate (%)
# 5. Retry count
# 6. End-to-end latency (seconds)
# 7. Final cost vs. cloud-only estimate
```

**Goal:** Establish a baseline. You need evidence, not intuition, about where the pipeline bleeds money.

### Phase 1: Implement the Classification Gate (Week 1)

Add Pattern B as a pre-filter:
- Deploy a `qwen3.5:4b` classifier on the orchestrator
- Route 40% of tasks directly to cloud (skip decomposition)
- Route 35% directly to local execution (skip decomposition + verification)
- Route 25% through existing decompose-execute-verify pipeline

**Expected impact:** 40% reduction in decomposition calls. Immediate cost savings.

### Phase 2: Deploy Ollama-as-Server on High-Capacity Nodes (Week 2)

On fnet5, fnet6, fnet7 (your nodes with the best hardware):
- Stop running `pi` sessions
- Run `ollama serve` with tunneled API access
- Configure model-router.json to route "local" tier to these HTTP endpoints

**Expected impact:** Local inference latency drops from 30–120s to 2–5s per call.

### Phase 3: Script Generation for Top 3 Recurring Workflows (Week 3–4)

Identify your 3 most frequent structured tasks:
1. Portfolio monitoring + logging
2. Daily reconciliation
3. Risk limit checking

For each:
- Use cloud model to generate a Python script template
- Validate script manually
- Deploy script to all lab nodes
- Replace decomposition pipeline with: `ssh fnetX "python3 /opt/scripts/portfolio_monitor.py"`

**Expected impact:** These 3 tasks drop from ~$0.05 each to ~$0.00 (script is deterministic, no model calls).

### Phase 4: Parallel Batch for Backtesting and Screening (Month 2)

When you need to backtest or screen:
- Split data by time period or asset
- Dispatch independent jobs to all 7 nodes via SSH
- Collect and merge results

**Expected impact:** 7× speedup on batch workloads.

### Phase 5: Cache Decomposition Plans for Remaining Recurring Tasks (Month 2)

For tasks that still go through decomposition:
- After the first successful decomposition, save the plan
- On subsequent identical tasks, skip the decomposer
- Load cached plan + execute + verify

**Expected impact:** Another 20–30% reduction in cloud calls for recurring tasks.

---

## Part 5: What to Stop Doing Immediately

| Current Practice | Why It Hurts | Replace With |
|------------------|--------------|--------------|
| Running `pi` interactively on every lab node for every sub-task | Session startup dominates execution time | Ollama API calls (Pattern A) or script execution (Pattern C) |
| Decomposing tasks that are obviously complex judgment tasks | Local models will fail, verifier will catch, cloud will re-run | Classifier gate → cloud direct (Pattern B) |
| Using pi-intercom for execution dispatch | Session-to-session tool, not designed for node-to-node batch dispatch | SSH command dispatch or HTTP API calls |
| Treating all 7 nodes as symmetric | Nodes have different hardware (fnet5 has many models, fnet6/fnet7 have gemma4:e4b) | Role-based assignment: fnet6/fnet7 for heavy inference, fnet1–fnet4 for light tasks or batch segments |
| Re-decomposing the same task types repeatedly | Paying $0.03 for the same plan every day | Cached plans (Pattern E) |
| Verifying every local output with a cloud model | Verification is 40–60% of your cloud spend | Differential execution (Pattern F) or deterministic scripts (Pattern C) |

---

## Appendix: Mathematical Model of Cost vs. Quality

For a task with probability `p` of local model success:

**Current pipeline cost:**
```
C_current = C_decompose + C_verify + (1-p) × C_cloud_retry + N × C_local
```

Where:
- `C_decompose` = ~$0.03
- `C_verify` = ~$0.02
- `C_cloud_retry` = ~$0.15 (full cloud execution on failure)
- `C_local` = ~$0.00 (but high latency)
- `p` = local success rate

**Break-even analysis:**

| Local Success Rate (p) | Current Cost | Cloud-Only Cost | Savings? |
|------------------------|--------------|-----------------|----------|
| 95% (structured data)  | $0.05        | $0.15           | ✅ 67%   |
| 85% (simple coding)    | $0.07        | $0.15           | ✅ 53%   |
| 70% (medium coding)    | $0.10        | $0.15           | ✅ 33%   |
| 50% (complex analysis) | $0.15        | $0.15           | ⚠️ 0%    |
| 30% (judgment tasks)   | $0.22        | $0.15           | ❌ -47%  |

**Conclusion:** Your decomposition pipeline only saves money when `p > ~60%`. For tasks where local models succeed less than 60% of the time, cloud-only is cheaper, faster, and more reliable.

---

*Document version: 1.0*
*Next review: After Phase 0 measurement data is collected*
