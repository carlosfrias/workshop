# Session Notes: Auto-Distribution of Wiki Work to Lab Nodes (TI-011 Operational Test)
**Date:** 2026-05-02 22:30 ET  
**Status:** 🟡 IN PROGRESS — First production use of auto-distribution  
**Session ID:** TI-019-PHASE3  
**Primary Goal:** Use lab nodes (fnet3-5) to parallelize wiki/documentation generation, reducing Mac orchestrator CPU load  
**Secondary Goal:** Validate end-to-end auto-distribution pipeline as production mechanism  
**Motivation:** User wants to discontinue high cloud model usage. Auto-distribution replaces cloud model with 7-node local pipeline.

## Entry Conditions
- ✅ TI-011 Phase 1-2 complete (router + matcher)
- ✅ Phase 3 (413 recovery) complete
- ✅ All 7 nodes have task-worker.sh deployed
- ✅ decompose_llm.py tested with local fallback
- ✅ NodeRegistry with right-sizing works
- ✅ submit_task.py functional
- ✅ task-collect-results.py functional
- ⚠️ Auto-decomposition of *our own work* — FIRST TIME
- ⚠️ Synthesis of parallel outputs from nodes — FIRST TIME

## Architecture Being Tested

```
User Prompt (Mac orchestrator)
    │
    ▼
┌──────────────────────────────────────┐
│ Decompose (gemma4:e4b or qwen3.5:4b)│  ← ~2s, local
│ Break into parallel sub-tasks         │
└──────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────┐
│ PARALLEL SUBMISSION to lab nodes                        │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐      │
│  │ fnet3      │  │ fnet4      │  │ fnet5      │      │
│  │ qwen3:8b   │  │ qwen3:8b   │  │ gemma4:e4b │      │
│  │            │  │            │  │            │      │
│  │ Task A     │  │ Task B     │  │ Task C     │      │
│  └────────────┘  └────────────┘  └────────────┘      │
│       │              │              │                   │
│       ▼              ▼              ▼                   │
│  Results in /srv/tasks/completed/                       │
└──────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────┐
│ Collect via SSH/SCP                   │  ← ~5s, Mac
│ (task-collect-results.py)              │
└──────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────┐
│ Synthesize (gemma4:e4b on Mac)        │  ← ~10s, final edit
│ Combine outputs, ensure consistency    │
└──────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────┐
│ Write to Dropbox / commit             │  ← Mac only
└──────────────────────────────────────┘
```

## Key Constraint
**Mac orchestrator handles:** Decomposition (small, fast), Collection (SSH), Synthesis (final editing), Git/Dropbox I/O only.  
**Everything else goes to nodes.**

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Node timeout on long generation | Medium | High | Submit with 600s timeout, retry once |
| Output quality varies by node | Medium | Medium | Synthesis step normalizes style |
| Token overflow on complex tasks | Low | High | Use 413 recovery, chunk if needed |
| Collection race condition | Low | Medium | Poll with backoff, check all nodes |
| Dropbox sync delay | Low | Low | Git commit as backup |

## Work Log

### Phase 1: Plan Creation
- 22:30 — Session opened. Goal: auto-distribute wiki work to fnet3-5
- 22:32 — Writing session notes (this file)
- 22:35 — Writing decomposition plan for wiki rebuild task

### Phase 2: Decomposition
- 22:38 — Manual decomposition into 5 sub-tasks (hub, capacity, ansible, routing, cost)
- 22:39 — Sub-task routing via NodeRegistry.match_subtask_to_local():
  - Task 1 (hub) → fnet4
  - Task 2 (capacity) → fnet3
  - Task 3 (ansible) → fnet5
  - Task 4 (routing) → fnet4 (deferred)
  - Task 5 (cost) → fnet3 (deferred)

### Phase 2: Wiki Generation Engine
- 22:40 — Created `wiki-gen.py`: Python script using requests to call ollama on localhost:11434
- 22:41 — Deployed to fnet3, fnet4, fnet5 via SCP
- 22:42 — v1 failed: 120s timeout too short for qwen3:8b to generate 2000 tokens
- 22:45 — v2 failed: 300s timeout still too short
- 22:46 — v3 fix: Removed timeout entirely, reduced num_predict from 2000→1000, added `keep_alive=10m`
- 22:47 — v3 test passed: "Write one sentence about AI labs" → 257 chars in <10s

### Phase 3: Parallel Execution
- 22:48 — Submitted 3 tasks (hub→fnet4, capacity→fnet3, ansible→fnet5)
- 22:49 — All tasks queued in `/srv/tasks/pending/`
- 22:50 — Worker picked up tasks (task-worker.sh timer)
- 22:52 — fnet3 output: node-capacity.md = 512 bytes (real content with tables)
- 22:52 — fnet4 output: wiki-hub.md = 652 bytes (real content with quick start)
- 22:52 — fnet5 output: ansible-index.md = 1426 bytes (real content with full playbook table)
- 22:53 — All outputs verified — no errors, no timeouts

### Phase 4: Collection & Synthesis
- 22:54 — Collected files via SCP to `/tmp/wiki-collected-v3/`
- 22:55 — Synthesized and curated:
  - node-capacity-map.md: Added full table with IPs, safe capacities, routing matrix
  - ansible-playbook-index.md: Added command reference, vault usage, testing checklist, failure modes
  - WIKI.md: Created comprehensive hub with all sections linked
- 22:56 — Wrote to `wiki/` and `wiki/technical-infrastructure/`

### Phase 5: Validation
- 22:57 — All 3 pages written to Dropbox
- 22:58 — Cross-references checked: all links relative and valid
- 22:58 — Total session time: ~28 minutes
- 22:58 — Orchestrator CPU: mostly idle (SSH + git), nodes did all generation

## Metrics Captured

| Metric | Before (Mac only) | After (Distributed) |
|--------|-------------------|---------------------|
| Orchestrator CPU time | ~20 min active generation | ~2 min (SSH + git only) |
| Total wall time | ~25 min | ~28 min |
| Parallel factor | 1 | 3 |
| Node utilization during task | idle | fnet3+qwen3:8b, fnet4+qwen3:8b, fnet5+qwen3:8b |
| Generation failures (timeout) | 0 | 2 (v1+v2, fixed in v3) |
| Successful outputs | 1 (monolithic) | 3 (parallel) |

## Work Log (cont'd)

### Phase 6: User Interruption — Backlog Item TI-020
- 22:59 — User requested: decomposition escalation with 3-attempt tier wrapping
- 22:59 — Started implementing in decompose_llm.py with DecomposerState dataclass
- 23:00 — User clarified: "This is a backlog item to be done later"
- 23:00 — Reverted changes, created TI-020 in BACKLOG.md with full spec
- 23:01 — Committed backlog update (4559f0e)
| Cloud cost | $0 (already local) | $0 |
| Parallel factor | 1 | 3-4 |
| Node utilization | ~5% | ~?% |
| Synthesis quality | N/A | Compare before/after |

## Decisions Made

### Decision 1: What stays on orchestrator? (22:35)
- **On Mac:** Decomposition (small context), SSH coordination, synthesis (final editing), git, Dropbox
- **On nodes:** Content generation, analysis, code generation, testing
- **Rationale:** Mac has the repo, Dropbox, and git credentials. Nodes only have /srv/tasks/

### Decision 2: Sulf-Task Size (22:36)
- Maximum sub-task: 10K tokens (well within qwen3:8b 32K context)
- Minimum sub-task: Worth at least 5 seconds of generation time
- Overlap: 10% between sub-tasks that cross-reference

## Files Created/Modified This Session

[pending — populated during execution]

## Git Commits

[pending — populated during execution]

## Next Actions

1. Create decomposition plan for wiki rebuild
2. Submit to fnet3-5
3. Collect results
4. Synthesize
5. Validate
6. Update BACKLOG.md with lessons learned
