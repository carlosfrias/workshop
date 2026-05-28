#!/usr/bin/env python3
"""
Covered Calls Tracker

Implements Phase 5.1: Covered calls tracking with premium, DTE, covered return %.

Usage:
    python covered-calls-tracker.py --symbol AAPL --shares 100 --call-strike 180 \\
        --call-premium 5.50 --call-expiry 2026-06-20 --stock-price 175.00
"""

import json
import argparse
from datetime import datetime, timezone
from pathlib import Path


def calculate_covered_return(call_premium: float, stock_price: float, shares: int = 100) -> float:
    """Calculate covered return percentage"""
    premium_received = call_premium * (shares // 100) * 100
    capital_committed = stock_price * shares
    
    if capital_committed == 0:
        return 0.0
    
    return (premium_received / capital_committed) * 100


def calculate_annualized_return(covered_return: float, dte: int) -> float:
    """Calculate annualized return from covered return and DTE"""
    if dte <= 0:
        return 0.0
    return (covered_return / dte) * 365


def calculate_max_profit(call_strike: float, stock_price: float, call_premium: float) -> float:
    """Calculate max profit on covered call"""
    # Max profit = (strike - stock_price) + premium, capped at premium if below strike
    if call_strike > stock_price:
        return (call_strike - stock_price) + call_premium
    else:
        return call_premium


def calculate_breakeven(stock_price: float, call_premium: float) -> float:
    """Calculate breakeven price for covered call"""
    return stock_price - call_premium


def calculate_downside_protection(stock_price: float, call_premium: float) -> float:
    """Calculate downside protection percentage from premium"""
    return (call_premium / stock_price) * 100


def main():
    parser = argparse.ArgumentParser(description="Track covered calls")
    
    parser.add_argument("--symbol", required=True, help="Underlying stock symbol")
    parser.add_argument("--shares", type=int, default=100, help="Number of shares (default: 100)")
    parser.add_argument("--call-strike", type=float, required=True, help="Call strike price")
    parser.add_argument("--call-premium", type=float, required=True, help="Call premium per share")
    parser.add_argument("--call-expiry", required=True, help="Call expiry date (YYYY-MM-DD)")
    parser.add_argument("--stock-price", type=float, required=True, help="Current stock price")
    parser.add_argument("--output", choices=["text", "json"], default="text", help="Output format")
    
    args = parser.parse_args()
    
    # Calculate DTE
    expiry_date = datetime.strptime(args.call_expiry, "%Y-%m-%d").date()
    today = datetime.now().date()
    dte = (expiry_date - today).days
    
    # Calculate metrics
    covered_return = calculate_covered_return(args.call_premium, args.stock_price, args.shares)
    annualized = calculate_annualized_return(covered_return, dte)
    max_profit = calculate_max_profit(args.call_strike, args.stock_price, args.call_premium)
    breakeven = calculate_breakeven(args.stock_price, args.call_premium)
    downside_protection = calculate_downside_protection(args.stock_price, args.call_premium)
    premium_received = args.call_premium * (args.shares // 100) * 100
    capital_committed = args.stock_price * args.shares
    
    result = {
        "symbol": args.symbol,
        "shares": args.shares,
        "callStrike": args.call_strike,
        "callPremium": args.call_premium,
        "callExpiry": args.call_expiry,
        "dte": dte,
        "stockPrice": args.stock_price,
        "premiumReceived": premium_received,
        "capitalCommitted": capital_committed,
        "coveredReturn": round(covered_return, 2),
        "annualizedReturn": round(annualized, 2),
        "maxProfit": round(max_profit, 2),
        "breakeven": round(breakeven, 2),
        "downsideProtection": round(downside_protection, 2)
    }
    
    if args.output == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"\n{'='*50}")
        print(f"COVERED CALL ANALYSIS — {args.symbol}")
        print(f"{'='*50}")
        print(f"Shares: {args.shares} @ ${args.stock_price:.2f}")
        print(f"Sell {args.call_strike}C @ ${args.call_premium:.2f} exp {args.call_expiry} ({dte} DTE)")
        print(f"\nPremium Received: ${premium_received:,.2f}")
        print(f"Capital Committed: ${capital_committed:,.2f}")
        print(f"Covered Return: {covered_return:.2f}%")
        print(f"Annualized Return: {annualized:.2f}%")
        print(f"Max Profit: ${max_profit:.2f}")
        print(f"Breakeven: ${breakeven:.2f}")
        print(f"Downside Protection: {downside_protection:.2f}%")
        print(f"{'='*50}\n")
    
    return result


if __name__ == "__main__":
    main()