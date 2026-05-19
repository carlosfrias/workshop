---
name: research-evaluate
description: Research all Obsidian-based alternatives then evaluate and recommend — full pipeline from investigation to decision. Based on unified prompt v6.
steps:
  - agent: research
    task: |
      Research the following Obsidian-based alternatives for managing personal workload as projects in a single-user macOS lab where Obsidian is the daily workspace.

      BEFORE STARTING: Read the authoritative prompt at ../../../personal-vault/01-Projects/workflow-orchestration-research/threads/workflow-orchestration-research/prompts/016-unified-prompt-v6.md — it contains the full strategic context, user profile, existing workflow, gap analysis, and requirements.

      For each alternative, produce a structured research brief covering: overview, core capabilities, data model (how it stores data in the vault), plugin/tool status and maintenance, known limitations, integration with the existing Tasks + Templater + Daily/Weekly workflow, support for custom statuses like "good enough" and "deferred", ability to surface cross-project task collisions, integration with pi orchestration, data portability (what survives if the tool disappears), and cost assessment (time to set up and learn, time to maintain per week, token expenditure on the hybrid local/cloud stack, whether routine use runs on local models or requires cloud tokens).

      Alternatives to research:
      1. Obsidian Tasks plugin — task tracking with queries, due dates, recurring tasks (EXISTING BACKBONE)
      2. Obsidian Projects plugin — project visualization (DISCONTINUED May 2025, evaluate risk)
      3. Obsidian + Dataview — dynamic queries and computed views from vault data
      4. Obsidian CLI + cron/launchd — scheduled automation reading/writing the vault externally
      5. pi orchestration → Obsidian — AI-driven vault management via Obsidian CLI and direct file operations
      6. Obsidian Bases (.base files) — native Obsidian database views
      7. Hybrid: Tasks + CLI + pi — combined approach using each layer for what it does best

      CRITICAL: Flag any discontinued or unmaintained tools explicitly. Check last commit dates, open issues, and maintainer activity.

      CRITICAL: All deliverables must use Mermaid diagrams for architecture, data flow, workflow, and comparison visuals. No ASCII art. Mermaid renders natively in Obsidian.

      CRITICAL: Do NOT put triple backticks (```) inside Mermaid node labels — this breaks the Mermaid block. Use curly braces like {dataview} or plain text descriptions instead.

      Write each brief as a wiki page under ../../../personal-vault/01-Projects/workflow-orchestration-research/wiki/workflow-orchestration-research/research/

      Context: The user manages their personal workload in an Obsidian vault (personal-vault/) with existing project structure (AGENTS.md routing, FOCUS.md, WORKBENCH.md, threads). The vault follows the project-blueprint pattern. pi agents already exist and can read/write files. The goal is to find the best Obsidian-based approach for project-level workload management.
    cwd: ./research
  - agent: evaluation
    task: |
      Based on the research briefs in ../../../personal-vault/01-Projects/workflow-orchestration-research/wiki/workflow-orchestration-research/research/, produce ALL evaluation deliverables.

      BEFORE STARTING: Read the authoritative prompt at ../../../personal-vault/01-Projects/workflow-orchestration-research/threads/workflow-orchestration-research/prompts/016-unified-prompt-v6.md and the vault-side evaluation AGENTS.md at ../../../personal-vault/01-Projects/workflow-orchestration-research/evaluation/AGENTS.md — they contain the full evaluation framework, scoring rubric, deliverable specifications, and quality checklist.

      Score each alternative on these 8 dimensions (weights shown):

      | Dimension | Weight |
      |-----------|--------|
      | Obsidian integration depth | 20% |
      | Project management capability | 20% |
      | Data portability | 15% |
      | Automation & execution | 15% |
      | pi orchestration integration | 10% |
      | Cost (time + tokens) | 10% |
      | Maintenance risk | 5% |
      | Setup simplicity | 5% |

      Scores are 1-5 with explicit justification citing research briefs. Include "what would change this score" for every cell. Calculate weighted totals.

      Produce these deliverables:

      1. **Evaluation Matrix** (write to: wiki/.../evaluation/01-evaluation-matrix.md)
         - Raw scores table, weighted scores table, Mermaid bar chart, justification with citations

      2. **Recommendation** (write to: wiki/.../evaluation/02-recommendation.md)
         - Ranked comparison, "best overall", scenario-specific recommendations, "when NOT to choose each", Mermaid architecture diagrams

      3. **Migration Assessment** (write to: wiki/.../evaluation/03-migration-assessment.md)
         - Current → target state, preservation analysis, custom status definitions, template changes, frontmatter enrichment, launchd specs, pi agent specs, phased rollout (Mermaid Gantt), rollback plan

      4. **Pi Integration Scoping** (write to: wiki/.../evaluation/04-pi-integration-scoping.md)
         - Integration model spectrum (Mermaid), 5 options with feasibility/effort, minimum viable steps, cost comparison, recommendation

      CRITICAL: Pay special attention to DATA PORTABILITY — plugin abandonment is a real risk.
      CRITICAL: Pay special attention to COST — the user runs a hybrid local/cloud stack. Routine use on local models scores higher.
      CRITICAL: All deliverables must use Mermaid diagrams. No ASCII art.
      CRITICAL: Do NOT put triple backticks inside Mermaid node labels.

      All paths resolve relative to ../../../personal-vault/01-Projects/workflow-orchestration-research/wiki/workflow-orchestration-research/.
    cwd: ./evaluation
---