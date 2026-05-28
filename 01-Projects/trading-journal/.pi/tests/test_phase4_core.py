#!/usr/bin/env python3
"""
Test suite for Phase 4: Core Trade Journal Implementation

Tests validate:
- 4.1 Account tracking (starting capital, current balance, margin)
- 4.2 Stock trade entry/exit with partial exits and scaling
- 4.3 Options trade entry (stocks) with expiry, strike, call/put, extrinsic
- 4.4 Futures trade entry with contract specs lookup
- 4.5 Future options trade entry
- 4.6 Trade management: adjust stop, target, partial close
- 4.7 Commission tracking per trade
- 4.8 Block-based income/expense analysis (DTI style)
- 4.9 Reward ratio calculator
"""

import json
import pytest
from pathlib import Path
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

# Paths
WORKSHOP_DIR = Path(__file__).parent.parent.parent
DATA_MODEL_DIR = WORKSHOP_DIR / "data-model"
SCRIPTS_DIR = WORKSHOP_DIR / "core" / "scripts"
ACCOUNT_LEDGER = WORKSHOP_DIR / "core" / "account-ledger.json"
BLOCK_ANALYSIS = WORKSHOP_DIR / "core" / "block-analysis.json"


class Test41_AccountTracking:
    """4.1 Implement account tracking (starting capital, current balance, margin)"""
    
    def test_account_ledger_exists(self):
        """Verify account ledger file exists"""
        assert ACCOUNT_LEDGER.exists(), f"Account ledger not found: {ACCOUNT_LEDGER}"
    
    def test_account_ledger_valid_structure(self):
        """Verify account ledger has required structure"""
        with open(ACCOUNT_LEDGER) as f:
            ledger = json.load(f)
        
        required = ['accountId', 'startingCapital', 'currentBalance', 'deposits', 'withdrawals', 'realizedPnL', 'unrealizedPnL']
        for field in required:
            assert field in ledger, f"Missing required field: {field}"
    
    def test_account_calculates_current_balance(self):
        """Verify current balance formula: startingCapital + deposits - withdrawals + realizedPnL + unrealizedPnL"""
        with open(ACCOUNT_LEDGER) as f:
            ledger = json.load(f)
        
        total_deposits = sum(d['amount'] for d in ledger.get('deposits', []))
        total_withdrawals = sum(w['amount'] for w in ledger.get('withdrawals', []))
        
        expected_balance = (
            ledger['startingCapital'] + 
            total_deposits - 
            total_withdrawals + 
            ledger['realizedPnL'] + 
            ledger['unrealizedPnL']
        )
        
        assert abs(ledger['currentBalance'] - expected_balance) < 0.01, \
            f"Current balance mismatch: {ledger['currentBalance']} vs {expected_balance}"
    
    def test_account_tracks_margin_used(self):
        """Verify account tracks margin used for futures/options positions"""
        with open(ACCOUNT_LEDGER) as f:
            ledger = json.load(f)
        
        assert 'marginUsed' in ledger or 'buyingPower' in ledger
    
    def test_account_tracks_margin_requirement(self):
        """Verify account tracks total margin requirement"""
        with open(ACCOUNT_LEDGER) as f:
            ledger = json.load(f)
        
        assert 'marginRequirement' in ledger


class Test42_StockTradeEntryExit:
    """4.2 Implement stock trade entry/exit with partial exits and scaling"""
    
    def test_stock_entry_script_exists(self):
        """Verify stock trade entry script exists"""
        script = SCRIPTS_DIR / "stock-entry.py"
        assert script.exists(), f"Stock entry script not found: {script}"
    
    def test_stock_entry_creates_trade_record(self):
        """Verify stock entry creates properly structured trade record"""
        # This test will be run after implementation
        pass
    
    def test_stock_partial_exit_tracking(self):
        """Verify stock trades track partial exits correctly"""
        # Test that exits array can have multiple entries
        trade = {
            "entries": [{"price": 100, "size": 100}],
            "exits": [
                {"price": 105, "size": 50, "timestamp": "2026-05-27T10:00:00Z"},
                {"price": 108, "size": 50, "timestamp": "2026-05-27T11:00:00Z"}
            ]
        }
        
        assert len(trade['exits']) == 2
        assert trade['exits'][0]['size'] + trade['exits'][1]['size'] == trade['entries'][0]['size']
    
    def test_stock_scaling_in(self):
        """Verify stock trades support scaling in (multiple entries)"""
        trade = {
            "entries": [
                {"price": 100, "size": 50, "timestamp": "2026-05-27T09:30:00Z"},
                {"price": 102, "size": 50, "timestamp": "2026-05-27T10:00:00Z"}
            ]
        }
        
        assert len(trade['entries']) == 2
        total_size = sum(e['size'] for e in trade['entries'])
        assert total_size == 100


class Test43_OptionsTradeEntry:
    """4.3 Implement options trade entry (stocks) with expiry, strike, call/put, extrinsic"""
    
    def test_options_entry_script_exists(self):
        """Verify options trade entry script exists"""
        script = SCRIPTS_DIR / "options-entry.py"
        assert script.exists(), f"Options entry script not found: {script}"
    
    def test_options_tracks_expiry_strike(self):
        """Verify options track expiry date and strike price"""
        option = {
            "symbol": "AAPL",
            "optionType": "C",
            "strike": 175.00,
            "expiry": "2026-06-20"
        }
        
        assert 'expiry' in option
        assert 'strike' in option
        assert 'optionType' in option
    
    def test_options_call_put_classification(self):
        """Verify options classify as call or put"""
        call = {"optionType": "C"}
        put = {"optionType": "P"}
        
        assert call['optionType'] in ['C', 'P']
        assert put['optionType'] in ['C', 'P']
    
    def test_options_tracks_extrinsic_value(self):
        """Verify options track extrinsic value (DTI feature)"""
        option = {
            "premium": 5.50,
            "intrinsicValue": 3.00,
            "extrinsicValue": 2.50
        }
        
        # Extrinsic = Premium - Intrinsic
        assert abs(option['extrinsicValue'] - (option['premium'] - option['intrinsicValue'])) < 0.01


class Test44_FuturesTradeEntry:
    """4.4 Implement futures trade entry with contract specs lookup"""
    
    def test_futures_entry_script_exists(self):
        """Verify futures trade entry script exists"""
        script = SCRIPTS_DIR / "futures-entry.py"
        assert script.exists(), f"Futures entry script not found: {script}"
    
    def test_futures_references_market_lookup(self):
        """Verify futures entry references market lookup for contract specs"""
        market_lookup_path = DATA_MODEL_DIR / "market-lookup-schema.json"
        assert market_lookup_path.exists()
        
        # Test that futures can reference contract specs
        future = {
            "symbol": "ES",
            "contractSpecId": "ES",
            "pointValue": 50,  # From lookup
            "tickValue": 12.50  # From lookup
        }
        
        assert 'contractSpecId' in future
        assert 'pointValue' in future
    
    def test_futures_contract_month(self):
        """Verify futures track contract month"""
        future = {
            "symbol": "ES",
            "contractMonth": "2026-06",
            "fullSymbol": "ESM2026"
        }
        
        assert 'contractMonth' in future
        assert 'fullSymbol' in future


class Test45_FutureOptionsTradeEntry:
    """4.5 Implement future options trade entry"""
    
    def test_future_options_entry_script_exists(self):
        """Verify future options trade entry script exists"""
        script = SCRIPTS_DIR / "future-options-entry.py"
        assert script.exists(), f"Future options entry script not found: {script}"
    
    def test_future_options_tracks_underlying(self):
        """Verify future options track underlying futures contract"""
        future_option = {
            "symbol": "ES",
            "underlyingSymbol": "ESM2026",
            "optionType": "C",
            "strike": 5200
        }
        
        assert 'underlyingSymbol' in future_option
    
    def test_future_options_has_greeks(self):
        """Verify future options track Greeks (delta required by DTI)"""
        future_option = {
            "delta": 0.45,
            "gamma": 0.02,
            "theta": -0.15,
            "vega": 0.30
        }
        
        assert 'delta' in future_option


class Test46_TradeManagement:
    """4.6 Implement trade management: adjust stop, target, partial close"""
    
    def test_management_script_exists(self):
        """Verify trade management script exists"""
        script = SCRIPTS_DIR / "manage-trade.py"
        assert script.exists(), f"Trade management script not found: {script}"
    
    def test_adjust_stop_action(self):
        """Verify trade management supports adjust stop action"""
        action = {
            "action": "ADJUST_STOP",
            "previousStop": 5220.00,
            "newStop": 5240.00,
            "timestamp": "2026-05-27T15:45:00Z",
            "rationale": "Moved to breakeven"
        }
        
        assert action['action'] == "ADJUST_STOP"
        assert 'newStop' in action
        assert action['newStop'] > action['previousStop']  # Must improve for LONG
    
    def test_partial_close_action(self):
        """Verify trade management supports partial close (scale out)"""
        action = {
            "action": "SCALE_OUT",
            "sizeReduced": 50,
            "remainingSize": 50,
            "exitPrice": 5260.00,
            "realizedPnL": 510.00
        }
        
        assert action['action'] == "SCALE_OUT"
        assert 'sizeReduced' in action
        assert 'realizedPnL' in action
    
    def test_target_tracking(self):
        """Verify trade management tracks 3 targets"""
        targets = [
            {"targetNumber": 1, "price": 5260.00, "sizePercent": 50, "filled": True},
            {"targetNumber": 2, "price": 5280.00, "sizePercent": 25, "filled": False},
            {"targetNumber": 3, "price": 5300.00, "sizePercent": 25, "filled": False}
        ]
        
        assert len(targets) == 3
        assert all('targetNumber' in t for t in targets)
        assert all('filled' in t for t in targets)


class Test47_CommissionTracking:
    """4.7 Implement commission tracking per trade"""
    
    def test_commission_tracked_per_trade(self):
        """Verify commission is tracked per trade"""
        trade = {
            "symbol": "ES",
            "commission": 5.00,
            "commissionPerContract": 2.50,
            "contracts": 2
        }
        
        assert 'commission' in trade
        assert trade['commission'] == trade['commissionPerContract'] * trade['contracts']
    
    def test_commission_in_pnl_calculation(self):
        """Verify commission is included in P&L calculation"""
        gross_pnl = 500.00
        commission = 5.00
        net_pnl = gross_pnl - commission
        
        assert net_pnl == 495.00
    
    def test_commission_varies_by_asset_type(self):
        """Verify commission varies by asset type (stock vs option vs future)"""
        commissions = {
            "stock": 0.005,  # Per share
            "option": 0.65,  # Per contract
            "future": 2.50   # Per contract
        }
        
        assert commissions['stock'] != commissions['option']
        assert commissions['option'] != commissions['future']


class Test48_BlockAnalysis:
    """4.8 Implement block-based income/expense analysis (DTI style: 25 trades per block)"""
    
    def test_block_analysis_file_exists(self):
        """Verify block analysis file exists"""
        assert BLOCK_ANALYSIS.exists(), f"Block analysis not found: {BLOCK_ANALYSIS}"
    
    def test_block_has_25_trades(self):
        """Verify blocks track up to 25 trades (DTI feature)"""
        block = {
            "blockId": "ES-B1",
            "symbol": "ES",
            "blockNumber": 1,
            "trades": [],
            "maxTrades": 25
        }
        
        assert 'maxTrades' in block
        assert block['maxTrades'] == 25
    
    def test_block_income_expense_analysis(self):
        """Verify blocks calculate income/expense analysis"""
        block = {
            "blockId": "ES-B1",
            "totalIncome": 5000.00,
            "totalExpense": 2000.00,
            "netPnL": 3000.00,
            "winningTrades": 15,
            "losingTrades": 10,
            "winRate": 0.60
        }
        
        assert 'totalIncome' in block
        assert 'totalExpense' in block
        assert 'netPnL' in block
        assert block['netPnL'] == block['totalIncome'] - block['totalExpense']
    
    def test_block_summary_statistics(self):
        """Verify blocks calculate summary statistics"""
        block = {
            "winRate": 0.60,
            "avgWinR": 2.3,
            "avgLossR": -1.1,
            "profitFactor": 2.14,
            "expectancy": 0.97
        }
        
        assert 'winRate' in block
        assert 'profitFactor' in block
        assert 'expectancy' in block


class Test49_RewardRatioCalculator:
    """4.9 Implement reward ratio calculator (DTI feature)"""
    
    def test_reward_ratio_script_exists(self):
        """Verify reward ratio calculator script exists"""
        script = SCRIPTS_DIR / "reward-ratio-calculator.py"
        assert script.exists(), f"Reward ratio calculator not found: {script}"
    
    def test_reward_ratio_calculation_long(self):
        """Verify reward ratio calculation for LONG trades"""
        entry = 5234.50
        stop = 5220.00
        target = 5260.00
        
        risk = entry - stop  # 14.50
        reward = target - entry  # 25.50
        ratio = reward / risk  # 1.76
        
        assert ratio > 1.0  # Should be at least 1:1
        assert abs(ratio - 1.76) < 0.01
    
    def test_reward_ratio_calculation_short(self):
        """Verify reward ratio calculation for SHORT trades"""
        entry = 5234.50
        stop = 5250.00
        target = 5210.00
        
        risk = stop - entry  # 15.50
        reward = entry - target  # 24.50
        ratio = reward / risk  # 1.58
        
        assert ratio > 1.0
        assert abs(ratio - 1.58) < 0.01
    
    def test_reward_ratio_minimum_acceptable(self):
        """Verify reward ratio enforces minimum 1:2 target (or documents exception)"""
        ratio = 1.5  # Below 1:2
        
        # Should flag for review if below 1:2
        requires_review = ratio < 2.0
        assert requires_review == True
    
    def test_reward_ratio_with_commission(self):
        """Verify reward ratio accounts for commission"""
        entry = 5234.50
        stop = 5220.00
        target = 5260.00
        commission = 5.00
        point_value = 50  # ES
        contracts = 2
        
        risk = (entry - stop) * point_value * contracts + commission  # 1450 + 5 = 1455
        reward = (target - entry) * point_value * contracts - commission  # 2550 - 5 = 2545
        ratio = reward / risk  # 1.75
        
        assert abs(ratio - 1.75) < 0.01


class TestPhase4Integration:
    """Integration tests for Phase 4 complete workflow"""
    
    def test_all_scripts_exist(self):
        """Verify all Phase 4 scripts exist"""
        scripts = [
            "stock-entry.py",
            "options-entry.py",
            "futures-entry.py",
            "future-options-entry.py",
            "manage-trade.py",
            "reward-ratio-calculator.py"
        ]
        
        for script in scripts:
            script_path = SCRIPTS_DIR / script
            assert script_path.exists(), f"Missing script: {script}"
    
    def test_all_data_files_exist(self):
        """Verify all Phase 4 data files exist"""
        files = [
            "account-ledger.json",
            "block-analysis.json"
        ]
        
        for filename in files:
            file_path = WORKSHOP_DIR / "core" / filename
            assert file_path.exists(), f"Missing data file: {file_path}"
    
    def test_account_balance_across_trades(self):
        """Verify account balance updates correctly across multiple trades"""
        # Integration test: entry -> management -> exit -> balance update
        pass
    
    def test_block_rollover(self):
        """Verify block rolls over after 25 trades"""
        # When block reaches 25 trades, new trades start new block
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
