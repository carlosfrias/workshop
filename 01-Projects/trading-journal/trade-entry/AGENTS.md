# AGENTS.md — Trade Entry

**Domain:** Trade Entry  
**Purpose:** Capture and log new trades with complete entry data.

## [S-TIGHT]

Self-contained domain. Load this file for all trade entry operations. Do not navigate to other files.

---

## Conventions

1. **Trade ID Format:** `YYYYMMDD-HHMM-SYMBOL-DIRECTION` (e.g., `20260527-0930-ES-LONG`)
2. **Data Structure:** Every trade entry must include:
   - Symbol/Instrument
   - Direction (LONG/SHORT)
   - Entry price
   - Position size
   - Stop loss level
   - Take profit target(s)
   - Risk-reward ratio
   - Entry rationale/setup
   - Timestamp
3. **Risk Calculation:** Always calculate R-multiple before entry confirmation.
4. **Validation Gate:** No trade is logged without stop loss and position size.

---

## Rules

1. **Mandatory Fields:** Entry price, stop loss, position size, symbol, direction.
2. **Risk Check:** Reject entries where risk exceeds predefined account risk % (default 1-2%).
3. **Duplicate Detection:** Check for existing open positions in same symbol before entry.
4. **Timestamp:** All entries must be timestamped in UTC.
5. **Journal Link:** Every trade entry creates a corresponding journal note in vault.

---

## Quality Checklist

Before confirming a trade entry:
- [ ] Symbol and direction specified
- [ ] Entry price recorded
- [ ] Stop loss level defined
- [ ] Position size calculated
- [ ] Risk-reward ratio ≥ 1:2 (or documented exception)
- [ ] Entry rationale documented
- [ ] No conflicting open positions
- [ ] Journal note created in vault

---

## Documentation Protocol

1. **Trade Log:** Update `trade-log.json` in workshop with structured data.
2. **Journal Note:** Create markdown note in `personal-vault/01-Projects/trading-journal/journal/` with format `YYYY-MM-DD-HHMM-Symbol.md`.
3. **Activity Log:** Append to `personal-vault/01-Projects/trading-journal/wiki/trade-entry/Activity Log.md`.

---

## Templates

### Trade Entry JSON Structure
```json
{
  "tradeId": "YYYYMMDD-HHMM-SYMBOL-DIRECTION",
  "symbol": "ES",
  "direction": "LONG",
  "entryPrice": 5234.50,
  "positionSize": 2,
  "stopLoss": 5220.00,
  "takeProfit": [5260.00, 5280.00],
  "riskReward": "1:2.5",
  "riskAmount": 290.00,
  "entryRationale": "Breakout above resistance with volume confirmation",
  "timestamp": "2026-05-27T14:30:00Z",
  "status": "OPEN"
}
```

### Journal Note Frontmatter
```markdown
---
trade-id: YYYYMMDD-HHMM-SYMBOL-DIRECTION
symbol: ES
direction: LONG
status: OPEN
date: 2026-05-27
tags: [trade, open, futures]
---
```

---

*Last updated: 2026-05-27*
