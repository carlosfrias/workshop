# TI-036: Playbook-Executor Natural-Language Trigger Expansion

**Issue Home:** [0-ISSUE.md](./0-ISSUE.md)
**Status:** TBD
**Priority:** TBD

---

### TI-036: Playbook-Executor Natural-Language Trigger Expansion
**Created:** 2026-05-13
**Status:** 📋 **PLANNED**
**Priority:** 🔴 **HIGH** — Low-capacity models cannot execute playbooks from natural-language prompts; breaks the "exact-match" execution promise
**Rationale:** The playbook-executor package is designed for 2–8B parameter models with a strict "Never reason — Always trigger" policy. However, the trigger registry (`config/playbook-index.json`) and the AGENTS.md routing table only map snake_case composite keywords and narrow technical phrases. When a user types `"run the wiki"`, `"start the wiki server"`, or `"deploy pi to the lab"`, none of the pipeline layers match. The keyword router does not route to playbook-executor, AGENTS.md keywords do not match, and the playbook index triggers are too literal. This leaves low-capacity models unable to perform the single task they are optimized for.

**Gap Analysis:**
| Layer | Current State | Gap |
|-------|--------------|-----|
| `playbook-index.json` triggers | `serve_wiki`, `wiki_server`, `wiki_serve` | Missing `run the wiki`, `start the wiki`, `launch wiki` |
| `playbook-index.json` verbs | None | Missing verb+object expansion (`run`, `start`, `launch`, `fix`, `deploy`) |
| `AGENTS.md` keywords | `playbook-executor, run playbook, execute playbook, service recovery...` | Missing natural-language variants |
| Keyword router | `infrastructure` route with generic keywords | No playbook-executor-specific keywords |
| Low-capacity model | "Never reason" instruction | Cannot bridge semantic gap; returns **E002** |

**Deliverables:**
- [ ] **Phase 1:** Expand `config/playbook-index.json` with ≥10 natural-language synonyms per playbook (verb + object + phrase triggers)
- [ ] **Phase 2:** Update `AGENTS.md` and `AGENTS-full.md` with broad natural-language keywords for playbook-executor
- [ ] **Phase 3:** Create `scripts/intent-to-trigger.py` — deterministic bridge from natural language to exact trigger
- [ ] **Phase 4:** Update keyword-router config with playbook-executor route (or sub-keywords under infrastructure)
- [ ] **Phase 5:** Integration validation — 10 natural-language prompts must execute correct playbooks on `qwen3.5:4b`
- [ ] **Phase 6:** Documentation discoverability — linked from `wiki/index.md`, product catalog, prompt-references

**Success Criteria:**
1. `"run the wiki"` → executes `serve-wiki.yml` on `qwen3.5:4b` with zero reasoning
2. `"deploy pi to the lab"` → executes `deploy-pi.yml`
3. `"fix ollama api"` → executes `fix-ollama-network-bind.yml`
4. `"get capacity report"` → executes `capacity-report.yml`
5. All tests pass without invoking cloud models

**Plan Document:** [`technical-infrastructure/wiki/products/playbook-executor/index.md`](../../../wiki/products/playbook-executor/index.md)

**Estimated Effort:** 11–15 hours
**Target Completion:** 2026-05-20

---

---

## Navigation

| Need | Location |
|------|----------|
| Back to backlog | [../BACKLOG.md](../BACKLOG.md) |
