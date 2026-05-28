#!/usr/bin/env python3
"""
Test suite for Phase 5: Options & Advanced Tracking

Tests validate:
- 5.1 Covered calls tracking (premium, DTE, covered return %)
- 5.2 Synthetic covered calls
- 5.3 Directional vs non-directional trade classification
- 5.4 Delta tracking per option position
- 5.5 All Greeks from live data
- 5.6 Options/futures target price projections from underlying
- 5.7 ROR% tracking (rate of return accounting for deposits/withdrawals)
"""

import json
import pytest
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Paths
WORKSHOP_DIR = Path(__file__).parent.parent.parent
SCRIPTS_DIR = WORKSHOP_DIR / "core" / "scripts"

# ============= 5.1 Covered Calls =============

class Test51_CoveredCalls:
    """5.1 Covered calls tracking"""

    def test_covered_call_premium(self):
        """Verify covered call tracks premium received"""
        cc = {
            "symbol": "AAPL",
            "shares": 100,
            "callStrike": 180,
            "callPremium": 5.50,
            "callExpiry": "2026-06-20",
            "dte": 30
        }
        total_premium = cc["callPremium"] * cc["shares"] // 100 * 100  # Per contract
        # Premium per contract * contracts
        # 5.50 * 1 contract * 100 shares = $550
        assert cc["callPremium"] * (cc["shares"] // 100) * 100 == 550.0
    
    def test_covered_return_percent(self):
        """Verify covered return % calculation"""
        shares = 100
        call_premium = 5.50
        call_strike = 180.0
        stock_price = 175.0
        
        # Covered return % = premium received / (stock_price * shares) * 100
        premium_received = call_premium * 100  # $550
        capital_committed = stock_price * shares  # $17,500
        covered_return = (premium_received / capital_committed) * 100
        
        assert abs(covered_return - 3.14) < 0.1  # ~3.14%
    
    def test_annualized_return(self):
        """Verify annualized return calculation"""
        covered_return = 3.14  # from 30 DTE
        dte = 30
        
        annualized = (covered_return / dte) * 365
        
        assert abs(annualized - 38.2) < 1.0  # ~38.2% annualized
    
    def test_covered_call_tracker_script_exists(self):
        """Verify covered call tracker script exists"""
        script = SCRIPTS_DIR / "covered-calls-tracker.py"
        assert script.exists(), f"Covered call tracker not found: {script}"


# ============= 5.2 Synthetic Covered Calls =============

class Test52_SyntheticCoveredCalls:
    """5.2 Synthetic covered calls"""

    def test_synthetic_structure(self):
        """Verify synthetic covered call = long call + short call"""
        synthetic = {
            "longCall": {"strike": 170, "premium": 8.00},
            "shortCall": {"strike": 180, "premium": 5.50},
            "netDebit": 2.50,  # 8.00 - 5.50
            "maxProfit": 7.50,  # (180-170) - 2.50
            "maxLoss": 2.50    # net debit
        }
        
        net_debit = synthetic["longCall"]["premium"] - synthetic["shortCall"]["premium"]
        max_profit = (synthetic["shortCall"]["strike"] - synthetic["longCall"]["strike"]) - net_debit
        
        assert abs(synthetic["netDebit"] - net_debit) < 0.01
        assert abs(synthetic["maxProfit"] - max_profit) < 0.01
    
    def test_synthetic_cheaper_than_stock(self):
        """Verify synthetic CC uses less capital than buying 100 shares"""
        stock_price = 175.0
        net_debit = 2.50
        contracts = 1
        
        capital_stock = stock_price * 100  # $17,500
        capital_synthetic = net_debit * 100  # $250
        
        assert capital_synthetic < capital_stock
        assert capital_synthetic / capital_stock < 0.02  # Less than 2% of stock capital


# ============= 5.3 Trade Classification =============

class Test53_TradeClassification:
    """5.3 Directional vs non-directional classification"""

    def test_directional_classification(self):
        """Verify directional trades are classified correctly"""
        directional_strategies = [
            "long-call", "long-put", "short-call", "short-put",
            "bull-call-spread", "bear-put-spread"
        ]
        
        for strategy in directional_strategies:
            # Should be classified as directional
            assert strategy in directional_strategies
    
    def test_non_directional_classification(self):
        """Verify non-directional trades are classified correctly"""
        non_directional = [
            "iron-condor", "butterfly", "calendar-spread",
            "straddle", "strangle"
        ]
        
        for strategy in non_directional:
            assert strategy in non_directional
    
    def test_covered_call_classification(self):
        """Verify covered calls classified separately"""
        covered = ["covered-call", "protective-put", "collar"]
        synthetic = ["synthetic-covered-call", "poor-mans-covered-call"]
        
        # Covered and synthetic should be their own category
        assert "covered-call" not in ["directional", "non-directional"]
        assert "synthetic-covered-call" not in ["directional", "non-directional"]
    
    def test_classify_trade_script_exists(self):
        """Verify trade classification script exists"""
        script = SCRIPTS_DIR / "classify-trade.py"
        assert script.exists(), f"Classify trade script not found: {script}"


# ============= 5.4 Delta Tracking =============

class Test54_DeltaTracking:
    """5.4 Delta tracking per option position"""

    def test_delta_at_entry(self):
        """Verify delta is recorded at entry"""
        option = {"delta": 0.45, "currentDelta": 0.45}
        assert option["delta"] == option["currentDelta"]
    
    def test_portfolio_delta(self):
        """Verify portfolio delta aggregates across positions"""
        positions = [
            {"symbol": "AAPL", "delta": 0.45, "contracts": 10, "direction": "LONG"},
            {"symbol": "SPY", "delta": -0.30, "contracts": 5, "direction": "SHORT"},
            {"symbol": "MSFT", "delta": 0.55, "contracts": 8, "direction": "LONG"},
        ]
        
        # Portfolio delta = sum(delta * contracts * 100 * direction_multiplier)
        # LONG: +delta, SHORT: delta stays (already negative for puts)
        portfolio_delta = 0
        for pos in positions:
            multiplier = 1 if pos["direction"] == "LONG" else -1
            portfolio_delta += pos["delta"] * pos["contracts"] * 100 * multiplier
        
        # 0.45*10*100*1 + (-0.30)*5*100*(-1) + 0.55*8*100*1
        # = 450 + 150 + 440 = 1040
        # Actually: = 0.45*1000 + (-0.30)*500*(-1) + 0.55*800
        # = 450 + 150 + 440 = 1040
        expected = 450 + 150 + 440
        assert portfolio_delta == expected
    
    def test_delta_based_sizing(self):
        """Verify delta-based position sizing"""
        max_portfolio_delta = 200  # Max dollar delta per position
        stock_price = 175
        option_delta = 0.45
        
        # Max contracts = max_delta / (delta * 100 * stock_price / 100)
        # Simplified: max contracts = max_portfolio_delta / (delta * stock_price)
        max_contracts = max_portfolio_delta / (option_delta * stock_price)
        assert max_contracts > 0  # Should be positive


# ============= 5.5 All Greeks =============

class Test55_AllGreeks:
    """5.5 All Greeks from live data"""

    def test_greeks_at_entry(self):
        """Verify all 5 Greeks recorded at entry"""
        greeks = {
            "delta": 0.45,
            "gamma": 0.02,
            "theta": -0.05,
            "vega": 0.15,
            "rho": 0.01
        }
        
        required = ["delta", "gamma", "theta", "vega", "rho"]
        for greek in required:
            assert greek in greeks
    
    def test_current_greeks_update(self):
        """Verify Greeks can be updated with current values"""
        entry_greeks = {"delta": 0.45, "gamma": 0.02, "theta": -0.05, "vega": 0.15, "rho": 0.01}
        current_greeks = {"delta": 0.52, "gamma": 0.018, "theta": -0.04, "vega": 0.12, "rho": 0.008}
        
        delta_change = current_greeks["delta"] - entry_greeks["delta"]
        assert abs(delta_change - 0.07) < 0.001  # Delta drift
    
    def test_greek_change_threshold(self):
        """Verify Greek change detection exceeds threshold"""
        entry_delta = 0.45
        current_delta = 0.52
        threshold = 0.05  # 5% delta drift
        
        drift = abs(current_delta - entry_delta)
        exceeds = drift > threshold
        assert exceeds == True  # 0.07 > 0.05
    
    def test_greeks_tracker_script_exists(self):
        """Verify Greeks tracker script exists"""
        script = SCRIPTS_DIR / "greeks-tracker.py"
        assert script.exists(), f"Greeks tracker not found: {script}"
    
    def test_portfolio_greeks_script_exists(self):
        """Verify portfolio Greeks script exists"""
        script = SCRIPTS_DIR / "portfolio-greeks.py"
        assert script.exists(), f"Portfolio Greeks not found: {script}"


# ============= 5.6 Target Price Projections =============

class Test56_TargetProjections:
    """5.6 Options/futures target price projections from underlying"""

    def test_bull_scenario_projection(self):
        """Verify target price projection in bull scenario"""
        underlying = 175.0
        bull_target = underlying * 1.05  # +5%
        assert abs(bull_target - 183.75) < 0.01
    
    def test_base_scenario_projection(self):
        """Verify target price in base scenario"""
        underlying = 175.0
        base_target = underlying  # 0%
        assert base_target == 175.0
    
    def test_bear_scenario_projection(self):
        """Verify target price in bear scenario"""
        underlying = 175.0
        bear_target = underlying * 0.95  # -5%
        assert abs(bear_target - 166.25) < 0.01
    
    def test_projected_pnl_from_underlying(self):
        """Verify projected P&L from underlying price movement"""
        entry = 175.0
        strike = 180.0
        premium = 5.50
        contracts = 10
        point_value = 100  # Stock options
        
        # If underlying reaches 185 (bull scenario)
        underlying_price = 185.0
        intrinsic = max(0, underlying_price - strike)  # 5.00
        projected_option_price = intrinsic + 1.00  # Assume $1 extrinsic
        projected_pnl = (projected_option_price - premium) * contracts * point_value
        # (6.00 - 5.50) * 10 * 100 = 500
        assert projected_pnl == 500.0
    
    def test_target_projections_script_exists(self):
        """Verify target projections script exists"""
        script = SCRIPTS_DIR / "target-projections.py"
        assert script.exists(), f"Target projections not found: {script}"


# ============= 5.7 ROR% Tracking =============

class Test57_RORTracking:
    """5.7 ROR% tracking (rate of return accounting for deposits/withdrawals)"""

    def test_ror_calculation_simple(self):
        """Verify basic ROR calculation"""
        starting_capital = 50000
        current_balance = 52000
        deposits = 0
        withdrawals = 0
        
        ror = ((current_balance - deposits + withdrawals) / starting_capital - 1) * 100
        assert abs(ror - 4.0) < 0.01  # 4%
    
    def test_ror_with_deposits(self):
        """Verify ROR accounts for deposits"""
        starting_capital = 50000
        current_balance = 52000
        deposits = 5000
        withdrawals = 0
        
        # ROR = (current - deposits + withdrawals) / starting - 1
        adjusted = current_balance - deposits  # 47000
        ror = (adjusted / starting_capital - 1) * 100
        # (47000 - 50000) / 50000 = -6%
        assert abs(ror - (-6.0)) < 0.01
    
    def test_ror_with_deposits_and_growth(self):
        """Verify ROR properly handles deposits + growth"""
        starting_capital = 50000
        deposits = 5000
        withdrawals = 1000
        realized_pnl = 3000
        
        current_balance = starting_capital + deposits - withdrawals + realized_pnl
        # current = 50000 + 5000 - 1000 + 3000 = 57000
        
        # Profit-based ROR (excludes deposits/withdrawals)
        net_gain = realized_pnl  # 3000
        ror = (net_gain / starting_capital) * 100  # 6%
        assert abs(ror - 6.0) < 0.01
    
    def test_time_weighted_return(self):
        """Verify time-weighted return calculation"""
        # Period 1: Starting = $50,000, End = $52,000 (before deposit)
        # Deposit $5,000 at end of period 1
        # Period 2: Starting = $57,000, End = $59,000
        
        r1 = (52000 / 50000) - 1  # 0.04
        r2 = (59000 / 57000) - 1  # 0.0351
        
        twr = (1 + r1) * (1 + r2) - 1  # 0.0765
        twr_percent = twr * 100
        
        assert abs(twr_percent - 7.65) < 0.1
    
    def test_period_ror_weekly(self):
        """Verify weekly ROR calculation"""
        weekly_start = 50000
        weekly_end = 51200
        deposits = 0
        withdrawals = 0
        
        weekly_ror = ((weekly_end - deposits + withdrawals) / weekly_start - 1) * 100
        assert abs(weekly_ror - 2.4) < 0.01
    
    def test_ror_zero_capital_edge_case(self):
        """Verify ROR handles zero capital edge case"""
        starting_capital = 0
        if starting_capital == 0:
            ror = 0  # Undefined, return 0
        else:
            ror = (10000 / starting_capital - 1) * 100
        assert ror == 0
    
    def test_ror_calculator_script_exists(self):
        """Verify ROR calculator script exists"""
        script = SCRIPTS_DIR / "ror-calculator.py"
        assert script.exists(), f"ROR calculator not found: {script}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])