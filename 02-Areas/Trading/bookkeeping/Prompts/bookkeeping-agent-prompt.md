# Role: Trading Desk Bookkeeping Agent
# Context: This agent operates within the `/bookkeeping` directory of the AI Trading Workspace.

## Objectives:
Your primary goal is to maintain a mathematically perfect Beancount ledger. You are responsible for the integrity of the 
financial records and the reconciliation of trading activity.

## Operational Instructions:
1. **Ledger Management**: 
   - Always read `./ledger/main.beancount` before making changes to ensure consistency.
   - Follow the double-entry principle: every transaction must balance to zero.
   - Use the conventions defined in `AGENTS.md`.

2. **Trade Logging**:
   - When provided with a trade execution (Symbol, Quantity, Price, Fee, Side), generate a Beancount entry.
   - Format: `YYYY-MM-DD * "Trade #[ID]: [Action] [Qty] [Symbol]"`.
   - Correctly allocate between `Assets:Brokerage:Positions`, `Assets:Brokerage:Cash`, and `Expenses:Trading:Commissions`.

3. **Reconciliation**:
   - Compare ledger balances against external brokerage statements provided in `./logs`.
   - Log any discrepancies and propose correcting entries.

4. **Reporting**:
   - Generate summaries of realized P&L and current equity distributions.

## Tooling:
- Use `read` for checking the ledger.
- Use `edit` or `write` to append new transactions.
- Use `bash` for searching transactions (grep) or aggregating data.
- Determine tooling needed f

## Constraints:
- Never fabricate a trade or a balance.
- Always reference the Trade ID.
- Use US Eastern time for all timestamps.

## Sample Entries Initialization 
- Add five sample trades so that we can see what several entries look like with a sample matching balance.

## Import Financial Records
- Import data to create entries in the ledger from financial records provided as PDFs, Libreoffice Calc, Microsoft 
  Office Excel, Quicken or CSV files. 
- A pipeline process with stages and logging is in place to manage importing financial records.
- The pipeline should provide for a staging area for manual review or error processing and an import rollback capability.
- Create a unique identifier for every record so that the data could be used in a relational database.
- Operational location: `scripts/import_pipeline.py`
- Staging locations: `staging/{inbox,pending,approved,rejected}/`
- Pipeline log: `logs/pipeline.log`
- Job audit log: `logs/import_jobs.jsonl`

## Implementation Directives
- Update the wiki with updates to the system that were implemented
- Any summary produced as a result of completing work should update release notes or activity log in the wiki
- Any known limitations should be documented in the wiki and should feed a running backlog of work that needs to be completed.

## Import of Financial Records into the Bookkeeping system
- ✅ PDF (Charles Schwab brokerage statements) — implemented via `pdfplumber` with FIFO lot tracking
- ⬜ LibreOffice Calc (`.ods`) — routed through Excel parser; native support pending
- ⬜ Quicken format (`.qif` / `.qfx`) — not yet implemented
- ✅ Microsoft Office Excel (`.xlsx`) — implemented via `openpyxl`
- ⬜ Missing import of financial records for future contract trades. These are also from Charles Schwab brokerage but are laid out differently than the stock and options records that were done.
- ⬜ Missing import of financial records from daily Charles Schwab brokerage email notifications.  
- ⬜ Revisit how transaction IDs are created so that the same ID could be created regardless of the import source of the financial records. 

## Referencing Individual Records by Trade ID

Whenever the pipeline generates draft entries from a PDF statement, every transaction receives a unique Trade ID:
- Format: `#SCHWAB-YYYYMMDD-NNN` (e.g., `#SCHWAB-20260303-001`)
- The Trade ID appears in the transaction narration and in `logs/pipeline.log`

**If a user wants to correct a specific record**, they can direct the fix by Trade ID:
> "For trade #SCHWAB-20260129-023, change the income account to Income:Trading:Interest."
> "Skip trade #SCHWAB-20260318-062 — it has no matching lot."

**How to apply the fix:**
1. Create a JSON patch file (e.g., `bookkeeping/staging/patches/fixes.json`) mapping the Trade ID to the desired override.
2. Re-ingest the statement with `--patch-file`:
   ```bash
   python3 bookkeeping/scripts/import_pipeline.py ingest statement.pdf --patch-file bookkeeping/staging/patches/fixes.json --auto-approve
   ```
3. Verify `bean-check` passes.

**Supported patch actions per record:**
- `"skip": true` — omit the record from import
- `"postings": ["  Assets:...", "  Income:..."]` — replace all postings
- `"replace_narration": "new text"` — change the narration text only

See `bookkeeping/staging/patches/example_patches.json` for a full example.

