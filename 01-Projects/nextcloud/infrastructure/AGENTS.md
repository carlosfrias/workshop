# NextCloud Infrastructure

Installation, configuration, deployment, and operations for NextCloud on lab node fnet2. Includes Ansible automation, Docker/services, DNS/VLAN networking, backups, and disaster recovery.

## [S-TIGHT]

Self-contained domain context. All conventions, rules, quality checks, and documentation protocols for NextCloud infrastructure live here. No supplementary files.

---

## Conventions

- **Target node:** fnet2 (`192.168.0.142`)
- **Ansible playbooks** live in `./ansible/` — one playbook per service or configuration step
- **Docker Compose** files live in `./infrastructure/` — named by service (e.g., `nextcloud-docker-compose.yml`)
- **All commands executed via Ansible** from the orchestrator unless explicitly noted
- **Config backups** stored in `./infrastructure/configs/`
- **Timestamps:** YYYY-MM-DD HH:MM:SS US Eastern
- **Test before deploy:** All playbooks run with `--check` first, then `--diff`

## Architecture Decisions

### Deployment Method
- **Docker-based** deployment (not bare-metal) for isolation and reproducibility
- NextCloud + MariaDB + Redis + Nginx reverse proxy in Docker Compose
- Ansible automates the full stack from the orchestrator

### Networking
- NextCloud reachable at `http://192.168.0.142:8080` (LAN) initially
- DNS: `cloud.home` or `nextcloud.home` via dnsmasq on the lab network
- External access deferred (requires OPNsense/Protectli — see TI-008)
- VLAN segmentation for services (planned, not yet implemented)

### Data
- NextCloud data directory: `/srv/nextcloud/data/` on fnet2
- Database: MariaDB container with persistent volume
- Backup target: fnet1 `/srv/archive/nextcloud/` or fnet3 secondary

### Authentication
- Local accounts initially (no LDAP)
- Admin account provisioned via Ansible vault

## Rules

### Must Always
- Run Ansible playbooks with `--check --diff` before applying
- Verify fnet2 connectivity (`ssh friasc@192.168.0.142`) before any deployment
- Commit all playbook changes to git before running
- Document every configuration change in the wiki activity log
- Use `ansible-vault` for any secrets (database passwords, admin credentials)
- Test NextCloud web UI accessibility after any deployment step
- Verify Docker containers are healthy after playbook runs

### Must Never
- Expose NextCloud to the public internet without OPNsense/Protectli (TI-008)
- Store secrets in plaintext playbooks — always use `ansible-vault`
- Run playbooks against the wrong node (always verify inventory)
- Skip the backup step before major configuration changes
- Delete NextCloud data without confirmation

## Quality Checklist

Before considering any task complete, verify:

- [ ] Ansible playbook ran successfully with no errors
- [ ] Docker containers are running and healthy (`docker ps` on fnet2)
- [ ] NextCloud web UI accessible at `http://192.168.0.142:8080`
- [ ] File upload/download works
- [ ] Activity log entry created in wiki
- [ ] Any secrets stored in ansible-vault, not plaintext
- [ ] Changes committed to git

## Common Mistakes

| Mistake | Correct Approach |
|---------|-----------------|
| Running playbook without `--check` first | Always dry-run with `--check --diff` |
| Using default NextCloud admin password | Generate and vault-encrypt from day one |
| Forgetting to create `/srv/nextcloud/data/` with correct permissions | Pre-create directories in playbook |
| Hardcoding IP in playbooks | Use Ansible inventory/group_vars |
| Skipping Redis for performance | Include Redis in the compose stack from the start |
| Exposing port 443 without proper TLS cert | Use self-signed initially, plan Let's Encrypt for production |

## Documentation Protocol

After completing any task, document what you did in the project wiki.

### When to Document
- After making decisions that affect the deployment architecture
- After running a playbook or configuration change
- After discovering and resolving issues
- After creating, modifying, or removing any files or configurations

### Where to Document
- Write to: `./wiki/nextcloud/infrastructure/Activity Log.md`
- Cross-reference from: `../../personal-vault/01-Projects/nextcloud/` for knowledge docs

### Format
```markdown
### YYYY-MM-DD — {Title}

**Task**: {What was requested}
**Outcome**: {What was done and result}
**Rationale**: {Why this approach was chosen}
**Files changed**: {List of files created/modified}
**Lessons**: {What to remember for next time}
```

## Cross-Domain References

- Knowledge/research docs: `../../../personal-vault/01-Projects/nextcloud/`
- Lab hardware specs: `../../../workshop/03-Resources/Infrastructure/lab-specs/`
- TI backlog: `../../../workshop/03-Resources/Infrastructure/technical-infrastructure-legacy/wiki/operational/BACKLOG.md`
- Routing table: `../AGENTS.md` (project root)