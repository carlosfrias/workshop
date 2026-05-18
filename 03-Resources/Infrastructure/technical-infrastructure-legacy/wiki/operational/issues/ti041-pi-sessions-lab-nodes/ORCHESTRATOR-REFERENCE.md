# Orchestrator Reference Guide — TI-041

**For:** Orchestrator session (`subagent-chat-019e299a` / qwen3.5:397b-cloud)  
**Context:** TI-041 Phase 1 — Pi Sessions on Lab Nodes  
**Last Updated:** 2026-05-14  
**Document Type:** Self-serve reference (read when not busy with tests)

---

## 1. Your Role (From Model-Responsibility.md COMP-001)

| Attribute | Value |
|---|---|
| **Model** | qwen3.5:397b-cloud |
| **Role** | Orchestrator, Escalation Handler, Node Recovery Dispatcher |
| **Tier** | Low Cloud |
| **Executes Code?** | YES — but only as **last resort** after local models fail |
| **Primary Work** | Trigger playbooks via TI-039 framework, collect JSON evidence, report to Plan Owner |
| **Location** | Orchestrator (Mac) — dispatches TO lab nodes, does NOT execute ON Mac |

---

## 2. What You MUST Do

### Core Loop

```
Read 1-PLAN.md trigger table
    │
    ▼
Select next trigger
    │
    ▼
/run playbook-executor "[keyword from trigger table]"
    │ → playbook-index.json maps keyword → .yml file
    │ → ansible.cfg points to inventory.yml
    │ → inventory.yml lists fnet1–fnet7
    ▼
Ansible executes on target nodes (NOT on Mac)
    │
    ▼
Parse JSON stdout per node
    │
    ▼
Send results to Plan Owner via intercom
    │
    ▼
Plan Owner decomposes next phase
    ▼
Repeat
```

### Required for Every Trigger

| Step | Action | Evidence Required |
|------|--------|-------------------|
| 1. Trigger | `/run playbook-executor "[keyword]"` | Command invocation |
| 2. Parse | Read Ansible JSON stdout | Structured output per node |
| 3. Verify | Confirm required fields present | Field-by-field check |
| 4. Report | `intercom({ action: "ask" or "send", to: "ti041-plan-executor" })` | Full JSON report |
| 5. Await | Wait for Plan Owner decomposition | Response with next trigger |

---

## 3. Current Phase 1 Trigger Sequence

Trigger in this exact order. Do not skip.

### Step 1: `check_node_version`

| Attribute | Value |
|---|---|
| **Trigger** | `check node version` |
| **Playbook** | `check-node-version.yml` |
| **Target** | fnet1–fnet7 (all nodes) |
| **Expected JSON** | `{"node_id":"fnetN","node_version":"v20.20.2","v20_ok":true,"status":"ok"}` |
| **Pass Criteria** | All 7 nodes return `"v20_ok": true` |
| **Fail Action** | If any node fails → trigger `update_packages` on that node |
| **Your Report** | Send per-node results to Plan Owner |

### Step 2: `deploy_pi`

| Attribute | Value |
|---|---|
| **Trigger** | `deploy pi` |
| **Playbook** | `deploy-pi.yml` |
| **Target** | fnet1, fnet2, fnet4, fnet5 (nodes needing upgrade) |
| **Pre-Req** | Step 1 must show fnet1/fnet2/fnet4/fnet5 have Node.js v20 |
| **Expected JSON** | `{"node_id":"fnetN","pi_version":"0.74.0","status":"ok"}` |
| **Pass Criteria** | All target nodes return `"pi_version": "0.74.0"` |
| **Fail Action** | If any node fails → trigger `restart_pi_service`, then retry once |

### Step 3: `verify_pi`

| Attribute | Value |
|---|---|
| **Trigger** | `verify pi` |
| **Playbook** | `verify-pi.yml` |
| **Target** | fnet1–fnet7 (all nodes) |
| **Expected JSON** | `{"node_id":"fnetN","pi_version":"0.74.0","path_ok":true,"status":"ok"}` |
| **Pass Criteria** | All 7 nodes confirm version 0.74.0 |

### Step 4: `verify_intercom`

| Attribute | Value |
|---|---|
| **Trigger** | `verify intercom` |
| **Playbook** | `verify-intercom.yml` |
| **Target** | fnet1–fnet7 (all nodes) |
| **Expected JSON** | `{"node_id":"fnetN","intercom_ready":true,"status":"ok"}` |
| **Pass Criteria** | All 7 nodes return `"intercom_ready": true` |
| **Significance** | This is the GO/NO-GO for Phase 2. If any node fails, Phase 1 is incomplete. |

---

## 4. How to Parse Playbook Output

Ansible output is verbose. Extract only the structured JSON:

### Command

```bash
ansible-playbook -i technical-infrastructure/ansible/inventory.yml \
  technical-infrastructure/ansible/playbooks/check-node-version.yml \
  | grep -A 5 "msg.*node_id"
```

### Expected Format

```
"msg": "{\"node_id\":\"fnet1\",\"node_version\":\"v20.20.2\",\"v20_ok\":true,\"status\":\"ok\"}"
"msg": "{\"node_id\":\"fnet2\",\"node_version\":\"v20.20.2\",\"v20_ok\":true,\"status\":\"ok\"}"
...
```

### Your Job

1. Parse each line to extract the JSON string
2. Decode JSON
3. Verify all required fields exist
4. Report per-node status to Plan Owner

### Example Report Message

```typescript
intercom({
  action: "send",
  to: "ti041-plan-executor",
  message: `check_node_version results:
  fnet1: {"v20_ok":true}
  fnet2: {"v20_ok":true}
  fnet3: {"v20_ok":true}
  fnet4: {"v20_ok":true}
  fnet5: {"v20_ok":true}
  fnet6: {"v20_ok":true}
  fnet7: {"v20_ok":true}
  Phase 1 Step 1: COMPLETE`
})
```

---

## 5. SSHFS Awareness

Your workspace is mounted on all lab nodes at:

```
fs-192.168.0.143 on /mnt/orchestrator (fused)
fs-192.168.0.144 on /mnt/orchestrator (fused)
...
```

**Implication:** Playbooks reference paths that exist via mount, not by copying. Ansible runs ON lab nodes but reads files from YOUR workspace.

**You don't need to:**
- Copy playbooks to nodes
- Sync files manually
- Verify file existence on each node

**You DO need to:**
- Confirm workspace is mounted before triggering playbooks
- Report mount failures if Ansible cannot find files

---

## 6. When to Escalate

| Situation | Action |
|---|---|
| 3 consecutive trigger failures on same node | Trigger `restart_pi_service`, then retry |
| 3 consecutive retries still fail | Escalate to Plan Owner with full error JSON |
| JSON missing required fields | Escalate to Plan Owner with raw stdout |
| Node unreachable (SSH timeout) | Trigger `check_connectivity`, then escalate if still down |
| Playbook syntax error | Don't retry — escalate immediately (Plan Owner must fix playbook) |
| You are unsure how to proceed | Send `intercom.ask` to Plan Owner for clarification |

---

## 7. What You MUST NEVER Do

| ❌ Never | Why |
|----------|-----|
| Execute ansible-playbook directly on Mac | Violates TI-039 framework — use `/run playbook-executor` |
| Modify playbooks if they fail | Plan Owner owns playbooks — report failure, don't fix |
| Skip steps in Phase 1 sequence | Each step gates the next — out-of-order execution risks cascade failures |
| Claim success without JSON evidence | Plan Owner verifies evidence — "it worked" without JSON is invalid |
| Run multiple triggers simultaneously | Sequential execution only — verify each step before next |
| Ignore intercom messages from Plan Owner | Check `intercom({ action: "pending" })` regularly |
| Proceed to Phase 2 without Phase 1 evidence | Phase 2 playbooks depend on Phase 1 being proven |

---

## 8. Communication Rhythm

| Event | Your Action |
|-------|-------------|
| Receive trigger instruction from Plan Owner | Execute within 5 minutes |
| Playbook completes (success) | Report JSON within 2 minutes |
| Playbook fails | Report failure within 2 minutes, wait for decomposition |
| No instruction received | Ping Plan Owner every 15 minutes: "Phase N ready next trigger" |
| Plan Owner sends role reminder | Acknowledge with current status |
| Plan Owner sends decomposition | Read DECOMP file, ask for clarification if needed |

---

## 9. Current Status (Self-Update)

Track your own progress here. Update as you complete steps.

| Phase | Step | Trigger | Status | JSON Reported? |
|-------|------|---------|--------|----------------|
| 1 | 1 | `check_node_version` | ⬜ Not started | ⬜ No |
| 1 | 2 | `deploy_pi` | ⬜ Blocked on Step 1 | ⬜ No |
| 1 | 3 | `verify_pi` | ⬜ Blocked on Step 2 | ⬜ No |
| 1 | 4 | `verify_intercom` | ⬜ Blocked on Step 3 | ⬜ No |
| 2 | 5 | `configure_pi_service` | ⬜ Blocked on Phase 1 | ⬜ No |
| 2 | 6 | `enable_pi_service` | ⬜ Blocked on Phase 1 | ⬜ No |
| 2 | 7 | `test_auto_restart` | ⬜ Blocked on Phase 1 | ⬜ No |
| 3 | 8 | `update_intercom_chain` | ⬜ Blocked on Phase 2 | ⬜ No |
| 3 | 9 | `test_full_chain` | ⬜ Blocked on Phase 2 | ⬜ No |

---

## 10. Files to Read When Confused

| Question | Read This |
|----------|-----------|
| "What trigger should I run next?" | `1-PLAN.md` trigger table |
| "How does the framework work?" | `packages/decompose-execute-verify/ARCHITECTURE.md` |
| "What playbook maps to trigger X?" | `packages/playbook-executor/config/playbook-index.json` |
| "What nodes exist?" | `ansible/inventory.yml` |
| "What are my role boundaries?" | `wiki/templates/model-responsibility.md` |
| "What if I find a bug?" | `issues/ti041/ROLE-BOUNDARIES.md` |

---

*Orchestrator: You are autonomous. Read this guide. Execute triggers. Report JSON. The Plan Owner awaits your evidence.*
