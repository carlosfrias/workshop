# Module 5: Performance Metrics

**Version:** 1.0  
**Tokens:** ~140  
**Load Trigger:** User asks "how long", "performance", "time", "speed", "latency"  
**Unload:** After response sent

---

## Expected Execution Times

| Environment | Avg Time | P95 Time | P99 Time | Target |
|-------------|----------|----------|----------|--------|
| Development | {time} | {time} | {time} | <{target} |
| Staging | {time} | {time} | {time} | <{target} |
| Production | {time} | {time} | {time} | <{target} |

**Example:**

| Environment | Avg Time | P95 Time | P99 Time | Target |
|-------------|----------|----------|----------|--------|
| Development | 8s | 12s | 18s | <15s |
| Staging | 10s | 15s | 22s | <20s |
| Production | 12s | 18s | 25s | <25s |

---

## Resource Usage

| Metric | Average | Peak | Limit |
|--------|---------|------|-------|
| **CPU** | {percentage} | {percentage} | {percentage} |
| **Memory** | {GB} | {GB} | {GB} |
| **Network** | {Mbps} | {Mbps} | {Mbps} |
| **Disk I/O** | {MB/s} | {MB/s} | {MB/s} |

**Example:**

| Metric | Average | Peak | Limit |
|--------|---------|------|-------|
| **CPU** | 15% | 35% | 50% |
| **Memory** | 2.1 GB | 3.5 GB | 4 GB |
| **Network** | 50 Mbps | 120 Mbps | 200 Mbps |
| **Disk I/O** | 25 MB/s | 45 MB/s | 100 MB/s |

---

## Performance History

| Date | Execution Time | Status | Notes |
|------|----------------|--------|-------|
| {date} | {time} | ✅/❌ | {notes} |
| {date} | {time} | ✅/❌ | {notes} |
| {date} | {time} | ✅/❌ | {notes} |

**Example:**

| Date | Execution Time | Status | Notes |
|------|----------------|--------|-------|
| 2026-05-04 | 11s | ✅ | Normal execution |
| 2026-05-03 | 28s | ⚠️ | High network latency |
| 2026-05-02 | 9s | ✅ | Optimal conditions |

---

## Performance by Model

| Model | Parameters | Avg Time | Context Tokens |
|-------|------------|----------|----------------|
| **gemma4:e4b** | 4B | 12s | 450-650 |
| **qwen3.5:4b** | 4B | 10s | 320-480 |
| **qwen3:8b** | 8B | 8s | 280-420 |
| **Cloud (qwen3.5:397b)** | 397B | 5s | 500-700 |

---

## Optimization Tips

1. **{Tip 1}**
   - Example: "Run during low-traffic hours (2:00-5:00 AM)"

2. **{Tip 2}**
   - Example: "Clear cache before execution for consistent timing"

3. **{Tip 3}**
   - Example: "Use parallel execution for large deployments"

---

## Performance Thresholds

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| Execution Time | >{value} | >{value} | {action} |
| CPU Usage | >{value} | >{value} | {action} |
| Memory Usage | >{value} | >{value} | {action} |

**Example:**

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| Execution Time | >20s | >30s | Investigate bottleneck |
| CPU Usage | >70% | >90% | Scale resources |
| Memory Usage | >75% | >90% | Clear cache |

---

## Benchmarking Command

```bash
# Run performance benchmark
python3 technical-infrastructure/scripts/benchmark-playbook.py \
  --playbook {playbook_name} \
  --iterations 10
```

---

## Questions This Module Answers

- ✅ "How long does {playbook} take?"
- ✅ "What is the performance of {playbook}?"
- ✅ "Can {playbook} complete in under {time}?"
- ✅ "What affects {playbook} performance?"

---

## Questions This Module Does NOT Answer

- ❌ "What does {playbook} do?" → Load Module 1
- ❌ "What does {playbook} depend on?" → Load Module 2
- ❌ "What data does {playbook} use?" → Load Module 3
- ❌ "When should {playbook} run?" → Load Module 4
- ❌ "What hardware is needed?" → Load Module 6

---

**Module End**

*Return to core prompt after use*
