#!/usr/bin/env python3
"""
time_cost_analyzer.py — Analyze time cost vs monetary cost tradeoffs.

Calculates break-even points where waiting for local models costs more
in developer time than the cloud premium would cost in infrastructure.

Usage:
    # Analyze all sessions
    python3 time_cost_analyzer.py

    # Analyze with custom hourly rate
    python3 time_cost_analyzer.py --hourly-rate 150

    # Show break-even analysis
    python3 time_cost_analyzer.py --breakdown

    # Generate decision framework report
    python3 time_cost_analyzer.py --report
"""

import argparse
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

# Default hourly rates by role
HOURLY_RATES = {
    "developer": 100,      # $75-150/hr
    "analyst": 75,         # $50-100/hr
    "executive": 300,      # $200-500/hr
    "default": 100
}


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


def estimate_response_time(model: str, tokens: int) -> float:
    """
    Estimate response time in seconds based on model and token count.
    
    Based on TI-016 benchmarking data:
    - Small local (4b): ~50 tokens/sec
    - Medium local (8b): ~30 tokens/sec
    - Large local (31b+): ~15 tokens/sec
    - Cloud models: ~100 tokens/sec
    """
    model_lower = model.lower()
    
    # Cloud models (faster)
    if "cloud" in model_lower or "glm" in model_lower or "deepseek" in model_lower:
        tps = 100  # tokens per second
    # Large local models
    elif "31b" in model_lower or "70b" in model_lower:
        tps = 15
    # Medium local models
    elif "8b" in model_lower or "14b" in model_lower:
        tps = 30
    # Small local models
    else:
        tps = 50
    
    return tokens / tps


def calculate_time_cost(entry: dict, hourly_rate: float) -> dict:
    """Calculate time cost for a single cost log entry."""
    model = entry.get("model", "unknown")
    input_tokens = entry.get("input_tokens", 0)
    output_tokens = entry.get("output_tokens", 0)
    total_tokens = input_tokens + output_tokens
    cost_usd = entry.get("cost_usd", 0)
    
    # Estimate response time (output tokens determine wait time)
    response_time_sec = estimate_response_time(model, output_tokens)
    response_time_min = response_time_sec / 60.0
    
    # Calculate time cost
    time_cost = (response_time_min / 60.0) * hourly_rate
    
    # Total cost = monetary + time
    total_cost = cost_usd + time_cost
    
    return {
        "model": model,
        "tokens": total_tokens,
        "response_time_sec": round(response_time_sec, 2),
        "response_time_min": round(response_time_min, 3),
        "monetary_cost": round(cost_usd, 6),
        "time_cost": round(time_cost, 6),
        "total_cost": round(total_cost, 6),
        "time_cost_ratio": round(time_cost / cost_usd if cost_usd > 0 else 0, 2)
    }


def analyze_by_model(entries: list, hourly_rate: float) -> dict:
    """Aggregate analysis by model."""
    by_model = defaultdict(lambda: {
        "count": 0,
        "total_tokens": 0,
        "total_time_sec": 0,
        "total_monetary_cost": 0,
        "total_time_cost": 0,
        "total_cost": 0
    })
    
    for entry in entries:
        analysis = calculate_time_cost(entry, hourly_rate)
        model = analysis["model"]
        
        by_model[model]["count"] += 1
        by_model[model]["total_tokens"] += analysis["tokens"]
        by_model[model]["total_time_sec"] += analysis["response_time_sec"]
        by_model[model]["total_monetary_cost"] += analysis["monetary_cost"]
        by_model[model]["total_time_cost"] += analysis["time_cost"]
        by_model[model]["total_cost"] += analysis["total_cost"]
    
    # Calculate averages
    for model, data in by_model.items():
        if data["count"] > 0:
            data["avg_time_sec"] = round(data["total_time_sec"] / data["count"], 2)
            data["avg_monetary_cost"] = round(data["total_monetary_cost"] / data["count"], 6)
            data["avg_time_cost"] = round(data["total_time_cost"] / data["count"], 6)
            data["time_cost_pct"] = round(
                (data["total_time_cost"] / data["total_cost"] * 100) if data["total_cost"] > 0 else 0, 1
            )
    
    return dict(by_model)


def break_even_analysis(hourly_rate: float) -> dict:
    """
    Calculate break-even points where time cost equals monetary cost premium.
    
    Returns break-even response times for different scenarios.
    """
    # Cloud premium costs ~$0.05/1K tokens (kimi-k2.6)
    # Local standard costs ~$0.006/1K tokens (qwen3:8b)
    # Premium = $0.044/1K tokens difference
    
    cloud_premium_per_1k = 0.050
    local_standard_per_1k = 0.006
    premium_difference = cloud_premium_per_1k - local_standard_per_1k
    
    # Break-even: time_cost = premium_difference
    # time_cost = (response_time_min / 60) * hourly_rate
    # response_time_min = (premium_difference * 60) / hourly_rate * tokens/1000
    
    results = {
        "hourly_rate": hourly_rate,
        "cloud_premium_per_1k": cloud_premium_per_1k,
        "local_standard_per_1k": local_standard_per_1k,
        "premium_difference_per_1k": premium_difference,
        "break_even_by_tokens": {}
    }
    
    # Calculate for different token counts
    for tokens in [1000, 5000, 10000, 50000, 100000]:
        premium_cost = (tokens / 1000) * premium_difference
        break_even_min = (premium_cost * 60) / hourly_rate
        break_even_sec = break_even_min * 60
        
        results["break_even_by_tokens"][tokens] = {
            "premium_cost_usd": round(premium_cost, 4),
            "break_even_minutes": round(break_even_min, 2),
            "break_even_seconds": round(break_even_sec, 1)
        }
    
    return results


def generate_decision_framework(break_even: dict) -> str:
    """Generate a decision framework quick reference."""
    hourly_rate = break_even["hourly_rate"]
    
    framework = f"""
# Time-Cost Decision Framework

**Assumptions:**
- Your hourly rate: ${hourly_rate}/hr
- Cloud Premium (kimi-k2.6): ${break_even['cloud_premium_per_1k']}/1K tokens
- Local Standard (qwen3:8b): ${break_even['local_standard_per_1k']}/1K tokens
- Premium difference: ${break_even['premium_difference_per_1k']}/1K tokens

---

## Quick Decision Card

| Scenario | Time Pressure | Recommended Model | Rationale |
|----------|--------------|-------------------|-----------|
| **URGENT** | < 5 min deadline | Cloud Premium | Time cost >> monetary savings |
| **IMPORTANT** | < 1 hr deadline | Cloud Standard | Balance of speed and cost |
| **ANALYTICAL** | Complex reasoning | Large Local or Cloud Std | Quality over speed |
| **BUDGET** | <$1/day limit | Small Local | Monetary cost priority |
| **PRIVATE** | Sensitive data | Local Only | Privacy over all else |

---

## Break-Even Analysis

When does waiting for local cost more than cloud premium?

| Tokens | Cloud Premium Cost | Break-Even Wait Time |
|--------|-------------------|---------------------|
"""
    
    for tokens, data in sorted(break_even["break_even_by_tokens"].items()):
        framework += f"| {tokens:,} | ${data['premium_cost_usd']:.4f} | {data['break_even_seconds']:.1f} sec ({data['break_even_minutes']:.2f} min) |\n"
    
    framework += f"""
---

## Rules of Thumb

1. **If response > {break_even['break_even_by_tokens'][10000]['break_even_seconds']:.0f} sec** (for 10K tokens)
   → Cloud is cheaper when counting your time

2. **If iteration count > 2**
   → Cloud pays off (fewer retries needed)

3. **If deadline < 5 minutes**
   → Always use cloud

4. **If data is sensitive**
   → Always use local (compliance > cost)

---

*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
    
    return framework


def main():
    parser = argparse.ArgumentParser(description="Analyze time cost vs monetary cost")
    parser.add_argument("--hourly-rate", type=float, default=100,
                        help="Your hourly rate (default: $100)")
    parser.add_argument("--breakdown", action="store_true",
                        help="Show breakdown by model")
    parser.add_argument("--break-even", action="store_true",
                        help="Show break-even analysis")
    parser.add_argument("--report", action="store_true",
                        help="Generate full decision framework report")
    args = parser.parse_args()
    
    # Load cost log
    print(f"Loading cost audit log...")
    entries = load_cost_log()
    print(f"Loaded {len(entries):,} entries")
    
    # Analyze by model
    if args.breakdown:
        print(f"\n=== Analysis by Model (Hourly Rate: ${args.hourly_rate}/hr) ===\n")
        by_model = analyze_by_model(entries, args.hourly_rate)
        
        print(f"{'Model':<30} {'Count':>6} {'Avg Time':>10} {'Monetary':>10} {'Time Cost':>10} {'Time %':>8}")
        print(f"{'':30} {'':6} {'(sec)':>10} {'($)':>10} {'($)':>10} {'of Total':>8}")
        print("-" * 86)
        
        for model, data in sorted(by_model.items(), key=lambda x: x[1]['total_cost'], reverse=True)[:15]:
            print(f"{model:<30} {data['count']:>6,} {data['avg_time_sec']:>10.2f} "
                  f"${data['avg_monetary_cost']:>8.4f} ${data['avg_time_cost']:>8.4f} {data['time_cost_pct']:>7.1f}%")
    
    # Break-even analysis
    if args.break_even or args.report:
        print(f"\n=== Break-Even Analysis ===\n")
        break_even = break_even_analysis(args.hourly_rate)
        
        print(f"Cloud Premium: ${break_even['cloud_premium_per_1k']}/1K tokens")
        print(f"Local Standard: ${break_even['local_standard_per_1k']}/1K tokens")
        print(f"Premium Difference: ${break_even['premium_difference_per_1k']}/1K tokens\n")
        
        print(f"Break-even wait time (when time cost = premium cost):")
        print(f"{'Tokens':>10} {'Premium Cost':>15} {'Break-Even Time':>20}")
        print("-" * 48)
        
        for tokens, data in sorted(break_even["break_even_by_tokens"].items()):
            print(f"{tokens:>10,} ${data['premium_cost_usd']:>12.4f} {data['break_even_seconds']:>8.1f} sec ({data['break_even_minutes']:.2f} min)")
    
    # Generate report
    if args.report:
        break_even = break_even_analysis(args.hourly_rate)
        report = generate_decision_framework(break_even)
        
        # Save report
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        report_path = OUTPUT_DIR / "time-cost-decision-framework.md"
        with open(report_path, 'w') as f:
            f.write(report)
        
        print(f"\n✓ Decision framework saved to: {report_path}")
        print("\n" + "=" * 60)
        print(report)
        print("=" * 60)


if __name__ == "__main__":
    main()
