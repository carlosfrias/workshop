#!/usr/bin/env python3
"""
prune-cloud-model-cache.py — Clean up pi cloud model cache
Removes cloud models from cache that are NOT in ~/.pi/agent/models.json.
Handles :cloud suffix mismatch between cache keys and config IDs.
"""
import json, shutil, sys
from pathlib import Path

CACHE_FILE = Path.home() / ".pi/agent/cache/ollama-cloud-models.json"
MODELS_FILE = Path.home() / ".pi/agent/models.json"
BACKUP_FILE = Path.home() / ".pi/agent/cache/ollama-cloud-models.json.bak"

def normalize_id(mid):
    """Strip :cloud suffix for comparison."""
    if mid and mid.endswith(":cloud"):
        return mid[:-6]
    return mid

def main():
    # Read configured models
    with open(MODELS_FILE) as f:
        models_cfg = json.load(f)

    configured_ids = set()
    for provider, cfg in models_cfg.get("providers", {}).items():
        for m in cfg.get("models", []):
            configured_ids.add(normalize_id(m.get("id")))

    print(f"Configured models: {len(configured_ids)}")
    for mid in sorted(configured_ids):
        print(f"  ✓ {mid}")

    # Read cache
    with open(CACHE_FILE) as f:
        cache = json.load(f)

    all_cached = cache.get("models", {})
    if isinstance(all_cached, list):
        all_cached = {m: m for m in all_cached}

    print(f"\nCached models before: {len(all_cached)}")

    # Prune
    pruned = {}
    removed = []
    for mid in all_cached:
        norm = normalize_id(mid)
        if norm in configured_ids:
            pruned[mid] = all_cached[mid]
        else:
            removed.append(mid)

    print(f"\nModels to REMOVE from cache:")
    for mid in removed:
        print(f"  ✗ {mid}")

    # Backup original
    shutil.copy2(CACHE_FILE, BACKUP_FILE)
    print(f"\nBackup saved to: {BACKUP_FILE}")

    # Write pruned cache
    cache["models"] = pruned
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

    print(f"\nCache after pruning: {len(pruned)} models")
    print(f"Removed: {len(removed)} models")
    print("\nRestart pi or press Ctrl+P to see the cleaned model list.")

if __name__ == "__main__":
    main()
