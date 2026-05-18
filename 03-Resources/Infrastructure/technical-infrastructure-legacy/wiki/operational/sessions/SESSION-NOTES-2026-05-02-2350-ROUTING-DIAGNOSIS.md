# Session Notes: Routing Failure Diagnosis & Multi-Issue Resolution
**Date:** 2026-05-02 23:50 ET  
**Status:** 🔴 Critical Issues Identified  
**Session:** TI-011-Routing-Diagnosis

## Issues Diagnosed

### Issue 1: Keyword Router Extension Not Installed ❌
**Symptom:** "decompose" keyword didn't trigger routing. Prompt ran on local qwen3.5:4b without orchestration.

**Root Cause:** `.pi/extensions/` only contains `README.md` — the actual extension code is NOT present.

```
.pi/extensions/
├── README.md      ← Only file (instructions)
└── (NO pi-keyword-router/ directory)
```

**Expected location:** `.pi/extensions/pi-keyword-router/index.ts` (and lib/ folder)
**Actual location:** `technical-infrastructure/extensions/pi-keyword-router/` (repo source)

**Why it matters:** Without the extension, pi has no keyword routing, no complexity classification, no AGENTS.md domain loading, and no model switching. Every prompt runs on whatever model is currently selected.

### Issue 2: AGENTS.md Too Large for Low Models ⚠️
**Symptom:** Latency when processing AGENTS.md on qwen3.5:4b

**Data:**
- File: `technical-infrastructure/AGENTS.md`
- Size: **21,850 bytes** (345 lines)
- Estimated tokens: **~5,429 tokens**
- Context limit: qwen3.5:4b = 131,072 → fits but consumes 4% of context
- **Real issue:** Not size, but the file is loaded in EVERY prompt because domain routing is broken (extension not installed)

### Issue 3: Multiple model-router.json Files 🔀
**Locations found:**
| File | Purpose | Status |
|------|---------|--------|
| `.pi/model-router.json` | Old pi model-router extension config | **DEPRECATED** |
| `~/.pi/agent/model-router.json` | Global model-router config | **DEPRECATED** |
| `lab-specs/node-configs/{fnet1-7}/model-router.json` | Per-node routing profiles | **ACTIVE** (for NodeRegistry) |
| `.pi/keyword-router.json` | **NEW** keyword-router extension config | **ACTIVE** (replaces model-router) |

**What happened:** The model-router.json was the old pi extension config. We replaced it with keyword-router.json when building the new extension. But the old files lingered.

### Issue 4: Domain Activation Not Working ❌
**Symptom:** Model didn't acknowledge reading AGENTS.md

**Root Cause:** The AGENTS.md domain activation check is part of the orchestration prompt template. If the extension isn't running, the domain check doesn't execute. The model just processes the raw prompt without loading any domain context.

**How it SHOULD work:**
```
User: "decompose this complex question..."
    ↓
[classify_prompt.py detects "decompose"]
    ↓
[Domain check: keywords "decompose, model-router, AGENTS.md" → technical-infrastructure]
    ↓
[Read technical-infrastructure/AGENTS.md]
    ↓
[Route to appropriate model via keyword-router.json]
```

**How it ACTUALLY works (broken):**
```
User: "decompose this complex question..."
    ↓
[No extension running]
    ↓
[Runs on currently selected model: qwen3.5:4b]
    ↓
[No domain context, no routing, no AGENTS.md]
```

## Resolution Plan

### Fix 1: Install Keyword Router Extension
```bash
pi install github:carlosfrias/pi-keyword-router
```
OR (local dev):
```bash
pi install ../technical-infrastructure/extensions/pi-keyword-router
```

### Fix 2: Clean Up model-router.json Files
- Delete `.pi/model-router.json` (old, superseded)
- Delete `~/.pi/agent/model-router.json` (old, superseded)
- Keep ONLY `.pi/keyword-router.json` (new extension)
- Keep `lab-specs/node-configs/*/model-router.json` (NodeRegistry per-node profiles)

### Fix 3: Modular AGENTS.md (for Low Model Efficiency)
Split AGENTS.md into 3 files:
- `AGENTS.md` — Core rules + quality checklist only (~100 lines)
- `AGENTS-full.md` — Complete documentation with all conventions
- `AGENTS-routing.md` — Domain routing table + prompt-triggered references

Low models load `AGENTS.md` (lightweight). When complexity > MEDIUM, load `AGENTS-full.md`.

### Fix 4: Verify Routing After Install
Test prompts:
1. "decompose this task" → Should trigger reasoning route → qwen3.5:397b-cloud
2. "check if fnet3 is online" → Should trigger monitoring route → qwen3.5:4b
3. "write an ansible playbook" → Should trigger infrastructure route → qwen3:8b

## Evidence

### Extension Status
```
$ ls -la .pi/extensions/
README.md    ← Only file
```

### Config Files
```
$ ls -la .pi/*.json
keyword-router.json    ← 4,789 bytes (correct, new extension)
model-router.json      ←   795 bytes (old, should delete)

$ ls -la ~/.pi/agent/*.json
model-router.json      ← 5,597 bytes (old, should delete)
settings.json          ←   811 bytes (pi settings)
models.json            ← 3,020 bytes (model definitions)
```

### AGENTS.md Size
```
$ wc -c technical-infrastructure/AGENTS.md
21850 bytes
$ python3 -c "print(f'{open('AGENTS.md').read().__len__()//4} tokens')"
5429 tokens
```

## Git Commit Required
- Delete old model-router.json files
- Install extension (or document install command)
- Create modular AGENTS.md split
- Update BACKLOG.md with routing fix

## Backlog Items
- TI-026: Install and verify keyword-router extension
- TI-027: Modular AGENTS.md for low model efficiency
- TI-028: Clean up deprecated model-router.json files
