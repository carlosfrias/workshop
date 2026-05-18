# Model Responsibility Matrix

**Template ID:** COMP-001  
**Extracted from:** `1-PLAN.md` Section "Model Responsibility"  
**Use in:** Any plan that routes work across model tiers and lab nodes.

---

## Responsibility Matrix

| Tier | Model | Role | Executes Code? | Typical Assignment |
|------|-------|------|---------------|-------------------|
| **High Cloud** | `{{HIGH_CLOUD_MODEL}}` | Plan Owner & Decomposer | **NO** — planning only | Complex architecture, plan updates, decomposition design |
| **Medium Cloud** | `{{MEDIUM_CLOUD_MODEL}}` | High-Frequency Decomposition Detection Assistant | **NO** — analysis only | Analyzes decomposition trends, recommends granularity adjustments, produces deeper decompositions when ratio > {{HIGH_FREQ_THRESHOLD}} |
| **Low Cloud** | `{{LOW_CLOUD_MODEL}}` | Orchestrator, Escalation Handler, Node Recovery Dispatcher | **YES** — last resort only | Orchestration, {{DECOMP_MULTIPLIER}}x decomposition, node recovery dispatch, direct execution when local pool exhausted |
| **High Local** | `{{HIGH_LOCAL_MODEL}}` | Complex Execution | **YES** | Complex classifier logic, multi-module refactoring, cloud escalation implementation |
| **Medium Local** | `{{MEDIUM_LOCAL_MODEL}}` | Standard Execution | **YES** | Standard test stub writing, implementation, integration wiring |
| **Low Local** | `{{LOW_LOCAL_MODEL}}` | Simple Execution | **YES** | Simple test stubs, config validation, log parsing, quick fixes |

**Execution Rule:** **Only local models (with `{{LOCAL_PREFIX}}` prefix) execute on Lab Nodes.** Cloud models (`{{CLOUD_PREFIX}}` prefix) never run locally — Medium Cloud does analysis only; Low Cloud orchestrates and dispatches to lab nodes via {{DISPATCH_METHOD}}. The Orchestrator Node ({{ORCHESTRATOR_OS}}) does not execute tests or write code.

---

## Decomposition & Escalation Flow

```
High Cloud Model ({{HIGH_CLOUD_MODEL}}) on Orchestrator ({{ORCHESTRATOR_OS}})
    │
    ├── Owns {{PLAN_FILE}}
    ├── Owns {{AGENTS_FILE}}
    └── Decomposes into local-model-sized steps
              │
              ▼
    Medium Cloud Model ({{MEDIUM_CLOUD_MODEL}}) on Orchestrator ({{ORCHESTRATOR_OS}})
        │
        ├── Monitors decomposition ratio (rolling {{WINDOW_MINUTES}}-min window)
        ├── When ratio > {{HIGH_FREQ_THRESHOLD}}: signals Low Cloud → engage deeper decomposition
        ├── Produces finer-grained decomposition recommendations
        └── Reports to High Cloud if ratio stays elevated > {{ESCALATION_MINUTES}} min
              │
              ▼
    Low Cloud Model ({{LOW_CLOUD_MODEL}}) on Orchestrator ({{ORCHESTRATOR_OS}})
        │
        ├── Reads {{AGENTS_FILE}}
        ├── Checks Medium Cloud signal (high-freq mode yes/no)
        ├── Assesses step complexity → Selects local model tier (low / medium / high)
        ├── Selects target lab node from {{NODE_CAPACITY_MAP}}
        ├── **Dispatches step via {{DISPATCH_METHOD}} to selected Lab Node**
        │
        │   Lab Node ({{NODE_POOL}})
        │       ├── Local Model loads ({{LOW_LOCAL_MODEL}} / {{MEDIUM_LOCAL_MODEL}} / {{HIGH_LOCAL_MODEL}})
        │       ├── Execution only — no thinking or decomposition beyond task scope
        │       ├── Writes failing test stubs (RED)
        │       ├── Implements to pass (GREEN)
        │       ├── Refactors
        │       └── Reports PASS / FAIL with test evidence back to Orchestrator
        │
        ├── **Collects test evidence from Lab Node via {{EVIDENCE_METHOD}}**
        ├── Verifies evidence before accepting completion
        │
        ├── If FAIL → performs {{DECOMP_MULTIPLIER}}x decomposition → Dispatches to Lab Node again
        │       │
        │       ├── Sub-step A → Lab Node → PASS/FAIL
        │       └── Sub-step B → Lab Node → PASS/FAIL
        │
        ├── If Lab Node fails → Dispatch {{PLAYBOOK_EXECUTOR}} recovery to spare node
        │
        └── If still failing after {{DECOMP_MULTIPLIER}}x decomposition:
                Low Cloud Model executes directly (last resort, still on cloud)
```

---

## Rules

**High Cloud Model:**
- Must Always: Own the plan, own `{{AGENTS_FILE}}`, decompose into local-model-sized steps, define acceptance criteria.
- Must Never: Execute code, write test stubs, modify source files, run commands on any node.

**Medium Cloud Model (`{{MEDIUM_CLOUD_MODEL}}`):**
- Must Always: Monitor decomposition ratio from session notes; when ratio > {{HIGH_FREQ_THRESHOLD}} over {{WINDOW_MINUTES}} min, produce deeper decomposition recommendations ({{DEEP_DECOMP_FACTOR}}x) and signal Low Cloud to engage high-frequency mode; report persistent elevation (> {{ESCALATION_MINUTES}} min) to High Cloud.
- Must Never: Execute code, directly modify source files, or skip notifying Low Cloud when high-frequency mode is warranted.

**Low Cloud Model:**
- Must Always: Orchestrate decomposed steps, **exercise discretion in model assignment** (low / medium / high local), monitor execution, perform {{DECOMP_MULTIPLIER}}x decomposition on failure, **dispatch {{PLAYBOOK_EXECUTOR}} for node recovery**, execute only as last resort, **respond to Medium Cloud high-frequency signals by engaging deeper decomposition**.
- Must Never: Modify the plan or `{{AGENTS_FILE}}` without high cloud approval, skip {{DECOMP_MULTIPLIER}}x decomposition, execute on Orchestrator Node, **ignore medium cloud high-frequency signals**.

**Local Models (All Tiers):**
- Must Always: **Execute only on Lab Nodes.** The orchestrator dispatches work via {{DISPATCH_METHOD}}; the local model loads on the lab node and performs the task. Focus on code, tests, and commands. Maintain performance. Write test stubs first (RED), then implement (GREEN), then refactor. Keep work in correct workspace. Run tests on the Lab Node. **Provide test evidence with every success claim.** Report results back to the orchestrator.
- Must Never: Modify the plan or `{{AGENTS_FILE}}`, orchestrate across steps, decide phase transitions, **claim success without passing tests**, **self-decompose or replan** (return to orchestrator instead). Execute on the Orchestrator Node ({{ORCHESTRATOR_OS}}).
- **On Failure or Uncertainty:** Return to orchestrator with step_id, exact reason, and request for reassignment / decomposition / direct execution. Never attempt independent decomposition.
- **Execution Location:** All file writes, test runs, and code changes occur on the Lab Node. The Orchestrator Node only dispatches commands and collects results.

For the full orchestration guide, see [`{{AGENTS_FILE}}`](./{{AGENTS_FILE}}).

---

## Placeholder Reference

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{HIGH_CLOUD_MODEL}}` | Premium cloud model for planning | `ollama-cloud/kimi-k2.6` |
| `{{MEDIUM_CLOUD_MODEL}}` | Standard cloud model for analysis | `ollama-cloud/deepseek-v4-pro` |
| `{{LOW_CLOUD_MODEL}}` | Cloud model for orchestration | `ollama-cloud/qwen3.5:397b` |
| `{{HIGH_LOCAL_MODEL}}` | High-capacity local model | `ollama/qwen3:8b` |
| `{{MEDIUM_LOCAL_MODEL}}` | Standard local model | `ollama/gemma4:e4b` |
| `{{LOW_LOCAL_MODEL}}` | Low-capacity local model | `ollama/qwen3.5:4b` |
| `{{LOCAL_PREFIX}}` | Prefix distinguishing local models | `ollama/` |
| `{{CLOUD_PREFIX}}` | Prefix distinguishing cloud models | `ollama-cloud/` |
| `{{DISPATCH_METHOD}}` | How orchestrator sends work to lab nodes | `SSH` or `pi-intercom` |
| `{{EVIDENCE_METHOD}}` | How evidence is collected | `SSH/SCP` |
| `{{ORCHESTRATOR_OS}}` | Orchestrator operating system | `Mac` |
| `{{NODE_POOL}}` | Available lab nodes | `fnet1–fnet7` |
| `{{NODE_CAPACITY_MAP}}` | Path to node capacity reference | `node-capacity-map.md` |
| `{{PLAN_FILE}}` | This plan's filename | `1-PLAN.md` |
| `{{AGENTS_FILE}}` | Domain agents file | `AGENTS.md` |
| `{{PLAYBOOK_EXECUTOR}}` | Recovery tool | `playbook-executor` |
| `{{WINDOW_MINUTES}}` | Decomposition monitoring window | `10` |
| `{{HIGH_FREQ_THRESHOLD}}` | Ratio threshold for high-frequency mode | `60%` |
| `{{ESCALATION_MINUTES}}` | Minutes before escalating to High Cloud | `20` |
| `{{DECOMP_MULTIPLIER}}` | Decomposition factor on failure | `2` |
| `{{DEEP_DECOMP_FACTOR}}` | Deeper decomposition factor | `3x–4x` |
