# AGENTS.md — Bookkeeping

**Documentation home:** `../../personal-vault/02-Areas/Trading/bookkeeping/` or `../../personal-vault/02-Areas/Trading/`
**Code workspace:** `./` (this directory)

## [S-TIGHT]

Bookkeeping system using Beancount plain-text accounting. Three sub-domains: financial ledger (Schwab brokerage), import pipeline (PDF/XLSX/CSV → Beancount), and AI cost model (cloud/local inference spend tracking). Fava UI managed via playbook-executor.

## Domain Routing

| Keywords | Read this file |
|----------|---------------|
| bookkeeping, ledger, beancount, reconciliation, p&l, realization, cost-basis, trade log, journal entry, financial records, double-entry, main.beancount, balance, trial balance, income statement, balance sheet | `./ledger/AGENTS.md` |
| import, pipeline, staging, ingest, pdfplumber, schwab, brokerage statement, pdf import, csv import, xlsx import, approved, rejected, patch file, rollback, bean-check | `./import/AGENTS.md` |
| ai cost, model cost, inference cost, token cost, cloud spend, local model cost, cost tracking, compute cost, routing efficiency, ai-cost-model, ai budget | `./cost-model/AGENTS.md` |
| fava, fava server, start fava, stop fava, restart fava, ledger viewer, bean counter | Use playbook-executor: `start-fava` playbook |

## Tech Stack

| Component | Technology | Managed By |
|-----------|-----------|-------------|
| Ledger | Beancount (plain-text) | This project |
| Web UI | Fava | playbook-executor (`start-fava.yml`) |
| PDF import | pdfplumber | `./scripts/import_pipeline.py` |
| Excel import | openpyxl | `./scripts/import_pipeline.py` |
| Python venv | Python 3.14 at `./.venv` | playbook-executor manages installs |

## Conventions

- All timestamps in US Eastern (America/New_York)
- All date formats: YYYY-MM-DD
- All monetary values in USD unless specified
- Trade IDs: `#SCHWAB-YYYYMMDD-NNN`
- Beancount format: `YYYY-MM-DD * "Description" Account:Name Amount Commodity`
- Double-entry: every transaction must balance to zero

## Key Files

| File | Purpose |
|------|---------|
| `ledger/main.beancount` | Primary Schwab brokerage ledger (706 lines) |
| `ledger/ai-cost-model.beancount` | AI inference cost tracking ledger (72 lines) |
| `ledger/combined.beancount` | Combined view merging all sub-ledgers |
| `scripts/import_pipeline.py` | Main import pipeline (811 lines) |
| `scripts/run_import.sh` | Bash wrapper for pipeline |
| `staging/inbox/` | Raw PDF/XLSX/CSV statements awaiting processing |
| `staging/approved/` | Approved processed statements |
| `staging/patches/` | JSON patch files for record corrections |
| `logs/pipeline.log` | Pipeline execution log |
| `logs/import_jobs.jsonl` | Import job audit trail |
| `Prompts/bookkeeping-agent-prompt.md` | Operational prompt for bookkeeping agent |

## Quality Checks

- [ ] All transactions balance to zero
- [ ] Every trade references a Trade ID in description
- [ ] Timestamps match US Eastern time
- [ ] `bean-check` passes on all ledgers
- [ ] Import pipeline creates backup before any ledger modification

## Documentation Protocol

- Session notes: `../../personal-vault/02-Areas/Trading/bookkeeping/journal/` or Carlos-Trading-Desk journal
- AI cost log: `../../personal-vault/02-Areas/Trading/bookkeeping/costs/AI-MODEL-COSTS.md`
- Prompt threads: Carlos-Trading-Desk thread system

## Cross-Reference

| Need | Go Here |
|------|---------|
| Project overview, sessions | `../../personal-vault/02-Areas/Trading/` |
| Start/stop Fava UI | `playbook-executor` → `start-fava` playbook |
| Trading desk root router | `../../AGENTS.md` |
