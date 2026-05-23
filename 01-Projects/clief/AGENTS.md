# Clief Notes

An online classroom for the study of AI use, built on the Interpretable Context Methodology (ICM) by Jake Van Clief. This project tracks curriculum study, practice exercises, code implementations, and personal notes from the Clief Notes community (skool.com/cliefnotes).

## Conventions

- All timestamps in US Eastern (America/New_York)
- All date formats: YYYY-MM-DD
- Study schedule: 45 minutes per session, 3 sessions per week
- Keep outputs concise and actionable
- When in doubt, ask — do not assume
- ICM = Interpretable Context Methodology (folder structure as agent architecture)
- 5-layer context hierarchy: CLAUDE.md → CONTEXT.md → Stage CONTEXT → Reference material → Working artifacts

## Domain Routing

When the task involves one of these domains, read the corresponding file before proceeding.
That file contains all context, conventions, rules, and quality checks for the domain.

| Keywords | Read this file |
|----------|---------------|
| study, notes, curriculum, schedule, learning, research, reading, vault, ICM concepts | `./vault/AGENTS.md` |
| code, implementation, exercise, practice, project, build, workshop, pipeline, workspace | `./workshop/AGENTS.md` |
| wiki, documentation, research, analysis | `./wiki/AGENTS.md` |

After reading the domain file, follow its instructions for the task.

**Domain Ambiguity Rule:** When the user's intent doesn't clearly match a single domain — either no keywords match, or keywords match multiple domains — do NOT guess. Instead:
1. Tell the user which domains their request could map to
2. Suggest the explicit form: "Switch to {domain-name}"
3. Wait for confirmation before loading any domain context