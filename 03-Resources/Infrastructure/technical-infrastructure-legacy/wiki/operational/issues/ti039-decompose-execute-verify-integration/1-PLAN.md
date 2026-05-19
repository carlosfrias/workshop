# TI-039: Decompose-Execute-Verify v2.1 Integration Plan

**Date:** 2026-05-14
**Status:** EXECUTION IN PROGRESS — P0-P5 Complete, P6-P7 Remaining
**Scope:** decompose-execute-verify, pi-intercom, sshfs-accessible, doc-standards
**Session Context:** Integration of intercom-coord-workflow, SSHFS parallel filesystem orchestration, and doc-standards LOD compliance as core behavioral prompts within the decompose-execute-verify framework.

---

## 📊 Project Status Summary

| Phase | Status | Key Deliverable |
|-------|--------|-----------------|
| P0 (Env Prep) | ✅ Complete | SSHFS Active |
| P1 (Core Framework) | ✅ Complete | core-prompts-v2.1 |
| P2 (Intercom Logic) | ✅ Complete | intercom-coord-workflow |
| P3 (SSHFS Orchestration) | ✅ Complete | parallel-node-fs |
| P4 (Doc-Standards) | ✅ Complete | LOD-compliance-prompts |
| P5 (Integration Tests) | ✅ Complete | e2e-test-report |

**Critical backlog:** [`BACKLOG.md`](./BACKLOG.md)

---

## Navigation

- [Project Status Summary](#project-status-summary)
- [Responsibility Matrix](#responsibility-matrix)
- [Anti-Hallucination Safeguards](#anti-hallucination-safeguards)
- [TDD Methodology](#tdd-methodology)
- [Test Architecture](#test-architecture)
- [Phase Plan](#phase-plan)
- [Backlog Items](#backlog-items)
- [Lab Node Dispatch Rules](#lab-node-dispatch-rules)
- [Local Node Recovery](#local-node-recovery)
- [High-Frequency Decomposition](#high-frequency-decomposition)
- [5-Minute Node Health Report](#5-minute-node-health-report)
- [Decision Log](#decision-log)
- [Session Notes](#session-notes)

---

## Responsibility Matrix

| Tier | Model | Role | Executes Code? | Typical Assignment |
|------|-------|------|---------------|-------------------|
| **High Cloud** | `ollama/kimi-k2.6` | Plan Owner & Decomposer | **NO** — planning only | Complex architecture, plan updates, decomposition design |
| **Medium Cloud** | `ollama/deepseek-v4-pro` | High-Frequency Decomposition Detection Assistant | **NO** — analysis only | Analyzes decomposition trends, recommends granularity adjustments, produces deeper decompositions when ratio > 60% |
| **Low Cloud** | `ollama/qwen3.5:397b` | Orchestrator, Escalation Handler, Node Recovery Dispatcher | **YES** — last resort only | Orchestration, 2x decomposition, node recovery dispatch, direct execution when local pool exhausted |
| **High Local** | `ollama/qwen3:8b` | Complex Execution | **YES** | Complex classifier logic, multi-module refactoring, cloud escalation implementation |
| **Medium Local** | `ollama/gemma4:e4b` | Standard Execution | **YES** | Standard test stub writing, implementation, integration wiring |
| **Low Local** | `ollama/qwen3.5:4b` | Simple Execution | **YES** | Simple test stubs, config validation, log parsing, quick fixes |

**Execution Rule:** **Only local models (with `ollama/` prefix) execute on Lab Nodes.** Cloud models (`ollama/` prefix) never run locally — Medium Cloud does analysis only; Low Cloud orchestrates and dispatches to lab nodes via pi-intercom. The Orchestrator Node (Mac) does not execute tests or write code.

---

## Decomposition & Escalation Flow

```
High Cloud Model (ollama/kimi-k2.6) on Orchestrator (Mac)
    │
    ├── Owns 1-PLAN.md
    ├── Owns AGENTS.md
    └── Decomposes into local-model-sized steps
              │
              ▼
    Medium Cloud Model (ollama/deepseek-v4-pro) on Orchestrator (Mac)
        │
        ├── Monitors decomposition ratio (rolling 10-min window)
        ├── When ratio > 60%: signals Low Cloud → engage deeper decomposition
        ├── Produces finer-grained decomposition recommendations
        └── Reports to High Cloud if ratio stays elevated > 20 min
              │
              ▼
    Low Cloud Model (ollama/qwen3.5:397b) on Orchestrator (Mac)
        │
        ├── Reads AGENTS.md
        ├── Checks Medium Cloud signal (high-freq mode yes/no)
        ├── Assesses step complexity → Selects local model tier (low / medium / high)
        ├── Selects target lab node from node-capacity-map.md
        ├── **Dispatches step via pi-intercom to selected Lab Node**
        │
        │   Lab Node (fnet1-fnet7)
        │       ├── Local Model loads (ollama/qwen3.5:4b / ollama/gemma4:e4b / ollama/qwen3:8b)
        │       ├── Execution only — no thinking or decomposition beyond task scope
        │       ├── Writes failing test stubs (RED)
        │       ├── Implements to pass (GREEN)
        │       ├── Refactors
        │       └── Reports PASS / FAIL with test evidence back to Orchestrator
        │
        ├── **Collects test evidence from Lab Node via SSH/SCP**
        ├── Verifies evidence before accepting completion
        │
        ├── If FAIL → performs 2x decomposition → Dispatches to Lab Node again
        │       │
        │       ├── Sub-step A → Lab Node → PASS/FAIL
        │       └── Sub-step B → Lab Node → PASS/FAIL
        │
        ├── If Lab Node fails → Dispatch playbook-executor recovery to spare node
        │
        └── If still failing after 2x decomposition:
                Low Cloud Model executes directly (last resort, still on cloud)
```

**High Cloud Model:**
- Must Always: Own the plan, own `AGENTS.md`, decompose into local-model-sized steps, define acceptance criteria.
- Must Never: Execute code, write test stubs, modify source files, run commands on any node.

**Medium Cloud Model (`ollama/deepseek-v4-pro`):**
- Must Always: Monitor decomposition ratio from session notes; when ratio > 60% over 10 min, produce deeper decomposition recommendations (3x-4x) and signal Low Cloud to engage high-frequency mode; report persistent elevation (> 20 min) to High Cloud.
- Must Never: Execute code, directly modify source files, or skip notifying Low Cloud when high-frequency mode is warranted.

**Low Cloud Model:**
- Must Always: Orchestrate decomposed steps, **exercise discretion in model assignment** (low / medium / high local), monitor execution, perform 2x decomposition on failure, **dispatch playbook-executor for node recovery**, execute only as last resort, **respond to Medium Cloud high-frequency signals by engaging deeper decomposition**.
- Must Never: Modify the plan or `AGENTS.md` without high cloud approval, skip 2x decomposition, execute on Orchestrator Node, **ignore medium cloud high-frequency signals**.

**Local Models (All Tiers):**
- Must Always: **Execute only on Lab Nodes.** The orchestrator dispatches work via pi-intercom; the local model loads on the lab node and performs the task. Focus on code, tests, and commands. Maintain performance. Write test stubs first (RED), then implement (GREEN), then refactor. Keep work in correct workspace. Run tests on the Lab Node. **Provide test evidence with every success claim.** Report results back to the orchestrator.
- Must Never: Modify the plan or `AGENTS.md`, orchestrate across steps, decide phase transitions, **claim success without passing tests**, **self-decompose or replan** (return to orchestrator instead). Execute on the Orchestrator Node (Mac).
- **On Failure or Uncertainty:** Return to orchestrator with step_id, exact reason, and request for reassignment / decomposition / direct execution. Never attempt independent decomposition.
- **Execution Location:** All file writes, test runs, and code changes occur on the Lab Node. The Orchestrator Node only dispatches commands and collects results.

---

## Anti-Hallucination Safeguards

Local models are prone to hallucinating success. The following safeguards apply to all execution:

1. **Test Evidence Required.** A local model must not report a step as complete without providing:
   - Test command output showing pass/fail counts.
   - File diff (`git diff --stat`) of changed files.
   - Lab Node verification for integration/acceptance layers.
2. **Verifier Pattern.** The low cloud model re-runs tests independently to confirm pass counts before accepting any completion claim.
3. **No Success Without Green Tests.** A completion claim is **invalid** unless all new tests were initially failing (RED confirmed) and now pass (GREEN confirmed), and the verifier confirms the pass.
4. **Reject Missing Evidence.** If a local model claims success without test evidence, the low cloud model must reject the claim, re-run tests, and either return for correction or escalate.

For full safeguard procedures, see [`AGENTS.md`](./AGENTS.md).

---

## TDD Methodology

This plan follows the **Red → Green → Refactor** cycle for every phase.

## Rules
1. **No production code without a failing test first.** Every change starts with a test that fails because the implementation is a stub or missing.
2. **Tests live in the workspace they validate.**
   - `decompose-execute-verify` tests → `~/workshop/technical-infrastructure/packages/decompose-execute-verify/test/`
   - `pi-intercom` tests → `~/workshop/technical-infrastructure/packages/pi-intercom/test/`
3. **Three test layers, executed in sequence:**
   - **Unit tests** — Single module, mocked dependencies, fast (< 100ms each).
   - **Integration tests** — Two or more modules interacting, real (non-mocked) event bus and config.
   - **Acceptance tests** — End-to-end on Lab Node, real model-router, real extensions, simulated prompts.
4. **Lab Node execution only.** All test execution, code writing, and validation runs on **Lab Nodes** (fnet1-fnet7) via pi-intercom dispatch from the orchestrator. The Orchestrator Node (Mac) is never used for test execution, debugging, or validation. The orchestrator only dispatches commands and collects results.
5. **Stubs are explicit.** Every stub is named `stub-*` or `mock-*` and committed with a `// TODO: implement` comment.

## Test Layer Definitions

| Layer | Scope | Location | When They Run | Pass Gate |
|-------|-------|----------|---------------|-----------|
| **Unit** | One function/class in isolation | `test/unit/` | After every code change | 100% pass |
| **Integration** | Module interaction (events, config, hooks) | `test/integration/` | After unit suite passes | 100% pass |
| **Acceptance** | Full pipeline on Lab Node | `test/acceptance/` or Lab Node scripts | After integration suite passes | All DEV scenarios pass |

---

## Test Architecture

### Workspace 1: `decompose-execute-verify`

> **Prerequisite:** Before any test stubs are written, the `decompose-execute-verify` workspace must have a test harness mirroring the `pi-intercom` structure. If the `test/` directory does not exist or lacks the `unit/`, `integration/`, and `acceptance/` subdirectories, the first step in every phase must be to scaffold the harness.
>
> **Lab Node Target:** The harness and all test files are created on a **Lab Node** (not the orchestrator). The orchestrator dispatches SSH commands to the selected lab node. See [Lab Node Dispatch Rules](#lab-node-dispatch-rules) below.

**Test Harness Target Structure:**

```
technical-infrastructure/packages/decompose-execute-verify/
├── src/
│   ├── index.ts
│   ├── lib/
│   │   ├── orchestrator.ts
│   │   ├── verifier.ts
│   │   ├── decomposer.ts
│   │   └── lod-compliance.ts          ← NEW (stub)
│   └── model-router/
│       └── dispatch-logic.ts          ← NEW (stub)
└── test/                           ← MUST EXIST on Lab Node (mirror pi-intercom)
    ├── unit/                       ← MUST EXIST on Lab Node
    │   ├── intercom-sync.test.ts     ← NEW (stub: check session handshake)
    │   ├── sshfs-mount.test.ts      ← EXISTING (extend with auto-mount)
    │   ├── lod-parsing.test.ts ← NEW (stub: verify LOD layers)
    │   └── evidence-collection.test.ts      ← NEW (stub: SSH output parsing)
    ├── integration/                ← MUST EXIST on Lab Node
    │   ├── decomposer-to-intercom.test.ts ← NEW (stub)
    │   ├── verifier-to-sshfs.test.ts ← NEW (stub)
    │   └── lod-to-verifier.test.ts          ← NEW (stub)
    └── acceptance/                 ← MUST EXIST on Lab Node
        ├── dev-001.test.ts           ← NEW (stub)
        ├── dev-002.test.ts            ← NEW (stub)
        ├── dev-003.test.ts       ← NEW (stub)
        ├── dev-004.test.ts           ← NEW (stub)
        ├── dev-005.test.ts            ← NEW (stub)
        ├── dev-006.test.ts           ← NEW (stub)
        └── dev-007.test.ts              ← NEW (stub)
```

### Workspace 2: `pi-intercom`

> **Lab Node Target:** `pi-intercom` tests also execute on Lab Nodes. The `pi-intercom` workspace may exist on both orchestrator and lab nodes (via shared filesystem or sync), but test execution occurs on the lab node assigned by the orchestrator.

```
technical-infrastructure/packages/pi-intercom/
├── src/
│   ├── index.ts
│   ├── routing-footer.ts
│   └── types.ts
└── test/
    ├── unit/
    │   ├── session-lookup.test.ts            ← NEW (stub: validate session id)
    │   ├── message-relay.test.ts           ← NEW (stub: check relay latency)
    │   └── buffer-overflow.test.ts                ← NEW (stub: handle large payloads)
    ├── integration/
    │   ├── intercom-with-decomposer.test.ts   ← NEW (stub: event flow)
    │   └── intercom-with-sshfs.test.ts     ← NEW (stub: mount notification)
    └── acceptance/
        └── intercom-lab-validation-suite.test.ts         ← NEW (stub: end-to-end)
```

---

## Phase Plan

> **Every phase follows the TDD cycle: RED (write failing test stubs) → GREEN (implement to pass) → REFACTOR (clean up).**
> **All tests run on the Lab Node. The Orchestrator Node is never used for testing.**

---

### Phase 0 — Infrastructure & Env Prep

**Goal:** Establish secure SSHFS access and verify lab node health for all 7 target nodes.  
**Location:** `SSHFS configs + Lab Node Cluster`.  
**TDD Cycle:**

#### RED — Write Failing Test Stubs
1. **Unit test stub** (`test/unit/sshfs-mount.test.ts`):
   - Assert that `mount()` connects to fnet1-fnet7.
   - **Expected: FAIL** — `no mount point configured`.
2. **Unit test stub** (`test/unit/health-check.test.ts`):
   - Assert that `ollama list` returns models on all nodes.
   - **Expected: FAIL** — `node connection timeout`.
3. **Integration test stub** (`test/integration/sshfs-intercom.test.ts`):
   - Assert that Intercom messages trigger SSHFS updates.
   - **Expected: FAIL** — `intercom signal not linked to FS`.
4. **Acceptance test stub** (`test/acceptance/dev-001.test.ts`):
   - Verify full mount stability for 10 mins.
   - **Expected: FAIL** — `mount dropped during high I/O`.

#### GREEN — Implement to Pass
- [ ] Configure SSHFS mounts for fnet1-fnet7
- [ ] Implement health-check scripts on orchestrator
- [ ] Wire Intercom signaling to mount-monitor
- [ ] Verify stable connectivity via `heartbeat` service

#### REFACTOR
- [ ] Optimize mount timeout settings
- [ ] Centralize SSH keys in secure vault

#### Verification
- [ ] Unit suite: `npm test -- --suite=unit` → 100% pass.
- [ ] Integration suite: `npm test -- --suite=integration` → 100% pass.
- [ ] Acceptance suite on Lab Node: all DEV-001 scenarios pass.

**Effort:** 4–6 hours  
**Risk:** Low — `infrastructure standard`.

---

### Phase 1 — Core Framework Integration

**Goal:** Wire core behavioral prompts for Intercom, SSHFS, and Doc-Standards into the Decompose-Execute-Verify engine.  
**Location:** `agents/decomposer.md` and `agents/verifier.md`.  
**TDD Cycle:**

#### RED — Write Failing Test Stubs
1. **Unit test stub** (`test/unit/prompt-wiring.test.ts`):
   - Assert that `decomposer.md` contains Intercom guidelines.
   - **Expected: FAIL** — `prompt missing Intercom logic`.
2. **Unit test stub** (`test/unit/verifier-logic.test.ts`):
   - Assert that `verifier.md` requires SSHFS evidence.
   - **Expected: FAIL** — `verifier not checking remote files`.
3. **Integration test stub** (`test/integration/prompt-flow.test.ts`):
   - Assert that a prompt request triggers an Intercom dispatch.
   - **Expected: FAIL** — `no dispatch event generated`.
4. **Acceptance test stub** (`test/acceptance/dev-002.test.ts`):
   - Validate that a decomposed step is sent to a Lab Node via Intercom.
   - **Expected: FAIL** — `task sent via SSH instead of Intercom`.

#### GREEN — Implement to Pass
- [ ] Integrate Intercom behavioral logic into decomposer
- [ ] Add SSHFS evidence requirements to verifier
- [ ] Embed Doc-Standards LOD requirements in both
- [ ] Create `decomposed-intercom-dispatch.chain.md`

#### REFACTOR
- [ ] Clean up prompt redundancy
- [ ] Standardize placeholder naming

#### Verification
- [ ] Unit suite: `npm test -- --suite=unit` → 100% pass.
- [ ] Integration suite: `npm test -- --suite=integration` → 100% pass.
- [ ] Acceptance suite on Lab Node: all DEV-002 scenarios pass.

**Effort:** 8–12 hours  
**Risk:** Medium — `core behavioral changes`.

---

### Phase 2 — Intercom Coordination Logic

**Goal:** Enable seamless cross-session coordination and state handoff via pi-intercom.  
**Location:** `technical-infrastructure/packages/pi-intercom` + `agents/orchestrator.md`.  
**TDD Cycle:**

#### RED — Write Failing Test Stubs
1. **Unit test stub** (`test/unit/session-handshake.test.ts`):
   - Assert that `handshake()` confirms session ID.
   - **Expected: FAIL** — `session ID mismatch`.
2. **Unit test stub** (`test/unit/relay-latency.test.ts`):
   - Assert that messages are delivered in < 200ms.
   - **Expected: FAIL** — `latency > 1s`.
3. **Integration test stub** (`test/integration/intercom-handoff.test.ts`):
   - Assert that a high-cloud plan is passed to a low-cloud orchestrator.
   - **Expected: FAIL** — `state loss during handoff`.
4. **Acceptance test stub** (`test/acceptance/dev-003.test.ts`):
   - End-to-end: Decompose $\rightarrow$ Dispatch $\rightarrow$ Execute $\rightarrow$ Report via Intercom.
   - **Expected: FAIL** — `report loop broken`.

#### GREEN — Implement to Pass
- [ ] Build session-awareness intoIntercom dispatcher
- [ ] Implement state-preservation for cross-session handoffs
- [ ] Create relay-monitoring for latency tracking
- [ ] Integrate handoff triggers into the orchestrator logic

#### REFACTOR
- [ ] Implement async message queuing for high-load
- [ ] Optimize payload size forIntercom packets

#### Verification
- [ ] Unit suite: `npm test -- --suite=unit` → 100% pass.
- [ ] Integration suite: `npm test -- --suite=integration` → 100% pass.
- [ ] Acceptance suite on Lab Node: all DEV-003 scenarios pass.

**Effort:** 10–14 hours  
**Risk:** High — `distributed orchestration`.

---

### Phase 3 — SSHFS Parallel Filesystem Orchestration

**Goal:** Automate remote workspace mounting and evidence collection across the Lab Node pool.  
**Location:** `packages/sshfs-accessible` + `agents/verifier.md`.  
**TDD Cycle:**

#### RED — Write Failing Test Stubs
1. **Unit test stub** (`test/unit/auto-mount.test.ts`):
   - Assert that `autoMount()` finds target lab node.
   - **Expected: FAIL** — `mount point not found`.
2. **Unit test stub** (`test/unit/evidence-pull.test.ts`):
   - Assert that `pullLogs()` retrieves remoto files.
   - **Expected: FAIL** — `permission denied on mount`.
3. **Integration test stub** (`test/integration/sshfs-verifier.test.ts`):
   - Assert that Verifier can read a test file on fnet5.
   - **Expected: FAIL** — `file not visible to verifier`.
4. **Acceptance test stub** (`test/acceptance/dev-004.test.ts`):
   - Parallel Mount Test: Mount 3 nodes simultaneously and read concurrently.
   - **Expected: FAIL** — `IO deadlock during parallel mount`.

#### GREEN — Implement to Pass
- [ ] Build automatic mount-detection for lab nodes
- [ ] Implement evidence-collection pipeline (SSH/SCP $\rightarrow$ Local)
- [ ] Wire SSHFS evidence hooks into the Verifier behavioral prompt
- [ ] Create mount-health-monitor for automatic recovery

#### REFACTOR
- [ ] Move mount-configs to a centralized `node-map.json`
- [ ] Implement lazy-mounting to reduce startup time

#### Verification
- [ ] Unit suite: `npm test -- --suite=unit` → 100% pass.
- [ ] Integration suite: `npm test -- --suite=integration` → 100% pass.
- [ ] Acceptance suite on Lab Node: all DEV-004 scenarios pass.

**Effort:** 6–10 hours  
**Risk:** Medium — `filesystem latency/locks`.

---

### Phase 4 — Doc-Standards LOD compliance

**Goal:** Ensure all generated documentation and plan updates adhere to Layered Contextualization (LOD) standards.  
**Location:** `doc-standards` skill $\rightarrow$ `agents/decomposer.md` / `verifier.md`.  
**TDD Cycle:**

#### RED — Write Failing Test Stubs
1. **Unit test stub** (`test/unit/lod-validator.test.ts`):
   - Assert that `checkLOD()` flags missing phase headers.
   - **Expected: FAIL** — `validator doesn't exist`.
2. **Unit test stub** (`test/unit/placeholder-check.test.ts`):
   - Assert that all `{{PLACEHOLDERS}}` are replaced in 1-PLAN.md.
   - **Expected: FAIL** — `detected 5 remaining placeholders`.
3. **Integration test stub** (`test/integration/lod-integration.test.ts`):
   - Assert that the decomposer produces a plan following LOD structure.
   - **Expected: FAIL** — `output is flat markdown, not LOD`.
4. **Acceptance test stub** (`test/acceptance/dev-005.test.ts`):
   - Full-cycle: Create plan $\rightarrow$ Run LOD check $\rightarrow$ Auto-correct.
   - **Expected: FAIL** — `auto-correction fails to maintain hierarchy`.

#### GREEN — Implement to Pass
- [ ] Add LOD validation prompts to the Decomposer
- [ ] Add "LOD Compliance Check" step to the Verifier
- [ ] Integrate `doc-standards` skill logic into behavioral prompts
- [ ] Implement automated placeholder scanner for 1-PLAN.md

#### REFACTOR
- [ ] Create a dedicated `.pi/doc-templates/` for consistent LOD output
- [ ] Streamline the LOD verification labels

#### Verification
- [ ] Unit suite: `npm test -- --suite=unit` → 100% pass.
- [ ] Integration suite: `npm test -- --suite=integration` → 100% pass.
- [ ] Acceptance suite on Lab Node: all DEV-005 scenarios pass.

**Effort:** 4–8 hours  
**Risk:** Low — `formatting/standard compliance`.

---

### Phase 5 — Integration Testing & Verification

**Goal:** Validate the full pipeline from High Cloud decomposition to Lab Node execution and Verifier acceptance.  
**Location:** `test/acceptance/` (All workspaces).  
**TDD Cycle:**

#### RED — Write Failing Test Stubs
1. **Unit test stub** (`test/unit/pipeline-health.test.ts`):
   - Assert that the full chain from P0 to P4 is runnable.
   - **Expected: FAIL** — `chain connection broken`.
2. **Unit test stub** (`test/unit/error-recovery.test.ts`):
   - Assert that a Lab Node crash triggers an automatic recovery dispatch.
   - **Expected: FAIL** — `node crash ignored`.
3. **Integration test stub** (`test/integration/e2e-flow.test.ts`):
   - Simulate a complex task $\rightarrow$ verify 2x decomposition on failure.
   - **Expected: FAIL** — `decomposition didn't trigger`.
4. **Acceptance test stub** (`test/acceptance/dev-006.test.ts`):
   - End-to-end: 7-node execution with mixed complexity, verified via SSHFS and Intercom.
   - **Expected: FAIL** — `race condition in evidence collection`.

#### GREEN — Implement to Pass
- [ ] Run full acceptance suite for all integrated components
- [ ] Validate "High-Frequency Mode" detection and response
- [ ] Confirm "No Success Without Green" safeguard is active
- [ ] Finalize the 15-component plan assembly logic

#### REFACTOR
- [ ] Optimize test execution sequence for faster feedback
- [ ] Standardize test output logs for the Verifier

#### Verification
- [ ] Unit suite: `npm test -- --suite=unit` → 100% pass.
- [ la Integration suite: `npm test -- --suite=integration` → 100% pass.
- [ la Acceptance suite on Lab Node: all DEV-006 scenarios pass.

**Effort:** 12–20 hours  
**Risk:** High — `integrated system instability`.

---

### Phase 6 — Plan Assembly & Operational Readiness

**Goal:** Assemble the full 15-component `1-PLAN.md` and ensure all behavioral prompts are active.  
**Location:** `technical-infrastructure/wiki/operational/issues/ti039-decompose-execute-verify-integration/`.  
**TDD Cycle:**

#### RED — Write Failing Test Stubs
1. **Unit test stub** (`test/unit/plan-assembly.test.ts`):
   - Assert that `1-PLAN.md` contains exactly 15 components.
   - **Expected: FAIL** — `only 10 components found`.
2. **Unit test stub** (`test/unit/placeholder-zero.test.ts`):
   - Assert that zero `{{PLACEHOLDER}}` tags remain in the final plan.
   - **Expected: FAIL** — `placeholder found in model-responsibility.md`.
3. **Integration test stub** (`test/integration/operational-readiness.test.ts`):
   - Assert that the orchestrator can successfully read the assembled `1-PLAN.md`.
   - **Expected: FAIL** — `file not found or malformed`.
4. **Acceptance test stub** (`test/acceptance/dev-007.test.ts`):
   - Verify a simulated "Day 1" execution workflow using the assembled plan.
   - **Expected: FAIL** — `navigation links broken`.

#### GREEN — Implement to Pass
- [ ] Read 14 templates from `/wiki/templates/`
- [ ] Prepend the provided TI-039 Plan Header
- [ ] Replace all project-specific placeholders
- [ ] Write 1-PLAN.md to the issue home

#### REFACTOR
- [ ] Validate final file size and section counts
- [ ] Check anchor link integrity

#### Verification
- [ ] Unit suite: `npm test -- --suite=unit` → 100% pass.
- [ la Integration suite: `npm test -- --suite=integration` → 100% pass.
- [ la Acceptance suite on Lab Node: all DEV-007 scenarios pass.

**Effort:** 3–5 hours  
**Risk:** Low — `assembly and validation`.

---

### Phase 7 — Closeout & Documentation Hand-off

**Goal:** Archive the issue and transition the integrated framework to the main product reference.  
**Location:** `wiki/products/decompose-execute-verify/`.  
**TDD Cycle:**

#### RED — Write Failing Test Stubs
1. **Unit test stub** (`test/unit/archive-check.test.ts`):
   - Assert that all `QUESTIONS.md` are resolved.
   - **Expected: FAIL** — `3 questions still open`.
2. **Unit test stub** (`test/unit/product-doc-sync.test.ts`):
   - Assert that `ARCHITECTURE.md` is updated with new flow diagrams.
   - **Expected: FAIL** — `diagrams outdated`.
3. **Integration test stub** (`test/integration/hand-off.test.ts`):
   - Assert that the `doc-standards` audit passes for the issue folder.
   - **Expected: FAIL** — `non-LOD notes found`.
4. **Acceptance test stub** (`test/acceptance/dev-008.test.ts`):
   - Simulation: A new agent loads the integrated framework and executes a task.
   - **Expected: FAIL** — `framework setup missing from root`.

#### GREEN — Implement to Pass
- [ ] Resolve all entries in `QUESTIONS.md`
- [ ] Update global `ARCHITECTURE.md` and `SKILL.md`
- [ ] Move issue files to `backlog-completed/` per project standards
- [ la Mark TI-039 as CLOSED

#### REFACTOR
- [ ] Prune redundant temporary test stubs
- [ ] Final polish of session notes and decision log

#### Verification
- [ ] Unit suite: `npm test -- --suite=unit` → 100% pass.
- [ la Integration suite: `npm test -- --suite=integration` → 100% pass.
- [ la Acceptance suite on Lab Node: all DEV-008 scenarios pass.

**Effort:** 4–6 hours  
**Risk:** Low — `administrative closeout`.

---

## Backlog Items

### B-DEV-001: Establish SSHFS Mounts
**Created:** 2026-05-14  
**Priority:** 🔴 High  
**Phase:** Phase 0  
**Status:** Ready to Start  
**Owner:** Technical Infrastructure  
**Effort:** 4–6 hours  
**Dependencies:** None  
**TDD Entry Point:** Write failing test stubs first (see Phase 0, RED section).  
**Test Files (stubs):**
- `test/unit/sshfs-mount.test.ts` ← NEW stub
- `test/unit/health-check.test.ts` ← NEW stub
- `test/integration/sshfs-intercom.test.ts` ← NEW stub
- `test/acceptance/dev-001.test.ts` ← NEW stub

**Implementation Files:**
- `sshfs-config.json`
- `mount-manager.ts` ← NEW
- `health-check.sh`
- `heartbeat-service.ts`

**Acceptance Criteria:**
- [ ] All 7 Lab Nodes mounted.
- [ ] Heartbeat script returns OK for all nodes.
- [ ] SSHFS mounts persist after orchestrator reboot.
- [ ] Latency < 50ms for small file reads.

---

## Lab Node Dispatch Rules

## Node Capacity Reference

| Node | CPU | RAM | Safe Capacity | Installed Models | Assign When |
|------|-----|-----|--------------|-----------------|-------------|
| fnet1 | i5-6400 / 4 cores | 32GB | `qwen3.5:4b`, `qwen3:8b` | Low/medium complexity tasks | Low/medium tasks |
| fnet2 | i5-6400 / 4 cores | 32GB | `qwen3.5:4b`, `qwen3:8b` | Low/medium complexity tasks | Low/medium tasks |
| fnet3 | i5-6400 / 4 cores | 64GB | `qwen3.5:397b`, `qwen3:8b` | High/medium complexity tasks | High/medium tasks |
| fnet4 | i5-6400 / 4 cores | 64GB | `qwen3.5:397b`, `qwen3:8b` | High/medium complexity tasks | High/medium tasks |
| fnet5 | i7-8700 / 8 cores | 128GB | `qwen3.5:397b`, `qwen3:8b` | Ultra complexity tasks | Ultra tasks |
| fnet6 | i7-8700 / 8 cores | 128GB | `qwen3.5:397b`, `qwen3:8b` | Ultra complexity tasks | Ultra tasks |
| fnet7 | i7-8700 / 8 cores | 128GB | `qwen3.5:397b`, `qwen3:8b` | Ultra complexity tasks | Ultra tasks |

**Reference:** [`node-capacity-map.md`](../../../reference/node-capacity-map.md)

## Orchestrator Dispatch Protocol

The **low cloud orchestrator** (`ollama/qwen3.5:397b`) runs on the **Orchestrator Node** (Mac). It does **not** execute code or tests itself. Instead, it:

1. **Selects the target lab node** based on the assigned model tier and current node health.
2. **Dispatches the task via `pi-intercom`** to the selected lab node's named session.
3. **Monitors execution** by polling the lab node for status and test output via intercom.
4. **Collects test evidence** (output, diffs, logs) from the lab node before accepting completion.

**pi-intercom Dispatch (Primary)**
```typescript
// low cloud orchestrator selects node (e.g., fnet3 for gemma4:e4b task)
// Dispatches via pi-intercom to the lab node's named session
intercom({
  action: "ask",
  to: "fnet3",
  message: "Step B-DEV-001-UNIT-001: Write failing test stub..."
})
```

**SSH Dispatch (Fallback — if pi-intercom is not responding)**
```bash
ssh -o ConnectTimeout=5 fnet3 "ollama ps && echo OK"
ssh fnet3 "cd ~/workshop/technical-infrastructure/packages/decompose-execute-verify && npm test -- test/unit/sshfs-mount.test.ts"
```

**Result Collection:**
```bash
# low cloud orchestrator collects test output from lab node
ssh fnet3 "cat ~/workshop/technical-infrastructure/packages/decompose-execute-verify/test-output.log"
ssh fnet3 "cd ~/workshop/technical-infrastructure/packages/decompose-execute-verify && git diff --stat"
```

## Node Selection Algorithm

1. **Determine required model** from the step's `recommended_model` (e.g., `gemma4:e4b`).
2. **Filter nodes** that have the model installed (from node-capacity-map.md).
3. **Check node health** — query the node's ollama status and available RAM.
4. **Select least-loaded qualifying node** — prefer the node with the most free RAM among those that have the required model.
5. **If no node has the required model** — dispatch playbook-executor to pull the model on the healthiest available node, then assign.
6. **If all qualifying nodes are saturated** — escalate to the next model tier (from node-capacity-map.md routing matrix) or invoke ollama/deepseek-v4-pro for deeper decomposition.

## Health Check Before Dispatch

Before every dispatch, the low cloud orchestrator must verify the target node is responsive via **pi-intercom** (primary) or SSH (fallback):

```bash
# Primary: pi-intercom health check
intercom({ action: "ask", to: "{node}", message: "echo OK" })
# Expected: "OK" reply within 10 seconds

# Fallback: SSH health check
ssh -o ConnectTimeout=5 {node} "ollama ps && echo OK" || echo "NODE_UNREACHABLE"
```

If the node is unreachable:
1. Log the failure.
2. Mark node as offline in the health report.
3. Select the next best node.
4. If no nodes are available, invoke node recovery via playbook-executor.

## Acceptance Test Execution on Lab Node

All acceptance tests are executed via **pi-intercom dispatch** to a Lab Node:

```typescript
// Orchestrator dispatches via intercom to lab node
intercom({
  action: "ask",
  to: "fnet3",
  message: "Run acceptance suite: cd ~/workshop/technical-infrastructure/packages/decompose-execute-verify && npm test -- --suite=acceptance"
})

// Results are collected via intercom reply or file transfer
ssh fnet3 "cat ~/workshop/technical-infrastructure/packages/decompose-execute-verify/test-results.jsonl"
```

Results are written to:
- `technical-infrastructure/wiki/products/decompose-execute-verify-debug/TEST-RESULTS-YYYY-MM-DD-HHMM.md`

---

## Local Node Recovery

If a lab node in the pool crashes, OOMs, or becomes unresponsive:

1. **Low cloud model detects failure** via test timeout or health-monitor events.
2. **Low cloud model dispatches a low-capacity lab node** to run the appropriate **playbook-executor** recovery playbook:
   ```bash
   pi playbook-execute --playbook node-recovery --target fnet3 \
     --vars "reason=oom,service=ollama"
   ```
3. **Playbook actions** may include restarting ollama, clearing model cache, pulling missing models, or restarting the pi agent.
4. **Low cloud model verifies recovery** via health check before resuming workload.
5. **If recovery fails:** Mark node offline and redistribute workload to healthy nodes.

For full recovery protocol, see [`AGENTS.md`](./AGENTS.md).

---

## High-Frequency Decomposition Detection

The **medium cloud model** (`ollama/deepseek-v4-pro`) and the **low cloud model** (`ollama/qwen3.5:397b`) collaborate to detect and respond to excessive decomposition rates. The medium cloud focuses on **analysis and recommendation**; the low cloud focuses on **action**.

## Roles

| Model | Role | Executes Code? |
|-------|------|---------------|
| **Medium Cloud** (`ollama/deepseek-v4-pro`) | Analyzes decomposition trends, produces deeper decomposition plans, signals Low Cloud | **NO** |
| **Low Cloud** (`ollama/qwen3.5:397b`) | Receives signal, engages deeper decomposition, logs metrics, reports to user | **YES** (action only) |

## Detection Protocol

1. **Low cloud collects metrics** — Every task assignment and decomposition event is timestamped in session notes.
2. **Medium cloud reads session notes** at 10-minute intervals and calculates the ratio:
   ```
   ratio = (tasks_decomposed in last 10 min) / (total_tasks_assigned in last 10 min)
   ```
3. **Threshold table:**

| Ratio | Window | Action | Owner |
|-------|--------|--------|-------|
| > 60% | Rolling 10 min | Medium Cloud signals Low Cloud → high-frequency mode | Medium Cloud |
| 40%–60% | Rolling 10 min | Monitor only, no action | Low Cloud |
| < 40% | Two consecutive windows | Exit high-frequency mode, resume 2x | Low Cloud |

4. **Medium Cloud produces deeper decomposition** — When ratio > 60%, the medium cloud re-examines pending and incoming steps from the High Cloud and produces **3x-4x finer decomposition plans**. These plans are passed to the Low Cloud as replacement step definitions.
5. **Medium Cloud escalates to High Cloud** — If the ratio stays > 60% for > 20 consecutive minutes, the medium cloud reports to the High Cloud that the initial decomposition granularity may be systematically too coarse.

## High-Frequency Mode Behavior (Low Cloud)

When the Low Cloud receives a high-frequency signal from the Medium Cloud:

1. **Adopt deeper decomposition plans** from Medium Cloud (3x-4x instead of 2x).
2. **Finer model matching** — assign simplest fragments to low local; reserve medium/high local for only the most complex pieces.
3. **Alert in next health report** — flag the condition and which step_ids triggered it.
4. **Log the signal** — record timestamp, ratio, and medium cloud recommendation in session notes.

For the full detection and reporting protocol, see [`AGENTS.md`](./AGENTS.md).

---

## 5-Minute Node Health Report

The low cloud model writes a node health report every 5 minutes during active execution. The report is discoverable in the wiki session folder for manual review and intervention.

## Report Location

```
wiki/operational/sessions/STATUS-DEV-INTEGRATION-YYYY-MM-DD-HHMM.md
```

## Report Contents

Each report includes:
- **Active lab nodes** — which models are loaded, health status, last task.
- **Failed nodes (last 5 min)** — failure time, reason, recovery action, current status.
- **Task decomposition metrics (last 10 min)** — total tasks, decomposed tasks, ratio, whether high-frequency mode is active.
- **Tasks in flight** — step IDs, assigned models, elapsed time.
- **Alerts** — specific, actionable alerts with step IDs.
- **Manual intervention prompts** — checkboxes the user can act on.

## User Discovery

```bash
# List all health reports for this session
ls -lt wiki/operational/sessions/STATUS-DEV-INTEGRATION-*
```

The most recent report is at the top. Open it to see current node health, decomposition trends, and any alerts requiring manual intervention.

For the full report template and rules, see [`AGENTS.md`](./AGENTS.md).

---

## Decision Log

### 2026-05-14 — Framework Integration Strategy
**Decision:** Use Intercom as the primary orchestrator for cross-node dispatch.  
**Rationale:** Lowers latency compared to pure SSH polling and provides better asynchronous state management.  
**Reference:** [`AGENTS.md`](./AGENTS.md)

---

## Session Notes

**Plan Owner:** High Cloud Model (ollama/kimi-k2.6) — planning and decomposition only; never executes.  
**Orchestrator:** Low Cloud Model (ollama/qwen3.5:397b) — routes steps, assigns to appropriate local tier, escalates via 2x decomposition, dispatches node recovery, executes only as last resort.  
**Primary Executor:** Medium Local Model (ollama/gemma4:e4b) — standard execution; writes stubs, implements, refactors, tests on Lab Node.  
**Secondary Executors:** Low Local (ollama/qwen3.5:4b) — simple tasks; High Local (ollama/qwen3:8b) — complex tasks. **Medium Cloud** (ollama/deepseek-v4-pro) — analysis only, never executes locally.  
**Anti-Hallucination:** Low cloud verifier re-runs all test claims before accepting completion.  
**Review required:** Yes — user must approve final integration report.  
**Next action:** Complete P6 assembly and transition to P7 closeout.
