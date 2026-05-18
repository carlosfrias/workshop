# TI-018: Cost-Aware Routing + Billing Model

**Issue Home:** [0-ISSUE.md](./0-ISSUE.md)
**Status:** TBD
**Priority:** TBD

---

### TI-018: Cost-Aware Routing + Billing Model
**Created:** 2026-05-02
**Status:** 🔄 **IN PROGRESS** - Cost calculation implemented, billing tiers defined
**Priority:** 🔴 High (enables customer billing and infrastructure monetization)
**Rationale:** Local models currently treated as "free" ($0) but they consume real resources - electricity, hardware depreciation, facility space. A unified cost model (cost per 1K tokens) allows billing customers regardless of execution venue and reveals that local compute is 70-78% cheaper than cloud.

**Deliverables:**
- [x] `ti011_node_registry.py` - `_compute_node_hourly_cost()` + `_compute_cost_per_1k_tokens()`
- [x] Hardware cost defaults by RAM tier ($500 for 15GB, $800 for 31GB)
- [x] Power cost: 0.15 kWh × $0.12/kWh = $0.018/hour per node
- [x] Scoring updated: 30% speed + 45% fit + 25% cost
- [x] Billing tiers defined:
  - Local Basic (qwen3.5:4b): $0.005/1Ktk (40% margin)
  - Local Standard (qwen3:8b): $0.006/1Ktk (50% margin)
  - Local Premium (gemma4:e4b): $0.005/1Ktk (56% margin)
  - Cloud Standard: $0.015/1Ktk (33% margin)
  - Cloud Premium: $0.050/1Ktk (20% margin)
- [ ] Invoice generation script (future)
- [ ] Customer usage tracking (future)

**Dependent On:** TI-019 (LLM-driven decomposition) ✅ COMPLETE - generates weighted sub-tasks for accurate per-task billing

**Estimated Effort:** 3-4 hours (core done, billing infrastructure pending)

---

---

## Navigation

| Need | Location |
|------|----------|
| Back to backlog | [../BACKLOG.md](../BACKLOG.md) |
