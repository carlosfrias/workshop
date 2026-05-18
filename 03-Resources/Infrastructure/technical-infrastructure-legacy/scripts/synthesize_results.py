#!/usr/bin/env python3
"""
synthesize_results.py — Combine sub-task results into coherent output (Phase 2)

Reads completed task JSONs from /srv/tasks/completed/ on nodes,
combines them into a single structured result, and optionally
updates the source PLAN document's Execution Results table.

Usage:
    # Synthesize results for a PLAN
    python3 synthesize_results.py --plan PLAN-ID --nodes fnet2,fnet3,fnet4

    # Synthesize + update PLAN document
    python3 synthesize_results.py --plan PLAN-ID --update-plan

    # List completed tasks
    python3 synthesize_results.py --list
"""
import json, sys, subprocess, os, argparse, re
from pathlib import Path
from datetime import datetime

def collect_results(plan_id: str = None, nodes: list = None) -> list:
    """Collect completed task JSONs from all nodes."""
    results = []
    
    if not nodes:
        nodes = [f"fnet{i}" for i in range(1, 8)]
    
    for node in nodes:
        result_dir = f"/tmp/tasks/completed/{node}"
        os.makedirs(result_dir, exist_ok=True)
        
        # SCP completed files
        subprocess.run(
            ["scp", f"friasc@{node}:/srv/tasks/completed/*.json", result_dir],
            capture_output=True
        )
        
        # Load JSONs
        for f in Path(result_dir).glob("*.json"):
            try:
                with open(f) as fh:
                    task = json.load(fh)
                if plan_id is None or task.get("plan_title", "").startswith(plan_id) or task.get("id", "").startswith(plan_id[:4]):
                    results.append(task)
            except (json.JSONDecodeError, KeyError):
                continue
    
    return sorted(results, key=lambda x: x.get("step", 0))

def synthesize_results(results: list) -> dict:
    """Combine sub-task results into a single structured output."""
    if not results:
        return {"error": "No results found", "steps_completed": 0}
    
    synthesis = {
        "plan_title": results[0].get("plan_title", "Unknown"),
        "total_steps": len(results),
        "successful": sum(1 for r in results if r.get("rc", 1) == 0),
        "failed": sum(1 for r in results if r.get("rc", 1) != 0),
        "total_elapsed_ms": sum(r.get("elapsed_seconds", 0) * 1000 for r in results),
        "steps": [],
        "combined_output": "",
    }
    
    for r in results:
        step = {
            "step": r.get("step", r.get("id", "?")[:4]),
            "sub_task": r.get("sub_task", r.get("command", "")[:50]),
            "status": "success" if r.get("rc", 1) == 0 else "failed",
            "rc": r.get("rc", 1),
            "elapsed_seconds": r.get("elapsed_seconds", 0),
            "stdout": r.get("stdout", "")[:500],
            "stderr": r.get("stderr", "")[:200] if r.get("stderr") else "",
        }
        synthesis["steps"].append(step)
        
        if r.get("stdout"):
            synthesis["combined_output"] += f"\n--- Step {step['step']}: {step['sub_task']} ---\n"
            synthesis["combined_output"] += r["stdout"][:1000]
    
    # Calculate quality metrics
    if synthesis["total_steps"] > 0:
        synthesis["success_rate"] = synthesis["successful"] / synthesis["total_steps"]
    else:
        synthesis["success_rate"] = 0.0
    
    return synthesis

def update_plan_execution_results(plan_path: str, synthesis: dict) -> bool:
    """Update the Execution Results table in a PLAN document."""
    if not Path(plan_path).exists():
        return False
    
    with open(plan_path) as f:
        content = f.read()
    
    # Build new Execution Results table
    new_table = "## Execution Results\n\n"
    new_table += "| Step | Actual Model | Actual Node | Actual Latency | Result | Adequate? | Notes |\n"
    new_table += "|------|------------|-------------|----------------|--------|-----------|-------|\n"
    
    for step in synthesis["steps"]:
        result_marker = "✅" if step["status"] == "success" else "❌"
        latency = f"{step['elapsed_seconds']}s" if step['elapsed_seconds'] else "N/A"
        notes = "Auto-recorded" if step["status"] == "success" else f"Failed: rc={step['rc']}"
        model = step.get("actual_model", "unknown")
        node = step.get("actual_node", "unknown")
        
        new_table += f"| {step['step']} | {model} | {node} | {latency} | {result_marker} | {'Yes' if step['status'] == 'success' else 'No'} | {notes} |\n"
    
    # Add summary
    new_table += f"\n**Summary:** {synthesis['successful']}/{synthesis['total_steps']} steps succeeded ({synthesis['success_rate']*100:.0f}%).\n"
    new_table += f"**Total elapsed:** {synthesis['total_elapsed_ms']/1000:.1f}s\n"
    new_table += f"**Updated:** {datetime.now().isoformat()}\n"
    
    # Replace existing Execution Results section or append
    pattern = r"## Execution Results\n(.*?)(?=\n## |\Z)"
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, new_table, content, flags=re.DOTALL)
    else:
        content += "\n\n" + new_table
    
    with open(plan_path, 'w') as f:
        f.write(content)
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Synthesize sub-task results")
    parser.add_argument("--plan", help="Plan ID or title to filter results")
    parser.add_argument("--nodes", help="Comma-separated nodes to collect from")
    parser.add_argument("--update-plan", help="Update PLAN document with results")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--list", action="store_true", help="List available results")
    args = parser.parse_args()
    
    if args.list:
        nodes = args.nodes.split(",") if args.nodes else [f"fnet{i}" for i in range(1, 8)]
        results = collect_results(nodes=nodes)
        print(f"Found {len(results)} completed tasks:")
        for r in results:
            print(f"  Step {r.get('step', '?')}: {r.get('sub_task', '?')[:40]}... (rc={r.get('rc', '?')})")
        return
    
    nodes = args.nodes.split(",") if args.nodes else None
    results = collect_results(args.plan, nodes)
    
    if not results:
        print("No results found", file=sys.stderr)
        sys.exit(1)
    
    synthesis = synthesize_results(results)
    
    if args.json:
        print(json.dumps(synthesis, indent=2))
        return
    
    # Print summary
    print(f"Plan: {synthesis['plan_title']}")
    print(f"Steps: {synthesis['successful']}/{synthesis['total_steps']} succeeded ({synthesis['success_rate']*100:.0f}%)")
    print(f"Total elapsed: {synthesis['total_elapsed_ms']/1000:.1f}s")
    print()
    print("Step-by-step:")
    for step in synthesis["steps"]:
        marker = "✅" if step["status"] == "success" else "❌"
        print(f"  {marker} Step {step['step']}: {step['sub_task'][:50]} ({step['elapsed_seconds']}s)")
    
    if args.update_plan:
        if update_plan_execution_results(args.update_plan, synthesis):
            print(f"\nUpdated: {args.update_plan}")
        else:
            print(f"\nFailed to update: {args.update_plan}", file=sys.stderr)

if __name__ == "__main__":
    main()
