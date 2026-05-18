# 5-Minute Node Health Report

**Template ID:** COMP-005  
**Extracted from:** `1-PLAN.md` Section "5-Minute Node Health Report"  
**Use in:** Any plan that dispatches work across a lab node pool and needs periodic status visibility.

---

The {{REPORT_WRITER}} writes a node health report every {{REPORT_INTERVAL}} minutes during active execution. The report is discoverable in the wiki session folder for manual review and intervention.

## Report Location

```
{{REPORT_PATH_PATTERN}}
```

## Report Contents

Each report includes:
- **Active lab nodes** — which models are loaded, health status, last task.
- **Failed nodes (last {{REPORT_INTERVAL}} min)** — failure time, reason, recovery action, current status.
- **Task decomposition metrics (last {{METRIC_WINDOW}} min)** — total tasks, decomposed tasks, ratio, whether high-frequency mode is active.
- **Tasks in flight** — step IDs, assigned models, elapsed time.
- **Alerts** — specific, actionable alerts with step IDs.
- **Manual intervention prompts** — checkboxes the user can act on.

## User Discovery

```bash
# List all health reports for this session
ls -lt {{GLOB_PATTERN}}
```

The most recent report is at the top. Open it to see current node health, decomposition trends, and any alerts requiring manual intervention.

For the full report template and rules, see [`{{AGENTS_MD_PATH}}`](./{{AGENTS_MD_PATH}}).

---

## Placeholder Reference

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{REPORT_WRITER}}` | Role that writes the report | `low cloud model` |
| `{{REPORT_INTERVAL}}` | Minutes between reports | `5` |
| `{{REPORT_PATH_PATTERN}}` | Path template for report files | `wiki/operational/sessions/STATUS-KEYWORD-ROUTER-DEBUG-YYYY-MM-DD-HHMM.md` |
| `{{METRIC_WINDOW}}` | Window for decomposition metrics | `10` |
| `{{GLOB_PATTERN}}` | Shell glob for listing reports | `wiki/operational/sessions/STATUS-KEYWORD-ROUTER-DEBUG-*` |
| `{{AGENTS_MD_PATH}}` | Path to full protocol | `AGENTS.md` |
