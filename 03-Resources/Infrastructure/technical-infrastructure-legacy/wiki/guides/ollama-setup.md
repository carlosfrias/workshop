# Ollama Lab Setup Guide

**LEGACY — MIGRATE TO:** `personal-vault/03-Resources/Technical-Infrastructure/ollama-setup.md`

**Last Updated**: 2026-04-29
**Status**: Infrastructure refactored, manual scripts operational, Ansible role staged.

---

## Lab Topology

```
┌─────────────────┐
│  Orchestrator   │  macOS (16GB) — Local routing, user-guarded
│  (this machine) │
└────────┬────────┘
         │ SSH control + deployment
         ▼
┌──────────────────────────────────────────┐
│              Lab Network (192.168.0.x)   │
│                                          │
│  ┌────────┐ ┌────────┐ ┌────────┐       │
│  │  fnet3 │ │  fnet4 │ │  fnet5 │  Tier 1 (31GB) — Heavy inference
│  │  fnet6 │ │        │ │        │         │
│  │ DEPOT  │ │        │ │        │         │
│  │ Ubuntu │ │ Ubuntu │ │ Ubuntu │         │
│  │ 20.04  │ │ 20.04  │ │ 20.04  │         │
│  └────────┘ └────────┘ └────────┘       │
│                                          │
│  ┌────────┐ ┌────────┐ ┌────────┐       │
│  │  fnet1 │ │  fnet2 │ │  fnet7 │  Tier 2 (14-16GB) — General purpose
│  │ Ubuntu  │ │ Ubuntu  │ │ Ubuntu  │         │
│  │ 24.04  │ │ 26.04   │ │ 22.04  │         │
│  └────────┘ └────────┘ └────────┘       │
└──────────────────────────────────────────┘
```

## Hardware Tiers

| Tier | Nodes | RAM | Models Deployed | Use Case |
|------|-------|-----|-----------------|----------|
| **Tier 1** | fnet3, fnet4, fnet5, fnet6 | 31GB | gemma4:e4b, qwen3:8b, qwen3.5:4b | Heavy inference, flagship workloads |
| **Tier 2** | fnet1, fnet2, fnet7 | 14-16GB | qwen3:8b, qwen3.5:4b | General tasks, monitoring |
| **Orchestrator** | localhost | 16GB | qwen3.5:4b, gemma4:e4b* | Local routing, prompt guard |

*Orchestrator gemma4:e4b requires explicit user approval.

## Performance Baseline

| Node | Model | Tokens/sec | Notes |
|------|-------|-----------|-------|
| **fnet3** (Tier 1) | qwen3.5:4b | 5.09 | Reference fast node |
| **fnet3** (Tier 1) | gemma4:e4b | 4.58 | Flagship speed |
| **fnet3** (Tier 1) | qwen3:8b | 3.83 | Generalist |
| **fnet2** (Tier 2) | qwen3.5:4b | 2.60 | Slow tier |
| **fnet2** (Tier 2) | gemma4:e4b | 0.65 | ⚠️ Unusable |

## Critical Finding: OS Fragmentation

The lab currently runs **four Ubuntu versions**. This must be standardized.

| Node | Current OS | Priority | Action |
|------|-----------|----------|--------|
| fnet1 | Ubuntu 24.04 LTS | Reference | ✅ Keep as target standard |
| fnet2 | Ubuntu 26.04 LTS | 🔴 Critical | Reimage → 24.04 (unstable) |
| fnet3 | Ubuntu 20.04 LTS | 🔴 Critical | Reimage → 24.04 (EOL April 2025) |
| fnet4 | Ubuntu 20.04 LTS | 🔴 Critical | Reimage → 24.04 (EOL April 2025) |
| fnet5 | Ubuntu 20.04 LTS | 🔴 Critical | Reimage → 24.04 (EOL April 2025) |
| fnet6 | Ubuntu 22.04 LTS | 🟡 Medium | Upgrade → 24.04 when convenient |
| fnet7 | Ubuntu 22.04 LTS | 🟡 Medium | Upgrade → 24.04 when convenient |

**Target standard**: Ubuntu 24.04 LTS (noble)

## Deployment Methods

### Method A: Manual (Recommended for Initial Setup)

Uses the depot pattern for fast LAN sync instead of slow WAN downloads.

```bash
# 1. Collect hardware specs
./scripts/extract-hardware-specs.sh

# 2. Clean a test node (optional)
./scripts/ollama-cleanup.sh fnet4

# 3. Deploy via depot sync
./scripts/ollama-lab-setup.sh fnet4 tier1 192.168.0.143

# 4. Benchmark
./scripts/ollama-benchmark.sh fnet4 qwen3.5:4b 128
```

### Method B: Ansible (For Scale Operations)

```bash
cd technical-infrastructure/ansible

# Cleanup all models for testing reset
ansible-playbook -i inventory.yml playbooks/cleanup-ollama.yml

# Deploy to all nodes
ansible-playbook -i inventory.yml playbooks/setup-ollama.yml

# Deploy with benchmarking
ansible-playbook -i inventory.yml playbooks/setup-ollama.yml -e "run_benchmarks=true"
```

### Method C: Model Depot Sync (Inter-Node)

For copying models between already-configured nodes:

```bash
# Sync specific models from depot to target
./scripts/model-depot-sync.sh 192.168.0.143 192.168.0.144 gemma4:e4b,qwen3:8b

# Sync entire model directory
./scripts/model-depot-sync.sh 192.168.0.143 192.168.0.144
```

**Note**: Inter-node rsync requires SSH key authentication between lab nodes (not yet configured). Alternative: copy via orchestrator as middleman.

## Scripts Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/extract-hardware-specs.sh` | Cross-platform hardware detection | `./extract-hardware-specs.sh --save` |
| `scripts/ollama-lab-setup.sh` | Master manual deployment | `./ollama-lab-setup.sh <host> <tier>` |
| `scripts/model-depot-sync.sh` | LAN blob sync between nodes | `./model-depot-sync.sh <depot_ip> <target_ip> [models]` |
| `scripts/ollama-benchmark.sh` | Performance tracking | `./ollama-benchmark.sh <host> <model> [tokens]` |
| `scripts/ollama-cleanup.sh` | Model reset for testing | `./ollama-cleanup.sh <host> \| all \| --local` |

## Known Issues & Resolutions

| Issue | Status | Resolution |
|-------|--------|------------|
| WAN download saturation (3+ hrs/node) | ✅ Solved | Depot pattern (fnet3 as LAN cache) |
| Ansible role blindly re-pulls models | ✅ Fixed | Idempotent `creates:` guard in models.yml |
| Benchmark via `ollama run` CLI corrupted | ✅ Solved | HTTP API via Python for clean JSON timing |
| Nodes run mixed Ubuntu versions | ⚠️ Flagged | OS standardization to 24.04 required |
| Inter-node SSH for rsync depot sync | ⚠️ Blocked | SSH keys between nodes not configured; manual sync works via scripts |
| fnet2 + gemma4:e4b = 0.65 tok/s | ⚠️ Validated | Do NOT deploy gemma4:e4b to Tier 2 nodes |

## Ansible Structure

```
ansible/
├── ansible.cfg                  # Roles path, SSH options
├── inventory.yml               # Tiered inventory with OS metadata
├── playbooks/
│   ├── setup-ollama.yml        # Main deployment
│   ├── cleanup-ollama.yml      # Reset for testing
│   └── gather-hardware-specs.yml  # Mass spec collection
└── roles/
    └── ollama-setup/
        └── tasks/
            ├── main.yml        # Orchestrator
            ├── preflight.yml   # RAM/disk/URL checks
            ├── depot.yml       # Seed depot (run_once)
            ├── install.yml     # Binary + systemd
            ├── models.yml      # Pull with idempotency
            ├── validate.yml    # API health check
            ├── benchmark.yml   # Optional perf test
            └── cleanup.yml     # Purge all models
```

## Next Steps

1. **OS Standardization**: Reimage Tier 1 nodes (fnet3, fnet4, fnet5) to Ubuntu 24.04 before EOL
2. **SSH Key Mesh**: Add orchestrator SSH key to all nodes' `~/.ssh/authorized_keys` for passwordless rsync
3. **Depot Sync Automation**: Enable Ansible to use depot sync once SSH mesh is ready
4. **Continuous Benchmarking**: Add cron job or systemd timer for weekly benchmark runs
5. **Model Lifecycle**: Establish policy for updating models (depot first, then re-sync)

## Prompts

- **`prompts/ollama-lab-setup.md`** — Master orchestrator prompt for full lab deployment
- **`prompts/hardware-spec-extraction.md`** — Hardware detection specification
- **`prompts/optimize-model-routing.md`** — Model routing optimization (existing)
