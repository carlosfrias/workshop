#!/usr/bin/env python3
"""
performance_logger.py — Log model routing decisions for cost/quality analysis
Part of Phase 1 Meta-Orchestration Framework

Usage:
    # Log a routing decision
    python3 performance_logger.py --log --prompt "Check if fnet2 is online" --complexity TRIVIAL --model qwen3.5:4b --latency 200 --cost 0

    # View weekly report
    python3 performance_logger.py --report

    # View all logs
    python3 performance_logger.py --list
"""
import json, os, sys, argparse, time
from datetime import datetime
from pathlib import Path

# Auto-detect repo root relative to this script
SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR / "../../"
OPERATIONAL_DIR = REPO_ROOT / "technical-infrastructure" / "wiki" / "operational"
SESSIONS_DIR = OPERATIONAL_DIR / "sessions"
STATUS_DIR = OPERATIONAL_DIR / "status"

LOG_FILE = SESSIONS_DIR / "model-performance-log.json"
JSONL_FILE = SESSIONS_DIR / "model-routing-decisions.jsonl"
DISPATCH_JSONL = SESSIONS_DIR / "model-dispatch-events.jsonl"


def log_retrieval(query: str, results_count: int, latency_ms: int, top_domain: str = "", top_distance: float = 0.0):
    """Log a RAG retrieval event."""
    event = {
        "timestamp": datetime.now().isoformat(),
        "event_type": "rag_retrieval",
        "query": query[:500],  # Truncate long queries
        "results_count": results_count,
        "latency_ms": latency_ms,
        "top_domain": top_domain,
        "top_distance": round(top_distance, 4),
    }
    _append_log(ROUTING_LOG, event)
    # Also append to a dedicated retrieval log
    retrieval_log = os.path.join(SESSIONS_DIR, "rag-retrievals.jsonl")
    _append_log(retrieval_log, event)


def log_routing_decision(prompt, complexity, model, latency_ms, cost=0, quality="", adequate="", node="orchestrator", provider="ollama"):
    """Log a routing decision to the performance database."""
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "prompt_preview": prompt[:200],
        "complexity": complexity.upper(),
        "model": model,
        "provider": provider,
        "node": node,
        "latency_ms": int(latency_ms),
        "cost": float(cost),
        "quality": quality,
        "adequate": adequate,
    }
    
    # Write to JSONL (append)
    with open(JSONL_FILE, 'a') as f:
        f.write(json.dumps(entry) + "\n")
    
    # Also update legacy JSON (merge + dedupe)
    _update_legacy_json(entry)
    
    return entry


def log_decomposition(trigger_id: str, prompt: str, sub_task_count: int, latency_ms: int, model_used: str = "unknown", provider: str = "unknown", success: bool = True, error: str = ""):
    """Log a decomposition event (trigger → sub-tasks)."""
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event_type": "decomposition",
        "trigger_id": trigger_id,
        "prompt_preview": prompt[:200],
        "sub_task_count": sub_task_count,
        "latency_ms": int(latency_ms),
        "model_used": model_used,
        "provider": provider,
        "success": success,
        "error": error,
    }
    
    with open(DISPATCH_JSONL, 'a') as f:
        f.write(json.dumps(entry) + "\n")
    
    return entry


def log_dispatch(trigger_id: str, sub_task_id: str, node: str, model: str, latency_ms: int, success: bool = True, error: str = "", provider: str = "ollama"):
    """Log a sub-task dispatch event."""
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event_type": "dispatch",
        "trigger_id": trigger_id,
        "sub_task_id": sub_task_id,
        "node": node,
        "model": model,
        "provider": provider,
        "latency_ms": int(latency_ms),
        "success": success,
        "error": error,
    }
    
    with open(DISPATCH_JSONL, 'a') as f:
        f.write(json.dumps(entry) + "\n")
    
    return entry

def _update_legacy_json(entry):
    """Merge JSONL entries into the legacy JSON file for backward compatibility."""
    legacy_path = Path(LOG_FILE)
    legacy_path.parent.mkdir(parents=True, exist_ok=True)
    
    if legacy_path.exists():
        with open(legacy_path) as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
    else:
        logs = []
    
    logs.append({
        "timestamp": entry["timestamp"],
        "prompt": entry["prompt_preview"],
        "complexity": entry["complexity"],
        "model": f"{entry['provider']}/{entry['model']}",
        "latency_ms": entry["latency_ms"],
        "cost": entry["cost"],
        "quality": entry.get("quality", ""),
        "adequate": entry.get("adequate", ""),
    })
    
    with open(legacy_path, 'w') as f:
        json.dump(logs, f, indent=2)


def ensure_log():
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    legacy = Path(LOG_FILE)
    if not legacy.exists():
        with open(legacy, 'w') as f:
            json.dump([], f)

def load_jsonl():
    """Load all entries from the JSONL log file."""
    if not JSONL_FILE.exists():
        return []
    logs = []
    with open(JSONL_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                logs.append({
                    "timestamp": entry.get("timestamp", ""),
                    "prompt": entry.get("prompt_preview", ""),
                    "complexity": entry.get("complexity", "UNKNOWN").upper(),
                    "model": f"{entry.get('provider', 'unknown')}/{entry.get('model', 'unknown')}",
                    "latency_ms": entry.get("latency_ms", 0),
                    "cost": entry.get("cost", 0),
                    "quality": entry.get("quality", ""),
                    "adequate": entry.get("adequate", ""),
                })
            except json.JSONDecodeError:
                continue
    return logs


def merge_logs():
    ensure_log()
    with open(LOG_FILE) as f:
        legacy = json.load(f)
    jsonl = load_jsonl()
    
    # Merge and deduplicate by timestamp
    seen = set()
    merged = []
    for log in jsonl + legacy:
        ts = log.get("timestamp", "")
        if ts and ts not in seen:
            seen.add(ts)
            merged.append(log)
    
    return merged

def ensure_log():
    if not os.path.exists(LOG_FILE):
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, 'w') as f:
            json.dump([], f)

def log_entry(prompt, complexity, model, latency_ms, cost, quality="", adequate=""):
    ensure_log()
    with open(LOG_FILE) as f:
        logs = json.load(f)
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt[:200],
        "complexity": complexity,
        "model": model,
        "latency_ms": latency_ms,
        "cost": cost,
        "quality": quality,
        "adequate": adequate,
    }
    logs.append(entry)
    
    with open(LOG_FILE, 'w') as f:
        json.dump(logs, f, indent=2)
    
    return entry

def list_logs(limit=20):
    return merge_logs()[-limit:]

def weekly_report():
    logs = merge_logs()
    dispatches = load_dispatch_jsonl()
    
    if not logs and not dispatches:
        return "No logs yet. Extension writes to model-routing-decisions.jsonl automatically.\nUse --log to add manual entries."
    
    # Group by complexity
    by_complexity = {}
    for log in logs:
        c = log.get("complexity", "UNKNOWN")
        if c not in by_complexity:
            by_complexity[c] = []
        by_complexity[c].append(log)
    
    # Dispatch stats
    dispatch_success = sum(1 for d in dispatches if d.get("success"))
    dispatch_total = len(dispatches)
    dispatch_failures = dispatch_total - dispatch_success
    avg_dispatch_latency = sum(d.get("latency_ms", 0) for d in dispatches) / max(dispatch_total, 1)
    
    # Decomposition stats
    decomps = [d for d in dispatches if d.get("event_type") == "decomposition"]
    decomp_success = sum(1 for d in decomps if d.get("success"))
    avg_decomp_latency = sum(d.get("latency_ms", 0) for d in decomps) / max(len(decomps), 1)
    total_sub_tasks = sum(d.get("sub_task_count", 0) for d in decomps)
    
    # Node usage
    node_counts = {}
    for d in dispatches:
        if d.get("event_type") == "dispatch":
            node = d.get("node", "unknown")
            node_counts[node] = node_counts.get(node, 0) + 1
    
    report = []
    report.append(f"# Performance Report — {datetime.now().strftime('%Y-%m-%d')}")
    report.append(f"\n## Routing Decisions")
    report.append(f"Total prompts: {len(logs)}")
    
    for complexity, entries in sorted(by_complexity.items()):
        avg_latency = sum(e.get("latency_ms", 0) for e in entries) / len(entries)
        total_cost = sum(e.get("cost", 0) for e in entries)
        models = set(e.get("model", "unknown") for e in entries)
        report.append(f"\n### {complexity} ({len(entries)} prompts)")
        report.append(f"- Avg latency: {avg_latency:.0f}ms")
        report.append(f"- Total cost: ${total_cost:.4f}")
        report.append(f"- Models: {', '.join(sorted(models))}")
    
    report.append(f"\n## Decomposition Pipeline")
    report.append(f"- Decomposition events: {len(decomps)}")
    report.append(f"- Decomposition success: {decomp_success}/{len(decomps)}")
    report.append(f"- Avg decomposition latency: {avg_decomp_latency:.0f}ms")
    report.append(f"- Total sub-tasks created: {total_sub_tasks}")
    
    report.append(f"\n## Sub-Task Dispatch")
    report.append(f"- Dispatch events: {dispatch_total}")
    report.append(f"- Successful: {dispatch_success}")
    report.append(f"- Failed: {dispatch_failures}")
    report.append(f"- Avg dispatch latency: {avg_dispatch_latency:.0f}ms")
    
    if node_counts:
        report.append(f"\n### Node Usage")
        for node, count in sorted(node_counts.items(), key=lambda x: -x[1]):
            report.append(f"- {node}: {count} tasks")
    
    return "\n".join(report)


def load_dispatch_jsonl():
    """Load all entries from the dispatch JSONL log file."""
    if not DISPATCH_JSONL.exists():
        return []
    logs = []
    with open(DISPATCH_JSONL) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                logs.append(entry)
            except json.JSONDecodeError:
                continue
    return logs

def main():
    parser = argparse.ArgumentParser(description="Performance logger for model routing")
    parser.add_argument("--log", action="store_true", help="Log a new entry")
    parser.add_argument("--prompt", help="The prompt text")
    parser.add_argument("--complexity", help="Classified complexity")
    parser.add_argument("--model", help="Model used")
    parser.add_argument("--latency", type=int, help="Latency in ms")
    parser.add_argument("--cost", type=float, default=0, help="Cost in USD")
    parser.add_argument("--quality", default="", help="Quality assessment")
    parser.add_argument("--adequate", default="", help="Adequacy assessment")
    parser.add_argument("--report", action="store_true", help="Show weekly report")
    parser.add_argument("--list", action="store_true", help="List recent logs")
    args = parser.parse_args()
    
    if args.log:
        if not all([args.prompt, args.complexity, args.model, args.latency is not None]):
            print("Required: --prompt, --complexity, --model, --latency", file=sys.stderr)
            sys.exit(1)
        entry = log_entry(args.prompt, args.complexity, args.model, args.latency, args.cost, args.quality, args.adequate)
        print(f"Logged: {entry['timestamp']} {entry['complexity']} → {entry['model']} ({entry['latency_ms']}ms)")
    elif args.report:
        print(weekly_report())
    elif args.list:
        logs = list_logs()
        print(f"Recent {len(logs)} logs:")
        for log in logs:
            print(f"  {log['timestamp'][:19]} | {log['complexity']:<8} | {log['model']:<25} | {log['latency_ms']}ms | ${log['cost']}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
