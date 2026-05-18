# Plan: Phase 1 — Natural-Language Trigger Expansion

**Plan:** [1-PLAN.md](./1-PLAN.md)
**Issue:** [0-ISSUE.md](./0-ISSUE.md)
**Status:** ✅ **COMPLETE**
**Created:** 2026-05-14
**Target Completion:** 2026-05-14

---

## Goal

Expand `config/playbook-index.json` so that everyday English phrases map directly to playbook triggers. Every playbook must have ≥10 natural-language variants (actual target: ≥20).

## Execution Strategy

Decomposed into 3 parallel chunks routed across mounted lab nodes (fnet1, fnet2, fnet3) via SSHFS-mounted workspace.

| Chunk | Lab Node | Playbooks | Count |
|-------|----------|-----------|-------|
| A | fnet1 | 1–12 | 12 |
| B | fnet2 | 13–24 | 12 |
| C | fnet3 | 25–35 | 11 |

## Tasks

### Phase 1.1 — Trigger Expansion (Delegated)

- [x] Add verb-normalized triggers (`run`, `start`, `launch`, `execute`, `fix`, `deploy`)
- [x] Add object-normalized triggers (`wiki` → `run_wiki`, `start_wiki`)
- [x] Add phrase triggers (`run the wiki`, `start the wiki server`)
- [x] Deduplicate within each playbook's triggers array

### Phase 1.2 — Combine & Validate

- [x] Combine 3 chunk outputs into unified `playbook-index.json`
- [x] Validate ≥10 triggers per playbook
- [x] Validate no duplicates per playbook
- [x] Run `validate-playbook-executor.sh` acceptance suite

### Phase 1.3 — Documentation

- [ ] Update `SKILL.md` with natural-language trigger documentation
- [ ] Update `README.md` keyword registry section
- [ ] Create issue home (`0-ISSUE.md`, `1-PLAN.md`, sessions, status, prompts)

## Results

- **35 playbooks** expanded → **865 total triggers** (avg 24.7/playbook, min 21, max 30)
- **playbook-index.json** updated to **v2.1.0**
- **13/13** acceptance tests passed
- **0 cloud model invocations** for execution
- Phase 2 captured as backlogged future session: [`2-PLAN-phase2.md`](./2-PLAN-phase2.md)

## Next Phase

**Phase 2** — Update `AGENTS.md` and `AGENTS-full.md` with broad natural-language keywords for playbook-executor routing.

---

## Navigation

| Need | Location |
|------|----------|
| Issue definition | [0-ISSUE.md](./0-ISSUE.md) |
| Session notes | [sessions/2026-05-14-2001.md](./sessions/2026-05-14-2001.md) |
| Status | [status/2026-05-14-2020-phase1-complete.md](./status/2026-05-14-2020-phase1-complete.md) |
| Prompts | [prompts/2026-05-14-2014-phase1-start.md](./prompts/2026-05-14-2014-phase1-start.md) |
