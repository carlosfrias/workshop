# pi-multimodal-proxy — Wiki Home

This wiki documents the work done by each domain in this project. Domains are the primary content — each domain owns its section and maintains it.

## Domain Index

Each domain has its own wiki section with an activity log and any additional pages the domain agent creates over time.

| Domain | Activity Log | Description |
|--------|-------------|-------------|
| vision-agent | [vision-agent/Activity Log](vision-agent/Activity Log.md) | Vision and image processing: OCR, visual analysis, diagram interpretation, screenshot analysis |

## Project Structure

```
pi-multimodal-proxy/
├── AGENTS.md                          # Conventions + routing table
├── .pi/
│   ├── APPEND_SYSTEM.md               # Identity only
│   └── agents/                        # Agent definitions & chains
│       └── vision-agent.md
├── vision-agent/
│   └── AGENTS.md                       # Self-contained domain context
└── wiki/
    └── pi-multimodal-proxy/
        ├── Home.md                      # This page — domain index
        ├── vision-agent/                # Domain wiki — front and center
        │   └── Activity Log.md
        └── _meta/                       # Reference docs (reachable, non-central)
            ├── Architecture.md
            ├── Agent Definitions.md
            └── Documentation Standard.md
```

## Token Budget

| Role | Size | Content |
|------|------|---------|
| Orchestrator (permanent) | ~1.2KB | Identity + routing table |
| Sub-agent (ephemeral) | ~4-5KB | Full domain context, loaded once |

No redundancy between orchestrator and sub-agent context.

## Token Budget by Operation

| Operation | Budget | Enforcement |
|-----------|--------|-------------|
| Vision analysis (single image) | <2KB input + <4KB output | Summarize, don't transcribe verbatim |
| Multi-image comparison | <4KB input + <6KB output | Focus on differences, not repetition |
| OCR extraction | <3KB input + <5KB output | Structured output only |
| Complex visual reasoning | <6KB total | Use decompose-execute-verify if exceeded |

## Reference Documentation

Project-level reference pages live in [_meta/](_meta/):

- [Architecture](_meta/Architecture.md) — Why structural routing, self-contained domains, and isolated context
- [Agent Definitions](_meta/Agent Definitions.md) — All agents with frontmatter, descriptions, and usage
- [Documentation Standard](_meta/Documentation Standard.md) — Conventions, formatting, Activity Log format, quality checklist

## For Non-Technical Users

See [_meta/Sample Prompts](_meta/Sample Prompts.md) for copy-paste prompts you can use to interact with the vision agent. No command-line knowledge needed — just type the prompt naturally.

---

*Last updated: 2026-05-24*
