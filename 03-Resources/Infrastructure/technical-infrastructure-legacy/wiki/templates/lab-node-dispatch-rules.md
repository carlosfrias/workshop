# Lab Node Dispatch Rules

**Template ID:** COMP-014  
**Extracted from:** `1-PLAN.md` Section "Lab Node Dispatch Rules"  
**Use in:** Any plan that dispatches work from an orchestrator to a pool of lab nodes.

---

## Node Capacity Reference

| {{NODE_COL}} | {{CPU_COL}} | {{RAM_COL}} | {{SAFE_CAPACITY_COL}} | {{MODELS_COL}} | {{ASSIGN_COL}} |
|------|-----|-----|--------------|-----------------|-------------|
| {{NODE_1}} | {{NODE_1_CPU}} | {{NODE_1_RAM}} | {{NODE_1_CAPACITY}} | {{NODE_1_MODELS}} | {{NODE_1_ASSIGN}} |
| {{NODE_2}} | {{NODE_2_CPU}} | {{NODE_2_RAM}} | {{NODE_2_CAPACITY}} | {{NODE_2_MODELS}} | {{NODE_2_ASSIGN}} |
| {{NODE_3}} | {{NODE_3_CPU}} | {{NODE_3_RAM}} | {{NODE_3_CAPACITY}} | {{NODE_3_MODELS}} | {{NODE_3_ASSIGN}} |
| {{NODE_4}} | {{NODE_4_CPU}} | {{NODE_4_RAM}} | {{NODE_4_CAPACITY}} | {{NODE_4_MODELS}} | {{NODE_4_ASSIGN}} |
| {{NODE_5}} | {{NODE_5_CPU}} | {{NODE_5_RAM}} | {{NODE_5_CAPACITY}} | {{NODE_5_MODELS}} | {{NODE_5_ASSIGN}} |
| {{NODE_6}} | {{NODE_6_CPU}} | {{NODE_6_RAM}} | {{NODE_6_CAPACITY}} | {{NODE_6_MODELS}} | {{NODE_6_ASSIGN}} |
| {{NODE_7}} | {{NODE_7_CPU}} | {{NODE_7_RAM}} | {{NODE_7_CAPACITY}} | {{NODE_7_MODELS}} | {{NODE_7_ASSIGN}} |

**Reference:** [`{{NODE_CAPACITY_MAP}}`]({{NODE_CAPACITY_MAP_PATH}})

## Orchestrator Dispatch Protocol

The **{{ORCHESTRATOR_ROLE}}** (`{{LOW_CLOUD_MODEL}}`) runs on the **Orchestrator Node** ({{ORCHESTRATOR_OS}}). It does **not** execute code or tests itself. Instead, it:

1. **Selects the target lab node** based on the assigned model tier and current node health.
2. **Dispatches the task via `{{PRIMARY_DISPATCH}}`** to the selected lab node's named session.
3. **Monitors execution** by polling the lab node for status and test output via intercom.
4. **Collects test evidence** (output, diffs, logs) from the lab node before accepting completion.

**{{PRIMARY_DISPATCH}} Dispatch (Primary)**
```typescript
// {{ORCHESTRATOR_ROLE}} selects node (e.g., {{EXAMPLE_NODE}} for {{EXAMPLE_MODEL}} task)
// Dispatches via {{PRIMARY_DISPATCH}} to the lab node's named session
intercom({
  action: "ask",
  to: "{{EXAMPLE_NODE}}",
  message: "Step {{EXAMPLE_STEP_ID}}: {{EXAMPLE_TASK}}"
})
```

**{{FALLBACK_DISPATCH}} Dispatch (Fallback — if {{PRIMARY_DISPATCH}} is not responding)**
```bash
ssh -o ConnectTimeout={{TIMEOUT_SEC}} {{EXAMPLE_NODE}} "ollama ps && echo OK"
ssh {{EXAMPLE_NODE}} "cd {{EXAMPLE_WORKSPACE_PATH}} && npm test -- {{EXAMPLE_TEST_PATH}}"
```

**Result Collection:**
```bash
# {{ORCHESTRATOR_ROLE}} collects test output from lab node
ssh {{EXAMPLE_NODE}} "cat {{EXAMPLE_LOG_PATH}}"
ssh {{EXAMPLE_NODE}} "cd {{EXAMPLE_WORKSPACE_PATH}} && git diff --stat"
```

## Node Selection Algorithm

1. **Determine required model** from the step's `recommended_model` (e.g., `{{EXAMPLE_MODEL}}`).
2. **Filter nodes** that have the model installed (from {{NODE_CAPACITY_MAP}}).
3. **Check node health** — query the node's ollama status and available RAM.
4. **Select least-loaded qualifying node** — prefer the node with the most free RAM among those that have the required model.
5. **If no node has the required model** — dispatch {{PLAYBOOK_EXECUTOR}} to pull the model on the healthiest available node, then assign.
6. **If all qualifying nodes are saturated** — escalate to the next model tier (from {{NODE_CAPACITY_MAP}} routing matrix) or invoke {{MEDIUM_CLOUD_MODEL}} for deeper decomposition.

## Health Check Before Dispatch

Before every dispatch, the {{ORCHESTRATOR_ROLE}} must verify the target node is responsive via **{{PRIMARY_DISPATCH}}** (primary) or {{FALLBACK_DISPATCH}} (fallback):

```bash
# Primary: {{PRIMARY_DISPATCH}} health check
intercom({ action: "ask", to: "{{HEALTH_CHECK_NODE}}", message: "echo OK" })
# Expected: "OK" reply within {{HEALTH_TIMEOUT}} seconds

# Fallback: {{FALLBACK_DISPATCH}} health check
ssh -o ConnectTimeout={{TIMEOUT_SEC}} {{HEALTH_CHECK_NODE}} "ollama ps && echo OK" || echo "NODE_UNREACHABLE"
```

If the node is unreachable:
1. Log the failure.
2. Mark node as offline in the health report.
3. Select the next best node.
4. If no nodes are available, invoke node recovery via {{PLAYBOOK_EXECUTOR}}.

## Acceptance Test Execution on Lab Node

All acceptance tests are executed via **{{PRIMARY_DISPATCH}} dispatch** to a Lab Node:

```typescript
// Orchestrator dispatches via intercom to lab node
intercom({
  action: "ask",
  to: "{{EXAMPLE_NODE}}",
  message: "Run acceptance suite: cd {{EXAMPLE_WORKSPACE_PATH}} && npm test -- --suite=acceptance"
})

// Results are collected via intercom reply or file transfer
ssh {{EXAMPLE_NODE}} "cat {{EXAMPLE_RESULTS_PATH}}"
```

Results are written to:
- `{{RESULTS_OUTPUT_PATH}}`

---

## Placeholder Reference

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{NODE_COL}}` | Node column header | `Node` |
| `{{CPU_COL}}` | CPU column header | `CPU` |
| `{{RAM_COL}}` | RAM column header | `RAM` |
| `{{SAFE_CAPACITY_COL}}` | Capacity column header | `Safe Capacity` |
| `{{MODELS_COL}}` | Models column header | `Installed Models` |
| `{{ASSIGN_COL}}` | Assignment column header | `Assign When` |
| `{{NODE_1}}`–`{{NODE_7}}` | Node names | `fnet1`–`fnet7` |
| `{{NODE_1_CPU}}`–`{{NODE_7_CPU}}` | Node CPU specs | `i5-6400 / 4 cores / 15GB` |
| `{{NODE_1_RAM}}`–`{{NODE_7_RAM}}` | Node RAM | `12.5GB` |
| `{{NODE_1_CAPACITY}}`–`{{NODE_7_CAPACITY}}` | Safe model capacity | `` `qwen3.5:4b`, `qwen3:8b` `` |
| `{{NODE_1_MODELS}}`–`{{NODE_7_MODELS}}` | Installed models | `Low/medium complexity tasks` |
| `{{NODE_1_ASSIGN}}`–`{{NODE_7_ASSIGN}}` | Assignment criteria | `Low/medium complexity tasks` |
| `{{NODE_CAPACITY_MAP}}` | Node capacity map filename | `node-capacity-map.md` |
| `{{NODE_CAPACITY_MAP_PATH}}` | Path to capacity map | `../../../reference/node-capacity-map.md` |
| `{{ORCHESTRATOR_ROLE}}` | Orchestrator role name | `low cloud orchestrator` |
| `{{LOW_CLOUD_MODEL}}` | Orchestrator model | `qwen3.5:397b-cloud` |
| `{{ORCHESTRATOR_OS}}` | Orchestrator OS | `Mac` |
| `{{PRIMARY_DISPATCH}}` | Primary dispatch method | `pi-intercom` |
| `{{FALLBACK_DISPATCH}}` | Fallback dispatch method | `SSH` |
| `{{EXAMPLE_NODE}}` | Example node in code | `fnet3` |
| `{{EXAMPLE_MODEL}}` | Example model in code | `gemma4:e4b` |
| `{{EXAMPLE_STEP_ID}}` | Example step ID | `B-KR-001-UNIT-001` |
| `{{EXAMPLE_TASK}}` | Example task description | `Write failing test stub...` |
| `{{EXAMPLE_WORKSPACE_PATH}}` | Example workspace path | `~/workshop/technical-infrastructure/packages/pi-keyword-router` |
| `{{EXAMPLE_TEST_PATH}}` | Example test path | `test/unit/kill-switch.test.ts` |
| `{{EXAMPLE_LOG_PATH}}` | Example log path | `~/workshop/technical-infrastructure/packages/pi-keyword-router/test-output.log` |
| `{{EXAMPLE_RESULTS_PATH}}` | Example results path | `~/workshop/technical-infrastructure/packages/pi-keyword-router/test-results.jsonl` |
| `{{TIMEOUT_SEC}}` | Connection timeout seconds | `5` |
| `{{HEALTH_CHECK_NODE}}` | Node for health check example | `{node}` |
| `{{HEALTH_TIMEOUT}}` | Health check timeout | `10` |
| `{{PLAYBOOK_EXECUTOR}}` | Recovery tool | `playbook-executor` |
| `{{MEDIUM_CLOUD_MODEL}}` | Model for deeper decomposition | `deepseek-v4-pro` |
| `{{RESULTS_OUTPUT_PATH}}` | Where results are written | `technical-infrastructure/wiki/products/keyword-router-debug/TEST-RESULTS-YYYY-MM-DD-HHMM.md` |
