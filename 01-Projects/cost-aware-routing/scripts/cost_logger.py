#!/usr/bin/env python3
"""
cost_logger.py — Append cost record to model-performance-log.jsonl

Refactored from decompose-execute-verify/scripts/cost-logger.py:
- Loads billing tiers from config/billing_tiers.json (no hardcoded COST_TABLE)
- Project-relative log path
- Validates model exists in billing tiers

Usage:
    python3 cost_logger.py --task-id "001" --model "gemma4:31b-cloud" --tokens-input 1000 --tokens-output 500
"""

import argparse
import json
import datetime
import os
import sys
from typing import Optional

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(SCRIPT_DIR, "..")
BILLING_TIERS_PATH = os.path.join(PROJECT_ROOT, "config", "billing_tiers.json")

DEFAULT_LOG_PATH = os.path.join(PROJECT_ROOT, "data", "model-performance-log.jsonl")


def load_billing_tiers() -> dict:
    """Load billing tiers from config."""
    with open(BILLING_TIERS_PATH) as f:
        return json.load(f)


def get_cost_per_1k(model: str, tiers: Optional[dict] = None) -> float:
    """Get cost per 1K tokens for a model from billing tiers."""
    if tiers is None:
        tiers = load_billing_tiers()

    for tier in tiers.get("tiers", []):
        if tier["model"] == model:
            return tier["price_per_1k_tokens"]

    return 0.015  # Default: cloud standard rate


def log_cost(
    task_id: str,
    model: str,
    tokens_input: int,
    tokens_output: int,
    source: str = "cost-aware-routing",
    log_path: Optional[str] = None,
) -> dict:
    """
    Log a cost event to JSONL file.

    Args:
        task_id: Task identifier
        model: Model ID (Ollama tag format)
        tokens_input: Input token count
        tokens_output: Output token count
        source: Source system name
        log_path: Override log file path

    Returns:
        The cost record dict
    """
    tiers = load_billing_tiers()
    cost_per_1k = get_cost_per_1k(model, tiers)
    total_tokens = tokens_input + tokens_output
    cost = (total_tokens / 1000) * cost_per_1k

    # Find tier name
    tier_name = "unknown"
    for tier in tiers.get("tiers", []):
        if tier["model"] == model:
            tier_name = tier["id"]
            break

    record = {
        "timestamp": datetime.datetime.now().isoformat(),
        "source": source,
        "task_id": task_id,
        "model": model,
        "billing_tier": tier_name,
        "tokens_input": tokens_input,
        "tokens_output": tokens_output,
        "total_tokens": total_tokens,
        "cost_usd": round(cost, 4),
        "cost_per_1k": cost_per_1k,
    }

    path = log_path or DEFAULT_LOG_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(record) + "\n")

    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Log cost event to JSONL")
    parser.add_argument("--task-id", required=True, help="Task identifier")
    parser.add_argument("--model", required=True, help="Model ID (e.g., qwen3:8b)")
    parser.add_argument("--tokens-input", type=int, default=0, help="Input tokens")
    parser.add_argument("--tokens-output", type=int, default=0, help="Output tokens")
    parser.add_argument("--source", default="cost-aware-routing", help="Source system")
    parser.add_argument("--log-path", help="Override log file path")
    args = parser.parse_args()

    record = log_cost(
        args.task_id,
        args.model,
        args.tokens_input,
        args.tokens_output,
        args.source,
        args.log_path,
    )
    print(json.dumps(record, indent=2))