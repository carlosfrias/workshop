# Domain Agent File Routing

**Section ID:** domain-routing  
**Size:** ~1.5KB  
**LOD:** Low  
**Purpose:** Task-keyword-to-domain-file routing for Trading areas and Infrastructure resources.

---

## [S-TIGHT]

Match task keywords to domain agent files. Trading tasks route to Areas subdirectories; Infrastructure tasks route to Resources. After reading the domain file, follow its instructions, then load the appropriate phase file.

---

## Domain Routing Table

| Task Keywords | Route To |
|---------------|----------|
| servers, APIs, infrastructure, deployment, monitoring, orchestration, routing, classify, complexity, decompose, queue, worker, task, node, cluster, performance, ansible, script, bash, playbook | `./01-Projects/*/AGENTS.md` or `./03-Resources/Infrastructure/*/AGENTS.md` |
| trade logging, reconciliation, P&L, accounting, balances, fees, bookkeeping, ledger, beancount, import pipeline, staging, ingest, pdfplumber, schwab statement, brokerage statement, ai cost, model cost, inference cost, token cost, cost tracking, compute cost, double-entry, financial records | `./02-Areas/Trading/bookkeeping/AGENTS.md` |
| research, analysis, signals, backtesting, data, indicators | `./02-Areas/Trading/market-research/AGENTS.md` |
| positions, orders, risk, allocation, sizing, exits, portfolio | `./02-Areas/Trading/position-management/AGENTS.md` |
| position status, monitoring, risk limits | `./02-Areas/Trading/position-management/AGENTS.md` |
| network troubleshooting, node offline, driver issue | `./03-Resources/Infrastructure/technical-infrastructure-legacy/prompts/network-troubleshooting.md` |
| scripts, automation, tooling, data processing | `./03-Resources/Trading/scripts/` |
| lab specs, hardware, node configuration | `./03-Resources/Infrastructure/lab-specs/` |
| legacy designs, architecture docs | `./03-Resources/Infrastructure/technical-infrastructure-legacy/` |

---

## After Domain Routing

1. Read the matched domain `AGENTS.md` for domain-specific rules
2. Load the appropriate phase file from `.pi/agents/phases/`
3. Execute per domain + phase instructions

---

*Next: For project-level routing, load [project-map.md](./project-map.md). For workspace layout, load [./workspace-structure.md](./workspace-structure.md).*