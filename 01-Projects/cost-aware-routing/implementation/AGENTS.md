# Implementation Domain — Cost-Aware Routing (Workshop)

Implementation domain context for the code workspace.

## [S-TIGHT]

Implementation domain. Cost calculation, billing scripts, configs.
All Python code and JSON configs live here.

## Key Files

| File | Purpose |
|------|---------|
| `../scripts/cost_calculator.py` | Per-node hourly cost, per-model cost per 1K tokens, scoring |
| `../scripts/cost_logger.py` | JSONL cost event logging |
| `../scripts/billing_engine.py` | Invoice generation (stub) |
| `../scripts/usage_tracker.py` | Customer usage tracking (stub) |
| `../config/billing_tiers.json` | Billing tier definitions (single source of truth) |
| `../config/cost_defaults.json` | Hardware/power cost defaults |
| `../tests/test_cost_calculator.py` | Unit tests for cost functions |
| `../tests/test_cost_logger.py` | Unit tests for logger |
| `../tests/test_billing_tiers.py` | Billing tier validation |

## Conventions

- Python 3.10+, type hints required
- Config in JSON files (`../config/`), never hardcoded
- Cost functions are pure (no side effects, testable)
- JSONL append-only logging for audit trail
- CLI interface on all scripts (argparse)

## Must Always

- Load billing tiers from `../config/billing_tiers.json`
- Validate input before cost calculation (tokens > 0, hourly_cost > 0)
- Write tests for every cost function
- Update `billing_tiers.json` when tiers change (never hardcode)

## Must Never

- Hardcode COST_TABLE in Python
- Store documentation in this workspace

## Cross-Reference

Documentation: `../../personal-vault/01-Projects/cost-aware-routing/implementation/AGENTS.md`