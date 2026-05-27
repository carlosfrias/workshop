# {project_name}

{project_description}

## Conventions

- All timestamps in {timezone} (default: US Eastern / America/New_York)
- All date formats: YYYY-MM-DD
- Keep outputs concise and actionable
- When in doubt, ask — do not assume

## Domain Routing

When the task involves one of these domains, read the corresponding file before proceeding.
That file contains all context, conventions, rules, and quality checks for the domain.

| Keywords | Read this file |
|----------|---------------|
| {domain1_keywords} | [{domain1}](./{domain1}/AGENTS.md) |
| {domain2_keywords} | [{domain2}](./{domain2}/AGENTS.md) |
| wiki, documentation, research, analysis | [Wiki](./wiki/AGENTS.md) |

After reading the domain file, follow its instructions for the task.

**Domain Ambiguity Rule:** When the user's intent doesn't clearly match a single domain — either no keywords match, or keywords match multiple domains — do NOT guess. Instead:
1. Tell the user which domains their request could map to
2. Suggest the explicit form: "Switch to {domain-name}"
3. Wait for confirmation before loading any domain context