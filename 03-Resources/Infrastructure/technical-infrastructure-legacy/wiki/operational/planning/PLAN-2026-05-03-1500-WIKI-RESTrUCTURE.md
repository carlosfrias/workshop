# PLAN-2026-05-03 — Wiki Restructure + Search Implementation

**Date:** 2026-05-03 15:00 ET  
**Status:** Phase 1 Complete — root-level wiki consolidation, search, nav hub, and playbook all verified  
**Complexity:** MEDIUM

---

## Problem

- `WIKI.md` is the runtime navigation hub but is manually maintained and drifts out of sync
- `wiki/index.md` (VitePress home page) uses stale hero layout and doesn't reflect actual content
- No search capability — operators must grep files or remember paths
- Growing volume of operational docs (STATUS, SESSION-NOTES, PLAN, recommendations) with no index
- `project-blueprint` / trading desk docs are scattered, not cross-linked
- Top nav (VitePress) doesn't match side nav (hierarchical file structure)
- The wiki is currently served from `technical-infrastructure/wiki-build/`, which only covers that domain — the root `wiki/` holds the unified content but has no launch path

## Solution

**Unify the wiki at the root level.** The root `wiki/` already contains all content (trading desk docs, operations, model assignment, and a symlink into `technical-infrastructure/wiki/`). The root `.vitepress/config.js` already serves it. We just need to make it the primary, functional site.

1. **Consolidate launch to root** — Retire `technical-infrastructure/wiki-build/` as the serve point; start VitePress from the project root
2. **Wiki home page rewrite** — `wiki/index.md` becomes a functional, searchable nav hub (no hero layout)
3. **Search implementation** — Enable VitePress `local` search in root `.vitepress/config.js`; add optional CLI script for grep-style fallback
4. **Auto-generated operational index** — STATUS, SESSION-NOTES, PLAN auto-listing
5. **Side nav alignment** — Root `.vitepress/config.js` sidebar matches the actual `wiki/` directory tree (trading-desk, operations, technical-infrastructure via symlink)
6. **Trading desk / project-blueprint cross-links** — WIKI.md and nav hub point to project-blueprint docs

---

## Decomposition

| Step | Sub-Task | Model | Node | Latency | Fallback |
|------|----------|-------|------|---------|----------|
| 1 | Update root `package.json` with VitePress scripts | qwen3.5:4b | orchestrator | 1s | qwen3:8b |
| 2 | Rewrite `wiki/index.md` as functional nav hub | qwen3.5:4b | orchestrator | 2s | qwen3:8b |
| 3 | Enable search in root `.vitepress/config.js` + align sidebar | deepseek-v4-pro | cloud | 8s | qwen3.5:397b |
| 4 | Update `bring-up-wiki.sh` to start from project root | qwen3.5:4b | orchestrator | 1s | qwen3:8b |
| 5 | Update `WIKI.md` with auto-generated operational index | qwen3.5:4b | orchestrator | 1s | qwen3:8b |
| 6 | Add project-blueprint / trading desk cross-links | qwen3.5:4b | orchestrator | 1s | qwen3:8b |
| 7 | Validate all links with `npx vitepress dev` | shell | orchestrator | 5s | manual |
| 8 | (Optional) Retire `technical-infrastructure/wiki-build/` as primary serve point | shell | orchestrator | 1s | manual |

---

## Acceptance Criteria

- [x] `npm run dev` (or `pnpm dev`) from the project root starts the unified wiki at `http://localhost:5173/`
- [x] `wiki/index.md` renders a functional nav hub (not marketing hero)
- [x] VitePress `local` search is enabled and indexes all `.md` files under `wiki/`
- [x] `.vitepress/config.js` side nav matches the actual `wiki/` directory tree
- [~] `WIKI.md` operational index is auto-generated (not manual) — *home page has manual listings; auto-generation deferred*
- [x] All 7+ STATUS files discoverable from home page
- [x] All 10+ SESSION-NOTES discoverable from home page
- [x] All 9+ PLAN files discoverable from home page
- [x] `bring-up-wiki.sh` starts from the root, not `technical-infrastructure/wiki-build/`
- [x] `technical-infrastructure/` docs remain accessible via `wiki/technical-infrastructure/` symlink
- [x] Ansible playbook `serve-wiki.yml` brings wiki up from project root
- [x] `bring-up-wiki.sh` toggle/start/stop/status all work correctly

---

## Risks

| Risk | Mitigation |
|------|-----------|
| VitePress config syntax errors | Validate with `npx vitepress dev` before committing |
| Symlinked `srcDir` build failures | Dev mode confirmed working; defer static build to upstream fix |
| Search index bloat | Limit to .md files, exclude generated artifacts |
| Broken cross-links | Run link validator as harness test |

---

*Created: 2026-05-03 15:00 ET*
*Updated: 2026-05-03 — clarified root-level consolidation*
