# Prompt Engineering for Model Routing & Orchestration

**Version:** 1.0 (2026-05-03)  
**Applies to:** pi-keyword-router v1.0.1+  
**Purpose:** How to formulate prompts so the AI routes them to the right model, triggers decomposition, and engages the orchestration framework.

---

## Quick Reference

| You want... | Add these words | Or use this tag |
|-------------|---------------|-----------------|
| **Fastest / lightest** (qwen3.5:4b) | "check", "list", "status", "ping", "count" | `<!-- model: ollama/qwen3.5:4b -->` |
| **Coding / infra** (qwen3:8b) | "build", "script", "deploy", "ssh", "configure" | `<!-- model: ollama/qwen3:8b -->` |
| **Structured / default** (gemma4:e4b) | "format", "parse", "log", "reconcile" | `<!-- model: ollama/gemma4:e4b -->` |
| **Deep reasoning** (qwen3.5:397b-cloud) | "analyze", "evaluate", "compare", "research" | `<!-- model: ollama/qwen3.5:397b-cloud -->` |
| **Maximum capability** (kimi-k2.6:cloud) | "synthesize", "comprehensive", "novel", "cross-domain" | `<!-- model: ollama/kimi-k2.6:cloud -->` |
| **Force decomposition** | "decompose", "fan out", "multi-step", "distribute to nodes" | `<!-- complexity: hard -->` |
| **Force orchestration** | "across all nodes", "orchestrate", "parallel execution" | `<!-- model-route: infrastructure -->` |

---

## 1. How Routing Works (The Pipeline)

When you type a prompt, the router evaluates it in this order:

```
1. Explicit tags in prompt          ← YOU control this directly
2. Keyword inference                ← semantic words you choose
3. Auto-complexity heuristic        ← length + structure (fallback)
4. Default model                    ← gemma4:e4b
```

**The golden rule:** The router trusts **what you say** more than what it guesses. Use explicit tags or strong keywords.

---

## 2. Targeting Specific Models

### 2.1 By Explicit Tag (100% Reliable)

Insert a tag at the **very start** of your prompt. The router reads this first and skips all guessing.

**Available tags:**

```markdown
<!-- model: ollama/qwen3.5:4b -->
<!-- model: ollama/qwen3:8b -->
<!-- model: ollama/gemma4:e4b -->
<!-- model: ollama/qwen3.5:397b-cloud -->
<!-- model: ollama/kimi-k2.6:cloud -->
```

**Route tags:**

```markdown
<!-- model-route: trivial -->       → qwen3.5:4b
<!-- model-route: simple -->        → qwen3:8b
<!-- model-route: medium -->        → gemma4:e4b
<!-- model-route: hard -->          → kimi-k2.6:cloud
<!-- model-route: reasoning -->      → qwen3.5:397b-cloud
<!-- model-route: infrastructure -->  → qwen3:8b
<!-- model-route: monitoring -->     → qwen3.5:4b
```

**Example:**

```markdown
<!-- model: ollama/kimi-k2.6:cloud -->
Synthesize a comprehensive trading strategy that integrates technical analysis, 
macro indicators, and risk management across multiple asset classes.
```

→ **Guaranteed** to use kimi-k2.6:cloud regardless of prompt length or keywords.

---

### 2.2 By Keyword (Semantic Routing)

If you don't use tags, the router scans your prompt for **route keywords**. Multiple matching keywords from the same route strengthen the match.

#### Low / Fast Models (qwen3.5:4b)

| Route | Keywords |
|-------|----------|
| trivial | "check", "ping", "list", "show", "count", "status", "is online", "format", "sort", "indent", "simple check" |
| monitoring | "status", "health", "verify", "monitor", "report", "watch", "alert", "uptime", "latency", "connectivity" |

**Example prompt:**
```
Check the ollama status on all lab nodes and list which models are currently loaded.
```
→ Routes to **qwen3.5:4b** (monitoring route). Fast, lightweight.

---

#### Medium Models (qwen3:8b, gemma4:e4b)

| Route | Keywords |
|-------|----------|
| simple | "write script", "basic", "straightforward", "bounded", "1-2 steps" |
| infrastructure | "deploy", "configure", "ssh", "ansible", "network", "server", "orchestrate", "decompose", "fan out", "distribute", "node", "cluster", "pipeline", "playbook", "wiring" |
| structured | "format", "parse", "log", "reconcile", "ledger", "beancount", "validate", "compute", "tabulate", "extract", "transform" |

**Example prompt:**
```
Write a bash script that deploys the monitoring agent to all 7 lab nodes using Ansible.
```
→ Routes to **qwen3:8b** (infrastructure + simple). Good for coding tasks.

---

#### High / Cloud Models (kimi-k2.6:cloud, qwen3.5:397b-cloud)

| Route | Keywords |
|-------|----------|
| reasoning | "analyze", "evaluate", "assess", "compare", "research", "strategize", "predict", "forecast", "backtest", "signal", "verify", "decomposer", "verifier" |
| hard | "synthesize", "comprehensive", "cross-domain", "creative", "novel", "deep dive", "mission-critical", "holistic", "systemic" |

**Example prompt:**
```
Analyze the correlation between VIX spikes and our portfolio drawdowns. 
Evaluate whether current position sizing is adequate and recommend adjustments.
```
→ Routes to **qwen3.5:397b-cloud** (reasoning). Deep analytical work.

**Example prompt:**
```
Synthesize a comprehensive framework that integrates our existing 
meta-orchestration pipeline with the new sub-agent system. 
This is a cross-domain integration spanning technical infrastructure, 
position management, and market research domains.
```
→ Routes to **kimi-k2.6:cloud** (hard). Maximum capability needed.

---

### 2.3 Keyword Amplification

Using **2+ keywords from the same route** strengthens the match and overrides length-based classification:

```
"Synthesize [a comprehensive] analysis..."
     ↑hard      ↑hard
→ Hard route (kimi-k2.6:cloud) — 2 hard keywords

"Analyze and evaluate the market signals..."
     ↑reasoning  ↑reasoning
→ Reasoning route (qwen3.5:397b-cloud) — 2 reasoning keywords

"Decompose and orchestrate across all nodes..."
     ↑infra    ↑infra          ↑infra
→ Infrastructure route (qwen3:8b) — 3 infrastructure keywords
```

---

## 3. Triggering Decomposition

Decomposition happens automatically when the classifier detects **MEDIUM or HARD** complexity. You can force this with:

### 3.1 Complexity Keywords

| Complexity | Trigger Words | What Happens |
|------------|---------------|--------------|
| MEDIUM | "multi-step", "coordinate", "plan", "design", "3-5 steps" | Task broken into 3-5 sub-tasks, distributed to lab nodes |
| HARD | "comprehensive", "cross-domain", "creative", "novel", "deep dive", "mission-critical" | Task broken into 5+ sub-tasks, may use recursive decomposition |

### 3.2 Explicit Complexity Tag

```markdown
<!-- complexity: medium -->
Plan a multi-step deployment: first backup configs, then update 
software, then verify services, then document changes.
```
→ Forces MEDIUM classification → decomposition trigger written → watcher distributes sub-tasks.

```markdown
<!-- complexity: hard -->
Comprehensive audit of all 7 domains — check every AGENTS.md, 
every BACKLOG.md, every PLAN file, and produce a consolidated status dashboard.
```
→ Forces HARD classification → recursive decomposition → distributed to multiple nodes.

### 3.3 Multi-Domain Decomposition

The strongest decomposition trigger: **spanning multiple domains in one prompt**.

```
Create a unified system that:
1. Monitors position risk (position-management)
2. Generates market signals (market-research)
3. Logs trades to ledger (bookkeeping)
4. Deploys on lab nodes (technical-infrastructure)
```
→ Detected as multi-domain → HARD → decomposed into domain-specific sub-tasks → each sent to appropriate nodes.

---

## 4. Engaging the Orchestration Framework

### 4.1 What Triggers Orchestration

The framework engages when ALL of these are true:

1. **Complexity is MEDIUM or HARD**
2. **Task touches ≥2 domains** OR **requires ≥3 sub-tasks**
3. **Lab nodes are online** (health check passes)

### 4.2 Orchestration Keywords

| Trigger | Effect |
|---------|--------|
| "decompose", "fan out" | Writes decomposition trigger to pending/ |
| "distribute", "orchestrate" | Signals node dispatch needed |
| "across all nodes", "on every node" | Multi-node execution |
| "parallel", "concurrent" | Parallel dispatch to multiple nodes |
| "collect results", "synthesize" | Post-execution result aggregation |

### 4.3 Complete Orchestration Example

```markdown
<!-- complexity: hard -->
Decompose this comprehensive task:
1. Analyze our current model routing performance from the logs
2. Identify which prompt types consistently fail on local models
3. Update the classifier's keyword lists based on findings
4. Test the updated classifier with 10 sample prompts
5. Document the changes in the wiki
6. Commit and push the changes to the repo

Distribute sub-tasks to available lab nodes. 
Collect results and synthesize a final report.
```

**What happens:**
1. Router: HARD → kimi-k2.6:cloud (for decomposition)
2. Decomposer: Breaks into 6 sub-tasks
3. Node matcher: Assigns each sub-task to best node based on model availability
4. Watcher: Dispatches via `submit_task.py --node {node} --file {task.json}`
5. Execution: Sub-tasks run in parallel on fnet3, fnet4, fnet5, etc.
6. Collection: Results pulled back to orchestrator
7. Synthesis: Final report generated (possibly on cloud model if complex)

---

## 5. Prompt Templates by Use Case

### 5.1 Quick Check / Status
```
Check if fnet3 is online and list loaded ollama models.
```
→ **qwen3.5:4b** — trivial, no decomposition.

### 5.2 Single Script / Config
```
Write a Python script that validates our router configuration 
against the keyword-router.json schema.
```
→ **qwen3:8b** — simple coding task.

### 5.3 Analysis / Evaluation
```
Analyze the decomposition pipeline latency from the logs. 
Identify bottlenecks and recommend optimizations.
```
→ **qwen3.5:397b-cloud** — reasoning route.

### 5.4 Multi-Step Infrastructure
```
Multi-step task: Update the decompose-watcher service on all lab nodes,
restart the daemon, verify it's running, and report status.
```
→ **qwen3:8b** or **gemma4:e4b** — infrastructure + medium complexity → decomposition triggered.

### 5.5 Cross-Domain Creative Work
```
Synthesize a comprehensive trading desk architecture that integrates:
- Real-time market data feeds (market-research)
- Automated position sizing with risk limits (position-management)
- Trade logging and P&L reconciliation (bookkeeping)
- Multi-node model orchestration (technical-infrastructure)

Design the system, identify integration points, and create implementation phases.
```
→ **kimi-k2.6:cloud** — hard + 4 domains → recursive decomposition.

---

## 6. Anti-Patterns (What NOT to Do)

| Anti-Pattern | Result | Fix |
|--------------|--------|-----|
| "Do we have any...?" | Trivial route (qwen3.5:4b) | Add keywords: "Analyze and evaluate which..." |
| Very short prompt (< 20 words) | Length-classified as trivial | Expand with context or use explicit tag |
| Mixing keywords from different routes | Highest-scoring route wins | Focus on words from your target route |
| "Check but also analyze deeply" | Conflicting signals — may default | Use explicit tag or split into separate prompts |
| No keywords, no tags | Defaults to gemma4:e4b | Add relevant keywords from target route |

---

## 7. Verification

After sending a prompt, verify routing in the TUI:

```
🔍 → ollama/kimi-k2.6:cloud (hard)
```

Or check the routing log:
```bash
python3 technical-infrastructure/scripts/performance_logger.py --list
```

---

## 8. Related Documentation

- `ROUTING-GAP-ANALYSIS-2026-05-03` — How the keyword-priority fix works
- [PLAN-2026-05-01-1645.md](/technical-infrastructure/operational/planning/PLAN-2026-05-01-1645) — Meta-orchestration architecture
- [PLAN-2026-05-03-1930-TI023-AUTO-DECOMPOSE-NODE-DISPATCH.md](/technical-infrastructure/operational/planning/PLAN-2026-05-03-1930-TI023-AUTO-DECOMPOSE-NODE-DISPATCH) — Decomposition pipeline
- [PI-Keyword-Router README](https://github.com/carlosfrias/pi-keyword-router/blob/main/README.md) — Extension documentation

---

## Changelog

| Date | Version | Change |
|------|---------|--------|
| 2026-05-03 | 1.0 | Initial — documents pi-keyword-router v1.0.1 keyword-priority routing |
