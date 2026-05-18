# AGENTS.md — Kingdom Warfare and Leadership (Workshop)

**Documentation home:** `../../personal-vault/01-Projects/kingdom-warfare-leadership/`  
**Workshop root:** `./` (this directory)

## [S-TIGHT]

Execution side of the Kingdom Warfare training project. Contains scrapers, downloaded course data, study aid generators, and the MkDocs Material site source. All planning and session documentation lives in personal-vault.

## Tech Stack

| Component | Technology | Entry Point |
|-----------|-----------|-------------|
| Website scraping | Playwright (Node.js) | `scrape/kw-scrape.js` |
| Data storage | JSON in `data/` | `data/curriculum-extract-2026-05-17.json` |
| Study aid generation | Python 3.14 | `study-aids/generate.py` (to create) |
| Private site | MkDocs Material | `site/mkdocs.yml` (to create) |
| Course content download | Playwright (Node.js) | `scrape/download-course.js` (to create) |

## Directory Structure

```
kingdom-warfare-leadership/
├── AGENTS.md              ← YOU ARE HERE
├── scrape/                # Browser automation scripts
│   └── kw-scrape.js       # Curriculum scraper (Playwright)
│   └── download-course.js # Course content downloader (to create)
├── data/                  # Structured data from scraping
│   └── curriculum-extract-2026-05-17.json  # 17 courses, 200+ lessons
├── site/                  # MkDocs Material site
│   └── mkdocs.yml         # Site configuration (to create)
│   └── docs/              # Site content (to generate)
└── study-aids/            # Study aid generators
    └── generate.py        # Flashcard/diagram/Q&A generator (to create)
```

## Conventions

- **Credentials:** NEVER hardcode. Use environment variables or `.env` (gitignored). See `.env.example`.
- **Node.js:** Use `npx` for Playwright scripts. No global installs required.
- **Python:** Target 3.14. Use `.venv` in project root if needed.
- **Data format:** JSON in `data/`. One file per data source, named with extraction date.
- **Outputs:** Generated study aids written to `site/docs/` for MkDocs consumption.

## Must Always

- Keep credentials out of git
- Test scrapers with `--dry-run` flag where supported
- Document schema changes to data files in commit messages
- Cross-reference documentation in personal-vault for context
- Run `npx playwright install chromium` before first scrape

## Must Never

- Commit `.env` files, auth tokens, or passwords
- Store downloaded course materials directly in personal-vault (they're artifacts, not docs)
- Deploy the MkDocs site without verifying content quality

## Entry Points

| Task | Command |
|------|---------|
| Scrape curriculum | `cd scrape && node kw-scrape.js` |
| Download course content | `cd scrape && node download-course.js` (to create) |
| Generate study aids | `cd study-aids && python generate.py` (to create) |
| Serve MkDocs locally | `cd site && mkdocs serve` (to configure) |
| Build MkDocs | `cd site && mkdocs build` (to configure) |

## Cross-Reference

| Need | Go Here |
|------|---------|
| Project overview, deliverables | `../../personal-vault/01-Projects/kingdom-warfare-leadership/README.md` |
| Current state, priorities | `../../personal-vault/01-Projects/kingdom-warfare-leadership/FOCUS.md` |
| Human workspace | `../../personal-vault/01-Projects/kingdom-warfare-leadership/WORKBENCH.md` |
| Prompt history | `../../personal-vault/01-Projects/kingdom-warfare-leadership/threads/kingdom-warfare-leadership/0-THREAD.md` |
| Session notes | `../../personal-vault/01-Projects/kingdom-warfare-leadership/journal/` |

---

*Last updated: 2026-05-17*
