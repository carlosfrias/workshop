# SESSION-NOTES-2026-05-03-1945 — Router Config Collision Cleanup + TI-023 Plan

**Date:** 2026-05-03 19:45 ET  
**Node:** orchestrator (friasc)  
**Task:** Clean router config collisions, fix TUI thinking level reporting, document plan  
**Status:** ✅ Phase 1 Complete (P1 fixed, P5 diagnosed, tools created)

---

## What Was Found

Three config files existed in the pi configuration area:

| File | Size | Read by Router? | Role |
|------|------|-----------------|------|
| `./.pi/keyword-router.json` | 4,789 bytes | ✅ Yes | **Project-level (highest priority)** |
| `~/.pi/agent/keyword-router.json` | 2,491 bytes | ✅ Yes (fallback) | Global fallback — merged with project |
| `~/.pi/model-router.json` | 3,820 bytes | ❌ **No** | **Stale — not read by router at all** |

The router extension (`lib/config.ts`) loads configs in this order:
1. Built-in defaults (from extension source code)
2. Global config (`~/.pi/agent/keyword-router.json`) — merged with defaults
3. Project config (`./.pi/keyword-router.json`) — **overrides entire routes**

**The collision:** The project-level config had `default.thinkingLevel: "medium"` which overrode the built-in default `"off"`. This caused the TUI to show "thinking: medium" for ALL routes, including infrastructure which is configured as "off".

Additionally, the stale `~/.pi/model-router.json` file (different filename, not read) created confusion — it had the same content as what I thought was the authoritative config, but the router never loaded it.

---

## Actions Taken

### 1. Fixed Project-Level Config (`./.pi/keyword-router.json`)
- Changed `default.thinkingLevel` from `"medium"` to `"off"`
- Added missing infrastructure keywords: `ansible`, `latency`, `pipeline`, `playbook`, `wiring`
- Verified reasoning route has NO stop-words (`"what"`, `"when"`, etc.)

### 2. Archived Stale Files
- `~/.pi/model-router.json` → `~/.pi/model-router.json.bak.20260503194119`
- `~/.pi/agent/keyword-router.json` → `~/.pi/agent/keyword-router.json.bak.20260503194132`

Rationale: The global fallback serves no purpose over the built-in defaults. Removing it eliminates divergence risk. The project-level config is the single source of truth.

### 3. Created Validation Tool

**Script:** `scripts/validate-router-config.py`
Checks:
- Stale files (model-router.json)
- Global fallback existence
- Default thinking level is "off"
- Reasoning route has no stop-words
- Infrastructure route has all required keywords
- Reasoning priority is 1

**Ansible Playbook:** `technical-infrastructure/ansible/playbooks/validate-router-config.yml`
- Runs validation script on orchestrator
- Reports results with exit code interpretation
- Fails on critical errors

**Usage:**
```bash
# Direct script
python3 scripts/validate-router-config.py

# Via Ansible
cd technical-infrastructure/ansible
ansible-playbook -i localhost, -c local playbooks/validate-router-config.yml
```

**Current result:**
```
🟢 Config is clean.
0 critical, 0 total issues
```

### 4. Updated TI-023 Backlog Entry
Added gap diagnosis and 5 prioritized fixes to `wiki/technical-infrastructure/operational/BACKLOG.md`.

### 5. Created Plan Document
`PLAN-2026-05-03-1930-TI023-AUTO-DECOMPOSE-NODE-DISPATCH.md` with full architecture and implementation order.

---

## Remaining Work (TI-023)

| Phase | Gap | Effort | Status |
|-------|-----|--------|--------|
| 1 | P1 — Fix router keywords | 10 min | ✅ DONE |
| 2 | P5 — Fix TUI thinking level | 30 min | ✅ DONE (config fix) |
| 3 | P2 — Automatic complexity detection | 1-2 hrs | 🔄 Planned |
| 4 | P3 — Wire decomposer into pipeline | 2-3 hrs | 🔄 Planned |
| 5 | P4 — Wire node dispatcher into pipeline | 2-3 hrs | 🔄 Planned |

---

## Files Created/Modified

| File | Action |
|------|--------|
| `.pi/keyword-router.json` | Fixed default thinkingLevel, added keywords |
| `~/.pi/model-router.json` | Archived (stale) |
| `~/.pi/agent/keyword-router.json` | Archived (redundant fallback) |
| `scripts/validate-router-config.py` | Created |
| `technical-infrastructure/ansible/playbooks/validate-router-config.yml` | Created |
| `technical-infrastructure/wiki/operational/planning/PLAN-2026-05-03-1930-TI023-AUTO-DECOMPOSE-NODE-DISPATCH.md` | Created |
| `technical-infrastructure/wiki/operational/BACKLOG.md` | Updated TI-023 |

---

## One-Liner for Future Use

```bash
# Validate router config before any routing work
ansible-playbook -i localhost, -c local technical-infrastructure/ansible/playbooks/validate-router-config.yml
```

---

**Next Review:** When implementing P2 (automatic complexity detection).
