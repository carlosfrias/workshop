# Workshop — Code & Implementation

This domain covers the code, implementation exercises, practice projects, and ICM workspace building. The workshop is where theory from the vault becomes practice: building ICM workspaces, writing pipeline code, implementing stages, and testing folder-structure-based orchestration.

## Conventions

- All code files use UTF-8 encoding
- Python scripts use type hints where practical
- Markdown files follow ICM conventions (CONTEXT.md, layered context)
- ICM workspace stages are numbered: `01_name/`, `02_name/`, etc.
- Stage contracts specify Inputs, Process, and Outputs
- Testing happens stage-by-stage before running full pipelines

## Rules

### Must Always
- Follow ICM conventions for workspace structure (Layers 0-4)
- Create CONTEXT.md for every stage with Inputs/Process/Outputs
- Test each stage independently before chaining
- Keep reference material (Layer 3) separate from working artifacts (Layer 4)
- Document all implementations in the wiki
- Use the 5-layer hierarchy: CLAUDE.md → CONTEXT.md → Stage CONTEXT → references → output

### Must Never
- Skip creating a stage contract (CONTEXT.md)
- Mix reference material with working artifacts in the same directory
- Hardcode configuration that should be in `_config/` or `references/`
- Commit pipeline output that should be regenerated
- Leave a stage without clear input/output specifications

## Quality Checklist

Before considering any task complete, verify:

- [ ] Each stage has a CONTEXT.md with Inputs/Process/Outputs
- [ ] Reference files (Layer 3) are in `references/` or `_config/` — not mixed with output
- [ ] Output directories are clean or gitignored
- [ ] Stage numbering is sequential and unambiguous
- [ ] Human review gates are documented at each stage boundary
- [ ] The workspace can be understood by reading CONTEXT.md files top to bottom

## Common Mistakes

| Mistake | Correct Approach |
|---------|-----------------|
| Loading all context into every stage | Use the Inputs table to scope context per stage |
| Skipping human review between stages | Build review gates into every stage boundary |
| Putting stage configuration in code | Put it in CONTEXT.md and reference files |
| Creating monolithic prompts instead of staged ones | One stage, one job — decompose further if needed |
| Forgetting to separate reference from working material | Layer 3 = stable rules (factory); Layer 4 = per-run content (product) |

## ICM Workspace Template

When creating new ICM workspaces, follow this structure:

```
workspace/
├── CLAUDE.md                    # Layer 0: Global identity (~800 tok)
├── CONTEXT.md                   # Layer 1: Workspace-level routing (~300 tok)
├── stages/
│   ├── 01_research/
│   │   ├── CONTEXT.md           # Layer 2: Stage contract (200-500 tok)
│   │   ├── references/          # Layer 3: Reference material
│   │   └── output/              # Layer 4: Working artifacts
│   ├── 02_script/
│   │   ├── CONTEXT.md
│   │   ├── references/
│   │   └── output/
│   └── 03_production/
│       ├── CONTEXT.md
│       ├── references/
│       └── output/
├── _config/                     # Layer 3: Global reference (voice, style, etc.)
├── shared/                      # Layer 3: Shared reference material
└── setup/
    └── questionnaire.md         # Workspace setup questions
```

## Documentation Protocol

After completing any task, document what you did in the project wiki.

### When to Document
- After building or modifying an ICM workspace
- After completing a practice exercise
- After discovering and resolving issues
- After creating, modifying, or removing code files

### What to Document
- **What was done** — Brief summary of the implementation or exercise
- **Why** — Rationale for design decisions
- **What changed** — Files created/modified, workspace structure updates
- **Lessons learned** — What worked, what didn't, ICM patterns discovered

### Where to Document
- Write to the workshop activity log: `wiki/clief/workshop/Activity Log.md`
- Create implementation notes in the workshop wiki section
- Cross-reference from related pages if the change affects multiple domains

### Format
```markdown
### YYYY-MM-DD — {Title}

**Task**: {What was implemented or practiced}
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

- **ICM Paper:** `./references/ICM-paper.pdf` (full paper)
- **ICM Source:** `./references/ICM-paper-source.tar.gz` (LaTeX source)
- **ICM GitHub:** https://github.com/RinDig/Interpretable-Context-Methodology-ICM-
- **Clief Notes:** https://www.skool.com/cliefnotes

## Cross-Domain References

For tasks that span domains, consult the routing table in `./AGENTS.md` (project root).
For study notes and curriculum tracking, switch to the vault domain: `./vault/AGENTS.md`.