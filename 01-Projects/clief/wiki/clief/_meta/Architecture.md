# Architecture

## Why Structural Routing

Clief Notes uses structural routing: the root `AGENTS.md` contains a keyword → file mapping. Any harness that discovers `AGENTS.md` files can follow it. No harness-specific configuration for routing.

## Why Self-Contained Domains

Each domain folder (`vault/`, `workshop/`) has exactly one `AGENTS.md` containing all conventions, rules, quality checks, and instructions. No supplementary files (no `CONTEXT.md`, `REFERENCES.md`, or `QualityControl.md`). Everything a domain agent needs is in one place.

## Why `inheritProjectContext: false`

Sub-agents discover context independently via `cwd` walk. The orchestrator does not inject its context into sub-agents. This eliminates redundancy and ensures sub-agents always get the latest version of context files.

## ICM Connection

The project itself follows ICM principles:
- **Layer 0 (CLAUDE.md equivalent):** Root `AGENTS.md` — project identity and routing
- **Layer 1 (CONTEXT.md equivalent):** Domain `AGENTS.md` files — domain-specific context and rules
- **Layer 2 (Stage CONTEXT equivalent):** Wiki activity logs and study notes — task-specific context
- **Layer 3 (Reference material):** ICM paper, source code, curriculum structure — stable knowledge
- **Layer 4 (Working artifacts):** Study notes, exercise outputs — per-session content

## Token Budget

| Role | Size | Content |
|------|------|---------|
| Orchestrator (permanent) | ~1.7KB | Identity + routing table |
| Sub-agent (ephemeral) | ~5-6KB | Full domain context, loaded once |

No redundancy between orchestrator and sub-agent context.