#!/usr/bin/env python3
"""
Escalation Loop Simulation — Phase 2
Uses a REAL decomposition plan from the decomposer subagent.
Simulates tiered execution with forced saturation to test escalation policy.
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path

# --- Inputs ---
# Real plan from decomposer subagent (2026-05-12)
PLAN = [
    {"id": 1, "action": "Check disk usage on all 7 lab nodes (fnet1-fnet7) by executing 'df -h' on each node and collecting output", "node": "bash", "complexity": "LOW"},
    {"id": 2, "action": "Parse disk usage results and identify which nodes have usage > 80%", "node": "local_model", "complexity": "MEDIUM"},
    {"id": 3, "action": "Generate markdown report with high-usage node details and cleanup recommendations", "node": "local_model", "complexity": "MEDIUM"}
]

# --- Configuration ---
LOG_FILE = Path("/Users/friasc/Cloud/ai-trading-workspace/technical-infrastructure/wiki/operational/sessions/escalation-simulation.jsonl")

TIERS = {
    "local_low":    {"model": "qwen3.5:4b",      "capacity": ["LOW"],         "latency_ms": 2000},
    "local_medium": {"model": "qwen3.5:4b",      "capacity": ["LOW", "MEDIUM"], "latency_ms": 6000},
    "local_high":   {"model": "gemma4:e4b",      "capacity": ["LOW", "MEDIUM", "HIGH"], "latency_ms": 15000},
    "cloud_low":    {"model": "qwen3.5:397b-cloud", "capacity": ["LOW", "MEDIUM", "HIGH"], "latency_ms": 8000},
    "cloud_medium": {"model": "qwen3.5:397b-cloud", "capacity": ["LOW", "MEDIUM", "HIGH"], "latency_ms": 12000},
    "cloud_high":   {"model": "kimi-k2.6",       "capacity": ["LOW", "MEDIUM", "HIGH"], "latency_ms": 25000},
}

TIER_ORDER = ["local_low", "local_medium", "local_high", "cloud_low", "cloud_medium", "cloud_high"]

# Stress test: MEDIUM/HIGH tasks saturate on tiers that don't list them in capacity
FORCE_SATURATION = True

def log_event(event_type, data):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event_type,
        **data
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"  [LOG] {event_type}: {json.dumps(data)}")

def simulate_execution(task, tier):
    """Simulate a task running on a specific model tier."""
    info = TIERS[tier]
    complexity = task.get("complexity", "MEDIUM")
    
    # Simulate latency
    time.sleep(min(info["latency_ms"] / 1000.0, 0.05))
    
    # Saturation logic
    if FORCE_SATURATION and complexity not in info["capacity"]:
        return {"status": "SATURATED", "reason": f"{complexity} task exceeds {tier} capacity {info['capacity']}"}
    
    return {
        "status": "SUCCESS",
        "output": f"Task {task['id']} completed on {tier} ({info['model']})",
        "latency_ms": info["latency_ms"]
    }

def split_task(task):
    """2x decomposition: split a task into 2 simpler sub-tasks."""
    return [
        {"id": f"{task['id']}-a", "action": f"First half of: {task['action']}", "complexity": "LOW"},
        {"id": f"{task['id']}-b", "action": f"Second half of: {task['action']}", "complexity": "LOW"},
    ]

def execute_task(task, tier="local_low", generation=0):
    """
    Execute a task with the user's tiered escalation policy.
    generation=0: original task (can be decomposed once)
    generation>0: already-decomposed sub-task (escalate only)
    """
    indent = "  " * generation
    print(f"{indent}▶ Task {task['id']} | tier={tier} | gen={generation} | complexity={task.get('complexity', 'MEDIUM')}")
    
    result = simulate_execution(task, tier)
    print(f"{indent}  Result: {result['status']}")
    
    log_event("execution_attempt", {
        "task_id": task["id"],
        "tier": tier,
        "model": TIERS[tier]["model"],
        "complexity": task.get("complexity"),
        "result": result["status"],
        "generation": generation
    })
    
    if result["status"] == "SUCCESS":
        return result
    
    # --- SATURATED ---
    if generation == 0:
        # Policy Step 1: 2x decomposition, retry on SAME tier
        print(f"{indent}  ⚠️ SATURATED → 2x decomposition → retry on {tier}")
        log_event("saturation_detected", {"task_id": task["id"], "tier": tier, "action": "2x_decompose"})
        
        sub_tasks = split_task(task)
        print(f"{indent}  Split into {len(sub_tasks)} sub-tasks")
        log_event("decomposition", {"task_id": task["id"], "sub_task_count": len(sub_tasks), "tier": tier})
        
        sub_results = []
        for sub in sub_tasks:
            sub_result = execute_task(sub, tier, generation + 1)
            
            if sub_result["status"] == "SATURATED":
                # Policy Step 2: still saturated → escalate to NEXT tier
                current_idx = TIER_ORDER.index(tier)
                if current_idx < len(TIER_ORDER) - 1:
                    next_tier = TIER_ORDER[current_idx + 1]
                    print(f"{indent}  ⬆️ ESCALATE '{sub['id']}' {tier} → {next_tier}")
                    log_event("escalation", {"task_id": sub["id"], "from_tier": tier, "to_tier": next_tier, "generation": generation + 1})
                    sub_result = execute_task(sub, next_tier, generation + 1)
                else:
                    print(f"{indent}  ❌ NO HIGHER TIER for '{sub['id']}'")
                    log_event("escalation_failed", {"task_id": sub["id"], "tier": tier, "generation": generation + 1})
            
            sub_results.append(sub_result)
        
        if all(r["status"] == "SUCCESS" for r in sub_results):
            return {"status": "SUCCESS", "sub_results": sub_results}
        else:
            return {"status": "FAILED", "reason": "Sub-task escalation exhausted"}
    
    else:
        # Already decomposed: escalate immediately (no further decomposition)
        current_idx = TIER_ORDER.index(tier)
        if current_idx < len(TIER_ORDER) - 1:
            next_tier = TIER_ORDER[current_idx + 1]
            print(f"{indent}  ⬆️ ESCALATE '{task['id']}' {tier} → {next_tier}")
            log_event("escalation", {"task_id": task["id"], "from_tier": tier, "to_tier": next_tier, "generation": generation})
            return execute_task(task, next_tier, generation)
        else:
            print(f"{indent}  ❌ NO HIGHER TIER for '{task['id']}'")
            log_event("escalation_failed", {"task_id": task["id"], "tier": tier, "generation": generation})
            return {"status": "FAILED", "reason": "Escalation exhausted"}

def run_simulation():
    print("╔════════════════════════════════════════════════════════╗")
    print("║   ESCALATION LOOP SIMULATION — LIVE DECOMP PLAN      ║")
    print("╚════════════════════════════════════════════════════════╝")
    print(f"\nLog: {LOG_FILE}\n")
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    start = time.time()
    results = []
    
    for task in PLAN:
        result = execute_task(task, tier="local_low", generation=0)
        results.append(result)
    
    duration = time.time() - start
    success = sum(1 for r in results if r["status"] == "SUCCESS")
    
    print("\n--- Simulation Complete ---")
    print(f"Duration: {duration:.2f}s")
    print(f"Tasks: {len(results)} | Success: {success}/{len(results)}")
    log_event("simulation_complete", {"duration_sec": duration, "total_tasks": len(results), "success_count": success})
    print(f"\n📊 Full trace: {LOG_FILE}")

if __name__ == "__main__":
    run_simulation()
