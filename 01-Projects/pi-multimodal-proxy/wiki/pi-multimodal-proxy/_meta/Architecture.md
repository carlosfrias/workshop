# Architecture — pi-multimodal-proxy

This document explains the architectural decisions behind pi-multimodal-proxy's orchestration design.

## Core Principles

### 1. Structural Routing

The routing table lives in the root `AGENTS.md`. Any harness that discovers `AGENTS.md` files can follow it — no harness-specific configuration required.

**Why:** Harness-agnostic design means the project works in pi, Cursor, Claude Code, or any system that reads `AGENTS.md` files. No vendor lock-in.

**Implementation:**
```markdown
## Domain Routing

| Keywords | Read this file |
|----------|---------------|
| vision, image, OCR, screenshot | `./vision-agent/AGENTS.md` |
| wiki, documentation, research | `./wiki/AGENTS.md` |
```

### 2. Self-Contained Domains

Each domain folder has exactly one `AGENTS.md` containing all context, conventions, rules, and quality checks. No supplementary files (no `CONTEXT.md`, `REFERENCES.md`, or `QualityControl.md`).

**Why:**
- Single source of truth per domain
- Reduces file discovery overhead for low-context models
- Easier to maintain and update

**Implementation:**
```
vision-agent/
└── AGENTS.md    # Everything: conventions, rules, quality checks, documentation protocol
```

### 3. inheritProjectContext: false

Sub-agents discover context independently via `cwd` walk. The orchestrator does NOT inject its context into sub-agents.

**Why:**
- Eliminates redundancy (orchestrator context ≠ sub-agent context)
- Ensures sub-agents always get the latest version of context files
- Reduces token waste from duplicated context

**Implementation:**
```yaml
inheritProjectContext: false
cwd: ./vision-agent
```

## Token Budget Design

| Role | Tokens | Content |
|------|--------|---------|
| Orchestrator (permanent) | ~1.2KB | Identity + routing table only |
| Sub-agent (ephemeral) | ~4-5KB | Full domain context, loaded once, released on completion |

**No redundancy** between orchestrator and sub-agent context.

### Per-Operation Budgets

| Operation | Budget | Rationale |
|-----------|--------|-----------|
| Vision analysis (single image) | <2KB input + <4KB output | Most OCR/analysis tasks fit comfortably |
| Multi-image comparison | <4KB input + <6KB output | Allows describing multiple images + differences |
| OCR extraction | <3KB input + <5KB output | Structured output is more compact than prose |
| Complex visual reasoning | <6KB total | Triggers decompose-execute-verify if exceeded |

## File Layout

```
pi-multimodal-proxy/
├── AGENTS.md                          # Root: identity + routing table (~1.5KB)
├── .pi/
│   ├── APPEND_SYSTEM.md               # Identity only (~200 bytes)
│   └── agents/
│       └── vision-agent.md            # Agent definition (~3.5KB)
├── vision-agent/
│   └── AGENTS.md                       # Domain context (~2.5KB)
└── wiki/
    └── pi-multimodal-proxy/
        ├── Home.md                     # Wiki index
        ├── vision-agent/
        │   └── Activity Log.md         # Running log of vision tasks
        └── _meta/
            ├── Architecture.md         # This file
            ├── Agent Definitions.md    # All agents catalog
            └── Documentation Standard.md
```

## Routing Flow

1. User submits request to orchestrator
2. Orchestrator matches keywords to routing table in root `AGENTS.md`
3. Orchestrator loads target domain `AGENTS.md` (e.g., `./vision-agent/AGENTS.md`)
4. Orchestrator invokes sub-agent with domain context
5. Sub-agent reads domain `AGENTS.md` via `cwd` walk (independent discovery)
6. Sub-agent performs task, documents in wiki, reports results
7. Orchestrator receives result, delivers to user

## Why This Design?

| Problem | Traditional Approach | This Approach |
|---------|---------------------|---------------|
| Context bloat | Inject all context into every agent | Each agent loads only what it needs |
| File sprawl | CONTEXT.md, RULES.md, QUALITY.md scattered across domain | Single AGENTS.md per domain |
| Harness lock-in | Custom routing per IDE/tool | Harness-agnostic routing table |
| Redundancy | Orchestrator context duplicated in sub-agents | Sub-agents discover context independently |
| Token waste | Full context loaded for every task | Domain context loaded once, released on completion |

## References

- [Root AGENTS.md](../../../AGENTS.md) — Routing table and conventions
- [Vision Agent Domain](../../../vision-agent/AGENTS.md) — Full domain context
- [Agent Definitions](./Agent Definitions.md) — All agents catalog

---

*Last updated: 2026-05-24*
