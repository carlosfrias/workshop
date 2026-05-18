# Status Summary Table

**Template ID:** COMP-012  
**Extracted from:** `1-PLAN.md` Section "Project Status Summary"  
**Use in:** Any plan that tracks multiple phases or deliverables with their current status.

---

## 📊 Project Status Summary

| {{PHASE_COL}} | {{STATUS_COL}} | {{DELIVERABLE_COL}} |
|-------|--------|-----------------|
| {{ITEM_1_ID}} ({{ITEM_1_NAME}}) | {{ITEM_1_STATUS}} | {{ITEM_1_DELIVERABLE}} |
| {{ITEM_2_ID}} ({{ITEM_2_NAME}}) | {{ITEM_2_STATUS}} | {{ITEM_2_DELIVERABLE}} |
| {{ITEM_3_ID}} ({{ITEM_3_NAME}}) | {{ITEM_3_STATUS}} | {{ITEM_3_DELIVERABLE}} |
| {{ITEM_4_ID}} ({{ITEM_4_NAME}}) | {{ITEM_4_STATUS}} | {{ITEM_4_DELIVERABLE}} |
| {{ITEM_5_ID}} ({{ITEM_5_NAME}}) | {{ITEM_5_STATUS}} | {{ITEM_5_DELIVERABLE}} |
| {{ITEM_6_ID}} ({{ITEM_6_NAME}}) | {{ITEM_6_STATUS}} | {{ITEM_6_DELIVERABLE}} |

**Critical backlog:** [`{{BACKLOG_FILE}}`](./{{BACKLOG_FILE}})

---

## Placeholder Reference

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{PHASE_COL}}` | Phase column header | `Phase` |
| `{{STATUS_COL}}` | Status column header | `Status` |
| `{{DELIVERABLE_COL}}` | Deliverable column header | `Key Deliverable` |
| `{{ITEM_1_ID}}`–`{{ITEM_6_ID}}` | Item identifiers | `B-KR-001` |
| `{{ITEM_1_NAME}}`–`{{ITEM_6_NAME}}` | Item names | `Kill-Switch` |
| `{{ITEM_1_STATUS}}`–`{{ITEM_6_STATUS}}` | Status with emoji | `✅ Complete`, `📋 Ready` |
| `{{ITEM_1_DELIVERABLE}}`–`{{ITEM_6_DELIVERABLE}}` | Deliverable descriptions | `20 tests, persistent kill-switch, TDD RED→GREEN` |
| `{{BACKLOG_FILE}}` | Link to backlog document | `BACKLOG-keyword-router.md` |
