# NextCloud Project — Architecture

## System Design Decisions

### Stack (Docker Compose on fnet2)

| Service | Image | Purpose |
|---------|-------|---------|
| NextCloud | `nextcloud:latest` | File sync, collaboration, web UI |
| MariaDB | `mariadb:10.11` | Primary database |
| Redis | `redis:7-alpine` | Caching, file locking |
| Nginx | `nginx:alpine` | Reverse proxy, TLS termination |
| Cron | `nextcloud:latest` | Background jobs (same image, cron entrypoint) |

### Network Layout

```
Internet ──[blocked]──► TP-Link AX6000
                           │
                     192.168.0.0/24
                     ┌─────┴──────┐
                     │  Lab Switch │
                     └─────┬──────┘
                     ┌─────┼─────┐
                  fnet1  fnet2  fnet3-7
                  depot  NEXT   workers
```

- **Internal DNS:** dnsmasq resolves `nextcloud.home` → `192.168.0.142`
- **External access:** Deferred (TI-008 — requires OPNsense/Protectli)
- **VLAN segmentation:** Planned but not yet implemented

### Data Flow

```
Client (Desktop/Phone)
  │
  ▼ http://nextcloud.home:8080 (or http://192.168.0.142:8080)
  │
  ▼ Nginx reverse proxy (port 443 → NextCloud)
  │
  ▼ NextCloud app container
  │
  ├──► MariaDB (database persistence)
  ├──► Redis (caching + file locking)
  └──► /srv/nextcloud/data/ (user files)
```

### Why This Approach

1. **Docker over bare-metal:** Isolation, reproducibility, easy upgrades
2. **Ansible automation:** Consistent deployment, idempotent, auditable
3. **Nginx as reverse proxy:** TLS termination, rate limiting, future domain flexibility
4. **Redis:** NextCloud performs poorly without it — required, not optional
5. **MariaDB over PostgreSQL:** Lighter resource footprint for a 7-node lab

### Ansible Role Evaluation

| Role | GitHub | Pros | Cons |
|------|--------|------|------|
| ReinerNippes/nextcloud | Full playbook | Complete (Nginx/Apache, MariaDB/Postgres, Redis, OnlyOffice/Collabora) | Opinionated, less modular |
| robertdebock/ansible-role-nextcloud | Role only | Clean, composable, well-maintained | Requires separate roles for DB/cache/proxy |

**Recommendation:** Start with a custom Docker Compose playbook rather than either role, since our stack is Docker-based and both roles target bare-metal installs. Use their patterns as reference.

### Deployment Phases

| Phase | Task | Status |
|-------|------|--------|
| 1 | Create Ansible playbook for Docker Compose deployment | ❌ Not started |
| 2 | Deploy NextCloud + MariaDB + Redis on fnet2 | ❌ Not started |
| 3 | Configure Nginx reverse proxy | ❌ Not started |
| 4 | Configure DNS (dnsmasq) for nextcloud.home | ❌ Not started |
| 5 | Create admin account, test file upload | ❌ Not started |
| 6 | Configure backup to fnet1/fnet3 | ❌ Not started |
| 7 | (Deferred) External access via OPNsense | ❌ Deferred (TI-008) |