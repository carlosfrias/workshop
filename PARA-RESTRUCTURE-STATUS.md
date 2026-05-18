# PARA Restructure Status — ai-trading-workspace

**Date:** 2026-05-18
**Task:** Move flat directories to PARA structure

---

## Target Structure

```
ai-trading-workspace/
├── 02-Areas/
│   └── Trading/
│       ├── bookkeeping/
│       ├── position-management/
│       └── market-research/
├── 03-Resources/
│   ├── Infrastructure/
│   │   ├── lab-specs/
│   │   └── technical-infrastructure/packages/ (all packages)
│   ├── Trading/
│   │   └── scripts/
│   └── Wiki/
│       └── trading-desk-wiki/
├── 04-Archive/
│   └── archive-legacy/
└── (root files stay)
```

---

## Move Status

| Source | Target | Status |
|--------|--------|--------|
| `bookkeeping/` | `02-Areas/Trading/bookkeeping/` | ✅ Already moved (AGENTS.md readable at target) |
| `position-management/` | `02-Areas/Trading/position-management/` | ✅ Already moved (AGENTS.md readable at target) |
| `market-research/` | `02-Areas/Trading/market-research/` | ✅ Already moved (AGENTS.md readable at target) |
| `lab-specs/` | `03-Resources/Infrastructure/lab-specs/` | ✅ Already moved (README.md readable at target) |
| `scripts/` | `03-Resources/Trading/scripts/` | ⏳ Needs verification |
| `wiki/` | `03-Resources/Wiki/trading-desk-wiki/` | ❌ Not found at target |
| `archive/` | `04-Archive/archive-legacy/` | ❌ Not found at target |
| `technical-infrastructure/packages/*` | `03-Resources/Infrastructure/` | ⏳ Needs verification |

---

## Packages to Move (from technical-infrastructure/packages/)

These should be moved to `03-Resources/Infrastructure/`:

- agenticos-kernel
- agenticos-mcp-bridge
- agenticos-memory
- agenticos-trading
- demos
- doc-standardizer
- e2e-test-suite
- find-skill
- framework
- gist-message-protocol
- gist-message-queue
- librarian
- master-prompt-system
- playbook-executor
- pi-keyword-router
- routing-transparency
- sshfs-integration
- telegram-export
- voice-input

---

## Root Files That Stay

- AGENTS.md
- package.json (trading-desk-wiki)
- node_modules/
- *.iml
- CLEAN-WORKSPACE-SUMMARY.md
- INDEX.md
- planbooks_list.txt
- progress.md
- README.md
- WORKSPACE-SETUP.md
- technical-infrastructure-backlog.md

---

## Next Steps

1. Verify `scripts/` moved to `03-Resources/Trading/scripts/`
2. Move `wiki/` to `03-Resources/Wiki/trading-desk-wiki/`
3. Move `archive/` to `04-Archive/archive-legacy/`
4. Move infrastructure packages to `03-Resources/Infrastructure/`
5. Update all path references in documentation
