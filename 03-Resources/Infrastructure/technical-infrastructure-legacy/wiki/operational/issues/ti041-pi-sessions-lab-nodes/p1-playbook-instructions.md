# TI-041 Phase 1 — Updated: Use Playbook-Executor for pi Installation

## Discovery
Playbook-executor ALREADY has `deploy-pi.yml` which does everything needed:
- Installs Node.js 20+ via NodeSource
- Installs pi CLI (`npm install -g @mariozechner/pi-coding-agent`)
- Installs pi-intercom skill
- Fixes hostnames
- Creates systemd service for pi-intercom
- Verifies installation

**Playbook path:** `technical-infrastructure/ansible/playbooks/deploy-pi.yml`
**Playbook-executor package:** `technical-infrastructure/packages/playbook-executor/`

## Instructions for Orchestrator

### Step 1: Verify playbook-executor is available
```bash
ls -la /Users/friasc/Dropbox/workshop/technical-infrastructure/packages/playbook-executor/scripts/run-playbook.sh
```

### Step 2: Run deploy-pi playbook via playbook-executor
```bash
cd /Users/friasc/Dropbox/workshop/technical-infrastructure/packages/playbook-executor
./scripts/run-playbook.sh deploy_pi
```

**OR** if keyword trigger doesn't work, run directly:
```bash
cd /Users/friasc/Dropbox/workshop/technical-infrastructure/ansible
ansible-playbook -i inventory.ini playbooks/deploy-pi.yml
```

**Note:** If no `inventory.ini` exists, create one or use `--limit` with SSH hosts.

### Step 3: Verify pi installed on each node
```bash
for node in fnet1 fnet2 fnet3 fnet4 fnet5 fnet6 fnet7; do
  echo "=== $node ==="
  ssh -o ConnectTimeout=3 "$node" "which pi && pi --version" 2>/dev/null || echo "NO pi CLI"
done
```

### Step 4: Report evidence
- Playbook execution output (success/failure per node)
- pi version on each reachable node
- Any errors

## Expected
- Node.js 20+ installed on all reachable nodes
- pi CLI available on all reachable nodes
- pi-intercom skill installed
- systemd service created (if playbook runs to completion)

## If Playbook Fails
Document the error and try direct Ansible:
```bash
ansible-playbook -i "fnet1,fnet2,fnet3,fnet4,fnet5,fnet6,fnet7," playbooks/deploy-pi.yml --user friasc
```

