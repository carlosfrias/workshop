# TI-037: TI-011 + Master Integration & Routing Transparency Fix

**Issue Home:** [0-ISSUE.md](./0-ISSUE.md)
**Status:** TBD
**Priority:** TBD

---

### TI-037: TI-011 + Master Integration & Routing Transparency Fix
**Created:** 2026-05-12
**Status:** 🔄 **IN PROGRESS** — 3 parallel agents executing
**Priority:** 🔴 **HIGH** — Consolidates orchestration systems, fixes critical bugs
**Rationale:** TI-011 meta-orchestration framework is broken (missing node configs), Master Prompt System lacks complexity-based routing, and routing-transparency has data integrity bugs causing command crashes. Three work streams initiated to consolidate architecture and fix bugs.

**Work Delegated (Parallel):**
1. **Restore TI-011 Node Configs** — Agent `a0991c30-fdeb-4ea`
   - Create `lab-specs/node-configs/{fnet1-7}/` directory structure
   - Generate `models.json` and `model-router.json` for each node
   - Verify `ti011_node_registry.py --dump` works
2. **Update Master Core-Prompt with TI-011 Integration** — Agent `8b825382-260f-440`
   - Add complexity classification step before decomposition
   - Integrate `classify_prompt.py` as pre-processing
   - Document trigger keywords for lab routing
3. **Fix Routing-Transparency Logging** — Agent `6e952201-f1f9-4ba`
   - Fix `mapEventToRoutingDecision()` — ensure all fields have defaults
   - Add Master + TI-011 event listeners
   - Fix `/routing-log`, `/routing-bill`, `/routing-stats` crashes

**Deliverables:**
- [ ] All 7 node config directories with models.json and model-router.json
- [ ] Updated core-prompt.md with TI-011 integration
- [ ] Fixed routing-transparency with no command crashes
- [ ] Status report: `wiki/operational/status/STATUS-2026-05-12-1730.md` ✅ COMPLETE
- [ ] Session notes: `wiki/operational/sessions/SESSION-NOTES-2026-05-12-1730.md`

**Architecture Decision:** Master Prompt System v2.0 remains primary orchestrator; TI-011 becomes lab-specific extension for multi-node tasks.

**Estimated Effort:** 15-20 minutes (agent execution time)
**Blocked By:** None

---

---

## Navigation

| Need | Location |
|------|----------|
| Back to backlog | [../BACKLOG.md](../BACKLOG.md) |
