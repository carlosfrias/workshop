# Keyword Router Debug Plan — Routing Transparency Side Effects

**Date:** 2026-05-13  
**Status:** ✅ **EXECUTION COMPLETE** — Core regression fixed. Remaining items tracked in BACKLOG-keyword-router.  
**Scope:** `pi-keyword-router`, `routing-transparency`, model selection pipeline  
**Session Context:** Side effects from routing-transparency fixes caused `pi-keyword-router` to consistently select low-capacity local models regardless of prompt intent.

---

## 📊 Project Status Summary

| Phase | Status | Key Deliverable |
|-------|--------|-----------------|
| B-KR-001 (Kill-Switch) | ✅ Complete | 20 tests, persistent kill-switch, TDD RED→GREEN |
| B-KR-002 (Bisection) | ✅ Complete | Regression commit `93e1d39` identified, root cause documented |
| B-KR-003 (Fix) | ✅ Complete | One-line config fix: `router:auto` → `ollama:gemma4:e4b` |
| B-KR-004 (Cloud Escalation) | 📋 Ready | Pending — add `kimi-k2.6:cloud` for deep research |
| B-KR-005 (Runbook) | 📋 Ready | Pending — operational documentation |
| B-KR-006 (CI Test) | 📋 Ready | Pending — prevent future regressions |

**Critical backlog:** [`BACKLOG-keyword-router.md`](./BACKLOG-keyword-router.md)

---

## [S-TIGHT]

The `pi-keyword-router` extension must remain disabled until a robust kill-switch and routing-bypass mechanism is implemented. This plan follows strict Test-Driven Development (TDD): tests are written first as failing stubs, then implemented to pass. Tests are layered (unit → integration → acceptance) and workspace-specific. All execution occurs on the **Lab Node only**; the Orchestrator Node is never used for testing.

This plan is owned by the **high cloud model** (`kimi-k2.6`). The high cloud model decomposes work into steps suitable for the **medium local model** (`gemma4:e4b`). The **low cloud model** (`qwen3.5:397b-cloud`) orchestrates those steps, escalates via 2x decomposition when the medium local model fails, and executes only as a last resort. See [`AGENTS.md`](./AGENTS.md) for the full responsibility matrix.

---

## Navigation

- [Model Responsibility](#model-responsibility)
- [Anti-Hallucination Safeguards](#anti-hallucination-safeguards)
- [Local Node Recovery](#local-node-recovery)
- [High-Frequency Decomposition Detection](#high-frequency-decomposition-detection)
- [5-Minute Node Health Report](#5-minute-node-health-report)
- [TDD Methodology](#tdd-methodology)
- [Test Architecture](#test-architecture)
- [Symptom Summary](#symptom-summary)
- [Root Cause Analysis](#root-cause-analysis)
- [Proposed Architecture](#proposed-architecture)
- [Phase Plan](#phase-plan)
- [Backlog Items](#backlog-items)
- [Related Documents](#related-documents)
- [Decision Log](#decision-log)

---

## Model Responsibility

This plan is owned, maintained, and updated by the **high cloud model** (`ollama-cloud/kimi-k2.6`). No other tier may modify the plan without high cloud model approval.

**Orchestration Skill:** The low cloud model uses the **decompose-execute-verify** skill (`/Users/friasc/.pi/agent/git/github.com/carlosfrias/decompose-execute-verify/skills/decompose-execute-verify/SKILL.md`) for structured decomposition, execution dispatch, and verification gates. See the skill file for decomposer agent, verifier agent, and pre-built chain definitions.

### Responsibility Matrix

| Tier | Model | Role | Executes Code? | Typical Assignment |
|------|-------|------|---------------|-------------------|
| **High Cloud** | `ollama-cloud/kimi-k2.6` | Plan Owner & Decomposer | **NO** — planning only | Complex architecture, plan updates, decomposition design |
| **Medium Cloud** | `ollama-cloud/deepseek-v4-pro` | High-Frequency Decomposition Detection Assistant | **NO** — analysis only | Analyzes decomposition trends, recommends granularity adjustments, produces deeper decompositions when ratio > 60% |
| **Low Cloud** | `ollama-cloud/qwen3.5:397b` | Orchestrator, Escalation Handler, Node Recovery Dispatcher | **YES** — last resort only | Orchestration, 2x decomposition, node recovery dispatch, direct execution when local pool exhausted |
| **High Local** | `ollama/qwen3:8b` | Complex Execution | **YES** | Complex classifier logic, multi-module refactoring, cloud escalation implementation |
| **Medium Local** | `ollama/gemma4:e4b` | Standard Execution | **YES** | Standard test stub writing, implementation, integration wiring |
| **Low Local** | `ollama/qwen3.5:4b` | Simple Execution | **YES** | Simple test stubs, config validation, log parsing, quick fixes |

**Execution Rule:** **Only local models (with `ollama/` prefix) execute on Lab Nodes.** Cloud models (`ollama-cloud/` prefix) never run locally — Medium Cloud does analysis only; Low Cloud orchestrates and dispatches to lab nodes via SSH. The Orchestrator Node (Mac) does not execute tests or write code.

### Decomposition & Escalation Flow

```
High Cloud Model (kimi-k2.6) on Orchestrator (Mac)
    │
    ├── Owns 1-PLAN.md
    ├── Owns AGENTS.md
    └── Decomposes into local-model-sized steps
              │
              ▼
    Medium Cloud Model (deepseek-v4-pro) on Orchestrator (Mac)
        │
        ├── Monitors decomposition ratio (rolling 10-min window)
        ├── When ratio > 60%: signals Low Cloud → engage deeper decomposition
        ├── Produces finer-grained decomposition recommendations
        └── Reports to High Cloud if ratio stays elevated > 20 min
              │
              ▼
    Low Cloud Model (qwen3.5:397b-cloud) on Orchestrator (Mac)
        │
        ├── Reads AGENTS.md
        ├── Checks Medium Cloud signal (high-freq mode yes/no)
        ├── Assesses step complexity → Selects local model tier (low / medium / high)
        ├── Selects target lab node from node-capacity-map
        ├── **Dispatches step via SSH to selected Lab Node**
        │
        │   Lab Node (fnet1–fnet7)
        │       ├── Local Model loads (qwen3.5:4b / gemma4:e4b / qwen3:8b)
        │       ├── Execution only — no thinking or decomposition beyond task scope
        │       ├── Writes failing test stubs (RED)
        │       ├── Implements to pass (GREEN)
        │       ├── Refactors
        │       └── Reports PASS / FAIL with test evidence back to Orchestrator
        │
        ├── **Collects test evidence from Lab Node via SSH/SCP**
        ├── Verifies evidence before accepting completion
        │
        ├── If FAIL → performs 2x decomposition → Dispatches to Lab Node again
        │       │
        │       ├── Sub-step A → Lab Node → PASS/FAIL
        │       └── Sub-step B → Lab Node → PASS/FAIL
        │
        ├── If Lab Node fails → Dispatch playbook-executor recovery to spare node
        │
        └── If still failing after 2x decomposition:
                Low Cloud Model executes directly (last resort, still on cloud)
```

### Rules

**High Cloud Model:**
- Must Always: Own the plan, own `AGENTS.md`, decompose into local-model-sized steps, define acceptance criteria.
- Must Never: Execute code, write test stubs, modify source files, run commands on any node.

**Medium Cloud Model (`deepseek-v4-pro`):**
- Must Always: Monitor decomposition ratio from session notes; when ratio > 60% over 10 min, produce deeper decomposition recommendations (3x–4x) and signal Low Cloud to engage high-frequency mode; report persistent elevation (> 20 min) to High Cloud.
- Must Never: Execute code, directly modify source files, or skip notifying Low Cloud when high-frequency mode is warranted.

**Low Cloud Model:**
- Must Always: Orchestrate decomposed steps, **exercise discretion in model assignment** (low / medium / high local), monitor execution, perform 2x decomposition on failure, **dispatch playbook-executor for node recovery**, execute only as last resort, **respond to Medium Cloud high-frequency signals by engaging deeper decomposition**.
- Must Never: Modify the plan or `AGENTS.md` without high cloud approval, skip 2x decomposition, execute on Orchestrator Node, **ignore medium cloud high-frequency signals**.

**Local Models (All Tiers):**
- Must Always: **Execute only on Lab Nodes.** The orchestrator dispatches work via SSH; the local model loads on the lab node and performs the task. Focus on code, tests, and commands. Maintain performance. Write test stubs first (RED), then implement (GREEN), then refactor. Keep work in correct workspace. Run tests on the Lab Node. **Provide test evidence with every success claim.** Report results back to the orchestrator.
- Must Never: Modify the plan or `AGENTS.md`, orchestrate across steps, decide phase transitions, **claim success without passing tests**, **self-decompose or replan** (return to orchestrator instead). Execute on the Orchestrator Node (Mac).
- **On Failure or Uncertainty:** Return to orchestrator with step_id, exact reason, and request for reassignment / decomposition / direct execution. Never attempt independent decomposition.
- **Execution Location:** All file writes, test runs, and code changes occur on the Lab Node. The Orchestrator Node only dispatches commands and collects results.

For the full orchestration guide, see [`AGENTS.md`](./AGENTS.md).

---

## Anti-Hallucination Safeguards

Local models are prone to hallucinating success. The following safeguards apply to all execution:

1. **Test Evidence Required.** A local model must not report a step as complete without providing:
   - Test command output showing pass/fail counts.
   - File diff (`git diff --stat`) of changed files.
   - Lab Node verification for integration/acceptance layers.
2. **Verifier Pattern.** The low cloud model re-runs tests independently to confirm pass counts before accepting any completion claim.
3. **No Success Without Green Tests.** A completion claim is **invalid** unless all new tests were initially failing (RED confirmed) and now pass (GREEN confirmed), and the verifier confirms the pass.
4. **Reject Missing Evidence.** If a local model claims success without test evidence, the low cloud model must reject the claim, re-run tests, and either return for correction or escalate.

For full safeguard procedures, see [`AGENTS.md`](./AGENTS.md).

---

## Local Node Recovery

If a lab node in the pool crashes, OOMs, or becomes unresponsive:

1. **Low cloud model detects failure** via test timeout or health-monitor events.
2. **Low cloud dispatches a low-capacity lab node** to run the appropriate **playbook-executor** recovery playbook:
   ```bash
   pi playbook-execute --playbook node-recovery --target {failed-node} \
     --vars "reason={oom|crash|network},service={ollama|pi-agent}"
   ```
3. **Playbook actions** may include restarting Ollama, clearing model cache, pulling missing models, or restarting the pi agent.
4. **Low cloud verifies recovery** via health check before resuming workload.
5. **If recovery fails:** Mark node offline and redistribute workload to healthy nodes.

For full recovery protocol, see [`AGENTS.md`](./AGENTS.md).

---

## High-Frequency Decomposition Detection

The **medium cloud model** (`deepseek-v4-pro`) and the **low cloud model** (`qwen3.5:397b`) collaborate to detect and respond to excessive decomposition rates. The medium cloud focuses on **analysis and recommendation**; the low cloud focuses on **action**.

### Roles

| Model | Role | Executes Code? |
|-------|------|---------------|
| **Medium Cloud** (`deepseek-v4-pro`) | Analyzes decomposition trends, produces deeper decomposition plans, signals Low Cloud | **NO** |
| **Low Cloud** (`qwen3.5:397b`) | Receives signal, engages deeper decomposition, logs metrics, reports to user | **YES** (action only) |

### Detection Protocol

1. **Low cloud collects metrics** — Every task assignment and decomposition event is timestamped in session notes.
2. **Medium cloud reads session notes** at 10-minute intervals and calculates the ratio:
   ```
   ratio = (tasks_decomposed in last 10 min) / (total_tasks_assigned in last 10 min)
   ```
3. **Threshold table:**

| Ratio | Window | Action | Owner |
|-------|--------|--------|-------|
| > 60% | Rolling 10 min | Medium Cloud signals Low Cloud → high-frequency mode | Medium Cloud |
| 40–60% | Rolling 10 min | Monitor only, no action | Low Cloud |
| < 40% | Two consecutive windows | Exit high-frequency mode, resume 2x | Low Cloud |

4. **Medium Cloud produces deeper decomposition** — When ratio > 60%, the medium cloud re-examines pending and incoming steps from the High Cloud and produces **3x–4x finer decomposition plans**. These plans are passed to the Low Cloud as replacement step definitions.
5. **Medium Cloud escalates to High Cloud** — If the ratio stays > 60% for > 20 consecutive minutes, the medium cloud reports to the High Cloud that the initial decomposition granularity may be systematically too coarse.

### High-Frequency Mode Behavior (Low Cloud)

When the Low Cloud receives a high-frequency signal from the Medium Cloud:

1. **Adopt deeper decomposition plans** from Medium Cloud (3x–4x instead of 2x).
2. **Finer model matching** — assign simplest fragments to low local; reserve medium/high local for only the most complex pieces.
3. **Alert in next health report** — flag the condition and which step_ids triggered it.
4. **Log the signal** — record timestamp, ratio, and medium cloud recommendation in session notes.

For the full detection and reporting protocol, see [`AGENTS.md`](./AGENTS.md).

---

## 5-Minute Node Health Report

The low cloud model writes a node health report every 5 minutes during active execution. The report is discoverable in the wiki session folder for manual review and intervention.

### Report Location

```
wiki/operational/sessions/STATUS-KEYWORD-ROUTER-DEBUG-YYYY-MM-DD-HHMM.md
```

### Report Contents

Each report includes:
- **Active lab nodes** — which models are loaded, health status, last task.
- **Failed nodes (last 5 min)** — failure time, reason, recovery action, current status.
- **Task decomposition metrics (last 10 min)** — total tasks, decomposed tasks, ratio, whether high-frequency mode is active.
- **Tasks in flight** — step IDs, assigned models, elapsed time.
- **Alerts** — specific, actionable alerts with step IDs.
- **Manual intervention prompts** — checkboxes the user can act on.

### User Discovery

```bash
# List all health reports for this debug session
ls -lt wiki/operational/sessions/STATUS-KEYWORD-ROUTER-DEBUG-*
```

The most recent report is at the top. Open it to see current node health, decomposition trends, and any alerts requiring manual intervention.

For the full report template and rules, see [`AGENTS.md`](./AGENTS.md).

---

## TDD Methodology

This plan follows the **Red → Green → Refactor** cycle for every phase.

### Rules
1. **No production code without a failing test first.** Every change starts with a test that fails because the implementation is a stub or missing.
2. **Tests live in the workspace they validate.**
   - `pi-keyword-router` tests → `technical-infrastructure/packages/pi-keyword-router/test/`
   - `routing-transparency` tests → `technical-infrastructure/packages/routing-transparency/test/`
3. **Three test layers, executed in sequence:**
   - **Unit tests** — Single module, mocked dependencies, fast (< 100ms each).
   - **Integration tests** — Two or more modules interacting, real (non-mocked) event bus and config.
   - **Acceptance tests** — End-to-end on Lab Node, real model-router, real extensions, simulated prompts.
4. **Lab Node execution only.** All test execution, code writing, and validation runs on **Lab Nodes** (fnet1–fnet7) via SSH dispatch from the orchestrator. The Orchestrator Node (Mac) is never used for test execution, debugging, or validation. The orchestrator only dispatches commands and collects results.
5. **Stubs are explicit.** Every stub is named `stub-*` or `mock-*` and committed with a `// TODO: implement` comment.

### Test Layer Definitions

| Layer | Scope | Location | When They Run | Pass Gate |
|-------|-------|----------|---------------|-----------|
| **Unit** | One function/class in isolation | `test/unit/` | After every code change | 100% pass |
| **Integration** | Module interaction (events, config, hooks) | `test/integration/` | After unit suite passes | 100% pass |
| **Acceptance** | Full pipeline on Lab Node | `test/acceptance/` or Lab Node scripts | After integration suite passes | All KR scenarios pass |

---

## Test Architecture

### Workspace 1: `pi-keyword-router`

> **Prerequisite:** Before any test stubs are written, the `pi-keyword-router` workspace must have a test harness mirroring the `routing-transparency` structure. If the `test/` directory does not exist or lacks the `unit/`, `integration/`, and `acceptance/` subdirectories, the first step in every phase must be to scaffold the harness.
> 
> **Lab Node Target:** The harness and all test files are created on a **Lab Node** (not the orchestrator). The orchestrator dispatches SSH commands to the selected lab node. See [Lab Node Dispatch Rules](#lab-node-dispatch-rules) below.

**Test Harness Target Structure:**

```
technical-infrastructure/packages/pi-keyword-router/
├── src/
│   ├── index.ts
│   ├── lib/
│   │   ├── classifier.ts
│   │   ├── types.ts
│   │   ├── config.ts
│   │   └── gatekeeper.ts          ← NEW (stub)
│   └── model-router/
│       └── gatekeeper.ts          ← NEW (stub)
└── test/                           ← MUST EXIST on Lab Node (mirror routing-transparency)
    ├── unit/                       ← MUST EXIST on Lab Node
    │   ├── kill-switch.test.ts     ← NEW (stub: config flag read)
    │   ├── classifier.test.ts      ← EXISTING (extend with upgradeThreshold)
    │   ├── cloud-escalation.test.ts ← NEW (stub: trigger detection)
    │   └── gatekeeper.test.ts      ← NEW (stub: bypass logic)
    ├── integration/                ← MUST EXIST on Lab Node
    │   ├── keyword-router-with-model-router.test.ts ← NEW (stub)
    │   ├── keyword-router-with-transparency.test.ts ← NEW (stub)
    │   └── cloud-cost-confirmation.test.ts          ← NEW (stub)
    └── acceptance/                 ← MUST EXIST on Lab Node
        ├── kr-001-monitoring-route.test.ts           ← NEW (stub)
        ├── kr-002-reasoning-route.test.ts            ← NEW (stub)
        ├── kr-003-infrastructure-route.test.ts       ← NEW (stub)
        ├── kr-004-cloud-escalation.test.ts           ← NEW (stub)
        ├── kr-005-minimal-keyword.test.ts            ← NEW (stub)
        ├── kr-006-manual-selection.test.ts           ← NEW (stub)
        └── kr-007-re-enablement.test.ts              ← NEW (stub)
```

### Workspace 2: `routing-transparency`

> **Lab Node Target:** `routing-transparency` tests also execute on Lab Nodes. The `routing-transparency` workspace may exist on both orchestrator and lab nodes (via shared filesystem or sync), but test execution occurs on the lab node assigned by the orchestrator.

```
technical-infrastructure/packages/routing-transparency/
├── src/
│   ├── index.ts
│   ├── routing-footer.ts
│   └── types.ts
└── test/
    ├── unit/
    │   ├── footer-disabled-state.test.ts            ← NEW (stub: footer shows "disabled")
    │   ├── footer-override-reason.test.ts           ← NEW (stub: footer shows overrideReason)
    │   └── footer-cloud-cost.test.ts                ← NEW (stub: footer shows cloud pricing)
    ├── integration/
    │   ├── transparency-with-keyword-router.test.ts   ← NEW (stub: event flow)
    │   └── transparency-with-model-router.test.ts     ← NEW (stub: manual selection)
    └── acceptance/
        └── lab-node-validation-suite.test.ts         ← NEW (stub: end-to-end)
```

---

## Lab Node Dispatch Rules

### Node Capacity Reference

| Node | CPU | RAM | Safe Capacity | Installed Models | Assign When |
|------|-----|-----|--------------|-----------------|-------------|
| fnet1 | i5-6400 / 4 cores / 15GB | 12.5GB | `qwen3.5:4b`, `qwen3:8b` | Low/medium complexity tasks |
| fnet2 | i5-6400 / 4 cores / 15GB | 12.5GB | `qwen3.5:4b`, `qwen3:8b` | Low/medium complexity tasks |
| fnet3 | i7-10710U / 12 cores / 31GB | 27.0GB | `qwen3.5:4b`, `qwen3:8b`, `gemma4:e4b` | All complexities including vision |
| fnet4 | i7-10710U / 12 cores / 31GB | 27.0GB | `qwen3.5:4b`, `qwen3:8b`, `gemma4:e4b` | All complexities including vision |
| fnet5 | i7-10710U / 12 cores / 31GB | 27.0GB | `qwen3.5:4b`, `qwen3:8b`, `gemma4:e4b` | All complexities including vision |
| fnet6 | i7-10710U / 12 cores / 31GB | 27.0GB | `qwen3.5:4b`, `qwen3:8b`, `gemma4:e4b` | All complexities including vision |
| fnet7 | i5-6400 / 4 cores / 15GB | 12.5GB | `qwen3.5:4b`, `qwen3:8b` | Low/medium complexity tasks |

**Reference:** [`node-capacity-map.md`](../../../reference/node-capacity-map.md)

### Orchestrator Dispatch Protocol

The **low cloud orchestrator** (`qwen3.5:397b-cloud`) runs on the **Orchestrator Node** (Mac). It does **not** execute code or tests itself. Instead, it:

1. **Selects the target lab node** based on the assigned model tier and current node health.
2. **Dispatches the task via `pi-intercom`** to the selected lab node's named session.
3. **Monitors execution** by polling the lab node for status and test output via intercom.
4. **Collects test evidence** (output, diffs, logs) from the lab node before accepting completion.

**pi-intercom Dispatch (Primary)**
```typescript
// Low Cloud selects node (e.g., fnet3 for gemma4:e4b task)
// Dispatches via pi-intercom to the lab node's named session
intercom({
  action: "ask",
  to: "fnet3",
  message: "Step B-KR-001-UNIT-001: Write failing test stub..."
})
```

**SSH Dispatch (Fallback — if pi-intercom is not responding)**
```bash
ssh -o ConnectTimeout=5 fnet3 "ollama ps && echo OK"
ssh fnet3 "cd ~/workshop/technical-infrastructure/packages/pi-keyword-router && npm test -- test/unit/kill-switch.test.ts"
```

**Result Collection:**
```bash
# Low Cloud collects test output from lab node
ssh fnet3 "cat ~/workshop/technical-infrastructure/packages/pi-keyword-router/test-output.log"
ssh fnet3 "cd ~/workshop/technical-infrastructure/packages/pi-keyword-router && git diff --stat"
```

### Node Selection Algorithm

1. **Determine required model** from the step's `recommended_model` (e.g., `gemma4:e4b`).
2. **Filter nodes** that have the model installed (from node-capacity-map).
3. **Check node health** — query the node's ollama status and available RAM.
4. **Select least-loaded qualifying node** — prefer the node with the most free RAM among those that have the required model.
5. **If no node has the required model** — dispatch playbook-executor to pull the model on the healthiest available node, then assign.
6. **If all qualifying nodes are saturated** — escalate to the next model tier (from node-capacity-map routing matrix) or invoke Medium Cloud for deeper decomposition.

### Health Check Before Dispatch

Before every dispatch, the low cloud orchestrator must verify the target node is responsive via **pi-intercom** (primary) or SSH (fallback):

```bash
# Primary: pi-intercom health check
intercom({ action: "ask", to: "{node}", message: "echo OK" })
# Expected: "OK" reply within 10 seconds

# Fallback: SSH health check
ssh -o ConnectTimeout=5 {node} "ollama ps && echo OK" || echo "NODE_UNREACHABLE"
```

If the node is unreachable:
1. Log the failure.
2. Mark node as offline in the health report.
3. Select the next best node.
4. If no nodes are available, invoke node recovery via playbook-executor.

### Acceptance Test Execution on Lab Node

All acceptance tests are executed via **pi-intercom dispatch** to a Lab Node:

```typescript
// Orchestrator dispatches via intercom to lab node
intercom({
  action: "ask",
  to: "fnet3",
  message: "Run acceptance suite: cd ~/workshop/technical-infrastructure/packages/pi-keyword-router && npm test -- --suite=acceptance"
})

// Results are collected via intercom reply or file transfer
ssh fnet3 "cat ~/workshop/technical-infrastructure/packages/pi-keyword-router/test-results.jsonl"
```

Results are written to:
- `technical-infrastructure/wiki/products/keyword-router-debug/TEST-RESULTS-YYYY-MM-DD-HHMM.md`

---

## Symptom Summary

| Symptom | Observation | Severity |
|---------|-------------|----------|
| Low-capacity lock-in | All prompts route to `qwen3.5:4b` regardless of keywords or complexity | 🔴 Critical |
| No cloud escalation | Keywords that should trigger `kimi-k2.6:cloud` or `qwen3.5:397b-cloud` never do | 🔴 Critical |
| No high-capacity local | Keywords that should trigger `gemma4:e4b` (reasoning) are ignored | 🔴 Critical |
| Keyword-router must stay OFF | User mandate: disabled state must persist across sessions until explicitly re-enabled | 🔴 Critical |
| Regression from transparency fixes | Issues began after `routing-transparency` Phase 1–4 implementation (2026-05-12/13) | 🔴 Critical |

**Pre-conditions for any fix:**
1. `pi-keyword-router` is OFF and stays OFF.
2. The OFF state persists past session restarts.
3. No prompt may re-enable the router automatically.
4. **All testing occurs on the Lab Node only.**

---

## Root Cause Analysis

### Hypothesis 1 — Classification Priority Inversion (CONFIRMED, PARTIALLY FIXED)

**Evidence:** The `FIX-SUMMARY-2026-05-13-1157.md` document confirms that `classifier.ts` was running auto-complexity heuristic **before** keyword inference. Short prompts like `"check position status for AAPL"` were classified as `"trivial"` based on length before keywords `"status"` and `"check"` could match the `monitoring` route.

**Fix applied:** Reordered classification priority:
```
OLD: 1.Model → 2.Route → 3.Complexity → 4.Auto-Complexity → 5.Keywords → 6.Default
NEW: 1.Model → 2.Route → 3.Complexity → 4.Keywords → 5.Auto-Complexity → 6.Default
```

**Remaining issue:** Even with keywords evaluated first, the **model selection** logic still falls back to the lowest-capacity model assigned to the matched route, or the route itself maps to a low-capacity model by default.

### Hypothesis 2 — Route-to-Model Mapping is Static and Conservative

**Evidence:** The `keyword-router.json` config maps routes to single models:
- `monitoring` → `qwen3.5:4b`
- `reasoning` → `gemma4:e4b`
- `infrastructure` → `qwen3:8b`

There is no **prompt-complexity override** within a route. If a prompt matches `monitoring` but contains reasoning keywords, the model stays `qwen3.5:4b`. The routing-transparency fixes added `costPerRoute` but did not add `complexityThreshold` or `modelOverride` logic.

### Hypothesis 3 — The "Simple Prompt" Trap

**Evidence:** The `ROUTING-TRANSPARENCY-FIX-2026-05-12-0956.md` document notes that the classifier uses prompt length and token count as complexity signals. After the transparency fixes enriched events with timing/cost data, the classifier may be **over-weighting** these heuristics. A prompt like `"analyze risk for NVDA"` is short (3 tokens) → classified as `trivial` → model `qwen3.5:4b`, even though the keyword `"analyze"` should trigger `reasoning` → `gemma4:e4b`.

**Key insight:** The `matchedKeywords` field is now populated (fixed in `classifier.ts`), but the **model chosen from the route** does not account for sub-route complexity or keyword intensity.

### Hypothesis 4 — Routing-Transparency Extension Interferes with Model-Router

**Evidence:** The `routing-transparency/src/index.ts` extension listens to `keyword-router:routed` events and updates the TUI footer. It does not modify the routing decision. However, the `handleModelSwitch()` function captures manual selections (`src: manual`). There is a risk that the extension's event handler subtly alters the event payload or timing in a way that causes the downstream `model-router` to receive incomplete state.

**Status:** Unconfirmed. Requires Lab Node isolation testing.

### Hypothesis 5 — No Persistent Disable Mechanism Exists

**Evidence:** There is no `PI_KEYWORD_ROUTER_DISABLED` flag, no gatekeeper service, and no config key in `.pi/keyword-router.json` that prevents the extension from loading. The user must manually uninstall or disable the extension after every session restart.

**Status:** Confirmed. This is the blocker for all other work.

---

## Proposed Architecture

### 1. Persistent Disable Flag (KILL-SWITCH)

Implement a system-level configuration flag that prevents `pi-keyword-router` from activating, survives session restarts, and requires explicit user action to clear.

**Option A — Config File Flag (Recommended)**
```json
// ~/.pi/agent/config.json
{
  "extensions": {
    "pi-keyword-router": {
      "enabled": false,
      "disableUntil": "2026-06-01T00:00:00Z",
      "disableReason": "TI-DEBUG-2026-05-13: Routing transparency regression"
    }
  }
}
```

**Option B — Environment Variable**
```bash
export PI_KEYWORD_ROUTER_DISABLED=1
```
- Pros: Simple, survives reboots if in shell profile.
- Cons: Not workspace-specific; easy to forget.

**Option C — Gatekeeper Service**
- A lightweight `RouterGatekeeper` module intercepts all model-selection requests.
- If the flag is set, it bypasses `pi-keyword-router` entirely.
- Returns `"Model Selection Skipped: Manual/Pending Review."`

**Decision:** Implement **Option A** (config file flag) as the primary mechanism, with **Option C** (gatekeeper) as the Lab Node validation wrapper. The config flag is the kill-switch; the gatekeeper is the safety harness for testing.

### 2. Pre-Router Gatekeeper (Lab Node Only)

Create a new module `model-router/src/gatekeeper.ts` (or equivalent) that:
1. Reads `config.extensions.pi-keyword-router.enabled` before any routing logic runs.
2. If `enabled === false`:
   - Skips keyword classification entirely.
   - Falls back to `model-router`'s default behavior (manual selection, complexity-only, or default model).
   - Logs a clear audit entry: `GATEKEEPER: keyword-router disabled by config. Routing via fallback.`
3. If `enabled === true` (future state):
   - Passes through to normal keyword routing.
   - But only after the user explicitly sets it and runs a validation suite.

### 3. Keyword-Router Revalidation Protocol

Before `pi-keyword-router` can be re-enabled, the following must pass on the **Lab Node**:

| Test ID | Scenario | Expected Model | Pass Criteria |
|---------|----------|----------------|---------------|
| KR-001 | `"check position status for AAPL"` | `qwen3.5:4b` (monitoring) | Keywords match, source=`keyword` |
| KR-002 | `"analyze the risk/reward for NVDA"` | `gemma4:e4b` (reasoning) | Keywords override short length |
| KR-003 | `"deploy playbook to fnet2"` | `qwen3:8b` (infrastructure) | Domain: technical-infrastructure |
| KR-004 | `"deep research on macro trends"` | `kimi-k2.6:cloud` (reasoning + depth) | Escalation to cloud for complex |
| KR-005 | `"status"` (single word) | `qwen3.5:4b` | Minimal match still works |
| KR-006 | Ctrl+P manual selection | User-selected model | `src: manual`, footer updates |
| KR-007 | Re-enable after disable | Keyword routing resumes | Config flag clears, no crash |

---

## Phase Plan

> **Every phase follows the TDD cycle: RED (write failing test stubs) → GREEN (implement to pass) → REFACTOR (clean up).**
> **All tests run on the Lab Node. The Orchestrator Node is never used for testing.**

---

### Phase 0 — Kill-Switch Implementation (IMMEDIATE)

**Goal:** Make the disable state persistent and session-surviving.  
**Location:** `pi-keyword-router` config layer + `model-router` gatekeeper.  
**TDD Cycle:**

#### RED — Write Failing Test Stubs
1. **Unit test stub** (`pi-keyword-router/test/unit/kill-switch.test.ts`):
   - Assert that `loadConfig()` reads `extensions.pi-keyword-router.enabled`.
   - **Expected: FAIL** — no config flag schema exists.
2. **Unit test stub** (`pi-keyword-router/test/unit/gatekeeper.test.ts`):
   - Assert that when `enabled === false`, `shouldRegisterHooks()` returns `false`.
   - **Expected: FAIL** — no gatekeeper logic exists.
3. **Unit test stub** (`routing-transparency/test/unit/footer-disabled-state.test.ts`):
   - Assert that footer displays `keyword-router: disabled` when flag is `false`.
   - **Expected: FAIL** — no footer state for disabled exists.
4. **Integration test stub** (`pi-keyword-router/test/integration/keyword-router-with-model-router.test.ts`):
   - Assert that when flag is `false`, `model-router` receives a fallback route, not a keyword route.
   - **Expected: FAIL** — no gatekeeper intercept exists.
5. **Acceptance test stub** (`pi-keyword-router/test/acceptance/kr-006-manual-selection.test.ts`):
   - Simulate session restart with `enabled = false`. Assert keyword-router does not load.
   - **Expected: FAIL** — no persistence mechanism exists.

#### GREEN — Implement to Pass
- [ ] Add `enabled` flag to `.pi/agent/config.json` schema.
- [ ] Modify `pi-keyword-router/index.ts` to check flag on init; if `false`, skip all hook registration.
- [ ] Modify `model-router` to detect disabled state and route via fallback.
- [ ] Modify `routing-transparency/src/index.ts` to render `keyword-router: disabled` state.

#### REFACTOR
- [ ] Extract gatekeeper logic into `pi-keyword-router/src/lib/gatekeeper.ts`.
- [ ] Write `technical-infrastructure/packages/routing-transparency/KILL-SWITCH-2026-05-13-1926.md` documenting the mechanism.

#### Verification
- [ ] Unit suite: `npm test -- --suite=unit` → 100% pass.
- [ ] Integration suite: `npm test -- --suite=integration` → 100% pass.
- [ ] Acceptance suite on Lab Node: all KR-006 scenarios pass.

**Effort:** 2–3 hours  
**Risk:** Low — additive, no existing logic changed.

---

### Phase 1 — Isolation & Root Cause Confirmation

**Goal:** Confirm exactly which transparency fix caused the regression.  
**Location:** Lab Node only.  
**TDD Cycle:**

#### RED — Write Failing Test Stubs (Acceptance Suite)
1. **Acceptance test stubs** (`pi-keyword-router/test/acceptance/kr-001` through `kr-007`):
   - Each stub defines a prompt, expected route, expected model, expected source.
   - **Expected: FAIL** on current code (this is the baseline — they document the intended behavior).

#### GREEN — Establish Baseline
- [ ] Create a Lab Node snapshot with pre-transparency code (git checkout of `pi-keyword-router` and `routing-transparency` to 2026-05-11 state).
- [ ] Run the 7 acceptance test stubs against the pre-transparency baseline.
- [ ] **Expected: PASS** on pre-transparency code (validates the stubs themselves).

#### REFACTOR — Bisection
- [ ] Apply transparency fixes one at a time (Phase 1 → 2 → 3 → 4), re-running the acceptance suite after each.
- [ ] Identify the **exact commit** where cloud/high-capacity routing breaks.
- [ ] Document findings in `technical-infrastructure/wiki/products/keyword-router-debug/ROOT-CAUSE-YYYY-MM-DD-HHMM.md`.

#### Verification
- [ ] Acceptance suite on Lab Node: pre-transparency baseline passes all KR tests.
- [ ] Regression commit identified and documented.

**Effort:** 4–6 hours  
**Risk:** Low — read-only testing, no production impact.

---

### Phase 2 — Model Selection Logic Repair

**Goal:** Fix the classifier so keywords within a route can trigger model upgrades.  
**Location:** `pi-keyword-router/lib/classifier.ts`.  
**TDD Cycle:**

#### RED — Write Failing Test Stubs
1. **Unit test stub** (`pi-keyword-router/test/unit/classifier.test.ts`):
   - Assert that `inferFromKeywords("analyze risk for NVDA")` returns `recommendedModel: "gemma4:e4b"` and `overrideReason: "keyword-intensity"`.
   - **Expected: FAIL** — no `recommendedModel` or `overrideReason` fields exist.
2. **Unit test stub** (`pi-keyword-router/test/unit/classifier.test.ts`):
   - Assert that `upgradeThreshold` config is validated on load (reject invalid thresholds).
   - **Expected: FAIL** — no `upgradeThreshold` schema exists.
3. **Integration test stub** (`pi-keyword-router/test/integration/keyword-router-with-transparency.test.ts`):
   - Assert that when a model upgrade occurs, the `keyword-router:routed` event contains `recommendedModel` and `overrideReason`.
   - **Expected: FAIL** — event payload does not include these fields.
4. **Unit test stub** (`routing-transparency/test/unit/footer-override-reason.test.ts`):
   - Assert that footer displays `overrideReason` when `routing-transparency` receives an event with `overrideReason`.
   - **Expected: FAIL** — footer does not handle `overrideReason`.

#### GREEN — Implement to Pass
- [ ] Add `complexityOverride` / `upgradeThreshold` field to route config schema.
- [ ] Modify `inferFromKeywords()` to return `recommendedModel` and `overrideReason`.
- [ ] Ensure the `RoutingResult` type includes the new fields.
- [ ] Update `routing-transparency/src/index.ts` to read `overrideReason` from events and render it.

#### REFACTOR
- [ ] Extract keyword-intensity scoring into a pure function for testability.
- [ ] Update `pi-keyword-router/lib/types.ts` with formal types.

#### Verification
- [ ] Unit suite: classifier tests pass (including KR-002 and KR-005 logic).
- [ ] Integration suite: event payloads include `recommendedModel` and `overrideReason`.
- [ ] Acceptance suite on Lab Node: KR-002 passes (`"analyze risk for NVDA"` → `gemma4:e4b`).

**Effort:** 6–8 hours  
**Risk:** Medium — touches core classification logic.

---

### Phase 3 — Cloud Escalation Path Restoration

**Goal:** Ensure prompts that require cloud models actually reach them.  
**Location:** `pi-keyword-router/lib/classifier.ts` + `model-router`.  
**TDD Cycle:**

#### RED — Write Failing Test Stubs
1. **Unit test stub** (`pi-keyword-router/test/unit/cloud-escalation.test.ts`):
   - Assert that `detectCloudEscalation("deep research on macro trends")` returns `provider: "cloud"`, `model: "kimi-k2.6:cloud"`.
   - **Expected: FAIL** — no `detectCloudEscalation` function exists.
2. **Unit test stub** (`pi-keyword-router/test/unit/cloud-escalation.test.ts`):
   - Assert that invalid `cloudEscalation` config is rejected at load time.
   - **Expected: FAIL** — no `cloudEscalation` schema exists.
3. **Integration test stub** (`pi-keyword-router/test/integration/cloud-cost-confirmation.test.ts`):
   - Assert that when a cloud escalation is detected, a confirmation prompt event is emitted before model invocation.
   - **Expected: FAIL** — no confirmation gate exists.
4. **Unit test stub** (`routing-transparency/test/unit/footer-cloud-cost.test.ts`):
   - Assert that footer shows cloud pricing (e.g., `$0.18`) when `provider: "cloud"` is in the event.
   - **Expected: FAIL** — footer does not handle cloud cost display.

#### GREEN — Implement to Pass
- [ ] Add `cloudEscalation` config section with validation.
- [ ] Implement `detectCloudEscalation()` in `classifier.ts`.
- [ ] Modify `model-router` to pause routing and emit a `cloud-confirmation` event when `provider === "cloud"`.
- [ ] Update `routing-transparency` footer to show cloud cost.

#### REFACTOR
- [ ] Extract escalation trigger matching into a configurable regex list.
- [ ] Add a `cloudEscalation` config validator.

#### Verification
- [ ] Unit suite: cloud escalation tests pass.
- [ ] Integration suite: confirmation prompt event is emitted and consumed correctly.
- [ ] Acceptance suite on Lab Node: KR-004 passes (`"deep research on macro trends"` → `kimi-k2.6:cloud`).

**Effort:** 4–6 hours  
**Risk:** Medium — involves cost confirmation UX.

---

### Phase 4 — Integration & Regression Testing

**Goal:** Prove the entire pipeline works end-to-end before re-enabling.  
**Location:** Lab Node only.  
**TDD Cycle:**

#### RED — Write Failing Test Stubs
1. **Integration test stub** (`pi-keyword-router/test/integration/keyword-router-with-model-router.test.ts`):
   - Assert that the full pipeline (prompt → classifier → model-router → execution) completes with the correct model for every KR scenario.
   - **Expected: FAIL** until Phases 2 and 3 are complete.
2. **Integration test stub** (`routing-transparency/test/integration/transparency-with-keyword-router.test.ts`):
   - Assert that every routing decision is logged to JSONL with correct timing, cost, and `overrideReason`.
   - **Expected: FAIL** until logging is wired to new fields.
3. **Acceptance test stubs** (edge cases):
   - Empty prompt, 10,000-char prompt, unicode, special characters, prompt with no keywords.
   - **Expected: FAIL** — stubs document expected graceful behavior.

#### GREEN — Wire Integration
- [ ] Connect all modules: classifier → gatekeeper → model-router → routing-transparency.
- [ ] Ensure JSONL logger receives all new fields (`recommendedModel`, `overrideReason`, `provider`).
- [ ] Ensure billing report generator handles cloud costs correctly.

#### REFACTOR
- [ ] Optimize routing decision time to < 5ms.
- [ ] Clean up any temporary debug logging.

#### Verification
- [ ] Integration suite: full pipeline tests pass for all KR scenarios.
- [ ] Acceptance suite on Lab Node:
  - [ ] KR-001 through KR-007 pass.
  - [ ] Edge cases pass (empty, long, unicode prompts).
  - [ ] Manual selection (Ctrl+P) works and persists for next prompt.
  - [ ] Billing report accuracy validated against known costs.
  - [ ] Routing decision time < 5ms for all cases.
- [ ] Document results in `technical-infrastructure/wiki/products/keyword-router-debug/VALIDATION-YYYY-MM-DD-HHMM.md`.

**Effort:** 4–6 hours  
**Risk:** Low — testing only.

---

### Phase 5 — Controlled Re-Enablement

**Goal:** Re-enable `pi-keyword-router` in production with monitoring.  
**Location:** Orchestrator Node (production) for activation only; all validation already done on Lab Node.  
**TDD Cycle:**

#### RED — Write Failing Test Stubs (Acceptance)
1. **Acceptance test stub** (`pi-keyword-router/test/acceptance/kr-007-re-enablement.test.ts`):
   - Assert that setting `config.extensions.pi-keyword-router.enabled = true` and restarting the session causes keyword routing to resume without crashes.
   - Assert that the kill-switch can be toggled back to `false` and keyword-router immediately stops.
   - **Expected: FAIL** — this is the final validation; it passes only after the entire plan is complete.

#### GREEN — Production Activation
- [ ] Set `config.extensions.pi-keyword-router.enabled = true` on Orchestrator Node.
- [ ] Enable `routing-transparency` verbose logging for 24 hours.
- [ ] Monitor `~/.pi/logs/routing-decisions.jsonl` for anomalies.

#### REFACTOR
- [ ] Update kill-switch documentation with rollback procedure.
- [ ] Archive test results to `wiki/operational/backlog-completed/`.

#### Verification
- [ ] Acceptance suite on Lab Node: KR-007 passes (re-enablement works, no crash).
- [ ] 24-hour production monitoring shows zero anomalous routing decisions.
- [ ] User explicitly approves the re-enablement.

**Effort:** 1–2 hours + 24h monitoring  
**Risk:** Low — kill-switch allows instant rollback.

---

## Backlog Items

### B-KR-001: Implement Persistent Kill-Switch for pi-keyword-router
**Created:** 2026-05-13  
**Priority:** 🔴 High  
**Phase:** Phase 0  
**Status:** Ready to Start  
**Owner:** Technical Infrastructure  
**Effort:** 2–3 hours  
**Dependencies:** None  
**TDD Entry Point:** Write failing test stubs first (see Phase 0, RED section).  
**Test Files (stubs):**
- `technical-infrastructure/packages/pi-keyword-router/test/unit/kill-switch.test.ts` ← NEW stub
- `technical-infrastructure/packages/pi-keyword-router/test/unit/gatekeeper.test.ts` ← NEW stub
- `technical-infrastructure/packages/routing-transparency/test/unit/footer-disabled-state.test.ts` ← NEW stub
- `technical-infrastructure/packages/pi-keyword-router/test/integration/keyword-router-with-model-router.test.ts` ← NEW stub
- `technical-infrastructure/packages/pi-keyword-router/test/acceptance/kr-006-manual-selection.test.ts` ← NEW stub

**Implementation Files:**
- `pi-keyword-router/index.ts`
- `pi-keyword-router/src/lib/gatekeeper.ts` ← NEW
- `model-router` config layer
- `routing-transparency/src/index.ts`

**Acceptance Criteria:**
- [ ] Unit stubs written and initially failing (RED).
- [ ] Kill-switch implemented, all unit tests pass (GREEN).
- [ ] Integration stubs written and initially failing (RED).
- [ ] Gatekeeper wired, all integration tests pass (GREEN).
- [ ] Acceptance test KR-006 passes on Lab Node (session restart → keyword-router stays disabled).
- [ ] Config flag `extensions.pi-keyword-router.enabled` survives session restart.
- [ ] Re-enabling requires manual config edit + session restart (no auto-re-enable).

---

### B-KR-002: Lab Node Bisection — Identify Regression Commit
**Created:** 2026-05-13  
**Priority:** 🔴 High  
**Phase:** Phase 1  
**Status:** Ready to Start (blocked by B-KR-001 if kill-switch needed for safe testing)  
**Owner:** Technical Infrastructure  
**Effort:** 4–6 hours  
**Dependencies:** B-KR-001  
**TDD Entry Point:** Write KR-001 through KR-007 acceptance test stubs first (see Phase 1, RED section).  
**Test Files (stubs):**
- `technical-infrastructure/packages/pi-keyword-router/test/acceptance/kr-001-monitoring-route.test.ts` ← NEW stub
- `technical-infrastructure/packages/pi-keyword-router/test/acceptance/kr-002-reasoning-route.test.ts` ← NEW stub
- `technical-infrastructure/packages/pi-keyword-router/test/acceptance/kr-003-infrastructure-route.test.ts` ← NEW stub
- `technical-infrastructure/packages/pi-keyword-router/test/acceptance/kr-004-cloud-escalation.test.ts` ← NEW stub
- `technical-infrastructure/packages/pi-keyword-router/test/acceptance/kr-005-minimal-keyword.test.ts` ← NEW stub
- `technical-infrastructure/packages/pi-keyword-router/test/acceptance/kr-007-re-enablement.test.ts` ← NEW stub

**Implementation Files:**
- Lab Node snapshot of pre-transparency baseline
- Git history of `pi-keyword-router` and `routing-transparency`

**Acceptance Criteria:**
- [ ] All KR acceptance stubs written and failing on current code (RED).
- [ ] Pre-transparency baseline passes all KR stubs (validates stubs).
- [ ] The exact commit where cloud/high-capacity routing fails is identified.
- [ ] A `ROOT-CAUSE-YYYY-MM-DD-HHMM.md` document is written to the wiki.

---

### B-KR-003: Repair Model Selection Inside Keyword Routes
**Created:** 2026-05-13  
**Priority:** 🔴 High  
**Phase:** Phase 2  
**Status:** Blocked by B-KR-002  
**Owner:** Technical Infrastructure  
**Effort:** 6–8 hours  
**Dependencies:** B-KR-002  
**TDD Entry Point:** Write unit test stubs for `recommendedModel` and `upgradeThreshold` first (see Phase 2, RED section).  
**Test Files (stubs):**
- `technical-infrastructure/packages/pi-keyword-router/test/unit/classifier.test.ts` ← EXTEND with upgradeThreshold stubs
- `technical-infrastructure/packages/pi-keyword-router/test/unit/gatekeeper.test.ts` ← EXTEND with bypass logic stubs
- `technical-infrastructure/packages/routing-transparency/test/unit/footer-override-reason.test.ts` ← NEW stub
- `technical-infrastructure/packages/pi-keyword-router/test/integration/keyword-router-with-transparency.test.ts` ← NEW stub

**Implementation Files:**
- `pi-keyword-router/lib/classifier.ts`
- `pi-keyword-router/lib/types.ts`
- `pi-keyword-router/lib/config.ts`
- `routing-transparency/src/index.ts`

**Acceptance Criteria:**
- [ ] Unit stubs for `recommendedModel` and `upgradeThreshold` written and failing (RED).
- [ ] `inferFromKeywords()` returns `recommendedModel` based on keyword intensity/complexity.
- [ ] Route config supports `upgradeThreshold` overrides.
- [ ] Unit tests pass (GREEN).
- [ ] Integration stubs written and failing (RED).
- [ ] Event payload includes `recommendedModel` and `overrideReason`; integration tests pass (GREEN).
- [ ] Acceptance test KR-002 passes on Lab Node (`"analyze risk for NVDA"` → `gemma4:e4b`).
- [ ] Acceptance test KR-005 passes on Lab Node (`"status"` single word → `qwen3.5:4b`).
- [ ] Footer shows `overrideReason` when a model upgrade occurs.

---

### B-KR-004: Restore Cloud Model Escalation Path
**Created:** 2026-05-13  
**Priority:** 🟡 Medium  
**Phase:** Phase 3  
**Status:** Blocked by B-KR-003  
**Owner:** Technical Infrastructure  
**Effort:** 4–6 hours  
**Dependencies:** B-KR-003  
**TDD Entry Point:** Write unit test stubs for `cloudEscalation` and `detectCloudEscalation` first (see Phase 3, RED section).  
**Test Files (stubs):**
- `technical-infrastructure/packages/pi-keyword-router/test/unit/cloud-escalation.test.ts` ← NEW stub
- `technical-infrastructure/packages/pi-keyword-router/test/integration/cloud-cost-confirmation.test.ts` ← NEW stub
- `technical-infrastructure/packages/routing-transparency/test/unit/footer-cloud-cost.test.ts` ← NEW stub

**Implementation Files:**
- `pi-keyword-router/lib/classifier.ts`
- `keyword-router.json` config schema
- `model-router` confirmation gate
- `routing-transparency/src/index.ts` (cloud cost display)

**Acceptance Criteria:**
- [ ] Unit stubs for `cloudEscalation` written and failing (RED).
- [ ] `cloudEscalation` config section exists and is validated on load.
- [ ] `detectCloudEscalation()` unit tests pass (GREEN).
- [ ] Integration stubs written and failing (RED).
- [ ] Confirmation prompt event is emitted before cloud model invocation; integration tests pass (GREEN).
- [ ] Acceptance test KR-004 passes on Lab Node (`"deep research on macro trends"` → `kimi-k2.6:cloud`).
- [ ] Cost tracking in `routing-transparency` shows correct cloud pricing.

---

### B-KR-005: End-to-End Regression Test Suite
**Created:** 2026-05-13  
**Priority:** 🟡 Medium  
**Phase:** Phase 4  
**Status:** Blocked by B-KR-004  
**Owner:** Technical Infrastructure  
**Effort:** 4–6 hours  
**Dependencies:** B-KR-004  
**TDD Entry Point:** Write integration and acceptance stubs for full pipeline first (see Phase 4, RED section).  
**Test Files (stubs):**
- `technical-infrastructure/packages/pi-keyword-router/test/integration/keyword-router-with-model-router.test.ts` ← EXTEND with full pipeline stubs
- `technical-infrastructure/packages/routing-transparency/test/integration/transparency-with-keyword-router.test.ts` ← NEW stub
- `technical-infrastructure/packages/routing-transparency/test/acceptance/lab-node-validation-suite.test.ts` ← NEW stub
- Edge-case acceptance stubs in `pi-keyword-router/test/acceptance/`

**Implementation Files:**
- Full pipeline wiring (classifier → gatekeeper → model-router → transparency)
- JSONL logger field updates
- Billing report generator cloud-cost handling

**Acceptance Criteria:**
- [ ] Integration stubs for full pipeline written and failing (RED).
- [ ] All modules wired; integration tests pass (GREEN).
- [ ] Acceptance test KR-001 through KR-007 pass on Lab Node.
- [ ] Edge cases pass (empty, long, unicode prompts).
- [ ] Manual selection (Ctrl+P) works and persists for next prompt.
- [ ] Billing report accuracy validated against known costs.
- [ ] Routing decision time < 5ms for all cases.
- [ ] `VALIDATION-YYYY-MM-DD-HHMM.md` document written to wiki.

---

### B-KR-006: Controlled Production Re-Enablement
**Created:** 2026-05-13  
**Priority:** 🟢 Low  
**Phase:** Phase 5  
**Status:** Blocked by B-KR-005  
**Owner:** Technical Infrastructure  
**Effort:** 1–2 hours + 24h monitoring  
**Dependencies:** B-KR-005  
**TDD Entry Point:** Write KR-007 re-enablement acceptance stub first (see Phase 5, RED section).  
**Test Files (stubs):**
- `technical-infrastructure/packages/pi-keyword-router/test/acceptance/kr-007-re-enablement.test.ts` ← EXTEND with toggle-back test

**Implementation Files:**
- Orchestrator Node config (`~/.pi/agent/config.json`)
- `~/.pi/logs/routing-decisions.jsonl` (monitoring target)

**Acceptance Criteria:**
- [ ] Acceptance stub KR-007 written and failing (RED).
- [ ] `pi-keyword-router` re-enabled on Orchestrator Node.
- [ ] Verbose logging enabled for 24 hours.
- [ ] No anomalous routing decisions detected in logs.
- [ ] Kill-switch documentation updated with rollback procedure.
- [ ] User explicitly approves the re-enablement.

---

## Related Documents

| Document | Purpose | Location |
|----------|---------|----------|
| `AGENTS.md` | **Model responsibility matrix & orchestration guide** | `technical-infrastructure/wiki/products/keyword-router-debug/` |
| `INVOCATION-GUIDE-2026-05-13.md` | **How to invoke each tier manually with `/router` commands** | `technical-infrastructure/wiki/products/keyword-router-debug/` |
| `DECOMP-B-KR-001-2026-05-13.md` | **Phase 0 decomposition (8 steps)** | `technical-infrastructure/wiki/products/keyword-router-debug/` |
| `ROUTING-TRANSPARENCY-FIX-2026-05-12-0956.md` | Original transparency fix design | `technical-infrastructure/packages/routing-transparency/` |
| `FIX-SUMMARY-2026-05-13-1157.md` | Classification priority fix | `technical-infrastructure/packages/routing-transparency/` |
| `COMPLETION-SUMMARY-2026-05-13-1129.md` | Event enrichment & timing fix | `technical-infrastructure/packages/routing-transparency/` |
| `keywords-system-architecture-2026-05-13-1815.md` | Gatekeeper architectural plan | `technical-infrastructure/packages/routing-transparency/` |
| `INSTALLATION-FIX-2026-05-13-1430.md` | Installation fix notes | `technical-infrastructure/packages/routing-transparency/` |
| `DEBUG-CONTEXT-2026-05-13-1926.md` | Consolidated debug context (this session) | `technical-infrastructure/packages/routing-transparency/` |
| `TEST-FOOTER-2026-05-13-11:28.md` | Footer test plan | `technical-infrastructure/packages/routing-transparency/` |

---

## Decision Log

### 2026-05-13 19:26 — Plan Drafted
**Decision:** Create a 6-phase plan (Phase 0 = kill-switch, Phases 1–4 = Lab Node debug, Phase 5 = production re-enablement).  
**Rationale:** The user requires the router to stay OFF until fixed. A kill-switch is the prerequisite for all other work. Isolating debug to Lab Node prevents production contamination.

### 2026-05-13 19:26 — Kill-Switch: Config File Over Environment Variable
**Decision:** Use `.pi/agent/config.json` `extensions.pi-keyword-router.enabled` as the primary mechanism.  
**Rationale:** Workspace-specific, version-controllable, and can be validated by `model-router` before any extension code runs.

### 2026-05-13 19:26 — No Auto-Re-Enable
**Decision:** Re-enabling `pi-keyword-router` requires manual config edit + session restart.  
**Rationale:** Prevents accidental activation. The user explicitly stated: "I won't enable it until we fix it."

### 2026-05-13 — TDD Mandate
**Decision:** Every phase follows strict Red → Green → Refactor. Tests written first as failing stubs.  
**Rationale:** Guarantees that every fix is verifiable, prevents regression, and produces a test suite that outlives the debug session.

### 2026-05-13 — Lab Node Testing Only
**Decision:** All unit, integration, and acceptance tests run on the Lab Node. The Orchestrator Node is never used for test execution.  
**Rationale:** Prevents test artifacts, temporary stubs, or incomplete code from affecting the production routing pipeline.

---

### 2026-05-13 — Model Tier Responsibility Assignment
**Decision:** Assign plan ownership to the high cloud model (`kimi-k2.6`), orchestration to the low cloud model (`qwen3.5:397b-cloud`), and execution to the medium local model (`gemma4:e4b`). The low cloud model handles 2x decomposition and executes only as last resort.  
**Rationale:** Maximizes cost efficiency by pushing execution to the cheapest capable tier (medium local). Reserves high cloud capacity for planning only. Uses low cloud for orchestration and fallback execution, which is cheaper than high cloud but more capable than medium local for complex fallback tasks.  
**Reference:** [`AGENTS.md`](./AGENTS.md)

### 2026-05-13 — High Cloud Model: Planning Only
**Decision:** The high cloud model must never write code, run commands, or execute tests. Its sole responsibility is plan maintenance and decomposition.  
**Rationale:** The high cloud model is the most expensive tier. Using it only for planning (which requires deep reasoning) and never for execution (which can be delegated) minimizes cost while preserving reasoning quality.

### 2026-05-13 — 2x Decomposition Rule
**Decision:** When the medium local model fails on a step, the low cloud model must perform 2x decomposition (split into two sub-steps) and retry with the medium local model before executing directly.  
**Rationale:** Prevents premature escalation to the low cloud model, which is more expensive than the medium local model. Forces an intermediate decomposition attempt that often succeeds without requiring the more expensive tier.

### 2026-05-13 — Low Cloud Model: Expanded Discretion in Local Model Assignment
**Decision:** The low cloud model may assign decomposed steps to any appropriate local model tier (low, medium, or high) based on task complexity. It is not bound to medium local by default.  
**Rationale:** Maximizes pool utilization and matches capacity to complexity. Simple config validation goes to low local; complex classifier logic goes to high local. See `AGENTS.md` for assignment guidelines.

### 2026-05-13 — Anti-Hallucination Safeguards: Test Evidence Required
**Decision:** Local models must provide test command output and file diffs with every success claim. The low cloud model acts as a verifier by re-running tests independently. No success claim is valid without confirmed green tests.  
**Rationale:** Local models are prone to hallucinating success. Test evidence and independent verification prevent broken code from being accepted. See `AGENTS.md` for the verifier protocol and report templates.

### 2026-05-13 — Local Models: Execution Only, No Self-Decomposition
**Decision:** Local models must not think, decompose, or replan beyond the scope of the task they have been given. If they encounter an issue they cannot resolve within the task boundary, they must return it to the low cloud model for reassignment, further decomposition, or direct execution.  
**Rationale:** Prevents inconsistent decomposition logic across tiers. Keeps local models focused on execution and performance. The low cloud model is the single point of orchestration intelligence.

### 2026-05-13 — Local Node Recovery via Playbook-Executor
**Decision:** If a lab node in the pool fails (crash, OOM, unresponsive), the low cloud model dispatches a low-capacity lab node to run the appropriate playbook-executor recovery playbook to restore the node.  
**Rationale:** Maintains pool health automatically without manual intervention. Uses existing playbook-executor infrastructure.

### 2026-05-13 — High-Frequency Decomposition Detection
**Decision:** If the low cloud model finds that 2x decomposition occurs on more than 60% of tasks over a 10-minute rolling window, it engages deeper decomposition (3x–4x) before assigning work to local models.  
**Rationale:** High decomposition frequency indicates the high cloud model's initial decomposition is too coarse for current task complexity. Deeper pre-assignment decomposition reduces local model failure rate and avoids cascading retries. Alerts the user via the 5-minute health report.

### 2026-05-13 — 5-Minute Node Health Report
**Decision:** The low cloud model writes a node health report every 5 minutes to `wiki/operational/sessions/STATUS-KEYWORD-ROUTER-DEBUG-YYYY-MM-DD-HHMM.md`. The report includes active nodes, failed nodes, decomposition metrics, tasks in flight, and actionable alerts for manual user intervention.  
**Rationale:** Provides the user with regular, discoverable visibility into node health and decomposition trends. Enables manual intervention (e.g., reviewing task complexity, approving deeper decomposition) without requiring continuous monitoring.

---

## Session Notes

**Plan Owner:** High Cloud Model (`ollama-cloud/kimi-k2.6`) — planning and decomposition only; never executes.  
**Orchestrator:** Low Cloud Model (`ollama-cloud/qwen3.5:397b`) — routes steps, assigns to appropriate local tier, escalates via 2x decomposition, dispatches node recovery, executes only as last resort.  
**Primary Executor:** Medium Local Model (`ollama/gemma4:e4b`) — standard execution; writes stubs, implements, refactors, tests on Lab Node.  
**Secondary Executors:** Low Local (`qwen3.5:4b`) — simple tasks; High Local (`qwen3:8b`) — complex tasks. **Medium Cloud** (`deepseek-v4-pro`) — analysis only, never executes locally.  
**Anti-Hallucination:** Low cloud verifier re-runs all test claims before accepting completion.  
**Review required:** Yes — user must approve before any Phase execution.  
**Next action:** Await user review of this plan. Once approved, the high cloud model will decompose Phase 0 (B-KR-001) into local-model-sized steps and hand off to the low cloud model for orchestration.
