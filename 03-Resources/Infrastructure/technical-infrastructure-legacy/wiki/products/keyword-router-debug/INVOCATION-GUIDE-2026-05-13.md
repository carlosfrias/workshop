# Invocation Guide — Multi-Tier Debug Execution

**Date:** 2026-05-13  
**Status:** 🔴 Active  
**Scope:** How to kick off and operate the keyword-router debug with correct tier separation  
**Skill:** `decompose-execute-verify` — provides decomposer agent, verifier agent, and pre-built chains  
**Prerequisite:** `pi-keyword-router` is OFF. Keyword routing is disabled. All routing is manual via `/router` commands.

---

## [S-TIGHT]

Step-by-step instructions for invoking each model tier in the keyword-router debug project using the decompose-execute-verify skill. The orchestrator dispatches all execution to lab nodes via SSH. Cloud models handle decomposition and verification only.

---

## Quick Reference: Tier → Command Mapping

| Tier | Role | Model | How to Invoke | Node |
|------|------|-------|-------------|------|
| **High Cloud** | Plan, decompose, update plan | `kimi-k2.6:cloud` | `/router profile cloud` then `/router tier high` | Orchestrator (Mac) |
| **Medium Cloud** | Decomposition detection, analysis | `deepseek-v4-pro:cloud` | `/router profile cloud` then `/router tier medium` | Orchestrator (Mac) |
| **Low Cloud** | Orchestrate, dispatch, verify | `qwen3.5:397b-cloud` | `/router profile auto` then `/router tier medium` | Orchestrator (Mac) |
| **Decomposer** | Fine-grained step breakdown | `qwen3.5:cloud` | `/run decomposer "Break down step X for {model} on {node}"` | Orchestrator (Mac) |
| **Verifier** | Output validation | `qwen3.5:cloud` | `/run verifier "Validate output from step X against criteria"` | Orchestrator (Mac) |
| **High Local** | Complex execution | `qwen3:8b` | SSH dispatch to lab node | fnet3–fnet6 |
| **Medium Local** | Standard execution | `gemma4:e4b` | SSH dispatch to lab node | fnet3–fnet6 |
| **Low Local** | Simple execution | `qwen3.5:4b` | SSH dispatch to lab node | fnet1, fnet2, fnet7 |

---

## How to Kick Off the Debug Session

### Step 1: Start the Orchestrator (Low Cloud)

The **low cloud model** is the entry point. It reads the decomposition, reads `AGENTS.md`, and begins dispatching steps.

**Command sequence:**
```bash
# In your pi session
/router profile auto          # Selects the auto profile
/router tier medium           # Routes to qwen3.5:397b-cloud (low cloud orchestrator)
```

**Then prompt the low cloud model:**
```
You are the low cloud orchestrator for the keyword-router debug project.

Read the updated decomposition file at:
technical-infrastructure/wiki/products/keyword-router-debug/DECOMP-B-KR-001-2026-05-13.md

Read the orchestration guide at:
technical-infrastructure/wiki/products/keyword-router-debug/AGENTS.md

Read the invocation guide at:
technical-infrastructure/wiki/products/keyword-router-debug/INVOCATION-GUIDE-2026-05-13.md

Use the decompose-execute-verify skill for any step breakdowns (/run decomposer) and output validation (/run verifier).

PRIMARY DISPATCH MECHANISM: pi-intercom (all nodes run pi-intercom already).
FALLBACK: SSH if intercom does not respond within 10 seconds.

This is a multi-node parallel decomposition with 20 sub-steps across 4 waves:
- Wave 0: Harness scaffold (sequential on fnet3)
- Wave 1: 7 unit test stubs (parallel on fnet1, fnet2, fnet7)
- Wave 2: 4 integration test stubs (parallel on fnet3, fnet4)
- Wave 3: 5 acceptance + doc stubs (parallel on fnet5, fnet6)

Execute the following:

1. Wave 0 -- Dispatch to fnet3 via pi-intercom:
   intercom({
     action: "ask",
     to: "fnet3",
     message: "Execute Wave 0: HARNESS-001, HARNESS-002, HARNESS-003 in sequence. Create test directories, test runner config, and wire package.json. Verify npm test runs. Report test output + git diff."
   })

2. Wait for wave 0 reply. Verify harness is runnable.

3. Waves 1, 2, 3 -- Dispatch in parallel via pi-intercom to all nodes:
   intercom({ action: "ask", to: "fnet1", message: "Wave 1: Execute UNIT-001A and UNIT-001B..." })
   intercom({ action: "ask", to: "fnet2", message: "Wave 1: Execute UNIT-002A and UNIT-002B..." })
   intercom({ action: "ask", to: "fnet7", message: "Wave 1: Execute UNIT-003A, UNIT-003B, UNIT-003C..." })
   intercom({ action: "ask", to: "fnet3", message: "Wave 2: Execute INT-001A and INT-001B..." })
   intercom({ action: "ask", to: "fnet4", message: "Wave 2: Execute INT-002A and INT-002B..." })
   intercom({ action: "ask", to: "fnet5", message: "Wave 3: Execute ACC-001A, ACC-001B, ACC-001C..." })
   intercom({ action: "ask", to: "fnet6", message: "Wave 3: Execute DOC-001A and DOC-001B..." })

4. Collect all replies. Invoke verifier for each output. Wave gate: all must pass before declaring Phase 0 complete.

Report back with session notes including all step_ids, nodes used, test evidence, and results.
```

**What happens next:**
1. Low cloud reads the decomposition and AGENTS.md.
2. Low cloud executes Wave 0 on fnet3 (harness scaffold).
3. Low cloud dispatches Waves 1, 2, 3 in parallel across fnet1–fnet7.
4. Low cloud collects all replies as they arrive.
5. Low cloud invokes verifier for each sub-step.
6. Low cloud reports Phase 0 complete when all waves pass.

---

### Step 2: How the Low Cloud Dispatches to Lab Nodes

The low cloud model runs on the **Orchestrator Node (Mac)**. It does **not** execute code itself. Instead, it:

1. **Selects the target lab node** based on the assigned model tier and current node health.
2. **Dispatches the task via `pi-intercom`** to the selected lab node's named session.
3. **Monitors execution** by waiting for the intercom reply with test output.
4. **Collects test evidence** from the intercom reply before accepting completion.

**Typical dispatch flow (pi-intercom — primary):**
```
Low Cloud (on Mac): "Step B-KR-001-UNIT-001 is a config schema test.
Assigning to Low Local on fnet1.
Dispatching via pi-intercom..."

Low Cloud executes:
intercom({
  action: "ask",
  to: "fnet1",
  message: "Step B-KR-001-UNIT-001: Write failing test stub for kill-switch config schema. Target: test/unit/kill-switch.test.ts. Acceptance: assert loadConfig() reads extensions.pi-keyword-router.enabled. Report test output + git diff."
})

Low Cloud receives reply from fnet1:
"Test output: 1 test, 1 fail. Expected: enabled field missing. git diff: 2 files changed..."
```

**Fallback (SSH — if pi-intercom is not responding):**
```bash
ssh -o ConnectTimeout=5 fnet1 "echo OK"
ssh fnet1 "cd ~/workshop/technical-infrastructure/packages/pi-keyword-router \&\& npm test -- test/unit/kill-switch.test.ts"
ssh fnet1 "cd ~/workshop/technical-infrastructure/packages/pi-keyword-router \&\& git diff --stat"
```

**Using decomposer for fine-grained breakdown:**
If a step is too complex for the assigned tier, the low cloud invokes the decomposer agent:
```bash
/run decomposer "Break down B-KR-001-INT-001 for qwen3.5:4b execution on fnet1"
```
The decomposer returns a finer-grained plan. The low cloud then dispatches each sub-task to the lab node.

**Using verifier for output validation:**
After the lab node reports completion, the low cloud invokes the verifier:
```bash
/run verifier "Validate test output from B-KR-001-UNIT-001 against:
- Test stubs were initially failing
- Implementation makes them pass
- git diff shows only target workspace files"
```

---

### Step 2b: How to Invoke Phase 1 (GREEN — Implementation)

After Phase 0 (RED) is complete and all test stubs are confirmed failing, invoke Phase 1 to write the implementation code that makes them pass.

**Command sequence:**
```bash
# In your pi session (same session as Phase 0)
/router profile auto
/router tier medium
```

**Copy-paste this prompt:**
```
You are the low cloud orchestrator for the keyword-router debug project.

Phase 0 is COMPLETE. All 20 test stubs are confirmed RED (failing).

Now execute Phase 1 (GREEN — implementation).

Read the Phase 1 decomposition file at:
technical-infrastructure/wiki/products/keyword-router-debug/DECOMP-B-KR-001-PHASE1-2026-05-13.md

Read the orchestration guide at:
technical-infrastructure/wiki/products/keyword-router-debug/AGENTS.md

Use the decompose-execute-verify skill for any step breakdowns (/run decomposer) and output validation (/run verifier).

PRIMARY DISPATCH MECHANISM: pi-intercom.
FALLBACK: SSH if intercom does not respond within 10 seconds.

Phase 1 has 14 implementation sub-steps across 4 waves:
- Wave 0: Config schema (sequential on fnet3) — PREREQUISITE for all other waves
- Wave 1: Core logic (parallel on fnet1, fnet2, fnet7, fnet3, fnet4)
- Wave 2: Persistence + documentation (parallel on fnet5, fnet6)
- Wave 3: System verification (sequential on fnet3)

WAVE GATE RULE: Do NOT start Wave N+1 until ALL sub-steps in Wave N are verified GREEN.

Execute:

1. Wave 0 — Dispatch to fnet3:
   intercom({
     action: "ask",
     to: "fnet3",
     message: "Phase 1 Wave 0: Execute IMPL-CONFIG-001, IMPL-CONFIG-002, IMPL-HARNESS-001 in sequence. Add enabled field to config schema with default true. Verify npm test compiles. Report test output + git diff."
   })

2. Wait for Wave 0 reply. Verify all config tests pass.

3. Wave 1 — Dispatch in parallel:
   intercom({ action: "ask", to: "fnet1", message: "Phase 1 Wave 1: Execute IMPL-GATE-001. Implement shouldRegisterHooks(). Report test output + git diff." })
   intercom({ action: "ask", to: "fnet2", message: "Phase 1 Wave 1: Execute IMPL-INDEX-001. Wire gatekeeper into index.ts. Report test output + git diff." })
   intercom({ action: "ask", to: "fnet7", message: "Phase 1 Wave 1: Execute IMPL-FOOTER-001. Add disabled state to footer. Report test output + git diff." })
   intercom({ action: "ask", to: "fnet3", message: "Phase 1 Wave 1: Execute IMPL-EVENT-001. Suppress keyword-router:routed when disabled. Report test output + git diff." })
   intercom({ action: "ask", to: "fnet4", message: "Phase 1 Wave 1: Execute IMPL-FALLBACK-001. Route to fallback when disabled. Report test output + git diff." })

4. Wait for all Wave 1 replies. Verify all core logic tests pass.

5. Wave 2 — Dispatch in parallel:
   intercom({ action: "ask", to: "fnet5", message: "Phase 1 Wave 2: Execute IMPL-PERSIST-001 and IMPL-PERSIST-002 in sequence. Implement session persistence. Report test output + git diff." })
   intercom({ action: "ask", to: "fnet6", message: "Phase 1 Wave 2: Execute IMPL-DOC-001. Populate kill-switch documentation. Report file contents + git diff." })

6. Wait for all Wave 2 replies. Verify persistence and documentation tests pass.

7. Wave 3 — Dispatch to fnet3:
   intercom({
     action: "ask",
     to: "fnet3",
     message: "Phase 1 Wave 3: Execute IMPL-SYS-001, IMPL-SYS-002, IMPL-SYS-003 in sequence. Run full test suite with enabled=true and enabled=false. Write completion report. Report all test outputs + git diff + session report."
   })

8. Verify ALL 20 original Phase 0 tests now pass (GREEN).

Report back with session notes including all step_ids, nodes used, test evidence, and Phase 1 completion status.
```

**What happens next:**
1. Low cloud reads the Phase 1 decomposition.
2. Low cloud executes Wave 0 on fnet3 (config schema).
3. Low cloud dispatches Waves 1, 2 in parallel across fnet1–fnet7.
4. Low cloud collects all replies and verifies each wave.
5. Low cloud runs Wave 3 system verification on fnet3.
6. Low cloud confirms all 20 Phase 0 tests now pass (GREEN).
7. Low cloud writes Phase 1 completion report.

---

### Step 2c: Option A — Start B-KR-002 (Lab Node Bisection)

After B-KR-001 is complete, start B-KR-002 to identify the exact regression commit where keyword-router stopped escalating to higher-capacity models.

**Command sequence:**
```bash
# In your pi session (same session as Phase 1)
/router profile auto
/router tier medium
```

**Copy-paste this prompt:**
```
You are the low cloud orchestrator for the keyword-router debug project.

B-KR-001 is COMPLETE. Now execute B-KR-002: Lab Node Bisection — Identify Regression Commit.

Read the B-KR-002 decomposition file at:
technical-infrastructure/wiki/products/keyword-router-debug/DECOMP-B-KR-002-2026-05-13.md

Read the orchestration guide at:
technical-infrastructure/wiki/products/keyword-router-debug/AGENTS.md

Use the decompose-execute-verify skill for any step breakdowns (/run decomposer) and output validation (/run verifier).

PRIMARY DISPATCH MECHANISM: pi-intercom.
FALLBACK: SSH if intercom does not respond within 10 seconds.

B-KR-002 has 10 sub-steps across 3 waves:
- Wave 0: Baseline + commit range (sequential on fnet3)
- Wave 1: Parallel bisection probes (parallel across fnet1–fnet7)
- Wave 2: Root cause analysis + documentation (sequential on fnet3)

WAVE GATE RULE: Do NOT start Wave N+1 until ALL sub-steps in Wave N are verified.

Execute:

1. Wave 0 — Dispatch to fnet3:
   intercom({
     action: "ask",
     to: "fnet3",
     message: "B-KR-002 Wave 0: Execute BASE-001, BASE-002, BASE-003 in sequence. Find known-good commit, list regression-range commits, define regression test criteria. Save commit list and test script. Report findings."
   })

2. Wait for Wave 0 reply. Verify commit range and regression test are ready.

3. Wave 1 — Read the commit list from fnet3, then dispatch in parallel:
   intercom({ action: "ask", to: "fnet1", message: "B-KR-002 Wave 1: Checkout commit <hash-1>, run regression test, report GOOD or BAD." })
   intercom({ action: "ask", to: "fnet2", message: "B-KR-002 Wave 1: Checkout commit <hash-2>, run regression test, report GOOD or BAD." })
   intercom({ action: "ask", to: "fnet3", message: "B-KR-002 Wave 1: Checkout commit <hash-3>, run regression test, report GOOD or BAD." })
   intercom({ action: "ask", to: "fnet4", message: "B-KR-002 Wave 1: Checkout commit <hash-4>, run regression test, report GOOD or BAD." })
   intercom({ action: "ask", to: "fnet5", message: "B-KR-002 Wave 1: Checkout commit <hash-5>, run regression test, report GOOD or BAD." })
   intercom({ action: "ask", to: "fnet6", message: "B-KR-002 Wave 1: Checkout commit <hash-6>, run regression test, report GOOD or BAD." })
   intercom({ action: "ask", to: "fnet7", message: "B-KR-002 Wave 1: Checkout commit <hash-7>, run regression test, report GOOD or BAD." })

4. Collect all replies. Use GOOD/BAD results to narrow the bisection range.

5. Wave 1 continued — Dispatch additional batches as needed until the regression commit is isolated:
   intercom({ action: "ask", to: "<node>", message: "B-KR-002 Wave 1 Batch 2: Checkout commit <hash>, run regression test, report GOOD or BAD." })

6. Once exact regression commit is identified, proceed to Wave 2 — Dispatch to fnet3:
   intercom({
     action: "ask",
     to: "fnet3",
     message: "B-KR-002 Wave 2: Execute ROOT-001, ROOT-002, ROOT-003 in sequence. Analyze regression commit diff, pinpoint exact function/line change, and write ROOT-CAUSE document. Report diff summary + root cause + document path."
   })

7. Verify ROOT-CAUSE document exists and is complete.

Report back with session notes including: exact regression commit hash, what changed, why it caused the regression, and document path.
```

**What happens next:**
1. Low cloud reads the B-KR-002 decomposition.
2. Low cloud executes Wave 0 on fnet3 (find baseline, list commits, define test).
3. Low cloud dispatches Wave 1 bisection probes across fnet1–fnet7 in parallel.
4. Low cloud narrows the range across 1–3 batches.
5. Low cloud isolates the exact regression commit.
6. Low cloud executes Wave 2 on fnet3 (diff analysis + root cause document).
7. Low cloud reports B-KR-002 complete with regression commit identified.

---

### Step 3: How to Invoke the Medium Cloud (Decomposition Detection)

The medium cloud (`deepseek-v4-pro:cloud`) monitors decomposition trends. You invoke it when you suspect high-frequency decomposition.

**Command sequence:**
```bash
/router profile cloud
/router tier medium
```

**Prompt:**
```
You are the medium cloud decomposition detector.
Read the session notes in wiki/operational/sessions/
for the keyword-router debug project.

Calculate the 2x decomposition ratio for the last 10 minutes.
If ratio > 60%, produce deeper decomposition recommendations (3x–4x)
and signal the low cloud orchestrator to engage high-frequency mode.
```

**When to invoke:**
- Every 10 minutes during active execution, or
- When the low cloud reports repeated task failures, or
- When you see the low cloud performing 2x decomposition on most tasks

---

### Step 4: How to Invoke the High Cloud (Plan Updates)

The high cloud (`kimi-k2.6:cloud`) is for plan changes only. Do not invoke it for execution.

**Command sequence:**
```bash
/router profile cloud
/router tier high
```

**When to invoke:**
- You need to modify the plan or AGENTS.md
- The medium cloud reports persistent high-frequency decomposition (> 20 min)
- A phase transition requires review
- You want to decompose the next phase (B-KR-002, etc.)

**What NOT to do:**
- Do NOT invoke high cloud to write test stubs or run commands
- Do NOT invoke high cloud to check health reports

---

## Monitoring During Execution

### Health Reports (User Checks)

Every 5 minutes, check for the latest report:
```bash
ls -lt wiki/operational/sessions/STATUS-KEYWORD-ROUTER-DEBUG-*
```

Open the most recent. Look for:
- Decomposition ratio (if > 60%, consider invoking medium cloud)
- Failed nodes (if any, low cloud should be recovering via playbook-executor)
- Tasks in flight (if stalled, low cloud may need help)

### Manual Intervention Triggers

| Observation | Action |
|-------------|--------|
| Decomposition ratio > 60% for > 10 min | Invoke medium cloud for deeper decomposition |
| Node OOM/crash in health report | Verify low cloud dispatched playbook-executor; if not, invoke manually |
| Task stalled > 15 min | Check if local model failed silently; ask low cloud for status |
| Low cloud claims success without test evidence | Reject claim, ask low cloud to re-verify per AGENTS.md |

---

## Example: Full Session Walkthrough

### Phase 0 Kickoff

```bash
# 1. Start as Low Cloud Orchestrator
/router profile auto
/router tier medium
```

**Prompt:**
```
You are the low cloud orchestrator.
Read DECOMP-B-KR-001-2026-05-13.md and AGENTS.md.
Use the decompose-execute-verify skill for any step breakdowns.
Begin with Step 0: B-KR-001-HARNESS-001.
```

**Low Cloud responds:**
```
Step 0: Scaffolding test harness on fnet3.
Dispatching via SSH:
ssh fnet3 "mkdir -p ..."
Verifying harness is runnable...
Harness confirmed. Proceeding to Step 1.
```

**Low cloud assigns Step 1:**
```
Step 1: B-KR-001-UNIT-001 assigned to Low Local (qwen3.5:4b) on fnet1.
Dispatching via SSH...
```

**Low cloud executes SSH dispatch, collects evidence, verifies.**

**Repeat until all 8 steps complete.**

---

### If Decomposition Ratio Spikes

After Step 4, you notice the health report shows 3 of 4 tasks needed 2x decomposition:

```bash
# Invoke Medium Cloud
/router profile cloud
/router tier medium
```

**Prompt:**
```
Analyze decomposition trends for B-KR-001 steps.
Ratio appears elevated. Produce finer decomposition for remaining steps.
```

**Medium Cloud responds with refined step definitions.**

```bash
# Return to Low Cloud
/router profile auto
/router tier medium
```

**Prompt:**
```
Medium cloud recommends 3x decomposition for remaining steps.
Here are the refined definitions: [paste]
Please adopt and continue orchestration.
```

---

## Tier Selection Cheat Sheet

| Task | Profile | Tier | Model | Node |
|------|---------|------|-------|------|
| Planning, plan updates | `cloud` | `high` | `kimi-k2.6:cloud` | Orchestrator (Mac) |
| Decomposition detection | `cloud` | `medium` | `deepseek-v4-pro:cloud` | Orchestrator (Mac) |
| Orchestration, verification | `auto` | `medium` | `qwen3.5:397b-cloud` | Orchestrator (Mac) |
| Fine-grained breakdown | `auto` | `medium` | `decomposer` agent | Orchestrator (Mac) |
| Output validation | `auto` | `medium` | `verifier` agent | Orchestrator (Mac) |
| Complex coding | `general` | `high` | `qwen3:8b` | fnet3–fnet6 |
| Standard coding | `auto` | `low` | `gemma4:e4b` | fnet3–fnet6 |
| Simple tasks | `general` | `low` | `qwen3.5:4b` | fnet1, fnet2, fnet7 |

---

## Important Rules

1. **Never use `coding` profile** for this debug project. The `coding` profile maps high tier to `qwen3.5:397b-cloud`, which is the Low Cloud orchestrator — you would accidentally use the orchestrator for execution.
2. **Always switch back to Low Cloud after a local model completes.** The low cloud is the single point of orchestration. Do not chain local model executions without low cloud verification.
3. **Do not invoke High Cloud for execution.** It is planning-only and expensive.
4. **Check health reports every 5 minutes.** This is your window into whether the low cloud is functioning correctly.
5. **All execution happens on Lab Nodes.** The orchestrator only dispatches SSH commands and collects results. Never run tests or write code on the Mac.
6. **Use decompose-execute-verify skill.** The low cloud invokes `decomposer` for fine-grained breakdown and `verifier` for output validation. Do not skip these gates.

---

## Files

| File | Purpose |
|------|---------|
| `DECOMP-B-KR-001-2026-05-13.md` | The decomposition the low cloud must execute |
| `AGENTS.md` | The orchestration rules the low cloud must follow |
| `PLAN-2026-05-13-1926.md` | The master plan (reference only for low cloud) |
| `INVOCATION-GUIDE-2026-05-13.md` | This document — how to invoke tiers |
| `decompose-execute-verify/SKILL.md` | The skill providing decomposer and verifier agents |
| `wiki/operational/sessions/STATUS-KEYWORD-ROUTER-DEBUG-*` | Health reports (user checks every 5 min) |

---

**Prepared by:** High Cloud Model (`ollama-cloud/kimi-k2.6`)  
**Location:** `technical-infrastructure/wiki/products/keyword-router-debug/INVOCATION-GUIDE-2026-05-13.md`  
**Next step:** User switches to `/router profile auto` + `/router tier medium` and prompts the low cloud model to begin Step 0.
