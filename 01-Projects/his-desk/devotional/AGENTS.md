# Devotional Domain

Devotional content, meditation guides, prayer frameworks, and spiritual formation resources. This domain covers the devotional and application side of Bible study — taking scripture from analysis to personal transformation.

## [S-TIGHT]

Self-contained domain context for devotional tasks. Read this file, follow its rules, then execute.

---

## Conventions

- Scripture references in standard format: Book Chapter:Verse (e.g., Psalm 23:1)
- Bible translations cited by abbreviation when quoting
- Devotional structure: Scripture → Reflection → Response → Prayer
- All dates in YYYY-MM-DD format
- Devotional notes stored in vault: `../../../personal-vault/01-Projects/his-desk/devotional/`
- Generation tools stored in workshop: `./devotional/`

## Rules

### Must Always
- Ground every devotional in specific scripture passages
- Distinguish between what the text says and personal application
- Offer practical response steps, not just reflection
- Include a prayer prompt or framework
- Respect the user's stated theological framework

### Must Never
- Present devotional application as exegetical certainty
- Skip the scripture text and jump straight to application
- Use vague spiritual language without grounding in specific passages
- Assume the user's life circumstances without asking
- Mix personal opinions with scripture teaching

## Quality Checklist

Before considering any devotional task complete, verify:

- [ ] Scripture passage is quoted or referenced at the start
- [ ] Translation is cited if quoting
- [ ] Clear distinction between observation and application
- [ ] Practical response steps are concrete and actionable
- [ ] Prayer prompt or framework is included
- [ ] The devotional is grounded in the passage, not imposed on it

## Common Mistakes

| Mistake | Correct Approach |
|---------|-----------------|
| Starting with application instead of text | Always begin with the scripture passage itself |
| Vague "pray about it" conclusions | Provide specific prayer prompts or frameworks |
| Treating devotional as commentary | Focus on personal response, not academic analysis |
| One-size-fits-all responses | Tailor to the user's season and stated framework |

## Documentation Protocol

After completing any task, document what you did in the project wiki.

### When to Document
- After creating a devotional series or individual devotional
- After developing a prayer framework or meditation guide
- After discovering patterns connecting study insights to devotional application
- After creating or modifying devotional generation tools

### What to Document
- **What was done** — Brief summary of the devotional and themes
- **Why** — Rationale for chosen passages and application approach
- **What changed** — Files created/modified
- **Lessons learned** — Patterns or methodological insights for future devotionals

### Where to Document
- Write to the devotional activity log: `../../wiki/his-desk/devotional/Activity Log.md`
- Create dedicated pages in `../../wiki/his-desk/devotional/` for series or guides
- Cross-reference study findings when the devotional builds on exegetical work
- Project-level reference pages live in `../../wiki/his-desk/_meta/`

### Format
```markdown
### YYYY-MM-DD — {Title}

**Task**: {What was requested}
**Outcome**: {What was done and result}
**Rationale**: {Why this approach was chosen}
**Files changed**: {List of files created/modified}
**Lessons**: {What to remember for next time}
```

## Cross-Domain References

For tasks that span domains, consult the routing table in `./AGENTS.md` (project root).

- Exegesis and passage analysis → `../study/AGENTS.md`
- Publishing devotional content → `../site/AGENTS.md`
- Fetching scripture data → `../data/AGENTS.md`
- Vault-side devotional notes → `../../../../personal-vault/01-Projects/his-desk/devotional/AGENTS.md`

---

*Last updated: 2026-05-19*