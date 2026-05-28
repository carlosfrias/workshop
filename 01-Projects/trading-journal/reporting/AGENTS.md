# AGENTS.md — Reporting

**Domain:** Reporting  
**Purpose:** Generate trade reports, export journal data, create summaries and reviews.

## [S-TIGHT]

Self-contained domain. Load this file for all reporting operations. Do not navigate to other files.

---

## Conventions

1. **Report Types:**
   - **Trade Summary** — List of trades in period with key stats
   - **Performance Report** — Analytics metrics with commentary
   - **Journal Export** — Full journal notes in markdown/PDF
   - **Weekly Review** — Week's trades, lessons, adjustments
   - **Monthly Review** — Month's performance, patterns, goals

2. **Export Formats:**
   - Markdown (`.md`) — For Obsidian vault
   - JSON (`.json`) — For data portability
   - CSV (`.csv`) — For spreadsheet analysis
   - PDF (`.pdf`) — For sharing/printing (via VitePress or conversion)

3. **Naming Convention:** `report-YYYY-MM-DD-[type].md`

---

## Rules

1. **Data Completeness:** Reports must include all trades in specified period.
2. **Timestamp:** All reports include generation timestamp.
3. **Versioning:** Revised reports increment version (e.g., `v2`).
4. **Privacy:** No account numbers or sensitive data in exports.
5. **Review Cadence:** Weekly reviews due Sunday EOD, monthly reviews due 1st of month.

---

## Quality Checklist

Before delivering a report:
- [ ] Time period clearly defined
- [ ] All trades in period included
- [ ] Metrics match analytics domain calculations
- [ ] Formatting consistent
- [ ] Timestamp included
- [ ] Export format correct
- [ ] File saved to correct location

---

## Documentation Protocol

1. **Report Storage:** Save reports to `personal-vault/01-Projects/trading-journal/reports/`.
2. **Index Update:** Add entry to `reports/README.md` index.
3. **Activity Log:** Append to `personal-vault/01-Projects/trading-journal/wiki/reporting/Activity Log.md`.

---

## Templates

### Weekly Review Template
```markdown
---
report-type: weekly-review
week-start: 2026-05-21
week-end: 2026-05-27
generated: 2026-05-27
tags: [report, weekly-review]
---

# Weekly Review — Week of {{week-start}}

## Summary
- Trades: {{count}}
- Win Rate: {{winRate}}%
- Net P&L: ${{netPnL}}
- Net R: {{netR}}R

## Trades This Week
{{trade-table}}

## Wins
- {{win-1}}
- {{win-2}}

## Losses
- {{loss-1}}
- {{loss-2}}

## Lessons Learned
1. {{lesson-1}}
2. {{lesson-2}}

## Adjustments for Next Week
1. {{adjustment-1}}
2. {{adjustment-2}}
```

### Monthly Review Template
```markdown
---
report-type: monthly-review
month: 2026-05
generated: 2026-06-01
tags: [report, monthly-review]
---

# Monthly Review — {{month}}

## Performance Summary
- Total Trades: {{count}}
- Win Rate: {{winRate}}%
- Expectancy: {{expectancy}}R
- Profit Factor: {{profitFactor}}
- Net P&L: ${{netPnL}}
- Net R: {{netR}}R
- Max Drawdown: {{maxDD}}R

## Metrics by Symbol
{{symbol-breakdown}}

## Best Trades
{{top-trades}}

## Worst Trades
{{bottom-trades}}

## Patterns Observed
{{patterns}}

## Goals for Next Month
{{goals}}
```

---

*Last updated: 2026-05-27*
