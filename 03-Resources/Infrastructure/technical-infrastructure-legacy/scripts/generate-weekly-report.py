#!/usr/bin/env python3
"""
generate-weekly-report.py — Generate a weekly performance report from model routing logs

Usage:
    python3 scripts/generate-weekly-report.py
    python3 scripts/generate-weekly-report.py --output wiki/operational/status/STATUS-2026-05-03.md
    python3 scripts/generate-weekly-report.py --since 2026-04-27
"""
import json
import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Auto-detect repo root relative to this script
SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR / ".."
OPERATIONAL_DIR = REPO_ROOT / "technical-infrastructure" / "wiki" / "operational"
SESSIONS_DIR = OPERATIONAL_DIR / "sessions"
STATUS_DIR = OPERATIONAL_DIR / "status"


def load_jsonl(path: Path):
    """Load all entries from a JSONL file."""
    if not path.exists():
        return []
    logs = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                logs.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return logs


def generate_report(since_date=None):
    """Generate a weekly performance report."""
    routing_logs = load_jsonl(SESSIONS_DIR / "model-routing-decisions.jsonl")
    dispatch_logs = load_jsonl(SESSIONS_DIR / "model-dispatch-events.jsonl")
    
    # Filter by date if specified
    if since_date:
        routing_logs = [l for l in routing_logs if l.get("timestamp", "") >= since_date]
        dispatch_logs = [l for l in dispatch_logs if l.get("timestamp", "") >= since_date]
    
    # Routing stats
    by_complexity = {}
    by_model = {}
    total_cost = 0
    total_latency = 0
    
    for log in routing_logs:
        c = log.get("complexity", "UNKNOWN")
        by_complexity.setdefault(c, []).append(log)
        
        model = log.get("model", "unknown")
        by_model.setdefault(model, []).append(log)
        
        total_cost += log.get("cost", 0)
        total_latency += log.get("latency_ms", 0)
    
    # Decomposition stats
    decomps = [l for l in dispatch_logs if l.get("event_type") == "decomposition"]
    decomp_success = sum(1 for d in decomps if d.get("success"))
    decomp_latency = sum(d.get("latency_ms", 0) for d in decomps)
    total_sub_tasks = sum(d.get("sub_task_count", 0) for d in decomps)
    
    # Dispatch stats
    dispatches = [l for l in dispatch_logs if l.get("event_type") == "dispatch"]
    dispatch_success = sum(1 for d in dispatches if d.get("success"))
    dispatch_latency = sum(d.get("latency_ms", 0) for d in dispatches)
    
    # Node usage
    node_counts = {}
    for d in dispatches:
        node = d.get("node", "unknown")
        node_counts[node] = node_counts.get(node, 0) + 1
    
    # Build report
    lines = []
    lines.append(f"# Performance Report — {datetime.now().strftime('%Y-%m-%d')}")
    lines.append(f"\n**Period:** {since_date or 'All time'} to {datetime.now().strftime('%Y-%m-%d')}")
    lines.append(f"**Generated:** {datetime.now().isoformat()}")
    
    lines.append(f"\n## Routing Decisions")
    lines.append(f"- **Total prompts routed:** {len(routing_logs)}")
    lines.append(f"- **Total cost:** ${total_cost:.4f}")
    lines.append(f"- **Avg latency:** {total_latency / max(len(routing_logs), 1):.0f}ms")
    
    for complexity in sorted(by_complexity.keys()):
        entries = by_complexity[complexity]
        avg_latency = sum(e.get("latency_ms", 0) for e in entries) / len(entries)
        cost = sum(e.get("cost", 0) for e in entries)
        models = sorted(set(e.get("model", "unknown") for e in entries))
        lines.append(f"\n### {complexity} ({len(entries)} prompts)")
        lines.append(f"- Avg latency: {avg_latency:.0f}ms")
        lines.append(f"- Total cost: ${cost:.4f}")
        lines.append(f"- Models: {', '.join(models)}")
    
    if by_model:
        lines.append(f"\n### Model Usage")
        for model in sorted(by_model.keys()):
            count = len(by_model[model])
            avg_latency = sum(e.get("latency_ms", 0) for e in by_model[model]) / count
            lines.append(f"- {model}: {count} calls, avg {avg_latency:.0f}ms")
    
    lines.append(f"\n## Decomposition Pipeline")
    lines.append(f"- **Decomposition events:** {len(decomps)}")
    lines.append(f"- **Successful:** {decomp_success}/{len(decomps)}")
    lines.append(f"- **Avg latency:** {decomp_latency / max(len(decomps), 1):.0f}ms")
    lines.append(f"- **Total sub-tasks created:** {total_sub_tasks}")
    
    lines.append(f"\n## Sub-Task Dispatch")
    lines.append(f"- **Dispatch events:** {len(dispatches)}")
    lines.append(f"- **Successful:** {dispatch_success}")
    lines.append(f"- **Failed:** {len(dispatches) - dispatch_success}")
    lines.append(f"- **Avg latency:** {dispatch_latency / max(len(dispatches), 1):.0f}ms")
    
    if node_counts:
        lines.append(f"\n### Node Usage")
        for node, count in sorted(node_counts.items(), key=lambda x: -x[1]):
            lines.append(f"- {node}: {count} tasks")
    
    lines.append(f"\n---")
    lines.append(f"*Report generated by `scripts/generate-weekly-report.py`*")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate weekly performance report")
    parser.add_argument("--since", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--output", help="Output file path")
    args = parser.parse_args()
    
    report = generate_report(args.since)
    
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report)
        print(f"Report written to: {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
