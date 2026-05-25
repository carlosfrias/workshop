# Gist Message Protocol — Off-Premise Remote Node Access

**LEGACY — MIGRATE TO:** `personal-vault/03-Resources/Technical-Infrastructure/gist-message-protocol.md`

**Status:** Deployed (scripts ready, Ansible playbook in progress)  
**Gist ID:** `0c517214489cb78c0484ca661f3d8463` (shared task queue)  
**Nodes:** fnet1-fnet7  
**Latency:** ~30s polling interval  
**Authentication:** GitHub Personal Access Token (gist scope)  

---

## Problem Solved

When off-premise, lab nodes are unreachable via SSH through the home router. The Gist Message Protocol bridges this gap by using **GitHub Gist as a persistent message queue** that both the orchestrator and nodes can access over HTTPS.

| Scenario | Before | After |
|----------|--------|-------|
| Nodes off-premise | SSH times out, no control | Tasks dispatched via Gist, results collected via Gist |
| Mobile data only | Cannot reach fnet3 at 192.168.0.x | HTTPS to gist.githubusercontent.com works everywhere |
| Firewall traversal | UDP WireGuard blocked | HTTPS on port 443 passes through |
| Audit trail | SSH commands lost | All tasks and results preserved in Gist revision history |

---

## Architecture

```
┌─────────────────┐         HTTPS          ┌─────────────────┐
│   Orchestrator  │◄──────────────────────►│  GitHub Gist    │
│  (Mac, mobile)  │    task-node-id.json    │  (message queue)│
│                 │◄──────────────────────►│                 │
│                 │    result-node-id.json  │                 │
└─────────────────┘                        └─────────────────┘
                                                     ▲
                                                     │ HTTPS
                                                     │
                                              ┌─────────────────┐
                                              │   Lab Node fnet3  │
                                              │  (systemd timer)  │
                                              │   polls every 30s   │
                                              │   executes tasks    │
                                              │   posts results     │
                                              └─────────────────┘
```

**Message Flow:**
1. Orchestrator writes `task-fnet3-<id>.json` to Gist
2. Node's `gist-worker` polls Gist every 30 seconds
3. Worker sees task addressed to its node, executes it
4. Worker writes `result-fnet3-<id>.json` back to Gist
5. Orchestrator polls for results and collects them

---

## Components

| Component | File | Role | Location |
|-----------|------|------|----------|
| Worker | `gist-worker.py` | Polls Gist, executes tasks, posts results | `/usr/local/bin/` on each node |
| Orchestrator | `gist-orchestrator.py` | Dispatches tasks, collects results | `orchestrator` (Mac) |
| Systemd Service | `gist-worker@.service` | Runs worker on demand | `/etc/systemd/system/` |
| Systemd Timer | `gist-worker.timer` | Triggers worker every 30s | `/etc/systemd/system/` |
| Ansible Playbook | `deploy-gist-worker.yml` | Deploys to all 7 nodes | `ansible/playbooks/` |

---

## File Naming Convention

| Pattern | Direction | Purpose |
|---------|-----------|---------|
| `task-<node>-<id>.json` | Orchestrator → Node | Task assignment |
| `result-<node>-<id>.json` | Node → Orchestrator | Execution result |
| `task-all-<id>.json` | Orchestrator → All nodes | Broadcast task |

---

## Deployment Playbooks

| Playbook | Purpose | Audience | Includes Orchestrator | Includes Workers |
|----------|---------|----------|----------------------|------------------|
| `deploy-gist-message-protocol.yml` | **One-shot full deployment** — orchestrator (Mac) + all workers | Owner with full cluster | ✅ Yes | ✅ Yes |
| `deploy-gist-workers-only.yml` | **Workers only** — for third-party clusters | Third parties joining your network | ❌ No | ✅ Yes |
| `deploy-gist-worker.yml` | Individual worker deployment (internal use) | Owner, single node | ❌ No | ✅ Yes |

### 1. Full Deployment (Orchestrator + Workers)

```bash
cd technical-infrastructure/ansible
ansible-playbook -i inventory.yml playbooks/deploy-gist-message-protocol.yml \
  --vault-password-file ./.vault_pass \
  --extra-vars "gist_id=$GIST_ORCHESTRATOR_GIST_ID"
```

**What it does:**
1. **Orchestrator (localhost):**
   - Verifies/creates the shared Gist
   - Installs `gist-orchestrator` wrapper to `~/.local/bin/`
   - Adds `GIST_ORCHESTRATOR_GIST_ID` to `.bashrc` or `.zshrc`
   - Warns if `GITHUB_TOKEN` is not set
2. **Workers (lab_nodes):**
   - Copies `gist-worker.py` to `/usr/local/bin/`
   - Creates `/srv/gist-tasks/{pending,running,completed,results}`
   - Installs systemd service template + timer
   - Enables timer for node-specific and all-node tasks
   - Verifies timer is active

### 2. Workers Only (Third-Party Cluster)

**For third parties who want to connect their nodes to your orchestrator:**

```bash
# On their machine (they provide their own inventory)
ansible-playbook -i their-inventory.ini deploy-gist-workers-only.yml \
  --extra-vars "gist_worker_gist_id=0c517214489cb78c0484ca661f3d8463"
```

**What they provide:**
- Their own inventory file with their nodes
- The Gist ID (you share this with them)
- A GitHub token with `gist` scope (they create this themselves)

**What they get:**
- Workers running on every node, polling your shared Gist
- Automatic task execution and result posting
- Systemd timer with automatic restart on boot

**Security:**
- Workers only read tasks addressed to their hostname
- Workers post results only for their own tasks
- No access to your orchestrator or other nodes
- Gist ID alone is harmless (it's just a queue URL)

### 3. Orchestrator Setup Script (Mac)

If you prefer a script over Ansible for the orchestrator side:

```bash
cd ~/Cloud/workshop
bash scripts/setup-gist-orchestrator.sh [--gist-id ID] [--token TOKEN]
```

**What it does:**
- Verifies or creates the Gist
- Installs `gist-orchestrator` command to `~/.local/bin/`
- Adds environment variables to shell profile
- Runs a connectivity test

## Setup

### 1. GitHub Token

Create a GitHub Personal Access Token with `gist` scope:
```bash
# Visit: https://github.com/settings/tokens/new
# Scopes: ✓ gist
# Save the token securely (1Password, Keychain)
```

Set environment variable:
```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"
```

### 2. Orchestrator Side (Mac)

```bash
cd ~/Cloud/workshop

# Submit a task to fnet3
python3 technical-infrastructure/scripts/gist-orchestrator.py \
  --gist-id 0c517214489cb78c0484ca661f3d8463 \
  --token "$GITHUB_TOKEN" \
  --submit --node fnet3 --command "ollama list"

# Submit to all nodes
python3 technical-infrastructure/scripts/gist-orchestrator.py \
  --gist-id 0c517214489cb78c0484ca661f3d8463 \
  --token "$GITHUB_TOKEN" \
  --submit-all --command "ollama ps"

# Collect results from last 5 minutes
python3 technical-infrastructure/scripts/gist-orchestrator.py \
  --gist-id 0c517214489cb78c0484ca661f3d8463 \
  --token "$GITHUB_TOKEN" \
  --collect --since 300

# Watch for new results (live)
python3 technical-infrastructure/scripts/gist-orchestrator.py \
  --gist-id 0c517214489cb78c0484ca661f3d8463 \
  --token "$GITHUB_TOKEN" \
  --watch

# Show queue status
python3 technical-infrastructure/scripts/gist-orchestrator.py \
  --gist-id 0c517214489cb78c0484ca661f3d8463 \
  --token "$GITHUB_TOKEN" \
  --status
```

### 3. Node Side (Linux)

```bash
# On each lab node (or via Ansible)
sudo cp gist-worker.py /usr/local/bin/
sudo chmod +x /usr/local/bin/gist-worker.py

# Install systemd timer
sudo systemctl daemon-reload
sudo systemctl enable gist-worker@fnet3.timer
sudo systemctl start gist-worker@fnet3.timer
sudo systemctl status gist-worker.timer
```

### 4. Ansible Deployment (All Nodes)

```bash
cd technical-infrastructure/ansible
ansible-playbook -i inventory.yml playbooks/deploy-gist-worker.yml \
  --vault-password-file ./.vault_pass
```

---

## Task Types

| Type | Description | Example Command |
|------|-------------|-----------------|
| `shell` | Execute shell command | `ollama list` |
| `ollama` | Run Ollama model inference | `prompt: "Explain quantum computing"` |

**Task JSON Format:**
```json
{
  "id": "20260503120000-a1b2c3d4",
  "node": "fnet3",
  "type": "shell",
  "command": "ollama list",
  "timeout": 300,
  "submitted_at": "2026-05-03T12:00:00Z"
}
```

**Result JSON Format:**
```json
{
  "task_id": "20260503120000-a1b2c3d4",
  "node": "fnet3",
  "status": "success",
  "rc": 0,
  "stdout": "NAME\tqwen3:8b\t...",
  "stderr": "",
  "elapsed_seconds": 2.14,
  "completed_at": "2026-05-03T12:00:35Z"
}
```

---

## Security

| Concern | Mitigation |
|---------|-----------|
| Token exposure | Stored in Ansible Vault, never in code |
| Unauthorized task execution | Tasks are node-specific (`task-fnet3-`), nodes reject tasks for other nodes |
| Command injection | Commands are shell-escaped in worker; no interpolation of user input |
| Gist visibility | Gist is secret (unlisted), but use private gist for production |
| Rate limiting | 30s polling interval stays well below GitHub API limits (5000/hr) |

---

## Limitations

| Limit | Value | Mitigation |
|-------|-------|----------|
| Polling latency | ~30 seconds | Acceptable for async workflows; use `--watch` for faster collection |
| Gist API rate limit | 5000 requests/hour | 7 nodes × 120 polls/hour = 840/hr; well within limit |
| File size | 10MB per file | Truncate stdout/stderr to 5KB/2KB respectively |
| Gist file limit | ~300 files | Implement cleanup of old completed results |

---

## Monitoring

```bash
# Worker logs on node
sudo journalctl -u gist-worker@fnet3 -f

# Worker status
python3 /usr/local/bin/gist-worker.py --status

# Orchestrator status
python3 gist-orchestrator.py --status
```

---

## Related Files

| File | Description |
|------|-------------|
| `scripts/gist-worker.py` | Autonomous worker (node-side) |
| `scripts/gist-orchestrator.py` | Task dispatcher + result collector (orchestrator-side) |
| `scripts/setup-gist-orchestrator.sh` | Orchestrator setup script for Mac |
| `ansible/playbooks/deploy-gist-message-protocol.yml` | **Full deployment** — orchestrator + workers |
| `ansible/playbooks/deploy-gist-workers-only.yml` | **Workers only** — for third-party clusters |
| `ansible/playbooks/deploy-gist-worker.yml` | Worker deployment (internal, single-node) |
| `ansible/templates/gist-worker@.service.j2` | Systemd service template |
| `ansible/templates/gist-worker.timer.j2` | Systemd timer template |
| `ansible/templates/gist-orchestrator-wrapper.sh.j2` | Orchestrator wrapper script |

---

*Created: 2026-05-03*
