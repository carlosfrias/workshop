# Integrated Health-Aware Playbook Monitoring System (Master Plan)

> **📍 Navigation**  
> **Parent:** [Technical Infrastructure Wiki](../../WIKI.md) | [Technical Infrastructure Docs](./)  
> **Related:** [Master Playbook Prompt](./master-playbook-prompt.md) | [Plan Location Guide](./PLAN-LOCATION-GUIDE.md) | [Orchestration Status](./orchestration-status-monitor.md)  
> **Quick Links:** [Health Monitor Script](/scripts/unified_health_monitor.py) | [Decision Engine](/scripts/unified_decision_engine.py) | [Model Routing Guide](../../../reference/model-routing-guide.md)  
> **Backlog:** [TI-032](/operational/BACKLOG.md#ti-032)

---

**Document ID:** `PLAN-INTEGRATED-HEALTH-MONITORING-v1.0`  
**Created:** 2026-05-05  
**Supersedes:** 
- `PLAN-TI031-INTEGRATION-v1.0.md` (individual TI-031 plan)
- `ASSESSMENT-TI031-MASTER-PROMPT-GAPS.md` (gap analysis)
- `master-playbook-prompt.md` standalone monitoring (now integrated)

**Priority:** 🔴 **CRITICAL**  
**Status:** 📋 **READY FOR REVIEW**  
**Estimated Effort:** 16 hours (P0: 5h, P1: 7h, P2: 4h)

---

## Executive Summary

This **integrated master plan** combines three previously separate work streams into a unified health-aware playbook execution framework:

| Component | Previous Location | Integration Status |
|-----------|-------------------|-------------------|
| **TI-031 Health Protocol** | `wiki/operational/backlog-completed/TI-031-health-monitoring-protocol.md` | ✅ Core health checks integrated |
| **Master Prompt Monitoring** | `technical-infrastructure/wiki/technical-infrastructure/master-playbook-prompt.md` | ✅ Playbook execution integrated |
| **Gap Analysis** | `technical-infrastructure/operational/planning/ASSESSMENT-TI031-MASTER-PROMPT-GAPS.md` | ✅ All 8 gaps addressed |

**What This Plan Provides:**
1. **Single source of truth** for health monitoring across orchestrator + lab nodes + playbooks
2. **Unified decision tree** for routing based on health, complexity, and availability
3. **Consistent escalation path** from local → decomposed → cloud (low → medium → high)
4. **Recovery mechanisms** with configurable timeouts
5. **Comprehensive logging** for post-hoc analysis and optimization

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    UNIFIED HEALTH MONITORING LAYER                  │
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐       │
│  │ Orchestrator    │  │ Lab Nodes       │  │ Playbook        │       │
│  │ (Mac M4 Pro)    │  │ (fnet1-fnet7)   │  │ Execution       │       │
│  │                 │  │                 │  │                 │       │
│  │ RAM%, CPU, Swap │  │ RAM%, CPU,      │  │ Queue depth,    │       │
│  │                 │  │ Ollama status   │  │ Latency, Errors │       │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘       │
│           │                    │                    │                  │
│           └────────────────────┴────────────────────┘                  │
│                            │                                        │
│                            ▼                                        │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │              UNIFIED DECISION ENGINE                       │       │
│  │                                                          │       │
│  │  Input: Health status + Task complexity + Node availability │     │
│  │                                                          │       │
│  │  Decision Tree:                                          │       │
│  │  ├─ HEALTHY + Local nodes available → Execute locally    │       │
│  │  ├─ STRESSED + Local nodes available → 2x decompose    │       │
│  │  ├─ CRITICAL + Local nodes available → 2x decompose +   │       │
│  │  │                                      cloud high tier │       │
│  │  └─ Any status + No local nodes → Escalate cloud tier   │       │
│  │                                                          │       │
│  └────────────────────────┬─────────────────────────────────┘       │
│                           │                                         │
│                           ▼                                         │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │              EXECUTION LAYER                              │       │
│  │                                                          │       │
│  │  ├─ Local Models: gemma4:e4b, qwen3.5:4b, qwen3:8b      │       │
│  │  ├─ Cloud Tier Low: qwen3.5:397b-cloud ($0.011/1K)      │       │
│  │  ├─ Cloud Tier Medium: qwen3.5:397b-cloud (priority)      │       │
│  │  └─ Cloud Tier High: kimi-k2.6 ($0.055/1K)              │       │
│  │                                                          │       │
│  └─────────────────────────────────────────────────────────┘       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Integration Points

### 1. Health Monitoring Integration

**Previously:** Three separate monitoring systems
- TI-031: Orchestrator only
- Master Prompt: Playbook metrics only
- Lab nodes: Not monitored

**Now:** Unified monitoring with shared decision engine

```python
# unified_health_monitor.py
class UnifiedHealthMonitor:
    def __init__(self):
        self.orchestrator_monitor = OrchestratorHealthMonitor()  # TI-031
        self.lab_node_monitor = LabNodeMonitor()                  # NEW
        self.playbook_monitor = PlaybookExecutionMonitor()        # Master Prompt
    
    def check_all_systems(self):
        """Check health of all components and return unified status."""
        return {
            'orchestrator': self.orchestrator_monitor.check(),
            'lab_nodes': self.lab_node_monitor.check_all(),
            'playbook_queue': self.playbook_monitor.check_queue(),
            'overall_status': self.calculate_overall_status()
        }
```

### 2. Decision Engine Integration

**Previously:** Separate routing decisions
- TI-031: Stressed → cloud
- Master Prompt: Queue depth → scale workers
- No coordination between systems

**Now:** Single decision tree with priority ordering

```python
# unified_decision_engine.py
class UnifiedDecisionEngine:
    def route_task(self, task, health_status):
        """
        Make routing decision based on unified health status.
        
        Priority:
        1. Orchestrator health (most critical - user experience)
        2. Lab node availability (cost efficiency)
        3. Playbook queue depth (throughput)
        """
        # Priority 1: Orchestrator health
        if health_status['orchestrator'] == 'critical':
            return self.route_to_cloud_high(task)
        
        if health_status['orchestrator'] == 'stressed':
            return self.decompose_and_route(task, tier='low')
        
        # Priority 2: Lab node availability
        available_nodes = health_status['lab_nodes']['available']
        if not available_nodes:
            return self.route_to_cloud_low(task)
        
        # Priority 3: Queue depth optimization
        if health_status['playbook_queue']['depth'] > 10:
            return self.route_to_least_loaded_node(task, available_nodes)
        
        # Default: Local execution on orchestrator
        return self.route_locally(task)
```

### 3. Recovery Mechanism Integration

**Previously:** No recovery mechanism in TI-031 or Master Prompt

**Now:** Unified recovery with timeout + retry logic

```python
# unified_recovery.py
class UnifiedRecovery:
    def handle_node_stress(self, node_id, timeout=60):
        """
        Handle stressed node with recovery timeout.
        
        Process:
        1. Mark node unavailable
        2. Reroute active tasks
        3. Wait for recovery (check every 10s)
        4. Mark node available when healthy
        """
        self.mark_unavailable(node_id)
        self.reroute_active_tasks(node_id)
        
        # Recovery loop
        for elapsed in range(0, timeout, 10):
            health = self.check_node_health(node_id)
            if self.is_healthy(health):
                self.mark_available(node_id)
                return {'status': 'recovered', 'time': elapsed}
            time.sleep(10)
        
        return {'status': 'timeout', 'time': timeout}
```

---

## Unified Implementation Plan

### Phase 0: Foundation (P0 — Critical, 5 hours)

#### P0.1: Create Unified Health Monitor

**File:** `technical-infrastructure/scripts/unified_health_monitor.py`

**Purpose:** Single entry point for all health checks

```python
#!/usr/bin/env python3
"""
unified_health_monitor.py — Single entry point for orchestrator + lab node health

Usage:
    python3 unified_health_monitor.py --all
    python3 unified_health_monitor.py --orchestrator
    python3 unified_health_monitor.py --lab-nodes
    python3 unified_health_monitor.py --playbook-queue
"""

import json
from datetime import datetime
from typing import Dict, List

class UnifiedHealthMonitor:
    """
    Unified health monitoring for:
    - Orchestrator (Mac M4 Pro)
    - Lab nodes (fnet1-fnet7)
    - Playbook execution queue
    """
    
    def __init__(self):
        self.orchestrator = OrchestratorHealthCheck()  # TI-031
        self.lab_nodes = LabNodeHealthCheck()           # NEW
        self.playbook_queue = PlaybookQueueMonitor()     # Master Prompt
    
    def check_all(self) -> Dict:
        """Run all health checks and return unified status."""
        return {
            'timestamp': datetime.now().isoformat(),
            'orchestrator': self.check_orchestrator(),
            'lab_nodes': self.check_lab_nodes(),
            'playbook_queue': self.check_playbook_queue(),
            'overall_status': self.calculate_overall_status()
        }
    
    def check_orchestrator(self) -> Dict:
        """Check orchestrator health using TI-031 protocol."""
        return self.orchestrator.check()
    
    def check_lab_nodes(self) -> List[Dict]:
        """Check health of all lab nodes."""
        return self.lab_nodes.check_all()
    
    def check_playbook_queue(self) -> Dict:
        """Check playbook execution metrics."""
        return self.playbook_queue.check()
    
    def calculate_overall_status(self) -> str:
        """
        Calculate overall system status.
        
        Rules:
        - CRITICAL if orchestrator is critical
        - STRESSED if orchestrator stressed OR >2 lab nodes offline
        - HEALTHY otherwise
        """
        orch = self.check_orchestrator()
        if orch['status'] == 'critical':
            return 'critical'
        
        nodes = self.check_lab_nodes()
        offline_count = sum(1 for n in nodes if n['status'] == 'offline')
        stressed_count = sum(1 for n in nodes if n['status'] == 'stressed')
        
        if orch['status'] == 'stressed' or offline_count >= 2 or stressed_count >= 3:
            return 'stressed'
        
        return 'healthy'
```

**Acceptance Criteria:**
- [ ] Single command checks all systems
- [ ] Returns unified status (healthy/stressed/critical)
- [ ] Individual component checks available
- [ ] JSON output for programmatic use

#### P0.2: Create Unified Decision Engine

**File:** `technical-infrastructure/scripts/unified_decision_engine.py`

**Purpose:** Single routing decision maker

```python
#!/usr/bin/env python3
"""
unified_decision_engine.py — Health-aware routing decisions

Usage:
    python3 unified_decision_engine.py --task "deploy_app" --complexity 5
"""

class UnifiedDecisionEngine:
    """
    Make routing decisions based on unified health status.
    """
    
    def __init__(self):
        self.health_monitor = UnifiedHealthMonitor()
        self.model_router = ModelRouter()
    
    def route_task(self, task_name: str, complexity: int) -> Dict:
        """
        Make routing decision for a task.
        
        Returns routing decision with:
        - action: execute_locally | decompose_and_route | route_to_cloud
        - target_model: specific model identifier
        - decomposition: none | 2x_binary | 4x_binary
        - cloud_tier: none | low | medium | high
        - estimated_cost: cost in USD
        """
        health = self.health_monitor.check_all()
        
        # Decision tree
        if health['overall_status'] == 'critical':
            return self._critical_routing(task_name, complexity)
        
        if health['overall_status'] == 'stressed':
            return self._stressed_routing(task_name, complexity)
        
        return self._healthy_routing(task_name, complexity)
    
    def _critical_routing(self, task_name, complexity):
        """Critical: Immediate cloud escalation with 2x decomposition."""
        sub_tasks = binary_decompose(task_name, complexity, depth=2)
        return {
            'action': 'decompose_and_route',
            'target_model': 'ollama-cloud/kimi-k2.6',
            'decomposition': '2x_binary',
            'cloud_tier': 'high',
            'estimated_cost': len(sub_tasks) * 0.055 * complexity * 100,
            'rationale': 'Orchestrator critical - immediate cloud offload'
        }
    
    def _stressed_routing(self, task_name, complexity):
        """Stressed: Cloud offloading with 2x decomposition."""
        sub_tasks = binary_decompose(task_name, complexity, depth=1)
        return {
            'action': 'decompose_and_route',
            'target_model': 'ollama-cloud/qwen3.5:397b',
            'decomposition': '2x_binary',
            'cloud_tier': 'low',
            'estimated_cost': len(sub_tasks) * 0.011 * complexity * 100,
            'rationale': 'Orchestrator stressed - cloud offload recommended'
        }
    
    def _healthy_routing(self, task_name, complexity):
        """Healthy: Local execution with node selection."""
        target_node = self.select_best_node()
        target_model = self.model_router.select_local_model(complexity)
        
        return {
            'action': 'execute_locally',
            'target_model': target_model,
            'target_node': target_node,
            'decomposition': 'none',
            'cloud_tier': 'none',
            'estimated_cost': 0,  # Local is "free"
            'rationale': 'Healthy orchestrator - local execution'
        }
```

**Acceptance Criteria:**
- [ ] Single entry point for routing decisions
- [ ] Consistent decision tree across all components
- [ ] Cost estimation included
- [ ] Rationale logging for transparency

#### P0.3: Integrate with Playbook Executor

**File:** `technical-infrastructure/scripts/playbook-executor.py` (UPDATE)

**Purpose:** Use unified decision engine for all playbook executions

```python
def execute_playbook(playbook_name, user_context):
    """
    Execute playbook with unified health monitoring.
    """
    # Step 1: Unified health check
    health = unified_health_monitor.check_all()
    
    # Step 2: Make routing decision
    decision = unified_decision_engine.route_task(playbook_name, complexity)
    
    # Step 3: Log decision
    log_routing_decision(playbook_name, health, decision)
    
    # Step 4: Execute based on decision
    if decision['action'] == 'execute_locally':
        return execute_locally(playbook_name, decision['target_model'])
    
    elif decision['action'] == 'decompose_and_route':
        sub_tasks = binary_decompose(playbook_name, decision['decomposition'])
        results = []
        for sub_task in sub_tasks:
            result = execute_sub_task(sub_task, decision['target_model'])
            results.append(result)
        return synthesize_results(results)
    
    else:  # route_to_cloud
        return execute_cloud(playbook_name, decision['target_model'])
```

**Acceptance Criteria:**
- [ ] All playbook executions use unified decision engine
- [ ] Health check runs before every execution
- [ ] Routing decision logged
- [ ] Test: Simulate stress → verify decomposition triggers

---

### Phase 1: High Priority (P1 — 7 hours)

#### P1.1: Node Recovery Timeout

**File:** `technical-infrastructure/scripts/node_recovery_watcher.py`

**Purpose:** Automatic node recovery with configurable timeout

**Integration Point:** Called by unified health monitor when node goes stressed

```python
class NodeRecoveryWatcher:
    def __init__(self, timeout=60):
        self.timeout = timeout
        self.check_interval = 10
    
    def watch_and_recover(self, node_id):
        """
        Monitor node and mark available after recovery.
        
        Process:
        1. Mark node unavailable
        2. Reroute any queued tasks
        3. Check health every 10 seconds
        4. Mark available when:
           - RAM < 75%
           - CPU load < 3.0
           - No swap usage
           - Timeout not exceeded
        """
        mark_node_unavailable(node_id)
        reroute_queued_tasks(node_id)
        
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            health = check_node_health(node_id)
            
            if (health['ram_pct'] < 75 and 
                health['cpu_load'] < 3.0 and 
                health['swap_used'] == 0):
                
                mark_node_available(node_id)
                log_recovery(node_id, time.time() - start_time)
                return {'status': 'recovered'}
            
            time.sleep(self.check_interval)
        
        log_timeout(node_id, self.timeout)
        return {'status': 'timeout'}
```

#### P1.2: Tiered Cloud Escalation

**File:** `technical-infrastructure/scripts/cloud_escalation.py`

**Purpose:** Progressive escalation (low → medium → high)

**Integration Point:** Called by unified decision engine when no local nodes available

```python
class CloudEscalationManager:
    def __init__(self):
        self.tiers = {
            'low': 'ollama-cloud/qwen3.5:397b',     # $0.011/1K tokens
            'medium': 'ollama-cloud/qwen3.5:397b',   # Same, priority boost
            'high': 'ollama-cloud/kimi-k2.6'         # $0.055/1K tokens
        }
        self.max_attempts_per_tier = 2
    
    def escalate_with_fallback(self, task, start_tier='low'):
        """
        Execute task with automatic escalation on failure.
        
        Flow:
        low → (fail) → medium → (fail) → high → (fail) → ERROR
        """
        current_tier = start_tier
        attempts = 0
        
        while True:
            model = self.tiers[current_tier]
            result = execute_task(task, model)
            
            if result['status'] == 'success':
                return result
            
            attempts += 1
            if attempts >= self.max_attempts_per_tier:
                if current_tier == 'low':
                    current_tier = 'medium'
                    attempts = 0
                elif current_tier == 'medium':
                    current_tier = 'high'
                    attempts = 0
                else:
                    return {'status': 'failed', 'error': 'All tiers exhausted'}
```

#### P1.3: Lab Node Health Monitoring

**File:** `technical-infrastructure/scripts/lab_node_monitor.py`

**Purpose:** SSH-based health checks for fnet1-fnet7

**Integration Point:** Called by unified health monitor

```python
class LabNodeHealthCheck:
    def check_all(self):
        """Check health of all lab nodes via SSH."""
        nodes = ['fnet1', 'fnet2', 'fnet3', 'fnet4', 'fnet5', 'fnet6', 'fnet7']
        return [self.check_node(n) for n in nodes]
    
    def check_node(self, node_id):
        """Check single node health."""
        try:
            # SSH and run health check
            result = ssh_command(node_id, 'python3 -c "import psutil; print(...)"')
            metrics = parse_metrics(result)
            
            # Evaluate status
            if metrics['ram_pct'] > 90 or metrics['swap_used'] > 0:
                status = 'critical'
            elif metrics['ram_pct'] > 75:
                status = 'stressed'
            else:
                status = 'healthy'
            
            return {'node_id': node_id, 'status': status, **metrics}
        
        except SSHException:
            return {'node_id': node_id, 'status': 'offline'}
```

---

### Phase 2: Medium Priority (P2 — 4 hours)

#### P2.1: Health-Based Model Selection

**File:** `technical-infrastructure/reference/model-routing-guide.md` (UPDATE)

**Purpose:** Model selection matrix with health states

| Task Type | Healthy | Stressed | Critical |
|-----------|---------|----------|----------|
| Bookkeeping | gemma4:e4b | qwen3.5:397b-cloud | kimi-k2.6 |
| Position monitoring | qwen3.5:4b | qwen3.5:397b-cloud | kimi-k2.6 |
| Infrastructure | qwen3:8b | qwen3.5:397b-cloud | kimi-k2.6 |
| Playbook execution | Local model | 2x decompose + cloud low | 2x decompose + cloud high |

#### P2.2: Phase File Integration

**Files:** 
- `.pi/agents/phases/phase-2-planning.md` (UPDATE)
- `.pi/agents/phases/phase-3-execution.md` (UPDATE)

**Purpose:** Integrate health checks into standard operating procedures

```markdown
## Phase 2: Planning — Framework Readiness

### Mandatory Health Check
```bash
python3 technical-infrastructure/scripts/unified_health_monitor.py --all
```

**If overall_status != "healthy":**
- Document health status in plan
- Include decomposition strategy if stressed
- Include cloud escalation if critical
```

#### P2.3: Memory Management Under Stress

**File:** `technical-infrastructure/scripts/memory_manager.py`

**Purpose:** Health-aware memory allocation

```python
def allocate_memory(health_status, task_size):
    """
    Allocate memory based on health status.
    
    Under stress:
    - Reduce context window by 50%
    - Clear non-essential caches
    - Use minimal state tracking
    """
    if health_status == 'critical':
        return minimal_allocation(task_size)
    elif health_status == 'stressed':
        return reduced_allocation(task_size)
    else:
        return full_allocation(task_size)
```

---

## Unified File Structure

```
technical-infrastructure/
├── scripts/
│   ├── unified_health_monitor.py        🆕 Single health check entry point
│   ├── unified_decision_engine.py       🆕 Single routing decision maker
│   ├── playbook-executor.py            🔄 Updated with unified integration
│   ├── binary_decompose.py             🆕 2x decomposition logic
│   ├── node_recovery_watcher.py        🆕 Recovery timeout mechanism
│   ├── cloud_escalation.py             🆕 Tiered escalation manager
│   ├── lab_node_monitor.py             🆕 SSH-based node monitoring
│   ├── memory_manager.py               🆕 Health-aware memory allocation
│   ├── health_logger.py                🆕 Unified logging
│   ├── orchestrator_health.py          ✅ TI-031 (existing, integrated)
│   └── orchestrator-status.py          ✅ Master Prompt (existing, integrated)
├── reference/
│   └── model-routing-guide.md          🔄 Updated with health states
├── phases/
│   ├── phase-2-planning.md             🔄 Add health check requirement
│   └── phase-3-execution.md            🔄 Add health monitoring
└── wiki/technical-infrastructure/
    ├── unified-health-monitoring.md    🆕 This document
    ├── master-playbook-prompt.md       🔄 Reference unified system
    ├── orchestration-status-monitor.md 🔄 Reference unified system
    └── low-capacity-model-validation.md 🔄 Reference unified system
```

---

## Decision Tree Summary

```
User Prompt
    ↓
Unified Health Check (orchestrator + lab nodes + queue)
    ↓
Overall Status?
    ├─ CRITICAL ────────────────────────────────────────────────┐
    │    ↓                                                        │
    │  2x Binary Decompose                                        │
    │    ↓                                                        │
    │  Route to Cloud High Tier (kimi-k2.6)                      │
    │    ↓                                                        │
    │  Execute with maximum resource limits                     │
    └─────────────────────────────────────────────────────────────┘
    ├─ STRESSED ──────────────────────────────────────────────────┐
    │    ↓                                                        │
    │  2x Binary Decompose                                        │
    │    ↓                                                        │
    │  Route to Cloud Low Tier (qwen3.5:397b)                    │
    │    ↓                                                        │
    │  Monitor for recovery (60s timeout)                         │
    └─────────────────────────────────────────────────────────────┘
    └─ HEALTHY ───────────────────────────────────────────────────┐
         ↓                                                        │
       Local nodes available?                                     │
         ├─ Yes ───→ Route to best local node (gemma4/qwen)      │
         └─ No ───→ Route to Cloud Low Tier                       │
              ↓                                                   │
         Monitor queue depth                                       │
              ↓                                                   │
         Scale if needed                                          │
    └─────────────────────────────────────────────────────────────┘
```

---

## Unified Metrics & Logging

### Log Format (JSONL)

```json
{
  "timestamp": "2026-05-05T10:30:00Z",
  "event_type": "routing_decision",
  "task": "deploy_app",
  "health_status": {
    "orchestrator": "stressed",
    "lab_nodes": {"healthy": 5, "stressed": 1, "offline": 1},
    "queue_depth": 3
  },
  "decision": {
    "action": "decompose_and_route",
    "decomposition": "2x_binary",
    "cloud_tier": "low",
    "target_model": "ollama-cloud/qwen3.5:397b",
    "estimated_cost": 0.33
  },
  "execution_time_ms": 1500
}
```

### Key Metrics

| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| Orchestrator saturation incidents | 0/week | >0 triggers alert |
| Average routing decision time | <2s | >5s |
| Node recovery success rate | >90% | <80% |
| Cloud escalation frequency | <10% | >20% |
| Cost per task | <$0.50 | >$1.00 |

---

## Superseded Documents

| Document | Status | Reference |
|----------|--------|-----------|
| `PLAN-TI031-INTEGRATION-v1.0.md` | 📦 **SUPERSEDED** | Replaced by this unified plan |
| `ASSESSMENT-TI031-MASTER-PROMPT-GAPS.md` | 📦 **SUPERSEDED** | Gaps addressed in this plan |
| `master-playbook-prompt.md` (standalone) | 🔄 **UPDATED** | Referenced by unified system |
| `TI-031-health-monitoring-protocol.md` | ✅ **INTEGRATED** | Core protocol embedded |

---

## Success Criteria

- [ ] Single command checks all system health (`unified_health_monitor.py --all`)
- [ ] All playbook executions use unified decision engine
- [ ] 2x decomposition triggers automatically on stress
- [ ] Nodes recover automatically after 60s timeout
- [ ] Cloud escalation follows low → medium → high
- [ ] All decisions logged with rationale
- [ ] Phase files updated with health check requirements
- [ ] Test: 100% of executions have health-aware routing

---

## Next Steps

1. **Review this plan** (current step)
2. **Approve and prioritize** implementation phases
3. **Begin Phase 0** (P0: 5 hours, critical foundation)
4. **Continue to Phase 1** (P1: 7 hours, high priority features)
5. **Complete Phase 2** (P2: 4 hours, optimization)

---

**Related Documents:**
- [Superseded: TI-031 Protocol](../backlog-completed/TI-031-health-monitoring-protocol.md)
- [Superseded: Gap Analysis](./ASSESSMENT-TI031-MASTER-PROMPT-GAPS.md)
- [Updated: Master Playbook Prompt](./master-playbook-prompt.md)
- [Updated: Orchestration Status](./orchestration-status-monitor.md)
- [Updated: Low-Capacity Validation](./low-capacity-model-validation.md)

---

**Plan Owner:** Technical Infrastructure Team  
**Created:** 2026-05-05  
**Version:** 1.0  
**Status:** 📋 **PENDING USER REVIEW**
