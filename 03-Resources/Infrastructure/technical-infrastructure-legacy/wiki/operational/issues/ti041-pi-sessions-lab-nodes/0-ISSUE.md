# TI-041: Pi Sessions on Lab Nodes — Cross-Node Intercom Infrastructure

**Issue ID:** ti041-pi-sessions-lab-nodes
**Status:** 📋 PLANNED
**Priority:** 🔴 HIGH
**Created:** 2026-05-14
**Owner:** Technical Infrastructure

---

## [S-TIGHT]

Install and run persistent pi CLI sessions on fnet1–fnet7 lab nodes to enable true cross-node intercom coordination, replacing SSH-based dispatch with real-time message passing.

---

## Objective

The `decomposed-intercom-dispatch` chain (TI-039) includes an `intercom({ action: "ask", to: "fnet3", ... })` step that **cannot execute** because intercom is same-machine only. Lab nodes have no pi sessions. The chain falls back to SSH dispatch, which breaks the "automatic real-time coordination" promise.

This issue closes that gap by provisioning pi as a persistent service on all 7 lab nodes.

---

## Gap Analysis

### What Works Today (TI-039)
| Layer | State | Limitation |
|-------|-------|------------|
| Orchestrator pi session | ✅ Running on Mac | Can send intercom messages |
| Lab node filesystem | ✅ Accessible via SSHFS | File-based coordination works |
| Lab node SSH | ✅ Passwordless SSH | Command execution works |
| Lab node pi session | ❌ None exist | Intercom messages have no recipient |

### What TI-041 Enables
| Layer | Target State |
|-------|-------------|
| Lab node pi daemon | ✅ `pi --name fnet3-worker` running persistently |
| Intercom reachability | ✅ `intercom({ action: "ask", to: "fnet3-worker" })` delivers |
| Chain execution | ✅ True cross-node dispatch without SSH fallback |

---

## Acceptance Criteria

- [ ] pi CLI installed on fnet1–fnet7 (npm or binary install)
- [ ] Persistent pi session running on each node (systemd service or tmux script)
- [ ] Intercom test: orchestrator sends message, lab node receives and replies
- [ ] `decomposed-intercom-dispatch` chain updated to use intercom instead of SSH fallback
- [ ] Node health monitoring: detect if pi session crashes, auto-restart
- [ ] Documentation: setup guide, troubleshooting, rollback procedure
- [ ] Backward compatibility: SSH fallback still works if pi session unavailable

---

## Dependencies

| Dependency | Status | Why |
|------------|--------|-----|
| TI-033 (SSHFS mounts) | ✅ Complete | Lab nodes can read/write workspace |
| TI-038 (SSHFS integration) | 📋 Planned | Auto-mounting for task dispatch |
| TI-039 (decompose-execute-verify v2.1) | ✅ Complete | Chain that needs cross-node intercom |
| Node network connectivity | ✅ Verified | All fnet1–fnet7 reachable via SSH |

---

## Estimated Effort

6–10 hours across 2 phases:
- Phase 1: Installation + basic connectivity (3–4h)
- Phase 2: Persistence + health monitoring + chain update (3–6h)

---

## References

1. `technical-infrastructure/wiki/operational/issues/ti039-decompose-execute-verify-integration/0-ISSUE.md`
2. `technical-infrastructure/packages/sshfs-accessible/skills/sshfs-accessible/SKILL.md`
3. `/usr/local/lib/node_modules/pi-intercom/skills/pi-intercom/SKILL.md`
4. `technical-infrastructure/packages/decompose-execute-verify/ARCHITECTURE.md` (Section 6: Cross-Node Execution)

---

*This issue follows the issue-centric documentation standard. All work lives in this folder.*
