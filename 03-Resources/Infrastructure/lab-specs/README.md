# Lab Specs — Node Configuration Registry

**Purpose:** Runtime (node × model) availability + performance map for TI-011 meta-orchestration.

**Location:** `/Users/friasc/Cloud/workshop/lab-specs/`

---

## Directory Structure

```
lab-specs/
├── README.md                          # This file
├── node-capacity-summary.json         # Machine-readable cluster index
└── node-configs/
    ├── fnet1/
    │   ├── models.json                # Installed models + performance
    │   └── model-router.json          # Routing profiles
    ├── fnet2/
    │   ├── models.json
    │   └── model-router.json
    ├── fnet3/                         # Vector Memory Node (ChromaDB)
    │   ├── models.json                # Includes nomic-embed-text
    │   └── model-router.json
    ├── fnet4/
    │   ├── models.json
    │   └── model-router.json
    ├── fnet5/
    │   ├── models.json
    │   └── model-router.json
    ├── fnet6/                         # Secondary Depot
    │   ├── models.json
    │   └── model-router.json
    └── fnet7/
        ├── models.json
        └── model-router.json
```

---

## Configuration File Formats

### models.json

```json
{
  "models": [
    {
      "id": "gemma4:e4b",
      "provider": "ollama",
      "tokens_per_sec": 1700,
      "throughput_tier": "local"
    },
    {
      "id": "qwen3:8b",
      "provider": "ollama",
      "tokens_per_sec": 2100,
      "throughput_tier": "auto"
    },
    {
      "id": "qwen3.5:4b",
      "provider": "ollama",
      "tokens_per_sec": 1450,
      "throughput_tier": "local"
    }
  ],
  "node_specialization": "worker",
  "services": ["ollama:11434"]
}
```

**Fields:**
- `models[]` — Array of installed models
  - `id` — Model identifier (e.g., `gemma4:e4b`)
  - `provider` — Model provider (`ollama`, `cloud`)
  - `tokens_per_sec` — Benchmark throughput
  - `throughput_tier` — `local`, `auto`, `embedding`
- `node_specialization` — Optional role (`vector-memory`, `primary-depot`, `secondary-depot`, `worker`)
- `services` — Optional list of services running on node

### model-router.json

```json
{
  "router_profiles": {
    "auto": {
      "description": "Automatic routing based on complexity",
      "TRIVIAL": "qwen3.5:4b",
      "SIMPLE": "qwen3:8b",
      "MEDIUM": "gemma4:e4b",
      "HARD": "kimi-k2.6:cloud"
    },
    "local": {
      "description": "Local models only",
      "TRIVIAL": "qwen3.5:4b",
      "SIMPLE": "qwen3:8b",
      "MEDIUM": "gemma4:e4b",
      "HARD": "gemma4:e4b"
    },
    "cloud": {
      "description": "Cloud models for all tasks",
      "TRIVIAL": "qwen3.5:397b-cloud",
      "SIMPLE": "qwen3.5:397b-cloud",
      "MEDIUM": "qwen3.5:397b-cloud",
      "HARD": "kimi-k2.6:cloud"
    },
    "fast": {
      "description": "Fastest model per complexity tier",
      "TRIVIAL": "qwen3.5:4b",
      "SIMPLE": "qwen3:8b",
      "MEDIUM": "gemma4:e4b",
      "HARD": "kimi-k2.6:cloud"
    }
  },
  "default_profile": "auto",
  "node_id": "fnet3",
  "node_name": "Vector Memory Node (ChromaDB)"
}
```

**Fields:**
- `router_profiles` — Named routing configurations
  - Profile name (`auto`, `local`, `cloud`, `fast`)
  - `description` — Human-readable explanation
  - Complexity tier mappings (`TRIVIAL`, `SIMPLE`, `MEDIUM`, `HARD`)
- `default_profile` — Default routing profile for this node
- `node_id` — Node identifier (e.g., `fnet3`)
- `node_name` — Human-readable node name

### node-capacity-summary.json

```json
{
  "generated_at": "2026-05-12T21:30:00Z",
  "total_nodes": 7,
  "nodes": {
    "fnet1": {
      "node_name": "Primary Depot Node",
      "specialization": "primary-depot",
      "models_installed": ["gemma4:e4b", "qwen3:8b", "qwen3.5:4b"],
      "primary_model": "qwen3:8b",
      "tokens_per_sec": 2200,
      "throughput_tier": "auto",
      "status": "active"
    }
  },
  "cluster_capacity": {
    "total_tokens_per_sec": 14150,
    "fastest_node": "fnet1",
    "vector_memory_node": "fnet3",
    "depot_nodes": ["fnet1", "fnet6"],
    "worker_nodes": ["fnet4", "fnet5", "fnet7"]
  }
}
```

---

## How to Update Node Configs

### After Installing New Models

1. **Pull the model on the node:**
   ```bash
   ssh fnet3 "ollama pull nomic-embed-text"
   ```

2. **Update models.json:**
   Add the new model to the `models` array:
   ```json
   {
     "id": "nomic-embed-text",
     "provider": "ollama",
     "tokens_per_sec": 5000,
     "throughput_tier": "embedding",
     "purpose": "ChromaDB embeddings"
   }
   ```

3. **Re-run benchmark (optional but recommended):**
   ```bash
   cd technical-infrastructure
   python3 scripts/benchmark-suite.py --node fnet3 --model nomic-embed-text
   ```

4. **Update node-capacity-summary.json:**
   Add model to `models_installed` list.

### After Hardware Changes

1. **Update RAM/CPU specs in models.json:**
   ```json
   {
     "safe_model_size_gb": 31.0,
     "node_ram_gb": 32,
     "node_cpu_cores": 8
   }
   ```

2. **Re-run benchmark suite:**
   ```bash
   python3 scripts/benchmark-suite.py --node fnet3 --all-models
   ```

3. **Regenerate node-capacity-summary.json:**
   ```bash
   python3 scripts/generate-node-profiles.py
   ```

### After Node Additions/Removals

1. **Add new node:**
   ```bash
   mkdir -p lab-specs/node-configs/fnet8
   cp lab-specs/node-configs/fnet1/models.json lab-specs/node-configs/fnet8/
   cp lab-specs/node-configs/fnet1/model-router.json lab-specs/node-configs/fnet8/
   ```

2. **Edit node_id in model-router.json:**
   ```json
   {
     "node_id": "fnet8",
     "node_name": "New Worker Node"
   }
   ```

3. **Update node-capacity-summary.json:**
   Add new node entry.

4. **Remove node:**
   ```bash
   rm -rf lab-specs/node-configs/fnet8
   ```

---

## How to Regenerate All Configs Automatically

Use the benchmark suite to auto-detect hardware and generate configs:

```bash
cd /Users/friasc/Cloud/workshop/technical-infrastructure

# Detect hardware on all nodes
python3 scripts/remote-detect.sh --all-nodes

# Run benchmarks on all nodes
python3 scripts/benchmark-lab.sh --all-nodes

# Generate node configs from benchmark data
python3 scripts/generate-node-profiles.py
```

This will:
1. SSH to each node
2. Detect RAM, CPU, GPU, storage
3. Run model benchmarks (tokens/sec)
4. Generate `models.json` and `model-router.json` for each node
5. Create `node-capacity-summary.json` index

---

## Testing the Node Registry

Verify configs are valid:

```bash
cd /Users/friasc/Cloud/workshop/technical-infrastructure

# Dump all node configs
python3 scripts/ti011_node_registry.py --dump

# Query specific node
python3 scripts/ti011_node_registry.py --query fnet3

# Test model selection
python3 -c "
from ti011_node_registry import NodeRegistry
reg = NodeRegistry()
print(reg.best_model_for(complexity='medium', vision=False))
"
```

Expected output:
```
Node Registry: 7 nodes loaded
Config dir: /Users/friasc/Cloud/workshop/lab-specs/node-configs

=== Per-Node Compute Cost ===
  fnet1: $0.0370/hour (RAM: ?GB)
  ...

=== Model Cost Per 1K Tokens ===
  fnet1 ($0.0370/hour):
    • gemma4:e4b (?): 1700 t/s → $0.0000 per 1K tokens
    ...
```

---

## Node Specializations

| Node | Specialization | Purpose |
|------|---------------|---------|
| **fnet1** | `primary-depot` | Primary model depot, high-throughput worker |
| **fnet2** | `nextcloud` | NextCloud services + general worker |
| **fnet3** | `vector-memory` | ChromaDB vector store + RAG retrieval |
| **fnet4** | `worker` | General-purpose worker |
| **fnet5** | `worker` | General-purpose worker |
| **fnet6** | `secondary-depot` | Backup model depot |
| **fnet7** | `worker` | General-purpose worker |

---

## Routing Profiles

| Profile | Use Case | Description |
|---------|----------|-------------|
| **auto** | Default | Routes by complexity: TRIVIAL→local low, HARD→cloud high |
| **local** | Cost savings | All tasks on local models, no cloud escalation |
| **cloud** | Maximum quality | All tasks on cloud models |
| **fast** | Low latency | Fastest available model per complexity tier |

---

## Related Documentation

- [TI-011 Orchestration Guide](../technical-infrastructure/wiki/guides/ti011-orchestration.md)
- [Master Prompt System](../technical-infrastructure/packages/master-prompt-system/core-prompt.md)
- [Node Benchmark Suite](../technical-infrastructure/scripts/benchmark-suite.py)
- [Node Registry Script](../technical-infrastructure/scripts/ti011_node_registry.py)

---

**Last Updated:** 2026-05-12  
**Version:** 1.0.0  
**Maintainer:** Technical Infrastructure Team
