#!/usr/bin/env python3
"""
ROR Calculator

Implements Phase 5.7: Rate of return accounting for deposits/withdrawals.

Calculates:
- Simple ROR% (accounting for deposits/withdrawals)
- Time-weighted return (TWR)
- Period-based ROR (weekly, monthly, YTD)

Usage:
    python ror-calculator.py --starting-capital 50000 --current-balance 52000 \\
        --deposits 5000 --withdrawals 1000 --realized-pnl 3000
    python ror-calculator.py --starting-capital 50000 --periods weekly
"""

import json
import argparse
from datetime import datetime, timezone
from pathlib import Path


def calculate_simple_ror(starting_capital: float, current_balance: float,
                         deposits: float = 0, withdrawals: float = 0) -> dict:
    """Calculate simple ROR% accounting for deposits/withdrawals.
    
    ROR = (currentBalance - deposits + withdrawals) / startingCapital - 1
    This isolates trading performance from cash flows.
    """
    if starting_capital == 0:
        return {"ror": 0, "rorPercent": 0, "error": "Starting capital is zero"}
    
    # Trading profit = current balance - deposits + withdrawals - starting capital
    trading_profit = current_balance - deposits + withdrawals - starting_capital
    
    # ROR based on starting capital (not modified by deposits)
    ror = trading_profit / starting_capital
    ror_percent = ror * 100
    
    # Simple balance change (includes deposits/withdrawals)
    simple_change = (current_balance / starting_capital - 1) * 100
    
    return {
        "startingCapital": starting_capital,
        "currentBalance": current_balance,
        "deposits": deposits,
        "withdrawals": withdrawals,
        "tradingProfit": round(trading_profit, 2),
        "ror": round(ror, 4),
        "rorPercent": round(ror_percent, 2),
        "simpleChangePercent": round(simple_change, 2)
    }


def calculate_time_weighted_return(periods: list) -> dict:
    """Calculate time-weighted return (TWR).
    
    Each period: {start_balance, end_balance, deposits, withdrawals}
    TWR = product(1 + r_i) - 1 where r_i = (end - deposits + withdrawals - start) / start
    """
    twr_periods = []
    cumulative_return = 1.0
    
    for i, period in enumerate(periods):
        start = period['start_balance']
        end = period['end_balance']
        deps = period.get('deposits', 0)
        wd = period.get('withdrawals', 0)
        
        # Adjust for cash flows
        adjusted_start = start  # Balance at start
        adjusted_end = end - deps + wd  # Remove cash flow impact
        
        if start == 0:
            period_return = 0
        else:
            period_return = (adjusted_end - adjusted_start) / adjusted_start
        
        cumulative_return *= (1 + period_return)
        
        twr_periods.append({
            "period": i + 1,
            "startBalance": start,
            "endBalance": end,
            "deposits": deps,
            "withdrawals": wd,
            "periodReturn": round(period_return, 4),
            "periodReturnPercent": round(period_return * 100, 2)
        })
    
    twr = cumulative_return - 1
    twr_percent = twr * 100
    
    return {
        "periods": twr_periods,
        "timeWeightedReturn": round(twr, 4),
        "timeWeightedReturnPercent": round(twr_percent, 2)
    }


def calculate_period_ror(starting_capital: float, period_start: float, period_end: float,
                         deposits: float = 0, withdrawals: float = 0, 
                         period_type: str = "weekly") -> dict:
    """Calculate ROR for a specific period."""
    if period_start == 0:
        return {"ror": 0, "rorPercent": 0, "error": "Period start balance is zero"}
    
    trading_profit = period_end - deposits + withdrawals - period_start
    ror = trading_profit / period_start
    ror_percent = ror * 100
    
    # Annualize based on period type
    annualization_factors = {
        "daily": 252,
        "weekly": 52,
        "monthly": 12,
        "quarterly": 4,
        "ytd": 1  # Already annualized for YTD
    }
    
    factor = annualization_factors.get(period_type, 1)
    annualized = ror_percent * factor if factor > 1 else ror_percent
    
    return {
        "periodType": period_type,
        "periodStart": period_start,
        "periodEnd": period_end,
        "deposits": deposits,
        "withdrawals": withdrawals,
        "tradingProfit": round(trading_profit, 2),
        "ror": round(ror, 4),
        "rorPercent": round(ror_percent, 2),
        "annualizedPercent": round(annualized, 2)
    }


def main():
    parser = argparse.ArgumentParser(description="Calculate Rate of Return")
    
    # Simple ROR
    parser.add_argument("--starting-capital", type=float, help="Starting capital")
    parser.add_argument("--current-balance", type=float, help="Current balance")
    parser.add_argument("--deposits", type=float, default=0, help="Total deposits")
    parser.add_argument("--withdrawals", type=float, default=0, help="Total withdrawals")
    parser.add_argument("--realized-pnl", type=float, default=0, help="Realized P&L")
    
    # Period-based
    parser.add_argument("--period", choices=["daily", "weekly", "monthly", "quarterly", "ytd"],
                       help="Period type for ROR calculation")
    parser.add_argument("--period-start", type=float, help="Period start balance")
    parser.add_argument("--period-end", type=float, help="Period end balance")
    
    # Account ledger path
    parser.add_argument("--account-ledger", help="Path to account-ledger.json for auto-calculation")
    
    parser.add_argument("--output", choices=["text", "json"], default="text", help="Output format")
    
    args = parser.parse_args()
    
    results = {}
    
    # Simple ROR calculation
    if args.starting_capital and args.current_balance is not None:
        # Use realized P&L if provided, otherwise calculate from balance
        if args.realized_pnl:
            current = args.starting_capital + args.deposits - args.withdrawals + args.realized_pnl
        else:
            current = args.current_balance
        
        results['simple_ror'] = calculate_simple_ror(
            args.starting_capital, current,
            args.deposits, args.withdrawals
        )
    
    # Period-based ROR
    if args.period and args.period_start and args.period_end:
        results['period_ror'] = calculate_period_ror(
            args.starting_capital or args.period_start,
            args.period_start, args.period_end,
            args.deposits, args.withdrawals, args.period
        )
    
    # Account ledger auto-calculation
    if args.account_ledger:
        ledger_path = Path(args.account_ledger)
        if ledger_path.exists():
            with open(ledger_path) as f:
                ledger = json.load(f)
            
            results['simple_ror'] = calculate_simple_ror(
                ledger['startingCapital'],
                ledger['currentBalance'],
                sum(d['amount'] for d in ledger.get('deposits', [])),
                sum(w['amount'] for w in ledger.get('withdrawals', []))
            )
    
    # Time-weighted return example
    example_periods = [
        {"start_balance": 50000, "end_balance": 52000, "deposits": 0, "withdrawals": 0},
        {"start_balance": 57000, "end_balance": 59000, "deposits": 5000, "withdrawals": 0}
    ]
    results['twr_example'] = calculate_time_weighted_return(example_periods)
    
    if args.output == "json":
        print(json.dumps(results, indent=2))
    else:
        print(f"\n{'='*50}")
        print(f"RATE OF RETURN ANALYSIS")
        print(f"{'='*50}")
        
        if 'simple_ror' in results:
            r = results['simple_ror']
            print(f"Starting Capital: ${r['startingCapital']:,.2f}")
            print(f"Current Balance: ${r['currentBalance']:,.2f}")
            print(f"Deposits: ${r['deposits']:,.2f}")
            print(f"Withdrawals: ${r['withdrawals']:,.2f}")
            print(f"Trading Profit: ${r['tradingProfit']:,.2f}")
            print(f"ROR: {r['rorPercent']:.2f}%")
            print(f"Simple Change: {r['simpleChangePercent']:.2f}%")
        
        if 'period_ror' in results:
            p = results['period_ror']
            print(f"\n{p['periodType'].upper()} ROR: {p['rorPercent']:.2f}%")
            print(f"Annualized: {p['annualizedPercent']:.2f}%")
        
        if 'twr_example' in results:
            t = results['twr_example']
            print(f"\nTime-Weighted Return: {t['timeWeightedReturnPercent']:.2f}%")
        
        print(f"{'='*50}\n")


if __name__ == "__main__":
    main()