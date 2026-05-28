#!/usr/bin/env python3
"""
Stock Trade Entry Script

Implements Phase 4.2: Stock trade entry/exit with partial exits and scaling.
Supports 3-target scaling system (LS Stock feature) and block-based analysis (DTI feature).

Usage:
    python stock-entry.py --symbol AAPL --direction LONG --entry 175.50 \\
        --size 100 --stop 170.00 --target 180.00 --target 185.00 --target 190.00 \\
        --rationale "Breakout above resistance" --block ES-B1
"""

import json
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP


def generate_trade_id(symbol: str, direction: str, timestamp: datetime) -> str:
    """Generate trade ID: YYYYMMDD-HHMM-SYMBOL-DIRECTION"""
    ts = timestamp.strftime("%Y%m%d-%H%M")
    return f"{ts}-{symbol.upper()}-{direction}"


def calculate_position_size(risk_amount: float, entry: float, stop: float) -> int:
    """Calculate position size based on risk amount and stop distance"""
    risk_per_share = abs(entry - stop)
    if risk_per_share <= 0:
        raise ValueError("Stop must differ from entry")
    
    shares = int(risk_amount / risk_per_share)
    return shares


def calculate_reward_ratio(entry: float, stop: float, targets: list, direction: str) -> tuple:
    """Calculate risk-reward ratio"""
    if direction == "LONG":
        risk = entry - stop
        rewards = [(t - entry) for t in targets]
    else:  # SHORT
        risk = stop - entry
        rewards = [(entry - t) for t in targets]
    
    if risk <= 0:
        raise ValueError("Stop must be worse than entry")
    
    primary_reward = rewards[0]
    rr_ratio = primary_reward / risk
    
    return f"1:{rr_ratio:.2f}", risk, primary_reward


def load_account_ledger(ledger_path: Path) -> dict:
    """Load account ledger"""
    if ledger_path.exists():
        with open(ledger_path, 'r') as f:
            return json.load(f)
    else:
        return {
            "accountId": "TRADING-001",
            "startingCapital": 50000.00,
            "currentBalance": 50000.00,
            "deposits": [],
            "withdrawals": [],
            "realizedPnL": 0.00,
            "unrealizedPnL": 0.00,
            "marginUsed": 0.00,
            "buyingPower": 50000.00
        }


def load_block_analysis(block_path: Path) -> dict:
    """Load block analysis file"""
    if block_path.exists():
        with open(block_path, 'r') as f:
            return json.load(f)
    else:
        return {
            "metadata": {
                "version": "1.0.0",
                "createdAt": datetime.now(timezone.utc).isoformat()
            },
            "blocks": {}
        }


def get_next_block_number(blocks: list, symbol: str) -> int:
    """Get next block number for symbol"""
    symbol_blocks = [b for b in blocks if b.get('symbol') == symbol]
    if not symbol_blocks:
        return 1
    
    max_block = max(b.get('blockNumber', 0) for b in symbol_blocks)
    return max_block + 1


def create_trade_record(args, timestamp: datetime) -> dict:
    """Create stock trade record"""
    trade_id = generate_trade_id(args.symbol, args.direction, timestamp)
    
    # Parse targets
    targets = args.target if isinstance(args.target, list) else [args.target]
    
    # Calculate reward ratio
    rr_ratio, risk_per_share, reward_per_share = calculate_reward_ratio(
        args.entry, args.stop, targets, args.direction
    )
    
    # Calculate position size if not provided
    position_size = args.size
    if not position_size and args.risk_amount:
        position_size = calculate_position_size(args.risk_amount, args.entry, args.stop)
    
    # Create 3-target structure
    target_records = []
    remaining_percent = 100.0
    for i, target_price in enumerate(targets[:3]):
        if i == len(targets) - 1 or i == 2:
            # Last target gets remaining percent
            percent = remaining_percent
        else:
            percent = args.target_percent[i] if hasattr(args, 'target_percent') and i < len(args.target_percent) else 50.0 / len(targets)
            remaining_percent -= percent
        
        target_records.append({
            "targetNumber": i + 1,
            "price": target_price,
            "sizePercent": round(percent, 1),
            "filled": False
        })
    
    # Calculate commission (stock: $0.005 per share typical)
    commission = abs(position_size * 0.005) if position_size else 0
    
    trade = {
        "tradeId": trade_id,
        "symbol": args.symbol.upper(),
        "direction": args.direction.upper(),
        "status": "OPEN",
        "timestamp": timestamp.isoformat(),
        "blockId": args.block if hasattr(args, 'block') and args.block else None,
        "entries": [{
            "price": args.entry,
            "size": position_size,
            "timestamp": timestamp.isoformat(),
            "commission": commission
        }],
        "exits": [],
        "targets": target_records,
        "stopLoss": args.stop,
        "stopLossHistory": [{
            "price": args.stop,
            "timestamp": timestamp.isoformat(),
            "rationale": "Initial stop"
        }],
        "positionSize": position_size,
        "averageEntryPrice": args.entry,
        "commission": commission,
        "realizedPnL": 0.00,
        "realizedR": 0.00,
        "unrealizedPnL": 0.00,
        "unrealizedR": 0.00,
        "riskReward": rr_ratio,
        "riskAmount": round(risk_per_share * position_size, 2),
        "entryRationale": args.rationale,
        "setupType": args.setup if hasattr(args, 'setup') and args.setup else "Unknown",
        "actions": [{
            "action": "ENTRY",
            "timestamp": timestamp.isoformat(),
            "details": {
                "price": args.entry,
                "size": position_size,
                "rationale": args.rationale
            }
        }]
    }
    
    return trade


def save_trade_to_ledger(trade: dict, trades_file: Path):
    """Save trade to trades ledger"""
    if trades_file.exists():
        with open(trades_file, 'r') as f:
            ledger = json.load(f)
    else:
        ledger = {"trades": []}
    
    ledger["trades"].append(trade)
    
    with open(trades_file, 'w') as f:
        json.dump(ledger, f, indent=2)


def update_block_analysis(trade: dict, block_path: Path):
    """Update block analysis with new trade"""
    with open(block_path, 'r') as f:
        blocks = json.load(f)
    
    symbol = trade['symbol']
    if symbol not in blocks['blocks']:
        blocks['blocks'][symbol] = []
    
    # Check if we need a new block
    current_blocks = blocks['blocks'][symbol]
    if not current_blocks or len(current_blocks[-1].get('trades', [])) >= 25:
        # Create new block
        block_number = get_next_block_number(current_blocks, symbol)
        new_block = {
            "blockId": f"{symbol}-B{block_number}",
            "symbol": symbol,
            "blockNumber": block_number,
            "trades": [],
            "maxTrades": 25,
            "status": "ACTIVE",
            "createdAt": datetime.now(timezone.utc).isoformat()
        }
        blocks['blocks'][symbol].append(new_block)
        current_block = new_block
    else:
        current_block = current_blocks[-1]
    
    # Add trade to block
    current_block['trades'].append({
        "tradeId": trade['tradeId'],
        "timestamp": trade['timestamp'],
        "direction": trade['direction'],
        "entryPrice": trade['averageEntryPrice'],
        "positionSize": trade['positionSize'],
        "status": "OPEN"
    })
    
    # Update block summary
    current_block['totalTrades'] = len(current_block['trades'])
    
    with open(block_path, 'w') as f:
        json.dump(blocks, f, indent=2)
    
    return current_block['blockId']


def main():
    parser = argparse.ArgumentParser(description="Enter a stock trade")
    
    parser.add_argument("--symbol", required=True, help="Stock ticker symbol")
    parser.add_argument("--direction", required=True, choices=["LONG", "SHORT"], help="Trade direction")
    parser.add_argument("--entry", type=float, required=True, help="Entry price")
    parser.add_argument("--size", type=int, help="Position size (shares)")
    parser.add_argument("--risk-amount", type=float, help="Dollar amount to risk (calculates size)")
    parser.add_argument("--stop", type=float, required=True, help="Stop loss price")
    parser.add_argument("--target", type=float, required=True, action="append", help="Take profit targets (up to 3)")
    parser.add_argument("--rationale", required=True, help="Entry rationale")
    parser.add_argument("--setup", help="Setup type (e.g., 'Breakout', 'Pullback')")
    parser.add_argument("--block", help="Block ID (e.g., 'AAPL-B1'), auto-created if not provided")
    
    args = parser.parse_args()
    
    # Validate targets (max 3 for 3-target system)
    if len(args.target) > 3:
        print("Warning: Only 3 targets supported. Using first 3.")
        args.target = args.target[:3]
    
    # Paths
    base_dir = Path(__file__).parent.parent
    account_ledger_path = base_dir / "account-ledger.json"
    block_analysis_path = base_dir / "block-analysis.json"
    trades_file = base_dir / "stock-trades.json"
    
    # Generate trade
    timestamp = datetime.now(timezone.utc)
    trade = create_trade_record(args, timestamp)
    
    # Save trade
    save_trade_to_ledger(trade, trades_file)
    print(f"✓ Stock trade logged: {trade['tradeId']}")
    print(f"  Symbol: {trade['symbol']} {trade['direction']}")
    print(f"  Entry: ${trade['averageEntryPrice']}, Stop: ${trade['stopLoss']}")
    print(f"  Targets: {[t['price'] for t in trade['targets']]}")
    print(f"  Position Size: {trade['positionSize']} shares")
    print(f"  Risk-Reward: {trade['riskReward']}, Risk Amount: ${trade['riskAmount']:.2f}")
    print(f"  Commission: ${trade['commission']:.2f}")
    
    # Update block analysis
    block_id = update_block_analysis(trade, block_analysis_path)
    trade['blockId'] = block_id
    print(f"  Block: {block_id}")
    
    # Update account ledger (unrealized P&L tracking)
    account = load_account_ledger(account_ledger_path)
    account['unrealizedPnL'] += trade['unrealizedPnL']
    account['currentBalance'] = (
        account['startingCapital'] + 
        sum(d['amount'] for d in account['deposits']) -
        sum(w['amount'] for w in account['withdrawals']) +
        account['realizedPnL'] +
        account['unrealizedPnL']
    )
    account['updatedAt'] = timestamp.isoformat()
    
    with open(account_ledger_path, 'w') as f:
        json.dump(account, f, indent=2)
    
    return trade['tradeId']


if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
