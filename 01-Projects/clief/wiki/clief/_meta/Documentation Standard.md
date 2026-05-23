# Documentation Standard

This document defines the conventions for all documentation in the Clief Notes project.

## General Conventions

- **Timestamps:** US Eastern (America/New_York)
- **Date formats:** YYYY-MM-DD
- **Headings:** Use ATX style (# Header)
- **Lists:** Use - (dash) for unordered, 1. for ordered
- **Links:** Use relative paths within the project, absolute URLs for external references
- **Code blocks:** Always specify language (```python, ```markdown, etc.)

## Activity Log Format

Every activity log entry follows this format:

```markdown
### YYYY-MM-DD — {Title}

**Task**: {What was studied or implemented}
**Outcome**: {What was done and result}
**Rationale**: {Why this approach was chosen}
**Files changed**: {List of files created/modified}
**Lessons**: {What to remember for next time}
```

### What to Document
- Study sessions (vault)
- Implementation work (workshop)
- Decisions that affect architecture or rules
- Issues discovered and resolved

### What NOT to Document
- Trivial lookups with no changes
- Ephemeral intercom messages
- Debugging steps that led nowhere

## Study Notes

Study notes should:
- Include a date and source reference (paper section, module name)
- Distinguish between what the source says (citation) and personal interpretation
- Connect new concepts to existing knowledge where possible
- Use the vault wiki section for storage

## Implementation Notes

Implementation notes should:
- Reference specific ICM layers and principles
- Include file paths and structure descriptions
- Note what worked and what didn't
- Use the workshop wiki section for storage

## Quality Checklist

Before publishing any documentation:
- [ ] Dates are in YYYY-MM-DD format
- [ ] Source references are included where applicable
- [ ] Personal interpretation is clearly labeled vs. cited material
- [ ] Cross-references use correct relative paths