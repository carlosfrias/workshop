# 2x Decomposition Workflow

## Overview

When a sub-task fails verification with multiple independent failure modes, the verifier can request a **2x decomposition** — splitting the problematic sub-task into 2-3 more atomic steps.

The detailed detection logic, communication templates, and decision guides for this workflow are maintained in the project wiki to keep the agent definition lean.

**Reference:** [`wiki/reference/decomposition-logic.md`](wiki/reference/decomposition-logic.md)

## Workflow Diagram

```
┌─────────────┐
│ Decomposer  │ → Creates initial decomposition plan
└─────────────┘
       ↓
┌─────────────┐
│   Executor  │ → Runs sub-task (position-management, position-monitor, etc.)
└─────────────┘
       ↓
┌─────────────┐
│  Verifier   │ → Checks output against criteria
└─────────────┘
       ↓
    Pass? ────→ Continue to bookkeeping
       │
       │ FAIL (2+ independent failures)
       ↓
┌─────────────────────────────────┐
│ Verifier detects over-complex   │
│ sub-task and sends intercom.ask │
└─────────────────────────────────┘
       ↓
┌─────────────────────────────────┐
│ Orchestrator receives request   │
│ and decides:                    │
│ - Re-decompose (launch new chain)│
│ - Decline (use cloud re-run)     │
└─────────────────────────────────┘
       ↓
┌─────────────────────────────────┐
│ Verifier finalizes report based │
│ on orchestrator's decision      │
└─────────────────────────────────┘
```

## Implementation Checklist

When acting as the orchestrator or verifier in this loop, always refer to the **Validation Matrix** and **Intercom Templates** in [`wiki/reference/decomposition-logic.md`](wiki/reference/decomposition-logic.md).

1. **Verifier**: Does the output show 2+ failure modes and task-switching?
2. **Intercom**: Use the standardized request template from the wiki.
3. **Orchestrator**: Follow the "Agree vs Decline" guide in the wiki.
4. **Execution**: Refine the lauch instructions based on the wiki's execution loop.

## Related Files

- `/Users/friasc/Dropbox/workshop/.pi/agents/verifier.md` — Updated with 2x decomposition protocol
- `/Users/friasc/Dropbox/workshop/.pi/agents/decomposer.md` — Updated with complexity flagging and re-decomposition handling
- `/Users/friasc/Dropbox/workshop/.pi/agents/decomposed-trade-to-log.chain.md` — Chain that uses decomposer → executor → verifier pattern
- `/Users/friasc/Dropbox/workshop/.pi/agents/decomposed-monitor-to-log.chain.md` — Chain that uses decomposer → executor → verifier pattern
