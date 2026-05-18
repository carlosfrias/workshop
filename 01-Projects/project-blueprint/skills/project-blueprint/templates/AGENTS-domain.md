# {domain_name}

{domain_description}

## Conventions

- {convention_1}
- {convention_2}
- All outputs should be {output_style}

## Rules

### Must Always
- {rule_always_1}
- {rule_always_2}

### Must Never
- {rule_never_1}
- {rule_never_2}

## Quality Checklist

Before considering any task complete, verify:

- [ ] {quality_check_1}
- [ ] {quality_check_2}
- [ ] {quality_check_3}

## Common Mistakes

| Mistake | Correct Approach |
|---------|-----------------|
| {mistake_1} | {correct_1} |
| {mistake_2} | {correct_2} |

## Documentation Protocol

After completing any task, document what you did in the project wiki.

### When to Document
- After making decisions that affect the domain's architecture or rules
- After completing a non-trivial task (anything beyond a simple lookup or status check)
- After discovering and resolving issues, edge cases, or common mistakes
- After creating, modifying, or removing any files or configurations

### What to Document
- **What was done** — Brief summary of the task and outcome
- **Why** — Rationale for decisions made (especially non-obvious ones)
- **What changed** — Files created/modified, configurations updated, rules added
- **Lessons learned** — Anything that would help the next person (or agent) avoid mistakes

### Where to Document
- Write to your domain's activity log: `{wiki_path}/{project_name}/{domain_name}/Activity Log.md`
- If the entry relates to a significant topic that deserves its own page, create a new page in `{wiki_path}/{project_name}/{domain_name}/` with a descriptive name
- Cross-reference from related pages if the change affects multiple domains
- Project-level reference pages (architecture, agents, sample prompts) live in `{wiki_path}/{project_name}/_meta/` — do not add domain-specific content there

### Format
Use a consistent format for wiki entries:

```markdown
### YYYY-MM-DD — {Title}

**Task**: {What was requested}
**Outcome**: {What was done and result}
**Rationale**: {Why this approach was chosen}
**Files changed**: {List of files created/modified}
**Lessons**: {What to remember for next time}
```

### Do Not Document
- Trivial lookups or status checks with no changes
- Orchestrator intercom messages (those are ephemeral)
- Intermediate debugging steps that led nowhere

## Cross-Domain References

For tasks that span domains, consult the routing table in `./AGENTS.md` (project root).