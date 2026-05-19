# Ansible Vault

**LEGACY — MIGRATE TO:** `personal-vault/03-Resources/Technical-Infrastructure/ansible-vault.md`

Lab node sudo passwords are managed via Ansible Vault. The vault master password lives in `~/.ansible/secure/.vault_pass` (mode 600, gitignored). Encrypted secrets are in `ansible/group_vars/lab_nodes/vault.yml` (sudo) and service-specific vault files in `~/.ansible/secure/`.

## Vault Password Location

**Secure location:** `~/.ansible/secure/.vault_pass`

This location is:
- Outside the workspace (not committed to git)
- User-specific (not shared across users)
- Protected with mode 600 (owner read/write only)

## Vault Files

All encrypted vault files use the same password (`~/.ansible/secure/.vault_pass`).

| Vault File | Contents | Location |
|-----------|----------|----------|
| `vault.yml` | `vault_sudo_password` (lab sudo) | `group_vars/lab_nodes/vault.yml` |
| `vault-nextcloud.yml` | NextCloud admin, DB, DB-root passwords | `~/.ansible/secure/vault-nextcloud.yml` |

## Running Playbooks with Vault

```bash
# Legacy infrastructure playbooks
cd technical-infrastructure/ansible
ansible-playbook -i inventory.yml playbooks/PLAYBOOK.yml --vault-password-file ~/.ansible/secure/.vault_pass

# NextCloud playbook (loads both vault files via vars_files)
cd workshop/01-Projects/nextcloud/ansible
ansible-playbook -i inventory.ini deploy-nextcloud.yml --vault-password-file ~/.ansible/secure/.vault_pass

# Or via env var (set in .bash_profile)
export ANSIBLE_VAULT_PASSWORD_FILE=~/.ansible/secure/.vault_pass
ansible-playbook -i inventory.ini deploy-nextcloud.yml
```

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
- Use service-scoped vault files (e.g., `vault-nextcloud.yml`) rather than one monolithic vault
- Add new service vaults to the Vault Files table above

---

**Related:** [Ansible Testing](ansible-testing.md)
