# Documentation Standard

## Conventions

- All timestamps in US Eastern (America/New_York)
- All date formats: YYYY-MM-DD
- Scripture references: Book Chapter:Verse (e.g., John 3:16, Genesis 1:1–3)
- Bible translations cited by abbreviation: ESV, NASB, NKJV, KJV, etc.
- Original language words transliterated with Greek/Hebrew in parentheses
- Active voice, plain language
- Code blocks tagged with language (`bash`, `python`, `json`, etc.)
- Relative paths only (no absolute paths)

## Activity Log Format

All domain activity logs follow this format:

```markdown
### YYYY-MM-DD — {Title}

**Task**: {What was requested}
**Outcome**: {What was done and result}
**Rationale**: {Why this approach was chosen}
**Files changed**: {List of files created/modified}
**Lessons**: {What to remember for next time}
```

New entries are prepended (most recent first).

## Quality Checklist

Before declaring any documentation task complete:

- [ ] Scripture references are accurate and properly formatted
- [ ] Translation is cited when quoting
- [ ] Active voice used throughout
- [ ] No absolute paths (relative only)
- [ ] Code blocks are language-tagged
- [ ] Cross-references link correctly
- [ ] Activity log updated if non-trivial

## File Naming

- Folder names: `kebab-case` for machine-facing paths
- Wiki pages: Title Case with spaces (Obsidian-compatible)
- Activity logs: `Activity Log.md`
- Meta pages: Title Case in `_meta/` directory