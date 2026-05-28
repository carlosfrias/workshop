#!/usr/bin/env python3
"""
cost_calculator.py — Standalone cost calculation for cost-aware routing.

Extracted from ti011_node_registry.py (TI-011) as part of TI-018 migration
to project-blueprint structure. Does not depend on NodeRegistry class.

Usage:
    python3 cost_calculator.py --dump
    python3 cost_calculator.py --hourly-cost --ram-gb 31
    python3 cost_calculator.py --cost-per-1k --hourly-cost 0.0367 --tokens-per-sec 5.5
    python3 cost_calculator.py --validate-tiers
"""

import argparse
import json
import os
import sys
from typing import Optional

# Resolve config paths relative to project root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(SCRIPT_DIR, "..")
BILLING_TIERS_PATH = os.path.join(PROJECT_ROOT, "config", "billing_tiers.json")
COST_DEFAULTS_PATH = os.path.join(PROJECT_ROOT, "config", "cost_defaults.json")


def load_cost_defaults(path: Optional[str] = None) -> dict:
    """Load cost defaults from JSON config."""
    config_path = path or COST_DEFAULTS_PATH
    with open(config_path) as f:
        return json.load(f)


def load_billing_tiers(path: Optional[str] = None) -> dict:
    """Load billing tiers from JSON config."""
    config_path = path or BILLING_TIERS_PATH
    with open(config_path) as f:
        return json.load(f)


def compute_hardware_cost(ram_gb: float, defaults: Optional[dict] = None) -> float:
    """
    Get hardware cost for a node based on RAM tier.

    Args:
        ram_gb: Node RAM in GB
        defaults: Cost defaults dict (loaded from config if None)

    Returns:
        Hardware cost in USD
    """
    if defaults is None:
        defaults = load_cost_defaults()

    for tier in defaults["hardware_costs"]["tiers"]:
        if ram_gb <= tier["max_ram_gb"]:
            return tier["cost_usd"]

    # Fallback: largest tier
    return defaults["hardware_costs"]["tiers"][-1]["cost_usd"]


def compute_node_hourly_cost(
    ram_gb: float,
    hardware_cost_usd: Optional[float] = None,
    power_draw_kwh: Optional[float] = None,
    electricity_rate: Optional[float] = None,
    defaults: Optional[dict] = None,
) -> float:
    """
    Compute synthetic compute cost per hour for a node.

    Includes hardware depreciation + electricity.
    Assumptions:
    - 3-year hardware depreciation (straight-line)
    - Default 0.15 kWh average load per node
    - Default $0.12/kWh electricity rate

    Args:
        ram_gb: Node RAM in GB
        hardware_cost_usd: Override hardware cost (computed from RAM tier if None)
        power_draw_kwh: Override power draw in kWh
        electricity_rate: Override electricity rate in USD/kWh
        defaults: Cost defaults dict (loaded from config if None)

    Returns:
        Cost in USD per hour
    """
    if defaults is None:
        defaults = load_cost_defaults()

    # Hardware cost from config or default by RAM tier
    if hardware_cost_usd is None:
        hardware_cost_usd = compute_hardware_cost(ram_gb, defaults)

    # Depreciation
    depreciation = defaults["depreciation"]
    hours_total = depreciation["years"] * depreciation["hours_per_year"]
    depreciation_per_hour = hardware_cost_usd / hours_total

    # Power
    power_defaults = defaults["power"]
    draw = power_draw_kwh if power_draw_kwh is not None else power_defaults["average_draw_kwh"]
    rate = electricity_rate if electricity_rate is not None else power_defaults["electricity_rate_usd_per_kwh"]
    power_per_hour = draw * rate

    return depreciation_per_hour + power_per_hour


def compute_cost_per_1k_tokens(
    tokens_per_sec: float,
    hourly_cost: float,
) -> float:
    """
    Compute synthetic cost per 1,000 tokens for a (node, model) pair.

    Formula: (hourly_cost / (tokens_per_sec * 3600)) * 1000

    Args:
        tokens_per_sec: Measured inference speed
        hourly_cost: Node hourly cost in USD

    Returns:
        Cost in USD per 1K tokens
    """
    if tokens_per_sec <= 0 or hourly_cost <= 0:
        return 0.0
    tokens_per_hour = tokens_per_sec * 3600
    cost_per_token = hourly_cost / tokens_per_hour
    return cost_per_token * 1000


def compute_score(
    tps: float,
    max_tps: float,
    model_size_gb: float,
    node_capacity_gb: float,
    candidate_cost: float,
    min_cost: float,
    max_cost: float,
) -> dict:
    """
    Score a candidate (node, model) pair for cost-aware routing.

    Formula: total = (0.30 * tps_norm) + (0.45 * fit_score) + (0.25 * cost_score)

    Args:
        tps: Candidate tokens per second
        max_tps: Maximum tps across all candidates
        model_size_gb: Model size in GB
        node_capacity_gb: Node safe capacity in GB
        candidate_cost: Candidate cost per 1K tokens
        min_cost: Minimum cost across candidates
        max_cost: Maximum cost across candidates

    Returns:
        Dict with individual scores and total
    """
    # Speed score
    tps_norm = tps / max_tps if max_tps > 0 else 0.0

    # Fit score
    fit_score = min(model_size_gb / node_capacity_gb, 1.0) if node_capacity_gb > 0 else 0.0

    # Cost score (cheaper = higher)
    cost_range = max_cost - min_cost
    cost_score = (max_cost - candidate_cost) / cost_range if cost_range > 0 else 1.0

    total = 0.30 * tps_norm + 0.45 * fit_score + 0.25 * cost_score

    return {
        "tps_norm": round(tps_norm, 3),
        "fit_score": round(fit_score, 3),
        "cost_score": round(cost_score, 3),
        "total_score": round(total, 3),
    }


def validate_billing_tiers(tiers: Optional[dict] = None) -> list:
    """
    Validate billing tiers have consistent pricing and margins.

    Returns list of validation errors (empty = valid).
    """
    if tiers is None:
        tiers = load_billing_tiers()

    errors = []

    for tier in tiers.get("tiers", []):
        price = tier.get("price_per_1k_tokens", 0)
        margin = tier.get("margin_pct", 0)

        if price <= 0:
            errors.append(f"{tier['id']}: price must be > 0, got {price}")
        if margin < 0 or margin > 100:
            errors.append(f"{tier['id']}: margin must be 0-100%, got {margin}%")

        # Check local tiers are cheaper than cloud tiers
        if tier["venue"] == "local" and price > 0.01:
            errors.append(f"{tier['id']}: local tier price ${price}/1Ktk exceeds $0.01 threshold")

    return errors


def dump_summary():
    """Print human-readable cost summary."""
    defaults = load_cost_defaults()
    tiers = load_billing_tiers()

    print("=== Cost Defaults ===")
    for tier in defaults["hardware_costs"]["tiers"]:
        print(f"  RAM ≤{tier['max_ram_gb']}GB: ${tier['cost_usd']}/node")
    print(f"  Power: {defaults['power']['average_draw_kwh']} kWh × "
          f"${defaults['power']['electricity_rate_usd_per_kwh']}/kWh = "
          f"${defaults['power']['cost_per_hour']}/hour")
    print(f"  Depreciation: {defaults['depreciation']['method']}, "
          f"{defaults['depreciation']['years']} years")
    print()

    # Per-RAM-tier costs
    print("=== Per-Node Hourly Costs ===")
    for ram in [15, 31]:
        hw = compute_hardware_cost(ram, defaults)
        hourly = compute_node_hourly_cost(ram, defaults=defaults)
        print(f"  {ram}GB node: hardware ${hw}, hourly ${hourly:.4f}/hour")
    print()

    # Billing tiers
    print("=== Billing Tiers ===")
    for tier in tiers["tiers"]:
        print(f"  {tier['name']:15s} ({tier['model']:20s}): "
              f"${tier['price_per_1k_tokens']:.4f}/1Ktk, "
              f"{tier['margin_pct']}% margin, {tier['venue']}")
    print()

    # Validation
    errors = validate_billing_tiers(tiers)
    if errors:
        print("=== Validation Errors ===")
        for e in errors:
            print(f"  ❌ {e}")
    else:
        print("✅ All billing tiers valid")


def main():
    parser = argparse.ArgumentParser(description="Cost-aware routing calculator")
    parser.add_argument("--dump", action="store_true", help="Print cost summary")
    parser.add_argument("--hourly-cost", action="store_true", help="Calculate hourly cost")
    parser.add_argument("--ram-gb", type=float, default=31, help="Node RAM in GB")
    parser.add_argument("--hardware-cost", type=float, help="Override hardware cost (USD)")
    parser.add_argument("--cost-per-1k", action="store_true", help="Calculate cost per 1K tokens")
    parser.add_argument("--tokens-per-sec", type=float, default=5.0, help="Model tokens/sec")
    parser.add_argument("--validate-tiers", action="store_true", help="Validate billing tiers")
    parser.add_argument("--defaults-path", help="Override cost defaults JSON path")
    parser.add_argument("--tiers-path", help="Override billing tiers JSON path")
    args = parser.parse_args()

    if args.dump:
        dump_summary()
        return

    if args.hourly_cost:
        defaults = load_cost_defaults(args.defaults_path) if args.defaults_path else None
        hourly = compute_node_hourly_cost(
            args.ram_gb,
            hardware_cost_usd=args.hardware_cost,
            defaults=defaults,
        )
        print(f"${hourly:.4f}/hour")
        return

    if args.cost_per_1k:
        hourly_str = input("Enter hourly cost (USD): ") if not args.hourly_cost else str(hourly)
        hourly = float(hourly_str) if not args.hourly_cost else compute_node_hourly_cost(args.ram_gb)
        cost_1k = compute_cost_per_1k_tokens(args.tokens_per_sec, hourly)
        print(f"${cost_1k:.4f}/1K tokens")
        return

    if args.validate_tiers:
        tiers = load_billing_tiers(args.tiers_path) if args.tiers_path else None
        errors = validate_billing_tiers(tiers)
        if errors:
            for e in errors:
                print(f"❌ {e}")
            sys.exit(1)
        else:
            print("✅ All billing tiers valid")
        return

    # Default: dump
    dump_summary()


if __name__ == "__main__":
    main()