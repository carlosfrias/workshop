# His Desk — Workshop

**Purpose:** Execution workspace for Bible study tools, scrapers, data processing, and build systems. Knowledge and documentation live in `../../../personal-vault/01-Projects/his-desk/`.

## [S-TIGHT]

Routing hub for his-desk code and tooling. Detects task from keywords, routes to domain agents. All markdown docs live in personal-vault.

---

## Domain Routing

When a task involves one of these domains, read the corresponding file before proceeding.
That file contains all context, conventions, rules, and quality checks for the domain.

| Keywords | Read this file |
|----------|---------------|
| study, passage, scripture, verse, chapter, exegesis, hermeneutics, interpretation, commentary, word study, Hebrew, Greek | `./study/AGENTS.md` |
| devotional, meditation, prayer, reflection, spiritual formation | `./devotional/AGENTS.md` |
| site, mkdocs, build, deploy, generate, web, private site | `./site/AGENTS.md` |
| scraper, download, crawl, API, data, fetch, Bible API | `./data/AGENTS.md` |

After reading the domain file, follow its instructions for the task.

**Domain Ambiguity Rule:** When the user's intent doesn't clearly match a single domain — either no keywords match, or keywords match multiple domains — do NOT guess. Instead:
1. Tell the user which domains their request could map to
2. Suggest the explicit form: "Switch to {domain-name}"
3. Wait for confirmation before loading any domain context

---

## Conventions

- All timestamps in US Eastern (America/New_York)
- All date formats: YYYY-MM-DD
- Scripture references in standard format: Book Chapter:Verse (e.g., John 3:16)
- Keep outputs concise and actionable
- When in doubt, ask — do not assume

## Model Routing

| Route | Model | Triggers |
|-------|-------|----------|
| ultra-reasoning | ollama/kimi-k2.6 | think deeply, comprehensive exegesis |
| reasoning | ollama/qwen3.5:397b | analyze, evaluate, decide, research, plan |
| coding | ollama/deepseek-v4-pro | code, implement, develop, debug |
| vision | ollama/qwen3-vl:235b | image, chart, visual |
| structured | ollama/gemma4:e4b | log, parse, format |
| (default) | ollama/gemma4:e4b | — |

## Project Map

| Keywords | Route To |
|----------|----------|
| study, exegesis, passage, word study, commentary | `./study/AGENTS.md` |
| devotional, meditation, reflection | `./devotional/AGENTS.md` |
| site, mkdocs, build, deploy | `./site/AGENTS.md` |
| scraper, API, download, crawl, data | `./data/AGENTS.md` |

## Default Execution Pattern

| Task Complexity | Default Action | Override |
|-----------------|---------------|----------|
| Single turn, well-scoped | Execute directly via model router | User specifies model |
| Multi-step or complex | `/run decomposer` → local execution → `/run verifier` | User explicitly says "use cloud" |
| Verification fails | Re-run failing sub-task only on cloud | — |

## Workspace Layout

```
workshop/01-Projects/his-desk/
├── AGENTS.md                  ← YOU ARE HERE (routing hub)
├── .pi/
│   ├── APPEND_SYSTEM.md       ← Identity only
│   └── agents/                # Agent definitions & chains
├── study/                     # Bible study tools & analysis
│   └── AGENTS.md
├── devotional/                # Devotional generation & reflection
│   └── AGENTS.md
├── site/                      # MkDocs site build
│   └── AGENTS.md
├── data/                      # Scrapers, downloads, API clients
│   └── AGENTS.md
└── wiki/                      # Project wiki (local reference)
    └── his-desk/
        ├── Home.md
        ├── study/
        ├── devotional/
        ├── site/
        ├── data/
        └── _meta/
```

## Cross-Reference

| From | To | Path |
|------|----|------|
| Workshop → Vault | `../../../personal-vault/01-Projects/his-desk/` | Docs, notes, study guides |
| Vault → Workshop | `../../../workshop/01-Projects/his-desk/` | Code, tools, scrapers, builds |

## Discovery Path

```
1. carlos-desktop/AGENTS.md              ← Pick workspace
2. workshop/AGENTS.md                    ← Pick project
3. workshop/01-Projects/his-desk/AGENTS.md ← YOU ARE HERE
4. workshop/01-Projects/his-desk/{domain}/AGENTS.md ← Domain context
```

---

*Last updated: 2026-05-19*