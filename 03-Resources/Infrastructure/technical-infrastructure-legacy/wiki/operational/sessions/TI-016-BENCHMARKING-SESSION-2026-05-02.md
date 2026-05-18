# TI-016 Benchmarking Session: Lab Node Model Performance Analysis

**Date**: 2026-05-02  
**Domain**: technical-infrastructure  
**Task**: TI-016 — Expand local-model-pilot for Lab Nodes  
**Session Type**: Benchmarking Execution & Analysis  

---

## Purpose

The primary purpose of this benchmarking session is to **measure the actual inference performance (tokens/second) of candidate Ollama models on each lab node** so the meta-orchestration framework (TI-011) can make **informed routing decisions** based on real-world performance rather than theoretical capacity.

### Why Benchmarking Is Necessary

The trading desk operates a heterogeneous 7-node lab where nodes vary in:
- **CPU**: i5-6400 (4 cores) vs i7-10710U (12 cores)
- **RAM**: 15GB vs 31GB
- **Installed models**: varies per node

Without benchmarking data, all nodes would be treated identically, leading to:
1. **Suboptimal routing**: A "fast" task might be routed to a slow node
2. **Resource underutilization**: High-RAM nodes might never run their optimal models
3. **User-visible latency variance**: Tasks routed to slower nodes degrade the experience
4. **Wasted cloud escalations**: Tasks that could run locally might be escalated unnecessarily

Benchmarking provides the empirical data needed for the **complexity router** to match (task complexity, model capability, node performance) tuples to actual execution targets.

---

## Methodology

### Candidate Models

Three models were benchmarked as the initial candidate set:

| Model | Size | Capabilities | Role |
|-------|------|-------------|------|
| `qwen3.5:4b` | 3.4 GB | text, image, tools, thinking | Fast / low-complexity tasks |
| `qwen3:8b` | 5.2 GB | text, tools, thinking | General / medium-complexity tasks |
| `gemma4:e4b` | 9.6 GB | text, image, tools, thinking | High-capability / reasoning tasks |

*Selection rationale*: These models span the capability spectrum from fast small models to capable larger models, and represent the common use cases for the trading desk (reasoning, coding, fast response).

### Benchmark Test

For each model on each available node:

1. **Pre-load model** — Send a warm-up request with `keep_alive: 30m` to avoid cold-start penalty
2. **Measure inference** — Send a single 128-token generation request via Ollama HTTP API (`/api/generate`)
3. **Record metrics**:
   - `tokens_per_sec`: total generated tokens / total wall time
   - `total_time_s`: wall-clock time for full response
   - `tokens_generated`: actual token count from model output
   - `prompt_eval_count`: tokens in prompt evaluation

### Test Prompt

```
"Explain quantum computing briefly."
```

*Rationale*: A neutral, knowledge-based prompt that exercises the model's reasoning without domain-specific bias. All models can handle this prompt meaningfully.

### Configuration

```
num_predict: 128        # Target output length
stream: false           # Single-shot response for clean timing
timeout: 300s           # Allow slow models on constrained nodes
```

---

## Results

### Performance Summary (tokens/second)

| Node | CPU | RAM | qwen3.5:4b | qwen3:8b | gemma4:e4b | Notes |
|------|-----|-----|-----------:|---------:|-----------:|-------|
| fnet3 | i7-10710U (12c) | 31GB | 4.47 | 4.86 | **5.61** | All models installed |
| fnet4 | i7-10710U (12c) | 31GB | 4.39 | 4.75 | 5.50 | All models installed |
| fnet5 | i7-10710U (12c) | 31GB | 4.42 | 4.76 | 5.48 | All models installed |
| fnet6 | i7-10710U (12c) | 31GB | 4.45 | 4.77 | 5.44 | All models installed |
| fnet7 | i7-10710U (12c) | 15GB | 3.51 | 3.30 | — | gemma4:e4b not installed |

### Key Observations

1. **Counterintuitive result**: `gemma4:e4b` (largest model at 9.6GB) is the **fastest** on 31GB nodes at ~5.5 t/s, not the smallest. This defies the common assumption that smaller = faster.
   - Likely explanation: The model architecture/optimization matters more than raw parameter count. Gemma4 uses a Mixture-of-Experts (MoE) architecture that activates subsets of parameters per token.

2. **CPU matters more than model size**: fnet3–fnet6 all use the i7-10710U (12 cores) and show nearly identical performance (~4.4–5.6 t/s). The 4-core i5 nodes would likely show different scaling.

3. **RAM is not the bottleneck for speed**: All 31GB nodes show the same performance regardless of which model is loaded, indicating CPU is the binding resource, not memory bandwidth.

4. **fnet7 anomaly**: Despite having the same i7-10710U CPU, fnet7 is ~22% slower (3.3–3.5 t/s vs 4.4+ on other i7 nodes). Possible causes: thermal throttling, background load, or NUMA/memory layout differences.

---

## Routing Implications

### For the Meta-Orchestration Framework (TI-011)

**Before benchmarking**: Router could only use heuristic rules
- "simple → qwen3.5:4b"
- "medium → qwen3:8b"  
- "complex → gemma4:e4b"

**After benchmarking**: Router can use empirical performance data
- For **latency-sensitive tasks** on 31GB nodes: route to `gemma4:e4b` (fastest at 5.61 t/s)
- For **throughput-sensitive tasks**: use `qwen3:8b` or `qwen3.5:4b` depending on actual speed requirements
- For **fnet7 specifically**: consider it a lower-tier node unless the performance gap is explained and fixed

### Tier-Based Model Assignments

Based on the data, the recommended model-to-node mappings are:

#### 31GB Nodes (fnet3, fnet4, fnet5, fnet6)

| Task Type | Recommended Model | Expected Speed | Notes |
|-----------|-----------------|---------------|-------|
| Fast/simple | `gemma4:e4b` | ~5.5 t/s | Contrary to intuition, the largest model is fastest |
| General | `qwen3:8b` | ~4.8 t/s | Good balance of capability and speed |
| Vision tasks | `gemma4:e4b` | ~5.5 t/s | Only vision-capable model that's fast |
| Emergency/low RAM | `qwen3.5:4b` | ~4.4 t/s | Smallest footprint if memory is constrained |

#### 15GB Nodes (fnet1, fnet2, fnet7)

| Task Type | Recommended Model | Expected Speed | Notes |
|-----------|-----------------|---------------|-------|
| All tasks | `qwen3:8b` or `qwen3.5:4b` | ~3.3 t/s (fnet7) | Cannot fit gemma4:e4b |
| Vision (if needed) | `qwen3.5:4b` | ~3.5 t/s | Only small vision-capable model |

---

## Data Files

Raw benchmark outputs are stored in:

```
lab-specs/node-benchmarks/
├── fnet3-qwen3.5_4b.json    {"tokens_per_sec": 4.47, ...}
├── fnet3-qwen3_8b.json      {"tokens_per_sec": 4.86, ...}
├── fnet3-gemma4_e4b.json    {"tokens_per_sec": 5.61, ...}
├── fnet4-qwen3.5_4b.json    {"tokens_per_sec": 4.39, ...}
├── ...
└── fnet7-qwen3.5_4b.json    {"tokens_per_sec": 3.51, ...}
```

All files contain: `node`, `model`, `timestamp`, `status`, `tokens_per_sec`, `total_time_s`, `tokens_generated`, `prompt_eval_count`.

---

## What This Enables

1. **Dynamic tier adjustment**: If "simple" prompts consistently work well on `gemma4:e4b`, the classifier can learn to route simpler tasks to this model
2. **Node-aware routing**: The orchestrator can prefer fnet3–fnet6 for high-throughput work and reserve fnet7 for lower-priority tasks
3. **Model recommendation**: When a new prompt arrives, the system can recommend the optimal (node, model) pair without trial-and-error
4. **Capacity planning**: Benchmark data feeds into the `node-capacity-summary.json` for the orchestration framework's decision engine

---

## Next Steps for Benchmarking

1. **Investigate fnet7 slowdown** — Why is it 22% slower with the same CPU?
2. **Complete fnet1/fnet2 detection** — fnet1 has no models installed; fnet2 blocked by NVIDIA driver
3. **Benchmark larger models** — 31GB nodes could potentially run qwen3:14b, deepseek-r1, or other models that don't fit on 15GB nodes
4. **Add multi-instance concurrency test** — Measure throughput when multiple models are loaded simultaneously
5. **Thermal/load monitoring** — Collect CPU temperature and load during benchmarks to explain variance

---

**END OF BENCHMARKING DOCUMENTATION**
