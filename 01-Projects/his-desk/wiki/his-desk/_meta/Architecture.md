# Architecture

## Why Structural Routing

His Desk uses **structural routing** — a pattern where the routing table lives in the root `AGENTS.md`, and each domain folder has exactly one `AGENTS.md` containing all conventions, rules, quality checks, and instructions for that domain.

**Benefits:**
- **Harness-agnostic** — Any system that reads `AGENTS.md` files can navigate the project (pi, Cursor, Claude Code, etc.)
- **Token-efficient** — The orchestrator loads only identity + routing (~1.2KB). Sub-agents load their domain context (~4-5KB) only when needed
- **Self-contained** — Each domain's `AGENTS.md` has everything it needs. No scattered supplementary files

## Why Self-Contained Domains

Each domain `AGENTS.md` includes:
- Conventions
- Must Always / Must Never rules
- Quality checklist
- Common mistakes table
- Documentation protocol
- Cross-domain references

This means a sub-agent never needs to look elsewhere for domain-specific context. One file, one read, all the rules.

## Why `inheritProjectContext: false`

Sub-agents discover context independently via `cwd` walk. The orchestrator does NOT inject its context into sub-agents. This eliminates redundancy and ensures sub-agents always get the latest version of context files.

## Two-Workspace Architecture

His Desk spans two workspaces:

| Component | Location | Purpose |
|-----------|----------|---------|
| Vault (knowledge) | `personal-vault/01-Projects/his-desk/` | Notes, study guides, commentary, devotionals |
| Workshop (execution) | `workshop/01-Projects/his-desk/` | Code, tools, scrapers, site builds |

Cross-references use relative paths between the two workspaces.

## Token Budget

| Role | Size | Content |
|------|------|---------|
| Orchestrator (permanent) | ~1.2KB | Identity + routing table |
| Sub-agent (ephemeral) | ~4-5KB | Full domain context, loaded once |

No redundancy between orchestrator and sub-agent context.