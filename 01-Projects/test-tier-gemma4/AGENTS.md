# test-tier-gemma4 — Threshold Evidence Research Project

## Identity & Purpose

You are orchestrating threshold evidence research for the **test-tier-gemma4** project.

**Description:** Validates gemma4:e4b (9.6 GB, 131K context) as the high-tier local model in model-router.json for decompose-execute-verify orchestrated workloads on M1 Pro / 16 GB.

**Primary Use Cases:**
- Model threshold validation
- DE framework stability testing
- Subagent memory pressure analysis
- Config calibration (maxTokens, thinking levels)

## Conventions

- **Timestamps:** ISO 8601 (`2026-05-22T10:30:00Z`)
- **Date Formats:** `YYYY-MM-DD`
- **Evidence Thresholds:** Minimum 3 independent sources for Level 1 evidence
- **Output Style:** Precise, evidence-cited, no hedging

## Domain Routing

| Keywords | Read this file |
|----------|---------------|
| validate, verification, quality, evidence, threshold, check, audit, assess | `./domain-validation/AGENTS.md` |
| results, analysis, compile, report, outcome, summary, findings | `./domain-results/AGENTS.md` |
| wiki, documentation, research, analysis, meta | `./wiki/test-tier-gemma4/AGENTS.md` |

## [S-TIGHT] Operational Rules

1. **Never improvise** — Follow templates exactly. No deviations.
2. **Self-contained domains** — Each domain AGENTS.md contains all context.
3. **inheritProjectContext: false** — Sub-agents discover context independently.
4. **Relative paths only** — All paths relative to project root.
5. **Health-gate all model tests** — Check health-monitor before any model execution. Halt if critical.

## Discovery Order

1. `./AGENTS.md` — This file (routing)
2. `./FOCUS.md` — Current state, handoff
3. `./PLAN.md` — Test plan, phases
4. `./domain-validation/AGENTS.md` — Validation domain
5. `./domain-results/AGENTS.md` — Results domain

---

*Last updated: 2026-05-22*
