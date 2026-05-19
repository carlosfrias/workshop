# Cost-Aware Routing (Workshop)

Code workspace for cost-aware routing and billing.

## Quick Start

```bash
# Calculate node costs
python scripts/cost_calculator.py --dump

# Log a cost event
python scripts/cost_logger.py --task-id "T001" --model "qwen3:8b" --tokens-input 500 --tokens-output 200

# Run tests
pytest tests/
```

## Documentation

All documentation lives in: `../../personal-vault/01-Projects/cost-aware-routing/`

## Project Structure

```
cost-aware-routing/
├── scripts/
│   ├── cost_calculator.py      # Per-node hourly cost, per-model cost per 1K tokens
│   ├── cost_logger.py           # JSONL cost event logging
│   ├── billing_engine.py        # Invoice generation (stub)
│   └── usage_tracker.py         # Customer usage tracking (stub)
├── config/
│   ├── billing_tiers.json       # Billing tier definitions (single source of truth)
│   └── cost_defaults.json       # Hardware/power cost defaults
├── tests/
│   ├── test_cost_calculator.py  # Unit tests for cost functions
│   ├── test_cost_logger.py      # Unit tests for logger
│   └── test_billing_tiers.py    # Billing tier validation
├── AGENTS.md
├── FOCUS.md
└── README.md
```