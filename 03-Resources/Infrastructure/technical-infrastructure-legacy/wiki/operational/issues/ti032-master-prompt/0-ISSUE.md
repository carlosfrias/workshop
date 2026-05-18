# TI-032: Integrated Health-Aware Playbook Monitoring System (Master Prompt)

**Issue Home:** [0-ISSUE.md](./0-ISSUE.md)
**Status:** TBD
**Priority:** TBD

---

### TI-032: Integrated Health-Aware Playbook Monitoring System (Master Prompt)
**Created:** 2026-05-05  
**Status:** 🔄 **IN PROGRESS** — Phase 0 Foundation started  
**Priority:** 🔴 **CRITICAL** — Non-negotiable safety guardrail  
**Rationale:** Merges TI-031 Health Monitoring, Master Prompt Monitoring, and ASSESSMENT-TI031-MASTER-PROMPT-GAPS.md into single cohesive system. Prevents orchestrator saturation through unified health checks, automatic decomposition, node recovery timeouts, and tiered cloud escalation.

**Supersedes:**
- [TI-PLAYBOOK-MASTER](#ti-playbook-master-master-prompt-for-playbook-keyword-system-with-wiki-documentation) — Items integrated
- [PLAN-TI031-INTEGRATION-v1.0.md](./planning/PLAN-TI031-INTEGRATION-v1.0.md) — Archived
- [ASSESSMENT-TI031-MASTER-PROMPT-GAPS.md](./planning/ASSESSMENT-TI031-MASTER-PROMPT-GAPS.md) — Archived

**Phase 0 Deliverables (IN PROGRESS):**
- [ ] `technical-infrastructure/prompts/core-prompt.md` — Always-loaded core instructions (150 tokens)
- [ ] `technical-infrastructure/prompts/module-{1-6}*.md` — On-demand module files (100-150 tokens each)
- [ ] `technical-infrastructure/ansible/playbooks/playbook-index.json` — Machine-readable playbook registry
- [ ] `technical-infrastructure/ansible/playbooks/template.yml` — Ansible playbook template
- [ ] `technical-infrastructure/scripts/unified_health_monitor.py` — Single health check entry point
- [ ] `technical-infrastructure/scripts/unified_decision_engine.py` — Single routing decision maker

**Phase 1 Deliverables (PENDING):**
- [ ] `technical-infrastructure/scripts/binary_decompose.py` — 2x binary decomposition logic
- [ ] `technical-infrastructure/scripts/node_recovery_watcher.py` — Recovery timeout mechanism
- [ ] `technical-infrastructure/scripts/cloud_escalation.py` — Tiered escalation manager
- [ ] `technical-infrastructure/scripts/lab_node_monitor.py` — SSH-based node monitoring

**Phase 2 Deliverables (PENDING):**
- [ ] `technical-infrastructure/scripts/memory_manager.py` — Health-aware memory allocation
- [ ] `technical-infrastructure/reference/model-routing-guide.md` — Updated with health states
- [ ] `.pi/agents/phases/phase-2-planning.md` — Health check requirement
- [ ] `.pi/agents/phases/phase-3-execution.md` — Health monitoring during execution

**Documentation Created:**
- ✅ [Master Playbook Prompt](../../wiki/technical-infrastructure/master-playbook-prompt) — Comprehensive prompt system
- ✅ [Unified Health Monitoring](../../wiki/technical-infrastructure/unified-health-monitoring) — Integrated master plan
- ✅ [Plan Location Guide](../../wiki/technical-infrastructure/PLAN-LOCATION-GUIDE) — Quick reference
- ✅ [Research Citations](./planning/RESEARCH-CITATIONS-MASTER-PROMPT) — 2025-2026 research validation
- ✅ [Integration Summary](./planning/TI031-TI032-INTEGRATION-MASTER-PROMPT) — Architecture details

**Wiki Location:** [Unified Health Monitoring](/technical-infrastructure/technical-infrastructure/unified-health-monitoring)

**Estimated Effort:** 16 hours (P0: 5h, P1: 7h, P2: 4h)
**Blocked By:** None
**Next Action:** Phase 0 implementation in progress

---

## 🆕 New Items

---

## Navigation

| Need | Location |
|------|----------|
| Back to backlog | [../BACKLOG.md](../BACKLOG.md) |
