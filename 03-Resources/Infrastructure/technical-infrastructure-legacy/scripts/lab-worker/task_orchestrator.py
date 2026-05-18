#!/usr/bin/env python3
"""Task Orchestrator
Submits tasks to lab node queues via SSH/SCP.
Replaces direct SSH command execution with queue-based delegation.
"""

import json
import sys
import subprocess
import uuid
import time
from pathlib import Path
from datetime import datetime, timezone

TASK_DIR = "/srv/lab-worker/pending"
RESULT_DIR = "/srv/lab-worker/results"
ORCHESTRATOR_QUEUE = Path.home() / ".pi" / "lab-worker"

LAB_NODES = {
    "fnet1": "192.168.0.141", "fnet2": "192.168.0.142",
    "fnet3": "192.168.0.143", "fnet4": "192.168.0.144",
    "fnet5": "192.168.0.145", "fnet6": "192.168.0.146",
    "fnet7": "192.168.0.147",
}

def submit_task(node, task_json):
    """Drop a task file into the node's pending queue."""
    task_id = str(uuid.uuid4())[:8]
    task_json["task_id"] = task_id
    task_json["submitted_at"] = datetime.now(timezone.utc).isoformat()
    
    # Handle local orchestrator (fnet0) differently
    if node == "fnet0":
        local_pending = ORCHESTRATOR_QUEUE / "pending"
        local_pending.mkdir(parents=True, exist_ok=True)
        
        task_file = local_pending / f"{task_id}.json"
        with open(task_file, "w") as f:
            json.dump(task_json, f, indent=2)
        
        print(f"✅ Task {task_id} submitted to fnet0 (local queue)")
        return task_id
    
    # Remote lab nodes via SCP
    remote_path = f"{TASK_DIR}/{task_id}.json"
    
    # Write temp file locally then scp
    tmp = f"/tmp/task_{task_id}.json"
    with open(tmp, "w") as f:
        json.dump(task_json, f)
    
    result = subprocess.run(
        ["scp", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null",
         tmp, f"friasc@{LAB_NODES[node]}:{remote_path}"],
        capture_output=True, text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Failed to submit to {node}: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    
    print(f"✅ Task {task_id} submitted to {node}")
    return task_id

def wait_for_result(node, task_id, timeout=300):
    """Poll for result file."""
    # Handle local orchestrator (fnet0)
    if node == "fnet0":
        local_results = ORCHESTRATOR_QUEUE / "results"
        result_file = local_results / f"{task_id}.json"
        
        start = time.time()
        while time.time() - start < timeout:
            if result_file.exists():
                with open(result_file, "r") as f:
                    return json.load(f)
            time.sleep(2)
        raise TimeoutError(f"Task {task_id} timed out after {timeout}s")
    
    # Remote lab nodes via SSH
    remote_path = f"{RESULT_DIR}/{task_id}.json"
    start = time.time()
    
    while time.time() - start < timeout:
        result = subprocess.run(
            ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null",
             f"friasc@{LAB_NODES[node]}", f"test -f {remote_path} && cat {remote_path}"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        time.sleep(2)
    
    raise TimeoutError(f"Task {task_id} timed out after {timeout}s")

def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <node> '<task_json>'")
        sys.exit(1)
    
    node = sys.argv[1]
    task_json = json.loads(sys.argv[2])
    
    task_id = submit_task(node, task_json)
    print(f"Waiting for result on {node}...")
    result = wait_for_result(node, task_id)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
