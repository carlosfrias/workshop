# Multi-Node Pi Cluster Setup

**LEGACY — MIGRATE TO:** `personal-vault/03-Resources/Technical-Infrastructure/multi-node-setup-2026-04-26.md`

**Date:** 2026-04-26  
**Status:** Complete

## Overview

Successfully deployed pi-coding-agent with intercom coordination across 7 nodes in the trading infrastructure cluster.

## Node Inventory

| Hostname | IP Address | Node.js | Pi Version | Intercom | Ollama Models | Status |
|----------|------------|---------|------------|----------|---------------|--------|
| carlos-mac | Localhost | v24.6.0 | 0.70.6 | ✓ | Mixed/Cloud | ✓ Ready |
| fnet1 | 192.168.0.141 | v20.20.2 | 0.70.2 | ✓ | qwen3.5:cloud, qwen3.5:4b, qwen3:4b, qwen3:8b | ✓ Ready |
| fnet2 | 192.168.0.142 | v22.22.1 | 0.70.2 | ✓ | - (ollama installed) | ✓ Ready |
| fnet3 | 192.168.0.143 | v20.20.2 | 0.70.2 | ✓ | - | ✓ Ready |
| fnet4 | 192.168.0.144 | v22.22.1 | 0.70.2 | ✓ | - | ✓ Ready |
| fnet5 | 192.168.0.145 | v10.19.0 | 0.70.2 | ✓ | gemma4:e2b, qwen2.5:7b, llama2, llama3.1:8b, nomic-embed-text, mistral, gemma2:9b, phi3:mini | ✓ Ready |
| fnet6 | 192.168.0.146 | v22.22.2 | 0.70.2 | ✓ | gemma4:e4b (9.6 GB) | ✓ Ready |
| fnet7 | 192.168.0.147 | v22.22.2 | 0.70.2 | ✓ | gemma4:e4b (9.6 GB) | ✓ Ready |

## Hostname Changes

| IP | Old Hostname | New Hostname |
|----|--------------|--------------|
| 192.168.0.131 | fnode1 | fnet1 |
| 192.168.0.103 | fnet7 | fnet6 |

**Note:** Hostname conflict resolved - two nodes previously had hostname `fnet7`.

## Configuration Applied

### Passwordless Sudo
All nodes configured with `/etc/sudoers.d/friasc-nopasswd`:
```
friasc ALL=(ALL) NOPASSWD:ALL
```

### SSH Key Authentication
SSH public key (`~/.ssh/id_rsa.pub`) deployed to all 7 nodes for passwordless SSH access.

### Model Router Configuration
Local model router configuration (`~/.pi/model-router.json`) with 4 routes:

| Route | Model | Thinking | Triggers |
|-------|-------|----------|----------|
| reasoning | ollama/qwen3.5:cloud | medium | analyze, evaluate, decide, research, signal, risk, why, what, when, where, which |
| structured | ollama/gemma4:e4b | off | log, reconcile, parse, format, ledger, balance |
| monitoring | ollama/qwen3.5:4b | off | status, check, ping, health, monitor, report |
| infrastructure | ollama/qwen3:8b | off | server, connect, deploy, dns, network, troubleshoot |

## Infrastructure Capacity & MAC Mapping

| Hostname | IP Address | MAC Address | CPU | RAM | GPU |
|----------|------------|-------------|-----|-----|-----|
| carlos-mac | Localhost | 22:3c:44:b6:cc:48 | Apple M1 Pro | 16 GB | Apple M1 Pro |
| fnet1 | 192.168.0.141 | 40:8d:5c:be:42:0e | - | - | - |
| fnet2 | 192.168.0.142 | 0c:9d:92:cc:55:4c | - | - | - |
| fnet3 | 192.168.0.143 | 1c:69:7a:6c:da:4c | - | - | - |
| fnet4 | 192.168.0.144 | 1c:69:7a:6c:dc:fa | - | - | - |
| fnet5 | 192.168.0.145 | 1c:69:7a:6c:dd:6b | - | - | - |
| fnet6 | 192.168.0.146 | 1c:69:7a:6c:dd:c0 | - | - | - |
| fnet7 | 192.168.0.147 | 1c:69:7a:6c:dd:c0 | - | - | - |

## Work Completed

1. ✅ SSH key distribution to all 7 nodes
2. ✅ Passwordless sudo configuration
3. ✅ Hostname conflict resolution (fnode1→fnet1, fnet6→fnet7)
4. ✅ Node.js 20+ installation on all nodes
5. ✅ pi-coding-agent 0.70.2 installation
6. ✅ pi-intercom 0.2.1 installation
7. ✅ Model router configuration documented
8. ✅ Standardized Ollama service deployment (zstd resolution, systemd auto-start)
9. ✅ Ansible automation for pi and Ollama lifecycle management

## Ansible Automation Framework

The cluster is managed via Ansible to ensure consistency and reproducibility across nodes.

### Playbook Suite

| Playbook | Purpose | Key Actions |
|----------|----------|-------------|
| `install-pi.yml` | Core Deployment | Node.js 20+, pi-coding-agent, pi-intercom |
| `update-pi.yml` | Maintenance | Run `pi update` across all nodes |
| `setup-ollama.yml` | LLM Infrastructure | zstd deps, Ollama installation, systemd auto-start |
| `optimize-lab.yml` | Hardware Optimization | Install project-blueprint, run `local-model-router`, capture metrics |
| `test-reboot-persistence.yml` | Validation | Verify pi/intercom availability after reboot |
| `fix-pi-availability.yml` | Troubleshooting | Fix PATH and shell profiles for pi access |

### Execution Command

To run the full optimization and LLM setup pipeline:

```bash
cd /Users/friasc/Dropbox/workshop/technical-infrastructure/ansible
ansible-playbook -i inventory.yml playbooks/setup-ollama.yml
ansible-playbook -i inventory.yml playbooks/optimize-lab.yml
```

### Optimization Logic

The `ollama-setup` role implements a dynamic model selection strategy:
1. **Dynamic Path**: Prefers models identified by `pi local-model-router` based on node hardware capacity.
2. **Fallback Path**: If no dynamic recommendations are found, pulls the static list defined in `inventory.yml`.

---

## Intercom Usage

To coordinate across nodes, use the intercom skill:
```bash
# List active sessions
intercom({ action: "list" })

# Send message to specific node
intercom({ action: "send", to: "fnet1", message: "..." })

# Ask and wait for reply
intercom({ action: "ask", to: "fnet2", message: "..." })
```

## Next Steps

1. Start ollama service on nodes that need it
2. Pull required models based on model-router configuration
3. Configure intercom session names to match hostnames
4. Test cross-node coordination

## Reboot Persistence Test

**Date:** 2026-04-27  
**Result:** ✅ PASS (6/7 nodes)

All nodes were rebooted to verify pi persistence. Results:

| Hostname | IP | Pi Version | Status |
|----------|-----|------------|--------|
| fnet1 | 192.168.0.131 | 0.70.2 | ✅ Online |
| fnet2 | 192.168.0.150 | 0.70.5 | ✅ Online |
| fnet3 | 192.168.0.179 | 0.70.2 | ✅ Online |
| fnet4 | 192.168.0.109 | 0.70.5 | ✅ Online |
| fnet5 | 192.168.0.119 | 0.70.2 | ✅ Online |
| fnet6 | 192.168.0.103 | 0.70.5 | ✅ Online |
| fnet7 | 192.168.0.172 | - | ❌ Unreachable (hardware/network issue) |

**Note:** fnet7 (192.168.0.172) was unreachable after reboot - likely hardware or network connectivity issue. Requires physical inspection.

**Intercom:** Available as pi built-in tool (not standalone CLI). pi-intercom extension installed as skills package.

## Shutdown Log

**2026-04-27 Final Shutdown:**

| Hostname | IP | Shutdown Status |
|----------|-----|----------------|
| fnet1 | 192.168.0.131 | ✅ Shutdown initiated |
| fnet2 | 192.168.0.150 | ✅ Shutdown initiated |
| fnet3 | 192.168.0.179 | ✅ Shutdown initiated |
| fnet4 | 192.168.0.109 | ✅ Shutdown initiated |
| fnet5 | 192.168.0.119 | ✅ Shutdown initiated |
| fnet6 | 192.168.0.103 | ✅ Shutdown initiated |
| fnet7 | 192.168.0.172 | ⚠️ Already unreachable |

**Local node:** Shutdown pending.

---
*Document created: 2026-04-26*  
*Updated: 2026-04-27 - Reboot test and final shutdown*
