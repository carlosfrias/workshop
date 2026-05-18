#!/usr/bin/env python3
"""
decompose_task.py — PLAN Document Decomposition Engine (Phase 2)

Reads a PLAN markdown document, extracts the decomposition table,
and generates executable task JSONs for the orchestration system.

Usage:
    # Parse PLAN and print task JSONs
    python3 decompose_task.py --plan wiki/planning/PLAN-2026-05-01-1547.md

    # Parse + submit to orchestration
    python3 decompose_task.py --plan wiki/planning/PLAN-2026-05-01-1547.md --submit

    # Dry run (print only, no submission)
    python3 decompose_task.py --plan PLAN.md --dry-run

    # List available PLAN documents
    python3 decompose_task.py --list-plans

Output: One task JSON per decomposition step, ready for task-worker.sh
"""
import json, re, sys, os, subprocess, argparse
from pathlib import Path
from datetime import datetime

# Add TI-011 node registry import path
TI011_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if TI011_SCRIPT_DIR not in sys.path:
    sys.path.insert(0, TI011_SCRIPT_DIR)

try:
    from ti011_node_registry import NodeRegistry
except ImportError:
    NodeRegistry = None

# ── PARSING ─────────────────────────────────────────────────────────

def extract_markdown_table(markdown: str, table_name: str = "Decomposition") -> list:
    """Extract a markdown table by looking for a section header and table.
    
    Looks for:
    ## Decomposition
    | Step | Sub-Task | Suggested Model | ...
    |------|----------|---------------| ...
    | 1 | ... | ... | ...
    """
    lines = markdown.split('\n')
    
    # Find the section header (e.g., "## Decomposition")
    section_start = None
    for i, line in enumerate(lines):
        if f"## {table_name}" in line or f"### {table_name}" in line:
            section_start = i
            break
    
    if section_start is None:
        return []
    
    # Find the first table after the section header
    table_start = None
    for i in range(section_start + 1, min(section_start + 10, len(lines))):
        if '| Step |' in lines[i]:
            table_start = i
            break
    
    if table_start is None:
        return []
    
    # Extract rows until non-table line
    rows = []
    for line in lines[table_start:]:
        line = line.strip()
        if not line.startswith('|'):
            if line and not line.startswith('#'):
                continue
            break
        if '|---' in line or line.startswith('|---'):
            continue
        # Skip header row
        if 'Step' in line and 'Sub-Task' in line:
            continue
        cells = [cell.strip() for cell in line.split('|')[1:-1]]
        if cells:
            rows.append(cells)
    
    return rows

def parse_decomposition_table(rows: list) -> list:
    """Parse table rows into structured step dicts."""
    steps = []
    for row in rows:
        if len(row) < 7:
            continue  # Skip malformed rows
        
        step = {
            "step": int(row[0]) if row[0].isdigit() else len(steps) + 1,
            "sub_task": row[1],
            "suggested_model": row[2],
            "suggested_node": row[3],
            "context_size": row[4],
            "estimated_latency": row[5],
            "fallback_model": row[6] if len(row) > 6 else "",
        }
        steps.append(step)
    
    return steps

def _resolve_route(complexity="medium", vision=False):
    """Look up optimal (node, model) from NodeRegistry, fallback to defaults."""
    if NodeRegistry is None:
        return "orchestrator", "qwen3:8b", "qwen3.5:397b-cloud"
    try:
        reg = NodeRegistry()
        route = reg.best_model_for(complexity.lower(), vision=vision)
        if route:
            return route["node"], route["model"], "qwen3.5:397b-cloud"
        return "orchestrator", "qwen3:8b", "kimi-k2.6:cloud"
    except Exception:
        return "orchestrator", "qwen3:8b", "qwen3.5:397b-cloud"


def plan_to_tasks(plan_path: str) -> list:
    """Convert a PLAN markdown file to a list of task dicts."""
    with open(plan_path) as f:
        markdown = f.read()
    
    # Extract title and context
    title_match = re.search(r'^#\s+Planning:\s+(.+)$', markdown, re.MULTILINE)
    title = title_match.group(1) if title_match else "Unknown Plan"
    
    context_match = re.search(r'\*\*Context:\*\*\s+(.+)$', markdown, re.MULTILINE)
    context = context_match.group(1) if context_match else ""
    
    # Extract complexity estimate
    complexity_match = re.search(r'\*\*Complexity Estimate:\*\*\s+(\w+)', markdown)
    complexity = complexity_match.group(1) if complexity_match else "MEDIUM"
    
    # Extract decomposition table
    rows = extract_markdown_table(markdown)
    steps = parse_decomposition_table(rows)
    
    if not steps:
        # No decomposition table found — create single task from plan
        node, model, fallback = _resolve_route(complexity.lower())
        return [{
            "id": generate_task_id(),
            "plan_title": title,
            "step": 1,
            "sub_task": context or title,
            "suggested_model": model,
            "suggested_node": node,
            "context_size": "~2000 tokens",
            "estimated_latency": "unknown",
            "fallback_model": fallback,
            "complexity": complexity,
            "type": "shell",
            "command": f"# Execute plan: {title}\n# Context: {context}",
            "status": "pending",
            "created": datetime.now().isoformat(),
        }]
    
    # Convert steps to task JSONs
    tasks = []
    for step in steps:
        # Resolve empty/placeholder values from registry
        sm = step["suggested_model"] if step["suggested_model"] and step["suggested_model"] != "?" else None
        sn = step["suggested_node"] if step["suggested_node"] and step["suggested_node"] != "?" else None
        if not sm or not sn:
            node, model, fallback = _resolve_route(complexity.lower())
            if not sm:
                sm = model
            if not sn:
                sn = node
            if not step.get("fallback_model"):
                step["fallback_model"] = fallback

        task = {
            "id": generate_task_id(),
            "plan_title": title,
            "step": step["step"],
            "sub_task": step["sub_task"],
            "suggested_model": sm,
            "suggested_node": sn,
            "context_size": step["context_size"],
            "estimated_latency": step["estimated_latency"],
            "fallback_model": step.get("fallback_model", "qwen3.5:397b-cloud"),
            "complexity": complexity,
            "type": "shell",
            "command": f"# Step {step['step']}: {step['sub_task']}\n# Model: {sm} on {sn}",
            "status": "pending",
            "created": datetime.now().isoformat(),
        }
        tasks.append(task)
    
    return tasks

def generate_task_id() -> str:
    import uuid
    return str(uuid.uuid4())[:8]

# ── SUBMISSION ────────────────────────────────────────────────────

def submit_task(task: dict, dry_run: bool = False) -> bool:
    """Submit a single task via the orchestration system."""
    node = task.get("suggested_node", "orchestrator")
    if node == "orchestrator":
        node = "fnet1"  # Default to fnet1 for orchestrator tasks
    
    task_json = json.dumps(task, indent=2)
    
    if dry_run:
        print(f"[DRY RUN] Would submit to {node}:")
        print(task_json)
        return True
    
    # Use submit_task.py
    script_path = Path(__file__).parent / "submit_task.py"
    if script_path.exists():
        # Write task to temp file
        tmp_path = f"/tmp/task-{task['id']}.json"
        with open(tmp_path, 'w') as f:
            json.dump(task, f)
        
        result = subprocess.run(
            [sys.executable, str(script_path), "--file", tmp_path],
            capture_output=True, text=True
        )
        return result.returncode == 0
    else:
        # Fallback: SCP directly
        tmp_path = f"/tmp/task-{task['id']}.json"
        with open(tmp_path, 'w') as f:
            json.dump(task, f)
        
        result = subprocess.run(
            ["scp", tmp_path, f"friasc@{node}:/srv/tasks/pending/{task['id']}.json"],
            capture_output=True
        )
        return result.returncode == 0

# ── CLI ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Decompose PLAN documents into executable tasks")
    parser.add_argument("--plan", help="Path to PLAN markdown file")
    parser.add_argument("--submit", action="store_true", help="Submit tasks to orchestration")
    parser.add_argument("--dry-run", action="store_true", help="Print tasks without submitting")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--list-plans", action="store_true", help="List available PLAN documents")
    args = parser.parse_args()
    
    if args.list_plans:
        plans_dir = Path("technical-infrastructure/wiki/planning")
        if plans_dir.exists():
            for plan in sorted(plans_dir.glob("PLAN-*.md")):
                print(f"  {plan}")
        else:
            print("No planning directory found")
        return
    
    if not args.plan:
        parser.print_help()
        sys.exit(1)
    
    # Resolve path
    plan_path = Path(args.plan)
    if not plan_path.exists():
        # Try relative to repo root
        plan_path = Path("technical-infrastructure/wiki/planning") / args.plan
        if not plan_path.exists():
            print(f"Plan not found: {args.plan}", file=sys.stderr)
            sys.exit(1)
    
    # Parse plan
    tasks = plan_to_tasks(str(plan_path))
    
    if args.json:
        print(json.dumps(tasks, indent=2))
        return
    
    # Print summary
    print(f"Plan: {tasks[0]['plan_title'] if tasks else 'Unknown'}")
    print(f"Steps: {len(tasks)}")
    print(f"Complexity: {tasks[0]['complexity'] if tasks else 'N/A'}")
    print()
    
    for task in tasks:
        print(f"Step {task['step']}: {task['sub_task']}")
        print(f"  Model: {task['suggested_model']} @ {task['suggested_node']}")
        print(f"  Latency: {task['estimated_latency']}")
        print()
    
    # Submit if requested
    if args.submit or args.dry_run:
        print("=" * 60)
        print("Submitting tasks..." if args.submit else "[DRY RUN] Tasks would be submitted:")
        print()
        
        success = 0
        for task in tasks:
            if submit_task(task, dry_run=args.dry_run):
                success += 1
                print(f"  ✅ Step {task['step']}: {task['sub_task'][:40]}")
            else:
                print(f"  ❌ Step {task['step']}: FAILED")
        
        print()
        print(f"Submitted: {success}/{len(tasks)} tasks")

if __name__ == "__main__":
    main()
