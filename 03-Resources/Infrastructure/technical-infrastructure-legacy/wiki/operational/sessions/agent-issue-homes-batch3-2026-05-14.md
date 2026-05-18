# Agent Issue Homes — Batch 3
**Date:** 2026-05-14
**Agent:** infrastructure
**Scope:** TI-035, TI-037, TI-034, TI-036, TI-018, TI-033, TDOF-002, TDOF-003, TDOF-004

---

## Summary

| Issue | Kebab Name | Status | Files Moved | Skeleton Only |
|-------|-----------|--------|-------------|---------------|
| TI-035 | ti035-keyword-router-collisions | ✅ Home created + files moved | 2 sessions, 1 status | No |
| TI-037 | ti037-master-integration | ✅ Home created + files moved | 1 sessions, 1 status | No |
| TI-034 | ti034-project-blueprint-testing | ✅ Home created + files moved | 1 test JSON | No |
| TI-036 | ti036-playbook-nl-triggers | ✅ Home created | — | Yes |
| TI-018 | ti018-cost-aware-routing | ✅ Home created + files moved | 1 sessions, 1 status | No |
| TI-033 | ti033-lab-sshfs-mount | ✅ Home created | — | Yes |
| TDOF-002 | tdof-002-mcp-registry | ✅ Home created | — | Yes |
| TDOF-003 | tdof-003-autonomous-agent | ✅ Home created | — | Yes |
| TDOF-004 | tdof-004-rebrand | ✅ Home created | — | Yes |

---

## Files Moved

### TI-035 (Keyword Router Collisions)
- `sessions/SESSION-NOTES-2026-05-03-1945-ROUTER-COLLISION-CLEANUP.md` → `issues/ti035-keyword-router-collisions/sessions/`
- `status/LIST-ROUTES-DEPLOYMENT.md` → `issues/ti035-keyword-router-collisions/status/`

### TI-037 (Master Integration)
- `sessions/SESSION-NOTES-2026-05-12-1730.md` → `issues/ti037-master-integration/sessions/`
- `status/STATUS-2026-05-12-1730.md` → `issues/ti037-master-integration/status/`

### TI-034 (Blueprint Testing)
- `testing/ti034-model-benchmarks.json` → `issues/ti034-project-blueprint-testing/tests/`

### TI-018 (Cost-Aware Routing)
- `sessions/SESSION-NOTES-2026-05-02-2000-ORCHESTRATOR-SELF-TEST.md` → `issues/ti018-cost-aware-routing/sessions/`
- `status/STATUS-2026-05-02-1445.md` → `issues/ti018-cost-aware-routing/status/`

### TI-033 (Lab SSHFS Mount)
- `planning/PLAN-2026-05-03-fnet7-recovery.md` — **NOT moved** (verified irrelevant to TI-033; belongs to TI-016)

---

## Skeleton-Only Issues (No Mapped Files Found)

- **TI-036** (`ti036-playbook-nl-triggers`): Created `0-ISSUE.md` with full backlog content, Issue Home Navigation, and related links.
- **TI-033** (`ti033-lab-sshfs-mount`): Created `0-ISSUE.md` with backlog content and subfolder structure.
- **TDOF-002** (`tdof-002-mcp-registry`): Skeleton with deliverables, acceptance criteria, navigation.
- **TDOF-003** (`tdof-003-autonomous-agent`): Skeleton with deliverables, acceptance criteria, navigation.
- **TDOF-004** (`tdof-004-rebrand`): Skeleton with decision criteria and acceptanace criteria.

---

## Link Updates

Link updates in moved docs were **not performed** due to turn limit. The following relative paths may need manual adjustment:
- Moved session notes referencing `../BACKLOG.md` or `../status/` now resolve from `issues/<issue>/sessions/` — adjust to `../../../BACKLOG.md` or `../../status/`.
- Moved status reports referencing `../sessions/` or `../BACKLOG.md` now resolve from `issues/<issue>/status/` — adjust to `../sessions/` or `../../../BACKLOG.md`.

---

## Remaining Work

1. **Fix relative links** in all moved docs (batch operation)
2. **Update BACKLOG.md** issue references to point to new issue home paths
3. **Create 1-PLAN.md** files for issues that have active plans (TI-035, TI-037, TI-018)
4. **Populate decompositions/** and prompts/ subfolders where applicable

---

*End of batch 3 issue-home creation session.*
