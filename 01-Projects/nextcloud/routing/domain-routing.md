# NextCloud — Domain Routing & Cross-Reference

**Section ID:** `nc-domain-routing` | **Size:** ~1.1KB | **LOD:** L2 (load on task) | **Purpose:** Keyword-to-file routing and path cross-references for navigation.

---

## [LOD: L2] Domain Routing

| Keywords | Read this file |
|----------|---------------|
| install, configure, deploy, ansible, playbook, docker, compose, nginx, SSL, certificate, nextcloud setup, provisioning, backup, restore, dns, proxy | `./infrastructure/AGENTS-REFINED.md` (post-completion, verified) |
| `./infrastructure/AGENTS.md` | Original scaffold (pre-deployment, less accurate) |
| rclone, external storage, dropbox, google drive, gdrive, cloud mount, fuse mount, bridge | `./infrastructure/AGENTS-REFINED-RCLONE.md` (post-completion, verified) |
| wiki, documentation, notes, research, planning, session, status, activity log | `../../personal-vault/01-Projects/nextcloud/wiki/nextcloud/AGENTS.md` |

**Prefer AGENTS-REFINED.md** — it contains the golden path proven by actual deployment, with all resolved ambiguities and common mistakes documented.

---

## [LOD: L2] Cross-Reference

| From | To | Path |
|------|----|------|
| Workshop → Vault (docs) | `../../personal-vault/01-Projects/nextcloud/` | Knowledge notes, research, wiki |
| Vault → Workshop (code) | `../../workshop/01-Projects/nextcloud/` | Ansible, configs, scripts |
| Workshop → Lab Specs | `../../workshop/03-Resources/Infrastructure/lab-specs/` | Hardware specs, node capacity |
| Workshop → Playbook Executor | `../../workshop/03-Resources/Infrastructure/playbook-executor/` | Trigger registration |

---

*Last updated: 2026-05-19*