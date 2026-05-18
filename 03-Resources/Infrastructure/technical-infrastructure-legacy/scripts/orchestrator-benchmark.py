#!/usr/bin/env python3
"""
Orchestrator Benchmark Script
Benchmarks local Ollama models for tokens/sec, latency, and RAM usage.
Uses Ollama API for faster execution.
"""

import json
import requests
import time
import os
from datetime import datetime

OLLAMA_API = "http://localhost:11434"

BENCHMARK_PROMPT = "Analyze the following trading scenario and provide a detailed response with specific entry points, stop losses, and take profit levels for a day trade on ES futures. Consider the current market context, support and resistance levels, and risk management principles."

LOCAL_MODELS = [
    {"name": "qwen3.5:4b", "size": "3.4GB", "context_window": 131072, "capabilities": ["vision", "tools", "reasoning"]},
    {"name": "qwen3:8b", "size": "5.2GB", "context_window": 131072, "capabilities": ["vision", "tools", "reasoning"]},
    {"name": "gemma4:e4b", "size": "9.6GB", "context_window": 131072, "capabilities": ["vision", "tools", "reasoning"]},
]

EMBEDDING_MODEL = "nomic-embed-text"
CLOUD_MODEL = "qwen3.5:397b-cloud"

def benchmark_generation(model_name, num_runs=3):
    """Benchmark a model's generation performance using Ollama API"""
    print(f"\n{'='*60}")
    print(f"Benchmarking: {model_name}")
    print(f"{'='*60}")
    
    results = []
    
    # Warm up
    print("  Warming up model...")
    try:
        requests.post(
            f"{OLLAMA_API}/api/generate",
            json={"model": model_name, "prompt": "Hello", "stream": False},
            timeout=60
        )
        time.sleep(1)
    except Exception as e:
        print(f"  Warning: Warm-up failed: {e}")
    
    for i in range(num_runs):
        print(f"  Run {i+1}/{num_runs}...")
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{OLLAMA_API}/api/generate",
                json={"model": model_name, "prompt": BENCHMARK_PROMPT, "stream": False},
                timeout=120
            )
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            data = response.json()
            token_count = data.get("eval_count", 0)
            tokens_per_sec = data.get("eval_rate", 0)
            
            results.append({
                "tokens_per_sec": round(tokens_per_sec, 2),
                "latency_ms": round(latency_ms, 2),
                "output_tokens": token_count
            })
            
            print(f"    Latency: {latency_ms:.0f}ms, Tokens/sec: {tokens_per_sec:.2f}, Tokens: {token_count}")
            
        except requests.Timeout:
            print(f"    Timeout on run {i+1}")
            continue
        except Exception as e:
            print(f"    Error on run {i+1}: {e}")
            continue
        
        time.sleep(1)
    
    if not results:
        return None
    
    # Calculate averages
    avg_tokens_per_sec = sum(r["tokens_per_sec"] for r in results) / len(results)
    avg_latency_ms = sum(r["latency_ms"] for r in results) / len(results)
    
    return {
        "tokens_per_sec": round(avg_tokens_per_sec, 2),
        "latency_ms": round(avg_latency_ms, 2),
        "runs": len(results)
    }

def benchmark_embedding(model_name, num_runs=3):
    """Benchmark embedding model performance"""
    print(f"\n{'='*60}")
    print(f"Benchmarking embeddings: {model_name}")
    print(f"{'='*60}")
    
    test_text = "This is a test sentence for benchmarking embedding performance. " * 10
    
    results = []
    
    for i in range(num_runs):
        print(f"  Run {i+1}/{num_runs}...")
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{OLLAMA_API}/api/embeddings",
                json={"model": model_name, "prompt": test_text},
                timeout=60
            )
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            results.append(latency_ms)
            print(f"    Latency: {latency_ms:.0f}ms")
            
        except Exception as e:
            print(f"    Error: {e}")
            continue
        
        time.sleep(1)
    
    if not results:
        return None
    
    avg_latency = sum(results) / len(results)
    
    return {
        "avg_latency_ms": round(avg_latency, 2),
        "runs": len(results)
    }

def main():
    print("="*60)
    print("ORCHESTRATOR BENCHMARK")
    print(f"Date: {datetime.now().isoformat()}")
    print("="*60)
    
    # Benchmark local models
    models_data = []
    
    for model in LOCAL_MODELS:
        print(f"\n{'#'*60}")
        print(f"# MODEL: {model['name']}")
        print(f"{'#'*60}")
        
        result = benchmark_generation(model["name"])
        
        if result:
            models_data.append({
                "name": model["name"],
                "provider": "ollama",
                "size": model["size"],
                "tokens_per_sec": result["tokens_per_sec"],
                "latency_ms": result["latency_ms"],
                "context_window": model["context_window"],
                "capabilities": model["capabilities"]
            })
        else:
            print(f"  Failed to benchmark {model['name']}")
    
    # Benchmark embedding model
    print(f"\n{'#'*60}")
    print(f"# EMBEDDING MODEL: {EMBEDDING_MODEL}")
    print(f"{'#'*60}")
    
    embed_result = benchmark_embedding(EMBEDDING_MODEL)
    
    if embed_result:
        models_data.append({
            "name": EMBEDDING_MODEL,
            "provider": "ollama",
            "type": "embedding",
            "avg_latency_ms": embed_result["avg_latency_ms"],
            "size": "274MB"
        })
    
    # Add cloud model info
    models_data.append({
        "name": CLOUD_MODEL,
        "provider": "ollama",
        "size": "cloud",
        "type": "cloud",
        "context_window": 131072,
        "capabilities": ["vision", "tools", "reasoning"],
        "note": "Cloud-hosted model, no local benchmark"
    })
    
    # Create final config
    config = {
        "node": "orchestrator",
        "hostname": "localhost",
        "ip": "192.168.0.140",
        "hardware": {
            "cpu": "Apple M4 Pro",
            "cores": 14,
            "ram_gb": 24,
            "os": "macOS 15"
        },
        "models": models_data,
        "benchmark_date": datetime.now().isoformat()
    }
    
    # Ensure output directory exists
    output_dir = "technical-infrastructure/lab-specs/node-configs/orchestrator"
    os.makedirs(output_dir, exist_ok=True)
    
    # Write results
    output_path = os.path.join(output_dir, "models.json")
    with open(output_path, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"BENCHMARK COMPLETE")
    print(f"Results saved to: {output_path}")
    print(f"{'='*60}")
    
    # Print summary
    print("\nSUMMARY:")
    for model in models_data:
        if model.get("type") == "embedding":
            print(f"  {model['name']}: {model['avg_latency_ms']}ms avg embedding latency")
        elif model.get("type") == "cloud":
            print(f"  {model['name']}: Cloud-only (no local benchmark)")
        else:
            print(f"  {model['name']}: {model['tokens_per_sec']} tokens/sec, {model['latency_ms']}ms latency")
    
    return config

if __name__ == "__main__":
    main()
