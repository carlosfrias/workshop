# Backlog Item Template

**Template ID:** COMP-009  
**Extracted from:** `1-PLAN.md` Section "Backlog Items"  
**Use in:** Any plan that tracks work items through a backlog.

---

### {{ID}}: {{TITLE}}
**Created:** {{CREATED_DATE}}  
**Priority:** {{PRIORITY}}  
**Phase:** {{PHASE}}  
**Status:** {{STATUS}}  
**Owner:** {{OWNER}}  
**Effort:** {{EFFORT}}  
**Dependencies:** {{DEPENDENCIES}}  
**TDD Entry Point:** {{TDD_ENTRY_POINT}}  
**Test Files (stubs):**
- `{{TEST_FILE_1}}` ← {{TEST_FILE_1_STATUS}}
- `{{TEST_FILE_2}}` ← {{TEST_FILE_2_STATUS}}
- `{{TEST_FILE_3}}` ← {{TEST_FILE_3_STATUS}}
- `{{TEST_FILE_4}}` ← {{TEST_FILE_4_STATUS}}
- `{{TEST_FILE_5}}` ← {{TEST_FILE_5_STATUS}}

**Implementation Files:**
- `{{IMPL_FILE_1}}`
- `{{IMPL_FILE_2}}` ← {{IMPL_FILE_2_STATUS}}
- `{{IMPL_FILE_3}}`
- `{{IMPL_FILE_4}}`

**Acceptance Criteria:**
- [ ] {{ACCEPTANCE_1}}
- [ ] {{ACCEPTANCE_2}}
- [ ] {{ACCEPTANCE_3}}
- [ ] {{ACCEPTANCE_4}}
- [ ] {{ACCEPTANCE_5}}
- [ ] {{ACCEPTANCE_6}}
- [ ] {{ACCEPTANCE_7}}

---

## Placeholder Reference

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{ID}}` | Backlog item identifier | `B-KR-001` |
| `{{TITLE}}` | Short title | `Implement Persistent Kill-Switch for pi-keyword-router` |
| `{{CREATED_DATE}}` | Creation date | `2026-05-13` |
| `{{PRIORITY}}` | Priority emoji + label | `🔴 High` |
| `{{PHASE}}` | Associated plan phase | `Phase 0` |
| `{{STATUS}}` | Current status | `Ready to Start` |
| `{{OWNER}}` | Team or individual | `Technical Infrastructure` |
| `{{EFFORT}}` | Estimated effort | `2–3 hours` |
| `{{DEPENDENCIES}}` | Blocking items | `None` or `B-KR-001` |
| `{{TDD_ENTRY_POINT}}` | Where to start with TDD | `Write failing test stubs first (see Phase 0, RED section).` |
| `{{TEST_FILE_1}}`–`{{TEST_FILE_5}}` | Test file paths | `technical-infrastructure/packages/pi-keyword-router/test/unit/kill-switch.test.ts` |
| `{{TEST_FILE_1_STATUS}}`–`{{TEST_FILE_5_STATUS}}` | File status | `NEW stub`, `EXTEND with upgradeThreshold` |
| `{{IMPL_FILE_1}}`–`{{IMPL_FILE_4}}` | Implementation file paths | `pi-keyword-router/index.ts` |
| `{{IMPL_FILE_2_STATUS}}` | New file marker | `NEW` |
| `{{ACCEPTANCE_1}}`–`{{ACCEPTANCE_7}}` | Acceptance criteria | `Unit stubs written and initially failing (RED).` |
