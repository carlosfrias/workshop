#!/usr/bin/env python3
"""
Portfolio Greeks Calculator

Implements Phase 5.4: Portfolio-level Greek aggregation and position sizing.

Usage:
    python portfolio-greeks.py --positions positions.json
    python portfolio-greeks.py --max-delta 200 --stock-price 175 --option-delta 0.45
"""

import json
import argparse
from pathlib import Path


def calculate_portfolio_greeks(positions: list) -> dict:
    """Calculate aggregate portfolio Greeks.
    
    Args:
        positions: List of position dicts with delta, gamma, theta, vega, rho, contracts, direction
    
    Returns:
        Portfolio-level Greeks aggregation
    """
    portfolio = {
        "netDelta": 0.0,
        "netGamma": 0.0,
        "netTheta": 0.0,
        "netVega": 0.0,
        "netRho": 0.0,
        "totalContracts": 0,
        "positions": len(positions),
        "longDelta": 0.0,
        "shortDelta": 0.0,
        "deltaExposure": 0.0
    }
    
    for pos in positions:
        contracts = pos.get('contracts', 1)
        multiplier = 100  # Standard option multiplier
        direction = pos.get('direction', 'LONG')
        
        # LONG adds to delta, SHORT subtracts (or adds negative delta for puts)
        sign = 1 if direction == "LONG" else -1
        
        delta = pos.get('delta', pos.get('currentDelta', 0)) * contracts * multiplier * sign
        gamma = pos.get('gamma', pos.get('currentGamma', 0)) * contracts * multiplier
        theta = pos.get('theta', pos.get('currentTheta', 0)) * contracts * multiplier * sign
        vega = pos.get('vega', pos.get('currentVega', 0)) * contracts * multiplier
        rho = pos.get('rho', pos.get('currentRho', 0)) * contracts * multiplier * sign
        
        portfolio['netDelta'] += delta
        portfolio['netGamma'] += gamma
        portfolio['netTheta'] += theta
        portfolio['netVega'] += vega
        portfolio['netRho'] += rho
        portfolio['totalContracts'] += contracts
        
        if delta > 0:
            portfolio['longDelta'] += delta
        else:
            portfolio['shortDelta'] += abs(delta)
    
    # Delta exposure = absolute value of net delta
    portfolio['deltaExposure'] = abs(portfolio['netDelta'])
    
    # Round all values
    for key in ['netDelta', 'netGamma', 'netTheta', 'netVega', 'netRho', 'longDelta', 'shortDelta', 'deltaExposure']:
        portfolio[key] = round(portfolio[key], 2)
    
    return portfolio


def calculate_delta_based_sizing(max_delta: float, stock_price: float, option_delta: float) -> dict:
    """Calculate position size based on delta limits.
    
    Args:
        max_delta: Maximum portfolio delta (dollar amount)
        stock_price: Current stock price
        option_delta: Option delta (0-1 for calls, -1-0 for puts)
    
    Returns:
        Position sizing recommendation
    """
    # Max contracts = max_delta / (delta * stock_price * 100)
    delta_per_contract = option_delta * stock_price * 100
    
    if delta_per_contract == 0:
        return {"error": "Delta per contract is zero"}
    
    max_contracts = max_delta / delta_per_contract
    
    return {
        "maxDelta": max_delta,
        "stockPrice": stock_price,
        "optionDelta": option_delta,
        "deltaPerContract": round(delta_per_contract, 2),
        "maxContracts": int(max_contracts),
        "actualDelta": round(int(max_contracts) * delta_per_contract, 2)
    }


def main():
    parser = argparse.ArgumentParser(description="Calculate portfolio Greeks")
    
    parser.add_argument("--positions-file", help="Path to positions JSON file")
    parser.add_argument("--max-delta", type=float, help="Maximum portfolio delta for sizing")
    parser.add_argument("--stock-price", type=float, help="Stock price for sizing calc")
    parser.add_argument("--option-delta", type=float, help="Option delta for sizing calc")
    parser.add_argument("--output", choices=["text", "json"], default="text", help="Output format")
    
    args = parser.parse_args()
    
    if args.positions_file:
        with open(args.positions_file) as f:
            positions = json.load(f).get('positions', [])
        portfolio = calculate_portfolio_greeks(positions)
        
        if args.output == "json":
            print(json.dumps(portfolio, indent=2))
        else:
            print(f"\n{'='*50}")
            print(f"PORTFOLIO GREEKS SUMMARY")
            print(f"{'='*50}")
            print(f"Positions: {portfolio['positions']}")
            print(f"Total Contracts: {portfolio['totalContracts']}")
            print(f"Net Delta: {portfolio['netDelta']:.2f}")
            print(f"Net Gamma: {portfolio['netGamma']:.4f}")
            print(f"Net Theta: {portfolio['netTheta']:.2f}")
            print(f"Net Vega: {portfolio['netVega']:.2f}")
            print(f"Net Rho: {portfolio['netRho']:.4f}")
            print(f"Long Delta: {portfolio['longDelta']:.2f}")
            print(f"Short Delta: {portfolio['shortDelta']:.2f}")
            print(f"Delta Exposure: {portfolio['deltaExposure']:.2f}")
            print(f"{'='*50}\n")
    
    elif args.max_delta and args.stock_price and args.option_delta:
        sizing = calculate_delta_based_sizing(args.max_delta, args.stock_price, args.option_delta)
        
        if args.output == "json":
            print(json.dumps(sizing, indent=2))
        else:
            print(f"\n{'='*40}")
            print(f"DELTA-BASED POSITION SIZING")
            print(f"{'='*40}")
            print(f"Max Delta: ${sizing['maxDelta']:.2f}")
            print(f"Stock Price: ${sizing['stockPrice']:.2f}")
            print(f"Option Delta: {sizing['optionDelta']:.2f}")
            print(f"Delta/Contract: ${sizing['deltaPerContract']:.2f}")
            print(f"Max Contracts: {sizing['maxContracts']}")
            print(f"Actual Delta: ${sizing['actualDelta']:.2f}")
            print(f"{'='*40}\n")


if __name__ == "__main__":
    main()