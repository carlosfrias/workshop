# Technical Infrastructure

Managing servers, APIs, network connectivity, and deployment pipeline that power Carlos' Desktop and the trading-desk domain.

## Conventions

- All hostnames and endpoints documented in lowercase
- All latency measurements in milliseconds (ms)
- All uptime as percentage
- Configuration changes must be tracked with timestamp and author
- Use environment variables for secrets — never hardcode credentials
- All outputs should be structured and machine-parseable where possible
- Seek the `.venv` in the project root folder and if found, then activate it
- Python 3.14.4 is the target version for `.venv`

## Rules

### Must Always
- **Verify TI-011 orchestration framework is operational before any multi-node or infrastructure work** (see Framework Readiness Check below)
- **Include orchestrator node (Mac) in infrastructure fixes** — when fixing model configs, caches, or extensions on lab nodes, apply the same fix to the orchestrator. See `AGENTS-full.md` Orchestrator Node Conventions.
- Verify API connectivity before executing any dependent operation
- Log all configuration changes with before/after state
- Test scripts and playbooks immediately after creating or fixing them
- Test in a staging environment before production deployment
- Monitor latency thresholds and alert on breaches
- Document every integration endpoint and authentication method
- Publish with semantic versioning (major.minor.patch)
- Test locally before publishing
- Follow the Quality Checklist before completing any task

### Must Never
- **Execute multi-node infrastructure work without routing through TI-011** (classify → decompose → submit → collect). Direct SSH to nodes from the orchestrator is only for framework bootstrap or single-node emergencies.
- Store API keys or secrets in plain text or code
- Deploy untested changes to production infrastructure
- Ignore connectivity alerts or latency degradation
- Run infrastructure changes without a rollback plan
- Assume a service is healthy without verifying
- Publish without updating README.md
- Break backward compatibility without a major version bump

## Quality Checklist

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

**Single-node exceptions:** Direct SSH is permitted for:
- Framework bootstrap (first install on a new node)
- Emergency repair (node unreachable by Ansible)
- Verification after framework-routed work completes

## Domain Agent File Routing

When the task involves one of these domains, read the corresponding file before proceeding.

| Task keywords | Read this file |
|----------|---------------|
| servers, APIs, connectivity, latency, infrastructure, deployment, monitoring, orchestration, orchestrate, route, routing, classify, classification, complexity, decompose, decomposition, fan out, distribute, distribution, workload, queue, worker, task, submit, collect, sync, artifact, node, cluster, meta-, framework, performance, ansible, script, scripts, bash, playbook | `./AGENTS.md` (this file) |
| trade logging, reconciliation, P&L, accounting, balances, fees, settlement | `../bookkeeping/AGENTS.md` |
| research, analysis, signals, backtesting, data, indicators, sentiment | `../market-research/AGENTS.md` |
| positions, orders, risk, allocation, sizing, exits, stops, portfolio | `../position-management/AGENTS.md` |
| position status, monitoring, risk limit checks, portfolio state | `../position-management/AGENTS.md` (use `position-monitor` agent) |


## Prompt-Triggered References

These files are loaded on demand when a task matches their keywords.

| Keywords | File |
|----------|------|
| network troubleshooting, node offline, driver issue, r8169 | `./prompts/network-troubleshooting.md` |
| pi-keyword-router, keyword routing, model routing | `./extensions/pi-keyword-router/README.md` |
| meta-orchestration, orchestration framework, complexity classification | `../personal-vault/01-Projects/Carlos-Trading-Desk/planning/` |
| task decomposition, sub-task routing, model assignment, fan out | `../personal-vault/01-Projects/Carlos-Trading-Desk/planning/` |
| package hygiene, DRY violation, duplicate agents, package structure, package policy | `./packages/PACKAGE-HYGIENE-POLICY.md` |
| **sshfs, parallel filesystem, distributed files, mount workspace, lab node files, fan out files, batch file process, file aggregation across nodes, parallel scan, distributed grep, parallel log analysis, auto-mount, ensure mounted, sshfs-integration** | `./packages/sshfs-integration/skills/sshfs-integration/SKILL.md` |

## Full Documentation

**AGENTS-full.md** is now a **modular index** (~100 lines) that links to topic-specific sections.

### Loading Strategy

| Task Type | Load This | Context Cost |
|-----------|-----------|--------------|
| **Publishing work** | `../personal-vault/03-Resources/Technical-Infrastructure/` | ~50 lines |
| **Ansible work** | `../personal-vault/03-Resources/Technical-Infrastructure/Operations/` | ~90 lines |
| **Orchestration work** | `../personal-vault/03-Resources/Technical-Infrastructure/` | ~100 lines |
| **Orchestrator-specific** | `../personal-vault/03-Resources/Technical-Infrastructure/` | ~80 lines |
| **Planning work** | `../personal-vault/01-Projects/Carlos-Trading-Desk/planning/` | ~20 lines |
| **Completing tasks** | `../personal-vault/01-Projects/` | ~50 lines |

**Typical load:** 50-150 lines (vs. 546+ lines for monolithic file)

### Quick Access

- **Full Index:** [`AGENTS-full.md`](AGENTS-full.md) — Context-optimized documentation map
- **Model Routing:** [`AGENTS-routing.md`](AGENTS-routing.md) — Model tier configuration

---

## Backlog Management

**Documentation home:** `../personal-vault/` — backlog and session tracking follow vault-native conventions.

**Active Backlog:** Tracked in `../personal-vault/01-Projects/Carlos-Trading-Desk/Overview.md`
