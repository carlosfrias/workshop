#!/usr/bin/env python3
"""TDD suite: Validate all models have real (non-zero) costs across the fleet.

Validates:
1. Every model in models.json has a 'cost' field
2. All cost values (input, output, cacheRead, cacheWrite) are > 0
3. billing_tiers.json has entries for all models in models.json
4. No model referenced in model-router.json is missing from models.json

Philosophy: There is no such thing as a zero-cost model.
Even free-tier API models consume real compute resources.
Every model must have a non-zero cost captured.
"""

import json
import os
import sys
from typing import List, Dict, Tuple

import pytest


# ─── Config path resolution ───────────────────────────────────────────

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(SCRIPT_DIR, "..")
COST_CONFIG_DIR = os.path.join(PROJECT_ROOT, "config")

# Primary model configs to validate (orchestrator + fleet nodes)
ORCHESTRATOR_MODELS_PATH = os.path.expanduser("~/.pi/agent/models.json")
ORCHESTRATOR_ROUTER_PATH = os.path.expanduser("~/.pi/agent/model-router.json")
BILLING_TIERS_PATH = os.path.join(COST_CONFIG_DIR, "billing_tiers.json")

# Fleet node configs (relative to workspace mount)
FLEET_NODE_NAMES = ["fnet1", "fnet2", "fnet3", "fnet4", "fnet5", "fnet6", "fnet7"]
FLEET_MOUNT_BASE = "/mnt/trading-desk"  # SSHFS mount point


def load_json(path: str) -> dict:
    """Load a JSON file, returning empty dict if not found."""
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


def get_model_list(models_json: dict) -> List[dict]:
    """Extract all models from models.json across all providers."""
    models = []
    for provider_name, provider_config in models_json.get("providers", {}).items():
        for model in provider_config.get("models", []):
            model["_provider"] = provider_name
            models.append(model)
    return models


def get_model_ids(models_json: dict) -> List[str]:
    """Get all model IDs from models.json."""
    return [m["id"] for m in get_model_list(models_json)]


def strip_provider_prefix(model_id: str) -> str:
    """Strip provider prefix (e.g., 'ollama/gemma4:e4b' -> 'gemma4:e4b')."""
    if "/" in model_id:
        parts = model_id.split("/", 1)
        # Only strip known provider prefixes, not model names with slashes
        if parts[0] in ("ollama", "openrouter", "openai", "google", "mistralai", "meta-llama", "qwen"):
            return parts[1]
    return model_id


def get_router_model_ids(router_json: dict) -> List[str]:
    """Extract all model references from model-router.json profiles."""
    model_ids = set()
    for profile_name, profile in router_json.get("profiles", {}).items():
        for tier in ["high", "medium", "low"]:
            if tier in profile:
                model = profile[tier].get("model", "")
                if model:
                    model_ids.add(strip_provider_prefix(model))
    return sorted(model_ids)


# ─── Test: models.json cost field presence ─────────────────────────────

class TestModelCostFieldPresence:
    """Every model in models.json MUST have a cost field with all values > 0."""

    REQUIRED_COST_KEYS = {"input", "output", "cacheRead", "cacheWrite"}

    @pytest.fixture
    def orchestrator_models(self):
        models_json = load_json(ORCHESTRATOR_MODELS_PATH)
        if not models_json:
            pytest.skip("Orchestrator models.json not found")
        return models_json

    @pytest.fixture
    def all_orchestrator_models(self, orchestrator_models):
        return get_model_list(orchestrator_models)

    def test_all_models_have_cost_field(self, all_orchestrator_models):
        """Every model must have a 'cost' dictionary."""
        missing = []
        for model in all_orchestrator_models:
            if "cost" not in model:
                missing.append(f"{model['_provider']}/{model['id']}")
        assert not missing, (
            f"Models missing 'cost' field: {missing}\n"
            f"Fix: Add cost dict with input, output, cacheRead, cacheWrite to each model."
        )

    def test_all_cost_values_positive(self, all_orchestrator_models):
        """Every cost value must be > 0. No zero-cost models."""
        violations = []
        for model in all_orchestrator_models:
            if "cost" not in model:
                continue  # Caught by test_all_models_have_cost_field
            cost = model["cost"]
            for key in self.REQUIRED_COST_KEYS:
                val = cost.get(key, 0)
                if val <= 0:
                    violations.append(
                        f"{model['_provider']}/{model['id']}.cost.{key} = {val} (must be > 0)"
                    )
        assert not violations, (
            f"Models with zero or negative cost values:\n" +
            "\n".join(f"  ❌ {v}" for v in violations) +
            "\nFix: Assign real non-zero costs. Even free-tier models consume compute resources."
        )

    def test_all_required_cost_keys_present(self, all_orchestrator_models):
        """All four cost keys (input, output, cacheRead, cacheWrite) must be present."""
        missing_keys = []
        for model in all_orchestrator_models:
            if "cost" not in model:
                continue  # Caught by other test
            cost = model["cost"]
            for key in self.REQUIRED_COST_KEYS:
                if key not in cost:
                    missing_keys.append(f"{model['_provider']}/{model['id']}.cost missing '{key}'")
        assert not missing_keys, (
            f"Models missing required cost keys:\n" +
            "\n".join(f"  ❌ {m}" for m in missing_keys)
        )

    def test_cache_read_less_than_input(self, all_orchestrator_models):
        """cacheRead should be cheaper than input (cache hits save money)."""
        violations = []
        for model in all_orchestrator_models:
            if "cost" not in model:
                continue
            cost = model["cost"]
            if cost.get("cacheRead", 0) >= cost.get("input", 0):
                violations.append(
                    f"{model['_provider']}/{model['id']}: "
                    f"cacheRead ({cost['cacheRead']}) >= input ({cost['input']})"
                )
        assert not violations, (
            f"Models where cache read is not cheaper than input:\n" +
            "\n".join(f"  ❌ {v}" for v in violations)
        )

    def test_cache_write_equals_input_cost(self, all_orchestrator_models):
        """cacheWrite should typically equal input cost."""
        violations = []
        for model in all_orchestrator_models:
            if "cost" not in model:
                continue
            cost = model["cost"]
            if cost.get("cacheWrite", 0) != cost.get("input", 0):
                violations.append(
                    f"{model['_provider']}/{model['id']}: "
                    f"cacheWrite ({cost['cacheWrite']}) != input ({cost['input']})"
                )
        assert not violations, (
            f"Models where cacheWrite != input cost:\n" +
            "\n".join(f"  ❌ {v}" for v in violations)
        )


# ─── Test: billing_tiers.json coverage ─────────────────────────────────

class TestBillingTiersCoverage:
    """Every model in models.json should have a corresponding billing tier entry."""

    @pytest.fixture
    def billing_tiers(self):
        tiers = load_json(BILLING_TIERS_PATH)
        if not tiers:
            pytest.skip("billing_tiers.json not found")
        return tiers

    @pytest.fixture
    def orchestrator_model_ids(self):
        models_json = load_json(ORCHESTRATOR_MODELS_PATH)
        if not models_json:
            pytest.skip("Orchestrator models.json not found")
        return get_model_ids(models_json)

    @pytest.fixture
    def tiered_model_ids(self, billing_tiers):
        return [t["model"] for t in billing_tiers.get("tiers", [])]

    def test_all_models_have_billing_tier(self, orchestrator_model_ids, tiered_model_ids):
        """Every model in models.json must have a billing tier entry."""
        missing = [m for m in orchestrator_model_ids if m not in tiered_model_ids]
        assert not missing, (
            f"Models without billing tier entries:\n" +
            "\n".join(f"  ❌ {m}" for m in missing) +
            "\nFix: Add entries to billing_tiers.json for each missing model."
        )

    def test_all_tier_prices_positive(self, billing_tiers):
        """Every billing tier must have a positive price_per_1k_tokens."""
        violations = []
        for tier in billing_tiers.get("tiers", []):
            price = tier.get("price_per_1k_tokens", 0)
            if price <= 0:
                violations.append(f"{tier['id']} ({tier['model']}): price=${price}")
        assert not violations, (
            f"Billing tiers with non-positive prices:\n" +
            "\n".join(f"  ❌ {v}" for v in violations)
        )

    def test_tier_models_exist_in_models_json(self, billing_tiers, orchestrator_model_ids):
        """No orphan billing tiers for models that don't exist in models.json."""
        orphans = []
        for tier in billing_tiers.get("tiers", []):
            if tier["model"] not in orchestrator_model_ids:
                orphans.append(f"{tier['id']} -> {tier['model']}")
        assert not orphans, (
            f"Billing tiers referencing models not in models.json:\n" +
            "\n".join(f"  ⚠️  {o}" for o in orphans) +
            "\nFix: Either add model to models.json or remove stale tier entry."
        )


# ─── Test: model-router.json references ─────────────────────────────────

class TestModelRouterReferences:
    """All models referenced in model-router.json must exist in models.json."""

    @pytest.fixture
    def orchestrator_model_ids(self):
        models_json = load_json(ORCHESTRATOR_MODELS_PATH)
        if not models_json:
            pytest.skip("Orchestrator models.json not found")
        return get_model_ids(models_json)

    @pytest.fixture
    def router_model_ids(self):
        router_json = load_json(ORCHESTRATOR_ROUTER_PATH)
        if not router_json:
            pytest.skip("model-router.json not found")
        return get_router_model_ids(router_json)

    def test_router_refs_exist_in_models(self, router_model_ids, orchestrator_model_ids):
        """No broken references from router to models."""
        broken = [m for m in router_model_ids if m not in orchestrator_model_ids]
        # Also check with provider prefix stripped (router uses ollama/ prefix)
        broken_stripped = []
        for m in broken:
            # Try matching without provider prefix
            if m not in orchestrator_model_ids:
                broken_stripped.append(m)
        assert not broken_stripped, (
            f"model-router.json references models not in models.json:\n" +
            "\n".join(f"  ❌ {b}" for b in broken_stripped) +
            "\nFix: Add missing models to models.json or update router references."
        )


# ─── Test: Fleet node model costs (conditional on SSHFS availability) ──

class TestFleetNodeModelCosts:
    """Validate model costs on fleet nodes when mounts are available."""

    @pytest.fixture
    def available_fleet_nodes(self):
        """Return list of (node_name, models_path) for mounted fleet nodes."""
        available = []
        for node in FLEET_NODE_NAMES:
            models_path = os.path.join(
                FLEET_MOUNT_BASE, f".pi-fleet/{node}/agent/models.json"
            )
            # Also check alternate path patterns
            alt_path = os.path.join(
                FLEET_MOUNT_BASE, f"{node}/.pi/agent/models.json"
            )
            for path in [models_path, alt_path]:
                if os.path.exists(path):
                    available.append((node, path))
                    break
        return available

    def test_fleet_nodes_accessible(self, available_fleet_nodes):
        """Report which fleet nodes are accessible for cost validation."""
        found = [n for n, _ in available_fleet_nodes]
        missing = [n for n in FLEET_NODE_NAMES if n not in found]
        if missing:
            pytest.skip(
                f"Fleet nodes not mounted: {missing}. "
                f"Mount with: sshfs friasc@<ip>:/mnt/trading-desk /mnt/trading-desk"
            )
        # If we get here, at least some nodes are available
        assert found, "No fleet nodes accessible"

    def test_fleet_models_have_costs(self, available_fleet_nodes):
        """Every model on every fleet node must have non-zero costs."""
        if not available_fleet_nodes:
            pytest.skip("No fleet nodes accessible")

        violations = []
        for node_name, models_path in available_fleet_nodes:
            models_json = load_json(models_path)
            if not models_json:
                violations.append(f"{node_name}: models.json not found at {models_path}")
                continue
            for model in get_model_list(models_json):
                model_key = f"{node_name}/{model['_provider']}/{model['id']}"
                if "cost" not in model:
                    violations.append(f"{model_key}: missing 'cost' field")
                    continue
                cost = model["cost"]
                for key in ["input", "output"]:
                    val = cost.get(key, 0)
                    if val <= 0:
                        violations.append(f"{model_key}.cost.{key} = {val} (must be > 0)")

        assert not violations, (
            f"Fleet node model cost violations:\n" +
            "\n".join(f"  ❌ {v}" for v in violations)
        )


# ─── CLI entry point ───────────────────────────────────────────────────

if __name__ == "__main__":
    args = sys.argv[1:] if len(sys.argv) > 1 else ["-v"]
    pytest.main([__file__, *args])
