#!/usr/bin/env python3
"""
Trading Analytics Calculator

Calculates performance metrics from trade-log.json including:
- Win rate, expectancy, profit factor
- Average R-multiple, max drawdown, Sharpe ratio
- Segmented analysis by symbol, direction, setup

Usage:
    python calculate-metrics.py [--period all-time|30d|90d|month|week]
                                [--segment symbol|direction|setup]
                                [--output json|text]
"""

import json
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Any
import statistics


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
        return [t for t in trades if t.get("status") == "CLOSED"]
    
    elif period == "30d":
        cutoff = now - timedelta(days=30)
        return [t for t in trades 
                if t.get("status") == "CLOSED" and 
                datetime.fromisoformat(t.get("exitTimestamp", "1970-01-01")) > cutoff]
    
    elif period == "90d":
        cutoff = now - timedelta(days=90)
        return [t for t in trades 
                if t.get("status") == "CLOSED" and 
                datetime.fromisoformat(t.get("exitTimestamp", "1970-01-01")) > cutoff]
    
    elif period == "month":
        cutoff = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return [t for t in trades 
                if t.get("status") == "CLOSED" and 
                datetime.fromisoformat(t.get("exitTimestamp", "1970-01-01")) > cutoff]
    
    elif period == "week":
        cutoff = now - timedelta(days=now.weekday() + 1)
        cutoff = cutoff.replace(hour=0, minute=0, second=0, microsecond=0)
        return [t for t in trades 
                if t.get("status") == "CLOSED" and 
                datetime.fromisoformat(t.get("exitTimestamp", "1970-01-01")) > cutoff]
    
    return trades


def calculate_r_multiple(trade: Dict) -> float:
    """Calculate realized R-multiple for a closed trade"""
    if trade.get("status") != "CLOSED":
        return 0.0
    
    realized_r = trade.get("realizedR", 0.0)
    return realized_r if realized_r else 0.0


def calculate_basic_metrics(trades: List[Dict]) -> Dict[str, Any]:
    """Calculate basic performance metrics"""
    if not trades:
        return {
            "totalTrades": 0,
            "winningTrades": 0,
            "losingTrades": 0,
            "winRate": 0.0,
            "avgWinR": 0.0,
            "avgLossR": 0.0,
            "expectancy": 0.0,
            "profitFactor": 0.0,
            "avgRPerTrade": 0.0
        }
    
    r_multiples = [calculate_r_multiple(t) for t in trades]
    wins = [r for r in r_multiples if r > 0]
    losses = [r for r in r_multiples if r < 0]
    
    total_trades = len(trades)
    winning_trades = len(wins)
    losing_trades = len(losses)
    
    win_rate = winning_trades / total_trades if total_trades > 0 else 0.0
    avg_win_r = statistics.mean(wins) if wins else 0.0
    avg_loss_r = statistics.mean(losses) if losses else 0.0
    
    # Expectancy = (avg win × win%) - (avg loss × loss%)
    expectancy = (avg_win_r * win_rate) - (abs(avg_loss_r) * (1 - win_rate))
    
    # Profit Factor = gross profit / gross loss
    gross_profit = sum(wins) if wins else 0.0
    gross_loss = abs(sum(losses)) if losses else 0.0
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
    
    avg_r_per_trade = statistics.mean(r_multiples) if r_multiples else 0.0
    
    return {
        "totalTrades": total_trades,
        "winningTrades": winning_trades,
        "losingTrades": losing_trades,
        "winRate": round(win_rate, 3),
        "avgWinR": round(avg_win_r, 2),
        "avgLossR": round(avg_loss_r, 2),
        "expectancy": round(expectancy, 2),
        "profitFactor": round(profit_factor, 2) if profit_factor != float('inf') else "∞",
        "avgRPerTrade": round(avg_r_per_trade, 2)
    }


def calculate_drawdown(trades: List[Dict]) -> float:
    """Calculate maximum drawdown using peak-to-trough method on cumulative R curve"""
    if not trades:
        return 0.0
    
    # Sort trades by exit timestamp
    sorted_trades = sorted(
        [t for t in trades if t.get("status") == "CLOSED"],
        key=lambda x: x.get("exitTimestamp", "1970-01-01")
    )
    
    cumulative_r = 0.0
    peak_r = 0.0
    max_drawdown = 0.0
    
    for trade in sorted_trades:
        r = calculate_r_multiple(trade)
        cumulative_r += r
        
        if cumulative_r > peak_r:
            peak_r = cumulative_r
        
        drawdown = peak_r - cumulative_r
        if drawdown > max_drawdown:
            max_drawdown = drawdown
    
    return -max_drawdown  # Return as negative number


def calculate_sharpe_ratio(trades: List[Dict], risk_free_rate: float = 0.0) -> float:
    """Calculate Sharpe ratio (annualized)"""
    if len(trades) < 2:
        return 0.0
    
    r_multiples = [calculate_r_multiple(t) for t in trades if t.get("status") == "CLOSED"]
    
    if not r_multiples:
        return 0.0
    
    avg_r = statistics.mean(r_multiples)
    std_r = statistics.stdev(r_multiples) if len(r_multiples) > 1 else 0.0
    
    if std_r == 0:
        return 0.0
    
    # Annualize (assuming ~252 trading days, but using trades as proxy)
    # Sharpe = (avg - rf) / std * sqrt(252)
    sharpe = (avg_r - risk_free_rate) / std_r * (252 ** 0.5)
    
    return round(sharpe, 2)


def calculate_streaks(trades: List[Dict]) -> Dict[str, int]:
    """Calculate consecutive wins and losses streaks"""
    if not trades:
        return {"consecutiveWins": 0, "consecutiveLosses": 0}
    
    sorted_trades = sorted(
        [t for t in trades if t.get("status") == "CLOSED"],
        key=lambda x: x.get("exitTimestamp", "1970-01-01")
    )
    
    max_wins = 0
    max_losses = 0
    current_wins = 0
    current_losses = 0
    
    for trade in sorted_trades:
        r = calculate_r_multiple(trade)
        
        if r > 0:
            current_wins += 1
            current_losses = 0
            max_wins = max(max_wins, current_wins)
        elif r < 0:
            current_losses += 1
            current_wins = 0
            max_losses = max(max_losses, current_losses)
        else:
            current_wins = 0
            current_losses = 0
    
    return {
        "consecutiveWins": max_wins,
        "consecutiveLosses": max_losses
    }


def segment_by_symbol(trades: List[Dict]) -> Dict[str, Dict]:
    """Segment metrics by symbol"""
    symbols = set(t.get("symbol") for t in trades)
    result = {}
    
    for symbol in symbols:
        symbol_trades = [t for t in trades if t.get("symbol") == symbol]
        metrics = calculate_basic_metrics(symbol_trades)
        result[symbol] = {
            "trades": metrics["totalTrades"],
            "winRate": metrics["winRate"],
            "avgR": metrics["avgRPerTrade"]
        }
    
    return result


def segment_by_direction(trades: List[Dict]) -> Dict[str, Dict]:
    """Segment metrics by direction (LONG/SHORT)"""
    result = {}
    
    for direction in ["LONG", "SHORT"]:
        dir_trades = [t for t in trades if t.get("direction") == direction]
        metrics = calculate_basic_metrics(dir_trades)
        result[direction] = {
            "trades": metrics["totalTrades"],
            "winRate": metrics["winRate"],
            "avgR": metrics["avgRPerTrade"]
        }
    
    return result


def calculate_all_metrics(trades: List[Dict], period: str = "all-time") -> Dict[str, Any]:
    """Calculate all metrics for a given period"""
    filtered_trades = filter_by_period(trades, period)
    
    basic_metrics = calculate_basic_metrics(filtered_trades)
    max_dd = calculate_drawdown(filtered_trades)
    sharpe = calculate_sharpe_ratio(filtered_trades)
    streaks = calculate_streaks(filtered_trades)
    
    return {
        "period": period,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        **basic_metrics,
        "maxDrawdownR": round(max_dd, 2),
        "sharpeRatio": sharpe,
        **streaks,
        "segmentedBySymbol": segment_by_symbol(filtered_trades),
        "segmentedByDirection": segment_by_direction(filtered_trades)
    }


def format_output(metrics: Dict, output_format: str) -> str:
    """Format metrics for output"""
    if output_format == "json":
        return json.dumps(metrics, indent=2)
    
    # Text format
    lines = [
        f"Performance Metrics — {metrics['period']}",
        f"Generated: {metrics['generatedAt']}",
        "",
        "=== Summary ===",
        f"Total Trades: {metrics['totalTrades']}",
        f"Winning: {metrics['winningTrades']}, Losing: {metrics['losingTrades']}",
        f"Win Rate: {metrics['winRate']*100:.1f}%",
        "",
        "=== Performance ===",
        f"Avg Win: {metrics['avgWinR']}R",
        f"Avg Loss: {metrics['avgLossR']}R",
        f"Expectancy: {metrics['expectancy']}R",
        f"Profit Factor: {metrics['profitFactor']}",
        f"Avg per Trade: {metrics['avgRPerTrade']}R",
        "",
        "=== Risk ===",
        f"Max Drawdown: {metrics['maxDrawdownR']}R",
        f"Sharpe Ratio: {metrics['sharpeRatio']}",
        f"Best Win Streak: {metrics['consecutiveWins']}",
        f"Worst Loss Streak: {metrics['consecutiveLosses']}",
    ]
    
    if metrics.get("segmentedBySymbol"):
        lines.extend(["", "=== By Symbol ==="])
        for symbol, data in metrics["segmentedBySymbol"].items():
            lines.append(f"  {symbol}: {data['trades']} trades, {data['winRate']*100:.1f}% win, {data['avgR']}R avg")
    
    if metrics.get("segmentedByDirection"):
        lines.extend(["", "=== By Direction ==="])
        for direction, data in metrics["segmentedByDirection"].items():
            lines.append(f"  {direction}: {data['trades']} trades, {data['winRate']*100:.1f}% win, {data['avgR']}R avg")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Calculate trading performance metrics")
    
    parser.add_argument("--period", default="all-time",
                        choices=["all-time", "30d", "90d", "month", "week"],
                        help="Time period for analysis")
    parser.add_argument("--segment", choices=["symbol", "direction", "setup"],
                        help="Segment analysis (optional)")
    parser.add_argument("--output", default="text", choices=["json", "text"],
                        help="Output format")
    parser.add_argument("--log-path", type=Path,
                        default=Path(__file__).parent.parent / "trade-entry" / "trade-log.json",
                        help="Path to trade-log.json")
    
    args = parser.parse_args()
    
    # Load trades
    trades = load_trades(args.log_path)
    
    if not trades:
        print("No trades found in trade-log.json")
        return
    
    # Calculate metrics
    metrics = calculate_all_metrics(trades, args.period)
    
    # Output
    print(format_output(metrics, args.output))


if __name__ == "__main__":
    main()
