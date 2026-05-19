# TI-041: Pi Sessions on Lab Nodes — Integration Plan

**Date:** 2026-05-14
**Status:** 📋 PLANNED — Ready for Phase 1 Execution
**Scope:** pi CLI, lab nodes fnet1–fnet7, intercom broker, systemd/tmux persistence
**Session Context:** Close the cross-node intercom gap identified in TI-039 smoke test.

---

## 📊 Project Status Summary

| Phase | Status | Key Deliverable |
|-------|--------|-----------------|
| P1 (Playbook Verification) | 📋 Ready | All nodes trigger ≥0 playbooks via playbook-executor |
| P2 (Persistence) | 📋 Ready | systemd services + intercom connectivity |
| P3 (Integration) | 📋 Ready | `decomposed-intercom-dispatch` chain updated |
| P4 (Monitoring) | 📋 Ready | pi-agent health monitor active |
| P5 (Doc) | 📋 Ready | Setup & Troubleshooting guide |

**Critical backlog:** [`ti041-backlog.md`](./ti041-backlog.md)

---

## Navigation

- [Model Responsibility](#model-responsibility)
- [Anti-Hallucination Safeguards](#anti-hallucination-safeguards)
- [Infrastructure Methodology](#infrastructure-methodology)
- [Test Architecture](#test-architecture)
- [Phase Plan](#phase-plan)
- [Backlog Items](#backlog-items)
- [Lab Node Dispatch Rules](#lab-node-dispatch-rules)
- [Local Node Recovery](#local-node-recovery)
- [High-Frequency Decomposition](#high-frequency-decomposition)
- [Node Health Report](#node-health-report)
- [Decision Log](#decision-log)
- [Session Notes](#session-notes)

---

## Model Responsibility

| Tier | Model | Role | Executes Code? | Typical Assignment |
|------|-------|------|---------------|-------------------|
| **High Cloud** | `ollama/kimi-k2.6` | Plan Owner & Decomposer | **NO** | Architecture and logic flows |
| **Medium Cloud** | `ollama/deepseek-v4-pro` | Analysis Assistant | **NO** | Performance analysis |
| **Low Cloud** | `ollama/qwen3.5:397b` | Orchestrator | **YES** (last resort) | Coordination and dispatch |
| **High Local** | `ollama/qwen3:8b` | Complex Execution | **YES** | Complex bash scripts |
| **Medium Local** | `ollama/gemma4:e4b` | Standard Execution | **YES** | Installation tasks |
| **Low Local** | `ollama/qwen3.5:4b` | Simple Execution | **YES** | Connectivity pings |

**Execution Rule:** All node operations execute through `playbook-executor` triggers. Zero direct commands. The orchestrator triggers playbooks; playbook-executor dispatches Ansible to nodes.

---

## Anti-Hallucination Safeguards

Every playbook execution returns structured JSON:
1. **Connectivity Evidence:** `{"node_id": "fnetN", "status": "reachable"}` from `check_connectivity.yml` trigger.
2. **Installation Evidence:** `{"pi_version": "0.74.0", "status": "ok"}` from `verify_pi.yml` trigger.
3. **Verification:** Trigger `verify_intercom` → playbook confirms intercom reply received.

---

## Playbook-Executor Integration

This plan delegates **every** node-level operation to the `playbook-executor` package. No direct commands of any kind.

### All Playbook Triggers

| Trigger | Playbook | Purpose | Target |
|---------|----------|---------|--------|
| `check_connectivity` | `check_connectivity.yml` | Confirm node is reachable | Per-node |
| `check_node_version` | `check_node_version.yml` | Verify Node.js ≥ v20 | fnet1–fnet7 |
| `deploy_pi` | `deploy-pi.yml` | Install/upgrade pi CLI | fnet1–fnet7 |
| `update_packages` | `update_packages_v1.0.yml` | Upgrade Node.js and system packages | fnet1–fnet7 |
| `verify_pi` | `verify_pi.yml` | Confirm pi version + PATH | Per-node |
| `verify_intercom` | `verify_intercom.yml` | Confirm intercom loopback works | Per-node |
| `configure_pi_service` | `configure-pi-service.yml` | Deploy systemd unit | fnet1–fnet7 |
| `enable_pi_service` | `enable_pi_service.yml` | Enable pi-agent on boot | fnet1–fnet7 |
| `restart_pi_service` | `restart_pi_service.yml` | Restart crashed pi-agent | Per-node |
| `test_auto_restart` | `test_auto_restart.yml` | Simulate crash, verify systemd recovers | Per-node |
| `test_intercom_handshake` | `test_intercom_handshake.yml` | Orchestrator → node → reply | Per-node |
| `test_full_chain` | `test_full_chain.yml` | Verify zero non-playbook commands | all_nodes |
| `update_intercom_chain` | `update_intercom_chain.yml` | Patch chain to use intercom primary | Orchestrator |

### Execution Model

```
Orchestrator (this session)
    │ Trigger: "deploy_pi"
    ▼
Playbook-Executor
    │ Ansible playbook → node
    ▼
Lab Node (fnetN)
    │ Execute playbook tasks
    ▼
Structured JSON report
    │ {"node_id": "fnetN", "pi_version": "0.74.0", "status": "ok"}
    ▼
Orchestrator receives result
    │ Trigger: "verify_intercom"
    ▼
Lab node session replies
    │ {"intercom_ready": true, "response": "OK"}
```

**Principle:** The orchestrator never types commands. It triggers playbooks.

---

## Infrastructure Methodology

**Install → Verify → Persist** cycle, every step a playbook trigger:
1. **Installation:** Trigger `deploy_pi` → playbook-executor runs `deploy-pi.yml`.
2. **Verification:** Trigger `verify_pi` + `verify_intercom` → JSON confirms state.
3. **Persistence:** Trigger `configure_pi_service` → systemd unit deployed.
4. **Recovery:** Trigger `restart_pi_service` → playbook fixes crashed service.

---

## Test Architecture

Every test is a playbook trigger that outputs structured JSON.

| Test | Trigger | Expected Output |
|------|---------|---------------|
| Node reachable | `check_connectivity` | `{"status": "reachable"}` |
| Node.js version | `check_node_version` | `{"version": "v20+"}` |
| pi installed | `verify_pi` | `{"pi_version": "0.74.0"}` |
| Intercom loopback | `verify_intercom` | `{"intercom_ready": true}` |
| Orchestrator handshake | `test_intercom_handshake` | `{"handshake": "success"}` |
| systemd persistence | `test_auto_restart` | `{"auto_restart": true}` |
| Full chain | `test_full_chain` | `{"zero_ssh": true}` |

**Anti-hallucination:** Every check produces JSON evidence. No human interpretation of stdout.

---

## Phase Plan

### Phase 1 — Playbook Verification
**Goal:** Every node responds to playbook triggers with structured JSON.
**Location:** Playbook-executor → Lab Nodes.

#### Playbook Checklist

| # | Trigger | Playbook | Status |
|---|---------|----------|--------|
| 1 | `check_connectivity` | `check_connectivity.yml` | 📋 |
| 2 | `check_node_version` | `check_node_version.yml` | 📋 |
| 3 | `deploy_pi` | `deploy-pi.yml` | 📋 |
| 4 | `verify_pi` | `verify_pi.yml` | 📋 |
| 5 | `verify_intercom` | `verify_intercom.yml` | 📋 |
| 6 | `update_packages` | `update_packages_v1.0.yml` | 📋 |
| 7 | `test_intercom_handshake` | `test_intercom_handshake.yml` | 📋 |

#### Node Status at Start

| Node | Node.js | pi | Trigger `deploy_pi` | Trigger `verify_pi` |
|------|---------|-----|--------------------|---------------------|
| fnet1 | v20.20.2 | 0.70.2 | Needed | Needed |
| fnet2 | v20.20.2 | 0.73.1 | Needed | Needed |
| fnet3 | v20.20.2 | 0.74.0 | Not needed | Confirm |
| fnet4 | v20.20.2 | broken | Playbook fix | Confirm post-fix |
| fnet5 | v18.19.1 | broken | Playbook fix | Confirm post-fix |
| fnet6 | v20.20.2 | 0.74.0 | Not needed | Confirm |
| fnet7 | v22.22.2 | 0.74.0 | Not needed | Confirm |

**Effort:** 3–4 hours. **Risk:** Low.

### Phase 2 — Persistence & Chain Integration
**Goal:** Persistent sessions and fully operational cross-node intercom.
**Location:** Playbook-executor → Lab Nodes.

#### Playbook Checklist

| # | Trigger | Playbook | Status |
|---|---------|----------|--------|
| 8 | `configure_pi_service` | `configure-pi-service.yml` | 📋 |
| 9 | `enable_pi_service` | `enable_pi_service.yml` | 📋 |
| 10 | `test_auto_restart` | `test_auto_restart.yml` | 📋 |
| 11 | `update_intercom_chain` | `update_intercom_chain.yml` | 📋 |
| 12 | `test_full_chain` | `test_full_chain.yml` | 📋 |

**Effort:** 3–6 hours. **Risk:** Medium (systemd config).

---

## Backlog Items

| ID | Status | Phase | Trigger | Effort | Description |
|----|--------|-------|---------|--------|-------------|
| B-PI-001 | 📋 Ready | P1 | `deploy_pi` | 2h | Trigger deploy on all nodes needing upgrade |
| B-PI-002 | 📋 Ready | P1 | `verify_intercom` | 1h | Trigger handshake fnet3, fnet4 |
| B-PI-003 | 📋 Ready | P2 | `configure_pi_service` | 2h | Trigger systemd deploy + enable |
| B-PI-004 | 📋 Ready | P1 | `update_packages` | 1h | Trigger Node.js upgrade on fnet5 |
| B-PI-005 | 📋 Ready | P1 | `restart_pi_service` | 0.5h | Trigger restart on any node post-fix |
| B-PI-006 | 📋 Ready | P2 | `test_full_chain` | 1h | Trigger end-to-end chain test |

---

## Lab Node Dispatch Rules

| Node | CPU | RAM | Safe Capacity | Models | Trigger When |
|------|-----|-----|--------------|-----------------|-------------|
| fnet1 | 4c | 12GB | Low | qwen3.5:4b | `check_connectivity` → `deploy_pi` |
| fnet2 | 4c | 12GB | Low | qwen3.5:4b | `check_connectivity` → `deploy_pi` |
| fnet3 | 8c | 31GB | High | gemma4:e4b | `verify_pi` → `verify_intercom` |
| fnet4 | 8c | 31GB | High | gemma4:e4b | `check_node_version` → `deploy_pi` |
| fnet5 | 8c | 31GB | High | qwen3:8b | `update_packages` → `deploy_pi` |
| fnet6 | 8c | 31GB | High | qwen3:8b | `verify_pi` → `verify_intercom` |
| fnet7 | 4c | 12GB | Low | qwen3.5:4b | `verify_pi` → `verify_intercom` |

**Dispatch Protocol:** Orchestrator triggers playbook → playbook-executor dispatches Ansible → `pi-intercom` confirms → JSON evidence returned.

**Fallback:** If playbook trigger fails and node shows offline, trigger `restart_pi_service`. If still offline, escalate to orchestrator.

---

## Local Node Recovery

If a pi session crashes:
1. **Detector:** Health monitor detects `SESSIONS_OFFLINE` event.
2. **Action:** Trigger `restart_pi_service` → playbook-executor restarts via Ansible.
3. **Verification:** Trigger `verify_intercom` → playbook confirms node replies with JSON.
4. **Escalation:** If verification fails after 3 trigger attempts, alert orchestrator.

---

## High-Frequency Decomposition

If playbook tasks exceed 20 triggers per hour, the load balancer signal for decomposition. Every trigger must produce JSON before the next trigger fires.

---

## Node Health Report

The health report is generated by triggering `check_connectivity` + `verify_pi` + `verify_intercom` in sequence:

```json
{
  "node_id": "fnet3",
  "connectivity": "reachable",
  "pi_version": "0.74.0",
  "intercom_ready": true,
  "systemd_active": true,
  "pi_session_status": "ACTIVE"
}
```

Statuses:
- `ACTIVE`: Session running, playbook verification passed.
- `CRASHED`: Playbook `restart_pi_service` dispatched.
- `DEAD`: All triggers failed, human escalation required.

---

## Decision Log

### 2026-05-14 — Zero Direct Commands Policy
**Decision:** Every node operation is a playbook trigger. No direct commands, no typing systemctl, no manual SSH.
**Rationale:**
1. **No thinking required** — trigger → playbook → result. The orchestrator never reasons about commands.
2. **Structured output** — every trigger returns JSON, not stdout to interpret.
3. **Rollback** — Ansible `check_mode` and handlers provide automatic rollback.
4. **Consistency** — same pattern for install, verify, persist, recover.

### 2026-05-14 — Shift to Playbook-Executor Model
**Decision:** All node operations (install, verify, persist, recover) execute through `playbook-executor` playbooks.
**Rationale:** Playbook-executor provides:
1. Standardized triggers (no manual command construction)
2. Structured JSON output per node
3. Rollback capability (Ansible `check_mode` and `handlers`)
4. Consistency with existing TI-027/TI-030 playbook infrastructure
**Playbooks:** `deploy-pi.yml`, `verify-pi.yml`, `configure-pi-service.yml`, `restart_pi_service.yml`, `test_auto_restart.yml`, `test_full_chain.yml`

### 2026-05-14 — Technical Debt Discovery
**Decision:** Plan owner (kimi-k2.6) previously executed commands directly and created playbooks without framework routing.
**Rationale:** Bypassed decompose-execute-verify (TI-039) framework, ran direct SSH/Agent calls.
**Consequence:** Playbooks were created in the orchestrator session rather than being dispatched to lab nodes via framework decomposition. Orchestrator now receives outdated/imperfect playbooks that have not been validated by node-side model execution.
**Resolution:** Documented in Decision Log. Future playbook creation MUST go through:
1. Plan Owner defines trigger → 2. Orchestrator invokes `/run decomposer` → 3. Lab node model writes playbook → 4. Verifier validates on node → 5. Synthesizer reports JSON.
**Debt Items:**
- Playbooks may need node-side review for lab-node specificity
- Inventory may need correction by node-side models
- Systemd template needs validation on target OS variants
- No formal verification evidence exists for created playbooks

### 2026-05-14 — Session Naming
**Decision:** Use `fnetX-worker` naming convention.
**Rationale:** Clear mapping between hardware and agent identity.

---

## Session Notes

**Plan Owner:** High Cloud Model (ollama/kimi-k2.6)
**Orchestrator:** User session `subagent-chat-019e299a` (qwen3.5:397b-cloud)
**Plan Executor:** This session `ti041-plan-executor` (kimi-k2.6:cloud)
**Execution Model:** Trigger playbook → playbook-executor dispatches → structured JSON returned.
**Anti-Hallucination:** Playbook output JSON is the only valid evidence.
**Review required:** None — plan updated and ready for Phase 1.
**Next action:** Await orchestrator approval to begin triggering playbooks.

---

*Plan updated 2026-05-14 to zero-direct-command playbook-executor architecture. Every operation is a trigger. Previous methodology archived in `sessions/2026-05-14-plan-update.md`.*

---

## Prerequisites

Before any playbook triggers, the orchestrator requires:

1. **Ansible inventory file** at `technical-infrastructure/ansible/inventory.yml` (created by plan owner). Defines `lab_nodes` group with fnet1–fnet7 IPs.
2. **Ansible config** at `technical-infrastructure/ansible/ansible.cfg` (already exists). Points to `inventory.yml`.
3. **SSH key access** to all nodes (already configured).

```yaml
# ansible/inventory.yml excerpt
[lab_nodes]
fnet1 ansible_host=192.168.0.141 ansible_user=friasc
fnet2 ansible_host=192.168.0.142 ansible_user=friasc
fnet3 ansible_host=192.168.0.143 ansible_user=friasc
fnet4 ansible_host=192.168.0.144 ansible_user=friasc
fnet5 ansible_host=192.168.0.145 ansible_user=friasc
fnet6 ansible_host=192.168.0.146 ansible_user=friasc
fnet7 ansible_host=192.168.0.147 ansible_user=friasc
```

**Status:** ✅ Inventory file created and committed.
