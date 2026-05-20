# NextCloud Infrastructure — Routing Stub

> **Full documentation lives in the vault.** This file is a routing stub only.
> Read the vault copy for all conventions, rules, and quality checks.

**Vault location:** `../../personal-vault/01-Projects/nextcloud/wiki/nextcloud/infrastructure/AGENTS.md`
**Golden path (post-completion):** `../../personal-vault/01-Projects/nextcloud/wiki/nextcloud/infrastructure/AGENTS-REFINED.md`

---

## Quick Reference

| What | Where |
|------|-------|
| Target node | fnet1 (`192.168.0.141`, 3TB primary depot) |
| Web UI | `https://nextcloud.home` |
| Playbooks | `./ansible/` (deploy, dns, proxy, backup, uninstall) |
| Docker Compose | `./infrastructure/docker/nextcloud-docker-compose.yml` |
| Nginx config | `./infrastructure/nginx/nextcloud.home.conf` |
| Backup script | `./infrastructure/backup/backup-nextcloud.sh` |
| Vault secrets | `~/.ansible/secure/vault-nextcloud.yml` |

**Prefer AGENTS-REFINED.md** — it contains the golden path proven by actual deployment, with all resolved ambiguities and common mistakes documented.