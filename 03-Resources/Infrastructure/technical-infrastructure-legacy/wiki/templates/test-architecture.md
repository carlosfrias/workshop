# Test Architecture

**Template ID:** COMP-007  
**Extracted from:** `1-PLAN.md` Section "Test Architecture"  
**Use in:** Any plan that requires a multi-layer test harness across multiple workspaces.

---

### Workspace 1: `{{WORKSPACE_1}}`

> **Prerequisite:** Before any test stubs are written, the `{{WORKSPACE_1}}` workspace must have a test harness mirroring the `{{WORKSPACE_2}}` structure. If the `test/` directory does not exist or lacks the `unit/`, `integration/`, and `acceptance/` subdirectories, the first step in every phase must be to scaffold the harness.
>
> **Lab Node Target:** The harness and all test files are created on a **Lab Node** (not the orchestrator). The orchestrator dispatches SSH commands to the selected lab node. See [Lab Node Dispatch Rules](#lab-node-dispatch-rules) below.

**Test Harness Target Structure:**

```
{{PACKAGE_PATH_1}}/
├── src/
│   ├── index.ts
│   ├── lib/
│   │   ├── {{MODULE_1}}.ts
│   │   ├── {{MODULE_2}}.ts
│   │   ├── {{MODULE_3}}.ts
│   │   └── {{NEW_MODULE}}.ts          ← NEW (stub)
│   └── model-router/
│       └── {{NEW_MODULE}}.ts          ← NEW (stub)
└── test/                           ← MUST EXIST on Lab Node (mirror {{WORKSPACE_2}})
    ├── unit/                       ← MUST EXIST on Lab Node
    │   ├── {{TEST_1}}.test.ts     ← NEW (stub: {{TEST_1_DESC}})
    │   ├── {{TEST_2}}.test.ts      ← EXISTING (extend with {{EXTEND_FEATURE}})
    │   ├── {{TEST_3}}.test.ts ← NEW (stub: {{TEST_3_DESC}})
    │   └── {{TEST_4}}.test.ts      ← NEW (stub: {{TEST_4_DESC}})
    ├── integration/                ← MUST EXIST on Lab Node
    │   ├── {{INT_TEST_1}}.test.ts ← NEW (stub)
    │   ├── {{INT_TEST_2}}.test.ts ← NEW (stub)
    │   └── {{INT_TEST_3}}.test.ts          ← NEW (stub)
    └── acceptance/                 ← MUST EXIST on Lab Node
        ├── {{ACC_TEST_1}}.test.ts           ← NEW (stub)
        ├── {{ACC_TEST_2}}.test.ts            ← NEW (stub)
        ├── {{ACC_TEST_3}}.test.ts       ← NEW (stub)
        ├── {{ACC_TEST_4}}.test.ts           ← NEW (stub)
        ├── {{ACC_TEST_5}}.test.ts            ← NEW (stub)
        ├── {{ACC_TEST_6}}.test.ts           ← NEW (stub)
        └── {{ACC_TEST_7}}.test.ts              ← NEW (stub)
```

### Workspace 2: `{{WORKSPACE_2}}`

> **Lab Node Target:** `{{WORKSPACE_2}}` tests also execute on Lab Nodes. The `{{WORKSPACE_2}}` workspace may exist on both orchestrator and lab nodes (via shared filesystem or sync), but test execution occurs on the lab node assigned by the orchestrator.

```
{{PACKAGE_PATH_2}}/
├── src/
│   ├── index.ts
│   ├── routing-footer.ts
│   └── types.ts
└── test/
    ├── unit/
    │   ├── {{W2_UNIT_1}}.test.ts            ← NEW (stub: {{W2_UNIT_1_DESC}})
    │   ├── {{W2_UNIT_2}}.test.ts           ← NEW (stub: {{W2_UNIT_2_DESC}})
    │   └── {{W2_UNIT_3}}.test.ts                ← NEW (stub: {{W2_UNIT_3_DESC}})
    ├── integration/
    │   ├── {{W2_INT_1}}.test.ts   ← NEW (stub: {{W2_INT_1_DESC}})
    │   └── {{W2_INT_2}}.test.ts     ← NEW (stub: {{W2_INT_2_DESC}})
    └── acceptance/
        └── {{W2_ACC_1}}.test.ts         ← NEW (stub: {{W2_ACC_1_DESC}})
```

---

## Placeholder Reference

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{WORKSPACE_1}}` | Primary workspace name | `pi-keyword-router` |
| `{{PACKAGE_PATH_1}}` | Primary package path | `technical-infrastructure/packages/pi-keyword-router` |
| `{{WORKSPACE_2}}` | Secondary workspace name | `routing-transparency` |
| `{{PACKAGE_PATH_2}}` | Secondary package path | `technical-infrastructure/packages/routing-transparency` |
| `{{MODULE_1}}` | Existing source module | `classifier` |
| `{{MODULE_2}}` | Existing source module | `types` |
| `{{MODULE_3}}` | Existing source module | `config` |
| `{{NEW_MODULE}}` | New module to create | `gatekeeper` |
| `{{TEST_1}}` | Unit test name | `kill-switch` |
| `{{TEST_1_DESC}}` | Test description | `config flag read` |
| `{{TEST_2}}` | Unit test name | `classifier` |
| `{{EXTEND_FEATURE}}` | Feature to extend | `upgradeThreshold` |
| `{{TEST_3}}` | Unit test name | `cloud-escalation` |
| `{{TEST_3_DESC}}` | Test description | `trigger detection` |
| `{{TEST_4}}` | Unit test name | `gatekeeper` |
| `{{TEST_4_DESC}}` | Test description | `bypass logic` |
| `{{INT_TEST_1}}` | Integration test name | `keyword-router-with-model-router` |
| `{{INT_TEST_2}}` | Integration test name | `keyword-router-with-transparency` |
| `{{INT_TEST_3}}` | Integration test name | `cloud-cost-confirmation` |
| `{{ACC_TEST_1}}`–`{{ACC_TEST_7}}` | Acceptance test names | `kr-001`–`kr-007` |
| `{{W2_UNIT_1}}` | Secondary workspace unit test | `footer-disabled-state` |
| `{{W2_UNIT_1_DESC}}` | Test description | `footer shows "disabled"` |
| `{{W2_UNIT_2}}` | Secondary workspace unit test | `footer-override-reason` |
| `{{W2_UNIT_2_DESC}}` | Test description | `footer shows overrideReason` |
| `{{W2_UNIT_3}}` | Secondary workspace unit test | `footer-cloud-cost` |
| `{{W2_UNIT_3_DESC}}` | Test description | `footer shows cloud pricing` |
| `{{W2_INT_1}}` | Secondary workspace integration test | `transparency-with-keyword-router` |
| `{{W2_INT_1_DESC}}` | Test description | `event flow` |
| `{{W2_INT_2}}` | Secondary workspace integration test | `transparency-with-model-router` |
| `{{W2_INT_2_DESC}}` | Test description | `manual selection` |
| `{{W2_ACC_1}}` | Secondary workspace acceptance test | `lab-node-validation-suite` |
| `{{W2_ACC_1_DESC}}` | Test description | `end-to-end` |
