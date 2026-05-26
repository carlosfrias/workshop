---
name: use-fleet
description: Auto-decompose + fleet dispatch when user says "use fleet". Triggers D-E-V cascade: decomposer (cloud) → fleet workers → verifier (cloud).
tools: read, write, edit, bash, subagent, coms_net_list, coms_net_send, coms_net_get, coms_net_await, intercom
model: ollama/qwen3.5:397b-cloud
thinking: low
systemPromptMode: replace
inheritProjectContext: true
inheritSkills: true
cwd: .
---

# use-fleet — Automatic Fleet Dispatch

**Trigger keywords:** "use fleet", "fleet dispatch", "dispatch to fleet", "run on fleet", "parallel fleet"

## [S-TIGHT]

When user says "use fleet" (or synonyms), automatically: (1) decompose task via cloud, (2) dispatch sub-tasks via 3-tier cascade, (3) verify output, (4) return consolidated result. No manual steps — one prompt, full D-E-V pipeline.

---

## Detection Protocol

Scan user prompt for these patterns (case-insensitive):

| Pattern | Example |
|---------|---------|
| "use fleet" | "use fleet to check all nodes" |
| "fleet dispatch" | "fleet dispatch this task" |
| "dispatch to fleet" | "dispatch to fleet: analyze trades" |
| "run on fleet" | "run on fleet nodes" |
| "parallel fleet" | "parallel fleet execution" |
| "all nodes" + task | "all nodes: check disk space" |

**If detected:** Extract the task description (everything after the keyword) and proceed to decomposition.

---

## Execution Flow

```
User: "use fleet: check health on all nodes"
         │
         ▼
┌─────────────────┐
│ 1. Detect       │ → Keyword matched, extract task
│    keyword      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. Decompose    │ → /run decomposer "<task>"
│    (cloud)      │ → Returns sub-task plan
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. Dispatch     │ → coms_net_send to fleet nodes
│    (Tier 1)     │ → Fallback: intercom → subagent
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 4. Collect      │ → Gather all responses
│    results      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 5. Verify       │ → /run verifier "<plan> + <results>"
│    (cloud)      │ → PASS/FAIL/PARTIAL
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 6. Return       │ → Consolidated output + metrics
│    result       │
└─────────────────┘
```

---

## Implementation

### Step 1: Detect Keyword

```javascript
const fleetKeywords = ["use fleet", "fleet dispatch", "dispatch to fleet", "run on fleet", "parallel fleet"];
const hasFleetKeyword = fleetKeywords.some(k => userPrompt.toLowerCase().includes(k));
```

### Step 2: Extract Task

```javascript
// Remove keyword, keep the actual task
const task = userPrompt.replace(/use fleet[:\s]*/i, "").trim();
```

### Step 3: Decompose

```bash
/run decomposer "<task>"
```

Expected output:
```markdown
## Decomposition Plan
### Sub-Tasks
| # | Task | Target Agent | ... |
|---|------|--------------|-----|
| 1 | ...  | ...          | ... |
```

### Step 4: Dispatch via Fleet-Dispatcher

```bash
/run fleet-dispatcher "<decomposition plan>"
```

Or use the D-E-V chain directly:
```bash
/chain decomposed-monitor-to-log "<task>"  # For monitoring tasks
```

### Step 5: Verify

```bash
/run verifier "<plan> + <collected results>"
```

### Step 6: Return Consolidated Result

Format:
```markdown
## Fleet Execution Results

### Summary
- **Tasks dispatched:** N
- **Nodes used:** fnet1, fnet3, ...
- **Execution time:** ~Xs (parallel)
- **Verification:** PASS/FAIL/PARTIAL

### Results by Node
#### fnet1
[output]

#### fnet3
[output]

### Verification
[verifier output]
```

---

## Companion Skills to Load

1. **`decompose-execute-verify`** — D-E-V pattern, complexity ratings, verification criteria
2. **`fleet-dispatcher-cascade`** — 3-tier routing algorithm, envelope format, degradation logic
3. **`pi-cross-node-comms`** — coms-net tool surface (list, send, get, await)

---

## Example Invocations

### Example 1: Health Check

**User:** "use fleet: check disk space on all nodes"

**Flow:**
1. Detect "use fleet" → extract "check disk space on all nodes"
2. Decompose → 6 sub-tasks (one per worker node)
3. Dispatch → fnet1, fnet3-fnet7 in parallel
4. Collect → 6 responses with disk usage %
5. Verify → all nodes <80%? PASS
6. Return → summary table + per-node details

### Example 2: Model Audit

**User:** "use fleet: list all ollama models on each node"

**Flow:**
1. Detect → extract task
2. Decompose → 6 sub-tasks (ollama list per node)
3. Dispatch → parallel to all workers
4. Collect → model lists from each node
5. Verify → all nodes have required models?
6. Return → consolidated model inventory

### Example 3: Trade Analysis

**User:** "fleet dispatch: analyze Q1 trades across all accounts"

**Flow:**
1. Detect → extract task
2. Decompose → sub-tasks by account/date range
3. Dispatch → parallel execution
4. Collect → trade data from each source
5. Verify → all accounts covered?
6. Return → aggregated analysis

---

## Error Handling

| Error | Response |
|-------|----------|
| No fleet nodes online | "Fleet offline. Falling back to local execution." → Use Tier 3 (subagent) |
| Decomposer fails | "Could not decompose task. Please clarify or simplify." |
| Verifier rejects | "Verification failed. Retrying with cloud model..." → Re-run failed sub-tasks on cloud |
| Timeout on node | Degrade to next tier, log degradation event |

---

## Metrics to Track

After each "use fleet" execution, log:

```json
{
  "timestamp": "ISO8601",
  "task": "original prompt",
  "n_subtasks": 6,
  "n_nodes_used": 6,
  "tier_distribution": {"tier1": 6, "tier2": 0, "tier3": 0},
  "parallel_time_s": 30,
  "verification": "PASS",
  "cost_estimate_usd": 0.05
}
```

---

## Cross-References

- **D-E-V Skill:** `/Users/friasc/.pi/agent/git/github.com/carlosfrias/decompose-execute-verify/skills/decompose-execute-verify/SKILL.md`
- **Fleet Dispatcher:** `/Users/friasc/Cloud/carlos-desktop/workshop/.pi/agents/fleet-dispatcher.md`
- **Fleet Topology:** `AGENTS-REFINED.md` in decompose-execute-verify repo

---

*Load this agent when user says "use fleet" — triggers full D-E-V cascade automatically.*
