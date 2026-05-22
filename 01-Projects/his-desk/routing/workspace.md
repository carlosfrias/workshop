# Workspace Layout & Cross-References

**Section ID:** workspace  
**Size:** ~2KB  
**LOD:** Low  
**Purpose:** Directory structure, cross-references to other workspaces, and discovery path for agents joining the project.

---

## [S-TIGHT]

His-desk has 4 domain subdirs (study, devotional, site, data) plus wiki/. Documentation lives in personal-vault. Discovery order: root AGENTS.md → routing/ sections → domain AGENTS.md → FOCUS.md.

---

## Workspace Layout [LOD: Low]

```
workshop/01-Projects/his-desk/
├── AGENTS.md                  ← Routing hub (manifest)
├── routing/                   ← Decomposed routing sections
│   ├── domains.md             ← Domain routing + ambiguity rule
│   ├── conventions.md         ← Conventions + model routing + execution
│   └── workspace.md           ← This file (layout, cross-refs, discovery)
├── .pi/
│   ├── APPEND_SYSTEM.md       ← Identity only
│   └── agents/                ← Agent definitions & chains
├── study/                     ← Bible study tools & analysis
│   └── AGENTS.md
├── devotional/                ← Devotional generation & reflection
│   └── AGENTS.md
├── site/                      ← MkDocs site build
│   └── AGENTS.md
├── data/                      ← Scrapers, downloads, API clients
│   └── AGENTS.md
└── wiki/                      ← Project wiki (local reference)
    └── his-desk/
        ├── Home.md
        ├── study/
        ├── devotional/
        ├── site/
        ├── data/
        └── _meta/
```

## Cross-References [LOD: Low]

| From | To | Path | Purpose |
|------|----|------|---------|
| Workshop → Vault | `../../../personal-vault/01-Projects/his-desk/` | Docs, notes, study guides |
| Vault → Workshop | `../../../workshop/01-Projects/his-desk/` | Code, tools, scrapers, builds |

Both workspaces reference each other. Knowledge and documentation live in personal-vault; execution and code live in workshop.

## Discovery Path [LOD: Low]

```
1. carlos-desktop/AGENTS.md              ← Pick workspace
2. workshop/AGENTS.md                    ← Pick project
3. workshop/01-Projects/his-desk/AGENTS.md ← Routing manifest (YOU ARE HERE)
4. routing/{domain|conventions|workspace}.md ← Detailed routing
5. workshop/01-Projects/his-desk/{domain}/AGENTS.md ← Domain context
6. FOCUS.md                              ← Current state & handoff
```

**Load order for domain work:** AGENTS.md (manifest) → routing/domains.md → domain/AGENTS.md → FOCUS.md.

---

*See [domains.md](domains.md) for domain keyword routing.*  
*See [conventions.md](conventions.md) for model routing and execution patterns.*