---
title: Product Catalog
description: Distribution-ready packages from the technical-infrastructure workspace
---

# Product Catalog

Packages developed and proven in the `technical-infrastructure/` workspace. Each is a **prompt-template distribution** — the `SKILL.md` (or equivalent prompt) is the product. The code in each package is the proven reference output.

## Installation

All packages install via `pi install`:

```bash
pi install github:carlosfrias/<package-name>
```

## Active Products

| Product | Type | Purpose | Install |
|---------|------|---------|---------|
| **[pi-keyword-router](/technical-infrastructure/products/pi-keyword-router)** | Extension | Dynamic keyword-based model routing | `pi install github:carlosfrias/pi-keyword-router` |
| **[routing-transparency](/technical-infrastructure/products/routing-transparency)** | Extension | TUI footer with routing visibility, cost tracking, billing | `pi install github:carlosfrias/pi-routing-transparency` |
| **[project-blueprint](/technical-infrastructure/products/project-blueprint)** | Skill | Scaffold orchestrated projects with domains and agents | `pi install github:carlosfrias/project-blueprint` |
| **[gist-message-queue](/technical-infrastructure/products/gist-message-queue)** | Skill | Async agent-to-agent communication via GitHub Gist | `pi install github:carlosfrias/gist-message-queue` |
| **[decomposition-skill](/technical-infrastructure/products/decomposition-skill)** | Skill | Cost-optimized task execution (decompose → execute → verify) | `pi install github:carlosfrias/decomposition-skill` |
| **[local-model-pilot](/technical-infrastructure/products/local-model-pilot)** | Skill | Configure Ollama local LLM routing for Apple Silicon | `pi install github:carlosfrias/local-model-pilot` |
| **[playbook-executor](/technical-infrastructure/products/playbook-executor)** | Skill | Ansible playbook execution triggered by natural-language keywords | `pi install github:carlosfrias/playbook-executor` |
| **[trading-agents](/technical-infrastructure/products/trading-agents)** | Agent Package | Reusable agent definitions (decomposer, verifier) | `pi install github:carlosfrias/trading-agents` |

## Design Work

| Document | Purpose |
|----------|---------|
| **[Trading Lab Architecture](/technical-infrastructure/products/trading-lab-architecture)** | Multi-node orchestration design and deployment patterns |
| **AgenticOS Raw Design** | Complete agentic operating system architecture (675-line specification) — Archived for reference |

## Active Debugging

| Investigation | Status | Plan | Backlog | Orchestration |
|---------------|--------|------|---------|-------------|
| **[Keyword Router Routing Regression](/technical-infrastructure/products/keyword-router-debug/index.md)** | ✅ Core Fixed | [`index.md`](./keyword-router-debug/index.md) | [`BACKLOG-MASTER.md`](./keyword-router-debug/BACKLOG-MASTER.md) | [`AGENTS.md`](./keyword-router-debug/AGENTS.md) |

## How Products Are Made

These packages follow the project-blueprint pattern:

1. **Develop** in the workspace — code, test, iterate
2. **Extract** into a standalone package directory with its own `.git`
3. **Template-ize** the setup process into a `SKILL.md` prompt
4. **Publish** to GitHub as a distribution package
5. **Document** in the workspace VitePress site (here)

The workspace itself is a project-blueprint exemplar — use it as a reference for your own package factory.
