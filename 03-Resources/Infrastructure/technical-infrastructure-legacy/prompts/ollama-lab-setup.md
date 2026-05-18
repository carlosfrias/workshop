# Ollama Lab Setup Prompt (Decomposed)

**Version**: 2026-04-29  
**Purpose**: Complete Ollama deployment across tiered lab infrastructure with hardware awareness, depot-based sync, and performance validation.
**Prerequisites**: SSH access to all lab nodes, Ansible installed, inventory.yml configured.

---

## Context

Read `technical-infrastructure/lab-specs/lab-capacity-report.json` before any action.

### Lab Topology

| Tier | Nodes | RAM | Models | Use Case |
|------|-------|-----|--------|----------|
| **Tier 1** | fnet3-6 | 31GB | gemma4:e4b, qwen3:8b, qwen3.5:4b | Heavy inference, flagship workloads |
| **Tier 2** | fnet1-2, fnet7 | 14-16GB | qwen3:8b, qwen3.5:4b | General tasks, monitoring |
| **Orchestrator** | localhost | 16GB | qwen3.5:4b, gemma4:e4b* | Local routing |

*Orchestrator gemma4:e4b requires **explicit user approval** before deployment.

### Depot Node

- **Host**: fnet3 (192.168.0.143)
- **Purpose**: Single internet download point; all other nodes sync blobs via LAN
- **Storage**: /usr/share/ollama/.ollama/models/ (systemd service path)

### Performance Baseline ( Established on 2026-04-29 )

| Node | Model | Tokens/sec | Verdict |
|------|-------|-----------|---------|
| fnet3 (Tier 1) | qwen3.5:4b | 5.09 | ✅ Deploy |
| fnet3 (Tier 1) | gemma4:e4b | 4.58 | ✅ Deploy |
| fnet3 (Tier 1) | qwen3:8b | 3.83 | ✅ Deploy |
| fnet2 (Tier 2) | qwen3.5:4b | 2.60 | ⚠️ Acceptable |
| fnet2 (Tier 2) | gemma4:e4b | 0.65 | ❌ Do NOT deploy |

---

## Execution Phases

### Phase 0 — Orchestrator Prompt (Mandatory Gate)

**If inventory_hostname is localhost (orchestrator):**
- STOP.
- Ask user: "I am about to modify models on the orchestrator node. Confirm which models to deploy."
- Default: only qwen3.5:4b
- Do NOT auto-deploy gemma4:e4b without explicit approval.

### Phase 1 — Hardware Validation

```bash
# Run on each target node
./scripts/extract-hardware-specs.sh --save
```

**Critical Checks:**
- RAM >= 8GB (fail if less)
- Disk free >= 30GB (fail if less)
- ollama.com reachable (warn if not — depot sync will be needed)

**OS Validation:**
- Ubuntu 24.04 LTS preferred
- Ubuntu 20.04 flagged as EOL (fnet3-5)
- Ubuntu 26.04 flagged as unstable (fnet2)

### Phase 2 — Depot Preparation (Run Once)

On the depot node (fnet3):
```bash
# Ensure service is running
sudo systemctl start ollama

# Pull models (ONE time from internet)
ollama pull gemma4:e4b
ollama pull qwen3:8b
ollama pull qwen3.5:4b

# Validate each model loads
for m in gemma4:e4b qwen3:8b qwen3.5:4b; do
  ollama run $m "hello" > /dev/null && echo "$m OK"
done
```

### Phase 3 — Tier 1 Deployment

```bash
# For each Tier 1 node, sync from depot
for node in fnet3 fnet4 fnet5 fnet6; do
  ./scripts/ollama-lab-setup.sh $node tier1 192.168.0.143
done
```

**Fallback**: If LAN rsync fails, direct pull with `OLLAMA_NUM_PARALLEL=1`.

### Phase 4 — Tier 2 Deployment

```bash
for node in fnet1 fnet2 fnet7; do
  ./scripts/ollama-lab-setup.sh $node tier2 192.168.0.143
done
```

**Constraint**: Do NOT deploy gemma4:e4b to Tier 2 regardless of inventory spec. Benchmark confirmed 0.65 tok/s = unusable.

### Phase 5 — Benchmarking

```bash
# Tier 1 reference
./scripts/ollama-benchmark.sh fnet3 gemma4:e4b 128
./scripts/ollama-benchmark.sh fnet3 qwen3.5:4b 128

# Tier 2 reference
./scripts/ollama-benchmark.sh fnet2 qwen3.5:4b 128
```

**Decision Gate**: If tokens/sec < 5 for qwen3.5:4b on any node, flag for investigation (thermal throttling, CPU governor, disk I/O).

### Phase 6 — Validation

```bash
# Verify all nodes have correct models
ansible-playbook -i ansible/inventory.yml playbooks/setup-ollama.yml --tags validate
```

Expected result: `ollama list` on each node matches its tier's model manifest.

---

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `scripts/extract-hardware-specs.sh` | Cross-platform hardware/JSON detection |
| `scripts/ollama-lab-setup.sh` | Master manual deployment (host tier depot_ip) |
| `scripts/model-depot-sync.sh` | LAN blob sync between nodes |
| `scripts/ollama-benchmark.sh` | HTTP API performance tracking |
| `scripts/ollama-cleanup.sh` | Reset for testing cycles |

## Ansible Reference

```bash
cd technical-infrastructure/ansible

# Full deployment (parallel across all nodes)
ansible-playbook -i inventory.yml playbooks/setup-ollama.yml

# With benchmarking
ansible-playbook -i inventory.yml playbooks/setup-ollama.yml -e "run_benchmarks=true"

# Cleanup for reset
ansible-playbook -i inventory.yml playbooks/cleanup-ollama.yml

# Hardware spec collection
ansible-playbook -i inventory.yml playbooks/gather-hardware-specs.yml
```

## Known Constraints

| Constraint | Mitigation |
|-----------|------------|
| Inter-node rsync requires SSH key auth | Orchestrator key already on all nodes (`authorized_keys` verified) |
| Ubuntu 20.04 EOL April 2025 | Flagged for reimaging; playbook still works |
| fnet2 on Ubuntu 26.04 (unstable) | Flagged for reimaging; direct pull may encounter package conflicts |
| Orchestrator model changes | **User approval required** — prompt hardcoded |
| gemma4:e4b on Tier 2 | Benchmarked at 0.65 tok/s — blocked by setup script |

## Quality Gates

- [ ] All nodes return empty `ollama list` after cleanup
- [ ] Depot node (fnet3) has all 3 models and can load each
- [ ] Tier 1 nodes have gemma4:e4b, qwen3:8b, qwen3.5:4b
- [ ] Tier 2 nodes have qwen3:8b, qwen3.5:4b (NO gemma4:e4b)
- [ ] Benchmarks logged for at least one Tier 1 and one Tier 2 node
- [ ] Re-deployment via Ansible completes in < 30 minutes for all 7 lab nodes
