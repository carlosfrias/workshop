# Planning: TI-023 Orchestrator Health Monitoring + Workload Redistribution
**Date:** 2026-05-02 23:00 ET  
**Status:** In Progress  
**Session:** TI-023  
**Rationale:** During wiki generation session, Mac orchestrator ran under heavy memory pressure while continuing to decompose tasks locally. No health monitoring existed to detect stress or redistribute workload to lab nodes. This causes the orchestrator to freeze for 20+ seconds, degrading user experience.

## Problem
- Lab nodes have health monitoring (`check-lab-status.yml`) → works ✅
- Orchestrator has ZERO health monitoring → blind ❌
- Decomposition always routes to Mac locally → never checks if Mac is stressed
- Result: Mac runs gemma4:e4b for synthesis + SSH/git/Dropbox simultaneously → frozen

## Solution
Add psutil-based health monitoring to Mac with 3 thresholds that affect decomposition routing.

## Components

### Component 1: Health Check Service (`orchestrator_health.py`)
Fast, lightweight check (<100ms, no model calls):
- `psutil.virtual_memory().percent` → RAM usage
- `os.getloadavg()[0]` → 1-min CPU load average
- `psutil.swap_memory().used > 0` → swap detection
- `psutil.sensors_temperatures()` → temperature (if available)

Returns: `"healthy" | "stressed" | "critical"`

### Component 2: Integration into Classifier (`classify_prompt.py`)
Before routing to "local" tier, check orchestrator health:
- `healthy` → route normally (qwen3.5:4b or qwen3:8b)
- `stressed` → skip local, route to fnet3 for decomposition
- `critical` → skip local + lab, route to cloud LOW

### Component 3: Integration into Decomposer (`decompose_llm.py`)
When `--orchestrator-health-aware` flag set:
- Check health before calling local model
- If stressed: submit task to fnet3 via submit_task.py
- If critical: use cloud LOW tier directly

### Component 4: Integration into Watcher (`decompose-watcher.py`)
Before local synthesis (gemma4:e4b):
- Check health
- If stressed: synthesis on fnet3 with qwen3:8b (slower but frees Mac)
- If critical: synthesis on cloud (kimi-k2.6 or qwen3.5:397b)

## Thresholds (Mac M4 Pro, 24GB RAM, 14 cores)

| Status | RAM % | CPU Load | Swap | Action |
|--------|-------|----------|------|--------|
| healthy | <80% | <4.0 | 0 | Decompose locally (qwen3.5:4b) |
| stressed | 80-92% | 4.0-6.0 | 0 | Decompose on fnet3 (qwen3:8b) |
| critical | >92% | >6.0 | >0 | Decompose on cloud LOW |

## Test Plan
1. Idle Mac → healthy → decompose locally
2. Load gemma4:e4b → stressed → decompose on fnet3
3. Load 2x models → critical → decompose on cloud
4. Verify synthesis also respects health levels

## Files
| File | Role |
|------|------|
| `scripts/orchestrator_health.py` | New — health check service |
| `scripts/classify_prompt.py` | Modified — health check before routing |
| `scripts/decompose_llm.py` | Modified — `--orchestrator-health-aware` flag |
| `scripts/decompose-watcher.py` | Modified — health before synthesis |

## Effort: 3-4 hours
