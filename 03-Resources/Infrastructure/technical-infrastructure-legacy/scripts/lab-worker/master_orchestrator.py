#!/usr/bin/env python3
"""Master Orchestrator
Executes the full loop: decompose -> submit to node -> wait -> verify -> log -> aggregate.
Called by the master prompt system after decomposition.
"""

import json
import sys
import subprocess
import time
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from task_orchestrator import submit_task, wait_for_result
from verify_result import verify
from log_performance import log_entry
from aggregate_logs import aggregate

LAB_NODES = {
    "fnet0": "192.168.0.184",   # Orchestrator (this machine)
    "fnet1": "192.168.0.141", "fnet2": "192.168.0.142",
    "fnet3": "192.168.0.143", "fnet4": "192.168.0.144",
    "fnet5": "192.168.0.145", "fnet6": "192.168.0.146",
    "fnet7": "192.168.0.147",
}

ORCHESTRATOR_QUEUE = Path.home() / ".pi" / "lab-worker"

def check_health(node):
    """Pre-flight health check using health-monitor pool snapshot.
    Returns (healthy, message) tuple.
    """
    try:
        # Get pool snapshot from health-monitor
        result = subprocess.run(
            ["python3", str(Path.home() / ".pi/agent/git/github.com/carlosfrias/health-monitor/scripts/pool_monitor.py")],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode != 0:
            return True, f"Health check unavailable: {result.stderr[:100]}"
        
        pool = json.loads(result.stdout)
        
        # Find the node in the pool
        node_data = None
        for n in pool.get("nodes", []):
            if n.get("node_id") == node:
                node_data = n
                break
        
        if not node_data:
            # Node not in pool (lab nodes may not report yet)
            if node == "fnet0":
                return False, "fnet0 not reporting to health-monitor"
            else:
                return True, f"{node} health not available (assuming healthy)"
        
        # Check status
        status = node_data.get("status", "unknown")
        metrics = node_data.get("metrics", {})
        
        if status == "critical":
            ram = metrics.get("ram_percent", 0)
            swap = metrics.get("swap_percent", 0)
            cpu = metrics.get("cpu_percent", 0)
            return False, f"Critical: RAM={ram:.1f}%, Swap={swap:.1f}%, CPU={cpu:.1f}%"
        elif status == "stressed":
            return False, f"Stressed: {json.dumps(metrics)}"
        else:
            ram = metrics.get("ram_percent", 0)
            cpu = metrics.get("cpu_percent", 0)
            return True, f"OK: RAM={ram:.1f}%, CPU={cpu:.1f}%"
            
    except subprocess.TimeoutExpired:
        return True, "Health check timeout (assuming healthy)"
    except Exception as e:
        return True, f"Health check error: {e}"

def wait_for_result_async(node, task_id, timeout=300, health_check_interval=10):
    """Async wait with health monitoring.
    Polls for result while checking node health.
    If health degrades, escalates to fallback node.
    """
    start = time.time()
    last_health_check = 0
    
    while time.time() - start < timeout:
        # Check health periodically
        if time.time() - last_health_check > health_check_interval:
            healthy, health_msg = check_health(node)
            if not healthy:
                print(f"[ORCHESTRATOR] ⚠️  {node} health degraded during execution: {health_msg}")
                print(f"[ORCHESTRATOR] Aborting wait, task may timeout on remote...")
                return {"error": f"Node health degraded: {health_msg}", "aborted": True}
            last_health_check = time.time()
        
        # Try to get result
        try:
            result = wait_for_result(node, task_id, timeout=2)  # Short timeout for polling
            return result
        except TimeoutError:
            pass  # Continue polling
        
        time.sleep(1)  # Small delay between polls
    
    raise TimeoutError(f"Task {task_id} timed out after {timeout}s")

def get_healthy_node_pool():
    """Get list of healthy nodes sorted by preference.
    Returns [(node_id, ip, health_score), ...] sorted by health (best first).
    """
    try:
        result = subprocess.run(
            ["python3", str(Path.home() / ".pi/agent/git/github.com/carlosfrias/health-monitor/scripts/pool_monitor.py")],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode != 0:
            # Fallback to static list if health-monitor unavailable
            return [("fnet2", LAB_NODES["fnet2"], 100)]
        
        pool = json.loads(result.stdout)
        healthy_nodes = []
        
        for node_data in pool.get("nodes", []):
            node_id = node_data.get("node_id")
            if node_id not in LAB_NODES:
                continue  # Skip unknown nodes
            
            status = node_data.get("status", "unknown")
            metrics = node_data.get("metrics", {})
            
            # Calculate health score (0-100)
            ram = metrics.get("ram_percent", 50)
            cpu = metrics.get("cpu_percent", 50)
            swap = metrics.get("swap_percent", 0)
            
            # Penalize high resource usage
            health_score = 100 - ram - cpu - (swap * 2)
            health_score = max(0, min(100, health_score))  # Clamp to 0-100
            
            # Only include healthy/stressed nodes (not critical)
            if status != "critical" and health_score >= 30:
                healthy_nodes.append((node_id, LAB_NODES[node_id], health_score))
        
        # Sort by health score (descending)
        healthy_nodes.sort(key=lambda x: x[2], reverse=True)
        
        return healthy_nodes if healthy_nodes else [("fnet2", LAB_NODES["fnet2"], 100)]
        
    except Exception as e:
        print(f"[ORCHESTRATOR] Health pool error: {e}")
        return [("fnet2", LAB_NODES["fnet2"], 100)]

def route_task(task_json, preferred_node=None, use_async=True, auto_escalate=True):
    """Route a task with multi-tier escalation based on health."""
    
    if auto_escalate:
        # Get healthy node pool
        print(f"[ORCHESTRATOR] Building healthy node pool...")
        healthy_pool = get_healthy_node_pool()
        
        if not healthy_pool:
            print(f"[ORCHESTRATOR] ⚠️  No healthy nodes available, using default fnet2")
            node = "fnet2"
        else:
            # Prefer requested node if healthy, otherwise use best available
            if preferred_node:
                for node_id, ip, score in healthy_pool:
                    if node_id == preferred_node:
                        node = node_id
                        print(f"[ORCHESTRATOR] ✅ Preferred node {node_id} available (health={score:.0f})")
                        break
                else:
                    # Preferred not healthy, use best available
                    node, ip, score = healthy_pool[0]
                    print(f"[ORCHESTRATOR] ⚠️  Preferred {preferred_node} unhealthy, escalating to {node} (health={score:.0f})")
            else:
                # No preference, use healthiest node
                node, ip, score = healthy_pool[0]
                print(f"[ORCHESTRATOR] ✅ Selected {node} (healthiest, score={score:.0f})")
    else:
        # No auto-escalation, use preferred or default
        node = preferred_node or "fnet2"
    
    # Pre-flight health check for selected node
    print(f"[ORCHESTRATOR] Pre-flight health check for {node}...")
    healthy, health_msg = check_health(node)
    
    if not healthy:
        print(f"[ORCHESTRATOR] ⚠️  {node} unhealthy: {health_msg}")
        if auto_escalate:
            # Try next healthy node
            healthy_pool = get_healthy_node_pool()
            for next_node, ip, score in healthy_pool:
                if next_node != node:
                    print(f"[ORCHESTRATOR] Escalating to {next_node} (health={score:.0f})...")
                    node = next_node
                    healthy, health_msg = check_health(node)
                    if healthy:
                        break
            else:
                print(f"[ORCHESTRATOR] ⚠️  No healthy alternatives, proceeding with {node}...")
        else:
            print(f"[ORCHESTRATOR] ⚠️  Proceeding anyway (auto-escalation disabled)...")
    else:
        print(f"[ORCHESTRATOR] ✅ {node}: {health_msg}")
    
    print(f"[ORCHESTRATOR] Routing to {node}")
    
    # Submit
    task_id = submit_task(node, task_json)
    
    # Wait (async with health monitoring)
    print(f"[ORCHESTRATOR] Waiting for result (async health monitoring enabled)...")
    start = time.time()
    
    if use_async:
        result = wait_for_result_async(node, task_id, timeout=300)
    else:
        result = wait_for_result(node, task_id, timeout=300)
    
    latency = time.time() - start
    
    # Verify
    print(f"[ORCHESTRATOR] Verifying result...")
    # Write temp result for verifier
    tmp_result = f"/tmp/result_{task_id}.json"
    with open(tmp_result, "w") as f:
        json.dump(result, f)
    verification = verify(tmp_result)
    
    # Log performance locally (orchestrator side)
    prompt_tokens = result.get("prompt_eval_count", 0)
    response_tokens = result.get("eval_count", 0)
    try:
        log_entry(node, task_json.get("model", "unknown"), task_id, latency,
                  prompt_tokens, response_tokens, verification["status"] == "PASS")
    except Exception as e:
        print(f"[ORCHESTRATOR] Log warning: {e}")
    
    # Aggregate
    aggregate()
    
    return {
        "task_id": task_id,
        "node": node,
        "result": result,
        "verification": verification,
        "latency_sec": round(latency, 3),
    }

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} '<task_json>' [preferred_node]")
        sys.exit(1)
    
    task_json = json.loads(sys.argv[1])
    preferred = sys.argv[2] if len(sys.argv) > 2 else None
    
    outcome = route_task(task_json, preferred)
    print(json.dumps(outcome, indent=2))

if __name__ == "__main__":
    main()
