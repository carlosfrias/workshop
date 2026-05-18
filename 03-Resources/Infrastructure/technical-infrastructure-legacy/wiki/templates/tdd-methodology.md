# TDD Methodology

**Template ID:** COMP-006  
**Extracted from:** `1-PLAN.md` Section "TDD Methodology"  
**Use in:** Any plan that involves code changes and requires test coverage.

---

This plan follows the **Red → Green → Refactor** cycle for every phase.

## Rules
1. **No production code without a failing test first.** Every change starts with a test that fails because the implementation is a stub or missing.
2. **Tests live in the workspace they validate.**
   - `{{WORKSPACE_1}}` tests → `{{WORKSPACE_1_TEST_PATH}}`
   - `{{WORKSPACE_2}}` tests → `{{WORKSPACE_2_TEST_PATH}}`
3. **Three test layers, executed in sequence:**
   - **Unit tests** — Single module, mocked dependencies, fast (< {{UNIT_TIME_MS}}ms each).
   - **Integration tests** — Two or more modules interacting, real (non-mocked) event bus and config.
   - **Acceptance tests** — End-to-end on Lab Node, real model-router, real extensions, simulated prompts.
4. **Lab Node execution only.** All test execution, code writing, and validation runs on **Lab Nodes** ({{NODE_POOL}}) via {{DISPATCH_METHOD}} dispatch from the orchestrator. The Orchestrator Node ({{ORCHESTRATOR_OS}}) is never used for test execution, debugging, or validation. The orchestrator only dispatches commands and collects results.
5. **Stubs are explicit.** Every stub is named `stub-*` or `mock-*` and committed with a `// TODO: implement` comment.

## Test Layer Definitions

| Layer | Scope | Location | When They Run | Pass Gate |
|-------|-------|----------|---------------|-----------|
| **Unit** | One function/class in isolation | `{{UNIT_DIR}}` | After every code change | 100% pass |
| **Integration** | Module interaction (events, config, hooks) | `{{INTEGRATION_DIR}}` | After unit suite passes | 100% pass |
| **Acceptance** | Full pipeline on Lab Node | `{{ACCEPTANCE_DIR}}` or Lab Node scripts | After integration suite passes | All {{SCENARIO_PREFIX}} scenarios pass |

---

## Placeholder Reference

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{WORKSPACE_1}}` | First workspace with tests | `pi-keyword-router` |
| `{{WORKSPACE_1_TEST_PATH}}` | Test path for workspace 1 | `technical-infrastructure/packages/pi-keyword-router/test/` |
| `{{WORKSPACE_2}}` | Second workspace with tests | `routing-transparency` |
| `{{WORKSPACE_2_TEST_PATH}}` | Test path for workspace 2 | `technical-infrastructure/packages/routing-transparency/test/` |
| `{{UNIT_TIME_MS}}` | Max time per unit test | `100` |
| `{{NODE_POOL}}` | Lab nodes for test execution | `fnet1–fnet7` |
| `{{DISPATCH_METHOD}}` | How tests are dispatched | `SSH` |
| `{{ORCHESTRATOR_OS}}` | Orchestrator OS | `Mac` |
| `{{UNIT_DIR}}` | Unit test directory | `test/unit/` |
| `{{INTEGRATION_DIR}}` | Integration test directory | `test/integration/` |
| `{{ACCEPTANCE_DIR}}` | Acceptance test directory | `test/acceptance/` |
| `{{SCENARIO_PREFIX}}` | Prefix for acceptance scenarios | `KR` |
