# Session Notes

**Template ID:** COMP-011  
**Extracted from:** `1-PLAN.md` Section "Session Notes"  
**Use in:** Any plan document footer that records session metadata and next actions.

---

**Plan Owner:** {{PLAN_OWNER}} — planning and decomposition only; never executes.  
**Orchestrator:** {{ORCHESTRATOR}} — routes steps, assigns to appropriate local tier, escalates via {{DECOMP_MULTIPLIER}}x decomposition, dispatches node recovery, executes only as last resort.  
**Primary Executor:** {{PRIMARY_EXECUTOR}} — standard execution; writes stubs, implements, refactors, tests on Lab Node.  
**Secondary Executors:** {{SECONDARY_EXECUTORS}}. **Medium Cloud** ({{MEDIUM_CLOUD_MODEL}}) — analysis only, never executes locally.  
**Anti-Hallucination:** {{ANTI_HALLUCINATION}}.  
**Review required:** {{REVIEW_REQUIRED}}  
**Next action:** {{NEXT_ACTION}}

---

## Placeholder Reference

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{PLAN_OWNER}}` | Plan owner role and model | `High Cloud Model (ollama-cloud/kimi-k2.6)` |
| `{{ORCHESTRATOR}}` | Orchestrator role and model | `Low Cloud Model (ollama-cloud/qwen3.5:397b)` |
| `{{DECOMP_MULTIPLIER}}` | Decomposition factor on failure | `2` |
| `{{PRIMARY_EXECUTOR}}` | Primary execution model | `Medium Local Model (ollama/gemma4:e4b)` |
| `{{SECONDARY_EXECUTORS}}` | Other execution models | `Low Local (qwen3.5:4b) — simple tasks; High Local (qwen3:8b) — complex tasks` |
| `{{MEDIUM_CLOUD_MODEL}}` | Medium cloud model for analysis | `deepseek-v4-pro` |
| `{{ANTI_HALLUCINATION}}` | Anti-hallucination protocol | `Low cloud verifier re-runs all test claims before accepting completion` |
| `{{REVIEW_REQUIRED}}` | Whether user review is needed | `Yes — user must approve before any Phase execution.` |
| `{{NEXT_ACTION}}` | Next step for user or orchestrator | `Await user review of this plan. Once approved, the high cloud model will decompose Phase 0 into local-model-sized steps and hand off to the low cloud model for orchestration.` |
