# Project Blueprint — Complete Build Instructions

This file contains everything needed to create the `project-blueprint` pi package from scratch. It captures all decisions, architecture, templates, prompts, agent definitions, and conventions established through iterative development.

## What You're Building

A pi skill package called `project-blueprint` that scaffolds new projects with sub-agent orchestration, structural routing, domain directories, agent definitions, chain files, and a self-documenting wiki (markdown + HTML). Installable via `pi install ./project-blueprint` or `pi install git:github.com/carlosfrias/project-blueprint`.

## Target Directory Structure

Create the package at a location of your choosing. The final structure:

```
project-blueprint/
├── package.json
├── README.md
├── skills/
│   ├── README.md
│   └── project-blueprint/
│       ├── SKILL.md
│       ├── templates/
│       │   ├── AGENTS-root.md
│       │   ├── AGENTS-domain.md
│       │   ├── APPEND_SYSTEM.md
│       │   ├── agent-domain.md
│       │   ├── chain-basic.md
│       │   ├── wiki-home.md
│       │   ├── wiki-page-stub.md
│       │   ├── wiki-activity-log.md
│       │   ├── wiki-build-README.md
│       │   ├── wiki-build-config.js
│       │   └── wiki-build-package.json
│       └── references/
│           └── architecture.md
├── prompts/
│   ├── README.md
│   ├── new-project.md
│   ├── add-domain.md
│   ├── rename-domain.md
│   ├── remove-domain.md
│   ├── list-domain.md
│   ├── integrate-wiki.md
│   └── extract-domain.md
└── agents/
    ├── README.md
    └── project-builder.md
```

---

## Core Architecture (3 Principles)

These principles govern every file in the package. Violate none of them.

1. **Structural routing** — The routing table lives in root `AGENTS.md`, not in harness-specific config. Any system that walks directories and reads `AGENTS.md` can follow it (pi, Cursor, Claude Code, etc.).

2. **Self-contained domains** — Each domain folder has exactly one `AGENTS.md` with all conventions, rules, quality checks, and instructions. No supplementary files (`CONTEXT.md`, `REFERENCES.md`, `QualityControl.md` are all forbidden).

3. **`inheritProjectContext: false`** — Sub-agents discover context independently via `cwd` walk. The orchestrator never injects its context into sub-agents. Eliminates redundancy and ensures sub-agents get the latest file versions.

---

## File Contents

### package.json

```json
{
  "name": "project-blueprint",
  "version": "1.0.0",
  "description": "Scaffold new projects with sub-agent orchestration, structural routing, domain directories, agent definitions, chain files, and a self-documenting wiki.",
  "keywords": ["pi-package"],
  "pi": {
    "skills": ["./skills"],
    "prompts": ["./prompts"],
    "agents": ["./agents"]
  }
}
```

### README.md

```markdown
# Project Blueprint

Set up a new project with smart AI agents, organized folders, and built-in documentation — one command does it all.

## What It Does

Sets up a complete project structure with:

- **Structural routing** — Keyword-based routing table in root `AGENTS.md` that any harness can follow
- **Self-contained domains** — One `AGENTS.md` per domain folder with all context, rules, and quality checks
- **Agent definitions** — `.pi/agents/` files with `inheritProjectContext: false` and `cwd` per domain
- **Chain files** — Multi-step workflow pipelines connecting agents
- **Wiki** — Auto-generated documentation with usage instructions and sample prompts
- **Minimal orchestrator load** — ~1.2KB permanent context, ~4-5KB per sub-agent invocation

## Installation

### From local path

```bash
pi install ./project-blueprint
```

### From GitHub (when published)

```bash
pi install git:github.com/carlosfrias/project-blueprint
```

## Usage

### Create a new project

| Method | Invocation |
|--------|-----------|
| Natural language | "Set up a new project for my healthcare analytics" |
| Slash command | `/new-project healthcare analytics with billing and compliance` |
| Agent | `{ agent: "project-builder", task: "..." }` |

### Manage domains in an existing project

| Command | Purpose |
|---------|---------|
| `/add-domain <name> <keywords>` | Add a new domain |
| `/rename-domain <old> <new>` | Rename across all touchpoints |
| `/remove-domain <name>` | Remove entirely (with confirmation) |

Every management operation keeps five touchpoints in sync: domain folder, agent definition, routing table, chains, and wiki.

## Architecture

Based on three principles:

1. **Structural routing** — Routing table in `AGENTS.md`, not harness-specific config. Works in pi, Cursor, Claude Code, etc.
2. **Self-contained domains** — One `AGENTS.md` per folder, no supplementary files.
3. **`inheritProjectContext: false`** — Sub-agents discover context independently. No redundancy.

See `skills/project-blueprint/references/architecture.md` for the full rationale.

## What's Included

```
project-blueprint/
├── package.json
├── README.md
├── skills/project-blueprint/
│   ├── SKILL.md                  # Full 10-phase setup + domain management
│   ├── templates/                # AGENTS-root, AGENTS-domain, agent, chain, wiki
│   └── references/
│       └── architecture.md       # 9 architectural decisions with rationale
├── prompts/
│   ├── new-project.md           # /new-project <description>
│   ├── add-domain.md             # /add-domain <name> <keywords>
│   ├── rename-domain.md          # /rename-domain <old> <new>
│   └── remove-domain.md          # /remove-domain <name>
└── agents/
    └── project-builder.md        # Guided, interactive scaffolding agent
```

## License

MIT
```

### skills/README.md

```markdown
# Skills

Skills are the **knowledge layer** of Project Blueprint. They contain the full architectural instructions and step-by-step processes that tell an AI agent *how* to set up and manage a project.

## Why Skills?

Skills use **progressive disclosure** — only the skill's name and description appear in the agent's context (a few bytes). The full instructions load on demand when a user's task matches the description. This means:

- **Zero context cost** until the skill is needed
- **Automatic trigger** — a user saying "set up a new project" or "add a domain" loads the skill automatically
- **Portable** — follows the [Agent Skills standard](https://agentskills.io/specification), shareable via npm or git

The other two layers (prompts and agents) depend on this skill. Prompts are shortcuts that load the skill. The agent definition is a wrapper that runs the skill in an isolated context.

### Why not just use prompt templates?

Prompt templates expand prompt text, but they don't contain multi-step processes, templates, or reference documentation. A skill is a full instruction package — it can reference templates, include scripts, and carry architectural rationale that a simple prompt can't hold.

### Why not just use a custom agent?

A custom agent runs in a separate context window, which adds process overhead. A skill loads into the current session, so the orchestrator can execute the steps directly without spawning a subprocess. The custom agent is available for users who specifically want an isolated, guided experience, but the skill is the primary mechanism.

## What's Included

```
skills/
└── project-blueprint/
    ├── SKILL.md                  # The skill itself (19.5KB)
    ├── templates/                # Scaffolding templates customized per project
    │   ├── AGENTS-root.md         # Root AGENTS.md (conventions + routing table)
    │   ├── AGENTS-domain.md       # Domain AGENTS.md (self-contained + documentation protocol)
    │   ├── APPEND_SYSTEM.md       # Identity file for .pi/
    │   ├── agent-domain.md        # Agent definition (includes documentation protocol)
    │   ├── chain-basic.md         # Chain file for multi-step workflows
    │   ├── wiki-home.md           # Wiki home page template
    │   ├── wiki-page-stub.md      # Generic wiki page template
    │   ├── wiki-activity-log.md   # Per-domain activity log (agents write here automatically)
    │   ├── wiki-build-README.md   # HTML wiki build instructions (VitePress)
    │   ├── wiki-build-config.js   # VitePress configuration template
    │   ├── wiki-build-package.json # VitePress package.json template
    │   └── documentation-standard.md # Documentation conventions and formatting standard
    └── references/
        └── architecture.md       # 9 architectural decisions with rationale
```

## How the Skill Works

1. **Auto-discovery** — pi scans skill directories and finds `SKILL.md` files
2. **Description match** — the skill's `description` field in the frontmatter tells pi when to load it
3. **On-demand loading** — when a user's prompt matches, pi reads the full `SKILL.md` into context
4. **Agent follows instructions** — the step-by-step process guides the agent through setup or management
5. **Templates are read as needed** — the agent reads template files during execution and customizes them

### Skill Sections

| Section | What It Covers |
|---------|---------------|
| Architecture Summary | 3 core principles, token budget targets |
| Setup Process (Phases 1–10) | Full interview → create → verify pipeline |
| Domain Management | Add, rename, remove domains while keeping 5 touchpoints in sync |
| Critical Rules | Hard constraints that must not be violated |
| Templates Index | Where each template lives and when to use it |

## Example Prompts

You don't need to remember commands or syntax. Just describe what you want in plain language and the skill loads automatically. Here are examples grouped by what you're trying to do:

### Setting Up a New Project

These prompts trigger the skill's 10-phase setup process. The agent will ask you follow-up questions before creating anything.

```
Set up a new project for my healthcare analytics work
```
```
I need a project structure for a law firm with case management and billing
```
```
Help me organize a project for monitoring manufacturing equipment with IoT sensors
```
```
Scaffold a project for student enrollment and course management
```
```
I want to set up sub-agent orchestration for my e-commerce platform with inventory and orders
```

### Adding a Domain to an Existing Project

These prompts trigger the "Add a Domain" section. The agent creates the folder, `AGENTS.md`, agent definition, routing table entry, and wiki updates — all kept in sync.

```
Add a compliance domain to my project
```
```
I need a new domain for handling user authentication and access control
```
```
Add a domain for report generation with keywords: reports, PDFs, dashboards, exports
```

### Renaming a Domain

These prompts trigger the "Rename a Domain" section. The agent updates the folder, agent definition, routing table, chains, and wiki — no stale references left behind.

```
Rename the bookkeeping domain to accounting
```
```
I want to change the name of my inventory domain to stock-management
```

### Removing a Domain

These prompts trigger the "Remove a Domain" section. The agent asks for confirmation before deleting anything and updates all five touchpoints.

```
Remove the network domain from my project
```
```
I don't need the shipping domain anymore, delete it
```

### Using Slash Commands

If you prefer typing a short command, these work the same way:

| Command | Example |
|---------|--------|
| `/new-project` | `/new-project healthcare analytics with billing and compliance` |
| `/add-domain` | `/add-domain compliance regulations audit` |
| `/rename-domain` | `/rename-domain bookkeeping accounting` |
| `/remove-domain` | `/remove-domain network` |

### Using the Project Builder Agent

For a guided, interactive setup in a separate context window:

```
{ agent: "project-builder", task: "Set up a project for my healthcare analytics work" }
```

This dispatches a dedicated agent that interviews you step by step and builds everything.

## Trigger Phrases

The skill auto-loads when a user says anything like:
- "Set up a new project"
- "Create project structure"
- "Scaffold a project"
- "Organize a workspace for agents"
- "Add a domain"
- "Rename a domain"
- "Remove a domain"

Or manually: `/skill:project-blueprint`

## Templates

Templates are starting points, not final outputs. The agent reads each template and customizes it for the user's specific project — substituting names, keywords, conventions, rules, and quality checks. Never use a template verbatim.

| Template | What It Produces |
|----------|-----------------|
| `AGENTS-root.md` | Root `AGENTS.md` with conventions and routing table |
| `AGENTS-domain.md` | Self-contained domain `AGENTS.md` with rules, quality checks, common mistakes, and documentation protocol |
| `APPEND_SYSTEM.md` | Identity file for `.pi/APPEND_SYSTEM.md` (who you're helping) |
| `agent-domain.md` | Agent definition with `cwd`, `inheritProjectContext: false`, intercom protocol, and documentation protocol |
| `chain-basic.md` | Chain file connecting agents in a pipeline |
| `wiki-home.md` | Wiki home page with navigation, structure map, token budget |
| `wiki-page-stub.md` | Generic wiki page for extending documentation |
| `wiki-activity-log.md` | Per-domain activity log — each domain gets its own `Activity Log.md` in its wiki subdirectory |
| `wiki-build-README.md` | Instructions for building HTML wiki from markdown source |
| `wiki-build-config.js` | VitePress config with sidebar, nav, and search |
| `wiki-build-package.json` | VitePress package.json for npm install + build |

## Architecture Reference

`references/architecture.md` documents the 9 key design decisions and their trade-offs:

1. Why structural routing (not feature-based)
2. Why self-contained domains (no supplementary files)
3. Why `inheritProjectContext: false`
4. Why `cwd` on domain agents
5. Why minimal orchestrator context
6. Why the default wiki name is `wiki`
7. Why intercom check-back
8. Why domains are central in the wiki
9. Why integrate-wiki and extract-domain operations

This reference is for anyone who wants to understand the "why" behind the architecture, or who wants to modify the skill's behavior with full awareness of the trade-offs.
```

### skills/project-blueprint/SKILL.md

This is the largest and most important file. It contains the full 10-phase setup process, domain management operations, critical rules, and template references.

```markdown
---
name: project-blueprint
description: >
  Set up a new project with sub-agent orchestration, structural routing, domain directories, 
  agent definitions, chain files, and a self-documenting wiki. Also manages existing projects: 
  add, rename, or remove domain folders while keeping routing tables, agent definitions, 
  chains, and wiki in sync. Use when the user wants to create or scaffold a new project, 
  set up domain-specific agents, organize a workspace for multi-agent workflows, initialize 
  sub-agent orchestration for any domain, add a new domain to an existing project, rename a 
  domain, or remove a domain.
  Also matches: "new project setup", "create project structure", "scaffold project", 
  "organize workspace for agents", "set up domains", "project template",
  "add domain", "rename domain", "remove domain", "delete domain".
license: MIT
compatibility: pi-coding-agent with pi-subagents, pi-intercom, pi-keyword-router, find-skill, librarian, and decompose-execute-verify packages
metadata:
  version: "1.0.0"
  author: "Trading Laboratory"
---

# Orchestrated Project — Skill Instructions

You are setting up a new project with sub-agent orchestration. This skill encodes the architecture and step-by-step process for creating a well-structured, domain-routed project that supports hybrid AI deployment (local + cloud LLMs).

## Architecture Summary

This project follows three core principles:

1. **Structural routing** — The routing table lives in the root `AGENTS.md`. Any harness that discovers `AGENTS.md` files can follow it. No harness-specific configuration for routing.
2. **Self-contained domains** — Each domain folder has exactly one `AGENTS.md` containing all conventions, rules, quality checks, and instructions. No supplementary files (no `CONTEXT.md`, `REFERENCES.md`, or `QualityControl.md` — everything is in `AGENTS.md`).
3. **`inheritProjectContext: false`** — Sub-agents discover context independently via `cwd` walk. The orchestrator does not inject its context into sub-agents. This eliminates redundancy and ensures sub-agents always get the latest version of context files.

### Token Budget Target

| Role | Tokens | Content |
|------|--------|---------|
| Orchestrator (permanent) | ~1.2KB | Identity + routing table only |
| Sub-agent (ephemeral) | ~4-5KB | Full domain context, loaded once, released on completion |

No redundancy between orchestrator and sub-agent context.

## Step-by-Step Setup Process

### Phase 1: Interview

Before creating anything, ask the user these questions. Use their answers to customize the setup:

1. **Project name** — What is the project called? (Used for the wiki title and root identity)
2. **Project description** — One or two sentences describing what this project does
3. **Domains** — What are the main domains/workflows? For each domain:
   - Domain name (lowercase, single word preferred, e.g., `bookkeeping`, `compliance`)
   - Domain description (1-2 sentences)
   - Domain keywords (for routing table, e.g., "trade logging, reconciliation, P&L")
   - Who should use this domain? (e.g., "trade analysts", "compliance officers")
4. **Wiki location** — Where should the documentation wiki live? Default: `./wiki/`
5. **HTML wiki** — Should the wiki also build a browser-friendly HTML version with sidebar, search, and modern navigation? Default: yes. Uses VitePress — reads the same markdown files, no duplication.
6. **Models** — What models for orchestrator and sub-agents? If unsure, use defaults:
   - Orchestrator: current default model
   - Reasoning-heavy sub-agents: `ollama/deepseek-v4-pro:cloud`
   - Fast sub-agents: `ollama/qwen3.5:4b`
7. **Check-back behavior** — Should sub-agents check back with the orchestrator via intercom? Default: yes, using the `delegate` pattern (check back on decisions and blockers)
8. **Any existing context** — Are there existing `AGENTS.md` files, conventions, or documentation to incorporate?

### Phase 2: Create Directory Structure

Create the following structure, substituting the user's domain names:

```
<project-root>/
├── AGENTS.md                          # Root: identity + conventions + routing table
├── .pi/
│   ├── APPEND_SYSTEM.md               # Identity only (who am I helping)
│   └── agents/                        # Project-level agent definitions & chains
│       ├── <domain1>.md               # One agent per domain
│       ├── <domain2>.md
│       ├── <domain1>-<domain2>.chain.md  # Multi-step chains
│       └── ...
├── <domain1>/
│   └── AGENTS.md                       # Self-contained domain context
├── <domain2>/
│   └── AGENTS.md                       # Self-contained domain context
└── wiki/                               # Documentation wiki (default name)
    └── <project-name>/                 # Wiki content directory
        ├── Home.md                      # Domain index + navigation
        ├── <domain1>/                  # Domain wiki (agent writes here) — front and center
        │   └── Activity Log.md
        ├── <domain2>/                  # Domain wiki (agent writes here)
        │   └── Activity Log.md
        └── _meta/                      # Reference docs (reachable, non-central)
            ├── Architecture.md
            ├── Agent Definitions.md
            └── ...
```

### Phase 3: Create the Root AGENTS.md

Use the template at `./templates/AGENTS-root.md`.

Customize it with:
- Project name and description
- Conventions (timestamps, currencies, date formats, output style)
- Routing table with the user's domains and keywords

**The routing table must include an entry for the wiki domain** so that research/documentation tasks route correctly. Example:

```markdown
## Domain Routing

When the task involves one of these domains, read the corresponding file before proceeding.
That file contains all context, conventions, rules, and quality checks for the domain.

| Keywords | Read this file |
|----------|---------------|
| <keywords for domain1> | `./<domain1>/AGENTS.md` |
| <keywords for domain2> | `./<domain2>/AGENTS.md` |
| wiki, documentation, research, analysis | `./wiki/AGENTS.md` |

After reading the domain file, follow its instructions for the task.
```

### Phase 4: Create the Identity File

Use the template at `./templates/APPEND_SYSTEM.md`.

This goes in `.pi/APPEND_SYSTEM.md` and should contain ONLY:
- Who you are helping
- Their role/context
- Any universal rules (NO domain-specific content — that goes in domain `AGENTS.md` files)

### Phase 5: Create Domain AGENTS.md Files

For each domain, use the template at `./templates/AGENTS-domain.md`.

Each domain `AGENTS.md` must be **self-contained** — it should contain:
1. **Title and purpose** — What this domain covers
2. **Conventions** — Domain-specific conventions (formats, units, terminology)
3. **Rules** — What must always be done, what must never be done
4. **Quality checklist** — What "good looks like" for this domain
5. **Common mistakes** — What to avoid
6. **Documentation protocol** — When and how to document work in the wiki (see template for details)
7. **Routing references** — If this domain links to others, mention the routing table in root `AGENTS.md`

**Do NOT create supplementary files** (no `CONTEXT.md`, `REFERENCES.md`, `QualityControl.md`). Everything goes in `AGENTS.md`.

### Phase 6: Create Agent Definitions

For each domain, create an agent definition in `.pi/agents/<domain>.md`.

Use the template at `./templates/agent-domain.md`.

Key frontmatter settings:
- `name`: domain name
- `cwd: ./<domain>` — Points to the domain directory for cwd walk
- `inheritProjectContext: false` — Sub-agents discover context independently
- `systemPromptMode: replace` — Agent gets a clean system prompt
- `model`: user's chosen model for this domain's tasks
- `tools`: appropriate tool set for the domain
- `intercom`: include if check-back behavior is desired

### Phase 7: Create Chain Files (Optional)

If the user identified multi-step workflows, create chain files in `.pi/agents/`.

Use the template at `./templates/chain-basic.md`.

Each chain file describes a pipeline where the output of one step feeds into the next. Chain steps use `{task}` and `{previous}` variables.

### Phase 8: Create the Wiki

Create a documentation wiki in the user's chosen location (default: `./wiki/<project-name>/`).

Use the templates at `./templates/wiki-home.md`, `./templates/wiki-page-stub.md`, and `./templates/wiki-activity-log.md`.

The wiki is organized with **domains at the center** and reference documentation in a dedicated subdirectory.

**1. Home page** (`Home.md`):
- Domain index — links to each domain's wiki section
- Navigation to `_meta/` reference pages
- Workspace map, token budget summary

**2. Domain wikis** (one directory per domain at wiki root — front and center):
- `./wiki/<project-name>/<domain1>/Activity Log.md` — Running log of what this domain's agent has done
- `./wiki/<project-name>/<domain1>/` — Additional pages created by the domain agent over time
- `./wiki/<project-name>/<domain2>/Activity Log.md`
- `./wiki/<project-name>/<domain2>/` — Additional pages
- ... (one subdirectory per domain)

Domains are the wiki's primary content. Each domain owns its section and is responsible for maintaining it. When you open the wiki, you see domains first — not documentation about the project structure. The home page links to each domain's activity log. The VitePress sidebar shows domain sections prominently at the top.

**3. Reference pages** (`_meta/` subdirectory — reachable, non-central):
1. **Architecture** — Why structural routing, self-contained domains, inheritProjectContext:false
2. **Agent Definitions** — All agents with frontmatter, descriptions, and usage
3. **Chain Files** — Multi-step workflows
4. **System & Context Files** — File layout, token budgets, routing table design
5. **Sample Prompts** — Ready-to-use prompts for each domain that non-technical users can copy
6. **Model Substitutions** — Cloud/local model mapping (optional, if user wants hybrid deployment)

The `_meta/` directory holds project-level reference documentation about the workspace's architecture and conventions. These pages are important but are *about* the system — they don't represent active working domains. Keeping them in `_meta/` ensures the wiki root is dominated by domains (the living, working content) rather than by documentation *about* the project blueprint. The `_` prefix signals "internal/reference" and groups them together in file listings without competing with domain directories for attention.

Ask the user:
- **Also build an HTML wiki?** — Default: yes. Produces a browser-friendly version with sidebar, search, and modern navigation alongside the markdown (Obsidian) version.

### Phase 8b: Create HTML Wiki Build (Optional)

If the user wants an HTML wiki, create a `wiki-build/` directory alongside the markdown wiki.

Use the templates:
- `./templates/wiki-build-README.md` → `wiki/<project-name>/wiki-build/README.md`
- `./templates/wiki-build-config.js` → `wiki/<project-name>/wiki-build/.vitepress/config.js`
- `./templates/wiki-build-package.json` → `wiki/<project-name>/wiki-build/package.json`
- `./templates/documentation-standard.md` → `wiki/<project-name>/_meta/Documentation Standard.md`

Customize the config with the user's project name, description, and wiki source directory path.

The HTML wiki reads the same markdown files — no duplication. Run `npm run build` to generate static HTML in `wiki-build/dist/`.

Add `wiki-build/dist/` and `wiki-build/node_modules/` to `.gitignore`.

### Phase 9: Verify Token Budget

After creating all files, calculate the token budget:

1. **Orchestrator load** (permanent): Root `AGENTS.md` + `.pi/APPEND_SYSTEM.md` — should be under 2KB
2. **Sub-agent load** (per invocation): Agent prompt + domain `AGENTS.md` + root `AGENTS.md` via cwd walk — should be under 6KB per domain
3. **No redundancy**: Orchestrator context should NOT be injected into sub-agents

Report the totals to the user.

### Phase 10: Final Verification

1. Verify the routing table in root `AGENTS.md` covers all domains
2. Verify each domain `AGENTS.md` is self-contained (no references to supplementary files)
3. Verify all agent definitions have `inheritProjectContext: false` and correct `cwd`
4. Verify the wiki navigation links all pages
5. Run `ls -la` on the project structure to confirm file layout
6. Report the final structure and token budget to the user

## Critical Rules

1. **Never put domain-specific content in root `AGENTS.md`.** Root is for identity + routing only.
2. **Never create supplementary files.** Each domain gets exactly one `AGENTS.md` with everything.
3. **Always set `inheritProjectContext: false`** on domain agents. Context is discovered via cwd walk.
4. **Always set `cwd` on domain agents** to point to their domain directory.
5. **The routing table is harness-agnostic.** It works in pi, Cursor, Claude Code, or any system that reads `AGENTS.md`.
6. **Default wiki directory name is `wiki`**, not `research`. Allow user override.
7. **Include sample prompts in the wiki** — non-technical users need copy-paste examples.
8. **Report token budget** before and after setup so the user understands the efficiency gains.

## Templates

All templates are in `./templates/`. Read each template file and customize it for the user's project. Never copy a template verbatim — always adapt it to the specific domain and project.

- `AGENTS-root.md` — Root AGENTS.md with routing table
- `AGENTS-domain.md` — Domain AGENTS.md structure (includes Documentation Protocol)
- `APPEND_SYSTEM.md` — Identity file for .pi/
- `agent-domain.md` — Agent definition with frontmatter (includes Documentation Protocol)
- `chain-basic.md` — Chain file structure
- `wiki-home.md` — Wiki home page
- `wiki-page-stub.md` — Generic wiki page template
- `wiki-activity-log.md` — Domain activity log template
- `wiki-build-README.md` — HTML wiki build instructions (VitePress)
- `wiki-build-config.js` — VitePress configuration template
- `wiki-build-package.json` — VitePress package.json template
- `documentation-standard.md` — How to document: conventions, Activity Log format, quality checklist (for `_meta/`)

## References

For deeper architectural rationale, see `./references/architecture.md`.

---

# Domain Management — Post-Setup Operations

After a project has been set up, domains may need to be added, renamed, or removed. Each of these operations touches multiple files that must stay in sync. Follow the steps below precisely to maintain consistency with the structural routing architecture.

## Management Principle: The Sync Checklist

Every domain management operation must update **all five** of these touchpoints. Missing any one breaks the routing:

| Touchpoint | File | What It Contains |
|-----------|------|------------------|
| 1. Domain directory | `./<domain>/` | Folder + `AGENTS.md` with all domain context |
| 2. Agent definition | `.pi/agents/<domain>.md` | `name`, `cwd: ./<domain>`, system prompt |
| 3. Routing table | Root `AGENTS.md` | Keywords → `./<domain>/AGENTS.md` entry |
| 4. Chain files | `.pi/agents/*.chain.md` | Any chains that reference this domain's agent |
| 5. Wiki | `wiki/<project>/` | Structure map, agent docs, sample prompts, domain activity log |

After every management operation, verify the token budget and confirm no broken references.

---

## Add a Domain

Adds a new domain to an existing project. Does not modify existing domains.

### Add: Interview

Ask the user:
1. **Domain name** — lowercase, single word preferred (e.g., `compliance`)
2. **Domain description** — 1-2 sentences
3. **Domain keywords** — for routing table (e.g., "regulations, compliance, audit")
4. **Who uses this domain?** — e.g., "compliance officers"
5. **Model** — which model for this domain's agent? (default: same as existing sub-agents)
6. **Check-back?** — Should this domain's agent check back via intercom? (default: same as existing agents)
7. **Chain workflows?** — Does this domain participate in any multi-step workflows with other domains?

### Add: Steps

1. **Create `./<domain>/AGENTS.md`** — Use the `AGENTS-domain.md` template from `./templates/`. Customize with domain name, description, conventions, rules, quality checklist, common mistakes.
2. **Create `.pi/agents/<domain>.md`** — Use the `agent-domain.md` template. Set `name: <domain>`, `cwd: ./<domain>`, `inheritProjectContext: false`. Choose model and tools.
3. **Update root `AGENTS.md` routing table** — Add a row: `| <keywords> | \`./<domain>/AGENTS.md\` |`
4. **Create chain files if needed** — If the domain joins multi-step workflows, create or update chain files in `.pi/agents/`. Use the `chain-basic.md` template.
5. **Update the wiki** — Add the new domain to: home page Domain Index table, `_meta/Agent Definitions` page, `_meta/Sample Prompts` page. Create `wiki/<project>/<domain>/Activity Log.md` using the `wiki-activity-log.md` template.
6. **Verify** — Confirm all five touchpoints are consistent. Run `ls -la` on the domain folder and `.pi/agents/`. Check the routing table renders correctly.

### Add: Critical Rules

- The new domain's `AGENTS.md` must be fully self-contained (no supplementary files).
- The agent definition must have `inheritProjectContext: false` and `cwd: ./<domain>`.
- Never duplicate an existing domain's content into the new domain's `AGENTS.md`.
- If the domain shares conventions with another domain, state that in the routing references section of the new `AGENTS.md`, not by copying content.

---

## Rename a Domain

Renames an existing domain across all five touchpoints. The old name ceases to exist.

### Rename: Interview

Ask the user:
1. **Old domain name** — Which domain to rename?
2. **New domain name** — What should it be called now?
3. **New keywords** — Do the routing table keywords need updating? (e.g., if renaming `bookkeeping` to `accounting`, keywords might change from "trade logging, reconciliation" to "financial records, ledgers, accounting")
4. **New description** — Does the domain description need updating, or just the name?

### Rename: Steps

1. **Rename the directory** — `mv ./<old> ./<new>`
2. **Update `./<new>/AGENTS.md`** — Change the title and any internal references from the old name to the new name.
3. **Rename the agent definition** — `mv .pi/agents/<old>.md .pi/agents/<new>.md`. Update the frontmatter: `name: <new>`, `cwd: ./<new>`. Update the system prompt body to reflect the new name.
4. **Update the root `AGENTS.md` routing table** — Change the keywords and/or path: `| <new-keywords> | \`./<new>/AGENTS.md\` |`. Remove the old row.
5. **Update chain files** — Search all `.pi/agents/*.chain.md` files for references to the old domain name (agent names, `cwd` paths). Replace with the new name.
6. **Update the wiki** — Rename `wiki/<project>/<old>/` to `wiki/<project>/<new>/`. Update: home page Domain Index table, `_meta/Agent Definitions` page, `_meta/Sample Prompts` page, any cross-references.
7. **Verify** — Run `ls -la` on `./<new>/` and `.pi/agents/`. Confirm routing table points to `./<new>/AGENTS.md`. Grep for the old name across the project root to confirm no stale references remain.

### Rename: Critical Rules

- Never rename just the folder without updating all five touchpoints. A folder rename alone breaks the agent `cwd`, routing table, chains, and wiki.
- After renaming, the old name must not appear anywhere in the project (except in session/history files).
- Chain files are the most likely place for stale references — always check them.
- If the domain had sample prompts in the wiki, update those too (users copy-paste them).

---

## Remove a Domain

Removes a domain entirely from the project. The folder, agent definition, routing entry, chains, and wiki references are all deleted or updated.

### Remove: Confirmation

Before removing, confirm with the user:
1. **Which domain?** — Name of the domain to remove.
2. **Should chain files be removed?** — If any chains only involve this domain's agent, they should be removed. If the domain participates in chains with other domains, those chains need updating (not removal).
3. **Should wiki content be removed?** — Remove the domain's wiki subdirectory, or leave historical documentation?
4. **Has the domain's data been preserved?** — If the domain folder contains data files (not just `AGENTS.md`), confirm the user wants to delete them.

### Remove: Steps

1. **Remove the directory** — `rm -rf ./<domain>/` (after confirming data preservation if needed).
2. **Remove the agent definition** — `rm .pi/agents/<domain>.md`.
3. **Remove chain files** — Delete any chains that only involve this domain. For chains where this domain is one step among others, remove the step that references this domain's agent.
4. **Update the root `AGENTS.md` routing table** — Remove the row for this domain from the routing table.
5. **Update the wiki** — Remove the domain's wiki directory: `wiki/<project>/<domain>/`. Remove the domain from: home page Domain Index table, `_meta/Agent Definitions` page, `_meta/Sample Prompts` page.
6. **Verify** — Run `ls -la` on the project root and `.pi/agents/`. Confirm the routing table has no entry for the removed domain. Grep for the domain name to check for stale references.

### Remove: Critical Rules

- Always confirm before deleting. Removing a domain is destructive and cannot be undone without version control.
- Chain file updates are critical — a chain that references a removed agent will fail at runtime.
- The routing table must not contain entries pointing to deleted folders. A stale routing entry causes the orchestrator to attempt reading a nonexistent file.
- After removal, recalculate the token budget (the orchestrator's permanent load shrinks if the routing table gets shorter).

---

## Management Verification Checklist

After any add/rename/remove operation, run through this checklist:

- [ ] Every domain folder has exactly one `AGENTS.md` (no supplementary files)
- [ ] Every domain has an agent definition in `.pi/agents/` with `inheritProjectContext: false` and correct `cwd`
- [ ] The routing table in root `AGENTS.md` has exactly one row per domain (no extras, no missing)
- [ ] All chain files reference agents that exist
- [ ] Wiki home page reflects domain-centric layout (domains at root, `_meta/` for reference)
- [ ] Wiki Domain Index table lists all current domains with accurate links
- [ ] Each domain has its own wiki directory at wiki root with Activity Log.md
- [ ] `_meta/` reference pages are accurate and up to date
- [ ] Sample prompts reference current domain names
- [ ] Grep for any stale old names (after rename/remove) — none should remain
- [ ] Token budget recalculated and reported

## Wiki Cross-Reference

After setup, update the project wiki to include:
- `_meta/` reference pages about the project architecture, agents, chains, and system design
- Sample prompts in `_meta/Sample Prompts` that would trigger domain agents for common tasks
- Home page Domain Index with links to each domain's wiki section
- Cross-references between domain wiki content and `_meta/` reference pages where relevant

---

The remaining domain management operations — **Integrate Wiki** and **Extract Domain** — follow the same interview-then-execute pattern as add/rename/remove. Their full specifications are in `SKILL.md` under those sections. The key principles:

**Integrate Wiki** (`/integrate-wiki`):
- Scans for scattered wiki content (numbered pages at root, wikis inside domain folders)
- Moves numbered reference pages to `_meta/` (stripping `NN — ` prefix)
- Consolidates in-domain wiki content to `wiki/<project>/<domain>/`
- Rebuilds Home.md for domain-centric layout
- Never deletes without user confirmation

**Extract Domain** (`/extract-domain`):
- Copies domain folder, agent definition, wiki content, relevant chains, and _meta pages
- Generates minimal workspace scaffold for independent use
- Never modifies the source project (read + copy only)
- Verifies extraction is self-contained with no references back

```

### skills/project-blueprint/templates/AGENTS-root.md

```markdown
# {project_name}

{project_description}

## Conventions

- All timestamps in {timezone} (default: US Eastern / America/New_York)
- All date formats: YYYY-MM-DD
- Keep outputs concise and actionable
- When in doubt, ask — do not assume

## Domain Routing

When the task involves one of these domains, read the corresponding file before proceeding.
That file contains all context, conventions, rules, and quality checks for the domain.

| Keywords | Read this file |
|----------|---------------|
| {domain1_keywords} | `./{domain1}/AGENTS.md` |
| {domain2_keywords} | `./{domain2}/AGENTS.md` |
| wiki, documentation, research, analysis | `./wiki/AGENTS.md` |

After reading the domain file, follow its instructions for the task.
```

### skills/project-blueprint/templates/AGENTS-domain.md

```markdown
# {domain_name}

{domain_description}

## Conventions

- {convention_1}
- {convention_2}
- All outputs should be {output_style}

## Rules

### Must Always
- {rule_always_1}
- {rule_always_2}

### Must Never
- {rule_never_1}
- {rule_never_2}

## Quality Checklist

Before considering any task complete, verify:

- [ ] {quality_check_1}
- [ ] {quality_check_2}
- [ ] {quality_check_3}

## Common Mistakes

| Mistake | Correct Approach |
|---------|-----------------|
| {mistake_1} | {correct_1} |
| {mistake_2} | {correct_2} |

## Documentation Protocol

After completing any task, document what you did in the project wiki.

### When to Document
- After making decisions that affect the domain's architecture or rules
- After completing a non-trivial task (anything beyond a simple lookup or status check)
- After discovering and resolving issues, edge cases, or common mistakes
- After creating, modifying, or removing any files or configurations

### What to Document
- **What was done** — Brief summary of the task and outcome
- **Why** — Rationale for decisions made (especially non-obvious ones)
- **What changed** — Files created/modified, configurations updated, rules added
- **Lessons learned** — Anything that would help the next person (or agent) avoid mistakes

### Where to Document
- Write to your domain's activity log: `{wiki_path}/{project_name}/{domain_name}/Activity Log.md`
- If the entry relates to a significant topic that deserves its own page, create a new page in `{wiki_path}/{project_name}/{domain_name}/` with a descriptive name
- Cross-reference from related pages if the change affects multiple domains
- Project-level reference pages (architecture, agents, sample prompts) live in `{wiki_path}/{project_name}/_meta/` — do not add domain-specific content there

### Format
Use a consistent format for wiki entries:

```markdown
### YYYY-MM-DD — {Title}

**Task**: {What was requested}
**Outcome**: {What was done and result}
**Rationale**: {Why this approach was chosen}
**Files changed**: {List of files created/modified}
**Lessons**: {What to remember for next time}
```

### Do Not Document
- Trivial lookups or status checks with no changes
- Orchestrator intercom messages (those are ephemeral)
- Intermediate debugging steps that led nowhere

## Cross-Domain References

For tasks that span domains, consult the routing table in `./AGENTS.md` (project root).
```

### skills/project-blueprint/templates/APPEND_SYSTEM.md

```markdown
You are helping {user_name} with {project_description}.

## Rules
- Write in plain, clear language
- Ask clarifying questions before making assumptions
- When you are unsure, say no
```

### skills/project-blueprint/templates/agent-domain.md

```markdown
---
name: {domain_name}
description: {domain_description_short}
tools: read, write, edit, bash, intercom
model: {model}
thinking: medium
systemPromptMode: replace
inheritProjectContext: false
inheritSkills: false
cwd: ./{domain_name}
---

You are a {domain_name} specialist. Your job is to {domain_role_description}.

## Your Domain

Read `./{domain_name}/AGENTS.md` for the full conventions, rules, and quality checks that govern your work. Follow them strictly.

## How You Work

1. Read the domain `AGENTS.md` for context and rules
2. Perform the requested task following all conventions and quality checks
3. Document what you did in the project wiki (see Documentation Protocol below)
4. Report results concisely and actionably
5. Check back with the orchestrator via intercom if you encounter:
   - Ambiguity in the task
   - Decisions that require human judgment
   - Blockers that prevent progress
   - Results that are unexpected or outside normal parameters

## Documentation Protocol

After completing any task, document what you did in the project wiki.

### When to Document
- After making decisions that affect the domain's architecture or rules
- After completing a non-trivial task (anything beyond a simple lookup or status check)
- After discovering and resolving issues, edge cases, or common mistakes
- After creating, modifying, or removing any files or configurations

### What to Document
- **What was done** — Brief summary of the task and outcome
- **Why** — Rationale for decisions made (especially non-obvious ones)
- **What changed** — Files created/modified, configurations updated, rules added
- **Lessons learned** — Anything that would help the next person (or agent) avoid mistakes

### Where to Document
- Write to your domain's activity log: `{wiki_path}/{project_name}/{domain_name}/Activity Log.md`
- If the entry relates to a significant topic that deserves its own page, create a new page in `{wiki_path}/{project_name}/{domain_name}/` with a descriptive name
- Cross-reference from related pages if the change affects multiple domains
- Project-level reference pages (architecture, agents, sample prompts) live in `{wiki_path}/{project_name}/_meta/` — do not add domain-specific content there

### Format
```markdown
### YYYY-MM-DD — {Title}

**Task**: {What was requested}
**Outcome**: {What was done and result}
**Rationale**: {Why this approach was chosen}
**Files changed**: {List of files created/modified}
**Lessons**: {What to remember for next time}
```

### Do Not Document
- Trivial lookups or status checks with no changes
- Orchestrator intercom messages (those are ephemeral)
- Intermediate debugging steps that led nowhere

## Intercom Protocol

When you need to check back:
- State what you found and what you need guidance on
- Provide your recommendation if you have one
- Wait for the orchestrator's response before proceeding
```

### skills/project-blueprint/templates/chain-basic.md

```markdown
---
name: {chain_name}
description: {chain_description}
steps:
  - agent: {agent1_name}
    task: |
      {agent1_task_template}
    cwd: ./{domain1}
  - agent: {agent2_name}
    task: |
      {agent2_task_template}
    cwd: ./{domain2}
---
```

### skills/project-blueprint/templates/wiki-home.md

```markdown
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
```

### skills/project-blueprint/templates/wiki-page-stub.md

```markdown
# {page_number} — {page_title}

{page_description}

## {section_1}

{section_1_content}

## {section_2}

{section_2_content}

## {section_3}

{section_3_content}
```

### skills/project-blueprint/templates/wiki-activity-log.md

```markdown
# {domain_name} — Activity Log

This log tracks what the {domain_name} agent has done. New entries are prepended so the most recent activity appears first.

---

### YYYY-MM-DD — {Title}

**Task**: {What was requested}
**Outcome**: {What was done and result}
**Rationale**: {Why this approach was chosen}
**Files changed**: {List of files created/modified}
**Lessons**: {What to remember for next time}

---

*This log is maintained by the {domain_name} agent. See the routing table in root `AGENTS.md` for cross-domain references.*
```

### skills/project-blueprint/templates/wiki-build-README.md

```markdown
# Wiki HTML Build

The markdown wiki is the source of truth. This directory builds a browser-friendly HTML version with React-based navigation.

## Why Two Outputs?

| Format | Best For | Tool |
|---------|----------|------|
| Markdown (.md) | Editing, Obsidian, git diffs | Any text editor |
| HTML | Browsing, sharing, non-technical users | Web browser |

The markdown files are never duplicated — the HTML is generated from them.

## Build

```bash
cd wiki-build
npm install
npm run build
```

Output goes to `wiki-build/dist/`. Open `dist/index.html` in any browser.

## Dev Server

```bash
npm run dev
```

Opens a local dev server with hot reload at `http://localhost:5173`.

## Architecture

Uses [VitePress](https://vitepress.dev) — a markdown-first static site generator built on Vite + Vue:

- Reads the same `.md` files the Obsidian wiki uses
- Generates React-style SPA navigation with sidebar, search, and breadcrumbs
- Produces static HTML (no server required — just open in a browser)
- Supports custom themes if you want to brand it

### Why VitePress?

| Option | Pros | Why Not |
|--------|------|---------|
| VitePress | Markdown-first, fast builds, nice defaults | Vue-based (not React) but produces identical UX |
| Docusaurus | React-based, mature | Heavier, more config, React JSX for customization |
| MkDocs | Simple, Python | Less polished UI, no SPA navigation |
| Custom React | Full control | You'd write the markdown parser, routing, and nav from scratch |
| mdBook | Rust-based, fast | Targets book format, not project wikis |

VitePress wins for a project wiki: it reads your existing markdown with zero modification, produces beautiful navigation, and builds in seconds. The Vue runtime is an implementation detail — the output looks and feels like a modern React SPA.

### Customization

Edit `wiki-build/.vitepress/config.{js,ts}` to customize:
- Sidebar navigation
- Site title and theme
- Search configuration
- Custom CSS (brand colors, fonts)

## Directory Structure

```
wiki/
└── {project-name}/
    ├── Home.md                      # Domain index — wiki landing page
    ├── {domain1}/                   # Domain wiki — front and center
    │   └── Activity Log.md
    ├── {domain2}/                   # Domain wiki
    │   └── Activity Log.md
    ├── _meta/                       # Reference docs (reachable, non-central)
    │   ├── Architecture.md
    │   ├── Agent Definitions.md
    │   └── ...
    └── wiki-build/                  # HTML build (this directory)
        ├── .vitepress/
        │   └── config.js
        ├── package.json
        └── dist/                    # Generated HTML output (gitignored)
```

The markdown source files live in the parent directory. VitePress reads from `.` (current directory) which contains all the `.md` files — no duplication.
```

### skills/project-blueprint/templates/wiki-build-config.js

```javascript
import { defineConfig } from 'vitepress'

export default defineConfig({
  title: '{project_name}',
  description: '{project_description}',

  // Source directory: parent directory (where markdown files live)
  srcDir: '.',
  srcExclude: ['**/wiki-build/**', '**/dist/**', '**/node_modules/**'],

  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Reference', link: '/_meta/Architecture' },
    ],

    sidebar: [
      // Domains first — they are the wiki's primary content
      {
        text: '{domain1_name}',
        items: [
          { text: 'Activity Log', link: '/{domain1_name}/Activity Log' },
        ],
      },
      {
        text: '{domain2_name}',
        items: [
          { text: 'Activity Log', link: '/{domain2_name}/Activity Log' },
        ],
      },
      // Reference docs — reachable but non-central
      {
        text: 'Reference',
        collapsed: true,
        items: [
          { text: 'Architecture', link: '/_meta/Architecture' },
          { text: 'Agent Definitions', link: '/_meta/Agent Definitions' },
          { text: 'System & Context Files', link: '/_meta/System & Context Files' },
        ],
      },
      {
        text: 'Agents & Workflows',
        collapsed: true,
        items: [
          { text: 'Chain Files', link: '/_meta/Chain Files' },
          { text: 'Model Substitutions', link: '/_meta/Model Substitutions' },
        ],
      },
      {
        text: 'Using This Project',
        collapsed: true,
        items: [
          { text: 'Sample Prompts', link: '/_meta/Sample Prompts' },
        ],
      },
    ],

    search: {
      provider: 'local',
    },

    footer: {
      message: 'Built with Project Blueprint',
    },
  },
})
```

### skills/project-blueprint/templates/wiki-build-package.json

```json
{
  "name": "{project_name}-wiki",
  "private": true,
  "scripts": {
    "dev": "vitepress dev",
    "build": "vitepress build",
    "preview": "vitepress preview"
  },
  "devDependencies": {
    "vitepress": "^1.6.0"
  }
}
```

### skills/project-blueprint/references/architecture.md

```markdown
# Structural Routing Architecture Reference

This is the stable reference for the architectural decisions encoded in the `project-blueprint` skill. It documents why each decision was made so that future setups don't need to re-derive them.

## 1. Why Structural Routing (Not Feature-Based Routing)

**Decision:** The routing table lives in `AGENTS.md`, not in harness-specific files like `.pi/APPEND_SYSTEM.md`.

**Rationale:**
- `AGENTS.md` is discovered by any harness that walks directories (pi, Cursor, Claude Code, etc.)
- `.pi/APPEND_SYSTEM.md` is only read by pi
- A routing table in `.pi/APPEND_SYSTEM.md` only works in pi; in `AGENTS.md` it works everywhere
- The routing table is structural (part of the project's organization), not operational (part of the harness configuration)

**Trade-off:** pi-specific features like `cwd` and `inheritProjectContext` provide stronger guarantees, but they're pi-only. The routing table provides weaker guarantees (the LLM might not follow it) but works everywhere.

**Resolution:** Use both. Structural routing in `AGENTS.md` for universality. `cwd` and `inheritProjectContext: false` for pi-specific optimization.

## 2. Why Self-Contained Domains (No Supplementary Files)

**Decision:** Each domain folder has exactly one `AGENTS.md` with everything. No `CONTEXT.md`, `REFERENCES.md`, or `QualityControl.md`.

**Rationale:**
- Pi auto-discovers `AGENTS.md` and `CLAUDE.md` via directory walk. It does NOT auto-discover custom file names.
- Multiple files per domain created confusion about which file had the right version of a rule.
- Supplementary files required explicit `reads:` directives in agent definitions, adding configuration burden.
- One file per domain is simpler to maintain, simpler to check, and simpler for new contributors to understand.

**Trade-off:** A single large `AGENTS.md` is less modular than multiple focused files. But modularity is lost anyway if the harness only auto-loads one of them.

**Resolution:** One `AGENTS.md` per domain. If a domain grows too large, split it into sub-domains with their own folders and `AGENTS.md` files, and add routing table entries.

## 3. Why `inheritProjectContext: false`

**Decision:** All domain agents set `inheritProjectContext: false`.

**Rationale:**
- With `inheritProjectContext: true` (default), the orchestrator's entire project context is injected into the sub-agent. This means the sub-agent gets a redundant copy of root `AGENTS.md` plus any other auto-discovered files.
- With `false`, the sub-agent discovers context independently via its own `cwd` walk. It still loads root `AGENTS.md` (because the walk goes up to root), but it gets the current version, not a stale copy.
- The key benefit: if `root/AGENTS.md` changes between the orchestrator's turn and the sub-agent's invocation, the sub-agent gets the latest version.
- Token savings: no redundant injection of orchestrator context.

**Trade-off:** The sub-agent doesn't see the orchestrator's conversation history. This is acceptable because:
- Sub-agents are task-focused, not conversation-aware
- If conversation history is needed, use `context: "fork"` or pass relevant context in the task description
- Intercom provides a channel for the sub-agent to ask questions if needed

## 4. Why `cwd` on Domain Agents

**Decision:** Each domain agent has `cwd: ./<domain>` in frontmatter.

**Rationale:**
- Without `cwd`, the sub-agent starts in the project root and walks up, discovering only root `AGENTS.md`. It would not auto-discover the domain's `AGENTS.md`.
- With `cwd: ./<domain>`, pi walks up from the domain directory and discovers:
  1. `./<domain>/AGENTS.md` (domain context, closest to cwd)
  2. `./AGENTS.md` (root context, walked up)
- This is a pi-specific optimization. The structural routing table in root `AGENTS.md` provides a fallback for non-pi harnesses.

**Trade-off:** `cwd` is a pi-specific setting. In other harnesses, the user or agent must follow the routing table manually.

**Resolution:** Use `cwd` for pi optimization, but always include the routing table in root `AGENTS.md` so the fallback works.

## 5. Why Minimal Orchestrator Context

**Decision:** The orchestrator carries only identity + routing table (~1.2KB).

**Rationale:**
- The orchestrator's context is permanent — loaded every turn, never released.
- Domain context (4-5KB per domain) is only needed when a task is routed to that domain.
- If domain context lives permanently in the orchestrator's context, every model call pays for it, even when the task has nothing to do with that domain.
- With multiple domains, the permanent load grows linearly. Three domains = 12-15KB permanently loaded.
- With structural routing, the orchestrator loads 1.2KB permanently. Domain context is loaded by sub-agents only when needed.

**Trade-off:** The orchestrator can't answer domain questions from memory. It must either:
- Read the domain `AGENTS.md` explicitly (adds to that turn's context)
- Delegate to a sub-agent (separate context, released after completion)

**Resolution:** For quick answers, the orchestrator can read the domain file. For substantial work, delegate to a sub-agent. The routing table tells the orchestrator where to look.

## 6. Why Default Wiki Name is `wiki`

**Decision:** The wiki directory defaults to `wiki/`, not `research/`.

**Rationale:**
- `wiki` is a universally understood term for documentation
- `research` implies a specific domain (academic/scientific research) that may not apply to all projects
- A non-technical user understands "wiki" immediately
- The wiki itself is a domain with its own `AGENTS.md` that gets a routing table entry

**Resolution:** Default to `wiki/`, allow user override via the interview phase.

## 7. Why Intercom Check-Back

**Decision:** Sub-agents are configured to check back with the orchestrator via intercom on decisions and blockers.

**Rationale:**
- Fully autonomous sub-agents can go down wrong paths without the orchestrator knowing
- Intercom provides a lightweight channel for sub-agents to ask "should I proceed with X?"
- The `delegate` agent pattern (check back on decisions and blockers) balances autonomy with oversight
- More autonomous patterns are available (e.g., `worker` which only checks back on blockers)

**Trade-off:** Check-back adds latency (waiting for orchestrator response). But it prevents costly mistakes.

**Resolution:** Default to `delegate` pattern. Allow user to choose stricter (more check-back) or looser (less) patterns per agent.

## 8. Why Domains Are Central in the Wiki

**Decision:** Domain wiki directories live at the root of the wiki. Project-level reference documentation lives in `_meta/`.

**Rationale:**
- Domains are the active, living content of the project — they are the reason the wiki exists
- Project-level reference pages (architecture, agent definitions, sample prompts) are "about" the system, not the work itself
- When each domain contained its own wiki (inside the domain folder), documentation and knowledge sharing became fragmented — you had to check multiple locations to understand cross-domain concerns
- By placing domains at the wiki root with a shared `_meta/` for reference, domains maintain their own space while sharing a common navigation layer
- The `_meta/` prefix signals "internal/reference" — grouped together, non-competing with domain directories

**Trade-off:** Reference pages are one extra click away (inside `_meta/` instead of wiki root). But this is the correct trade-off: domains are what users and agents interact with daily; reference pages are consulted occasionally.

**Resolution:** Domains at wiki root, reference docs in `_meta/`. The home page provides a domain index at the top and a reference navigation section below it.

## 9. Why Integrate Wiki and Extract Domain Operations

**Decision:** The skill provides `integrate-wiki` and `extract-domain` as first-class domain management operations alongside add, rename, and remove.

**Rationale:**
- Projects evolve. A workspace created with an older project-blueprint may have wiki content in legacy layouts (numbered pages at root, wikis inside domain folders). `integrate-wiki` restructures existing content into the domain-centric layout without losing anything.
- Domains mature and may outgrow their current project. `extract-domain` packages a domain (folder, agent, wiki, chains) as a self-contained unit that can seed a new workspace.
- Without `extract-domain`, the only way to share a domain between projects is manual copy — error-prone and likely to miss touchpoints.
- Without `integrate-wiki`, migrating from old wiki layouts requires manual file-by-file reorganization.

**Trade-off:** These operations add complexity to the skill. But they address real migration and reuse needs that arise in any project that grows over time.

**Resolution:** Both operations follow the same interview-then-execute pattern as add/rename/remove. `integrate-wiki` is non-destructive (copies, confirms before moves). `extract-domain` is read-only on the source project.
```

### prompts/README.md

```markdown
# Prompts

Prompt templates are the **command layer** of Project Blueprint. They give you short, typed commands that expand into full prompts — so you don't have to remember the skill's full instructions or type long prompts.

## Why Prompt Templates?

When you type `/new-project healthcare analytics`, three things happen:

1. The template expands the short command into a full prompt
2. The full prompt instructs the agent to read the skill
3. The skill loads and the agent follows its step-by-step process

Without prompt templates, you'd have to type something like: *"Read the skill at ~/.pi/agent/skills/project-blueprint/SKILL.md and set up a new project for healthcare analytics. Ask me the interview questions first, then follow all 10 phases."*

The template does that for you. One line instead of a paragraph.

### Why not just use the skill directly?

You can — the skill auto-loads when your prompt matches its description. Prompt templates are for when you want a **short, explicit command** with arguments, like `/add-domain compliance regulations audit`. They're also useful for autocomplete: type `/` in the pi editor and see a list of available commands with descriptions.

### How they differ from the skill and agent

| Layer | What It Is | How You Use It |
|-------|-----------|---------------|
| **Skill** | The knowledge | Loads automatically, or via `/skill:project-blueprint` |
| **Prompt template** | The shortcut | Type `/new-project`, `/add-domain`, etc. |
| **Custom agent** | The builder | `{ agent: "project-builder", task: "..." }` |

All three end up reading the same skill. They're just different ways to trigger it.

## What's Included

| Command | File | What It Does |
|---------|------|-------------|
| `/new-project` | `new-project.md` | Scaffold a brand new project from scratch |
| `/add-domain` | `add-domain.md` | Add a domain to an existing project |
| `/rename-domain` | `rename-domain.md` | Rename a domain across all project files |
| `/remove-domain` | `remove-domain.md` | Remove a domain entirely (with confirmation) |

## Usage

### `/new-project <description>`

Creates a full project structure: root `AGENTS.md`, domain folders, agent definitions, chains, and wiki.

```
/new-project healthcare analytics with patient records, billing, and compliance
```

The agent will ask you the interview questions from the skill (project name, domains, model preferences, wiki location, check-back behavior) before creating anything.

### `/add-domain <name> <keywords>`

Adds a new domain to an existing project. Creates the folder, `AGENTS.md`, agent definition, routing table entry, and wiki updates.

```
/add-domain compliance regulations audit
```

All five touchpoints are kept in sync (domain folder, agent definition, routing table, chains, wiki).

### `/rename-domain <old> <new>`

Renames a domain across every file that references it — folder, agent definition (name + `cwd`), routing table, chain files, and wiki.

```
/rename-domain bookkeeping accounting
```

After renaming, the agent verifies no stale references to the old name remain.

### `/remove-domain <name>`

Removes a domain entirely — folder, agent definition, routing table entry, affected chains, and wiki references. Asks for confirmation before deleting.

```
/remove-domain network
```

Confirms whether chains should be removed or updated, and whether wiki content should be kept or deleted.

## Creating Your Own Prompt Templates

If you have a workflow you run frequently, create a prompt template for it:

```markdown
---
description: What this command does
argument-hint: "<argument-name>"
---
Your expanded prompt here. Use $1, $2 for positional arguments
and $@ for all arguments joined.
```

Save it as `~/.pi/agent/prompts/my-template.md` and it appears when you type `/my-template` in the pi editor.
```

### prompts/new-project.md

```markdown
---
description: Set up a new orchestrated project with sub-agents, domain routing, and wiki
argument-hint: "<project-description>"
---
Set up an orchestrated project structure for: $@

Read the skill at ../skills/project-blueprint/SKILL.md for full instructions.

Before creating anything, ask me the interview questions the skill defines (project name, domains, wiki location, models, check-back behavior). Then follow the skill's step-by-step process to create the full project structure.
```

### prompts/add-domain.md

```markdown
---
description: Add a new domain to an existing orchestrated project (creates folder, AGENTS.md, agent definition, routing entry, wiki updates)
argument-hint: "<domain-name> <keywords>"
---
Add a new domain called "$1" to this project with keywords: ${@:2}

Read the skill at ~/.pi/agent/skills/project-blueprint/SKILL.md for full instructions, specifically the "Add a Domain" section.

Before creating anything, ask me the interview questions the skill defines for adding a domain (description, who uses it, model, check-back, chains). Then follow the skill's add steps, making sure to update all five touchpoints: domain directory + AGENTS.md, agent definition, routing table, chain files, and wiki.
```

### prompts/rename-domain.md

```markdown
---
description: Rename an existing domain across all project files (folder, agent, routing table, chains, wiki)
argument-hint: "<old-name> <new-name>"
---
Rename the domain "$1" to "$2" across this project.

Read the skill at ~/.pi/agent/skills/project-blueprint/SKILL.md for full instructions, specifically the "Rename a Domain" section.

Before making changes, ask me the interview questions the skill defines for renaming (new keywords, new description). Then follow the skill's rename steps, making sure to update all five touchpoints: domain directory + AGENTS.md, agent definition (name + cwd), routing table, chain files, and wiki. After renaming, grep for the old name to confirm no stale references remain.
```

### prompts/remove-domain.md

```markdown
---
description: Remove a domain entirely from the project (folder, agent, routing entry, chains, wiki — with confirmation)
argument-hint: "<domain-name>"
---
Remove the domain "$1" entirely from this project.

Read the skill at ~/.pi/agent/skills/project-blueprint/SKILL.md for full instructions, specifically the "Remove a Domain" section.

Before deleting anything, ask me the confirmation questions the skill defines: should chains be removed or updated, should wiki content be removed, and has the domain's data been preserved. Then follow the skill's remove steps, making sure to update all five touchpoints: domain directory, agent definition, routing table, chain files, and wiki. After removal, verify no stale references remain.
```

### prompts/integrate-wiki.md

```markdown
---
description: Consolidate scattered or legacy wiki content into the domain-centric wiki structure
argument-hint: "[--scan-only]"
---
Integrate the project wiki into the domain-centric layout.

Read the skill at ~/.pi/agent/skills/project-blueprint/SKILL.md for full instructions, specifically the "Integrate Wiki" section.

**Before modifying anything**, scan the project for scattered wiki content and report findings.

**If `--scan-only` flag is provided**, only scan and report — do not make any changes.

**Otherwise**, after scanning, ask me the interview questions the skill defines, then follow the integrate steps: move numbered reference pages to `_meta/`, consolidate in-domain wiki content to central wiki, rebuild Home.md, update VitePress config, verify all links.
```

### prompts/extract-domain.md

```markdown
---
description: Extract a domain from the current project as a self-contained package for a new workspace
argument-hint: "<domain-name> [destination]"
---
Extract the domain "$1" from this project as a self-contained package.

Read the skill at ~/.pi/agent/skills/project-blueprint/SKILL.md for full instructions, specifically the "Extract Domain" section.

Before extracting, ask me the interview questions the skill defines, then follow the extract steps: copy domain folder, agent definition, wiki content, relevant _meta and chain files, generate workspace scaffold, verify extraction is self-contained. **Never modify the original project.**
```

### agents/README.md

```markdown
# Agents

Agent definitions are the **guided experience layer** of Project Blueprint. They describe a specialist AI agent that can be dispatched to set up a project in its own isolated context window.

## Why a Custom Agent?

The skill and prompt templates work within the current session — the orchestrator reads the skill and follows the steps using its own context. A custom agent is different: it runs in a **separate process** with its own context window, model, and tool set.

This matters when you want:

- **Isolation** — the setup process doesn't consume the orchestrator's context window
- **Different model** — the builder can use a more capable model for the interview and scaffolding
- **Interactive interview** — the agent asks questions and waits for answers, without cluttering the main conversation
- **Clean handoff** — the agent creates everything, reports a summary, and exits

### How it differs from the skill and prompts

| Layer | Context | Best For |
|-------|---------|----------|
| **Skill** | Loads into your current session | Quick setup, no process overhead |
| **Prompt template** | Expands a command in your editor | Fast invocation with parameters |
| **Custom agent** | Separate context window | Guided, interactive setup when you want isolation |

All three read the same `SKILL.md`. The agent is just another way to invoke it.

### Why not always use the agent?

An agent spawns a new `pi` process, which adds startup time. For a quick `add-domain` operation, loading the skill directly in the current session is faster. The agent is best when you want a full guided setup experience — asking questions, getting recommendations, and reviewing the plan before anything is created.

## What's Included

| Agent | File | What It Does |
|-------|------|-------------|
| `project-builder` | `project-builder.md` | Interviews you, reads the skill, creates the full project structure |

## Usage

### From any pi session

```typescript
{ agent: "project-builder", task: "Set up a project for my healthcare analytics work" }
```

### From a prompt template

```
/new-project healthcare analytics with billing and compliance
```

The prompt template loads the skill in the current session, which is equivalent but without spawning a separate process.

### What the project-builder does

1. **Reads the skill** at `../skills/project-blueprint/SKILL.md`
2. **Interviews you** about your project (name, domains, models, wiki location, check-back)
3. **Reads the templates** and customizes them for your project
4. **Creates everything** following the skill's 10-phase process
5. **Verifies** the token budget and file structure
6. **Reports** a summary of what was created

### Configuration

The agent definition's frontmatter controls its behavior:

| Setting | Value | Why |
|---------|-------|-----|
| `model` | `ollama/deepseek-v4-pro:cloud` | Capable model for the interview and scaffolding |
| `thinking` | `high` | Thoughtful analysis of domain structure and routing |
| `systemPromptMode` | `replace` | Clean system prompt focused on project setup |
| `inheritProjectContext` | `true` | Sees the current project context for awareness |
| `inheritSkills` | `true` | Can load the project-blueprint skill |
| `tools` | `read, write, edit, bash, intercom` | File operations + orchestrator communication |

## Creating Your Own Agent Definitions

If you want a specialized variant of the project-builder (e.g., one that only adds domains, or one that uses a local model), create a new `.md` file in your agents directory:

```markdown
---
name: my-agent
description: What this agent does
tools: read, write, bash
model: ollama/qwen3:8b
systemPromptMode: replace
inheritProjectContext: false
cwd: ./my-domain
---
Your system prompt goes here.
```

Save it as `~/.pi/agent/agents/my-agent.md` (user-level) or `.pi/agents/my-agent.md` (project-level) and invoke it with `{ agent: "my-agent", task: "..." }`.
```

### agents/project-builder.md

```markdown
---
name: project-builder
description: Interactive project scaffolding that interviews the user and creates a full orchestrated project structure
tools: read, write, edit, bash, intercom
model: ollama/deepseek-v4-pro:cloud
thinking: high
systemPromptMode: replace
inheritProjectContext: true
inheritSkills: true
---
You are a project scaffolding specialist. Your job is to help users set up a new project with sub-agent orchestration, structural routing, and a self-documenting wiki.

## What You Do

1. Read the skill at `../skills/project-blueprint/SKILL.md` for the full architecture and step-by-step process.
2. Interview the user about their project: name, description, domains, wiki location, models, and check-back preferences.
3. Follow the skill's 10-phase process to create the complete project structure.
4. Read all templates from `../skills/project-blueprint/templates/` and customize them for the user's project.
5. Verify the token budget and file structure after setup.
6. Report a summary of what was created.

## Key Defaults

- Wiki directory: `wiki/` (user can override)
- Orchestrator model: current default
- Sub-agent model: `ollama/deepseek-v4-pro:cloud` for reasoning, `ollama/qwen3.5:4b` for fast tasks
- Check-back: delegate pattern (check back on decisions and blockers)

## Interview Questions

Always ask these before creating anything:
1. Project name?
2. Project description (1-2 sentences)?
3. Domains — name, description, keywords for each?
4. Wiki location? (default: `./wiki/`)
5. Models for orchestrator and sub-agents?
6. Check-back behavior? (default: yes)
7. Any existing context to incorporate?

## Rules

- Never create supplementary files. Each domain gets exactly one `AGENTS.md`.
- Always set `inheritProjectContext: false` and `cwd` on domain agents.
- The routing table lives in root `AGENTS.md`, not in harness-specific files.
- Report token budget before and after setup.
- Include sample prompts in the wiki for non-technical users.
```

---

## Key Decisions Record

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | Three-layer system: Skill → Prompt → Agent | Distinct names for distinct functions. Skill = knowledge, Prompt = command, Agent = builder. |
| 2 | Structural routing in AGENTS.md | Harness-agnostic. Works in pi, Cursor, Claude Code. |
| 3 | Self-contained domains (one AGENTS.md) | No supplementary files. Auto-discovered by cwd walk. |
| 4 | `inheritProjectContext: false` | No redundancy. Sub-agents get latest file versions. |
| 5 | `cwd` on domain agents | Ensures domain AGENTS.md is auto-discovered. |
| 6 | Wiki default name: `wiki/` | Universally understood. `research/` implies specific domain. |
| 7 | Five-touchpoint sync for domain management | Folder, agent, routing table, chains, wiki. Missing any breaks routing. |
| 8 | Documentation protocol in domain AGENTS.md | Agents automatically log their work to domain-specific wiki subdirectory. |
| 9 | Partitioned wiki by domain | Each domain gets its own wiki subdirectory with Activity Log.md. Scannable browsing. |
| 10 | VitePress for HTML wiki | Markdown-first, reads existing files, SPA navigation, fast builds. Better than Docusaurus/mkDocs/custom React for this use case. |
| 11 | `pi-package` keyword in package.json | Enables `pi install` from local path or GitHub. |
| 12 | Relative paths in skill/templates | Package is self-contained regardless of install location. |
| 13 | Cross-domain agents get `cwd: .` | Agents that span domains (market-scout, risk-analyst, etc.) point to project root so they discover the routing table. |

## Commit to GitHub

After creating all files, initialize a git repo and push to `github.com/carlosfrias/project-blueprint`:

```bash
cd project-blueprint
git init
git add -A
git commit -m "Initial release: Project Blueprint"
git remote add origin git@github.com:carlosfrias/project-blueprint.git
git push -u origin main
```

Then update the GitHub repo description:
```bash
gh repo edit carlosfrias/project-blueprint --description "Scaffold new projects with smart AI agents, organized folders, and built-in documentation"
```