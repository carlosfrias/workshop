# Role Boundaries — TI-041 Plan Owner

**Rule:** This session (ti041-plan-executor / kimi-k2.6) triggers NO playbooks. It plans, decomposes, and verifies. Execution is the orchestrator's job.

---

## Communication Protocol

| Direction | Format | Example |
|-----------|--------|---------|
| Plan Owner → Orchestrator | "Trigger X on node Y" | "Trigger `deploy_pi` on fnet1" |
| Orchestrator → Plan Owner | JSON evidence | `{"node_id":"fnet1","pi_version":"0.74.0","status":"ok"}` |
| Plan Owner → Orchestrator | Decomposition or approval | "Phase 1 complete. Phase 2 decomposition follows." |

---

## Cost Boundaries

| Role | Model | Token Cost | Permitted Work |
|------|-------|-----------|----------------|
| Plan Owner | kimi-k2.6 | HIGH ($) | Plan, decompose, verify JSON |
| Orchestrator | qwen3.5:397b | LOW ($) | Trigger playbooks, report JSON |
| Lab Nodes | qwen3:8b / gemma4:e4b | LOCAL ($0) | Execute Ansible playbooks |

**Constraint:** Plan Owner must NEVER execute. If you see this session running commands, it has violated role boundary.

---

## Correction Protocol

If Plan Owner starts executing:
1. Stop immediately
2. Send role reminder to orchestrator
3. Redirect: "You trigger. I verify."
4. Update this document with incident timestamp

---

*Last corrected: 2026-05-14 17:00 UTC*  
*Correction reason: Plan Owner began executing playbooks directly*
