#!/usr/bin/env python3
"""
Target Price Projections

Implements Phase 5.6: Options/futures target price projections from underlying.
Supports bull/base/bear scenarios with projected P&L per scenario.

Usage:
    python target-projections.py --underlying 175.00 --strike 180 --premium 5.50 \\
        --contracts 10 --point-value 100 --direction LONG
"""

import json
import argparse
from pathlib import Path


def calculate_scenarios(underlying: float, strike: float = None, premium: float = None,
                        contracts: int = 1, point_value: float = 100, direction: str = "LONG",
                        asset_type: str = "option", scenario_pct: list = None) -> dict:
    """Calculate target price projections under bull/base/bear scenarios.
    
    Args:
        underlying: Current underlying price
        strike: Option strike price (None for stock/future)
        premium: Option premium (None for stock/future)
        contracts: Number of contracts
        point_value: Dollar value per point (1.0 for stocks)
        direction: LONG or SHORT
        asset_type: 'option', 'stock', or 'future'
        scenario_pct: List of scenario percentages [bull, base, bear]
    """
    if scenario_pct is None:
        scenario_pct = [0.05, 0.0, -0.05]  # +5%, 0%, -5%
    
    scenarios = {}
    labels = ["bull", "base", "bear"]
    
    for i, pct in enumerate(scenario_pct):
        label = labels[i]
        target_price = underlying * (1 + pct)
        
        if asset_type == "option" and strike is not None and premium is not None:
            # Calculate option value at target
            if direction == "LONG":
                intrinsic = max(0, target_price - strike)
            else:
                intrinsic = max(0, strike - target_price)
            
            # Estimate extrinsic (decreases with time)
            extrinsic_est = max(0.50, premium * 0.3)  # Rough estimate
            option_value = intrinsic + extrinsic_est
            
            # P&L
            if direction == "LONG":
                pnl = (option_value - premium) * contracts * point_value
            else:
                pnl = (premium - option_value) * contracts * point_value
            
            scenarios[label] = {
                "underlyingPrice": round(target_price, 2),
                "pctChange": round(pct * 100, 1),
                "optionValue": round(option_value, 2),
                "pnl": round(pnl, 2),
                "intrinsic": round(intrinsic, 2),
                "extrinsic": round(extrinsic_est, 2)
            }
        else:
            # Stock or future
            if direction == "LONG":
                pnl = (target_price - underlying) * contracts * point_value
            else:
                pnl = (underlying - target_price) * contracts * point_value
            
            scenarios[label] = {
                "underlyingPrice": round(target_price, 2),
                "pctChange": round(pct * 100, 1),
                "pnl": round(pnl, 2)
            }
    
    # Calculate breakeven
    breakeven = None
    if asset_type == "option" and premium is not None and strike is not None:
        if direction == "LONG":
            breakeven = strike + premium  # Call breakeven
        else:
            breakeven = strike - premium  # Put breakeven
    
    return {
        "underlyingPrice": underlying,
        "strike": strike,
        "premium": premium,
        "contracts": contracts,
        "pointValue": point_value,
        "direction": direction,
        "assetType": asset_type,
        "scenarios": scenarios,
        "breakeven": round(breakeven, 2) if breakeven else None
    }


def main():
    parser = argparse.ArgumentParser(description="Calculate target price projections")
    
    parser.add_argument("--underlying", type=float, required=True, help="Current underlying price")
    parser.add_argument("--strike", type=float, help="Option strike price")
    parser.add_argument("--premium", type=float, help="Option premium")
    parser.add_argument("--contracts", type=int, default=1, help="Number of contracts")
    parser.add_argument("--point-value", type=float, default=100, help="Dollar value per point")
    parser.add_argument("--direction", choices=["LONG", "SHORT"], default="LONG", help="Trade direction")
    parser.add_argument("--asset-type", choices=["option", "stock", "future"], default="option", help="Asset type")
    parser.add_argument("--bull-pct", type=float, default=0.05, help="Bull scenario % (default: +5%)")
    parser.add_argument("--bear-pct", type=float, default=-0.05, help="Bear scenario % (default: -5%)")
    parser.add_argument("--output", choices=["text", "json"], default="text", help="Output format")
    
    args = parser.parse_args()
    
    result = calculate_scenarios(
        args.underlying, args.strike, args.premium,
        args.contracts, args.point_value, args.direction,
        args.asset_type, [args.bull_pct, 0.0, args.bear_pct]
    )
    
    if args.output == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"\n{'='*50}")
        print(f"TARGET PROJECTIONS — {args.asset_type.upper()} {args.direction}")
        print(f"{'='*50}")
        print(f"Underlying: ${args.underlying:.2f}")
        if args.strike:
            print(f"Strike: ${args.strike:.2f}")
            print(f"Premium: ${args.premium:.2f}")
        if result['breakeven']:
            print(f"Breakeven: ${result['breakeven']:.2f}")
        print(f"\nScenarios:")
        for label, scenario in result['scenarios'].items():
            print(f"  {label.upper()}: ${scenario['underlyingPrice']:.2f} ({scenario['pctChange']:+.1f}%)", end="")
            if 'optionValue' in scenario:
                print(f" → Opt=${scenario['optionValue']:.2f}", end="")
            print(f" → P&L=${scenario['pnl']:.2f}")
        print(f"{'='*50}\n")


if __name__ == "__main__":
    main()