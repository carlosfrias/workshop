# TI-036 Phase 2 — AGENTS.md Natural-Language Routing Update

**Issue:** TI-036: Playbook-Executor Natural-Language Trigger Expansion
**Captured:** 2026-05-14 20:25 EDT
**Status:** 📋 **BACKLOGGED** (ready for future session)
**Priority:** 🔴 **HIGH**
**Estimated Effort:** 1 hour (formerly Phase 1 → now Phase 2, standalone)

---

## Scope

Update routing tables so that natural-language prompts reach the playbook-executor **before** they fail at the trigger registry layer.

### Gap

| Layer | Current | Gap |
|-------|---------|-----|
| `AGENTS.md` keywords | `playbook-executor, run playbook, execute playbook, service recovery...` | Missing `run the wiki`, `start the wiki`, `deploy pi`, `fix ollama`, `get capacity report` |
| `AGENTS-full.md` | References `packages/playbook-executor/README.md` | Not expanded with per-playbook keyword rows |

### Deliverables

1. **Update `AGENTS.md` keyword row** in technical-infrastructure/AGENTS.md:
   - Expand playbook-executor trigger row with broad natural-language keywords:
   - `run the wiki, start the wiki, serve wiki, deploy pi, install pi, update packages, upgrade packages, backup data, snapshot, restart ollama, reset ollama, fix ollama, fix broken links, configure ssh, setup vpn, add vpn peer, shutdown lab, cleanup lab, gather hardware, capacity report, validate router, optimize lab, run pilot, benchmark lab, test pi installation, test reboot, full pi validation, shutdown nodes, power off, configure sudo, deploy worker, deploy gist worker, deploy chromadb, migrate worker, fix pi availability, fix ollama network`

2. **Add per-playbook keyword rows** (optional, for common playbooks):
   - `wiki, serve wiki, run wiki, start wiki` → `packages/playbook-executor/README.md#serve-wiki`
   - `backup, snapshot, archive, run backup` → `packages/playbook-executor/README.md#backup`

3. **Update `AGENTS-full.md`** in technical-infrastructure/AGENTS-full.md:
   - Add natural-language keyword variants to the playbook-executor routing table
   - Add `packages/playbook-executor/README.md` under "Playbook Executor" with natural-language trigger examples

### Success Criteria
- `"run the wiki"` matches AGENTS.md routing before failing at playbook-index
- Both `AGENTS.md` and `AGENTS-full.md` are consistent (no stale references)

---

## Pre-work (Phase 1) — COMPLETE

Phase 1 trigger expansion done — playbook-index.json has 865 triggers across 35 playbooks.

## Navigation
- Source Issue: [issues/ti036-playbook-nl-triggers/0-ISSUE.md](../issues/ti036-playbook-nl-triggers/0-ISSUE.md)
- Issue Home: [issues/playbook-executor/0-ISSUE.md](../issues/playbook-executor/0-ISSUE.md)
- Plan: [issues/playbook-executor/1-PLAN.md](../issues/playbook-executor/1-PLAN.md)
