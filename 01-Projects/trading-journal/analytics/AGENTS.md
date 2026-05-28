# AGENTS.md — Analytics

**Domain:** Analytics  
**Purpose:** Calculate performance metrics, analyze trading statistics, generate insights.

## [S-TIGHT]

Self-contained domain. Load this file for all analytics operations. Do not navigate to other files.

---

## Conventions

1. **Metrics Calculated:**
   - Win Rate (% winning trades)
   - Expectancy (avg win × win% - avg loss × loss%)
   - Profit Factor (gross profit / gross loss)
   - Average R-multiple per trade
   - Max Drawdown (peak-to-trough equity decline)
   - Sharpe Ratio (risk-adjusted returns)
   - Average win/loss ratio
   - Consecutive wins/losses streaks

2. **Time Periods:** All metrics should be calculable for:
   - All-time
   - Last 30 days
   - Last 90 days
   - Current month
   - Current week

3. **Segmentation:** Metrics should be segmentable by:
   - Symbol/Instrument
   - Direction (LONG/SHORT)
   - Setup type
   - Time of day
   - Day of week

---

## Rules

1. **Data Integrity:** Only include closed trades in performance metrics.
2. **R-Multiple Standard:** All P&L should be normalized to R-multiples for comparison.
3. **Outlier Handling:** Flag trades >3 standard deviations from mean for review.
4. **Sample Size Warning:** Display warning if sample size < 30 trades for statistical metrics.
5. **Drawdown Calculation:** Use peak-to-trough method on cumulative R-multiple curve.

---

## Quality Checklist

Before delivering analytics:
- [ ] Data source verified (closed trades only)
- [ ] Time period clearly specified
- [ ] Sample size noted
- [ ] All calculations double-checked
- [ ] R-multiple and dollar P&L both shown
- [ ] Drawdown correctly calculated (peak-to-trough)
- [ ] Visualizations labeled with axes and units

---

## Documentation Protocol

1. **Metrics Storage:** Save calculated metrics to `analytics/metrics-YYYY-MM-DD.json`.
2. **Journal Summary:** Create summary note in `personal-vault/01-Projects/trading-journal/analytics/`.
3. **Activity Log:** Append to `personal-vault/01-Projects/trading-journal/wiki/analytics/Activity Log.md`.

---

## Templates

### Metrics Output Structure
```json
{
  "period": "all-time",
  "generatedAt": "2026-05-27T16:00:00Z",
  "totalTrades": 47,
  "winningTrades": 29,
  "losingTrades": 18,
  "winRate": 0.617,
  "avgWinR": 2.3,
  "avgLossR": -1.1,
  "expectancy": 0.97,
  "profitFactor": 2.14,
  "avgRPerTrade": 0.89,
  "maxDrawdownR": -4.2,
  "sharpeRatio": 1.43,
  "consecutiveWins": 7,
  "consecutiveLosses": 3
}
```

### Segmented Analysis
```json
{
  "segment": "by-symbol",
  "data": {
    "ES": {"trades": 23, "winRate": 0.65, "avgR": 1.2},
    "NQ": {"trades": 15, "winRate": 0.60, "avgR": 0.8},
    "CL": {"trades": 9, "winRate": 0.56, "avgR": 0.4}
  }
}
```

---

*Last updated: 2026-05-27*
