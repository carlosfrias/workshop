# Session Notes: Wiki Reorganization & Package Re-integration

**Date:** 2026-05-02
**Model:** ollama/gemma4:e4b (structured routing — fast local)
**Context:** Technical infrastructure wiki reorganization + package re-integration

---

## Summary

Reorganized `technical-infrastructure/wiki/` into a nested hierarchy and re-integrated 6 distribution-ready packages from `../agent-workspace/` into `technical-infrastructure/packages/`. Updated VitePress config to auto-generate navigation from the directory tree.

---

## What We Learned

The insight that changed the entire architecture: **prompt templates are the distribution artifact, not the code.**

`project-blueprint/SKILL.md` IS the product — it's what the user installs. The code in `packages/project-blueprint/` is the proven reference output. This means:
- Package `wiki/` folders are redundant (workspace VitePress is canonical)
- Nested `.git` dirs are sufficient (no submodules needed)
- The workspace itself is a project-blueprint exemplar for any domain

---

## Changes

### Phase 1 — New Directory Structure
| Created | Purpose |
|---------|---------|
| `packages/` | Distribution-ready packages (each = own .git repo) |
| `designs/` | Non-distribution design documents |
| `wiki/products/` | Product catalog landing + per-package overviews |

### Phase 2 — Package Relocation
| Package | From | To |
|---------|------|-----|
| `pi-keyword-router` | `extensions/` | `packages/pi-keyword-router/` |
| `project-blueprint` | `../agent-workspace/` | `packages/project-blueprint/` |
| `gist-message-queue` | `../agent-workspace/` | `packages/gist-message-queue/` |
| `decomposition-skill` | `../agent-workspace/` | `packages/decomposition-skill/` |
| `local-model-pilot` | `../agent-workspace/` | `packages/local-model-pilot/` |
| `trading-agents` | `agents-publish/` | `packages/trading-agents/` |
| `trading-lab-architecture` | `../agent-workspace/` | `designs/trading-lab-architecture/` |

### Phase 3 — Removed Stubs
| Removed | Reason |
|---------|--------|
| `wiki/pi-keyword-router/` | Stale stub |
| `wiki/project-blueprint/` | Stale stub |
| `wiki/trading-agents/` | Stale stub |
| `skills/gist-message-queue/` | Fragmented, moved whole package |
| `extensions/` | Empty after move |
| `wiki/local-model-pilot/` | Stale, journal moved to operational/ |
| `wiki/sessions/` | Duplicate JSONL |
| Package `wiki/` folders | Redundant with workspace VitePress |

### Phase 4 — New Documentation (wiki/products/)
| File | Content |
|------|---------|
| `index.md` | Product catalog landing |
| `pi-keyword-router.md` | Route table, install, quick commands |
| `project-blueprint.md` | Architecture principles, usage, install |
| `gist-message-queue.md` | Commands, use cases, install |
| `decomposition-skill.md` | Cost analysis, agents, chains, install |
| `local-model-pilot.md` | Hardware detect, config generation, install |
| `trading-agents.md` | Decomposer/verifier agents, chain usage |
| `trading-lab-architecture.md` | Design scope, references |

### Phase 5 — VitePress Config Rewrite
| Change | From | To |
|--------|------|-----|
| `srcDir` | `'wiki'` → broken | `'../wiki'` → correct |
| Sidebar | Hand-curated ~40 entries | Auto-recursive from directory tree |
| Nav items | Extensions, subagents | Guides, Reference, Products, Operational |
| New section | — | Products (auto-discovered) |

---

## Final Directory Structure

```
technical-infrastructure/
├── AGENTS.md, AGENTS-full.md, AGENTS-routing.md
├── WIKI.md
│
├── packages/                     ← DISTRIBUTION PACKAGES (each = .git)
│   ├── pi-keyword-router/        ← Extension: keyword-based model routing
│   ├── project-blueprint/          ← Skill: scaffold orchestrated projects
│   ├── gist-message-queue/         ← Skill: async agent communication via Gist
│   ├── decomposition-skill/       ← Skill: decompose → execute → verify
│   ├── local-model-pilot/          ← Skill: Ollama config for Apple Silicon
│   └── trading-agents/           ← Agent Package: decomposer + verifier
│
├── designs/                      ← DESIGN DOCUMENTS
│   └── trading-lab-architecture/ ← Multi-node orchestration design
│
├── prompts/                      ← Workspace operational prompts
├── scripts/                      ← Workspace operational scripts
├── ansible/                      ← Workspace operational playbooks
├── lab-specs/                    ← Hardware inventory
│
├── wiki/                         ← VITEPRESS SOURCE — CANONICAL DOCS
│   ├── index.md                  ← Landing page
│   ├── README.md                 ← Nav hub
│   ├── guides/                   ← How-to docs
│   ├── reference/                ← Lookup docs
│   ├── troubleshooting/            ← Diagnostic docs
│   ├── products/                 ← PACKAGE CATALOG
│   ├── operational/              ← Backlog, planning, sessions, status
│   ├── templates/                ← Machine-readable doc templates
│   ├── tools/                    ← Tool integration docs
│   └── decomposition-examples/   ← Step-by-step patterns
│
└── wiki-build/
    └── .vitepress/
        └── config.js             ← Renders wiki/ + products/
```

---

## What This Enables

### For the model reading the workspace:
- `packages/` signals "products" — a clear semantic layer
- `designs/` signals "architecture, not code" — separates thinking from doing
- `wiki/products/` provides a catalog with install commands the model can copy

### For VitePress website:
- Auto-generated sidebar covers all 113+ markdown files
- Products section gives users a clear: "what can I install?" view
- No stale stubs or broken links
- Single documentation tree, not scattered across workspace + package wikis

### For prompt-template distribution:
- Each package's `SKILL.md` IS the product
- Workspace `README.md` describes what it generates
- Code in the package is the proven reference output
- User installs prompt → their AI executes it → same structure reproduced

---

## Open Questions

1. Should we auto-generate `wiki/products/` from package `package.json` metadata?
2. Should the VitePress build include package `README.md` files directly (symlinks)?
3. How do versioned docs work when packages release independently?
4. Should `designs/trading-lab-architecture/` have its own repo or stay workspace-only?

---

**Next Steps (Proposed in Future Sessions):**
- Build out product READMEs with real SKILl.md references
- Add "Usage in context" examples to each product page (trade monitoring, multi-node orchestration)
- Create a workspace setup guide showing the project-blueprint pattern in action
