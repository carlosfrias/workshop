# Technical Infrastructure

Managing servers, APIs, network connectivity, and deployment pipeline that power Carlos' Desktop and the trading-desk domain.

## [S-TIGHT]

Technical infrastructure routes all server, API, network, deployment, orchestration, and Ansible work. Verify TI-011 framework readiness before multi-node work. Follow Must Always/Never rules strictly. Use routing tables to navigate to domain agents and prompt-triggered references on demand.

---

## Domain Routing Table

| Section | File | LOD | When to Load |
|---------|------|-----|-------------|
| Conventions, Must Always/Never rules | [conventions-and-rules.md](./routing/conventions-and-rules.md) | Low | Any infrastructure task |
| Quality Checklist, TI-011 Framework Readiness | [quality-and-readiness.md](./routing/quality-and-readiness.md) | Medium | Before completing tasks or multi-node work |
| Domain routing, prompt-triggered references | [routing-tables.md](./routing/routing-tables.md) | Low | When navigating to other domains or loading on-demand files |
| Documentation loading, backlog management | [documentation-loading.md](./routing/documentation-loading.md) | Low | When accessing AGENTS-full, model routing, or backlog |

## Load Directive

| Model Tier | Max Context | Load These Only |
|------------|-------------|-----------------|
| **Low local** (<4K ctx) | This manifest + 1 section relevant to task | |
| **Medium local** (~8K ctx) | This manifest + conventions-and-rules + 1 additional section | |
| **High local** (~32K ctx) | This manifest + all sections | |
| **Cloud** (>32K ctx) | Load as needed; prefer targeted sections | |

## Quick Task Routing

| Task | Load |
|------|------|
| Any infrastructure task | [conventions-and-rules.md](./routing/conventions-and-rules.md) |
| Multi-node or orchestration work | [quality-and-readiness.md](./routing/quality-and-readiness.md) |
| Finding which domain handles a task | [routing-tables.md](./routing/routing-tables.md) |
| Accessing full docs or backlog | [documentation-loading.md](./routing/documentation-loading.md) |
| Before completing any task | [quality-and-readiness.md](./routing/quality-and-readiness.md) (Quality Checklist) |

---

*Decomposed 2026-05-21. Original monolithic AGENTS.md split into 4 routing sections for low-capacity model compatibility.*