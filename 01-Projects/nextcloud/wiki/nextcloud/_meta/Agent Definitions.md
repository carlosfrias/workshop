# NextCloud Project — Agent Definitions

## nextcloud-infra

| Field | Value |
|-------|-------|
| **Name** | `nextcloud-infra` |
| **Description** | Install, configure, and operate NextCloud on lab node fnet2 via Ansible/Docker |
| **Tools** | read, write, edit, bash, intercom |
| **Model** | `ollama/qwen3:8b` |
| **CWD** | `./infrastructure` |
| **Inherit Project Context** | false |
| **Inherit Skills** | false |

### Usage

```
/run nextcloud-infra "Deploy NextCloud Docker stack on fnet2"
/run nextcloud-infra "Check NextCloud service status on fnet2"
/run nextcloud-infra "Create backup playbook for NextCloud data"
```

### What It Does

- Deploys NextCloud via Ansible + Docker Compose
- Manages configuration changes (Nginx, MariaDB, Redis)
- Runs health checks and status reports
- Creates and manages backups
- Documents all changes in the wiki activity log