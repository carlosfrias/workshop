# TI-041: Pi Sessions on Lab Nodes — Issue Home

**Status:** In Progress (Phase 1)  
**Created:** 2026-05-14  
**Owner:** ti041-plan-executor (kimi-k2.6)  
**Orchestrator:** qwen3.5:397b-cloud  
**Domain:** technical-infrastructure  

---

## Objective

Deploy and validate pi coding agent sessions across all 7 lab nodes (fnet1–fnet7) with:
- Node.js v20+ runtime
- pi CLI v0.74.0
- systemd auto-restart persistence
- intercom coordination readiness

---

## Phase Plan

| Phase | Status | Description |
|-------|--------|-------------|
| **Phase 1** | 🟡 In Progress | Verify pi on fnet1–fnet7, fix broken nodes |
| **Phase 2** | ⚪ Pending | Configure systemd auto-restart, test crash recovery |
| **Phase 3** | ⚪ Pending | Full chain e2e test (zero non-playbook commands) |
| **Phase 4** | ⚪ Pending | Production handoff |
| **Phase 5** | ⚪ Pending | Documentation + session notes |

---

## Node Status Matrix

| Node | Node.js | pi Version | Status | Last Updated |
|------|---------|-----------|--------|--------------|
| fnet1 | v20 | 0.70.2 → 0.74.0 | ✅ Upgraded | 2026-05-15 00:00 |
| fnet2 | v20 | 0.73.1 → 0.74.0 | ✅ Upgraded | 2026-05-15 00:00 |
| fnet3 | v20 | 0.74.0 | ✅ Ready | 2026-05-14 23:00 |
| fnet4 | v20 | broken → 0.74.0 | ✅ Upgraded | 2026-05-15 00:00 |
| fnet5 | v18 → v20.20.2 | broken → 0.74.0 | ✅ Upgraded | 2026-05-15 00:00 |
| fnet6 | v20 | 0.74.0 | ✅ Ready | 2026-05-14 23:00 |
| fnet7 | v22 | 0.74.0 | ✅ Ready | 2026-05-14 23:00 |

---

## Playbooks Created/Updated

### New Playbooks (TI-041)
- `check-node-version.yml` — Verify Node.js v20+ (fixed version comparison bug)
- `deploy-pi.yml` — Install/upgrade pi CLI (fixed version comparison bug)
- `verify-pi.yml` — Confirm pi version + PATH
- `verify-intercom.yml` — Handshake test
- `configure-pi-service.yml` — Deploy systemd unit
- `restart-pi-service.yml` — Crash recovery
- `test-auto-restart.yml` — Crash simulation + verify
- `test-full-chain.yml` — E2E zero-SSH validation

### Updated Playbooks
- `install-nodejs.yml` — Direct installation from nodejs.org (not Ubuntu repos)

### Bug Fixes Applied
1. **Version comparison bug** — Ansible `version()` test requires string comparison, not direct version test on strings with 'v' prefix
   - Fixed in: `check-node-version.yml`, `deploy-pi.yml`
   - Root cause: `node_current.stdout is version('20.0.0', '<')` fails when stdout is `v20.20.2`
   - Fix: `(node_current.stdout | regex_replace('^v', '')) is version('20.0.0', '<')`

2. **Empty version comparison** — When `pi_current` fails (not installed), comparison fails
   - Fixed in: `deploy-pi.yml`
   - Fix: Check for empty string before version comparison

3. **Ubuntu repo Node.js version** — Ubuntu Noble repos have outdated Node.js
   - Fixed in: `install-nodejs.yml`
   - Fix: Download directly from nodejs.org official distribution

---

## Activity Log

### 2026-05-15 00:00 — pi Deployment Complete on fnet1, fnet2, fnet4, fnet5 ✅
- **Action:** Ran `deploy-pi.yml` on fnet1, fnet2, fnet4, fnet5
- **Result:** All nodes upgraded from 0.70.2/0.73.1/broken → v0.74.0
- **Bug Fixes Applied:**
  1. `pi --version` outputs to stderr, not stdout — fixed version detection
  2. Old @mariozechner/pi-coding-agent blocking upgrade — added uninstall step
  3. Symlink conflict between /usr/local/bin and /home/friasc/.npm-global — cleanup added
- **JSON Evidence:**
```json
{"node_id": "fnet1", "pi_version": "0.74.0", "node_version": "v20.20.2", "status": "ok"}
{"node_id": "fnet2", "pi_version": "0.74.0", "node_version": "v20.20.2", "status": "ok"}
{"node_id": "fnet4", "pi_version": "0.74.0", "node_version": "v20.20.2", "status": "ok"}
{"node_id": "fnet5", "pi_version": "0.74.0", "node_version": "v20.20.2", "status": "ok"}
```

### 2026-05-14 23:45 — fnet5 Node.js Upgrade Complete ✅
- **Action:** Ran `install-nodejs.yml` on fnet5
- **Result:** v18.19.1 → v20.20.2, npm 10.8.2
- **Method:** Direct download from nodejs.org (bypasses Ubuntu repo limitations)
- **JSON Evidence:**
```json
{
  "node_id": "fnet5",
  "node_version": "v20.20.2",
  "npm_version": "10.8.2",
  "target_version": "v20.x",
  "status": "ok"
}
```

### 2026-05-14 23:50 — Playbook Bug Fixes
- **Action:** Fixed version comparison bugs in `check-node-version.yml` and `deploy-pi.yml`
- **Root Cause:** Ansible `version()` test requires clean version strings (no 'v' prefix)
- **Fix Applied:** Added `regex_replace('^v', '')` filter before version comparisons
- **Files Modified:**
  - `ansible/playbooks/check-node-version.yml`
  - `ansible/playbooks/deploy-pi.yml`
  - `ansible/playbooks/install-nodejs.yml` (rewrote for direct nodejs.org install)

### 2026-05-14 23:55 — Documentation Created
- **Action:** Created issue home per doc-standards
- **Location:** `wiki/operational/issues/TI-041/0-ISSUE.md`
- **Standards Applied:** [S-TIGHT] header, relative paths, timestamps, structured activity log

---

## Next Actions

1. **Deploy pi to fnet1, fnet2, fnet4, fnet5** — Run `deploy-pi.yml`
2. **Verify intercom on all 7 nodes** — Run `verify-intercom.yml`
3. **Configure systemd service** — Run `configure-pi-service.yml` (Phase 2)
4. **Test auto-restart** — Run `test-auto-restart.yml` (Phase 2)

---

## Related Files

| File | Purpose |
|------|---------|
| `ansible/playbooks/deploy-pi.yml` | pi CLI installation |
| `ansible/playbooks/check-node-version.yml` | Node.js version verification |
| `ansible/playbooks/install-nodejs.yml` | Node.js direct installation |
| `packages/playbook-executor/config/playbook-index.json` | Trigger registry |
| `../../AGENTS.md` | Domain conventions |

---

*Issue home follows doc-standards CORE.md — single canonical location, full lifecycle immutability (append-only), relative paths.*
