#!/usr/bin/env python3
"""Unit tests for billing_tiers.json consistency"""

import json
import os
import sys

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..")
BILLING_TIERS_PATH = os.path.join(PROJECT_ROOT, "config", "billing_tiers.json")
COST_DEFAULTS_PATH = os.path.join(PROJECT_ROOT, "config", "cost_defaults.json")

import pytest


class TestBillingTiersFile:
    def test_file_exists(self):
        assert os.path.exists(BILLING_TIERS_PATH)

    def test_valid_json(self):
        with open(BILLING_TIERS_PATH) as f:
            data = json.load(f)
        assert "tiers" in data
        assert len(data["tiers"]) > 0

    def test_local_tiers_cheaper_than_cloud(self):
        with open(BILLING_TIERS_PATH) as f:
            data = json.load(f)

        local_prices = [t["price_per_1k_tokens"] for t in data["tiers"] if t["venue"] == "local"]
        cloud_prices = [t["price_per_1k_tokens"] for t in data["tiers"] if t["venue"] == "cloud"]

        assert max(local_prices) < min(cloud_prices), "Local tiers should be cheaper than cloud"

    def test_each_tier_has_required_fields(self):
        with open(BILLING_TIERS_PATH) as f:
            data = json.load(f)

        required = {"id", "name", "model", "venue", "price_per_1k_tokens", "margin_pct", "provider"}
        for tier in data["tiers"]:
            missing = required - set(tier.keys())
            assert not missing, f"Tier {tier.get('id', '?')} missing fields: {missing}"


class TestCostDefaultsFile:
    def test_file_exists(self):
        assert os.path.exists(COST_DEFAULTS_PATH)

    def test_valid_json(self):
        with open(COST_DEFAULTS_PATH) as f:
            data = json.load(f)
        assert "hardware_costs" in data
        assert "power" in data
        assert "depreciation" in data

    def test_hardware_tiers_complete(self):
        with open(COST_DEFAULTS_PATH) as f:
            data = json.load(f)

        tiers = data["hardware_costs"]["tiers"]
        assert len(tiers) >= 3  # At least 16GB, 32GB, >32GB tiers


if __name__ == "__main__":
    pytest.main([__file__, "-v"])