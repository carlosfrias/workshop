# Keyword Router Debug Project

**Project:** pi-keyword-router Regression + Routing Transparency  
**Status:** ✅ Core regression FIXED — Remaining items tracked in BACKLOG-MASTER  
**Created:** 2026-05-13  
**Last updated:** 2026-05-14  

---

## Quick Links

| Document | Purpose |
|----------|---------|
| [`BACKLOG-MASTER.md`](./BACKLOG-MASTER.md) | **Critical backlog** — all remaining items (B-KR-004, B-KR-005, B-KR-006) |
| [`PLAN-2026-05-13-1926.md`](./PLAN-2026-05-13-1926.md) | Master plan with full project status |
| [`AGENTS.md`](./AGENTS.md) | Orchestration guide for low/medium/high cloud models |
| [`INVOCATION-GUIDE-2026-05-13.md`](./INVOCATION-GUIDE-2026-05-13.md) | Copy-paste prompts for each phase |
| [`DECOMP-B-KR-001-2026-05-13.md`](./DECOMP-B-KR-001-2026-05-13.md) | Phase 0 decomposition (20 test stubs) |
| [`DECOMP-B-KR-001-PHASE1-2026-05-13.md`](./DECOMP-B-KR-001-PHASE1-2026-05-13.md) | Phase 1 decomposition (14 implementation steps) |
| [`DECOMP-B-KR-002-2026-05-13.md`](./DECOMP-B-KR-002-2026-05-13.md) | B-KR-002 bisection decomposition |
| [`B-KR-002-REFINED-DISPATCH-2026-05-13.md`](./B-KR-002-REFINED-DISPATCH-2026-05-13.md) | Refined bisection dispatch after test flaw found |

---

## Session Reports

| Report | What it covers |
|--------|---------------|
| [`ROOT-CAUSE-B-KR-002-2026-05-14.md`](../../wiki/operational/sessions/ROOT-CAUSE-B-KR-002-2026-05-14.md) | Regression analysis — commit 93e1d39 |
| [`B-KR-003-COMPLETION-2026-05-14.md`](../../wiki/operational/sessions/B-KR-003-COMPLETION-2026-05-14.md) | Fix application + verification results |

---

## What Happened

1. **B-KR-001** — Built persistent kill-switch so keyword-router can be safely disabled
2. **B-KR-002** — Bisected 9 commits across 7 lab nodes in parallel, found regression at `93e1d39`
3. **B-KR-003** — One-line fix: restored `gemma4:e4b` as default fallback

**Verification:** All 3 KR scenarios passing (reasoning → gemma4:e4b, monitoring → qwen3.5:4b, simple → qwen3.5:4b)

---

## What Remains

See [`BACKLOG-MASTER.md`](./BACKLOG-MASTER.md) for the critical backlog. In short:

- **B-KR-006** (1–2 hrs) — CI regression test to prevent this from recurring
- **B-KR-004** (4–6 hrs) — Cloud escalation for deep research prompts
- **B-KR-005** (2–3 hrs) — Operational runbook for future maintainers

**Recommended next step:** B-KR-006 (highest ROI — prevent regression)

---

## Kill-Switch Status

The kill-switch added in B-KR-001 is **ACTIVE** (enabled: true). The regression is fixed, so there is no need to disable it. If future issues arise, set `enabled: false` in config and restart.

---

*This project uses the decompose-execute-verify skill with pi-intercom dispatch across 7 lab nodes (fnet1–fnet7). See AGENTS.md for the full protocol.*
