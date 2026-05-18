# [S-TIGHT] TI-038 Implementation Plan — Phased build of sshfs-integration skill with 4 parallel workstreams, delivering automatic mount/routing/unmount for the decompose-execute-verify pipeline.

**Issue Home:** [0-ISSUE.md](./0-ISSUE.md)  
**Plan:** [1-PLAN.md](./1-PLAN.md) (this file)  
**Updated:** 2026-05-14 12:00:00 US Eastern  
**Status:** 📋 **PLANNED**

---

## Navigation

| Need | Location |
|------|----------|
| Up to issue definition | [0-ISSUE.md](./0-ISSUE.md) |
| Session notes | [sessions/](./sessions/) |
| Status snapshots | [status/](./status/) |
| Test plans + evidence | [tests/](./tests/) |
| Prompts that drove work | [prompts/](./prompts/) |
| Decomposition docs | [decompositions/](./decompositions/) |
| Troubleshooting | [troubleshooting/](./troubleshooting/) |

---

## Parallel Workstreams

| Stream | Owner | Focus | File Locations |
|--------|-------|-------|---------------|
| **A — Scripts** | Bash engineering | `ensure-mounted`, `route-tasks`, `execute-on-node`, `collect-results` | `scripts/` |
| **B — Python modules** | Core logic | `detect_parallel_need`, `validate_decomposition`, `decompose_task`, `synthesize_results` | `src/` |
| **C — Tests** | QA | pytest suite, bats suite, acceptance tests | `tests/` |
| **D — Docs** | Technical writing | Architecture, integration guide, wiki, README | `docs/`, `wiki/` |

---

## Phase 1: Foundation (Week 1)

### [S-TIGHT] Build test harness, mount lifecycle policy, and parallel-need detection heuristics for the SSHFS integration skill.

### Deliverables

- [ ] T-001 — pytest fixtures for SSHFS mocking (`tests/conftest.py`)
- [ ] T-002 — `sshfs-accessible` script mocking layer (`tests/mocks/`)
- [ ] T-003 — Mock mount state manager for tests (`tests/mocks/mount_state.py`)
- [ ] T-004 — Mock node topology for isolated test runs (`tests/mocks/nodes.py`)
- [ ] Stream A: `ensure-mounted.sh` script — auto-mount gate before task fan-out
- [ ] Stream A: `verify-mounts.sh` integration — consume `--json` output for mount state
- [ ] Stream A: Mount lifecycle policy scripts (`mount-policy-check.sh`, `mount-policy-apply.sh`)
- [ ] Stream B: `src/detect_parallel_need.py` — heuristic detection of multi-node task need
- [ ] Stream B: `src/detect_parallel_need.py` — unit tests (`tests/test_detect_parallel_need.py`)
- [ ] Stream C: pytest suite baseline with 100% pass rate on Phase 1 deliverables
- [ ] Stream D: Architecture draft — component interaction diagram
- [ ] Stream D: `scripts/` and `src/` directory structure README

### Success Criteria

1. `pytest tests/` passes with zero failures for T-001 through T-004 fixtures.
2. `ensure-mounted.sh` returns exit code 0 when all required nodes are mounted, non-zero with actionable stderr when any node is unmounted.
3. `detect_parallel_need.py` correctly identifies multi-node dispatch need with >90% precision on a hand-crafted test corpus of 20 prompts.
4. Mount lifecycle policy scripts execute without manual intervention and log decisions to stdout.

### Dependencies

- [TI-033](../../../issues/ti033-lab-sshfs-mount/0-ISSUE.md) — SSHFS mount scripts must exist and be callable.
- `sshfs-accessible` skill package must be installed locally for script reuse.

### Risk and Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Mock SSHFS diverges from real behavior | Medium | High | Keep mocks versioned alongside `sshfs-accessible`; run reconciliation script weekly |
| `detect_parallel_need.py` heuristic precision <90% | Medium | Medium | Add labeled prompt corpus; retrain with 50+ examples; human-in-the-loop fallback for edge cases |
| Lab node topology changes break mount state logic | Low | High | Consume live `nodes.json` in tests; fail fast with descriptive error |

### Estimated Hours

| Stream | Hours |
|--------|-------|
| A — Scripts | 4-5 |
| B — Python modules | 3-4 |
| C — Tests | 2-3 |
| D — Docs | 2 |
| **Phase 1 Total** | **11-14** |

---

## Phase 2: Core Routing (Week 1–2)

### [S-TIGHT] Implement task routing, node dispatch execution, and decomposition engine with schema validation.

### Deliverables

- [ ] T-005 — `route-tasks.sh` pytest integration tests (`tests/test_route_tasks.py`)
- [ ] T-006 — `execute-on-node.sh` pytest integration tests (`tests/test_execute_on_node.py`)
- [ ] T-007 — Decomposition schema validation pytest tests (`tests/test_validate_decomposition.py`)
- [ ] Stream A: `route-tasks.sh` — reads node health + mount status, assigns tasks to nodes
- [ ] Stream A: `route-tasks.sh` — handles unmounted-node exclusion with fallback to orchestrator
- [ ] Stream A: `execute-on-node.sh` — dispatches a single task to a lab node via SSH, streams logs back
- [ ] Stream A: `execute-on-node.sh` — captures exit code and stderr for synthesis
- [ ] Stream B: `src/validate_decomposition.py` — JSON schema validation for decompose-execute-verify task specs
- [ ] Stream B: `src/decompose_task.py` — decomposition engine, calls `detect_parallel_need` and `ensure-mounted` hook before fan-out
- [ ] Stream B: `src/decompose_task.py` — unit tests (`tests/test_decompose_task.py`)
- [ ] Stream C: bats suite for bash scripts (`tests/bats/`)
- [ ] Stream C: pytest coverage report ≥80% for Phase 2 modules
- [ ] Stream D: Integration guide draft — how to wire into `decompose-execute-verify`

### Success Criteria

1. `route-tasks.sh` dispatches tasks to mounted nodes only; unmounted nodes receive score penalty of −999 (effective exclusion).
2. `execute-on-node.sh` completes a no-op task (`echo "hello"`) on each lab node and returns correct exit code within 10 seconds.
3. `validate_decomposition.py` rejects invalid task specs with detailed error messages; accepts all valid specs from `decompose-execute-verify` test corpus.
4. `decompose_task.py` end-to-end mock run: input prompt → decomposed tasks → route calls → execution calls, with all steps traceable in logs.

### Dependencies

- Phase 1 completion: T-001 through T-004, `ensure-mounted.sh`, `detect_parallel_need.py`
- `node-router` skill must expose scoring API or CLI for mount-status consumption.
- `decompose-execute-verify` skill package installed for schema alignment.

### Risk and Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| SSH latency causes `execute-on-node.sh` timeouts | High | High | Implement 60s timeout with retry (1 retry); log slow nodes for topology review |
| `node-router` scoring API changes | Low | Medium | Pin to known version; add contract test that alerts on schema drift |
| Decomposition schema mismatch with `decompose-execute-verify` | Medium | High | Joint review session with TI-011 owner; shared JSON schema in `src/schemas/decomposition.json` |

### Estimated Hours

| Stream | Hours |
|--------|-------|
| A — Scripts | 5-6 |
| B — Python modules | 5-6 |
| C — Tests | 3-4 |
| D — Docs | 2-3 |
| **Phase 2 Total** | **15-19** |

---

## Phase 3: Collection & Synthesis (Week 2)

### [S-TIGHT] Build result collection, synthesis, and error recovery logic for multi-node parallel execution.

### Deliverables

- [ ] T-008 — `collect-results.sh` pytest integration tests (`tests/test_collect_results.py`)
- [ ] T-009 — Result synthesis pytest tests (`tests/test_synthesize_results.py`)
- [ ] T-010 — Error recovery and retry logic pytest tests (`tests/test_error_recovery.py`)
- [ ] Stream A: `collect-results.sh` — gathers stdout, stderr, exit codes, and artifacts from all nodes
- [ ] Stream A: `collect-results.sh` — supports partial collection when some nodes fail
- [ ] Stream B: `src/synthesize_results.py` — merges partial results, produces unified output for user
- [ ] Stream B: `src/synthesize_results.py` — marks incomplete results with confidence flag
- [ ] Stream B: Error recovery module (`src/error_recovery.py`) — retry with exponential backoff
- [ ] Stream B: `src/error_recovery.py` — max retry count configurable, default 3
- [ ] Stream B: `src/error_recovery.py` — fallback to orchestrator after max retries
- [ ] Stream C: End-to-end mock test: 3-node parallel execution with 1 simulated node failure
- [ ] Stream C: bats suite expanded for result collection scripts
- [ ] Stream D: Error recovery runbook

### Success Criteria

1. `collect-results.sh` returns a JSON blob with per-node results, including failed nodes with error classification.
2. `synthesize_results.py` produces a coherent merged output when ≥2 nodes succeed; flags incomplete results when <50% nodes succeed.
3. Error recovery retries failed tasks up to 3 times with backoff [1s, 3s, 9s]; notifies orchestrator on final failure.
4. End-to-end mock test: one node fails, retries exhaust, remaining two nodes' results are still synthesized and returned.

### Dependencies

- Phase 2 completion: `route-tasks.sh`, `execute-on-node.sh`, `decompose_task.py`
- `synthesize_results.py` schema must align with TI-011 output expectations.

### Risk and Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Result file corruption on slow nodes | Medium | Medium | Checksum validation (MD5) on collected artifacts; re-collect on mismatch |
| Synthesis produces hallucinated data from partial results | Medium | High | Confidence flag enforcement — downstream consumers MUST check `confidence: low` |
| Retry storm overwhelms healthy nodes | Low | High | Exponential backoff with jitter; circuit breaker after 5 total failures |

### Estimated Hours

| Stream | Hours |
|--------|-------|
| A — Scripts | 3-4 |
| B — Python modules | 4-5 |
| C — Tests | 3-4 |
| D — Docs | 1-2 |
| **Phase 3 Total** | **11-15** |

---

## Phase 4: Integration (Week 2–3)

### [S-TIGHT] Package as installable skill, wire into decompose-execute-verify framework, run end-to-end acceptance on live lab nodes.

### Deliverables

- [ ] Stream A: Final script polish and shellcheck compliance (`scripts/*.sh`)
- [ ] Stream B: `package.json` with pi skill registration, metadata, dependencies
- [ ] Stream B: `SKILL.md` — agent skill manifest with triggers and load rules
- [ ] Stream D: `README.md` — install instructions, quickstart, architecture overview
- [ ] Framework integration hook: `decompose-execute-verify` calls `sshfs-integration` auto-mount before fan-out
- [ ] Framework integration hook: `synthesize_results.py` triggers lazy-unmount on completion
- [ ] Orchestration framework chain updates in TI-011: node-router consumes mount status
- [ ] End-to-end acceptance test on live lab nodes (7 nodes)
- [ ] Acceptance test: 10 consecutive runs, 100% success rate
- [ ] Stream D: Architecture diagrams finalized (PNG + source in `docs/diagrams/`)

### Success Criteria

1. `package.json` validates against pi skill schema (`pi skill validate`).
2. `SKILL.md` declares auto-load triggers: `parallel`, `lab node`, `cross-node filesystem`, `fan out`.
3. One user prompt for parallel analysis triggers the full chain: auto-mount → decompose → route → execute → collect → synthesize → lazy-unmount, with no manual mount commands.
4. End-to-end acceptance test: 10 consecutive runs on 7 lab nodes, 0 manual interventions, 100% pass rate.
5. All changes backward-compatible: `sshfs-accessible` manual scripts continue to work independently.

### Dependencies

- Phase 3 completion: all collection, synthesis, and error recovery modules
- TI-011 must accept framework hooks for mount/unmount triggers
- Live lab nodes must be online and reachable via SSH

### Risk and Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Live node offline during acceptance test | Medium | High | Pre-test health ping; accept test with N−1 nodes if one is down |
| TI-011 framework rejects integration hooks | Low | High | Early prototype hook with TI-011 owner in Phase 2; do not wait until Phase 4 |
| Package schema changes break pi skill registration | Low | Medium | Run `pi skill validate` in CI before merge; pin to current pi version |

### Estimated Hours

| Stream | Hours |
|--------|-------|
| A — Scripts | 2-3 |
| B — Python modules | 3-4 |
| C — Tests (acceptance) | 4-6 |
| D — Docs + packaging | 3-4 |
| **Phase 4 Total** | **12-17** |

---

## Phase 5: Documentation & Polish (Week 3)

### [S-TIGHT] Finalize all documentation, publish wiki operational page, establish semantic versioning at 0.1.0.

### Deliverables

- [ ] Stream D: Wiki operational page — this issue's knowledge distilled for reference
- [ ] Stream D: Integration guide — step-by-step for adopters (target: new agent reads once, deploys)
- [ ] Stream D: Architecture diagrams finalized and linked from README
- [ ] Stream D: README with install instructions, quickstart, troubleshooting section
- [ ] Stream D: `CHANGELOG.md` — initial version 0.1.0 entry
- [ ] Semantic versioning established: `0.1.0` for first release
- [ ] Git tag `v0.1.0` pushed to repository
- [ ] Stream C: Final regression suite run — all tests pass
- [ ] Stream A: Final shellcheck and lint pass on all bash scripts
- [ ] Stream B: Final type check and lint pass on all Python modules
- [ ] Issue home updated: `0-ISSUE.md` deliverables checkboxes marked complete

### Success Criteria

1. README enables a new team member to install, configure, and run a single-node test within 15 minutes.
2. Wiki operational page is discoverable from domain manifest and backlinks to this issue home.
3. All diagrams are version-controlled (source + rendered PNG).
4. `CHANGELOG.md` follows Keep a Changelog format.
5. `pi skill install` works from the package directory with no additional manual steps.

### Dependencies

- Phase 4 completion: acceptance test passed, package validated
- Domain manifest (`technical-infrastructure/manifest.md`) must be updated with skill pointer.

### Risk and Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Documentation drifts from implementation | Medium | Medium | Generate CLI help text from source; inline docs in `--help` are source of truth |
| Install instructions miss OS-specific dependencies | Medium | Medium | Test install on clean macOS and Ubuntu VMs; automate via CI |
| Versioning not enforced in subsequent PRs | Low | Low | Add `pi skill validate` to pre-commit hook |

### Estimated Hours

| Stream | Hours |
|--------|-------|
| A — Scripts (polish) | 1-2 |
| B — Python modules (polish) | 1-2 |
| C — Tests (regression) | 1-2 |
| D — Docs | 3-4 |
| **Phase 5 Total** | **6-10** |

---

## Summary

| Phase | Stream A | Stream B | Stream C | Stream D | Total Hours |
|-------|----------|----------|----------|----------|-------------|
| Phase 1: Foundation | 4-5 | 3-4 | 2-3 | 2 | 11-14 |
| Phase 2: Core Routing | 5-6 | 5-6 | 3-4 | 2-3 | 15-19 |
| Phase 3: Collection & Synthesis | 3-4 | 4-5 | 3-4 | 1-2 | 11-15 |
| Phase 4: Integration | 2-3 | 3-4 | 4-6 | 3-4 | 12-17 |
| Phase 5: Documentation & Polish | 1-2 | 1-2 | 1-2 | 3-4 | 6-10 |
| **Grand Total** | **15-20** | **16-21** | **13-19** | **11-15** | **55-75** |

**Duration:** 3 weeks (Week 1–3)  
**Critical Path:** Stream B → Phase 2 → Phase 3 → Phase 4 (longest chain: ~40-44 hours)  
**Team Size:** 1-2 engineers (all streams can be owned by one engineer with sequential priority; Stream C can parallelize if second engineer available)
