# NextCloud — Project Router

**Purpose:** Deploy and operate NextCloud private cloud on fnet1 (3TB primary depot). Ansible-automated Docker stack with proxy, DNS, and backup.

**Status:** Deployed (TI-006) — all phases 1-9 complete, external access deferred (TI-008)

## [S-TIGHT]

Infrastructure project router. Match keywords to domain, load domain context, execute. All documentation lives in the vault (`../../personal-vault/01-Projects/nextcloud/`). This project contains code and agent configs only.

---

## Conventions

- Timestamps: US Eastern (America/New_York) | Dates: YYYY-MM-DD
- Target node: **fnet1** (`192.168.0.141`, 3TB primary depot)
- Ansible via playbook-executor or directly
- **Docs in vault, code in workshop** — no mixing

---

## Domain Routing

| Keywords | Route To |
|----------|----------|
| deploy, ansible, docker, nginx, SSL, dns, proxy, backup, restore, provision | [`routing/domain-routing.md`](./routing/domain-routing.md) → `infrastructure/AGENTS-REFINED.md` |
| rclone, external storage, dropbox, gdrive, fuse mount, cloud mount | [`routing/domain-routing.md`](./routing/domain-routing.md) → `infrastructure/AGENTS-REFINED-RCLONE.md` |
| wiki, notes, research, planning, session, status, activity log | [`routing/domain-routing.md`](./routing/domain-routing.md) → vault wiki |
| node, fnet, lab, playbook, trigger, inventory | [`routing/lab-inventory.md`](./routing/lab-inventory.md) |

---

## Load Directive

| Section | File | LOD | Size | Load When |
|---------|------|-----|------|-----------|
| Project overview & conventions | [`routing/overview.md`](./routing/overview.md) | L1 | ~1.2KB | Always |
| Lab node & playbook inventory | [`routing/lab-inventory.md`](./routing/lab-inventory.md) | L2 | ~1.4KB | Executing playbooks, targeting nodes |
| Domain routing & cross-reference | [`routing/domain-routing.md`](./routing/domain-routing.md) | L2 | ~1.1KB | Navigating to infrastructure or vault docs |

---

## Quick Task Routing

| Task | Route |
|------|-------|
| Deploy/reconfigure NextCloud | `./infrastructure/AGENTS-REFINED.md` |
| Set up rclone mounts | `./infrastructure/AGENTS-REFINED-RCLONE.md` |
| Run a playbook | [`routing/lab-inventory.md`](./routing/lab-inventory.md) |
| Read docs/research | `../../personal-vault/01-Projects/nextcloud/` |

---

*Last updated: 2026-05-21*