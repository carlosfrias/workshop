# Carlos' Desktop — Root Context

**Updated:** 2026-05-14

---

## What Is This?

Carlos' Desktop is an AI-orchestrated workspace built on the `pi` coding agent harness, with a **trading-desk domain** at its center. It delegates all work to domain sub-agents rather than doing tasks directly.

---

## Quick Navigation

| Domain | Agent File | Purpose |
|--------|-----------|---------|
| Trading | `./position-management/AGENTS.md` | Position sizing, orders, risk |
| Research | `./market-research/AGENTS.md` | Backtesting, signals, data |
| Books | `./bookkeeping/AGENTS.md` | P&L, reconciliation, balances |
| Infrastructure | `./technical-infrastructure/AGENTS.md` | Servers, APIs, deployment |
| Wiki | `./wiki/AGENTS.md` | Documentation, planning |

---

## How to Route Tasks

1. **Domain detection** — Keywords trigger domain agent loading (see AGENTS.md routing table)
2. **Phase loading** — Only the relevant phase file loads (Phase 1–5)
3. **Skill loading** — Auto-load doc-standards for any `.md` work
4. **Lab delegation** — Route to cheapest capable model

---

## Doc-Standards Skill

All markdown documentation follows the [doc-standards](../../technical-infrastructure/packages/doc-standards/skills/doc-standards/SKILL.md) framework:
- Issue-centric homes in `wiki/operational/issues/`
- Backlog index at `wiki/operational/BACKLOG.md`
- No orphan files — every issue links back

---

## Current Projects

See [wiki/operational/BACKLOG.md](../../technical-infrastructure/wiki/operational/BACKLOG.md) for the full prioritized backlog.

---

*Phase files: `.pi/agents/phases/phase-{1-5}-{name}.md`
Meta instructions: `AGENTS.md`*
