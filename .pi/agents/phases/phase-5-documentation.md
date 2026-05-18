# Phase 5: Documentation

**Purpose:** Session notes, status updates, backlog updates, recommendation capture.
**When to load:** After quality check passes, before ending session.
**Target model:** gemma4:e4b

---

## Documentation Rules

All documentation must adhere to the universal standards defined in the `doc-standards` skill.

**Required Action**: Before proceeding with any documentation task:
1. Load the `doc-standards` skill: `/Users/friasc/.pi/agent/git/github.com/carlosfrias/doc-standards/skills/doc-standards/SKILL.md`
2. Load the vault-native taxonomy mapping: `/Users/friasc/Dropbox/carlos-desktop/personal-vault/01-Projects/Carlos-Trading-Desk/archive/Doc-Standards Vault Taxonomy.md`

No documentation file may be created, edited, or reviewed until BOTH are loaded.

- Every session MUST produce either a STATUS or SESSION-NOTES file as defined in the skill.
- Incomplete items MUST be captured in BACKLOG.md as defined in the skill.
- Recommendations and planning ideas MUST be captured without interrupting flow.

## Session Documentation

Follow the **Session & Lifecycle Documentation** section of the `doc-standards` skill for the creation and formatting of:

- **Status Files**: `wiki/operational/status/STATUS-{YYYY-MM-DD-HHMM}.md` → **LEGACY** — migrate to `personal-vault/01-Projects/.../status/STATUS-{YYYY-MM-DD-HHMM}.md`
- **Session Notes**: `wiki/operational/sessions/SESSION-NOTES-{YYYY-MM-DD-HHMM}.md` → **LEGACY** — migrate to `personal-vault/01-Projects/.../journal/JOURNAL-{YYYY-MM-DD-HHMM}.md`
- **Backlog Updates**: `wiki/operational/BACKLOG.md` → **LEGACY** — migrate to `personal-vault/01-Projects/.../Overview.md`
- **Recommendation Capture**: `wiki/recommendations/RECOMMENDATION-{YYYY-MM-DD-HHMM}.md` → **LEGACY** — migrate to `personal-vault/03-Resources/Recommendations/`
- **Planning Capture**: `wiki/operational/planning/PLAN-{YYYY-MM-DD-HHMM}.md` → **LEGACY** — migrate to `personal-vault/01-Projects/.../` (new Plan folder)

**Enforcement**: BOTH the `doc-standards` skill AND the vault-native taxonomy mapping must be loaded before writing any of the above files.

## Common Mistakes to Avoid

- Writing scripts to `/tmp/` without relocating to permanent path
- Forgetting to update BACKLOG.md with incomplete items
- Skipping status/session notes for "quick" tasks
- Not linking new docs in WIKI.md

## Prompt-Triggered References

Load these on-demand when task keywords match:

| Keywords | File |
|----------|------|
| network troubleshooting, node offline, driver issue | `./prompts/network-troubleshooting.md` |
| pi-keyword-router, keyword routing | `./extensions/pi-keyword-router/README.md` |
| meta-orchestration, complexity classification | `./wiki/operational/planning/PLAN-2026-05-01-1645.md` **LEGACY — migrate to `personal-vault/01-Projects/.../1-PLAN.md`** |
| task decomposition, model assignment | `./wiki/operational/planning/PLAN-2026-05-01-1547.md` **LEGACY — migrate to `personal-vault/01-Projects/.../1-PLAN.md`** |

## Cross-Domain References

| Need | Location |
|------|----------|
| Trading Desk Wiki | `../../WIKI.md` |
| Node connection guide | `../wiki/node-connection-guide.md` |
| Ollama setup | `../wiki/ollama-setup.md` |
| Orchestration plan | `../planning/PLAN-2026-05-01-1547.md` **LEGACY — migrate to `personal-vault/01-Projects/.../1-PLAN.md`** |
| Decomposition plan | `../planning/PLAN-2026-05-02-1930-LLM-DRIVEN-DECOMPOSITION.md` **LEGACY — migrate to `personal-vault/01-Projects/.../1-PLAN.md`** |

## Published Packages

| Package | Repository | Install |
|---------|-----------|---------|
| pi-keyword-router | `carlosfrias/pi-keyword-router` | `pi install github:carlosfrias/pi-keyword-router` |
| project-blueprint | `carlosfrias/project-blueprint` | `pi install github:carlosfrias/project-blueprint` |
| trading-agents | `carlosfrias/trading-agents` | `pi install github:carlosfrias/trading-agents` |

---

**Session complete.** All 5 phases executed. Documentation captured.
