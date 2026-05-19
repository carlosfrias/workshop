# NextCloud Wiki — AGENTS.md

Documentation domain for the NextCloud project. Manages the wiki, research notes, and knowledge base.

## [S-TIGHT]

Documentation and knowledge management for NextCloud. Read this file when working on wiki pages, research notes, or documentation.

---

## Conventions

- Wiki pages use Markdown with wikilinks (`[[]]`) for cross-references
- Activity log entries are prepended (newest first)
- Research notes link back to their source URLs when applicable
- All timestamps in YYYY-MM-DD HH:MM:SS US Eastern

## Documentation Protocol

After completing any documentation task, update the relevant activity log in the wiki.

### Where to Document
- Infrastructure work → `infrastructure/Activity Log.md`
- Research → `research/Activity Log.md`
- Architecture decisions → `_meta/Architecture.md`

### Cross-References
- Vault knowledge notes: `../../../../../personal-vault/01-Projects/nextcloud/`
- Lab specs: `../../../../03-Resources/Infrastructure/lab-specs/`

## Quality Checklist

- [ ] Activity log entries have date, task, outcome, and lessons
- [ ] Architecture decisions document why, not just what
- [ ] Links to external sources (URLs) are preserved
- [ ] No absolute paths — use relative paths only