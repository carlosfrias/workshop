# pi-cross-node-comms — Quick Start

Cross-node pi communication using an HTTP/SSE hub.

## Install

```bash
cd workshop/01-Projects/pi-cross-node-comms
bun install        # install bun itself (if not already)
pi install .       # install extension
```

## Usage

### Fleet Standup (Single Command)

```bash
# Humanized invocation
./scripts/run-playbook.sh "stand up the fleet"
./scripts/run-playbook.sh "get the lab online"
./scripts/run-playbook.sh "deploy pi and ollama to the lab"

# Or programmatically
./scripts/run-playbook.sh standup_fleet

# Or directly
ansible-playbook -i ansible/inventory.yml ansible/standup-fleet.yml
```

### 1. Start the Hub Server

```bash
# Loopback (auto-generates token, writes to server.secret.json)
bun server/coms-net-server.ts
# → coms-net: listening on http://127.0.0.1:XXXXX

# Or with explicit port and auth
PI_COMS_NET_PORT=8080 PI_COMS_NET_AUTH_TOKEN=$(openssl rand -hex 32) \
  bun server/coms-net-server.ts
```

### 2. Connect Agents

```bash
# Agent 1 (auto-discovers server via server.json)
pi -e src/index.ts -- --name orchestrator --project demo

# Agent 2 (explicit server URL)
pi -e src/index.ts -- --name worker --project demo --server-url http://127.0.0.1:XXXXX --auth-token <token>
```

### 3. Communicate

```
> coms_net_list()
→ 1 peer(s):
  ● worker (sonnet-4-6) 15% — doing research

> coms_net_send({ target: "worker", prompt: "Check SSHFS mounts on lab nodes" })
→ coms_net_send → worker
  msg_id 01JQK...

> coms_net_await({ msg_id: "01JQK..." })
→ Reply from worker:
  All 7 lab nodes healthy. fnet3 swap at 60% — worth monitoring.
```

## Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--name` | `agent-XXXXXX` | Agent display name |
| `--purpose` | `""` | One-liner shown to peers |
| `--project` | `"default"` | Project namespace |
| `--server-url` | auto-discovered | Hub URL (overrides env/server.json) |
| `--auth-token` | auto-discovered | Bearer token |
| `--explicit` | `false` | Hide from auto-discovery |
| `--color` | auto | Hex color `#RRGGBB` |

## Cross-Node Setup

For agents on different machines:

1. Start hub on orchestrator (bind to LAN IP):
   ```bash
   PI_COMS_NET_HOST=0.0.0.0 PI_COMS_NET_PORT=8080 \
     PI_COMS_NET_AUTH_TOKEN=$(openssl rand -hex 32) \
     bun server/coms-net-server.ts
   ```

2. On remote node, connect with server URL:
   ```bash
   pi -e src/index.ts -- --name lab-worker --server-url http://192.168.1.100:8080 --auth-token <token>
   ```

**Security note:** Plain HTTP. For production, add TLS via reverse proxy (nginx/Caddy).
