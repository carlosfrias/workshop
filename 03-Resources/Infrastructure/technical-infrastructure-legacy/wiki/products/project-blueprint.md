---
title: project-blueprint
description: Scaffold orchestrated projects with structural routing
---

# project-blueprint

**Type:** Skill  
**Install:** `pi install github:carlosfrias/project-blueprint`

Scaffold new projects with sub-agent orchestration, structural routing, domain directories, agent definitions, chain files, and a self-documenting wiki.

## What It Does

Creates a complete project structure:
- **Root `AGENTS.md`** — Routing table with keyword dispatch
- **`.pi/agents/`** — Configurable per-domain agent definitions
- **Domain directories** — Self-contained `AGENTS.md` per domain
- **Wiki** — Activity logs, usage instructions, sample prompts
- **VitePress** — Optional HTML wiki build

## Usage

```bash
# In a new project directory
cd ~/my-new-project
pi skill project-blueprint
```

The agent interviews you and generates:
1. Project name and description
2. Domain identification
3. Agent requirements
4. Workflow chains
5. Wiki documentation

## Domain Management

After project setup, manage domains with these commands:

```bash
# List all configured domains
/list-domain

# List with full metadata (directory paths, agent files, etc.)
/list-domain --verbose

# Add a new domain
/add-domain <name> <keywords>

# Rename a domain
/rename-domain <old-name> <new-name>

# Remove a domain (with confirmation)
/remove-domain <name>
```

**Example:**
```bash
/add-domain compliance regulations audit HIPAA
/list-domain
# Output: Configured Domains (1):
#   1. compliance — regulations, audit, HIPAA
```

All domain management operations update **five touchpoints** to maintain consistency:
1. Domain directory + `AGENTS.md`
2. Agent definition in `.pi/agents/`
3. Routing table in root `AGENTS.md`
4. Chain files (if applicable)
5. Wiki documentation

## Architecture

| Principle | What It Means |
|-----------|---------------|
| **Structural routing** | Routing table in `AGENTS.md`, not harness config |
| **Self-contained domains** | One `AGENTS.md` per folder with everything needed |
| **`inheritProjectContext: false`** | Sub-agents discover context via cwd walk |
| **Minimal orchestrator load** | ~1.2KB permanent, ~4-5KB per sub-agent |

## Repository

[github.com/carlosfrias/project-blueprint](https://github.com/carlosfrias/project-blueprint)
