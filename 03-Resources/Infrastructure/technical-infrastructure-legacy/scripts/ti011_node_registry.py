#!/usr/bin/env python3
"""
ti011_node_registry.py — Load per-node model profiles for runtime routing.
Part of TI-011 meta-orchestration integration with TI-016 node profiles.

Reads lab-specs/node-configs/*/models.json and builds a runtime
(node × model) availability + performance map.

Usage:
    from ti011_node_registry import NodeRegistry
    reg = NodeRegistry()
    node_model = reg.best_model_for(complexity="medium", vision=True)
    # Returns: {"node": "fnet3", "model": "gemma4:e4b", "tokens_per_sec": 5.61}

Standalone:
    python3 ti011_node_registry.py --dump
    python3 ti011_node_registry.py --query medium vision
"""

import glob
import json
import os
import sys
from typing import Optional


def find_repo_root():
    """Find the repo root relative to this script's location."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Script is in technical-infrastructure/scripts/
    # Repo root (ai-trading-workspace/) is one level above technical-infrastructure/
    return os.path.join(script_dir, "../..")


class NodeRegistry:
    """Runtime registry that maps (complexity, capability) -> optimal (node, model)."""

    def __init__(self, node_configs_dir=None):
        if node_configs_dir is None:
            node_configs_dir = os.path.join(find_repo_root(), "lab-specs", "node-configs")
        self.node_configs_dir = os.path.abspath(node_configs_dir)
        self.nodes = {}
        self._load_all()

    def _load_all(self):
        """Load both models.json and model-router.json for each node."""
        if not os.path.isdir(self.node_configs_dir):
            raise FileNotFoundError(f"Node configs dir not found: {self.node_configs_dir}")

        for node_dir in glob.glob(os.path.join(self.node_configs_dir, "*/")):
            node_name = os.path.basename(node_dir.rstrip("/"))
            models_path = os.path.join(node_dir, "models.json")
            router_path = os.path.join(node_dir, "model-router.json")

            if not os.path.exists(models_path):
                continue

            with open(models_path) as f:
                models_data = json.load(f)

            # Merge router profiles into the models data if available
            if os.path.exists(router_path):
                with open(router_path) as f:
                    router_data = json.load(f)
                models_data["profiles"] = router_data.get("profiles", {})

            self.nodes[node_name] = models_data

    def list_nodes(self):
        """Return sorted list of node names."""
        return sorted(self.nodes.keys())

    def node_info(self, node_name):
        """Return full models.json payload for a node."""
        return self.nodes.get(node_name)

    def available_models(self, node_name, provider="ollama"):
        """Return models that are installed on this node (default: local Ollama)."""
        data = self.nodes.get(node_name)
        if not data:
            return []
        return [m for m in data.get("models", []) if m.get("provider") == provider]

    def _complexity_to_tier(self, complexity: str) -> str:
        """Map TI-011 complexity -> model-router tier."""
        mapping = {
            "trivial": "low",
            "simple": "low",
            "medium": "medium",
            "hard": "high",
        }
        return mapping.get(complexity.lower(), "medium")

    @staticmethod
    def _parse_size_gb(size_str: str) -> float:
        """Parse '3.4GB' or '9.6 GB' to float 3.4 / 9.6."""
        if not size_str or size_str == "?":
            return 0.0
        s = size_str.strip().upper().replace(" ", "")
        if s.endswith("GB"):
            s = s[:-2]
        elif s.endswith("G"):
            s = s[:-1]
        try:
            return float(s)
        except (ValueError, TypeError):
            return 0.0

    @staticmethod
    def _parse_capacity_gb(data: dict) -> float:
        """Extract usable capacity in GB from node config."""
        safe = data.get("safe_model_size_gb")
        if safe is not None:
            try:
                return float(safe)
            except (ValueError, TypeError):
                pass
        ram = data.get("node_ram_gb")
        if ram is not None:
            try:
                return float(ram) * 0.6  # heuristic: 60% of RAM for model
            except (ValueError, TypeError):
                pass
        return 8.0  # fallback: assume 8GB safe

    @staticmethod
    def _compute_node_hourly_cost(data: dict) -> float:
        """
        Compute synthetic compute cost per hour for a node.
        
        Includes hardware depreciation + electricity.
        Assumptions:
        - 3-year hardware depreciation (straight-line)
        - 0.15 kWh average load per node
        - $0.12/kWh electricity rate
        
        Returns cost in USD per hour.
        """
        # Hardware cost from config or default by node RAM tier
        hw_cost = data.get("hardware_cost_usd")
        if hw_cost is None:
            ram = data.get("node_ram_gb", "15")
            try:
                ram_gb = float(ram)
            except (ValueError, TypeError):
                ram_gb = 15.0
            # Tiered defaults: small = $500, medium = $800, large = $1200
            if ram_gb <= 16:
                hw_cost = 500.0
            elif ram_gb <= 32:
                hw_cost = 800.0
            else:
                hw_cost = 1200.0
        
        # Depreciation: 3-year straight-line
        hours_3yr = 3 * 365 * 24  # 26,280 hours
        depreciation_per_hour = hw_cost / hours_3yr
        
        # Electricity: 0.15 kWh * $0.12/kWh = $0.018/hour
        power_kwh = data.get("power_draw_kwh", 0.15)
        power_rate = data.get("electricity_rate_usd_per_kwh", 0.12)
        power_per_hour = power_kwh * power_rate
        
        return depreciation_per_hour + power_per_hour

    @staticmethod
    def _compute_cost_per_1k_tokens(tokens_per_sec: float, hourly_cost: float) -> float:
        """
        Compute synthetic cost per 1,000 tokens for a (node, model) pair.
        
        Formula: hourly_cost / (tokens_per_sec * 3600) * 1000
        
        Returns cost in USD per 1K tokens.
        """
        if tokens_per_sec <= 0 or hourly_cost <= 0:
            return 0.0
        tokens_per_hour = tokens_per_sec * 3600
        cost_per_token = hourly_cost / tokens_per_hour
        return cost_per_token * 1000

    def _score_candidates(self, candidates: list) -> list:
        """
        Score candidates with right-sizing + cost awareness.
        
        Scoring formula (updated with cost weight):
            tps_norm   = candidate_tps / max_tps_across_candidates  [0,1]
            fit_score  = min(model_size_gb / node_capacity_gb, 1.0) [0,1]
            cost_score = min(reference_cost / candidate_cost, 1.0)    [0,1]
            total      = (0.30 * tps_norm) + (0.45 * fit_score) + (0.25 * cost_score)
        
        Cost score rewards cheaper (more efficient) compute per token.
        """
        # Normalize tps
        max_tps = max(c.get("tokens_per_sec", 0.0) for c in candidates) or 1.0
        
        # Compute costs for all candidates
        for c in candidates:
            node_data = self.nodes.get(c["node"], {})
            hourly_cost = self._compute_node_hourly_cost(node_data)
            cost_per_1k = self._compute_cost_per_1k_tokens(
                c.get("tokens_per_sec", 0.0), hourly_cost
            )
            c["_hourly_cost"] = round(hourly_cost, 4)
            c["_cost_per_1k_tokens"] = round(cost_per_1k, 4)
        
        # Normalize cost (cheaper = higher score)
        min_cost = min(c.get("_cost_per_1k_tokens", 9999) for c in candidates) or 1.0
        max_cost = max(c.get("_cost_per_1k_tokens", 0) for c in candidates) or 1.0
        cost_range = max_cost - min_cost if max_cost != min_cost else 1.0

        for c in candidates:
            tps_norm = c.get("tokens_per_sec", 0.0) / max_tps

            model_size_gb = self._parse_size_gb(c.get("size", ""))
            node_cap_gb = self._parse_capacity_gb(
                self.nodes.get(c["node"], {})
            )
            fit_score = min(model_size_gb / node_cap_gb, 1.0) if node_cap_gb > 0 else 0.0
            
            # Cost score: cheaper = higher (inverse linear)
            cost_raw = c.get("_cost_per_1k_tokens", 0)
            cost_score = (max_cost - cost_raw) / cost_range if cost_range > 0 else 1.0

            speed_weight = 0.30
            fit_weight = 0.45
            cost_weight = 0.25
            c["_tps_norm"] = round(tps_norm, 3)
            c["_fit_score"] = round(fit_score, 3)
            c["_cost_score"] = round(cost_score, 3)
            c["_total_score"] = round(
                speed_weight * tps_norm + fit_weight * fit_score + cost_weight * cost_score, 3
            )

        candidates.sort(key=lambda c: (-c.get("_total_score", 0), c["node"]))
        return candidates

    def best_model_for(
        self,
        complexity: str = "medium",
        vision: bool = False,
        tools: bool = True,
        profile: str = "auto",
    ) -> Optional[dict]:
        """
        Find the best (node, model) pair for a given complexity + capability.

        Rules:
        1. Filter nodes that have a model matching the complexity tier.
        2. Of those, prefer nodes with the highest tokens_per_sec.
        3. If vision is required, filter to models with vision=True.
        4. If tools is required, filter to models with tools=True.
        5. RIGHT-SIZE: prefer nodes where the model is a better fit for
           node capacity (e.g., 3.4GB model on 15GB node, not 31GB node).

        Returns dict or None:
            {
                "node": "fnet1",
                "model": "qwen3.5:4b",
                "full_id": "ollama/qwen3.5:4b",
                "tokens_per_sec": 4.48,
                "provider": "ollama",
                "_tps_norm": 1.0,
                "_fit_score": 0.378,
                "_total_score": 0.63,
            }
        """
        tier = self._complexity_to_tier(complexity)
        candidates = []

        for node_name, data in sorted(self.nodes.items()):
            profile_name = profile if profile in data.get("profiles", {}) else "auto"
            tier_config = (
                data.get("profiles", {})
                .get(profile_name, {})
                .get(tier)
            )
            if not tier_config:
                continue

            full_model = tier_config.get("model", "")
            if not full_model.startswith("ollama/"):
                continue  # Cloud model -- skip for local routing

            bare_model = full_model.replace("ollama/", "")

            model_spec = None
            for m in data.get("models", []):
                if m["id"] == bare_model:
                    model_spec = m
                    break

            if not model_spec:
                continue

            # Capability filters
            if vision and not model_spec.get("capabilities", {}).get("vision"):
                continue
            if tools and not model_spec.get("capabilities", {}).get("tools"):
                continue

            tps = model_spec.get("tokens_per_sec", "unknown")
            try:
                tps_val = float(tps)
            except (ValueError, TypeError):
                tps_val = 0.0

            candidates.append({
                "node": node_name,
                "model": bare_model,
                "full_id": full_model,
                "tokens_per_sec": tps_val,
                "provider": "ollama",
                "tokens_per_sec_raw": tps,
                "size": model_spec.get("size", "?"),
            })

        if not candidates:
            return None

        # Right-size: score by (speed × 0.35) + (fit × 0.65)
        candidates = self._score_candidates(candidates)
        return candidates[0]

    def match_subtask_to_local(self, subtask: dict) -> dict:
        """
        Match a weighted sub-task from LLM decomposition to the best local (node, model).
        
        Checks:
        1. Complexity -> model tier mapping
        2. Capabilities (vision, tools, reasoning, coding)
        3. Token limit (estimated < context * 0.85)
        4. Capacity (model_size < node_safe_capacity)
        5. Right-sizing score
        
        Returns dict with status and route info:
            {"status": "MATCHED", "node": "fnet3", "model": "qwen3:8b", ...}
            {"status": "TOKEN_OVERFLOW", "reason": "...", ...}
            {"status": "CAPACITY_EXCEEDED", "reason": "...", ...}
            {"status": "CAPABILITY_GAP", "reason": "...", ...}
            {"status": "NO_CANDIDATE", "reason": "..."}
            {"status": "UNCERTAIN", "reason": "..."}
        """
        complexity = subtask.get("complexity", "medium")
        tokens_in = subtask.get("estimated_tokens_in", 0)
        tokens_out = subtask.get("estimated_tokens_out", 0)
        tokens_needed = tokens_in + tokens_out
        capabilities = set(subtask.get("required_capabilities", []))
        confidence = subtask.get("confidence", 0.0)
        
        # If decomposer was uncertain, don't trust the complexity
        if confidence < 0.70:
            return {
                "status": "UNCERTAIN",
                "reason": f"confidence {confidence:.2f} < 0.70 threshold",
                "subtask_id": subtask.get("id", "?"),
                "description": subtask.get("description", "")[:50],
            }
        
        # Map capabilities to vision/tools flags
        vision = "vision" in capabilities
        tools = "tools" in capabilities or "coding" in capabilities or "reasoning" in capabilities
        
        # Query registry for best match
        route = self.best_model_for(complexity, vision=vision, tools=tools)
        
        if not route:
            return {
                "status": "NO_CANDIDATE",
                "reason": f"no local model matches complexity '{complexity}' with capabilities {capabilities}",
                "subtask_id": subtask.get("id", "?"),
                "description": subtask.get("description", "")[:50],
            }
        
        node = route["node"]
        model = route["model"]
        
        # Get model spec for token limit and size checks
        node_data = self.nodes.get(node, {})
        model_spec = None
        for m in node_data.get("models", []):
            if m["id"] == model:
                model_spec = m
                break
        
        if not model_spec:
            return {
                "status": "NO_CANDIDATE",
                "reason": f"model {model} not found in {node} config",
                "subtask_id": subtask.get("id", "?"),
            }
        
        # Check token limit (85% of context window)
        context_limit = model_spec.get("capabilities", {}).get("contextSize", 32768)
        token_limit = int(context_limit * 0.85)
        if tokens_needed > token_limit:
            return {
                "status": "TOKEN_OVERFLOW",
                "reason": f"{tokens_needed} tokens needed > {token_limit} limit (85% of {context_limit} context)",
                "subtask_id": subtask.get("id", "?"),
                "description": subtask.get("description", "")[:50],
                "tokens_needed": tokens_needed,
                "token_limit": token_limit,
                "context_limit": context_limit,
                "node": node,
                "model": model,
            }
        
        # Check capacity (model size < node safe capacity)
        model_size_gb = self._parse_size_gb(model_spec.get("size", "0"))
        node_cap_gb = self._parse_capacity_gb(node_data)
        if model_size_gb > node_cap_gb:
            return {
                "status": "CAPACITY_EXCEEDED",
                "reason": f"model {model_size_gb}GB > node safe capacity {node_cap_gb}GB",
                "subtask_id": subtask.get("id", "?"),
                "description": subtask.get("description", "")[:50],
                "model_size_gb": model_size_gb,
                "node_capacity_gb": node_cap_gb,
                "node": node,
                "model": model,
            }
        
        # Check capabilities
        # "reasoning" is assumed available for all LLMs — it's not a hardware feature
        # Only "vision" is a true hardware capability requirement
        model_caps = set()
        caps = model_spec.get("capabilities", {})
        if caps.get("tools"):
            model_caps.add("tools")
            model_caps.add("coding")  # tools implies coding capability
        if caps.get("vision"):
            model_caps.add("vision")
        # Reasoning is available on all models — infer from complexity
        model_caps.add("reasoning")
        # Math is available on all models
        model_caps.add("math")
        # Creative is available on all models
        model_caps.add("creative")
        
        # Only check for vision gap (true hardware limitation)
        # All other capabilities are software features available on all models
        required_hard_caps = capabilities & {"vision"}
        missing_hard_caps = required_hard_caps - model_caps
        
        if missing_hard_caps:
            return {
                "status": "CAPABILITY_GAP",
                "reason": f"missing hardware capabilities: {missing_hard_caps}",
                "subtask_id": subtask.get("id", "?"),
                "description": subtask.get("description", "")[:50],
                "missing_capabilities": list(missing_hard_caps),
                "available_capabilities": list(model_caps),
                "node": node,
                "model": model,
            }
        
        # All checks passed — route to local
        utilization = round(100 * model_size_gb / node_cap_gb, 1) if node_cap_gb > 0 else 0
        return {
            "status": "MATCHED",
            "node": node,
            "model": model,
            "provider": "ollama",
            "tokens_per_sec": route.get("tokens_per_sec", 0),
            "cost_per_1k_tokens": route.get("_cost_per_1k_tokens", 0),
            "fit_score": route.get("_fit_score", 0),
            "total_score": route.get("_total_score", 0),
            "utilization_percent": utilization,
            "subtask_id": subtask.get("id", "?"),
            "description": subtask.get("description", "")[:50],
            "tokens_needed": tokens_needed,
            "token_limit": token_limit,
            "confidence": confidence,
            "weight": subtask.get("weight", 0),
        }

    def dump(self):
        """Print human-readable summary."""
        print(f"Node Registry: {len(self.nodes)} nodes loaded")
        print(f"Config dir: {self.node_configs_dir}")
        print()

        # Per-node cost summary
        print("=== Per-Node Compute Cost ===")
        for node_name in sorted(self.nodes):
            data = self.nodes[node_name]
            hourly = self._compute_node_hourly_cost(data)
            ram = data.get("node_ram_gb", "?")
            print(f"  {node_name}: ${hourly:.4f}/hour (RAM: {ram}GB)")
        print()

        # Per-model cost on each node
        print("=== Model Cost Per 1K Tokens ===")
        for node_name in sorted(self.nodes):
            data = self.nodes[node_name]
            hourly = self._compute_node_hourly_cost(data)
            print(f"  {node_name} (${hourly:.4f}/hour):")
            for m in data.get("models", []):
                if m.get("provider") != "ollama":
                    continue
                tps_raw = m.get("tokens_per_sec", "unknown")
                try:
                    tps = float(tps_raw)
                except (ValueError, TypeError):
                    tps = 0.0
                cost_1k = self._compute_cost_per_1k_tokens(tps, hourly) if tps > 0 else 0.0
                size = m.get("size", "?")
                print(f"    • {m['id']} ({size}): {tps_raw} t/s → ${cost_1k:.4f} per 1K tokens")
        print()

        # Best assignments with cost
        print("Best model assignments by complexity (with cost):")
        for complexity in ["trivial", "simple", "medium", "hard"]:
            result = self.best_model_for(complexity)
            if result:
                cost_1k = result.get("_cost_per_1k_tokens", 0)
                score = result.get("_total_score", 0)
                print(f"  {complexity:>7} -> {result['node']}/{result['model']} "
                      f"({result['tokens_per_sec']} t/s, ${cost_1k:.4f}/1Ktk, score={score})")
            else:
                print(f"  {complexity:>7} -> None (cloud fallback)")
        print()
        
        # Cloud comparison
        print("=== Cloud Cost Reference ===")
        print("  Cloud LOW (qwen3.5:397b):  ~$0.011 per decomp (~2500 tokens)")
        print("  Cloud MEDIUM (gemma4:31b): ~$0.017 per decomp")
        print("  Cloud HIGH (kimi-k2.6):    ~$0.055 per decomp")
        print()
        
        # Savings summary
        print("=== Local vs Cloud Savings ===")
        for complexity in ["trivial", "simple", "medium", "hard"]:
            result = self.best_model_for(complexity)
            if result and result.get("_cost_per_1k_tokens"):
                local_cost = result["_cost_per_1k_tokens"]
                cloud_cost = 0.011  # cheapest cloud (LOW tier)
                savings = (1 - local_cost / cloud_cost) * 100
                print(f"  {complexity:>7}: local ${local_cost:.4f}/1Ktk vs cloud LOW ${cloud_cost:.3f}/1Ktk -> {savings:.0f}% cheaper")
        print()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dump", action="store_true", help="Print registry summary")
    parser.add_argument("--query", nargs="+", help="Query: complexity [vision] [tools]")
    parser.add_argument("--match", help="Test match_subtask_to_local with JSON subtask")
    args = parser.parse_args()

    reg = NodeRegistry()

    if args.dump:
        reg.dump()
        return

    if args.match:
        import json
        subtask = json.loads(args.match)
        result = reg.match_subtask_to_local(subtask)
        print(json.dumps(result, indent=2))
        return

    if args.query:
        complexity = args.query[0]
        vision = "vision" in args.query
        tools = "tools" in args.query or "tools" not in ["notools"]
        result = reg.best_model_for(complexity, vision=vision, tools=tools)
        print(json.dumps(result, indent=2))
        return

    # Default: print summary + assignments
    reg.dump()


if __name__ == "__main__":
    main()
