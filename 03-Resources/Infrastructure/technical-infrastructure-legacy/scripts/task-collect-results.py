#!/usr/bin/env python3
"""
task-collect-results.py — Orchestrator Result Collection
Pull completed task JSONs from all lab nodes and aggregate into a report.

Usage:
    python3 task-collect-results.py --nodes fnet1,fnet2,fnet3,fnet4,fnet5,fnet6,fnet7
    python3 task-collect-results.py --nodes all --output results.json
"""
import json, sys, subprocess, os, argparse
from datetime import datetime

def collect_from_node(node, remote_dir="/srv/tasks/completed", local_dir="/tmp/tasks/completed"):
    """Collect all completed tasks from a node."""
    os.makedirs(local_dir, exist_ok=True)
    
    # SCP all completed files
    result = subprocess.run(
        ["scp", f"friasc@{node}:{remote_dir}/*.json", local_dir],
        capture_output=True, text=True
    )
    
    if result.returncode != 0:
        if "No such file or directory" not in result.stderr:
            print(f"Warning: {node} collection issue: {result.stderr.strip()}", file=sys.stderr)
    
    # Load all JSONs
    results = []
    node_dir = os.path.join(local_dir, node)
    os.makedirs(node_dir, exist_ok=True)
    # Move collected files to node-specific dir
    for f in os.listdir(local_dir):
        if f.endswith('.json') and os.path.isfile(os.path.join(local_dir, f)):
            os.rename(os.path.join(local_dir, f), os.path.join(node_dir, f))
    
    for f in os.listdir(node_dir):
        if f.endswith('.json'):
            with open(os.path.join(node_dir, f)) as fh:
                try:
                    results.append(json.load(fh))
                except json.JSONDecodeError:
                    pass
    
    return results

def collect_all(nodes):
    """Collect results from all nodes and aggregate."""
    all_results = []
    
    for node in nodes:
        results = collect_from_node(node)
        all_results.extend(results)
        print(f"{node}: {len(results)} completed tasks collected")
    
    return all_results

def generate_report(results, output=None):
    """Generate summary report."""
    report = {
        "collected_at": datetime.now().isoformat(),
        "total_tasks": len(results),
        "successful": len([r for r in results if r.get("rc", 1) == 0]),
        "failed": len([r for r in results if r.get("rc", 1) != 0]),
        "pending_or_running": None,  # Not known without checking pending/running dirs
        "tasks": results,
    }
    
    if output:
        with open(output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Report saved to {output}")
    
    print(f"\nSummary: {report['successful']}/{report['total_tasks']} tasks succeeded")
    if report['failed']:
        print(f"Failures: {report['failed']}")
        for r in results:
            if r.get("rc", 1) != 0:
                print(f"  [{r.get('node','?')}] {r.get('id','?')}: rc={r.get('rc','?')} cmd={r.get('command','?')[:50]}")
    
    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collect task results from lab nodes")
    parser.add_argument("--nodes", default="all", help="Comma-separated nodes or 'all'")
    parser.add_argument("--output", "-o", default="/tmp/tasks/report.json", help="Report output file")
    
    args = parser.parse_args()
    
    if args.nodes == "all":
        nodes = [f"fnet{i}" for i in range(1, 8)]
    else:
        nodes = args.nodes.split(",")
    
    results = collect_all(nodes)
    generate_report(results, args.output)
