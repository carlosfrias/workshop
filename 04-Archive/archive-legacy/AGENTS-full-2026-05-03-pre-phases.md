# Trading Desk — Full Documentation

Complete conventions, model routing details, and configuration reference.
Load this file for MEDIUM/HARD tasks or when orchestration is active.

---

## Conventions (Complete)

- All timestamps in US Eastern / America/New_York
- All date formats: YYYY-MM-DD
- All monetary values in USD unless stated otherwise
- Keep outputs concise and actionable
- When in doubt, ask — do not assume

## Domain Activation Check — MUST OCCUR BEFORE ANY WORK

Before proceeding with any task, reflect on **which domain keywords in the user's prompt activate which domain**. This check is **mandatory** — no work proceeds until a domain is clearly activated or explicitly chosen.

### Step 1: Extract Trigger Words
Scan the user's prompt for any keywords that match the **Domain Agent File Routing** table below. List all matches found.

### Step 2: Verify Activation
- **Does the prompt contain one or more keywords that map to exactly ONE domain?** → Proceed with that domain. Read its AGENTS.md file before any work.
- **Does the prompt contain NO matching keywords?** → The domain is **not activated**. See [No Match Resolution](#no-match-resolution).
- **Does the prompt contain keywords that map to MULTIPLE domains?** → The domain is **ambiguously activated**. See [Ambiguity Resolution](#ambiguity-resolution).

### Step 3: Confirm Before Proceeding
State the detected keywords and the activated domain clearly.

### No Match Resolution

If **no keywords** from the prompt match any domain in the Domain Agent File Routing table:

1. **Present the trigger words** from the prompt to the user:
   > "I did not find clear domain activation keywords in your prompt. The words that appeared most relevant were: [list potential keywords]. None of these match the domains I know about: [list available domains]. Which domain should I activate?"

2. **Offer the available domains** with examples:
   - `technical-infrastructure` — servers, APIs, orchestration, deployment
   - `bookkeeping` — trade logging, reconciliation, P&L
   - `market-research` — research, analysis, signals, backtesting
   - `position-management` — positions, orders, risk, allocation
   - `wiki` — documentation, planning, recommendations

3. **Add new trigger words** — If the user specifies a domain, ask: _"Should the keywords [words] be added to activate [domain] in future prompts?"_ Then update the Domain Agent File Routing table.

### Ambiguity Resolution

If the prompt contains keywords from **multiple domains**:

1. **Present the ambiguity** to the user clearly:
   > "Trigger words activate multiple domains:
   > - 'orchestration, routing' → technical-infrastructure
   > - 'P&L, reconciliation' → bookkeeping
   > - 'portfolio, risk' → position-management
   > Which domain should take precedence for this task?"

2. **Do not proceed** until the user specifies one domain.

3. **Record the resolution** — After the user clarifies, note which keywords caused the ambiguity so future prompts can be disambiguated.

### Hard Rule

**No work proceeds without clear domain activation.** This means:
- No file reads outside the activated domain
- No code changes
- No script execution
- No model routing decisions
- **Until** a domain is clearly activated and its AGENTS.md is read.

The only exception: the user explicitly says `"Proceed regardless"` or provides a direct override.

---

## Model Routing (Detailed)

The `pi-keyword-router` extension automatically routes prompts to the appropriate model based on content keywords and domain routing. The configuration is in `~/.pi/agent/model-router.json` (global) with optional project overrides in `.pi/model-router.json`.

### Route Reference

| Route | Provider | Model | Thinking | Priority | Key Triggers |
|-------|----------|-------|----------|----------|---------------|
| ultra-reasoning | ollama | kimi-k2.6 (1042B) | high | 2 | think deeply, comprehensive, thorough, mission-critical, deep dive |
| reasoning | ollama | qwen3.5:397b (397B) | medium | 1 | analyze, evaluate, decide, research, signal, risk, plan, decompose |
| coding | ollama | deepseek-v4-pro (158B) | medium | 0 | code, implement, develop, program, script, debug code |
| vision | ollama | qwen3-vl:235b (235B) | medium | 0 | image, screenshot, chart, diagram, visual, analyze chart |
| structured | ollama | gemma4:e4b (32B) | off | 0 | log, reconcile, parse, format, ledger, balance |
| monitoring | ollama | qwen3.5:4b (4B) | off | 0 | status, check, ping, health, monitor, report |
| infrastructure | ollama | qwen3:8b (8B) | off | 0 | server, connect, deploy, dns, network, troubleshoot, ansible, ollama, model, node, cluster, orchestration, orchestrate, route, routing, classify, classification, complexity, decompose, decomposition, fan out, distribute, distribution, workload, queue, worker, task, submit, collect, sync, artifact, performance, latency, framework, meta- |
| (default) | ollama | gemma4:e4b (32B) | off | — | No matching keywords |

### Domain-to-Route Mapping

| Domain keywords | Auto-routes to route |
|----------------|---------------------|
| market-research, position-management | reasoning |
| bookkeeping | structured |
| position-monitor | monitoring |
| technical-infrastructure | infrastructure |
| decomposer, verifier | reasoning |

### Explicit Routing

```html
<!-- model-route: ultra-reasoning -->
<!-- model-route: reasoning -->
<!-- model-route: coding -->
<!-- model: ollama/kimi-k2.6 thinking: high -->
```

Commands: `/model-route` (status), `/model-route-off` (disable), `/model-route-on` (enable)

### Configuration Files

| File | Location | Purpose |
|------|----------|---------|
| Model Router (global) | `~/.pi/agent/model-router.json` | Keyword routing config |
| Model Router (project) | `.pi/model-router.json` | Project-level overrides |
| Models | `~/.pi/agent/models.json` | Model provider & capability definitions |
| Cloud Cache | `~/.pi/agent/cache/ollama-models.json` | Cloud model capabilities |

**See `technical-infrastructure/wiki/model-routing-guide.md` for full documentation.**

---

## Domain Agent File Routing

| Task keywords | Read this domain's AGENTS.md |
|----------|---------------|
| servers, APIs, connectivity, latency, infrastructure, deployment, monitoring, orchestration, orchestrate, route, routing, classify, classification, complexity, decompose, decomposition, fan out, distribute, distribution, workload, queue, queues, worker, workers, task, tasks, submit, collect, sync, synchronize, artifact, artifacts, node, nodes, cluster, meta-, framework, performance, ansible, script, scripts, bash, playbook, playbooks | `./technical-infrastructure/AGENTS.md` |
| trade logging, reconciliation, P&L, accounting, balances, fees, settlement | `./bookkeeping/AGENTS.md` |
| research, analysis, signals, backtesting, data, indicators, sentiment | `./market-research/AGENTS.md` |
| positions, orders, risk, allocation, sizing, exits, stops, portfolio | `./position-management/AGENTS.md` |
| position status, monitoring, risk limit checks, portfolio state | `./position-management/AGENTS.md` (use `position-monitor` agent) |
| wiki, documentation, research, analysis | `./wiki/AGENTS.md` |
| network troubleshooting, node offline, driver issue, r8169, can't reach internet | `./technical-infrastructure/prompts/network-troubleshooting.md` |

After reading the domain file, follow its instructions for the task.
