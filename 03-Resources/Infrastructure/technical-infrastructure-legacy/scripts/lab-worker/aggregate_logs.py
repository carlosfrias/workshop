#!/usr/bin/env python3
"""Aggregate performance logs from all lab nodes to the orchestrator."""

import subprocess
import json
from pathlib import Path
from datetime import datetime, timezone

LAB_NODES = [
    ("fnet1", "192.168.0.141"), ("fnet2", "192.168.0.142"),
    ("fnet3", "192.168.0.143"), ("fnet4", "192.168.0.144"),
    ("fnet5", "192.168.0.145"), ("fnet6", "192.168.0.146"),
    ("fnet7", "192.168.0.147"),
]

LOCAL_LOG = Path("/Users/friasc/Dropbox/ai-trading-workspace/technical-infrastructure/wiki/operational/sessions/model-performance-log.jsonl")
REMOTE_LOG = "/srv/lab-worker/performance-log.jsonl"

def fetch_node_logs(node, ip):
    """Fetch logs from a single node via SSH."""
    result = subprocess.run(
        ["ssh", "-o", "StrictHostKeyChecking=no", f"friasc@{ip}",
         f"cat {REMOTE_LOG} 2>/dev/null || echo ''"],
        capture_output=True, text=True
    )
    if result.returncode != 0 or not result.stdout.strip():
        return []
    
    entries = []
    for line in result.stdout.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
            entry["_source_node"] = node
            entries.append(entry)
        except json.JSONDecodeError:
            continue
    return entries

def aggregate():
    """Collect all node logs and write to local aggregate file."""
    LOCAL_LOG.parent.mkdir(parents=True, exist_ok=True)
    
    all_entries = []
    for node, ip in LAB_NODES:
        entries = fetch_node_logs(node, ip)
        all_entries.extend(entries)
        print(f"  {node}: {len(entries)} entries")
    
    # Write to local aggregate log
    with open(LOCAL_LOG, "a") as f:
        for entry in all_entries:
            f.write(json.dumps(entry) + "\n")
    
    print(f"\nAggregated {len(all_entries)} entries to {LOCAL_LOG}")
    return len(all_entries)

if __name__ == "__main__":
    aggregate()
