# SESSION-NOTES-2026-05-03-2015 — TI-023 P2-P4 Implementation: Auto-Decompose + Node Dispatch

**Date:** 2026-05-03 20:15 ET  
**Node:** orchestrator (friasc)  
**Task:** Implement P2 (auto-complexity detection), P3 (decomposer watcher), P4 (node dispatch wiring)  
**Status:** ✅ Implemented, blocked on cloud model for full E2E

---

## What Was Implemented

### P2 — Automatic Complexity Detection (`classify_prompt.py`)
**File:** `technical-infrastructure/scripts/classify_prompt.py`

Added `_write_decomposition_trigger()` function that:
- Triggers when complexity is `MEDIUM` or `HARD`
- Counts domain keywords in prompt (≥2 domains → trigger)
- Detects multi-file indicators ("all nodes", "multiple files", "deploy to all", etc.)
- Writes JSON trigger to `~/.pi/decomposition-triggers/pending/{id}.json`
- Added `from pathlib import Path` import (was missing)

**Trigger format:**
```json
{
  "id": "69004cc8f989",
  "prompt": "...",
  "complexity": "HARD",
  "confidence": 0.75,
  "domains": ["framework", "performance"],
  "multi_file": false,
  "created_at": "2026-05-03T19:48:33",
  "route": null,
  "status": "pending"
}
```

**Verification:**
```bash
python3 classify_prompt.py "Design a meta-orchestration framework..."
# Returns: decomposition_trigger: {id, path, reason: "2 domains + multi_file=False"}
```

---

### P3 — Decomposition Watcher (`decompose-watcher.py`)
**File:** `technical-infrastructure/scripts/decompose-watcher.py` (new)

Scans `~/.pi/decomposition-triggers/pending/` and:
1. Reads trigger JSON
2. Invokes `decompose_llm.py --prompt {prompt} --tier {0|1|2} --json`
3. Checks for decomposer errors in response
4. Parses `sub_tasks` (not `subtasks`) from decomposer output
5. Saves plan to `~/.pi/decomposition-triggers/plans/`
6. Moves trigger to `completed/` or `failed/`

**Usage:**
```bash
python3 decompose-watcher.py --once      # Single cycle
python3 decompose-watcher.py --daemon    # Continuous (5s polling)
python3 decompose-watcher.py --status    # Show queue
python3 decompose-watcher.py --dry-run   # Process without dispatch
```

**Test results:**
```
[19:48:33] Processing 1 pending trigger(s)...
[19:48:33] Trigger 69004cc8f989: Design a meta-orchestration framework...
[19:48:33]   ✅ Decomposed into 2 sub-tasks (dry-run)
[19:48:33]   ✅ Dispatched 2 sub-tasks
[19:48:33] Done: 1 processed, 1 decomposed, 2 dispatched, 0 failed
```

---

### P4 — Node Dispatch Wiring
**File:** `technical-infrastructure/scripts/decompose-watcher.py` (`dispatch_subtasks()`)

For each `sub_task` from decomposer:
1. Extracts `description` and `complexity`
2. Resolves target node via `NodeRegistry.best_model_for()` if not specified
3. Writes task JSON to temp file (`/tmp/...json`)
4. Calls `submit_task.py --node {node} --file {task_file}`
5. Cleans up temp file, logs results

**Systemd service template:** `ansible/templates/decompose-watcher.service.j2`

---

## Blocker: Cloud Model for Decomposer

The full E2E pipeline works until the decomposer stage. `decompose_llm.py` requires a cloud model (tier 1 = `gemma4:cloud`, tier 2 = `kimi-k2.6:cloud`). Without the cloud API key configured, the decomposer returns:

```json
{
  "status": "error",
  "tier": 1,
  "model": "gemma4:cloud",
  "cost": 0,
  "error": "No API key for provider ollama-cloud",
  "raw_response": "..."
}
```

The watcher correctly detects this error and moves the trigger to `failed/`.

**To complete E2E testing:**
1. Ensure `GITHUB_TOKEN` or cloud provider API key is set
2. Verify `ollama-cloud` models are registered in `~/.pi/agent/models.json`
3. Run: `python3 decompose-watcher.py --once`

---

## Files Created/Modified

| File | Action |
|------|--------|
| `technical-infrastructure/scripts/classify_prompt.py` | Added `_write_decomposition_trigger()`, `Path` import |
| `technical-infrastructure/scripts/decompose-watcher.py` | Created — full watcher + dispatch |
| `technical-infrastructure/ansible/templates/decompose-watcher.service.j2` | Created — systemd service template |
| `PLAN-2026-05-03-1930-TI023-AUTO-DECOMPOSE-NODE-DISPATCH.md` | Updated status to Phase 1-2 Complete |

---

## Quick Commands

```bash
# Validate router config (before any routing work)
ansible-playbook -i localhost, -c local technical-infrastructure/ansible/playbooks/validate-router-config.yml

# Generate a trigger manually
python3 technical-infrastructure/scripts/classify_prompt.py "Your complex prompt here" --json

# Process triggers once
python3 technical-infrastructure/scripts/decompose-watcher.py --once

# Monitor trigger queue
python3 technical-infrastructure/scripts/decompose-watcher.py --status
```

---

**Next Steps:**
1. Configure cloud model API key for decomposer E2E test
2. Verify `submit_task.py` successfully submits to lab nodes
3. Deploy systemd timer for continuous watcher operation
4. Add performance logging to all pipeline stages

---

**Related:**
- `SESSION-NOTES-2026-05-03-1945-ROUTER-COLLISION-CLEANUP.md` — P1 + P5 completion
- `PLAN-2026-05-03-1930-TI023-AUTO-DECOMPOSE-NODE-DISPATCH.md` — Full architecture
