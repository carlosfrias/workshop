# Project Map

**Section ID:** project-map  
**Size:** ~2.5KB  
**LOD:** Low  
**Purpose:** Keyword-to-project routing table. Match prompt keywords to the correct project AGENTS.md.

---

## [S-TIGHT]

Match keywords from the prompt to the project AGENTS.md file. Each project has its own router with domain-specific rules. After reading the project file, follow its instructions, then load the appropriate phase file.

---

## Project Routing Table

| Keywords | Route To |
|----------|----------|
| kingdom, warfare, leadership, mike brewer, nancy, training, curriculum, flashcard, study aid, mkdocs, deliverance, demonology | `./01-Projects/kingdom-warfare-leadership/AGENTS.md` |
| doc-standards, enablement, scaffold, project template, topology, documentation standard, prompt thread, workbench, focus | `./01-Projects/doc-standards-enablement/AGENTS.md` |
| project-blueprint, blueprint, orchestration, domain routing, agent definition, structural routing, wiki, post-completion, golden path, learning loop, library | `./02-Areas/project-blueprint/AGENTS.md` |
| clief, core-agent-architecture, evaluation-metrics, workflow-design | `./01-Projects/clief/AGENTS.md` |
| decompose, execute, verify, decomposition, cost-optimization, verification, fleet-dispatcher, cascade | `./01-Projects/decompose-execute-verify/AGENTS.md` or `.pi/agents/decomposer.md` or `.pi/agents/fleet-dispatcher.md` |
| health, monitor, RAM, CPU, swap, system status, resource, saturation | `./01-Projects/health-monitor/AGENTS.md` |
| model, pilot, ollama, local model, model routing, models.json | `./01-Projects/local-model-pilot/AGENTS.md` |
| node, router, routing plan, node scoring, execution location | `./01-Projects/node-router/AGENTS.md` |
| cross-node, coms-net, coms net, fleet, hub, multi-machine, pi-cross-node, fleet-dispatcher cascade | `./01-Projects/pi-cross-node-comms/AGENTS.md` |
| sshfs, mount, remote, lab node, workspace mount | `./01-Projects/sshfs-accessible/AGENTS.md` |
| cost, billing, tier, margin, invoice, cost-aware, cost model, cost per token, depreciation, power cost, billing engine, cost tracker, cost status, cost audit | `./01-Projects/cost-aware-routing/AGENTS.md` |
| nextcloud, cloud storage, file sync, collaboration, private cloud, fnet2, nc config, nc deploy, nc ansible | `./01-Projects/nextcloud/AGENTS.md` |
| workflow, orchestration, cadence, temporal, taskwarrior, research workflow, durable execution, evaluate orchestration, obsidian tasks, obsidian projects, obsidian bases, obsidian CLI, dataview | `./01-Projects/workflow-orchestration-research/AGENTS.md` |
| bible, scripture, study, exegesis, word study, devotional, passage, commentary, Hebrew, Greek, theology, doctrine, his-desk | `./01-Projects/his-desk/AGENTS.md` |

---

## After Project Routing

1. Read the matched project `AGENTS.md` for domain-specific rules
2. Load the appropriate phase file from `.pi/agents/phases/`
3. Execute per project + phase instructions

---

*Next: For domain-level routing (Trading areas, Infrastructure), load [domain-routing.md](./domain-routing.md).*