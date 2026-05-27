---
description: Documentation for the Project Blueprint skills layer and architecture.
---

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
    │   └── wiki-build-package.json # VitePress package.json template
    └── references/
        └── architecture.md       # 7 architectural decisions with rationale
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
- "Integrate wiki"
- "Consolidate wiki content"
- "Extract a domain"
- "Extract domain for new workspace"

Or manually: `/skill:project-blueprint`

## Templates

Templates are starting points, not final outputs. The agent reads each template and customizes it for the user's specific project — substituting names, keywords, conventions, rules, and quality checks. Never use a template verbatim.

| Template | What It Produces |
|----------|-----------------|
| `AGENTS-root.md` | Root `AGENTS.md` with conventions and routing table |
| `AGENTS-domain.md` | Self-contained domain `AGENTS.md` with rules, quality checks, common mistakes, and documentation protocol |
| `AGENTS-post-completion.md` | Post-completion refined AGENTS file — golden path, battle-tested rules, resolved ambiguities, delta report. Generated by `post-completion-architect` agent. |
| `APPEND_SYSTEM.md` | Identity file for `.pi/APPEND_SYSTEM.md` (who you're helping) |
| `agent-domain.md` | Agent definition with `cwd`, `inheritProjectContext: false`, intercom protocol, and documentation protocol |
| `chain-basic.md` | Chain file connecting agents in a pipeline |
| `wiki-home.md` | Wiki home page with domain index, navigation, structure map, token budget |
| `wiki-page-stub.md` | Generic wiki page for extending documentation |
| `wiki-activity-log.md` | Per-domain activity log — each domain gets its own `Activity Log.md` in its wiki directory at wiki root |
| `wiki-build-README.md` | HTML wiki build instructions (VitePress) |
| `documentation-standard.md` | Documentation conventions, Activity Log format, quality checklist (always included in _meta/) |
| `wiki-build-config.js` | VitePress config with sidebar, nav, and search |
| `wiki-build-package.json` | VitePress package.json for npm install + build |

## Architecture Reference

`references/architecture.md` documents the 7 key design decisions and their trade-offs:

1. Why structural routing (not feature-based)
2. Why self-contained domains (no supplementary files)
3. Why `inheritProjectContext: false`
4. Why `cwd` on domain agents
5. Why minimal orchestrator context
6. Why the default wiki name is `wiki`
7. Why intercom check-back

This reference is for anyone who wants to understand the "why" behind the architecture, or who wants to modify the skill's behavior with full awareness of the trade-offs.