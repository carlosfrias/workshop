# PLAN Template with Decomposition Tracking
**Use this template when creating new PLAN documents that involve multi-step work.**

The decomposition tracking table allows the meta-orchestration system to learn from past plans and improve routing decisions.

---

## Standard Header

```markdown
# Planning: {Brief Title}
**Date:** YYYY-MM-DD HHMM
**Context:** {What triggered this plan}
**Complexity Estimate:** {SIMPLE | MEDIUM | HARD}
```

---

## Decomposition Tracking Table

Add this table for any plan that involves multi-step execution across models or nodes:

```markdown
## Decomposition

| Step | Sub-Task | Suggested Model | Suggested Node | Context Size | Estimated Latency | Fallback Model |
|------|----------|---------------|----------------|--------------|-------------------|--------------|
| 1 | Classify prompt complexity | qwen3.5:4b | orchestrator | ~500 tokens | 0.2s | qwen3:8b |
| 2 | Generate playbook skeleton | qwen3:8b | fnet3 | ~2000 tokens | 3s | cloud/qwen3.5:397b |
| 3 | Validate YAML syntax | qwen3.5:4b | any available | ~500 tokens | 0.5s | qwen3:8b |
| 4 | Test on one node | shell command | fnet2 | N/A | 5s | manual execution |
| 5 | Deploy to all 7 nodes | Ansible | fnet3 | N/A | 30s | manual per-node SSH |
| 6 | Verify with hardware spec | qwen3.5:4b | any available | ~1000 tokens | 1s | qwen3:8b |
```

**Fields:**
- **Step:** Sequence number
- **Sub-Task:** What needs to be done
- **Suggested Model:** Which local (or cloud) model is appropriate
- **Suggested Node:** Which lab node should execute it (or "orchestrator" for local execution)
- **Context Size:** Approximate token count (helps with routing decisions)
- **Estimated Latency:** How long this step should take
- **Fallback Model:** What to use if the primary model/node fails or times out

---

## Actual Execution Tracking (Fill After Execution)

After the plan is executed, update this table with actual results:

```markdown
## Execution Results

| Step | Actual Model | Actual Node | Actual Latency | Result | Adequate? | Notes |
|------|------------|-------------|----------------|--------|-----------|-------|
| 1 | qwen3.5:4b | orchestrator | 0.18s | ✅ | Yes | Classification correct |
| 2 | qwen3:8b | fnet3 | 4.2s | ✅ | Yes | Slightly slower than est |
| 3 | qwen3.5:4b | fnet2 | 0.4s | ✅ | Yes | |
| 4 | shell | fnet2 | 3.1s | ✅ | Yes | Ansible faster than est |
| 5 | Ansible | fnet3 | 45s | ✅ | Yes | Network latency higher |
| 6 | qwen3.5:4b | fnet4 | 0.9s | ✅ | Yes | |
```

**Fields:**
- **Actual Model:** What model actually ran the step
- **Actual Node:** What node actually executed it
- **Actual Latency:** Measured wall-clock time
- **Result:** ✅ (success) ❌ (failure) ⚠️ (degraded)
- **Adequate?:** Yes/No — was the output quality sufficient?
- **Notes:** Any deviations from plan, lessons learned

---

## Cost Justification Summary

After execution, summarize not just cost but whether the cost was justified:

```markdown
## Summary

| Metric | Planned | Actual |
|--------|---------|--------|
| Total Local Prompts | 5 | 5 |
| Total Cloud Prompts | 0 | 0 |
| Total Latency | ~40s | ~54s |
| Local Cost | $0 | $0 |
| Cloud Cost | $0 | $0 |
| Quality | High | High |

### Tiered Cost Analysis

| Task Type | Model Used | Cost | Justified? | Evidence |
|-----------|-----------|------|------------|----------|
| (none — all local) | — | $0 | N/A | N/A |

**Target for Next Plan:** Maintain 100% local for SIMPLE/MEDIUM tasks.
```

For plans that used cloud models:

```markdown
## Summary

| Metric | Planned | Actual |
|--------|---------|--------|
| Total Local Prompts | 4 | 4 |
| Total Cloud Prompts | 1 | 1 |
| Total Latency | ~45s | ~62s |
| Local Cost | $0 | $0 |
| Cloud Cost | $0.05 | $0.05 |
| Quality | High | High |

### Tiered Cost Analysis

| Step | Task Type | Model Used | Cost | Justified? | Evidence |
|------|-----------|-----------|------|------------|----------|
| 1 | Classification | qwen3.5:4b | $0 | Yes | Local, trivial |
| 2 | Architecture design | qwen3.5:397b | $0.03 | Yes | Multi-step reasoning with constraints |
| 3 | Syntax validation | qwen3.5:4b | $0 | Yes | Local, deterministic |
| 4 | Integration testing | shell | $0 | Yes | Local, script execution |
| 5 | Edge case analysis | kimi-k2.6 | $0.05 | Yes | Novel failure mode requiring cross-domain synthesis |

**Learning:** Edge case analysis (step 5) consistently requires Cloud Premium. Consider pre-building an edge-case pattern library so future similar cases can use Cloud Standard instead.
```

---

## Complete Example

See [PLAN-2026-05-01-0915.md](/technical-infrastructure/operational/planning/PLAN-2026-05-01-0915) for a real example without tracking (pre-convention).
See [PLAN-2026-05-01-1547.md](/technical-infrastructure/operational/planning/PLAN-2026-05-01-1547) for a planning document with decomposition design.

The next PLAN document created should use this template.
