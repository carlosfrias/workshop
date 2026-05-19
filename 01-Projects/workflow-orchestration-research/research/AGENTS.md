# Research

Investigate and analyze Obsidian-based options for managing personal workload as projects. This domain produces research briefs on Obsidian plugins, workflows, CLI capabilities, and integration patterns.

## Conventions

- Every option investigated gets a structured research brief (see Quality Checklist)
- Research briefs are stored in the vault wiki under `research/` pages
- All comparisons must use the same evaluation dimensions so they're directly comparable
- Cite sources: plugin repos, Obsidian docs, version numbers, API references
- Distinguish between plugin capabilities and Obsidian core capabilities
- All outputs should be structured, evidence-backed, and citation-rich
- **All deliverables must use Mermaid diagrams** to visualize architectures, workflows, data flows, and comparisons. No ASCII art diagrams.

## Rules

### Must Always
- Verify claims against plugin documentation, source code, and Obsidian API docs
- Note plugin status: actively maintained, discontinued, beta, etc.
- Flag limitations, gotchas, and hidden costs explicitly
- Check plugin compatibility: does it work with current Obsidian version?
- Assess whether the option leverages Obsidian workspace features (frontmatter, links, embeds, etc.)
- Evaluate data portability: if the plugin disappears, is your data still useful?
- **Use Mermaid diagrams** for all visual content: architecture, data flow, workflow, comparisons, layering

### Must Never
- Make claims without citing sources
- Recommend discontinued or unmaintained plugins without flagging risk
- Confuse plugin features with Obsidian core features
- Ignore data lock-in risks (plugin-specific formats, hidden config)
- Assume plugins are stable just because they're in the community list
- **Use ASCII art diagrams** — always use Mermaid instead

## Quality Checklist

Before considering any research task complete, verify:

- [ ] Research brief covers: overview, core capabilities, data model, plugin status/maintenance, known limitations, integration with pi orchestration, data portability
- [ ] Claims are backed by citations (plugin repos, Obsidian docs, version numbers)
- [ ] Evaluation dimensions are consistent with other briefs for direct comparison
- [ ] Limitations and gotchas are explicitly called out
- [ ] Assessment considers what happens if the plugin is abandoned
- [ ] Brief is written in the vault wiki under `research/` with a clear page title

## Common Mistakes

| Mistake | Correct Approach |
|---------|-----------------|
| Assuming Obsidian Projects plugin is active | It was discontinued May 2025 — flag this explicitly |
| Confusing Obsidian core features with plugin features | Clearly distinguish "Obsidian core" vs "requires plugin X" |
| Ignoring data lock-in | If a plugin stores data in a plugin-specific format, you lose it when the plugin dies |
| Treating all plugin ecosystems as equal | Obsidian plugins are community-maintained; always check last commit date and open issues |
| Recommending a plugin without testing compatibility | Check Obsidian version compatibility and plugin status before recommending |

## Documentation Protocol

After completing any task, document what you did in the project wiki.

### Where to Document
- Write to your domain's activity log: `../../../personal-vault/01-Projects/workflow-orchestration-research/wiki/workflow-orchestration-research/research/Activity Log.md`
- If the entry relates to a significant topic, create a new page in `../../../personal-vault/01-Projects/workflow-orchestration-research/wiki/workflow-orchestration-research/research/` with a descriptive name
- Cross-reference from related pages if the change affects multiple domains
- Project-level reference pages live in `../../../personal-vault/01-Projects/workflow-orchestration-research/wiki/workflow-orchestration-research/_meta/` — do not add domain-specific content there

**Documentation lives in the vault.** All wiki content paths resolve to `personal-vault/01-Projects/workflow-orchestration-research/wiki/`. The workshop wiki directory contains only the AGENTS.md router and VitePress build config.

## Cross-Domain References

For tasks that span domains, consult the routing table in `./AGENTS.md` (project root).