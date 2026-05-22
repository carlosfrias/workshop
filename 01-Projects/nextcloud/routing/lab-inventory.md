# NextCloud — Lab & Playbook Inventory

**Section ID:** `nc-lab-inventory` | **Size:** ~1.4KB | **LOD:** L2 (load on task) | **Purpose:** Node roles and playbook triggers for NextCloud infrastructure operations.

---

## [LOD: L2] Lab Node Context

Load this section when: executing playbooks, targeting nodes, planning deploys, or troubleshooting infrastructure.

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

## [LOD: L2] Playbook Inventory

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

*Last updated: 2026-05-19*