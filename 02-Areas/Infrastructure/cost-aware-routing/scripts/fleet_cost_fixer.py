#!/usr/bin/env python3
"""
fleet_cost_fixer.py — Add non-zero costs to all models across fleet nodes.

Reads a models.json, adds/replaces cost fields with real non-zero values
based on model ID, and writes back. Preserves all other fields.

Usage:
    python3 fleet_cost_fixer.py --dry-run ~/.pi/agent/models.json
    python3 fleet_cost_fixer.py ~/.pi/agent/models.json
    python3 fleet_cost_fixer.py --all-nodes  # Fleet-wide via SSH
"""

import argparse
import json
import os
import subprocess
import sys
from typing import Dict, Optional

# ─── Cost table: base cost per 1M tokens ──────────────────────────────
# These are the authoritative costs. Zero is not acceptable.
# Costs reflect: hardware depreciation + electricity for local models.
# For cloud models: API provider retail pricing.

COST_TABLE: Dict[str, dict] = {
    # Local Ollama models
    "qwen3.5:4b": {
        "input": 0.005, "output": 0.01,
        "cacheRead": 0.001, "cacheWrite": 0.005,
        "_note": "Local 4B vision lightweight — 3.4GB"
    },
    "qwen3:8b": {
        "input": 0.006, "output": 0.012,
        "cacheRead": 0.0012, "cacheWrite": 0.006,
        "_note": "Local 8B text — mid-tier cost"
    },
    "qwen3.5:9b": {
        "input": 0.007, "output": 0.014,
        "cacheRead": 0.0014, "cacheWrite": 0.007,
        "_note": "Local 9.65B vision+tools — next-class model"
    },
    "openbmb/minicpm-o2.6:8b": {
        "input": 0.006, "output": 0.012,
        "cacheRead": 0.0012, "cacheWrite": 0.006,
        "_note": "Local 8B vision 5.5GB — fast 39 tok/s"
    },
    "qwen3.5:35b-a3b": {
        "input": 0.007, "output": 0.014,
        "cacheRead": 0.0014, "cacheWrite": 0.007,
        "_note": "Local MoE 35B/3B active — 23GB disk"
    },
    "gemma4:e4b": {
        "input": 0.01, "output": 0.02,
        "cacheRead": 0.002, "cacheWrite": 0.01,
        "_note": "Local flagship — only local vision at high tier, 9.6GB"
    },
    # Cloud models (via ollama-cloud / openrouter)
    "deepseek-v4-pro:cloud": {
        "input": 0.435, "output": 0.87,
        "cacheRead": 0.003625, "cacheWrite": 0.435,
        "_note": "DeepSeek V4 Pro — 1M context, 75% promo"
    },
    "glm-5.1:cloud": {
        "input": 1.4, "output": 4.4,
        "cacheRead": 0.26, "cacheWrite": 1.4,
        "_note": "GLM-5.1 via Zhipu AI — 202K context"
    },
    "kimi-k2.6:cloud": {
        "input": 0.95, "output": 4.0,
        "cacheRead": 0.16, "cacheWrite": 0.95,
        "_note": "Kimi K2.6 via Moonshot — vision, 262K context, 1T MoE"
    },
    "gemma4:31b-cloud": {
        "input": 0.12, "output": 0.37,
        "cacheRead": 0.065, "cacheWrite": 0.12,
        "_note": "Gemma 4 31B via Google — cheapest cloud option"
    },
    "qwen3.5:397b-cloud": {
        "input": 0.6, "output": 3.6,
        "cacheRead": 0.12, "cacheWrite": 0.6,
        "_note": "Qwen 3.5 397B via Alibaba — strongest Chinese model"
    },
    # OpenRouter free tier — symbolic tracking cost
    "google/gemma-3-4b-instruct:free": {
        "input": 0.0005, "output": 0.001,
        "cacheRead": 0.0001, "cacheWrite": 0.0005,
        "_note": "OpenRouter free tier — symbolic tracking cost"
    },
    "meta-llama/llama-3-8b-instruct:free": {
        "input": 0.0005, "output": 0.001,
        "cacheRead": 0.0001, "cacheWrite": 0.0005,
        "_note": "OpenRouter free tier — symbolic tracking cost"
    },
    "mistralai/mistral-7b-instruct:free": {
        "input": 0.0005, "output": 0.001,
        "cacheRead": 0.0001, "cacheWrite": 0.0005,
        "_note": "OpenRouter free tier — symbolic tracking cost"
    },
    "qwen/qwen-2.5-7b-instruct:free": {
        "input": 0.0005, "output": 0.001,
        "cacheRead": 0.0001, "cacheWrite": 0.0005,
        "_note": "OpenRouter free tier — symbolic tracking cost"
    },
    # OpenRouter paid models
    "google/gemini-2.5-flash-preview": {
        "input": 0.075, "output": 0.3,
        "cacheRead": 0.01875, "cacheWrite": 0.075,
        "_note": "Best value multimodal — 1M context"
    },
    "openai/gpt-4o": {
        "input": 2.5, "output": 7.5,
        "cacheRead": 0.625, "cacheWrite": 2.5,
        "_note": "GPT-4o omni modal"
    },
}


def fix_costs_in_models(models_json: dict) -> tuple[int, int, list]:
    """
    Add/replace cost fields in all models across all providers.

    Returns: (fixed_count, total_models, log_messages)
    """
    fixed = 0
    total = 0
    log = []

    for provider_name, provider_config in models_json.get("providers", {}).items():
        for model in provider_config.get("models", []):
            total += 1
            model_id = model["id"]
            cost_info = COST_TABLE.get(model_id)

            if cost_info is None:
                log.append(f"⚠️  {provider_name}/{model_id}: no cost entry in COST_TABLE")
                continue

            old_cost = model.get("cost", {})
            had_zeros = any(old_cost.get(k, 0) <= 0 for k in ("input", "output", "cacheRead", "cacheWrite"))
            had_missing = "cost" not in model

            if had_missing or had_zeros:
                model["cost"] = dict(cost_info)  # Copy so we can remove _note
                note = model["cost"].pop("_note", "")
                fixed += 1
                if had_missing:
                    log.append(f"✅ {provider_name}/{model_id}: ADDED cost field — {note}")
                else:
                    log.append(f"🔧 {provider_name}/{model_id}: REPLACED zero costs — {note}")
            else:
                log.append(f"✔️  {provider_name}/{model_id}: costs already valid")

    return fixed, total, log


def fix_file(path: str, dry_run: bool = False) -> bool:
    """
    Fix a models.json file in-place.

    Returns True if fixes were needed and applied.
    """
    if not os.path.exists(path):
        print(f"❌ File not found: {path}")
        return False

    with open(path) as f:
        original = f.read()
        models_json = json.loads(original)

    fixed, total, log = fix_costs_in_models(models_json)

    print(f"\n── {path} ──")
    print(f"   Models: {total}, Fixed: {fixed}, Unchanged: {total - fixed}")
    for entry in log:
        print(f"   {entry}")

    if fixed > 0 and not dry_run:
        new_json = json.dumps(models_json, indent=2, ensure_ascii=False)
        with open(path, "w") as f:
            f.write(new_json)
        print(f"   💾 Written to {path}")
    elif fixed > 0 and dry_run:
        print(f"   🔍 DRY RUN — no changes written")

    return fixed > 0


def fix_fleet_node(ip: str, dry_run: bool = False) -> bool:
    """
    Fix a remote fleet node's models.json via SSH.

    Returns True if node was reachable and fixes were applied.
    """
    remote_path = "~/.pi/agent/models.json"
    node_name = f"fnet{ip.split('.')[-1]}"

    try:
        # Read remote file
        result = subprocess.run(
            ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=5",
             f"friasc@{ip}", f"cat {remote_path}"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            print(f"❌ {node_name} ({ip}): Cannot read models.json — {result.stderr.strip()}")
            return False

        models_json = json.loads(result.stdout)
        fixed, total, log = fix_costs_in_models(models_json)

        print(f"\n── {node_name} ({ip}) ──")
        print(f"   Models: {total}, Fixed: {fixed}, Unchanged: {total - fixed}")
        for entry in log:
            print(f"   {entry}")

        if fixed > 0 and not dry_run:
            new_json = json.dumps(models_json, indent=2, ensure_ascii=False)
            # Write back via SSH
            write_result = subprocess.run(
                ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=5",
                 f"friasc@{ip}", f"cat > {remote_path}"],
                input=new_json, capture_output=True, text=True, timeout=10
            )
            if write_result.returncode != 0:
                print(f"   ❌ Write failed: {write_result.stderr.strip()}")
                return False
            print(f"   💾 Written to {node_name}")
        elif fixed > 0 and dry_run:
            print(f"   🔍 DRY RUN — no changes written")

        return fixed > 0

    except subprocess.TimeoutExpired:
        print(f"❌ {node_name} ({ip}): SSH timeout")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ {node_name} ({ip}): JSON parse error — {e}")
        return False
    except Exception as e:
        print(f"❌ {node_name} ({ip}): {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Add non-zero costs to all models in models.json files"
    )
    parser.add_argument(
        "path", nargs="?", default=None,
        help="Path to models.json file"
    )
    parser.add_argument(
        "--all-nodes", action="store_true",
        help="Fix all fleet nodes (fnet1-fnet7) via SSH"
    )
    parser.add_argument(
        "--orchestrator", action="store_true",
        help="Fix orchestrator models.json"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Report what would change without writing"
    )
    args = parser.parse_args()

    if args.all_nodes:
        fleet_ips = [
            "192.168.0.141", "192.168.0.142", "192.168.0.143",
            "192.168.0.144", "192.168.0.145", "192.168.0.146",
            "192.168.0.147",
        ]
        print(f"=== Fleet Cost Fixer: {len(fleet_ips)} nodes ===\n")
        fixed_count = 0
        for ip in fleet_ips:
            if fix_fleet_node(ip, dry_run=args.dry_run):
                fixed_count += 1
        print(f"\n=== Summary: {fixed_count}/{len(fleet_ips)} nodes had fixes ===")
    elif args.orchestrator:
        orchestrator_path = os.path.expanduser("~/.pi/agent/models.json")
        fix_file(orchestrator_path, dry_run=args.dry_run)
    elif args.path:
        fix_file(args.path, dry_run=args.dry_run)
    else:
        # Default: fix orchestrator only
        orchestrator_path = os.path.expanduser("~/.pi/agent/models.json")
        fix_file(orchestrator_path, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
