#!/usr/bin/env python3
"""
Canary Simulation: Multi-Tier Escalation Loop
Tests the master-prompt-system decomposition and tiered escalation logic
on the orchestrator using subagent invocation for cognitive steps.
"""

import json
import time
import random
import subprocess
from datetime import datetime
from pathlib import Path

# --- Configuration ---
LOG_FILE = Path("/Users/friasc/Dropbox/ai-trading-workspace/technical-infrastructure/wiki/operational/sessions/escalation-simulation.jsonl")
DECOMPOSER_AGENT = "/Users/friasc/Dropbox/ai-trading-workspace/technical-infrastructure/packages/decompose-execute-verify/agents/decomposer.md"
VERIFIER_AGENT = "/Users/friasc/Dropbox/ai-trading-workspace/technical-infrastructure/packages/decompose-execute-verify/agents/verifier.md"

# Model Tiers (from keyword-router.json and user's policy)
TIERS = {
    "local_low":    {"model": "qwen3.5:4b",      "capacity": "LOW",    "latency_ms": 2000},
    "local_medium": {"model": "qwen3.5:4b",      "capacity": "MEDIUM", "latency_ms": 6000},
    "local_high":   {"model": "gemma4:e4b",      "capacity": "HIGH",   "latency_ms": 15000},
    "cloud_low":    {"model": "qwen3.5:397b-cloud", "capacity": "HIGH+",  "latency_ms": 8000},
    "cloud_medium": {"model": "qwen3.5:397b-cloud", "capacity": "HIGH+",  "latency_ms": 12000},
    "cloud_high":   {"model": "kimi-k2.6",       "capacity": "ULTRA",  "latency_ms": 25000},
}

TIER_ORDER = ["local_low", "local_medium", "local_high", "cloud_low", "cloud_medium", "cloud_high"]

# Canary Task
CANARY_TASK = """
Monitor the disk usage of all 7 lab nodes (fnet1-fnet7), identify any node with 
usage over 80%, and generate a markdown report with recommendations for cleanup.
"""

def log_event(event_type, data):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event_type,
        **data
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"  [LOG] {event_type}: {data}")

def invoke_subagent(agent_file, prompt, timeout=60):
    """Invoke a pi subagent using the agent file as system prompt."""
    # Read the agent definition
    system_prompt = Path(agent_file).read_text()
    
    # For this simulation, we mock the subagent call.
    # In a live harness, this would use the actual subagent tool.
    # We simulate by returning a structured response based on the agent type.
    
    if "decomposer" in agent_file:
        return mock_decomposer(prompt)
    elif "verifier" in agent_file:
        return mock_verifier(prompt)
    else:
        return {"status": "unknown", "output": "Mock response"}

def mock_decomposer(prompt, factor=1):
    """Simulate decomposer output."""
    if "disk usage" in prompt.lower():
        tasks = []
        for i in range(1, 8):
            tasks.append({
                "id": f"check-disk-fnet{i}",
                "action": f"Check disk usage on fnet{i}",
                "node": f"fnet{i}",
                "complexity": "LOW"
            })
        tasks.append({
            "id": "aggregate-report",
            "action": "Aggregate results and generate markdown report",
            "complexity": "MEDIUM"
        })
        return {"status": "decomposed", "tasks": tasks, "factor": factor}
    
    # 2x decomposition: split the task further
    if factor >= 2:
        return {
            "status": "decomposed",
            "tasks": [
                {"id": "sub-task-a", "action": "Extract raw data", "complexity": "LOW"},
                {"id": "sub-task-b", "action": "Analyze thresholds", "complexity": "LOW"},
            ],
            "factor": factor
        }
    
    return {"status": "decomposed", "tasks": [{"id": "task-1", "action": prompt, "complexity": "MEDIUM"}]}

def mock_verifier(prompt, result=None):
    """Simulate verifier output."""
    return {"status": "verified", "pass": True, "issues": []}

def check_health(tier):
    """Simulate health monitor check."""
    # Simulate saturation based on task complexity vs model capacity
    # For this canary, we force specific saturation events to test escalation
    return "HEALTHY"

# --- Stress Test Configuration ---
FORCE_SATURATION = True  # Set to True to test escalation logic
SATURATION_DEPTH = 1   # How many levels deep before success (0=never sat, 1=local_low sat, 2=local_med sat, etc.)

def simulate_execution(task, tier):
    """Simulate task execution on a node."""
    tier_info = TIERS[tier]
    latency = tier_info["latency_ms"] / 1000.0
    
    # Simulate processing time
    time.sleep(min(latency, 0.1))  # Cap at 0.1s for simulation speed
    
    # Force saturation for stress testing
    if FORCE_SATURATION:
        current_idx = TIER_ORDER.index(tier)
        if current_idx < SATURATION_DEPTH:
            return {"status": "SATURATED", "reason": f"Simulated saturation at {tier} for stress testing"}
    
    # Simulate saturation for specific conditions
    # - If task complexity is HIGH and model capacity is LOW/MEDIUM
    if task.get("complexity") == "HIGH" and tier_info["capacity"] in ["LOW", "MEDIUM"]:
        return {"status": "SATURATED", "reason": "Task complexity exceeds model capacity"}
    
    # - Random saturation for cloud tier (to test cloud escalation)
    if "cloud" in tier and random.random() < 0.1:
        return {"status": "SATURATED", "reason": "Cloud node temporarily overloaded"}
    
    return {
        "status": "SUCCESS",
        "output": f"Task '{task['id']}' completed on {tier} ({tier_info['model']})",
        "latency_ms": tier_info["latency_ms"]
    }

def execute_task(task, tier="local_low", generation=0):
    """Execute a task with the tiered escalation policy.
    
    generation=0: Original task (can be decomposed once)
    generation>0: Already decomposed sub-task (escalate only, no further decomposition)
    """
    indent = "  " * generation
    print(f"{indent}▶ Executing '{task['id']}' on {tier} (gen={generation})")
    
    # 1. Check Health
    health = check_health(tier)
    print(f"{indent}  Health: {health}")
    
    # 2. Attempt Execution
    result = simulate_execution(task, tier)
    print(f"{indent}  Result: {result['status']}")
    
    log_event("execution_attempt", {
        "task_id": task["id"],
        "tier": tier,
        "model": TIERS[tier]["model"],
        "health": health,
        "result": result["status"],
        "generation": generation
    })
    
    if result["status"] == "SUCCESS":
        return result
    
    # 3. SATURATED
    if generation == 0:
        # First saturation: try 2x decomposition and retry on same tier
        print(f"{indent}  ⚠️ SATURATED. Triggering 2x decomposition...")
        log_event("saturation_detected", {"task_id": task["id"], "tier": tier, "action": "2x_decompose"})
        
        decomp = mock_decomposer(task["action"], factor=2)
        sub_tasks = decomp.get("tasks", [task])
        
        print(f"{indent}  Decomposed into {len(sub_tasks)} sub-tasks")
        log_event("decomposition", {"task_id": task["id"], "sub_task_count": len(sub_tasks), "tier": tier})
        
        # Retry each sub-task on same tier (generation=1)
        sub_results = []
        for sub in sub_tasks:
            sub_result = execute_task(sub, tier, generation + 1)
            
            if sub_result["status"] == "SATURATED":
                # 4. Still saturated after 2x: escalate to next model in tier
                current_idx = TIER_ORDER.index(tier)
                if current_idx < len(TIER_ORDER) - 1:
                    next_tier = TIER_ORDER[current_idx + 1]
                    print(f"{indent}  ⬆️ Escalating '{sub['id']}' to {next_tier}")
                    log_event("escalation", {"task_id": sub["id"], "from_tier": tier, "to_tier": next_tier, "generation": generation + 1})
                    sub_result = execute_task(sub, next_tier, generation + 1)
                else:
                    print(f"{indent}  ❌ No higher tier available for '{sub['id']}'!")
                    log_event("escalation_failed", {"task_id": sub["id"], "tier": tier, "generation": generation + 1})
            
            sub_results.append(sub_result)
        
        # Check if all sub-tasks succeeded
        if all(r["status"] == "SUCCESS" for r in sub_results):
            return {"status": "SUCCESS", "sub_results": sub_results}
        else:
            return {"status": "FAILED", "reason": "Sub-task escalation exhausted"}
    
    else:
        # Already decomposed (generation > 0): escalate immediately, no more decomposition
        current_idx = TIER_ORDER.index(tier)
        if current_idx < len(TIER_ORDER) - 1:
            next_tier = TIER_ORDER[current_idx + 1]
            print(f"{indent}  ⬆️ Escalating '{task['id']}' to {next_tier}")
            log_event("escalation", {"task_id": task["id"], "from_tier": tier, "to_tier": next_tier, "generation": generation})
            return execute_task(task, next_tier, generation)
        else:
            print(f"{indent}  ❌ No higher tier available for '{task['id']}'!")
            log_event("escalation_failed", {"task_id": task["id"], "tier": tier, "generation": generation})
            return {"status": "FAILED", "reason": "Escalation exhausted"}

def run_simulation():
    print("╔════════════════════════════════════════════════════════╗")
    print("║   CANARY SIMULATION: Multi-Tier Escalation Loop        ║")
    print("╚════════════════════════════════════════════════════════╝")
    print(f"\nTask: {CANARY_TASK.strip()}")
    print(f"Log: {LOG_FILE}\n")
    
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    start_time = time.time()
    
    # Phase 1: Decomposition
    print("--- Phase 1: Initial Decomposition ---")
    plan = invoke_subagent(DECOMPOSER_AGENT, CANARY_TASK)
    print(f"Plan: {len(plan['tasks'])} tasks")
    log_event("initial_decomposition", {"task_count": len(plan["tasks"])})
    
    # Phase 2: Execution with Escalation
    print("\n--- Phase 2: Execution with Tiered Escalation ---")
    final_results = []
    for task in plan["tasks"]:
        result = execute_task(task, tier="local_low", generation=0)
        final_results.append(result)
    
    # Phase 3: Verification
    print("\n--- Phase 3: Verification ---")
    # Only verify the aggregate report task
    report_tasks = [t for t in plan["tasks"] if "report" in t["id"]]
    if report_tasks:
        verify = invoke_subagent(VERIFIER_AGENT, report_tasks[0]["action"])
        print(f"Verification: {verify['status']}")
        log_event("verification", {"status": verify["status"]})
    
    # Phase 4: Summary
    duration = time.time() - start_time
    success_count = sum(1 for r in final_results if r["status"] == "SUCCESS")
    
    print("\n--- Simulation Complete ---")
    print(f"Duration: {duration:.2f}s")
    print(f"Tasks: {len(final_results)}")
    print(f"Success: {success_count}/{len(final_results)}")
    
    log_event("simulation_complete", {
        "duration_sec": duration,
        "total_tasks": len(final_results),
        "success_count": success_count
    })
    
    print(f"\n📊 Full trace logged to: {LOG_FILE}")

if __name__ == "__main__":
    run_simulation()
