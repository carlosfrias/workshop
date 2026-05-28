# pi-cross-node-comms — Quick Start

Cross-node pi communication using an HTTP/SSE hub.

## Install & Update

### First-time install

```bash
cd workshop/02-Areas/Infrastructure/pi-cross-node-comms
pi install .       # install extension globally into pi
```

This reads `package.json` for the extension entry point, copies the package into pi's extension directory, and adds it to `~/.pi/settings.json`. After installing, the `coms_net_send`, `coms_net_await`, `coms_net_list`, and `coms_net` tools become available in any pi session.

### Update after code changes

After making changes to the extension source:

```bash
pi update ./workshop/02-Areas/Infrastructure/pi-cross-node-comms
```

Or update all installed extensions at once:

```bash
pi update --extensions
```

**Restart required:** pi reads extension configs at session start. After install or update, restart pi (or start a new session) for changes to take effect. `/reload` does NOT pick up extension changes.

## Usage

### Fleet Standup

**Concurrent chains (recommended):** Runs 3 chains in parallel — much faster than the monolith.

```bash
ansible-playbook -i ansible/inventory.yml ansible/standup-fleet-chains.yml
```

| Chain | Playbooks (sequential) | Rationale |
|-------|----------------------|------------|
| Chain 1 | Phase 3 — Ollama + Models | Longest-running, no deps |
| Chain 2 | Phase 2 → Phase 4 | Pi before extension; independent of hub |
| Chain 3 | Phase 1 → Phase 5 → Phase 6 | Hub → Agents → Validate |

**Individual phases (run standalone):**

```bash
ansible-playbook -i ansible/inventory.yml ansible/phase1-hub-server.yml     # Hub on fnet2
ansible-playbook -i ansible/inventory.yml ansible/phase2-pi-availability.yml  # Pi on all nodes
ansible-playbook -i ansible/inventory.yml ansible/phase3-ollama-models.yml     # Ollama + models
ansible-playbook -i ansible/inventory.yml ansible/phase4-extension-deploy.yml # Extension on all nodes
ansible-playbook -i ansible/inventory.yml ansible/phase5-agent-services.yml   # systemd agents
ansible-playbook -i ansible/inventory.yml ansible/phase6-fleet-validation.yml # Validate + prune
```

**Legacy monolith (still available):**

```bash
ansible-playbook -i ansible/inventory.yml ansible/standup-fleet.yml
```

**Humanized invocation (playbook-executor):**

```bash
./scripts/run-playbook.sh "stand up the fleet"
./scripts/run-playbook.sh "get the lab online"
./scripts/run-playbook.sh "deploy pi and ollama to the lab"
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
