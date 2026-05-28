#!/usr/bin/env python3
"""
Futures Trade Entry Script

Implements Phase 4.4: Futures trade entry with contract specs lookup.
References market lookup table for point value, tick size, commission (LS Futures feature).

Usage:
    python futures-entry.py --symbol ES --contract-month 2026-06 --direction LONG \\
        --entry 5234.50 --contracts 2 --stop 5220.00 --target 5260.00 \\
        --rationale "Breakout above resistance"
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
        # Default specs for common futures
        return {
            "contractSpecs": [
                {
                    "symbol": "ES",
                    "name": "E-mini S&P 500",
                    "pointValue": 50,
                    "tickSize": 0.25,
                    "tickValue": 12.50,
                    "marginRequirement": 12100,
                    "commissionPerContract": 2.50
                },
                {
                    "symbol": "NQ",
                    "name": "E-mini NASDAQ-100",
                    "pointValue": 20,
                    "tickSize": 0.25,
                    "tickValue": 5.00,
                    "marginRequirement": 17600,
                    "commissionPerContract": 2.50
                },
                {
                    "symbol": "CL",
                    "name": "Crude Oil WTI",
                    "pointValue": 1000,
                    "tickSize": 0.01,
                    "tickValue": 10.00,
                    "marginRequirement": 7700,
                    "commissionPerContract": 2.50
                }
            ]
        }


def get_contract_spec(symbol: str, lookup: dict) -> dict:
    """Get contract spec from lookup table"""
    for spec in lookup.get('contractSpecs', []):
        if spec['symbol'] == symbol.upper():
            return spec
    
    # Default if not found
    return {
        "symbol": symbol.upper(),
        "pointValue": 50,
        "tickSize": 0.25,
        "tickValue": 12.50,
        "marginRequirement": 10000,
        "commissionPerContract": 2.50
    }


def generate_trade_id(symbol: str, contract_month: str, direction: str, timestamp: datetime) -> str:
    """Generate trade ID: YYYYMMDD-HHMM-SYMBOL-YEAR-MONTH-DIRECTION"""
    ts = timestamp.strftime("%Y%m%d-%H%M")
    year_month = contract_month.replace("-", "")
    return f"{ts}-{symbol.upper()}-{year_month}-{direction}"


def calculate_full_symbol(symbol: str, contract_month: str) -> str:
    """Generate full futures symbol (e.g., ESZ2026)"""
    month_codes = {
        '01': 'F', '02': 'G', '03': 'H', '04': 'J', '05': 'K', '06': 'M',
        '07': 'N', '08': 'Q', '09': 'U', '10': 'V', '11': 'X', '12': 'Z'
    }
    
    year = contract_month[:4]
    month = contract_month[5:7]
    month_code = month_codes.get(month, 'M')
    
    return f"{symbol.upper()}{month_code}{year}"


def calculate_reward_ratio(entry: float, stop: float, targets: list, direction: str, point_value: float) -> tuple:
    """Calculate risk-reward ratio in points and dollars"""
    if direction == "LONG":
        risk_points = entry - stop
        rewards = [(t - entry) for t in targets]
    else:  # SHORT
        risk_points = stop - entry
        rewards = [(entry - t) for t in targets]
    
    if risk_points <= 0:
        raise ValueError("Stop must be worse than entry")
    
    primary_reward_points = rewards[0]
    rr_ratio = primary_reward_points / risk_points
    
    risk_dollars = risk_points * point_value
    reward_dollars = primary_reward_points * point_value
    
    return f"1:{rr_ratio:.2f}", risk_points, risk_dollars, reward_dollars


def create_futures_trade(args, timestamp: datetime, contract_spec: dict) -> dict:
    """Create futures trade record"""
    trade_id = generate_trade_id(args.symbol, args.contract_month, args.direction, timestamp)
    full_symbol = calculate_full_symbol(args.symbol, args.contract_month)
    
    # Parse targets
    targets = args.target if isinstance(args.target, list) else [args.target]
    
    # Calculate reward ratio
    rr_ratio, risk_points, risk_dollars, reward_dollars = calculate_reward_ratio(
        args.entry, args.stop, targets, args.direction, contract_spec['pointValue']
    )
    
    # Calculate commission
    commission_per_contract = contract_spec.get('commissionPerContract', 2.50)
    total_commission = commission_per_contract * args.contracts
    
    # Calculate margin
    margin_per_contract = contract_spec.get('marginRequirement', 10000)
    total_margin = margin_per_contract * args.contracts
    
    # Create 3-target structure
    target_records = []
    remaining_percent = 100.0
    for i, target_price in enumerate(targets[:3]):
        if i == len(targets) - 1 or i == 2:
            percent = remaining_percent
        else:
            percent = 50.0 if len(targets) == 2 else 33.3
            remaining_percent -= percent
        
        target_records.append({
            "targetNumber": i + 1,
            "price": target_price,
            "contractsPercent": round(percent, 1),
            "filled": False
        })
    
    trade = {
        "tradeId": trade_id,
        "symbol": args.symbol.upper(),
        "contractMonth": args.contract_month,
        "fullSymbol": full_symbol,
        "direction": args.direction.upper(),
        "status": "OPEN",
        "timestamp": timestamp.isoformat(),
        "contractSpecId": args.symbol.upper(),
        "pointValue": contract_spec['pointValue'],
        "tickSize": contract_spec['tickSize'],
        "tickValue": contract_spec['tickValue'],
        "contractSize": contract_spec.get('contractSize', f"${contract_spec['pointValue']} x Index"),
        "entries": [{
            "price": args.entry,
            "contracts": args.contracts,
            "timestamp": timestamp.isoformat(),
            "commission": total_commission
        }],
        "exits": [],
        "targets": target_records,
        "stopLoss": args.stop,
        "stopLossHistory": [{
            "price": args.stop,
            "timestamp": timestamp.isoformat(),
            "rationale": "Initial stop"
        }],
        "contracts": args.contracts,
        "averageEntryPrice": args.entry,
        "commission": round(total_commission, 2),
        "commissionPerContract": commission_per_contract,
        "marginRequirement": margin_per_contract,
        "totalMarginUsed": total_margin,
        "realizedPnL": 0.00,
        "realizedR": 0.00,
        "unrealizedPnL": 0.00,
        "unrealizedR": 0.00,
        "riskReward": rr_ratio,
        "riskAmount": round(risk_dollars * args.contracts, 2),
        "entryRationale": args.rationale,
        "setupType": args.setup if hasattr(args, 'setup') else "Unknown",
        "actions": [{
            "action": "ENTRY",
            "timestamp": timestamp.isoformat(),
            "details": {
                "price": args.entry,
                "contracts": args.contracts,
                "rationale": args.rationale
            }
        }]
    }
    
    return trade


def save_trade(trade: dict, trades_file: Path):
    """Save trade to futures trades ledger"""
    if trades_file.exists():
        with open(trades_file, 'r') as f:
            ledger = json.load(f)
    else:
        ledger = {"trades": []}
    
    ledger["trades"].append(trade)
    
    with open(trades_file, 'w') as f:
        json.dump(ledger, f, indent=2)


def update_account_margin(trade: dict, account_path: Path):
    """Update account ledger with margin used"""
    if account_path.exists():
        with open(account_path, 'r') as f:
            account = json.load(f)
    else:
        account = {
            "startingCapital": 50000.00,
            "currentBalance": 50000.00,
            "realizedPnL": 0.00,
            "unrealizedPnL": 0.00,
            "marginUsed": 0.00
        }
    
    account['marginUsed'] = account.get('marginUsed', 0) + trade['totalMarginUsed']
    account['marginRequirement'] = account.get('marginRequirement', 0) + trade['totalMarginUsed']
    account['buyingPower'] = account.get('startingCapital', 50000) - account['marginUsed']
    account['updatedAt'] = trade['timestamp']
    
    with open(account_path, 'w') as f:
        json.dump(account, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Enter a futures trade")
    
    parser.add_argument("--symbol", required=True, help="Futures root symbol (e.g., ES, NQ, CL)")
    parser.add_argument("--contract-month", required=True, help="Contract month (YYYY-MM)")
    parser.add_argument("--direction", required=True, choices=["LONG", "SHORT"], help="Trade direction")
    parser.add_argument("--entry", type=float, required=True, help="Entry price")
    parser.add_argument("--contracts", type=int, required=True, help="Number of contracts")
    parser.add_argument("--stop", type=float, required=True, help="Stop loss price")
    parser.add_argument("--target", type=float, required=True, action="append", help="Take profit targets (up to 3)")
    parser.add_argument("--rationale", required=True, help="Entry rationale")
    parser.add_argument("--setup", help="Setup type")
    
    args = parser.parse_args()
    
    # Validate targets
    if len(args.target) > 3:
        print("Warning: Only 3 targets supported. Using first 3.")
        args.target = args.target[:3]
    
    # Paths
    base_dir = Path(__file__).parent.parent
    data_model_dir = base_dir / "data-model"
    market_lookup_path = data_model_dir / "market-lookup-schema.json"
    trades_file = base_dir / "futures-trades.json"
    account_ledger_path = base_dir / "account-ledger.json"
    
    # Load contract specs
    lookup = load_market_lookup(market_lookup_path)
    contract_spec = get_contract_spec(args.symbol, lookup)
    
    # Generate trade
    timestamp = datetime.now(timezone.utc)
    trade = create_futures_trade(args, timestamp, contract_spec)
    
    # Save trade
    save_trade(trade, trades_file)
    print(f"✓ Futures trade logged: {trade['tradeId']}")
    print(f"  Symbol: {trade['fullSymbol']} {trade['direction']}")
    print(f"  Entry: {trade['averageEntryPrice']}, Stop: {trade['stopLoss']}")
    print(f"  Targets: {[t['price'] for t in trade['targets']]}")
    print(f"  Contracts: {trade['contracts']}, Point Value: ${trade['pointValue']}")
    print(f"  Risk-Reward: {trade['riskReward']}, Risk Amount: ${trade['riskAmount']:.2f}")
    print(f"  Tick Value: ${trade['tickValue']}, Margin per Contract: ${trade['marginRequirement']}")
    print(f"  Commission: ${trade['commission']:.2f} (${trade['commissionPerContract']}/contract)")
    print(f"  Total Margin Used: ${trade['totalMarginUsed']:.2f}")
    
    # Update account margin
    update_account_margin(trade, account_ledger_path)
    
    return trade['tradeId']


if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
