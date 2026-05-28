# Trading Journal — Quick Start Guide

**Purpose:** Capture and manage trades with live data, options support, Greeks, account-level P&L, bookkeeping integration, and Gmail notification parsing. Replaces DTI and LS spreadsheet journals.

---

## Overview

The Trading Journal provides:
- **Trade Capture** — Log new trades with complete entry data
- **Trade Management** — Track adjustments, exits, and P&L
- **Analytics** — Calculate win rate, expectancy, drawdown, Sharpe ratio
- **Reporting** — Generate weekly/monthly reviews and trade summaries

---

## Quick Commands

### 1. Capture a New Trade

```bash
cd workshop/01-Projects/trading-journal/trade-entry/scripts

python capture-trade.py \
  --symbol ES \
  --direction LONG \
  --entry 5234.50 \
  --size 2 \
  --stop 5220.00 \
  --target 5260.00 \
  --target 5280.00 \
  --rationale "Breakout above resistance with volume confirmation"
```

**Output:**
- Updates `trade-log.json` with structured trade data
- Creates journal note in `personal-vault/01-Projects/trading-journal/journal/`

---

### 2. View Performance Metrics

```bash
cd workshop/01-Projects/trading-journal/analytics/scripts

# All-time metrics
python calculate-metrics.py --period all-time

# Last 30 days
python calculate-metrics.py --period 30d

# This week
python calculate-metrics.py --period week

# JSON output
python calculate-metrics.py --period all-time --output json
```

**Metrics Calculated:**
- Win rate, expectancy, profit factor
- Average R-multiple per trade
- Max drawdown (peak-to-trough)
- Sharpe ratio
- Consecutive wins/losses streaks
- Segmented analysis by symbol and direction

---

### 3. Generate Reports

```bash
cd workshop/01-Projects/trading-journal/reporting/scripts

# Weekly review
python generate-report.py --type weekly --period week

# Monthly review
python generate-report.py --type monthly --period month

# Trade summary (last 30 days)
python generate-report.py --type summary --period 30d
```

**Reports saved to:** `personal-vault/01-Projects/trading-journal/reports/`

---

## File Structure

```
trading-journal/
├── workshop/01-Projects/trading-journal/
│   ├── trade-entry/
│   │   ├── trade-log.json              # Structured trade data
│   │   └── scripts/
│   │       └── capture-trade.py        # Trade entry script
│   ├── trade-management/
│   ├── analytics/
│   │   └── scripts/
│   │       └── calculate-metrics.py    # Performance metrics
│   └── reporting/
│       └── scripts/
│           └── generate-report.py      # Report generation
│
└── personal-vault/01-Projects/trading-journal/
    ├── journal/
    │   ├── TRADE-TEMPLATE.md           # Journal note template
    │   └── YYYY-MM-DD-HHMM-Symbol.md   # Individual trade notes
    ├── reports/
    │   └── report-YYYY-MM-DD-type.md   # Generated reports
    └── wiki/                           # Domain documentation
```

---

## Trade Log Schema

```json
{
  "tradeId": "20260527-0930-ES-LONG",
  "symbol": "ES",
  "direction": "LONG",
  "entryPrice": 5234.50,
  "positionSize": 2,
  "stopLoss": 5220.00,
  "takeProfit": [5260.00, 5280.00],
  "riskReward": "1:2.5",
  "riskAmount": 290.00,
  "entryRationale": "Breakout above resistance",
  "timestamp": "2026-05-27T14:30:00Z",
  "status": "OPEN"
}
```

---

## Journal Note Template

Each trade creates a markdown note with:
- Frontmatter with trade metadata
- Entry details table
- Entry rationale
- Trade management actions log
- Exit details (when closed)
- Post-trade analysis

---

## Domain Routing

| Task | Route To |
|------|----------|
| Capture trade, log entry | [Trade Entry](./trade-entry/AGENTS.md) |
| Adjust stop, close trade | [Trade Management](./trade-management/AGENTS.md) |
| View metrics, analytics | [Analytics](./analytics/AGENTS.md) |
| Generate report, export | [Reporting](./reporting/AGENTS.md) |

---

## Model Configuration

| Role | Model |
|------|-------|
| Orchestrator | qwen3.5:397b-cloud |
| Reasoning | deepseek-v4-pro:cloud |
| Fast | gemma4:31b-cloud |

---

## Next Development

- [ ] Trade management workflow (adjust stops, scale in/out)
- [ ] Position monitoring script
- [ ] Real-time P&L tracking
- [ ] Integration with bookkeeping (Beancount)

---

*For detailed domain rules, see each domain's AGENTS.md file*
