# ⚠️ SUPERSEDED BY UNIFIED PLAN

**Status:** 📦 **ARCHIVED / SUPERSEDED**  
**Superseded By:** [`unified-health-monitoring.md`](../../wiki/technical-infrastructure/unified-health-monitoring.md)  
**Reason:** Gap analysis has been addressed and integrated into the Integrated Health-Aware Playbook Monitoring System (Master Plan).

---

**Original Content Below (For Reference):**

*Note: All 8 gaps identified in this assessment have been resolved in the unified plan. Please refer to the unified plan for current implementation guidance.*

---

**Date:** 2026-05-05  
**Assessor:** Systematic evaluation of TI-031 vs. Master Prompt Monitoring  
**Status:** 🔍 **ASSESSMENT COMPLETE** — Critical gaps identified

---

## Executive Summary

**TI-031 (Orchestrator Health Monitoring Protocol)** is a **critical safety guardrail** that monitors the Mac orchestrator's health (RAM, CPU, swap) on every prompt. It triggers automatic decomposition and cloud offloading when thresholds are breached.

**Current Master Prompt work** includes basic monitoring (orchestrator-status.py) but **lacks**:
1. Real-time orchestrator health integration
2. Automatic decomposition triggers based on health
3. Node recovery timeout mechanisms
4. Tiered cloud escalation for saturated nodes
5. Integration with phase-2/phase-3 planning files

**Assessment:** The master prompt monitoring is **playbook-centric** (queue depth, execution latency, failed executions). TI-031 is **orchestrator-centric** (RAM%, CPU load, swap usage). These are complementary but **not integrated**.

---

## TI-031 Coverage Matrix

### What TI-031 Covers ✅

| Feature | Implementation | Status |
|---------|---------------|--------|
| **RAM% monitoring** | `psutil.virtual_memory()` | ✅ Active |
| **CPU load monitoring** | `os.getloadavg()` | ✅ Active |
| **Swap usage monitoring** | `psutil.swap_memory()` | ✅ Active |
| **Health thresholds** | Healthy <80% / Stressed 80-92% / Critical >92% | ✅ Active |
| **Automatic decomposition** | Triggered on stressed/critical | ✅ Active |
| **Cloud offloading** | Routes to qwen3.5:397b-cloud or kimi-k2.6 | ✅ Active |
| **Health logging** | `health-decisions.jsonl` | ✅ Active |
| **Phase-2 integration** | Framework readiness check | ✅ Active |
| **Phase-3 integration** | Pre-execution health check | ✅ Active |

### What Master Prompt Monitoring Covers ✅

| Feature | Implementation | Status |
|---------|---------------|--------|
| **Queue depth monitoring** | `--queue` flag | ✅ Active |
| **Execution latency** | Performance metrics | ✅ Active |
| **Failed execution rate** | >5% warning, >15% critical | ✅ Active |
| **Keyword match rate** | <80% warning, <60% critical | ✅ Active |
| **Background scheduling** | Cron-based with resource limits | ✅ Active |
| **Trigger keyword registry** | 32 registered triggers | ✅ Active |
| **Playbook health** | `--health` check (6 components) | ✅ Active |

---

## 🚨 Critical Gaps Identified

### Gap 1: Orchestrator Health → Playbook Routing Integration
**Severity:** 🔴 **CRITICAL**

**Issue:** TI-031 health checks run on the orchestrator (Mac M4 Pro), but playbook execution decisions are not dynamically adjusted based on orchestrator health.

**Current Behavior:**
```
User Prompt → Keyword Router → Playbook Executor
                    ↓
           (No health check before execution)
```

**Required Behavior:**
```
User Prompt → Health Check (TI-031) → Decision
                  ↓
    ├─ HEALTHY → Keyword Router → Local Model
    ├─ STRESSED → Decompose → Cloud Model (Tier 0)
    └─ CRITICAL → Decompose → Cloud Model (Tier 1)
```

**Impact:** Without integration, the orchestrator can become saturated while executing playbooks locally, degrading performance and user experience.

**Solution:** Integrate `orchestrator_health.py --json` call into the playbook execution flow before model selection.

---

### Gap 2: Node Stress → 2x Decomposition
**Severity:** 🔴 **CRITICAL**

**Issue:** The user's requirement specifies that if a node becomes stressed or memory saturated, the task should be **decomposed into 2x smaller tasks** and rerouted. TI-031 only triggers standard decomposition (not 2x). The master prompt has no decomposition logic at all.

**Current State:**
- TI-031: "Decompose and offload" (single decomposition)
- Master Prompt: No decomposition logic
- User Requirement: "2x decomposition" (binary split, recursive)

**Required Implementation:**
```python
def handle_node_stress(task, node):
    """
    Binary decomposition for stressed nodes.
    Split task into 2 sub-tasks, attempt routing.
    """
    # Check node health
    health = check_node_health(node)
    
    if health['status'] in ['stressed', 'critical']:
        # Decompose into 2x tasks
        sub_task_1, sub_task_2 = binary_decompose(task)
        
        # Attempt routing to other nodes
        for sub_task in [sub_task_1, sub_task_2]:
            target_node = find_healthy_node(sub_task['complexity'])
            if target_node:
                route_task(sub_task, target_node)
            else:
                # No nodes available → escalate to cloud
                escalate_to_cloud(sub_task, tier='low')
```

**Solution:** Add binary decomposition logic to the orchestration framework with recursive routing.

---

### Gap 3: Node Recovery Timeout
**Severity:** 🟡 **HIGH**

**Issue:** Neither TI-031 nor the master prompt defines a **recovery timeout** for saturated nodes. The user specifically requires this.

**Current State:**
- TI-031: Monitors health but has no recovery mechanism
- Master Prompt: No timeout configuration

**Required Implementation:**
```yaml
recovery_timeout:
  duration: 60  # Seconds
  conditions:
    - memory < 75%
    - cpu_load < 3.0
    - swap_used == 0
  action: "mark_node_available"
  retry_interval: 10  # Check every 10 seconds
```

**Solution:** Add node recovery watcher with configurable timeout.

---

### Gap 4: Tiered Cloud Escalation (Low → Medium → High)
**Severity:** 🟡 **HIGH**

**Issue:** TI-031 routes to `qwen3.5:397b-cloud` (stressed) or `kimi-k2.6` (critical). The user wants **progressive escalation** starting from low tier, then medium, then high.

**TI-031 Current:**
- Stressed → qwen3.5:397b-cloud (Tier 0)
- Critical → kimi-k2.6 (Tier 1)

**User Requirement:**
- No nodes available → Low tier (qwen3.5:397b-cloud)
- Low tier saturated → Medium tier (qwen3.5:397b-cloud with higher priority)
- Medium tier saturated → High tier (kimi-k2.6)

**Solution:** Implement tiered escalation with fallback logic.

---

### Gap 5: Lab Node Health Monitoring
**Severity:** 🟡 **HIGH**

**Issue:** TI-031 only monitors the **orchestrator** (Mac). The master prompt only monitors **playbook execution metrics**. Neither monitors **lab node health** (fnet1-fnet7).

**Current State:**
- Orchestrator health: ✅ Monitored (TI-031)
- Playbook metrics: ✅ Monitored (orchestrator-status.py)
- Lab node health: ❌ Not monitored

**Required:**
```python
def check_lab_node_health(node_id):
    """
    Check health of fnet{1-7} nodes.
    Returns: healthy | stressed | critical | offline
    """
    ssh_result = ssh_check(node_id, 'ollama list')
    memory = ssh_check(node_id, 'free -m')
    cpu = ssh_check(node_id, 'uptime')
    
    # Evaluate thresholds
    if memory['available'] < 1GB:
        return 'critical'
    elif cpu['load'] > 4.0:
        return 'stressed'
    else:
        return 'healthy'
```

**Solution:** Extend health monitoring to lab nodes via SSH/remote checks.

---

### Gap 6: Health-Based Model Selection
**Severity:** 🟡 **MEDIUM**

**Issue:** The master prompt's model routing guide does not factor orchestrator health into model selection.

**Current Model Routing:**
```yaml
Bookkeeping: ollama/gemma4:e4b
Position monitoring: ollama/qwen3.5:4b
Infrastructure: ollama/qwen3:8b
```

**Required Health-Aware Routing:**
```yaml
Bookkeeping:
  healthy: ollama/gemma4:e4b
  stressed: ollama-cloud/qwen3.5:397b
  critical: ollama-cloud/kimi-k2.6

Position monitoring:
  healthy: ollama/qwen3.5:4b
  stressed: ollama-cloud/qwen3.5:397b
  critical: ollama-cloud/kimi-k2.6
```

**Solution:** Add health state to model routing decisions.

---

### Gap 7: Integration with Phase Files
**Severity:** 🟡 **MEDIUM**

**Issue:** TI-031 requires integration with `phase-2-planning.md` and `phase-3-execution.md`. The master prompt does not reference phase files.

**TI-031 Requirement:**
- Phase 2: "Framework Readiness Check" must include health check
- Phase 3: "Pre-execution health check" must run before file edits/scripts

**Master Prompt Current:** No phase file references.

**Solution:** Add phase-aware health checks to master prompt execution flow.

---

### Gap 8: Memory Reuse Under Stress
**Severity:** 🟡 **MEDIUM**

**Issue:** The master prompt's "memory-reuse" pattern (Module 2 in execution framework) does not account for orchestrator memory stress.

**Current:**
```python
persistent_state = {
    'trigger_keyword': playbook['trigger'],
    'execution_id': generate_id(),
    'start_time': datetime.now(),
}
```

**Required Under Stress:**
```python
# Check health before allocating state
health = check_orchestrator_health()
if health['status'] == 'critical':
    # Minimal state only
    persistent_state = {
        'execution_id': generate_id(),
    }
    # Offload context to cloud model
    return route_to_cloud(playbook, tier='low')
else:
    # Full state allocation
    persistent_state = {
        'trigger_keyword': playbook['trigger'],
        'execution_id': generate_id(),
        'start_time': datetime.now(),
    }
```

**Solution:** Make memory-reuse pattern health-aware.

---

## Integration Requirements

### Required Changes

#### 1. Update `orchestrator-status.py`
```python
def check_orchestrator_health():
    """Add TI-031 health check integration"""
    result = subprocess.run(
        ['python3', 'orchestrator_health.py', '--json'],
        capture_output=True, text=True
    )
    return json.loads(result.stdout)

def check_lab_node_health(node_id):
    """Add lab node health check"""
    # SSH-based health check for fnet nodes
    pass

def make_routing_decision(task, health_status):
    """Health-aware routing with 2x decomposition"""
    if health_status == 'healthy':
        return route_to_local(task)
    elif health_status == 'stressed':
        # 2x decomposition
        sub_tasks = binary_decompose(task)
        return [route_to_cloud(t, tier='low') for t in sub_tasks]
    else:  # critical
        # 2x decomposition + high tier
        sub_tasks = binary_decompose(task)
        return [route_to_cloud(t, tier='high') for t in sub_tasks]
```

#### 2. Update `master-playbook-prompt.md`
Add new module:
```markdown
## Module 7: Health-Aware Execution

**Load Trigger:** Before any playbook execution

### Pre-Execution Health Check
```python
health = check_orchestrator_health()

if health['status'] == 'critical':
    action = "IMMEDIATE_OFFLOAD"
    target = "cloud_tier_high"
elif health['status'] == 'stressed':
    action = "DECOMPOSE_AND_OFFLOAD"
    target = "cloud_tier_low"
else:
    action = "EXECUTE_LOCALLY"
    target = "local_model"
```

### Binary Decomposition
```python
def binary_decompose(task):
    """Split task into 2 equal sub-tasks"""
    mid = len(task['steps']) // 2
    return [
        {'steps': task['steps'][:mid], 'complexity': task['complexity'] / 2},
        {'steps': task['steps'][mid:], 'complexity': task['complexity'] / 2}
    ]
```

### Node Recovery
```python
def wait_for_node_recovery(node, timeout=60):
    """Wait for node to become healthy again"""
    for _ in range(timeout // 10):
        health = check_node_health(node)
        if health['status'] == 'healthy':
            return True
        time.sleep(10)
    return False  # Timeout exceeded
```

### Tiered Escalation
```yaml
escalation_tiers:
  low: qwen3.5:397b-cloud    # $0.011/1K tokens
  medium: qwen3.5:397b-cloud  # Same, with priority boost
  high: kimi-k2.6             # $0.055/1K tokens
  
escalation_rules:
  - if: "no_local_nodes_available"
    then: "escalate_to_low"
  - if: "low_tier_saturated"
    then: "escalate_to_medium"
  - if: "medium_tier_saturated"
    then: "escalate_to_high"
```
```

#### 3. Update `orchestration-status-monitor.md`
Add sections:
- Health-aware routing decision tree
- Node recovery timeout configuration
- Tiered escalation flow
- Lab node health integration

#### 4. Update Phase Files
**Phase 2 (`phase-2-planning.md`):**
```markdown
### Framework Readiness Check
- [ ] Run `python3 orchestrator_health.py --json`
- [ ] If status != "healthy": Decompose task
- [ ] Route decomposed tasks to cloud models
```

**Phase 3 (`phase-3-execution.md`):**
```markdown
### Pre-Execution Health Check
- [ ] Re-check health every 5 minutes during long tasks
- [ ] If status degraded: Pause and re-route remaining work
- [ ] Log all health transitions
```

---

## Recommended Implementation Priority

| Priority | Gap | Effort | Impact |
|----------|-----|--------|--------|
| 🔴 P0 | Gap 1: Orchestrator → Playbook Integration | 2 hrs | Prevents orchestrator saturation |
| 🔴 P0 | Gap 2: 2x Binary Decomposition | 3 hrs | Core user requirement |
| 🟡 P1 | Gap 3: Node Recovery Timeout | 2 hrs | Enables node reuse |
| 🟡 P1 | Gap 4: Tiered Cloud Escalation | 2 hrs | Complete user requirement |
| 🟡 P1 | Gap 5: Lab Node Health | 3 hrs | Full ecosystem coverage |
| 🟡 P2 | Gap 6: Health-Based Model Selection | 2 hrs | Optimized routing |
| 🟡 P2 | Gap 7: Phase File Integration | 1 hr | Process compliance |
| 🟡 P2 | Gap 8: Memory Reuse Under Stress | 1 hr | Resource optimization |

**Total Estimated Effort:** 16 hours

---

## Test Plan

### Test Case 1: Orchestrator Stress Detection
```bash
# Simulate high memory usage
python3 -c "import psutil; print(psutil.virtual_memory().percent)"

# Run playbook with health check
python3 orchestrator-status.py --health

# Verify routing decision
# Expected: "stressed" → decompose → cloud tier low
```

### Test Case 2: 2x Decomposition
```bash
# Submit complex playbook
# Verify binary split into 2 sub-tasks
# Verify each sub-task routed separately
```

### Test Case 3: Node Recovery
```bash
# Mark node as stressed
# Wait 60 seconds
# Verify node marked healthy again
```

### Test Case 4: Tiered Escalation
```bash
# Block all local nodes
# Verify escalation to low tier
# Block low tier
# Verify escalation to medium tier
# Block medium tier
# Verify escalation to high tier
```

---

## Conclusion

**Current State:** The master prompt monitoring is **playbook-centric** and functional. TI-031 is **orchestrator-centric** and functional. They are **not integrated**.

**Gap Analysis:** 8 gaps identified, 2 critical (P0), 3 high (P1), 3 medium (P2).

**Recommendation:** Implement P0 gaps immediately to prevent orchestrator saturation. P1 gaps complete the user's 2x decomposition + recovery timeout requirements. P2 gaps optimize the overall system.

**Next Action:** Create implementation plan for P0 gaps (Gap 1 + Gap 2).

---

**Related Documents:**
- [TI-031 Protocol](../backlog-completed/TI-031-health-monitoring-protocol.md)
- [Master Playbook Prompt](./master-playbook-prompt.md)
- [Orchestration Status Monitor](./orchestration-status-monitor.md)
- [Low-Capacity Validation](./low-capacity-model-validation.md)
- [Phase 2 Planning](../../phases/phase-2-planning.md)
- [Phase 3 Execution](../../phases/phase-3-execution.md)
