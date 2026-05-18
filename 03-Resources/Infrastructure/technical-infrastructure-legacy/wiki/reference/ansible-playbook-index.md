# Ansible Playbook Index
**Generated:** 2026-05-02 by fnet5/qwen3:8b (auto-distributed)  
**Location:** `technical-infrastructure/ansible/`

## Playbook Inventory

| Playbook | Target Hosts | Purpose | Variables | Status |
|----------|-------------|---------|-----------|--------|
| `detect-lab-nodes.yml` | localhost | Discover fnet1-fnet7 via ping + SSH | `lab_subnet` | ✅ Active |
| `check-lab-status.yml` | lab_nodes | Health check: CPU, RAM, disk, ollama | — | ✅ Active |
| `run-pilot-lab.yml` | lab_nodes | Full cycle: detect + hardware specs + benchmark | `benchmark_duration` | ✅ Active |
| `deploy-task-workers.yml` | lab_nodes | Deploy task-worker.sh + systemd timer | — | ✅ Active |
| `install-ollama.yml` | lab_nodes | Install ollama, pull models | `models_to_pull` | 📋 Planned |
| `update-lab-nodes.yml` | lab_nodes | apt update + upgrade | — | 📋 Planned |
| `backup-configs.yml` | lab_nodes | Backup /etc configs to orchestrator | `backup_dir` | 📋 Planned |

## Quick Command Reference

```bash
cd technical-infrastructure/ansible

# Syntax check (always first)
ansible-playbook -i inventory.yml playbooks/PLAYBOOK.yml --syntax-check --vault-password-file ./.vault_pass

# Dry run (see what would change)
ansible-playbook -i inventory.yml playbooks/PLAYBOOK.yml --check --vault-password-file ./.vault_pass

# Verbose execution (for debugging)
ansible-playbook -i inventory.yml playbooks/PLAYBOOK.yml --vault-password-file ./.vault_pass -vvv

# Normal execution
ansible-playbook -i inventory.yml playbooks/PLAYBOOK.yml --vault-password-file ./.vault_pass
```

## Vault Usage

```bash
# Encrypt a secret
ansible-vault encrypt_string --vault-password-file ./.vault_pass 'SECRET_VALUE' --name 'vault_var_name'

# Edit vault
cd technical-infrastructure/ansible
ansible-vault edit group_vars/lab_nodes/vault.yml --vault-password-file ./.vault_pass

# Run with vault
ansible-playbook playbooks/deploy-task-workers.yml --vault-password-file ./.vault_pass
```

## Testing Checklist

| Before Deploy | Check |
|--------------|-------|
| [ ] | `--syntax-check` passes |
| [ ] | `--check` shows expected changes |
| [ ] | Inventory resolves all target hosts |
| [ ] | Vault password file exists (mode 600) |
| [ ] | One-node test (`--limit fnet3`) first |

## Common Failure Modes

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `UNREACHABLE` | Node offline or SSH key missing | Check `ssh fnetN hostname` |
| `FAILED` > 0 | Script error on node | Check node logs in `/srv/tasks/completed/` |
| Timeout | Task hangs (ollama loading) | Increase `async` timeout in playbook |
| Vault error | Wrong password or missing file | Verify `.vault_pass` exists and is readable |
| Permission denied | sudo password wrong | Re-run `ansible-vault edit` for `vault_sudo_password` |
