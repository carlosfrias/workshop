# {project_name} — Wiki Home

This wiki documents the work done by each domain in this project. Domains are the primary content — each domain owns its section and maintains it.

## Domain Index

Each domain has its own wiki section with an activity log and any additional pages the domain agent creates over time.

| Domain | Activity Log | Description |
|--------|-------------|-------------|
| {domain1} | [{domain1}/Activity Log]({domain1}/Activity Log.md) | {domain1_description} |
| {domain2} | [{domain2}/Activity Log]({domain2}/Activity Log.md) | {domain2_description} |

## Project Structure

```
{project_root}/
├── AGENTS.md                          # Conventions + routing table
├── .pi/
│   ├── APPEND_SYSTEM.md               # Identity only
│   └── agents/                        # Agent definitions & chains
├── {domain1}/
│   └── AGENTS.md                       # Self-contained domain context
├── {domain2}/
│   └── AGENTS.md                       # Self-contained domain context
└── wiki/                               # This wiki
    └── {project_name}/
        ├── Home.md                      # This page — domain index
        ├── {domain1}/                   # Domain wiki — front and center
        │   └── Activity Log.md
        ├── {domain2}/                   # Domain wiki
        │   └── Activity Log.md
        └── _meta/                       # Reference docs (reachable, non-central)
            ├── Architecture.md
            ├── Agent Definitions.md
            ├── Chain Files.md
            ├── System & Context Files.md
            ├── Sample Prompts.md
            └── Model Substitutions.md
```

## Token Budget

| Role | Size | Content |
|------|------|---------|
| Orchestrator (permanent) | ~1.2KB | Identity + routing table |
| Sub-agent (ephemeral) | ~4-5KB | Full domain context, loaded once |

No redundancy between orchestrator and sub-agent context.

## Reference Documentation

Project-level reference pages live in [_meta/](_meta/):

- [Architecture](_meta/Architecture.md) — Why structural routing, self-contained domains, and isolated context
- [Agent Definitions](_meta/Agent Definitions.md) — All agents with frontmatter, descriptions, and usage
- [Chain Files](_meta/Chain Files.md) — Multi-step workflow pipelines
- [System & Context Files](_meta/System & Context Files.md) — File layout, token budgets, routing table design
- [Sample Prompts](_meta/Sample Prompts.md) — Ready-to-use prompts for each domain
- [Model Substitutions](_meta/Model Substitutions.md) — Cloud/local model mapping
- [Documentation Standard](_meta/Documentation Standard.md) — Conventions, formatting, Activity Log format, quality checklist

## For Non-Technical Users

See [_meta/Sample Prompts](_meta/Sample Prompts.md) for copy-paste prompts you can use to interact with each domain. No command-line knowledge needed — just type the prompt naturally.

---

> 📋 **Checkbox states:** `[ ]` To Do | `[/]` In Progress | `[~]` Good Enough | `[x]` Done | `[>]` Deferred | `[!]` Blocked | `[-]` Cancelled — [[01-Projects/doc-standards/wiki/doc-standards/reference/Checkbox-State-Legend|full legend]]