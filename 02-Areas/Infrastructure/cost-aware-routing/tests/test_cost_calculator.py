#!/usr/bin/env python3
"""Unit tests for cost_calculator.py"""

import json
import os
import tempfile
import sys

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from cost_calculator import (
    compute_hardware_cost,
    compute_node_hourly_cost,
    compute_cost_per_1k_tokens,
    compute_score,
    validate_billing_tiers,
)

import pytest


class TestComputeHardwareCost:
    def test_15gb_node(self):
        assert compute_hardware_cost(15) == 500.0

    def test_31gb_node(self):
        assert compute_hardware_cost(31) == 800.0

    def test_64gb_node(self):
        assert compute_hardware_cost(64) == 1200.0

    def test_boundary_16gb(self):
        assert compute_hardware_cost(16) == 500.0

    def test_boundary_32gb(self):
        assert compute_hardware_cost(32) == 800.0


class TestComputeNodeHourlyCost:
    def test_15gb_node_hourly(self):
        hourly = compute_node_hourly_cost(15)
        # 500 / (3*8760) + 0.018 = 0.01903 + 0.018 ≈ 0.0370
        assert 0.036 < hourly < 0.038

    def test_31gb_node_hourly(self):
        hourly = compute_node_hourly_cost(31)
        # 800 / (3*8760) + 0.018 = 0.03044 + 0.018 ≈ 0.0484
        assert 0.047 < hourly < 0.050

    def test_zero_ram_uses_fallback(self):
        hourly = compute_node_hourly_cost(0)
        assert hourly > 0  # Should use smallest tier, not crash

    def test_custom_power_rate(self):
        hourly_default = compute_node_hourly_cost(15)
        hourly_high = compute_node_hourly_cost(15, electricity_rate=0.20)
        assert hourly_high > hourly_default


class TestComputeCostPer1kTokens:
    def test_typical_local(self):
        # 31GB node, gemma4:e4b at 5.5 t/s
        hourly = 0.0367
        cost = compute_cost_per_1k_tokens(5.5, hourly)
        # 0.0367 / (5.5 * 3600) * 1000 = 0.00185
        assert 0.001 < cost < 0.003

    def test_zero_tps(self):
        assert compute_cost_per_1k_tokens(0, 0.0367) == 0.0

    def test_zero_cost(self):
        assert compute_cost_per_1k_tokens(5.5, 0) == 0.0

    def test_high_tps_low_cost(self):
        cost = compute_cost_per_1k_tokens(100, 0.01)
        assert cost < 0.001  # Very efficient


class TestComputeScore:
    def test_all_components(self):
        result = compute_score(
            tps=5.5, max_tps=6.18,
            model_size_gb=9.6, node_capacity_gb=25.0,
            candidate_cost=0.002, min_cost=0.001, max_cost=0.003,
        )
        assert 0 < result["total_score"] < 1
        assert "tps_norm" in result
        assert "fit_score" in result
        assert "cost_score" in result

    def test_cheaper_gets_higher_cost_score(self):
        cheap = compute_score(5.0, 6.0, 5.0, 25.0, 0.001, 0.001, 0.005)
        expensive = compute_score(5.0, 6.0, 5.0, 25.0, 0.005, 0.001, 0.005)
        assert cheap["cost_score"] > expensive["cost_score"]

    def test_better_fit_gets_higher_fit_score(self):
        good_fit = compute_score(5.0, 6.0, 8.0, 10.0, 0.002, 0.001, 0.005)
        bad_fit = compute_score(5.0, 6.0, 2.0, 25.0, 0.002, 0.001, 0.005)
        assert good_fit["fit_score"] > bad_fit["fit_score"]


class TestValidateBillingTiers:
    def test_valid_tiers(self):
        errors = validate_billing_tiers()
        assert len(errors) == 0

    def test_invalid_price(self):
        tiers = {"tiers": [{"id": "bad", "name": "Bad", "model": "test", "venue": "local", "price_per_1k_tokens": -1, "margin_pct": 40, "provider": "ollama"}]}
        errors = validate_billing_tiers(tiers)
        assert any("price must be > 0" in e for e in errors)

    def test_local_too_expensive(self):
        tiers = {"tiers": [{"id": "bad_local", "name": "Bad Local", "model": "test", "venue": "local", "price_per_1k_tokens": 0.05, "margin_pct": 40, "provider": "ollama"}]}
        errors = validate_billing_tiers(tiers)
        assert any("exceeds" in e for e in errors)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])