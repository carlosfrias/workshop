# Ansible Vault

**LEGACY — MIGRATE TO:** `personal-vault/03-Resources/Technical-Infrastructure/ansible-vault.md`

Lab node sudo passwords are managed via Ansible Vault. The vault master password lives in `~/.ansible/secure/.vault_pass` (mode 600, gitignored). Encrypted secrets are in `ansible/group_vars/lab_nodes/vault.yml`.

## Vault Password Location

**Secure location:** `~/.ansible/secure/.vault_pass`

This location is:
- Outside the workspace (not committed to git)
- User-specific (not shared across users)
- Protected with mode 600 (owner read/write only)

## Running Playbooks with Vault

```bash
cd technical-infrastructure/ansible
ansible-playbook -i inventory.yml playbooks/PLAYBOOK.yml --vault-password-file ~/.ansible/secure/.vault_pass
```

All playbooks targeting `lab_nodes` automatically load `ansible_become_pass` from `group_vars/lab_nodes/all.yml`, which references the encrypted `vault_sudo_password` in `vault.yml`.

## Encrypting a New Secret

```bash
ansible-vault encrypt_string --vault-password-file ~/.ansible/secure/.vault_pass 'SECRET_VALUE' --name 'vault_var_name'
```

## Editing the Vault

```bash
ansible-vault edit group_vars/lab_nodes/vault.yml --vault-password-file ~/.ansible/secure/.vault_pass
```

## Viewing Encrypted Content

```bash
ansible-vault view group_vars/lab_nodes/vault.yml --vault-password-file ~/.ansible/secure/.vault_pass
```

## Best Practices

- Never commit `.vault_pass` to git (it's in `.gitignore`)
- Use descriptive variable names (e.g., `vault_sudo_password` not `vault_pass`)
- Rotate vault password annually or when team members leave
- Store vault password backup in secure location (1Password, etc.)
- Directory `~/.ansible/secure/` should have mode 700

---

**Related:** [Ansible Testing](ansible-testing.md)
