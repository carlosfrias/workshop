# Keyword Router Regression — Decomposition Index

**Location:** `technical-infrastructure/wiki/operational/issues/keyword-router-regression/decompositions/`
**Created:** 2026-05-14
**Purpose:** Master index of all decomposition documents for this issue.

---

## Decomposition Documents

| File | Item | Steps | Waves | Nodes | Wall-Clock | Status |
|------|------|-------|-------|-------|------------|--------|
| [`DECOMP-B-KR-001-2026-05-13.md`](./DECOMP-B-KR-001-2026-05-13.md) | B-KR-001: Kill-Switch | 20 | 4 | fnet1–fnet7 | ~45 min | ✅ Complete |
| [`DECOMP-B-KR-001-PHASE1-2026-05-13.md`](./DECOMP-B-KR-001-PHASE1-2026-05-13.md) | B-KR-001: Phase 1 Detail | — | — | — | — | ✅ Complete |
| [`DECOMP-B-KR-002-2026-05-13.md`](./DECOMP-B-KR-002-2026-05-13.md) | B-KR-002: Bisection | — | — | — | — | ✅ Complete |
| [`B-KR-002-REFINED-DISPATCH-2026-05-13.md`](./B-KR-002-REFINED-DISPATCH-2026-05-13.md) | B-KR-002: Refined Dispatch | — | — | — | — | ✅ Complete |
| [`DECOMP-B-KR-004-2026-05-14.md`](./DECOMP-B-KR-004-2026-05-14.md) | B-KR-004: Cloud Escalation | 16 | 4 | fnet1–fnet6 | ~60 min | 📋 Ready |
| [`DECOMP-B-KR-005-2026-05-14.md`](./DECOMP-B-KR-005-2026-05-14.md) | B-KR-005: Operational Runbook | 9 | 3 | fnet1–fnet7 | ~35 min | 📋 Ready |
| [`DECOMP-B-KR-006-2026-05-14.md`](./DECOMP-B-KR-006-2026-05-14.md) | B-KR-006: CI Regression Test | 10 | 4 | fnet1–fnet5 | ~25 min | 📋 Ready |
| [`DECOMP-1-PLAN-REUSABLE-COMPONENTS-2026-05-14.md`](./DECOMP-1-PLAN-REUSABLE-COMPONENTS-2026-05-14.md) | 1-PLAN: Reusable Components | 17 | 4 | fnet1–fnet7 | ~40 min | 📋 Ready |

---

## Reusable Plan Component Templates (from 1-PLAN.md)

| # | Template File | ID | Source Section |
|---|---------------|----|----------------|
| 1 | [`model-responsibility.md`](./model-responsibility.md) | COMP-001 | Model Responsibility |
| 2 | [`anti-hallucination-safeguards.md`](./anti-hallucination-safeguards.md) | COMP-002 | Anti-Hallucination Safeguards |
| 3 | [`local-node-recovery.md`](./local-node-recovery.md) | COMP-003 | Local Node Recovery |
| 4 | [`high-frequency-decomposition.md`](./high-frequency-decomposition.md) | COMP-004 | High-Frequency Decomposition Detection |
| 5 | [`node-health-report.md`](./node-health-report.md) | COMP-005 | 5-Minute Node Health Report |
| 6 | [`tdd-methodology.md`](./tdd-methodology.md) | COMP-006 | TDD Methodology |
| 7 | [`test-architecture.md`](./test-architecture.md) | COMP-007 | Test Architecture |
| 8 | [`phase-plan-structure.md`](./phase-plan-structure.md) | COMP-008 | Phase Plan |
| 9 | [`backlog-item-template.md`](./backlog-item-template.md) | COMP-009 | Backlog Items |
| 10 | [`decision-log.md`](./decision-log.md) | COMP-010 | Decision Log |
| 11 | [`session-notes.md`](./session-notes.md) | COMP-011 | Session Notes |
| 12 | [`status-summary-table.md`](./status-summary-table.md) | COMP-012 | Project Status Summary |
| 13 | [`navigation-pattern.md`](./navigation-pattern.md) | COMP-013 | Navigation |
| 14 | [`lab-node-dispatch-rules.md`](./lab-node-dispatch-rules.md) | COMP-014 | Lab Node Dispatch Rules |
| 15 | [`master-assembly-guide.md`](./master-assembly-guide.md) | COMP-015 | Assembly Guide |

**Usage:** See [`master-assembly-guide.md`](./master-assembly-guide.md) for how to compose a full plan from these templates. All templates use `{{PLACEHOLDER}}` variables for cross-plan reuse.

---

## How to Use

1. Pick the item to execute from the index above.
2. Read the decomposition file for step details, node allocation, and dispatch commands.
3. Follow the wave-based dispatch protocol: verify nodes → dispatch in parallel → collect results → verify → proceed to next wave.
4. All decompositions reference [`AGENTS.md`](../AGENTS.md) for model tier rules and escalation policy.

## Conventions

- `DECOMP-*` files follow the `[S-TIGHT]` + wave format established in B-KR-001.
- Each decomposition is owned by the **high cloud model** (`kimi-k2.6`) and handed off to the **low cloud model** (`qwen3.5:397b`) for orchestration.
- Lab nodes execute via SSHFS-mounted workspace or local clone.
