# Prompt-Triggered References

**LEGACY — MIGRATE TO:** `personal-vault/03-Resources/Technical-Infrastructure/prompt-references.md`

These files are loaded on demand when a task matches their keywords. For model routing keywords, see the routing table in root `AGENTS.md`.

| Keywords | File |
|----------|------|
| network troubleshooting, node offline, driver issue, r8169, can't reach internet | `./prompts/network-troubleshooting.md` |
| network troubleshooting deployment, offline node setup, tether troubleshooting | `./archive/deployment-examples/network-troubleshooting/README.md` |
| extension publishing, skill publishing, npm publish, github release | `./wiki/guides/publishing-workflow.md` |
| pi-keyword-router, keyword routing, model routing, model selection, complexity routing | `./packages/pi-keyword-router/README.md` |
| model routing, model-router, route configuration, cloud models, local models, tiered routing | `./wiki/model-routing-guide.md` |
| node 2 troubleshooting, offline node, ethernet down, r8168, r8169 | `./wiki/node2-troubleshooting-session.md` |
| gist-message-queue, gist-mq, agent-to-agent communication | `./wiki/node2-troubleshooting-session.md` |
| block device busy, device resource busy, can't wipe disk, lsof shows nothing, mount namespace | `./wiki/decomposition-examples/systemd-mount-lock/00-decomposition-plan.md` |
| meta-orchestration, orchestration framework, complexity classification, prompt routing, workload distribution | `./wiki/guides/ti011-orchestration.md` |
| task decomposition, sub-task routing, model assignment, node assignment, fan out, parallel execution | `./wiki/operational/planning/PLAN-2026-05-01-1547.md` |
| artifact sync, bidirectional sync, wiki artifact collection, node documentation | `./wiki/operational/planning/PLAN-2026-05-01-1605.md` |
| **playbook-executor, run playbook, execute playbook, service recovery, API failure, restart service, node remediation, fnet failure, HTTP 000, health-aware execution, deploy playbook, run the, start the, launch the, serve wiki, run wiki, start wiki, deploy pi, install pi, update packages, upgrade packages, backup data, snapshot, restart ollama, reset ollama, fix ollama, shutdown lab, power off, configure ssh, setup vpn, add vpn peer, fix broken links, capacity report, hardware report, gather hardware, optimize lab, run pilot, benchmark lab, test pi, validate router, migrate worker, deploy worker, deploy gist worker, deploy chromadb, full pi validation** | `./packages/playbook-executor/README.md` |
| ansible vault, vault password, encrypt secret, ansible_become_pass | `./wiki/guides/ansible-vault.md` |
| ansible testing, syntax-check, playbook debug, -vvv | `./wiki/guides/ansible-testing.md` |
| orchestrator health, ctrl-p model cycling, ollama-cloud extension | `./wiki/guides/orchestrator-conventions.md` |
| quality checklist, session documentation, testing requirements | `./wiki/guides/quality-checklist.md` |
| planning gates, latency budget, pivot contingency | `./wiki/guides/planning-gates.md` |

## Loading Instructions for Agents

When a task involves specific keywords, load the corresponding reference file **before** executing:

```
Task: "Deploy playbook to fix ollama on fnet3"
Keywords: deploy, playbook, ollama, fix
→ Load: ansible-testing.md (for testing)
→ Load: orchestrator-conventions.md (if orchestrator also needs fix)

Task: "Set up vault for new node"
Keywords: vault, encrypt, ansible
→ Load: ansible-vault.md

Task: "Why is classification taking 6 seconds?"
Keywords: classification, latency, slow
→ Load: planning-gates.md (latency budgets)
→ Load: ti011-orchestration.md (routing architecture)
```

---

**Related:** [AGENTS.md](../AGENTS.md) — Domain routing table
