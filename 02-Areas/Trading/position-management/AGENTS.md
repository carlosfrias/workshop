# Position Management

Managing open positions, order execution, risk controls, and portfolio allocation for Carlos' Desktop trading desk. This domain is where research meets execution — signals become trades, and risk is monitored in real time.

## Agent Split

This domain is served by two agents:

| Agent | Model | Scope |
|-------|-------|-------|
| `position-management` | Cloud (qwen3.5:cloud) | Position sizing, trade execution, risk evaluation, portfolio allocation |
| `position-monitor` | Local (qwen3.5:4b) | Position monitoring, status reads, risk limit checks, portfolio state reporting |

Use `position-monitor` for routine status checks and logging. Use `position-management` for decisions that require judgment — sizing, execution, and risk evaluation.

## Conventions

- All positions reported with: instrument, direction, size, entry price, current price, unrealized P&L
- Risk limits stated as percentage of portfolio (e.g., "max 2% risk per trade")
- Order types: market, limit, stop, stop-limit — always specify explicitly
- Position sizing using defined methodology (e.g., fixed fractional, Kelly, volatility-based)
- All timestamps in US Eastern / America/New_York
- All monetary values in USD with 2 decimal places

## Rules

### Must Always
- Check risk limits before submitting any order
- Use defined position-sizing methodology — do not ad-hoc size trades
- Set stop-loss or exit criteria for every position
- Monitor portfolio-level exposure (net delta, sector concentration, correlation)
- Log every order with timestamp, type, price, quantity, and fill status

### Must Never
- Enter a position without a defined exit criteria
- Exceed pre-set risk limits per trade or portfolio-level
- Override risk controls without explicit acknowledgment and logging
- Ignore correlation between positions — portfolio risk ≠ sum of individual risks
- Execute orders without verifying API connectivity (see technical-infrastructure)

## Quality Checklist

Before considering any task complete, verify:

- [ ] Risk limits checked before order submission
- [ ] Position sizing follows defined methodology
- [ ] Exit criteria defined for every position
- [ ] Portfolio-level exposure is within limits
- [ ] All orders logged with full details

---

## Backlog Management

**Documentation home:** `../personal-vault/` — backlog and session tracking follow vault-native conventions.

**Active Backlog:** Tracked in `../personal-vault/02-Areas/Trading/Overview.md`

## Common Mistakes

| Mistake | Correct Approach |
|---------|-----------------|
| Entering a trade without a stop-loss | Always define exit criteria before entry |
| Ad-hoc position sizing | Follow the defined sizing methodology consistently |
| Ignoring portfolio correlation | Calculate net exposure, not just per-position risk |
| Overriding risk limits informally | Any override must be logged with justification |
| Executing without checking connectivity | Verify API health before order submission |

## Cross-Domain References

For tasks that span domains, consult the routing table in `./AGENTS.md` (project root). Relevant cross-domain interactions:
- **market-research** — signals from research drive position entry/exit decisions
- **bookkeeping** — every executed trade must be logged for P&L and reconciliation
- **technical-infrastructure** — API connectivity must be verified before order execution