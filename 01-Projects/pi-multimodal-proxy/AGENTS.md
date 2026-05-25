# pi-multimodal-proxy

AI-powered proxy for multimodal operations (vision, audio, document processing). Routes requests to appropriate vision/audio agents and manages token budgets for cost-efficient processing.

## Conventions

- All timestamps in US Eastern (America/New_York)
- All date formats: YYYY-MM-DD
- Keep outputs concise and actionable
- When in doubt, ask — do not assume
- Token budgets enforced per request (see Quality Checklist)

## Domain Routing

When the task involves one of these domains, read the corresponding file before proceeding.
That file contains all context, conventions, rules, and quality checks for the domain.

| Keywords | Read this file |
|----------|---------------|
| vision, image, screenshot, OCR, visual analysis, diagram, chart, photo | `./vision-agent/AGENTS.md` |
| wiki, documentation, research, analysis | `./wiki/AGENTS.md` |

After reading the domain file, follow its instructions for the task.

**Domain Ambiguity Rule:** When the user's intent doesn't clearly match a single domain — either no keywords match, or keywords match multiple domains — do NOT guess. Instead:
1. Tell the user which domains their request could map to
2. Suggest the explicit form: "Switch to {domain-name}"
3. Wait for confirmation before loading any domain context

## Token Budget Conventions

| Operation | Budget | Enforcement |
|-----------|--------|-------------|
| Vision analysis (single image) | <2KB input + <4KB output | Summarize, don't transcribe verbatim |
| Multi-image comparison | <4KB input + <6KB output | Focus on differences, not repetition |
| OCR extraction | <3KB input + <5KB output | Structured output only |
| Complex visual reasoning | <6KB total | Use decompose-execute-verify if exceeded |

**Rules:**
- Always count tokens before and after processing
- If budget exceeded, summarize or chunk the task
- Log token usage in wiki Activity Log for cost tracking

## Quality Checklist

Before delivering any vision-agent result:

- [ ] Token budget respected (see table above)
- [ ] Output structured and actionable (not verbose prose)
- [ ] All user questions answered explicitly
- [ ] Uncertainties flagged (e.g., "low confidence on text region")
- [ ] Wiki Activity Log updated with task summary
- [ ] Intercom check-back triggered if decisions needed

---

*Last updated: 2026-05-24*
