#!/usr/bin/env python3
"""
Reward Ratio Calculator

Implements Phase 4.9: Reward ratio calculator (DTI feature).
Calculates risk-reward ratios for LONG/SHORT trades with commission accounting.

Usage:
    python reward-ratio-calculator.py --entry 5234.50 --stop 5220.00 --target 5260.00 \\
        --direction LONG --point-value 50 --contracts 2 --commission 5.00
"""

import argparse
import sys
from decimal import Decimal, ROUND_HALF_UP


def calculate_reward_ratio(entry: float, stop: float, targets: list, direction: str, 
                           point_value: float = 1.0, contracts: int = 1, 
                           commission: float = 0.0) -> dict:
    """
    Calculate risk-reward ratio with optional commission accounting.
    
    Args:
        entry: Entry price
        stop: Stop loss price
        targets: List of target prices
        direction: LONG or SHORT
        point_value: Dollar value per point (1.0 for stocks)
        contracts: Number of contracts/shares
        commission: Total commission paid
    
    Returns:
        Dictionary with ratio, risk, reward, and analysis
    """
    if direction == "LONG":
        risk_points = entry - stop
        rewards_points = [(t - entry) for t in targets]
    else:  # SHORT
        risk_points = stop - entry
        rewards_points = [(entry - t) for t in targets]
    
    if risk_points <= 0:
        raise ValueError("Stop must be worse than entry price")
    
    # Calculate in points
    primary_reward_points = rewards_points[0]
    ratio_points = primary_reward_points / risk_points
    
    # Calculate in dollars
    risk_dollars = risk_points * point_value * contracts + commission
    reward_dollars = primary_reward_points * point_value * contracts - commission
    
    ratio_dollars = reward_dollars / risk_dollars if risk_dollars > 0 else 0
    
    # Calculate for all targets
    target_analysis = []
    for i, target in enumerate(targets):
        if direction == "LONG":
            reward_pts = target - entry
        else:
            reward_pts = entry - target
        
        ratio = reward_pts / risk_points
        reward_usd = reward_pts * point_value * contracts - commission
        target_analysis.append({
            "target": i + 1,
            "price": target,
            "ratio_points": round(ratio, 2),
            "reward_dollars": round(reward_usd, 2)
        })
    
    return {
        "direction": direction,
        "entry": entry,
        "stop": stop,
        "risk_points": round(risk_points, 2),
        "risk_dollars": round(risk_dollars, 2),
        "primary_target": targets[0],
        "primary_reward_points": round(primary_reward_points, 2),
        "primary_reward_dollars": round(reward_dollars, 2),
        "ratio_points": f"1:{ratio_points:.2f}",
        "ratio_dollars": f"1:{ratio_dollars:.2f}",
        "ratio_raw": round(ratio_dollars, 2),
        "targets": target_analysis,
        "meets_minimum": ratio_dollars >= 2.0,
        "requires_review": ratio_dollars < 2.0
    }


def analyze_trade_quality(ratio: float, win_rate: float = None) -> dict:
    """
    Analyze trade quality based on R:R and win rate.
    
    Args:
        ratio: Risk-reward ratio (reward/risk)
        win_rate: Optional win rate (0-1)
    
    Returns:
        Quality analysis
    """
    analysis = {
        "ratio": ratio,
        "quality": "UNKNOWN",
        "recommendation": "",
        "notes": []
    }
    
    if ratio >= 3.0:
        analysis["quality"] = "EXCELLENT"
        analysis["notes"].append("Exceptional R:R, acceptable even with 25% win rate")
    elif ratio >= 2.0:
        analysis["quality"] = "GOOD"
        analysis["notes"].append("Meets minimum 1:2 target")
    elif ratio >= 1.5:
        analysis["quality"] = "FAIR"
        analysis["notes"].append("Below 1:2 target, requires high win rate")
        analysis["recommendation"] = "Ensure win rate > 50% or look for better setup"
    elif ratio >= 1.0:
        analysis["quality"] = "POOR"
        analysis["notes"].append("1:1 or worse, needs very high win rate")
        analysis["recommendation"] = "Avoid unless win rate > 60%"
    else:
        analysis["quality"] = "NEGATIVE"
        analysis["notes"].append("Negative expectancy setup")
        analysis["recommendation"] = "DO NOT TAKE - risk exceeds reward"
    
    # Calculate required win rate for breakeven
    if ratio > 0:
        required_wr = 1 / (1 + ratio)
        analysis["required_win_rate"] = round(required_wr * 100, 1)
        analysis["notes"].append(f"Breakeven win rate: {required_wr*100:.1f}%")
    
    # If win rate provided, calculate expectancy
    if win_rate:
        loss_rate = 1 - win_rate
        avg_win_r = ratio
        avg_loss_r = -1.0
        expectancy = (win_rate * avg_win_r) + (loss_rate * avg_loss_r)
        analysis["expectancy"] = round(expectancy, 2)
        
        if expectancy > 0:
            analysis["notes"].append(f"Positive expectancy: {expectancy:.2f}R per trade")
        else:
            analysis["notes"].append(f"NEGATIVE expectancy: {expectancy:.2f}R per trade")
            analysis["recommendation"] = "AVOID - negative expectancy"
    
    return analysis


def main():
    parser = argparse.ArgumentParser(description="Calculate risk-reward ratio")
    
    parser.add_argument("--entry", type=float, required=True, help="Entry price")
    parser.add_argument("--stop", type=float, required=True, help="Stop loss price")
    parser.add_argument("--target", type=float, required=True, action="append", 
                        help="Take profit target(s)")
    parser.add_argument("--direction", required=True, choices=["LONG", "SHORT"], 
                        help="Trade direction")
    parser.add_argument("--point-value", type=float, default=1.0, 
                        help="Dollar value per point (default: 1.0 for stocks)")
    parser.add_argument("--contracts", type=int, default=1, 
                        help="Number of contracts/shares")
    parser.add_argument("--commission", type=float, default=0.0, 
                        help="Total commission")
    parser.add_argument("--win-rate", type=float, 
                        help="Expected win rate (0-1) for expectancy calc")
    parser.add_argument("--output", choices=["text", "json"], default="text",
                        help="Output format")
    
    args = parser.parse_args()
    
    try:
        # Calculate ratio
        result = calculate_reward_ratio(
            args.entry, args.stop, args.target, args.direction,
            args.point_value, args.contracts, args.commission
        )
        
        # Analyze quality
        quality = analyze_trade_quality(result['ratio_raw'], args.win_rate)
        result['quality'] = quality
        
        # Output
        if args.output == "json":
            import json
            print(json.dumps(result, indent=2))
        else:
            print(f"\n{'='*60}")
            print(f"REWARD RATIO ANALYSIS - {result['direction']}")
            print(f"{'='*60}")
            print(f"Entry:  ${result['entry']:.2f}")
            print(f"Stop:   ${result['stop']:.2f}")
            print(f"Target: ${result['primary_target']:.2f}")
            print(f"\nRisk:  {result['risk_points']} points (${result['risk_dollars']:.2f})")
            print(f"Reward: {result['primary_reward_points']} points (${result['primary_reward_dollars']:.2f})")
            print(f"\nRatio (points):  {result['ratio_points']}")
            print(f"Ratio (dollars): {result['ratio_dollars']}")
            print(f"\nQuality: {quality['quality']}")
            
            if quality.get('required_win_rate'):
                print(f"Breakeven Win Rate: {quality['required_win_rate']}%")
            
            if quality.get('expectancy'):
                print(f"Expectancy: {quality['expectancy']}R per trade")
            
            if quality['recommendation']:
                print(f"\n⚠️  {quality['recommendation']}")
            
            print(f"\nTarget Analysis:")
            for t in result['targets']:
                print(f"  T{t['target']}: {t['price']:.2f} → {t['ratio_points']}R (${t['reward_dollars']:.2f})")
            
            if not result['meets_minimum']:
                print(f"\n⚠️  WARNING: Ratio below 1:2 minimum. Requires review.")
            
            print(f"{'='*60}\n")
        
        # Exit code based on quality
        if quality['quality'] in ['NEGATIVE', 'POOR']:
            sys.exit(1)
        elif result.get('requires_review'):
            sys.exit(0)  # Warning but allowed
        else:
            sys.exit(0)
    
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
