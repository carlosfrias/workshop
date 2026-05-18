# Session Notes — Type-Based to Issue-Home Migration Progress
**Date:** 2026-05-14
**Scope:** Document scattered type-based docs (`planning/`, `status/`, `sessions/`, `testing/`, `recommendations/`) and map them to issue homes.
**Constraint:** Only 6 exploration turns available before wrap-up. Best-effort mapping only.

---

## Active Issues Identified (from BACKLOG.md)

| Issue | Status | Priority | Has Issue Home? |
|-------|--------|----------|-----------------|
| TI-036 | PLANNED | HIGH | NO |
| TI-035 | OPEN | HIGH | NO |
| TI-011 | IN PROGRESS | HIGH | NO |
| TI-018 | IN PROGRESS | HIGH | NO |
| TI-033 | IN PROGRESS | MEDIUM | NO |
| TI-032 | IN PROGRESS | CRITICAL | NO |
| TI-037 | IN PROGRESS | HIGH | NO |
| TI-034 | COMPLETE (residuals) | HIGH | NO |
| PB-001 | IMPLEMENTED | MEDIUM | NO |
| TDOF-001 | COMPLETE | CRITICAL | NO |
| TDOF-002 | BACKLOG | HIGH | NO |
| TDOF-003 | BACKLOG | MEDIUM | NO |
| TDOF-004 | FUTURE | LOW | NO |
| keyword-router-regression | CORE FIXED | HIGH | YES (skip per rules) |

---

## Files Scanned

- `BACKLOG.md` — read in full (~1200 lines)
- `issues/` — 1 issue home: `keyword-router-regression/`
- `planning/` — 41 files
- `status/` — 55 files
- `sessions/` — 28 files
- `testing/` — 15 files
- `recommendations/` — 4 files

---

## Key Mapping Discoveries

### TI-011 (Meta-Orchestration Framework)
**Docs found:**
- `planning/PLAN-2026-05-03-0800-ORCHESTRATION-FRAMEWORK-FIX.md`
- `status/STATUS-2026-05-02-1515.md`
- `status/ROUTING-DASHBOARD-2026-05-02.md`
- `sessions/SESSION-NOTES-2026-05-02-2200-AUTONOMOUS-413-RECOVERY.md`
- `sessions/SESSION-NOTES-2026-05-02-2230-AUTO-DISTRIBUTION.md`
- `sessions/SESSION-NOTES-2026-05-03-0845.md`
- `sessions/SESSION-NOTES-2026-05-03-2015-TI030-TI023-TI011-P3.md`
- `sessions/SESSION-NOTES-TI011-RIGHT-SIZING-2026-05-02.md`
- `testing/TEST-REPORT-2026-05-03-1020.md`
- `status/STATUS-2026-05-02-0900.md` (mentions TI-011)
- `status/STATUS-2026-05-02-1015.md` (mentions TI-011)

### TI-023 (Orchestrator Health Monitoring + Workload Redistribution)
**Docs found:**
- `planning/PLAN-2026-05-02-2300-TI023-ORCHESTRATOR-HEALTH.md`
- `planning/PLAN-2026-05-03-1930-TI023-AUTO-DECOMPOSE-NODE-DISPATCH.md`
- `sessions/SESSION-NOTES-2026-05-03-2025-TI023-E2E-TEST.md`
- `sessions/SESSION-NOTES-2026-05-03-2015-TI023-P2-P4-IMPLEMENTATION.md`
- `status/ROUTING-PERFORMANCE-ANALYSIS-2026-05-03.md`
- `sessions/SESSION-NOTES-2026-05-03-0432.md` (mentions TI-023)
- `sessions/SESSION-NOTES-2026-05-03-1945-ROUTER-COLLISION-CLEANUP.md` (mentions TI-023)
- `sessions/ROUTING-GAP-ANALYSIS-2026-05-03.md`

### TI-032 (Integrated Health-Aware Playbook Monitoring / Master Prompt)
**Docs found:**
- `status/BENCHMARK-RESULTS-2026-05-05.md`
- `status/PHASE0-COMPLETE-SUMMARY.md`
- `status/PHASE0-STATUS-DASHBOARD.md`
- `status/PHASE1-FINAL-COMPLETE.md`
- `status/PHASE1-PARTIAL-COMPLETE-SUMMARY.md`
- `status/PHASE1-STATUS-DASHBOARD.md`
- `status/PROJECT-COMPLETION-REPORT.md`
- `status/STATUS-2026-05-04-agenticos-archive.md` (mentions TI-032)
- `planning/RESEARCH-CITATIONS-MASTER-PROMPT.md`
- `planning/TI031-TI032-INTEGRATION-MASTER-PROMPT.md`
- `planning/TI031-TI032-INTEGRATION-SUMMARY.md`
- `planning/INTEGRATION-TI027-TI030-PLAYBOOK-MASTER.md`
- `status/FINAL-PROJECT-SUMMARY.md`
- `status/LIST-ROUTES-DEPLOYMENT.md`

### TI-035 (Keyword Router Collision Fixes)
**Docs found:**
- `status/LIST-ROUTES-DEPLOYMENT.md` (contains `5a0f7f1 fix(TI-035)`)
- `sessions/SESSION-NOTES-2026-05-03-1945-ROUTER-COLLISION-CLEANUP.md`

### TI-037 (TI-011 + Master Integration)
**Docs found:**
- `status/STATUS-2026-05-12-1730.md`
- `sessions/SESSION-NOTES-2026-05-12-1730.md`

### PB-001 (/list-domain Command)
**Docs found:**
- `planning/PB-001-list-domain-implementation.md`
- `status/STATUS-PB-001-IMPLEMENTATION.md`
- `status/PB-001-DEPLOYMENT.md`
- `status/PB-001-STANDALONE-DEPLOYMENT.md`
- `status/PB-001-COMPLETION-SUMMARY.md`
- `testing/pb-001-list-domain-acceptance-test.md`
- `testing/PB-001-verification-report.md`

### TDOF-001 (Vector Memory / ChromaDB)
**Docs found:**
- `planning/PLAN-TDOF-001-CHROMADB.md`

### TI-010 (Event-Driven Gist Message Protocol)
**Docs found:**
- `planning/PLAN-TI010-EVENT-DRIVEN.md`
- `planning/prompts/PROMPT-TI010-EVENT-DRIVEN.md`
- `status/STATUS-2026-05-05-TI010-COMPLETE.md`
- `status/STATUS-2026-05-05-TI010-TEST-RESULTS.md`
- `testing/TI010-EVALUATION-REPORT.md`
- `testing/ti010-acceptance-report.json`

### TI-018 (Cost-Aware Routing)
**Docs found:**
- `sessions/SESSION-NOTES-2026-05-02-2000-ORCHESTRATOR-SELF-TEST.md` (mentions TI-018)
- `status/STATUS-2026-05-02-1445.md` (mentions TI-018)

### TI-033 (Lab Node SSHFS Mount)
**Docs found:**
- `status/STATUS-2026-05-03-fnet7-recovery.md` (mentions TI-033)
- `planning/PLAN-2026-05-03-fnet7-recovery.md` (may relate)

### TI-034 (Project-Blueprint Consumer Testing)
**Docs found:**
- `testing/ti034-model-benchmarks.json`

---

## Issue Homes Created

**None created** — hit turn limit before creation phase.

---

## Broken Links Found

| File | Broken Link | Context |
|------|-------------|---------|
| `BACKLOG.md` | `ASSESSMENT-TI031-MASTER-PROMPT-GAPS.md` under TI-032 references `../operational/planning/ASSESSMENT-TI031-MASTER-PROMPT-GAPS.md` | Should be `./planning/ASSESSMENT-TI031-MASTER-PROMPT-GAPS.md` |
| `BACKLOG.md` | `PLAN-TI031-INTEGRATION-v1.0.md` referenced as `../operational/planning/PLAN-TI031-INTEGRATION-v1.0.md` | Should be `./planning/PLAN-TI031-INTEGRATION-v1.0.md` |
| Multiple files | Links to `../../../prompts/` may break after VitePress build if prompts/ is outside wiki tree | Known from WIKI-LINKS issue |

---

## Next Actions (for follow-up session)

1. Create issue homes for all 13 active issues using BACKLOG.md entries as source
2. Populate `DOCUMENT-MIGRATION-PENDING.md` with full table
3. Identify orphaned docs that don't map to any issue
4. Fix broken links in BACKLOG.md
5. Move type-based docs into appropriate issue homes
6. Archive completed items to `backlog-completed/`

---

*Session terminated at turn limit. Mapping is partial.*
