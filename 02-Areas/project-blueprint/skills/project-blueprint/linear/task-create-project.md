# Linear Script: create-project (Project Blueprint)

**Target Tier:** <8K (Low Capacity)
**Token Budget:** ~3.5KB
**Objective:** Initialize a full orchestrated project structure (Vault + Workshop) without navigation overhead.

## [LOD: Low] Context

**Required Paths:**
- Vault Root: `personal-vault/01-Projects/`
- Workshop Root: `workshop/01-Projects/`
- Skill Templates: `workshop/02-Areas/project-blueprint/templates/`

**Core Rules:**
- Use vault-native terms: `Plan` (not issue), `journal/` (not sessions/).
- Two Locations Mandate: Docs in Vault, Code in Workshop.
- S-TIGHT headers on operational files.

---

## [LOD: Low] Execution Steps

### Phase 1: Interview
Ask the user for:
1. Project Name
2. Project Description
3. Domains (Name, Description, Keywords)
4. Wiki Location (Default: `./wiki/`)
5. HTML Wiki? (Default: Yes)
6. Models (Orchestrator, Reasoning, Fast)
7. Intercom check-back? (Default: Yes)

### Phase 2: Workshop Infrastructure
Create the following directory structure:
`workshop/01-Projects/<project-name>/`
- `AGENTS.md` (Identity + Routing Table)
- `.pi/APPEND_SYSTEM.md` (Identity)
- `.pi/agents/<domain>.md` (Agent definitions: `inheritProjectContext: false`, `cwd: ./<domain>`)
- `<domain>/AGENTS.md` (Self-contained context)
- `wiki/<project-name>/` (The wiki structure)

### Phase 3: Vault Documentation
Create the following in `personal-vault/01-Projects/<project-name>/`:
- `WORKBENCH.md` (Human workspace)
- `AGENTS.md` (Documentation routing)
- `FOCUS.md` (Current state)
- `README.md` (Overview)
- `Overview.md` (Dashboard)
- `threads/<project-name>/0-THREAD.md` (Prompt capture)

### Phase 4: Wiki Content
Initialize the wiki at `personal-vault/01-Projects/<project-name>/wiki/`:
- `Home.md` (Domain index)
- `<domain>/Activity Log.md` (One per domain)
- `_meta/` (Architecture, Agent Definitions, Doc Standards)

### Phase 5: HTML Build (If requested)
Create `wiki/<project-name>/wiki-build/` with:
- `.vitepress/config.js`
- `package.json`
- `README.md`

---

## [LOD: Low] Inlined Templates

### Template: WORKBENCH.md
Frontmatter: `workbench: true`, `project: <name>`
Content: "Desk for this project. Notes, half-thoughts, current focus."

### Template: Root AGENTS.md
Header: "# AGENTS.md — <Project Name>"
Section: "## Domain Routing" -> Table with keywords mapping to `./<domain>/AGENTS.md`.

### Template: Domain AGENTS.md
Header: "# AGENTS.md — <Domain Name>"
Sections: "Conventions", "Rules", "Quality Checklist", "Documentation Protocol".

### Template: Agent Definition
Frontmatter: `name: <domain>`, `cwd: ./<domain>`, `inheritProjectContext: false`, `systemPromptMode: replace`.

---

## [LOD: Low] Verification Gate

Verify the following before completion:
1. [ ] No domain content in root `AGENTS.md`.
2. [ ] All agent definitions have `inheritProjectContext: false`.
3. [ ] All `cwd` paths correctly point to domain directories.
4. [ ] `S-TIGHT` headers present on `FOCUS.md` and `AGENTS.md`.
5. [ ] Two Locations Mandate: No docs in workshop, no code in vault.
6. [ ] All files created in the correct `personal-vault` vs `workshop` paths.
