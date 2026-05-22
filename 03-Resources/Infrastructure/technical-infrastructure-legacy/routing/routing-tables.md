# Domain Routing and Prompt-Triggered References

**Section ID:** routing-tables  
**Size:** ~2.5KB  
**LOD:** Low  
**Purpose:** Maps task keywords to domain agent files and on-demand reference files.

---

## [S-TIGHT]

Two routing tables govern agent navigation: the Domain Agent File Routing table maps broad task keywords to domain AGENTS.md files, and the Prompt-Triggered References table loads specific files on demand when task keywords match.

---

## Domain Agent File Routing

When the task involves one of these domains, read the corresponding file before proceeding.

| Task keywords | Read this file |
|----------|---------------|
| servers, APIs, connectivity, latency, infrastructure, deployment, monitoring, orchestration, orchestrate, route, routing, classify, classification, complexity, decompose, decomposition, fan out, distribute, distribution, workload, queue, worker, task, submit, collect, sync, artifact, node, cluster, meta-, framework, performance, ansible, script, scripts, bash, playbook | `./AGENTS.md` (this domain — stay here) |
| trade logging, reconciliation, P&L, accounting, balances, fees, settlement | `../bookkeeping/AGENTS.md` |
| research, analysis, signals, backtesting, data, indicators, sentiment | `../market-research/AGENTS.md` |
| positions, orders, risk, allocation, sizing, exits, stops, portfolio | `../position-management/AGENTS.md` |
| position status, monitoring, risk limit checks, portfolio state | `../position-management/AGENTS.md` (use `position-monitor` agent) |

## Prompt-Triggered References

[LOD: Medium]

These files are loaded on demand when a task matches their keywords.

| Keywords | File |
|----------|------|
| network troubleshooting, node offline, driver issue, r8169 | `./prompts/network-troubleshooting.md` |
| pi-keyword-router, keyword routing, model routing | `./extensions/pi-keyword-router/README.md` |
| meta-orchestration, orchestration framework, complexity classification | `../personal-vault/01-Projects/Carlos-Trading-Desk/planning/` |
| task decomposition, sub-task routing, model assignment, fan out | `../personal-vault/01-Projects/Carlos-Trading-Desk/planning/` |
| package hygiene, DRY violation, duplicate agents, package structure, package policy | `./packages/PACKAGE-HYGIENE-POLICY.md` |
| sshfs, parallel filesystem, distributed files, mount workspace, lab node files, fan out files, batch file process, file aggregation across nodes, parallel scan, distributed grep, parallel log analysis, auto-mount, ensure mounted, sshfs-integration | `./packages/sshfs-integration/skills/sshfs-integration/SKILL.md` |

---

*Load [conventions-and-rules.md](./conventions-and-rules.md) for behavioral rules. Load [documentation-loading.md](./documentation-loading.md) for full documentation loading strategy.*