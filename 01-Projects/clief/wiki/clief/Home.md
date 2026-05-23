# Clief Notes — Wiki Home

This wiki documents the work done by each domain in the Clief Notes project. Domains are the primary content — each domain owns its section and maintains it.

## Domain Index

Each domain has its own wiki section with an activity log and any additional pages the domain agent creates over time.

| Domain | Activity Log | Description |
|--------|-------------|-------------|
| vault | [vault/Activity Log](vault/Activity Log.md) | Study notes, curriculum tracking, knowledge management |
| workshop | [workshop/Activity Log](workshop/Activity Log.md) | Code, ICM implementations, practice exercises |

## Project Structure

```
workshop/01-Projects/clief/
├── AGENTS.md                          # Conventions + routing table
├── .pi/
│   ├── APPEND_SYSTEM.md               # Identity only
│   └── agents/                        # Agent definitions
│       ├── vault.md
│       └── workshop.md
├── vault/
│   └── AGENTS.md                       # Study & knowledge domain
├── workshop/
│   ├── AGENTS.md                       # Code & implementation domain
│   └── references/                     # ICM paper, source code
└── wiki/                               # This wiki
    └── clief/
        ├── Home.md                      # This page — domain index
        ├── vault/                       # Vault wiki — front and center
        │   └── Activity Log.md
        ├── workshop/                    # Workshop wiki
        │   └── Activity Log.md
        └── _meta/                       # Reference docs (reachable, non-central)
            ├── Architecture.md
            ├── Agent Definitions.md
            ├── Curriculum.md
            ├── Study Schedule.md
            └── Sample Prompts.md
```

## Token Budget

| Role | Size | Content |
|------|------|---------|
| Orchestrator (permanent) | ~1.7KB | Identity + routing table |
| Sub-agent (ephemeral) | ~5-6KB | Full domain context, loaded once |

No redundancy between orchestrator and sub-agent context.

## Reference Documentation

Project-level reference pages live in [_meta/](_meta/):

- [Architecture](_meta/Architecture.md) — Why structural routing, self-contained domains, and isolated context
- [Agent Definitions](_meta/Agent Definitions.md) — All agents with frontmatter, descriptions, and usage
- [Curriculum](_meta/Curriculum.md) — Clief Notes curriculum structure and module descriptions
- [Study Schedule](_meta/Study Schedule.md) — 45 min/day, 3x/week study plan
- [Sample Prompts](_meta/Sample Prompts.md) — Ready-to-use prompts for each domain
- [Documentation Standard](_meta/Documentation Standard.md) — Conventions, formatting, Activity Log format

## For Non-Technical Users

See [_meta/Sample Prompts](_meta/Sample Prompts.md) for copy-paste prompts you can use to interact with each domain. No command-line knowledge needed — just type the prompt naturally.