# NextCloud — Project Router

**Purpose:** Deploy and operate NextCloud private cloud storage on lab node fnet1 (3TB primary depot). Ansible-automated Docker stack with proxy, DNS, and backup.

**Status:** ✅ Deployed (TI-006) — all phases 1-9 complete, external access deferred (TI-008)

## [S-TIGHT]

Infrastructure project router. Match keywords to domain, load domain context, execute. No domain-specific content in this file. **All documentation lives in the vault** (`../../personal-vault/01-Projects/nextcloud/`). This project contains code and agent configs only.

---

## Conventions

- All timestamps in US Eastern (America/New_York)
- All dates: YYYY-MM-DD
- Target node: **fnet1** (`192.168.0.141`, 3TB primary depot)
- Ansible playbooks run through playbook-executor or directly
- **Documentation in vault**, code in workshop — no mixing

---

## Domain Routing

| Keywords | Read this file |
|----------|---------------|
| install, configure, deploy, ansible, playbook, docker, compose, nginx, SSL, certificate, nextcloud setup, provisioning, backup, restore, dns, proxy | `./infrastructure/AGENTS-REFINED.md` (post-completion, verified) |
| `./infrastructure/AGENTS.md` | Original scaffold (pre-deployment, less accurate) |
| rclone, external storage, dropbox, google drive, gdrive, cloud mount, fuse mount, bridge | `./infrastructure/AGENTS-REFINED-RCLONE.md` (post-completion, verified) |
| wiki, documentation, notes, research, planning, session, status, activity log | `../../personal-vault/01-Projects/nextcloud/wiki/nextcloud/AGENTS.md` |

**Prefer AGENTS-REFINED.md** — it contains the golden path proven by actual deployment, with all resolved ambiguities and common mistakes documented.

---

## Lab Context

| Node | IP | Specialization | Role |
|------|-----|---------------|------|
| **fnet1** | **192.168.0.141** | **primary-depot** | **NextCloud + model depot** |
| fnet2 | 192.168.0.142 | worker | Former NextCloud (uninstalled) |
| fnet3 | 192.168.0.143 | vector-memory | ChromaDB + RAG |
| fnet4 | 192.168.0.144 | worker | General worker |
| fnet5 | 192.168.0.145 | worker | General worker |
| fnet6 | 192.168.0.146 | secondary-depot | Backup target (NextCloud → fnet6) |
| fnet7 | 192.168.0.147 | worker | General worker |

All nodes run Ubuntu, have Docker + Ollama installed, and are managed via Ansible from the orchestrator.

---

## Playbook Inventory

| Playbook | Executor Trigger | Purpose |
|----------|-----------------|---------|
| `deploy-nextcloud.yml` | `deploy nextcloud` (92 triggers) | Docker Compose stack on fnet1 |
| `configure-nextcloud-dns.yml` | `configure nextcloud dns` (21 triggers) | dnsmasq + /etc/hosts on 7 nodes |
| `configure-nextcloud-proxy.yml` | `configure nextcloud proxy` (27 triggers) | Nginx + SSL + trusted domains |
| `backup-nextcloud.yml` | `backup nextcloud` (39 triggers) | rsync to fnet6 with maintenance mode |
| `configure-nextcloud-rclone.yml` | `configure nextcloud rclone` (26 triggers) | rclone FUSE mounts for Dropbox + Google Drive |
| `uninstall-nextcloud.yml` | `uninstall nextcloud` (60+ triggers) | Remove from fnet2 |

**Dependency:** DNS playbook MUST run before proxy playbook.

---

## Cross-Reference

| From | To | Path |
|------|----|------|
| Workshop → Vault (docs) | `../../personal-vault/01-Projects/nextcloud/` | Knowledge notes, research, wiki |
| Vault → Workshop (code) | `../../workshop/01-Projects/nextcloud/` | Ansible, configs, scripts |
| Workshop → Lab Specs | `../../workshop/03-Resources/Infrastructure/lab-specs/` | Hardware specs, node capacity |
| Workshop → Playbook Executor | `../../workshop/03-Resources/Infrastructure/playbook-executor/` | Trigger registration |

---

## Discovery Path

```
1. workshop/AGENTS.md                                    ← Pick project (infrastructure keywords)
2. workshop/01-Projects/nextcloud/AGENTS.md              ← YOU ARE HERE (pick domain)
3. workshop/01-Projects/nextcloud/infrastructure/AGENTS-REFINED.md  ← Golden path (proven, deployment)
   OR
   workshop/01-Projects/nextcloud/infrastructure/AGENTS-REFINED-RCLONE.md ← Golden path (proven, rclone external storage)
   OR
   workshop/01-Projects/nextcloud/infrastructure/AGENTS.md          ← Original scaffold (pre-deployment)
   OR
   personal-vault/01-Projects/nextcloud/                 ← Knowledge, research, wiki (all docs)
```

---

*Last updated: 2026-05-19*