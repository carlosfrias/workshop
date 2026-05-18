# Binary Decomposition System

**Document ID:** `TI-032-BINARY-DECOMPOSITION-v1.0`  
**Created:** 2026-05-05  
**Priority:** 🔴 **P1 (High)**  
**Status:** ✅ **IMPLEMENTED**  
**Related:** [TI-031-TI032 Integration Master Prompt](../../operational/planning/TI031-TI032-INTEGRATION-MASTER-PROMPT.md)

---

## Overview

The Binary Decomposition System splits high-complexity tasks into 2 equal sub-tasks with recursive decomposition when needed. It is **health-aware** — only triggering when the orchestrator is in `stressed` or `critical` status.

---

## How Binary Decomposition Works

### Core Algorithm

```
┌─────────────────────────────────────────────────────────────────┐
│  Input: High-complexity task (complexity >= 7)                 │
│         Health status: stressed or critical                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: Split task into 2 equal sub-tasks (Part A, Part B)    │
│         - Complexity reduced by ~40% per split                 │
│         - Description split by sentences or words              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: Check each sub-task                                    │
│         - If complexity still > 5 AND depth < max_depth:       │
│           → Recursively decompose                              │
│         - If complexity <= 5 OR depth >= max_depth:            │
│           → Stop decomposition                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Output: List of leaf sub-tasks (complexity <= 5)              │
│          Ready for parallel execution                          │
└─────────────────────────────────────────────────────────────────┘
```

### Recursive Decomposition

```
Depth 0: Original Task (complexity=10)
              ↓
         ┌────┴────┐
         ↓         ↓
Depth 1: A         B        (complexity=6 each)
         ↓         ↓
      ┌──┴──┐   ┌──┴──┐
      ↓     ↓   ↓     ↓
Depth 2: Aa  Ab  Ba  Bb   (complexity=4 each — STOP)

Result: 4 leaf tasks (Aa, Ab, Ba, Bb)
```

**Max Depth:** 3 levels (configurable via `--max-depth`)

---

## When Binary Decomposition Triggers

### Health-Aware Triggering

| Health Status | Complexity < 7 | Complexity >= 7 |
|---------------|----------------|-----------------|
| **HEALTHY**   | No decompose   | Decompose       |
| **STRESSED**  | No decompose   | **Decompose**   |
| **CRITICAL**  | No decompose   | **Decompose**   |

**Key Rule:** Decomposition only triggers when:
1. Complexity score >= 7, **AND**
2. Health status is `stressed` or `critical` (or complexity alone if very high)

### Complexity Thresholds

| Score | Level | Action |
|-------|-------|--------|
| 1-3   | LOW   | Execute as-is |
| 4-6   | MEDIUM | Execute as-is |
| 7-8   | HIGH  | Binary decompose (depth 1-2) |
| 9-10  | CRITICAL | Binary decompose (depth 2-3) |

---

## Files

| File | Purpose |
|------|---------|
| `technical-infrastructure/scripts/binary_decompose.py` | Decomposition engine |
| `technical-infrastructure/scripts/task_synthesizer.py` | Result synthesis |
| `technical-infrastructure/logs/binary_decomposition.jsonl` | Decomposition logs |
| `technical-infrastructure/logs/task_synthesis.jsonl` | Synthesis logs |

---

## Usage

### Decompose a Task

```bash
# Basic usage
python3 technical-infrastructure/scripts/binary_decompose.py \
    --task "Analyze market data and generate trading signals" \
    --complexity 8

# With health check
python3 technical-infrastructure/scripts/binary_decompose.py \
    --task "Complex integration task" \
    --complexity 9 \
    --check-health

# Output as JSON
python3 technical-infrastructure/scripts/binary_decompose.py \
    --task "Task description" \
    --complexity 8 \
    --json

# Run tests
python3 technical-infrastructure/scripts/binary_decompose.py --test
```

### Synthesize Results

```bash
# Synthesize from result files
python3 technical-infrastructure/scripts/task_synthesizer.py \
    --results result1.json result2.json

# Synthesize from directory
python3 technical-infrastructure/scripts/task_synthesizer.py \
    --directory /srv/tasks/completed/ \
    --pattern "*.json"

# Output as JSON
python3 technical-infrastructure/scripts/task_synthesizer.py \
    --results *.json \
    --json

# Save to file
python3 technical-infrastructure/scripts/task_synthesizer.py \
    --results *.json \
    --output synthesis.json

# Run tests
python3 technical-infrastructure/scripts/task_synthesizer.py --test
```

---

## Examples

### Example 1: Before/After Decomposition

**Before (Single Task):**
```json
{
  "id": "task-20260505120000",
  "description": "Analyze market data from multiple exchanges, synchronize trading signals, and coordinate execution across nodes",
  "complexity": 9,
  "estimated_latency": "45-60s"
}
```

**After (Decomposed):**
```json
{
  "status": "decomposed",
  "total_sub_tasks": 4,
  "max_depth_reached": 2,
  "sub_tasks": [
    {
      "id": "task-20260505120000-a-0",
      "description": "Analyze market data from multiple exchanges",
      "complexity": 5,
      "depth": 1,
      "part": "A"
    },
    {
      "id": "task-20260505120000-b-0",
      "description": "Synchronize trading signals and coordinate execution across nodes",
      "complexity": 5,
      "depth": 1,
      "part": "B"
    },
    {
      "id": "task-20260505120000-a-1",
      "description": "Synchronize trading signals",
      "complexity": 3,
      "depth": 2,
      "part": "A"
    },
    {
      "id": "task-20260505120000-b-1",
      "description": "Coordinate execution across nodes",
      "complexity": 3,
      "depth": 2,
      "part": "B"
    }
  ]
}
```

### Example 2: Synthesis Result

**Input:** 2 sub-task results
```json
[
  {"id": "task-a", "status": "success", "stdout": "Market analysis complete"},
  {"id": "task-b", "status": "success", "stdout": "Signals synchronized"}
]
```

**Output (Synthesis):**
```json
{
  "synthesis_id": "synth-20260505120500",
  "synthesis_status": "success",
  "combined_output": "--- task-a ---\nMarket analysis complete\n\n--- task-b ---\nSignals synchronized",
  "metrics": {
    "total_sub_tasks": 2,
    "successful_tasks": 2,
    "success_rate": 1.0,
    "efficiency_score": 95.5
  },
  "recommendation": "All sub-tasks completed successfully."
}
```

---

## Performance Metrics

### Decomposition Performance

| Metric | Target | Actual (Test) |
|--------|--------|---------------|
| Decomposition latency | < 100ms | ~50ms |
| Max depth enforcement | 100% | ✅ Pass |
| Complexity reduction | 40% per split | ✅ Pass |
| Health-aware triggering | 100% | ✅ Pass |

### Synthesis Performance

| Metric | Target | Actual (Test) |
|--------|--------|---------------|
| Synthesis latency | < 200ms | ~100ms |
| Partial failure handling | 100% | ✅ Pass |
| Metrics accuracy | 100% | ✅ Pass |
| Output combination | Sequential | ✅ Pass |

---

## Integration Points

### With Health Monitoring (TI-031)

```python
# binary_decompose.py automatically checks health
from binary_decompose import check_health, binary_decompose

health = check_health()  # Returns: healthy/stressed/critical
result = binary_decompose(task, complexity=8, health_status=health)
```

### With Task Orchestrator

```bash
# Decompose high-complexity task
sub_tasks=$(python3 binary_decompose.py --task "$TASK" --complexity 8 --json)

# Execute sub-tasks in parallel
for task in $(echo "$sub_tasks" | jq -r '.sub_tasks[]'); do
    submit_task.py --task "$task" &
done

# Wait and synthesize
wait
python3 task_synthesizer.py --directory /srv/tasks/completed/
```

---

## Testing

### Run All Tests

```bash
# Test binary decomposition
python3 technical-infrastructure/scripts/binary_decompose.py --test

# Test task synthesizer
python3 technical-infrastructure/scripts/task_synthesizer.py --test
```

### Test Coverage

| Test | Status |
|------|--------|
| High complexity → binary split | ✅ Pass |
| Recursive decomposition | ✅ Pass |
| Low complexity → no decompose | ✅ Pass |
| Health-aware triggering | ✅ Pass |
| Max depth enforcement | ✅ Pass |
| Partial failure handling | ✅ Pass |
| Complete failure handling | ✅ Pass |
| Metrics calculation | ✅ Pass |

---

## Logs

### Decomposition Log Format

**File:** `technical-infrastructure/logs/binary_decomposition.jsonl`

```json
{
  "timestamp": "2026-05-05T12:00:00",
  "health_status": "stressed",
  "original_task_id": "task-20260505120000",
  "original_complexity": 8,
  "sub_task_count": 4,
  "sub_task_ids": ["task-a-0", "task-b-0", "task-a-1", "task-b-1"],
  "max_depth": 2
}
```

### Synthesis Log Format

**File:** `technical-infrastructure/logs/task_synthesis.jsonl`

```json
{
  "timestamp": "2026-05-05T12:05:00",
  "synthesis_id": "synth-20260505120500",
  "original_task_id": "task-20260505120000",
  "synthesis_status": "success",
  "total_sub_tasks": 4,
  "successful_tasks": 4,
  "efficiency_score": 95.5,
  "total_elapsed_seconds": 12.5,
  "partial_failure": false
}
```

---

## Troubleshooting

### Issue: Decomposition not triggering

**Check:**
1. Is complexity >= 7?
2. Is health status stressed/critical?
3. Run with `--verbose` flag

### Issue: Too many sub-tasks generated

**Solution:** Reduce `--max-depth` parameter (default: 3)

### Issue: Synthesis fails with partial results

**Expected:** Partial failures are handled gracefully. Check `failure_details` in synthesis output.

---

## Related Documents

- [TI-031 Health Monitoring](./unified-health-monitoring.md)
- [TI-032 Master Prompt Architecture](./master-prompt-architecture.md)
- [Task Orchestration Guide](../../operational/task-orchestration.md)

---

**Owner:** Technical Infrastructure Team  
**Last Updated:** 2026-05-05  
**Version:** 1.0
