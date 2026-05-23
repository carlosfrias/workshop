# Vault — Study & Knowledge Management

This domain covers the study, note-taking, and curriculum-tracking side of Clief Notes. The vault is where learning happens: reading the ICM paper, tracking progress through the Clief Notes curriculum, capturing insights, and building a personal knowledge base.

## Conventions

- Study sessions are 45 minutes, 3 times per week
- Use session dates in YYYY-MM-DD format for all notes
- Capture insights as you study — don't wait until later
- Link concepts to their source (paper section, lesson module, etc.)
- Maintain a curriculum tracker showing what's been studied and what's next

## Rules

### Must Always
- Date-stamp all study notes and activity log entries
- Track curriculum progress in the schedule
- Reference specific sections of the ICM paper when discussing concepts
- Connect new concepts back to the 5-layer ICM hierarchy when relevant
- Keep study notes factual and sourced — distinguish between what the paper says and personal interpretation

### Must Never
- Skip recording a study session in the activity log
- Mix personal opinions with paper citations without clear labeling
- Create notes without dates or source references
- Fall behind on curriculum tracking without flagging it

## Quality Checklist

Before considering any task complete, verify:

- [ ] Study notes have dates and source references
- [ ] Curriculum tracker is up to date
- [ ] New concepts are connected to existing knowledge where possible
- [ ] The schedule reflects actual progress, not aspirational progress

## Common Mistakes

| Mistake | Correct Approach |
|---------|-----------------|
| Writing vague notes like "learned about layers" | Write specific notes: "ICM Layer 0 (CLAUDE.md) provides global identity — ~800 tokens" |
| Skipping the activity log after a session | Always log, even for short sessions |
| Reading ahead without anchoring to the paper | Always tie insights to specific paper sections |
| Losing track of what module you're on | Update the curriculum tracker after every session |

## Curriculum Structure

The Clief Notes curriculum (from skool.com/cliefnotes) has these levels:

1. **Getting Started** — Navigation, leveling, community orientation
2. **The Foundation** — ICM fundamentals: 5-layer context hierarchy, stage contracts, folder structure as orchestration
3. **The Archive** — Three years of evidence validating the methodology
4. **Implementation Playbooks** — Domain-specific build guides using ICM
5. **Building Your Stack** — Custom interfaces, remote access, infrastructure
6. **The Vault** — Assets, templates, CLAUDE.md examples, workflow starters, reference docs
7. **The Drawing Room (VIP)** — Live sessions, bespoke folder/build builds

## Study Schedule

**Target:** 45 minutes per session, 3 sessions per week (Mon/Wed/Fri recommended)

| Week | Focus Area | Sessions | Material |
|------|-----------|----------|----------|
| 1 | Orientation + ICM Paper §1-2 (Introduction, Background) | 3 | Getting Started module, paper pp. 1-6 |
| 2 | ICM Paper §3.1-3.2 (Design Principles, Architecture) | 3 | Foundation module, paper pp. 6-12 |
| 3 | ICM Paper §3.3-3.4 (Stage Contracts, Portability) | 3 | Foundation module, paper pp. 12-16 |
| 4 | ICM Paper §4 (Working Implementations) | 3 | Implementation Playbooks intro |
| 5 | ICM Paper §5 (Discussion — where ICM works and doesn't) | 3 | Archive module (evidence) |
| 6 | ICM Paper §6 (Future Directions) + Review | 3 | Building Your Stack intro |
| 7 | Implementation Playbooks — hands-on workspace build | 3 | Choose a playbook, build first workspace |
| 8-10 | Building Your Stack — custom interfaces, remote access | 6-9 | Stack module, practice projects |
| Ongoing | The Vault + Drawing Room | 3/week | Templates, live sessions, community |

## Documentation Protocol

After completing any task, document what you did in the project wiki.

### When to Document
- After every study session
- After making decisions about curriculum pacing
- After discovering and resolving confusion about concepts
- After creating, modifying, or removing files

### What to Document
- **What was done** — Brief summary of the study session or task
- **Why** — Rationale for study decisions
- **What changed** — Files created/modified, progress updates
- **Lessons learned** — Key insights, connections between concepts

### Where to Document
- Write to the vault activity log: `wiki/clief/vault/Activity Log.md`
- Create study notes in the vault wiki section
- Cross-reference from related pages if the change affects multiple domains

### Format
```markdown
### YYYY-MM-DD — {Title}

**Task**: {What was studied or requested}
**Outcome**: {What was done and result}
**Rationale**: {Why this approach was chosen}
**Files changed**: {List of files created/modified}
**Lessons**: {What to remember for next time}
```

### Do Not Document
- Trivial lookups or status checks with no changes
- Orchestrator intercom messages
- Intermediate debugging steps that led nowhere

## Key References

- **ICM Paper:** `../../workshop/references/ICM-paper.pdf` (full paper)
- **ICM Source:** `../../workshop/references/ICM-paper-source.tar.gz` (LaTeX source)
- **Clief Notes Community:** https://www.skool.com/cliefnotes
- **ICM GitHub:** https://github.com/RinDig/Interpretable-Context-Methodology-ICM-

## Cross-Domain References

For tasks that span domains, consult the routing table in `./AGENTS.md` (project root).
For implementation exercises, switch to the workshop domain: `./workshop/AGENTS.md`.