---
section_id: troubleshooting
size_estimate: ~1.2KB
lod_level: Medium
purpose: Symptom-based diagnostics for fleet health issues.
---

# Troubleshooting This Deployment

## [S-TIGHT]

Symptom-based diagnostic table mapping fleet health issues to checks and fixes, plus an escalation path.

[LOD: Medium] *Load when diagnosing fleet symptoms. Pair with MONITORING.md for commands.*

## Symptom → Check → Fix

| Symptom | Check | Fix |
|---------|-------|-----|
| Hub not responding | `curl http://192.168.0.142:8080/health` | Re-run Phase 1 |
| 0 agents online | `curl .../v1/agents?project=lab` | Re-run Phase 5 |
| Auth rejected | Verify `$TOKEN` env var | `export PI_COMS_NET_AUTH_TOKEN=TOKEN` |
| Node DOWN | `ssh fnet3 "echo OK"` | Physical check / network |
| Ollama missing models | `ssh fnet3 "ollama list"` | Re-run Phase 3 |
| Agent log has errors | `ssh fnet3 "tail -50 /tmp/pi-agent-fnet3.log"` | Check model / extension |
| Hub log has errors | `ssh fnet2 "tail -50 /tmp/coms-net-hub.log"` | Check Bun / token |

## Escalation Path

1. **Quick fix:** Re-run the relevant playbook phase (see [PLAYBOOKS.md](PLAYBOOKS.md)).
2. **Logs:** Check agent/hub logs in `/tmp/` (see [MONITORING.md](MONITORING.md)).
3. **Full standup:** `./scripts/run-playbook.sh "stand up the fleet"`.

---

*See also: [MONITORING.md](MONITORING.md) for check commands, [PLAYBOOKS.md](PLAYBOOKS.md) for playbook phases.*