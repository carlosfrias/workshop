# Workshop — Root Router

**Purpose:** Execution workspace for code, scripts, scrapers, data processing, and build systems.
**Counterpart:** `../personal-vault/` — documentation and knowledge management.
**Rule:** This file is a router only. Match project keywords to the project's workshop AGENTS.md.

## [S-TIGHT]

Project-mirrored execution workspace. Each project here mirrors its documentation counterpart in personal-vault at the same `01-Projects/{name}/` path. Code lives here. Documentation lives in personal-vault.

---

## Workshop Map

| Project Keywords | Route To |
|-----------------|----------|
| kingdom, warfare, leadership, mike brewer, nancy, training, curriculum, flashcard, study aid, mkdocs | `./01-Projects/kingdom-warfare-leadership/AGENTS.md` |
| doc-standards, enablement, scaffold, project template, topology, documentation standard | `./01-Projects/doc-standards-enablement/AGENTS.md` |

---

## How This Works

1. **Read this file** — match project keywords
2. **Load the project's workshop AGENTS.md** — conventions, tech stack, entry points
3. **Documentation lives in personal-vault** — `../../personal-vault/01-Projects/{project}/`

## Cross-Reference Convention

| From | To | Path |
|------|----|------|
| Workshop → Docs | `../../personal-vault/01-Projects/{project}/` | Always relative from workshop root |
| Docs → Workshop | `../../workshop/01-Projects/{project}/` | Always relative from personal-vault root |

## Discovery Path

```
1. carlos-desktop/AGENTS.md              ← Pick workspace (broad keywords)
2. workshop/AGENTS.md                    ← YOU ARE HERE (pick project)
3. workshop/01-Projects/{project}/AGENTS.md ← Tech stack, entry points, code conventions
4. personal-vault/01-Projects/{project}/   ← Documentation, plans, session history
```

---

*Last updated: 2026-05-17*
