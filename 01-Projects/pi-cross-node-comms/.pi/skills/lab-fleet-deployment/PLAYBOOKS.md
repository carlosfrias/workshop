---
section_id: playbooks
size_estimate: ~1.4KB
lod_level: Low
purpose: Ansible playbook triggers and commands for fleet standup and agent relaunch.
---

# Playbook Triggers

## [S-TIGHT]

Ansible playbook commands and trigger phrases for fleet standup, agent relaunch, and single-node targeting.

[LOD: Low] *Load when standing up the fleet or re-launching agents.*

## Trigger Table

| Trigger | Playbook | What It Does |
|---------|----------|-------------|
| `standup_fleet` / `stand up the fleet` | `standup-fleet.yml` | Full 6-phase standup |
| `--start-at-task "Kill any existing agent"` | Phase 5–6 | Re-launch agents |
| `--limit fnet3` | Any phase | Target single node |

## Commands

```bash
# Full standup (via helper script)
./scripts/run-playbook.sh "stand up the fleet"

# Direct ansible
cd workshop/01-Projects/pi-cross-node-comms/ansible
ansible-playbook -i inventory.yml standup-fleet.yml

# Re-launch agents only (skip phases 1–4)
ansible-playbook -i inventory.yml standup-fleet.yml \
  --start-at-task "Kill any existing agent on this node"

# Target a single node
ansible-playbook -i inventory.yml standup-fleet.yml \
  --start-at-task "Kill any existing agent on this node" \
  --limit fnet3
```

## Playbook Phases (reference)

1. Install deps (Bun, Node)
2. Deploy hub on fnet2
3. Install Ollama + pull models
4. Deploy extension code
5. Kill existing agents
6. Launch agents

---

*See also: [MONITORING.md](MONITORING.md) for post-standup health checks, [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for failed standup recovery.*