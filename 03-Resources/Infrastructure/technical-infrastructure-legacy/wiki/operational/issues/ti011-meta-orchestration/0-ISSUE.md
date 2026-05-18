# TI-011: Meta-Orchestration Framework (Local-First LLM Routing)

**Issue Home:** [0-ISSUE.md](./0-ISSUE.md)
**Status:** TBD
**Priority:** TBD

---

### TI-011: Meta-Orchestration Framework (Local-First LLM Routing)
**Created:** 2026-05-01
**Status:** ▶️ **IN PROGRESS** - Phase 1 classifier complete
**Priority:** 🔴 High (reduces cloud costs by 75-90%)
**Rationale:** Cloud model usage dominates sessions despite 7 local nodes being available. Current routing is keyword-based, not complexity-based. Every "think deeply" triggers ultra-reasoning even for simple analysis. Building a meta-orchestration framework classifies prompts by complexity, decomposes multi-step tasks, routes to appropriate local models, and escalates only specific sub-tasks to cloud.

**Phase 1: Classification + Simple Routing ✅ COMPLETE**
- [x] Build hybrid heuristic classifier (classify_prompt.py) - 1ms latency, 100% heuristic
- [x] Add infrastructure keywords to model-router.json
- [x] Create complexity-router.json mapping complexity to models
- [x] Wire complexity layer into actual routing logic - NodeRegistry integration
- [x] Test with live prompts through full pipeline - `classify_prompt.py --route` working
- [ ] Start performance logging (needs session data)

**Phase 2: Decomposition Engine ✅ COMPLETE**
- [x] Build decompose_task.py (PLAN template → task JSON)
- [x] Integrate with submit_task.py for fan-out
- [x] Build synthesize_results.py for combining sub-outputs
- [x] Wire NodeRegistry into decompose_task.py for dynamic model/node assignment

**Phase 3: Performance Monitor ✅ COMPLETE**
- [x] Log every prompt: type, model, latency, tokens, cost, quality - `performance_logger.py` with JSONL output
- [x] Log every decomposition: trigger_id, sub_task_count, latency, model_used, success/failure
- [x] Log every dispatch: trigger_id, sub_task_id, node, model, latency, success/failure
- [x] Weekly report script: `scripts/generate-weekly-report.py` - markdown output with routing/decomposition/dispatch stats
- [x] Benchmark data collected and integrated into routing decisions

**Phase 4: Adaptive Feedback 🔄 PENDING (needs 2+ weeks of performance data)**
- [ ] Auto-update classifier few-shot examples from logs
- [ ] Auto-update PLAN templates from successful decompositions
- [ ] Auto-generate SESSION-NOTES summaries for knowledge base
- [ ] Tier adjustment engine (monthly analysis)

**Dependent On:** TI-009 (orchestration must be working - ✅ MVP complete), TI-016 (per-node profiles - ✅ complete)

**Estimated Effort:** 25-35 hours total (2-3 weeks)

---

---

## Navigation

| Need | Location |
|------|----------|
| Back to backlog | [../BACKLOG.md](../BACKLOG.md) |
