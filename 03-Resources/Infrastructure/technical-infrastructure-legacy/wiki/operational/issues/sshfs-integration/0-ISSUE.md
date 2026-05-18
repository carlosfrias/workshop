# [S-TIGHT] Build automatic SSHFS filesystem orchestration so tasks decompose, mount, execute in parallel on lab nodes, and collect results without manual intervention.

**Issue Home:** [0-ISSUE.md](./0-ISSUE.md)
**Issue ID:** TI-038
**Created:** 2026-05-14 09:00:00 US Eastern
**Status:** 📋 **PLANNED**
**Priority:** 🔴 **HIGH**
**Code Workspace:** [technical-infrastructure/packages/sshfs-integration/](../../../packages/sshfs-integration/)
**Document Workspace:** [technical-infrastructure/wiki/operational/sshfs-integration/](../../../wiki/operational/sshfs-integration/)

---

## 1. Rationale

Manual SSHFS mounting (`sshfs-accessible` skill) blocks the decompose-execute-verify pipeline. Every multi-node task currently requires:

1. User explicitly requests a mount
2. Agent runs `mount-all.sh`
3. User then asks for parallel work
4. Agent manually verifies mounts before routing

This adds 2-3 turns of friction per parallel task. The orchestrator should detect when a task needs filesystem access across nodes, mount automatically, fan out work, and collect results — all in one pipeline turn. Without this, the TI-011 meta-orchestration framework cannot achieve hands-off parallel execution.

---

## 2. Gap Analysis

### What `sshfs-accessible` Does (Manual)

| Capability | How It Works | Limitation |
|------------|--------------|------------|
| Mount | User prompt → `mount-all.sh` | Requires explicit user request |
| Unmount | User prompt → `unmount-all.sh` | Requires explicit user request |
| Verify | `verify-mounts.sh --json` | Called on demand, not integrated into routing |
| Topology | Static `config/nodes.json` | No runtime discovery of node health |
| Integration | Skill loads on keyword match | No auto-trigger from task decomposition |

### What `sshfs-integration` Should Do (Automatic)

| Capability | Target Behavior |
|------------|-----------------|
| Auto-mount | `decompose_task.py` detects node dispatch need → mounts before fan-out |
| Health-aware routing | `verify-mounts.sh --json` consumed by `node-router` pre-dispatch |
| Lazy unmount | Task completion triggers unmount (or keep-alive with TTL) |
| Topology hot-reload | `nodes.json` changes propagate without restart |
| Single-turn pipeline | User asks for parallel work → mount + decompose + execute + synthesize in one flow |

---

## 3. Deliverables Checklist

### Phase 1: Auto-Mount Hook
- [ ] `sshfs-integration/scripts/auto-mount.py` — called by `decompose_task.py` before fan-out
- [ ] Mount gate: check `verify-mounts.sh --json`, mount only unmounted nodes
- [ ] Fail-fast: if mount fails, log to issue home and route to orchestrator fallback
- [ ] Configuration: `sshfs-integration/config/auto-mount.json` with `enabled`, `ttl_seconds`, `retry_count`

### Phase 2: Node Health Integration
- [ ] `node-router` reads mount status before scoring nodes for dispatch
- [ ] Unmounted nodes get score penalty (or exclusion if `require_mounted: true`)
- [ ] `health-monitor` publishes mount-health events to Gist bus

### Phase 3: Lazy Unmount
- [ ] `sshfs-integration/scripts/lazy-unmount.py` — TTL-based unmount after last task
- [ ] Keep-alive: reset TTL on new task dispatch to same node
- [ ] Force-unmount fallback for stuck mounts

### Phase 4: Single-Turn Pipeline
- [ ] Update `decompose_task.py` to call auto-mount hook in decomposition phase
- [ ] Update `synthesize_results.py` to trigger lazy-unmount on completion
- [ ] End-to-end test: one user prompt → parallel execution on 3 nodes → results synthesized

### Phase 5: Documentation + Skill Packaging
- [ ] `skills/sshfs-integration/SKILL.md` — agent skill manifest
- [ ] Package `package.json` with pi skill registration
- [ ] Issue home documentation (this file and children)

---

## 4. Success Criteria

1. A user prompts for parallel work (e.g., "analyze these 5 files across lab nodes") and the system mounts SSHFS, decomposes, executes, and returns results in a single turn without manual mount commands.
2. `verify-mounts.sh --json` output is consumed by `node-router` within 500ms of dispatch decision.
3. A node that fails to mount is excluded from dispatch; the task is re-routed to an available node or the orchestrator.
4. Mount TTL expires 300 seconds after the last task completes; unmount runs automatically without user intervention.
5. The `sshfs-integration` skill auto-loads when the user mentions parallel work, lab nodes, or cross-node filesystem tasks.
6. All changes are backward-compatible: `sshfs-accessible` manual scripts continue to work independently.
7. End-to-end test passes on the full lab node fleet (7 nodes) with 100% success rate across 10 consecutive runs.

---

## 5. Dependencies on Other Issues

| Issue | Status | Relationship |
|-------|--------|--------------|
| [TI-011](../../../issues/ti011-meta-orchestration/0-ISSUE.md) | ▶️ In Progress | Framework: decomposition, routing, synthesis |
| [TI-033](../../../issues/ti033-lab-sshfs-mount/0-ISSUE.md) | ✅ Complete | Prerequisite: SSHFS mount capability |
| [TI-037](../../../issues/ti037-master-integration/0-ISSUE.md) | 📋 Planned | Master integration test may cover this |
| [sshfs-accessible-package](../../../issues/sshfs-accessible-package/0-ISSUE.md) | ✅ Complete | Manual skill — this issue extends it to automatic |

---

## 6. Estimated Effort

| Phase | Hours | Notes |
|-------|-------|-------|
| Phase 1: Auto-Mount Hook | 4-6 | Reuses `sshfs-accessible` scripts, adds Python wrapper |
| Phase 2: Node Health Integration | 3-4 | Extend `node-router` scoring function |
| Phase 3: Lazy Unmount | 3-4 | TTL tracking, background unmount process |
| Phase 4: Single-Turn Pipeline | 4-6 | Wire into `decompose_task.py` and `synthesize_results.py` |
| Phase 5: Documentation + Packaging | 2-3 | Skill manifest, README, issue home |
| Testing + Debugging | 4-6 | Full fleet end-to-end |
| **Total** | **20-29 hours** | **1.5-2 weeks** |

---

## 7. Navigation

| Need | Location |
|------|----------|
| Back to backlog | [../../BACKLOG.md](../../BACKLOG.md) |
| Active plan | [1-PLAN.md](./1-PLAN.md) |
| Session notes | [sessions/](./sessions/) |
| Status snapshots | [status/](./status/) |
| Test plans + evidence | [tests/](./tests/) |
| User prompts that drove work | [prompts/](./prompts/) |
| Decomposition docs | [decompositions/](./decompositions/) |
| Troubleshooting | [troubleshooting/](./troubleshooting/) |
| Supporting artifacts | [artifacts/](./artifacts/) |
| Code package | [../../../packages/sshfs-integration/](../../../packages/sshfs-integration/) |
| Prerequisite (manual skill) | [../../../packages/sshfs-accessible/](../../../packages/sshfs-accessible/) |
| TI-011 meta-orchestration | [../ti011-meta-orchestration/0-ISSUE.md](../ti011-meta-orchestration/0-ISSUE.md) |
| TI-033 SSHFS mount | [../ti033-lab-sshfs-mount/0-ISSUE.md](../ti033-lab-sshfs-mount/0-ISSUE.md) |
