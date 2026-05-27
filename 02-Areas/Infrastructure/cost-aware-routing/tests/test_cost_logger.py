#!/usr/bin/env python3
"""Unit tests for cost_logger.py"""

import json
import os
import tempfile
import sys

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from cost_logger import log_cost, get_cost_per_1k, load_billing_tiers

import pytest


class TestGetCostPer1k:
    def test_known_model(self):
        cost = get_cost_per_1k("qwen3.5:4b")
        assert cost == 0.005

    def test_unknown_model_returns_default(self):
        cost = get_cost_per_1k("nonexistent:model")
        assert cost == 0.015  # Default cloud standard rate


class TestLogCost:
    def test_log_creates_record(self):
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
            log_path = f.name

        try:
            record = log_cost("test-001", "qwen3:8b", 100, 50, log_path=log_path)
            assert record["task_id"] == "test-001"
            assert record["model"] == "qwen3:8b"
            assert record["tokens_input"] == 100
            assert record["tokens_output"] == 50
            assert record["cost_usd"] > 0
            assert record["billing_tier"] == "local_standard"

            # Verify written to file
            with open(log_path) as f:
                lines = f.readlines()
            assert len(lines) == 1
            written = json.loads(lines[0])
            assert written["task_id"] == "test-001"
        finally:
            os.unlink(log_path)

    def test_multiple_appends(self):
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
            log_path = f.name

        try:
            log_cost("t1", "qwen3.5:4b", 100, 50, log_path=log_path)
            log_cost("t2", "gemma4:e4b", 200, 100, log_path=log_path)

            with open(log_path) as f:
                lines = f.readlines()
            assert len(lines) == 2
        finally:
            os.unlink(log_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])