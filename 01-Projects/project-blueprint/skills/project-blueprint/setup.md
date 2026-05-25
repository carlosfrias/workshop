# Orchestrated Project — Skill Instructions

You are setting up a new project with sub-agent orchestration. This skill encodes the architecture and step-by-step process for creating a well-structured, domain-routed project that supports hybrid AI deployment (local + cloud LLMs).


## [S-TIGHT]

Full project creation walkthrough: interview user, create directory structure, write AGENTS.md files, define agents, scaffold wiki, verify token budget. Load ONLY when creating a new project.
## Architecture Summary

This project follows three core principles:

1. **Structural routing** — The routing table lives in the root `AGENTS.md`. Any harness that discovers `AGENTS.md` files can follow it. No harness-specific configuration for routing.
2. **Self-contained domains** — Each domain folder has exactly one `AGENTS.md` containing all conventions, rules, quality checks, and instructions. No supplementary files (no `CONTEXT.md`, `REFERENCES.md`, or `QualityControl.md` — everything is in `AGENTS.md`).
3. **`inheritProjectContext: false`** — Sub-agents discover context independently via `cwd` walk. The orchestrator does not inject its context into sub-agents. This eliminates redundancy and ensures sub-agents always get the latest version of context files.

### Token Budget Target

| Role                     | Tokens | Content                                                  |
|--------------------------|--------|----------------------------------------------------------|
| Orchestrator (permanent) | ~1.2KB | Identity + routing table only                            |
| Sub-agent (ephemeral)    | ~4-5KB | Full domain context, loaded once, released on completion |

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

Create the following structure, substituting the user's domain names. This covers the **workshop side** (code, agents, domains, wiki). The **vault side** (WORKBENCH.md, AGENTS.md, FOCUS.md, threads) is created in Phase 3.

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

### Phase 3: Create Vault-Side Documentation

Create the human-facing documentation in the vault (`personal-vault/01-Projects/{project-name}/`). This side contains the Workbench, AI handoff, and prompt threads.

**1. WORKBENCH.md** — Use the template at `./templates/WORKBENCH.md`.

This is the **human's workspace** (Workbench Pattern). Deliberately exempt from [S-TIGHT], LOD markers, and AI formatting rules. Customize:
- Project name in title and frontmatter
- Current date
- One checkbox: "Project scaffolded" as first completed item

**Rules:**
- Put here: current thinking, half-formed ideas, brain dumps, working checklists, questions, sketches
- Don't put here: finished decisions (→ decision-log), concrete tasks (→ FOCUS.md), prompt captures (→ thread)
- When content matures, migrate to the appropriate structural file
- Strike through completed items with `~~done~~`

**2. Vault AGENTS.md** — Contains documentation-domain routing, conventions, discovery order (WORKBENCH → AGENTS → FOCUS → README → thread), and workshop cross-reference.

**3. FOCUS.md** — Frontmatter (`name`, `summary`, `status`, `phase`, `progress`), current focus, active work, session handoff, blocked/needs-decision, next-agent discovery path.

**4. README.md** — Project overview, description, deliverables, quick links.

**5. Overview.md** — Progress dashboard with phase status table and session history.

**6. Thread** — `threads/{project-name}/0-THREAD.md` + first prompt.

### Phase 4: Create the Root AGENTS.md (Workshop)

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

### Phase 5: Create the Identity File

Use the template at `./templates/APPEND_SYSTEM.md`.

This goes in `.pi/APPEND_SYSTEM.md` and should contain ONLY:
- Who you are helping
- Their role/context
- Any universal rules (NO domain-specific content — that goes in domain `AGENTS.md` files)

### Phase 6: Create Domain AGENTS.md Files

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

### Phase 7: Create Agent Definitions

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

## Critical Rules

1. **Never put domain-specific content in root `AGENTS.md`.** Root is for identity + routing only.
2. **Never create supplementary files.** Each domain gets exactly one `AGENTS.md` with everything.
3. **Always set `inheritProjectContext: false`** on domain agents. Context is discovered via cwd walk.
4. **Always set `cwd` on domain agents** to point to their domain directory.
5. **The routing table is harness-agnostic.** It works in pi, Cursor, Claude Code, or any system that reads `AGENTS.md`.
6. **Default wiki directory name is `wiki`**, not `research`. Allow user override.
7. **Include sample prompts in the wiki** — non-technical users need copy-paste examples.
8. **Report token budget** before and after setup so the user understands the efficiency gains.

### Phase 8: Create the Wiki

Create a documentation wiki in the user's chosen location (default: `./wiki/<project-name>/`).

Use the templates at `./templates/wiki-home.md`, `./templates/wiki-page-stub.md`, `./templates/wiki-activity-log.md`, and `./templates/documentation-standard.md`.

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
2. **Documentation Standard** — This file: conventions, formatting, Activity Log format, quality checklist
3. **Agent Definitions** — All agents with frontmatter, descriptions, and usage
4. **Chain Files** — Multi-step workflows
4. **System & Context Files** — File layout, token budgets, routing table design
5. **Sample Prompts** — Ready-to-use prompts for each domain that non-technical users can copy
6. **Model Substitutions** — Cloud/local model mapping (optional, if user wants hybrid deployment)
7. **Documentation Standard** — Conventions, formatting, Activity Log format, quality checklist (always included)

The `_meta/` directory holds project-level reference documentation about the workspace's architecture and conventions. These pages are important but are *about* the system — they don't represent active working domains. Keeping them in `_meta/` ensures the wiki root is dominated by domains (the living, working content) rather than by documentation *about* the project blueprint. The `_` prefix signals "internal/reference" and groups them together in file listings without competing with domain directories for attention.

**4. Architecture pages** (optional):
- Update `_meta/Model Substitutions.md` to reference the decomposition pattern (if applicable)

**5. Documentation Standard** — Copy `./templates/documentation-standard.md` to `wiki/<project-name>/_meta/Documentation Standard.md` and customize it with:
   - Project-specific date/timezone conventions
   - Project name in cross-references
   - Any domain-specific documentation conventions that apply project-wide
   This document serves as the human + agent style guide for all documentation in the project

Ask the user:
- **Also build an HTML wiki?** — Default: yes. Produces a browser-friendly version with sidebar, search, and modern navigation alongside the markdown (Obsidian) version.

### Phase 8b: Create HTML Wiki Build (Optional)

If the user wants an HTML wiki, create a `wiki-build/` directory **inside the wiki directory** as a subdirectory:

```
wiki/
└── {project-name}/
    ├── Home.md
    ├── {domain1}/
    │   └── Activity Log.md
    ├── _meta/
    │   └── ...
    └── wiki-build/              # HTML build directory
        ├── .vitepress/
        │   └── config.js
        ├── package.json
        └── dist/                # Generated HTML (gitignored)
```

Use the templates:
- `./templates/wiki-build-README.md` → `wiki/{project-name}/wiki-build/README.md`
- `./templates/wiki-build-config.js` → `wiki/{project-name}/wiki-build/.vitepress/config.js`
- `./templates/wiki-build-package.json` → `wiki/{project-name}/wiki-build/package.json`

Customize the config with the user's project name and description. The VitePress config uses `srcDir: '.'` to read markdown files from the parent directory.

The HTML wiki reads the same markdown files — no duplication. Run `npm run build` to generate static HTML in `wiki/{project-name}/wiki-build/dist/`.

Add `wiki/{project-name}/wiki-build/dist/` and `wiki/{project-name}/wiki-build/node_modules/` to `.gitignore`.

### Phase 9: Verify Token Budget

After creating all files, calculate the token budget:

1. **Orchestrator load** (permanent): Root `AGENTS.md` + `.pi/APPEND_SYSTEM.md` — should be under 2KB
2. **Sub-agent load** (per invocation): Agent prompt + domain `AGENTS.md` + root `AGENTS.md` via cwd walk — should be under 6KB per domain
3. **No redundancy**: Orchestrator context should NOT be injected into sub-agents

Report the totals to the user.

### Phase 10: Final Verification

1. Verify the routing table in root `AGENTS.md` covers all domains
2. Verify the vault AGENTS.md discovery order starts with WORKBENCH.md
3. Verify each domain `AGENTS.md` is self-contained (no references to supplementary files)
3. Verify all agent definitions have `inheritProjectContext: false` and correct `cwd`
4. Verify the wiki navigation links all pages
5. Run `ls -la` on the project structure to confirm file layout
6. Report the final structure and token budget to the user

### Phase 11: Distribution Deployment

> **Rule:** Workshop paths and symlinks are scaffolding only. If the project is not a clean git distribution installable via `pi install`, it is a failure.

After verification passes, deploy the project as a clean pi package:

1. **Create GitHub repo** — Use `gh repo create carlosfrias/{project-name} --private`
2. **Initialize git and push** — The project root must contain `package.json` with `"pi"` key:
   ```bash
   cd {project-root}
   git init
   git add -A
   git commit -m "Initial distribution: {project-name}"
   git remote add origin git@github.com:carlosfrias/{project-name}.git
   git push -u origin main
   ```
3. **Add to pi settings** — Replace any local path with the git entry:
   ```bash
   # In ~/.pi/agent/settings.json, add:
   "git:git@github.com:carlosfrias/{project-name}.git"
   ```
4. **Run pi update** — Clones and installs the package:
   ```bash
   pi update --extensions
   ```
5. **Verify distribution** — Confirm no local paths remain for this package in settings.json and no stale symlinks in `~/.pi/agent/extensions/`

### Development Cycle (After Distribution)

Once distributed, the development cycle is:

```
workshop/ edit → git commit → git push → pi update --extensions
```

**Never leave a session with uncommitted workshop changes.** Workshop edits that aren't committed and pushed are invisible to pi — the git clone at `~/.pi/agent/git/...` is what pi loads.

## Critical Rules

1. **Never put domain-specific content in root `AGENTS.md`.** Root is for identity + routing only.
2. **Never create supplementary files.** Each domain gets exactly one `AGENTS.md` with everything.
3. **Always set `inheritProjectContext: false`** on domain agents. Context is discovered via cwd walk.
4. **Always set `cwd` on domain agents** to point to their domain directory.
5. **The routing table is harness-agnostic.** It works in pi, Cursor, Claude Code, or any system that reads `AGENTS.md`.
6. **Default wiki directory name is `wiki`**, not `research`. Allow user override.
7. **Include sample prompts in the wiki** — non-technical users need copy-paste examples.
8. **Report token budget** before and after setup so the user understands the efficiency gains.
9. **Never leave local paths or symlinks as the permanent state.** Workshop paths (`../../Cloud/...`) and extension symlinks are scaffolding only. Every pi package must complete the commit→push→`pi update` cycle. If the project isn't installed via `git:` in settings.json, it's broken. See Phase 11: Distribution Deployment.

## Templates

All templates are in `./templates/`. Read each template file and customize it for the user's project. Never copy a template verbatim — always adapt it to the specific domain and project.

- `WORKBENCH.md` — Human workspace, exempt from AI formatting (Workbench Pattern)
- `AGENTS-root.md` — Workshop root AGENTS.md with routing table
- `AGENTS-domain.md` — Domain AGENTS.md structure (includes Documentation Protocol)
- `APPEND_SYSTEM.md` — Identity file for .pi/
- `agent-domain.md` — Agent definition with frontmatter (includes Documentation Protocol)
- `chain-basic.md` — Chain file structure
- `wiki-home.md` — Wiki home page (domain-centric layout)
- `wiki-page-stub.md` — Generic wiki page template
- `wiki-activity-log.md` — Domain activity log template
- `documentation-standard.md` — How to document: conventions, Activity Log format, quality checklist (for `_meta/`)
- `wiki-build-README.md` — HTML wiki build instructions (VitePress)
- `wiki-build-config.js` — VitePress configuration template
- `wiki-build-package.json` — VitePress package.json template

## References

For deeper architectural rationale, see `./references/architecture.md`.

---

