# NextCloud — Project Overview

**Section ID:** `nc-overview` | **Size:** ~1.2KB | **LOD:** L1 (always load) | **Purpose:** Project identity, status, conventions, and discovery path.

---

## [S-TIGHT]

NextCloud private cloud deployment on fnet1. Status: deployed (TI-006, all phases 1-9 complete). External access deferred (TI-008). Documentation lives in vault; this project contains code and agent configs only.

---

## Project Identity

- **Purpose:** Deploy and operate NextCloud private cloud storage on lab node fnet1 (3TB primary depot). Ansible-automated Docker stack with proxy, DNS, and backup.
- **Status:** Deployed (TI-006) — all phases 1-9 complete, external access deferred (TI-008)

## Conventions

- All timestamps in US Eastern (America/New_York)
- All dates: YYYY-MM-DD
- Target node: **fnet1** (`192.168.0.141`, 3TB primary depot)
- Ansible playbooks run through playbook-executor or directly
- **Documentation in vault**, code in workshop — no mixing

---

## Discovery Path

```
1. workshop/AGENTS.md                                    ← Pick project (infrastructure keywords)
2. workshop/01-Projects/nextcloud/AGENTS.md              ← Pick domain (this project)
3. workshop/01-Projects/nextcloud/routing/overview.md    ← YOU ARE HERE (project context)
4a. workshop/01-Projects/nextcloud/infrastructure/AGENTS-REFINED.md          ← Golden path (deployment)
4b. workshop/01-Projects/nextcloud/infrastructure/AGENTS-REFINED-RCLONE.md  ← Golden path (rclone)
4c. workshop/01-Projects/nextcloud/infrastructure/AGENTS.md                  ← Original scaffold
4d. personal-vault/01-Projects/nextcloud/                                    ← Knowledge, research, wiki
```

---

*Last updated: 2026-05-19*