# Wiki Domain

Documentation, research, and analysis operations for pi-multimodal-proxy.

## Purpose

This domain handles:
- Writing and maintaining wiki documentation
- Research tasks (web searches, documentation lookups)
- Analysis and synthesis of information
- Creating sample prompts for non-technical users

## Conventions

- All timestamps in US Eastern (America/New_York)
- Date format: YYYY-MM-DD
- Wiki pages: Markdown with clear headings and bullet lists
- Cross-references: Use relative paths or wikilinks
- Research citations: Include URLs with access dates

## Rules

### Must Do
- Document all non-trivial work in the wiki
- Update Activity Logs after completing tasks
- Create sample prompts for new capabilities
- Keep documentation accessible to non-technical users
- Cross-reference related pages

### Must Not Do
- Never create duplicate content (DRY principle)
- Never put domain-specific content in _meta/ (use domain wiki instead)
- Never exceed token budget for research tasks (<4KB total)
- Never skip citation of external sources

## Quality Checklist

Before delivering documentation:

- [ ] Clear structure with headings and bullet lists
- [ ] Cross-references working (relative paths or wikilinks)
- [ ] Timestamps in correct format (YYYY-MM-DD)
- [ ] Sample prompts included (if applicable)
- [ ] Activity Log updated
- [ ] No redundant content

## Token Budget

| Operation | Budget |
|-----------|--------|
| Wiki page creation | <3KB total |
| Research + synthesis | <4KB total |
| Sample prompt creation | <2KB total |

## Documentation Protocol

Log all work in: `../wiki/pi-multimodal-proxy/wiki-domain/Activity Log.md`

**Format:**
```markdown
### YYYY-MM-DD — {Task Title}

**Task**: {What was requested}
**Outcome**: {What was created/updated}
**Pages affected**: {List of wiki pages}
**Lessons**: {What to remember for next time}
```

---

*Last updated: 2026-05-24*
