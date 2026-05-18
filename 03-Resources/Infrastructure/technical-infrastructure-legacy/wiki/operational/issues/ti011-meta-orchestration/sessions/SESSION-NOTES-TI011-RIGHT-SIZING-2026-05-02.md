# Right-Sizing Model-to-Node Mapping

**Date**: 2026-05-02 19:00 ET  
**Domain**: technical-infrastructure  
**Task**: TI-011 — Fit model sizes to lab node capacity

## Problem Statement

The meta-orchestration framework was routing tasks to the **fastest node** regardless of whether the model was appropriately sized for the node's capacity:

- **Before fix**: `trivial` → fnet6/qwen3.5:4b (3.4GB model on 31GB node, 14% utilization)
- **Before fix**: 15GB nodes (fnet1/fnet2/fnet7) **never received traffic**
- 31GB nodes wasted capacity running tiny models while large models were available

## Root Cause

1. `ti011_node_registry.py` `best_model_for()` only sorted by `tokens_per_sec` — no capacity awareness
2. Most `models.json` files had `"size": "?"` — no model size data
3. `model-router.json` configs assigned oversized models to small nodes (e.g., fnet7 medium tier = qwen3:8b on 9GB safe)

## Changes

### 1. ti011_node_registry.py — Right-Sizing Logic

Added three new methods:

- `_parse_size_gb("3.4GB")` → 3.4
- `_parse_capacity_gb(data)` → reads `safe_model_size_gb` or `node_ram_gb * 0.6`
- `_score_candidates(candidates)` → combined score = 35% speed + 65% fit

New scoring formula:
```
fps_norm  = candidate_tps / max_tps_across_candidates
fit_score = min(model_size_gb / node_capacity_gb, 1.0)
total     = 0.35 * tps_norm + 0.65 * fit_score
```

### 2. Model Sizes in All Node Configs

Updated `models.json` for all 7 nodes with actual sizes:

| Model | Size |
|-------|------|
| qwen3.5:4b | 3.4 GB |
| qwen3:8b | 5.2 GB |
| gemma4:e4b | 9.6 GB |

### 3. model-router.json Tier Adjustments

**15GB nodes** (fnet1, fnet2, fnet7):
- low/trivial: qwen3.5:4b (fits in 9GB safe, 38% util)
- medium/simple: qwen3.5:4b
- hard: qwen3:8b (58% util — close to limit but acceptable)

**31GB nodes** (fnet3-fnet6):
- low: qwen3.5:4b (14% util)
- medium: qwen3:8b (21% util)
- hard: gemma4:e4b (38% util)

## Verification

### Per-Node Capacity Utilization

**15GB nodes:**
```
fnet1: qwen3.5:4b (3.4GB / 9GB safe = 38%)
fnet1: qwen3:8b   (5.2GB / 9GB safe = 58%)
fnet7: qwen3.5:4b (3.4GB / 9GB safe = 38%)
fnet7: qwen3:8b   (5.2GB / 9GB safe = 58%)
```

**31GB nodes:**
```
fnet3: qwen3.5:4b (3.4GB / 25GB safe = 14%)
fnet3: qwen3:8b   (5.2GB / 25GB safe = 21%)
fnet3: gemma4:e4b (9.6GB / 25GB safe = 38%)
```

### Runtime Routing Results

```
trivial: fnet7/qwen3.5:4b  tps=3.47 fit=0.378 score=0.517  (38% util)
simple:  fnet7/qwen3.5:4b  tps=3.47 fit=0.378 score=0.517  (38% util)
medium:  fnet7/qwen3.5:4b  tps=3.47 fit=0.378 score=0.499  (38% util)
hard:    fnet6/gemma4:e4b  tps=6.18 fit=0.384 score=0.600  (38% util)
```

All routed to nodes where the model is a **good fit** (38% utilization target).

## Impact

- 15GB nodes now receive traffic for small models (freeing 31GB capacity)
- No model exceeds its node's safe capacity
- All utilized at ~38% of safe capacity = healthy headroom

## Files Changed

| File | Change |
|------|--------|
| `scripts/ti011_node_registry.py` | `_parse_size_gb`, `_parse_capacity_gb`, `_score_candidates` methods |
| `lab-specs/node-configs/*/models.json` | Added `size` field to model specs |
| `lab-specs/node-configs/fnet1/model-router.json` | Medium tier: qwen3:8b → qwen3.5:4b |
| `lab-specs/node-configs/fnet7/model-router.json` | Medium tier: qwen3:8b → qwen3.5:4b |
| `lab-specs/node-configs/fnet{3-6}/model-router.json` | Medium tier: qwen3.5:4b → qwen3:8b |

## Next Steps

- Monitor for load imbalance (too much traffic to fnet7)
- Add saturation detection in registry (skip nodes with high queue depth)
