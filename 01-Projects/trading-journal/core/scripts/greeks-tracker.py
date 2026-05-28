#!/usr/bin/env python3
"""
Greeks Tracker

Implements Phase 5.4-5.5: Delta tracking per option position and all Greeks from live data.

Usage:
    python greeks-tracker.py --trade-id 20260528-0010-ES-LONG \\
        --delta 0.45 --gamma 0.02 --theta -0.05 --vega 0.15 --rho 0.01
"""

import json
import argparse
from datetime import datetime, timezone
from pathlib import Path


def update_greeks(trade_id: str, greeks: dict, trades_file: Path) -> dict:
    """Update Greeks for an existing trade"""
    if trades_file.exists():
        with open(trades_file, 'r') as f:
            ledger = json.load(f)
    else:
        return {"error": "Trades ledger not found"}
    
    trade = None
    for t in ledger.get('trades', []):
        if t['tradeId'] == trade_id:
            trade = t
            break
    
    if not trade:
        return {"error": f"Trade not found: {trade_id}"}
    
    # Track entry Greeks vs current Greeks
    if 'delta' not in trade:
        trade['delta'] = greeks.get('delta')
        trade['gamma'] = greeks.get('gamma')
        trade['theta'] = greeks.get('theta')
        trade['vega'] = greeks.get('vega')
        trade['rho'] = greeks.get('rho')
    
    # Update current Greeks
    trade['currentDelta'] = greeks.get('delta')
    trade['currentGamma'] = greeks.get('gamma')
    trade['currentTheta'] = greeks.get('theta')
    trade['currentVega'] = greeks.get('vega')
    trade['currentRho'] = greeks.get('rho')
    trade['updatedAt'] = datetime.now(timezone.utc).isoformat()
    
    # Calculate Greek changes
    if 'delta' in trade and trade['delta'] is not None:
        delta_drift = abs(trade['currentDelta'] - trade['delta'])
        trade['deltaDrift'] = round(delta_drift, 4)
    
    # Save
    with open(trades_file, 'w') as f:
        json.dump(ledger, f, indent=2)
    
    return trade


def check_greek_thresholds(trade: dict, thresholds: dict = None) -> list:
    """Check if Greek changes exceed thresholds"""
    if thresholds is None:
        thresholds = {
            "delta_drift": 0.05,
            "theta_decay": 0.10,
            "vega_change": 0.05
        }
    
    alerts = []
    
    # Delta drift alert
    if 'deltaDrift' in trade:
        if trade['deltaDrift'] > thresholds['delta_drift']:
            alerts.append({
                "type": "DELTA_DRIFT",
                "message": f"Delta drift {trade['deltaDrift']:.3f} exceeds threshold {thresholds['delta_drift']}",
                "severity": "WARNING"
            })
    
    return alerts


def main():
    parser = argparse.ArgumentParser(description="Track Greeks for option positions")
    
    parser.add_argument("--trade-id", required=True, help="Trade ID to update")
    parser.add_argument("--delta", type=float, help="Current delta")
    parser.add_argument("--gamma", type=float, help="Current gamma")
    parser.add_argument("--theta", type=float, help="Current theta")
    parser.add_argument("--vega", type=float, help="Current vega")
    parser.add_argument("--rho", type=float, help="Current rho")
    parser.add_argument("--threshold-delta", type=float, default=0.05, help="Delta drift threshold")
    parser.add_argument("--output", choices=["text", "json"], default="text", help="Output format")
    
    args = parser.parse_args()
    
    # Determine trades file
    base_dir = Path(__file__).parent.parent
    
    greeks = {}
    if args.delta is not None: greeks['delta'] = args.delta
    if args.gamma is not None: greeks['gamma'] = args.gamma
    if args.theta is not None: greeks['theta'] = args.theta
    if args.vega is not None: greeks['vega'] = args.vega
    if args.rho is not None: greeks['rho'] = args.rho
    
    # Try all trade files
    for trades_file in ["options-trades.json", "future-options-trades.json", "stock-trades.json", "futures-trades.json"]:
        filepath = base_dir / trades_file
        if filepath.exists():
            result = update_greeks(args.trade_id, greeks, filepath)
            if 'error' not in result or 'not found' not in result.get('error', ''):
                break
    
    if 'error' in result:
        print(f"Error: {result['error']}")
        return
    
    # Check thresholds
    alerts = check_greek_thresholds(result, {"delta_drift": args.threshold_delta})
    
    if args.output == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"\n{'='*50}")
        print(f"GREEKS UPDATE — {result['tradeId']}")
        print(f"{'='*50}")
        print(f"Entry Δ: {result.get('delta', 'N/A')} → Current Δ: {result.get('currentDelta', 'N/A')}")
        print(f"Entry Γ: {result.get('gamma', 'N/A')} → Current Γ: {result.get('currentGamma', 'N/A')}")
        print(f"Entry Θ: {result.get('theta', 'N/A')} → Current Θ: {result.get('currentTheta', 'N/A')}")
        print(f"Entry ν: {result.get('vega', 'N/A')} → Current ν: {result.get('currentVega', 'N/A')}")
        print(f"Entry ρ: {result.get('rho', 'N/A')} → Current ρ: {result.get('currentRho', 'N/A')}")
        if 'deltaDrift' in result:
            print(f"Delta Drift: {result['deltaDrift']:.4f}")
        for alert in alerts:
            print(f"⚠️  {alert['type']}: {alert['message']}")
        print(f"{'='*50}\n")


if __name__ == "__main__":
    main()