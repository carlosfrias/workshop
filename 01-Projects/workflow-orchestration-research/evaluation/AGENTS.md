# Evaluation

Score, rank, and recommend Obsidian-based options for managing personal workload as projects. This domain consumes research output and produces decision artifacts.

## Conventions

- All evaluations use a consistent scoring rubric (see below)
- Scores are 1-5 (1=poor fit, 5=excellent fit) with explicit justification
- Weighted totals are calculated with weights disclosed upfront
- Recommendations include a "when to choose this" and "when NOT to choose this" section
- All outputs should be decisive, evidence-backed, and actionable
- **All deliverables must use Mermaid diagrams** for evaluation matrices, comparison charts, architecture visualizations, and recommendations. No ASCII art diagrams.

## Evaluation Dimensions

Every option is scored on these dimensions:

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Obsidian integration depth | 20% | How deeply does it leverage Obsidian workspace (frontmatter, links, embeds, vault structure)? |
| Project management capability | 20% | Can it track projects, tasks, status, dependencies, priorities? Hub-and-spoke dashboard? Collision detection? Good-enough statuses? |
| Data portability | 15% | If the plugin/tool disappears, is data still accessible and useful in plain markdown? |
| Automation &amp; execution | 15% | Can it trigger actions, schedule tasks, run workflows? |
| pi orchestration integration | 10% | Can pi agents read/write to it? Can it trigger pi workflows? Project context alignment? |
| Cost (time + tokens) | 10% | Time to set up, learn, maintain. Token expenditure per session on hybrid local/cloud stack. Local vs cloud model requirements. |
| Maintenance risk | 5% | Is it actively maintained? Community size? Risk of abandonment? |
| Setup simplicity | 5% | How easy to install, configure, and start using? |

## Rules

### Must Always
- Score every dimension for every option — no blank scores
- Justify every score with evidence from research briefs
- Weight scores explicitly and disclose weights
- Produce a final recommendation with "best overall" and "best for specific scenarios"
- Consider hybrid approaches (e.g., Tasks plugin + Obsidian CLI + pi orchestration)
- **Use Mermaid diagrams** for all visual content: evaluation matrices, radar charts, comparison flows, architecture layers

### Must Never
- Let personal preference override evidence
- Score without citing the research brief that justifies the score
- Recommend a discontinued plugin without flagging the risk
- Produce an evaluation without a final recommendation

## Quality Checklist

Before considering any evaluation task complete, verify:

- [ ] Every option has scores on all 8 dimensions
- [ ] Every score has a citation to a research brief or source
- [ ] Weights are disclosed and summed to 100%
- [ ] Final recommendation includes "best overall" and scenario-specific alternatives
- [ ] Data portability risk is explicitly assessed for each option
- [ ] The wiki has a complete evaluation matrix page

## Common Mistakes

| Mistake | Correct Approach |
|---------|-----------------|
| Scoring all plugins equally on "automation" without distinguishing | Tasks plugin has zero automation; Obsidian CLI has full automation — reflect this in scores |
| Ignoring maintenance risk for popular plugins | Obsidian Projects was popular but is now discontinued — always check current status |
| Recommending the most feature-rich plugin | In a single-user lab, simplicity and data portability often beat features |

## Documentation Protocol

After completing any task, document what you did in the project wiki.

### Where to Document
- Write to your domain's activity log: `../../../personal-vault/01-Projects/workflow-orchestration-research/wiki/workflow-orchestration-research/evaluation/Activity Log.md`
- If the entry relates to a significant topic, create a new page in `../../../personal-vault/01-Projects/workflow-orchestration-research/wiki/workflow-orchestration-research/evaluation/` with a descriptive name

**Documentation lives in the vault.** All wiki content paths resolve to `personal-vault/01-Projects/workflow-orchestration-research/wiki/`. The workshop wiki directory contains only the AGENTS.md router and VitePress build config.

## Cross-Domain References

For tasks that span domains, consult the routing table in `./AGENTS.md` (project root).