# Phase 1 Decomposition — B-KR-001: Implement Persistent Kill-Switch (GREEN)

**Date:** 2026-05-13  
**Phase:** Phase 1 (Implementation / GREEN)  
**Backlog Item:** B-KR-001  
**Decomposed by:** High Cloud Model (`ollama/kimi-k2.6`)  
**Handoff to:** Low Cloud Model (`ollama/qwen3.5:397b`)  
**Skill:** `decompose-execute-verify`  
**Reference:** [`AGENTS.md`](./AGENTS.md), [`DECOMP-B-KR-001-2026-05-13.md`](./DECOMP-B-KR-001-2026-05-13.md)

---

## [S-TIGHT]

Phase 1 takes the 20 RED test stubs from Phase 0 and implements the minimal code to make them pass (GREEN). The 20 implementation steps are grouped into 4 implementation waves that mirror the test waves, with additional dependency constraints: **config schema must be implemented before gatekeeper logic, and gatekeeper logic before hook registration.** All implementation steps are parallelizable within their wave dependency constraints.

**Estimated total effort:** 2.5 hours, wall-clock: ~40 minutes with full parallelism.

---

## Dependency Chain

```
CONFIG SCHEMA ──→ GATEKEEPER ──→ HOOK REGISTRATION ──→ EVENT EMISSION ──→ FOOTER RENDERING
    │                  │                  │                     │                  │
    ▼                  ▼                  ▼                     ▼                  ▼
HARNESS         UNIT-001/002      INT-001/002            ACC-001           DOC-001
```

**Hard rule:** A downstream step may only start after its upstream dependency is verified GREEN.

---

## Implementation Wave 0 — Config Schema + Harness Fix (Sequential)

These steps establish the foundational config flag. All other implementation depends on this.

### Impl-0A: B-KR-001-IMPL-CONFIG-001 — Add `enabled` Field to Config Schema

| Field | Value |
|-------|-------|
| `step_id` | `B-KR-001-IMPL-CONFIG-001` |
| `title` | Add `extensions.pi-keyword-router.enabled` boolean field to config schema |
| `workspace` | `pi-keyword-router` |
| `target_file` | `lib/config.ts` (or equivalent config module) |
| `target_node` | **fnet3** |
| `acceptance_criteria` | `loadConfig()` returns object with `enabled: boolean` field. UNIT-001A/B tests now pass. |
| `estimated_effort` | 15 min |
| `recommended_model` | `medium-local` (`gemma4:e4b`) |

### Impl-0B: B-KR-001-IMPL-CONFIG-002 — Default `enabled` to `true` for Backward Compatibility

| Field | Value |
|-------|-------|
| `step_id` | `B-KR-001-IMPL-CONFIG-002` |
| `title` | Set default value of `enabled` to `true` when not specified in config |
| `workspace` | `pi-keyword-router` |
| `target_file` | `lib/config.ts` |
| `target_node` | **fnet3** (same session as Impl-0A) |
| `acceptance_criteria` | `loadConfig()` returns `{ enabled: true }` when no config exists. No existing behavior changes. |
| `estimated_effort` | 10 min |
| `recommended_model` | `low-local` (`qwen3.5:4b`) |

### Impl-0C: B-KR-001-IMPL-HARNESS-001 — Fix Test Runner if Needed

| Field | Value |
|-------|-------|
| `step_id` | `B-KR-001-IMPL-HARNESS-001` |
| `title` | Verify test runner config can load the config module without errors |
| `workspace` | `pi-keyword-router` |
| `target_file` | `jest.config.js` or `vitest.config.ts` |
| `target_node` | **fnet3** (same session) |
| `acceptance_criteria` | `npm test` runs and all tests compile (even if failing). No module resolution errors. |
| `estimated_effort` | 10 min |
| `recommended_model` | `low-local` |

**Wave 0 Dispatch (pi-intercom):**
```typescript
intercom({
  action: "ask",
  to: "fnet3",
  message: "Implementation Wave 0: Execute IMPL-CONFIG-001, IMPL-CONFIG-002, IMPL-HARNESS-001 in sequence on fnet3. Add enabled field to config schema with default true. Verify npm test compiles. Report test output + git diff."
})
```

---

## Implementation Wave 1 — Core Logic (Parallel, 5 sub-steps)

**Prerequisite:** Wave 0 verified GREEN (config schema exists and tests pass).

### Impl-1A: B-KR-001-IMPL-GATE-001 — Implement `shouldRegisterHooks()`

| Field | Value |
|-------|-------|
| `step_id` | `B-KR-001-IMPL-GATE-001` |
| `title` | Implement `shouldRegisterHooks(config)` that returns `false` when `enabled === false` |
| `workspace` | `pi-keyword-router` |
| `target_file` | `lib/gatekeeper.ts` (new file) |
| `target_node` | **fnet1** |
| `acceptance_criteria` | `shouldRegisterHooks({ enabled: false })` returns `false`. `shouldRegisterHooks({ enabled: true })` returns `true`. UNIT-002A/B tests pass. |
| `estimated_effort` | 15 min |
| `recommended_model` | `low-local` |

### Impl-1B: B-KR-001-IMPL-INDEX-001 — Wire Gatekeeper into Extension Entry Point

| Field | Value |
|-------|-------|
| `step_id` | `B-KR-001-IMPL-INDEX-001` |
| `title` | Update `index.ts` to call `shouldRegisterHooks()` before registering any hooks |
| `workspace` | `pi-keyword-router` |
| `target_file` | `index.ts` |
| `target_node` | **fnet2** |
| `acceptance_criteria` | When `enabled === false`, `index.ts` skips `registerHooks()`. When `enabled === true`, normal registration occurs. |
| `estimated_effort` | 15 min |
| `recommended_model` | `medium-local` |

### Impl-1C: B-KR-001-IMPL-FOOTER-001 — Add Disabled State Handler to Footer

| Field | Value |
|-------|-------|
| `step_id` | `B-KR-001-IMPL-FOOTER-001` |
| `title` | Update routing-transparency footer to render `keyword-router: disabled` when enabled === false |
| `workspace` | `routing-transparency` |
| `target_file` | `src/footer.ts` (or equivalent) |
| `target_node` | **fnet7** |
| `acceptance_criteria` | Footer output contains `keyword-router: disabled` and `src: disabled` when `enabled === false`. UNIT-003A/B/C tests pass. |
| `estimated_effort` | 20 min |
| `recommended_model` | `low-local` |

### Impl-1D: B-KR-001-IMPL-EVENT-001 — Suppress `keyword-router:routed` Event when Disabled

| Field | Value |
|-------|-------|
| `step_id` | `B-KR-001-IMPL-EVENT-001` |
| `title` | Add event guard: do not emit `keyword-router:routed` when `enabled === false` |
| `workspace` | `pi-keyword-router` |
| `target_file` | `lib/events.ts` or `index.ts` |
| `target_node` | **fnet3** |
| `acceptance_criteria` | Event `keyword-router:routed` is not emitted when `enabled === false`. INT-002A/B tests pass. |
| `estimated_effort` | 15 min |
| `recommended_model` | `medium-local` |

### Impl-1E: B-KR-001-IMPL-FALLBACK-001 — Route to Model-Router Fallback when Disabled

| Field | Value |
|-------|-------|
| `step_id` | `B-KR-001-IMPL-FALLBACK-001` |
| `title` | When `enabled === false`, route events to model-router fallback instead of keyword-routed path |
| `workspace` | `pi-keyword-router` |
| `target_file` | `lib/router.ts` or `index.ts` |
| `target_node` | **fnet4** |
| `acceptance_criteria` | `model-router` receives fallback route event when `enabled === false`. INT-001A/B tests pass. |
| `estimated_effort` | 20 min |
| `recommended_model` | `medium-local` |

**Wave 1 Parallel Dispatch (pi-intercom):**
```typescript
intercom({ action: "ask", to: "fnet1", message: "Impl Wave 1: Execute IMPL-GATE-001. Implement shouldRegisterHooks(). Report test output + git diff." })
intercom({ action: "ask", to: "fnet2", message: "Impl Wave 1: Execute IMPL-INDEX-001. Wire gatekeeper into index.ts. Report test output + git diff." })
intercom({ action: "ask", to: "fnet7", message: "Impl Wave 1: Execute IMPL-FOOTER-001. Add disabled state to footer. Report test output + git diff." })
intercom({ action: "ask", to: "fnet3", message: "Impl Wave 1: Execute IMPL-EVENT-001. Suppress keyword-router:routed when disabled. Report test output + git diff." })
intercom({ action: "ask", to: "fnet4", message: "Impl Wave 1: Execute IMPL-FALLBACK-001. Route to fallback when disabled. Report test output + git diff." })
```

---

## Implementation Wave 2 — Session Persistence + Acceptance (Parallel, 3 sub-steps)

**Prerequisite:** Wave 1 verified GREEN (all core logic implemented).

### Impl-2A: B-KR-001-IMPL-PERSIST-001 — Persist Config State Across Session Restarts

| Field | Value |
|-------|-------|
| `step_id` | `B-KR-001-IMPL-PERSIST-001` |
| `title` | Read config from persistent storage (not just in-memory) so `enabled` survives restart |
| `workspace` | `pi-keyword-router` |
| `target_file` | `lib/config.ts` |
| `target_node` | **fnet5** |
| `acceptance_criteria` | Config is read from disk/state on every session start. ACC-001A/B tests pass. |
| `estimated_effort` | 20 min |
| `recommended_model` | `medium-local` |

### Impl-2B: B-KR-001-IMPL-PERSIST-002 — Manual Selection Persistence

| Field | Value |
|-------|-------|
| `step_id` | `B-KR-001-IMPL-PERSIST-002` |
| `title` | Store manual Ctrl+P selection in persistent state so it survives restart |
| `workspace` | `pi-keyword-router` |
| `target_file` | `lib/persistence.ts` (new file) or `lib/config.ts` |
| `target_node` | **fnet5** (same session as Impl-2A) |
| `acceptance_criteria` | Manual model selection persists across simulated session restart. ACC-001C test passes. |
| `estimated_effort` | 20 min |
| `recommended_model` | `medium-local` |

### Impl-2C: B-KR-001-IMPL-DOC-001 — Populate Kill-Switch Documentation

| Field | Value |
|-------|-------|
| `step_id` | `B-KR-001-IMPL-DOC-001` |
| `title` | Replace TODO placeholders in kill-switch documentation with actual descriptions |
| `workspace` | `routing-transparency` |
| `target_file` | `src/KILL-SWITCH-2026-05-13-1926.md` |
| `target_node` | **fnet6** |
| `acceptance_criteria` | All `// TODO: populate` placeholders replaced with accurate descriptions of implemented behavior. DOC-001A/B tests pass (if any). |
| `estimated_effort` | 15 min |
| `recommended_model` | `low-local` |

**Wave 2 Parallel Dispatch (pi-intercom):**
```typescript
intercom({ action: "ask", to: "fnet5", message: "Impl Wave 2: Execute IMPL-PERSIST-001 and IMPL-PERSIST-002 in sequence. Implement session persistence. Report test output + git diff." })
intercom({ action: "ask", to: "fnet6", message: "Impl Wave 2: Execute IMPL-DOC-001. Populate kill-switch documentation. Report file contents + git diff." })
```

---

## Implementation Wave 3 — Full System Verification (Sequential)

**Prerequisite:** Waves 0–2 verified GREEN.

### Impl-3A: B-KR-001-IMPL-SYS-001 — Run Full Test Suite (Enabled = true)

| Field | Value |
|-------|-------|
| `step_id` | `B-KR-001-IMPL-SYS-001` |
| `title` | Run all tests with `enabled = true` to verify no regression in normal operation |
| `workspace` | `pi-keyword-router` + `routing-transparency` |
| `target_file` | All test files |
| `target_node` | **fnet3** |
| `acceptance_criteria` | All tests pass. No existing functionality broken. |
| `estimated_effort` | 15 min |
| `recommended_model` | `medium-local` |

### Impl-3B: B-KR-001-IMPL-SYS-002 — Run Full Test Suite (Enabled = false)

| Field | Value |
|-------|-------|
| `step_id` | `B-KR-001-IMPL-SYS-002` |
| `title` | Run all tests with `enabled = false` to verify kill-switch fully disables the extension |
| `workspace` | `pi-keyword-router` + `routing-transparency` |
| `target_file` | All test files |
| `target_node` | **fnet3** (same session) |
| `acceptance_criteria` | All kill-switch-related tests pass. Extension produces no hooks, no events, and footer shows disabled state. |
| `estimated_effort` | 15 min |
| `recommended_model` | `medium-local` |

### Impl-3C: B-KR-001-IMPL-SYS-003 — Write Phase 1 Completion Report

| Field | Value |
|-------|-------|
| `step_id` | `B-KR-001-IMPL-SYS-003` |
| `title` | Document what was implemented, what tests pass, and any known issues |
| `workspace` | `keyword-router-debug` wiki |
| `target_file` | `wiki/operational/sessions/PHASE1-GREEN-2026-05-13-HHMM.md` |
| `target_node` | **fnet3** (same session) |
| `acceptance_criteria` | Report exists with: list of implemented files, test results summary, node allocation log, any TODOs for Phase 2. |
| `estimated_effort` | 10 min |
| `recommended_model` | `low-local` |

**Wave 3 Dispatch (pi-intercom):**
```typescript
intercom({
  action: "ask",
  to: "fnet3",
  message: "Impl Wave 3: Execute IMPL-SYS-001, IMPL-SYS-002, IMPL-SYS-003 in sequence. Run full test suite with enabled=true and enabled=false. Write completion report. Report all test outputs + git diff + session report."
})
```

---

## Node Allocation Map (Phase 1)

| Node | Models | Assigned Waves | Rationale |
|------|--------|---------------|-----------|
| fnet1 | qwen3.5:4b, qwen3:8b | Wave 1: IMPL-GATE-001 | Simple boolean gate implementation |
| fnet2 | qwen3.5:4b, qwen3:8b | Wave 1: IMPL-INDEX-001 | Entry point wiring |
| fnet3 | qwen3.5:4b, qwen3:8b, gemma4:e4b | Wave 0: CONFIG + Wave 1: EVENT + Wave 3: SYSTEM | Highest capacity; runs config, event suppression, and full suite |
| fnet4 | qwen3.5:4b, qwen3:8b, gemma4:e4b | Wave 1: IMPL-FALLBACK-001 | Fallback routing logic |
| fnet5 | qwen3.5:4b, qwen3:8b, gemma4:e4b | Wave 2: IMPL-PERSIST-001/002 | Session persistence implementation |
| fnet6 | qwen3.5:4b, qwen3:8b, gemma4:e4b | Wave 2: IMPL-DOC-001 | Documentation population |
| fnet7 | qwen3.5:4b, qwen3:8b | Wave 1: IMPL-FOOTER-001 | Footer rendering implementation |

**Utilization:** 7/7 nodes active across 4 waves.

---

## Wave Gate Rules (Phase 1)

```
Wave 0: CONFIG (sequential on fnet3)
    │
    ├── IMPL-CONFIG-001  ──┐
    ├── IMPL-CONFIG-002  ──┼── ALL PASS? ──→ Wave 0 complete
    └── IMPL-HARNESS-001 ──┘         │
                                     ├── NO → Fix and re-run Wave 0
                                     │
                                     ├── YES → Start Wave 1 (parallel across fnet1, fnet2, fnet7, fnet3, fnet4)

Wave 1: CORE LOGIC (parallel)
    │
    ├── IMPL-GATE-001    ──┐
    ├── IMPL-INDEX-001   ──┤
    ├── IMPL-FOOTER-001  ──┼── ALL PASS? ──→ Wave 1 complete
    ├── IMPL-EVENT-001   ──┤         │
    └── IMPL-FALLBACK-001┘          ├── NO → Fix and re-run Wave 1
                                    │
                                    ├── YES → Start Wave 2 (parallel across fnet5, fnet6)

Wave 2: PERSISTENCE + DOC (parallel)
    │
    ├── IMPL-PERSIST-001 ──┐
    ├── IMPL-PERSIST-002 ──┼── ALL PASS? ──→ Wave 2 complete
    └── IMPL-DOC-001     ──┘         │
                                     ├── NO → Fix and re-run Wave 2
                                     │
                                     ├── YES → Start Wave 3 (sequential on fnet3)

Wave 3: SYSTEM VERIFICATION (sequential on fnet3)
    │
    ├── IMPL-SYS-001 ──┐
    ├── IMPL-SYS-002 ──┼── ALL PASS? ──→ Phase 1 complete
    └── IMPL-SYS-003 ──┘         │
                                 ├── NO → Fix and re-run Wave 3
                                 │
                                 ├── YES → Phase 1 GREEN complete. Ready for Phase 2 (refactor).
```

---

## Handoff Checklist

- [x] 14 implementation sub-steps decomposed across 4 waves.
- [x] Wave 0 (config schema) is sequential prerequisite for all other waves.
- [x] Each sub-step maps to specific Phase 0 test stubs that must turn GREEN.
- [x] Each sub-step has step_id, workspace, target_file, target_node, acceptance_criteria.
- [x] Each sub-step has recommended_model and fallback_model per AGENTS.md.
- [x] No sub-step exceeds 20 min estimated effort.
- [x] Wave gate rules enforce dependency order (config → gatekeeper → hooks → events → footer).
- [x] Parallel dispatch protocol defined using pi-intercom.
- [x] Node allocation map shows 7/7 nodes utilized.
- [x] Phase 1 completion criteria: all 20 Phase 0 test stubs pass (GREEN).

---

**Next Action:** Low Cloud Model (`qwen3.5:397b`) reads this decomposition, reads [`AGENTS.md`](./AGENTS.md), and begins Phase 1 orchestration.

**Wave 0 dispatch:** Send to `fnet3` via pi-intercom: "Execute IMPL-CONFIG-001, IMPL-CONFIG-002, IMPL-HARNESS-001."

**Plan Owner:** High Cloud Model (`kimi-k2.6`) — Phase 1 decomposition complete. Standing by for user escalation requests only.  
**No further action from high cloud model. Passing control to low cloud model.**
