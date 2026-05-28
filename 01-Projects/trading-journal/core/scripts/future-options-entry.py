#!/usr/bin/env python3
"""
Future Options Trade Entry Script

Implements Phase 4.5: Future options trade entry with underlying futures contract and Greeks.
DTI requirement: Track delta at minimum, preferably all Greeks from live data.

Usage:
    python future-options-entry.py --symbol ES --underlying ESZ2026 --option-type C \\
        --strike 5200 --expiry 2026-06-20 --direction LONG --premium 25.50 \\
        --contracts 5 --delta 0.45 --gamma 0.02 --theta -0.15 --vega 0.30
"""

import json
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path


def load_market_lookup(lookup_path: Path) -> dict:
    """Load market lookup table for contract specs"""
    if lookup_path.exists():
        with open(lookup_path, 'r') as f:
            return json.load(f)
    else:
        return {"contractSpecs": []}


def get_contract_spec(symbol: str, lookup: dict) -> dict:
    """Get contract spec from lookup table"""
    for spec in lookup.get('contractSpecs', []):
        if spec['symbol'] == symbol.upper():
            return spec
    
    # Default for ES
    return {
        "symbol": symbol.upper(),
        "pointValue": 50,
        "tickSize": 0.25,
        "tickValue": 12.50,
        "optionMultiplier": 1
    }


def generate_trade_id(symbol: str, underlying: str, option_type: str, strike: float, expiry: str, timestamp: datetime) -> str:
    """Generate trade ID for future options"""
    ts = timestamp.strftime("%Y%m%d-%H%M")
    expiry_short = expiry.replace("-", "")
    strike_str = str(strike).replace(".", "")
    return f"{ts}-{symbol.upper()}-{underlying.upper()}-{expiry_short}-{option_type}-{strike_str}"


def calculate_dte(expiry: str) -> int:
    """Calculate days to expiry"""
    expiry_date = datetime.strptime(expiry, "%Y-%m-%d").date()
    today = datetime.now().date()
    return (expiry_date - today).days


def calculate_extrinsic_value(premium: float, underlying_price: float, strike: float, option_type: str) -> tuple:
    """Calculate intrinsic and extrinsic value"""
    if option_type == "C":  # Call
        intrinsic = max(0, underlying_price - strike)
    else:  # Put
        intrinsic = max(0, strike - underlying_price)
    
    extrinsic = premium - intrinsic
    return intrinsic, extrinsic


def create_future_options_trade(args, timestamp: datetime, contract_spec: dict) -> dict:
    """Create future options trade record"""
    trade_id = generate_trade_id(
        args.symbol, args.underlying, args.option_type, 
        args.strike, args.expiry, timestamp
    )
    
    # Calculate DTE
    dte = calculate_dte(args.expiry)
    
    # Calculate intrinsic/extrinsic if underlying price provided
    intrinsic_value = 0.0
    extrinsic_value = args.premium
    if hasattr(args, 'underlying_price') and args.underlying_price:
        intrinsic_value, extrinsic_value = calculate_extrinsic_value(
            args.premium, args.underlying_price, args.strike, args.option_type
        )
    
    # Calculate commission (future options: typically $2.50 + $0.65 per contract)
    commission_per_contract = contract_spec.get('commissionPerContract', 3.15)
    total_commission = commission_per_contract * args.contracts
    
    # Calculate risk/reward
    if args.direction == "LONG":
        risk_amount = args.premium * args.contracts * contract_spec.get('optionMultiplier', 1)
    else:  # SHORT
        max_reward = args.premium * args.contracts * contract_spec.get('optionMultiplier', 1)
        risk_amount = None  # Unlimited for calls, large for puts
    
    trade = {
        "tradeId": trade_id,
        "symbol": args.symbol.upper(),
        "underlyingSymbol": args.underlying.upper(),
        "futureSymbol": args.underlying.upper(),
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
        "delta": args.delta,
        "gamma": args.gamma if hasattr(args, 'gamma') else None,
        "theta": args.theta if hasattr(args, 'theta') else None,
        "vega": args.vega if hasattr(args, 'vega') else None,
        "rho": args.rho if hasattr(args, 'rho') else None,
        "impliedVolatility": args.iv if hasattr(args, 'iv') else None,
        "contracts": args.contracts,
        "averageEntryPrice": args.premium,
        "commission": round(total_commission, 2),
        "realizedPnL": 0.00,
        "realizedR": 0.00,
        "unrealizedPnL": 0.00,
        "unrealizedR": 0.00,
        "entryRationale": args.rationale,
        "setupType": args.setup if hasattr(args, 'setup') else "Unknown",
        "actions": [{
            "action": "ENTRY",
            "timestamp": timestamp.isoformat(),
            "details": {
                "premium": args.premium,
                "contracts": args.contracts,
                "delta": args.delta,
                "rationale": args.rationale
            }
        }]
    }
    
    # Add contract spec references
    if contract_spec:
        trade['contractSpecId'] = args.symbol.upper()
        trade['pointValue'] = contract_spec.get('pointValue', 50)
        trade['tickValue'] = contract_spec.get('tickValue', 12.50)
        trade['optionMultiplier'] = contract_spec.get('optionMultiplier', 1)
    
    return trade


def save_trade(trade: dict, trades_file: Path):
    """Save trade to future options ledger"""
    if trades_file.exists():
        with open(trades_file, 'r') as f:
            ledger = json.load(f)
    else:
        ledger = {"trades": []}
    
    ledger["trades"].append(trade)
    
    with open(trades_file, 'w') as f:
        json.dump(ledger, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Enter a future options trade")
    
    parser.add_argument("--symbol", required=True, help="Futures root symbol (e.g., ES, NQ)")
    parser.add_argument("--underlying", required=True, help="Underlying futures contract (e.g., ESZ2026)")
    parser.add_argument("--option-type", required=True, choices=["C", "P"], help="Call or Put")
    parser.add_argument("--strike", type=float, required=True, help="Strike price")
    parser.add_argument("--expiry", required=True, help="Expiration date (YYYY-MM-DD)")
    parser.add_argument("--direction", required=True, choices=["LONG", "SHORT"], help="Trade direction")
    parser.add_argument("--premium", type=float, required=True, help="Option premium")
    parser.add_argument("--contracts", type=int, required=True, help="Number of contracts")
    parser.add_argument("--delta", type=float, required=True, help="Delta (DTI requirement)")
    parser.add_argument("--gamma", type=float, help="Gamma")
    parser.add_argument("--theta", type=float, help="Theta")
    parser.add_argument("--vega", type=float, help="Vega")
    parser.add_argument("--rho", type=float, help="Rho")
    parser.add_argument("--iv", type=float, help="Implied volatility")
    parser.add_argument("--underlying-price", type=float, help="Underlying futures price")
    parser.add_argument("--setup", help="Setup type")
    parser.add_argument("--rationale", required=True, help="Entry rationale")
    
    args = parser.parse_args()
    
    # Validate delta is provided (DTI requirement)
    if not args.delta:
        print("Error: Delta is required (DTI requirement)")
        sys.exit(1)
    
    # Paths
    base_dir = Path(__file__).parent.parent
    data_model_dir = base_dir / "data-model"
    market_lookup_path = data_model_dir / "market-lookup-schema.json"
    trades_file = base_dir / "future-options-trades.json"
    account_ledger_path = base_dir / "account-ledger.json"
    
    # Load contract specs
    lookup = load_market_lookup(market_lookup_path)
    contract_spec = get_contract_spec(args.symbol, lookup)
    
    # Generate trade
    timestamp = datetime.now(timezone.utc)
    trade = create_future_options_trade(args, timestamp, contract_spec)
    
    # Save trade
    save_trade(trade, trades_file)
    print(f"✓ Future options trade logged: {trade['tradeId']}")
    print(f"  {trade['symbol']} {trade['optionType']} {trade['strike']} @ {trade['expiry']}")
    print(f"  Underlying: {trade['underlyingSymbol']}, Direction: {trade['direction']}")
    print(f"  Premium: ${trade['premium']:.2f}, Contracts: {trade['contracts']}")
    print(f"  DTE: {trade['dte']} days")
    print(f"  Intrinsic: ${trade['intrinsicValue']:.2f}, Extrinsic: ${trade['extrinsicValue']:.2f}")
    print(f"  Greeks: Δ={trade['delta']:.2f}", end="")
    if trade['gamma']:
        print(f", Γ={trade['gamma']:.4f}", end="")
    if trade['theta']:
        print(f", Θ={trade['theta']:.4f}", end="")
    if trade['vega']:
        print(f", ν={trade['vega']:.2f}", end="")
    print()
    print(f"  Commission: ${trade['commission']:.2f}")
    
    return trade['tradeId']


if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
