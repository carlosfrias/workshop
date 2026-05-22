# Documentation Loading and Backlog Management

**Section ID:** documentation-loading  
**Size:** ~1.5KB  
**LOD:** Low  
**Purpose:** Context-optimized documentation loading strategy and backlog management conventions.

---

## [S-TIGHT]

AGENTS-full.md is now a modular index (~100 lines) linking to topic-specific sections. Use the Loading Strategy table to load only what's needed by task type. Backlog and session tracking live in the personal-vault, not in this workspace.

---

## Full Documentation

**AGENTS-full.md** is now a **modular index** (~100 lines) that links to topic-specific sections.

### Loading Strategy

[LOD: Low]

| Task Type | Load This | Context Cost |
|-----------|-----------|--------------|
| **Publishing work** | `../personal-vault/03-Resources/Technical-Infrastructure/` | ~50 lines |
| **Ansible work** | `../personal-vault/03-Resources/Technical-Infrastructure/Operations/` | ~90 lines |
| **Orchestration work** | `../personal-vault/03-Resources/Technical-Infrastructure/` | ~100 lines |
| **Orchestrator-specific** | `../personal-vault/03-Resources/Technical-Infrastructure/` | ~80 lines |
| **Planning work** | `../personal-vault/01-Projects/Carlos-Trading-Desk/planning/` | ~20 lines |
| **Completing tasks** | `../personal-vault/01-Projects/` | ~50 lines |

**Typical load:** 50-150 lines (vs. 546+ lines for monolithic file)

### Quick Access

- **Full Index:** [`AGENTS-full.md`](AGENTS-full.md) — Context-optimized documentation map
- **Model Routing:** [`AGENTS-routing.md`](AGENTS-routing.md) — Model tier configuration

## Backlog Management

**Documentation home:** `../personal-vault/` — backlog and session tracking follow vault-native conventions.

**Active Backlog:** Tracked in `../personal-vault/01-Projects/Carlos-Trading-Desk/Overview.md`

---

*Load [routing-tables.md](./routing-tables.md) for domain and prompt-triggered routing. Load [conventions-and-rules.md](./conventions-and-rules.md) for behavioral rules.*