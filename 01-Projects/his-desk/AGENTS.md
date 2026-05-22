# His Desk — Workshop

**Purpose:** Execution workspace for Bible study tools, scrapers, data processing, and build systems. Knowledge and documentation live in `../../../personal-vault/01-Projects/his-desk/`.

## [S-TIGHT]

Routing hub for his-desk code and tooling. Detects task from keywords, routes to domain agents. All markdown docs live in personal-vault. Low-capacity models: load only the routing section relevant to your task.

---

## Domain Routing

Match task keywords to a domain, then load that domain's AGENTS.md.

| Keywords | Domain | Route To |
|----------|--------|----------|
| study, passage, scripture, verse, chapter, exegesis, hermeneutics, interpretation, commentary, word study, Hebrew, Greek | Study | `./study/AGENTS.md` |
| devotional, meditation, prayer, reflection, spiritual formation | Devotional | `./devotional/AGENTS.md` |
| site, mkdocs, build, deploy, generate, web, private site | Site | `./site/AGENTS.md` |
| scraper, download, crawl, API, data, fetch, Bible API | Data | `./data/AGENTS.md` |

**Ambiguity rule:** If no clear match or multiple matches, tell the user and wait for confirmation before loading domain context.

---

## Load Directive

For detailed context beyond the domain routing above, load the corresponding routing section:

| Need | Load |
|------|------|
| Domain keywords, ambiguity rules | `./routing/domains.md` |
| Conventions, model routing, execution patterns | `./routing/conventions.md` |
| Workspace layout, cross-refs, discovery path | `./routing/workspace.md` |

| Model Tier | Strategy |
|------------|----------|
| Low-capacity (<4K) | This manifest only + one routing section if needed. Max 1 section. |
| Medium-capacity (~8K) | This manifest + up to 2 routing sections. |
| High-capacity (~32K+) | This manifest + all routing sections. |

## Quick Task Routing

| Task | Domain | Routing Detail |
|------|--------|---------------|
| Exegesis on a passage | Study | `./study/AGENTS.md` |
| Write a devotional | Devotional | `./devotional/AGENTS.md` |
| Build or deploy site | Site | `./site/AGENTS.md` |
| Scrape or fetch Bible data | Data | `./data/AGENTS.md` |
| Which model to use? | — | `./routing/conventions.md` (model routing) |
| Where does X file live? | — | `./routing/workspace.md` (layout) |

## Discovery Path

```
1. carlos-desktop/AGENTS.md              ← Pick workspace
2. workshop/AGENTS.md                    ← Pick project
3. workshop/01-Projects/his-desk/AGENTS.md ← YOU ARE HERE (manifest)
4. routing/{section}.md                   ← Detailed routing (demand-loaded)
5. {domain}/AGENTS.md                     ← Domain context
6. FOCUS.md                               ← Current state & handoff
```

---

*Last updated: 2026-05-21*  
*Decomposed from monolithic AGENTS.md per doc-standards LOD pattern.*