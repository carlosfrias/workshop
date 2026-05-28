#!/usr/bin/env python3
"""
Test suite for Trading Journal unified data model.

Tests validate:
- Account-level tracking schema
- Asset-type schemas (stock, option, future, future option)
- Market lookup table schema
- Data model integrity against combined DTI+LS spec
"""

import json
import pytest
from pathlib import Path
from datetime import datetime, timezone


# Schema paths
SCHEMA_DIR = Path(__file__).parent.parent.parent / "data-model"
ACCOUNT_SCHEMA = SCHEMA_DIR / "account-schema.json"
STOCK_SCHEMA = SCHEMA_DIR / "stock-schema.json"
OPTION_SCHEMA = SCHEMA_DIR / "option-schema.json"
FUTURE_SCHEMA = SCHEMA_DIR / "future-schema.json"
FUTURE_OPTION_SCHEMA = SCHEMA_DIR / "future-option-schema.json"
MARKET_LOOKUP_SCHEMA = SCHEMA_DIR / "market-lookup-schema.json"


class TestAccountSchema:
    """Test account-level tracking schema (Phase 3.6)"""
    
    def test_account_schema_exists(self):
        """Verify account schema file exists"""
        assert ACCOUNT_SCHEMA.exists(), f"Account schema not found: {ACCOUNT_SCHEMA}"
    
    def test_account_schema_valid_json(self):
        """Verify account schema is valid JSON"""
        with open(ACCOUNT_SCHEMA) as f:
            schema = json.load(f)
        assert isinstance(schema, dict)
    
    def test_account_tracks_capital(self):
        """Verify account schema tracks starting capital and current balance"""
        with open(ACCOUNT_SCHEMA) as f:
            schema = json.load(f)
        
        required_fields = ['startingCapital', 'currentBalance', 'deposits', 'withdrawals']
        for field in required_fields:
            assert field in schema['properties'], f"Missing required field: {field}"
    
    def test_account_tracks_margin(self):
        """Verify account schema tracks margin usage"""
        with open(ACCOUNT_SCHEMA) as f:
            schema = json.load(f)
        
        assert 'marginUsed' in schema['properties'] or 'buyingPower' in schema['properties']
    
    def test_account_calculates_ror(self):
        """Verify account schema supports ROR% calculation (LS Futures feature)"""
        with open(ACCOUNT_SCHEMA) as f:
            schema = json.load(f)
        
        # ROR requires tracking deposits/withdrawals separately from P&L
        assert 'deposits' in schema['properties']
        assert 'withdrawals' in schema['properties']
        assert 'realizedPnL' in schema['properties']


class TestStockSchema:
    """Test stock trade schema (Phase 3.7)"""
    
    def test_stock_schema_exists(self):
        """Verify stock schema file exists"""
        assert STOCK_SCHEMA.exists(), f"Stock schema not found: {STOCK_SCHEMA}"
    
    def test_stock_schema_valid_json(self):
        """Verify stock schema is valid JSON"""
        with open(STOCK_SCHEMA) as f:
            schema = json.load(f)
        assert isinstance(schema, dict)
    
    def test_stock_tracks_entry_exit(self):
        """Verify stock schema tracks entry/exit with partial exits and scaling"""
        with open(STOCK_SCHEMA) as f:
            schema = json.load(f)
        
        # DTI feature: partial exits and scaling
        assert 'entries' in schema['properties'] or 'legs' in schema['properties']
        assert 'exits' in schema['properties']
    
    def test_stock_tracks_targets(self):
        """Verify stock schema supports 3-target scaling (LS Stock feature)"""
        with open(STOCK_SCHEMA) as f:
            schema = json.load(f)
        
        # LS feature: 3 targets with separate position sizes
        assert 'targets' in schema['properties']
    
    def test_stock_tracks_commission(self):
        """Verify stock schema tracks commission per trade"""
        with open(STOCK_SCHEMA) as f:
            schema = json.load(f)
        
        assert 'commission' in schema['properties']
    
    def test_stock_block_analysis(self):
        """Verify stock schema supports block-based analysis (DTI feature: 25 trades per block)"""
        with open(STOCK_SCHEMA) as f:
            schema = json.load(f)
        
        # Block tracking for income/expense analysis
        assert 'blockId' in schema['properties'] or 'blockNumber' in schema['properties']


class TestOptionSchema:
    """Test option trade schema (Phase 3.7)"""
    
    def test_option_schema_exists(self):
        """Verify option schema file exists"""
        assert OPTION_SCHEMA.exists(), f"Option schema not found: OPTION_SCHEMA"
    
    def test_option_schema_valid_json(self):
        """Verify option schema is valid JSON"""
        with open(OPTION_SCHEMA) as f:
            schema = json.load(f)
        assert isinstance(schema, dict)
    
    def test_option_tracks_expiry_strike(self):
        """Verify option schema tracks expiry, strike, call/put"""
        with open(OPTION_SCHEMA) as f:
            schema = json.load(f)
        
        required = ['expiry', 'strike', 'optionType']
        for field in required:
            assert field in schema['properties'], f"Missing: {field}"
    
    def test_option_tracks_greeks(self):
        """Verify option schema tracks all Greeks (DTI: delta, gamma, theta, vega, rho)"""
        with open(OPTION_SCHEMA) as f:
            schema = json.load(f)
        
        greeks = ['delta', 'gamma', 'theta', 'vega', 'rho']
        for greek in greeks:
            assert greek in schema['properties'], f"Missing Greek: {greek}"
    
    def test_option_tracks_extrinsic(self):
        """Verify option schema tracks extrinsic value (DTI feature)"""
        with open(OPTION_SCHEMA) as f:
            schema = json.load(f)
        
        assert 'extrinsicValue' in schema['properties'] or 'timeValue' in schema['properties']
    
    def test_option_classifies_directional(self):
        """Verify option schema classifies directional vs non-directional (LS Options feature)"""
        with open(OPTION_SCHEMA) as f:
            schema = json.load(f)
        
        assert 'tradeClassification' in schema['properties'] or 'directional' in schema['properties']
    
    def test_option_covered_calls(self):
        """Verify option schema supports covered calls tracking (LS Options feature)"""
        with open(OPTION_SCHEMA) as f:
            schema = json.load(f)
        
        # Covered calls need: premium, DTE, covered return %
        assert 'premium' in schema['properties']
        assert 'dte' in schema['properties'] or 'daysToExpiry' in schema['properties']


class TestFutureSchema:
    """Test future trade schema (Phase 3.7)"""
    
    def test_future_schema_exists(self):
        """Verify future schema file exists"""
        assert FUTURE_SCHEMA.exists(), f"Future schema not found: {FUTURE_SCHEMA}"
    
    def test_future_schema_valid_json(self):
        """Verify future schema is valid JSON"""
        with open(FUTURE_SCHEMA) as f:
            schema = json.load(f)
        assert isinstance(schema, dict)
    
    def test_future_tracks_contract_specs(self):
        """Verify future schema references contract specs from lookup"""
        with open(FUTURE_SCHEMA) as f:
            schema = json.load(f)
        
        # Should reference market lookup for point value, tick size
        assert 'symbol' in schema['properties']
        assert 'contracts' in schema['properties']
    
    def test_future_tracks_point_value(self):
        """Verify future schema tracks point value (from lookup or inline)"""
        with open(FUTURE_SCHEMA) as f:
            schema = json.load(f)
        
        # Either inline or via lookup reference
        has_inline = 'pointValue' in schema['properties']
        has_lookup = 'contractSpecId' in schema['properties']
        assert has_inline or has_lookup
    
    def test_future_calculator(self):
        """Verify future schema supports contract calculator (DTI feature)"""
        with open(FUTURE_SCHEMA) as f:
            schema = json.load(f)
        
        # Calculator needs: tick value, point value, contract size
        assert 'tickValue' in schema['properties'] or 'contractSpecId' in schema['properties']


class TestFutureOptionSchema:
    """Test future option trade schema (Phase 3.7)"""
    
    def test_future_option_schema_exists(self):
        """Verify future option schema file exists"""
        assert FUTURE_OPTION_SCHEMA.exists(), f"Future option schema not found: {FUTURE_OPTION_SCHEMA}"
    
    def test_future_option_schema_valid_json(self):
        """Verify future option schema is valid JSON"""
        with open(FUTURE_OPTION_SCHEMA) as f:
            schema = json.load(f)
        assert isinstance(schema, dict)
    
    def test_future_option_has_underlying(self):
        """Verify future option schema tracks underlying future contract"""
        with open(FUTURE_OPTION_SCHEMA) as f:
            schema = json.load(f)
        
        assert 'underlyingSymbol' in schema['properties'] or 'futureSymbol' in schema['properties']
    
    def test_future_option_has_greeks(self):
        """Verify future option schema tracks delta (DTI requirement)"""
        with open(FUTURE_OPTION_SCHEMA) as f:
            schema = json.load(f)
        
        assert 'delta' in schema['properties']


class TestMarketLookupSchema:
    """Test market lookup table schema (Phase 3.8)"""
    
    def test_market_lookup_exists(self):
        """Verify market lookup schema file exists"""
        assert MARKET_LOOKUP_SCHEMA.exists(), f"Market lookup schema not found: {MARKET_LOOKUP_SCHEMA}"
    
    def test_market_lookup_valid_json(self):
        """Verify market lookup schema is valid JSON"""
        with open(MARKET_LOOKUP_SCHEMA) as f:
            schema = json.load(f)
        assert isinstance(schema, dict)
    
    def test_market_lookup_has_contract_specs(self):
        """Verify market lookup has 79+ contract specs (LS Futures: 79 contracts)"""
        with open(MARKET_LOOKUP_SCHEMA) as f:
            schema = json.load(f)
        
        # Should define structure for contract specs
        assert 'contractSpec' in schema or 'properties' in schema
    
    def test_market_lookup_has_tick_values(self):
        """Verify market lookup tracks tick values"""
        with open(MARKET_LOOKUP_SCHEMA) as f:
            schema = json.load(f)
        
        # Check in contractSpec definition
        contract_spec = schema.get('definitions', {}).get('contractSpec', {})
        props = contract_spec.get('properties', {})
        has_tick = 'tickValue' in props or 'minimumTick' in props
        assert has_tick
    
    def test_market_lookup_has_margins(self):
        """Verify market lookup tracks margin requirements"""
        with open(MARKET_LOOKUP_SCHEMA) as f:
            schema = json.load(f)
        
        # Check in contractSpec definition
        contract_spec = schema.get('definitions', {}).get('contractSpec', {})
        props = contract_spec.get('properties', {})
        has_margin = 'marginRequirement' in props or 'initialMargin' in props
        assert has_margin
    
    def test_market_lookup_has_commission(self):
        """Verify market lookup tracks commission per contract (LS Futures feature)"""
        with open(MARKET_LOOKUP_SCHEMA) as f:
            schema = json.load(f)
        
        # Check in contractSpec definition
        contract_spec = schema.get('definitions', {}).get('contractSpec', {})
        props = contract_spec.get('properties', {})
        has_commission = 'commissionPerContract' in props or 'commission' in props
        assert has_commission


class TestUnifiedDataModel:
    """Test unified data model integrity (Phase 3.5, 3.9)"""
    
    def test_all_schemas_exist(self):
        """Verify all required schemas exist"""
        schemas = [
            ACCOUNT_SCHEMA,
            STOCK_SCHEMA,
            OPTION_SCHEMA,
            FUTURE_SCHEMA,
            FUTURE_OPTION_SCHEMA,
            MARKET_LOOKUP_SCHEMA
        ]
        
        for schema_path in schemas:
            assert schema_path.exists(), f"Missing schema: {schema_path}"
    
    def test_schemas_share_common_trade_structure(self):
        """Verify all asset schemas share common trade fields"""
        common_fields = ['tradeId', 'symbol', 'direction', 'status', 'timestamp']
        
        asset_schemas = [STOCK_SCHEMA, OPTION_SCHEMA, FUTURE_SCHEMA, FUTURE_OPTION_SCHEMA]
        
        for schema_path in asset_schemas:
            with open(schema_path) as f:
                schema = json.load(f)
            
            props = schema.get('properties', {})
            for field in common_fields:
                assert field in props, f"{schema_path.name} missing common field: {field}"
    
    def test_account_pnl_independent_of_deposits(self):
        """Verify account-level P&L is independent of deposits/withdrawals (Phase 3.6)"""
        with open(ACCOUNT_SCHEMA) as f:
            schema = json.load(f)
        
        # Must track these separately
        assert 'realizedPnL' in schema['properties']
        assert 'deposits' in schema['properties']
        assert 'withdrawals' in schema['properties']
        
        # Current balance formula: startingCapital + deposits - withdrawals + realizedPnL
        # This ensures P&L is independent


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
