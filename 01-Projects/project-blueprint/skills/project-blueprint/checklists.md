---
name: project-blueprint/checklists
description: Verification checklists and critical rules for project-blueprint operations.
---

# Checklists & Critical Rules

## [S-TIGHT]

Consolidated verification checklists from project-blueprint. Run these after setup, domain operations, wiki integration, or extraction. Keep them short — verify, don't narrate.

---

## Setup Verification (Phase 10)

After creating a new project:
- [ ] Routing table in root `AGENTS.md` covers all domains
- [ ] Each domain `AGENTS.md` is self-contained (no references to supplementary files)
- [ ] All agent definitions have `inheritProjectContext: false` and correct `cwd`
- [ ] Wiki navigation links all pages
- [ ] Token budget calculated: orchestrator <2KB, sub-agent <6KB
- [ ] `ls -la` confirms file layout matches template

---

## Domain Management Verification

After any add/rename/remove operation:
- [ ] Every domain folder has exactly one `AGENTS.md` (no supplementary files)
- [ ] Every domain has an agent definition with `inheritProjectContext: false` and correct `cwd`
- [ ] The routing table in root `AGENTS.md` has exactly one row per domain
- [ ] All chain files reference agents that exist
- [ ] Wiki home page reflects domain-centric layout
- [ ] Wiki Domain Index table lists all current domains
- [ ] Each domain has its own wiki directory with Activity Log.md
- [ ] `_meta/` reference pages are accurate and up to date
- [ ] Sample prompts reference current domain names
- [ ] Grep for stale old names after rename/remove — none should remain
- [ ] Token budget recalculated and reported

---

## Wiki Integration Verification

After consolidating wiki content:
- [ ] All numbered pages moved from wiki root to `_meta/`
- [ ] Each domain has a wiki directory at `wiki/<project>/<domain>/`
- [ ] `_meta/` contains all reference pages
- [ ] Home.md links are valid
- [ ] VitePress sidebar matches actual file layout (if html wiki exists)
- [ ] No stale references to old numbered page paths

---

## Domain Extraction Verification

After extracting a domain:
- [ ] Destination directory contains complete, self-contained structure
- [ ] All internal links point to valid files within the extraction
- [ ] Domain `AGENTS.md` is self-contained (no references to original project)
- [ ] Agent definition has correct `cwd` and `name`
- [ ] Routing table points to the domain
- [ ] Source project remains untouched

---

## Critical Rules (Applies to ALL Operations)

1. **Never put domain-specific content in root `AGENTS.md`.** Root is for identity + routing only.
2. **Never create supplementary files.** Each domain gets exactly one `AGENTS.md` with everything.
3. **Always set `inheritProjectContext: false`** on domain agents. Context is discovered via cwd walk.
4. **Always set `cwd` on domain agents** to point to their domain directory.
5. **The routing table is harness-agnostic.** Works in pi, Cursor, Claude Code, or any system that reads `AGENTS.md`.
6. **Default wiki directory name is `wiki`**, not `research`. Allow user override.
7. **Include sample prompts in the wiki** — non-technical users need copy-paste examples.
8. **Report token budget** before and after setup.
9. **Never leave local paths or symlinks as the permanent state.** Workshop paths and extension symlinks are scaffolding only. Every pi package must be git-distributed (`git:` in settings.json). See Distribution Gate.
10. **Never use `pi.agents` or `pi.chains` in package.json.** Pi's package manager processes only `extensions`, `skills`, `prompts`, `themes`. Agent and chain files must be deployed as real files to `~/.pi/agent/agents/` and `~/.pi/agent/chains/`. Symlinks to git clones break when paths change.

### Add Domain — Critical Rules
- New domain's `AGENTS.md` must be fully self-contained.
- Agent definition must have `inheritProjectContext: false` and `cwd: ./<domain>`.
- Never duplicate existing domain content into the new domain.

### Rename Domain — Critical Rules
- Never rename just the folder without updating all five touchpoints.
- Old name must not appear anywhere except session/history files.
- Chain files are most likely place for stale references.

### Remove Domain — Critical Rules
- Always confirm before deleting. Destructive, cannot undo without version control.
- Chain file updates are critical — stale agent reference fails at runtime.
- Routing table must not contain entries pointing to deleted folders.

### Integrate Wiki — Critical Rules
- Never delete wiki content without explicit user confirmation.
- Always scan before modifying. Report findings, get approval before moving.
- Numbered pages must lose prefixes when moved to `_meta/`.
- Domain wiki content belongs in central wiki, not inside domain folders.

### Extract Domain — Critical Rules
- Never modify the original project. Extraction is read + copy only.
- Extracted domain must be self-contained — no references back to source.
- All internal references must be localized to work within extraction.
- Multi-domain chains require attention — mark other-domain steps as stubs.

---

## Distribution Gate (After Every Session)

> **Anti-pattern:** Workshop paths and symlinks that persist across sessions. These bypass git distribution and create fragile, unreproducible installations.

> **Agent Deployment Rule:** `pi update` syncs the git clone but does NOT sync agent files to `~/.pi/agent/agents/` or chains to `~/.pi/agent/chains/`. You must copy them as real files after every update.

Before closing a session:
- [ ] All workshop changes committed and pushed to the git remote
- [ ] `pi update --extensions` run to reconcile git clones
- [ ] Agent files copied from git clone → `~/.pi/agent/agents/` (not symlinks — check with `ls -la`)
- [ ] Chain files copied from git clone → `~/.pi/agent/chains/` (not symlinks — check with `ls -la`)
- [ ] `settings.json` contains zero local paths (`../../Cloud/...`) for this project
- [ ] No stale symlinks in `~/.pi/agent/extensions/` (only npm/git-managed dirs)
- [ ] All 10 pi packages are git-sourced — verify with: `grep -c '"git:' ~/.pi/agent/settings.json`
- [ ] `~/.pi/agent/git/github.com/carlosfrias/` clones match remote HEADs
- [ ] No `pi.agents` or `pi.chains` in package.json (vestigial fields, silently ignored by pi)
