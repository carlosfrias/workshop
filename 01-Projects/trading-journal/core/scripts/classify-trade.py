#!/usr/bin/env python3
"""
Trade Classification Script

Implements Phase 5.3: Directional vs non-directional trade classification.

Usage:
    python classify-trade.py --strategy "iron-condor" --direction SHORT
    python classify-trade.py --strategy "long-call" --direction LONG
"""

import json
import argparse
from pathlib import Path


DIRECTIONAL_STRATEGIES = [
    "long-call", "long-put", "short-call", "short-put",
    "bull-call-spread", "bear-put-spread",
    "bull-put-spread", "bear-call-spread",
    "call-debit-spread", "put-debit-spread",
    "call-calendar-spread"  # Directional variant
]

NON_DIRECTIONAL_STRATEGIES = [
    "iron-condor", "iron-butterfly", "butterfly",
    "calendar-spread", "diagonal-spread",
    "straddle", "strangle",
    "short-iron-butterfly", "jade-lizard",
    "double-calendar"
]

COVERED_STRATEGIES = [
    "covered-call", "protective-put", "collar",
    "buy-write"
]

SYNTHETIC_COVERED_STRATEGIES = [
    "synthetic-covered-call", "poor-mans-covered-call",
    "deep-itm-leap-call-spread"
]


def classify_trade(strategy: str, direction: str = None) -> dict:
    """Classify a trade as directional, non-directional, or covered.
    
    Args:
        strategy: Strategy name (e.g., 'iron-condor', 'long-call')
        direction: Trade direction (LONG, SHORT)
    
    Returns:
        Dictionary with classification details
    """
    strategy_lower = strategy.lower().replace(" ", "-").replace("_", "-")
    
    if strategy_lower in COVERED_STRATEGIES:
        classification = "covered-call"
        is_directional = False
    elif strategy_lower in SYNTHETIC_COVERED_STRATEGIES:
        classification = "synthetic-covered-call"
        is_directional = False
    elif strategy_lower in NON_DIRECTIONAL_STRATEGIES:
        classification = "non-directional"
        is_directional = False
    elif strategy_lower in DIRECTIONAL_STRATEGIES:
        classification = "directional"
        is_directional = True
    else:
        # Default classification based on direction
        classification = "directional"
        is_directional = True
    
    return {
        "strategy": strategy_lower,
        "direction": direction,
        "classification": classification,
        "isDirectional": is_directional,
        "strategies_list": {
            "directional": DIRECTIONAL_STRATEGIES,
            "non_directional": NON_DIRECTIONAL_STRATEGIES,
            "covered": COVERED_STRATEGIES,
            "synthetic_covered": SYNTHETIC_COVERED_STRATEGIES
        }
    }


def main():
    parser = argparse.ArgumentParser(description="Classify trade strategy")
    
    parser.add_argument("--strategy", required=True, help="Strategy name (e.g., 'iron-condor')")
    parser.add_argument("--direction", help="Trade direction (LONG, SHORT)")
    parser.add_argument("--output", choices=["text", "json"], default="text", help="Output format")
    
    args = parser.parse_args()
    
    result = classify_trade(args.strategy, args.direction)
    
    if args.output == "json":
        print(json.dumps(result, indent=2, default=str))
    else:
        print(f"\n{'='*40}")
        print(f"TRADE CLASSIFICATION")
        print(f"{'='*40}")
        print(f"Strategy: {result['strategy']}")
        print(f"Classification: {result['classification']}")
        print(f"Directional: {result['isDirectional']}")
        print(f"Direction: {result['direction']}")
        print(f"{'='*40}\n")
    
    return result


if __name__ == "__main__":
    main()