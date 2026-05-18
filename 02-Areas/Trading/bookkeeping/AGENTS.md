# Bookkeeping Agent Protocol
# Framework: Beancount (Plain Text Accounting)

## Domain Routing
When any of the following keywords appear in a prompt, load the specialized initialization prompt from `./Prompts/bookkeeping-agent-prompt.md`:
- a list of keywords: `bookkeeping, ledger, beancount, reconciliation, p&l, realization, cost-basis, financial-records`

## Workflow
1. **Event Trigger**: The `trade-to-log.chain` or `position-management` agent signals a trade execution.

2. **Entry Generation**: The `bookkeeping` agent creates a Beancount transaction in `./bookkeeping/ledger/main.beancount`.
3. **Reconciliation**: Periodically, the agent reads brokerage CSVs and compares them against the ledger.
4. **Import Pipeline**: Staged, auditable import of CSV/XLSX/ODS financial records via `./scripts/import_pipeline.py`. See `./Prompts/bookkeeping-agent-prompt.md` for operational details.
5. **P&L Calculation**: Use Beancount/Fava to generate realized and unrealized P&L reports.

## Financial Records Import Pipeline

Supported formats: CSV, Microsoft Excel (XLSX), LibreOffice Calc (ODS).

**Stages:** Inbox → Validate → Pending → Review → Import → Archive

**Rollback:** Every import creates a timestamped backup in `./ledger/.backups/`. Rollback restores the pre-import ledger state.

## Fava Visualization

[Fava](https://beancount.github.io/fava/) is the web-based UI layered on top of Beancount. It runs from the Python virtual environment at `.venv` in the project root.

**To launch Fava:**
```bash
source .venv/bin/activate
fava bookkeeping/ledger/main.beancount
```

This starts a local web server at `http://127.0.0.1:5000` with interactive views for trial balance, income statement, balance sheet, and commodity price charts.

## Beancount Conventions
- **Format**: `YYYY-MM-DD * "Description" Account:Name Amount Commodity`
- **Positions**: Tracked in `Assets:Brokerage:Positions`.
- **Fees**: Always logged to `Expenses:Trading:Commissions`.

## Quality Checks
- [ ] All transactions must balance to zero.
- [ ] Every trade must reference a Trade ID in the description.
- [ ] Timestamps must match US Eastern time.

---

## Backlog Management

**Documentation home:** `../personal-vault/` — backlog and session tracking follow vault-native conventions.

**Active Backlog:** Tracked in `../personal-vault/01-Projects/Carlos-Trading-Desk/Overview.md`
