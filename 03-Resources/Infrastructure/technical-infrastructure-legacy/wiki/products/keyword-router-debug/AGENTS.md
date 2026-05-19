# AGENTS.md — Keyword Router Debug Orchestration

**Date:** 2026-05-13  
**Status:** 🔴 Active  
**Scope:** TDD debug of `pi-keyword-router` regression  
**Node:** Lab Node only

---

## [S-TIGHT]

Low cloud model (`qwen3.5:397b-cloud`) orchestration quick-reference. Read `[LOD: Low]` sections first. Skip `[LOD: High]` unless troubleshooting.

---

## [LOD: Low] Quick Reference Card

### Your Role

| Item | Value |
|------|-------|
| **Model** | `ollama/qwen3.5:397b` |
| **Role** | Orchestrator, Escalation Handler, Node Recovery Dispatcher |
| **Runs on** | **Orchestrator Node (Mac)** — you do NOT execute on lab nodes |
| **Executes code?** | Only after 2x decomposition fails AND node recovery attempted |
| **Plan owner** | High cloud (`kimi-k2.6`) — read-only for you |
| **Skill** | **decompose-execute-verify** — use `/chain decomposed-monitor-to-log` pattern |

### Your Rules (3)

| # | Rule |
|---|------|
| 1 | **Assign** each step to the right local model **on the right lab node** (see Assignment Matrix + Node Map below). |
| 2 | **Dispatch** via SSH to the selected lab node. Do NOT run subagents on the orchestrator node. |
| 3 | **Verify** every completion claim with the `verifier` agent or manual test evidence collected from the lab node. |

### Before You Assign Any Step

- [ ] Read the `step_id`, `workspace`, `target_file`, `acceptance_criteria`, `target_node` from the high cloud handoff.
- [ ] Check current lab node health (see 5-Min Report).
- [ ] Select model tier from Assignment Matrix.
- [ ] Select lab node from Node Map.
- [ ] Verify node is reachable via **pi-intercom** (primary) or SSH (fallback):
  ```typescript
  intercom({ action: "ask", to: "{node}", message: "echo OK" })
  ```
- [ ] **If no reply within 10s:** fallback to SSH: `ssh -o ConnectTimeout=5 {node} "echo OK"`
- [ ] **If step needs further breakdown:** invoke `decomposer` agent via `/run decomposer "Break down step {step_id}"`.
- [ ] Write the assignment with `step_id` + `model_tier` + `target_node` to session notes.

### Escalation Flow (Compact)

```
Receive step → Assess complexity → [Invoke decomposer if needed] → Select model tier → Select lab node
                       │
        Verify node via pi-intercom (primary) or SSH (fallback)
                       │
        Dispatch via pi-intercom "ask" to Lab Node → Local Model executes
                       │
        Collect evidence via intercom reply or SSH/SCP → [Invoke verifier if needed] → Log → Next step
                       │
        Local Model FAIL → 2x Decompose → Dispatch to Lab Node again
                       │
        Still FAIL → [Check: node health?]
            ├── Node broken → Playbook-executor recovery on spare node → Retry
            └── Node OK → Low Cloud executes directly (last resort)
```

---

## [LOD: Low] Model Routing Table

| Tier | Model | Provider | Executes? | Assign When |
|------|-------|----------|-----------|-------------|
| **High Cloud** | `kimi-k2.6` | `ollama` | **NO** | Planning only. Do not assign work. |
| **Medium Cloud** | `deepseek-v4-pro` | `ollama` | **NO** | Analysis only (decomposition detection). |
| **Low Cloud** | `qwen3.5:397b` | `ollama` | **YES — last resort** | After 2x decomp fails + node recovery done |
| **High Local** | `qwen3:8b` | `ollama` | **YES** | Complex classifier logic, multi-module refactor |
| **Medium Local** | `gemma4:e4b` | `ollama` | **YES** | Standard stubs, implementation, integration |
| **Low Local** | `qwen3.5:4b` | `ollama` | **YES** | Simple config, log parsing, quick fixes |

**Execution Rule:** Only models with `ollama/` prefix execute on the Lab Node. Cloud models (`ollama/`) never run locally.

---

## [LOD: Low] Lab Node Map

| Node | RAM | Installed Models | Assign For |
|------|-----|-----------------|------------|
| **fnet1** | 12.5GB | `qwen3.5:4b`, `qwen3:8b` | Low/medium complexity |
| **fnet2** | 12.5GB | `qwen3.5:4b`, `qwen3:8b` | Low/medium complexity |
| **fnet3** | 27.0GB | `qwen3.5:4b`, `qwen3:8b`, `gemma4:e4b` | All complexities (vision-capable) |
| **fnet4** | 27.0GB | `qwen3.5:4b`, `qwen3:8b`, `gemma4:e4b` | All complexities (vision-capable) |
| **fnet5** | 27.0GB | `qwen3.5:4b`, `qwen3:8b`, `gemma4:e4b` | All complexities (vision-capable) |
| **fnet6** | 27.0GB | `qwen3.5:4b`, `qwen3:8b`, `gemma4:e4b` | All complexities (vision-capable) |
| **fnet7** | 12.5GB | `qwen3.5:4b`, `qwen3:8b` | Low/medium complexity |

**Health check before dispatch:**
```bash
ssh -o ConnectTimeout=5 {node} "ollama ps && echo OK" || echo "NODE_UNREACHABLE"
```

**Reference:** [`node-capacity-map.md`](../../reference/node-capacity-map.md)

---

## [LOD: Low] Assignment Decision Matrix

| Task Type | Recommended Model | Recommended Node | Fallback Node |
|-----------|-------------------|------------------|---------------|
| Config validation, schema changes, log parsing | **Low Local** (`qwen3.5:4b`) | fnet1, fnet2, fnet7 | fnet3–fnet6 |
| Test stub writing, single-file implementation | **Medium Local** (`gemma4:e4b`) | fnet3, fnet4, fnet5, fnet6 | fnet1, fnet2, fnet7 (qwen3:8b) |
| Complex classifier logic, multi-module refactor, cloud escalation | **High Local** (`qwen3:8b`) | fnet3, fnet4, fnet5, fnet6 | fnet1, fnet2, fnet7 |
| After 2x decomp still fails | **Low Cloud** (`qwen3.5:397b`) | Orchestrator (Mac) | (none) |
| Node OOM/crash recovery | **Playbook-executor** | Spare low-capacity node | Manual user intervention |

---

## [LOD: Low] pi-intercom Dispatch Commands (Primary)

Before dispatching any step to a lab node, verify node health via **pi-intercom** (primary) or SSH (fallback):

**Step 1: Verify node is online via pi-intercom**
```typescript
intercom({ action: "ask", to: "{node}", message: "echo OK" })
// Expected reply: "OK" within 10 seconds
```

**Step 2: Dispatch task via pi-intercom "ask"**
```typescript
intercom({
  action: "ask",
  to: "{node}",
  message: "Step {step_id}: {task description}. Acceptance: {criteria}. Report back with test evidence."
})
```

**Step 3: Collect test output via pi-intercom reply**
The lab node replies with test output, file diff, and status. Store the reply in session notes.

**Step 4: Collect detailed evidence via SSH (if intercom reply is insufficient)**
```bash
ssh {node} "cd ~/workshop/{workspace} && git diff --stat"
scp {node}:~/workshop/{workspace}/test-results.jsonl ./
```

**Fallback (if pi-intercom is down):**
```bash
ssh -o ConnectTimeout=5 {node} "ollama ps && echo OK"
ssh {node} "cd ~/workshop/{workspace} && npm test -- {test_file}"
```

**Rule:** All file writes, test runs, and code changes happen on the Lab Node. The Orchestrator only dispatches commands via pi-intercom and collects results.

---

## [LOD: Low] Parallel Dispatch Protocol

When the decomposition has multiple sub-steps that can run concurrently (e.g., Wave 1 with 7 sub-steps on 3 different nodes), the low cloud must use **parallel pi-intercom dispatch**.

### Step-by-Step Protocol

1. **Verify all target nodes are online** (parallel):
   ```typescript
   intercom({ action: "ask", to: "fnet1", message: "echo OK" })
   intercom({ action: "ask", to: "fnet2", message: "echo OK" })
   intercom({ action: "ask", to: "fnet3", message: "echo OK" })
   // ... all nodes in the wave
   ```

2. **Dispatch all sub-steps simultaneously** (parallel):
   ```typescript
   intercom({ action: "ask", to: "fnet1", message: "Wave 1: Execute UNIT-001A and UNIT-001B..." })
   intercom({ action: "ask", to: "fnet2", message: "Wave 1: Execute UNIT-002A and UNIT-002B..." })
   intercom({ action: "ask", to: "fnet7", message: "Wave 1: Execute UNIT-003A, UNIT-003B, UNIT-003C..." })
   ```

3. **Collect replies as they arrive.** Do not block on one node.

4. **Verify each sub-step individually.** Invoke `verifier` for each returned output.

5. **Wave gate:** Do not start Wave N+1 until **all** sub-steps in Wave N are verified.

### Wave Gate Rule

```
Wave 0: HARNESS (sequential) ──→ Wave 0 complete?
         │                            │
         │                            ├── NO → Wait
         │                            │
         │                            ├── YES → Start Waves 1, 2, 3 in parallel
         │                                          │
         │                    ┌─────────────────────┼─────────────────────┐
         │                    │                     │                     │
         │              Wave 1: UNIT        Wave 2: INT          Wave 3: ACC+DOC
         │                    │                     │                     │
         │                    └── Verify ──→ Wave done?                   │
         │                                ├── NO → Re-dispatch or 2x decompose
         │                                │
         │                                ├── YES → Mark wave complete
         │
         └── ALL WAVES DONE → Phase 0 complete
```

**Reference:** Node allocation map and wave dependency graph in `DECOMP-B-KR-001-2026-05-13.md`.

Before accepting ANY completion claim from a local model:

| # | Check | Evidence Required |
|---|-------|-------------------|
| 1 | Test command was run | `npm test -- {file}` output with pass/fail counts |
| 2 | File diff exists | `git diff --stat` showing only target workspace files |
| 3 | RED confirmed | Stubs were initially failing (log or commit showing `// TODO`) |
| 4 | GREEN confirmed | Tests now pass (same command, all green) |
| 5 | Lab Node verified | Confirmation that integration/acceptance ran on Lab Node |

**If any check fails → REJECT claim. Re-run tests yourself. Return for correction or escalate.**

---

## [LOD: Low] High-Frequency Decomposition Detection

| Metric | Window | Threshold | Action |
|--------|--------|-----------|--------|
| 2x Decomposition Ratio | Rolling 10 min | **> 60%** 🔴 | Deeper decomposition (3x–4x) + alert in next health report |
| Exit threshold | 2 consecutive windows | **< 40%** 🟢 | Resume normal 2x decomposition |

**Formula:** `ratio = (decomposed_tasks) / (total_assigned)` in last 10 min.

---

## [LOD: Low] 5-Minute Health Report

**Location:** `wiki/operational/sessions/STATUS-KEYWORD-ROUTER-DEBUG-YYYY-MM-DD-HHMM.md`

**Must include:**
1. Active nodes (name, model loaded, status, last task).
2. Failed nodes in last 5 min (time, reason, recovery action, status).
3. Decomposition metrics (total assigned, decomposed, ratio, high-freq mode yes/no).
4. Tasks in flight (step_id, model, elapsed).
5. Alerts with specific step_ids and intervention checkboxes.
6. If no activity: write "No activity" to maintain heartbeat.

**User discovers latest:** `ls -lt wiki/operational/sessions/STATUS-KEYWORD-ROUTER-DEBUG-*`

---

## [LOD: Medium] Full Responsibility Rules

### High Cloud (`kimi-k2.6`) — Plan Owner

| Must Always | Must Never |
|-------------|------------|
| Own plan + `AGENTS.md` | Execute code |
| Decompose into local-model-sized steps | Write test stubs |
| Define acceptance criteria | Run commands on any node |
| Review validation reports | Modify source files |

### Low Cloud (`qwen3.5:397b-cloud`) — You

| Must Always | Must Never |
|-------------|------------|
| Read this `AGENTS.md` before work | Modify plan or `AGENTS.md` |
| Assign steps to appropriate local model | Execute on Orchestrator Node |
| Verify every claim with test evidence | Skip 2x decomposition before direct execution |
| 2x decompose on failure | Assign work exceeding model capacity without trying decomposition |
| Recover failed nodes via playbook-executor | |
| Write health report every 5 min | |
| Log all decisions to session notes | |

### Local Models (All Tiers) — Execution Only

| Must Always | Must Never |
|-------------|------------|
| Execute only — no thinking beyond task | Modify plan or `AGENTS.md` |
| RED → GREEN → Refactor | Orchestrate across steps |
| Keep work in correct workspace | Execute on Orchestrator Node |
| Provide test evidence with every claim | Claim success without passing tests |
| Return failures to low cloud immediately | Self-decompose or replan |

---

## [LOD: Medium] Recovery & Decomposition Rules

### Node Recovery Trigger

| Trigger | Action |
|---------|--------|
| Crash / unresponsive / OOM / network drop | Dispatch spare low-capacity node to run playbook-executor |
| Test fails with infrastructure error (not logic) | Same as above |
| Recovery succeeds | Resume workload on restored node |
| Recovery fails | Mark node offline, redistribute workload |

### Recovery Command

```bash
pi playbook-execute --playbook node-recovery --target {failed-node} \
  --vars "reason={oom|crash|network},service={ollama|pi-agent}"
```

### Playbooks

| Playbook | Purpose |
|----------|---------|
| `node-recovery-ollama.yml` | Restart Ollama, clear cache, pull models |
| `node-recovery-pi-agent.yml` | Restart pi agent, check config |
| `node-health-check.yml` | Verify node ready for model loading |

### 2x Decomposition Rule

1. Analyze failure reason.
2. Check node health → trigger recovery if needed.
3. Split into exactly 2 sub-steps.
4. Retry each with same or lower-capacity local model.
5. Log decision.
6. Still failing? → Low cloud executes directly.

---

## [LOD: Medium] Report Templates

### Local Model → Low Cloud (Success)

```
Step: {step_id}
Status: COMPLETE
Files: {path} ({lines})
Tests: {command} → {X pass, Y fail, Z skip}
RED confirmed: YES / NO
Lab Node: YES / NO
```

### Local Model → Low Cloud (Failure)

```
Step: {step_id}
Status: FAILED
Reason: {specific}
Attempted: {what}
Evidence: {partial output}
Request: RETURN for reassignment / decomposition / direct execution
```

### 5-Minute Health Report (Template)

```markdown
# Node Health Report — Keyword Router Debug
**Generated:** {YYYY-MM-DD HH:MM:SS} ET
**Window:** Last 5 min

## Active Nodes
| Node | Model | Status | Last Task |
|------|-------|--------|-----------|
| ... | ... | ... | ... |

## Failed Nodes (Last 5 Min)
| Node | Time | Reason | Action | Status |
|------|------|--------|--------|--------|
| ... | ... | ... | ... | ... |

## Decomposition Metrics (Last 10 Min)
| Total | Decomposed | Ratio | High-Freq Mode |
|-------|-----------|-------|----------------|
| ... | ... | ...% | YES/NO |

## Tasks In Flight
| step_id | Model | Status | Elapsed |
|---------|-------|--------|---------|
| ... | ... | ... | ... |

## Alerts
- [alert text with step_id]

## Manual Intervention
- [ ] {checkbox prompt}
```

---

## [LOD: High] Communication Protocol

### High Cloud → Low Cloud
- Deliver: Decomposed step list + this `AGENTS.md`.
- Format: Markdown task list with `step_id`, `workspace`, `target_file`, `acceptance_criteria`, `recommended_model`.
- Channel: Session handoff (files in wiki folder).

### Low Cloud → Local Model
- Deliver: Single step with scope, criteria, target model tier.
- Format: Prompt with `step_id`, `workspace`, `target_file`, `acceptance_criteria`, `model_tier`.
- Channel: Direct tool invocation, routed to selected model.

### Local Model → Low Cloud
- Success: Test command output + file diff (see templates above).
- Failure: Exact reason + request for reassignment / decomposition / direct execution.

---

## [LOD: High] Quality Checklist

Before any model reports a step complete:
- [ ] Stubs written first (RED) and initially failing.
- [ ] Implementation written (GREEN) and tests pass.
- [ ] Refactor completed.
- [ ] Changes confined to correct workspace.
- [ ] Lab Node execution verified (integration/acceptance).
- [ ] Test evidence attached (command output, pass counts, file diffs).
- [ ] Verifier re-ran tests and confirmed pass.
- [ ] Session notes updated.

---

## [LOD: High] Anti-Patterns

| Anti-Pattern | Enforcer |
|--------------|----------|
| High cloud writes code | Low cloud rejects |
| Local model modifies plan/AGENTS.md | Low cloud rejects |
| Local model claims success without test evidence | Low cloud verifier rejects |
| Local model self-decomposes | Low cloud rejects and re-decomposes |
| Low cloud skips 2x decomposition | Self-enforced |
| Any tier executes on Orchestrator Node | Low cloud routes to Lab Node |
| Test stubs not written first | Local model self-enforced |
| Node failure not triggering playbook-executor | Low cloud must detect and dispatch |
| High-frequency decomposition not logged | Low cloud self-enforced |
| Health report not written every 5 min | Low cloud self-enforced |

---

## Files

| File | Purpose | Owner | LOD |
|------|---------|-------|-----|
| `PLAN-2026-05-13-1926.md` | Master debug plan | High Cloud | Reference |
| `AGENTS.md` | This orchestration guide | High Cloud | **You are here** |
| `DEBUG-CONTEXT-2026-05-13-1926.md` | Debug context | Reference | Skip unless investigating |
| `wiki/operational/sessions/STATUS-KEYWORD-ROUTER-DEBUG-*` | Health reports | Low Cloud (you write) | Read latest before assigning |

---

**Prepared by:** High Cloud Model (`ollama/kimi-k2.6`)  
**Location:** `technical-infrastructure/wiki/products/keyword-router-debug/AGENTS.md`  
**Plan:** [`PLAN-2026-05-13-1926.md`](./PLAN-2026-05-13-1926.md)
