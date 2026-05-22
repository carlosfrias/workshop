# PIPELINE — Import Workflow Commands

**Section ID:** `import-pipeline`
**Size:** ~1.5KB | **LOD:** Low | **Load:** When running imports or rollbacks

---

## Standard Import

```bash
cd /Users/friasc/Dropbox/carlos-desktop/workshop/02-Areas/Trading/bookkeeping
python3 scripts/import_pipeline.py ingest staging/inbox/statement.pdf
```

Ingests a statement from `staging/inbox/`. Records enter `pending/` for review. Pipeline creates a timestamped backup of the ledger before writing.

## Import with Auto-Approval

```bash
python3 scripts/import_pipeline.py ingest staging/inbox/statement.pdf --auto-approve
```

Skips the pending review stage. Records go directly to `approved/` and are written to the ledger. Use only after verifying the statement has no issues.

## Import with Patch File

```bash
python3 scripts/import_pipeline.py ingest statement.pdf --patch-file staging/patches/fixes.json --auto-approve
```

Applies per-record corrections from a patch file during ingestion. Combine with `--auto-approve` for end-to-end automated import. See [PATCHES.md](PATCHES.md) for patch file format.

## Rollback

```bash
python3 scripts/import_pipeline.py rollback
```

Restores the ledger to its pre-import state using the most recent backup in `ledger/.backups/`. Safe to use at any point during or after an import session.

## Pipeline Execution Order

1. Backup ledger → `ledger/.backups/main_{timestamp}.beancount`
2. Parse statement (PDF/XLSX/CSV)
3. Generate Trade IDs (`#SCHWAB-YYYYMMDD-NNN`)
4. Apply patch file (if provided)
5. Write approved records to `staging/approved/`
6. Import records into Beancount ledger
7. Run `bean-check` validation
8. Log job to `logs/import_jobs.jsonl`