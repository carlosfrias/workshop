# Technical Infrastructure — Documentation Index

**Purpose:** This file is a **context-optimized index** for the technical-infrastructure domain. Local models load this file (≈100 lines) instead of the full documentation (≈600 lines).

**Loading Strategy:** When a task matches keywords in the "Keywords" column, load the corresponding section file **before** executing.

---

## Documentation Map

| Section | File | Keywords | Context Cost |
|---------|------|----------|--------------|
| **Publishing** | [wiki/guides/publishing-workflow.md](wiki/guides/publishing-workflow.md) | publish, extension, skill, npm, github, package | ~50 lines |
| **Conventions** | [wiki/guides/conventions.md](wiki/guides/conventions.md) | conventions, standards, execution, chunking | ~40 lines |
| **Ansible Vault** | [wiki/guides/ansible-vault.md](wiki/guides/ansible-vault.md) | vault, encrypt, secrets, ansible_become_pass | ~30 lines |
| **Ansible Testing** | [wiki/guides/ansible-testing.md](wiki/guides/ansible-testing.md) | syntax-check, -vvv, playbook test, script test | ~60 lines |
| **TI-011 Orchestration** | [wiki/guides/ti011-orchestration.md](wiki/guides/ti011-orchestration.md) | meta-orchestration, classify, decompose, route, escalate | ~100 lines |
| **Orchestrator Node** | [wiki/guides/orchestrator-conventions.md](wiki/guides/orchestrator-conventions.md) | orchestrator, Mac, ctrl-p, ollama, health | ~80 lines |
| **Playbook Executor** | [packages/playbook-executor/README.md](packages/playbook-executor/README.md) | playbook-executor, run playbook, execute, service recovery, health-aware, run the, start the, launch the, serve wiki, run wiki, start wiki, deploy pi, install pi, update packages, upgrade packages, backup data, snapshot, restart ollama, reset ollama, fix ollama, shutdown lab, power off, configure ssh, setup vpn, add vpn peer, fix broken links, capacity report, hardware report, gather hardware, optimize lab, run pilot, benchmark lab, test pi, validate router, migrate worker, deploy worker, deploy gist worker, deploy chromadb, full pi validation | ~80 lines |
| **Rules** | [wiki/guides/rules.md](wiki/guides/rules.md) | must always, must never, rules | ~30 lines |
| **Quality Checklist** | [wiki/guides/quality-checklist.md](wiki/guides/quality-checklist.md) | checklist, complete, session docs, testing | ~50 lines |
| **Planning Gates** | [wiki/guides/planning-gates.md](wiki/guides/planning-gates.md) | PLAN, latency budget, pivot, contingency | ~20 lines |
| **Prompt References** | [wiki/guides/prompt-references.md](wiki/guides/prompt-references.md) | file routing, keyword triggers | ~30 lines |
| **Published Packages** | [wiki/guides/published-packages.md](wiki/guides/published-packages.md) | packages, install, version | ~20 lines |

**Total if all loaded:** ~510 lines (still 30% smaller than monolithic file)  
**Typical load:** 50-150 lines (1-2 sections as needed)

---

## Quick Reference

### Must Always (Top 5)
1. Test scripts/playbooks immediately after creating
2. Log configuration changes with before/after state
3. Verify API connectivity before dependent operations
4. Follow the Quality Checklist before completing tasks
5. Publish with semantic versioning + local test

### Must Never (Top 5)
1. Store API keys/secrets in plain text
2. Deploy untested changes to production
3. Ignore connectivity alerts or latency degradation
4. Run infrastructure changes without rollback plan
5. Publish without updating README.md

### Orchestrator Health Thresholds

| Metric | Healthy | Stressed | Critical |
|--------|---------|----------|----------|
| RAM % | <80% | 80-92% | >92% |
| CPU load | <4.0 | 4.0-6.0 | >6.0 |
| Swap | 0 | 0 | >0 |

### TI-011 Routing Rules

1. Heuristic classification first (<50ms, keyword-based)
2. LLM fallback if confidence < 0.75
3. Node-model lookup from NodeRegistry
4. Capability filtering (vision, tools)
5. Cloud escalation only when no local match
6. Escalation is per sub-task (not whole prompt)

---

## Domain Agent Routing

For domain activation keywords, see the root [`AGENTS.md`](AGENTS.md) file.

**Common Technical Infrastructure Keywords:**
- servers, APIs, connectivity, latency
- infrastructure, deployment, monitoring, orchestration
- classify, decompose, distribute, queue, worker
- ansible, script, playbook, node, cluster
- performance, meta-orchestration, framework

---

## Full Documentation (Pre-Modularization)

The original monolithic `AGENTS-full.md` content has been split into the sections above. If you need the full historical document for reference, see:

- **Archived:** `technical-infrastructure/archive/AGENTS-full-original.md` (read-only reference)

---

**Version:** 2.0.0 (modular)  
**Last Updated:** 2026-05-12  
**Maintained By:** Technical Infrastructure domain agents
