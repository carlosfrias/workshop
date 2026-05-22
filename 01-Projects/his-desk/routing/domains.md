# Domain Routing

**Section ID:** domains  
**Size:** ~2KB  
**LOD:** Low  
**Purpose:** Maps task keywords to domain agents. Read the matching domain file before proceeding with any task.

---

## [S-TIGHT]

Four domains handle all his-desk tasks: study, devotional, site, data. Match keywords from the user prompt to a domain, then load that domain's AGENTS.md. If no clear match or multiple matches, ask the user — do not guess.

---

## Domain Table

When a task involves one of these domains, read the corresponding file before proceeding.
That file contains all context, conventions, rules, and quality checks for the domain.

| Keywords | Domain | Read this file |
|----------|--------|---------------|
| study, passage, scripture, verse, chapter, exegesis, hermeneutics, interpretation, commentary, word study, Hebrew, Greek | Study | `./study/AGENTS.md` |
| devotional, meditation, prayer, reflection, spiritual formation | Devotional | `./devotional/AGENTS.md` |
| site, mkdocs, build, deploy, generate, web, private site | Site | `./site/AGENTS.md` |
| scraper, download, crawl, API, data, fetch, Bible API | Data | `./data/AGENTS.md` |

## Domain Ambiguity Rule [LOD: Medium]

When the user's intent doesn't clearly match a single domain — either no keywords match, or keywords match multiple domains — do NOT guess. Instead:

1. Tell the user which domains their request could map to
2. Suggest the explicit form: "Switch to {domain-name}"
3. Wait for confirmation before loading any domain context

**Example:** "Commentary on John 3" could match **Study** (exegesis) or **Devotional** (reflection). Ask the user which they intend.

## After Domain Load [LOD: Low]

After reading the domain file, follow its instructions for the task. Do not layer additional domain context unless the user explicitly requests it.

---

*See [conventions.md](conventions.md) for model routing and working conventions.*  
*See [workspace.md](workspace.md) for directory layout and cross-references.*