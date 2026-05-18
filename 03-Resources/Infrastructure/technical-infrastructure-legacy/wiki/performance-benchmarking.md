# Performance Benchmarking Suite

**Status:** ✅ COMPLETE  
**Last Updated:** 2026-05-05  
**Related:** [TI-032 Master Prompt System](master-prompt-guide), [Benchmark Results](operational/status/BENCHMARK-RESULTS-2026-05-05)

---

## Overview

The **Performance Benchmarking Suite** measures the speed and efficiency of all TI-032 Master Prompt System components. It validates that our 2-billion parameter models can trigger playbooks at production speed.

**Philosophy:** If health check, decomposition, or escalation takes too long, the small model will time out or lose context. Every millisecond matters.

---

## Quick Start

```bash
# Run full benchmark suite
python3 technical-infrastructure/scripts/benchmark-suite.py --all --iterations 10

# Run specific benchmark
python3 technical-infrastructure/scripts/benchmark-suite.py --health-check
python3 technical-infrastructure/scripts/benchmark-suite.py --decomposition
python3 technical-infrastructure/scripts/benchmark-suite.py --escalation

# Generate JSON report
python3 technical-infrastructure/scripts/benchmark-suite.py --all --json --output report.json

# Use custom iterations
python3 technical-infrastructure/scripts/benchmark-suite.py --all --iterations 20
```

---

## Benchmarks

### 1. Health Check Benchmark

**What it measures:** Time to check system health (RAM, CPU, swap)  
**Target:** < 1000 ms  
**Critical:** If health check is slow, every playbook execution is delayed

```bash
python3 technical-infrastructure/scripts/benchmark-suite.py --health-check
```

**Components tested:**
- `orchestrator_health.py --json`
- psutil RAM/CPU measurement
- JSON serialization

**Latest Result:** 1122 ms average (⚠️ 12% over target)  
**Root cause:** Python interpreter cold-start  
**Fix:** Pre-warm with `python3 -c "import psutil; psutil.virtual_memory()"`

---

### 2. Decomposition Speed Benchmark

**What it measures:** Time to split a complex task into sub-tasks  
**Target:** < 2000 ms  
**Critical:** Decomposition happens on stressed systems — must be fast

```bash
python3 technical-infrastructure/scripts/benchmark-suite.py --decomposition
```

**Components tested:**
- `binary_decompose.py --task X --complexity Y`
- Recursive splitting (max depth 3)
- Task graph construction

**Latest Result:** 1260 ms average (✅ 37% under target)  
**Status:** Plenty of headroom for growth

---

### 3. Escalation Speed Benchmark

**What it measures:** Time to route to cloud tiers  
**Target:** < 3000 ms  
**Critical:** Users shouldn't wait for escalation decisions

```bash
python3 technical-infrastructure/scripts/benchmark-suite.py --escalation
```

**Components tested:**
- `cloud_escalation.py --task X`
- Tier selection logic
- Cost calculation

**Latest Result:** 120 ms average (✅ 96% under target)  
**Status:** Extremely fast — minimal user-visible delay

---

### 4. Module Loading Benchmark

**What it measures:** Time to load modular prompt components  
**Target:** < 500 ms  
**Critical:** Module loading is on-demand — every request may need it

```bash
python3 technical-infrastructure/scripts/benchmark-suite.py --module-loading
```

**Components tested:**
- File I/O for `module-{1-6}-*.md`
- Markdown parsing
- Token counting

**Latest Result:** ~100 ms estimated (✅ 80% under target)  
**Status:** File I/O on SSD is negligible

---

### 5. Context Size Benchmark

**What it measures:** Token count of loaded prompts  
**Target:** < 650 tokens total  
**Critical:** 2B models have small context windows

```bash
python3 technical-infrastructure/scripts/benchmark-suite.py --context-size
```

**Components tested:**
- `core-prompt.md` (always loaded)
- `module-{1-6}-*.md` (on-demand)
- Token estimation (chars ÷ 4)

**Latest Results:**

| Scenario | Tokens | Status |
|----------|--------|--------|
| Core only | ~200 | ✅ |
| Core + 1 module | ~300 | ✅ |
| Core + 2 modules | ~350 | ✅ |
| Core + 3 modules | ~400 | ✅ |
| Core + all modules | ~480 | ✅ |

**Status:** 60-70% headroom — can add 2-3 more modules without exceeding limit

---

## Results Archive

| Date | Report | Status | Health | Decomp | Escalation |
|------|--------|--------|--------|--------|------------|
| 2026-05-05 | [BENCHMARK-RESULTS-2026-05-05](operational/status/BENCHMARK-RESULTS-2026-05-05) | 90% pass | 1122ms | 1260ms | 120ms |

---

## Benchmark Script Reference

**Location:** `technical-infrastructure/scripts/benchmark-suite.py`

**Features:**
- Configurable iterations (default: 10)
- Statistical analysis (mean, p95, p99, stddev)
- JSON export for automation
- Threshold validation (pass/warn/fail)
- Historical comparison (future feature)

**Dependencies:**
- Python 3.10+
- NumPy (for statistics)
- All TI-032 scripts (health, decompose, escalate)

---

## Performance Targets

| Metric | Target | Critical Threshold | Current |
|--------|--------|-------------------|---------|
| Health Check | < 1000 ms | > 2000 ms | 1122 ms |
| Decomposition | < 2000 ms | > 5000 ms | 1260 ms |
| Escalation | < 3000 ms | > 5000 ms | 120 ms |
| Module Loading | < 500 ms | > 1000 ms | ~100 ms |
| Context Size | < 650 tokens | > 1000 tokens | ~480 tokens |

---

## Optimization Guide

### If Health Check is Slow (>1000ms)

1. **Pre-warm Python process**
   ```bash
   python3 -c "import psutil; psutil.virtual_memory()"
   ```

2. **Keep process alive (daemon mode)**
   ```bash
   # Add to systemd or launchd
   python3 orchestrator_health.py --daemon
   ```

3. **Cache results for 100ms TTL**
   ```python
   # In health_aware_executor.py
   if time_since_last_check < 0.1:
       return cached_result
   ```

### If Decomposition is Slow (>2000ms)

1. **Increase parallelism**
   ```python
   # Use asyncio.gather for sub-task creation
   sub_tasks = await asyncio.gather(*tasks)
   ```

2. **Cache decomposition patterns**
   ```python
   decomposition_cache = {}
   if task_hash in cache:
       return cache[task_hash]
   ```

### If Context Exceeds 650 Tokens

1. **Compress module content**
   - Remove verbose examples
   - Use abbreviations
   - Strip markdown formatting

2. **Load fewer modules**
   - Only load modules matching keywords
   - Lazy-load on first use

3. **Split into multiple prompts**
   - First prompt: identify keyword
   - Second prompt: load relevant module

---

## Related Documents

- [Master Prompt Guide](master-prompt-guide) — Full system documentation
- [Benchmark Results](operational/status/BENCHMARK-RESULTS-2026-05-05) — Latest measurements
- [Quick Start](master-prompt-quickstart) — Deploy in 5 minutes
- [Architecture](master-prompt-architecture) — Design decisions
- [Acceptance Testing](technical-infrastructure/acceptance-testing) — Functional tests
