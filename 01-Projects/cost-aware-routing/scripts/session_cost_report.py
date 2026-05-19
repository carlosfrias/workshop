#!/usr/bin/env python3
"""
session_cost_report.py — Parse pi session JSONL files and aggregate costs.

Reads pi's native session JSONL files and produces cost summaries by model,
provider, and session. Works with the cost data populated from models.json
billing tier prices (TI-018).

Usage:
    # Report current session
    python3 session_cost_report.py

    # Report a specific session
    python3 session_cost_report.py --session /path/to/session.jsonl

    # Report all sessions
    python3 session_cost_report.py --all

    # Export to persistent cost log (append-only JSONL)
    python3 session_cost_report.py --export

    # Show running totals from persistent cost log
    python3 session_cost_report.py --totals
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Project paths
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
COST_LOG_DIR = PROJECT_ROOT / "data"
COST_LOG_PATH = COST_LOG_DIR / "cost-audit-log.jsonl"

# Default session directory
DEFAULT_SESSION_DIR = Path.home() / ".pi" / "agent" / "sessions"

# Try project-local session dir first
PROJECT_SESSION_DIR = Path(os.environ.get("PI_SESSION_DIR", ".pi/sessions"))


def find_session_dir() -> Path:
    """Find the active pi session directory."""
    # Check project-local first
    cwd_sessions = Path.cwd() / ".pi" / "sessions"
    if cwd_sessions.exists():
        return cwd_sessions
    # Fall back to global
    if DEFAULT_SESSION_DIR.exists():
        return DEFAULT_SESSION_DIR
    raise FileNotFoundError("No pi session directory found")


def find_latest_session(session_dir: Path = None) -> Path:
    """Find the most recently modified session JSONL."""
    if session_dir is None:
        session_dir = find_session_dir()
    jsonl_files = list(session_dir.glob("*.jsonl"))
    if not jsonl_files:
        raise FileNotFoundError(f"No session files in {session_dir}")
    return max(jsonl_files, key=lambda p: p.stat().st_mtime)


def parse_session(session_path: Path) -> dict:
    """Parse a pi session JSONL and extract cost data."""
    entries = []
    total_cost = 0.0
    total_input_tokens = 0
    total_output_tokens = 0
    by_model = {}
    session_id = None
    session_start = None
    current_model = "unknown"
    current_provider = "unknown"

    with open(session_path) as f:
        for line in f:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue

            if d.get("type") == "session":
                session_id = d.get("id", "unknown")
                session_start = d.get("timestamp", "unknown")

            if d.get("type") == "model_change":
                current_provider = d.get("provider", "unknown")
                current_model = d.get("modelId", "unknown")

            if d.get("type") == "message":
                msg = d.get("message", {})
                usage = msg.get("usage", {})
                if usage and msg.get("role") == "assistant":
                    cost_obj = usage.get("cost", {})
                    cost = float(cost_obj.get("total", 0))
                    input_tokens = int(usage.get("input", 0))
                    output_tokens = int(usage.get("output", 0))

                    entry = {
                        "timestamp": d.get("timestamp", ""),
                        "model": current_model,
                        "provider": current_provider,
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "total_tokens": input_tokens + output_tokens,
                        "cost_usd": cost,
                        "cost_input": float(cost_obj.get("input", 0)),
                        "cost_output": float(cost_obj.get("output", 0)),
                        "cache_read_tokens": int(usage.get("cacheRead", 0)),
                        "cache_write_tokens": int(usage.get("cacheWrite", 0)),
                    }
                    entries.append(entry)

                    total_cost += cost
                    total_input_tokens += input_tokens
                    total_output_tokens += output_tokens

                    if current_model not in by_model:
                        by_model[current_model] = {
                            "provider": current_provider,
                            "turns": 0,
                            "input_tokens": 0,
                            "output_tokens": 0,
                            "cost_usd": 0.0,
                        }
                    by_model[current_model]["turns"] += 1
                    by_model[current_model]["input_tokens"] += input_tokens
                    by_model[current_model]["output_tokens"] += output_tokens
                    by_model[current_model]["cost_usd"] += cost

    return {
        "session_id": session_id,
        "session_start": session_start,
        "session_file": str(session_path),
        "total_cost_usd": total_cost,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "total_turns": len(entries),
        "by_model": by_model,
        "entries": entries,
    }


def format_report(report: dict) -> str:
    """Format a session cost report as readable text."""
    lines = []
    lines.append(f"# Cost Report — Session {report['session_id'][:12]}...")
    lines.append(f"Session start: {report['session_start']}")
    lines.append(f"Session file: {report['session_file']}")
    lines.append("")
    lines.append("## Totals")
    lines.append(f"  Turns:         {report['total_turns']}")
    lines.append(f"  Input tokens:  {report['total_input_tokens']:,}")
    lines.append(f"  Output tokens: {report['total_output_tokens']:,}")
    lines.append(f"  Total cost:    ${report['total_cost_usd']:.4f}")
    lines.append("")

    if report["by_model"]:
        lines.append("## By Model")
        lines.append(f"  {'Model':30s} {'Provider':10s} {'Turns':>5s} {'In':>10s} {'Out':>10s} {'Cost':>10s}")
        lines.append(f"  {'─'*30} {'─'*10} {'─'*5} {'─'*10} {'─'*10} {'─'*10}")
        for model, data in sorted(report["by_model"].items(), key=lambda x: -x[1]["cost_usd"]):
            lines.append(
                f"  {model:30s} {data['provider']:10s} {data['turns']:5d} "
                f"{data['input_tokens']:10,d} {data['output_tokens']:10,d} "
                f"${data['cost_usd']:9.4f}"
            )
        lines.append("")

        # Local vs Cloud breakdown
        local_cost = sum(
            d["cost_usd"] for m, d in report["by_model"].items()
            if ":cloud" not in m and "cloud" not in m.lower()
        )
        cloud_cost = sum(
            d["cost_usd"] for m, d in report["by_model"].items()
            if ":cloud" in m or "cloud" in m.lower()
        )
        lines.append("## Local vs Cloud")
        lines.append(f"  Local:  ${local_cost:.4f}")
        lines.append(f"  Cloud:  ${cloud_cost:.4f}")
        if cloud_cost > 0:
            savings_pct = (1 - local_cost / (local_cost + cloud_cost)) * 100 if (local_cost + cloud_cost) > 0 else 0
            lines.append(f"  Cloud share: {cloud_cost / max(report['total_cost_usd'], 0.01) * 100:.0f}%")

    return "\n".join(lines)


def export_to_cost_log(report: dict) -> int:
    """Export session cost entries to persistent append-only JSONL.
    
    Returns number of entries exported.
    """
    COST_LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Read existing entries to avoid duplicates
    existingKeys = set()
    if COST_LOG_PATH.exists():
        with open(COST_LOG_PATH) as f:
            for line in f:
                try:
                    d = json.loads(line)
                    key = (d.get("session_id", ""), d.get("timestamp", ""), d.get("model", ""))
                    existingKeys.add(key)
                except json.JSONDecodeError:
                    continue

    exported = 0
    with open(COST_LOG_PATH, "a") as f:
        for entry in report["entries"]:
            key = (report["session_id"], entry["timestamp"], entry["model"])
            if key not in existingKeys:
                record = {
                    **entry,
                    "session_id": report["session_id"],
                    "session_start": report["session_start"],
                    "exported_at": datetime.now().isoformat(),
                    "source": "session_cost_report",
                }
                f.write(json.dumps(record) + "\n")
                exported += 1

    return exported


def show_totals() -> str:
    """Show running totals from the persistent cost audit log."""
    if not COST_LOG_PATH.exists():
        return "No cost audit log found at {COST_LOG_PATH}"

    entries = []
    with open(COST_LOG_PATH) as f:
        for line in f:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    if not entries:
        return "Cost audit log is empty"

    total_cost = sum(e.get("cost_usd", 0) for e in entries)
    by_model = {}
    by_session = {}

    for e in entries:
        model = e.get("model", "unknown")
        sid = e.get("session_id", "unknown")[:12]

        if model not in by_model:
            by_model[model] = {"turns": 0, "cost": 0.0}
        by_model[model]["turns"] += 1
        by_model[model]["cost"] += e.get("cost_usd", 0)

        if sid not in by_session:
            by_session[sid] = {"cost": 0.0, "turns": 0}
        by_session[sid]["cost"] += e.get("cost_usd", 0)
        by_session[sid]["turns"] += 1

    lines = []
    lines.append(f"# Cost Audit Log — Running Totals")
    lines.append(f"Log file: {COST_LOG_PATH}")
    lines.append(f"Total entries: {len(entries)}")
    lines.append(f"Total cost: ${total_cost:.4f}")
    lines.append("")
    lines.append("## By Model")
    for model, data in sorted(by_model.items(), key=lambda x: -x[1]["cost"]):
        lines.append(f"  {model:30s} {data['turns']:5d} turns  ${data['cost']:.4f}")
    lines.append("")
    lines.append("## By Session")
    for sid, data in sorted(by_session.items(), key=lambda x: -x[1]["cost"]):
        lines.append(f"  {sid}...  {data['turns']:5d} turns  ${data['cost']:.4f}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Pi session cost report")
    parser.add_argument("--session", help="Path to specific session JSONL")
    parser.add_argument("--all", action="store_true", help="Report all sessions")
    parser.add_argument("--export", action="store_true", help="Export to persistent cost log")
    parser.add_argument("--totals", action="store_true", help="Show running totals from cost log")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.totals:
        print(show_totals())
        return

    if args.export:
        try:
            session_path = Path(args.session) if args.session else find_latest_session()
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        report = parse_session(session_path)
        count = export_to_cost_log(report)
        print(f"Exported {count} cost entries to {COST_LOG_PATH}")
        return

    if args.all:
        try:
            session_dir = find_session_dir()
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        total_cost = 0
        for session_file in sorted(session_dir.glob("*.jsonl")):
            try:
                report = parse_session(session_file)
                if report["total_turns"] > 0:
                    total_cost += report["total_cost_usd"]
                    print(f"  {session_file.name[:40]:40s} {report['total_turns']:5d} turns  ${report['total_cost_usd']:.4f}")
            except Exception as e:
                print(f"  {session_file.name[:40]:40s} ERROR: {e}", file=sys.stderr)
        print(f"\n  Total across all sessions: ${total_cost:.4f}")
        return

    # Default: report latest session
    try:
        session_path = Path(args.session) if args.session else find_latest_session()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    report = parse_session(session_path)
    if args.json:
        print(json.dumps(report, indent=2, default=str))
    else:
        print(format_report(report))


if __name__ == "__main__":
    main()