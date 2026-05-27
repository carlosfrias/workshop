#!/usr/bin/env python3
"""
time_tax_report.py — Report on "time tax" paid when choosing cheaper/slower models.

The "time tax" is the difference between your time cost and the monetary savings
from choosing a slower/cheaper model.

Usage:
    # Report time tax for all sessions
    python3 time_tax_report.py

    # Report with custom hourly rate
    python3 time_tax_report.py --hourly-rate 150

    # Show time tax by model
    python3 time_tax_report.py --by-model

    # Export to CSV
    python3 time_tax_report.py --export time-tax-report.csv
"""

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Project paths
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
COST_LOG_PATH = DATA_DIR / "cost-audit-log.jsonl"
OUTPUT_DIR = PROJECT_ROOT / "analysis"

# Reference: fastest cloud model baseline (kimi-k2.6:cloud ~100 tokens/sec)
BASELINE_TPS = 100


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


def estimate_response_time(model: str, output_tokens: int) -> float:
    """Estimate response time in seconds based on model."""
    model_lower = model.lower()
    
    # Cloud models (fast)
    if "cloud" in model_lower or "glm" in model_lower or "deepseek" in model_lower or "kimi" in model_lower:
        tps = 100
    # Large local models
    elif "31b" in model_lower or "70b" in model_lower or "397b" in model_lower:
        tps = 15
    # Medium local models
    elif "8b" in model_lower or "14b" in model_lower:
        tps = 30
    # Small local models
    else:
        tps = 50
    
    return output_tokens / tps


def calculate_time_tax(entry: dict, hourly_rate: float) -> dict:
    """
    Calculate time tax for a single entry.
    
    Time tax = (actual_time_cost - baseline_time_cost) + monetary_savings_lost
    
    Where baseline is the fastest cloud model (kimi-k2.6).
    """
    model = entry.get("model", "unknown")
    output_tokens = entry.get("output_tokens", 0)
    cost_usd = entry.get("cost_usd", 0)
    
    # Actual response time and time cost
    actual_time_sec = estimate_response_time(model, output_tokens)
    actual_time_cost = (actual_time_sec / 3600.0) * hourly_rate
    
    # Baseline (fastest cloud) time and cost
    baseline_time_sec = output_tokens / BASELINE_TPS
    baseline_time_cost = (baseline_time_sec / 3600.0) * hourly_rate
    
    # Monetary cost difference (vs cloud premium)
    cloud_premium_per_1k = 0.050
    baseline_cost = (output_tokens / 1000) * cloud_premium_per_1k
    monetary_savings = baseline_cost - cost_usd  # positive if local is cheaper
    
    # Time tax = extra time cost - monetary savings
    extra_time_cost = actual_time_cost - baseline_time_cost
    time_tax = extra_time_cost - monetary_savings
    
    return {
        "timestamp": entry.get("timestamp", ""),
        "session_id": entry.get("session_id", ""),
        "model": model,
        "output_tokens": output_tokens,
        "actual_time_sec": round(actual_time_sec, 2),
        "baseline_time_sec": round(baseline_time_sec, 2),
        "time_lost_sec": round(actual_time_sec - baseline_time_sec, 2),
        "monetary_cost": round(cost_usd, 6),
        "baseline_monetary_cost": round(baseline_cost, 6),
        "monetary_savings": round(monetary_savings, 6),
        "actual_time_cost": round(actual_time_cost, 6),
        "baseline_time_cost": round(baseline_time_cost, 6),
        "extra_time_cost": round(extra_time_cost, 6),
        "time_tax": round(time_tax, 6),
        "time_tax_ratio": round(time_tax / cost_usd if cost_usd > 0 else 0, 2)
    }


def aggregate_time_tax(entries: list, hourly_rate: float) -> dict:
    """Aggregate time tax across all entries."""
    total = {
        "total_entries": len(entries),
        "total_output_tokens": 0,
        "total_time_lost_sec": 0,
        "total_monetary_cost": 0,
        "total_baseline_cost": 0,
        "total_monetary_savings": 0,
        "total_extra_time_cost": 0,
        "total_time_tax": 0
    }
    
    by_model = defaultdict(lambda: {
        "count": 0,
        "total_time_tax": 0,
        "total_monetary_savings": 0,
        "net_cost": 0
    })
    
    for entry in entries:
        tax = calculate_time_tax(entry, hourly_rate)
        
        total["total_output_tokens"] += tax["output_tokens"]
        total["total_time_lost_sec"] += tax["time_lost_sec"]
        total["total_monetary_cost"] += tax["monetary_cost"]
        total["total_baseline_cost"] += tax["baseline_monetary_cost"]
        total["total_monetary_savings"] += tax["monetary_savings"]
        total["total_extra_time_cost"] += tax["extra_time_cost"]
        total["total_time_tax"] += tax["time_tax"]
        
        model = tax["model"]
        by_model[model]["count"] += 1
        by_model[model]["total_time_tax"] += tax["time_tax"]
        by_model[model]["total_monetary_savings"] += tax["monetary_savings"]
        by_model[model]["net_cost"] += tax["time_tax"] - tax["monetary_savings"]
    
    # Averages
    total["avg_time_tax_per_request"] = total["total_time_tax"] / total["total_entries"] if total["total_entries"] > 0 else 0
    total["total_time_lost_min"] = total["total_time_lost_sec"] / 60.0
    total["total_time_lost_hr"] = total["total_time_lost_sec"] / 3600.0
    total["time_tax_value"] = total["total_time_lost_hr"] * hourly_rate
    
    for model, data in by_model.items():
        data["avg_time_tax"] = data["total_time_tax"] / data["count"] if data["count"] > 0 else 0
        data["net_benefit"] = data["total_monetary_savings"] - data["total_time_tax"]
    
    return {
        "total": total,
        "by_model": dict(by_model)
    }


def print_summary(agg: dict, hourly_rate: float):
    """Print time tax summary."""
    t = agg["total"]
    
    print(f"\n{'='*70}")
    print(f"TIME TAX REPORT (Hourly Rate: ${hourly_rate}/hr)")
    print(f"{'='*70}\n")
    
    print(f"Total Requests Analyzed: {t['total_entries']:,}")
    print(f"Total Output Tokens: {t['total_output_tokens']:,}")
    print()
    
    print(f"MONETARY COSTS:")
    print(f"  Actual spend:           ${t['total_monetary_cost']:>10.4f}")
    print(f"  Baseline (cloud prem):  ${t['total_baseline_cost']:>10.4f}")
    print(f"  Monetary savings:       ${t['total_monetary_savings']:>10.4f}")
    print()
    
    print(f"TIME COSTS:")
    print(f"  Time lost:              {t['total_time_lost_sec']:>10.1f} sec ({t['total_time_lost_min']:.1f} min / {t['total_time_lost_hr']:.2f} hr)")
    print(f"  Extra time cost:        ${t['total_extra_time_cost']:>10.4f}")
    print(f"  Time tax value:         ${t['time_tax_value']:>10.4f}")
    print()
    
    print(f"NET RESULT:")
    net_position = t['total_monetary_savings'] - t['total_extra_time_cost']
    print(f"  Monetary savings:       ${t['total_monetary_savings']:>10.4f}")
    print(f"  Less extra time cost:  -${t['total_extra_time_cost']:>9.4f}")
    print(f"  ──────────────────────────────────────")
    print(f"  Net position:           ${net_position:>10.4f} {'(LOSS)' if net_position < 0 else '(GAIN)'}")
    print()
    
    print(f"  Average time tax per request: ${t['avg_time_tax_per_request']:.4f}")
    print(f"  Time tax as % of spend: {(t['total_extra_time_cost'] / t['total_monetary_cost'] * 100) if t['total_monetary_cost'] > 0 else 0:.1f}%")
    print()


def print_by_model(agg: dict):
    """Print time tax breakdown by model."""
    print(f"\n{'='*70}")
    print(f"TIME TAX BY MODEL")
    print(f"{'='*70}\n")
    
    print(f"{'Model':<30} {'Count':>6} {'Time Tax':>12} {'Savings':>12} {'Net':>12}")
    print(f"{'':30} {'':6} {'(paid)':>12} {'(kept)':>12} {'Benefit':>12}")
    print("-" * 74)
    
    for model, data in sorted(agg["by_model"].items(), key=lambda x: x[1]['net_benefit'], reverse=True):
        net = data['net_benefit']
        net_str = f"${net:>10.4f}" + (" ✓" if net > 0 else "")
        print(f"{model:<30} {data['count']:>6,} ${data['total_time_tax']:>10.4f} ${data['total_monetary_savings']:>10.4f} {net_str}")
    
    print()


def export_to_csv(agg: dict, output_path: Path):
    """Export time tax data to CSV."""
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Model', 'Requests', 'Total Time Tax', 'Total Savings', 'Net Benefit', 'Avg Time Tax'])
        
        for model, data in sorted(agg["by_model"].items(), key=lambda x: x[1]['net_benefit'], reverse=True):
            writer.writerow([
                model,
                data['count'],
                f"{data['total_time_tax']:.4f}",
                f"{data['total_monetary_savings']:.4f}",
                f"{data['net_benefit']:.4f}",
                f"{data['avg_time_tax']:.4f}"
            ])
    
    print(f"✓ Exported to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Report on time tax paid for cheaper models")
    parser.add_argument("--hourly-rate", type=float, default=100,
                        help="Your hourly rate (default: $100)")
    parser.add_argument("--by-model", action="store_true",
                        help="Show breakdown by model")
    parser.add_argument("--export", type=Path,
                        help="Export to CSV file")
    args = parser.parse_args()
    
    # Load cost log
    print(f"Loading cost audit log...")
    entries = load_cost_log()
    print(f"Loaded {len(entries):,} entries")
    
    # Aggregate
    agg = aggregate_time_tax(entries, args.hourly_rate)
    
    # Print summary
    print_summary(agg, args.hourly_rate)
    
    # Print by model
    if args.by_model:
        print_by_model(agg)
    
    # Export
    if args.export:
        export_to_csv(agg, args.export)


if __name__ == "__main__":
    main()
