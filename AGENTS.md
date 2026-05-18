# Workshop — Unified Root Router

**Purpose:** Execution workspace for all code, scripts, scrapers, data processing, infrastructure, and build systems.  
**Counterpart:** `../personal-vault/` — documentation and knowledge management.  
**Rule:** This file is a router only. Match keywords, route to the correct domain or project.

## [S-TIGHT]

Unified routing hub. Detects domain from prompt keywords, routes to domain/project agents, loads only the phase file needed for the current cognitive stage. All markdown docs live in personal-vault.

---

## Phase-Based Instruction Loading

This file is a **router only**. Load the phase file matching your current cognitive stage.

| Phase | File | Purpose | Load When | Size |
|-------|------|---------|-----------|------|
| 1 — Domain Activation | `.pi/agents/phases/phase-1-domain-activation.md` | Detect domain from prompt keywords | **Every prompt** | ~630 tokens |
| 2 — Planning | `.pi/agents/phases/phase-2-planning.md` | Framework readiness, complexity, decomposition | After domain activated | ~850 tokens |
| 3 — Execution | `.pi/agents/phases/phase-3-execution.md` | Must Always / Must Never, tool rules, safety | During active work | ~2,800 tokens |
| 4 — Quality Check | `.pi/agents/phases/phase-4-quality-check.md` | Verify checklist before declaring done | After work complete | ~1,300 tokens |
| 5 — Documentation | `.pi/agents/phases/phase-5-documentation.md` | Session notes, status, backlog | Before ending session | ~700 tokens |

**Index:** `.pi/agents/phases/phase-index.json` — machine-readable phase map.

**Convention:** Only load the phase you need. Do not load all phases in one inference.

**Skill Loading Convention:** Only load the skill matching the active task. Do not load skills speculatively.

---

## Quick Reference

### Model Routing

| Route | Model | Triggers |
|-------|-------|----------|
| ultra-reasoning | ollama-cloud/kimi-k2.6 | think deeply, comprehensive, thorough |
| reasoning | ollama-cloud/qwen3.5:397b | analyze, evaluate, decide, research, plan |
| coding | ollama-cloud/deepseek-v4-pro | code, implement, develop, debug |
| vision | ollama-cloud/qwen3-vl:235b | image, screenshot, chart, visual |
| structured | ollama/gemma4:e4b | log, reconcile, parse, format, ledger |
| monitoring | ollama/qwen3.5:4b | status, check, ping, health, monitor |
| infrastructure | ollama/qwen3:8b | server, deploy, network, ansible, node, orchestration |
| (default) | ollama/gemma4:e4b | — |

---

## Project Map

| Keywords | Route To |
|----------|----------|
| kingdom, warfare, leadership, mike brewer, nancy, training, curriculum, flashcard, study aid, mkdocs, deliverance, demonology | `./01-Projects/kingdom-warfare-leadership/AGENTS.md` |
| doc-standards, enablement, scaffold, project template, topology, documentation standard, prompt thread, workbench, focus | `./01-Projects/doc-standards-enablement/AGENTS.md` |
| project-blueprint, blueprint, orchestration, domain routing, agent definition, structural routing, wiki, post-completion, golden path, learning loop, library | `./01-Projects/project-blueprint/AGENTS.md` |
| decompose, execute, verify, decomposition, cost-optimization, verification | `./01-Projects/decompose-execute-verify/AGENTS.md` or `.pi/agents/decomposer.md` |
| health, monitor, RAM, CPU, swap, system status, resource, saturation | `./01-Projects/health-monitor/AGENTS.md` |
| model, pilot, ollama, local model, model routing, models.json | `./01-Projects/local-model-pilot/AGENTS.md` |
| node, router, routing plan, node scoring, execution location | `./01-Projects/node-router/AGENTS.md` |
| sshfs, mount, remote, lab node, workspace mount | `./01-Projects/sshfs-accessible/AGENTS.md` |

---

## Domain Agent File Routing

| Task keywords | Read this file |
|----------|---------------|
| servers, APIs, infrastructure, deployment, monitoring, orchestration, routing, classify, complexity, decompose, queue, worker, task, node, cluster, performance, ansible, script, bash, playbook | `./01-Projects/*/AGENTS.md` or `./03-Resources/Infrastructure/*/AGENTS.md` |
| trade logging, reconciliation, P&L, accounting, balances, fees | `./02-Areas/Trading/bookkeeping/AGENTS.md` |
| research, analysis, signals, backtesting, data, indicators | `./02-Areas/Trading/market-research/AGENTS.md` |
| positions, orders, risk, allocation, sizing, exits, portfolio | `./02-Areas/Trading/position-management/AGENTS.md` |
| position status, monitoring, risk limits | `./02-Areas/Trading/position-management/AGENTS.md` |
| network troubleshooting, node offline, driver issue | `./03-Resources/Infrastructure/technical-infrastructure-legacy/prompts/network-troubleshooting.md` |
| scripts, automation, tooling, data processing | `./03-Resources/Trading/scripts/` |
| lab specs, hardware, node configuration | `./03-Resources/Infrastructure/lab-specs/` |
| legacy designs, architecture docs | `./03-Resources/Infrastructure/technical-infrastructure-legacy/` |

After reading the domain file, follow its instructions. Then load the appropriate phase file.

---

## Default Execution Pattern

| Task Complexity | Default Action | Override |
|-----------------|---------------|----------|
| Single turn, well-scoped | Execute directly via model router | User specifies model |
| Multi-step or complex | `/run decomposer` → local execution → `/run verifier` | User explicitly says "use cloud" |
| Verification fails | Re-run failing sub-task only on cloud | — |

**Rule:** Do not manually pick models. Let the model router and decomposer make routing decisions.

**Reference:** See `.pi/APPEND_SYSTEM.md` for the full cost-optimized execution framework.

---

### Skill Auto-Load Rules — MANDATORY

Before executing any task, check the user prompt and activated domain against this table. If a match is found, **load the skill via `read` before any work begins**. The skill takes precedence over general conventions.

| Trigger (keywords or domain) | Skill to load | Load path |
|--------------------------------|---------------|-----------|
| wiki, documentation, docs, markdown, `*.md`, README, status, session-notes, backlog, activity log, manifest, planning doc | **doc-standards** | `/Users/friasc/.pi/agent/git/github.com/carlosfrias/doc-standards/skills/doc-standards/SKILL.md` |
| wiki, documentation, docs, markdown, `*.md`, README, status, session-notes, backlog, activity log, manifest, planning doc | **vault taxonomy mapping** | `../personal-vault/01-Projects/Carlos-Trading-Desk/archive/Doc-Standards Vault Taxonomy.md` |

**Hard Rule:** If the task involves creating, editing, or reviewing any file ending in `.md`, BOTH skills MUST be loaded first. Do not skip this step because the task seems "small" or "quick."

---

## Workspace Layout

```
workshop/
├── AGENTS.md                          ← YOU ARE HERE
├── 01-Projects/                       # Active project code
│   ├── kingdom-warfare-leadership/    # Study aids, scrapers, site
│   ├── doc-standards-enablement/      # Scaffolding, validation
│   ├── project-blueprint/             # Project orchestration
│   ├── decompose-execute-verify/      # Cost-optimized execution
│   ├── health-monitor/                # Resource monitoring
│   ├── local-model-pilot/             # Ollama LLM routing
│   ├── node-router/                   # Execution location scoring
│   └── sshfs-accessible/              # Remote workspace mounts
├── 02-Areas/Trading/                  # Trading operations
│   ├── bookkeeping/                   # Ledger, P&L, reconciliation
│   ├── market-research/               # Analysis, signals, backtesting
│   └── position-management/           # Orders, risk, allocation
├── 03-Resources/                      # Reference, infrastructure, legacy
│   ├── Infrastructure/                # 24 infrastructure packages
│   ├── Trading/scripts/               # Operational scripts
│   └── Wiki/                          # Trading desk wiki
├── .pi/agents/phases/                 # Phase-based routing files
└── .pi/agents/                        # Agent + chain definitions
```

---

## Cross-Reference

| From | To | Path |
|------|----|------|
| Workshop → Docs | `../../personal-vault/01-Projects/{project}/` | Always relative from workshop root |
| Docs → Workshop | `../../workshop/01-Projects/{project}/` | Always relative from personal-vault root |
| Workshop → Vault (areas) | `../../personal-vault/02-Areas/` | For domain documentation |

## Discovery Path

```
1. carlos-desktop/AGENTS.md              ← Pick workspace (broad keywords)
2. workshop/AGENTS.md                    ← YOU ARE HERE (pick project/domain)
3. workshop/01-Projects/{project}/AGENTS.md ← Tech stack, entry points, code conventions
   OR
   workshop/02-Areas/Trading/{area}/AGENTS.md ← Domain rules, workflows
4. personal-vault/01-Projects/{project}/   ← Documentation, plans, session history
```

---

*Last updated: 2026-05-18 — merged ai-trading-workspace into workshop; trading keywords now route here*
