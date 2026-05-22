# import — Financial Records Import Pipeline

Staged, auditable import of Schwab brokerage statements (PDF/XLSX/CSV) into the Beancount ledger. Runs `import_pipeline.py` with validation, patching, backup, and rollback support. Sub-domain of `../AGENTS.md` (Bookkeeping).

## [S-TIGHT]

Six-stage pipeline: Inbox → Validate → Pending → Review → Import → Archive. Every import creates a timestamped backup. Patch files correct individual records via Trade ID. Rollback restores pre-import state. Load only the routing section relevant to your task.

---

## Domain Routing Table

| Section | File | LOD | Purpose |
|---------|------|-----|---------|
| CORE | [routing/CORE.md](routing/CORE.md) | Low | Identity, conventions, supported formats, key files |
| PIPELINE | [routing/PIPELINE.md](routing/PIPELINE.md) | Low | Import commands: standard, auto-approve, patch, rollback |
| PATCHES | [routing/PATCHES.md](routing/PATCHES.md) | Medium | Patch file format and supported patch actions |
| RULES | [routing/RULES.md](routing/RULES.md) | Low | Must/must-never rules, quality checklist, common mistakes |

## Load Directive

| Model Tier | Max Context | Strategy |
|------------|-------------|----------|
| **Low local** (<4K ctx) | Load ONLY the section listed for your task. Max 1 section. | |
| **Medium local** (~8K ctx) | Load CORE + 1 task section. Max 2 sections. | |
| **High local** (~32K ctx) | Load CORE + up to 3 task sections. Max 4 sections. | |
| **Cloud** (>32K ctx) | Load all sections if needed. Prefer targeted loading. | |

## Quick Task Routing

| Task | Load |
|------|------|
| Run a standard import | PIPELINE.md |
| Run import with patches | PIPELINE.md → PATCHES.md |
| Rollback an import | PIPELINE.md |
| Verify import quality | RULES.md |
| Check supported formats | CORE.md |
| Find a key file path | CORE.md |
| Create a patch file | PATCHES.md → CORE.md (for Trade ID format) |
| Troubleshoot a failed import | RULES.md → PIPELINE.md |

---

*This manifest is the only file loaded by default. All other sections are demand-loaded from `routing/`.*