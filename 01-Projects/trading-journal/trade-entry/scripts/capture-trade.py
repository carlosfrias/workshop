#!/usr/bin/env python3
"""
Trade Entry Capture Script

Captures a new trade entry, updates trade-log.json, and creates a journal note.

Usage:
    python capture-trade.py --symbol ES --direction LONG --entry 5234.50 \
        --size 2 --stop 5220.00 --target 5260.00 --rationale "Breakout above resistance"
"""

import json
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path
import re


def generate_trade_id(symbol: str, direction: str, timestamp: datetime) -> str:
    """Generate trade ID in format YYYYMMDD-HHMM-SYMBOL-DIRECTION"""
    ts = timestamp.strftime("%Y%m%d-%H%M")
    return f"{ts}-{symbol}-{direction}"


def calculate_risk_reward(entry: float, stop: float, targets: list, direction: str) -> tuple:
    """Calculate risk-reward ratio and risk amount"""
    if direction == "LONG":
        risk_per_share = entry - stop
        rewards = [(t - entry) for t in targets]
    else:  # SHORT
        risk_per_share = stop - entry
        rewards = [(entry - t) for t in targets]
    
    if risk_per_share <= 0:
        raise ValueError("Stop loss must be worse than entry price")
    
    primary_reward = rewards[0] if rewards else 0
    rr_ratio = primary_reward / risk_per_share
    
    return f"1:{rr_ratio:.1f}", risk_per_share


def load_trade_log(log_path: Path) -> dict:
    """Load existing trade log or create new structure"""
    if log_path.exists():
        with open(log_path, 'r') as f:
            return json.load(f)
    else:
        return {
            "metadata": {
                "version": "1.0.0",
                "createdAt": datetime.now(timezone.utc).isoformat(),
                "updatedAt": datetime.now(timezone.utc).isoformat(),
                "description": "Trading journal trade log - structured trade data"
            },
            "trades": []
        }


def save_trade_log(log_path: Path, data: dict):
    """Save trade log with updated timestamp"""
    data["metadata"]["updatedAt"] = datetime.now(timezone.utc).isoformat()
    with open(log_path, 'w') as f:
        json.dump(data, f, indent=2)


def create_journal_note(template_path: Path, journal_dir: Path, trade_data: dict) -> Path:
    """Create journal note from template"""
    with open(template_path, 'r') as f:
        template = f.read()
    
    # Replace template variables
    note_content = template
    for key, value in trade_data.items():
        if isinstance(value, list):
            value = ", ".join(map(str, value))
        note_content = note_content.replace(f"{{{{{key}}}}}", str(value))
    
    # Handle special transformations
    note_content = note_content.replace(
        "{{SYMBOL|lower}}", 
        trade_data["SYMBOL"].lower()
    )
    
    # Generate filename
    date_str = datetime.now().strftime("%Y-%m-%d-%H%M")
    filename = f"{date_str}-{trade_data['SYMBOL']}.md"
    note_path = journal_dir / filename
    
    with open(note_path, 'w') as f:
        f.write(note_content)
    
    return note_path


def capture_trade(args):
    """Main trade capture logic"""
    # Paths
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent.parent  # workshop/01-Projects/trading-journal
    log_path = base_dir / "trade-entry" / "trade-log.json"
    template_path = base_dir.parent.parent.parent / "personal-vault" / "01-Projects" / "trading-journal" / "journal" / "TRADE-TEMPLATE.md"
    journal_dir = base_dir.parent.parent.parent / "personal-vault" / "01-Projects" / "trading-journal" / "journal"
    
    # Validate template exists
    if not template_path.exists():
        print(f"Error: Template not found at {template_path}")
        sys.exit(1)
    
    # Generate trade data
    timestamp = datetime.now(timezone.utc)
    trade_id = generate_trade_id(args.symbol, args.direction, timestamp)
    
    # Parse take profit targets (can be multiple)
    targets = args.target if isinstance(args.target, list) else [args.target]
    
    # Calculate risk-reward
    rr_ratio, risk_per_share = calculate_risk_reward(
        args.entry, args.stop, targets, args.direction
    )
    risk_amount = risk_per_share * args.size
    
    trade_data = {
        "tradeId": trade_id,
        "symbol": args.symbol.upper(),
        "direction": args.direction.upper(),
        "entryPrice": args.entry,
        "positionSize": args.size,
        "stopLoss": args.stop,
        "takeProfit": targets,
        "riskReward": rr_ratio,
        "riskAmount": round(risk_amount, 2),
        "entryRationale": args.rationale,
        "timestamp": timestamp.isoformat(),
        "status": "OPEN"
    }
    
    # Load existing trade log
    trade_log = load_trade_log(log_path)
    
    # Check for duplicate (same symbol, open position)
    for trade in trade_log["trades"]:
        if (trade["symbol"] == trade_data["symbol"] and 
            trade["status"] == "OPEN"):
            print(f"Warning: Open position already exists for {trade_data['symbol']}")
            print(f"  Existing trade: {trade['tradeId']}")
            if not args.force:
                print("Use --force to add anyway")
                sys.exit(1)
    
    # Add trade to log
    trade_log["trades"].append({
        **trade_data,
        "actions": [{
            "action": "ENTRY",
            "timestamp": timestamp.isoformat(),
            "details": {
                "price": args.entry,
                "size": args.size,
                "rationale": args.rationale
            }
        }]
    })
    
    # Save trade log
    save_trade_log(log_path, trade_log)
    print(f"✓ Trade logged: {trade_id}")
    print(f"  Symbol: {trade_data['symbol']} {trade_data['direction']}")
    print(f"  Entry: {args.entry}, Stop: {args.stop}, Target: {targets}")
    print(f"  Risk-Reward: {rr_ratio}, Risk Amount: ${risk_amount:.2f}")
    
    # Create journal note
    journal_template_vars = {
        "TRADE_ID": trade_id,
        "SYMBOL": trade_data["symbol"],
        "DIRECTION": trade_data["direction"],
        "DATE": datetime.now().strftime("%Y-%m-%d"),
        "ENTRY_PRICE": str(args.entry),
        "POSITION_SIZE": str(args.size),
        "STOP_LOSS": str(args.stop),
        "TAKE_PROFIT": ", ".join(map(str, targets)),
        "RISK_REWARD": rr_ratio,
        "RISK_AMOUNT": f"{risk_amount:.2f}",
        "ENTRY_RATIONALE": args.rationale
    }
    
    note_path = create_journal_note(template_path, journal_dir, journal_template_vars)
    print(f"✓ Journal note created: {note_path.name}")
    
    return trade_id


def main():
    parser = argparse.ArgumentParser(description="Capture a new trade entry")
    
    parser.add_argument("--symbol", required=True, help="Symbol (e.g., ES, NQ)")
    parser.add_argument("--direction", required=True, choices=["LONG", "SHORT"], 
                        help="Trade direction")
    parser.add_argument("--entry", type=float, required=True, help="Entry price")
    parser.add_argument("--size", type=float, required=True, help="Position size")
    parser.add_argument("--stop", type=float, required=True, help="Stop loss level")
    parser.add_argument("--target", type=float, required=True, action="append",
                        help="Take profit target (can specify multiple)")
    parser.add_argument("--rationale", required=True, help="Entry rationale/setup")
    parser.add_argument("--force", action="store_true", 
                        help="Force entry even if position already open")
    
    args = parser.parse_args()
    
    try:
        capture_trade(args)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
