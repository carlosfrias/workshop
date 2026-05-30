---
tags:
  - infrastructure
  - pi-cross-node-comms
  - fleet
  - PARA
  - area
version: 0.3.1
status: active
last_updated: 2026-05-29
---

# pi-cross-node-comms — Project AGENTS

**Purpose:** Cross-node SSE coordination, fleet standup, and coms-net hub/agent management.

## [S-TIGHT]

Project AGENTS for `workshop/02-Areas/Infrastructure/pi-cross-node-comms/`. Contains the Ansible fleet standup playbooks, coms-net hub server, and pi extension source. Read this file for project-level routing, then load the refined agents for battle-tested rules.

---

## Project Status

| | |
|---|---|
| **Status** | 🔧 Active |
| **Version** | 0.2.1 |
| **Upstream** | `carlosfrias/pi-cross-node-comms` (GitHub private, main branch) |
| **Last release** | `0328ee24` — fix(fleet): eliminate idle CPU burn from persistent Ollama connections |

## Key Files

| Path | Purpose |
|------|---------|
| `ansible/standup-fleet.yml` | Full fleet standup (6 phases) |
| `ansible/phase1-hub-server.yml` | Docker hub deploy on fnet2 |
| `ansible/phase2-pi-availability.yml` | Pi agent install/upgrade via nvm |
| `ansible/phase3-ollama-models.yml` | LVM expansion + Ollama + model pulls |
| `ansible/phase4-extension-deploy.yml` | coms-net extension deploy |
| `ansible/phase5-agent-services.yml` | Systemd agent launch |
| `ansible/phase6-fleet-validation.yml` | Fleet validation + prune down nodes |
| `ansible/deploy-fleet.yml` | Legacy fleet deploy |
| `ansible/start-agents.yml` | Start agents (standalone) |
| `ansible/shutdown-fleet.yml` | Graceful fleet shutdown |
| `ansible/systemd/` | Systemd unit templates and wrapper |
| `server/coms-net-server.ts` | Hub server source |
| `src/` | coms-net extension source |
| `tests/unit/` | TDD test suite (5 files, 42 tests) |
| `tests/integration/` | Integration test suite |

## Refined Agents

| Version | Date | Session | Key Rules |
|---------|------|---------|-----------|
| [v1](./refined-agents/AGENTS-REFINED-v1.md) | 2026-05-29 | fleet-standup-bugfix | Workshop-first, TDD for playbooks, paren balance |
| [v3](./refined-agents/AGENTS-REFINED-v3.md) | 2026-05-30 | fleet-idle-cpu-burn | No hardcoded --model, OLLAMA_KEEP_ALIVE=0, fan/governor checks |
| [v4](./refined-agents/AGENTS-REFINED-v4.md) | 2026-05-29 | fleet-model-loading-root-cause | pi-model-router required, defaultModel required (NOT removed), fleet-cooling systemd oneshot |

## Routing

| What are you trying to do? | Load this |
|----------------------------|-----------|
| Stand up or manage the fleet | `ansible/standup-fleet.yml` |
| Fix a playbook syntax error | `tests/unit/test-ansible-playbook-syntax.sh` |
| Check when-clause balance | `tests/unit/test-ansible-when-clauses.sh` |
| Verify pi version currency | `tests/unit/test-ansible-pi-version.sh` |
| Check systemctl status comparisons | `tests/unit/test-ansible-systemctl-status.sh` |
| Run full integration | `tests/integration/test-fleet-standup-integration.sh` |
| Update playbooks for fleet | Refined agents v1 (release pipeline rule) |
| Push changes to .pi | Refined agents v1 (workshop-first rule — NEVER edit .pi directly) |

## Discovery Path

```
1. carlos-desktop/AGENTS.md                    ← Root router (pick workspace)
2. workshop/AGENTS.md                          ← Workspace router
3. workshop/02-Areas/Infrastructure/AGENTS.md  ← Domain router
4. pi-cross-node-comms/AGENTS.md              ← YOU ARE HERE (project router)
5. pi-cross-node-comms/FOCUS.md               ← Current state
6. pi-cross-node-comms/refined-agents/         ← Battle-tested rules by version
```

---

*Last updated: 2026-05-29*