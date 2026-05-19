# Workflow Orchestration Research

Research project evaluating Obsidian-based options for managing personal workload as projects. The goal is to determine the best approach for durable project and task management within an Obsidian workspace in a single-user lab environment.

## Conventions

- All timestamps in US Eastern / America/New_York
- All date formats: YYYY-MM-DD
- Keep outputs concise and actionable
- Evaluation criteria must be explicitly scored, not just described
- All alternatives must use Obsidian as the workspace foundation
- When in doubt, ask — do not assume

## Domain Routing

When the task involves one of these domains, read the corresponding file before proceeding.
That file contains all context, conventions, rules, and quality checks for the domain.

| Keywords | Read this file |
|----------|---------------|
| research, investigate, explore, compare, plugin, Obsidian, capabilities, features, SDK, API | `./research/AGENTS.md` |
| evaluate, score, rank, recommend, decision, conclusion, verdict, criteria, matrix | `./evaluation/AGENTS.md` |
| wiki, documentation, notes, findings, write-up, summary, report | `./wiki/AGENTS.md` |

After reading the domain file, follow its instructions for the task.

**Domain Ambiguity Rule:** When the user's intent doesn't clearly match a single domain — either no keywords match, or keywords match multiple domains — do NOT guess. Instead:
1. Tell the user which domains their request could map to
2. Suggest the explicit form: "Switch to {domain-name}"
3. Wait for confirmation before loading any domain context

## Project Map

| Keywords | Route To |
|----------|----------|
| research, investigate, explore, compare, plugin, Obsidian, capabilities, features, SDK, API | `./research/AGENTS.md` |
| evaluate, score, rank, recommend, decision, conclusion, verdict, criteria, matrix | `./evaluation/AGENTS.md` |
| wiki, documentation, notes, findings, write-up, summary, report | `./wiki/AGENTS.md` |