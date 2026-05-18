# Hardware Spec Extraction Prompt

## Objective
Extract comprehensive hardware specifications from a target node to determine Ollama capacity, optimal model tiering, and OS standardization status.

## Execution

```bash
./scripts/extract-hardware-specs.sh [--save]
```

## Output Schema

```json
{
  "timestamp": "2026-04-29T12:00:00Z",
  "node": "fnet1",
  "system": {
    "hostname": "...",
    "os": "GNU/Linux",
    "kernel": "6.17.0-22-generic",
    "arch": "x86_64",
    "dist_name": "Ubuntu 24.04.4 LTS",
    "dist_version": "24.04",
    "dist_codename": "noble",
    "dist_id": "ubuntu"
  },
  "cpu": {
    "model": "Intel i5-6400",
    "cores": 4,
    "flags": ["avx2"]
  },
  "memory": {
    "total_gb": 15,
    "available_gb": 13,
    "swap_total_gb": 238
  },
  "gpu": {
    "detected": true,
    "model": "Intel HD Graphics 530",
    "vram_gb": 0,
    "driver": ""
  },
  "storage": {
    "total_gb": 227,
    "free_gb": 136,
    "ollama_dir_exists": true,
    "ollama_dir_size_gb": 47
  },
  "network": {
    "ollama_com_reachable": true,
    "download_speed_mbps": 0,
    "latency_ms": 0
  },
  "ollama": {
    "installed": true,
    "version": "0.20.2",
    "service_active": true,
    "models": ["qwen3:8b", "qwen3.5:4b", "gemma4:e4b"]
  }
}
```

## Decision Gates

| Condition | Tier | Action |
|-----------|------|--------|
| RAM >= 31GB | Tier 1 | gemma4:e4b, qwen3:8b, qwen3.5:4b |
| RAM 14-16GB | Tier 2 | qwen3:8b, qwen3.5:4b only |
| RAM < 8GB | — | Fail preflight |
| dist_version != "24.04" | — | Flag for OS standardization |
| dist_codename == "focal" | — | URGENT — EOL April 2025 |
| dist_codename == "resolute" | — | CRITICAL — unstable pre-release |
| download_speed_mbps < 10 | — | Activate depot sync |
| disk_free_gb < 50 | — | Flag disk pressure |

## Standardization Target

All lab nodes should converge to **Ubuntu 24.04 LTS (noble)**.

```yaml
os_standardization_target:
  dist: "Ubuntu"
  version: "24.04"
  codename: "noble"
  supported_until: "2029-04"
```
