#!/usr/bin/env python3
"""
Options Trade Entry Script

Implements Phase 4.3: Options trade entry with expiry, strike, call/put, extrinsic value.
Supports directional/non-directional classification and covered calls (LS Options features).

Usage:
    python options-entry.py --symbol AAPL --option-type C --strike 175 --expiry 2026-06-20 \\
        --direction LONG --premium 5.50 --contracts 10 --rationale "Bullish breakout"
"""

import json
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path


def generate_trade_id(symbol: str, option_type: str, strike: float, expiry: str, direction: str, timestamp: datetime) -> str:
    """Generate trade ID: YYYYMMDD-HHMM-SYMBOL-EXPIRY-C/P-STRIKE-DIRECTION"""
    ts = timestamp.strftime("%Y%m%d-%H%M")
    expiry_short = expiry.replace("-", "")
    strike_str = str(strike).replace(".", "")
    return f"{ts}-{symbol.upper()}-{expiry_short}-{option_type}-{strike_str}-{direction}"


def calculate_extrinsic_value(premium: float, underlying_price: float, strike: float, option_type: str) -> tuple:
    """Calculate intrinsic and extrinsic value"""
    if option_type == "C":  # Call
        intrinsic = max(0, underlying_price - strike)
    else:  # Put
        intrinsic = max(0, strike - underlying_price)
    
    extrinsic = premium - intrinsic
    return intrinsic, extrinsic


def classify_trade(strategy: str) -> tuple:
    """Classify as directional/non-directional and return trade type"""
    directional_strategies = [
        'long-call', 'long-put', 'short-call', 'short-put',
        'bull-call-spread', 'bear-put-spread'
    ]
    non_directional_strategies = [
        'iron-condor', 'butterfly', 'calendar-spread', 'straddle', 'strangle'
    ]
    covered_strategies = ['covered-call', 'protective-put']
    synthetic_covered = ['synthetic-covered-call', 'poor-mans-covered-call']
    
    strategy_lower = strategy.lower() if strategy else ''
    
    if strategy_lower in covered_strategies:
        return 'covered-call', True
    elif strategy_lower in synthetic_covered:
        return 'synthetic-covered-call', True
    elif strategy_lower in directional_strategies:
        return 'directional', True
    elif strategy_lower in non_directional_strategies:
        return 'non-directional', False
    else:
        return 'directional', True  # Default


def calculate_dte(expiry: str) -> int:
    """Calculate days to expiry"""
    expiry_date = datetime.strptime(expiry, "%Y-%m-%d").date()
    today = datetime.now().date()
    return (expiry_date - today).days


def create_options_trade(args, timestamp: datetime) -> dict:
    """Create options trade record"""
    trade_id = generate_trade_id(
        args.symbol, args.option_type, args.strike, 
        args.expiry, args.direction, timestamp
    )
    
    # Calculate intrinsic/extrinsic if underlying price provided
    intrinsic_value = 0.0
    extrinsic_value = args.premium
    if hasattr(args, 'underlying_price') and args.underlying_price:
        intrinsic_value, extrinsic_value = calculate_extrinsic_value(
            args.premium, args.underlying_price, args.strike, args.option_type
        )
    
    # Calculate DTE
    dte = calculate_dte(args.expiry)
    
    # Classify trade
    trade_classification, is_directional = classify_trade(
        args.strategy if hasattr(args, 'strategy') else None
    )
    
    # Calculate commission (options: $0.65 per contract typical)
    commission = args.contracts * 0.65
    
    # Calculate risk/reward
    if args.direction == "LONG":
        risk_amount = args.premium * args.contracts * 100
        max_reward = None  # Unlimited for calls, strike*100 for puts
    else:  # SHORT
        risk_amount = None  # Unlimited for calls, strike*100 for puts
        max_reward = args.premium * args.contracts * 100
    
    trade = {
        "tradeId": trade_id,
        "symbol": args.symbol.upper(),
        "direction": args.direction.upper(),
        "status": "OPEN",
        "timestamp": timestamp.isoformat(),
        "optionType": args.option_type.upper(),
        "strike": args.strike,
        "expiry": args.expiry,
        "dte": dte,
        "daysToExpiry": dte,
        "premium": args.premium,
        "intrinsicValue": round(intrinsic_value, 2),
        "extrinsicValue": round(extrinsic_value, 2),
        "timeValue": round(extrinsic_value, 2),
        "contracts": args.contracts,
        "averageEntryPrice": args.premium,
        "commission": round(commission, 2),
        "realizedPnL": 0.00,
        "realizedR": 0.00,
        "unrealizedPnL": 0.00,
        "unrealizedR": 0.00,
        "tradeClassification": trade_classification,
        "directional": is_directional,
        "strategy": args.strategy if hasattr(args, 'strategy') else None,
        "entryRationale": args.rationale,
        "setupType": args.setup if hasattr(args, 'setup') else "Unknown",
        "actions": [{
            "action": "ENTRY",
            "timestamp": timestamp.isoformat(),
            "details": {
                "premium": args.premium,
                "contracts": args.contracts,
                "rationale": args.rationale
            }
        }]
    }
    
    # Add covered call details if applicable
    if trade_classification == 'covered-call':
        trade['coveredCallDetails'] = {
            "underlyingShares": args.contracts * 100,
            "coveredReturnPercent": round((args.premium / args.strike) * 100, 2),
            "annualizedReturn": round((args.premium / args.strike) * (365 / dte) * 100, 2) if dte > 0 else 0
        }
    
    return trade


def save_trade(trade: dict, trades_file: Path):
    """Save trade to options trades ledger"""
    if trades_file.exists():
        with open(trades_file, 'r') as f:
            ledger = json.load(f)
    else:
        ledger = {"trades": []}
    
    ledger["trades"].append(trade)
    
    with open(trades_file, 'w') as f:
        json.dump(ledger, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Enter an options trade")
    
    parser.add_argument("--symbol", required=True, help="Underlying stock ticker")
    parser.add_argument("--option-type", required=True, choices=["C", "P"], help="Call or Put")
    parser.add_argument("--strike", type=float, required=True, help="Strike price")
    parser.add_argument("--expiry", required=True, help="Expiration date (YYYY-MM-DD)")
    parser.add_argument("--direction", required=True, choices=["LONG", "SHORT"], help="Trade direction")
    parser.add_argument("--premium", type=float, required=True, help="Option premium")
    parser.add_argument("--contracts", type=int, required=True, help="Number of contracts")
    parser.add_argument("--underlying-price", type=float, help="Current underlying price (for intrinsic/extrinsic calc)")
    parser.add_argument("--strategy", help="Strategy type (e.g., 'covered-call', 'long-call', 'iron-condor')")
    parser.add_argument("--setup", help="Setup type")
    parser.add_argument("--rationale", required=True, help="Entry rationale")
    
    args = parser.parse_args()
    
    # Paths
    base_dir = Path(__file__).parent.parent
    trades_file = base_dir / "options-trades.json"
    account_ledger_path = base_dir / "account-ledger.json"
    
    # Generate trade
    timestamp = datetime.now(timezone.utc)
    trade = create_options_trade(args, timestamp)
    
    # Save trade
    save_trade(trade, trades_file)
    print(f"✓ Options trade logged: {trade['tradeId']}")
    print(f"  {trade['symbol']} {trade['optionType']} {trade['strike']} @ {trade['expiry']}")
    print(f"  Direction: {trade['direction']}, Premium: ${trade['premium']:.2f}")
    print(f"  Contracts: {trade['contracts']}, DTE: {trade['dte']} days")
    print(f"  Intrinsic: ${trade['intrinsicValue']:.2f}, Extrinsic: ${trade['extrinsicValue']:.2f}")
    print(f"  Classification: {trade['tradeClassification']} (Directional: {trade['directional']})")
    print(f"  Commission: ${trade['commission']:.2f}")
    
    if trade.get('coveredCallDetails'):
        cc = trade['coveredCallDetails']
        print(f"  Covered Call Return: {cc['coveredReturnPercent']:.2f}% ({cc['annualizedReturn']:.2f}% annualized)")
    
    return trade['tradeId']


if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
