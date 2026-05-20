# Site Domain

MkDocs site build, deployment, and configuration for His Desk. This domain covers building and deploying the Bible study site — VitePress/MkDocs configuration, templates, navigation, search, and publishing.

## [S-TIGHT]

Self-contained domain context for site tasks. Read this file, follow its rules, then execute.

---

## Conventions

- Site source in `./site/`
- Build tool: MkDocs with Material theme (unless user specifies otherwise)
- All content sourced from vault markdown files (single source of truth)
- Clean URLs without `.html` extensions
- Mobile-first responsive design
- All dates in YYYY-MM-DD format

## Rules

### Must Always
- Keep content in the vault; site references it, never duplicates
- Use relative links within the site
- Test builds locally before deploying
- Maintain consistent navigation structure
- Ensure all scripture references are formatted consistently in site output

### Must Never
- Duplicate vault content into site source — reference or symlink instead
- Break existing URLs when restructuring
- Deploy without running a local build test
- Hard-code absolute paths that break across environments

## Quality Checklist

Before considering any site task complete, verify:

- [ ] `mkdocs build` (or equivalent) completes without errors
- [ ] All internal links resolve correctly
- [ ] Navigation is consistent and complete
- [ ] Mobile rendering is acceptable
- [ ] Search indexing covers all content pages
- [ ] No duplicate content between site and vault

## Common Mistakes

| Mistake | Correct Approach |
|---------|-----------------|
| Copying vault content into site | Reference vault content via symlinks or build scripts |
| Hard-coded absolute paths | Use relative paths or site configuration variables |
| Ignoring mobile layout | Always test responsive breakpoints |
| Deploying without local test | Run `mkdocs build` locally first |

## Documentation Protocol

After completing any task, document what you did in the project wiki.

### When to Document
- After modifying site configuration or navigation
- After deploying a new version
- After adding new content sections or templates
- After resolving build or deployment issues

### What to Document
- **What was done** — Brief summary of the site change
- **Why** — Rationale for configuration or structure decisions
- **What changed** — Config files modified, templates added
- **Lessons learned** — Build quirks, deployment steps, gotchas

### Where to Document
- Write to the site activity log: `../../wiki/his-desk/site/Activity Log.md`
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

- Study content to publish → `../study/AGENTS.md`
- Devotional content to publish → `../devotional/AGENTS.md`
- Data pipelines for site content → `../data/AGENTS.md`
- Vault source content → `../../../../personal-vault/01-Projects/his-desk/`

---

*Last updated: 2026-05-19*