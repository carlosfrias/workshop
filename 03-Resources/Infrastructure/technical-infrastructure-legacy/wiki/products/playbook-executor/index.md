---
title: playbook-executor
sidebar: auto
---

# playbook-executor

## Overview

**Type:** Skill + CLI Package  
**Purpose:** Ansible playbook execution triggered by natural-language keywords, designed for low-capacity local models.  
**Install:** `pi install github:carlosfrias/playbook-executor`  

The playbook-executor closes the "last mile" gap between a user's natural-language request (e.g., *"run the wiki"*) and the execution of the correct Ansible playbook. It is intentionally built for models with **2–8B parameters** that cannot perform deep intent reasoning.

---

## Problem Statement

### Symptom
When a user types a natural-language prompt such as:

> *"run the wiki"*  
> *"start the wiki server"*  
> *"deploy pi to the lab"*

…the playbook-executor is **never reached**.

### Root Cause Analysis

| Layer | What Happens | Why It Fails |
|-------|-------------|--------------|
| **User Input** | "run the wiki" | Natural language, no snake_case keywords |
| **Keyword Router** | Routes to `infrastructure` or `simple` route | No playbook-specific trigger routing |
| **AGENTS.md** | Prompt-Triggered References checked | Keywords: `playbook-executor, run playbook, execute playbook, service recovery, API failure, restart service, node remediation, fnet failure, HTTP 000, health-aware execution` — **"run the wiki" matches none** |
| **playbook-index.json** | Triggers checked against user input | Triggers are `serve_wiki, wiki_server, wiki_serve` — **"run the wiki" matches none** |
| **Low-Capacity Model** | Told *"Never reason — Always trigger a playbook"* | Cannot bridge the semantic gap; returns **E002 No playbook matched** |

### Core Gap

The entire pipeline assumes one of two things:
1. The user types exact snake_case trigger keywords (`serve_wiki`, `deploy_pi`), or
2. A high-capacity model reasons about intent and translates natural language to triggers.

Neither assumption holds in practice. Users speak naturally, and the target models for this package are **explicitly prevented from reasoning**.

---

## Design Principles

| Principle | Rationale |
|-----------|-----------|
| **Exact-match first** | Low-capacity models thrive on lookup tables, not inference |
| **Natural-language synonym expansion** | Every playbook trigger must include plain-English variants |
| **No reasoning required** | The model sees `input → exact trigger → playbook path`; nothing else |
| **Health-aware but not health-dependent** | Playbooks marked `health_aware: true` get a pre-flight check; others execute immediately |
| **Fail fast with suggestions** | If no match, return E002 with a ranked list of closest triggers |

---

## Architecture

```
User Input
    │
    ▼
┌──────────────────────────────┐
│  Phase 0: Intent Expansion   │  ← NEW (this plan)
│  Natural Language → Triggers │
│  • synonym table (JSON)      │
│  • fuzzy prefix matching     │
│  • verb normalization        │
└───────────┬──────────────────┘
            │
    ┌───────┴───────┐
    │ Exact Match?  │
    └───────┬───────┘
       YES /  NO
       │      │
       ▼      ▼
┌─────────┐ ┌─────────────────────────────┐
│ HEALTH  │ │  Phase 0b: Suggestion Rank  │
│ CHECK   │ │  Return E002 + top-3        │
│ (if     │ │  similar triggers           │
│ needed) │ │                             │
└────┬────┘ └─────────────────────────────┘
     │
     ▼
┌──────────────────────────┐
│ EXECUTION                │
│ ansible-playbook <path>  │
└──────────────────────────┘
```

---

## Implementation Plan

### Phase 1 — Natural Language Trigger Expansion *(Critical Path)*

**Goal:** Enrich `config/playbook-index.json` so that everyday English phrases map directly to playbook triggers.

**Tasks:**
1. **Add verb-normalized triggers**
   - For every playbook, add triggers for common action verbs:
     - `run`, `start`, `launch`, `execute` → prefixed/suffixed variants
     - `stop`, `kill`, `shutdown` → where applicable
     - `fix`, `repair`, `resolve` → for remediation playbooks
     - `get`, `show`, `generate`, `produce` → for report playbooks

2. **Add object-normalized triggers**
   - "wiki" → `serve_wiki`, `run_wiki`, `start_wiki`, `wiki_server`, `wiki_serve`
   - "pi" → `deploy_pi`, `install_pi`, `update_pi`, `setup_pi`, `pi_install`
   - "backup" → `backup`, `backup_data`, `snapshot`, `archive`, `run_backup`

3. **Add phrase triggers**
   - `run the wiki` → `serve_wiki`
   - `start the wiki server` → `serve_wiki`
   - `deploy pi to the lab` → `deploy_pi`
   - `update all packages` → `update`
   - `restart ollama` → `cleanup_ollama` (service reset)
   - `fix broken symlinks` → `fix_broken_links`

**Deliverable:** Updated `config/playbook-index.json` with every trigger expanded to ≥10 natural-language variants.

**Estimated Effort:** 2–3 hours

---

### Phase 2 — AGENTS.md Prompt-Triggered Reference Expansion

**Goal:** Ensure natural-language prompts hit the AGENTS.md routing table before failing.

**Tasks:**
1. **Expand the playbook-executor keyword row** in `AGENTS.md`:

   **Current:**  
   `playbook-executor, run playbook, execute playbook, service recovery, API failure, restart service, node remediation, fnet failure, HTTP 000, health-aware execution`

   **Expanded:**  
   `run the wiki, start the wiki, serve wiki, deploy pi, install pi, update packages, upgrade packages, backup data, snapshot, restart ollama, reset ollama, fix ollama, fix broken links, configure ssh, setup vpn, add vpn peer, shutdown lab, cleanup lab, gather hardware, capacity report, validate router, optimize lab, run pilot, benchmark lab, test pi installation, test reboot, full pi validation, shutdown nodes, power off, configure sudo, deploy worker, deploy gist worker, deploy chromadb, migrate worker, fix pi availability, fix ollama network`

2. **Add per-playbook keyword rows** (optional, for very common playbooks):
   - `wiki, serve wiki, run wiki, start wiki` → `packages/playbook-executor/README.md#serve-wiki`
   - `backup, snapshot, archive` → `packages/playbook-executor/README.md#backup`

**Deliverable:** Updated `AGENTS.md` and `AGENTS-full.md` with broad natural-language coverage.

**Estimated Effort:** 1 hour

---

### Phase 3 — Intent→Trigger Bridge Script *(New Component)*

**Goal:** A deterministic, zero-reasoning script that translates natural-language input into an exact playbook trigger.

**Design:**
```python
# scripts/intent-to-trigger.py
# Usage: python3 intent-to-trigger.py "run the wiki"
# Output: {"trigger": "serve_wiki", "confidence": 1.0, "method": "exact"}
```

**Matching Strategy (in priority order):**
1. **Exact substring match** — if input contains any trigger verbatim (case-insensitive, word-bounded)
2. **Verb + object expansion** — normalize verbs (`run`, `start`, `launch` → `execute`; `get`, `show` → `report`) and match against trigger synonyms
3. **Fuzzy prefix match** — Levenshtein distance ≤ 2 on trigger words
4. **Ranked suggestions** — if no match above threshold, return top-3 closest triggers

**Integration Point:**
- `run-playbook.sh` calls `intent-to-trigger.py` first, then falls back to direct trigger lookup if a trigger is returned
- The core-prompt.md is updated to instruct models to use `./scripts/run-playbook.sh "<natural language>"`

**Deliverable:**
- `scripts/intent-to-trigger.py`
- Unit tests in `scripts/test-intent-to-trigger.py`
- Updated `run-playbook.sh` with bridge integration

**Estimated Effort:** 3–4 hours

---

### Phase 4 — Low-Capacity Model Routing Fix

**Goal:** Ensure prompts that should reach playbook-executor are routed to models capable of exact-match lookup (not cloud reasoning models).

**Tasks:**
1. **Add `playbook-executor` route to keyword-router.json** (or mark as infrastructure sub-route)
   - Keywords: `run playbook, execute playbook, run the, start the, launch the, deploy the, fix the, configure the`
   - Model: `qwen3.5:4b` (trivial/simple route; exact-match lookup only)
   - Priority: 1 (low, so it doesn't override domain detection)

2. **Ensure the playbook-executor core-prompt is ≤300 tokens** (already true; maintain this constraint)
   - Core prompt: ~150 tokens
   - Playbook index (cached): ~50 tokens
   - Headroom for response: ~100 tokens

3. **Test with target models:**
   - `qwen3.5:4b`
   - `gemma4:e4b`
   - `Phi-3` (if available)

**Deliverable:** Verified keyword-router config + model smoke-test results.

**Estimated Effort:** 2–3 hours

---

### Phase 5 — Integration Validation

**Goal:** Prove the full pipeline works end-to-end with natural-language input.

**Test Matrix:**

| Input | Expected Playbook | Model | Health Check? |
|-------|------------------|-------|---------------|
| `"run the wiki"` | `serve-wiki.yml` | qwen3.5:4b | No |
| `"start the wiki server"` | `serve-wiki.yml` | qwen3.5:4b | No |
| `"deploy pi to the lab"` | `deploy-pi.yml` | qwen3.5:4b | Yes |
| `"update all packages"` | `update_packages_v1.0.yml` | qwen3.5:4b | Yes |
| `"restart ollama"` | `cleanup-ollama.yml` | qwen3.5:4b | Yes |
| `"fix broken links"` | `fix-broken-links.yml` | qwen3.5:4b | No |
| `"get capacity report"` | `capacity-report.yml` | qwen3.5:4b | No |
| `"deploy gist workers"` | `deploy-gist-worker.yml` | qwen3.5:4b | Yes |
| `"shutdown lab"` | `shutdown-lab-nodes.yml` | qwen3.5:4b | No |
| `"run backup"` | `backup_data_v1.0.yml` | qwen3.5:4b | Yes |

**Deliverable:** `./scripts/validate-playbook-executor.sh` updated with natural-language test cases and all tests passing.

**Estimated Effort:** 2–3 hours

---

### Phase 6 — Documentation & Discoverability

**Goal:** The plan itself, the product, and the backlog must be findable from every navigation path.

**Tasks:**
1. **Update this product page** (`technical-infrastructure/wiki/products/playbook-executor/index.md`) — ✅ In progress
2. **Update product catalog** (`technical-infrastructure/wiki/products/index.md`) — Add playbook-executor row
3. **Add to AGENTS.md routing table** — "playbook execution" as a first-class domain trigger
4. **Add to AGENTS-full.md** — `packages/playbook-executor/README.md` under "Playbook Executor"
5. **Add to wiki/guides/prompt-references.md** — Natural-language keyword examples
6. **Create backlog item** in `technical-infrastructure/wiki/operational/BACKLOG.md`
7. **Link from master index** (`wiki/index.md`) — Backlog summary row update

**Deliverable:** All navigation paths lead to playbook-executor documentation from any reasonable starting point.

**Estimated Effort:** 1 hour

---

## Files & Assets

| File | Purpose | Status |
|------|---------|--------|
| `config/playbook-index.json` | Trigger → Playbook registry | ✅ Exists, needs expansion |
| `scripts/run-playbook.sh` | CLI executor with keyword fallback | ✅ Exists, needs intent bridge |
| `scripts/health-check.sh` | Pre-flight health check | ✅ Exists |
| `prompts/core-prompt.md` | Low-capacity model instructions | ✅ Exists, needs verb examples |
| `skills/playbook-executor/SKILL.md` | pi installable skill | ✅ Exists |
| **NEW:** `scripts/intent-to-trigger.py` | NLP → trigger bridge | 🆕 Phase 3 |
| **NEW:** `scripts/test-intent-to-trigger.py` | Unit tests for bridge | 🆕 Phase 3 |
| **NEW:** `config/natural-language-synonyms.json` | Verb/object synonym table | 🆕 Phase 1 |

---

## Success Criteria

> A user can type `"run the wiki"` and the correct playbook executes within 5 seconds on `qwen3.5:4b` with zero cloud cost.

1. ✅ `"run the wiki"` → `ansible-playbook serve-wiki.yml`
2. ✅ `"start the wiki server"` → `ansible-playbook serve-wiki.yml`
3. ✅ `"deploy pi to the lab"` → `ansible-playbook deploy-pi.yml`
4. ✅ `"fix ollama api"` → `ansible-playbook fix-ollama-network-bind.yml`
5. ✅ `"get capacity report"` → `ansible-playbook capacity-report.yml`
6. ✅ All tests pass on `qwen3.5:4b` without reasoning
7. ✅ No cloud model invoked for any of the above prompts
8. ✅ Documentation discoverable from `wiki/index.md`, `AGENTS.md`, and `AGENTS-full.md`

---

## Related

- [pi-keyword-router](../pi-keyword-router) — Model routing that must include playbook-executor triggers
- [health-monitor](../health-monitor) — Pre-flight health checks for `health_aware: true` playbooks
- [decomposition-skill](../decomposition-skill) — If a prompt is too complex for direct playbook mapping
- [Routing Transparency](../routing-transparency) — Audit trail for every execution

---

**Plan ID:** TI-036  
**Status:** 📋 **PLANNED**  
**Created:** 2026-05-13  
**Priority:** 🔴 **HIGH**  
**Estimated Total Effort:** 11–15 hours  
**Target Completion:** 2026-05-20
