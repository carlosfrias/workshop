# NextCloud — Project Router

**Purpose:** Install and configure NextCloud on lab node fnet2 for private cloud storage, file sync, and collaboration. Covers Ansible automation, service configuration, DNS/VLAN networking, and ongoing operations.

**Status:** In Progress (TI-006) — scaffolded, awaiting secrets generation and dry-run.

## [S-TIGHT]

Infrastructure project router. Match keywords to domain, load domain context, execute. No domain-specific content in this file. **All documentation lives in the vault** (`../../personal-vault/01-Projects/nextcloud/`). This project contains code and agent configs only.

---

## Conventions

- All timestamps in US Eastern (America/New_York)
- All dates: YYYY-MM-DD
- Node IPs: `192.168.0.14{1-7}` (fnet1–fnet7)
- Target node: **fnet1** (`192.168.0.141`, 3TB primary depot, specialization: primary-depot)
- Keep outputs concise, actionable
- Ansible playbooks in `./ansible/`
- Config and compose files in `./infrastructure/`
- **Documentation in vault**, code in workshop — no mixing

---

## Domain Routing

| Keywords | Read this file |
|----------|---------------|
| install, configure, deploy, ansible, playbook, docker, compose, nginx, apache, php, mariadb, postgres, redis, SSL, certificate, nextcloud setup, provisioning | `./infrastructure/AGENTS.md` |
| dns, dnsmasq, VLAN, network, firewall, segmentation, ddns, tplinkdns, router, subnet | `./infrastructure/AGENTS.md` |
| backup, restore, disaster recovery, migration, sync, depot | `./infrastructure/AGENTS.md` |
| wiki, documentation, notes, research, planning, session, status, activity log | `../../personal-vault/01-Projects/nextcloud/wiki/nextcloud/AGENTS.md` |

**Domain Ambiguity Rule:** If keywords don't clearly match, ask the user which domain they intend. Do not guess.

---

## Lab Context

| Node | IP | Specialization | Role |
|------|-----|---------------|------|
| fnet1 | 192.168.0.141 | primary-depot | Model depot + worker |
| fnet1 | 192.168.0.141 | **primary-depot** | **NextCloud + model depot** |
| fnet3 | 192.168.0.143 | vector-memory | ChromaDB + RAG |
| fnet4 | 192.168.0.144 | worker | General worker |
| fnet5 | 192.168.0.145 | worker | General worker |
| fnet6 | 192.168.0.146 | secondary-depot | Backup model depot |
| fnet7 | 192.168.0.147 | worker | General worker |

All nodes run Ubuntu, have Docker + Ollama installed, and are managed via Ansible from the orchestrator.

---

## Cross-Reference

| From | To | Path |
|------|----|------|
| Workshop → Vault (docs) | `../../personal-vault/01-Projects/nextcloud/` | Knowledge notes, research, wiki |
| Vault → Workshop (code) | `../../workshop/01-Projects/nextcloud/` | Ansible, configs, scripts |
| Workshop → Lab Specs | `../../workshop/03-Resources/Infrastructure/lab-specs/` | Hardware specs, node capacity |
| Workshop → TI Backlog | `../../workshop/03-Resources/Infrastructure/technical-infrastructure-legacy/wiki/operational/BACKLOG.md` | TI-006 NextCloud Installation |

---

## Discovery Path

```
1. workshop/AGENTS.md                       ← Pick project (infrastructure keywords)
2. workshop/01-Projects/nextcloud/AGENTS.md  ← YOU ARE HERE (pick domain)
3. workshop/01-Projects/nextcloud/infrastructure/AGENTS.md  ← Full domain context (code)
   OR
   personal-vault/01-Projects/nextcloud/     ← Knowledge, research, wiki (all docs)
```

---

*Last updated: 2026-05-19*