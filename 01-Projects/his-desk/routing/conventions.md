# Conventions & Model Routing

**Section ID:** conventions  
**Size:** ~2KB  
**LOD:** Low  
**Purpose:** Working conventions, model routing table, and default execution patterns for his-desk.

---

## [S-TIGHT]

All timestamps US Eastern, dates YYYY-MM-DD, scripture refs in standard format (Book Chapter:Verse). Default model is gemma4:e4b. Use decomposer for multi-step tasks. Verification failures re-run on cloud.

---

## Working Conventions [LOD: Low]

| Rule | Convention |
|------|-----------|
| Timezone | US Eastern (America/New_York) |
| Date format | YYYY-MM-DD |
| Scripture references | Book Chapter:Verse (e.g., John 3:16) |
| Output style | Concise and actionable |
| Uncertainty | Ask — do not assume |

## Model Routing [LOD: Medium]

| Route | Model | Triggers |
|-------|-------|----------|
| ultra-reasoning | ollama/kimi-k2.6 | think deeply, comprehensive exegesis |
| reasoning | ollama/qwen3.5:397b | analyze, evaluate, decide, research, plan |
| coding | ollama/deepseek-v4-pro | code, implement, develop, debug |
| vision | ollama/qwen3-vl:235b | image, chart, visual |
| structured | ollama/gemma4:e4b | log, parse, format |
| (default) | ollama/gemma4:e4b | — |

## Default Execution Pattern [LOD: Medium]

| Task Complexity | Default Action | Override |
|-----------------|---------------|----------|
| Single turn, well-scoped | Execute directly via model router | User specifies model |
| Multi-step or complex | `/run decomposer` → local execution → `/run verifier` | User explicitly says "use cloud" |
| Verification fails | Re-run failing sub-task only on cloud | — |

**Model selection rule:** Match the task's dominant action to the model routing table. If multiple actions are present, use the reasoning-tier model. Never escalate to a higher-cost model without explicit trigger.

---

*See [domains.md](domains.md) for domain routing.*  
*See [workspace.md](workspace.md) for directory layout and cross-references.*