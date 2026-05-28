# Model Routing

**Section ID:** model-routing  
**Size:** ~1.2KB  
**LOD:** Low  
**Purpose:** Map task types to local Ollama models for cost-optimized execution.

---

## [S-TIGHT]

Route tasks to the correct model by keyword trigger. Default is gemma4:e4b. Do not manually pick models — let the model router and decomposer decide.

---

## Model Routing Table

| Route | Model | Triggers |
|-------|-------|----------|
| ultra-reasoning | ollama/kimi-k2.6 | think deeply, comprehensive, thorough |
| reasoning | ollama/qwen3.5:397b | analyze, evaluate, decide, research, plan |
| coding | ollama/deepseek-v4-pro | code, implement, develop, debug |
| vision | ollama/qwen3-vl:235b | image, screenshot, chart, visual |
| structured | ollama/gemma4:e4b | log, reconcile, parse, format, ledger |
| monitoring | ollama/qwen3.5:4b | status, check, ping, health, monitor |
| infrastructure | ollama/qwen3:8b | server, deploy, network, ansible, node, orchestration |
| (default) | ollama/gemma4:e4b | — |

---

## Default Execution Pattern [LOD: Low]

| Task Complexity | Default Action | Override |
|-----------------|---------------|----------|
| Single turn, well-scoped | Execute directly via model router | User specifies model |
| Multi-step or complex | `/run decomposer` → local execution → `/run verifier` | User explicitly says "use cloud" |
| Verification fails | Re-run failing sub-task only on cloud | — |

**Rule:** Do not manually pick models. Let the model router and decomposer make routing decisions.

**Reference:** See `.pi/APPEND_SYSTEM.md` for the full cost-optimized execution framework.

---

*Next: For project-level routing, load [project-map.md](./project-map.md). For execution rules, load [execution-and-skills.md](./execution-and-skills.md).*