#!/usr/bin/env python3
"""
usage_tracker.py — Aggregate customer usage from cost audit log.

Reads the persistent cost audit log (JSONL) and aggregates usage by customer/account.
Outputs to customer-usage.jsonl for invoice generation.

Usage:
    # Aggregate all usage
    python3 usage_tracker.py

    # Aggregate for specific month
    python3 usage_tracker.py --month 2026-05

    # Show customer summary
    python3 usage_tracker.py --summary
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# Project paths
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
COST_LOG_PATH = DATA_DIR / "cost-audit-log.jsonl"
USAGE_OUTPUT_PATH = DATA_DIR / "customer-usage.jsonl"


def load_cost_log(log_path: Path = None) -> list:
    """Load cost audit log entries."""
    if log_path is None:
        log_path = COST_LOG_PATH
    
    if not log_path.exists():
        print(f"Error: Cost log not found at {log_path}")
        sys.exit(1)
    
    entries = []
    with open(log_path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


def aggregate_by_customer(entries: list, month: str = None) -> dict:
    """
    Aggregate cost entries by customer/account.
    
    Args:
        entries: List of cost audit log entries
        month: Filter by month (YYYY-MM format)
    
    Returns:
        Dict of customer_id → aggregated usage data
    """
    customers = defaultdict(lambda: {
        "customer_id": None,
        "total_cost": 0.0,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "total_tasks": 0,
        "models_used": defaultdict(int),
        "first_use": None,
        "last_use": None,
        "entries": []
    })
    
    for entry in entries:
        # Filter by month if specified
        if month:
            entry_date = entry.get("timestamp", "")[:7]  # YYYY-MM
            if entry_date != month:
                continue
        
        # Use session_id as customer proxy (no customer_id in current log format)
        customer_id = entry.get("session_id", "unknown")
        cost = float(entry.get("cost_usd", 0))
        input_tokens = int(entry.get("input_tokens", 0))
        output_tokens = int(entry.get("output_tokens", 0))
        model = entry.get("model", "unknown")
        timestamp = entry.get("timestamp", "")
        
        cust = customers[customer_id]
        cust["customer_id"] = customer_id
        cust["total_cost"] += cost
        cust["total_input_tokens"] += input_tokens
        cust["total_output_tokens"] += output_tokens
        cust["total_tasks"] += 1
        cust["models_used"][model] += 1
        
        if cust["first_use"] is None or timestamp < cust["first_use"]:
            cust["first_use"] = timestamp
        if cust["last_use"] is None or timestamp > cust["last_use"]:
            cust["last_use"] = timestamp
        
        cust["entries"].append(entry)
    
    return dict(customers)


def write_usage_file(customers: dict, output_path: Path = None):
    """Write aggregated usage to JSONL file."""
    if output_path is None:
        output_path = USAGE_OUTPUT_PATH
    
    # Ensure parent directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        for customer_id, data in sorted(customers.items()):
            # Convert defaultdict to regular dict for JSON serialization
            output = {
                "customer_id": data["customer_id"],
                "total_cost": round(data["total_cost"], 6),
                "total_input_tokens": data["total_input_tokens"],
                "total_output_tokens": data["total_output_tokens"],
                "total_tasks": data["total_tasks"],
                "models_used": dict(data["models_used"]),
                "first_use": data["first_use"],
                "last_use": data["last_use"],
                "generated_at": datetime.now().isoformat()
            }
            f.write(json.dumps(output) + '\n')
    
    return output_path


def show_summary(customers: dict):
    """Display customer usage summary."""
    if not customers:
        print("No customer data found.")
        return
    
    print(f"\n{'Customer':<20} {'Tasks':>8} {'Input':>12} {'Output':>12} {'Cost':>10}")
    print(f"{'':20} {'':8} {'Tokens':>12} {'Tokens':>12} {'(USD)':>10}")
    print("-" * 64)
    
    total_cost = 0
    total_tasks = 0
    total_input = 0
    total_output = 0
    
    for customer_id, data in sorted(customers.items()):
        print(f"{customer_id:<20} {data['total_tasks']:>8,} "
              f"{data['total_input_tokens']:>12,} {data['total_output_tokens']:>12,} "
              f"${data['total_cost']:>8.4f}")
        
        total_cost += data["total_cost"]
        total_tasks += data["total_tasks"]
        total_input += data["total_input_tokens"]
        total_output += data["total_output_tokens"]
    
    print("-" * 64)
    print(f"{'TOTAL':<20} {total_tasks:>8,} {total_input:>12,} {total_output:>12,} ${total_cost:>8.4f}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Aggregate customer usage from cost audit log")
    parser.add_argument("--month", help="Filter by month (YYYY-MM format)")
    parser.add_argument("--summary", action="store_true", help="Show customer summary")
    parser.add_argument("--output", type=Path, help="Output file path")
    args = parser.parse_args()
    
    # Load cost log
    print(f"Loading cost audit log from {COST_LOG_PATH}...")
    entries = load_cost_log()
    print(f"Loaded {len(entries):,} entries")
    
    # Aggregate by customer
    if args.month:
        print(f"Filtering for month: {args.month}")
    customers = aggregate_by_customer(entries, month=args.month)
    print(f"Found {len(customers):,} customer(s)")
    
    # Show summary if requested
    if args.summary:
        show_summary(customers)
    
    # Write usage file
    output_path = args.output or USAGE_OUTPUT_PATH
    if args.month:
        # Include month in output filename
        output_path = DATA_DIR / f"customer-usage-{args.month}.jsonl"
    
    write_usage_file(customers, output_path)
    print(f"Wrote usage data to {output_path}")


if __name__ == "__main__":
    main()
