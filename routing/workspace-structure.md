# Workspace Structure & Cross-References

**Section ID:** workspace-structure  
**Size:** ~3.5KB  
**LOD:** Low  
**Purpose:** Workspace directory layout, cross-reference paths, and discovery order.

---

## [S-TIGHT]

Workshop has two zones: Projects (active code) and Resources (reference infrastructure). All paths are relative from workshop root. Cross-references to personal-vault use `../../personal-vault/`. Discovery path: root AGENTS.md → project/area AGENTS.md → personal-vault project docs.

---

## Workspace Layout [LOD: Low]

```
workshop/
├── AGENTS.md                          ← Manifest (routes to routing/ section files)
├── routing/                           ← Decomposed section files
├── 01-Projects/                       ← Active project code (see project-map.md)
│   ├── kingdom-warfare-leadership/
│   ├── doc-standards-enablement/
│   ├── project-blueprint/
│   ├── decompose-execute-verify/
│   ├── health-monitor/
│   ├── local-model-pilot/
│   ├── node-router/
│   ├── sshfs-accessible/
│   ├── cost-aware-routing/
│   ├── nextcloud/                     # (has AGENTS.md, infrastructure/, ansible/, wiki/)
│   ├── his-desk/                      # (has AGENTS.md, study/, devotional/, data/, site/, wiki/)
│   └── workflow-orchestration-research/
├── 02-Areas/
│   └── Trading/
│       ├── bookkeeping/               # Ledger, P&L, reconciliation
│       ├── market-research/           # Analysis, signals, backtesting
│       └── position-management/       # Orders, risk, allocation
├── 03-Resources/                      # Reference, infrastructure, legacy
│   ├── Infrastructure/                # 24 infrastructure packages
│   ├── Trading/scripts/               # Operational scripts
│   └── Wiki/                          # Trading desk wiki
├── .pi/agents/phases/                 # Phase-based routing files
└── .pi/agents/                        # Agent + chain definitions
```

---

## Cross-Reference Paths [LOD: Low]

| From | To | Path |
|------|----|------|
| Workshop → Docs | personal-vault project docs | `../../personal-vault/01-Projects/{project}/` |
| Docs → Workshop | personal-vault → workshop project | `../../workshop/01-Projects/{project}/` |
| Workshop → Vault (areas) | personal-vault areas | `../../personal-vault/02-Areas/` |

**Convention:** All paths are relative from workshop root. Never use absolute paths.

---

## Discovery Path [LOD: Medium]

```
1. carlos-desktop/AGENTS.md              ← Pick workspace (broad keywords)
2. workshop/AGENTS.md                    ← Pick section (this manifest)
3. routing/{section}.md                  ← Load only the section you need
4. workshop/01-Projects/{project}/AGENTS.md ← Tech stack, entry points, code conventions
   OR
   workshop/02-Areas/Trading/{area}/AGENTS.md ← Domain rules, workflows
5. personal-vault/01-Projects/{project}/   ← Documentation, plans, session history
```

---

*Next: For project routing, load [project-map.md](./project-map.md). For domain routing, load [domain-routing.md](./domain-routing.md).*