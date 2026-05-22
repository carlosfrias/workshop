# RULES — Guard Rails, Quality & Common Mistakes

**Section ID:** `import-rules`
**Size:** ~2KB | **LOD:** Low | **Load:** When verifying imports or troubleshooting

---

## Must Always

- Back up the ledger before running imports (pipeline does this automatically)
- Place raw statements in `staging/inbox/` before ingesting
- Review `bean-check` output after import
- Check `logs/pipeline.log` for SKIP/ERROR events

## Must Never

- Modify the ledger directly during an import session — let the pipeline handle it
- Delete backup files — `.backups/` preserves audit history
- Ingest the same statement twice without checking logs first
- Skip `bean-check` validation after import

---

## Quality Checklist

- [ ] `bean-check` passes on final ledger
- [ ] No unexpected SKIP events in `logs/pipeline.log`
- [ ] Backup created before import (`ledger/.backups/` has new file)
- [ ] Trade IDs match format `#SCHWAB-YYYYMMDD-NNN`
- [ ] Import job recorded in `logs/import_jobs.jsonl`

---

## Common Mistakes

| Mistake | Correct Approach |
|---------|-----------------|
| Ingesting statement without checking for prior import | Check `logs/pipeline.log` for statement filename |
| Forgetting `--auto-approve` flag | Without it, records stay in pending |
| Modifying ledger during pipeline run | Let pipeline complete, then verify `bean-check` |
| Not checking patch file format | Validate JSON structure before running ingest |
| Skipping `bean-check` after rollback | Always run `bean-check` after rollback restores |
| Ignoring SKIP events in logs | Each SKIP indicates a record that was not imported — investigate |