# ⚠️ SUPERSEDED BY UNIFIED PLAN

**Status:** 📦 **ARCHIVED / SUPERSEDED**  
**Superseded By:** [`unified-health-monitoring.md`](../../wiki/technical-infrastructure/unified-health-monitoring.md)  
**Reason:** Individual TI-031 integration plan has been merged into the Integrated Health-Aware Playbook Monitoring System (Master Plan).

---

**Original Content Below (For Reference):**

*Note: All implementation details from this plan have been incorporated into the unified plan. Please refer to the unified plan for current implementation guidance.*

---

**Document ID:** `PLAN-TI031-INTEGRATION-v1.0`  
**Created:** 2026-05-05  
**Priority:** 🔴 **CRITICAL** — Non-negotiable safety guardrail  
**Status:** 📋 **PENDING USER REVIEW**  
**Estimated Effort:** 16 hours total (P0: 5h, P1: 7h, P2: 4h)

---

## Executive Summary

This plan integrates **TI-031 Orchestrator Health Monitoring Protocol** with the **Master Playbook Prompt System** to create a health-aware execution framework that:

1. **Prevents orchestrator saturation** by checking health before every playbook execution
2. **Implements 2x binary decomposition** when nodes become stressed or memory-saturated
3. **Enables node recovery timeouts** so saturated nodes become available again after 60 seconds
4. **Provides tiered cloud escalation** (low → medium → high) when no local nodes are available
5. **Monitors lab node health** (fnet1-fnet7) in addition to orchestrator health

**Business Impact:** Without this integration, the Mac orchestrator can become saturated during playbook execution, causing 20+ second freezes and degraded user experience. This plan implements the safety guardrails required for production use.

---

## Problem Statement

### Current State

```
┌─────────────────────────────────────────────────────────┐
│  User Prompt                                            │
│       ↓                                                  │
│  Keyword Router (no health check)                       │
│       ↓                                                  │
│  Playbook Executor (no health awareness)                │
│       ↓                                                  │
│  Local Model (gemma4:e4b, qwen3.5:4b, qwen3:8b)         │
│       ↓                                                  │
│  ⚠️ Orchestrator can saturate → 20+ second freezes     │
└─────────────────────────────────────────────────────────┘
```

**TI-031 exists but is NOT connected to playbook execution flow.**

### Required State

```
┌─────────────────────────────────────────────────────────┐
│  User Prompt                                            │
│       ↓                                                  │
│  ┌──────────────────────────────────────────┐           │
│  │ Health Check (TI-031)                    │           │
│  │ - RAM% (threshold: 80% / 92%)            │           │
│  │ - CPU load (threshold: 4.0 / 6.0)        │           │
│  │ - Swap used (threshold: >0 = critical)   │           │
│  └──────────────────────────────────────────┘           │
│       ↓                                                  │
│  ┌──────────────────────────────────────────┐           │
│  │ Health Status Decision                   │           │
│  │ - HEALTHY → Local execution              │           │
│  │ - STRESSED → 2x decompose + cloud low    │           │
│  │ - CRITICAL → 2x decompose + cloud high   │           │
│  └──────────────────────────────────────────┘           │
│       ↓                                                  │
│  ┌──────────────────────────────────────────┐           │
│  │ Node Availability Check                  │           │
│  │ - Local nodes available? → Route         │           │
│  │ - No nodes? → Escalate tier (low→high)   │           │
│  │ - Timeout reached? → Mark available      │           │
│  └──────────────────────────────────────────┘           │
│       ↓                                                  │
│  Execution with health-aware routing                    │
└─────────────────────────────────────────────────────────┘
```

---

## Gap Analysis Summary

| Gap # | Description | Severity | Effort | Priority |
|-------|-------------|----------|--------|----------|
| 1 | Orchestrator health → playbook routing integration | 🔴 Critical | 2h | P0 |
| 2 | 2x binary decomposition for stressed nodes | 🔴 Critical | 3h | P0 |
| 3 | Node recovery timeout (60s) | 🟡 High | 2h | P1 |
| 4 | Tiered cloud escalation (low→medium→high) | 🟡 High | 2h | P1 |
| 5 | Lab node health monitoring (fnet1-fnet7) | 🟡 High | 3h | P1 |
| 6 | Health-based model selection | 🟡 Medium | 2h | P2 |
| 7 | Phase file integration | 🟡 Medium | 1h | P2 |
| 8 | Memory-reuse under stress | 🟡 Medium | 1h | P2 |

**Total:** 16 hours (P0: 5h, P1: 7h, P2: 4h)

---

## Phase 0: Foundation (P0 — Critical)

### Gap 1: Orchestrator Health → Playbook Routing Integration

**Problem:** Playbook execution does not check orchestrator health before running.

**Solution:** Add health check as pre-flight requirement for all playbook executions.

#### Implementation Steps

**Step 1.1:** Update `orchestrator-status.py` to include TI-031 health check

```python
# File: technical-infrastructure/scripts/orchestrator-status.py

def check_orchestrator_health():
    """
    Call TI-031 health check script and return parsed result.
    Returns: dict with status, ram_pct, cpu_load, swap_used
    """
    import subprocess
    import json
    
    result = subprocess.run(
        ['python3', 'technical-infrastructure/scripts/orchestrator_health.py', '--json'],
        capture_output=True,
        text=True,
        cwd='/Users/friasc/Dropbox/workshop'
    )
    
    if result.returncode != 0:
        return {
            'status': 'unknown',
            'error': 'Health check failed',
            'ram_pct': 0,
            'cpu_load': 0,
            'swap_used': 0
        }
    
    return json.loads(result.stdout)


def make_routing_decision(health_status, task_complexity):
    """
    Make routing decision based on health status and task complexity.
    
    Returns: dict with action, target_model, decomposition_required
    """
    if health_status['status'] == 'healthy':
        return {
            'action': 'execute_locally',
            'target_model': select_local_model(task_complexity),
            'decomposition_required': False
        }
    
    elif health_status['status'] == 'stressed':
        return {
            'action': 'decompose_and_offload',
            'target_model': 'ollama/qwen3.5:397b',
            'decomposition_required': True,
            'decomposition_type': '2x_binary',
            'cloud_tier': 'low'
        }
    
    else:  # critical
        return {
            'action': 'decompose_and_offload',
            'target_model': 'ollama/kimi-k2.6',
            'decomposition_required': True,
            'decomposition_type': '2x_binary',
            'cloud_tier': 'high'
        }
```

**Step 1.2:** Update playbook execution flow

```python
# File: technical-infrastructure/scripts/playbook-executor.py

def execute_playbook(playbook_name, user_context):
    """
    Execute playbook with health-aware routing.
    """
    # Step 1: Health check (TI-031)
    health = check_orchestrator_health()
    
    # Step 2: Log health status
    log_health_decision(health, playbook_name)
    
    # Step 3: Make routing decision
    routing = make_routing_decision(health, playbook_name)
    
    # Step 4: Execute based on routing decision
    if routing['decomposition_required']:
        # 2x binary decomposition
        sub_tasks = binary_decompose(playbook_name, user_context)
        results = []
        for sub_task in sub_tasks:
            result = execute_sub_task(sub_task, routing['target_model'])
            results.append(result)
        return synthesize_results(results)
    else:
        # Direct local execution
        return execute_local(playbook_name, user_context, routing['target_model'])
```

**Step 1.3:** Add health decision logging

```python
# File: technical-infrastructure/scripts/health-logger.py

def log_health_decision(health, playbook_name, routing=None):
    """
    Log health check decision to health-decisions.jsonl
    """
    from datetime import datetime
    import json
    from pathlib import Path
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'playbook': playbook_name,
        'health_status': health['status'],
        'ram_pct': health.get('ram_pct', 0),
        'cpu_load': health.get('cpu_load', 0),
        'swap_used_gb': health.get('swap_used', 0) / 1_000_000_000,
        'routing_action': routing['action'] if routing else 'none',
        'target_model': routing.get('target_model', 'none'),
        'decomposition_required': routing.get('decomposition_required', False)
    }
    
    log_file = Path('/Users/friasc/Dropbox/workshop/wiki/operational/sessions/health-decisions.jsonl')
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
```

**Acceptance Criteria:**
- [ ] `orchestrator-status.py` includes `check_orchestrator_health()` function
- [ ] Health check runs before every playbook execution
- [ ] Routing decision logged to `health-decisions.jsonl`
- [ ] Stressed/critical status triggers decomposition
- [ ] Test: Simulate high memory → verify decomposition triggers

---

### Gap 2: 2x Binary Decomposition for Stressed Nodes

**Problem:** When nodes become stressed, tasks should split into 2 equal sub-tasks and route independently. Current decomposition is not binary.

**Solution:** Implement binary decomposition with recursive routing.

#### Implementation Steps

**Step 2.1:** Create binary decomposition module

```python
# File: technical-infrastructure/scripts/binary_decompose.py

#!/usr/bin/env python3
"""
binary_decompose.py — Split tasks into 2 equal sub-tasks for stressed nodes

Usage:
    python3 binary_decompose.py --task "deploy_app" --complexity 8
"""

import argparse
import json
from typing import List, Dict

def binary_decompose(task: Dict, max_depth: int = 3, current_depth: int = 0) -> List[Dict]:
    """
    Recursively decompose task into 2 sub-tasks until fit threshold met.
    
    Args:
        task: Task dict with 'steps', 'complexity', 'estimated_tokens'
        max_depth: Maximum recursion depth (default: 3)
        current_depth: Current recursion level
    
    Returns:
        List of sub-task dicts
    """
    # Base case: task is small enough or max depth reached
    if task['complexity'] <= 4 or current_depth >= max_depth:
        return [task]
    
    # Split steps in half
    mid = len(task['steps']) // 2
    
    if mid == 0:
        # Can't split further
        return [task]
    
    # Create 2 sub-tasks
    sub_task_1 = {
        'steps': task['steps'][:mid],
        'complexity': task['complexity'] / 2,
        'estimated_tokens': task['estimated_tokens'] / 2,
        'parent_task_id': task.get('task_id'),
        'sub_task_index': 1,
        'description': f"{task.get('description', 'Task')} (part 1/2)"
    }
    
    sub_task_2 = {
        'steps': task['steps'][mid:],
        'complexity': task['complexity'] / 2,
        'estimated_tokens': task['estimated_tokens'] / 2,
        'parent_task_id': task.get('task_id'),
        'sub_task_index': 2,
        'description': f"{task.get('description', 'Task')} (part 2/2)"
    }
    
    # Recursively decompose if still too large
    result = []
    result.extend(binary_decompose(sub_task_1, max_depth, current_depth + 1))
    result.extend(binary_decompose(sub_task_2, max_depth, current_depth + 1))
    
    return result


def synthesize_results(sub_task_results: List[Dict]) -> Dict:
    """
    Combine results from sub-tasks into single result.
    """
    return {
        'status': 'complete',
        'sub_task_count': len(sub_task_results),
        'results': sub_task_results,
        'synthesis': 'All sub-tasks completed successfully'
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Binary task decomposition')
    parser.add_argument('--task', type=str, required=True, help='Task name')
    parser.add_argument('--complexity', type=int, default=5, help='Task complexity (1-10)')
    parser.add_argument('--max-depth', type=int, default=3, help='Max recursion depth')
    
    args = parser.parse_args()
    
    task = {
        'task_id': f'task_{args.task}',
        'steps': ['step1', 'step2', 'step3', 'step4', 'step5', 'step6'],
        'complexity': args.complexity,
        'estimated_tokens': args.complexity * 100,
        'description': args.task
    }
    
    sub_tasks = binary_decompose(task, args.max_depth)
    
    print(f"Original task: {task['description']} (complexity: {task['complexity']})")
    print(f"Decomposed into {len(sub_tasks)} sub-tasks:")
    for i, st in enumerate(sub_tasks):
        print(f"  {i+1}. {st['description']} (complexity: {st['complexity']:.1f})")
```

**Step 2.2:** Integrate binary decomposition into playbook executor

```python
# File: technical-infrastructure/scripts/playbook-executor.py

from binary_decompose import binary_decompose, synthesize_results

def execute_with_decomposition(playbook_name, user_context, cloud_tier):
    """
    Execute playbook with 2x binary decomposition.
    """
    # Create task representation
    task = {
        'task_id': f'playbook_{playbook_name}',
        'steps': get_playbook_steps(playbook_name),
        'complexity': estimate_complexity(playbook_name),
        'estimated_tokens': estimate_tokens(playbook_name),
        'description': playbook_name
    }
    
    # Binary decompose
    sub_tasks = binary_decompose(task, max_depth=3)
    
    # Route each sub-task
    results = []
    for sub_task in sub_tasks:
        target_model = select_model_for_tier(cloud_tier)
        result = execute_sub_task(sub_task, target_model)
        results.append(result)
    
    # Synthesize results
    return synthesize_results(results)
```

**Acceptance Criteria:**
- [ ] `binary_decompose.py` created and tested
- [ ] Tasks split into 2 equal sub-tasks when stressed
- [ ] Recursive decomposition if sub-tasks still too large
- [ ] Results synthesized back into single response
- [ ] Test: High complexity task → verify binary split

---

## Phase 1: High Priority (P1)

### Gap 3: Node Recovery Timeout (60 seconds)

**Problem:** Saturated nodes stay unavailable indefinitely. Need automatic recovery after timeout.

**Solution:** Implement node recovery watcher with 60-second timeout.

#### Implementation

```python
# File: technical-infrastructure/scripts/node-recovery-watcher.py

#!/usr/bin/env python3
"""
node-recovery-watcher.py — Monitor stressed nodes and mark available after recovery

Usage:
    python3 node-recovery-watcher.py --node fnet3 --timeout 60
"""

import argparse
import time
from datetime import datetime
from typing import Dict

class NodeRecoveryWatcher:
    def __init__(self, node_id: str, timeout: int = 60):
        self.node_id = node_id
        self.timeout = timeout
        self.marked_unavailable_at = None
        self.check_interval = 10  # Check every 10 seconds
    
    def mark_unavailable(self, reason: str):
        """Mark node as unavailable due to stress/saturation"""
        self.marked_unavailable_at = datetime.now()
        log_event(self.node_id, 'unavailable', reason)
    
    def wait_for_recovery(self) -> bool:
        """
        Wait for node to recover. Returns True if recovered, False if timeout.
        """
        start_time = time.time()
        
        while time.time() - start_time < self.timeout:
            health = check_node_health(self.node_id)
            
            if health['status'] == 'healthy':
                # Check thresholds
                if (health['ram_pct'] < 75 and 
                    health['cpu_load'] < 3.0 and 
                    health['swap_used'] == 0):
                    
                    log_event(self.node_id, 'recovered', f'Recovered after {int(time.time() - start_time)}s')
                    self.mark_available()
                    return True
            
            time.sleep(self.check_interval)
        
        # Timeout exceeded
        log_event(self.node_id, 'timeout', f'No recovery after {self.timeout}s')
        return False
    
    def mark_available(self):
        """Mark node as available for task routing"""
        update_node_status(self.node_id, 'available')


def check_node_health(node_id: str) -> Dict:
    """
    Check health of lab node via SSH.
    Returns: dict with status, ram_pct, cpu_load, swap_used
    """
    import subprocess
    
    # SSH to node and run health check
    cmd = f"ssh {node_id} 'python3 -c \"import psutil; m=psutil.virtual_memory(); s=psutil.swap_memory(); print(m.percent, s.used)\"'"
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        ram_pct, swap_used = map(float, result.stdout.strip().split())
        
        if ram_pct > 90 or swap_used > 0:
            status = 'critical'
        elif ram_pct > 75:
            status = 'stressed'
        else:
            status = 'healthy'
        
        return {
            'status': status,
            'ram_pct': ram_pct,
            'cpu_load': 0,  # Would need additional SSH call
            'swap_used': swap_used
        }
    except Exception as e:
        return {'status': 'offline', 'error': str(e)}
```

**Acceptance Criteria:**
- [ ] `node-recovery-watcher.py` created
- [ ] Nodes marked unavailable when stressed
- [ ] Recovery check every 10 seconds
- [ ] Node marked available after 60s timeout or when healthy
- [ ] Test: Simulate stress → verify recovery after timeout

---

### Gap 4: Tiered Cloud Escalation (Low → Medium → High)

**Problem:** Current escalation goes directly to high tier. Need progressive escalation.

**Solution:** Implement 3-tier escalation with fallback logic.

#### Implementation

```python
# File: technical-infrastructure/scripts/cloud-escalation.py

#!/usr/bin/env python3
"""
cloud-escalation.py — Progressive cloud tier escalation

Usage:
    python3 cloud-escalation.py --task "complex_task" --start-tier low
"""

from enum import Enum
from typing import Optional, Dict

class CloudTier(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

TIER_MODELS = {
    CloudTier.LOW: "ollama/qwen3.5:397b",      # $0.011/1K tokens
    CloudTier.MEDIUM: "ollama/qwen3.5:397b",   # Same model, priority boost
    CloudTier.HIGH: "ollama/kimi-k2.6"         # $0.055/1K tokens
}

TIER_COSTS = {
    CloudTier.LOW: 0.011,
    CloudTier.MEDIUM: 0.011,
    CloudTier.HIGH: 0.055
}

class CloudEscalator:
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.current_tier = CloudTier.LOW
        self.attempt_count = 0
        self.max_attempts_per_tier = 2
    
    def get_target_model(self) -> str:
        """Get model for current tier"""
        return TIER_MODELS[self.current_tier]
    
    def escalate(self, reason: str) -> bool:
        """
        Escalate to next tier. Returns False if already at highest tier.
        """
        self.attempt_count += 1
        
        if self.attempt_count >= self.max_attempts_per_tier:
            # Move to next tier
            if self.current_tier == CloudTier.LOW:
                self.current_tier = CloudTier.MEDIUM
                self.attempt_count = 0
                log_escalation(self.task_id, 'low→medium', reason)
                return True
            elif self.current_tier == CloudTier.MEDIUM:
                self.current_tier = CloudTier.HIGH
                self.attempt_count = 0
                log_escalation(self.task_id, 'medium→high', reason)
                return True
            else:
                # Already at highest tier
                log_escalation(self.task_id, 'max_tier_reached', reason)
                return False
        
        return True  # Can retry at current tier
    
    def execute_with_escalation(self, task: Dict) -> Dict:
        """
        Execute task with automatic escalation on failure.
        """
        while True:
            model = self.get_target_model()
            
            try:
                result = execute_task(task, model)
                
                if result['status'] == 'success':
                    log_execution(self.task_id, model, 'success')
                    return result
                else:
                    # Execution failed
                    if not self.escalate(f"Execution failed: {result.get('error')}"):
                        return {'status': 'failed', 'error': 'All tiers exhausted'}
            
            except Exception as e:
                if not self.escalate(f"Exception: {str(e)}"):
                    return {'status': 'failed', 'error': f'All tiers exhausted: {str(e)}'}
```

**Acceptance Criteria:**
- [ ] `cloud-escalation.py` created with 3-tier logic
- [ ] Escalation from low → medium → high on failure
- [ ] Max 2 attempts per tier before escalation
- [ ] Cost logging for each tier
- [ ] Test: Simulate low tier failure → verify escalation to medium

---

### Gap 5: Lab Node Health Monitoring (fnet1-fnet7)

**Problem:** TI-031 only monitors orchestrator. Lab nodes not monitored.

**Solution:** Extend health monitoring to all lab nodes via SSH.

#### Implementation

```python
# File: technical-infrastructure/scripts/lab-node-monitor.py

#!/usr/bin/env python3
"""
lab-node-monitor.py — Health monitoring for fnet1-fnet7 lab nodes

Usage:
    python3 lab-node-monitor.py --all
    python3 lab-node-monitor.py --node fnet3
"""

import argparse
import subprocess
import json
from typing import Dict, List
from datetime import datetime

LAB_NODES = ['fnet1', 'fnet2', 'fnet3', 'fnet4', 'fnet5', 'fnet6', 'fnet7']

def check_node_health(node_id: str) -> Dict:
    """
    Check health of single lab node via SSH.
    """
    health_check_script = '''
import psutil, json
mem = psutil.virtual_memory()
swap = psutil.swap_memory()
cpu = psutil.cpu_percent(interval=1)
print(json.dumps({
    "ram_pct": mem.percent,
    "ram_available_gb": mem.available / 1_000_000_000,
    "cpu_percent": cpu,
    "swap_used_gb": swap.used / 1_000_000_000
}))
'''
    
    try:
        # SSH to node and run health check
        cmd = f"ssh {node_id} 'python3 -c \"{health_check_script}\"'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            return {
                'node_id': node_id,
                'status': 'offline',
                'error': result.stderr
            }
        
        metrics = json.loads(result.stdout)
        
        # Evaluate thresholds
        if metrics['ram_pct'] > 90 or metrics['swap_used_gb'] > 0:
            status = 'critical'
        elif metrics['ram_pct'] > 75 or metrics['cpu_percent'] > 70:
            status = 'stressed'
        else:
            status = 'healthy'
        
        return {
            'node_id': node_id,
            'status': status,
            **metrics
        }
    
    except Exception as e:
        return {
            'node_id': node_id,
            'status': 'error',
            'error': str(e)
        }


def check_all_nodes() -> List[Dict]:
    """Check health of all lab nodes"""
    results = []
    for node in LAB_NODES:
        health = check_node_health(node)
        results.append(health)
    return results


def get_available_nodes(complexity: int) -> List[str]:
    """Get list of nodes available for task with given complexity"""
    all_health = check_all_nodes()
    available = []
    
    for health in all_health:
        if health['status'] == 'healthy':
            # High complexity tasks need more resources
            if complexity > 7 and health['ram_available_gb'] < 4:
                continue
            available.append(health['node_id'])
    
    return available


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Lab node health monitor')
    parser.add_argument('--all', action='store_true', help='Check all nodes')
    parser.add_argument('--node', type=str, help='Check specific node')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    parser.add_argument('--available-for', type=int, help='Get nodes available for complexity level')
    
    args = parser.parse_args()
    
    if args.all:
        results = check_all_nodes()
    elif args.node:
        results = [check_node_health(args.node)]
    else:
        parser.print_help()
        exit(1)
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"{'Node':<10} {'Status':<10} {'RAM%':<8} {'CPU%':<8} {'Available':<10}")
        print("-" * 54)
        for r in results:
            if r['status'] == 'healthy':
                print(f"{r['node_id']:<10} {r['status']:<10} {r['ram_pct']:.1f}%    {r.get('cpu_percent', 'N/A'):<8} {r['ram_available_gb']:.1f}GB")
            else:
                print(f"{r['node_id']:<10} {r['status']:<10} {'N/A':<8} {'N/A':<8} {'N/A':<10}")
    
    if args.available_for:
        available = get_available_nodes(args.available_for)
        print(f"\nAvailable nodes for complexity {args.available_for}: {', '.join(available)}")
```

**Acceptance Criteria:**
- [ ] `lab-node-monitor.py` created
- [ ] SSH health checks for all 7 lab nodes
- [ ] Status: healthy / stressed / critical / offline
- [ ] Available nodes list based on task complexity
- [ ] Test: Check all nodes → verify status reported

---

## Phase 2: Medium Priority (P2)

### Gap 6: Health-Based Model Selection

**Implementation:** Update model routing guide to include health states

```yaml
# File: technical-infrastructure/reference/model-routing-guide.md

Model Routing with Health Awareness:

| Task Type | Healthy | Stressed | Critical |
|-----------|---------|----------|----------|
| Bookkeeping | gemma4:e4b | qwen3.5:397b-cloud | kimi-k2.6 |
| Position monitoring | qwen3.5:4b | qwen3.5:397b-cloud | kimi-k2.6 |
| Infrastructure | qwen3:8b | qwen3.5:397b-cloud | kimi-k2.6 |
| Playbook execution | Local model | Decompose + cloud low | Decompose + cloud high |
```

---

### Gap 7: Phase File Integration

**Implementation:** Update phase-2-planning.md and phase-3-execution.md

```markdown
# Phase 2: Planning — Framework Readiness Check

## Mandatory Health Check

Before any planning begins:

```bash
python3 technical-infrastructure/scripts/orchestrator_health.py --json
```

**If status != "healthy":**
- Decompose task automatically
- Route to cloud model based on stress level
- Log decision to health-decisions.jsonl

---

# Phase 3: Execution — Pre-Execution Health Check

## Health Monitoring During Execution

- Re-check health every 5 minutes during long tasks
- If status degraded: pause and re-route remaining work
- Log all health transitions
```

---

### Gap 8: Memory-Reuse Under Stress

**Implementation:** Make memory-reuse pattern health-aware

```python
# File: technical-infrastructure/scripts/memory-manager.py

def allocate_persistent_state(health_status, playbook):
    """
    Allocate persistent state based on health status.
    Minimal state under stress to conserve memory.
    """
    if health_status['status'] == 'critical':
        # Minimal state only
        return {
            'execution_id': generate_id(),
            'timestamp': datetime.now().isoformat()
        }
    elif health_status['status'] == 'stressed':
        # Reduced state
        return {
            'execution_id': generate_id(),
            'trigger_keyword': playbook['trigger'],
            'timestamp': datetime.now().isoformat()
        }
    else:
        # Full state
        return {
            'execution_id': generate_id(),
            'trigger_keyword': playbook['trigger'],
            'start_time': datetime.now().isoformat(),
            'user_context': playbook.get('user_context'),
            'playbook_metadata': playbook.get('metadata')
        }
```

---

## Testing Plan

### Test Case 1: Orchestrator Stress Detection
```bash
# Simulate high memory usage
python3 -c "data = ['x' * 1000000 for _ in range(5000)]"

# Run health check
python3 technical-infrastructure/scripts/orchestrator_health.py --json

# Expected: status = "stressed" or "critical"
```

### Test Case 2: 2x Binary Decomposition
```bash
# Submit complex playbook
python3 technical-infrastructure/scripts/binary_decompose.py \
  --task "deploy_complex_app" \
  --complexity 9 \
  --max-depth 3

# Expected: 4-8 sub-tasks (2^3 max depth)
```

### Test Case 3: Node Recovery Timeout
```bash
# Mark node as stressed
python3 technical-infrastructure/scripts/node-recovery-watcher.py \
  --node fnet3 \
  --timeout 60

# Wait 60 seconds
# Expected: node marked available
```

### Test Case 4: Tiered Escalation
```bash
# Submit task that fails on low tier
python3 technical-infrastructure/scripts/cloud-escalation.py \
  --task "test_escalation" \
  --start-tier low

# Expected: escalation to medium, then high if needed
```

---

## File Structure

```
technical-infrastructure/
├── scripts/
│   ├── orchestrator_health.py          # ✅ TI-031 (existing)
│   ├── orchestrator-status.py          # 🔄 Update with health integration
│   ├── playbook-executor.py            # 🆕 Create
│   ├── binary_decompose.py             # 🆕 Create
│   ├── health-logger.py                # 🆕 Create
│   ├── node-recovery-watcher.py        # 🆕 Create
│   ├── cloud-escalation.py             # 🆕 Create
│   └── lab-node-monitor.py             # 🆕 Create
├── reference/
│   └── model-routing-guide.md          # 🔄 Update with health states
├── phases/
│   ├── phase-2-planning.md             # 🔄 Add health check requirement
│   └── phase-3-execution.md            # 🔄 Add health monitoring
└── wiki/technical-infrastructure/
    ├── master-playbook-prompt.md       # 🔄 Add health-aware module
    └── orchestration-status-monitor.md # 🔄 Add node health section
```

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| SSH failures to lab nodes | Medium | High | Fallback to cloud models |
| Decomposition overhead | Low | Medium | Cache decomposition results |
| Cloud cost increase | Medium | Low | Cost tracking + alerts |
| Recovery timeout too short | Low | Medium | Configurable timeout (60-120s) |
| False positive stress detection | Low | Medium | Hysteresis in thresholds |

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Orchestrator saturation incidents | 0 per week | health-decisions.jsonl |
| Average playbook execution time | <30s | Performance logs |
| Node recovery success rate | >90% | node-recovery-watcher logs |
| Cloud escalation frequency | <10% of tasks | cloud-escalation logs |
| Lab node availability | >95% | lab-node-monitor logs |

---

## Approval & Sign-Off

| Role | Name | Date | Status |
|------|------|------|--------|
| **Plan Author** | AI Trading Desk | 2026-05-05 | ✅ Complete |
| **Technical Review** | Pending | — | 📋 Awaiting |
| **User Approval** | Carlos | — | 📋 **PENDING REVIEW** |

---

## Related Documents

- [TI-031 Protocol](../backlog-completed/TI-031-health-monitoring-protocol.md)
- [Gap Analysis](./ASSESSMENT-TI031-MASTER-PROMPT-GAPS.md)
- [Master Playbook Prompt](./technical-infrastructure/master-playbook-prompt.md)
- [Orchestration Status Monitor](./technical-infrastructure/orchestration-status-monitor.md)
- [Low-Capacity Validation](./technical-infrastructure/low-capacity-model-validation.md)
- [Phase 2 Planning](../../phases/phase-2-planning.md)
- [Phase 3 Execution](../../phases/phase-3-execution.md)

---

**Next Action:** User review and approval. Upon approval, implementation begins with P0 gaps (5 hours).
