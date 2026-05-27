---
name: lab-fleet-deployment
description: Site-specific deployment config for the fnet lab fleet (7 nodes, hub on fnet2:8080). Hub URL, auth token, node inventory, playbook triggers, monitoring commands. Use when operating this specific fleet deployment.
scope: project
---

# Lab Fleet Deployment — Manifest

**Decomposed skill.** Do NOT load all sections at once. Use the load directive below.

## [S-TIGHT]

7-node lab fleet. Hub on fnet2 (192.168.0.142:8080). Auth token in env var or `-e` flag. 5 agents typically online (fnet3–7). Standup via `standup-fleet.yml`. Monitor via curl + SSH. Load only the section you need per the table below.

---

## Section Table

| Section | File | Size | LOD | What It Covers | Load When |
|---------|------|------|-----|----------------|-----------|
| INVENTORY | [INVENTORY.md](INVENTORY.md) | ~1.5KB | Low | Node IPs, roles, Ollama models, topology diagram | Always (core reference) |
| CONNECTION | [CONNECTION.md](CONNECTION.md) | ~1.1KB | Low | Hub URL, auth, project name, connect command | Connecting to fleet or configuring agents |
| MONITORING | [MONITORING.md](MONITORING.md) | ~2.3KB | Medium | Fleet status one-liner, SSH checks, key file paths | Checking fleet health or debugging |
| PLAYBOOKS | [PLAYBOOKS.md](PLAYBOOKS.md) | ~1.4KB | Low | Ansible triggers, phases, run commands | Standing up fleet or re-launching agents |
| TROUBLESHOOTING | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | ~1.3KB | Medium | Symptom → check → fix table, escalation path | Diagnosing fleet issues |

## Load Directive

| Model Tier | Max Sections | Strategy |
|------------|-------------|----------|
| **Low** (<4K ctx) | 2 | INVENTORY.md + one task-relevant section only |
| **Medium** (~8K ctx) | 3 | INVENTORY.md + up to 2 task-relevant sections |
| **High** (~32K ctx) | 5 | INVENTORY.md + all others as needed |
| **Cloud** (>32K ctx) | All | Load full skill if needed; prefer targeted sections |

## Quick Task Routing

| Task | Load |
|------|------|
| Check fleet health | INVENTORY.md → MONITORING.md |
| Connect to fleet | INVENTORY.md → CONNECTION.md |
| Stand up / re-launch fleet | INVENTORY.md → PLAYBOOKS.md |
| Diagnose a problem | TROUBLESHOOTING.md → MONITORING.md |
| Configure a new agent | INVENTORY.md → CONNECTION.md |
| Full deployment from scratch | INVENTORY.md → CONNECTION.md → PLAYBOOKS.md |

---

## Cross-References

- `pi-cross-node-comms` skill — coms-net tool surface (portable)
- `fleet-dispatcher-cascade` skill — three-tier cascade pattern (portable)
- Wiki: `fleet-operations/Monitoring & Management` — full API reference and dashboard

## Machine-Readable Manifest

See [MANIFEST.json](MANIFEST.json) for programmatic section loading by task type.