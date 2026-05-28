# Identity & Phase-Based Loading

**Section ID:** identity-and-phases  
**Size:** ~2KB  
**LOD:** Low  
**Purpose:** Workshop identity, S-TIGHT summary, and phase-based instruction loading protocol.

---

## [S-TIGHT]

Unified routing hub. Detects domain from prompt keywords, routes to domain/project agents, loads only the phase file needed for the current cognitive stage. All markdown docs live in personal-vault.

---

## Workspace Identity

**Workspace:** `workshop/`  
**Purpose:** Execution workspace for all code, scripts, scrapers, data processing, infrastructure, and build systems.  
**Counterpart:** `../personal-vault/` — documentation and knowledge management.  
**Rule:** This file is a router only. Match keywords, route to the correct domain or project.

---

## Phase-Based Instruction Loading

This workspace uses a phased cognitive model. Load **only** the phase file matching your current stage.

| Phase | File | Purpose | Load When | Size |
|-------|------|---------|-----------|------|
| 1 — Domain Activation | `.pi/agents/phases/phase-1-domain-activation.md` | Detect domain from prompt keywords | **Every prompt** | ~630 tokens |
| 2 — Planning | `.pi/agents/phases/phase-2-planning.md` | Framework readiness, complexity, decomposition | After domain activated | ~850 tokens |
| 3 — Execution | `.pi/agents/phases/phase-3-execution.md` | Must Always / Must Never, tool rules, safety | During active work | ~2,800 tokens |
| 4 — Quality Check | `.pi/agents/phases/phase-4-quality-check.md` | Verify checklist before declaring done | After work complete | ~1,300 tokens |
| 5 — Documentation | `.pi/agents/phases/phase-5-documentation.md` | Session notes, status, backlog | Before ending session | ~700 tokens |

**Index:** `.pi/agents/phases/phase-index.json` — machine-readable phase map.

**Convention:** Only load the phase you need. Do not load all phases in one inference.

**Skill Loading Convention:** Only load the skill matching the active task. Do not load skills speculatively.

---

*Next: For which model to route tasks, load [model-routing.md](./model-routing.md). For project-level routing, load [project-map.md](./project-map.md).*