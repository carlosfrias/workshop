# Wiki Separation Plan

Migrating from a single monolithic wiki to a wiki-per-workspace model.

## Current State (Problem)

```
trading-workspace/wiki/
├── model-assignment-strategy.md      ← Technical infra concern
├── decompose-execute-verify-pattern.md ← Technical infra concern
├── trading-desk/
│   ├── 00 — Home.md
│   ├── ...
│   └── 09 — Known Limitations & Backlog.md
└── (mixed trading + infra content)
```

**Problems:**
- Hard to navigate — trading concerns mixed with infra concerns
- Unclear ownership — who maintains what?
- Duplicated content — same info appears in multiple places
- Search noise — finding trading docs requires wading through infra docs

## Target State (Solution)

```
technical-infrastructure/wiki/
├── README.md                         ← Navigation hub
├── publishing-workflow.md            ← How to publish extensions/skills
├── pi-keyword-router/                ← Extension documentation
│   ├── README.md
│   ├── development.md
│   └── changelog.md
├── project-blueprint/                ← Skill documentation
│   ├── README.md
│   └── usage.md
├── trading-agents/                   ← Agent package documentation
│   ├── README.md
│   ├── decomposer.md
│   └── verifier.md
└── wiki-separation-plan.md           ← This document

trading-workspace/wiki/
├── README.md                         ← Navigation hub
├── model-assignment-strategy.md      ← Trading-specific model usage
├── decompose-execute-verify-pattern.md ← How to use in trading context
├── bookkeeping/                      ← Domain-specific guides
│   └── usage.md
├── position-management/
│   └── usage.md
└── market-research/
    └── usage.md

project-blueprint/wiki/
├── README.md
├── getting-started.md
└── examples/
```

## Ownership Model

| Workspace | Owns | Consumes |
|-----------|------|----------|
| `technical-infrastructure` | Extension docs, skill docs, publishing workflow | — |
| `trading-workspace` | Trading usage guides, domain guides, model assignments | `pi-keyword-router`, `project-blueprint`, `trading-agents` |
| `project-blueprint` | Skill usage examples, project setup guides | `project-blueprint` skill |

## Migration Strategy

### Phase 1: Create Structure (Do Now)

1. **Create wiki directories in each workspace**
   ```bash
   mkdir -p technical-infrastructure/wiki/{pi-keyword-router,project-blueprint,trading-agents}
   mkdir -p trading-workspace/wiki/{bookkeeping,position-management,market-research}
   mkdir -p project-blueprint/wiki/examples
   ```

2. **Create README.md in each wiki** — Navigation hub with links to all pages

3. **Move technical content to technical-infrastructure**
   - `pi-keyword-router` extension docs
   - `project-blueprint` skill docs
   - `decompose-execute-verify-pattern.md` (core architecture)
   - `publishing-workflow.md`

4. **Move trading content to trading-workspace**
   - `model-assignment-strategy.md` (trading-specific usage)
   - Domain-specific guides (bookkeeping, position-management, market-research)

5. **Update cross-references** — Links from one wiki to another use relative paths or GitHub URLs

### Phase 2: Interactive Wiki (Future)

Build an HTML wiki with better navigation using VitePress or similar:

```
technical-infrastructure/
└── wiki-build/              ← VitePress site
    ├── package.json
    ├── .vitepress/config.js
    └── docs/               ← Source markdown (symlinked from wiki/)
```

Features:
- **Sidebar navigation** — Grouped by package/topic
- **Search** — Algolia DocSearch or similar
- **Version picker** — For published packages
- **Next/Prev navigation** — Sequential reading
- **Edit on GitHub** — Direct link to source

### Phase 3: Automated Sync (Future)

When a package is published, auto-update its wiki:

```yaml
# GitHub Actions workflow
on:
  release:
    types: [published]
jobs:
  update-wiki:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Update changelog
        run: |
          echo "# ${{ github.event.release.tag_name }}" >> wiki/${{ github.event.repository.name }}/changelog.md
          echo "${{ github.event.release.body }}" >> wiki/${{ github.event.repository.name }}/changelog.md
      - name: Commit and push
        run: |
          git add wiki/
          git commit -m "Update changelog for ${{ github.event.release.tag_name }}"
          git push
```

## Content Guidelines

### What Goes in Technical Infrastructure Wiki

- Extension documentation (how it works, how to develop)
- Skill documentation (how it works, how to extend)
- Agent package documentation
- Publishing workflow
- Architecture decisions
- API references

### What Goes in Trading Workspace Wiki

- How to use extensions for trading tasks
- Model assignment strategy (trading context)
- Domain-specific guides (bookkeeping, position management, market research)
- Trading workflows and pipelines
- Lessons learned from trading operations

### What Goes in Project Blueprint Wiki

- Skill usage examples
- Project setup walkthroughs
- Template customization
- Common patterns and anti-patterns

## Linking Between Wikis

Use GitHub URLs for cross-workspace references:

```markdown
## See Also

- [pi-keyword-router Documentation](https://github.com/carlosfrias/pi-keyword-router/blob/main/README.md)
- [Project Blueprint Skill](https://github.com/carlosfrias/project-blueprint/blob/main/skills/project-blueprint/README.md)
- [Technical Infrastructure Wiki](https://github.com/carlosfrias/trading-workspace/tree/main/technical-infrastructure/wiki)
```

For local development, use relative paths within the same workspace:

```markdown
## See Also

- [Publishing Workflow](../../guides/publishing-workflow.md)
- [Model Assignment Strategy](./model-assignment-strategy.md)
```

## Implementation Checklist

- [ ] Create `technical-infrastructure/wiki/` structure
- [ ] Create `trading-workspace/wiki/` structure (reorganize existing)
- [ ] Create `project-blueprint/wiki/` structure
- [ ] Move `pi-keyword-router` docs to `technical-infrastructure/wiki/`
- [ ] Move `project-blueprint` skill docs to `technical-infrastructure/wiki/`
- [ ] Move `decompose-execute-verify-pattern.md` to `technical-infrastructure/wiki/`
- [ ] Keep `model-assignment-strategy.md` in `trading-workspace/wiki/` (trading-specific)
- [ ] Create README.md navigation hubs in each wiki
- [ ] Update all cross-references
- [ ] Test all links
- [ ] Document the new structure in each wiki's README
