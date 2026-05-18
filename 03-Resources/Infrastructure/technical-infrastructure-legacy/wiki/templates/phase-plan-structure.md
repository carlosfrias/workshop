# Phase Plan Structure

**Template ID:** COMP-008  
**Extracted from:** `1-PLAN.md` Section "Phase Plan"  
**Use in:** Any plan that is broken into sequential phases following TDD.

---

> **Every phase follows the TDD cycle: RED (write failing test stubs) → GREEN (implement to pass) → REFACTOR (clean up).**
> **All tests run on the Lab Node. The Orchestrator Node is never used for testing.**

---

### {{PHASE_NAME}} — {{PHASE_TITLE}}

**Goal:** {{GOAL}}  
**Location:** {{LOCATION}}.  
**TDD Cycle:**

#### RED — Write Failing Test Stubs
1. **Unit test stub** (`{{UNIT_TEST_PATH}}`):
   - Assert that {{TEST_ASSERTION_1}}.
   - **Expected: FAIL** — {{FAIL_REASON_1}}.
2. **Unit test stub** (`{{UNIT_TEST_PATH_2}}`):
   - Assert that {{TEST_ASSERTION_2}}.
   - **Expected: FAIL** — {{FAIL_REASON_2}}.
3. **Integration test stub** (`{{INTEGRATION_TEST_PATH}}`):
   - Assert that {{TEST_ASSERTION_3}}.
   - **Expected: FAIL** — {{FAIL_REASON_3}}.
4. **Acceptance test stub** (`{{ACCEPTANCE_TEST_PATH}}`):
   - {{ACCEPTANCE_SCENARIO}}.
   - **Expected: FAIL** — {{FAIL_REASON_4}}.

#### GREEN — Implement to Pass
- [ ] {{GREEN_TASK_1}}
- [ ] {{GREEN_TASK_2}}
- [ ] {{GREEN_TASK_3}}
- [ ] {{GREEN_TASK_4}}

#### REFACTOR
- [ ] {{REFACTOR_TASK_1}}
- [ ] {{REFACTOR_TASK_2}}

#### Verification
- [ ] Unit suite: {{UNIT_PASS_GATE}}.
- [ ] Integration suite: {{INTEGRATION_PASS_GATE}}.
- [ ] Acceptance suite on Lab Node: {{ACCEPTANCE_PASS_GATE}}.

**Effort:** {{EFFORT_RANGE}}  
**Risk:** {{RISK_LEVEL}} — {{RISK_RATIONALE}}.

---

## Placeholder Reference

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{PHASE_NAME}}` | Phase identifier | `Phase 0` |
| `{{PHASE_TITLE}}` | Phase title | `Kill-Switch Implementation` |
| `{{GOAL}}` | One-sentence goal | `Make the disable state persistent and session-surviving.` |
| `{{LOCATION}}` | Where work happens | `` `pi-keyword-router` config layer + `model-router` gatekeeper `` |
| `{{UNIT_TEST_PATH}}` | Path to unit test file | `pi-keyword-router/test/unit/kill-switch.test.ts` |
| `{{UNIT_TEST_PATH_2}}` | Path to second unit test | `pi-keyword-router/test/unit/gatekeeper.test.ts` |
| `{{INTEGRATION_TEST_PATH}}` | Path to integration test | `pi-keyword-router/test/integration/keyword-router-with-model-router.test.ts` |
| `{{ACCEPTANCE_TEST_PATH}}` | Path to acceptance test | `pi-keyword-router/test/acceptance/kr-006-manual-selection.test.ts` |
| `{{TEST_ASSERTION_1}}` | What the test asserts | `` `loadConfig()` reads `extensions.pi-keyword-router.enabled` `` |
| `{{FAIL_REASON_1}}` | Why it fails initially | `no config flag schema exists` |
| `{{GREEN_TASK_1}}`–`{{GREEN_TASK_4}}` | Implementation tasks | `Add enabled flag to config schema` |
| `{{REFACTOR_TASK_1}}`–`{{REFACTOR_TASK_2}}` | Refactoring tasks | `Extract gatekeeper logic into lib/gatekeeper.ts` |
| `{{UNIT_PASS_GATE}}` | Unit test pass criteria | `` `npm test -- --suite=unit` → 100% pass `` |
| `{{INTEGRATION_PASS_GATE}}` | Integration test pass criteria | `` `npm test -- --suite=integration` → 100% pass `` |
| `{{ACCEPTANCE_PASS_GATE}}` | Acceptance test pass criteria | `all KR-006 scenarios pass` |
| `{{EFFORT_RANGE}}` | Estimated effort | `2–3 hours` |
| `{{RISK_LEVEL}}` | Risk assessment | `Low` |
| `{{RISK_RATIONALE}}` | Why risk is at this level | `additive, no existing logic changed` |
