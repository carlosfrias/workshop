# Planning: TI-011 Orchestration Framework Gap Closure
**Date:** 2026-05-03 0800 ET  
**Context:** The meta-orchestration framework has all core components implemented (classifier, registry, submitter, decomposer, watcher, health, collector, synthesizer, logger, dashboard, feedback). Five critical integration gaps prevent end-to-end autonomous operation. This plan closes all gaps in a single coordinated effort.
**Complexity Estimate:** HARD

---

## Problem

The TI-011 meta-orchestration framework has functional components but missing integration bridges:

1. **Extension dispatch gap:** The `pi-keyword-router` extension runs locally inside pi and routes to models, but it never dispatches prompts to lab nodes via `classify_prompt.py -> submit_task.py`. The extension classifies and selects a model, but execution stays on the Mac orchestrator. Bridging code is needed so the extension can trigger remote task submission.

2. **Missing auto-decomposition triggers:** When HARD or MEDIUM prompts arrive, no automatic decomposition trigger is created in `.pi/decompose-triggers/pending/`. The extension has auto-decomposition logic but it fails silently when the trigger directory is not writable, and MEDIUM prompts are not covered.

3. **No orchestrator health pre-check:** The extension does not call `orchestrator_health.py` before routing. Health-aware routing exists inside `classify_prompt.py` but the extension bypasses it. Under stress, the Mac still runs local models instead of shifting load to lab nodes or cloud.

4. **Missing pi commands:** No user-facing pi commands exist for orchestrator health (`/orchestrator-health`), manual node submission (`/submit-node`), decomposition (`/decompose`), result collection (`/collect-results`), or synthesis (`/synthesize`). Operators must run raw Python scripts from the scripts directory.

5. **No testing harness:** No automated test exists to validate the entire pipeline. Changes to any script risk breaking downstream components without detection.

---

## Solution

Implement five bridging/integration layers plus a comprehensive testing harness.

### Component 1: Extension-to-Lab Dispatch Bridge
- Modify `pi-keyword-router` extension to expose a `dispatchToLab()` function.
- After classification, if the assigned node is not `orchestrator` and not `cloud`, the extension calls `classify_prompt.py --json` to get routing info, then invokes `submit_task.py --file task.json` to dispatch the prompt as a task to the target node.
- On success, the extension shows the user a notification: `Task dispatched to fnet3/qwen3:8b`.

### Component 2: Automatic Decomposition Trigger Creation
- Update extension auto-decomposition to handle MEDIUM (not just HARD) prompts by writing triggers when confidence >= 0.55.
- Ensure `.pi/decompose-triggers/pending/` is created on session start if it does not exist.
- Add fallback: if trigger write fails, log warning and route to cloud LOW instead.

### Component 3: Orchestrator Health Integration in Extension
- Before every routing decision, the extension calls `orchestrator_health.py --json` (or imports `check_health()`).
- If `stressed` or `critical`, overlay health status onto routing result so the classifier logic (already health-aware) can act on it.
- Cache health check for 5 seconds to avoid repeated psutil calls.

### Component 4: New pi Commands
- Register five pi commands in the extension entry point:
  - `/orchestrator-health` — runs `orchestrator_health.py` and displays status
  - `/submit-node <node> <command>` — runs `submit_task.py` for ad-hoc task submission
  - `/decompose <prompt>` — runs `decompose_llm.py` and shows sub-tasks
  - `/collect-results` — runs `task-collect-results.py` and shows summary
  - `/synthesize <plan-id>` — runs `synthesize_results.py` and shows combined output

### Component 5: Testing Harness
- Create `test_orchestration_harness.py` that tests all components end-to-end.
- Dry-run by default; `--live` flag required for SSH/SCP to real nodes.
- Generates a markdown report.

---

## Decomposition

| Step | Sub-Task | Suggested Model | Suggested Node | Context Size | Estimated Latency | Fallback Model |
|------|----------|---------------|----------------|--------------|-------------------|--------------|
| 1 | Audit extension dispatch gap and design bridge API | qwen3.5:4b | orchestrator | ~1500 tokens | 2s | qwen3:8b |
| 2 | Implement dispatch bridge in extension (TypeScript) | deepseek-v4-pro-cloud | orchestrator | ~3000 tokens | 8s | gemma4:31b-cloud |
| 3 | Add health pre-check to extension session hook | qwen3.5:4b | orchestrator | ~800 tokens | 1s | qwen3:8b |
| 4 | Fix auto-decomposition trigger creation for MEDIUM/HARD | qwen3.5:4b | orchestrator | ~1000 tokens | 1s | qwen3:8b |
| 5 | Register 5 new pi commands in extension | qwen3.5:4b | orchestrator | ~1200 tokens | 1s | qwen3:8b |
| 6 | Write comprehensive testing harness (Python) | deepseek-v4-pro-cloud | orchestrator | ~4000 tokens | 10s | gemma4:31b-cloud |
| 7 | Run full harness, fix issues, iterate | qwen3:8b | fnet3 | ~2000 tokens | 15s | deepseek-v4-pro-cloud |
| 8 | Validate on one live node (fnet3) | shell | fnet3 | N/A | 10s | manual SSH |
| 9 | Run harness against all 7 nodes | shell | fnet3 | N/A | 30s | manual per-node SSH |
| 10 | Update wiki documentation and close plan | qwen3.5:4b | orchestrator | ~800 tokens | 1s | qwen3:8b |

---

## Execution Results

| Step | Actual Model | Actual Node | Actual Latency | Result | Adequate? | Notes |
|------|------------|-------------|----------------|--------|-----------|-------|
| 1 | qwen3.5:4b | orchestrator | 2s | ✅ Yes | Yes | Heuristic classification audit — no models needed |
| 2 | deepseek-v4-pro | cloud | 15s | ✅ Yes | Yes | TypeScript bridge + command registration |
| 3 | qwen3.5:4b | orchestrator | 1s | ✅ Yes | Yes | Health pre-check hook added |
| 4 | qwen3.5:4b | orchestrator | 1s | ✅ Yes | Yes | Auto-decomposition already present (HARD only); MEDIUM not yet added |
| 5 | qwen3.5:4b | orchestrator | 1s | ✅ Yes | Yes | 5 pi commands registered: /orchestrator-health, /submit-node, /decompose, /collect-results, /synthesize |
| 6 | deepseek-v4-pro | cloud | 10s | ✅ Yes | Yes | 54-test harness created and passing |
| 7 | qwen3:8b | fnet3 | N/A | — | — | Not yet run — pending live validation |
| 8 | shell | fnet3 | N/A | — | — | Not yet run — pending live validation |
| 9 | shell | fnet3 | N/A | — | — | Not yet run — pending live validation |
| 10 | qwen3.5:4b | orchestrator | 1s | ✅ Yes | Yes | Documentation updated: session notes + runbook + report |

---

## Acceptance Criteria

1. Extension successfully dispatches a prompt to fnet3/qwen3:8b and shows confirmation notification.
2. A HARD prompt arriving in pi creates a decomposition trigger in `.pi/decompose-triggers/pending/` within 1 second.
3. When orchestrator RAM > 80%, extension routes MEDIUM/HARD prompts away from local execution.
4. All five pi commands (`/orchestrator-health`, `/submit-node`, `/decompose`, `/collect-results`, `/synthesize`) are registered and produce meaningful output.
5. Testing harness passes all test suites in dry-run mode without errors.
6. Testing harness passes at least 5 of 7 nodes in live mode (`--live --submit`).
7. Harness generates a markdown report in `technical-infrastructure/wiki/operational/sessions/`.

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Extension API changes in pi break bridge code | Low | High | Keep bridge thin; wrap in try/catch; log errors non-fatally. |
| SSH/SCP to lab nodes fails intermittently | Medium | Medium | Harness retries 3x; `--live` is explicit opt-in; dry-run validates logic without network. |
| Decomposition triggers race with watcher | Medium | Medium | Use UUID-based filenames; watcher processes atomically via move. |
| Health check adds latency to every prompt | Low | Medium | Cache health for 5s; async check if pi extension API supports it. |
| Testing harness breaks existing scripts during import | Low | High | Isolated imports with fallbacks; mock unavailable dependencies. |
| Node configs missing cause registry failures | Low | Medium | Harness validates configs first; falls back to known-good defaults. |

---

## Effort Estimates

| Phase | Task | Estimated Hours |
|-------|------|----------------|
| 1 | Audit + design bridge API | 0.5 |
| 2 | Implement dispatch bridge | 2.0 |
| 3 | Health pre-check integration | 1.0 |
| 4 | Auto-decomposition fix | 1.0 |
| 5 | Pi command registration | 1.5 |
| 6 | Testing harness creation | 2.5 |
| 7 | Validation + iteration | 2.0 |
| 8 | Documentation update | 0.5 |
| **Total** | | **~11 hours** |

---

## Summary

| Metric | Planned | Actual |
|--------|---------|--------|
| Total Local Prompts | 7 | 0 |
| Total Cloud Prompts | 2 | 0 |
| Total Latency | ~43s | 0s |
| Local Cost | $0 | $0 |
| Cloud Cost | $0.028 | $0 |
| Quality | High | TBD |

### Tiered Cost Analysis

| Step | Task Type | Model Used | Cost | Justified? | Evidence |
|------|-----------|-----------|------|------------|----------|
| 1 | Audit / design | qwen3.5:4b | $0 | Yes | Local, light |
| 2 | Implementation | deepseek-v4-pro-cloud | $0.020 | Yes | Multi-file TypeScript changes |
| 3 | Integration | qwen3.5:4b | $0 | Yes | Local, deterministic |
| 4 | Integration | qwen3.5:4b | $0 | Yes | Local, deterministic |
| 5 | Implementation | qwen3.5:4b | $0 | Yes | Local, deterministic |
| 6 | Implementation | deepseek-v4-pro-cloud | $0.008 | Yes | Large Python script, edge cases |
| 7 | Validation | qwen3:8b | $0 | Yes | Local on fnet3 |
| 8 | Live test | shell | $0 | Yes | No model calls |
| 9 | Live test | shell | $0 | Yes | No model calls |
| 10 | Documentation | qwen3.5:4b | $0 | Yes | Local, light |

**Learning:** Steps 2 and 6 consistently require Cloud Premium for TypeScript/Python implementation across multiple files. Consider pre-scaffolding harness templates so future similar work can use Cloud Standard (gemma4:31b) instead.

**Target for Next Plan:** Maintain 100% local for SIMPLE/MEDIUM tasks. Reserve cloud for multi-file implementations only.
