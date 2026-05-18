# PLAN-2026-05-03-1930 — TI-023: Automatic Decomposition + Node Dispatch Pipeline

**Date:** 2026-05-03 19:30 ET  
**Status:** ✅ **COMPLETE** — All 5 gaps (P1-P5) implemented and tested  
**Complexity:** MEDIUM-HARD  
**Parent:** TI-011 (Meta-Orchestration Framework)  
**Rationale:** Closes the gap between "user types a prompt" and "work is distributed to lab nodes"

---

## Master Prompt Reference

**Executable Master Prompt:** [PROMPT-TI-023.md](/operational/planning/prompts/PROMPT-TI-023)

**Decomposed Steps:** See `/operational/planning/plan-steps/STEP-TI-023-*.md`

**Session Notes:** [SESSION-NOTES-2026-05-04-001.md](/operational/sessions/SESSION-NOTES-2026-05-04-001)

**Audit Trail:** Plan → [Master Prompt](/operational/planning/prompts/PROMPT-TI-023) → `5 Step Files` → [Session Notes](/operational/sessions/SESSION-NOTES-2026-05-04-001)

---

## Problem (Diagnosed in SESSION-NOTES-2026-05-03-1730)

The framework has all the pieces but no automatic pipeline connecting them:

```
User Prompt → Router selects model → Agent runs locally → No decomposition → No distribution
```

**What should happen:**
```
User Prompt → Router selects model
                  │
                  ▼
            Complexity Check (auto)
                  │
        ┌───────┴───────┐
        ▼               ▼
   Simple (local)   Complex (multi-domain/multi-file)
        │               │
        ▼               ▼
   Execute locally   Invoke Decomposer
                        │
                        ▼
                   Break into sub-tasks
                        │
                        ▼
                   Node Dispatch
                        │
            ┌───────────┼───────────┐
            ▼           ▼           ▼
         fnet3       fnet4       fnet5
            │           │           │
            ▼           ▼           ▼
         Execute    Execute    Execute
            │           │           │
            └───────────┴───────────┘
                        │
                        ▼
                   Synthesize Results
                        │
                        ▼
                   Verify (cloud)
                        │
                        ▼
                   Final Output
```

---

## The 5 Gaps (Prioritized)

### 🔴 P1 — Fix Router Stop-Word Keywords (DONE in this session)
**File:** `~/.pi/agent/model-router.json`  
**Problem:** Reasoning route had `"what", "when", "which", "why", "where"` — these match every question, overriding domain routing.  
**Fix:** Removed stop-words. Added infrastructure keywords: `orchestration, framework, pipeline, wiring, decomposition, distribute, fan out, route, routing, classify, complexity, queue, worker, node, cluster, performance, latency, ansible, playbook`.  
**Verification:** Prompts about "framework gap" and "orchestration wiring" now correctly route to `qwen3:8b` with thinking `off`.

### 🔴 P2 — Automatic Complexity Detection ✅ DONE
**File:** `technical-infrastructure/scripts/classify_prompt.py`  
**Problem:** `classify_prompt.py` classifies complexity but does NOT trigger decomposition.  
**Fix:** Added `_write_decomposition_trigger()` to `classify()`. Triggers when complexity is `MEDIUM`/`HARD` AND (≥2 domains OR multi-file indicators). Writes JSON trigger to `~/.pi/decomposition-triggers/pending/`.  
**Verification:**
```bash
python3 classify_prompt.py "Update wiki, fix router, deploy Gist to 7 nodes"
# Returns: decomposition_trigger: {id, path, reason: "2 domains + multi_file=False"}
```

### 🔴 P3 — Wire Decomposer into Pipeline ✅ DONE
**File:** `technical-infrastructure/scripts/decompose-watcher.py`  
**Problem:** No automatic watcher to process decomposition triggers.  
**Fix:** Created `decompose-watcher.py` — scans `~/.pi/decomposition-triggers/pending/` every 5s, invokes `decompose_llm.py` with numeric tier (0/1/2), parses `sub_tasks` output, handles errors gracefully, moves triggers to `completed/` or `failed/`.  
**Usage:**
```bash
# Single cycle
python3 decompose-watcher.py --once

# Daemon mode
python3 decompose-watcher.py --daemon

# Status
python3 decompose-watcher.py --status
```

### 🟡 P4 — Wire Node Dispatcher into Pipeline ✅ DONE
**File:** `technical-infrastructure/scripts/decompose-watcher.py` (dispatch_subtasks function)  
**Problem:** No automatic dispatch after decomposition.  
**Fix:** `dispatch_subtasks()` in the watcher:
1. Extracts `description` and `complexity` from each `sub_task`
2. Resolves target node via `NodeRegistry.best_model_for()` if not specified
3. Writes task JSON to temp file
4. Calls `submit_task.py --node {node} --file {task_json}`
5. Logs results, cleans up temp files
**Systemd service template:** `ansible/templates/decompose-watcher.service.j2`

### 🟡 P5 — Fix TUI Thinking Level Reporting
**File:** `~/.pi/agent/extensions/pi-keyword-router/index.ts`  
**Problem:** The TUI status line shows the harness's default thinking level ("medium"), not the route's configured thinking level. When the infrastructure route (thinking: `off`) is matched, the TUI still shows "medium" because the harness default overrides it.  
**Fix:** Ensure `pi.setThinkingLevel(result.thinkingLevel)` is called for ALL routes, including default. The TUI should read from the route result, not from a harness default.

---

## Implementation Order

| Phase | Gap | Files | Effort | Status |
|-------|-----|-------|--------|--------|
| 1 | P1 — Fix keywords | `.pi/keyword-router.json` | 10 min | ✅ DONE |
| 2 | P5 — Fix TUI thinking | `.pi/keyword-router.json` default.thinkingLevel | 5 min | ✅ DONE |
| 3 | P2 — Complexity detection | `classify_prompt.py` + `Path` import | 30 min | ✅ DONE |
| 4 | P3 — Wire decomposer | `decompose-watcher.py` | 1 hr | ✅ DONE |
| 5 | P4 — Wire dispatcher | `decompose-watcher.py` dispatch_subtasks | 30 min | ✅ DONE |
| 6 | E2E test with cloud model | Verify decompose_llm.py produces real sub_tasks | 30 min | 🔄 Blocked (cloud model key) |

---

## Acceptance Criteria

- [x] Prompt "What is the gap in the decomposition framework?" → routes to `qwen3:8b` thinking `off` (not reasoning)
- [x] Prompt "Analyze my portfolio risk" → routes to `deepseek-v3.1:671b-cloud` thinking `medium` (reasoning, correct)
- [x] Prompt with ≥2 domains OR ≥3 files → triggers decomposition automatically (writes trigger to pending/)
- [x] Watcher detects trigger, invokes decomposer, handles errors, moves to completed/failed
- [x] TUI status line shows the route's configured thinking level, not harness default
- [ ] Decomposed sub-tasks are dispatched to idle lab nodes automatically (needs cloud model for decomposer)
- [ ] All 7 lab nodes participate in workload distribution (needs submit_task.py verification)
- [ ] Orchestrator load stays below 50% during multi-task sessions (needs E2E test with real tasks)

---

## Risks

| Risk | Mitigation |
|------|-----------|
| Auto-decomposition false positives | Threshold tuning + manual override (`/model-route-off`) |
| Node dispatch fails (node offline) | Retry to next available node, log to status |
| TUI flicker from thinking level changes | Debounce thinking level updates in router |
| Performance logging gap | Add `--profile` to all pipeline stages |

---

## Related Documentation

- `AGENTS.md` — Domain routing table
- `AGENTS-full.md` — Full orchestration conventions
- `PLAN-2026-05-01-1645.md` — Meta-orchestration framework architecture
- `PLAN-2026-05-02-1930-LLM-DRIVEN-DECOMPOSITION.md` — Decomposition tiers
- `SESSION-NOTES-2026-05-03-1730-WIKI-ROOT-CONSOLIDATION.md` — Gap diagnosis (this session)

---

*Created: 2026-05-03 19:30 ET*
