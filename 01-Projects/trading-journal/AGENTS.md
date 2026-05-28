# AGENTS.md — Trading Journal

**Purpose:** Trading journal to capture and manage trades with live data, options support, Greeks, account-level P&L, bookkeeping integration, and Gmail notification parsing. Replaces DTI and LS spreadsheet journals.
**Workspace:** `workshop/01-Projects/trading-journal/`  
**Two Locations Mandate:** Docs in `personal-vault/`, Code in `workshop/`.

## [S-TIGHT]

Tier-routed orchestrator. Models <32K context: load linear scripts only. Models ≥32K context: read this file + domain AGENTS.md as needed.

---

## Domain Routing

| Keywords | Route To |
|----------|----------|
| trade entry, capture trade, log trade, new position, open trade, entry, stop loss, take profit, risk-reward, position size | [Trade Entry](./trade-entry/AGENTS.md) |
| trade management, adjust stop, scale in, scale out, close trade, exit, partial close, trailing stop, position monitoring | [Trade Management](./trade-management/AGENTS.md) |
| analytics, performance, metrics, win rate, expectancy, drawdown, P&L, statistics, analysis, chart, graph | [Analytics](./analytics/AGENTS.md) |
| reporting, export, summary, journal export, trade report, monthly review, weekly review, performance report | [Reporting](./reporting/AGENTS.md) |

---

## Model Configuration

| Role | Model |
|------|-------|
| Orchestrator | qwen3.5:397b-cloud |
| Reasoning | deepseek-v4-pro:cloud |
| Fast | gemma4:31b-cloud |

---

## Intercom Coordination

**Enabled:** Yes — cross-session coordination active. Use `intercom` tool for planner-worker workflows.

---

## Discovery Path

```
1. workshop/01-Projects/trading-journal/AGENTS.md  ← YOU ARE HERE
2. ./<domain>/AGENTS.md                            ← Load after routing match
3. personal-vault/01-Projects/trading-journal/FOCUS.md ← Current state
```

---

*Last updated: 2026-05-27*
