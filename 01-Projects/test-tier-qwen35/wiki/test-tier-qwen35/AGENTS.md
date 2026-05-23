# wiki/test-tier-qwen35 — Documentation Wiki

## Purpose

This domain manages the documentation wiki for the test-tier-qwen35 project. All documentation, research, analysis, and reference material belongs here.

**Primary Use Cases:**
- Domain documentation and wiki pages
- Activity log management
- Reference documentation
- Project metadata and navigation

## Conventions

- **Directory Structure:** `./domain-name/` for domain content
- **Wiki Directory:** `./wiki/test-tier-qwen35/<domain>/` for structured wiki pages
- **Activity Logs:** `./Activity Log.md` in each domain directory
- **Cross-References:** Use `[link](url)` format with relative paths
- **Tags:** Use `#domain` `#status` `#validation` tags for categorization

## Rules

### Mandatory Rules

1. **Domain-Centric Layout** — Wiki must show domains first, documentation second
2. **Activity Log Format** — All entries must follow the template format with timestamp, item, and cross-references
3. **Reference Pages** — `_meta/` directory holds reference docs only (architecture, agent definitions, sample prompts)
4. **Navigation** — Home page must link to all domain activity logs

### Prohibited Actions

1. **No duplication** — Don't duplicate content between wiki and domain AGENTS.md
2. **No central documentation** — Reference docs never belong at wiki root; they belong in `_meta/`
3. **No raw output** — Do not expose raw JSON or unformatted data in wiki pages

## Quality Checklist

**Good wiki looks like:**
- Clear domain organization
- Complete activity logs with timestamps
- Proper cross-references
- Sample prompts and documentation standards

**Bad wiki looks like:**
- Raw JSON output pages
- Missing cross-references
- Unclear domain separation
- Redundant content

## Documentation Protocol

When documenting in the wiki:
1. Follow the `documentation-standard.md` convention in `_meta/`
2. Use Activity Log format for domain-specific entries
3. Reference the domain AGENTS.md for source context
4. Tag entries with relevant tags and cross-reference IDs
5. Update Home.md navigation when adding new sections

**For the Home page (Home.md):**
```markdown
# test-tier-qwen35 Wiki
## Domain Navigation
### [Validation Domain](../domain-validation/Activity Log.md)
### [Results Domain](../domain-results/Activity Log.md)
## Reference Pages
### [Architecture](../_meta/Architecture.md)
### [Documentation Standard](../_meta/Documentation Standard.md)
```

**For activity logs:**
```markdown
### Timestamp-TT — Item Name
**Status:** #passing #completed
**Cross-references:** [domain/Activity Log.md](path)

Item description with evidence reference.
```

## Routing References

Related to domain: **domain-validation** — All validation work should be documented here
Related to domain: **domain-results** — All results should be documented here

After documenting results or validation work, route to the appropriate domain AGENTS.md for further processing. The wiki serves as the public-facing record.

---

*Last updated: 2026-05-22*
