#!/usr/bin/env python3
# generate-node-profiles.py — Generate per-node models.json and model-router.json
# Part of TI-016: local-model-pilot lab expansion
#
# Usage: python3 generate-node-profiles.py
# Reads: lab-specs/node-hardware/*.json, lab-specs/node-benchmarks/*.json
# Writes: lab-specs/node-configs/{node}/models.json, model-router.json

import json
import os
import glob
import sys

TI_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../..")
HARDWARE_DIR = os.path.join(TI_ROOT, "lab-specs", "node-hardware")
BENCHMARK_DIR = os.path.join(TI_ROOT, "lab-specs", "node-benchmarks")
OUTPUT_DIR = os.path.join(TI_ROOT, "lab-specs", "node-configs")

# Candidate models with approximate sizes (GB) for capacity checking
CANDIDATE_MODELS = {
    "qwen3.5:4b": {"size_gb": 3.4, "context_window": 131072, "max_tokens": 8192, "reasoning": True, "vision": True, "tools": True},
    "qwen3:8b": {"size_gb": 5.2, "context_window": 131072, "max_tokens": 8192, "reasoning": True, "vision": False, "tools": True},
    "gemma4:e4b": {"size_gb": 9.6, "context_window": 131072, "max_tokens": 8192, "reasoning": True, "vision": True, "tools": True},
}

# Cloud models (always available, not size-constrained)
CLOUD_MODELS = [
    {"id": "gemma4:31b-cloud", "provider": "ollama-cloud", "reasoning": True, "vision": True, "tools": True, "input": ["text", "image"], "contextWindow": 131072, "maxTokens": 32768},
    {"id": "glm-5.1:cloud", "provider": "ollama-cloud", "reasoning": True, "vision": True, "tools": True, "input": ["text", "image"], "contextWindow": 32768, "maxTokens": 16384},
    {"id": "kimi-k2.6:cloud", "provider": "ollama-cloud", "reasoning": True, "vision": False, "tools": True, "input": ["text"], "contextWindow": 131072, "maxTokens": 32768},
]

def load_hardware():
    """Load all node hardware reports"""
    nodes = {}
    for path in glob.glob(os.path.join(HARDWARE_DIR, "*-hardware.json")):
        node_name = os.path.basename(path).replace("-hardware.json", "")
        with open(path) as f:
            data = json.load(f)
            if data.get("status") == "success":
                nodes[node_name] = data
            else:
                print(f"⚠️  {node_name}: hardware probe failed ({data.get('error','unknown')})")
    return nodes

def load_benchmarks():
    """Load all benchmark results"""
    benchmarks = {}
    for path in glob.glob(os.path.join(BENCHMARK_DIR, "*.json")):
        with open(path) as f:
            data = json.load(f)
            node = data.get("node")
            model = data.get("model")
            if node and model:
                benchmarks.setdefault(node, {})[model] = data
    return benchmarks

def compute_safe_model_size(total_ram_gb):
    """Same formula as detect-hardware.sh: total RAM - 6GB buffer"""
    try:
        safe = int(total_ram_gb) - 6
        return max(safe, 2)
    except (ValueError, TypeError):
        return 2

def generate_models_json(node_name, hw, benchmarks):
    """Generate models.json for a single node"""
    total_ram = hw.get("memory", {}).get("total_gb", "0")
    safe_size = compute_safe_model_size(total_ram)

    models = []

    # Add local models that fit
    for model_id, specs in CANDIDATE_MODELS.items():
        if specs["size_gb"] <= safe_size:
            bm = benchmarks.get(node_name, {}).get(model_id, {})
            tps = bm.get("tokens_per_sec", "unknown") if bm.get("status") == "success" else "unknown"

            models.append({
                "id": model_id,
                "provider": "ollama",
                "contextWindow": specs["context_window"],
                "maxTokens": specs["max_tokens"],
                "reasoning": specs["reasoning"],
                "input": ["text", "image"] if specs["vision"] else ["text"],
                "capabilities": {
                    "completion": True,
                    "vision": specs["vision"],
                    "tools": specs["tools"],
                    "thinking": specs["reasoning"],
                    "audio": False
                },
                "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
                "size_gb": specs["size_gb"],
                "tokens_per_sec": tps
            })
        else:
            print(f"     ⚠️  {model_id} ({specs['size_gb']}GB) > safe limit ({safe_size}GB) for {node_name}")

    # Add cloud models (always)
    for cloud in CLOUD_MODELS:
        models.append({
            **cloud,
            "cost": {"input": 0.001, "output": 0.002, "cacheRead": 0, "cacheWrite": 0}  # placeholder
        })

    return {
        "version": "1.0",
        "timestamp": hw.get("timestamp", ""),
        "node": node_name,
        "node_ram_gb": total_ram,
        "safe_model_size_gb": safe_size,
        "providers": [
            {"id": "ollama", "type": "local", "url": "http://localhost:11434"},
            {"id": "ollama-cloud", "type": "cloud", "url": "https://api.ollama.cloud"}
        ],
        "models": models
    }

def generate_router_json(node_name, hw, benchmarks):
    """Generate model-router.json with per-node routing profiles"""
    total_ram = hw.get("memory", {}).get("total_gb", "0")
    safe_size = compute_safe_model_size(total_ram)

    # Determine which models are available on this node
    local_models = []
    for model_id, specs in CANDIDATE_MODELS.items():
        if specs["size_gb"] <= safe_size:
            local_models.append(model_id)

    # Sort by benchmark speed (fastest first), fallback to size (smallest first)
    def sort_key(m):
        bm = benchmarks.get(node_name, {}).get(m, {})
        tps = bm.get("tokens_per_sec", 0) if bm.get("status") == "success" else 0
        size = CANDIDATE_MODELS[m]["size_gb"]
        return (-tps, size)  # negative tps for descending

    local_models.sort(key=sort_key)

    # Build routing profiles
    profiles = {}
    if local_models:
        profiles["auto"] = {
            "high":   {"model": f"ollama/{local_models[0]}", "thinking": "high"},
            "medium": {"model": f"ollama/{local_models[-1] if len(local_models) > 1 else local_models[0]}", "thinking": "medium"},
            "low":    {"model": f"ollama/{local_models[-1]}", "thinking": "off"}
        }
        profiles["local"] = {
            "high":   {"model": f"ollama/{local_models[0]}", "thinking": "high"},
            "medium": {"model": f"ollama/{local_models[0]}", "thinking": "medium"},
            "low":    {"model": f"ollama/{local_models[-1]}", "thinking": "off"}
        }
    else:
        profiles["auto"] = {
            "high":   {"model": "ollama-cloud/gemma4:31b-cloud", "thinking": "high"},
            "medium": {"model": "ollama-cloud/glm-5.1:cloud", "thinking": "medium"},
            "low":    {"model": "ollama-cloud/qwen3.5:4b", "thinking": "off"}
        }

    # Cloud escalation profile (for tasks beyond local capacity)
    profiles["cloud"] = {
        "high":   {"model": "ollama-cloud/kimi-k2.6:cloud", "thinking": "high"},
        "medium": {"model": "ollama-cloud/gemma4:31b-cloud", "thinking": "medium"},
        "low":    {"model": "ollama-cloud/glm-5.1:cloud", "thinking": "off"}
    }

    # Always add a "fast" profile pointing to the smallest model
    if local_models:
        smallest = min(local_models, key=lambda m: CANDIDATE_MODELS[m]["size_gb"])
        profiles["fast"] = {
            "high":   {"model": f"ollama/{smallest}", "thinking": "off"},
            "medium": {"model": f"ollama/{smallest}", "thinking": "off"},
            "low":    {"model": f"ollama/{smallest}", "thinking": "off"}
        }

    return {
        "version": "1.0",
        "timestamp": hw.get("timestamp", ""),
        "node": node_name,
        "defaultProfile": "auto",
        "profiles": profiles
    }

def main():
    print("=== Generating Node Profiles ===")
    print(f"Hardware dir: {HARDWARE_DIR}")
    print(f"Benchmark dir: {BENCHMARK_DIR}")
    print(f"Output dir: {OUTPUT_DIR}")
    print("")

    nodes = load_hardware()
    benchmarks = load_benchmarks()

    if not nodes:
        print("❌ No successful hardware probes found. Run remote-detect.sh first.")
        sys.exit(1)

    print(f"Found {len(nodes)} nodes with successful hardware probes")
    print("")

    for node_name, hw in sorted(nodes.items()):
        node_dir = os.path.join(OUTPUT_DIR, node_name)
        os.makedirs(node_dir, exist_ok=True)

        total_ram = hw.get("memory", {}).get("total_gb", "0")
        safe_size = compute_safe_model_size(total_ram)

        print(f"--- {node_name} ---")
        print(f"     RAM: {total_ram}GB | Safe model size: {safe_size}GB")

        models_json = generate_models_json(node_name, hw, benchmarks)
        router_json = generate_router_json(node_name, hw, benchmarks)

        with open(os.path.join(node_dir, "models.json"), "w") as f:
            json.dump(models_json, f, indent=2)

        with open(os.path.join(node_dir, "model-router.json"), "w") as f:
            json.dump(router_json, f, indent=2)

        available = [m["id"] for m in models_json["models"] if m["provider"] == "ollama"]
        print(f"     Local models: {', '.join(available) if available else 'NONE (all too large)'}")
        print(f"     ✅ models.json + model-router.json → {node_dir}/")
        print("")

    # Generate summary
    summary = {
        "timestamp": max(hw.get("timestamp", "") for hw in nodes.values()),
        "node_count": len(nodes),
        "nodes": {}
    }
    for node_name, hw in sorted(nodes.items()):
        total_ram = hw.get("memory", {}).get("total_gb", "0")
        safe_size = compute_safe_model_size(total_ram)
        summary["nodes"][node_name] = {
            "ram_gb": total_ram,
            "safe_model_size_gb": safe_size,
            "primary_ip": hw.get("network", {}).get("primary_ip", ""),
            "cpu": hw.get("cpu", {}),
            "available_models": [mid for mid, s in CANDIDATE_MODELS.items() if s["size_gb"] <= safe_size],
            "ollama_running": hw.get("ollama", {}).get("running", "false")
        }

    with open(os.path.join(TI_ROOT, "lab-specs", "node-capacity-summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    print(f"=== Summary written to: {TI_ROOT}/lab-specs/node-capacity-summary.json ===")
    print(f"Total nodes: {len(nodes)}")
    print("Done.")

if __name__ == "__main__":
    main()
