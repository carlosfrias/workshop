---
section_id: connection
size_estimate: ~1.4KB
lod_level: Low
purpose: Hub URL, auth token sources, project name, and connection commands.
---

# Connection Config

## [S-TIGHT]

Hub URL, auth token sources, project name, and connection commands for attaching pi agents to the fleet hub.

[LOD: Low] *Load when connecting to the fleet or configuring agents.*

## Parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| Hub URL | `http://192.168.0.142:8080` | Ansible inventory |
| Auth token | `$PI_COMS_NET_AUTH_TOKEN` | Env var or `-e coms_token=TOKEN` |
| Project name | `lab` | Fleet-wide default |
| Fallback token | `7e095b8e...386a0` | Used when env var unset in playbook |

## How to Connect

```bash
# From orchestrator pi session
pi -e src/index.ts \
  --name orchestrator \
  --project lab \
  --server-url http://192.168.0.142:8080 \
  --auth-token $PI_COMS_NET_AUTH_TOKEN
```

## Key Facts

- **Always use the env var** `$PI_COMS_NET_AUTH_TOKEN` for auth.
- Fallback token is embedded in Ansible playbooks for non-interactive runs.
- Project name `lab` must match across all agents and the hub.

---

*See also: [INVENTORY.md](INVENTORY.md) for node IPs, [MONITORING.md](MONITORING.md) for health checks.*