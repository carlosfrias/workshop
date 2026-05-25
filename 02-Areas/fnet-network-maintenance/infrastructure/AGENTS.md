# AGENTS.md — Infrastructure

Address networking issues & maintaining the network definition for FNET infrastructure.

## [S-TIGHT]

## Conventions

- All network configurations must be version-controlled
- Document every change to the network definition
- Follow least-privilege principle for network access rules
- All timestamps in US Eastern / America/New_York
- All date formats: YYYY-MM-DD

## Rules

### Must Always
- Verify network connectivity before and after changes
- Back up current network configuration before making modifications
- Document the rationale for every network rule change
- Test changes in a non-production context when possible

### Must Never
- Modify production network rules without explicit approval
- Leave temporary firewall rules in place after troubleshooting
- Store credentials or secrets in plain text within network configs
- Assume network topology — always verify current state

## Quality Checklist

Before considering any task complete, verify:

- [ ] Network connectivity verified before and after changes
- [ ] Configuration backed up before modifications
- [ ] Changes documented in the activity log
- [ ] No orphaned or temporary rules left behind
- [ ] Least-privilege principle followed for access rules

## Common Mistakes

| Mistake | Correct Approach |
|---------|-----------------|
| Assuming network topology matches documentation | Verify current state with live checks before making changes |
| Leaving temporary firewall rules after troubleshooting | Always schedule cleanup or add explicit TTL/removal notes |
| Modifying production rules directly | Stage changes, get approval, then apply with rollback plan |

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
- Write to your domain's activity log: `wiki/fnet-network-maintenance/infrastructure/Activity Log.md`
- If the entry relates to a significant topic that deserves its own page, create a new page in `wiki/fnet-network-maintenance/infrastructure/`
- Cross-reference from related pages if the change affects multiple domains
- Project-level reference pages (architecture, agents, sample prompts) live in `wiki/fnet-network-maintenance/_meta/` — do not add domain-specific content there

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