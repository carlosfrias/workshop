# Study Domain

Bible passage analysis, exegesis, word studies, and commentary research. This domain covers the academic and analytical side of Bible study — diving deep into passages, original languages, cross-references, and theological frameworks.

## [S-TIGHT]

Self-contained domain context for study tasks. Read this file, follow its rules, then execute.

---

## Conventions

- Scripture references in standard format: Book Chapter:Verse (e.g., John 3:16, Genesis 1:1–3)
- Bible translations cited by abbreviation: ESV, NASB, NKJV, KJV, NIV, CSB, etc.
- Original language words transliterated with Greek/Hebrew script in parentheses when needed (e.g., *logos* (λόγος), *hesed* (חֶסֶד))
- Hebrew words follow Strong's numbering (e.g., H2617)
- Greek words follow Strong's numbering (e.g., G3056)
- All dates in YYYY-MM-DD format
- Study notes stored in vault: `../../../personal-vault/01-Projects/his-desk/study/`
- Code and tools stored in workshop: `./study/`

## Rules

### Must Always
- Cite the specific translation when quoting scripture
- Present multiple interpretive views when passage meaning is disputed
- Distinguish between translation choices and interpretive claims
- Cross-reference related passages when analyzing a text
- Note the literary and historical context of passages

### Must Never
- Present a single interpretive view as the only valid reading
- Confuse translation choices with the original text's meaning
- Skip historical/cultural context
- Treat devotional application as exegetical finding
- Mix personal application with textual analysis without clear separation

## Quality Checklist

Before considering any study task complete, verify:

- [ ] Scripture references are accurate and properly formatted
- [ ] Translation is cited when quoting
- [ ] Multiple views presented where interpretation is disputed
- [ ] Historical and literary context included
- [ ] Original language terms referenced where relevant
- [ ] Cross-references provided to related passages
- [ ] Clear distinction between observation, interpretation, and application

## Common Mistakes

| Mistake | Correct Approach |
|---------|-----------------|
| Reading modern assumptions into ancient text | Study the cultural and historical context first |
| Treating one translation as definitive | Compare multiple translations and note differences |
| Skipping the original language | At minimum reference Strong's numbers; transliterate key terms |
| Mixing observation and application | Clearly label each section: Observation → Interpretation → Application |
| Assuming all passages are prescriptive | Consider genre: narrative, law, poetry, prophecy, epistle |

## Documentation Protocol

After completing any task, document what you did in the project wiki.

### When to Document
- After completing a passage study or word study
- After discovering significant cross-references or patterns
- After creating or modifying study tools or scripts
- After resolving interpretive questions or edge cases

### What to Document
- **What was done** — Brief summary of the study and findings
- **Why** — Rationale for interpretive choices and methodology
- **What changed** — Files created/modified, notes added
- **Lessons learned** — Patterns, discoveries, or methodological insights

### Where to Document
- Write to the study activity log: `../../wiki/his-desk/study/Activity Log.md`
- Create dedicated study pages in `../../wiki/his-desk/study/` for significant studies
- Cross-reference from related pages if the study connects to devotional or site work
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

- Devotional application of study findings → `../devotional/AGENTS.md`
- Publishing study content → `../site/AGENTS.md`
- Fetching scripture data or APIs → `../data/AGENTS.md`
- Vault-side study notes → `../../../../personal-vault/01-Projects/his-desk/study/AGENTS.md`

---

*Last updated: 2026-05-19*