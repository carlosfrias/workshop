# Quality Checklist and Framework Readiness

**Section ID:** quality-and-readiness  
**Size:** ~2.5KB  
**LOD:** Medium  
**Purpose:** Pre-completion quality verification and mandatory TI-011 orchestration framework readiness check before multi-node work.

---

## [S-TIGHT]

Before completing any task, run the Quality Checklist (13 items covering documentation, testing, metrics, secrets, and rollback). Before any multi-node infrastructure work, run the Framework Readiness Check (6 checks) — if any check fails, stop and fix the framework first.

---

## Quality Checklist

[LOD: Low]

Before considering any technical-infrastructure task complete, verify:

- [ ] Document session activity in `../personal-vault/` following vault-native conventions
- [ ] Before deleting ephemeral files, audit for scripts to promote from `/tmp/`
- [ ] Update backlog in `../personal-vault/01-Projects/.../Overview.md`
- [ ] Capture session narrative in `../personal-vault/01-Projects/.../journal/`
- [ ] Document technical work comprehensively so it can be done fully without assistance
- [ ] Test before declaring complete: validate scripts, run syntax-check, test on subset of nodes
- [ ] Budget 20-30% contingency for architectural pivots
- [ ] Performance logging is required, not optional
- [ ] Documentation updates are part of the plan, not afterthoughts
- [ ] API connectivity confirmed for all affected endpoints
- [ ] Secrets are stored in environment variables, not in code
- [ ] Configuration changes are logged with timestamp
- [ ] Rollback plan documented for any deployment
- [ ] Latency and uptime metrics are within acceptable thresholds

## Framework Readiness Check (Mandatory Before Multi-Node Work)

[LOD: Medium]

Before any infrastructure task that touches ≥2 nodes, verify TI-011 is operational:

| Check | Command | Expected Result |
|-------|---------|-----------------|
| Extension installed | `ls ~/.pi/agent/extensions/pi-keyword-router/index.ts` | File exists |
| Classifier functional | `cd technical-infrastructure && python3 scripts/classify_prompt.py --help` | Returns usage |
| Node registry functional | `python3 scripts/ti011_node_registry.py --help` | Returns usage |
| Submitter functional | `python3 scripts/submit_task.py --help` | Returns usage |
| Lab nodes reachable | `ansible -i ansible/inventory.yml lab_nodes -m ping` | All green |
| Orchestrator healthy | `python3 scripts/orchestrator_health.py` | Status: healthy |

**If any check fails:** Stop. Fix the framework before proceeding. Do not "just SSH manually" — that introduces orchestrator load exactly as TI-023 warns.

### Single-Node Exceptions

Direct SSH is permitted for:
- Framework bootstrap (first install on a new node)
- Emergency repair (node unreachable by Ansible)
- Verification after framework-routed work completes

---

*Load [conventions-and-rules.md](./conventions-and-rules.md) for behavioral rules and prohibitions.*