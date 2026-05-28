---
tags:
  - domain
  - infrastructure
  - PARA
---

# Infrastructure Domain

**Purpose:** Orchestration infrastructure, fleet management, execution pipelines, project scaffolding, and network maintenance.

## [S-TIGHT]

Infrastructure domain for workshop/02-Areas/. Contains 10 active infrastructure projects with matching documentation in personal-vault/02-Areas/Infrastructure/.

---

## Projects

| Project | Status | Version | Purpose |
|---------|--------|---------|---------|
| [`cost-aware-routing/`](./cost-aware-routing/) | ✅ Archived | - | Cost tracking and routing |
| [`decompose-execute-verify/`](./decompose-execute-verify/) | ✅ Archived | v2.0.0 | Cost-optimized execution pipeline (99% savings) |
| [`fnet-network-maintenance/`](./fnet-network-maintenance/) | ✅ Archived | Phase 1 | Fleet network maintenance, NextCloud server |
| [`health-monitor/`](./health-monitor/) | ✅ Archived | - | Resource monitoring (RAM, CPU, swap, disk, network) |
| [`local-model-pilot/`](./local-model-pilot/) | ✅ Archived | - | Ollama model routing configuration |
| [`node-router/`](./node-router/) | ✅ Archived | v1.0.0 | Execution location scoring + routing |
| [`pi-cross-node-comms/`](./pi-cross-node-comms/) | ✅ Archived | - | Cross-node SSE coordination |
| [`playbook-executor/`](./playbook-executor/) | ✅ Archived | - | Playbook execution framework |
| [`project-blueprint/`](./project-blueprint/) | ✅ Archived | v1.4.0 | Orchestration framework scaffolding |
| [`sshfs-accessible/`](./sshfs-accessible/) | ✅ Archived | - | SSHFS mounts for lab nodes |

---

## Domain Routing

**This domain:** Infrastructure projects live here under `02-Areas/Infrastructure/`.

**Cross-references:**
- **Documentation mirror:** `../../personal-vault/02-Areas/Infrastructure/`
- **Reference packages:** `../../03-Resources/Technical-Infrastructure/Packages/`
- **Related domains:**
  - [`../Trading/`](../Trading/) — Trading-specific infrastructure
  - [`../Faith-Practice/`](../Faith-Practice/) — Faith and ministry resources

---

## Discovery Path

```
1. workshop/AGENTS.md             ← Root router
2. workshop/INDEX.md              ← Workspace index
3. 02-Areas/Infrastructure/AGENTS.md ← YOU ARE HERE (domain router)
4. <project>/FOCUS.md             ← Current state
```

---

## Quality Checks

Before declaring infrastructure work complete:
- [ ] Tests pass (pytest, integration tests)
- [ ] Documentation updated (README, AGENTS, FOCUS)
- [ ] Version tagged (if applicable)
- [ ] Changelog written
- [ ] Artifacts preserved (benchmarks, configs, deployment scripts)
- [ ] FOCUS.md status set to `archived`
- [ ] Progress set to 100%
- [ ] Moved to 02-Areas per LIFECYCLE.md
- [ ] Vault documentation mirrors workshop code

---

*Last updated: 2026-05-26*
