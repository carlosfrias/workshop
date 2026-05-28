# His Desk — Wiki Home

This wiki documents the work done by each domain in the His Desk Bible study project. Domains are the primary content — each domain owns its section and maintains it.

## Domain Index

Each domain has its own wiki section with an activity log and any additional pages the domain agent creates over time.

| Domain | Activity Log | Description |
|--------|-------------|-------------|
| Study | [study/Activity Log](study/Activity%20Log.md) | Bible passage analysis, exegesis, word studies, commentary |
| Devotional | [devotional/Activity Log](devotional/Activity%20Log.md) | Devotional content, meditation guides, prayer frameworks |
| Data | [data/Activity Log](data/Activity%20Log.md) | Bible APIs, scrapers, data pipelines |
| Site | [site/Activity Log](site/Activity%20Log.md) | MkDocs site build, deployment, configuration |

## Project Structure

```
his-desk/
├── AGENTS.md                          # Conventions + routing table
├── .pi/
│   ├── APPEND_SYSTEM.md               # Identity only
│   └── agents/                        # Agent definitions
│       ├── study.md
│       ├── devotional.md
│       ├── data.md
│       └── site.md
├── study/
│   └── AGENTS.md                       # Study domain context
├── devotional/
│   └── AGENTS.md                       # Devotional domain context
├── data/
│   └── AGENTS.md                       # Data domain context
├── site/
│   └── AGENTS.md                       # Site domain context
└── wiki/
    └── his-desk/
        ├── Home.md                      # This page
        ├── study/                       # Study domain wiki
        ├── devotional/                  # Devotional domain wiki
        ├── data/                        # Data domain wiki
        ├── site/                        # Site domain wiki
        └── _meta/                       # Reference docs
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
- [Agent Definitions](_meta/Agent%20Definitions.md) — All agents with frontmatter, descriptions, and usage
- [Sample Prompts](_meta/Sample%20Prompts.md) — Ready-to-use prompts for each domain
- [Documentation Standard](_meta/Documentation%20Standard.md) — Conventions, formatting, Activity Log format

## For Non-Technical Users

See [_meta/Sample Prompts](_meta/Sample%20Prompts.md) for copy-paste prompts you can use to interact with each domain. No command-line knowledge needed — just type the prompt naturally.

---

> 📋 **Checkbox states:** `[ ]` To Do | `[/]` In Progress | `[~]` Good Enough | `[x]` Done | `[>]` Deferred | `[!]` Blocked | `[-]` Cancelled — [full legend](../../../../../personal-vault/01-Projects/doc-standards/wiki/doc-standards/reference/Checkbox-State-Legend.md)
*Last updated: 2026-05-27*
