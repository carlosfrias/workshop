# Cost-Aware Routing + Billing (Workshop)

Code and execution workspace for cost-aware routing and billing.

## [S-TIGHT]

Workshop execution side of cost-aware routing. Scripts, configs, tests,
and agent definitions. All documentation lives in personal-vault.

## Tech Stack

| Component | Technology | Entry Point |
|-----------|-----------|-------------|
| Cost calculator | Python | scripts/cost_calculator.py |
| Cost logger | Python | scripts/cost_logger.py |
| Session cost report | Python | scripts/session_cost_report.py |
| Cost dashboard | Python → HTML | scripts/cost_dashboard.py |
| Billing engine | Python (future) | scripts/billing_engine.py |
| Usage tracker | Python (future) | scripts/usage_tracker.py |
| Billing tiers | JSON config | config/billing_tiers.json |
| Cost defaults | JSON config | config/cost_defaults.json |
| Cost audit log | JSONL | data/cost-audit-log.jsonl |
| Cost dashboard | HTML | data/cost-dashboard.html |
| Pi cost-tracker | TypeScript extension | ~/.pi/agent/extensions/cost-tracker/ |
| Tests | pytest | tests/ |

## Domain Routing

When the task involves one of these domains, read the corresponding file before proceeding.

| Keywords | Read this file |
|----------|---------------|
| analyze, benchmark, research, compare, margin, tier | `./analysis/AGENTS.md` |
| implement, code, script, build, cost calculator, billing, logger | `./implementation/AGENTS.md` |
| document, guide, explain, architecture | `./documentation/AGENTS.md` |

## Entry Points

| Task | Command |
|------|---------|
| Calculate costs | `python scripts/cost_calculator.py --dump` |
| Log cost event | `python scripts/cost_logger.py --task-id "T001" --model "qwen3:8b" --tokens-input 500` |
| Session cost report | `python scripts/session_cost_report.py` |
| Export costs to audit log | `python scripts/session_cost_report.py --export` |
| Show audit log totals | `python scripts/session_cost_report.py --totals` |
| Generate dashboard | `python scripts/cost_dashboard.py` |
| Dashboard (no open) | `python scripts/cost_dashboard.py --no-open` |
| Run tests | `pytest tests/` |
| Validate billing tiers | `python scripts/cost_calculator.py --validate-tiers` |
| Cost status (in pi) | `/cost-status` |
| Cost export (in pi) | `/cost-export` |

## Conventions

- Python 3.10+, type hints required
- Config in JSON, never hardcoded
- Tests cover cost calculation edge cases (zero tokens, zero cost, overflow)
- Logging to JSONL for audit trail

## Must Never

- Commit .env files or API keys
- Store documentation here (docs live in personal-vault)
- Hardcode billing tiers (use `config/billing_tiers.json`)

## Cross-Reference

| Need | Go Here |
|------|--------|
| Issue definition, acceptance criteria | `../../personal-vault/01-Projects/cost-aware-routing/README.md` |
| Current state, priorities | `../../personal-vault/01-Projects/cost-aware-routing/FOCUS.md` |
| Prompt history | `../../personal-vault/01-Projects/cost-aware-routing/threads/cost-aware-routing/0-THREAD.md` |
| Session notes | `../../personal-vault/01-Projects/cost-aware-routing/journal/` |