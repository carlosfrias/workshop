---
name: Infrastructure Domain
summary: Infrastructure domain consolidating orchestration, fleet, execution, and network projects
status: active
phase: "Reorganized"
progress: 100
updated: "2026-05-26"
---

# Current Focus — Infrastructure Domain

**Last Updated:** 2026-05-26  
**Status:** Reorganized — All infrastructure projects consolidated under single domain

---

## [S-TIGHT]

Infrastructure domain contains 10 projects (all archived at 100%). Domain created 2026-05-26 to consolidate orchestration infrastructure projects. Reference packages live in `03-Resources/Technical-Infrastructure/Packages/`.

---

## Archived (Completed)

| Project | Version | Completed | Notes |
|---------|---------|-----------|-------|
| **cost-aware-routing** | - | 2026-05-26 | Cost tracking and AI routing |
| **decompose-execute-verify** | v2.0.0 | 2026-05-26 | 99% cost savings, 100% pass rate, 7-node fleet validated |
| **fnet-network-maintenance** | Phase 1 | 2026-05-26 | NextCloud hardened, SSL fixed, pi-playwright installed |
| **health-monitor** | - | 2026-05-26 | Resource monitoring (RAM, CPU, swap, disk, network) |
| **local-model-pilot** | - | 2026-05-26 | Ollama model routing configuration |
| **node-router** | v1.0.0 | 2026-05-26 | Fleet scoring algorithm, Ansible deployment, benchmarks |
| **pi-cross-node-comms** | - | 2026-05-26 | Cross-node SSE coordination |
| **playbook-executor** | - | 2026-05-26 | Playbook execution framework |
| **project-blueprint** | v1.4.0 | 2026-05-26 | Distribution discipline, 10 pi packages, TUI UX design |
| **sshfs-accessible** | - | 2026-05-26 | SSHFS mounts for lab nodes |

---

## Domain Structure

```
Infrastructure/
├── AGENTS.md                    ← Domain router
├── FOCUS.md                     ← Current state (you are here)
├── cost-aware-routing/          ← Archived
├── decompose-execute-verify/    ← Archived (v2.0.0)
├── fnet-network-maintenance/    ← Archived (Phase 1)
├── health-monitor/              ← Archived
├── local-model-pilot/           ← Archived
├── node-router/                 ← Archived (v1.0.0)
├── pi-cross-node-comms/         ← Archived
├── playbook-executor/           ← Archived
├── project-blueprint/           ← Archived (v1.4.0)
└── sshfs-accessible/            ← Archived
```

---

## Cross-References

- **Workshop Index:** [`../../INDEX.md`](../../INDEX.md)
- **Documentation Mirror:** `../../personal-vault/02-Areas/Infrastructure/`
- **Reference Packages:** `../../03-Resources/Technical-Infrastructure/Packages/`
- **Trading Domain:** [`../Trading/`](../Trading/)
- **Faith-Practice Domain:** [`../Faith-Practice/`](../Faith-Practice/)

---

## Next Actions

Domain reorganization complete. All 10 projects archived at 100% progress. Future work:
- Monitor for new infrastructure initiatives
- Maintain existing systems as needed
- Update documentation when changes occur

---

*Last updated: 2026-05-26*
