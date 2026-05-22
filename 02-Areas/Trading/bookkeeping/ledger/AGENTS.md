# ledger — Financial Ledger Management

Maintain a mathematically perfect Beancount ledger for Schwab brokerage trading activity. This domain owns the chart of accounts, transaction generation, reconciliation, and P&L reporting.

## [S-TIGHT]

Read `ledger/main.beancount` before any change. Every transaction must balance to zero. Use double-entry accounting with Trade ID references. Run reconciliation against brokerage statements. Generate P&L reports on request. Sub-domain of `../AGENTS.md` (Bookkeeping).

## Conventions

- **Beancount format**: `YYYY-MM-DD * "Trade #[ID]: [Action] [Qty] [Symbol]"  Account:Name  Amount Commodity`
- **Trade ID format**: `#SCHWAB-YYYYMMDD-NNN`
- **Positions**: `Assets:Brokerage:Positions`
- **Cash**: `Assets:Brokerage:Cash`
- **Commissions/Fees**: `Expenses:Trading:Commissions`
- **Dividends**: `Income:Trading:Dividends`
- **Interest**: `Income:Trading:Interest`
- **All timestamps**: US Eastern (America/New_York)

## Rules

### Must Always
- Read `ledger/main.beancount` before making any change
- Every transaction must balance to zero (double-entry)
- Reference a Trade ID in every transaction narration
- Back up the ledger before running imports — see `../import/AGENTS.md`
- Run `bean-check` after any manual entry

### Must Never
- Fabricate a trade, balance, or price
- Skip the Trade ID reference
- Modify the ledger without first reading its current state
- Delete backup files — `.backups/` is sacred audit history

## Workflow

1. **Event trigger**: Trade execution signal → generate Beancount entry
2. **Manual entry**: Use `edit` tool to append transaction to `main.beancount`
3. **Import entry**: Handled by `../import/AGENTS.md` — pipeline generates entries, this domain validates
4. **Reconciliation**: Compare ledger against external brokerage CSV/PDF statements
5. **P&L**: Run `bean-report` or Fava to generate realized/unrealized P&L

## Quality Checklist

- [ ] All transactions balance to zero
- [ ] Every trade has a Trade ID in description
- [ ] Timestamps match US Eastern time
- [ ] `bean-check` passes with no errors
- [ ] Ledger matches brokerage statement total (after reconciliation)

## Common Mistakes

| Mistake | Correct Approach |
|---------|-----------------|
| Forgetting to read ledger before editing | Always `read ledger/main.beancount` first |
| Missing Trade ID in transaction | Include `#SCHWAB-YYYYMMDD-NNN` in narration |
| Wrong timestamp timezone | Use US Eastern (America/New_York) |
| Unbalanced transaction (forgetting commission) | Include fees in `Expenses:Trading:Commissions` |
