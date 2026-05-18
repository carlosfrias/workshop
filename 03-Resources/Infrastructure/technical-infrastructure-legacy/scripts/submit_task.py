#!/usr/bin/env python3
"""
submit_task.py — Orchestrator Task Submission
Submit a task JSON to a lab node's pending queue via SSH/SCP.

Usage:
    python3 submit_task.py --node fnet2 --command "ollama list" --type shell
    python3 submit_task.py --node orchestrator --command "ollama ps" --type shell
    python3 submit_task.py --node fnet1 --command "/usr/local/bin/task-worker.sh" --type worker
    python3 submit_task.py --file task_definition.json
    python3 submit_task.py --nodes all --command "hostname" --type shell

Environment:
    SSH user 'friasc' with key auth to all nodes (pre-configured)
    /srv/tasks/pending/ must be writable on target nodes
"""
import json, uuid, sys, subprocess, os, argparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

def ensure_remote_dirs(host):
    """Ensure /srv/tasks directories exist on remote node."""
    subprocess.run(
        ["ssh", "-o", "ConnectTimeout=3", f"friasc@{host}",
         "mkdir -p /srv/tasks/{pending,running,completed}"],
        capture_output=True
    )

def submit_task(node, command, task_type="shell", task_dir="/srv/tasks/pending",
                local_store="/tmp/tasks/pending"):
    """Submit a single task to a node. Returns task_id or None."""
    task_id = str(uuid.uuid4())[:8]

    task = {
        "id": task_id,
        "node": node,
        "type": task_type,
        "command": command,
        "status": "pending",
        "submitted": datetime.now().isoformat(),
    }

    # Save locally for tracking
    os.makedirs(local_store, exist_ok=True)
    local_path = f"{local_store}/{task_id}.json"
    with open(local_path, 'w') as f:
        json.dump(task, f, indent=2)

    # Handle orchestrator (local execution, no SSH)
    if node == "orchestrator":
        orch_pending = os.path.expanduser("~/Dropbox/ai-trading-workspace/srv/tasks/pending")
        os.makedirs(orch_pending, exist_ok=True)
        orch_path = os.path.join(orch_pending, f"{task_id}.json")
        with open(orch_path, 'w') as f:
            json.dump(task, f, indent=2)
        print(f"Task {task_id} submitted to orchestrator (local)")
        return task_id

    # Ensure remote dirs exist
    ensure_remote_dirs(node)

    # SCP to remote
    remote_path = f"friasc@{node}:{task_dir}/{task_id}.json"
    result = subprocess.run(
        ["scp", "-o", "ConnectTimeout=3", local_path, remote_path],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        print(f"Task {task_id} submitted to {node}")
        return task_id
    else:
        print(f"Failed to submit task {task_id} to {node}: {result.stderr}",
              file=sys.stderr)
        return None

def submit_to_all(nodes, command, task_type="shell"):
    """Submit the same task to all nodes in parallel."""
    results = {}
    with ThreadPoolExecutor(max_workers=7) as pool:
        futures = {pool.submit(submit_task, node, command, task_type): node
                   for node in nodes}
        for future in futures:
            node = futures[future]
            results[node] = future.result()
    return results

def main():
    parser = argparse.ArgumentParser(description="Submit tasks to lab nodes")
    parser.add_argument("--node", help="Target node (fnet1-fnet7, orchestrator)")
    parser.add_argument("--nodes", default="all",
                        help="Comma-separated nodes or 'all' (default)")
    parser.add_argument("--command", help="Command to execute")
    parser.add_argument("--type", default="shell",
                        help="Task type (shell, ansible, worker)")
    parser.add_argument("--file", help="Read task from JSON file")
    args = parser.parse_args()

    if args.file:
        with open(args.file) as f:
            task_def = json.load(f)
        node = task_def.get("node", args.node)
        if not node:
            print("--node or task file 'node' field required", file=sys.stderr)
            sys.exit(1)
        result = submit_task(node, task_def["command"],
                             task_def.get("type", "shell"))
        sys.exit(0 if result else 1)

    if not args.command:
        print("--command or --file required", file=sys.stderr)
        sys.exit(1)

    if args.node:
        # Single node
        result = submit_task(args.node, args.command, args.type)
        sys.exit(0 if result else 1)
    else:
        # All nodes (default or --nodes)
        if args.nodes == "all":
            nodes = [f"fnet{i}" for i in range(1, 8)]
        else:
            nodes = args.nodes.split(",")
        results = submit_to_all(nodes, args.command, args.type)
        success = sum(1 for v in results.values() if v is not None)
        print(f"\nSubmitted {success}/{len(nodes)} tasks")
        for node, task_id in results.items():
            print(f"  {node}: {'OK' if task_id else 'FAILED'}")
        sys.exit(0 if success == len(nodes) else 1)

if __name__ == "__main__":
    main()
