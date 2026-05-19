# playbook-executor: Natural-Language Trigger Expansion

**Issue Home:** [0-ISSUE.md](./0-ISSUE.md)
**Status:** 📋 **PHASE 1 COMPLETE / PHASE 2 BACKLOGGED**
**Priority:** 🔴 **HIGH**
**Created:** 2026-05-14
**Labels:** playbook-executor, ti036, phase-1, natural-language, triggers

---

## Defect Summary

Low-capacity models (2–8B parameters) cannot execute Ansible playbooks from natural-language prompts because `config/playbook-index.json` only maps snake_case technical triggers. The model is instructed "Never reason — Always trigger a playbook," leaving it unable to bridge the semantic gap between "run the wiki" and `serve_wiki`.

## Gap Analysis

| Layer | Current State | Gap |
|-------|--------------|-----|
| `playbook-index.json` triggers | `serve_wiki`, `wiki_server`, `wiki_serve` | Missing `run the wiki`, `start the wiki`, `launch wiki` |
| `playbook-index.json` verbs | None | Missing verb+object expansion (`run`, `start`, `launch`, `fix`, `deploy`) |
| `AGENTS.md` keywords | `playbook-executor, run playbook, execute playbook, service recovery...` | Missing natural-language variants |
| Keyword router | `infrastructure` route with generic keywords | No playbook-executor-specific keywords |
| Low-capacity model | "Never reason" instruction | Cannot bridge semantic gap; returns **E002** |

## Deliverables

- [x] **Phase 1:** Expand `config/playbook-index.json` with ≥10 natural-language synonyms per playbook
- [ ] **Phase 2:** (BACKLOGGED for future session) Update `AGENTS.md` and `AGENTS-full.md` with broad natural-language keywords
- [ ] **Phase 3:** Create `scripts/intent-to-trigger.py` — deterministic bridge from natural language to exact trigger
- [ ] **Phase 4:** Update keyword-router config with playbook-executor route
- [ ] **Phase 5:** Integration validation — 10 natural-language prompts must execute correct playbooks on `qwen3.5:4b`
- [ ] **Phase 6:** Documentation discoverability — linked from `wiki/index.md`, product catalog, prompt-references
- Phase 2 captured in: [`2-PLAN-phase2.md`](./2-PLAN-phase2.md)

## Success Criteria

1. `"run the wiki"` → executes `serve-wiki.yml` on `qwen3.5:4b` with zero reasoning
2. `"deploy pi to the lab"` → executes `deploy-pi.yml`
3. `"fix ollama api"` → executes `fix-ollama-network-bind.yml`
4. `"get capacity report"` → executes `capacity-report.yml`
5. All tests pass without invoking cloud models

## Related

- Parent Plan: [TI-036 — Playbook-Executor Natural-Language Trigger Expansion](../ti036-playbook-nl-triggers/0-ISSUE.md)
- Product Page: [technical-infrastructure/wiki/products/playbook-executor/index.md](../../../products/playbook-executor/index.md)
- Package: [technical-infrastructure/packages/playbook-executor](../../../../packages/playbook-executor/)
- Active Deployment: [TI-041 — Pi Sessions on Lab Nodes](../ti041-pi-sessions-lab-nodes/0-ISSUE.md) — uses `deploy-pi.yml` for cross-node intercom infrastructure

---

## Integration Usage

| Playbook | Consumer | Purpose | Status |
|----------|----------|---------|--------|
| `deploy-pi.yml` | [TI-041](../ti041-pi-sessions-lab-nodes/0-ISSUE.md) | Install Node.js + pi CLI + pi-intercom on fnet1–fnet7 | 🔄 In Progress |
| `serve-wiki.yml` | Wiki server | Serve documentation via HTTP | ✅ Ready |
| `fix-ollama-network-bind.yml` | Ollama recovery | Fix API binding issues | ✅ Ready |
| `capacity-report.yml` | Infrastructure ops | Generate node capacity report | ✅ Ready |

---

## Navigation

| Need | Location |
|------|----------|
| Active plan | [1-PLAN.md](./1-PLAN.md) |
| Session notes | [sessions/](./sessions/) |
| Status snapshots | [status/](./status/) |
| Prompts | [prompts/](./prompts/) |
| Back to backlog | [../../BACKLOG.md](../../BACKLOG.md) |

---

## Cross-Reference: pi-cross-node-comms (added 2026-05-18)

3 coms-net playbooks registered in `playbook-index.json`:

| Trigger | Playbook | Domain |
|---------|----------|--------|
| `deploy_coms_net` | `deploy-fleet.yml` | Full fleet deploy: hub + extension |
| `deploy_coms_hub` | `deploy-hub-to-fnet2.yml` | Hub server → fnet2 only |
| `start_coms_agents` | `start-agents.yml` | pi sessions on 7 lab nodes |

**Vault documentation:** `personal-vault/01-Projects/pi-cross-node-comms/` — assessment, deployment plan, workbench
**Vault mirror:** `personal-vault/03-Resources/Infrastructure/playbook-executor/` — cross-reference hub
