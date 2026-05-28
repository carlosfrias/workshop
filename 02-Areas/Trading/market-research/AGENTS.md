# Market Research

Generating, evaluating, and backtesting trading signals and market analysis. This domain covers data acquisition, 
indicator computation, sentiment analysis, and signal research that informs trading decisions.

## Conventions

- All price data in OHLCV format with timestamps in US Eastern
- All signals include: instrument, direction (long/short), timestamp, confidence level (0-1)
- Backtest results must include: total return, max drawdown, Sharpe ratio, win rate, trade count
- Data sources must be cited (e.g., "Source: Polygon.io daily bars")
- All outputs should include the observation period (e.g., "2020-01-01 to 2026-04-20")
- Distinguish between in-sample and out-of-sample results

## Rules

### Must Always
- Cite data sources for all research outputs
- Distinguish in-sample vs out-of-sample results in backtests
- Report confidence level for every signal
- Include transaction costs in backtest results
- State all assumptions explicitly (e.g., slippage model, fill assumptions)

### Must Never
- Report in-sample results as if they are out-of-sample
- Omit transaction costs from backtest results
- Present a signal without confidence level and observation period
| Cherry-pick start/end dates to flatter results
| Confuse correlation with causation in analysis

### Honesty Gap Management
- Only extract values that are explicitly stated in the document. 
- When a response is ambiguous, missing evidence, or unclear, please consider this a BLANK RESPONSE. 
- When you encounter a blank response, I want you to provide an indication of which type blank response is applicable. 
- In addition to indicating a blank response, please provide a one-sentence explanation as to why you think the response 
should be considered a blank response. 
- Base every value on what the source document actually says and quote/reference the specific sections used 
- A wrong answer is 3x worse than a blank response answer. When in doubt, leave it blank. 
- For each field with a value, add a "Source" column:
  - EXTRACTED = directly stated, exact match 
  - INFERRED = derived, calculated or interpreted 
- For every INFERRED field, add a one-sentence explanation. 
- For every BLANK RESPONSE field, add a row to a separate "Flags" table explaining why the value could not be extracted.

## Quality Checklist

Before considering any task complete, verify:

- [ ] Data sources are cited
- [ ] In-sample and out-of-sample periods are clearly separated

---

## Backlog Management

**Documentation home:** `../personal-vault/` — backlog and session tracking follow vault-native conventions.

**Active Backlog:** Tracked in `../personal-vault/02-Areas/Trading/Overview.md`
- [ ] Transaction costs are included in backtest results
- [ ] Signal includes direction, timestamp, and confidence level
- [ ] Assumptions are stated explicitly
- [ ] Honesty gap assessment done

## Common Mistakes

| Mistake | Correct Approach |
|---------|-----------------|
| Omitting transaction costs in backtest | Always include realistic commission and slippage |
| Treating in-sample as out-of-sample | Walk-forward or hold-out validation, clearly labeled |
| Not citing data sources | Every dataset must have a provenance record |
| Cherry-picking date ranges | Use full available history or justify subset selection |
| Reporting point-in-time without confidence | Every signal needs a confidence score |

## Cross-Domain References

For tasks that span domains, consult the routing table in `./AGENTS.md` (project root). Relevant cross-domain interactions:
- **position-management** — research signals feed into position sizing and entry/exit decisions
- **bookkeeping** — data feed subscriptions and research costs are trackable expenses
- **technical-infrastructure** — data pipeline health affects research quality