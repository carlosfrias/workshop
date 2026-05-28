#!/usr/bin/env python3
"""
Trade Management Script

Implements Phase 4.6: Trade management - adjust stop, target, partial close.
Supports: ADJUST_STOP, SCALE_IN, SCALE_OUT, CLOSE, TRAIL actions.

Usage:
    python manage-trade.py --trade-id 20260528-0010-ES-LONG --action ADJUST_STOP \\
        --new-stop 5240.00 --rationale "Moved to breakeven"
    
    python manage-trade.py --trade-id 20260528-0010-ES-LONG --action SCALE_OUT \\
        --size 1 --exit-price 5260.00
"""

import json
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path


def load_trades(trades_file: Path) -> dict:
    """Load trades ledger"""
    if trades_file.exists():
        with open(trades_file, 'r') as f:
            return json.load(f)
    else:
        return {"trades": []}


def save_trades(trades_file: Path, ledger: dict):
    """Save trades ledger"""
    with open(trades_file, 'w') as f:
        json.dump(ledger, f, indent=2)


def find_trade(ledger: dict, trade_id: str) -> tuple:
    """Find trade by ID, return (trade, index)"""
    for i, trade in enumerate(ledger.get('trades', [])):
        if trade['tradeId'] == trade_id:
            return trade, i
    return None, -1


def adjust_stop(trade: dict, new_stop: float, rationale: str, timestamp: datetime) -> dict:
    """Adjust stop loss (must improve position)"""
    direction = trade['direction']
    current_stop = trade['stopLoss']
    
    # Validate stop improvement
    if direction == "LONG" and new_stop <= current_stop:
        raise ValueError(f"For LONG, new stop ({new_stop}) must be > current stop ({current_stop})")
    elif direction == "SHORT" and new_stop >= current_stop:
        raise ValueError(f"For SHORT, new stop ({new_stop}) must be < current stop ({current_stop})")
    
    # Update trade
    trade['stopLossHistory'].append({
        "price": new_stop,
        "timestamp": timestamp.isoformat(),
        "rationale": rationale
    })
    trade['stopLoss'] = new_stop
    
    # Add action
    trade['actions'].append({
        "action": "ADJUST_STOP",
        "timestamp": timestamp.isoformat(),
        "details": {
            "previousStop": current_stop,
            "newStop": new_stop,
            "rationale": rationale
        }
    })
    
    return trade


def scale_out(trade: dict, size: float, exit_price: float, timestamp: datetime) -> dict:
    """Partial close (scale out)"""
    remaining_size = trade['positionSize'] - sum(e.get('size', 0) for e in trade.get('exits', []))
    
    if size > remaining_size:
        raise ValueError(f"Cannot exit {size}, only {remaining_size} remaining")
    
    # Calculate P&L
    if trade['direction'] == "LONG":
        pnl = (exit_price - trade['averageEntryPrice']) * size
    else:
        pnl = (trade['averageEntryPrice'] - exit_price) * size
    
    # For futures/options, apply multiplier
    if 'pointValue' in trade:
        pnl *= trade['pointValue']
    elif trade.get('symbol') in ['ES', 'NQ', 'CL', 'GC', 'SI']:
        # Default futures multiplier
        pnl *= 50
    
    # Record exit
    trade['exits'].append({
        "price": exit_price,
        "size": size,
        "timestamp": timestamp.isoformat(),
        "pnl": pnl
    })
    
    # Update status
    if size >= remaining_size:
        trade['status'] = "CLOSED"
    else:
        trade['status'] = "PARTIAL"
    
    # Update realized P&L
    trade['realizedPnL'] = trade.get('realizedPnL', 0) + pnl
    
    # Calculate realized R
    risk_per_unit = abs(trade['averageEntryPrice'] - trade['stopLoss'])
    if 'pointValue' in trade:
        risk_per_unit *= trade['pointValue']
    realized_r = pnl / (risk_per_unit * size) if risk_per_unit > 0 else 0
    trade['realizedR'] = round(realized_r, 2)
    
    # Add action
    trade['actions'].append({
        "action": "SCALE_OUT",
        "timestamp": timestamp.isoformat(),
        "details": {
            "sizeReduced": size,
            "remainingSize": remaining_size - size,
            "exitPrice": exit_price,
            "realizedPnL": pnl,
            "realizedR": trade['realizedR']
        }
    })
    
    return trade


def scale_in(trade: dict, size: float, entry_price: float, timestamp: datetime) -> dict:
    """Add to position (scale in)"""
    # Record new entry
    trade['entries'].append({
        "price": entry_price,
        "size": size,
        "timestamp": timestamp.isoformat()
    })
    
    # Update position size
    trade['positionSize'] += size
    
    # Recalculate average entry
    total_value = sum(e['price'] * e['size'] for e in trade['entries'])
    trade['averageEntryPrice'] = total_value / trade['positionSize']
    
    # Add action
    trade['actions'].append({
        "action": "SCALE_IN",
        "timestamp": timestamp.isoformat(),
        "details": {
            "additionalSize": size,
            "newPositionSize": trade['positionSize'],
            "newAverageEntry": trade['averageEntryPrice']
        }
    })
    
    return trade


def close_position(trade: dict, exit_price: float, rationale: str, timestamp: datetime) -> dict:
    """Close entire position"""
    remaining_size = trade['positionSize'] - sum(e.get('size', 0) for e in trade.get('exits', []))
    
    # Calculate final P&L
    if trade['direction'] == "LONG":
        pnl = (exit_price - trade['averageEntryPrice']) * remaining_size
    else:
        pnl = (trade['averageEntryPrice'] - exit_price) * remaining_size
    
    if 'pointValue' in trade:
        pnl *= trade['pointValue']
    
    # Record final exit
    trade['exits'].append({
        "price": exit_price,
        "size": remaining_size,
        "timestamp": timestamp.isoformat(),
        "pnl": pnl,
        "rationale": rationale
    })
    
    # Update status
    trade['status'] = "CLOSED"
    trade['exitRationale'] = rationale
    
    # Update realized P&L
    trade['realizedPnL'] = trade.get('realizedPnL', 0) + pnl
    
    # Calculate realized R
    risk_per_unit = abs(trade['averageEntryPrice'] - trade['stopLoss'])
    if 'pointValue' in trade:
        risk_per_unit *= trade['pointValue']
    realized_r = pnl / (risk_per_unit * remaining_size) if risk_per_unit > 0 else 0
    trade['realizedR'] = round(realized_r, 2)
    
    # Add action
    trade['actions'].append({
        "action": "CLOSE",
        "timestamp": timestamp.isoformat(),
        "details": {
            "exitPrice": exit_price,
            "size": remaining_size,
            "realizedPnL": pnl,
            "realizedR": trade['realizedR'],
            "rationale": rationale
        }
    })
    
    return trade


def trail_stop(trade: dict, trail_distance: float, timestamp: datetime) -> dict:
    """Activate or update trailing stop"""
    # Get current price (would come from live data in production)
    current_price = trade.get('currentPrice', trade['averageEntryPrice'])
    
    if trade['direction'] == "LONG":
        new_stop = current_price - trail_distance
    else:
        new_stop = current_price + trail_distance
    
    # Validate improvement
    if trade['direction'] == "LONG" and new_stop <= trade['stopLoss']:
        raise ValueError("Trailing stop must improve position")
    elif trade['direction'] == "SHORT" and new_stop >= trade['stopLoss']:
        raise ValueError("Trailing stop must improve position")
    
    # Update stop
    trade['stopLossHistory'].append({
        "price": new_stop,
        "timestamp": timestamp.isoformat(),
        "rationale": f"Trailing stop, distance: {trail_distance}"
    })
    trade['stopLoss'] = new_stop
    
    # Add action
    trade['actions'].append({
        "action": "TRAIL",
        "timestamp": timestamp.isoformat(),
        "details": {
            "trailDistance": trail_distance,
            "priceAtTrail": current_price,
            "newStop": new_stop
        }
    })
    
    return trade


def manage_trade(args):
    """Main trade management logic"""
    # Paths
    base_dir = Path(__file__).parent.parent
    
    # Determine which trades file based on symbol
    if hasattr(args, 'symbol') and args.symbol:
        symbol = args.symbol.upper()
        # Check futures symbols
        if symbol in ['ES', 'NQ', 'CL', 'GC', 'SI', 'NG', 'ZB', 'ZN']:
            trades_file = base_dir / "futures-trades.json"
        else:
            trades_file = base_dir / "stock-trades.json"
    else:
        # Try all files
        for filename in ["stock-trades.json", "options-trades.json", "futures-trades.json", "future-options-trades.json"]:
            filepath = base_dir / filename
            if filepath.exists():
                trades_file = filepath
                break
        else:
            raise FileNotFoundError("No trades ledger found")
    
    # Load trades
    ledger = load_trades(trades_file)
    trade, index = find_trade(ledger, args.trade_id)
    
    if not trade:
        raise ValueError(f"Trade not found: {args.trade_id}")
    
    timestamp = datetime.now(timezone.utc)
    
    # Execute action
    if args.action == "ADJUST_STOP":
        if not args.new_stop:
            raise ValueError("--new-stop required for ADJUST_STOP")
        trade = adjust_stop(trade, args.new_stop, args.rationale, timestamp)
    
    elif args.action == "SCALE_OUT":
        if not args.size or not args.exit_price:
            raise ValueError("--size and --exit-price required for SCALE_OUT")
        trade = scale_out(trade, args.size, args.exit_price, timestamp)
    
    elif args.action == "SCALE_IN":
        if not args.size or not args.entry_price:
            raise ValueError("--size and --entry-price required for SCALE_IN")
        trade = scale_in(trade, args.size, args.entry_price, timestamp)
    
    elif args.action == "CLOSE":
        if not args.exit_price:
            raise ValueError("--exit-price required for CLOSE")
        trade = close_position(trade, args.exit_price, args.rationale or "Closed position", timestamp)
    
    elif args.action == "TRAIL":
        if not args.trail_distance:
            raise ValueError("--trail-distance required for TRAIL")
        trade = trail_stop(trade, args.trail_distance, timestamp)
    
    else:
        raise ValueError(f"Unknown action: {args.action}")
    
    # Update timestamp
    trade['updatedAt'] = timestamp.isoformat()
    
    # Save
    ledger['trades'][index] = trade
    save_trades(trades_file, ledger)
    
    print(f"✓ Trade updated: {trade['tradeId']}")
    print(f"  Action: {args.action}")
    print(f"  Status: {trade['status']}")
    
    if args.action == "ADJUST_STOP":
        print(f"  New Stop: {trade['stopLoss']}")
    elif args.action in ["SCALE_OUT", "CLOSE"]:
        print(f"  Realized P&L: ${trade['realizedPnL']:.2f}")
        print(f"  Realized R: {trade['realizedR']}R")
    
    return trade['tradeId']


def main():
    parser = argparse.ArgumentParser(description="Manage an open trade")
    
    parser.add_argument("--trade-id", required=True, help="Trade ID to manage")
    parser.add_argument("--action", required=True, 
                        choices=["ADJUST_STOP", "SCALE_IN", "SCALE_OUT", "CLOSE", "TRAIL"],
                        help="Management action")
    parser.add_argument("--new-stop", type=float, help="New stop loss (for ADJUST_STOP)")
    parser.add_argument("--size", type=float, help="Size to add/reduce (for SCALE_IN/SCALE_OUT)")
    parser.add_argument("--entry-price", type=float, help="Entry price (for SCALE_IN)")
    parser.add_argument("--exit-price", type=float, help="Exit price (for SCALE_OUT/CLOSE)")
    parser.add_argument("--trail-distance", type=float, help="Trailing stop distance (for TRAIL)")
    parser.add_argument("--rationale", help="Rationale for action")
    parser.add_argument("--symbol", help="Symbol (to determine which ledger)")
    
    args = parser.parse_args()
    
    try:
        manage_trade(args)
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
