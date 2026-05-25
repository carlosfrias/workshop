# Documentation Standard — pi-multimodal-proxy

Conventions, formatting rules, Activity Log format, and quality checklist for all documentation in this project.

## Conventions

### Timestamps
- Timezone: US Eastern (America/New_York)
- Format: `YYYY-MM-DD HH:MM` for timestamps, `YYYY-MM-DD` for dates
- Example: `2026-05-24 14:30` or `2026-05-24`

### File Naming
- Use kebab-case: `activity-log.md`, not `ActivityLog.md` or `activity_log.md`
- Exception: `Home.md`, `Activity Log.md` (spaces allowed for wiki readability)
- Dates in filenames: `YYYY-MM-DD-description.md`

### Cross-References
- Use relative paths: `[Architecture](_meta/Architecture.md)`
- Use wikilinks in Obsidian: `[[Architecture]]`
- For workshop files: `[Root AGENTS](../../../AGENTS.md)`

## Activity Log Format

Each domain maintains an Activity Log at `wiki/pi-multimodal-proxy/{domain}/Activity Log.md`.

### Entry Template

```markdown
### YYYY-MM-DD — {Task Title}

**Task**: {What was requested}
**Input**: {Image type, dimensions, complexity — if applicable}
**Outcome**: {What was extracted/analyzed}
**Tokens**: {Input KB / Output KB}
**Files changed**: {List of files created/modified}
**Lessons**: {Edge cases, quality issues, tips for next time}
```

### Example Entry

```markdown
### 2026-05-24 — Invoice OCR Extraction

**Task**: Extract line items from vendor invoice screenshot
**Input**: PNG screenshot, 1920x1080, moderate complexity (table with 12 rows)
**Outcome**: Extracted 12 line items with quantities, prices, totals to JSON
**Tokens**: 2.1KB input / 3.8KB output
**Files changed**: `./vision-agent/extracted-invoice-2026-05-24.json`
**Lessons**: Table borders were faint — used row alignment heuristic instead of border detection. For future invoices, ask user to confirm table structure if confidence <90%.
```

### When to Log

**Log:**
- Non-trivial analysis (anything beyond simple lookup)
- Decisions made that affect interpretation
- Edge cases discovered (unusual image formats, quality issues)
- Files created or modified
- Token budget exceeded (and how it was handled)

**Do Not Log:**
- Trivial lookups or status checks
- Intermediate debugging steps that led nowhere
- Failed attempts with no lasting changes

## Quality Checklist

Before publishing any documentation:

- [ ] Timestamps in correct format (YYYY-MM-DD)
- [ ] Relative paths for cross-references
- [ ] Activity Log entries follow template
- [ ] Token budgets documented (if applicable)
- [ ] Lessons learned captured (not just what, but why)
- [ ] No redundant content (DRY principle)

## Wiki Organization

```
wiki/pi-multimodal-proxy/
├── Home.md                          # Domain index + navigation
├── vision-agent/                    # Domain wiki — front and center
│   └── Activity Log.md              # Running log of tasks
└── _meta/                           # Reference docs (reachable, non-central)
    ├── Architecture.md              # Why this design
    ├── Agent Definitions.md         # All agents catalog
    └── Documentation Standard.md    # This file
```

**Principle:** Domains are the wiki's primary content. Reference docs about the system live in `_meta/` — important but not the main focus.

## For Non-Technical Users

Documentation should be accessible to non-technical users:
- Avoid jargon where possible
- Include copy-paste examples
- Explain *why* not just *what*
- Use tables and bullet lists (easier to scan than prose)

---

*Last updated: 2026-05-24*
