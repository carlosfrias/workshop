# 2x Decomposition Workflow

## [S-TIGHT]

When a sub-task fails verification with 2+ independent failure modes, split it into 2-3 more atomic steps. Detailed logic in wiki/reference/decomposition-logic.md.

## LOD Loading Directive

| Model Tier | Load |
|------------|------|
| **Low (<4K)** | CORE (Overview + Diagram) |
| **Medium+** | Full file (~2KB) |

---

## CORE — Overview (LOD: Low)

When a sub-task fails verification with multiple independent failure modes, the verifier can request a **2x decomposition** — splitting the problematic sub-task into 2-3 more atomic steps.

Since v2 (fleet-dispatcher cascade), the D-E-V pipeline routes sub-tasks through a three-tier cascade:

1. **Tier 1 (fleet):** `coms_net_send` to remote pi agents
2. **Tier 2 (intercom):** `intercom ask` to local pi sessions
3. **Tier 3 (subagent):** Built-in `subagent()` tool (always available)

The fleet-dispatcher handles routing and degradation. The decomposer and verifier remain tier-agnostic.

The detailed detection logic, communication templates, and decision guides for this workflow are maintained in the project wiki to keep the agent definition lean.

**Reference:** [`wiki/reference/decomposition-logic.md`](wiki/reference/decomposition-logic.md)

## Workflow Diagram

```
┌─────────────┐
│ Decomposer  │ → Creates tier-agnostic decomposition plan
└──────┬───────┘
       │
       ▼
┌─────────────────────┐
│ Fleet-Dispatcher    │ → Routes sub-tasks through cascade
│                     │   Tier 1: coms_net (fleet)
│                     │   Tier 2: intercom (local sessions)
│                     │   Tier 3: subagent (always available)
└──────┬──────────────┘
       │
       ▼
┌─────────────┐
│  Verifier    │ → Checks output (tier-agnostic)
└──────┬───────┘
       │
    Pass? ────→ Continue to bookkeeping
       │
       │ FAIL (2+ independent failures)
       ▼
┌─────────────────────────────────┐
│ Verifier detects over-complex    │
│ sub-task and sends intercom.ask │
└─────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ Orchestrator receives request   │
│ and decides:                    │
│ - Re-decompose (launch new chain)│
│ - Decline (use cloud re-run)     │
└─────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ Verifier finalizes report based │
│ on orchestrator's decision      │
└─────────────────────────────────┘
```

## CHECKLIST — Implementation Checklist (LOD: Medium)

When acting as the orchestrator or verifier in this loop, always refer to the **Validation Matrix** and **Intercom Templates** in [`wiki/reference/decomposition-logic.md`](wiki/reference/decomposition-logic.md).

1. **Verifier**: Does the output show 2+ failure modes and task-switching?
2. **Intercom**: Use the standardized request template from the wiki.
3. **Orchestrator**: Follow the "Agree vs Decline" guide in the wiki.
4. **Execution**: Refine the lauch instructions based on the wiki's execution loop.

## Related Files

- `/Users/friasc/Cloud/workshop/.pi/agents/verifier.md` — Updated with 2x decomposition protocol
- `/Users/friasc/Cloud/workshop/.pi/agents/decomposer.md` — Updated with complexity flagging and re-decomposition handling
- `/Users/friasc/Cloud/workshop/.pi/agents/decomposed-trade-to-log.chain.md` — Chain that uses decomposer → executor → verifier pattern
- `/Users/friasc/Cloud/workshop/.pi/agents/decomposed-monitor-to-log.chain.md` — Chain that uses decomposer → executor → verifier pattern
