# AGENTS.md — Trade Management

**Domain:** Trade Management  
**Purpose:** Monitor and adjust open positions throughout their lifecycle.

## [S-TIGHT]

Self-contained domain. Load this file for all trade management operations. Do not navigate to other files.

---

## Conventions

1. **Action Types:**
   - `ADJUST_STOP` — Move stop loss (must be in profitable direction for longs, opposite for shorts)
   - `SCALE_IN` — Add to existing position
   - `SCALE_OUT` — Reduce position (partial close)
   - `CLOSE` — Full exit
   - `TRAIL` — Activate trailing stop

2. **State Tracking:** Every action updates trade status and creates an audit trail.

3. **P&L Calculation:** Real-time unrealized P&L must be calculated on every action.

4. **Breakeven Rule:** Stop loss should move to breakeven once trade reaches 1R profit.

---

## Rules

1. **Stop Adjustment:** Never move stop loss against the position (no widening risk).
2. **Scale-In Limits:** Maximum 3 adds per position; each add requires its own stop.
3. **Scale-Out Triggers:** Take partial profits at predefined levels (e.g., 50% at 1R, 25% at 2R).
4. **Close Confirmation:** Require explicit confirmation before full close.
5. **Trailing Stop:** Trail distance must be documented (e.g., ATR-based, fixed points, swing low/high).

---

## Quality Checklist

Before executing any management action:
- [ ] Current position status verified
- [ ] Unrealized P&L calculated
- [ ] Action type confirmed (ADJUST_STOP, SCALE_IN, SCALE_OUT, CLOSE, TRAIL)
- [ ] Risk parameters updated (new stop, new position size, etc.)
- [ ] Journal note updated
- [ ] Trade log updated
- [ ] Activity logged

---

## Documentation Protocol

1. **Trade Log Update:** Append action to trade's `actions` array in `trade-log.json`.
2. **Journal Update:** Edit existing journal note with management action and new status.
3. **Activity Log:** Append to `personal-vault/01-Projects/trading-journal/wiki/trade-management/Activity Log.md`.

---

## Templates

### Management Action Structure
```json
{
  "tradeId": "20260527-0930-ES-LONG",
  "action": "ADJUST_STOP",
  "timestamp": "2026-05-27T15:45:00Z",
  "previousStop": 5220.00,
  "newStop": 5240.00,
  "priceAtAction": 5255.00,
  "unrealizedPnL": 410.00,
  "rationale": "Moved to breakeven after reaching 1R target"
}
```

### Position Status
```json
{
  "tradeId": "20260527-0930-ES-LONG",
  "status": "OPEN",
  "entryPrice": 5234.50,
  "currentPrice": 5255.00,
  "currentStop": 5240.00,
  "positionSize": 2,
  "unrealizedPnL": 410.00,
  "unrealizedR": 1.41,
  "actions": [...]
}
```

---

*Last updated: 2026-05-27*
