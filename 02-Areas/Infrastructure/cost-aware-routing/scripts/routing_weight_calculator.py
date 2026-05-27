#!/usr/bin/env python3
"""
routing_weight_calculator.py — Calculate optimal model scores with configurable time-cost weighting.

Supports three modes:
- budget: Minimize monetary cost (accept time tax)
- balanced: Optimize total cost (money + time)
- speed: Minimize wait time (pay cloud premium)

Usage:
    # Score available models for a task
    python3 routing_weight_calculator.py --tokens 10000 --mode balanced

    # Compare all modes
    python3 routing_weight_calculator.py --tokens 10000 --compare

    # Show configuration
    python3 routing_weight_calculator.py --show-config
"""

import argparse
import json
from pathlib import Path
from datetime import datetime

# Project paths
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "routing_weights.json"
TIERS_PATH = PROJECT_ROOT / "config" / "billing_tiers.json"


def load_config() -> dict:
    """Load routing weights configuration."""
    if not CONFIG_PATH.exists():
        return {
            "default_mode": "balanced",
            "time_cost_config": {"default_hourly_rate": 100, "baseline_tps": 100}
        }
    
    with open(CONFIG_PATH) as f:
        return json.load(f)


def load_billing_tiers() -> list:
    """Load billing tier definitions."""
    if not TIERS_PATH.exists():
        return []
    
    with open(TIERS_PATH) as f:
        data = json.load(f)
    return data.get("tiers", [])


def get_model_specs() -> list:
    """Get model specifications for scoring."""
    tiers = load_billing_tiers()
    
    # Add model performance specs (from TI-016 benchmarking)
    model_specs = {
        "qwen3.5:4b": {"tps": 50, "category": "local", "size": "small"},
        "qwen3:8b": {"tps": 30, "category": "local", "size": "medium"},
        "gemma4:e4b": {"tps": 35, "category": "local", "size": "small"},
        "gemma4:31b-cloud": {"tps": 100, "category": "cloud", "size": "large"},
        "kimi-k2.6:cloud": {"tps": 100, "category": "cloud", "size": "large"},
        "deepseek-v4-pro:cloud": {"tps": 100, "category": "cloud", "size": "large"},
        "glm-5.1:cloud": {"tps": 100, "category": "cloud", "size": "large"}
    }
    
    models = []
    for tier in tiers:
        model_name = tier.get("model", "")
        spec = model_specs.get(model_name, {"tps": 50, "category": "local", "size": "medium"})
        
        models.append({
            "model": model_name,
            "tier": tier.get("name", "Custom"),
            "price_per_1k": tier.get("price_per_1k", 0.005),
            "tps": spec["tps"],
            "category": spec["category"],
            "size": spec["size"]
        })
    
    return models


def calculate_score(model: dict, tokens: int, hourly_rate: float, 
                    monetary_weight: float, time_weight: float, fit_weight: float) -> dict:
    """
    Calculate weighted score for a model.
    
    Score = (monetary_weight × cost_score) + (time_weight × speed_score) + (fit_weight × fit_score)
    
    All scores normalized to [0, 1] where higher is better.
    """
    price_per_1k = model["price_per_1k"]
    tps = model["tps"]
    category = model["category"]
    
    # Monetary cost for this task
    monetary_cost = (tokens / 1000) * price_per_1k
    
    # Time cost (response time × hourly rate)
    # Assume output is ~20% of total tokens for estimation
    output_tokens = tokens * 0.2
    response_time_sec = output_tokens / tps
    time_cost = (response_time_sec / 3600.0) * hourly_rate
    
    # Total cost
    total_cost = monetary_cost + time_cost
    
    # Normalize scores (inverse - lower cost = higher score)
    # Using realistic reference points based on actual model costs
    ref_monetary_cost = 0.50  # $0.50 per request reference (cloud premium for 10K)
    ref_time_sec = 60  # 60 seconds reference (local model response time)
    
    cost_score = max(0, 1 - (monetary_cost / ref_monetary_cost))
    speed_score = max(0, 1 - (response_time_sec / ref_time_sec))
    fit_score = 1.0 if category == "local" else 0.7  # Prefer local for fit (privacy, control)
    
    # Weighted total
    weighted_score = (
        monetary_weight * cost_score +
        time_weight * speed_score +
        fit_weight * fit_score
    )
    
    return {
        "model": model["model"],
        "tier": model["tier"],
        "monetary_cost": round(monetary_cost, 6),
        "response_time_sec": round(response_time_sec, 2),
        "time_cost": round(time_cost, 6),
        "total_cost": round(total_cost, 6),
        "cost_score": round(cost_score, 3),
        "speed_score": round(speed_score, 3),
        "fit_score": round(fit_score, 3),
        "weighted_score": round(weighted_score, 3),
        "category": category
    }


def rank_models(tokens: int, mode: str = "balanced", hourly_rate: float = None) -> list:
    """Rank all models by weighted score."""
    config = load_config()
    
    if hourly_rate is None:
        hourly_rate = config.get("time_cost_config", {}).get("default_hourly_rate", 100)
    
    # Get weights for mode
    presets = config.get("weight_presets", {})
    weights = presets.get(mode, presets.get("balanced", {}))
    
    monetary_weight = weights.get("monetary_weight", 0.35)
    time_weight = weights.get("time_weight", 0.40)
    fit_weight = weights.get("fit_weight", 0.25)
    
    # Score all models
    models = get_model_specs()
    scores = []
    
    for model in models:
        score = calculate_score(
            model, tokens, hourly_rate,
            monetary_weight, time_weight, fit_weight
        )
        scores.append(score)
    
    # Rank by weighted score (descending)
    ranked = sorted(scores, key=lambda x: x["weighted_score"], reverse=True)
    
    # Add rank
    for i, item in enumerate(ranked):
        item["rank"] = i + 1
    
    return ranked


def compare_modes(tokens: int, hourly_rate: float = None) -> dict:
    """Compare ranking across all modes."""
    modes = ["budget", "balanced", "speed"]
    results = {}
    
    for mode in modes:
        ranked = rank_models(tokens, mode, hourly_rate)
        results[mode] = {
            "top_choice": ranked[0]["model"],
            "top_score": ranked[0]["weighted_score"],
            "top_cost": ranked[0]["total_cost"],
            "top_time_sec": ranked[0]["response_time_sec"],
            "full_ranking": ranked
        }
    
    return results


def print_ranking(ranked: list, mode: str, tokens: int):
    """Print ranked model list."""
    print(f"\n{'='*80}")
    print(f"ROUTING RECOMMENDATIONS — {mode.upper()} MODE ({tokens:,} tokens)")
    print(f"{'='*80}\n")
    
    print(f"{'Rank':>5} {'Model':<25} {'Tier':<18} {'Score':>7} {'Cost':>10} {'Time':>8} {'Category':>10}")
    print(f"{'':5} {'':25} {'':18} {'':7} {'(USD)':>10} {'(sec)':>8} {'':10}")
    print("-" * 85)
    
    for item in ranked:
        print(f"{item['rank']:>5} {item['model']:<25} {item['tier']:<18} "
              f"{item['weighted_score']:>7.3f} ${item['monetary_cost']:>8.4f} "
              f"{item['response_time_sec']:>7.2f} {item['category']:>10}")
    
    print(f"\n🏆 RECOMMENDED: {ranked[0]['model']} ({ranked[0]['tier']})")
    print(f"   Total cost: ${ranked[0]['total_cost']:.4f} (${ranked[0]['monetary_cost']:.4f} + ${ranked[0]['time_cost']:.4f} time)")
    print(f"   Response time: {ranked[0]['response_time_sec']:.2f} sec")


def print_comparison(comparison: dict, tokens: int):
    """Print comparison across modes."""
    print(f"\n{'='*80}")
    print(f"CROSS-MODE COMPARISON ({tokens:,} tokens)")
    print(f"{'='*80}\n")
    
    print(f"{'Mode':<12} {'Top Choice':<25} {'Score':>8} {'Total Cost':>12} {'Time':>8}")
    print(f"{'':12} {'':25} {'':8} {'(USD)':>12} {'(sec)':>8}")
    print("-" * 70)
    
    for mode, data in comparison.items():
        print(f"{mode.upper():<12} {data['top_choice']:<25} "
              f"{data['top_score']:>8.3f} ${data['top_cost']:>10.4f} {data['top_time_sec']:>7.2f}")
    
    print(f"\n💡 INSIGHT:")
    budget_choice = comparison["budget"]["top_choice"]
    speed_choice = comparison["speed"]["top_choice"]
    if budget_choice != speed_choice:
        print(f"   Budget mode chooses {budget_choice}")
        print(f"   Speed mode chooses {speed_choice}")
        print(f"   → Your priority determines the optimal model")
    else:
        print(f"   All modes agree on {budget_choice}")


def main():
    parser = argparse.ArgumentParser(description="Calculate optimal routing with time-cost weighting")
    parser.add_argument("--tokens", type=int, default=10000,
                        help="Task token count (default: 10,000)")
    parser.add_argument("--mode", choices=["budget", "balanced", "speed"], default="balanced",
                        help="Routing mode (default: balanced)")
    parser.add_argument("--compare", action="store_true",
                        help="Compare all modes")
    parser.add_argument("--hourly-rate", type=float, default=None,
                        help="Override hourly rate")
    parser.add_argument("--show-config", action="store_true",
                        help="Show current configuration")
    args = parser.parse_args()
    
    if args.show_config:
        config = load_config()
        print(json.dumps(config, indent=2))
        return
    
    if args.compare:
        comparison = compare_modes(args.tokens, args.hourly_rate)
        print_comparison(comparison, args.tokens)
    else:
        ranked = rank_models(args.tokens, args.mode, args.hourly_rate)
        print_ranking(ranked, args.mode, args.tokens)


if __name__ == "__main__":
    main()
