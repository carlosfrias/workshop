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

### Standard Prompts (≥32K context models)

These prompts instruct the agent to read the skill manifest and follow cross-references. Suitable for models that can navigate 3-4 hops.

| Command | File | What It Does |
|---------|------|-------------|
| `/new-project` | `new-project.md` | Scaffold a brand new project from scratch |
| `/add-domain` | `add-domain.md` | Add a domain to an existing project |
| `/rename-domain` | `rename-domain.md` | Rename a domain across all project files |
| `/remove-domain` | `remove-domain.md` | Remove a domain entirely (with confirmation) |
| `/list-domain` | `list-domain.md` | List all configured domains with keywords and metadata |
| `/integrate-wiki` | `integrate-wiki.md` | Consolidate scattered/legacy wiki content into domain-centric layout |
| `/extract-domain` | `extract-domain.md` | Extract a domain as a self-contained package for a new workspace |

### Linear Prompts (<32K context models)

These prompts inline the linear script directly — no cross-references, no navigation. Validated on gemma4:e4b (4B) and qwen3:8b (8B). A 4B model with a linear script outperforms an 8B model with the decomposed approach.

| Command | File | What It Does |
|---------|------|-------------|
| `/new-project-linear` | `new-project-linear.md` | Scaffold a new project (flat instructions, no navigation) |
| `/add-domain-linear` | `add-domain-linear.md` | Add a domain (flat instructions) |
| `/remove-domain-linear` | `remove-domain-linear.md` | Remove a domain (flat instructions) |
| `/list-domain-linear` | `list-domain-linear.md` | List domains (flat instructions) |

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

### `/list-domain [--verbose]`

Lists all configured domains in the project with their keywords and metadata. Non-destructive (read-only).

```
/list-domain
```

**Basic output** (domain names + keywords):
```
Configured Domains (3):
  1. bookkeeping      — invoice, payment, reconciliation, P&L
  2. position-management — position, order, risk, allocation, sizing
  3. market-research  — research, analysis, signal, backtest, data
```

**Verbose output** (full metadata):
```
/list-domain --verbose
```

Shows directory paths, agent definition files, and domain context files for each domain.

### `/integrate-wiki [--scan-only]`

Consolidates scattered or legacy wiki content into the domain-centric layout. Scans for numbered pages at wiki root, wiki directories inside domain folders, and orphaned content — then restructures everything.

```
/integrate-wiki
```

**Scan-only mode** (reports findings without making changes):
```
/integrate-wiki --scan-only
```

The agent asks before making any changes: migration strategy for legacy pages (move to `_meta/`, archive, or delete), domain wiki content handling (move to central wiki or link), and whether to preserve originals as backup.

### `/extract-domain <name> [destination]`

Extracts a domain from the current project as a self-contained package that can seed a new workspace. Copies the domain folder, agent definition, wiki content, relevant chains, and generates a minimal workspace scaffold.

```
/extract-domain bookkeeping
/extract-domain compliance ./new-compliance-workspace
```

The agent asks interview questions before extracting: whether to include wiki content, `_meta/` pages, chains, and whether to generate a workspace scaffold. **Never modifies the original project** — extraction is read + copy only.

---

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