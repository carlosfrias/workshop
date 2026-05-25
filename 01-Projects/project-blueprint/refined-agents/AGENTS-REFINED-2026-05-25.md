# AGENTS-REFINED — Project Blueprint — 2026-05-25

> **Session:** Distribution discipline + Phase 5 completion
> **Generated:** 2026-05-25 from session artifact analysis
> **Status:** BATTLED-TESTED — all rules verified against pi source code

## [S-TIGHT]

Session discovered that `pi.agents` and `pi.chains` in package.json are vestigial fields silently ignored by pi. Pi's package manager only processes `extensions`, `skills`, `prompts`, `themes`. Agents and chains must be deployed as real files to `~/.pi/agent/agents/` and `~/.pi/agent/chains/` — symlinks to git clones break. This knowledge is now encoded as Critical Rule #10 and a Distribution Gate checklist item.

---

## Conventions (Verified)

- **Skill vs Agent: know the difference.** Skills are directory-based with `SKILL.md` and are auto-discovered by pi from `pi.skills` in package.json. Agents are individual `.md` files with frontmatter and are NOT auto-discovered by pi — they require manual deployment to `~/.pi/agent/agents/`.
- **Vestigial fields mislead.** Including `pi.agents` or `pi.chains` in package.json creates false confidence. Remove them to avoid confusion.
- **Real files survive path changes.** Agent files copied to `~/.pi/agent/agents/` are stable. Symlinks to git clone paths break when Dropbox→Cloud migrations or repo moves happen.

## Rules (Battle-Tested)

### Must Always
- **Verify agents are real files.** After `pi update`, run `ls -la ~/.pi/agent/agents/` and confirm no entries start with `l` (symlink).
- **Remove `pi.agents` and `pi.chains` from package.json.** These fields are not in pi's `RESOURCE_TYPES` array `["extensions", "skills", "prompts", "themes"]` and are silently ignored.
- **Deploy agent files manually after every update.** `pi update --extensions` syncs git clones but does NOT sync agent files to `~/.pi/agent/agents/`.

### Must Never
- **Never create symlinks in `~/.pi/agent/agents/` or `~/.pi/agent/chains/`.** These point to git clone paths that change during migrations, reinstalls, or path updates.
- **Never assume `pi install` handles agents.** It doesn't. The `custom-agents.js` discovery only reads flat `.md` files from `~/.pi/agent/agents/` and `<cwd>/.pi/agents/`.

## Quality Checklist (Verified)

Before considering any distribution complete:

- [ ] `pi.agents` field removed from all package.json files
- [ ] `pi.chains` field removed from all package.json files
- [ ] Agent files in `~/.pi/agent/agents/` are real files (not symlinks)
- [ ] Chain files in `~/.pi/agent/chains/` are real files (not symlinks)
- [ ] `pi update --extensions` completes without errors
- [ ] `subagent list` shows all expected custom agents
- [ ] No Dropbox or stale path references in agent files

## Common Mistakes (Discovered)

| Mistake | Symptom | Root Cause | Correct Approach |
|---------|---------|------------|-----------------|
| Agent symlinks to git clones | Agents disappear after path migration | Symlink target becomes invalid | Copy as real files |
| `pi.agents` in package.json | False confidence that agents deploy automatically | Field is vestigial, not in RESOURCE_TYPES | Remove field, deploy agents manually |
| `pi update` then forget to copy agents | Old agent version used after update | pi update only syncs git clone | Add "copy agents" to Distribution Gate |
| Fleet-dispatcher as symlink | Same fragility as agents | All agent files need same treatment | Copy as real file |

## Delta Report

### What Changed from Original AGENTS.md

| Section | Change | Rationale |
|---------|--------|-----------|
| SKILL.md Architecture Summary | Added "Agent vs Skill Deployment" table | Prevents future agent/skill confusion |
| setup.md Phase 11 | Added "Deploy agent files" step + warning | Makes agent deployment explicit |
| checklists.md Distribution Gate | Added 2 agent/chain checklist items + anti-pattern docs | Catches symlink errors before session close |
| checklists.md Critical Rules | Added Rule #10: never use pi.agents/pi.chains | Prevents vestigial field regression |
| package.json | Removed pi.agents and pi.chains | Eliminates false confidence |

## Documentation Protocol

After completing any distribution task:
1. Verify agents are real files: `find ~/.pi/agent/agents/ -type l -ls` → should return empty
2. Verify chains are real files: `find ~/.pi/agent/chains/ -type l -ls` → should return empty
3. Run `subagent list` and confirm all custom agents appear
4. Update this AGENTS-REFINED if new mistakes are discovered
