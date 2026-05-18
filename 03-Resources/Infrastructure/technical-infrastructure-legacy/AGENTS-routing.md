# Technical Infrastructure — Routing Reference
**For:** Medium/Hard tasks requiring full TI-011 context  
**Companion to:** `AGENTS.md` (lightweight) + `AGENTS-full.md` (complete)

## TI-011 Meta-Orchestration

The meta-orchestration framework routes prompts to the optimal (node, model) pair.

### Architecture

```
User Prompt
    ↓
classify_prompt.py → complexity (TRIVIAL/SIMPLE/MEDIUM/HARD)
    ↓
ti011_node_registry.py → best (node, model)
    ↓
Route via SSH / task-worker.sh
    ↓
Collect result → log: prompt_type, model, node, latency, tokens, cost
    ↓
Adaptive feedback loop
```

### Routing Rules

1. **Heuristic classification first** — <50ms, keyword-based
2. **LLM fallback** — If confidence < 0.75, run qwen3.5:4b locally (≤ 0.5s)
3. **Node-model lookup** — Query NodeRegistry for fastest node running appropriate model
4. **Capability filtering** — Vision → vision-capable models; tools → tools-capable models
5. **Cloud escalation** — Only when no local match or local failure
6. **Per sub-task** — If 4 of 5 sub-tasks succeed locally, only 1 goes to cloud

### Health-Aware Routing (TI-023)

| Orchestrator Status | Decompose On | Synthesize On |
|---------------------|-------------|---------------|
| healthy (RAM<80%) | Mac qwen3.5:4b | Mac gemma4:e4b |
| stressed (RAM 80-92%) | fnet3 qwen3:8b | Mac gemma4:e4b |
| critical (RAM>92%) | Cloud LOW | Cloud LOW |

### Node Capacity Reference

| Node | CPU | RAM | Models | Max Tokens |
|------|-----|-----|--------|-----------|
| fnet1/2/7 | i5-6400 | 15GB | qwen3.5:4b | 111,411 |
| fnet3-6 | i7-10710U | 31GB | qwen3.5:4b, qwen3:8b, gemma4:e4b | 27,852-111,411 |

## Keyword Router Extension

### Configuration Files

| File | Purpose | Priority |
|------|---------|----------|
| `.pi/keyword-router.json` | Project-level routes | **Highest** |
| `~/.pi/agent/keyword-router.json` | Global fallback | Medium |
| Built-in defaults | Hardcoded fallback | Lowest |

### Routes (from `.pi/keyword-router.json`)

| Route | Provider/Model | Keywords | Use For |
|-------|---------------|----------|---------|
| reasoning | ollama-cloud/qwen3.5:397b | analyze, evaluate, decompose, plan, verify | Complex analysis |
| structured | ollama/gemma4:e4b | log, reconcile, parse, format, ledger | Bookkeeping ops |
| monitoring | ollama/qwen3.5:4b | status, check, ping, health, monitor | Status checks |
| infrastructure | ollama/qwen3:8b | server, deploy, network, orchestration, task | Infra ops |
| trivial | ollama/qwen3.5:4b | trivial, ping, echo, list, format | Quick tasks |
| simple | ollama/qwen3:8b | write script, basic, bounded | Small scripts |
| medium | ollama/gemma4:e4b | multi-step, plan, design | Medium tasks |
| hard | ollama-cloud/kimi-k2.6 | novel, creative, deep dive, comprehensive | Complex tasks |

### Explicit Tags

```html
<!-- model: ollama/gemma4:e4b thinking: medium -->
<!-- model-route: reasoning -->
<!-- complexity: medium -->
```

## Extension Installation

```bash
# From GitHub (production)
pi install github:carlosfrias/pi-keyword-router

# Local development
pi install ../technical-infrastructure/extensions/pi-keyword-router
```

### Verification

```bash
# Check extension loaded
/keyword-route

# Check decomposition triggers
/keyword-route-decompose

# View routing log
/keyword-route-log
```

## Commands

| Command | Purpose |
|---------|---------|
| `/keyword-route` | Show routing status and history |
| `/keyword-route-off` | Disable automatic routing |
| `/keyword-route-on` | Re-enable automatic routing |
| `/keyword-route-decompose` | List decomposition triggers |
| `/keyword-route-log` | Show recent routing decisions |

## Data Sources

| File | Purpose | How Updated |
|------|---------|-------------|
| `lab-specs/node-configs/{node}/models.json` | Per-node model definitions | `generate-node-profiles.py` |
| `lab-specs/node-configs/{node}/model-router.json` | Per-node routing profiles | `generate-node-profiles.py` |
| `lab-specs/node-capacity-summary.json` | Node index | `generate-node-profiles.py` |
| `lab-specs/node-hardware/*.json` | Hardware inventory | `remote-detect.sh` |
| `lab-specs/node-benchmarks/*.json` | Benchmark results | `benchmark-lab.sh` |

## Performance Logging

Every routed prompt must log:
```json
{
  "timestamp": "2026-05-02T15:00:00Z",
  "prompt_type": "ansible_playbook_generation",
  "complexity": "MEDIUM",
  "node": "fnet6",
  "model": "gemma4:e4b",
  "latency_ms": 2847,
  "tokens_in": 450,
  "tokens_out": 128,
  "cost": 0,
  "adequate": true,
  "cloud_escalated": false
}
```
