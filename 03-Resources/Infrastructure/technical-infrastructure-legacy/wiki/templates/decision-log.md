# Decision Log

**Template ID:** COMP-010  
**Extracted from:** `1-PLAN.md` Section "Decision Log"  
**Use in:** Any plan that records architectural or process decisions with rationale.

---

### {{DATE}} — {{DECISION_TITLE}}
**Decision:** {{DECISION_TEXT}}  
**Rationale:** {{RATIONALE}}  
**Reference:** [`{{REFERENCE_FILE}}`](./{{REFERENCE_FILE}})

---

## Placeholder Reference

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{DATE}}` | Decision timestamp | `2026-05-13 19:26` |
| `{{DECISION_TITLE}}` | Short decision name | `Plan Drafted` |
| `{{DECISION_TEXT}}` | Full decision description | `Create a 6-phase plan (Phase 0 = kill-switch, Phases 1–4 = Lab Node debug, Phase 5 = production re-enablement).` |
| `{{RATIONALE}}` | Why this decision was made | `The user requires the router to stay OFF until fixed. A kill-switch is the prerequisite for all other work.` |
| `{{REFERENCE_FILE}}` | Link to related document | `AGENTS.md` |
