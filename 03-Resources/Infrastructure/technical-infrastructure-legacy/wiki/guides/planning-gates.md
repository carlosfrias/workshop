# Planning Quality Gates

**LEGACY — MIGRATE TO:** `personal-vault/03-Resources/Technical-Infrastructure/planning-gates.md`

These gates apply specifically when creating PLAN documents or planning multi-step work. They are derived from session execution analysis.

| Gate | Check | Why It Matters |
|------|-------|---------------|
| **Latency budget per component** | Every step has estimated latency | Prevents 3-6s classifier disasters |
| **Pivot contingency (20-30%)** | Budget for alternative approaches | First attempt often fails |
| **Keyword coverage** | Domain terms are in routing table | Prevents silent domain activation failures |
| **Performance logging** | Decision tracking is required | Without logs, impact is unmeasurable |
| **Docs as deliverable** | AGENTS.md updates budgeted | Undocumented conventions are lost |

## Latency Budget Examples

| Component | Target | Max Acceptable | Pivot Threshold |
|-----------|--------|----------------|-----------------|
| Heuristic classification | <50ms | 100ms | >200ms |
| LLM classification | <500ms | 1000ms | >2000ms |
| Local model inference (4b) | <5s | 15s | >30s |
| Local model inference (8b) | <10s | 20s | >40s |
| Local model inference (large) | <20s | 40s | >60s |
| Cloud API call | <3s | 10s | >20s |
| SSH to lab node | <100ms | 500ms | >1000ms |
| SCP file transfer | <1s | 5s | >10s |

## Pivot Decision Tree

```
Step latency > 2× budget?
    │
    ├─ YES → Is there alternative B?
    │         │
    │         ├─ YES → Pivot to B, log reason
    │         └─ NO  → Escalate to user, pause task
    │
    └─ NO  → Continue, log actual latency
```

## Contingency Budgeting

For any task estimated at N minutes:

- **Simple (well-understood):** N + 20%
- **Medium (some unknowns):** N + 30%
- **Hard (multiple unknowns):** N + 50%
- **Research/Exploration:** N + 100%

**Example:** A 30-minute playbook deployment with medium complexity:
- Base estimate: 30 min
- Contingency (30%): 9 min
- **Total budget: 39 min**

---

**Related:** [Quality Checklist](quality-checklist.md) | [TI-011 Orchestration](ti011-orchestration.md)
