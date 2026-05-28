#!/usr/bin/env python3
"""
Trading Report Generator

Generates trading reports including:
- Weekly reviews
- Monthly reviews
- Trade summaries
- Performance reports

Usage:
    python generate-report.py --type weekly|monthly|summary|performance
                              --period week|month|30d|90d|all-time
                              [--output md|json|csv]
"""

import json
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Any


def load_trades(log_path: Path) -> List[Dict]:
    """Load trades from trade-log.json"""
    if not log_path.exists():
        return []
    
    with open(log_path, 'r') as f:
        data = json.load(f)
    
    return data.get("trades", [])


def filter_by_period(trades: List[Dict], period: str) -> List[Dict]:
    """Filter trades by time period"""
    now = datetime.now(timezone.utc)
    
    if period == "all-time":
        return trades
    
    elif period == "30d":
        cutoff = now - timedelta(days=30)
        return [t for t in trades 
                if datetime.fromisoformat(t.get("timestamp", "1970-01-01")) > cutoff]
    
    elif period == "90d":
        cutoff = now - timedelta(days=90)
        return [t for t in trades 
                if datetime.fromisoformat(t.get("timestamp", "1970-01-01")) > cutoff]
    
    elif period == "month":
        cutoff = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return [t for t in trades 
                if datetime.fromisoformat(t.get("timestamp", "1970-01-01")) > cutoff]
    
    elif period == "week":
        cutoff = now - timedelta(days=now.weekday() + 1)
        cutoff = cutoff.replace(hour=0, minute=0, second=0, microsecond=0)
        return [t for t in trades 
                if datetime.fromisoformat(t.get("timestamp", "1970-01-01")) > cutoff]
    
    return trades


def calculate_trade_pnl(trade: Dict) -> float:
    """Calculate P&L for a trade"""
    if trade.get("status") == "OPEN":
        return 0.0
    
    return trade.get("realizedPnL", 0.0)


def calculate_trade_r(trade: Dict) -> float:
    """Calculate R-multiple for a trade"""
    if trade.get("status") == "OPEN":
        return 0.0
    
    return trade.get("realizedR", 0.0)


def generate_weekly_review(trades: List[Dict], period: str) -> str:
    """Generate weekly review report"""
    now = datetime.now(timezone.utc)
    week_start = now - timedelta(days=now.weekday() + 1)
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    
    filtered = filter_by_period(trades, period)
    
    # Calculate stats
    total_trades = len(filtered)
    closed_trades = [t for t in filtered if t.get("status") == "CLOSED"]
    winning = [t for t in closed_trades if calculate_trade_r(t) > 0]
    losing = [t for t in closed_trades if calculate_trade_r(t) < 0]
    
    win_rate = len(winning) / len(closed_trades) * 100 if closed_trades else 0
    net_pnl = sum(calculate_trade_pnl(t) for t in closed_trades)
    net_r = sum(calculate_trade_r(t) for t in closed_trades)
    
    # Generate trade table
    trade_rows = []
    for trade in closed_trades:
        r = calculate_trade_r(trade)
        pnl = calculate_trade_pnl(trade)
        outcome = "✓" if r > 0 else "✗" if r < 0 else "○"
        trade_rows.append(
            f"| {outcome} | {trade['tradeId']} | {trade['symbol']} | {trade['direction']} | {r:+.2f}R | ${pnl:+.2f} |"
        )
    
    trade_table = "\n".join(trade_rows) if trade_rows else "| - | No trades this week | - | - | - | - |"
    
    # Wins and losses
    wins = [t for t in closed_trades if calculate_trade_r(t) > 0]
    losses = [t for t in closed_trades if calculate_trade_r(t) < 0]
    
    win_details = []
    for t in wins[:3]:  # Top 3 wins
        win_details.append(f"- **{t['tradeId']}**: {calculate_trade_r(t):+.2f}R (${calculate_trade_pnl(t):+.2f}) - {t.get('entryRationale', 'N/A')[:50]}")
    
    loss_details = []
    for t in losses[:3]:  # Top 3 losses
        loss_details.append(f"- **{t['tradeId']}**: {calculate_trade_r(t):+.2f}R (${calculate_trade_pnl(t):+.2f})")
    
    report = f"""---
report-type: weekly-review
week-start: {week_start.strftime("%Y-%m-%d")}
week-end: {now.strftime("%Y-%m-%d")}
generated: {now.strftime("%Y-%m-%d")}
tags: [report, weekly-review]
---

# Weekly Review — Week of {week_start.strftime("%Y-%m-%d")}

## Summary
- Trades: {total_trades}
- Win Rate: {win_rate:.1f}%
- Net P&L: ${net_pnl:+.2f}
- Net R: {net_r:+.2f}R

## Trades This Week

| Outcome | Trade ID | Symbol | Direction | R-Multiple | P&L |
|---------|----------|--------|-----------|------------|-----|
{trade_table}

## Wins

{chr(10).join(win_details) if win_details else "- No winning trades this week"}

## Losses

{chr(10).join(loss_details) if loss_details else "- No losing trades this week"}

## Lessons Learned

1. *[Add lesson learned]*
2. *[Add lesson learned]*

## Adjustments for Next Week

1. *[Add adjustment]*
2. *[Add adjustment]*

---

*Generated by Trading Journal Report Generator*
"""
    
    return report


def generate_monthly_review(trades: List[Dict], period: str) -> str:
    """Generate monthly review report"""
    now = datetime.now(timezone.utc)
    filtered = filter_by_period(trades, period)
    closed_trades = [t for t in filtered if t.get("status") == "CLOSED"]
    
    # Calculate metrics
    total_trades = len(closed_trades)
    winning = [t for t in closed_trades if calculate_trade_r(t) > 0]
    losing = [t for t in closed_trades if calculate_trade_r(t) < 0]
    
    win_rate = len(winning) / total_trades * 100 if total_trades else 0
    
    # Calculate R-multiples
    r_multiples = [calculate_trade_r(t) for t in closed_trades]
    avg_r = sum(r_multiples) / len(r_multiples) if r_multiples else 0
    net_r = sum(r_multiples)
    
    # P&L
    net_pnl = sum(calculate_trade_pnl(t) for t in closed_trades)
    
    # Profit factor
    gross_profit = sum(calculate_trade_r(t) for t in winning)
    gross_loss = abs(sum(calculate_trade_r(t) for t in losing))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
    
    # Expectancy
    expectancy = avg_r  # Simplified
    
    # Symbol breakdown
    symbols = {}
    for t in closed_trades:
        sym = t.get("symbol", "UNKNOWN")
        if sym not in symbols:
            symbols[sym] = {"trades": 0, "wins": 0, "total_r": 0}
        symbols[sym]["trades"] += 1
        if calculate_trade_r(t) > 0:
            symbols[sym]["wins"] += 1
        symbols[sym]["total_r"] += calculate_trade_r(t)
    
    symbol_rows = []
    for sym, data in symbols.items():
        wr = data["wins"] / data["trades"] * 100 if data["trades"] else 0
        avg = data["total_r"] / data["trades"] if data["trades"] else 0
        symbol_rows.append(f"| {sym} | {data['trades']} | {wr:.1f}% | {avg:+.2f}R |")
    
    symbol_table = "\n".join(symbol_rows) if symbol_rows else "| - | No data | - | - |"
    
    # Top and bottom trades
    sorted_by_r = sorted(closed_trades, key=lambda t: calculate_trade_r(t), reverse=True)
    top_trades = sorted_by_r[:3]
    bottom_trades = sorted_by_r[-3:] if len(sorted_by_r) >= 3 else []
    
    top_rows = []
    for t in top_trades:
        top_rows.append(f"- **{t['tradeId']}**: {calculate_trade_r(t):+.2f}R (${calculate_trade_pnl(t):+.2f})")
    
    bottom_rows = []
    for t in bottom_trades:
        bottom_rows.append(f"- **{t['tradeId']}**: {calculate_trade_r(t):+.2f}R (${calculate_trade_pnl(t):+.2f})")
    
    report = f"""---
report-type: monthly-review
month: {now.strftime("%Y-%m")}
generated: {now.strftime("%Y-%m-%d")}
tags: [report, monthly-review]
---

# Monthly Review — {now.strftime("%B %Y")}

## Performance Summary
- Total Trades: {total_trades}
- Win Rate: {win_rate:.1f}%
- Expectancy: {expectancy:+.2f}R
- Profit Factor: {profit_factor:.2f} if profit_factor != float('inf') else "∞"}
- Net P&L: ${net_pnl:+.2f}
- Net R: {net_r:+.2f}R
- Max Drawdown: *[Calculate from equity curve]*

## Metrics by Symbol

| Symbol | Trades | Win Rate | Avg R |
|--------|--------|----------|-------|
{symbol_table}

## Best Trades

{chr(10).join(top_rows) if top_rows else "- No profitable trades this month"}

## Worst Trades

{chr(10).join(bottom_rows) if bottom_rows else "- No losing trades this month"}

## Patterns Observed

*[Add observations about trading patterns, setups that worked, market conditions, etc.]*

## Goals for Next Month

1. *[Add goal]*
2. *[Add goal]*
3. *[Add goal]*

---

*Generated by Trading Journal Report Generator*
"""
    
    return report


def generate_trade_summary(trades: List[Dict], period: str) -> str:
    """Generate trade summary report"""
    filtered = filter_by_period(trades, period)
    
    rows = []
    for trade in filtered:
        status = trade.get("status", "UNKNOWN")
        r = calculate_trade_r(trade) if status == "CLOSED" else 0
        pnl = calculate_trade_pnl(trade) if status == "CLOSED" else 0
        
        if status == "OPEN":
            outcome = "○"
        else:
            outcome = "✓" if r > 0 else "✗" if r < 0 else "○"
        
        rows.append(
            f"| {outcome} | {trade['tradeId']} | {trade['symbol']} | {trade['direction']} | "
            f"{trade['entryPrice']} | {trade.get('exitPrice', '-')} | {status} | {r:+.2f}R | ${pnl:+.2f} |"
        )
    
    trade_table = "\n".join(rows) if rows else "| - | No trades in period | - | - | - | - | - | - | - |"
    
    report = f"""---
report-type: trade-summary
period: {period}
generated: {datetime.now(timezone.utc).strftime("%Y-%m-%d")}
tags: [report, trade-summary]
---

# Trade Summary — {period}

**Generated:** {datetime.now(timezone.utc).isoformat()}

## All Trades

| Outcome | Trade ID | Symbol | Direction | Entry | Exit | Status | R | P&L |
|---------|----------|--------|-----------|-------|------|--------|---|-----|
{trade_table}

## Summary Stats

- Total Trades: {len(filtered)}
- Open: {len([t for t in filtered if t.get('status') == 'OPEN'])}
- Closed: {len([t for t in filtered if t.get('status') == 'CLOSED'])}

---

*Generated by Trading Journal Report Generator*
"""
    
    return report


def main():
    parser = argparse.ArgumentParser(description="Generate trading reports")
    
    parser.add_argument("--type", required=True,
                        choices=["weekly", "monthly", "summary", "performance"],
                        help="Report type")
    parser.add_argument("--period", default="all-time",
                        choices=["week", "month", "30d", "90d", "all-time"],
                        help="Time period")
    parser.add_argument("--output", default="md", choices=["md", "json", "csv"],
                        help="Output format")
    parser.add_argument("--log-path", type=Path,
                        default=Path(__file__).parent.parent.parent / "trade-entry" / "trade-log.json",
                        help="Path to trade-log.json")
    parser.add_argument("--output-dir", type=Path,
                        default=Path(__file__).parent.parent.parent.parent / "personal-vault" / "01-Projects" / "trading-journal" / "reports",
                        help="Output directory for reports")
    
    args = parser.parse_args()
    
    # Load trades
    trades = load_trades(args.log_path)
    
    if not trades:
        print("No trades found in trade-log.json")
        return
    
    # Generate report
    if args.type == "weekly":
        report = generate_weekly_review(trades, args.period)
    elif args.type == "monthly":
        report = generate_monthly_review(trades, args.period)
    elif args.type == "summary":
        report = generate_trade_summary(trades, args.period)
    else:
        print(f"Report type '{args.type}' not implemented yet")
        return
    
    # Save report
    filename = f"report-{datetime.now().strftime('%Y-%m-%d')}-{args.type}.md"
    output_path = args.output_dir / filename
    
    with open(output_path, 'w') as f:
        f.write(report)
    
    print(f"✓ Report generated: {filename}")
    print(f"  Saved to: {output_path}")


if __name__ == "__main__":
    main()
