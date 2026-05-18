# Phase 3: Ansible & Vault Module

**Purpose:** Detailed instructions for Ansible Vault and Playbook testing.
**When to load:** When executing tasks involving Ansible, Vault, or multi-node deployments.

---

## Ansible Vault

Lab node sudo passwords are managed via Ansible Vault. The vault master password lives in `ansible/.vault_pass` (mode 600, gitignored). Encrypted secrets are in `ansible/group_vars/lab_nodes/vault.yml`.

### Running playbooks with vault
```bash
cd technical-infrastructure/ansible
ansible-playbook -i inventory.yml playbooks/PLAYBOOK.yml --vault-password-file ./.vault_pass
```

### Encrypting a new secret
```bash
ansible-vault encrypt_string --vault-password-file ./.vault_pass 'SECRET_VALUE' --name 'vault_var_name'
```

### Editing the vault
```bash
ansible-vault edit group_vars/lab_nodes/vault.yml --vault-password-file ./.vault_pass
```

---

## Playbook and Script Testing

**Testing is co-equal with authoring.** Every change must be tested in the same session it is created.

### Running Playbooks
1. **Syntax check:** `ansible-playbook -i inventory.yml playbooks/PLAYBOOK.yml --syntax-check --vault-password-file ./.vault_pass`
2. **Dry-run (check mode):** `ansible-playbook -i inventory.yml playbooks/PLAYBOOK.yml --check --vault-password-file ./.vault_pass`
3. **Verbose execution:** `ansible-playbook -i inventory.yml playbooks/PLAYBOOK.yml --vault-password-file ./.vault_pass -vvv` (Essential for debugging fails/hangs)
4. **Normal execution:** `ansible-playbook -i inventory.yml playbooks/PLAYBOOK.yml --vault-password-file ./.vault_pass`

### Running Scripts Through Playbooks
Preference: Wrap bash/Python scripts in Ansible for idempotency, inventory awareness, and secure vault integration.

**Example Wrapper Pattern:**
```yaml
- name: Run remote detection
  hosts: localhost
  connection: local
  tasks:
    - name: Detect lab node hardware
      ansible.builtin.command:
        argv: ["bash", "{{ scripts_dir }}/remote-detect.sh", "--output-dir", "{{ lab_specs_dir }}/node-hardware"]
      register: detect_result
      changed_when: true
      ignore_errors: yes
      async: 600
      poll: 10
```

### Testing Matrix

| Object | Test Sequence |
| :--- | :--- |
| **Bash script** | `bash -n script.sh` $\rightarrow$ Execute |
| **Python script** | `python3 -m py_compile script.py` $\rightarrow$ Execute |
| **Ansible playbook** | `--syntax-check` $\rightarrow$ `--check` $\rightarrow$ Execute with `-vvv` |
| **SSH config** | `ssh -v HOSTNAME "hostname"` |
| **Inventory file** | `ansible-inventory -i inventory.yml --graph` |
