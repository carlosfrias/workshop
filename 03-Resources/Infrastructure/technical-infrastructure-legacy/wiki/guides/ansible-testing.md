# Ansible Testing

**LEGACY — MIGRATE TO:** `personal-vault/03-Resources/Technical-Infrastructure/ansible-testing.md`

All scripts and playbooks **must be tested in the same session they are created or modified**. Testing is co-equal with authoring and documentation, not an afterthought.

## Running Playbooks

```bash
cd technical-infrastructure/ansible

# 1. Syntax check (always first)
ansible-playbook -i inventory.yml playbooks/PLAYBOOK.yml --syntax-check --vault-password-file ~/.ansible/secure/.vault_pass

# 2. Dry-run / check mode (see what would change)
ansible-playbook -i inventory.yml playbooks/PLAYBOOK.yml --check --vault-password-file ~/.ansible/secure/.vault_pass

# 3. Verbose execution (for debugging)
ansible-playbook -i inventory.yml playbooks/PLAYBOOK.yml --vault-password-file ~/.ansible/secure/.vault_pass -vvv

# 4. Normal execution
ansible-playbook -i inventory.yml playbooks/PLAYBOOK.yml --vault-password-file ~/.ansible/secure/.vault_pass
```

**`-vvv` flag**: Use `-vvv` (triple verbose) when a playbook fails or hangs. It shows the exact commands Ansible is running, SSH connections, module arguments, and return codes. This is essential for debugging tasks that call scripts or connect to remote nodes.

## Running Scripts Through Playbooks

Where possible, scripts should be wrapped in an Ansible playbook rather than executed directly. This provides:

- **Idempotency**: Ansible tracks what changed
- **Inventory awareness**: Playbooks know which nodes are in which groups
- **Vault integration**: Sensitive data is handled securely
- **Error recovery**: `ignore_errors`, `async`, and `poll` for long-running tasks
- **Parallelism**: Ansible runs tasks across nodes concurrently

### Example Playbook Structure

```yaml
- name: Run remote detection
  hosts: localhost
  connection: local
  tasks:
    - name: Detect lab node hardware
      ansible.builtin.command:
        argv:
          - "bash"
          - "{{ scripts_dir }}/remote-detect.sh"
          - "--output-dir"
          - "{{ lab_specs_dir }}/node-hardware"
      register: detect_result
      changed_when: true
      ignore_errors: yes        # Continue even if one node fails
      async: 600                # Timeout after 10 minutes
      poll: 10                  # Check every 10 seconds
```

## Testing After Every Change

| What changed | Test to run |
|-------------|-------------|
| Bash script | `bash -n script.sh` (syntax), then execute |
| Python script | `python3 -m py_compile script.py`, then execute |
| Ansible playbook | `--syntax-check`, then `--check`, then live with `-vvv` if issues |
| SSH config | `ssh -v HOSTNAME "hostname"` |
| Inventory file | `ansible-inventory -i inventory.yml --graph` |

## Session Integration

Playbooks, scripts, and their tests are authored and validated in a single working session. **Do not defer testing to a future session** — context is lost and issues go undetected.

---

**Related:** [Ansible Vault](ansible-vault.md) | [Quality Checklist](quality-checklist.md)
