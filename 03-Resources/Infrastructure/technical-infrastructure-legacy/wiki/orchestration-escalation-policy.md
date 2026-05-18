# Lab-Node Orchestration Escalation Policy

**Version:** 1.0
**Status:** Verified (Simulation 2026-05-12)
**Context:** This policy defines the automated routing and escalation behavior when the orchestrator detects lab-node saturation.

---

## 1. Core Objective
Minimize cloud expenditure by utilizing lower-capacity local models to their limit, using 2x decomposition as a primary recovery mechanism before escalating to more expensive compute tiers.

## 2. The Escalation Chain
Tasks must follow this linear progression if a node exhibits saturation (high CPU/RAM/Swap):

**Local Tier (The Buffer)**
1. **Local Low** (`qwen3.5:4b`) -> *Initial Target*
2. **Local Medium** (`qwen3.5:4b` w/ higher context/thinking)
3. **Local High** (`gemma4:e4b`)

**Cloud Tier (The Heavy Lifters)**
4. **Cloud Low** (`qwen3.5:397b-cloud`) -> *Presumed more capable than Local High*
5. **Cloud Medium** (`qwen3.5:397b-cloud` w/ high thinking)
6. **Cloud High** (`kimi-k2.6`) -> *Final Resort*

---

## 3. The Recovery Workflow (Step-by-Step)

Whenever a task is routed to a tier and the **Health Monitor** detects saturation:

### Step A: 2x Decomposition (The First Response)
- **Trigger:** First saturation event on a specific task.
- **Action:** Return the task to the `decomposer` agent for a 2x split (into smaller, more atomic sub-tasks).
- **Retry:** Attempt to execute these sub-tasks on the **same original tier**.

### Step B: Tier Escalation (The Second Response)
- **Trigger:** Sub-tasks from 2x decomposition still encounter saturation on the current tier.
- **Action:** Escalate the failing sub-task to the **next higher model in the stack**.
- **Logic:** `Local Low` -> `Local Medium` -> `Local High` -> `Cloud Low`.

### Step C: Cloud Escalation (The Final Response)
- **Trigger:** `Local High` tier is saturated.
- **Action:** Route the task to `Cloud Low`.
- **Presumption:** All cloud-tier models are inherently more capable than local-tier models.

---

## 4. Verification & Logging
Every escalation event must be logged to `wiki/operational/sessions/escalation-simulation.jsonl` (or appropriate session log) including:
- Original complexity
- Final tier used
- Total number of decompositions
- Latency overhead introduced by escalation

**End of Policy**
