# TI-034: Project-Blueprint Consumer Acceptance Testing

**Issue Home:** [0-ISSUE.md](./0-ISSUE.md)
**Status:** TBD
**Priority:** TBD

---

### TI-034: Project-Blueprint Consumer Acceptance Testing
**Created:** 2026-05-06
**Status:** ✅ **COMPLETE** — All 6 fixes implemented, 27/27 acceptance tests pass
**Priority:** 🔴 **HIGH** — Causes incorrect model routing, wasted API cost, wrong model for task complexity
**Rationale:** When consumers install project-blueprint via `pi install github:carlosfrias/project-blueprint`, the scaffolding wizard creates unexpected files in the workspace root (`technical-infrastructure/`, `templates/`, `Final Summary.md`, `model-routing-decisions.*`). These artifacts belong in the skill folder (`~/.pi/agent/skills/project-blueprint/`) or in `.pi/sessions/`, NOT in the consumer's workspace. This breaks the "clean root" contract and makes consumers lose trust in the tool.

**Discovered in:** `~/Dropbox/carlos-desktop` workspace (his-desk domain setup)

**Critical Bugs to Fix:**
- 🔴 **CRITICAL:** `technical-infrastructure/` created in workspace root (Trading Desk artifact leaked)
- 🔴 **CRITICAL:** `templates/` copied to workspace root (should stay in skill folder only)
- 🔴 **CRITICAL:** `Final Summary.md` dumped to root (should archive to `.pi/sessions/`)
- 🟡 **MEDIUM:** `model-routing-decisions.jsonl` stored in wrong directory (`technical-infrastructure/wiki/sessions/` instead of `.pi/sessions/`)
- 🟡 **MEDIUM:** No skill reference file in `.pi/agents/skills/project-blueprint.md`

**Deliverables:**
- [x] Consumer acceptance prompt: `technical-infrastructure/prompts/PROMPT-TI034-PROJECT-BLUEPRINT-CONSUMER.md`
- [x] Wiki page with embedded prompt: `wiki/operational/planning/prompts/PROMPT-TI034-PROJECT-BLUEPRINT-CONSUMER.md`
- [ ] Fix scaffolding logic: remove `technical-infrastructure/` from root creation
- [ ] Fix scaffolding logic: keep `templates/` in skill folder only
- [ ] Fix scaffolding logic: redirect `Final Summary.md` to `.pi/sessions/`
- [ ] Fix scaffolding logic: store session artifacts in `.pi/sessions/`
- [ ] Add skill reference: `.pi/agents/skills/project-blueprint.md`
- [ ] Run acceptance test: execute prompt in fresh workspace
- [ ] Verify clean root: `ls -la` shows only AGENTS.md, .pi/, domain folders, wiki/ (if requested)
- [ ] Verify consumer access: confirm `~/.pi/agent/skills/project-blueprint/` is readable/modifiable
- [ ] Tag as production-ready when all AC-4 (clean root) criteria pass

**Acceptance Criteria (30+ checklist items):**
- **AC-1 (Installation):** Install succeeds, skill in `pi skill list`, no root files created during install
- **AC-2 (Skill Location):** Templates in `~/.pi/agent/skills/project-blueprint/templates/`, NOT root
- **AC-3 (Scaffolding Interview):** Interview starts, questions stored in `.pi/sessions/`, no root files during interview
- **AC-4 (Clean Root — CRITICAL):** Only `AGENTS.md`, `.pi/`, domain folders, `wiki/` (if requested) in root. ❌ No `technical-infrastructure/`, ❌ No `templates/`, ❌ No `Final Summary.md`, ❌ No `model-routing-decisions.*`
- **AC-5 (Wiki & VitePress):** `wiki/` has markdown only, `wiki-build/` is sibling to `wiki/`, NOT in root
- **AC-6 (Session Storage):** All artifacts in `.pi/sessions/`, none in root
- **AC-7 (Consumer Access):** Can locate and modify skill files at `~/.pi/agent/skills/project-blueprint/`
- **AC-8 (Domain Management):** `/add-domain`, `/rename-domain`, `/remove-domain` maintain clean root

**Prompts:**
- Standalone prompt: [`technical-infrastructure/prompts/PROMPT-TI034-PROJECT-BLUEPRINT-CONSUMER.md`](../../prompts/PROMPT-TI034-PROJECT-BLUEPRINT-CONSUMER.md)
- Wiki page: [`wiki/operational/planning/prompts/PROMPT-TI034-PROJECT-BLUEPRINT-CONSUMER.md`](../../../wiki/operational/planning/prompts/PROMPT-TI034-PROJECT-BLUEPRINT-CONSUMER.md)

**Known Issues:**
| Issue | Severity | Root Cause | Required Fix |
|-------|----------|-----------|--------------|
| `technical-infrastructure/` in root | 🔴 Critical | Scaffolding logic creates Trading Desk artifact | Remove hardcoded path |
| `templates/` in root | 🔴 Critical | Copy step misplaces templates | Templates stay in skill folder only |
| `Final Summary.md` in root | 🔴 Critical | Output file location hardcoded to root | Redirect to `.pi/sessions/` |
| `model-routing-decisions.jsonl` wrong location | 🟡 Medium | Session data stored in wrong directory | Move to `.pi/sessions/` |
| Missing skill reference in `.pi/agents/` | 🟡 Medium | No skill metadata file created | Add `skills/project-blueprint.md` |

**Test Environment:**
- Fresh workspace: `mkdir ~/pb-consumer-test`
- No git init, no existing files
- Run `pi install github:carlosfrias/project-blueprint`
- Run `pi skill project-blueprint`
- Verify with `ls -la`

**Estimated Effort:** 4-6 hours (prompt creation ✅ done, fixes 3-4h, testing 1-2h)

---

## 🟡 Medium Priority

---

## Navigation

| Need | Location |
|------|----------|
| Back to backlog | [../BACKLOG.md](../BACKLOG.md) |
