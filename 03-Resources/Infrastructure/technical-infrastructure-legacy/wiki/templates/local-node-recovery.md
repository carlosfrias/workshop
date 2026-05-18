# Local Node Recovery

**Template ID:** COMP-003  
**Extracted from:** `1-PLAN.md` Section "Local Node Recovery"  
**Use in:** Any plan that dispatches work to a pool of lab nodes.

---

If a lab node in the pool crashes, OOMs, or becomes unresponsive:

1. **{{DETECTOR}} detects failure** via test timeout or {{HEALTH_MONITOR}} events.
2. **{{DETECTOR}} dispatches a low-capacity lab node** to run the appropriate **{{PLAYBOOK_EXECUTOR}}** recovery playbook:
   ```bash
   pi playbook-execute --playbook {{RECOVERY_PLAYBOOK}} --target {{FAILED_NODE}} \
     --vars "reason={{REASON}},service={{SERVICE}}"
   ```
3. **Playbook actions** may include restarting {{SERVICE}}, clearing model cache, pulling missing models, or restarting the {{PI_AGENT}}.
4. **{{DETECTOR}} verifies recovery** via health check before resuming workload.
5. **If recovery fails:** Mark node offline and redistribute workload to healthy nodes.

For full recovery protocol, see [`{{AGENTS_MD_PATH}}`](./{{AGENTS_MD_PATH}}).

---

## Placeholder Reference

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{DETECTOR}}` | Role that detects and dispatches recovery | `Low cloud model` |
| `{{HEALTH_MONITOR}}` | Health monitoring system | `health-monitor` |
| `{{PLAYBOOK_EXECUTOR}}` | Recovery tool | `playbook-executor` |
| `{{RECOVERY_PLAYBOOK}}` | Name of recovery playbook | `node-recovery` |
| `{{FAILED_NODE}}` | Node that failed | `fnet3` |
| `{{REASON}}` | Failure reason | `oom`, `crash`, `network` |
| `{{SERVICE}}` | Service to recover | `ollama`, `pi-agent` |
| `{{PI_AGENT}}` | Agent name | `pi agent` |
| `{{AGENTS_MD_PATH}}` | Path to full recovery protocol | `AGENTS.md` |
