# Execution Pattern & Skill Auto-Load

**Section ID:** execution-and-skills  
**Size:** ~2KB  
**LOD:** Low  
**Purpose:** Default execution pattern and mandatory skill auto-load rules for all tasks.

---

## [S-TIGHT]

Complex tasks go through decomposer → local execution → verifier. Before any task, check skill auto-load rules — if the task involves `.md` files, both doc-standards and vault taxonomy mapping MUST be loaded first.

---

## Default Execution Pattern

| Task Complexity | Default Action | Override |
|-----------------|---------------|----------|
| Single turn, well-scoped | Execute directly via model router | User specifies model |
| Multi-step or complex | `/run decomposer` → local execution → `/run verifier` | User explicitly says "use cloud" |
| Verification fails | Re-run failing sub-task only on cloud | — |

**Rule:** Do not manually pick models. Let the model router and decomposer make routing decisions.

**Reference:** See `.pi/APPEND_SYSTEM.md` for the full cost-optimized execution framework.

---

## Skill Auto-Load Rules — MANDATORY

Before executing any task, check the user prompt and activated domain against this table. If a match is found, **load the skill via `read` before any work begins**. The skill takes precedence over general conventions.

| Trigger (keywords or domain) | Skill to load | Load path |
|-------------------------------|---------------|-----------|
| wiki, documentation, docs, markdown, `*.md`, README, status, session-notes, backlog, activity log, manifest, planning doc | **doc-standards** | `/Users/friasc/.pi/agent/git/github.com/carlosfrias/doc-standards/skills/doc-standards/SKILL.md` |
| wiki, documentation, docs, markdown, `*.md`, README, status, session-notes, backlog, activity log, manifest, planning doc | **vault taxonomy mapping** | `../personal-vault/01-Projects/Carlos-Trading-Desk/archive/Doc-Standards Vault Taxonomy.md` |

### Hard Rules

1. **If the task involves creating, editing, or reviewing any file ending in `.md`, BOTH skills MUST be loaded first.** Do not skip this step because the task seems "small" or "quick."
2. Skill auto-load applies regardless of task complexity — even single-turn tasks must check.
3. Loaded skills take precedence over general conventions in this file.

---

*Next: For model routing details, load [model-routing.md](model-routing.md). For workspace layout and cross-references, load [workspace-structure.md](workspace-structure.md).*