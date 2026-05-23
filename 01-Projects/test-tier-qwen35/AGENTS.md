# test-tier-qwen35 — Threshold Evidence Research Project

## Identity & Purpose

You are orchestrating threshold evidence research for the **test-tier-qwen35** project.

**Description:** This project validates and curates evidence at threshold levels using Qwen3.5 models for automated data processing and analysis across validation and results domains.

**Primary Use Cases:**
- Automated evidence threshold validation
- Data quality verification
- Automated result compilation
- Cross-domain evidence synthesis

## Conventions

- **Timestamps:** ISO 8601 (`2026-05-22T10:30:00Z`)
- **Currencies:** USD (formatted as `$1,234.56`)
- **Date Formats:** `YYYY-MM-DD` (vault side), `YYYY-MM-DD[TechTime]` (workshop side)
- **Evidence Thresholds:** Minimum 3 independent sources for Level 1 evidence
- **Output Style:** Precise, evidence-cited, no hedging

## Domain Routing

When the task involves one of these domains, read the corresponding file before proceeding.
That file contains all context, conventions, rules, and quality checks for the domain.

| Keywords | Read this file |
|------|---------|
| validate, verification, quality, evidence, threshold, check, audit, assess | `./domain-validation/AGENTS.md` |
| results, analysis, compile, report, outcome, summary, findings | `./domain-results/AGENTS.md` |
| wiki, documentation, research, analysis, meta | `./wiki/test-tier-qwen35/AGENTS.md` |

After reading the domain file, follow its instructions for the task.

---

## [S-TIGHT] Operational Rules

1. **Never improvise** — Follow templates exactly. No deviations, no improvisation.
2. **Self-contained domains** — Each domain `AGENTS.md` contains all context; no supplementary files.
3. **inheritProjectContext: false** — Sub-agents discover context independently via cwd walk.
4. **Relative paths only** — All file paths must be relative to the project root.
5. **Two-Locations Mandate** — Docs belong in `personal-vault/`, code and agents belong in `workshop/`.

---

## Discovery Order (Vault Side)

When discovering the project structure, follow this order:

1. `./WORKBENCH.md` — Human workspace, current thinking, work-in-progress
2. `./AGENTS.md` — Domain routing table, operational rules
3. `./FOCUS.md` — Session handoff, active work, next steps
4. `./README.md` — Project overview
5. `./threads/*` — Prompt captures, prompt threads

---

## Discovery Order (Workshop Side)

When discovering the project structure, follow this order:

1. `./AGENTS.md` — Root routing file
2. `./domain-validation/AGENTS.md` — Validation domain context
3. `./domain-results/AGENTS.md` — Results domain context
4. `./wiki/test-tier-qwen35/` — Documentation wiki
5. `./agents/` — Agent definitions (if any)

---

## Post-Completion Protocol

After session completion, follow the post-completion protocol:
1. Update `journal/YYYY-MM-DD-HHMM.md` with session summary
2. Update `./FOCUS.md` active work and handoff notes
3. Update `./PLAN.md` phase progress and next steps
4. Record AI cost usage in the journal entry

---

*Last updated: 2026-05-22*
